from __future__ import annotations

import hashlib
import itertools
import json
import os
import struct
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"
PHASE95_PATH = OUTPUT_DIR / "phase94_hypercube_completion_results.json"
PHASE97_PATH = OUTPUT_DIR / "phase96_bridge_robustness_results.json"
PHASE100_PATH = OUTPUT_DIR / "phase99_unit_cardinality_period_potency_results.json"
PHASE102_PATH = OUTPUT_DIR / "phase101_cut_coverage_law_results.json"
LEDGER_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_ledger.bin"
MANIFEST_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_manifest.json"
RESULTS_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_results.json"
REPORT_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_report.md"

EXPECTED_HASHES = {
    "phase95": (
        "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3",
        "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429",
    ),
    "phase97": (
        "3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858",
        "85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b",
    ),
    "phase100": (
        "39ec272b72c54f07c0996064c3d755fff9d4b6690fdfdbe3eb4d771ac0710c8c",
        "f79e047d22dddb375db7f351bc9bdd55b978ce29ed22e9c22d9195fb70935d22",
    ),
    "phase102": (
        "2eae9b4825bb78d9c396a47bfe365c0beedda198de7c8a2a6093fede3423fb2c",
        "3ecad4486d9ac87c5c7efc58726a41dcaacd738d6450ffc6024b3577dbd0b74e",
    ),
}

EXPECTED_CUBE_COUNT = 48
EXPECTED_TARGET_COUNT = 219
EXPECTED_UNIT_AUDIT_COUNT = 43425
EXPECTED_STRATUM_COUNT = 142
EXPECTED_KAPPA_STRATA = 126
EXPECTED_LAMBDA_STRATA = 139
EXPECTED_PAIR_COUNT = 404054
EXPECTED_KAPPA_PAIR_COUNT = 384354
EXPECTED_LAMBDA_PAIR_COUNT = 372299
EXPECTED_ADJACENT_PAIR_COUNT = 16307
EXPECTED_NONADJACENT_PAIR_COUNT = 387747
EXPECTED_STRATA_BY_PERIOD = {2: 15, 3: 65, 6: 32, 8: 1, 12: 29}
EXPECTED_PAIRS_BY_PERIOD = {2: 68115, 3: 96793, 6: 229494, 8: 66, 12: 9586}
EXPECTED_ADJACENT_BY_PERIOD = {2: 2449, 3: 5020, 6: 8330, 8: 4, 12: 504}
EXPECTED_STRATA_BY_RULE = {73: 61, 109: 81}
EXPECTED_PAIRS_BY_RULE = {73: 157796, 109: 246258}

HISTORICAL_CATEGORY = "HISTORICAL_SOURCE_POSITIVE"
LONG_CATEGORY = "LONG_PERIOD_CAP_CANDIDATE"
COLLECTIVE = "COLLECTIVE_ONLY_PERIOD_RESCUE"
KAPPA = "kappa_v"
LAMBDA = "lambda_e"

# 10-byte, little-endian fixed record.
LEDGER_RECORD = struct.Struct("<HBBHBBBB")
LEDGER_FORMAT = "<HBBHBBBB"
LEDGER_FIELDS = [
    {"name": "stratum_index", "offset": 0, "width": 2, "type": "uint16"},
    {"name": "left_word", "offset": 2, "width": 1, "type": "uint8"},
    {"name": "right_word", "offset": 3, "width": 1, "type": "uint8"},
    {"name": "flags", "offset": 4, "width": 2, "type": "uint16_bitmask"},
    {"name": "uncovered_original_vertices", "offset": 6, "width": 1, "type": "uint8"},
    {"name": "uncovered_original_edges", "offset": 7, "width": 1, "type": "uint8"},
    {"name": "new_vertex_separator_mask", "offset": 8, "width": 1, "type": "uint8_bitmask"},
    {"name": "new_edge_separator_count", "offset": 9, "width": 1, "type": "uint8"},
]
FLAG_BITS = {
    "adjacent_pair": 0,
    "kappa_collective_scope": 1,
    "lambda_collective_scope": 2,
    "kappa_route_a_rescue": 3,
    "lambda_route_a_rescue": 4,
    "kappa_route_b_rescue": 5,
    "lambda_route_b_rescue": 6,
    "mutual_edge_required_kappa": 7,
    "mutual_edge_required_lambda": 8,
    "distributed_vertex_coverage": 9,
    "distributed_edge_coverage": 10,
}


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
            for source, targets in adjacency.items()
            for target in targets
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
    seen = {node for node in starts if node in adjacency and node != removed_vertex}
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


