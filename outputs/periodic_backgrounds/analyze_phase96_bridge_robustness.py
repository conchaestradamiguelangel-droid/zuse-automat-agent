#!/usr/bin/env python3
"""Fase 97: measure robustness of the intracube bridges mapped in Fase 96."""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


OUT_DIR = Path(__file__).resolve().parent
PHASE95_PATH = OUT_DIR / "phase94_hypercube_completion_results.json"
PHASE96_PATH = OUT_DIR / "phase95_fragment_bridge_results.json"
RESULTS_PATH = OUT_DIR / "phase96_bridge_robustness_results.json"
REPORT_PATH = OUT_DIR / "phase96_bridge_robustness_report.md"

EXPECTED_PHASE95_RAW_SHA256 = (
    "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3"
)
EXPECTED_PHASE95_CANONICAL_SHA256 = (
    "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429"
)
EXPECTED_PHASE96_RAW_SHA256 = (
    "cbd414180e89658b3e20c73559dbcb490b2bca845a1165f3f6a8e36f25c2e823"
)
EXPECTED_PHASE96_CANONICAL_SHA256 = (
    "5c43278492fa09f9367fa971e06d0a7b3e2b99e295a63279721bc78a4946f825"
)

EXPECTED_CUBE_COUNT = 48
EXPECTED_NODE_COUNT = 12_288
EXPECTED_CLASS_COUNT = 192
EXPECTED_INTERSECTION_COUNT = 272
EXPECTED_PAIR_COUNT = 979
EXPECTED_SHORTEST_PATH_COUNT = 51_778
EXPECTED_EARLIEST_COUNTS = {
    "F1_ALL_LONG_PERIOD": 627,
    "F2_ALL_CONFIRMED_PERSISTENT": 350,
    "F3_ALL_LEDGER_BACKED_NONZERO": 2,
}
EXPECTED_DISTANCE_COUNTS = {2: 417, 3: 244, 4: 189, 5: 96, 6: 31, 7: 2}

LEVEL_NAMES = {
    0: "F0_TARGET_CLASS_ONLY",
    1: "F1_ALL_LONG_PERIOD",
    2: "F2_ALL_CONFIRMED_PERSISTENT",
    3: "F3_ALL_LEDGER_BACKED_NONZERO",
    4: "F4_FULL_Q8_DIAGNOSTIC",
}
LEVEL_BY_NAME = {name: level for level, name in LEVEL_NAMES.items()}
LONG_CATEGORY = "LONG_PERIOD_CAP_CANDIDATE"
F2_CATEGORIES = {"HISTORICAL_SOURCE_POSITIVE", "STATIC_T1"}
F3_CATEGORIES = {"EXTINCT", "SPAN_ESCAPE", "ZERO_INITIAL_DEFECT"}
ZERO_CATEGORY = "ZERO_IC_BOUNDARY_UNSAMPLED"
SPAN_CATEGORY = "SPAN_ESCAPE"
INF = 1_000_000


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    with temporary.open("r+b") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def distribution(values: Iterable[Any]) -> dict[str, int]:
    counts = Counter(str(value) for value in values)
    return dict(sorted(counts.items()))


def q8_neighbors(word: int) -> tuple[int, ...]:
    if not 0 <= word < 256:
        raise ValueError("Q8 words must be in [0, 255]")
    return tuple(word ^ (1 << bit) for bit in range(8))


def component_words(words: set[int]) -> list[list[int]]:
    pending = set(words)
    components = []
    while pending:
        root = min(pending)
        pending.remove(root)
        queue = deque([root])
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in q8_neighbors(current):
                if neighbor in pending:
                    pending.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda row: (-len(row), row[0]))


def node_levels(nodes: list[dict[str, Any]], physical_class: str) -> list[int]:
    levels = []
    for node in nodes:
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


def connected_between(
    allowed: set[int],
    component_a: Iterable[int],
    component_b: Iterable[int],
    *,
    removed_vertices: Iterable[int] = (),
    removed_edges: Iterable[tuple[int, int]] = (),
) -> bool:
    removed_v = set(removed_vertices)
    removed_e = {tuple(sorted(edge)) for edge in removed_edges}
    roots = sorted(set(component_a) & allowed - removed_v)
    targets = set(component_b) & allowed - removed_v
    if not roots or not targets:
        return False
    visited = set(roots)
    queue = deque(roots)
    while queue:
        current = queue.popleft()
        if current in targets:
            return True
        for neighbor in q8_neighbors(current):
            edge = tuple(sorted((current, neighbor)))
            if (
                neighbor in allowed
                and neighbor not in removed_v
                and neighbor not in visited
                and edge not in removed_e
            ):
                visited.add(neighbor)
                queue.append(neighbor)
    return False


