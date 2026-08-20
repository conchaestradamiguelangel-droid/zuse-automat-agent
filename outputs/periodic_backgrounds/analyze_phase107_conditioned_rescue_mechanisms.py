from __future__ import annotations

import argparse
import hashlib
import json
import os
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"

MOTIF_RESULTS_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_results.json"
MOTIF_MANIFEST_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_manifest.json"
SOURCE_RESULTS = {
    2: OUTPUT_DIR / "phase102_pairwise_synergy_results.json",
    3: OUTPUT_DIR / "phase103_triple_synergy_results.json",
    4: OUTPUT_DIR / "phase104_quadruple_synergy_results.json",
}
RESULTS_PATH = OUTPUT_DIR / "phase107_conditioned_rescue_mechanism_results.json"
MANIFEST_PATH = OUTPUT_DIR / "phase107_conditioned_rescue_mechanism_manifest.json"
REPORT_PATH = OUTPUT_DIR / "phase107_conditioned_rescue_mechanism_report.md"

EXPECTED_HASHES = {
    MOTIF_RESULTS_PATH: (
        "9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24",
        "982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353",
    ),
    MOTIF_MANIFEST_PATH: (
        "d092aa050942967b4da15651841e20a4d6521f57a209f676695c17a9c5d4bdc2",
        "45135b64e6936865298a203d03493aeffe8911b50b564af8a9e6d886bc14ba6c",
    ),
    SOURCE_RESULTS[2]: (
        "9a5c70318085c8d6d1a7ad82a59fb631abda524926288c46cb0da30a7cd47268",
        "152003197716bff38e552b3b51754df6dbfe4c6dc9f93326c3a55de594e5a6c3",
    ),
    SOURCE_RESULTS[3]: (
        "7487631d098876d51c24eaba75c30dfa693341833f8c85b8170a75ff647d0200",
        "ce00fc3085c7f19f0193d2d19939b6fa0e196cb8d26bcfc0c189319e4ae667ce",
    ),
    SOURCE_RESULTS[4]: (
        "35c83d1bd7be565d9ebb61cafc6b618ce9efdbfb1799bbd72061f08bd9d5f28c",
        "37e9594fb0029d19a4926ac44c0e518ddaf84cf896f784795ca4b734b8d16bf1",
    ),
}

MOTIF_CATALOG = {
    "2I": {"cardinality": 2, "internal_edge_count": 0},
    "K2": {"cardinality": 2, "internal_edge_count": 1},
    "3I": {"cardinality": 3, "internal_edge_count": 0},
    "K2+I": {"cardinality": 3, "internal_edge_count": 1},
    "P3": {"cardinality": 3, "internal_edge_count": 2},
    "4I": {"cardinality": 4, "internal_edge_count": 0},
    "K2+2I": {"cardinality": 4, "internal_edge_count": 1},
    "2K2": {"cardinality": 4, "internal_edge_count": 2},
    "P3+I": {"cardinality": 4, "internal_edge_count": 2},
    "P4": {"cardinality": 4, "internal_edge_count": 3},
    "K1_3": {"cardinality": 4, "internal_edge_count": 3},
    "C4": {"cardinality": 4, "internal_edge_count": 4},
}
METRICS = ("kappa", "lambda")
EXTERNAL = "EXTERNAL_ATTACHMENT_RESCUE"
INTERNAL = "INTERNAL_EDGE_DEPENDENT_RESCUE"
MECHANISMS = (EXTERNAL, INTERNAL)
CUT_MECHANISMS = (
    "INDIVIDUAL",
    "DISTRIBUTED_EXTERNAL",
    "INTERNAL_EDGE_ENABLED",
)
EXPECTED_RESCUES = 1_476
EXPECTED_INSTANCES = 265


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
    expected_raw, expected_canonical = EXPECTED_HASHES[path]
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