def enumerate_terminal_cuts(
    adjacency: dict[int, set[int]], component_a: set[int], component_b: set[int]
) -> tuple[tuple[int, ...], tuple[tuple[int, int], ...]]:
    if not terminals_connected(adjacency, component_a, component_b):
        raise RuntimeError("Base graph does not connect terminal sets")
    vertices = tuple(
        node
        for node in sorted(set(adjacency) - component_a - component_b)
        if not terminals_connected(
            adjacency, component_a, component_b, removed_vertex=node
        )
    )
    edges = tuple(
        edge
        for edge in graph_edges(adjacency)
        if not terminals_connected(
            adjacency, component_a, component_b, removed_edge=edge
        )
    )
    return vertices, edges


def add_pair(
    base: dict[int, set[int]], left: int, right: int
) -> tuple[dict[int, set[int]], tuple[tuple[int, int], ...], bool]:
    if left >= right or left in base or right in base:
        raise RuntimeError("Invalid unordered pair intervention")
    adjacency = {node: set(targets) for node, targets in base.items()}
    adjacency[left] = set()
    adjacency[right] = set()
    new_edges = set()
    for node in (left, right):
        for target in q8_neighbors(node):
            if target in adjacency and target != node:
                edge = tuple(sorted((node, target)))
                new_edges.add(edge)
                adjacency[node].add(target)
                adjacency[target].add(node)
    mutual = right in adjacency[left]
    return adjacency, tuple(sorted(new_edges)), mutual


def flag_mask(values: dict[str, bool]) -> int:
    mask = 0
    for name, bit in FLAG_BITS.items():
        if values.get(name, False):
            mask |= 1 << bit
    return mask


@dataclass
class FlowEdge:
    target: int
    reverse: int
    capacity: int


class Dinic:
    def __init__(self, size: int):
        self.graph: list[list[FlowEdge]] = [[] for _ in range(size)]

    def add_edge(self, source: int, target: int, capacity: int) -> None:
        forward = FlowEdge(target, len(self.graph[target]), capacity)
        reverse = FlowEdge(source, len(self.graph[source]), 0)
        self.graph[source].append(forward)
        self.graph[target].append(reverse)

    def max_flow(self, source: int, sink: int, limit: int = 2) -> int:
        total = 0
        while total < limit:
            level = [-1] * len(self.graph)
            level[source] = 0
            queue = deque([source])
            while queue:
                node = queue.popleft()
                for edge in self.graph[node]:
                    if edge.capacity > 0 and level[edge.target] < 0:
                        level[edge.target] = level[node] + 1
                        queue.append(edge.target)
            if level[sink] < 0:
                break
            cursor = [0] * len(self.graph)

            def send(node: int, amount: int) -> int:
                if node == sink:
                    return amount
                while cursor[node] < len(self.graph[node]):
                    edge = self.graph[node][cursor[node]]
                    if edge.capacity > 0 and level[edge.target] == level[node] + 1:
                        pushed = send(edge.target, min(amount, edge.capacity))
                        if pushed:
                            edge.capacity -= pushed
                            self.graph[edge.target][edge.reverse].capacity += pushed
                            return pushed
                    cursor[node] += 1
                return 0

            while total < limit:
                pushed = send(source, limit - total)
                if not pushed:
                    break
                total += pushed
        return total


def edge_connectivity_two(
    adjacency: dict[int, set[int]], component_a: set[int], component_b: set[int]
) -> bool:
    nodes = sorted(adjacency)
    index = {node: position for position, node in enumerate(nodes)}
    source = len(nodes)
    sink = source + 1
    flow = Dinic(len(nodes) + 2)
    for left, right in graph_edges(adjacency):
        flow.add_edge(index[left], index[right], 1)
        flow.add_edge(index[right], index[left], 1)
    for node in component_a:
        flow.add_edge(source, index[node], 2)
    for node in component_b:
        flow.add_edge(index[node], sink, 2)
    return flow.max_flow(source, sink, 2) >= 2


