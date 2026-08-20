from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import statistics
import struct
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"

PAIR_LEDGER_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_ledger.bin"
PAIR_MANIFEST_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_manifest.json"
PAIR_RESULTS_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_results.json"
MOTIF_RESULTS_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_results.json"
QUBO_MODELS_PATH = OUTPUT_DIR / "phase106_minimal_rescue_qubo_models.jsonl"

RESULTS_PATH = OUTPUT_DIR / "phase108_ambient_rescue_geometry_results.json"
MANIFEST_PATH = OUTPUT_DIR / "phase108_ambient_rescue_geometry_manifest.json"
REPORT_PATH = OUTPUT_DIR / "phase108_ambient_rescue_geometry_report.md"

EXPECTED_JSON_HASHES = {
    PAIR_MANIFEST_PATH: (
        "d434a20dd0c66350fadceac6ea4f6e3d73bd9769e51195083efc628ed8170057",
        "580635c42efc2bb042e539f0a1f61d6ae15693d38d77a3333041757be9257ea5",
    ),
    PAIR_RESULTS_PATH: (
        "9a5c70318085c8d6d1a7ad82a59fb631abda524926288c46cb0da30a7cd47268",
        "152003197716bff38e552b3b51754df6dbfe4c6dc9f93326c3a55de594e5a6c3",
    ),
    MOTIF_RESULTS_PATH: (
        "9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24",
        "982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353",
    ),
}
EXPECTED_LEDGER_SHA256 = "24de12594fe8b95f6e70be4278b2dfadb7f29f181aef3d7aeea41f9fbe58de52"
EXPECTED_QUBO_MODELS_SHA256 = "d6c813602e914b8863d248d47d7cecfcd498172ba2c3831441b750d5203c82ab"
EXPECTED_PAIR_RECORDS = 404_054
EXPECTED_STRATA = 142
EXPECTED_RESCUES = 319
EXPECTED_K2_MIXED_INSTANCES = 24
EXPECTED_K2I_MIXED_INSTANCES = 4