def shortest_path_profile(
    allowed: set[int], component_a: Iterable[int], component_b: Iterable[int]
) -> dict[str, Any]:
    roots = sorted(set(component_a) & allowed)
    targets = sorted(set(component_b) & allowed)
    if not roots or not targets:
        return {"distance": None, "count": 0, "common_interior_vertices": []}

    def distances_and_counts(starts: list[int]):
        distances = {word: 0 for word in starts}
        counts = {word: 1 for word in starts}
        queue = deque(starts)
        while queue:
            current = queue.popleft()
            for neighbor in q8_neighbors(current):
                if neighbor not in allowed:
                    continue
                candidate = distances[current] + 1
                if neighbor not in distances:
                    distances[neighbor] = candidate
                    counts[neighbor] = counts[current]
                    queue.append(neighbor)
                elif distances[neighbor] == candidate:
                    counts[neighbor] += counts[current]
        return distances, counts

    dist_a, count_a = distances_and_counts(roots)
    reachable_targets = [word for word in targets if word in dist_a]
    if not reachable_targets:
        return {"distance": None, "count": 0, "common_interior_vertices": []}
    distance = min(dist_a[word] for word in reachable_targets)
    total = sum(count_a[word] for word in reachable_targets if dist_a[word] == distance)
    dist_b, count_b = distances_and_counts(targets)
    terminals = set(roots) | set(targets)
    common = []
    for word in sorted(allowed - terminals):
        if (
            word in dist_a
            and word in dist_b
            and dist_a[word] + dist_b[word] == distance
            and count_a[word] * count_b[word] == total
        ):
            common.append(word)
    return {
        "distance": distance,
        "count": total,
        "common_interior_vertices": common,
    }


@dataclass
class FlowEdge:
    to: int
    reverse: int
    capacity: int
    original_capacity: int
    original: bool


class Dinic:
    def __init__(self, size: int):
        self.graph: list[list[FlowEdge]] = [[] for _ in range(size)]

    def add_edge(self, source: int, target: int, capacity: int) -> None:
        forward = FlowEdge(target, len(self.graph[target]), capacity, capacity, True)
        reverse = FlowEdge(source, len(self.graph[source]), 0, 0, False)
        self.graph[source].append(forward)
        self.graph[target].append(reverse)

    def max_flow(self, source: int, sink: int) -> int:
        total = 0
        size = len(self.graph)
        while True:
            level = [-1] * size
            level[source] = 0
            queue = deque([source])
            while queue:
                current = queue.popleft()
                for edge in self.graph[current]:
                    if edge.capacity > 0 and level[edge.to] < 0:
                        level[edge.to] = level[current] + 1
                        queue.append(edge.to)
            if level[sink] < 0:
                break
            cursor = [0] * size

            def send(current: int, amount: int) -> int:
                if current == sink:
                    return amount
                while cursor[current] < len(self.graph[current]):
                    edge = self.graph[current][cursor[current]]
                    if edge.capacity > 0 and level[edge.to] == level[current] + 1:
                        pushed = send(edge.to, min(amount, edge.capacity))
                        if pushed:
                            edge.capacity -= pushed
                            self.graph[edge.to][edge.reverse].capacity += pushed
                            return pushed
                    cursor[current] += 1
                return 0

            while True:
                pushed = send(source, INF)
                if not pushed:
                    break
                total += pushed
        return total

    def residual_reachable(self, source: int) -> set[int]:
        visited = {source}
        queue = deque([source])
        while queue:
            current = queue.popleft()
            for edge in self.graph[current]:
                if edge.capacity > 0 and edge.to not in visited:
                    visited.add(edge.to)
                    queue.append(edge.to)
        return visited

    def cut_capacity(self, reachable: set[int]) -> int:
        return sum(
            edge.original_capacity
            for source, edges in enumerate(self.graph)
            if source in reachable
            for edge in edges
            if edge.original and edge.to not in reachable
        )

    def decompose_unit_paths(self, source: int, sink: int) -> int:
        remaining = {
            (origin, index): edge.original_capacity - edge.capacity
            for origin, edges in enumerate(self.graph)
            for index, edge in enumerate(edges)
            if edge.original and edge.original_capacity - edge.capacity > 0
        }
        count = 0
        while True:
            parent: dict[int, tuple[int, int]] = {}
            queue = deque([source])
            seen = {source}
            while queue and sink not in seen:
                current = queue.popleft()
                for index, edge in enumerate(self.graph[current]):
                    if remaining.get((current, index), 0) > 0 and edge.to not in seen:
                        seen.add(edge.to)
                        parent[edge.to] = (current, index)
                        queue.append(edge.to)
            if sink not in seen:
                break
            current = sink
            while current != source:
                origin, index = parent[current]
                remaining[(origin, index)] -= 1
                current = origin
            count += 1
        if any(value > 0 for value in remaining.values()):
            # Integral max flows can contain cycles; cycles do not add source-sink paths.
            pass
        return count


def q8_edges(allowed: set[int]) -> list[tuple[int, int]]:
    return sorted(
        (word, neighbor)
        for word in allowed
        for neighbor in q8_neighbors(word)
        if word < neighbor and neighbor in allowed
    )


def mapped_terminal(word: int, component_a: set[int], component_b: set[int]):
    if word in component_a:
        return "SOURCE"
    if word in component_b:
        return "SINK"
    return word