def vertex_connectivity_two(
    adjacency: dict[int, set[int]], component_a: set[int], component_b: set[int]
) -> bool:
    nodes = sorted(adjacency)
    position = {node: index for index, node in enumerate(nodes)}
    source = 2 * len(nodes)
    sink = source + 1
    flow = Dinic(2 * len(nodes) + 2)
    terminals = component_a | component_b
    for node in nodes:
        incoming = 2 * position[node]
        outgoing = incoming + 1
        flow.add_edge(incoming, outgoing, 2 if node in terminals else 1)
    for left, right in graph_edges(adjacency):
        flow.add_edge(2 * position[left] + 1, 2 * position[right], 2)
        flow.add_edge(2 * position[right] + 1, 2 * position[left], 2)
    for node in component_a:
        flow.add_edge(source, 2 * position[node], 2)
    for node in component_b:
        flow.add_edge(2 * position[node] + 1, sink, 2)
    return flow.max_flow(source, sink, 2) >= 2


def route_a_audit(
    adjacency: dict[int, set[int]],
    component_a: set[int],
    component_b: set[int],
    original_vertices: tuple[int, ...],
    original_edges: tuple[tuple[int, int], ...],
    left: int,
    right: int,
    new_edges: tuple[tuple[int, int], ...],
) -> dict[str, Any]:
    uncovered_vertices = sum(
        not terminals_connected(
            adjacency, component_a, component_b, removed_vertex=vertex
        )
        for vertex in original_vertices
    )
    uncovered_edges = sum(
        not terminals_connected(
            adjacency, component_a, component_b, removed_edge=edge
        )
        for edge in original_edges
    )
    new_vertex_mask = 0
    for bit, node in enumerate((left, right)):
        if not terminals_connected(
            adjacency, component_a, component_b, removed_vertex=node
        ):
            new_vertex_mask |= 1 << bit
    new_edge_separators = tuple(
        edge
        for edge in new_edges
        if not terminals_connected(
            adjacency, component_a, component_b, removed_edge=edge
        )
    )
    return {
        "kappa_rescue": uncovered_vertices == 0 and new_vertex_mask == 0,
        "lambda_rescue": uncovered_edges == 0 and not new_edge_separators,
        "uncovered_original_vertices": uncovered_vertices,
        "uncovered_original_edges": uncovered_edges,
        "new_vertex_separator_mask": new_vertex_mask,
        "new_edge_separators": new_edge_separators,
    }


def remove_edge_copy(
    adjacency: dict[int, set[int]], edge: tuple[int, int]
) -> dict[int, set[int]]:
    output = {node: set(targets) for node, targets in adjacency.items()}
    output[edge[0]].discard(edge[1])
    output[edge[1]].discard(edge[0])
    return output


def build_context(
    cube: dict[str, Any], pair: dict[str, Any], target_class: str, audit: dict[str, Any]
) -> dict[str, Any]:
    nodes = cube["nodes"]
    component_a = {int(word, 2) for word in pair["left_component_words"]}
    component_b = {int(word, 2) for word in pair["right_component_words"]}
    allowed = {
        index
        for index, node in enumerate(nodes)
        if node["physical_class_sha256"] == target_class
        or node["category"] == LONG_CATEGORY
    }
    adjacency = build_q8_adjacency(allowed)
    vertices, edges = enumerate_terminal_cuts(adjacency, component_a, component_b)
    expected_vertices = tuple(sorted(map(int, audit["critical_vertices"])))
    expected_edges = tuple(
        sorted(tuple(sorted(map(int, edge))) for edge in audit["critical_edges"])
    )
    if vertices != expected_vertices or edges != expected_edges:
        raise RuntimeError("Fase-102 critical-cut replay mismatch")
    return {
        "nodes": nodes,
        "component_a": component_a,
        "component_b": component_b,
        "adjacency": adjacency,
        "critical_vertices": vertices,
        "critical_edges": edges,
    }


