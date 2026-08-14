from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"

PHASE95_PATH = OUTPUT_DIR / "phase94_hypercube_completion_results.json"
PHASE97_PATH = OUTPUT_DIR / "phase96_bridge_robustness_results.json"
PHASE100_PATH = OUTPUT_DIR / "phase99_unit_cardinality_period_potency_results.json"
PHASE101_PATH = OUTPUT_DIR / "phase100_measured_geometry_matching_results.json"
RESULTS_PATH = OUTPUT_DIR / "phase101_cut_coverage_law_results.json"
REPORT_PATH = OUTPUT_DIR / "phase101_cut_coverage_law_report.md"

EXPECTED_HASHES = {
    "phase95": {
        "raw": "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3",
        "canonical": "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429",
    },
    "phase97": {
        "raw": "3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858",
        "canonical": "85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b",
    },
    "phase100": {
        "raw": "39ec272b72c54f07c0996064c3d755fff9d4b6690fdfdbe3eb4d771ac0710c8c",
        "canonical": "f79e047d22dddb375db7f351bc9bdd55b978ce29ed22e9c22d9195fb70935d22",
    },
    "phase101": {
        "raw": "e8ad1f10fc066c4e22ae5e14556d8794e2d98c3bdff19cbdc69c9df8889520f7",
        "canonical": "53281bd7493a573faad25852e87abcd03797c56e83851719b35deba6180943f2",
    },
}