EXTERNAL = "EXTERNAL_ATTACHMENT_RESCUE"
INTERNAL = "INTERNAL_EDGE_DEPENDENT_RESCUE"
MECHANISMS = (EXTERNAL, INTERNAL)
FORBIDDEN_EXPLANATORY_FIELDS = {
    "cut_mechanisms",
    "cut_mechanism_counts",
    "external_rescue",
    "per_internal_edge_removal",
    "source_internal_edge_required",
    "full_rescue",
    "covers_all_original_cuts",
    "new_separator_count",
    "internal_edge_required",
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


def instance_key(row: dict[str, Any]) -> str:
    return "|".join(
        (
            str(row["cube_key"]),
            str(int(row["pair_index"])),
            str(int(row["period"])),
            str(row["metric"]),
        )
    )


def reconstruct_universes(
    ledger_path: Path,
    manifest: dict[str, Any],
    pair_results: dict[str, Any],
) -> tuple[dict[int, tuple[int, ...]], dict[str, Any]]:
    if raw_sha256(ledger_path) != EXPECTED_LEDGER_SHA256:
        raise RuntimeError("Pair ledger SHA-256 mismatch")
    if manifest["ledger_sha256"] != EXPECTED_LEDGER_SHA256:
        raise RuntimeError("Pair manifest ledger SHA-256 mismatch")
    if manifest["record_format"] != "<HBBHBBBB":
        raise RuntimeError("Unexpected pair ledger record format")
    record = struct.Struct(manifest["record_format"])
    if record.size != int(manifest["record_size"]):
        raise RuntimeError("Pair ledger record-size mismatch")
    record_count = int(manifest["record_count"])
    if record_count != EXPECTED_PAIR_RECORDS:
        raise RuntimeError("Unexpected pair ledger record count")
    if ledger_path.stat().st_size != record_count * record.size:
        raise RuntimeError("Pair ledger size mismatch")

    words: dict[int, set[int]] = defaultdict(set)
    counts: Counter[int] = Counter()
    with ledger_path.open("rb") as handle:
        for _ in range(record_count):
            raw = handle.read(record.size)
            if len(raw) != record.size:
                raise RuntimeError("Truncated pair ledger")
            stratum_index, left_word, right_word, *_rest = record.unpack(raw)
            if left_word >= right_word:
                raise RuntimeError("Pair ledger words are not canonical")
            words[int(stratum_index)].update((int(left_word), int(right_word)))
            counts[int(stratum_index)] += 1
        if handle.read(1):
            raise RuntimeError("Pair ledger has trailing bytes")

    strata = {int(row["stratum_index"]): row for row in pair_results["strata"]}
    if len(strata) != EXPECTED_STRATA or len(words) != EXPECTED_STRATA:
        raise RuntimeError("Unexpected stratum count")
    if set(strata) != set(words):
        raise RuntimeError("Ledger/result stratum mismatch")

    universes: dict[int, tuple[int, ...]] = {}
    for index, source in strata.items():
        universe = tuple(sorted(words[index]))
        node_count = int(source["node_count"])
        if len(universe) != node_count:
            raise RuntimeError(f"V_i/node_count mismatch at stratum {index}")
        if counts[index] != math.comb(node_count, 2):
            raise RuntimeError(f"Pair combinatorics mismatch at stratum {index}")
        universes[index] = universe
    return universes, {
        "record_count": sum(counts.values()),
        "stratum_count": len(universes),
        "node_count_mismatches": 0,
        "combination_count_mismatches": 0,
    }


def hamming_one(a: int, b: int) -> bool:
    return (int(a) ^ int(b)).bit_count() == 1


def external_degree(word: int, rescue: Iterable[int], universe: Iterable[int]) -> int:
    rescue_set = set(map(int, rescue))
    return sum(hamming_one(word, other) for other in universe if other not in rescue_set)


def k2_geometry(words: Iterable[int], universe: Iterable[int]) -> dict[str, int]:
    rescue = tuple(sorted(map(int, words)))
    if len(rescue) != 2 or not hamming_one(*rescue):
        raise RuntimeError("K2 rescue does not contain exactly one internal edge")
    degrees = tuple(external_degree(word, rescue, universe) for word in rescue)
    return {
        "S_ext": sum(degrees),
        "M_ext": min(degrees),
        "B_ext": abs(degrees[0] - degrees[1]),
        "endpoint_external_degrees": list(degrees),
    }


def k2i_geometry(words: Iterable[int], universe: Iterable[int]) -> dict[str, Any]:
    rescue = tuple(sorted(map(int, words)))
    if len(rescue) != 3:
        raise RuntimeError("K2+I rescue cardinality mismatch")
    internal_degrees = {
        word: sum(hamming_one(word, other) for other in rescue if other != word)
        for word in rescue
    }
    endpoints = sorted(word for word, degree in internal_degrees.items() if degree == 1)
    isolated = sorted(word for word, degree in internal_degrees.items() if degree == 0)
    if len(endpoints) != 2 or len(isolated) != 1:
        raise RuntimeError("K2+I roles are not uniquely identifiable")
    degrees = {word: external_degree(word, rescue, universe) for word in rescue}
    return {
        "S_ext_all": sum(degrees.values()),
        "S_ext_edge": sum(degrees[word] for word in endpoints),
        "d_ext_isolated": degrees[isolated[0]],
        "edge_endpoints": endpoints,
        "isolated_word": isolated[0],
        "external_degrees": {str(word): degrees[word] for word in rescue},
    }


def load_qubo_universes(path: Path) -> dict[str, tuple[int, ...]]:
    if raw_sha256(path) != EXPECTED_QUBO_MODELS_SHA256:
        raise RuntimeError("QUBO model SHA-256 mismatch")
    output: dict[str, tuple[int, ...]] = {}
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            model = json.loads(line)
            key = str(model["instance_key"])
            if key in output:
                raise RuntimeError("Duplicate QUBO instance key")
            output[key] = tuple(map(int, model["variables"]["x_words"]))
    return output


def enrich_rescues(
    motif_results: dict[str, Any],
    pair_results: dict[str, Any],
    universes: dict[int, tuple[int, ...]],
    qubo_universes: dict[str, tuple[int, ...]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    strata_by_natural_key: dict[tuple[str, int, int], dict[str, Any]] = {}
    for source in pair_results["strata"]:
        natural_key = (
            str(source["cube_key"]),
            int(source["pair_index"]),
            int(source["period"]),
        )
        if natural_key in strata_by_natural_key:
            raise RuntimeError("Duplicate natural stratum key")
        strata_by_natural_key[natural_key] = source
    source_rows = motif_results["atlas"]["mechanism_audits"]
    selected = [row for row in source_rows if row["motif"] in ("K2", "K2+I")]
    if len(selected) != EXPECTED_RESCUES:
        raise RuntimeError("Unexpected K2/K2+I rescue count")

    enriched: list[dict[str, Any]] = []
    cross_checks: set[str] = set()
    identities: set[tuple[str, tuple[int, ...]]] = set()
    for source in selected:
        row = dict(source)
        key = instance_key(row)
        natural_key = (
            str(row["cube_key"]),
            int(row["pair_index"]),
            int(row["period"]),
        )
        try:
            origin = strata_by_natural_key[natural_key]
        except KeyError as exc:
            raise RuntimeError("Missing natural-key source stratum") from exc
        pair_stratum_index = int(origin["stratum_index"])
        universe = universes[pair_stratum_index]
        if key not in qubo_universes:
            raise RuntimeError("Missing QUBO universe cross-check")
        if universe != qubo_universes[key]:
            raise RuntimeError("V_i/QUBO x_words mismatch")
        cross_checks.add(key)

        label = str(row["mechanism_label"])
        expected_label = INTERNAL if row["internal_edge_required"] else EXTERNAL
        if label != expected_label or label not in MECHANISMS:
            raise RuntimeError("Mechanism label mismatch")
        words = tuple(sorted(map(int, row["words"])))
        identity = (key, words)
        if identity in identities:
            raise RuntimeError("Duplicate rescue within instance")
        identities.add(identity)
        if not set(words).issubset(universe):
            raise RuntimeError("Rescue is outside V_i")

        geometry = (
            k2_geometry(words, universe)
            if row["motif"] == "K2"
            else k2i_geometry(words, universe)
        )
        reversed_geometry = (
            k2_geometry(reversed(words), universe)
            if row["motif"] == "K2"
            else k2i_geometry(reversed(words), universe)
        )
        if geometry != reversed_geometry:
            raise RuntimeError("Geometry is not order invariant")

        enriched.append(
            {
                "instance_key": key,
                "motif_source_stratum_index": int(row["stratum_index"]),
                "pair_universe_stratum_index": pair_stratum_index,
                "cube_key": row["cube_key"],
                "pair_index": int(row["pair_index"]),
                "period": int(row["period"]),
                "rule": int(row["rule"]),
                "metric": str(row["metric"]),
                "node_count": len(universe),
                "motif": str(row["motif"]),
                "words": list(words),
                "mechanism_label": label,
                "geometry": geometry,
            }
        )
    return enriched, {
        "rescue_count": len(enriched),
        "qubo_universe_cross_checked_instance_count": len(cross_checks),
        "universe_mismatches": 0,
        "order_invariance_failures": 0,
    }


def summarize_values(values: Iterable[float]) -> dict[str, Any]:
    ordered = sorted(values)
    if not ordered:
        return {"count": 0, "min": None, "median": None, "max": None, "mean": None}
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": statistics.median(ordered),
        "max": ordered[-1],
        "mean": statistics.fmean(ordered),
    }


def histogram(values: Iterable[int]) -> dict[str, int]:
    counts = Counter(map(int, values))
    return {str(value): counts[value] for value in sorted(counts)}


def leave_one_out_mean_range(values: list[float]) -> dict[str, float]:
    if len(values) < 2:
        raise RuntimeError("Leave-one-out stability requires at least two instances")
    total = sum(values)
    estimates = [(total - value) / (len(values) - 1) for value in values]
    return {"min": min(estimates), "max": max(estimates)}


def mixed_instance_rows(
    rows: list[dict[str, Any]], motif: str
) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        if row["motif"] == motif:
            grouped[row["instance_key"]].append(row)
    return {
        key: group
        for key, group in grouped.items()
        if {row["mechanism_label"] for row in group} == set(MECHANISMS)
    }


def balanced_k2_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    mixed = mixed_instance_rows(rows, "K2")
    if len(mixed) != EXPECTED_K2_MIXED_INSTANCES:
        raise RuntimeError("Unexpected mixed K2 instance count")
    feature_names = ("S_ext", "M_ext", "B_ext")
    per_instance: list[dict[str, Any]] = []
    feature_deltas: dict[str, list[float]] = {name: [] for name in feature_names}
    for key in sorted(mixed):
        group = mixed[key]
        entry: dict[str, Any] = {
            "instance_key": key,
            "external_count": sum(row["mechanism_label"] == EXTERNAL for row in group),
            "internal_count": sum(row["mechanism_label"] == INTERNAL for row in group),
            "deltas": {},
        }
        for name in feature_names:
            external_values = [
                row["geometry"][name]
                for row in group
                if row["mechanism_label"] == EXTERNAL
            ]
            internal_values = [
                row["geometry"][name]
                for row in group
                if row["mechanism_label"] == INTERNAL
            ]
            delta = statistics.fmean(external_values) - statistics.fmean(internal_values)
            entry["deltas"][name] = delta
            feature_deltas[name].append(delta)
        per_instance.append(entry)

    summaries: dict[str, Any] = {}
    k2_rows = [row for row in rows if row["motif"] == "K2"]
    for name in feature_names:
        deltas = feature_deltas[name]
        summaries[name] = {
            "role": "primary" if name == "S_ext" else "secondary",
            "delta_definition": "mean_external_minus_mean_internal",
            "instance_balanced": True,
            "delta_summary": summarize_values(deltas),
            "delta_signs": {
                "positive": sum(value > 0 for value in deltas),
                "zero": sum(value == 0 for value in deltas),
                "negative": sum(value < 0 for value in deltas),
            },
            "leave_one_instance_out_mean_range": leave_one_out_mean_range(deltas),
            "full_census_by_mechanism": {
                mechanism: {
                    "summary": summarize_values(
                        row["geometry"][name]
                        for row in k2_rows
                        if row["mechanism_label"] == mechanism
                    ),
                    "histogram": histogram(
                        row["geometry"][name]
                        for row in k2_rows
                        if row["mechanism_label"] == mechanism
                    ),
                }
                for mechanism in MECHANISMS
            },
        }
    return {
        "motif": "K2",
        "mixed_instance_count": len(mixed),
        "per_instance": per_instance,
        "features": summaries,
    }


def descriptive_k2i_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    mixed = mixed_instance_rows(rows, "K2+I")
    if len(mixed) != EXPECTED_K2I_MIXED_INSTANCES:
        raise RuntimeError("Unexpected mixed K2+I instance count")
    feature_names = ("S_ext_all", "S_ext_edge", "d_ext_isolated")
    mixed_rows = [row for group in mixed.values() for row in group]
    return {
        "motif": "K2+I",
        "interpretation": "descriptive_only",
        "mixed_instance_count": len(mixed),
        "mixed_rescue_count": len(mixed_rows),
        "features": {
            name: {
                mechanism: {
                    "summary": summarize_values(
                        row["geometry"][name]
                        for row in mixed_rows
                        if row["mechanism_label"] == mechanism
                    ),
                    "histogram": histogram(
                        row["geometry"][name]
                        for row in mixed_rows
                        if row["mechanism_label"] == mechanism
                    ),
                }
                for mechanism in MECHANISMS
            }
            for name in feature_names
        },
    }


def between_instance_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for motif in ("K2", "K2+I"):
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            if row["motif"] == motif:
                grouped[row["instance_key"]].append(row)
        instance_rows: list[dict[str, Any]] = []
        for key in sorted(grouped):
            group = grouped[key]
            external_count = sum(row["mechanism_label"] == EXTERNAL for row in group)
            internal_count = sum(row["mechanism_label"] == INTERNAL for row in group)
            fixed_fields = ("node_count", "rule", "metric", "period")
            for field in fixed_fields:
                if len({row[field] for row in group}) != 1:
                    raise RuntimeError(f"Instance field is not fixed: {field}")
            instance_rows.append(
                {
                    "instance_key": key,
                    "node_count": group[0]["node_count"],
                    "rule": group[0]["rule"],
                    "metric": group[0]["metric"],
                    "period_provenance_only": group[0]["period"],
                    "external_count": external_count,
                    "internal_count": internal_count,
                    "total": len(group),
                    "internal_proportion": internal_count / len(group),
                }
            )
        strata: list[dict[str, Any]] = []
        for rule in sorted({row["rule"] for row in instance_rows}):
            for metric in ("kappa", "lambda"):
                selected = [
                    row for row in instance_rows if row["rule"] == rule and row["metric"] == metric
                ]
                if not selected:
                    continue
                strata.append(
                    {
                        "rule": rule,
                        "metric": metric,
                        "instance_count": len(selected),
                        "node_count": summarize_values(row["node_count"] for row in selected),
                        "instance_internal_proportion": summarize_values(
                            row["internal_proportion"] for row in selected
                        ),
                        "rescue_counts": {
                            EXTERNAL: sum(row["external_count"] for row in selected),
                            INTERNAL: sum(row["internal_count"] for row in selected),
                        },
                    }
                )
        output[motif] = {
            "unit": "metric_specific_instance",
            "period_role": "provenance_only_not_a_covariate",
            "instance_count": len(instance_rows),
            "instances": instance_rows,
            "by_rule_metric": strata,
        }
    return output


def analyze() -> tuple[dict[str, Any], dict[str, Any]]:
    pair_manifest, pair_manifest_hashes = read_gated_json(PAIR_MANIFEST_PATH)
    pair_results, pair_results_hashes = read_gated_json(PAIR_RESULTS_PATH)
    motif_results, motif_results_hashes = read_gated_json(MOTIF_RESULTS_PATH)
    universes, universe_audit = reconstruct_universes(
        PAIR_LEDGER_PATH, pair_manifest, pair_results
    )
    qubo_universes = load_qubo_universes(QUBO_MODELS_PATH)
    rows, rescue_audit = enrich_rescues(
        motif_results, pair_results, universes, qubo_universes
    )

    results = {
        "phase": 109,
        "artifact_prefix": "phase108",
        "status": "AMBIENT_GEOMETRY_CONDITIONED_RESCUE_ANALYSIS_VERIFIED",
        "scope": {
            "interpretation": "exact_census_characterization",
            "causal_claim": False,
            "population_generalization": False,
            "period_used_as_covariate": False,
            "qubo_coefficients_analyzed": False,
            "new_simulation_or_sweep": False,
        },
        "source_audit": {
            "universe_reconstruction": universe_audit,
            "rescues": rescue_audit,
            "forbidden_explanatory_fields": sorted(FORBIDDEN_EXPLANATORY_FIELDS),
        },
        "primary_k2_within_instance": balanced_k2_analysis(rows),
        "descriptive_k2i": descriptive_k2i_analysis(rows),
        "secondary_between_instance": between_instance_analysis(rows),
        "rescue_geometry": rows,
        "sources": {
            PAIR_LEDGER_PATH.name: {"sha256": EXPECTED_LEDGER_SHA256},
            PAIR_MANIFEST_PATH.name: pair_manifest_hashes,
            PAIR_RESULTS_PATH.name: pair_results_hashes,
            MOTIF_RESULTS_PATH.name: motif_results_hashes,
            QUBO_MODELS_PATH.name: {"sha256": EXPECTED_QUBO_MODELS_SHA256},
        },
    }
    return results, results["sources"]


def render_report(results: dict[str, Any]) -> str:
    primary = results["primary_k2_within_instance"]
    main = primary["features"]["S_ext"]
    delta = main["delta_summary"]
    signs = main["delta_signs"]
    stability = main["leave_one_instance_out_mean_range"]
    k2i = results["descriptive_k2i"]
    lines = [
        "# Fase 109 — Geometría ambiental de rescates",
        "",
        f"**Veredicto:** `{results['status']}`",
        "",
        "## Auditoría de fuentes",
        "",
        "- Pares del ledger: 404.054",
        "- Strata reconstruidos: 142",
        "- Rescates K2/K2+I: 319",
        "- Discrepancias `V_i` frente a `node_count`: 0",
        "- Discrepancias `V_i` frente a `x_words`: 0",
        "- Fallos de invariancia al orden: 0",
        "",
        "## Resultado principal K2",
        "",
        f"- Instancias mixtas: {primary['mixed_instance_count']}",
        "- Variable principal: `S_ext`.",
        f"- Media de Delta_i: {delta['mean']:.6f}",
        f"- Mediana de Delta_i: {delta['median']:.6f}",
        f"- Rango de Delta_i: [{delta['min']:.6f}, {delta['max']:.6f}]",
        "- Signos de Delta_i: "
        f"{signs['positive']} positivos, {signs['zero']} nulos, "
        f"{signs['negative']} negativos.",
        "- Estabilidad leave-one-instance-out de la media: "
        f"[{stability['min']:.6f}, {stability['max']:.6f}]",
        "",
        "### Distribución completa de S_ext en K2",
        "",
    ]
    for mechanism in MECHANISMS:
        census = main["full_census_by_mechanism"][mechanism]["summary"]
        lines.append(
            f"- {mechanism}: n={census['count']}, media={census['mean']:.6f}, "
            f"mediana={census['median']:.6f}, rango=[{census['min']}, {census['max']}]."
        )
    lines.extend(["", "### Variables secundarias K2", ""])
    for name in ("M_ext", "B_ext"):
        feature = primary["features"][name]
        feature_delta = feature["delta_summary"]
        feature_signs = feature["delta_signs"]
        lines.append(
            f"- `{name}`: media Delta_i={feature_delta['mean']:.6f}, "
            f"mediana={feature_delta['median']:.6f}; "
            f"{feature_signs['positive']} positivos, {feature_signs['zero']} nulos, "
            f"{feature_signs['negative']} negativos."
        )
    lines.extend(
        [
        "",
        "## K2+I descriptivo",
        "",
        f"- Instancias mixtas: {k2i['mixed_instance_count']}",
        f"- Rescates en esas instancias: {k2i['mixed_rescue_count']}",
        "- Se reportan por separado `S_ext_all`, `S_ext_edge` y "
        "`d_ext_isolated`; no sostienen inferencia propia.",
        "",
        "| Variable | Mecanismo | n | Media | Mediana | Rango |",
        "|---|---|---:|---:|---:|---|",
        ]
    )
    for name in ("S_ext_all", "S_ext_edge", "d_ext_isolated"):
        for mechanism in MECHANISMS:
            summary = k2i["features"][name][mechanism]["summary"]
            lines.append(
                f"| {name} | {mechanism} | {summary['count']} | "
                f"{summary['mean']:.6f} | {summary['median']:.6f} | "
                f"[{summary['min']}, {summary['max']}] |"
            )
    lines.extend(
        [
        "",
        "## Descripción entre instancias",
        "",
        "`period` se conserva únicamente como procedencia y no se usa como covariable.",
        "",
        "| Motivo | Regla | Métrica | Instancias | node_count medio | "
        "Proporción interna media por instancia | Externos | Internos |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
        ]
    )
    for motif in ("K2", "K2+I"):
        for stratum in results["secondary_between_instance"][motif]["by_rule_metric"]:
            lines.append(
                f"| {motif} | {stratum['rule']} | {stratum['metric']} | "
                f"{stratum['instance_count']} | {stratum['node_count']['mean']:.6f} | "
                f"{stratum['instance_internal_proportion']['mean']:.6f} | "
                f"{stratum['rescue_counts'][EXTERNAL]} | "
                f"{stratum['rescue_counts'][INTERNAL]} |"
            )
    lines.extend(
        [
        "",
        "## Límites",
        "",
        "El análisis caracteriza el censo certificado. No separa un efecto de "
        "periodo frente a `node_count`, no formula causalidad y no generaliza "
        "fuera de los datos. Los modelos QUBO se usaron únicamente para "
        "comprobar `x_words`; no se analizaron sus coeficientes.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(results: dict[str, Any], sources: dict[str, Any]) -> None:
    results_bytes = json.dumps(
        results, indent=2, sort_keys=True, ensure_ascii=False
    ).encode("utf-8") + b"\n"
    report_bytes = render_report(results).encode("utf-8")
    atomic_write(RESULTS_PATH, results_bytes)
    atomic_write(REPORT_PATH, report_bytes)
    script_path = Path(__file__).resolve()
    manifest = {
        "phase": 109,
        "artifact_prefix": "phase108",
        "status": results["status"],
        "runner": script_path.name,
        "runner_normalized_sha256": normalized_source_sha256(script_path),
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
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        + b"\n",
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