def relation_scope(stratum: dict[str, Any], metric: str) -> bool:
    return stratum["relations"][metric] == COLLECTIVE


def minimal_label(scope: bool, rescuing_pair_count: int) -> str:
    if not scope:
        return "NOT_APPLICABLE_NOT_COLLECTIVE"
    return "EXACTLY_2" if rescuing_pair_count else "AT_LEAST_3"


def build_payloads(
    phase95: dict[str, Any],
    phase97: dict[str, Any],
    phase100: dict[str, Any],
    phase102: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], bytes]:
    if len(phase95["cube_nodes"]) != EXPECTED_CUBE_COUNT:
        raise RuntimeError("Fase-95 cube denominator mismatch")
    if len(phase102["audit_records"]) != EXPECTED_UNIT_AUDIT_COUNT:
        raise RuntimeError("Fase-102 unit-audit denominator mismatch")
    if phase102["status"] != "EXACT_CUT_COVERAGE_RESCUE_LAW_VERIFIED":
        raise RuntimeError("Fase-102 law is not closed")

    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    pairs = {(row["cube_key"], int(row["pair_index"])): row for row in phase97["component_pairs"]}
    unit_lookup = {
        (row["cube_key"], int(row["pair_index"]), int(row["word_int"])): row
        for row in phase102["audit_records"]
    }
    target_audits = {
        (row["cube_key"], int(row["pair_index"])): row
        for row in phase102["target_cut_audits"]
    }
    if len(unit_lookup) != EXPECTED_UNIT_AUDIT_COUNT or len(target_audits) != EXPECTED_TARGET_COUNT:
        raise RuntimeError("Fase-102 replay identity mismatch")

    strata_source = [
        row
        for row in phase100["target_period_strata"]
        if COLLECTIVE in (row["relations"][KAPPA], row["relations"][LAMBDA])
    ]
    strata_source.sort(
        key=lambda row: (row["cube_key"], int(row["pair_index"]), int(row["period"]))
    )
    if len(strata_source) != EXPECTED_STRATUM_COUNT:
        raise RuntimeError("Collective stratum denominator mismatch")
    if sum(relation_scope(row, KAPPA) for row in strata_source) != EXPECTED_KAPPA_STRATA:
        raise RuntimeError("Kappa collective-stratum denominator mismatch")
    if sum(relation_scope(row, LAMBDA) for row in strata_source) != EXPECTED_LAMBDA_STRATA:
        raise RuntimeError("Lambda collective-stratum denominator mismatch")

    contexts = {}
    for row in strata_source:
        key = (row["cube_key"], int(row["pair_index"]))
        if key not in contexts:
            contexts[key] = build_context(
                cubes[key[0]], pairs[key], row["physical_class_sha256"], target_audits[key]
            )

    ledger = bytearray()
    stratum_results = []
    total_pairs = 0
    kappa_pairs = 0
    lambda_pairs = 0
    adjacent_pairs = 0
    pairs_by_period = Counter()
    adjacent_by_period = Counter()
    pairs_by_rule = Counter()
    route_disagreements = []
    monotonicity_failures = []

    for stratum_index, source in enumerate(strata_source):
        key = (source["cube_key"], int(source["pair_index"]))
        context = contexts[key]
        period = int(source["period"])
        historical_words = tuple(
            index
            for index, node in enumerate(context["nodes"])
            if node["category"] == HISTORICAL_CATEGORY
            and int(node["ledger"]["source_period"]) == period
        )
        if len(historical_words) != int(source["node_count"]):
            raise RuntimeError("Historical stratum node-count replay mismatch")
        kappa_scope = relation_scope(source, KAPPA)
        lambda_scope = relation_scope(source, LAMBDA)
        if kappa_scope and (
            int(source["vertex_rescue_count"]) != 0
            or int(source["group_values"][KAPPA]) < 2
        ):
            raise RuntimeError("Kappa collective-only gate failed")
        if lambda_scope and (
            int(source["edge_rescue_count"]) != 0
            or int(source["group_values"][LAMBDA]) < 2
        ):
            raise RuntimeError("Lambda collective-only gate failed")
        for word in historical_words:
            unit = unit_lookup[(key[0], key[1], word)]
            if kappa_scope and bool(unit["vertex_direct"]):
                raise RuntimeError("Kappa collective stratum contains singleton rescue")
            if lambda_scope and bool(unit["edge_direct"]):
                raise RuntimeError("Lambda collective stratum contains singleton rescue")

        pair_count = 0
        adjacent_count = 0
        kappa_rescuing = []
        lambda_rescuing = []
        mutual_required_kappa_count = 0
        mutual_required_lambda_count = 0
        mechanism_counts = Counter()
        for left, right in itertools.combinations(historical_words, 2):
            adjacency, new_edges, adjacent = add_pair(context["adjacency"], left, right)
            route_a = route_a_audit(
                adjacency,
                context["component_a"],
                context["component_b"],
                context["critical_vertices"],
                context["critical_edges"],
                left,
                right,
                new_edges,
            )
            route_b_kappa = vertex_connectivity_two(
                adjacency, context["component_a"], context["component_b"]
            )
            route_b_lambda = edge_connectivity_two(
                adjacency, context["component_a"], context["component_b"]
            )
            if (
                route_a["kappa_rescue"] != route_b_kappa
                or route_a["lambda_rescue"] != route_b_lambda
            ):
                route_disagreements.append((stratum_index, left, right))

            mutual_edge = tuple(sorted((left, right)))
            mutual_required_kappa = False
            mutual_required_lambda = False
            if adjacent and (route_b_kappa or route_b_lambda):
                without_mutual = remove_edge_copy(adjacency, mutual_edge)
                if route_b_kappa:
                    mutual_required_kappa = not vertex_connectivity_two(
                        without_mutual, context["component_a"], context["component_b"]
                    )
                if route_b_lambda:
                    mutual_required_lambda = not edge_connectivity_two(
                        without_mutual, context["component_a"], context["component_b"]
                    )
            if mutual_required_kappa:
                mutual_required_kappa_count += 1
            if mutual_required_lambda:
                mutual_required_lambda_count += 1

            left_unit = unit_lookup[(key[0], key[1], left)]
            right_unit = unit_lookup[(key[0], key[1], right)]
            distributed_vertex = (
                route_a["uncovered_original_vertices"] == 0
                and not left_unit["vertex_direct"]
                and not right_unit["vertex_direct"]
            )
            distributed_edge = (
                route_a["uncovered_original_edges"] == 0
                and not left_unit["edge_direct"]
                and not right_unit["edge_direct"]
            )
            if route_b_kappa:
                kappa_rescuing.append((left, right))
            if route_b_lambda:
                lambda_rescuing.append((left, right))
            if route_a["uncovered_original_vertices"]:
                mechanism_counts["ORIGINAL_VERTEX_CUTS_UNCOVERED"] += 1
            if route_a["uncovered_original_edges"]:
                mechanism_counts["ORIGINAL_EDGE_CUTS_UNCOVERED"] += 1
            if route_a["new_vertex_separator_mask"]:
                mechanism_counts["NEW_VERTEX_BOTTLENECK"] += 1
            if route_a["new_edge_separators"]:
                mechanism_counts["NEW_EDGE_BOTTLENECK"] += 1
            if distributed_vertex:
                mechanism_counts["DISTRIBUTED_VERTEX_COVERAGE"] += 1
            if distributed_edge:
                mechanism_counts["DISTRIBUTED_EDGE_COVERAGE"] += 1

            flags = flag_mask(
                {
                    "adjacent_pair": adjacent,
                    "kappa_collective_scope": kappa_scope,
                    "lambda_collective_scope": lambda_scope,
                    "kappa_route_a_rescue": route_a["kappa_rescue"],
                    "lambda_route_a_rescue": route_a["lambda_rescue"],
                    "kappa_route_b_rescue": route_b_kappa,
                    "lambda_route_b_rescue": route_b_lambda,
                    "mutual_edge_required_kappa": mutual_required_kappa,
                    "mutual_edge_required_lambda": mutual_required_lambda,
                    "distributed_vertex_coverage": distributed_vertex,
                    "distributed_edge_coverage": distributed_edge,
                }
            )
            ledger.extend(
                LEDGER_RECORD.pack(
                    stratum_index,
                    left,
                    right,
                    flags,
                    int(route_a["uncovered_original_vertices"]),
                    int(route_a["uncovered_original_edges"]),
                    int(route_a["new_vertex_separator_mask"]),
                    len(route_a["new_edge_separators"]),
                )
            )
            pair_count += 1
            adjacent_count += int(adjacent)

            if kappa_scope and route_b_kappa and int(source["group_values"][KAPPA]) < 2:
                monotonicity_failures.append((stratum_index, left, right, KAPPA))
            if lambda_scope and route_b_lambda and int(source["group_values"][LAMBDA]) < 2:
                monotonicity_failures.append((stratum_index, left, right, LAMBDA))

        expected_pairs = len(historical_words) * (len(historical_words) - 1) // 2
        if pair_count != expected_pairs:
            raise RuntimeError("Pair enumeration denominator mismatch")
        stratum_results.append(
            {
                "stratum_index": stratum_index,
                "cube_key": key[0],
                "pair_index": key[1],
                "rule": int(source["rule"]),
                "background_index": int(source["background_index"]),
                "period": period,
                "node_count": len(historical_words),
                "pair_count": pair_count,
                "adjacent_pair_count": adjacent_count,
                "relations": source["relations"],
                "kappa_pair_rescue_count": len(kappa_rescuing),
                "lambda_pair_rescue_count": len(lambda_rescuing),
                "kappa_minimal_cardinality": minimal_label(kappa_scope, len(kappa_rescuing)),
                "lambda_minimal_cardinality": minimal_label(lambda_scope, len(lambda_rescuing)),
                "kappa_rescuing_pair_examples": [list(pair) for pair in kappa_rescuing[:20]],
                "lambda_rescuing_pair_examples": [list(pair) for pair in lambda_rescuing[:20]],
                "mutual_edge_required_kappa_count": mutual_required_kappa_count,
                "mutual_edge_required_lambda_count": mutual_required_lambda_count,
                "mechanism_counts": dict(sorted(mechanism_counts.items())),
            }
        )
        total_pairs += pair_count
        kappa_pairs += pair_count if kappa_scope else 0
        lambda_pairs += pair_count if lambda_scope else 0
        adjacent_pairs += adjacent_count
        pairs_by_period[period] += pair_count
        adjacent_by_period[period] += adjacent_count
        pairs_by_rule[int(source["rule"])] += pair_count

    if route_disagreements:
        raise RuntimeError(f"Route A/B disagreement: {route_disagreements[:5]}")
    if monotonicity_failures:
        raise RuntimeError(f"Pair/group monotonicity failure: {monotonicity_failures[:5]}")
    if total_pairs != EXPECTED_PAIR_COUNT:
        raise RuntimeError("Global pair denominator mismatch")
    if kappa_pairs != EXPECTED_KAPPA_PAIR_COUNT or lambda_pairs != EXPECTED_LAMBDA_PAIR_COUNT:
        raise RuntimeError("Metric pair denominator mismatch")
    if adjacent_pairs != EXPECTED_ADJACENT_PAIR_COUNT:
        raise RuntimeError("Adjacent pair denominator mismatch")
    if total_pairs - adjacent_pairs != EXPECTED_NONADJACENT_PAIR_COUNT:
        raise RuntimeError("Nonadjacent pair denominator mismatch")
    if dict(sorted(pairs_by_period.items())) != EXPECTED_PAIRS_BY_PERIOD:
        raise RuntimeError("Pair period distribution mismatch")
    if dict(sorted(adjacent_by_period.items())) != EXPECTED_ADJACENT_BY_PERIOD:
        raise RuntimeError("Adjacent period distribution mismatch")
    if dict(sorted(pairs_by_rule.items())) != EXPECTED_PAIRS_BY_RULE:
        raise RuntimeError("Pair rule distribution mismatch")
    if dict(sorted(Counter(row["period"] for row in strata_source).items())) != EXPECTED_STRATA_BY_PERIOD:
        raise RuntimeError("Stratum period distribution mismatch")
    if dict(sorted(Counter(int(row["rule"]) for row in strata_source).items())) != EXPECTED_STRATA_BY_RULE:
        raise RuntimeError("Stratum rule distribution mismatch")
    if len(ledger) != EXPECTED_PAIR_COUNT * LEDGER_RECORD.size:
        raise RuntimeError("Ledger byte-size reconciliation failed")

    ledger_bytes = bytes(ledger)
    ledger_sha = hashlib.sha256(ledger_bytes).hexdigest()
    kappa_exact_two = sum(
        row["kappa_minimal_cardinality"] == "EXACTLY_2" for row in stratum_results
    )
    kappa_higher = sum(
        row["kappa_minimal_cardinality"] == "AT_LEAST_3" for row in stratum_results
    )
    lambda_exact_two = sum(
        row["lambda_minimal_cardinality"] == "EXACTLY_2" for row in stratum_results
    )
    lambda_higher = sum(
        row["lambda_minimal_cardinality"] == "AT_LEAST_3" for row in stratum_results
    )
    summary = {
        "cube_count": EXPECTED_CUBE_COUNT,
        "collective_stratum_count": len(stratum_results),
        "kappa_collective_stratum_count": EXPECTED_KAPPA_STRATA,
        "lambda_collective_stratum_count": EXPECTED_LAMBDA_STRATA,
        "pair_intervention_count": total_pairs,
        "kappa_pair_trial_count": kappa_pairs,
        "lambda_pair_trial_count": lambda_pairs,
        "adjacent_pair_count": adjacent_pairs,
        "nonadjacent_pair_count": total_pairs - adjacent_pairs,
        "kappa_exactly_two_strata": kappa_exact_two,
        "kappa_at_least_three_strata": kappa_higher,
        "lambda_exactly_two_strata": lambda_exact_two,
        "lambda_at_least_three_strata": lambda_higher,
        "kappa_pair_rescue_count": sum(
            row["kappa_pair_rescue_count"]
            for row in stratum_results
            if row["relations"][KAPPA] == COLLECTIVE
        ),
        "lambda_pair_rescue_count": sum(
            row["lambda_pair_rescue_count"]
            for row in stratum_results
            if row["relations"][LAMBDA] == COLLECTIVE
        ),
        "mutual_edge_required_kappa_count": sum(
            row["mutual_edge_required_kappa_count"]
            for row in stratum_results
            if row["relations"][KAPPA] == COLLECTIVE
        ),
        "mutual_edge_required_lambda_count": sum(
            row["mutual_edge_required_lambda_count"]
            for row in stratum_results
            if row["relations"][LAMBDA] == COLLECTIVE
        ),
        "route_disagreement_count": 0,
        "monotonicity_failure_count": 0,
        "unit_replay_failure_count": 0,
        "ledger_record_count": EXPECTED_PAIR_COUNT,
        "ledger_record_size": LEDGER_RECORD.size,
        "ledger_size": len(ledger_bytes),
        "ledger_sha256": ledger_sha,
        "simulation_executed": False,
    }
    result = {
        "phase": 103,
        "status": "PAIRWISE_SYNERGY_ATLAS_BUILT",
        "sources": {
            "phase95": {"path": PHASE95_PATH.name, "raw_sha256": EXPECTED_HASHES["phase95"][0], "canonical_sha256": EXPECTED_HASHES["phase95"][1]},
            "phase97": {"path": PHASE97_PATH.name, "raw_sha256": EXPECTED_HASHES["phase97"][0], "canonical_sha256": EXPECTED_HASHES["phase97"][1]},
            "phase100": {"path": PHASE100_PATH.name, "raw_sha256": EXPECTED_HASHES["phase100"][0], "canonical_sha256": EXPECTED_HASHES["phase100"][1]},
            "phase102": {"path": PHASE102_PATH.name, "raw_sha256": EXPECTED_HASHES["phase102"][0], "canonical_sha256": EXPECTED_HASHES["phase102"][1]},
        },
        "protocol": {
            "simulation_executed": False,
            "pair_order": "LEXICOGRAPHIC_UNORDERED",
            "route_a": "ORIGINAL_CUTS_PLUS_ALL_NEW_VERTEX_EDGE_CANDIDATES",
            "route_b": "FRESH_INTEGER_MAX_FLOW_CAP_2",
            "metric_denominators_separate": True,
            "threshold_scan_executed": False,
        },
        "summary": summary,
        "strata": stratum_results,
        "methodological_limits": [
            "EXACTLY_2 is proven only where no singleton rescues and at least one pair does.",
            "AT_LEAST_3 is a lower bound; triples and higher subsets are not enumerated here.",
            "Period labels index available historical-node families and are not treated as temporal causes.",
            "The atlas is restricted to 142 frozen target-period strata in 48 Q8 cubes.",
        ],
    }
    manifest = {
        "phase": 103,
        "ledger_file": LEDGER_PATH.name,
        "byte_order": "little-endian",
        "record_format": LEDGER_FORMAT,
        "record_size": LEDGER_RECORD.size,
        "record_count": EXPECTED_PAIR_COUNT,
        "ledger_size": len(ledger_bytes),
        "ledger_sha256": ledger_sha,
        "fields": LEDGER_FIELDS,
        "flag_bits": FLAG_BITS,
        "stratum_index_source": f"{RESULTS_PATH.name}::strata[].stratum_index",
        "decoder": "decode_phase102_pairwise_synergy_ledger.py",
    }
    return result, manifest, ledger_bytes


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Rule 73/109 pairwise historical synergy atlas - Fase 103",
        "",
        "## Gates and scope",
        "",
        f"- Collective strata: `{summary['collective_stratum_count']}`",
        f"- Kappa strata/trials: `{summary['kappa_collective_stratum_count']}` / `{summary['kappa_pair_trial_count']}`",
        f"- Lambda strata/trials: `{summary['lambda_collective_stratum_count']}` / `{summary['lambda_pair_trial_count']}`",
        f"- Unique unordered pair interventions: `{summary['pair_intervention_count']}`",
        f"- Adjacent/nonadjacent pairs: `{summary['adjacent_pair_count']}` / `{summary['nonadjacent_pair_count']}`",
        f"- Route disagreements: `{summary['route_disagreement_count']}`",
        f"- Monotonicity failures: `{summary['monotonicity_failure_count']}`",
        "",
        "## Minimum observed cardinality",
        "",
        "| Metric | Exactly 2 strata | At least 3 strata | Rescuing pair trials |",
        "|---|---:|---:|---:|",
        f"| kappa_v | {summary['kappa_exactly_two_strata']} | {summary['kappa_at_least_three_strata']} | {summary['kappa_pair_rescue_count']} |",
        f"| lambda_e | {summary['lambda_exactly_two_strata']} | {summary['lambda_at_least_three_strata']} | {summary['lambda_pair_rescue_count']} |",
        "",
        "## Pair interaction",
        "",
        f"- Kappa rescues requiring the mutual Hamming-1 edge: `{summary['mutual_edge_required_kappa_count']}`",
        f"- Lambda rescues requiring the mutual Hamming-1 edge: `{summary['mutual_edge_required_lambda_count']}`",
        "",
        "## Binary ledger",
        "",
        f"- Records: `{summary['ledger_record_count']}`",
        f"- Record size: `{summary['ledger_record_size']}` bytes",
        f"- Ledger size: `{summary['ledger_size']}` bytes",
        f"- SHA-256: `{summary['ledger_sha256']}`",
        "- Format and bit meanings are fully specified in the JSON manifest; the decoder uses only the Python standard library.",
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


def main() -> int:
    phase95 = read_and_gate(PHASE95_PATH, EXPECTED_HASHES["phase95"])
    phase97 = read_and_gate(PHASE97_PATH, EXPECTED_HASHES["phase97"])
    phase100 = read_and_gate(PHASE100_PATH, EXPECTED_HASHES["phase100"])
    phase102 = read_and_gate(PHASE102_PATH, EXPECTED_HASHES["phase102"])
    result, manifest, ledger = build_payloads(phase95, phase97, phase100, phase102)
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