EXPECTED_CUBE_COUNT = 48
EXPECTED_TARGET_COUNT = 219
EXPECTED_EXPOSURE_COUNT = 43425
EXPECTED_VERTEX_CUT_TOTAL = 411
EXPECTED_EDGE_CUT_TOTAL = 394
EXPECTED_VERTEX_CUTS_BY_TARGET = {1: 103, 2: 54, 3: 54, 4: 4, 5: 2, 6: 2}
EXPECTED_EDGE_CUTS_BY_TARGET = {1: 90, 2: 93, 3: 28, 4: 6, 5: 2}
EXPECTED_WEIGHTED_VERTEX_CUTS = {1: 20051, 2: 10825, 3: 10854, 4: 896, 5: 403, 6: 396}
EXPECTED_WEIGHTED_EDGE_CUTS = {1: 17347, 2: 18571, 3: 5812, 4: 1299, 5: 396}
EXPECTED_PREDICTED_JOINT = {
    "NEITHER": 41859,
    "EDGE_ONLY": 61,
    "VERTEX_ONLY": 0,
    "BOTH": 1505,
}
EXPECTED_MATCH_PARTITIONS = {
    "MATCHED_GEOMETRY": {"NEITHER": 31493, "EDGE_ONLY": 0, "VERTEX_ONLY": 0, "BOTH": 189},
    "UNMATCHED_GEOMETRY": {"NEITHER": 10366, "EDGE_ONLY": 61, "VERTEX_ONLY": 0, "BOTH": 1316},
}
HISTORICAL_CATEGORY = "HISTORICAL_SOURCE_POSITIVE"
LONG_CATEGORY = "LONG_PERIOD_CAP_CANDIDATE"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_and_gate(path: Path, expected: dict[str, str]) -> dict[str, Any]:
    raw = raw_sha256(path)
    if raw != expected["raw"]:
        raise RuntimeError(f"Raw SHA mismatch for {path.name}: {raw}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    canonical = canonical_sha256(payload)
    if canonical != expected["canonical"]:
        raise RuntimeError(f"Canonical SHA mismatch for {path.name}: {canonical}")
    return payload


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def q8_neighbors(word: int) -> tuple[int, ...]:
    return tuple(word ^ (1 << bit) for bit in range(8))


def build_q8_adjacency(allowed: set[int]) -> dict[int, set[int]]:
    return {
        word: {neighbor for neighbor in q8_neighbors(word) if neighbor in allowed}
        for word in allowed
    }


def graph_edges(adjacency: dict[int, set[int]]) -> tuple[tuple[int, int], ...]:
    return tuple(
        sorted(
            (source, target)
            for source, neighbors in adjacency.items()
            for target in neighbors
            if source < target
        )
    )


def reachable(
    adjacency: dict[int, set[int]],
    starts: Iterable[int],
    *,
    removed_vertex: int | None = None,
    removed_edge: tuple[int, int] | None = None,
) -> set[int]:
    blocked_edge = frozenset(removed_edge) if removed_edge is not None else None
    seen = {word for word in starts if word in adjacency and word != removed_vertex}
    queue = deque(sorted(seen))
    while queue:
        source = queue.popleft()
        for target in adjacency[source]:
            if target == removed_vertex or target in seen:
                continue
            if blocked_edge is not None and frozenset((source, target)) == blocked_edge:
                continue
            seen.add(target)
            queue.append(target)
    return seen


def terminals_connected(
    adjacency: dict[int, set[int]],
    component_a: set[int],
    component_b: set[int],
    *,
    removed_vertex: int | None = None,
    removed_edge: tuple[int, int] | None = None,
) -> bool:
    return bool(
        reachable(
            adjacency,
            component_a,
            removed_vertex=removed_vertex,
            removed_edge=removed_edge,
        )
        & component_b
    )


def shortest_distances(
    adjacency: dict[int, set[int]], starts: Iterable[int]
) -> dict[int, int]:
    distances = {word: 0 for word in starts if word in adjacency}
    queue = deque(sorted(distances))
    while queue:
        source = queue.popleft()
        for target in adjacency[source]:
            if target not in distances:
                distances[target] = distances[source] + 1
                queue.append(target)
    return distances


def enumerate_terminal_cuts(
    adjacency: dict[int, set[int]], component_a: set[int], component_b: set[int]
) -> tuple[tuple[int, ...], tuple[tuple[int, int], ...]]:
    if not terminals_connected(adjacency, component_a, component_b):
        raise RuntimeError("Base graph does not connect terminal components")
    removable_vertices = sorted(set(adjacency) - component_a - component_b)
    critical_vertices = tuple(
        vertex
        for vertex in removable_vertices
        if not terminals_connected(
            adjacency, component_a, component_b, removed_vertex=vertex
        )
    )
    critical_edges = tuple(
        edge
        for edge in graph_edges(adjacency)
        if not terminals_connected(
            adjacency, component_a, component_b, removed_edge=edge
        )
    )
    return critical_vertices, critical_edges


def add_unit_node(
    adjacency: dict[int, set[int]], word: int
) -> tuple[dict[int, set[int]], set[int]]:
    if word in adjacency:
        raise RuntimeError("Unit intervention node already belongs to F1")
    neighbors = {neighbor for neighbor in q8_neighbors(word) if neighbor in adjacency}
    augmented = {node: set(targets) for node, targets in adjacency.items()}
    augmented[word] = set(neighbors)
    for neighbor in neighbors:
        augmented[neighbor].add(word)
    return augmented, neighbors


def direct_unit_rescue(
    adjacency: dict[int, set[int]], component_a: set[int], component_b: set[int]
) -> tuple[bool, bool, tuple[int, ...], tuple[tuple[int, int], ...]]:
    critical_vertices, critical_edges = enumerate_terminal_cuts(
        adjacency, component_a, component_b
    )
    return (
        len(critical_vertices) == 0,
        len(critical_edges) == 0,
        critical_vertices,
        critical_edges,
    )


def homogeneity_status(values: Iterable[bool]) -> str:
    observed = set(bool(value) for value in values)
    if observed == {True}:
        return "ALL_TRUE"
    if observed == {False}:
        return "ALL_FALSE"
    if observed == {False, True}:
        return "MIXED"
    return "EMPTY"


def confusion_matrix(rows: list[dict[str, Any]], prefix: str) -> dict[str, int]:
    output = Counter()
    for row in rows:
        predicted = bool(row[f"{prefix}_predicted"])
        actual = bool(row[f"{prefix}_direct"])
        if predicted and actual:
            output["TP"] += 1
        elif predicted:
            output["FP"] += 1
        elif actual:
            output["FN"] += 1
        else:
            output["TN"] += 1
    return {key: output[key] for key in ("TP", "FP", "TN", "FN")}


def joint_label(vertex: bool, edge: bool) -> str:
    if vertex and edge:
        return "BOTH"
    if vertex:
        return "VERTEX_ONLY"
    if edge:
        return "EDGE_ONLY"
    return "NEITHER"


def connectivity_rescued(value: int) -> bool:
    return int(value) >= 2


def compact_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "exposure_count": len(rows),
        "predicted_joint_distribution": dict(
            sorted(Counter(row["predicted_joint"] for row in rows).items())
        ),
        "direct_joint_distribution": dict(
            sorted(Counter(row["direct_joint"] for row in rows).items())
        ),
        "vertex_confusion": confusion_matrix(rows, "vertex"),
        "edge_confusion": confusion_matrix(rows, "edge"),
        "law_mismatch_count": sum(not row["law_match"] for row in rows),
    }