def source_index(
    source_results: dict[int, dict[str, Any]],
) -> dict[int, dict[int, dict[str, Any]]]:
    indexes: dict[int, dict[int, dict[str, Any]]] = {}
    for cardinality, results in source_results.items():
        rows = results["strata"]
        index = {int(row["stratum_index"]): row for row in rows}
        if len(index) != len(rows):
            raise RuntimeError(f"Duplicate source stratum for cardinality {cardinality}")
        indexes[cardinality] = index
    return indexes


def enrich_audits(
    audits: Iterable[dict[str, Any]],
    indexes: dict[int, dict[int, dict[str, Any]]],
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for source in audits:
        row = dict(source)
        motif = str(row["motif"])
        if motif not in MOTIF_CATALOG:
            raise RuntimeError(f"Unknown motif: {motif}")
        cardinality = int(row["cardinality"])
        if cardinality != MOTIF_CATALOG[motif]["cardinality"]:
            raise RuntimeError(f"Motif/cardinality mismatch: {motif}")
        label = str(row["mechanism_label"])
        required = bool(row["internal_edge_required"])
        expected_label = INTERNAL if required else EXTERNAL
        if label != expected_label:
            raise RuntimeError("mechanism_label/internal_edge_required mismatch")
        if label not in MECHANISMS:
            raise RuntimeError(f"Unknown mechanism label: {label}")
        unknown_cuts = set(row["cut_mechanisms"]) - set(CUT_MECHANISMS)
        if unknown_cuts:
            raise RuntimeError(f"Unknown cut mechanisms: {sorted(unknown_cuts)}")

        stratum_index = int(row["stratum_index"])
        try:
            origin = indexes[cardinality][stratum_index]
        except KeyError as exc:
            raise RuntimeError("Missing source stratum") from exc
        for field in ("cube_key", "pair_index", "period"):
            if origin[field] != row[field]:
                raise RuntimeError(f"Source join mismatch: {field}")
        node_count = int(origin["node_count"])
        if node_count <= 0:
            raise RuntimeError("Invalid node_count")
        row["node_count"] = node_count
        row["instance_key"] = instance_key(row)
        enriched.append(row)
    return enriched


def mechanism_counts(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(row["mechanism_label"]) for row in rows)
    return {label: int(counts[label]) for label in MECHANISMS}


def cell_classification(
    motif: str, external_count: int, internal_count: int
) -> str:
    total = external_count + internal_count
    if total == 0:
        return "ZERO_OBSERVED"
    if MOTIF_CATALOG[motif]["internal_edge_count"] == 0:
        if internal_count:
            raise RuntimeError("Edgeless motif has an internal-edge-dependent rescue")
        return "LOGICALLY_FORCED"
    if external_count == 0 or internal_count == 0:
        return "OBSERVED_COMPLETE_SEPARATION"
    return "EMPIRICALLY_VARIABLE"


def proportion(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def summarize_values(values: Iterable[int]) -> dict[str, int | float | None]:
    ordered = sorted(map(int, values))
    if not ordered:
        return {"count": 0, "min": None, "median": None, "max": None, "mean": None}
    return {
        "count": len(ordered),
        "min": ordered[0],
        "median": statistics.median(ordered),
        "max": ordered[-1],
        "mean": statistics.fmean(ordered),
    }


def odds_ratio(table: dict[str, dict[str, int]]) -> dict[str, float | bool]:
    # Rows are metric; columns are mechanism. The ratio is lambda vs kappa.
    a = table["lambda"][INTERNAL]
    b = table["lambda"][EXTERNAL]
    c = table["kappa"][INTERNAL]
    d = table["kappa"][EXTERNAL]
    corrected = 0 in (a, b, c, d)
    offset = 0.5 if corrected else 0.0
    value = ((a + offset) * (d + offset)) / ((b + offset) * (c + offset))
    return {"lambda_vs_kappa": value, "haldane_anscombe_corrected": corrected}


def motif_table(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for motif, metadata in MOTIF_CATALOG.items():
        motif_rows = [row for row in rows if row["motif"] == motif]
        counts = mechanism_counts(motif_rows)
        total = len(motif_rows)
        by_metric: dict[str, Any] = {}
        for metric in METRICS:
            selected = [row for row in motif_rows if row["metric"] == metric]
            metric_counts = mechanism_counts(selected)
            by_metric[metric] = {
                "total": len(selected),
                "mechanism_counts": metric_counts,
                "internal_proportion": proportion(metric_counts[INTERNAL], len(selected)),
                "cell_classification": cell_classification(
                    motif, metric_counts[EXTERNAL], metric_counts[INTERNAL]
                ),
            }
        output.append(
            {
                "motif": motif,
                **metadata,
                "total": total,
                "mechanism_counts": counts,
                "internal_proportion": proportion(counts[INTERNAL], total),
                "cell_classification": cell_classification(
                    motif, counts[EXTERNAL], counts[INTERNAL]
                ),
                "by_metric": by_metric,
            }
        )
    return output


def variable_strata(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for motif in ("K2", "K2+I"):
        selected = [row for row in rows if row["motif"] == motif]
        table: dict[str, dict[str, int]] = {}
        metric_summaries: dict[str, Any] = {}
        for metric in METRICS:
            metric_rows = [row for row in selected if row["metric"] == metric]
            counts = mechanism_counts(metric_rows)
            table[metric] = counts
            metric_summaries[metric] = {
                "total": len(metric_rows),
                "mechanism_counts": counts,
                "internal_proportion": proportion(counts[INTERNAL], len(metric_rows)),
                "instance_count": len({row["instance_key"] for row in metric_rows}),
            }
        node_count_by_mechanism = {
            label: summarize_values(
                row["node_count"] for row in selected if row["mechanism_label"] == label
            )
            for label in MECHANISMS
        }
        output[motif] = {
            "cardinality": MOTIF_CATALOG[motif]["cardinality"],
            "total": len(selected),
            "instance_count": len({row["instance_key"] for row in selected}),
            "by_metric": metric_summaries,
            "lambda_minus_kappa_internal_proportion": (
                metric_summaries["lambda"]["internal_proportion"]
                - metric_summaries["kappa"]["internal_proportion"]
            ),
            "odds_ratio": odds_ratio(table),
            "node_count_by_mechanism": node_count_by_mechanism,
        }
    return output


def multiplicity_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["instance_key"] for row in rows)
    distribution = Counter(counts.values())
    return {
        "instance_count": len(counts),
        "rescues_per_instance": summarize_values(counts.values()),
        "distribution": {str(k): distribution[k] for k in sorted(distribution)},
    }


def cut_analysis(rows: list[dict[str, Any]]) -> dict[str, Any]:
    overall = Counter()
    nested: dict[str, Any] = {}
    cuts_per_rescue: list[int] = []
    mixed = 0
    for row in rows:
        cuts = list(map(str, row["cut_mechanisms"]))
        cuts_per_rescue.append(len(cuts))
        overall.update(cuts)
        mixed += int(len(set(cuts)) >= 2)
        key = (str(row["motif"]), str(row["metric"]), str(row["mechanism_label"]))
        if key not in nested:
            nested[key] = Counter()
        nested[key].update(cuts)
    nested_rows = [
        {
            "motif": key[0],
            "metric": key[1],
            "mechanism_label": key[2],
            "cut_counts": {category: int(nested[key][category]) for category in CUT_MECHANISMS},
        }
        for key in sorted(nested)
    ]
    return {
        "unit": "rescue_x_critical_cut",
        "cut_count": sum(overall.values()),
        "cut_counts": {category: int(overall[category]) for category in CUT_MECHANISMS},
        "rescues_with_multiple_cut_categories": mixed,
        "cuts_per_rescue": summarize_values(cuts_per_rescue),
        "by_motif_metric_mechanism": nested_rows,
    }


def analyze() -> tuple[dict[str, Any], dict[str, dict[str, str]]]:
    motif_results, motif_hashes = read_gated_json(MOTIF_RESULTS_PATH)
    _motif_manifest, manifest_hashes = read_gated_json(MOTIF_MANIFEST_PATH)
    source_results: dict[int, dict[str, Any]] = {}
    source_hashes: dict[str, dict[str, str]] = {
        MOTIF_RESULTS_PATH.name: motif_hashes,
        MOTIF_MANIFEST_PATH.name: manifest_hashes,
    }
    for cardinality, path in SOURCE_RESULTS.items():
        source_results[cardinality], hashes = read_gated_json(path)
        source_hashes[path.name] = hashes

    audits = motif_results["atlas"]["mechanism_audits"]
    rows = enrich_audits(audits, source_index(source_results))
    if len(rows) != EXPECTED_RESCUES:
        raise RuntimeError(f"Expected {EXPECTED_RESCUES} rescues, found {len(rows)}")
    instances = {row["instance_key"] for row in rows}
    if len(instances) != EXPECTED_INSTANCES:
        raise RuntimeError(f"Expected {EXPECTED_INSTANCES} instances, found {len(instances)}")

    catalog = motif_table(rows)
    absent = [row["motif"] for row in catalog if row["total"] == 0]
    if absent != ["4I", "K1_3", "C4"]:
        raise RuntimeError(f"Unexpected zero-observed motif set: {absent}")

    primary_counts = mechanism_counts(rows)
    results = {
        "phase": 108,
        "artifact_prefix": "phase107",
        "status": "CONDITIONED_MINIMAL_RESCUE_MECHANISM_ATLAS_VERIFIED",
        "scope": {
            "interpretation": "exact_census_of_certified_rescues",
            "causal_claim": False,
            "population_generalization": False,
            "quantum_hardware_used": False,
            "qubo_models_used_as_analytic_source": False,
        },
        "primary": {
            "unit": "minimal_rescue",
            "rescue_count": len(rows),
            "instance_count": len(instances),
            "mechanism_counts": primary_counts,
            "mechanism_label_matches_internal_edge_required": True,
            "motif_catalog": catalog,
            "zero_observed_motifs": absent,
            "empirically_variable_motifs": ["K2", "K2+I"],
            "variable_strata": variable_strata(rows),
            "instance_multiplicity": multiplicity_summary(rows),
        },
        "secondary_cut_analysis": cut_analysis(rows),
        "sources": source_hashes,
    }

    if sum(primary_counts.values()) != len(rows):
        raise RuntimeError("Primary mechanism counts do not reconcile")
    if results["secondary_cut_analysis"]["cut_count"] != sum(
        len(row["cut_mechanisms"]) for row in rows
    ):
        raise RuntimeError("Cut counts do not reconcile")
    return results, source_hashes


def render_report(results: dict[str, Any]) -> str:
    primary = results["primary"]
    format_int = lambda value: f"{value:,}".replace(",", ".")
    lines = [
        "# Fase 108 — Atlas condicionado de mecanismos de rescate",
        "",
        f"**Veredicto:** `{results['status']}`",
        "",
        f"- Rescates certificados: {format_int(primary['rescue_count'])}",
        f"- Instancias: {format_int(primary['instance_count'])}",
        f"- Mecanismo externo: {format_int(primary['mechanism_counts'][EXTERNAL])}",
        f"- Dependencia de arista interna: {format_int(primary['mechanism_counts'][INTERNAL])}",
        "- Discrepancias entre `mechanism_label` e `internal_edge_required`: 0",
        "",
        "## Catálogo exacto",
        "",
        "| Motivo | n | Aristas | Externo | Interno | Clasificación |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for row in primary["motif_catalog"]:
        lines.append(
            "| {motif} | {cardinality} | {internal_edge_count} | {external} | "
            "{internal} | {classification} |".format(
                motif=row["motif"],
                cardinality=row["cardinality"],
                internal_edge_count=row["internal_edge_count"],
                external=row["mechanism_counts"][EXTERNAL],
                internal=row["mechanism_counts"][INTERNAL],
                classification=row["cell_classification"],
            )
        )
    lines.extend(["", "## Estratos con variación empírica", ""])
    for motif, summary in primary["variable_strata"].items():
        lines.append(f"### {motif}")
        lines.append("")
        for metric in METRICS:
            cell = summary["by_metric"][metric]
            lines.append(
                f"- {metric}: {cell['mechanism_counts'][INTERNAL]}/{cell['total']} "
                f"internos ({cell['internal_proportion']:.6f}); "
                f"{cell['instance_count']} instancias."
            )
        lines.append(
            "- Diferencia de proporciones lambda−kappa: "
            f"{summary['lambda_minus_kappa_internal_proportion']:.6f}."
        )
        lines.append(
            "- Odds ratio lambda/kappa: "
            f"{summary['odds_ratio']['lambda_vs_kappa']:.6f}."
        )
        for mechanism in MECHANISMS:
            node_summary = summary["node_count_by_mechanism"][mechanism]
            lines.append(
                f"- `node_count`, {mechanism}: n={node_summary['count']}, "
                f"mín={node_summary['min']}, mediana={node_summary['median']}, "
                f"máx={node_summary['max']}, media={node_summary['mean']:.6f}."
            )
        lines.append("")
    cuts = results["secondary_cut_analysis"]
    lines.extend(
        [
            "## Análisis secundario de cortes",
            "",
            f"- Cortes críticos: {format_int(cuts['cut_count'])}",
            f"- `INDIVIDUAL`: {format_int(cuts['cut_counts']['INDIVIDUAL'])}",
            "- `DISTRIBUTED_EXTERNAL`: "
            f"{format_int(cuts['cut_counts']['DISTRIBUTED_EXTERNAL'])}",
            "- `INTERNAL_EDGE_ENABLED`: "
            f"{format_int(cuts['cut_counts']['INTERNAL_EDGE_ENABLED'])}",
            "- Rescates con varias categorías de corte: "
            f"{format_int(cuts['rescues_with_multiple_cut_categories'])}",
            "",
            "## Límite de interpretación",
            "",
            "Los ceros estructurales no se interpretan como hallazgos estadísticos. "
            "Las diferencias son descriptivas del censo certificado y no implican "
            "causalidad ni generalización poblacional. No se usaron modelos QUBO, "
            "solvers ni hardware cuántico.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(results: dict[str, Any], source_hashes: dict[str, dict[str, str]]) -> None:
    results_bytes = json.dumps(
        results, indent=2, sort_keys=True, ensure_ascii=False
    ).encode("utf-8") + b"\n"
    report_bytes = render_report(results).encode("utf-8")
    atomic_write(RESULTS_PATH, results_bytes)
    atomic_write(REPORT_PATH, report_bytes)
    script_path = Path(__file__).resolve()
    manifest = {
        "phase": 108,
        "artifact_prefix": "phase107",
        "status": results["status"],
        "runner": script_path.name,
        "runner_normalized_sha256": normalized_source_sha256(script_path),
        "sources": source_hashes,
        "outputs": {
            RESULTS_PATH.name: {
                "raw": raw_sha256(RESULTS_PATH),
                "canonical": canonical_sha256(results),
            },
            REPORT_PATH.name: {"raw": raw_sha256(REPORT_PATH)},
        },
    }
    manifest_bytes = json.dumps(
        manifest, indent=2, sort_keys=True, ensure_ascii=False
    ).encode("utf-8") + b"\n"
    atomic_write(MANIFEST_PATH, manifest_bytes)


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