def edge_connectivity_profile(
    allowed: set[int], component_a: Iterable[int], component_b: Iterable[int]
) -> dict[str, Any]:
    left, right = set(component_a), set(component_b)
    interior = sorted(allowed - left - right)
    index = {word: position for position, word in enumerate(interior)}
    source, sink = len(interior), len(interior) + 1
    flow = Dinic(len(interior) + 2)

    def mapped(word: int) -> int:
        terminal = mapped_terminal(word, left, right)
        if terminal == "SOURCE":
            return source
        if terminal == "SINK":
            return sink
        return index[word]

    edges = q8_edges(allowed)
    for left_word, right_word in edges:
        u, v = mapped(left_word), mapped(right_word)
        if u == v:
            continue
        flow.add_edge(u, v, 1)
        flow.add_edge(v, u, 1)
    value = flow.max_flow(source, sink)
    if value >= INF:
        raise RuntimeError("Unexpected direct terminal adjacency")
    reachable = flow.residual_reachable(source)
    cut_capacity = flow.cut_capacity(reachable)
    path_count = flow.decompose_unit_paths(source, sink)
    if not (value == cut_capacity == path_count):
        raise RuntimeError("Edge Menger reconciliation failed")
    cut_edges = []
    for edge in edges:
        u, v = mapped(edge[0]), mapped(edge[1])
        if u != v and ((u in reachable) != (v in reachable)):
            cut_edges.append(list(edge))
    if len(cut_edges) != value:
        raise RuntimeError("Edge cut cardinality mismatch")
    return {
        "lambda_e": value,
        "edge_disjoint_path_count": path_count,
        "minimum_edge_cut": cut_edges,
    }


def vertex_connectivity_profile(
    allowed: set[int], component_a: Iterable[int], component_b: Iterable[int]
) -> dict[str, Any]:
    left, right = set(component_a), set(component_b)
    interior = sorted(allowed - left - right)
    position = {word: index for index, word in enumerate(interior)}
    source, sink = 2 * len(interior), 2 * len(interior) + 1
    flow = Dinic(2 * len(interior) + 2)

    def in_node(word: int) -> int:
        if word in left:
            return source
        if word in right:
            return sink
        return 2 * position[word]

    def out_node(word: int) -> int:
        if word in left:
            return source
        if word in right:
            return sink
        return 2 * position[word] + 1

    for word in interior:
        flow.add_edge(in_node(word), out_node(word), 1)
    for left_word, right_word in q8_edges(allowed):
        u_out, v_in = out_node(left_word), in_node(right_word)
        v_out, u_in = out_node(right_word), in_node(left_word)
        if u_out != v_in:
            flow.add_edge(u_out, v_in, INF)
        if v_out != u_in:
            flow.add_edge(v_out, u_in, INF)
    value = flow.max_flow(source, sink)
    if value >= INF:
        raise RuntimeError("Unexpected direct terminal adjacency")
    reachable = flow.residual_reachable(source)
    cut_capacity = flow.cut_capacity(reachable)
    path_count = flow.decompose_unit_paths(source, sink)
    if not (value == cut_capacity == path_count):
        raise RuntimeError("Vertex Menger reconciliation failed")
    cut_vertices = [
        word
        for word in interior
        if in_node(word) in reachable and out_node(word) not in reachable
    ]
    if len(cut_vertices) != value:
        raise RuntimeError("Vertex cut cardinality mismatch")
    return {
        "kappa_v": value,
        "internally_vertex_disjoint_path_count": path_count,
        "minimum_vertex_cut": cut_vertices,
    }


def articulation_and_bridges(allowed: set[int]):
    discovery: dict[int, int] = {}
    low: dict[int, int] = {}
    parent: dict[int, int | None] = {}
    articulations: set[int] = set()
    bridges: set[tuple[int, int]] = set()
    clock = 0

    def visit(word: int) -> None:
        nonlocal clock
        clock += 1
        discovery[word] = low[word] = clock
        children = 0
        for neighbor in q8_neighbors(word):
            if neighbor not in allowed:
                continue
            if neighbor not in discovery:
                parent[neighbor] = word
                children += 1
                visit(neighbor)
                low[word] = min(low[word], low[neighbor])
                if parent[word] is None and children > 1:
                    articulations.add(word)
                if parent[word] is not None and low[neighbor] >= discovery[word]:
                    articulations.add(word)
                if low[neighbor] > discovery[word]:
                    bridges.add(tuple(sorted((word, neighbor))))
            elif neighbor != parent[word]:
                low[word] = min(low[word], discovery[neighbor])

    for root in sorted(allowed):
        if root not in discovery:
            parent[root] = None
            visit(root)
    return articulations, bridges


def individually_critical(
    allowed: set[int], component_a: list[int], component_b: list[int]
) -> tuple[list[int], list[list[int]]]:
    terminals = set(component_a) | set(component_b)
    articulations, bridges = articulation_and_bridges(allowed)
    critical_vertices = [
        word
        for word in sorted(articulations - terminals)
        if not connected_between(
            allowed, component_a, component_b, removed_vertices={word}
        )
    ]
    critical_edges = [
        list(edge)
        for edge in sorted(bridges)
        if not connected_between(allowed, component_a, component_b, removed_edges={edge})
    ]
    return critical_vertices, critical_edges


