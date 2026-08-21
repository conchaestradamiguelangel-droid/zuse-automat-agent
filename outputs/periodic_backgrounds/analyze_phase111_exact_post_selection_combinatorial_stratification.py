from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"

MOTIF_RESULTS_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_results.json"
PARTITION_RESULTS_PATH = OUTPUT_DIR / "phase109_fixed_budget_hamming_partition_results.json"
LOIO_RESULTS_PATH = OUTPUT_DIR / "phase110_internal_loio_a_g_results.json"
RESULTS_PATH = OUTPUT_DIR / "phase111_exact_post_selection_combinatorial_stratification_results.json"
MANIFEST_PATH = OUTPUT_DIR / "phase111_exact_post_selection_combinatorial_stratification_manifest.json"
REPORT_PATH = OUTPUT_DIR / "phase111_exact_post_selection_combinatorial_stratification_report.md"

EXPECTED_JSON_HASHES = {
    MOTIF_RESULTS_PATH: (
        "9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24",
        "982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353",
    ),
    PARTITION_RESULTS_PATH: (
        "ba5cf94330ce5c27c6b7c4420f910c637debac1273b9b25d3ad4fd787c141d04",
        "dcf3d5847af14b3128e88dac765e491900340ddf4587b50281f42ac8ade147b1",
    ),
    LOIO_RESULTS_PATH: (
        "c135f9d0c63b0baa5ffd0a8c9d4c16a9f258482fbe1ac560a3eff076feb76c0d",
        "6a8223b20905eafb92cb6fa5727574587d4f4e2313a414e274500d789fd75d80",
    ),
}

EXTERNAL = "EXTERNAL_ATTACHMENT_RESCUE"
INTERNAL = "INTERNAL_EDGE_DEPENDENT_RESCUE"
LABELS = {EXTERNAL, INTERNAL}
EXPECTED_RESCUES = 223
EXPECTED_INSTANCES = 101
EXPECTED_EXTERNAL = 54
EXPECTED_INTERNAL = 169
EXPECTED_MULTIPLICITIES = {1: 56, 2: 18, 3: 3, 4: 14, 6: 4, 7: 6}
LOW_SIZES = {2, 3}
HIGH_SIZES = {4, 6, 7}
LOW_INSTANCES = 21
HIGH_INSTANCES = 24
STATUS = "EXACT_POST_SELECTION_COMBINATORIAL_STRATIFICATION_CALIBRATED"