def grouped_stats(rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row[field]].append(row)
    return {str(key): compact_stats(selected) for key, selected in sorted(grouped.items())}


def law_verdict(records: list[dict[str, Any]]) -> str:
    return (
        "EXACT_CUT_COVERAGE_RESCUE_LAW_VERIFIED"
        if all(row["law_match"] for row in records)
        else "CUT_COVERAGE_RESCUE_LAW_REJECTED"
    )


def build_context(
    cube: dict[str, Any], pair: dict[str, Any], target_class: str
) -> dict[str, Any]:
    nodes = cube["nodes"]
    component_a = {int(word, 2) for word in pair["left_component_words"]}
    component_b = {int(word, 2) for word in pair["right_component_words"]}
    allowed = {
        word
        for word, node in enumerate(nodes)
        if node["physical_class_sha256"] == target_class
        or node["category"] == LONG_CATEGORY
    }
    adjacency = build_q8_adjacency(allowed)
    critical_vertices, critical_edges = enumerate_terminal_cuts(
        adjacency, component_a, component_b
    )
    expected_vertices = tuple(
        sorted(int(row["word_value"]) for row in pair["g_min"]["individually_critical_vertices"])
    )
    expected_edges = tuple(
        sorted(tuple(sorted(map(int, edge))) for edge in pair["g_min"]["individually_critical_edges"])
    )
    if critical_vertices != expected_vertices or critical_edges != expected_edges:
        raise RuntimeError("Independent critical-cut enumeration disagrees with Fase 97")
    if int(pair["g_min"]["kappa_v"]) != 1 or int(pair["g_min"]["lambda_e"]) != 1:
        raise RuntimeError("Fase 102 target is not a unit bottleneck")
    vertex_partitions = []
    for vertex in critical_vertices:
        left = reachable(adjacency, component_a, removed_vertex=vertex)
        right = reachable(adjacency, component_b, removed_vertex=vertex)
        if left & component_b or right & component_a or left & right:
            raise RuntimeError("Critical-vertex partition is inconsistent")
        vertex_partitions.append((left, right))
    edge_partitions = []
    for edge in critical_edges:
        left = reachable(adjacency, component_a, removed_edge=edge)
        right = reachable(adjacency, component_b, removed_edge=edge)
        if left & component_b or right & component_a or left & right:
            raise RuntimeError("Critical-edge partition is inconsistent")
        edge_partitions.append((left, right))
    return {
        "nodes": nodes,
        "target_class": target_class,
        "component_a": component_a,
        "component_b": component_b,
        "allowed": allowed,
        "adjacency": adjacency,
        "critical_vertices": critical_vertices,
        "critical_edges": critical_edges,
        "vertex_partitions": vertex_partitions,
        "edge_partitions": edge_partitions,
        "distance_a": shortest_distances(adjacency, component_a),
        "distance_b": shortest_distances(adjacency, component_b),
    }