def category_for_word(
    word: int,
    nodes: list[dict[str, Any]],
    physical_class: str,
    component_a: set[int],
    component_b: set[int],
) -> str:
    if word in component_a:
        return "LEFT_TERMINAL_COMPONENT"
    if word in component_b:
        return "RIGHT_TERMINAL_COMPONENT"
    if nodes[word]["physical_class_sha256"] == physical_class:
        return "TARGET_CLASS_OTHER_COMPONENT"
    return nodes[word]["category"]


def annotate_vertices(
    words: Iterable[int],
    nodes: list[dict[str, Any]],
    physical_class: str,
    component_a: set[int],
    component_b: set[int],
) -> list[dict[str, Any]]:
    return [
        {
            "word8": format(word, "08b"),
            "word_value": word,
            "strict_initial_state_sha256": nodes[word]["strict_initial_state_sha256"],
            "category": category_for_word(
                word, nodes, physical_class, component_a, component_b
            ),
        }
        for word in sorted(words)
    ]


def span_escape_tests(
    allowed: set[int],
    component_a: list[int],
    component_b: list[int],
    nodes: list[dict[str, Any]],
    shortest: dict[str, Any],
    kappa_v: int,
    critical_vertices: list[int],
) -> dict[str, Any]:
    span_words = {word for word in allowed if nodes[word]["category"] == SPAN_CATEGORY}
    without_span = allowed - span_words
    category_essential = not connected_between(
        without_span, component_a, component_b
    )
    shortest_without = shortest_path_profile(without_span, component_a, component_b)
    shortest_mandatory = (
        shortest_without["distance"] is None
        or shortest_without["distance"] > shortest["distance"]
    )
    common_span = sorted(
        set(shortest["common_interior_vertices"]) & span_words
    )
    unique_span = (
        kappa_v == 1
        and len(critical_vertices) == 1
        and critical_vertices[0] in span_words
    )
    return {
        "category_essential": category_essential,
        "shortest_path_category_mandatory": shortest_mandatory,
        "common_span_state_on_all_shortest_paths": bool(common_span),
        "common_span_state_words": [format(word, "08b") for word in common_span],
        "unique_span_vertex_bottleneck": unique_span,
    }


def graph_profile(
    allowed: set[int],
    component_a: list[int],
    component_b: list[int],
    nodes: list[dict[str, Any]],
    physical_class: str,
    *,
    run_span_tests: bool,
) -> dict[str, Any]:
    if not connected_between(allowed, component_a, component_b):
        raise RuntimeError("Robustness graph does not connect its terminal components")
    shortest = shortest_path_profile(allowed, component_a, component_b)
    vertex = vertex_connectivity_profile(allowed, component_a, component_b)
    edge = edge_connectivity_profile(allowed, component_a, component_b)
    critical_vertices, critical_edges = individually_critical(
        allowed, component_a, component_b
    )
    if connected_between(
        allowed,
        component_a,
        component_b,
        removed_vertices=vertex["minimum_vertex_cut"],
    ):
        raise RuntimeError("Reported minimum vertex cut does not disconnect pair")
    if connected_between(
        allowed,
        component_a,
        component_b,
        removed_edges={tuple(edge) for edge in edge["minimum_edge_cut"]},
    ):
        raise RuntimeError("Reported minimum edge cut does not disconnect pair")
    if vertex["kappa_v"] > edge["lambda_e"]:
        raise RuntimeError("Undirected local connectivity inequality failed")
    if (vertex["kappa_v"] == 1) != bool(critical_vertices):
        raise RuntimeError("Unit vertex-cut direct deletion gate failed")
    if (edge["lambda_e"] == 1) != bool(critical_edges):
        raise RuntimeError("Unit edge-cut direct deletion gate failed")
    left, right = set(component_a), set(component_b)
    annotated_critical = annotate_vertices(
        critical_vertices, nodes, physical_class, left, right
    )
    annotated_cut = annotate_vertices(
        vertex["minimum_vertex_cut"], nodes, physical_class, left, right
    )
    result = {
        "allowed_node_count": len(allowed),
        "shortest_path_distance": shortest["distance"],
        "shortest_path_count": shortest["count"],
        "kappa_v": vertex["kappa_v"],
        "lambda_e": edge["lambda_e"],
        "internally_vertex_disjoint_path_count": vertex[
            "internally_vertex_disjoint_path_count"
        ],
        "edge_disjoint_path_count": edge["edge_disjoint_path_count"],
        "minimum_vertex_cut": annotated_cut,
        "minimum_edge_cut": edge["minimum_edge_cut"],
        "individually_critical_vertices": annotated_critical,
        "individually_critical_edges": critical_edges,
        "critical_vertex_category_counts": distribution(
            row["category"] for row in annotated_critical
        ),
        "robustness_label": (
            "SINGLE_VERTEX_BOTTLENECK"
            if vertex["kappa_v"] == 1
            else "REDUNDANT_VERTEX_PATHS"
        ),
    }
    result["span_escape_tests"] = (
        span_escape_tests(
            allowed,
            component_a,
            component_b,
            nodes,
            shortest,
            vertex["kappa_v"],
            critical_vertices,
        )
        if run_span_tests
        else "NOT_APPLICABLE_SPAN_NOT_PRESENT_AT_MIN_LEVEL"
    )
    return result


