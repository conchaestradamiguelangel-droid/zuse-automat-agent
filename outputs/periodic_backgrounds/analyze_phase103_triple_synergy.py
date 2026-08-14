from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import itertools
import json
import math
import os
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"
PHASE95_PATH = OUTPUT_DIR / "phase94_hypercube_completion_results.json"
PHASE97_PATH = OUTPUT_DIR / "phase96_bridge_robustness_results.json"
PHASE102_PATH = OUTPUT_DIR / "phase101_cut_coverage_law_results.json"
PHASE103_RESULTS_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_results.json"
PHASE103_MANIFEST_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_manifest.json"
PHASE103_LEDGER_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_ledger.bin"
LEDGER_PATH = OUTPUT_DIR / "phase103_triple_synergy_ledger.bin"
MANIFEST_PATH = OUTPUT_DIR / "phase103_triple_synergy_manifest.json"
RESULTS_PATH = OUTPUT_DIR / "phase103_triple_synergy_results.json"
REPORT_PATH = OUTPUT_DIR / "phase103_triple_synergy_report.md"

EXPECTED_HASHES = {
    "phase95": (
        "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3",
        "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429",
    ),
    "phase97": (
        "3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858",
        "85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b",
    ),
    "phase102": (
        "2eae9b4825bb78d9c396a47bfe365c0beedda198de7c8a2a6093fede3423fb2c",
        "3ecad4486d9ac87c5c7efc58726a41dcaacd738d6450ffc6024b3577dbd0b74e",
    ),
    "phase103_results": (
        "9a5c70318085c8d6d1a7ad82a59fb631abda524926288c46cb0da30a7cd47268",
        "152003197716bff38e552b3b51754df6dbfe4c6dc9f93326c3a55de594e5a6c3",
    ),
    "phase103_manifest": (
        "d434a20dd0c66350fadceac6ea4f6e3d73bd9769e51195083efc628ed8170057",
        "580635c42efc2bb042e539f0a1f61d6ae15693d38d77a3333041757be9257ea5",
    ),
}
EXPECTED_PHASE103_LEDGER_SHA = (
    "24de12594fe8b95f6e70be4278b2dfadb7f29f181aef3d7aeea41f9fbe58de52"
)

EXPECTED_CUBE_COUNT = 48
EXPECTED_TARGET_COUNT = 219
EXPECTED_UNIT_AUDIT_COUNT = 43425
EXPECTED_PHASE103_STRATA = 142
EXPECTED_PHASE103_PAIRS = 404054
EXPECTED_PHASE103_KAPPA_RESCUES = 454
EXPECTED_PHASE103_LAMBDA_RESCUES = 470
EXPECTED_STRATUM_COUNT = 73
EXPECTED_KAPPA_STRATA = 57
EXPECTED_LAMBDA_STRATA = 71
EXPECTED_TRIPLE_COUNT = 3061466
EXPECTED_KAPPA_TRIALS = 2745416
EXPECTED_LAMBDA_TRIALS = 3031106
EXPECTED_STRATA_BY_PERIOD = {2: 8, 3: 43, 6: 3, 12: 19}
EXPECTED_TRIPLES_BY_PERIOD = {2: 1107320, 3: 1382119, 6: 520251, 12: 51776}
EXPECTED_TRIPLES_BY_RULE = {73: 1413087, 109: 1648379}
EXPECTED_KAPPA_BY_PERIOD = {2: 1107320, 3: 1066069, 6: 520251, 12: 51776}
EXPECTED_LAMBDA_BY_PERIOD = {2: 1107320, 3: 1351759, 6: 520251, 12: 51776}
EXPECTED_KAPPA_BY_RULE = {73: 1253837, 109: 1491579}
EXPECTED_LAMBDA_BY_RULE = {73: 1413087, 109: 1618019}
EXPECTED_INTERNAL_EDGE_DISTRIBUTION = {0: 2693722, 1: 353303, 2: 14441, 3: 0}
EXPECTED_INTERNAL_EDGES_BY_PERIOD = {
    2: {0: 995220, 1: 108880, 2: 3220, 3: 0},
    3: {0: 1190889, 1: 182288, 2: 8942, 3: 0},
    6: {0: 463328, 1: 54945, 2: 1978, 3: 0},
    12: {0: 44285, 1: 7190, 2: 301, 3: 0},
}

HISTORICAL_CATEGORY = "HISTORICAL_SOURCE_POSITIVE"
AT_LEAST_THREE = "AT_LEAST_3"
KAPPA = "kappa_v"
LAMBDA = "lambda_e"

# 10-byte little-endian record. The last byte packs a 3-bit vertex mask and
# a 5-bit count of new-edge separators.
LEDGER_RECORD = struct.Struct("<HBBBHBBB")
LEDGER_FORMAT = "<HBBBHBBB"
LEDGER_FIELDS = [
    {"name": "stratum_index", "offset": 0, "width": 2, "type": "uint16"},
    {"name": "first_word", "offset": 2, "width": 1, "type": "uint8"},
    {"name": "second_word", "offset": 3, "width": 1, "type": "uint8"},
    {"name": "third_word", "offset": 4, "width": 1, "type": "uint8"},
    {"name": "flags", "offset": 5, "width": 2, "type": "uint16_bitmask"},
    {"name": "uncovered_original_vertices", "offset": 7, "width": 1, "type": "uint8"},
    {"name": "uncovered_original_edges", "offset": 8, "width": 1, "type": "uint8"},
    {"name": "packed_new_separators", "offset": 9, "width": 1, "type": "uint8_packed"},
]
FLAG_BITS = {
    "kappa_scope": 2,
    "lambda_scope": 3,
    "kappa_route_a_rescue": 4,
    "lambda_route_a_rescue": 5,
    "kappa_route_b_rescue": 6,
    "lambda_route_b_rescue": 7,
    "distributed_vertex_coverage": 8,
    "distributed_edge_coverage": 9,
    "internal_edge_required_kappa": 10,
    "internal_edge_required_lambda": 11,
    "three_node_vertex_coverage": 12,
    "three_node_edge_coverage": 13,
}