def bypass_count(neighbors: set[int], partitions: list[tuple[set[int], set[int]]]) -> int:
    return sum(bool(neighbors & left) and bool(neighbors & right) for left, right in partitions)


def geometry_signature(context: dict[str, Any], word: int, neighbors: set[int]) -> dict[str, Any]:
    nodes = context["nodes"]
    roles = Counter()
    for neighbor in neighbors:
        if neighbor in context["component_a"]:
            roles["A"] += 1
        elif neighbor in context["component_b"]:
            roles["B"] += 1
        elif nodes[neighbor]["physical_class_sha256"] == context["target_class"]:
            roles["F0"] += 1
        else:
            roles["OTHER_F1"] += 1
    distance_a = min(
        (1 + context["distance_a"][neighbor] for neighbor in neighbors if neighbor in context["distance_a"]),
        default="UNREACHABLE",
    )
    distance_b = min(
        (1 + context["distance_b"][neighbor] for neighbor in neighbors if neighbor in context["distance_b"]),
        default="UNREACHABLE",
    )
    critical_vertex_set = set(context["critical_vertices"])
    return {
        "f1_degree": len(neighbors),
        "neighbors_A": roles["A"],
        "neighbors_B": roles["B"],
        "neighbors_F0_nonterminal": roles["F0"],
        "neighbors_other_F1": roles["OTHER_F1"],
        "distance_to_A": distance_a,
        "distance_to_B": distance_b,
        "critical_vertex_count": len(context["critical_vertices"]),
        "bypassed_critical_vertex_count": bypass_count(neighbors, context["vertex_partitions"]),
        "adjacent_critical_vertex_count": len(neighbors & critical_vertex_set),
        "critical_edge_count": len(context["critical_edges"]),
        "bypassed_critical_edge_count": bypass_count(neighbors, context["edge_partitions"]),
        "incident_critical_edge_endpoint_count": sum(
            int(edge[0] in neighbors) + int(edge[1] in neighbors)
            for edge in context["critical_edges"]
        ),
    }