def minimum_hamming_profile(
    component_a: list[int], component_b: list[int], levels: list[int]
) -> dict[str, Any]:
    minimum = min((a ^ b).bit_count() for a in component_a for b in component_b)
    endpoint_pairs = sorted(
        (a, b)
        for a in component_a
        for b in component_b
        if (a ^ b).bit_count() == minimum
    )
    level_counts = Counter()
    for start, target in endpoint_pairs:
        differing = start ^ target
        masks = [1 << bit for bit in range(8) if differing & (1 << bit)]
        dynamic: dict[int, Counter[int]] = {0: Counter({levels[start]: 1})}
        for size in range(len(masks)):
            for subset in sorted(
                value for value in dynamic if value.bit_count() == size
            ):
                for mask in masks:
                    if subset & mask:
                        continue
                    destination = dynamic.setdefault(subset | mask, Counter())
                    next_word = start ^ subset ^ mask
                    for required_level, count in dynamic[subset].items():
                        destination[max(required_level, levels[next_word])] += count
        level_counts.update(dynamic[differing])
    return {
        "minimum_hamming_distance": minimum,
        "minimum_endpoint_pair_count": len(endpoint_pairs),
        "shortest_path_count": sum(level_counts.values()),
        "shortest_path_count_by_required_level": {
            LEVEL_NAMES[level]: level_counts[level] for level in sorted(level_counts)
        },
        "best_shortest_path_level": LEVEL_NAMES[min(level_counts)],
        "worst_shortest_path_level": LEVEL_NAMES[max(level_counts)],
        "shortest_paths_using_zero_word": level_counts[4],
        "all_shortest_paths_require_zero_word": min(level_counts) == 4,
    }


def reconstruct_inputs(phase95: dict[str, Any], phase96: dict[str, Any]):
    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    if len(cubes) != EXPECTED_CUBE_COUNT:
        raise RuntimeError("Fase-95 cube count mismatch")
    if sum(len(cube["nodes"]) for cube in cubes.values()) != EXPECTED_NODE_COUNT:
        raise RuntimeError("Fase-95 node count mismatch")
    if len(phase95["physical_classes"]) != EXPECTED_CLASS_COUNT:
        raise RuntimeError("Fase-95 class count mismatch")

    class_metadata = {
        row["physical_class_sha256"]: row for row in phase95["physical_classes"]
    }
    words_by_class_cube: dict[tuple[str, str], set[int]] = defaultdict(set)
    for cube_key, cube in cubes.items():
        if [node["word8"] for node in cube["nodes"]] != [
            format(word, "08b") for word in range(256)
        ]:
            raise RuntimeError("Fase-95 Q8 word ordering mismatch")
        for word, node in enumerate(cube["nodes"]):
            physical_class = node["physical_class_sha256"]
            if physical_class is not None:
                words_by_class_cube[(physical_class, cube_key)].add(word)

    intersections = []
    for physical_class, metadata in sorted(class_metadata.items()):
        for cube in sorted(metadata["cubes"], key=lambda row: row["cube_key"]):
            cube_key = cube["cube_key"]
            components = component_words(words_by_class_cube[(physical_class, cube_key)])
            if len(components) != cube["component_count"]:
                raise RuntimeError("Fase-95 component count mismatch")
            if [len(row) for row in components] != cube["component_sizes"]:
                raise RuntimeError("Fase-95 component size mismatch")
            if len(components) > 1:
                intersections.append(
                    {
                        "physical_class_sha256": physical_class,
                        "cube_key": cube_key,
                        "components": components,
                        "rules": metadata["rules"],
                        "defect_periods": metadata["defect_periods"],
                    }
                )
    if len(intersections) != EXPECTED_INTERSECTION_COUNT:
        raise RuntimeError("Fase-95 fragmented-intersection count mismatch")

    expected_pairs = phase96["component_pairs"]
    if len(expected_pairs) != EXPECTED_PAIR_COUNT:
        raise RuntimeError("Fase-96 pair count mismatch")
    pair_specs = []
    pair_index = 0
    earliest_counts = Counter()
    distance_counts = Counter()
    total_hamming_paths = 0
    for intersection in intersections:
        physical_class = intersection["physical_class_sha256"]
        cube_key = intersection["cube_key"]
        nodes = cubes[cube_key]["nodes"]
        levels = node_levels(nodes, physical_class)
        components = intersection["components"]
        for left_index, component_a in enumerate(components):
            for right_index in range(left_index + 1, len(components)):
                component_b = components[right_index]
                pair_index += 1
                earliest = next(
                    level
                    for level in range(1, 4)
                    if connected_between(
                        allowed_words(levels, level), component_a, component_b
                    )
                )
                hamming = minimum_hamming_profile(component_a, component_b, levels)
                observed = expected_pairs[pair_index - 1]
                replay = {
                    "pair_index": pair_index,
                    "physical_class_sha256": physical_class,
                    "cube_key": cube_key,
                    "left_component_index": left_index,
                    "right_component_index": right_index,
                    "left_component_size": len(component_a),
                    "right_component_size": len(component_b),
                    "earliest_any_path_level": LEVEL_NAMES[earliest],
                    **hamming,
                }
                for key, value in replay.items():
                    if observed[key] != value:
                        raise RuntimeError(
                            f"Fase-96 pair replay mismatch at {pair_index}:{key}"
                        )
                earliest_counts[LEVEL_NAMES[earliest]] += 1
                distance_counts[hamming["minimum_hamming_distance"]] += 1
                total_hamming_paths += hamming["shortest_path_count"]
                pair_specs.append(
                    {
                        **replay,
                        "component_a": component_a,
                        "component_b": component_b,
                        "nodes": nodes,
                        "levels": levels,
                    }
                )
    if pair_index != EXPECTED_PAIR_COUNT:
        raise RuntimeError("Reconstructed pair denominator mismatch")
    if dict(earliest_counts) != EXPECTED_EARLIEST_COUNTS:
        raise RuntimeError("Fase-96 closure distribution mismatch")
    if dict(distance_counts) != EXPECTED_DISTANCE_COUNTS:
        raise RuntimeError("Fase-96 distance distribution mismatch")
    if total_hamming_paths != EXPECTED_SHORTEST_PATH_COUNT:
        raise RuntimeError("Fase-96 shortest-path total mismatch")
    return cubes, intersections, pair_specs


