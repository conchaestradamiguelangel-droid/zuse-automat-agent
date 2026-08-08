#!/usr/bin/env python3
"""Fase 96: filter bridges between intracube fragments from Fase 95."""

from __future__ import annotations

import hashlib
import json
import math
import os
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Callable, Iterable


OUT_DIR = Path(__file__).resolve().parent
SOURCE_PATH = OUT_DIR / "phase94_hypercube_completion_results.json"
RESULTS_PATH = OUT_DIR / "phase95_fragment_bridge_results.json"
REPORT_PATH = OUT_DIR / "phase95_fragment_bridge_report.md"

EXPECTED_RAW_SHA256 = "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3"
EXPECTED_CANONICAL_SHA256 = "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429"
EXPECTED_CUBE_COUNT = 48
EXPECTED_NODE_COUNT = 12288
EXPECTED_CLASS_COUNT = 192
EXPECTED_FRAGMENTED_INTERSECTION_COUNT = 272
EXPECTED_COMPONENT_PAIR_COUNT = 979
EXPECTED_INTERSECTION_COMPONENT_DISTRIBUTION = {2: 121, 3: 85, 4: 31, 5: 24, 6: 9, 7: 2}
EXPECTED_MINIMUM_HAMMING_DISTRIBUTION = {2: 206, 3: 47, 4: 10, 5: 9}

WINDOW_POSITIONS = tuple(range(124, 132))
LEVEL_NAMES = {
    0: "F0_TARGET_CLASS_ONLY",
    1: "F1_ALL_LONG_PERIOD",
    2: "F2_ALL_CONFIRMED_PERSISTENT",
    3: "F3_ALL_LEDGER_BACKED_NONZERO",
    4: "F4_FULL_Q8_DIAGNOSTIC",
}
F2_CATEGORIES = {"HISTORICAL_SOURCE_POSITIVE", "STATIC_T1"}
F3_CATEGORIES = {"EXTINCT", "SPAN_ESCAPE", "ZERO_INITIAL_DEFECT"}
ZERO_CATEGORY = "ZERO_IC_BOUNDARY_UNSAMPLED"
LONG_CATEGORY = "LONG_PERIOD_CAP_CANDIDATE"


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
    return {
        str(key): count
        for key, count in sorted(Counter(values).items(), key=lambda item: str(item[0]))
    }


def q8_target(word_value: int, flip_position: int) -> int:
    if not 0 <= word_value < 256:
        raise ValueError("Q8 word is outside 0..255")
    if flip_position not in WINDOW_POSITIONS:
        raise ValueError("Q8 flip is outside positions 124..131")
    return word_value ^ (1 << (7 - (flip_position - WINDOW_POSITIONS[0])))


def q8_neighbors(word_value: int) -> tuple[int, ...]:
    neighbors = tuple(q8_target(word_value, position) for position in WINDOW_POSITIONS)
    if len(set(neighbors)) != 8:
        raise RuntimeError("Q8 node does not have eight unique neighbors")
    return neighbors


def component_words(words: set[int]) -> list[list[int]]:
    unseen = set(words)
    components = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in q8_neighbors(current):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda values: (-len(values), values[0]))


def minimum_component_hamming(components: list[list[int]]) -> int | None:
    if len(components) < 2:
        return None
    return min(
        (left ^ right).bit_count()
        for left_index, left_component in enumerate(components)
        for right_component in components[left_index + 1 :]
        for left in left_component
        for right in right_component
    )


def connected_filtered(
    component_a: Iterable[int],
    component_b: Iterable[int],
    allowed: Callable[[int], bool],
) -> bool:
    targets = set(component_b)
    roots = [word for word in component_a if allowed(word)]
    if not roots or not all(allowed(word) for word in targets):
        return False
    visited = set(roots)
    queue = deque(roots)
    while queue:
        current = queue.popleft()
        if current in targets:
            return True
        for neighbor in q8_neighbors(current):
            if neighbor not in visited and allowed(neighbor):
                visited.add(neighbor)
                queue.append(neighbor)
    return False


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
            raise RuntimeError(f"Unknown Fase-95 node category: {category}")
        levels.append(level)
    if len(levels) != 256:
        raise RuntimeError("A level map must contain exactly 256 Q8 nodes")
    return levels


def earliest_connection_level(
    component_a: list[int], component_b: list[int], levels: list[int]
) -> int:
    for level in range(1, 5):
        if connected_filtered(
            component_a, component_b, lambda word, limit=level: levels[word] <= limit
        ):
            return level
    raise RuntimeError("Q8 pair remains disconnected even at F4")