def build_payload(
    phase95: dict[str, Any],
    phase97: dict[str, Any],
    phase100: dict[str, Any],
    phase101: dict[str, Any],
) -> dict[str, Any]:
    if len(phase95["cube_nodes"]) != EXPECTED_CUBE_COUNT:
        raise RuntimeError("Fase-95 cube denominator mismatch")
    if len(phase100["exposures"]) != EXPECTED_EXPOSURE_COUNT:
        raise RuntimeError("Fase-100 exposure denominator mismatch")
    if len(phase101["exposures"]) != EXPECTED_EXPOSURE_COUNT:
        raise RuntimeError("Fase-101 exposure denominator mismatch")

    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    pairs = {(row["cube_key"], int(row["pair_index"])): row for row in phase97["component_pairs"]}
    phase101_lookup = {
        (row["cube_key"], int(row["pair_index"]), int(row["word_int"])): row
        for row in phase101["exposures"]
    }
    if len(phase101_lookup) != EXPECTED_EXPOSURE_COUNT:
        raise RuntimeError("Fase-101 exposure identity duplication")

    target_classes: dict[tuple[str, int], str] = {}
    exposure_counts = Counter()
    for row in phase100["exposures"]:
        key = (row["cube_key"], int(row["pair_index"]))
        previous = target_classes.setdefault(key, row["physical_class_sha256"])
        if previous != row["physical_class_sha256"]:
            raise RuntimeError("Target physical-class conflict")
        exposure_counts[key] += 1
    if len(target_classes) != EXPECTED_TARGET_COUNT:
        raise RuntimeError("Fase-102 target denominator mismatch")

    contexts = {
        key: build_context(cubes[key[0]], pairs[key], target_class)
        for key, target_class in sorted(target_classes.items())
    }
    vertex_counts = Counter(len(context["critical_vertices"]) for context in contexts.values())
    edge_counts = Counter(len(context["critical_edges"]) for context in contexts.values())
    if dict(sorted(vertex_counts.items())) != EXPECTED_VERTEX_CUTS_BY_TARGET:
        raise RuntimeError("Critical-vertex target distribution mismatch")
    if dict(sorted(edge_counts.items())) != EXPECTED_EDGE_CUTS_BY_TARGET:
        raise RuntimeError("Critical-edge target distribution mismatch")
    if sum(len(context["critical_vertices"]) for context in contexts.values()) != EXPECTED_VERTEX_CUT_TOTAL:
        raise RuntimeError("Critical-vertex total mismatch")
    if sum(len(context["critical_edges"]) for context in contexts.values()) != EXPECTED_EDGE_CUT_TOTAL:
        raise RuntimeError("Critical-edge total mismatch")

    records = []
    replay_failures = []
    for source in phase100["exposures"]:
        key = (source["cube_key"], int(source["pair_index"]))
        identity = (key[0], key[1], int(source["word_int"]))
        context = contexts[key]
        node = context["nodes"][int(source["word_int"])]
        if (
            node["category"] != HISTORICAL_CATEGORY
            or node["word8"] != source["word8"]
            or int(node["ledger"]["source_period"]) != int(source["period"])
        ):
            raise RuntimeError("Historical node replay mismatch")
        augmented, neighbors = add_unit_node(context["adjacency"], int(source["word_int"]))
        signature = geometry_signature(context, int(source["word_int"]), neighbors)
        phase101_row = phase101_lookup[identity]
        if signature != phase101_row["geometry_signature"]:
            raise RuntimeError("Fase-101 geometry-signature replay mismatch")
        if canonical_sha256(signature) != phase101_row["geometry_signature_sha256"]:
            raise RuntimeError("Fase-101 geometry-signature SHA mismatch")

        vertex_total = len(context["critical_vertices"])
        edge_total = len(context["critical_edges"])
        vertex_bypassed = signature["bypassed_critical_vertex_count"]
        edge_bypassed = signature["bypassed_critical_edge_count"]
        vertex_predicted = vertex_bypassed == vertex_total
        edge_predicted = edge_bypassed == edge_total
        vertex_direct, edge_direct, direct_vertices, direct_edges = direct_unit_rescue(
            augmented, context["component_a"], context["component_b"]
        )
        vertex_actual = bool(source["vertex_rescued"])
        edge_actual = bool(source["edge_rescued"])
        if (
            vertex_direct != vertex_actual
            or edge_direct != edge_actual
            or (vertex_actual and edge_actual) != bool(source["same_node_both_rescued"])
            or connectivity_rescued(source["kappa_v"]) != vertex_actual
            or connectivity_rescued(source["lambda_e"]) != edge_actual
        ):
            replay_failures.append(identity)
        if vertex_predicted and not edge_predicted:
            raise RuntimeError("Predicted rescue violates kappa<=lambda")
        record = {
            "cube_key": key[0],
            "pair_index": key[1],
            "rule": int(source["rule"]),
            "word_int": int(source["word_int"]),
            "word8": source["word8"],
            "period": int(source["period"]),
            "geometry_match_status": phase101_row["geometry_match_status"],
            "vertex_cut_count": vertex_total,
            "vertex_bypassed_count": vertex_bypassed,
            "vertex_deficit": vertex_total - vertex_bypassed,
            "vertex_predicted": vertex_predicted,
            "vertex_direct": vertex_direct,
            "vertex_phase100": vertex_actual,
            "edge_cut_count": edge_total,
            "edge_bypassed_count": edge_bypassed,
            "edge_deficit": edge_total - edge_bypassed,
            "edge_predicted": edge_predicted,
            "edge_direct": edge_direct,
            "edge_phase100": edge_actual,
            "predicted_joint": joint_label(vertex_predicted, edge_predicted),
            "direct_joint": joint_label(vertex_direct, edge_direct),
            "direct_vertex_separator_count": len(direct_vertices),
            "direct_edge_separator_count": len(direct_edges),
            "law_match": vertex_predicted == vertex_direct and edge_predicted == edge_direct,
        }
        records.append(record)
    if replay_failures:
        raise RuntimeError(f"Direct audit disagrees with Fase 100: {replay_failures[:5]}")

    # Recompute Fase-101 matching status only after every outcome-blind signature is replayed.
    periods_by_geometry: dict[tuple[str, int, str], set[int]] = defaultdict(set)
    for source in phase101["exposures"]:
        periods_by_geometry[
            (
                source["cube_key"],
                int(source["pair_index"]),
                source["geometry_signature_sha256"],
            )
        ].add(int(source["period"]))
    for source in phase101["exposures"]:
        expected_status = (
            "MATCHED_GEOMETRY"
            if len(
                periods_by_geometry[
                    (
                        source["cube_key"],
                        int(source["pair_index"]),
                        source["geometry_signature_sha256"],
                    )
                ]
            )
            >= 2
            else "UNMATCHED_GEOMETRY"
        )
        if source["geometry_match_status"] != expected_status:
            raise RuntimeError("Fase-101 match-status replay mismatch")

    weighted_vertices = Counter()
    weighted_edges = Counter()
    for key, context in contexts.items():
        weighted_vertices[len(context["critical_vertices"])] += exposure_counts[key]
        weighted_edges[len(context["critical_edges"])] += exposure_counts[key]
    if dict(sorted(weighted_vertices.items())) != EXPECTED_WEIGHTED_VERTEX_CUTS:
        raise RuntimeError("Weighted critical-vertex distribution mismatch")
    if dict(sorted(weighted_edges.items())) != EXPECTED_WEIGHTED_EDGE_CUTS:
        raise RuntimeError("Weighted critical-edge distribution mismatch")

    predicted_joint = Counter(row["predicted_joint"] for row in records)
    for label in EXPECTED_PREDICTED_JOINT:
        predicted_joint.setdefault(label, 0)
    if dict(predicted_joint) != EXPECTED_PREDICTED_JOINT:
        raise RuntimeError("Frozen feature-only prediction distribution mismatch")
    match_partitions = {}
    for status in ("MATCHED_GEOMETRY", "UNMATCHED_GEOMETRY"):
        counts = Counter(
            row["predicted_joint"]
            for row in records
            if row["geometry_match_status"] == status
        )
        for label in EXPECTED_PREDICTED_JOINT:
            counts.setdefault(label, 0)
        match_partitions[status] = dict(counts)
    if match_partitions != EXPECTED_MATCH_PARTITIONS:
        raise RuntimeError("Frozen matched/unmatched prediction distribution mismatch")

    verdict = law_verdict(records)
    counterexamples = [row for row in records if not row["law_match"]]
    target_audits = [
        {
            "cube_key": key[0],
            "pair_index": key[1],
            "exposure_count": exposure_counts[key],
            "critical_vertices": list(context["critical_vertices"]),
            "critical_edges": [list(edge) for edge in context["critical_edges"]],
            "base_node_count": len(context["adjacency"]),
            "base_edge_count": len(graph_edges(context["adjacency"])),
        }
        for key, context in sorted(contexts.items())
    ]
    audit_stream_sha = hashlib.sha256(
        b"\n".join(canonical_json_bytes(row) for row in records)
    ).hexdigest()
    summary = {
        "cube_count": EXPECTED_CUBE_COUNT,
        "target_count": len(contexts),
        "exposure_count": len(records),
        "critical_vertex_total": EXPECTED_VERTEX_CUT_TOTAL,
        "critical_edge_total": EXPECTED_EDGE_CUT_TOTAL,
        "predicted_joint_distribution": dict(sorted(predicted_joint.items())),
        "direct_joint_distribution": dict(
            sorted(Counter(row["direct_joint"] for row in records).items())
        ),
        "vertex_confusion": confusion_matrix(records, "vertex"),
        "edge_confusion": confusion_matrix(records, "edge"),
        "both_confusion": {
            "TP": sum(
                row["vertex_predicted"]
                and row["edge_predicted"]
                and row["vertex_direct"]
                and row["edge_direct"]
                for row in records
            ),
            "FP": sum(
                row["vertex_predicted"]
                and row["edge_predicted"]
                and not (row["vertex_direct"] and row["edge_direct"])
                for row in records
            ),
            "TN": sum(
                not (row["vertex_predicted"] and row["edge_predicted"])
                and not (row["vertex_direct"] and row["edge_direct"])
                for row in records
            ),
            "FN": sum(
                not (row["vertex_predicted"] and row["edge_predicted"])
                and row["vertex_direct"]
                and row["edge_direct"]
                for row in records
            ),
        },
        "law_mismatch_count": len(counterexamples),
        "phase100_replay_failure_count": 0,
        "phase101_replay_failure_count": 0,
        "critical_cut_reconciliation_failure_count": 0,
        "audit_stream_sha256": audit_stream_sha,
        "by_match_status": grouped_stats(records, "geometry_match_status"),
        "by_rule": grouped_stats(records, "rule"),
        "by_period": grouped_stats(records, "period"),
        "by_vertex_cut_count": grouped_stats(records, "vertex_cut_count"),
        "by_edge_cut_count": grouped_stats(records, "edge_cut_count"),
        "by_vertex_deficit": grouped_stats(records, "vertex_deficit"),
        "by_edge_deficit": grouped_stats(records, "edge_deficit"),
        "simulation_executed": False,
    }
    return {
        "phase": 102,
        "status": verdict,
        "sources": {
            "phase95_path": PHASE95_PATH.name,
            "phase95_raw_sha256": EXPECTED_HASHES["phase95"]["raw"],
            "phase95_canonical_sha256": EXPECTED_HASHES["phase95"]["canonical"],
            "phase97_path": PHASE97_PATH.name,
            "phase97_raw_sha256": EXPECTED_HASHES["phase97"]["raw"],
            "phase97_canonical_sha256": EXPECTED_HASHES["phase97"]["canonical"],
            "phase100_path": PHASE100_PATH.name,
            "phase100_raw_sha256": EXPECTED_HASHES["phase100"]["raw"],
            "phase100_canonical_sha256": EXPECTED_HASHES["phase100"]["canonical"],
            "phase101_path": PHASE101_PATH.name,
            "phase101_raw_sha256": EXPECTED_HASHES["phase101"]["raw"],
            "phase101_canonical_sha256": EXPECTED_HASHES["phase101"]["canonical"],
        },
        "protocol": {
            "simulation_executed": False,
            "scientific_rule": "RESCUE_IFF_ALL_CORRESPONDING_INDIVIDUAL_CUTS_ARE_BYPASSED",
            "threshold_scan_executed": False,
            "critical_cuts_reenumerated": True,
            "unit_outcomes_recomputed_by_direct_cut_removal": True,
            "preflight_was_exploratory_not_blind": True,
        },
        "summary": summary,
        "target_cut_audits": target_audits,
        "audit_records": records,
        "counterexamples": counterexamples,
        "proof_note": (
            "Removing the added node recovers connected F1, so it cannot be a new A/B separator. "
            "Adding one node cannot create a new separator among previously noncritical base vertices or edges. "
            "Each original individual cut ceases to separate exactly when the added node has a neighbor on both terminal sides of that cut."
        ),
        "methodological_limits": [
            "The preflight was exploratory after Fases 100-101; Fase 102 is a formal audit, not a blind discovery claim.",
            "The law covers unit interventions in 219 frozen F1 targets across 48 Q8 cubes.",
            "The phase does not test interactions among two or more added historical nodes.",
            "No temporal-period causality, universal basin, other WIDTH, or quantum-computing claim is made.",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Rule 73/109 exact cut-coverage rescue law - Fase 102",
        "",
        "## Scope and gates",
        "",
        f"- Targets: `{summary['target_count']}`",
        f"- Exposures: `{summary['exposure_count']}`",
        f"- Re-enumerated critical vertices: `{summary['critical_vertex_total']}`",
        f"- Re-enumerated critical edges: `{summary['critical_edge_total']}`",
        f"- Input/replay/cut reconciliation failures: `{summary['phase100_replay_failure_count'] + summary['phase101_replay_failure_count'] + summary['critical_cut_reconciliation_failure_count']}`",
        f"- Scientific counterexamples: `{summary['law_mismatch_count']}`",
        "",
        "## Exact law",
        "",
        "- Vertex rescue iff every individually critical F1 vertex is bypassed.",
        "- Edge rescue iff every individually critical F1 edge is bypassed.",
        "- Both predicates use equality with the total cut count; no threshold was scanned.",
        "",
        "| Metric | TP | FP | TN | FN |",
        "|---|---:|---:|---:|---:|",
        f"| kappa_v | {summary['vertex_confusion']['TP']} | {summary['vertex_confusion']['FP']} | {summary['vertex_confusion']['TN']} | {summary['vertex_confusion']['FN']} |",
        f"| lambda_e | {summary['edge_confusion']['TP']} | {summary['edge_confusion']['FP']} | {summary['edge_confusion']['TN']} | {summary['edge_confusion']['FN']} |",
        f"| both | {summary['both_confusion']['TP']} | {summary['both_confusion']['FP']} | {summary['both_confusion']['TN']} | {summary['both_confusion']['FN']} |",
        "",
        "## Complete coverage",
        "",
        "| Fase-101 geometry status | Exposures | Neither | Edge only | Vertex only | Both | Law mismatches |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for status in ("MATCHED_GEOMETRY", "UNMATCHED_GEOMETRY"):
        row = summary["by_match_status"][status]
        dist = row["direct_joint_distribution"]
        lines.append(
            f"| {status} | {row['exposure_count']} | {dist.get('NEITHER', 0)} | {dist.get('EDGE_ONLY', 0)} | "
            f"{dist.get('VERTEX_ONLY', 0)} | {dist.get('BOTH', 0)} | {row['law_mismatch_count']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Fase 101 showed that period-associated differences disappear within geometry-matched strata. Fase 102 closes the unmatched remainder for unit interventions: the complete cut-coverage predicate reproduces every directly re-enumerated rescue outcome across all 43,425 exposures.",
            "",
            "The result is mechanistic rather than correlational within this frozen graph family. It does not imply that source period causes rescue; period only changes which nodes and geometries are available.",
            "",
            "## Epistemic disclosure",
            "",
            "The exact correspondence was visible in an exploratory preflight after Fases 100-101. This phase independently re-enumerates cuts and unit outcomes to audit that correspondence; it is not presented as a blind prospective discovery.",
            "",
            "## Verdict",
            "",
            f"`{payload['status']}`",
            "",
            "## Methodological limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["methodological_limits"])
    return "\n".join(lines) + "\n"


def main() -> int:
    phase95 = read_and_gate(PHASE95_PATH, EXPECTED_HASHES["phase95"])
    phase97 = read_and_gate(PHASE97_PATH, EXPECTED_HASHES["phase97"])
    phase100 = read_and_gate(PHASE100_PATH, EXPECTED_HASHES["phase100"])
    phase101 = read_and_gate(PHASE101_PATH, EXPECTED_HASHES["phase101"])
    first = build_payload(phase95, phase97, phase100, phase101)
    second = build_payload(phase95, phase97, phase100, phase101)
    if canonical_json_bytes(first) != canonical_json_bytes(second):
        raise RuntimeError("Independent in-memory constructions disagree")
    atomic_write(RESULTS_PATH, json.dumps(first, indent=2, sort_keys=True, ensure_ascii=True) + "\n")
    atomic_write(REPORT_PATH, render_report(first))
    print(json.dumps(first["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