def summarize_profiles(rows: list[dict[str, Any]], scope: str) -> dict[str, Any]:
    return {
        "pair_count": len(rows),
        "kappa_v_distribution": distribution(row[scope]["kappa_v"] for row in rows),
        "lambda_e_distribution": distribution(row[scope]["lambda_e"] for row in rows),
        "robustness_label_counts": distribution(
            row[scope]["robustness_label"] for row in rows
        ),
        "shortest_path_distance_distribution": distribution(
            row[scope]["shortest_path_distance"] for row in rows
        ),
        "pairs_with_individually_critical_vertices": sum(
            bool(row[scope]["individually_critical_vertices"]) for row in rows
        ),
        "pairs_with_individually_critical_edges": sum(
            bool(row[scope]["individually_critical_edges"]) for row in rows
        ),
    }


def build_payload(phase95: dict[str, Any], phase96: dict[str, Any]) -> dict[str, Any]:
    cubes, intersections, pair_specs = reconstruct_inputs(phase95, phase96)
    pair_rows = []
    for spec in pair_specs:
        earliest = LEVEL_BY_NAME[spec["earliest_any_path_level"]]
        component_a = spec["component_a"]
        component_b = spec["component_b"]
        nodes = spec["nodes"]
        levels = spec["levels"]
        g_min = graph_profile(
            allowed_words(levels, earliest),
            component_a,
            component_b,
            nodes,
            spec["physical_class_sha256"],
            run_span_tests=earliest == 3,
        )
        g_f3 = graph_profile(
            allowed_words(levels, 3),
            component_a,
            component_b,
            nodes,
            spec["physical_class_sha256"],
            run_span_tests=True,
        )
        if earliest == 3 and g_min["span_escape_tests"] != g_f3["span_escape_tests"]:
            raise RuntimeError("F3 G_min/G_F3 SPAN_ESCAPE gate failed")
        pair_rows.append(
            {
                key: value
                for key, value in spec.items()
                if key not in {"component_a", "component_b", "nodes", "levels"}
            }
            | {
                "left_component_words": [format(word, "08b") for word in component_a],
                "right_component_words": [format(word, "08b") for word in component_b],
                "g_min": g_min,
                "g_f3": g_f3,
            }
        )

    rows_by_intersection: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        rows_by_intersection[(row["physical_class_sha256"], row["cube_key"])].append(row)
    intersection_rows = []
    for intersection in intersections:
        key = (intersection["physical_class_sha256"], intersection["cube_key"])
        rows = rows_by_intersection[key]
        intersection_rows.append(
            {
                "physical_class_sha256": key[0],
                "cube_key": key[1],
                "component_count": len(intersection["components"]),
                "component_pair_count": len(rows),
                "g_min_weakest_kappa_v": min(row["g_min"]["kappa_v"] for row in rows),
                "g_min_weakest_lambda_e": min(row["g_min"]["lambda_e"] for row in rows),
                "g_f3_weakest_kappa_v": min(row["g_f3"]["kappa_v"] for row in rows),
                "g_f3_weakest_lambda_e": min(row["g_f3"]["lambda_e"] for row in rows),
                "rules": intersection["rules"],
                "defect_periods": intersection["defect_periods"],
            }
        )

    strata = {}
    for level_name in EXPECTED_EARLIEST_COUNTS:
        level_rows = [
            row for row in pair_rows if row["earliest_any_path_level"] == level_name
        ]
        strata[level_name] = {
            "g_min": summarize_profiles(level_rows, "g_min"),
            "g_f3": summarize_profiles(level_rows, "g_f3"),
        }

    span_fields = (
        "category_essential",
        "shortest_path_category_mandatory",
        "common_span_state_on_all_shortest_paths",
        "unique_span_vertex_bottleneck",
    )
    span_summary = {
        field: sum(bool(row["g_f3"]["span_escape_tests"][field]) for row in pair_rows)
        for field in span_fields
    }
    f3_rows = [row for row in pair_rows if row["earliest_any_path_level"] == LEVEL_NAMES[3]]
    if len(f3_rows) != 2:
        raise RuntimeError("Expected exactly two first-closing F3 pairs")
    f3_span_rows = [
        {
            "pair_index": row["pair_index"],
            "cube_key": row["cube_key"],
            "physical_class_sha256": row["physical_class_sha256"],
            "g_min": row["g_min"]["span_escape_tests"],
            "g_f3": row["g_f3"]["span_escape_tests"],
        }
        for row in f3_rows
    ]

    return {
        "phase": 97,
        "status": "BRIDGE_ROBUSTNESS_ATLAS_BUILT",
        "sources": {
            "phase95_raw_sha256": EXPECTED_PHASE95_RAW_SHA256,
            "phase95_canonical_sha256": EXPECTED_PHASE95_CANONICAL_SHA256,
            "phase96_raw_sha256": EXPECTED_PHASE96_RAW_SHA256,
            "phase96_canonical_sha256": EXPECTED_PHASE96_CANONICAL_SHA256,
        },
        "protocol": {
            "graph": "UNDIRECTED_Q8_HAMMING_1_INTERVENTION_GRAPH",
            "terminal_policy": "COMPONENT_SETS_UNREMOVABLE_SHARED_ENDPOINTS_ALLOWED",
            "g_min": "INDUCED_AT_EARLIEST_F1_F2_F3_CLOSURE",
            "g_f3": "ALL_255_LEDGER_BACKED_NONZERO_STATES",
            "vertex_connectivity": "NODE_SPLIT_INTEGER_MAX_FLOW",
            "edge_connectivity": "UNIT_CAPACITY_INTEGER_MAX_FLOW",
            "zero_word_policy": "EXCLUDED_FROM_ALL_PRIMARY_ROBUSTNESS_METRICS",
            "simulation_executed": False,
            "external_ledger_read": False,
        },
        "summary": {
            "cube_count": len(cubes),
            "fragmented_intersection_count": len(intersections),
            "component_pair_count": len(pair_rows),
            "phase96_replay_status": "EXACT_PAIRWISE_RECONCILIATION",
            "phase96_earliest_counts": EXPECTED_EARLIEST_COUNTS,
            "phase96_total_hamming_shortest_paths": EXPECTED_SHORTEST_PATH_COUNT,
            "strata": strata,
            "g_min_intersection_weakest_kappa_v_distribution": distribution(
                row["g_min_weakest_kappa_v"] for row in intersection_rows
            ),
            "g_min_intersection_weakest_lambda_e_distribution": distribution(
                row["g_min_weakest_lambda_e"] for row in intersection_rows
            ),
            "g_f3_intersection_weakest_kappa_v_distribution": distribution(
                row["g_f3_weakest_kappa_v"] for row in intersection_rows
            ),
            "g_f3_intersection_weakest_lambda_e_distribution": distribution(
                row["g_f3_weakest_lambda_e"] for row in intersection_rows
            ),
            "g_f3_span_escape_test_true_counts": span_summary,
            "f3_first_closing_pair_count": len(f3_rows),
            "reconciliation_failure_count": 0,
            "simulation_executed": False,
            "external_ledger_read": False,
        },
        "f3_span_escape_pairs": f3_span_rows,
        "intersections": intersection_rows,
        "component_pairs": pair_rows,
        "methodological_limits": [
            "Only the 48 frozen Fase-95 length-8 Q8 cubes are analyzed.",
            "Q8 edges are reversible bit-flip interventions, not directed CA-time transitions.",
            "Connectivity is topological and is not a transition probability.",
            "The unsimulated zero word is excluded from every primary robustness metric.",
            "No claim is made about universal WIDTH=256 basin connectivity.",
        ],
    }