FORBIDDEN_FIELDS = {
    "A_V",
    "A_R",
    "minimum_vertex_cut",
    "minimum_edge_cut",
    "individually_critical_vertices",
    "individually_critical_edges",
    "kappa_v",
    "lambda_e",
    "robustness_label",
    "cut_mechanisms",
    "cut_mechanism_counts",
    "external_rescue",
    "per_internal_edge_removal",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def raw_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def read_gated_json(path: Path) -> tuple[dict[str, Any], dict[str, str]]:
    expected_raw, expected_canonical = EXPECTED_JSON_HASHES[path]
    actual_raw = raw_sha256(path)
    if actual_raw != expected_raw:
        raise RuntimeError(f"Raw SHA-256 mismatch: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual_canonical = canonical_sha256(value)
    if actual_canonical != expected_canonical:
        raise RuntimeError(f"Canonical SHA-256 mismatch: {path.name}")
    return value, {"raw": actual_raw, "canonical": actual_canonical}


def fraction_payload(value: Fraction) -> dict[str, Any]:
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def canonical_identity(instance_key: Any, words: Iterable[int]):
    ordered = tuple(sorted(map(int, words)))
    if len(ordered) != 2 or ordered[0] == ordered[1]:
        raise RuntimeError("Invalid K2 rescue identity")
    return str(instance_key), ordered


def motif_rows(payload: dict[str, Any]) -> dict[tuple[str, tuple[int, ...]], dict[str, Any]]:
    output = {}
    for source in payload["atlas"]["mechanism_audits"]:
        if source["motif"] != "K2":
            continue
        instance_key = "|".join(
            (
                str(source["cube_key"]),
                str(int(source["pair_index"])),
                str(int(source["period"])),
                str(source["metric"]),
            )
        )
        identity = canonical_identity(instance_key, source["words"])
        if identity in output:
            raise RuntimeError("Duplicate identity in motif source")
        output[identity] = {
            "mechanism_label": str(source["mechanism_label"]),
        }
    return output


def partition_rows(payload: dict[str, Any]) -> dict[tuple[str, tuple[int, ...]], dict[str, Any]]:
    output = {}
    for source in payload["supplementary_full_census_pairs"]:
        identity = canonical_identity(source["instance_key"], source["words"])
        if identity in output:
            raise RuntimeError("Duplicate identity in partition source")
        output[identity] = {
            "mechanism_label": str(source["mechanism_label"]),
            "A_G": int(source["A_G"]),
        }
    return output


def loio_rows(payload: dict[str, Any]) -> dict[tuple[str, tuple[int, ...]], dict[str, Any]]:
    output = {}
    for source in payload["out_of_fold_predictions"]:
        identity = canonical_identity(source["instance_key"], source["words"])
        if identity in output:
            raise RuntimeError("Duplicate identity in LOIO source")
        output[identity] = {
            "actual": str(source["actual"]),
            "predicted": str(source["predicted"]),
            "A_G": int(source["A_G"]),
        }
    return output


def reconcile_sources(
    motif: dict[tuple[str, tuple[int, ...]], dict[str, Any]],
    partition: dict[tuple[str, tuple[int, ...]], dict[str, Any]],
    loio: dict[tuple[str, tuple[int, ...]], dict[str, Any]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if not (len(motif) == len(partition) == len(loio) == EXPECTED_RESCUES):
        raise RuntimeError("Unexpected source identity count")
    if not (set(motif) == set(partition) == set(loio)):
        raise RuntimeError("Incomplete identity join between sources")
    rows = []
    for identity in sorted(motif):
        label = motif[identity]["mechanism_label"]
        if label not in LABELS:
            raise RuntimeError("Unexpected mechanism label")
        if partition[identity]["mechanism_label"] != label or loio[identity]["actual"] != label:
            raise RuntimeError("Actual/mechanism mismatch between sources")
        if partition[identity]["A_G"] != loio[identity]["A_G"]:
            raise RuntimeError("A_G mismatch between sources")
        if loio[identity]["predicted"] not in LABELS:
            raise RuntimeError("Unexpected LOIO prediction label")
        rows.append(
            {
                "instance_key": identity[0],
                "words": list(identity[1]),
                "mechanism_label": label,
                "A_G": partition[identity]["A_G"],
                "predicted": loio[identity]["predicted"],
            }
        )
    return rows, {
        "identity_count": len(rows),
        "missing_or_duplicate_identities": 0,
        "actual_or_mechanism_mismatches": 0,
        "A_G_mismatches": 0,
        "invalid_prediction_labels": 0,
    }


def build_instances(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["instance_key"]].append(row)
    if len(groups) != EXPECTED_INSTANCES:
        raise RuntimeError("Unexpected instance count")
    distribution = Counter(map(len, groups.values()))
    if dict(distribution) != EXPECTED_MULTIPLICITIES or distribution[5] != 0:
        raise RuntimeError("Unexpected n_i distribution or n_i=5 support")
    labels = Counter(row["mechanism_label"] for row in rows)
    if labels != Counter({EXTERNAL: EXPECTED_EXTERNAL, INTERNAL: EXPECTED_INTERNAL}):
        raise RuntimeError("Unexpected mechanism totals")
    return dict(groups)


def group_code(n_i: int) -> str:
    if n_i == 1:
        return "X"
    if n_i in LOW_SIZES:
        return "Y"
    if n_i in HIGH_SIZES:
        return "Z"
    raise RuntimeError(f"Unsupported instance size: {n_i}")


def is_mixed(group: list[dict[str, Any]]) -> bool:
    return len({row["mechanism_label"] for row in group}) == 2


def instance_specs(groups: dict[str, list[dict[str, Any]]]):
    return [
        {"instance_key": key, "n_i": len(group), "stratum": group_code(len(group))}
        for key, group in sorted(groups.items())
    ]


def observed_statistic(groups: dict[str, list[dict[str, Any]]]) -> dict[str, Any]:
    mixed_y = sum(
        is_mixed(group) for group in groups.values() if len(group) in LOW_SIZES
    )
    mixed_z = sum(
        is_mixed(group) for group in groups.values() if len(group) in HIGH_SIZES
    )
    d_obs = Fraction(mixed_z, HIGH_INSTANCES) - Fraction(mixed_y, LOW_INSTANCES)
    return {"mixed_Y": mixed_y, "mixed_Z": mixed_z, "D_obs": fraction_payload(d_obs)}


def exact_dp(specs: list[dict[str, Any]]) -> dict[tuple[int, int], int]:
    states: dict[tuple[int, int, int], int] = {(0, 0, 0): 1}
    for spec in specs:
        n_i = int(spec["n_i"])
        stratum = str(spec["stratum"])
        updated: dict[tuple[int, int, int], int] = defaultdict(int)
        for (external_used, mixed_y, mixed_z), count in states.items():
            for external_here in range(n_i + 1):
                new_external = external_used + external_here
                if new_external > EXPECTED_EXTERNAL:
                    continue
                mixed = 0 < external_here < n_i
                new_y = mixed_y + int(stratum == "Y" and mixed)
                new_z = mixed_z + int(stratum == "Z" and mixed)
                updated[(new_external, new_y, new_z)] += count * math.comb(
                    n_i, external_here
                )
        states = dict(updated)
    return {
        (mixed_y, mixed_z): count
        for (external_used, mixed_y, mixed_z), count in states.items()
        if external_used == EXPECTED_EXTERNAL
    }


def exact_null_distribution(
    specs: list[dict[str, Any]], d_obs: Fraction
) -> dict[str, Any]:
    forward = exact_dp(specs)
    reverse = exact_dp(list(reversed(specs)))
    if forward != reverse:
        raise RuntimeError("Full DP map depends on instance processing order")
    denominator = math.comb(EXPECTED_RESCUES, EXPECTED_EXTERNAL)
    total = sum(forward.values())
    if total != denominator:
        raise RuntimeError("DP mass does not equal C(223,54)")

    joint_rows = []
    qualifying = []
    tail_count = 0
    for (mixed_y, mixed_z), count in sorted(forward.items()):
        d_value = Fraction(mixed_z, HIGH_INSTANCES) - Fraction(
            mixed_y, LOW_INSTANCES
        )
        mass = Fraction(count, denominator)
        joint_rows.append(
            {
                "y": mixed_y,
                "z": mixed_z,
                "count": count,
                "mass": fraction_payload(mass),
                "D": fraction_payload(d_value),
            }
        )
        if d_value >= d_obs:
            tail_count += count
            qualifying.append(
                {
                    "y": mixed_y,
                    "z": mixed_z,
                    "count": count,
                    "mass": fraction_payload(mass),
                    "D": fraction_payload(d_value),
                }
            )
    tail = Fraction(tail_count, denominator)
    return {
        "state_map_cell_count": len(forward),
        "order_invariance_failures": 0,
        "total_assignment_count": denominator,
        "summed_dp_count": total,
        "full_joint_distribution": joint_rows,
        "qualifying_pairs": qualifying,
        "tail_count": tail_count,
        "tail_mass": fraction_payload(tail),
    }


def marginal_table(groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    output = []
    for n_i in (2, 3, 4, 6, 7):
        selected = [group for group in groups.values() if len(group) == n_i]
        count = len(selected)
        mixed = sum(is_mixed(group) for group in selected)
        p_mono = Fraction(
            math.comb(EXPECTED_EXTERNAL, n_i) + math.comb(EXPECTED_INTERNAL, n_i),
            math.comb(EXPECTED_RESCUES, n_i),
        )
        expected_mono = count * p_mono
        expected_mixed = count * (1 - p_mono)
        output.append(
            {
                "n_i": n_i,
                "instance_count": count,
                "observed_mixed": mixed,
                "observed_monolabel": count - mixed,
                "null_p_monolabel": fraction_payload(p_mono),
                "null_expected_mixed": fraction_payload(expected_mixed),
                "null_expected_monolabel": fraction_payload(expected_mono),
            }
        )
    return output


def secondary_summary(groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    output = []
    for n_i in (4, 6, 7):
        selected_groups = [group for group in groups.values() if len(group) == n_i]
        if not all(is_mixed(group) for group in selected_groups):
            raise RuntimeError("A high-stratum instance is not mixed")
        rows = [row for group in selected_groups for row in group]
        labels = Counter(row["mechanism_label"] for row in rows)
        ambiguous = sum(row["A_G"] in {4, 5} for row in rows)
        errors = sum(row["predicted"] != row["mechanism_label"] for row in rows)
        output.append(
            {
                "n_i": n_i,
                "instance_count": len(selected_groups),
                "rescue_count": len(rows),
                "external_count": labels[EXTERNAL],
                "internal_count": labels[INTERNAL],
                "A_G_4_or_5_count": ambiguous,
                "A_G_4_or_5_proportion": fraction_payload(Fraction(ambiguous, len(rows))),
                "phase111_error_count": errors,
                "phase111_error_proportion": fraction_payload(Fraction(errors, len(rows))),
            }
        )
    return output


def analyze() -> tuple[dict[str, Any], dict[str, Any]]:
    payloads = {}
    source_hashes = {}
    for path in EXPECTED_JSON_HASHES:
        payloads[path], source_hashes[path.name] = read_gated_json(path)

    motif = motif_rows(payloads[MOTIF_RESULTS_PATH])
    partition = partition_rows(payloads[PARTITION_RESULTS_PATH])
    loio = loio_rows(payloads[LOIO_RESULTS_PATH])
    rows, reconciliation = reconcile_sources(motif, partition, loio)
    groups = build_instances(rows)
    specs = instance_specs(groups)
    observed = observed_statistic(groups)
    d_obs = Fraction(
        observed["D_obs"]["numerator"], observed["D_obs"]["denominator"]
    )
    null = exact_null_distribution(specs, d_obs)
    marginals = marginal_table(groups)
    expected_total_mixed = sum(
        (
            Fraction(row["null_expected_mixed"]["numerator"], row["null_expected_mixed"]["denominator"])
            for row in marginals
        ),
        Fraction(0),
    )

    results = {
        "phase": 112,
        "artifact_prefix": "phase111",
        "status": STATUS,
        "scope": {
            "outcome_data_seen_during_feature_design": True,
            "threshold_selected_after_outcome_inspection": True,
            "exact_null_model_is_descriptive_post_selection": True,
            "directional_hypothesis": False,
            "external_validation": False,
            "prospective_validation": False,
            "causal_claim": False,
            "population_generalization": False,
            "formal_null_hypothesis_test": False,
            "tail_probability_is_confirmatory_p_value": False,
            "tail_direction_selected_after_outcome_inspection": True,
            "multiple_selection_adjustment": False,
            "new_simulation_or_sweep": False,
        },
        "source_audit": {
            "reconciliation": reconciliation,
            "rescue_count": len(rows),
            "instance_count": len(groups),
            "external_count": sum(row["mechanism_label"] == EXTERNAL for row in rows),
            "internal_count": sum(row["mechanism_label"] == INTERNAL for row in rows),
            "n_i_distribution": {
                str(n_i): sum(len(group) == n_i for group in groups.values())
                for n_i in EXPECTED_MULTIPLICITIES
            },
            "n_i_5_support": 0,
            "forbidden_fields": sorted(FORBIDDEN_FIELDS),
        },
        "strata": {
            "X": {"sizes": [1], "instance_count": 56, "contributes_to_D": False, "included_in_DP": True},
            "Y": {"sizes": [2, 3], "instance_count": LOW_INSTANCES},
            "Z": {"sizes": [4, 6, 7], "instance_count": HIGH_INSTANCES},
        },
        "observed_statistic": observed,
        "marginal_strata": marginals,
        "aggregate_mixed": {
            "observed_excluding_X": sum(is_mixed(group) for group in groups.values() if len(group) != 1),
            "null_expected_excluding_X": fraction_payload(expected_total_mixed),
        },
        "exact_joint_null": null,
        "secondary_phase111_errors_by_n_i": secondary_summary(groups),
        "sources": source_hashes,
    }
    return results, source_hashes


def render_report(results: dict[str, Any]) -> str:
    observed = results["observed_statistic"]
    null = results["exact_joint_null"]
    aggregate = results["aggregate_mixed"]
    lines = [
        "# Fase 112 — Calibración combinatoria exacta posselección",
        "",
        f"**Veredicto:** `{results['status']}`",
        "",
        "## Auditoría",
        "",
        "- 223 rescates K2 en 101 instancias; 54 externos y 169 internos.",
        "- Distribución n_i: 1→56, 2→18, 3→3, 4→14, 6→4, 7→6; n_i=5 ausente.",
        "- Reconciliaciones de identidad, etiqueta y A_G entre tres fuentes: 0 discrepancias.",
        f"- Mapa conjunto exacto: {null['state_map_cell_count']} celdas; invariancia al orden confirmada.",
        "- Masa DP: C(223,54), exacta y sin pérdida.",
        "",
        "## Estratificación observada",
        "",
    ]
    for row in results["marginal_strata"]:
        lines.append(
            f"- n_i={row['n_i']}: {row['observed_mixed']}/{row['instance_count']} mixtas; "
            f"expectativa marginal nula={row['null_expected_mixed']['decimal']:.6f}."
        )
    lines.extend(
        [
            "",
            f"- Total observado fuera de X: {aggregate['observed_excluding_X']} mixtas.",
            "- Total esperado marginal fuera de X: "
            f"{aggregate['null_expected_excluding_X']['decimal']:.6f}.",
            f"- D_obs: {observed['D_obs']['decimal']:.6f}.",
            "- Masa de cola descriptiva posselección P(D≥D_obs): "
            f"{null['tail_mass']['numerator']}/{null['tail_mass']['denominator']} "
            f"= {null['tail_mass']['decimal']:.12g}.",
            "",
            "## Errores certificados de Fase 111 por n_i",
            "",
        ]
    )
    for row in results["secondary_phase111_errors_by_n_i"]:
        lines.append(
            f"- n_i={row['n_i']}: EXT/INT={row['external_count']}/{row['internal_count']}; "
            f"A_G∈{{4,5}}={row['A_G_4_or_5_count']}/{row['rescue_count']}; "
            f"errores={row['phase111_error_count']}/{row['rescue_count']}."
        )
    lines.extend(
        [
            "",
            "## Límites",
            "",
            "El estadístico, el umbral y la dirección de cola fueron seleccionados después "
            "de observar los resultados. La masa exacta es una calibración descriptiva "
            "posselección, no un p-valor confirmatorio ni un rechazo formal. No existe "
            "afirmación causal, predictiva, prospectiva o de generalización poblacional.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(results: dict[str, Any], sources: dict[str, Any]) -> None:
    atomic_write(
        RESULTS_PATH,
        json.dumps(results, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n",
    )
    atomic_write(REPORT_PATH, render_report(results).encode("utf-8"))
    runner = Path(__file__).resolve()
    manifest = {
        "phase": 112,
        "artifact_prefix": "phase111",
        "status": results["status"],
        "runner": runner.name,
        "runner_normalized_sha256": normalized_source_sha256(runner),
        "sources": sources,
        "outputs": {
            RESULTS_PATH.name: {
                "raw": raw_sha256(RESULTS_PATH),
                "canonical": canonical_sha256(results),
            },
            REPORT_PATH.name: {"raw": raw_sha256(REPORT_PATH)},
        },
    }
    atomic_write(
        MANIFEST_PATH,
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8") + b"\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    results, sources = analyze()
    if not args.check_only:
        write_outputs(results, sources)
    print(results["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
