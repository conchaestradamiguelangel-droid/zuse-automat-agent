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

PHASE94_PATH = OUTPUT_DIR / "phase94_hypercube_completion_results.json"
PHASE95_PATH = OUTPUT_DIR / "phase95_fragment_bridge_results.json"
PHASE96_PATH = OUTPUT_DIR / "phase96_bridge_robustness_results.json"
PHASE96_SCRIPT_PATH = OUTPUT_DIR / "analyze_phase96_bridge_robustness.py"
PAIR_LEDGER_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_ledger.bin"
PAIR_MANIFEST_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_manifest.json"
PAIR_RESULTS_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_results.json"
MOTIF_RESULTS_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_results.json"
PHASE109_RESULTS_PATH = OUTPUT_DIR / "phase108_ambient_rescue_geometry_results.json"

RESULTS_PATH = OUTPUT_DIR / "phase109_fixed_budget_hamming_partition_results.json"
MANIFEST_PATH = OUTPUT_DIR / "phase109_fixed_budget_hamming_partition_manifest.json"
REPORT_PATH = OUTPUT_DIR / "phase109_fixed_budget_hamming_partition_report.md"

EXPECTED_JSON_HASHES = {
    PHASE94_PATH: (
        "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3",
        "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429",
    ),
    PHASE95_PATH: (
        "cbd414180e89658b3e20c73559dbcb490b2bca845a1165f3f6a8e36f25c2e823",
        "5c43278492fa09f9367fa971e06d0a7b3e2b99e295a63279721bc78a4946f825",
    ),
    PHASE96_PATH: (
        "3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858",
        "85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b",
    ),
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
    PHASE109_RESULTS_PATH: (
        "02c858e4b8a801e39bec9512a54e317f0dfdd8c43cbe02ee5342c09442cfdae9",
        "b479df629574d25d0655b3524962846de410b5382cb1b9c26b400117ac2ca1c0",
    ),
}
EXPECTED_PAIR_LEDGER_SHA256 = "24de12594fe8b95f6e70be4278b2dfadb7f29f181aef3d7aeea41f9fbe58de52"
EXPECTED_PHASE96_SCRIPT_SHA256 = "b282191a91b4f25dc5f3406d4ba30adb58465d2913c64446a6bca5dddd8e47f0"

EXPECTED_PAIR_RECORDS = 404_054
EXPECTED_PAIR_STRATA = 142
EXPECTED_BRIDGE_PAIRS = 979
EXPECTED_K2_TOTAL = 223
EXPECTED_PRIMARY_INSTANCES = 24
EXPECTED_PRIMARY_RESCUES = 122

EXTERNAL = "EXTERNAL_ATTACHMENT_RESCUE"
INTERNAL = "INTERNAL_EDGE_DEPENDENT_RESCUE"
MECHANISMS = (EXTERNAL, INTERNAL)

LEVEL_BY_NAME = {
    "F0_TARGET_CLASS_ONLY": 0,
    "F1_ALL_LONG_PERIOD": 1,
    "F2_ALL_CONFIRMED_PERSISTENT": 2,
    "F3_ALL_LEDGER_BACKED_NONZERO": 3,
    "F4_FULL_Q8_DIAGNOSTIC": 4,
}
LONG_CATEGORY = "LONG_PERIOD_CAP_CANDIDATE"
F2_CATEGORIES = {"HISTORICAL_SOURCE_POSITIVE", "STATIC_T1"}
F3_CATEGORIES = {"EXTINCT", "SPAN_ESCAPE", "ZERO_INITIAL_DEFECT"}
ZERO_CATEGORY = "ZERO_IC_BOUNDARY_UNSAMPLED"