def endpoint_pairs_at_minimum(
    component_a: list[int], component_b: list[int]
) -> tuple[int, list[tuple[int, int]]]:
    minimum = min((left ^ right).bit_count() for left in component_a for right in component_b)
    pairs = sorted(
        (left, right)
        for left in component_a
        for right in component_b
        if (left ^ right).bit_count() == minimum
    )
    return minimum, pairs


def shortest_path_level_counts(
    start: int, target: int, levels: list[int]
) -> Counter[int]:
    differing = start ^ target
    bit_masks = [1 << bit for bit in range(8) if differing & (1 << bit)]
    dynamic: dict[int, Counter[int]] = {0: Counter({levels[start]: 1})}
    for size in range(len(bit_masks)):
        for subset in sorted(
            value
            for value in dynamic
            if value.bit_count() == size
        ):
            counts = dynamic[subset]
            for bit in bit_masks:
                if subset & bit:
                    continue
                next_subset = subset | bit
                next_word = start ^ next_subset
                destination = dynamic.setdefault(next_subset, Counter())
                for required_level, count in counts.items():
                    destination[max(required_level, levels[next_word])] += count
    result = dynamic[differing]
    expected = math.factorial(len(bit_masks))
    if sum(result.values()) != expected:
        raise RuntimeError("Shortest-path DP did not reconcile to d factorial")
    return result


def shortest_component_pair_profile(
    component_a: list[int], component_b: list[int], levels: list[int]
) -> dict[str, Any]:
    minimum, endpoint_pairs = endpoint_pairs_at_minimum(component_a, component_b)
    counts = Counter()
    for start, target in endpoint_pairs:
        counts.update(shortest_path_level_counts(start, target, levels))
    if not counts:
        raise RuntimeError("No shortest paths were counted")
    return {
        "minimum_hamming_distance": minimum,
        "minimum_endpoint_pair_count": len(endpoint_pairs),
        "shortest_path_count": sum(counts.values()),
        "shortest_path_count_by_required_level": {
            LEVEL_NAMES[level]: counts[level] for level in sorted(counts)
        },
        "best_shortest_path_level": LEVEL_NAMES[min(counts)],
        "worst_shortest_path_level": LEVEL_NAMES[max(counts)],
        "shortest_paths_using_zero_word": counts[4],
        "all_shortest_paths_require_zero_word": min(counts) == 4,
    }


def f3_ablation(
    component_a: list[int],
    component_b: list[int],
    nodes: list[dict[str, Any]],
    levels: list[int],
) -> dict[str, Any]:
    rows = []
    for category in sorted(F3_CATEGORIES):
        connected_without = connected_filtered(
            component_a,
            component_b,
            lambda word, category=category: levels[word] <= 3
            and nodes[word]["category"] != category,
        )
        connected_with_only = connected_filtered(
            component_a,
            component_b,
            lambda word, category=category: levels[word] <= 2
            or nodes[word]["category"] == category,
        )
        rows.append(
            {
                "category": category,
                "connected_without_category": connected_without,
                "category_is_necessary": not connected_without,
                "connected_with_base_plus_only_category": connected_with_only,
                "category_is_sufficient_over_F2": connected_with_only,
            }
        )
    return {
        "categories": rows,
        "necessary_categories": [
            row["category"] for row in rows if row["category_is_necessary"]
        ],
        "sufficient_categories": [
            row["category"]
            for row in rows
            if row["category_is_sufficient_over_F2"]
        ],
    }


def validate_nonzero_q8_connectivity() -> None:
    nonzero = set(range(1, 256))
    component = component_words(nonzero)
    if len(component) != 1 or len(component[0]) != 255:
        raise RuntimeError("F3 nonzero Q8 is not connected")