def load_phase103_module():
    path = OUTPUT_DIR / "analyze_phase102_pairwise_synergy.py"
    name = "_zuse_phase103_dependency"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load Fase-103 dependency")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase103 = load_phase103_module()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_and_gate(path: Path, expected: tuple[str, str]) -> dict[str, Any]:
    raw = raw_sha256(path)
    if raw != expected[0]:
        raise RuntimeError(f"Raw SHA mismatch for {path.name}: {raw}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    canonical = canonical_sha256(payload)
    if canonical != expected[1]:
        raise RuntimeError(f"Canonical SHA mismatch for {path.name}: {canonical}")
    return payload


def atomic_write_bytes(path: Path, data: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def atomic_write_text(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))


def build_flags(values: dict[str, bool], internal_edge_count: int) -> int:
    if not 0 <= internal_edge_count <= 3:
        raise ValueError("Internal-edge count does not fit two bits")
    mask = internal_edge_count
    for name, bit in FLAG_BITS.items():
        if values.get(name, False):
            mask |= 1 << bit
    return mask


def pack_separators(vertex_mask: int, edge_count: int) -> int:
    if not 0 <= vertex_mask <= 0b111:
        raise ValueError("New-vertex separator mask does not fit three bits")
    if not 0 <= edge_count <= 31:
        raise ValueError("New-edge separator count does not fit five bits")
    return vertex_mask | (edge_count << 3)


def unpack_separators(value: int) -> tuple[int, int]:
    return value & 0b111, value >> 3


def add_nodes(
    base: dict[int, set[int]], words: Iterable[int]
) -> tuple[dict[int, set[int]], tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
    ordered = tuple(words)
    if tuple(sorted(ordered)) != ordered or len(set(ordered)) != len(ordered):
        raise RuntimeError("Intervention words must be unique and sorted")
    if any(word in base for word in ordered):
        raise RuntimeError("Intervention word already belongs to F1")
    adjacency = {node: set(targets) for node, targets in base.items()}
    for word in ordered:
        adjacency[word] = set()
    new_edges: set[tuple[int, int]] = set()
    for word in ordered:
        for neighbor in phase103.q8_neighbors(word):
            if neighbor in adjacency:
                edge = tuple(sorted((word, neighbor)))
                new_edges.add(edge)
                adjacency[word].add(neighbor)
                adjacency[neighbor].add(word)
    intervention_set = set(ordered)
    internal_edges = tuple(
        edge for edge in sorted(new_edges) if set(edge) <= intervention_set
    )
    return adjacency, tuple(sorted(new_edges)), internal_edges


def direct_cut_audit(
    adjacency: dict[int, set[int]],
    component_a: set[int],
    component_b: set[int],
    original_vertices: tuple[int, ...],
    original_edges: tuple[tuple[int, int], ...],
    added_words: tuple[int, int, int],
    new_edges: tuple[tuple[int, int], ...],
    *,
    kappa_scope: bool,
    lambda_scope: bool,
) -> dict[str, Any]:
    uncovered_vertices = (
        sum(
            not phase103.terminals_connected(
                adjacency, component_a, component_b, removed_vertex=vertex
            )
            for vertex in original_vertices
        )
        if kappa_scope
        else 0
    )
    uncovered_edges = (
        sum(
            not phase103.terminals_connected(
                adjacency, component_a, component_b, removed_edge=edge
            )
            for edge in original_edges
        )
        if lambda_scope
        else 0
    )
    new_vertex_mask = 0
    if kappa_scope:
        for bit, word in enumerate(added_words):
            if not phase103.terminals_connected(
                adjacency, component_a, component_b, removed_vertex=word
            ):
                new_vertex_mask |= 1 << bit
    new_edge_separators = (
        tuple(
            edge
            for edge in new_edges
            if not phase103.terminals_connected(
                adjacency, component_a, component_b, removed_edge=edge
            )
        )
        if lambda_scope
        else ()
    )
    return {
        "kappa_rescue": bool(
            kappa_scope and uncovered_vertices == 0 and new_vertex_mask == 0
        ),
        "lambda_rescue": bool(
            lambda_scope and uncovered_edges == 0 and not new_edge_separators
        ),
        "uncovered_original_vertices": uncovered_vertices,
        "uncovered_original_edges": uncovered_edges,
        "new_vertex_separator_mask": new_vertex_mask,
        "new_edge_separators": new_edge_separators,
    }


def internal_edge_required(
    adjacency: dict[int, set[int]],
    component_a: set[int],
    component_b: set[int],
    internal_edges: tuple[tuple[int, int], ...],
    *,
    metric: str,
    rescue: bool,
) -> bool:
    if not rescue:
        return False
    for edge in internal_edges:
        reduced = phase103.remove_edge_copy(adjacency, edge)
        still_rescues = (
            phase103.vertex_connectivity_two(reduced, component_a, component_b)
            if metric == KAPPA
            else phase103.edge_connectivity_two(reduced, component_a, component_b)
        )
        if not still_rescues:
            return True
    return False


def triple_minimal_label(scope: bool, rescue_count: int) -> str:
    if not scope:
        return "NOT_APPLICABLE_NOT_AT_LEAST_THREE"
    return "EXACTLY_3" if rescue_count else "AT_LEAST_4"


def validate_phase103_replay(
    results: dict[str, Any], manifest: dict[str, Any]
) -> dict[int, dict[str, set[tuple[int, int]]]]:
    summary = results["summary"]
    if len(results["strata"]) != EXPECTED_PHASE103_STRATA:
        raise RuntimeError("Fase-103 stratum replay mismatch")
    if int(summary["pair_intervention_count"]) != EXPECTED_PHASE103_PAIRS:
        raise RuntimeError("Fase-103 pair denominator mismatch")
    if int(summary["kappa_pair_rescue_count"]) != EXPECTED_PHASE103_KAPPA_RESCUES:
        raise RuntimeError("Fase-103 kappa rescue mismatch")
    if int(summary["lambda_pair_rescue_count"]) != EXPECTED_PHASE103_LAMBDA_RESCUES:
        raise RuntimeError("Fase-103 lambda rescue mismatch")
    if manifest["ledger_sha256"] != EXPECTED_PHASE103_LEDGER_SHA:
        raise RuntimeError("Fase-103 manifest ledger digest mismatch")
    if raw_sha256(PHASE103_LEDGER_PATH) != EXPECTED_PHASE103_LEDGER_SHA:
        raise RuntimeError("Fase-103 ledger digest mismatch")
    if int(manifest["record_count"]) != EXPECTED_PHASE103_PAIRS:
        raise RuntimeError("Fase-103 manifest count mismatch")

    old_record = struct.Struct(manifest["record_format"])
    if old_record.size != int(manifest["record_size"]):
        raise RuntimeError("Fase-103 ledger layout mismatch")
    flag_bits = {name: int(bit) for name, bit in manifest["flag_bits"].items()}
    pair_sets: dict[int, dict[str, set[tuple[int, int]]]] = {}
    unresolved_old = {
        int(row["stratum_index"])
        for row in results["strata"]
        if row["kappa_minimal_cardinality"] == AT_LEAST_THREE
        or row["lambda_minimal_cardinality"] == AT_LEAST_THREE
    }
    for old_index in unresolved_old:
        pair_sets[old_index] = {
            "seen": set(),
            "vertex_complete": set(),
            "edge_complete": set(),
        }
    kappa_rescues = 0
    lambda_rescues = 0
    out_of_scope_bits = 0
    route_disagreements = 0
    record_count = 0
    with PHASE103_LEDGER_PATH.open("rb") as handle:
        while True:
            raw = handle.read(old_record.size)
            if not raw:
                break
            if len(raw) != old_record.size:
                raise RuntimeError("Truncated Fase-103 ledger")
            (
                old_index,
                left,
                right,
                flags,
                uncovered_vertices,
                uncovered_edges,
                _new_vertex_mask,
                _new_edge_count,
            ) = old_record.unpack(raw)
            decoded = {
                name: bool(flags & (1 << bit)) for name, bit in flag_bits.items()
            }
            if decoded["kappa_route_a_rescue"] != decoded["kappa_route_b_rescue"]:
                route_disagreements += 1
            if decoded["lambda_route_a_rescue"] != decoded["lambda_route_b_rescue"]:
                route_disagreements += 1
            if decoded["kappa_collective_scope"] and decoded["kappa_route_b_rescue"]:
                kappa_rescues += 1
            if decoded["lambda_collective_scope"] and decoded["lambda_route_b_rescue"]:
                lambda_rescues += 1
            if (
                not decoded["kappa_collective_scope"]
                and decoded["mutual_edge_required_kappa"]
            ) or (
                not decoded["lambda_collective_scope"]
                and decoded["mutual_edge_required_lambda"]
            ):
                out_of_scope_bits += 1
            if old_index in pair_sets:
                pair = (left, right)
                pair_sets[old_index]["seen"].add(pair)
                if uncovered_vertices == 0:
                    pair_sets[old_index]["vertex_complete"].add(pair)
                if uncovered_edges == 0:
                    pair_sets[old_index]["edge_complete"].add(pair)
                source = results["strata"][old_index]
                if (
                    source["kappa_minimal_cardinality"] == AT_LEAST_THREE
                    and decoded["kappa_route_b_rescue"]
                ) or (
                    source["lambda_minimal_cardinality"] == AT_LEAST_THREE
                    and decoded["lambda_route_b_rescue"]
                ):
                    raise RuntimeError("Unresolved Fase-103 stratum contains pair rescue")
            record_count += 1
    if record_count != EXPECTED_PHASE103_PAIRS:
        raise RuntimeError("Fase-103 ledger record reconciliation failed")
    if route_disagreements or out_of_scope_bits:
        raise RuntimeError("Fase-103 clean-ledger replay failed")
    if (kappa_rescues, lambda_rescues) != (
        EXPECTED_PHASE103_KAPPA_RESCUES,
        EXPECTED_PHASE103_LAMBDA_RESCUES,
    ):
        raise RuntimeError("Fase-103 raw rescue totals changed")
    for old_index, sets in pair_sets.items():
        node_count = int(results["strata"][old_index]["node_count"])
        if len(sets["seen"]) != math.comb(node_count, 2):
            raise RuntimeError("Fase-103 unresolved pair coverage mismatch")
    return pair_sets


def process_stratum(task: dict[str, Any]) -> dict[str, Any]:
    stratum_index = int(task["stratum_index"])
    words = tuple(task["historical_words"])
    kappa_scope = bool(task["kappa_scope"])
    lambda_scope = bool(task["lambda_scope"])
    context = task["context"]
    complete_vertex_pairs = set(task["complete_vertex_pairs"])
    complete_edge_pairs = set(task["complete_edge_pairs"])
    ledger = bytearray()
    kappa_rescues: list[tuple[int, int, int]] = []
    lambda_rescues: list[tuple[int, int, int]] = []
    internal_edge_distribution = Counter()
    required_kappa = 0
    required_lambda = 0
    distributed_vertex = 0
    distributed_edge = 0
    kappa_rescues_by_internal_edge_count = Counter()
    lambda_rescues_by_internal_edge_count = Counter()
    route_disagreements = 0
    monotonicity_failures = 0

    for first, second, third in itertools.combinations(words, 3):
        triple = (first, second, third)
        adjacency, new_edges, internal_edges = add_nodes(context["adjacency"], triple)
        internal_count = len(internal_edges)
        if internal_count == 3:
            raise RuntimeError("Q8 triangle contradiction")
        internal_edge_distribution[internal_count] += 1
        route_a = direct_cut_audit(
            adjacency,
            context["component_a"],
            context["component_b"],
            context["critical_vertices"],
            context["critical_edges"],
            triple,
            new_edges,
            kappa_scope=kappa_scope,
            lambda_scope=lambda_scope,
        )
        route_b_kappa = (
            phase103.vertex_connectivity_two(
                adjacency, context["component_a"], context["component_b"]
            )
            if kappa_scope
            else False
        )
        route_b_lambda = (
            phase103.edge_connectivity_two(
                adjacency, context["component_a"], context["component_b"]
            )
            if lambda_scope
            else False
        )
        if route_a["kappa_rescue"] != route_b_kappa:
            route_disagreements += 1
        if route_a["lambda_rescue"] != route_b_lambda:
            route_disagreements += 1

        triple_pairs = ((first, second), (first, third), (second, third))
        if any(pair not in task["seen_pairs"] for pair in triple_pairs):
            raise RuntimeError("Triple contains an unreplayed Fase-103 pair")
        three_node_vertex = bool(
            kappa_scope
            and route_a["uncovered_original_vertices"] == 0
            and all(pair not in complete_vertex_pairs for pair in triple_pairs)
        )
        three_node_edge = bool(
            lambda_scope
            and route_a["uncovered_original_edges"] == 0
            and all(pair not in complete_edge_pairs for pair in triple_pairs)
        )
        kappa_required = internal_edge_required(
            adjacency,
            context["component_a"],
            context["component_b"],
            internal_edges,
            metric=KAPPA,
            rescue=route_b_kappa,
        )
        lambda_required = internal_edge_required(
            adjacency,
            context["component_a"],
            context["component_b"],
            internal_edges,
            metric=LAMBDA,
            rescue=route_b_lambda,
        )
        if route_b_kappa:
            kappa_rescues.append(triple)
            kappa_rescues_by_internal_edge_count[internal_count] += 1
        if route_b_lambda:
            lambda_rescues.append(triple)
            lambda_rescues_by_internal_edge_count[internal_count] += 1
        required_kappa += int(kappa_required)
        required_lambda += int(lambda_required)
        distributed_vertex += int(three_node_vertex)
        distributed_edge += int(three_node_edge)
        if route_b_kappa and not task["group_kappa_rescues"]:
            monotonicity_failures += 1
        if route_b_lambda and not task["group_lambda_rescues"]:
            monotonicity_failures += 1

        flags = build_flags(
            {
                "kappa_scope": kappa_scope,
                "lambda_scope": lambda_scope,
                "kappa_route_a_rescue": route_a["kappa_rescue"],
                "lambda_route_a_rescue": route_a["lambda_rescue"],
                "kappa_route_b_rescue": route_b_kappa,
                "lambda_route_b_rescue": route_b_lambda,
                "distributed_vertex_coverage": three_node_vertex,
                "distributed_edge_coverage": three_node_edge,
                "internal_edge_required_kappa": kappa_required,
                "internal_edge_required_lambda": lambda_required,
                "three_node_vertex_coverage": three_node_vertex,
                "three_node_edge_coverage": three_node_edge,
            },
            internal_count,
        )
        ledger.extend(
            LEDGER_RECORD.pack(
                stratum_index,
                first,
                second,
                third,
                flags,
                int(route_a["uncovered_original_vertices"]),
                int(route_a["uncovered_original_edges"]),
                pack_separators(
                    int(route_a["new_vertex_separator_mask"]),
                    len(route_a["new_edge_separators"]),
                ),
            )
        )

    expected = math.comb(len(words), 3)
    if len(ledger) != expected * LEDGER_RECORD.size:
        raise RuntimeError("Stratum triple denominator mismatch")
    if route_disagreements:
        raise RuntimeError(f"Route A/B disagreement in stratum {stratum_index}")
    if monotonicity_failures:
        raise RuntimeError(f"Monotonicity failure in stratum {stratum_index}")
    return {
        "stratum_index": stratum_index,
        "ledger": bytes(ledger),
        "triple_count": expected,
        "kappa_rescue_count": len(kappa_rescues),
        "lambda_rescue_count": len(lambda_rescues),
        "kappa_examples": [list(row) for row in kappa_rescues[:20]],
        "lambda_examples": [list(row) for row in lambda_rescues[:20]],
        "internal_edge_distribution": dict(internal_edge_distribution),
        "internal_edge_required_kappa_count": required_kappa,
        "internal_edge_required_lambda_count": required_lambda,
        "three_node_vertex_coverage_count": distributed_vertex,
        "three_node_edge_coverage_count": distributed_edge,
        "kappa_rescues_by_internal_edge_count": dict(kappa_rescues_by_internal_edge_count),
        "lambda_rescues_by_internal_edge_count": dict(lambda_rescues_by_internal_edge_count),
    }


def build_payloads(
    phase95: dict[str, Any],
    phase97: dict[str, Any],
    phase102: dict[str, Any],
    phase103_results: dict[str, Any],
    phase103_manifest: dict[str, Any],
    *,
    workers: int,
) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    if len(phase95["cube_nodes"]) != EXPECTED_CUBE_COUNT:
        raise RuntimeError("Fase-95 cube denominator mismatch")
    if len(phase102["audit_records"]) != EXPECTED_UNIT_AUDIT_COUNT:
        raise RuntimeError("Fase-102 unit-audit denominator mismatch")
    if len(phase102["target_cut_audits"]) != EXPECTED_TARGET_COUNT:
        raise RuntimeError("Fase-102 target denominator mismatch")
    if phase102["status"] != "EXACT_CUT_COVERAGE_RESCUE_LAW_VERIFIED":
        raise RuntimeError("Fase-102 law is not closed")
    if any(
        not row["law_match"]
        or bool(row["vertex_direct"]) != bool(row["vertex_phase100"])
        or bool(row["edge_direct"]) != bool(row["edge_phase100"])
        for row in phase102["audit_records"]
    ):
        raise RuntimeError("Fase-102 unit-audit replay mismatch")
    if phase103_results["status"] != "PAIRWISE_SYNERGY_ATLAS_BUILT":
        raise RuntimeError("Fase-103 atlas is not closed")

    pair_replay = validate_phase103_replay(phase103_results, phase103_manifest)
    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    pairs = {
        (row["cube_key"], int(row["pair_index"])): row
        for row in phase97["component_pairs"]
    }
    target_audits = {
        (row["cube_key"], int(row["pair_index"])): row
        for row in phase102["target_cut_audits"]
    }
    unresolved = [
        row
        for row in phase103_results["strata"]
        if row["kappa_minimal_cardinality"] == AT_LEAST_THREE
        or row["lambda_minimal_cardinality"] == AT_LEAST_THREE
    ]
    unresolved.sort(
        key=lambda row: (row["cube_key"], int(row["pair_index"]), int(row["period"]))
    )
    if len(unresolved) != EXPECTED_STRATUM_COUNT:
        raise RuntimeError("Fase-104 stratum denominator mismatch")
    if sum(row["kappa_minimal_cardinality"] == AT_LEAST_THREE for row in unresolved) != EXPECTED_KAPPA_STRATA:
        raise RuntimeError("Fase-104 kappa denominator mismatch")
    if sum(row["lambda_minimal_cardinality"] == AT_LEAST_THREE for row in unresolved) != EXPECTED_LAMBDA_STRATA:
        raise RuntimeError("Fase-104 lambda denominator mismatch")

    contexts: dict[tuple[str, int], dict[str, Any]] = {}
    tasks = []
    for stratum_index, source in enumerate(unresolved):
        key = (source["cube_key"], int(source["pair_index"]))
        pair = pairs[key]
        if key not in contexts:
            contexts[key] = phase103.build_context(
                cubes[key[0]], pair, pair["physical_class_sha256"], target_audits[key]
            )
        context = contexts[key]
        period = int(source["period"])
        historical_words = tuple(
            index
            for index, node in enumerate(context["nodes"])
            if node["category"] == HISTORICAL_CATEGORY
            and int(node["ledger"]["source_period"]) == period
        )
        if len(historical_words) != int(source["node_count"]):
            raise RuntimeError("Historical stratum node-count mismatch")
        old_index = int(source["stratum_index"])
        replay = pair_replay[old_index]
        tasks.append(
            {
                "stratum_index": stratum_index,
                "source_stratum_index": old_index,
                "historical_words": historical_words,
                "kappa_scope": source["kappa_minimal_cardinality"] == AT_LEAST_THREE,
                "lambda_scope": source["lambda_minimal_cardinality"] == AT_LEAST_THREE,
                "group_kappa_rescues": source["relations"][KAPPA] == "COLLECTIVE_ONLY_PERIOD_RESCUE",
                "group_lambda_rescues": source["relations"][LAMBDA] == "COLLECTIVE_ONLY_PERIOD_RESCUE",
                "context": {
                    "component_a": context["component_a"],
                    "component_b": context["component_b"],
                    "adjacency": context["adjacency"],
                    "critical_vertices": context["critical_vertices"],
                    "critical_edges": context["critical_edges"],
                },
                "seen_pairs": replay["seen"],
                "complete_vertex_pairs": replay["vertex_complete"],
                "complete_edge_pairs": replay["edge_complete"],
            }
        )

    completed: dict[int, dict[str, Any]] = {}
    if workers == 1:
        for task in tasks:
            row = process_stratum(task)
            completed[int(row["stratum_index"])] = row
            print(f"completed {len(completed)}/{len(tasks)} strata", flush=True)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {executor.submit(process_stratum, task): task for task in tasks}
            for future in concurrent.futures.as_completed(futures):
                row = future.result()
                completed[int(row["stratum_index"])] = row
                print(f"completed {len(completed)}/{len(tasks)} strata", flush=True)
    if len(completed) != EXPECTED_STRATUM_COUNT:
        raise RuntimeError("Worker result denominator mismatch")

    ledger = b"".join(completed[index]["ledger"] for index in range(len(tasks)))
    strata = []
    triples_by_period = Counter()
    triples_by_rule = Counter()
    kappa_by_period = Counter()
    lambda_by_period = Counter()
    kappa_by_rule = Counter()
    lambda_by_rule = Counter()
    internal_edges = Counter()
    internal_edges_by_period: dict[int, Counter] = {}
    kappa_rescues_by_period = Counter()
    lambda_rescues_by_period = Counter()
    kappa_rescues_by_rule = Counter()
    lambda_rescues_by_rule = Counter()
    kappa_rescues_by_internal_edge_count = Counter()
    lambda_rescues_by_internal_edge_count = Counter()
    for stratum_index, source in enumerate(unresolved):
        row = completed[stratum_index]
        period = int(source["period"])
        rule = int(source["rule"])
        kappa_scope = source["kappa_minimal_cardinality"] == AT_LEAST_THREE
        lambda_scope = source["lambda_minimal_cardinality"] == AT_LEAST_THREE
        distribution = Counter({int(k): int(v) for k, v in row["internal_edge_distribution"].items()})
        internal_edges.update(distribution)
        internal_edges_by_period.setdefault(period, Counter()).update(distribution)
        triples_by_period[period] += row["triple_count"]
        triples_by_rule[rule] += row["triple_count"]
        if kappa_scope:
            kappa_by_period[period] += row["triple_count"]
            kappa_by_rule[rule] += row["triple_count"]
            kappa_rescues_by_period[period] += row["kappa_rescue_count"]
            kappa_rescues_by_rule[rule] += row["kappa_rescue_count"]
            kappa_rescues_by_internal_edge_count.update(
                {int(k): int(v) for k, v in row["kappa_rescues_by_internal_edge_count"].items()}
            )
        if lambda_scope:
            lambda_by_period[period] += row["triple_count"]
            lambda_by_rule[rule] += row["triple_count"]
            lambda_rescues_by_period[period] += row["lambda_rescue_count"]
            lambda_rescues_by_rule[rule] += row["lambda_rescue_count"]
            lambda_rescues_by_internal_edge_count.update(
                {int(k): int(v) for k, v in row["lambda_rescues_by_internal_edge_count"].items()}
            )
        strata.append(
            {
                "stratum_index": stratum_index,
                "phase103_stratum_index": int(source["stratum_index"]),
                "cube_key": source["cube_key"],
                "pair_index": int(source["pair_index"]),
                "rule": rule,
                "background_index": int(source["background_index"]),
                "period": period,
                "node_count": int(source["node_count"]),
                "triple_count": int(row["triple_count"]),
                "kappa_scope": kappa_scope,
                "lambda_scope": lambda_scope,
                "kappa_triple_rescue_count": int(row["kappa_rescue_count"]),
                "lambda_triple_rescue_count": int(row["lambda_rescue_count"]),
                "kappa_minimal_cardinality": triple_minimal_label(kappa_scope, int(row["kappa_rescue_count"])),
                "lambda_minimal_cardinality": triple_minimal_label(lambda_scope, int(row["lambda_rescue_count"])),
                "kappa_rescuing_triple_examples": row["kappa_examples"],
                "lambda_rescuing_triple_examples": row["lambda_examples"],
                "internal_edge_distribution": dict(sorted(distribution.items())),
                "internal_edge_required_kappa_count": int(row["internal_edge_required_kappa_count"]),
                "internal_edge_required_lambda_count": int(row["internal_edge_required_lambda_count"]),
                "three_node_vertex_coverage_count": int(row["three_node_vertex_coverage_count"]),
                "three_node_edge_coverage_count": int(row["three_node_edge_coverage_count"]),
                "kappa_rescues_by_internal_edge_count": {
                    edge_count: int(row["kappa_rescues_by_internal_edge_count"].get(edge_count, 0))
                    for edge_count in range(3)
                },
                "lambda_rescues_by_internal_edge_count": {
                    edge_count: int(row["lambda_rescues_by_internal_edge_count"].get(edge_count, 0))
                    for edge_count in range(3)
                },
            }
        )

    total_triples = sum(row["triple_count"] for row in strata)
    kappa_trials = sum(row["triple_count"] for row in strata if row["kappa_scope"])
    lambda_trials = sum(row["triple_count"] for row in strata if row["lambda_scope"])
    if total_triples != EXPECTED_TRIPLE_COUNT:
        raise RuntimeError("Global triple denominator mismatch")
    if (kappa_trials, lambda_trials) != (EXPECTED_KAPPA_TRIALS, EXPECTED_LAMBDA_TRIALS):
        raise RuntimeError("Metric triple denominator mismatch")
    if dict(sorted(triples_by_period.items())) != EXPECTED_TRIPLES_BY_PERIOD:
        raise RuntimeError("Triple period distribution mismatch")
    if dict(sorted(triples_by_rule.items())) != EXPECTED_TRIPLES_BY_RULE:
        raise RuntimeError("Triple rule distribution mismatch")
    if dict(sorted(kappa_by_period.items())) != EXPECTED_KAPPA_BY_PERIOD:
        raise RuntimeError("Kappa period denominator mismatch")
    if dict(sorted(lambda_by_period.items())) != EXPECTED_LAMBDA_BY_PERIOD:
        raise RuntimeError("Lambda period denominator mismatch")
    if dict(sorted(kappa_by_rule.items())) != EXPECTED_KAPPA_BY_RULE:
        raise RuntimeError("Kappa rule denominator mismatch")
    if dict(sorted(lambda_by_rule.items())) != EXPECTED_LAMBDA_BY_RULE:
        raise RuntimeError("Lambda rule denominator mismatch")
    complete_internal = {edge_count: int(internal_edges[edge_count]) for edge_count in range(4)}
    if complete_internal != EXPECTED_INTERNAL_EDGE_DISTRIBUTION:
        raise RuntimeError("Internal-edge geometry mismatch")
    for period, expected in EXPECTED_INTERNAL_EDGES_BY_PERIOD.items():
        actual = {edge_count: int(internal_edges_by_period[period][edge_count]) for edge_count in range(4)}
        if actual != expected:
            raise RuntimeError(f"Internal-edge geometry mismatch for T={period}")
    if len(ledger) != EXPECTED_TRIPLE_COUNT * LEDGER_RECORD.size:
        raise RuntimeError("Ledger byte-size mismatch")

    ledger_sha = hashlib.sha256(ledger).hexdigest()
    summary = {
        "cube_count": EXPECTED_CUBE_COUNT,
        "target_count": EXPECTED_TARGET_COUNT,
        "phase103_stratum_replay_count": EXPECTED_PHASE103_STRATA,
        "phase103_pair_replay_count": EXPECTED_PHASE103_PAIRS,
        "triple_stratum_count": EXPECTED_STRATUM_COUNT,
        "kappa_stratum_count": EXPECTED_KAPPA_STRATA,
        "lambda_stratum_count": EXPECTED_LAMBDA_STRATA,
        "triple_intervention_count": total_triples,
        "kappa_trial_count": kappa_trials,
        "lambda_trial_count": lambda_trials,
        "kappa_exactly_three_strata": sum(row["kappa_minimal_cardinality"] == "EXACTLY_3" for row in strata),
        "kappa_at_least_four_strata": sum(row["kappa_minimal_cardinality"] == "AT_LEAST_4" for row in strata),
        "lambda_exactly_three_strata": sum(row["lambda_minimal_cardinality"] == "EXACTLY_3" for row in strata),
        "lambda_at_least_four_strata": sum(row["lambda_minimal_cardinality"] == "AT_LEAST_4" for row in strata),
        "kappa_triple_rescue_count": sum(row["kappa_triple_rescue_count"] for row in strata if row["kappa_scope"]),
        "lambda_triple_rescue_count": sum(row["lambda_triple_rescue_count"] for row in strata if row["lambda_scope"]),
        "internal_edge_distribution": complete_internal,
        "internal_edge_required_kappa_count": sum(row["internal_edge_required_kappa_count"] for row in strata if row["kappa_scope"]),
        "internal_edge_required_lambda_count": sum(row["internal_edge_required_lambda_count"] for row in strata if row["lambda_scope"]),
        "three_node_vertex_coverage_count": sum(row["three_node_vertex_coverage_count"] for row in strata if row["kappa_scope"]),
        "three_node_edge_coverage_count": sum(row["three_node_edge_coverage_count"] for row in strata if row["lambda_scope"]),
        "kappa_rescues_by_period": dict(sorted(kappa_rescues_by_period.items())),
        "lambda_rescues_by_period": dict(sorted(lambda_rescues_by_period.items())),
        "kappa_rescues_by_rule": dict(sorted(kappa_rescues_by_rule.items())),
        "lambda_rescues_by_rule": dict(sorted(lambda_rescues_by_rule.items())),
        "kappa_rescues_by_internal_edge_count": {
            edge_count: int(kappa_rescues_by_internal_edge_count[edge_count])
            for edge_count in range(3)
        },
        "lambda_rescues_by_internal_edge_count": {
            edge_count: int(lambda_rescues_by_internal_edge_count[edge_count])
            for edge_count in range(3)
        },
        "route_disagreement_count": 0,
        "monotonicity_failure_count": 0,
        "phase103_out_of_scope_bit_count": 0,
        "ledger_record_count": total_triples,
        "ledger_record_size": LEDGER_RECORD.size,
        "ledger_size": len(ledger),
        "ledger_sha256": ledger_sha,
        "workers": workers,
        "simulation_executed": False,
    }
    result = {
        "phase": 104,
        "status": "TRIPLE_SYNERGY_ATLAS_BUILT",
        "sources": {
            key: {"raw_sha256": value[0], "canonical_sha256": value[1]}
            for key, value in EXPECTED_HASHES.items()
        }
        | {"phase103_ledger_sha256": EXPECTED_PHASE103_LEDGER_SHA},
        "protocol": {
            "simulation_executed": False,
            "triple_order": "LEXICOGRAPHIC_UNORDERED",
            "route_a": "DIRECT_EXHAUSTIVE_REMOVAL_OF_ALL_ORIGINAL_AND_NEW_SEPARATORS",
            "route_b": "FRESH_INTEGER_MAX_FLOW_CAP_2",
            "phase103_pair_replay": "ALL_404054_RECORDS",
            "threshold_scan_executed": False,
            "metric_denominators_separate": True,
        },
        "summary": summary,
        "strata": strata,
        "preflight": {
            "strata_by_period": dict(sorted(Counter(row["period"] for row in strata).items())),
            "triples_by_period": dict(sorted(triples_by_period.items())),
            "triples_by_rule": dict(sorted(triples_by_rule.items())),
            "kappa_trials_by_period": dict(sorted(kappa_by_period.items())),
            "lambda_trials_by_period": dict(sorted(lambda_by_period.items())),
            "kappa_trials_by_rule": dict(sorted(kappa_by_rule.items())),
            "lambda_trials_by_rule": dict(sorted(lambda_by_rule.items())),
            "internal_edges_by_period": {
                period: {edge_count: int(counter[edge_count]) for edge_count in range(4)}
                for period, counter in sorted(internal_edges_by_period.items())
            },
        },
        "methodological_limits": [
            "EXACTLY_3 is proven only where every singleton and pair fails and at least one triple rescues.",
            "AT_LEAST_4 is a lower bound; quadruples and larger subsets are not enumerated here.",
            "Period labels index frozen historical-node families and are not treated as temporal causes.",
            "The atlas is restricted to 73 unresolved target-period strata in 48 frozen Q8 cubes.",
        ],
    }
    manifest = {
        "phase": 104,
        "ledger_file": LEDGER_PATH.name,
        "byte_order": "little-endian",
        "record_format": LEDGER_FORMAT,
        "record_size": LEDGER_RECORD.size,
        "record_count": total_triples,
        "ledger_size": len(ledger),
        "ledger_sha256": ledger_sha,
        "fields": LEDGER_FIELDS,
        "flag_bits": FLAG_BITS,
        "packed_new_separators": {
            "new_vertex_separator_mask": {"bits": "0..2", "width": 3},
            "new_edge_separator_count": {"bits": "3..7", "width": 5},
        },
        "internal_edge_count_bits": "flags bits 0..1",
        "stratum_index_source": f"{RESULTS_PATH.name}::strata[].stratum_index",
        "decoder": "decode_phase103_triple_synergy_ledger.py",
    }
    return result, manifest, ledger


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Rule 73/109 triple historical synergy atlas - Fase 104",
        "",
        "## Gates and scope",
        "",
        f"- Fase-103 strata/pairs replayed: `{summary['phase103_stratum_replay_count']}` / `{summary['phase103_pair_replay_count']}`",
        f"- Triple strata: `{summary['triple_stratum_count']}`",
        f"- Kappa strata/trials: `{summary['kappa_stratum_count']}` / `{summary['kappa_trial_count']}`",
        f"- Lambda strata/trials: `{summary['lambda_stratum_count']}` / `{summary['lambda_trial_count']}`",
        f"- Unique unordered triple interventions: `{summary['triple_intervention_count']}`",
        f"- Route disagreements: `{summary['route_disagreement_count']}`",
        f"- Monotonicity failures: `{summary['monotonicity_failure_count']}`",
        f"- Fase-103 out-of-scope bits: `{summary['phase103_out_of_scope_bit_count']}`",
        "",
        "## Minimum observed cardinality",
        "",
        "| Metric | Exactly 3 strata | At least 4 strata | Rescuing triple trials |",
        "|---|---:|---:|---:|",
        f"| kappa_v | {summary['kappa_exactly_three_strata']} | {summary['kappa_at_least_four_strata']} | {summary['kappa_triple_rescue_count']} |",
        f"| lambda_e | {summary['lambda_exactly_three_strata']} | {summary['lambda_at_least_four_strata']} | {summary['lambda_triple_rescue_count']} |",
        "",
        "## Triple interaction",
        "",
        f"- Internal-edge distribution: `{summary['internal_edge_distribution']}`",
        f"- Kappa rescues requiring an internal Hamming-1 edge: `{summary['internal_edge_required_kappa_count']}`",
        f"- Lambda rescues requiring an internal Hamming-1 edge: `{summary['internal_edge_required_lambda_count']}`",
        f"- Genuine three-node original vertex-cut coverage: `{summary['three_node_vertex_coverage_count']}`",
        f"- Genuine three-node original edge-cut coverage: `{summary['three_node_edge_coverage_count']}`",
        f"- Kappa rescues by internal-edge count: `{summary['kappa_rescues_by_internal_edge_count']}`",
        f"- Lambda rescues by internal-edge count: `{summary['lambda_rescues_by_internal_edge_count']}`",
        f"- Kappa rescues by period/rule: `{summary['kappa_rescues_by_period']}` / `{summary['kappa_rescues_by_rule']}`",
        f"- Lambda rescues by period/rule: `{summary['lambda_rescues_by_period']}` / `{summary['lambda_rescues_by_rule']}`",
        "",
        "## Binary ledger",
        "",
        f"- Records: `{summary['ledger_record_count']}`",
        f"- Record size: `{summary['ledger_record_size']}` bytes",
        f"- Ledger size: `{summary['ledger_size']}` bytes",
        f"- SHA-256: `{summary['ledger_sha256']}`",
        "- The manifest specifies every field, bit and packed subfield; the decoder uses only the Python standard library.",
        "",
        "## Verdict",
        "",
        f"`{payload['status']}`",
        "",
        "## Methodological limits",
        "",
    ]
    lines.extend(f"- {item}" for item in payload["methodological_limits"])
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Fase-104 triple-synergy audit")
    parser.add_argument("--workers", type=int, default=5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    phase95 = read_and_gate(PHASE95_PATH, EXPECTED_HASHES["phase95"])
    phase97 = read_and_gate(PHASE97_PATH, EXPECTED_HASHES["phase97"])
    phase102 = read_and_gate(PHASE102_PATH, EXPECTED_HASHES["phase102"])
    phase103_results = read_and_gate(
        PHASE103_RESULTS_PATH, EXPECTED_HASHES["phase103_results"]
    )
    phase103_manifest = read_and_gate(
        PHASE103_MANIFEST_PATH, EXPECTED_HASHES["phase103_manifest"]
    )
    result, manifest, ledger = build_payloads(
        phase95,
        phase97,
        phase102,
        phase103_results,
        phase103_manifest,
        workers=args.workers,
    )
    if hashlib.sha256(ledger).hexdigest() != manifest["ledger_sha256"]:
        raise RuntimeError("Ledger digest changed before write")
    atomic_write_bytes(LEDGER_PATH, ledger)
    atomic_write_text(MANIFEST_PATH, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    atomic_write_text(RESULTS_PATH, json.dumps(result, indent=2, sort_keys=True) + "\n")
    atomic_write_text(REPORT_PATH, render_report(result))
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