FORBIDDEN_PREDICTORS = {
    "minimum_vertex_cut",
    "minimum_edge_cut",
    "individually_critical_vertices",
    "individually_critical_edges",
    "kappa_v",
    "lambda_e",
    "robustness_label",
    "edge_disjoint_path_count",
    "internally_vertex_disjoint_path_count",
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


def node_levels(nodes: list[dict[str, Any]], physical_class: str) -> list[int]:
    levels: list[int] = []
    for word, node in enumerate(nodes):
        if int(node["word8"], 2) != word:
            raise RuntimeError("Phase-94 nodes are not in canonical Q8 order")
        category = node["category"]
        if node["physical_class_sha256"] == physical_class:
            level = 0
        elif category == LONG_CATEGORY:
            level = 1
        elif category in F2_CATEGORIES:
            level = 2
        elif category in F3_CATEGORIES:
            level = 3
        elif category == ZERO_CATEGORY:
            level = 4
        else:
            raise RuntimeError(f"Unknown node category: {category}")
        levels.append(level)
    if len(levels) != 256:
        raise RuntimeError("Every Q8 cube must contain 256 ordered nodes")
    return levels


def allowed_words(levels: list[int], maximum_level: int) -> set[int]:
    return {word for word, level in enumerate(levels) if level <= maximum_level}


def reconstruct_gmin(
    phase94: dict[str, Any], phase96: dict[str, Any]
) -> tuple[dict[tuple[str, int], frozenset[int]], dict[str, Any]]:
    cubes = {str(row["cube_key"]): row["nodes"] for row in phase94["cube_nodes"]}
    if len(cubes) != len(phase94["cube_nodes"]):
        raise RuntimeError("Duplicate phase-94 cube key")
    pairs: dict[tuple[str, int], frozenset[int]] = {}
    for row in phase96["component_pairs"]:
        key = (str(row["cube_key"]), int(row["pair_index"]))
        if key in pairs:
            raise RuntimeError("Duplicate bridge pair key")
        levels = node_levels(cubes[key[0]], str(row["physical_class_sha256"]))
        try:
            maximum_level = LEVEL_BY_NAME[str(row["earliest_any_path_level"])]
        except KeyError as exc:
            raise RuntimeError("Unknown earliest path level") from exc
        gmin = frozenset(allowed_words(levels, maximum_level))
        if len(gmin) != int(row["g_min"]["allowed_node_count"]):
            raise RuntimeError("Reconstructed G_min size mismatch")
        pairs[key] = gmin
    if len(pairs) != EXPECTED_BRIDGE_PAIRS:
        raise RuntimeError("Unexpected bridge-pair count")
    return pairs, {"pair_count": len(pairs), "allowed_node_count_mismatches": 0}


def reconstruct_universes(
    ledger_path: Path,
    manifest: dict[str, Any],
    pair_results: dict[str, Any],
) -> tuple[dict[tuple[str, int, int], frozenset[int]], dict[str, Any]]:
    if raw_sha256(ledger_path) != EXPECTED_PAIR_LEDGER_SHA256:
        raise RuntimeError("Pair ledger SHA-256 mismatch")
    if manifest["ledger_sha256"] != EXPECTED_PAIR_LEDGER_SHA256:
        raise RuntimeError("Pair manifest ledger hash mismatch")
    if manifest["record_format"] != "<HBBHBBBB":
        raise RuntimeError("Unexpected pair ledger format")
    record = struct.Struct(manifest["record_format"])
    record_count = int(manifest["record_count"])
    if record_count != EXPECTED_PAIR_RECORDS:
        raise RuntimeError("Unexpected pair record count")
    if ledger_path.stat().st_size != record_count * record.size:
        raise RuntimeError("Pair ledger size mismatch")

    words: dict[int, set[int]] = defaultdict(set)
    counts: Counter[int] = Counter()
    with ledger_path.open("rb") as handle:
        for _ in range(record_count):
            raw = handle.read(record.size)
            if len(raw) != record.size:
                raise RuntimeError("Truncated pair ledger")
            stratum_index, left, right, *_rest = record.unpack(raw)
            if left >= right:
                raise RuntimeError("Non-canonical ledger pair")
            words[int(stratum_index)].update((int(left), int(right)))
            counts[int(stratum_index)] += 1
        if handle.read(1):
            raise RuntimeError("Pair ledger has trailing data")

    strata = {int(row["stratum_index"]): row for row in pair_results["strata"]}
    if len(strata) != EXPECTED_PAIR_STRATA or set(strata) != set(words):
        raise RuntimeError("Unexpected universe stratum set")
    output: dict[tuple[str, int, int], frozenset[int]] = {}
    for index, row in strata.items():
        universe = frozenset(words[index])
        node_count = int(row["node_count"])
        if len(universe) != node_count or counts[index] != math.comb(node_count, 2):
            raise RuntimeError("Universe reconstruction mismatch")
        key = (str(row["cube_key"]), int(row["pair_index"]), int(row["period"]))
        if key in output:
            raise RuntimeError("Duplicate universe natural key")
        output[key] = universe
    return output, {
        "record_count": sum(counts.values()),
        "stratum_count": len(output),
        "reconstruction_mismatches": 0,
    }


def hamming_one(a: int, b: int) -> bool:
    return (int(a) ^ int(b)).bit_count() == 1


def bridge_incidence(words: Iterable[int], gmin: Iterable[int]) -> int:
    rescue = tuple(sorted(map(int, words)))
    if len(rescue) != 2 or not hamming_one(*rescue):
        raise RuntimeError("Rescue is not K2")
    bridge_words = set(map(int, gmin))
    return sum(hamming_one(word, other) for word in rescue for other in bridge_words)


def phase109_k2_rows(phase109: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row for row in phase109["rescue_geometry"] if row["motif"] == "K2"]
    if len(rows) != EXPECTED_K2_TOTAL:
        raise RuntimeError("Unexpected total K2 count")
    identities: set[tuple[str, tuple[int, ...]]] = set()
    output: list[dict[str, Any]] = []
    for source in rows:
        row = dict(source)
        words = tuple(sorted(map(int, row["words"])))
        identity = (str(row["instance_key"]), words)
        if identity in identities:
            raise RuntimeError("Duplicate K2 identity")
        identities.add(identity)
        if row["mechanism_label"] not in MECHANISMS:
            raise RuntimeError("Unexpected mechanism label")
        if int(row["geometry"]["S_ext"]) < 0:
            raise RuntimeError("Invalid certified A_V")
        row["words"] = list(words)
        output.append(row)
    return output


def reconcile_motif_source(
    motif_results: dict[str, Any], phase109_rows: list[dict[str, Any]]
) -> dict[str, int]:
    motif_map: dict[tuple[str, tuple[int, ...]], str] = {}
    for row in motif_results["atlas"]["mechanism_audits"]:
        if row["motif"] != "K2":
            continue
        key = "|".join(
            (
                str(row["cube_key"]),
                str(int(row["pair_index"])),
                str(int(row["period"])),
                str(row["metric"]),
            )
        )
        identity = (key, tuple(sorted(map(int, row["words"]))))
        if identity in motif_map:
            raise RuntimeError("Duplicate K2 identity in motif source")
        motif_map[identity] = str(row["mechanism_label"])
    phase109_map = {
        (str(row["instance_key"]), tuple(map(int, row["words"]))): str(
            row["mechanism_label"]
        )
        for row in phase109_rows
    }
    if len(motif_map) != EXPECTED_K2_TOTAL or len(phase109_map) != EXPECTED_K2_TOTAL:
        raise RuntimeError("K2 identity count mismatch")
    if motif_map != phase109_map:
        raise RuntimeError("Phase-105/Phase-109 K2 identity or mechanism mismatch")
    return {"identity_count": len(motif_map), "identity_or_mechanism_mismatches": 0}


def mixed_groups(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row["instance_key"])].append(row)
    mixed = {
        key: group
        for key, group in groups.items()
        if {row["mechanism_label"] for row in group} == set(MECHANISMS)
    }
    if len(mixed) != EXPECTED_PRIMARY_INSTANCES:
        raise RuntimeError("Unexpected mixed-instance count")
    if sum(map(len, mixed.values())) != EXPECTED_PRIMARY_RESCUES:
        raise RuntimeError("Unexpected primary rescue count")
    return mixed