def reconstruct_intersections(source: dict[str, Any]):
    cubes = {cube["cube_key"]: cube for cube in source["cube_nodes"]}
    if len(cubes) != EXPECTED_CUBE_COUNT:
        raise RuntimeError("Unexpected Fase-95 cube count")
    category_counts = Counter()
    for key, cube in cubes.items():
        nodes = cube["nodes"]
        if len(nodes) != 256:
            raise RuntimeError(f"Cube {key} does not have 256 nodes")
        expected_words = [format(value, "08b") for value in range(256)]
        if [node["word8"] for node in nodes] != expected_words:
            raise RuntimeError(f"Cube {key} word order is not exact Q8 order")
        category_counts.update(node["category"] for node in nodes)
        for value in range(256):
            if len(set(q8_neighbors(value))) != 8:
                raise RuntimeError("Q8 degree gate failed")
    if sum(category_counts.values()) != EXPECTED_NODE_COUNT:
        raise RuntimeError("Unexpected Fase-95 node total")
    if dict(sorted(category_counts.items())) != source["summary"]["node_category_counts"]:
        raise RuntimeError("Fase-95 category distribution mismatch")

    source_classes = {
        row["physical_class_sha256"]: row for row in source["physical_classes"]
    }
    if len(source_classes) != EXPECTED_CLASS_COUNT:
        raise RuntimeError("Unexpected Fase-95 physical-class count")
    words_by_class_cube: dict[tuple[str, str], set[int]] = defaultdict(set)
    for key, cube in cubes.items():
        for value, node in enumerate(cube["nodes"]):
            physical_class = node["physical_class_sha256"]
            if physical_class is not None:
                words_by_class_cube[(physical_class, key)].add(value)

    intersections = []
    component_distribution = Counter()
    minimum_distribution = Counter()
    pair_count = 0
    for physical_class, source_class in sorted(source_classes.items()):
        source_cubes = {row["cube_key"]: row for row in source_class["cubes"]}
        observed_keys = {
            key for (candidate_class, key) in words_by_class_cube if candidate_class == physical_class
        }
        if observed_keys != set(source_cubes):
            raise RuntimeError("Fase-95 class/cube occupancy mismatch")
        for key in sorted(observed_keys):
            components = component_words(words_by_class_cube[(physical_class, key)])
            expected = source_cubes[key]
            if len(components) != expected["component_count"]:
                raise RuntimeError("Fase-95 component count mismatch")
            if [len(component) for component in components] != expected["component_sizes"]:
                raise RuntimeError("Fase-95 component sizes mismatch")
            minimum = minimum_component_hamming(components)
            if minimum != expected["minimum_intercomponent_hamming"]:
                raise RuntimeError("Fase-95 minimum Hamming mismatch")
            if len(components) > 1:
                component_distribution[len(components)] += 1
                minimum_distribution[minimum] += 1
                pair_count += len(components) * (len(components) - 1) // 2
                intersections.append(
                    {
                        "physical_class_sha256": physical_class,
                        "cube_key": key,
                        "components": components,
                        "rules": source_class["rules"],
                        "defect_periods": source_class["defect_periods"],
                    }
                )
    if len(intersections) != EXPECTED_FRAGMENTED_INTERSECTION_COUNT:
        raise RuntimeError("Fragmented-intersection denominator mismatch")
    if dict(component_distribution) != EXPECTED_INTERSECTION_COMPONENT_DISTRIBUTION:
        raise RuntimeError("Intersection component distribution mismatch")
    if pair_count != EXPECTED_COMPONENT_PAIR_COUNT:
        raise RuntimeError("Component-pair denominator mismatch")
    if dict(minimum_distribution) != EXPECTED_MINIMUM_HAMMING_DISTRIBUTION:
        raise RuntimeError("Fase-95 minimum Hamming distribution mismatch")
    return cubes, intersections


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 96 - Intracube fragment bridge filtration",
        "",
        "## Question",
        "",
        "Which Q8 state families connect the disconnected components of one physical long-period class inside the same frozen background/rule cube?",
        "",
        "## Frozen source and gates",
        "",
        f"- Source raw SHA-256: `{payload['source_raw_sha256']}`",
        f"- Source canonical JSON SHA-256: `{payload['source_canonical_sha256']}`",
        f"- Fragmented class/cube intersections: {summary['fragmented_intersection_count']}",
        f"- Unordered component pairs: {summary['component_pair_count']}",
        f"- Reconciliation failures: {summary['reconciliation_failure_count']}",
        "- Input is only the committed Fase-95 JSON; no Stage-A ledger and no ECA simulation is used.",
        "",
        "## Filtration",
        "",
        "- F1: all long-period classes.",
        "- F2: F1 plus historical short-period positives and static-T1 states.",
        "- F3: every ledger-backed non-zero state.",
        "- F4: full Q8 including the unsimulated zero word, diagnostic only.",
        "",
        "## Pairwise closure by any Q8 path",
        "",
        f"`{json.dumps(summary['earliest_any_path_level_counts'], sort_keys=True)}`",
        "",
        f"- Pairs unbridged without zero word: {summary['pairs_unbridged_without_zero_word']}",
        f"- Intersection closure levels: `{json.dumps(summary['intersection_closure_level_counts'], sort_keys=True)}`",
        "",
        "## Exhaustive shortest-path anatomy",
        "",
        f"- Minimum pairwise Hamming distribution: `{json.dumps(summary['pairwise_minimum_hamming_distribution'], sort_keys=True)}`",
        f"- Best shortest-path levels: `{json.dumps(summary['best_shortest_path_level_counts'], sort_keys=True)}`",
        f"- Worst shortest-path levels: `{json.dumps(summary['worst_shortest_path_level_counts'], sort_keys=True)}`",
        f"- Total shortest paths counted: {summary['total_shortest_path_count']}",
        f"- Shortest paths using zero word: {summary['shortest_paths_using_zero_word']}",
        f"- Pairs with at least one zero-word shortest path: {summary['pairs_with_some_zero_word_shortest_path']}",
        f"- Pairs whose every shortest path requires zero: {summary['pairs_all_shortest_paths_require_zero_word']}",
        "",
        "## F3 category ablation",
        "",
        f"- Pairs first closing at F3: {summary['f3_pair_count']}",
        f"- Necessary-category counts: `{json.dumps(summary['f3_necessary_category_counts'], sort_keys=True)}`",
        f"- Sufficient-over-F2 counts: `{json.dumps(summary['f3_sufficient_category_counts'], sort_keys=True)}`",
        "",
        "## Example component pairs",
        "",
        "| closure | d | shortest paths | best | worst | zero paths | class | cube |",
        "|---|---:|---:|---|---|---:|---|---|",
    ]
    examples = sorted(
        payload["component_pairs"],
        key=lambda row: (
            -int(row["earliest_any_path_level"][1]),
            -row["shortest_paths_using_zero_word"],
            -row["minimum_hamming_distance"],
            row["pair_index"],
        ),
    )
    for row in examples[:20]:
        lines.append(
            f"| {row['earliest_any_path_level']} | {row['minimum_hamming_distance']} | "
            f"{row['shortest_path_count']} | {row['best_shortest_path_level']} | "
            f"{row['worst_shortest_path_level']} | {row['shortest_paths_using_zero_word']} | "
            f"{row['physical_class_sha256'][:12]} | {row['cube_key']} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"`{payload['status']}`",
            "",
            "The filtration maps local Q8 corridors between observed long-period fragments. It does not measure dynamical transitions or universal basin connectivity.",
            "",
            "## Methodological limits",
            "",
            "- The 979 pairs belong only to the 48 frozen Fase-95 Q8 cubes.",
            "- Filtration levels classify initial states from prior detector outputs; they are not transition probabilities.",
            "- The zero word was never simulated and is used only to count optional diagnostic shortest paths.",
            "- No Stage-A ledger, ECA simulation, paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> dict[str, Any]:
    raw = SOURCE_PATH.read_bytes()
    raw_sha = sha256_bytes(raw)
    if raw_sha != EXPECTED_RAW_SHA256:
        raise RuntimeError(f"Fase-95 raw SHA mismatch: {raw_sha}")
    source = json.loads(raw)
    canonical_sha = canonical_sha256(source)
    if canonical_sha != EXPECTED_CANONICAL_SHA256:
        raise RuntimeError(f"Fase-95 canonical JSON SHA mismatch: {canonical_sha}")
    validate_nonzero_q8_connectivity()
    cubes, intersections = reconstruct_intersections(source)

    pair_rows = []
    intersection_rows = []
    earliest_counts = Counter()
    best_counts = Counter()
    worst_counts = Counter()
    pairwise_minimums = Counter()
    intersection_closure_counts = Counter()
    necessary_counts = Counter()
    sufficient_counts = Counter()
    total_shortest_paths = 0
    total_zero_paths = 0
    pairs_some_zero = 0
    pairs_all_zero = 0
    pair_index = 0
    for intersection in intersections:
        physical_class = intersection["physical_class_sha256"]
        key = intersection["cube_key"]
        nodes = cubes[key]["nodes"]
        levels = node_levels(nodes, physical_class)
        components = intersection["components"]
        local_rows = []
        for left_index, component_a in enumerate(components):
            for right_index in range(left_index + 1, len(components)):
                component_b = components[right_index]
                pair_index += 1
                earliest = earliest_connection_level(component_a, component_b, levels)
                profile = shortest_component_pair_profile(
                    component_a, component_b, levels
                )
                ablation = (
                    f3_ablation(component_a, component_b, nodes, levels)
                    if earliest == 3
                    else None
                )
                row = {
                    "pair_index": pair_index,
                    "physical_class_sha256": physical_class,
                    "cube_key": key,
                    "left_component_index": left_index,
                    "right_component_index": right_index,
                    "left_component_size": len(component_a),
                    "right_component_size": len(component_b),
                    "earliest_any_path_level": LEVEL_NAMES[earliest],
                    **profile,
                    "f3_ablation": ablation,
                }
                local_rows.append(row)
                pair_rows.append(row)
                earliest_counts[LEVEL_NAMES[earliest]] += 1
                best_counts[profile["best_shortest_path_level"]] += 1
                worst_counts[profile["worst_shortest_path_level"]] += 1
                pairwise_minimums[profile["minimum_hamming_distance"]] += 1
                total_shortest_paths += profile["shortest_path_count"]
                total_zero_paths += profile["shortest_paths_using_zero_word"]
                if profile["shortest_paths_using_zero_word"]:
                    pairs_some_zero += 1
                if profile["all_shortest_paths_require_zero_word"]:
                    pairs_all_zero += 1
                if ablation is not None:
                    necessary_counts.update(ablation["necessary_categories"])
                    sufficient_counts.update(ablation["sufficient_categories"])
        closure_level = max(
            int(row["earliest_any_path_level"][1]) for row in local_rows
        )
        intersection_closure_counts[LEVEL_NAMES[closure_level]] += 1
        intersection_rows.append(
            {
                "physical_class_sha256": physical_class,
                "cube_key": key,
                "component_count": len(components),
                "component_pair_count": len(local_rows),
                "closure_level_for_all_components": LEVEL_NAMES[closure_level],
                "pair_closure_level_counts": distribution(
                    row["earliest_any_path_level"] for row in local_rows
                ),
                "rules": intersection["rules"],
                "defect_periods": intersection["defect_periods"],
            }
        )
    if pair_index != EXPECTED_COMPONENT_PAIR_COUNT:
        raise RuntimeError("Final component-pair count mismatch")

    f3_pair_count = earliest_counts[LEVEL_NAMES[3]]
    summary = {
        "fragmented_intersection_count": len(intersections),
        "component_pair_count": len(pair_rows),
        "earliest_any_path_level_counts": dict(sorted(earliest_counts.items())),
        "intersection_closure_level_counts": dict(
            sorted(intersection_closure_counts.items())
        ),
        "pairs_unbridged_without_zero_word": earliest_counts[LEVEL_NAMES[4]],
        "pairwise_minimum_hamming_distribution": distribution(
            pairwise_minimums.elements()
        ),
        "best_shortest_path_level_counts": dict(sorted(best_counts.items())),
        "worst_shortest_path_level_counts": dict(sorted(worst_counts.items())),
        "total_shortest_path_count": total_shortest_paths,
        "shortest_paths_using_zero_word": total_zero_paths,
        "pairs_with_some_zero_word_shortest_path": pairs_some_zero,
        "pairs_all_shortest_paths_require_zero_word": pairs_all_zero,
        "f3_pair_count": f3_pair_count,
        "f3_necessary_category_counts": dict(sorted(necessary_counts.items())),
        "f3_sufficient_category_counts": dict(sorted(sufficient_counts.items())),
        "reconciliation_failure_count": 0,
        "simulation_executed": False,
        "external_ledger_read": False,
    }
    payload = {
        "phase": 96,
        "status": "FRAGMENT_BRIDGE_FILTRATION_MAPPED",
        "source_raw_sha256": raw_sha,
        "source_canonical_sha256": canonical_sha,
        "protocol": {
            "cube": "Q8",
            "adjacency": "HAMMING_DISTANCE_1_ONLY",
            "fragmented_intersections": EXPECTED_FRAGMENTED_INTERSECTION_COUNT,
            "component_pairs": EXPECTED_COMPONENT_PAIR_COUNT,
            "shortest_path_method": "EXACT_SUBSET_DP_ALL_MINIMUM_ENDPOINT_PAIRS",
            "zero_word_policy": "DIAGNOSTIC_ONLY_UNSIMULATED",
            "simulation_executed": False,
            "external_ledger_read": False,
        },
        "summary": summary,
        "intersections": intersection_rows,
        "component_pairs": pair_rows,
        "methodological_limits": [
            "Only the 48 frozen Fase-95 length-8 Q8 cubes are analyzed.",
            "Filtration categories are detector-state labels, not transition probabilities.",
            "The zero word is diagnostic and was not simulated.",
            "No claim is made about universal WIDTH=256 basin connectivity.",
        ],
    }
    atomic_write(RESULTS_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    atomic_write(REPORT_PATH, render_report(payload))
    return payload


def main() -> None:
    payload = run()
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