def render_report(
    payload: dict[str, Any], output_raw_sha256: str, output_canonical_sha256: str
) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 97 - Intracube bridge robustness atlas",
        "",
        "## Question",
        "",
        "Are the 979 Fase-96 component bridges supported by redundant intervention paths, or do they depend on pair-specific vertex/edge bottlenecks?",
        "",
        "## Frozen sources and reconciliation",
        "",
        f"- Fase-95 raw SHA-256: `{payload['sources']['phase95_raw_sha256']}`",
        f"- Fase-95 canonical SHA-256: `{payload['sources']['phase95_canonical_sha256']}`",
        f"- Fase-96 raw SHA-256: `{payload['sources']['phase96_raw_sha256']}`",
        f"- Fase-96 canonical SHA-256: `{payload['sources']['phase96_canonical_sha256']}`",
        f"- Fase-97 result raw SHA-256: `{output_raw_sha256}`",
        f"- Fase-97 result canonical SHA-256: `{output_canonical_sha256}`",
        f"- Cubes/intersections/pairs: {summary['cube_count']}/{summary['fragmented_intersection_count']}/{summary['component_pair_count']}",
        f"- Fase-96 replay: `{summary['phase96_replay_status']}`",
        f"- Reconciliation failures: {summary['reconciliation_failure_count']}",
        "",
        "## Graph semantics",
        "",
        "The graph is the undirected Q8 Hamming-1 intervention graph. It is not a directed CA-time graph. Vertex and edge connectivity are measured separately between complete F0 terminal components.",
        "",
        "## Robustness by predeclared closure stratum",
        "",
        "| stratum | pairs | G_min kappa_v | G_min lambda_e | G_F3 kappa_v | G_F3 lambda_e |",
        "|---|---:|---|---|---|---|",
    ]
    for level_name, row in summary["strata"].items():
        lines.append(
            f"| {level_name} | {row['g_min']['pair_count']} | "
            f"{json.dumps(row['g_min']['kappa_v_distribution'], sort_keys=True)} | "
            f"{json.dumps(row['g_min']['lambda_e_distribution'], sort_keys=True)} | "
            f"{json.dumps(row['g_f3']['kappa_v_distribution'], sort_keys=True)} | "
            f"{json.dumps(row['g_f3']['lambda_e_distribution'], sort_keys=True)} |"
        )
    lines.extend(
        [
            "",
            "No aggregate robustness percentage mixes F1, F2, and F3 denominators.",
            "",
            "## Pair-specific bottlenecks",
            "",
        ]
    )
    for level_name, row in summary["strata"].items():
        lines.append(
            f"- {level_name}: G_min single-vertex bottlenecks "
            f"{row['g_min']['robustness_label_counts'].get('SINGLE_VERTEX_BOTTLENECK', 0)}/"
            f"{row['g_min']['pair_count']}; G_F3 "
            f"{row['g_f3']['robustness_label_counts'].get('SINGLE_VERTEX_BOTTLENECK', 0)}/"
            f"{row['g_f3']['pair_count']}."
        )
    lines.extend(
        [
            "",
            "## SPAN_ESCAPE tests",
            "",
            f"- G_F3 true counts over 979 pairs: `{json.dumps(summary['g_f3_span_escape_test_true_counts'], sort_keys=True)}`",
            "- G_min is NOT_APPLICABLE for the 977 F1/F2 pairs.",
            "- The two first-closing F3 pairs must have identical G_min and G_F3 test results.",
            "",
            "| pair | cube | category essential | shortest mandatory | common state | unique vertex bottleneck |",
            "|---:|---|---|---|---|---|",
        ]
    )
    for row in payload["f3_span_escape_pairs"]:
        tests = row["g_f3"]
        cube_label = row["cube_key"].replace("|", "\\|")
        lines.append(
            f"| {row['pair_index']} | {cube_label} | {tests['category_essential']} | "
            f"{tests['shortest_path_category_mandatory']} | "
            f"{tests['common_span_state_on_all_shortest_paths']} | "
            f"{tests['unique_span_vertex_bottleneck']} |"
        )
    lines.extend(
        [
            "",
            "## Intersection weakest links",
            "",
            f"- G_min weakest kappa_v: `{json.dumps(summary['g_min_intersection_weakest_kappa_v_distribution'], sort_keys=True)}`",
            f"- G_min weakest lambda_e: `{json.dumps(summary['g_min_intersection_weakest_lambda_e_distribution'], sort_keys=True)}`",
            f"- G_F3 weakest kappa_v: `{json.dumps(summary['g_f3_intersection_weakest_kappa_v_distribution'], sort_keys=True)}`",
            f"- G_F3 weakest lambda_e: `{json.dumps(summary['g_f3_intersection_weakest_lambda_e_distribution'], sort_keys=True)}`",
            "",
            "## Verdict",
            "",
            f"`{payload['status']}`",
            "",
            "## Methodological limits",
            "",
        ]
    )
    lines.extend(f"- {limit}" for limit in payload["methodological_limits"])
    lines.append("")
    return "\n".join(lines)