def enrich_rows(
    rows: list[dict[str, Any]],
    mixed: dict[str, list[dict[str, Any]]],
    universes: dict[tuple[str, int, int], frozenset[int]],
    gmins: dict[tuple[str, int], frozenset[int]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    primary_keys = set(mixed)
    enriched: list[dict[str, Any]] = []
    primary_count = 0
    for source in rows:
        words = tuple(map(int, source["words"]))
        universe_key = (
            str(source["cube_key"]),
            int(source["pair_index"]),
            int(source["period"]),
        )
        bridge_key = (str(source["cube_key"]), int(source["pair_index"]))
        try:
            universe = universes[universe_key]
            gmin = gmins[bridge_key]
        except KeyError as exc:
            raise RuntimeError("Incomplete natural-key join") from exc
        a_v = int(source["geometry"]["S_ext"])
        a_g = bridge_incidence(words, gmin)
        if a_g != bridge_incidence(reversed(words), gmin):
            raise RuntimeError("A_G depends on word order")
        row = {
            "instance_key": str(source["instance_key"]),
            "cube_key": str(source["cube_key"]),
            "pair_index": int(source["pair_index"]),
            "period": int(source["period"]),
            "metric": str(source["metric"]),
            "words": list(words),
            "mechanism_label": str(source["mechanism_label"]),
            "A_V": a_v,
            "A_G": a_g,
            "primary_partition_scope": str(source["instance_key"]) in primary_keys,
        }
        if row["primary_partition_scope"]:
            primary_count += 1
            if not set(words).issubset(universe):
                raise RuntimeError("H is not a subset of V_i")
            if universe & gmin:
                raise RuntimeError("V_i and G_min are not disjoint")
            a_r = 14 - a_v - a_g
            if a_v + a_g + a_r != 14 or a_r < 0:
                raise RuntimeError("Fixed-budget partition failure")
            row["A_R"] = a_r
        enriched.append(row)
    if primary_count != EXPECTED_PRIMARY_RESCUES:
        raise RuntimeError("Primary enrichment count mismatch")
    return enriched, {
        "total_k2": len(enriched),
        "primary_instances": len(primary_keys),
        "primary_rescues": primary_count,
        "subset_failures": 0,
        "disjointness_failures": 0,
        "partition_failures": 0,
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


def feature_analysis(
    primary_groups: dict[str, list[dict[str, Any]]],
    feature: str,
    role: str,
) -> dict[str, Any]:
    per_instance: list[dict[str, Any]] = []
    deltas: list[float] = []
    for key in sorted(primary_groups):
        group = primary_groups[key]
        external = [row[feature] for row in group if row["mechanism_label"] == EXTERNAL]
        internal = [row[feature] for row in group if row["mechanism_label"] == INTERNAL]
        delta = statistics.fmean(external) - statistics.fmean(internal)
        deltas.append(delta)
        per_instance.append(
            {
                "instance_key": key,
                "external_count": len(external),
                "internal_count": len(internal),
                "delta_external_minus_internal": delta,
            }
        )
    total = sum(deltas)
    loo = [(total - value) / (len(deltas) - 1) for value in deltas]
    return {
        "feature": feature,
        "role": role,
        "instance_balanced": True,
        "per_instance": per_instance,
        "delta_summary": summarize_values(deltas),
        "delta_signs": {
            "positive": sum(value > 0 for value in deltas),
            "zero": sum(value == 0 for value in deltas),
            "negative": sum(value < 0 for value in deltas),
        },
        "leave_one_instance_out_mean_range": {"min": min(loo), "max": max(loo)},
    }


def weighted_centered_relation(
    primary_groups: dict[str, list[dict[str, Any]]]
) -> dict[str, Any]:
    residual_rows: list[dict[str, Any]] = []
    covariance = 0.0
    variance_a_v = 0.0
    variance_a_g = 0.0
    instance_count = len(primary_groups)
    for key in sorted(primary_groups):
        group = primary_groups[key]
        mean_a_v = statistics.fmean(row["A_V"] for row in group)
        mean_a_g = statistics.fmean(row["A_G"] for row in group)
        weight = 1.0 / (instance_count * len(group))
        for row in group:
            x = row["A_V"] - mean_a_v
            y = row["A_G"] - mean_a_g
            covariance += weight * x * y
            variance_a_v += weight * x * x
            variance_a_g += weight * y * y
            residual_rows.append(
                {
                    "instance_key": key,
                    "words": row["words"],
                    "A_V_centered": x,
                    "A_G_centered": y,
                    "weight": weight,
                }
            )
    correlation = (
        covariance / math.sqrt(variance_a_v * variance_a_g)
        if variance_a_v > 0 and variance_a_g > 0
        else None
    )
    return {
        "method": "instance_centered_equal_instance_weight_pearson",
        "covariance": covariance,
        "variance_A_V": variance_a_v,
        "variance_A_G": variance_a_g,
        "correlation": correlation,
        "correlation_defined": correlation is not None,
        "residual_rows": residual_rows,
    }


def analyze() -> tuple[dict[str, Any], dict[str, Any]]:
    if raw_sha256(PHASE96_SCRIPT_PATH) != EXPECTED_PHASE96_SCRIPT_SHA256:
        raise RuntimeError("Phase-96 runner SHA-256 mismatch")

    payloads: dict[Path, dict[str, Any]] = {}
    source_hashes: dict[str, Any] = {}
    for path in EXPECTED_JSON_HASHES:
        payloads[path], hashes = read_gated_json(path)
        source_hashes[path.name] = hashes
    source_hashes[PAIR_LEDGER_PATH.name] = {"sha256": EXPECTED_PAIR_LEDGER_SHA256}
    source_hashes[PHASE96_SCRIPT_PATH.name] = {"sha256": EXPECTED_PHASE96_SCRIPT_SHA256}

    gmins, gmin_audit = reconstruct_gmin(payloads[PHASE94_PATH], payloads[PHASE96_PATH])
    universes, universe_audit = reconstruct_universes(
        PAIR_LEDGER_PATH,
        payloads[PAIR_MANIFEST_PATH],
        payloads[PAIR_RESULTS_PATH],
    )
    # The motif source is independently gated and reconciled to the Phase-109 census.
    phase109_rows = phase109_k2_rows(payloads[PHASE109_RESULTS_PATH])
    motif_audit = reconcile_motif_source(payloads[MOTIF_RESULTS_PATH], phase109_rows)
    mixed = mixed_groups(phase109_rows)
    enriched, partition_audit = enrich_rows(phase109_rows, mixed, universes, gmins)
    primary_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in enriched:
        if row["primary_partition_scope"]:
            primary_groups[row["instance_key"]].append(row)

    a_g_analysis = feature_analysis(primary_groups, "A_G", "primary")
    a_r_analysis = feature_analysis(primary_groups, "A_R", "secondary")
    census_a_g = {
        mechanism: {
            "summary": summarize_values(
                row["A_G"] for row in enriched if row["mechanism_label"] == mechanism
            ),
            "histogram": histogram(
                row["A_G"] for row in enriched if row["mechanism_label"] == mechanism
            ),
        }
        for mechanism in MECHANISMS
    }
    raw_primary_pairs = [
        {
            "instance_key": row["instance_key"],
            "words": row["words"],
            "mechanism_label": row["mechanism_label"],
            "A_V": row["A_V"],
            "A_G": row["A_G"],
            "A_R": row["A_R"],
        }
        for row in enriched
        if row["primary_partition_scope"]
    ]
    raw_census_pairs = [
        {
            "instance_key": row["instance_key"],
            "words": row["words"],
            "mechanism_label": row["mechanism_label"],
            "A_V": row["A_V"],
            "A_G": row["A_G"],
        }
        for row in enriched
    ]

    results = {
        "phase": 110,
        "artifact_prefix": "phase109",
        "status": "FIXED_BUDGET_HAMMING_PARTITION_K2_VERIFIED",
        "scope": {
            "causal_claim": False,
            "population_generalization": False,
            "directional_hypothesis": False,
            "statistical_independence_claimed": False,
            "partition_scope": "122_K2_rescues_in_24_mixed_instances",
            "full_census_partition_claim": False,
            "new_simulation_or_sweep": False,
        },
        "source_audit": {
            "gmin": gmin_audit,
            "universes": universe_audit,
            "partition": partition_audit,
            "motif_reconciliation": motif_audit,
            "forbidden_predictors": sorted(FORBIDDEN_PREDICTORS),
        },
        "primary_A_G": a_g_analysis,
        "secondary_A_R": a_r_analysis,
        "centered_A_V_A_G_relation": weighted_centered_relation(primary_groups),
        "full_census_A_G": census_a_g,
        "primary_partition_rows": raw_primary_pairs,
        "supplementary_full_census_pairs": raw_census_pairs,
        "sources": source_hashes,
    }
    return results, source_hashes


def render_report(results: dict[str, Any]) -> str:
    primary = results["primary_A_G"]
    secondary = results["secondary_A_R"]
    relation = results["centered_A_V_A_G_relation"]
    lines = [
        "# Fase 110 — Partición Hamming de presupuesto fijo",
        "",
        f"**Veredicto:** `{results['status']}`",
        "",
        "## Auditoría",
        "",
        "- Pares-puente G_min reconstruidos: 979",
        "- Universos V_i reconstruidos: 142",
        "- Rescates K2 totales: 223",
        "- Discrepancias de identidad/mecanismo Fase 105–109: 0",
        "- Universo principal: 122 rescates en 24 instancias mixtas",
        "- Fallos de contención, disyunción, partición u orden: 0",
        "",
        "## Resultado principal A_G",
        "",
        f"- Media de Delta_i: {primary['delta_summary']['mean']:.6f}",
        f"- Mediana: {primary['delta_summary']['median']:.6f}",
        f"- Rango: [{primary['delta_summary']['min']:.6f}, "
        f"{primary['delta_summary']['max']:.6f}]",
        "- Signos: "
        f"{primary['delta_signs']['positive']} positivos, "
        f"{primary['delta_signs']['zero']} nulos, "
        f"{primary['delta_signs']['negative']} negativos.",
        "- Estabilidad leave-one-instance-out: "
        f"[{primary['leave_one_instance_out_mean_range']['min']:.6f}, "
        f"{primary['leave_one_instance_out_mean_range']['max']:.6f}]",
        "",
        "### Distribución completa A_G",
        "",
    ]
    for mechanism in MECHANISMS:
        summary = results["full_census_A_G"][mechanism]["summary"]
        lines.append(
            f"- {mechanism}: n={summary['count']}, media={summary['mean']:.6f}, "
            f"mediana={summary['median']:.6f}, rango=[{summary['min']}, {summary['max']}]."
        )
    lines.extend(
        [
            "",
            "## Resultado secundario A_R",
            "",
            f"- Media de Delta_i: {secondary['delta_summary']['mean']:.6f}",
            f"- Mediana: {secondary['delta_summary']['median']:.6f}",
            "- Signos: "
            f"{secondary['delta_signs']['positive']} positivos, "
            f"{secondary['delta_signs']['zero']} nulos, "
            f"{secondary['delta_signs']['negative']} negativos.",
            "",
            "## Relación centrada A_V–A_G",
            "",
            f"- Covarianza ponderada: {relation['covariance']:.6f}",
            f"- Varianza ponderada A_V: {relation['variance_A_V']:.6f}",
            f"- Varianza ponderada A_G: {relation['variance_A_G']:.6f}",
            f"- Correlación ponderada: {relation['correlation']:.6f}",
            "",
            "## Límites",
            "",
            "La partición solo se certifica para los 122 rescates de las 24 instancias "
            "mixtas. No existe hipótesis direccional, afirmación causal, generalización "
            "poblacional ni afirmación de independencia estadística. Los 223 pares "
            "completos son únicamente un suplemento descriptivo no particional.",
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
    runner = Path(__file__).resolve()
    manifest = {
        "phase": 110,
        "artifact_prefix": "phase109",
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