def read_and_gate(path: Path, expected_raw: str, expected_canonical: str):
    raw = path.read_bytes()
    raw_sha = sha256_bytes(raw)
    if raw_sha != expected_raw:
        raise RuntimeError(f"Raw SHA mismatch for {path.name}: {raw_sha}")
    payload = json.loads(raw)
    canonical_sha = canonical_sha256(payload)
    if canonical_sha != expected_canonical:
        raise RuntimeError(f"Canonical SHA mismatch for {path.name}: {canonical_sha}")
    return payload


def run() -> dict[str, Any]:
    phase95 = read_and_gate(
        PHASE95_PATH,
        EXPECTED_PHASE95_RAW_SHA256,
        EXPECTED_PHASE95_CANONICAL_SHA256,
    )
    phase96 = read_and_gate(
        PHASE96_PATH,
        EXPECTED_PHASE96_RAW_SHA256,
        EXPECTED_PHASE96_CANONICAL_SHA256,
    )
    first = build_payload(phase95, phase96)
    second = build_payload(phase95, phase96)
    if canonical_json_bytes(first) != canonical_json_bytes(second):
        raise RuntimeError("Deterministic second-build gate failed")
    result_text = json.dumps(first, indent=2, sort_keys=True) + "\n"
    output_raw_sha = sha256_bytes(result_text.encode("utf-8"))
    output_canonical_sha = canonical_sha256(first)
    atomic_write(RESULTS_PATH, result_text)
    atomic_write(REPORT_PATH, render_report(first, output_raw_sha, output_canonical_sha))
    return first


def main() -> None:
    payload = run()
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
