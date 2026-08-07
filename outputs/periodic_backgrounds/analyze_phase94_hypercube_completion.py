#!/usr/bin/env python3
"""Fase 95: complete frozen length-8 Hamming cubes around long-period states."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


OUT_DIR = Path(__file__).resolve().parent
PHASE94_SCRIPT = OUT_DIR / "analyze_phase93_hamming_topology.py"
PHASE94_RESULTS = OUT_DIR / "phase93_hamming_topology_results.json"
PHASE93_SCRIPT = OUT_DIR / "analyze_phase91_physical_initial_states.py"
PHASE93_RESULTS = OUT_DIR / "phase91_physical_initial_state_results.json"
PHASE91_RESULTS = OUT_DIR / "phase90_long_period_attractor_results.json"
BASE_PATH = OUT_DIR / "sweep_periodic_background_oscillators.py"
CORE_PATH = OUT_DIR / "phase90_resweep_core.py"
RESULTS_PATH = OUT_DIR / "phase94_hypercube_completion_results.json"
REPORT_PATH = OUT_DIR / "phase94_hypercube_completion_report.md"

EXPECTED_CANONICAL_SHA256 = {
    "phase94": "8191312c06a59e6ae8b84528d26f09219f5d000de4ca13e1f8a0d550b6a1f21d",
    "phase93": "4b780a715ea061968593f42e3a9db4b6a84b0a654988a6653b96eb32446eeb3c",
    "phase91": "9da3abaae907c63fc06b440729de0e48f7e433a19b4a729a960f3fae8495e8de",
}
EXPECTED_LONG_NODE_COUNT = 1829
EXPECTED_PHYSICAL_CLASS_COUNT = 192
EXPECTED_PHASE94_EDGE_COUNT = 14632
EXPECTED_BASELINE_DESCRIPTOR_COUNT = 160
EXPECTED_PRIMITIVE_DESCRIPTOR_COUNT = 3136
WIDTH = 256
IC_COUNT = 502
WINDOW_POSITIONS = tuple(range(124, 132))
Q8_NODE_COUNT = 256
Q8_DIRECTED_EDGE_COUNT = 2048
Q8_UNDIRECTED_EDGE_COUNT = 1024


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


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


def background_state_from_hex(value: str) -> tuple[int, ...]:
    bits = int(value, 16)
    return tuple(position for position in range(WIDTH) if (bits >> position) & 1)


def cube_key(cohort: str, rule: int, background_index: int) -> str:
    return f"{cohort}|rule_{int(rule):03d}|bg_{int(background_index):03d}"


def word8_from_diff(background_hex: str, initial_diff: Iterable[int]) -> str:
    background = int(background_hex, 16)
    diff = set(int(position) for position in initial_diff)
    return "".join(
        str(((background >> position) & 1) ^ int(position in diff))
        for position in WINDOW_POSITIONS
    )


def q8_target(word_value: int, flip_position: int) -> int:
    if not 0 <= word_value < Q8_NODE_COUNT:
        raise ValueError("Q8 word is outside 0..255")
    if flip_position not in WINDOW_POSITIONS:
        raise ValueError("Q8 flip is outside positions 124..131")
    offset = flip_position - WINDOW_POSITIONS[0]
    return word_value ^ (1 << (7 - offset))


def q8_edges() -> list[tuple[int, int, int]]:
    edges = [
        (source, q8_target(source, position), position)
        for source in range(Q8_NODE_COUNT)
        for position in WINDOW_POSITIONS
    ]
    if len(edges) != Q8_DIRECTED_EDGE_COUNT:
        raise RuntimeError("Q8 directed-edge count mismatch")
    edge_set = set(edges)
    if any((target, source, position) not in edge_set for source, target, position in edges):
        raise RuntimeError("Q8 reciprocity mismatch")
    undirected = {
        (min(source, target), max(source, target), position)
        for source, target, position in edges
    }
    if len(undirected) != Q8_UNDIRECTED_EDGE_COUNT:
        raise RuntimeError("Q8 undirected-edge count mismatch")
    return edges


def ledger_record_from_bytes(core, payload: bytes, background_index: int, ic_index: int):
    if background_index < 0 or not 0 <= ic_index < IC_COUNT:
        raise ValueError("Ledger address is outside the frozen generator")
    offset = (background_index * IC_COUNT + ic_index) * core.LEDGER_SCHEMA.size
    record = payload[offset : offset + core.LEDGER_SCHEMA.size]
    if len(record) != core.LEDGER_SCHEMA.size:
        raise RuntimeError(f"Incomplete ledger record at byte offset {offset}")
    return core.LedgerRecord.decode(record)


def fragmentation_label(cube_component_counts: list[int]) -> str:
    if not cube_component_counts or any(count < 1 for count in cube_component_counts):
        raise ValueError("A physical class must occupy at least one non-empty cube")
    multiple_cubes = len(cube_component_counts) > 1
    within_fragmented = any(count > 1 for count in cube_component_counts)
    if not multiple_cubes and not within_fragmented:
        return "CONNECTED_SINGLE_CUBE"
    if multiple_cubes and not within_fragmented:
        return "CROSS_CUBE_ONLY"
    if not multiple_cubes and within_fragmented:
        return "WITHIN_CUBE_FRAGMENTED"
    return "MIXED"


def component_words(words: set[int]) -> list[list[int]]:
    unseen = set(words)
    components = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        stack = [root]
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for position in WINDOW_POSITIONS:
                neighbor = q8_target(current, position)
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    stack.append(neighbor)
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


def validate_source(payload: Any, name: str) -> None:
    observed = canonical_sha256(payload)
    expected = EXPECTED_CANONICAL_SHA256[name]
    if observed != expected:
        raise RuntimeError(f"Canonical {name} SHA mismatch: {observed} != {expected}")


def phase94_views(phase94, phase93_payload, edges: list[dict[str, Any]]):
    state_rows = phase93_payload["initial_states"]
    state_by_digest = {row["initial_state_sha256"]: row for row in state_rows}
    phase94.verify_reciprocity(edges, state_by_digest)
    counts = Counter(edge["outcome"] for edge in edges)
    outside_counts = Counter()
    adjacency_same: dict[str, set[str]] = defaultdict(set)
    class_links = Counter()
    for edge in edges:
        if edge["outcome"] == "REPRESENTED_OUTSIDE_LONG_PERIOD_SET":
            detail = edge["ledger"]
            if detail["source_positive"]:
                outside_counts["HISTORICAL_SOURCE_POSITIVE"] += 1
            elif detail["static_t1"]:
                outside_counts["STATIC_T1"] += 1
            else:
                outside_counts[detail["source_kind"]] += 1
        elif edge["outcome"] == "SAME_PHYSICAL_CLASS":
            adjacency_same[edge["source_initial_state_sha256"]].add(
                edge["target_initial_state_sha256"]
            )
        elif edge["outcome"] == "DIFFERENT_LONG_PERIOD_CLASS":
            pair = tuple(
                sorted(
                    (
                        edge["source_physical_class_sha256"],
                        edge["target_physical_class_sha256"],
                    )
                )
            )
            class_links[pair] += 1
    in_set_edges = [edge for edge in edges if edge["target_initial_state_sha256"]]
    undirected_in_set = {
        (
            min(edge["source_initial_state_sha256"], edge["target_initial_state_sha256"]),
            max(edge["source_initial_state_sha256"], edge["target_initial_state_sha256"]),
            int(edge["flip_position"]),
        )
        for edge in in_set_edges
    }
    undirected_same = {
        item
        for item in undirected_in_set
        if state_by_digest[item[0]]["physical_class_sha256"]
        == state_by_digest[item[1]]["physical_class_sha256"]
    }
    nodes_by_class: dict[str, list[str]] = defaultdict(list)
    for row in state_rows:
        nodes_by_class[row["physical_class_sha256"]].append(row["initial_state_sha256"])
    edge_counts_by_class: dict[str, Counter] = defaultdict(Counter)
    for edge in edges:
        edge_counts_by_class[edge["source_physical_class_sha256"]][edge["outcome"]] += 1
    metadata_by_class = {
        row["physical_class_sha256"]: row for row in phase93_payload["physical_classes"]
    }
    class_rows = []
    component_counts = []
    for physical_class, nodes in nodes_by_class.items():
        components = phase94.connected_components(nodes, adjacency_same)
        component_counts.append(len(components))
        edge_counts = edge_counts_by_class[physical_class]
        metadata = metadata_by_class[physical_class]
        class_rows.append(
            {
                "physical_class_sha256": physical_class,
                "node_count": len(nodes),
                "component_count": len(components),
                "component_sizes": [len(component) for component in components],
                "same_class_directed": edge_counts["SAME_PHYSICAL_CLASS"],
                "different_long_class_directed": edge_counts[
                    "DIFFERENT_LONG_PERIOD_CLASS"
                ],
                "represented_outside_long_set": edge_counts[
                    "REPRESENTED_OUTSIDE_LONG_PERIOD_SET"
                ],
                "zero_ic_unsampled": edge_counts["ZERO_IC_UNSAMPLED"],
                "rules": metadata["rules"],
                "defect_periods": metadata["defect_periods"],
            }
        )
    class_rows.sort(key=lambda row: (-row["node_count"], row["physical_class_sha256"]))
    class_graph_rows = [
        {
            "left_physical_class_sha256": pair[0],
            "right_physical_class_sha256": pair[1],
            "directed_edge_count": count,
            "undirected_edge_count": count // 2,
        }
        for pair, count in sorted(class_links.items())
    ]
    summary = {
        "node_count": len(state_rows),
        "physical_class_count": len(class_rows),
        "directed_intervention_count": len(edges),
        "ledger_backed_intervention_count": len(edges) - counts["ZERO_IC_UNSAMPLED"],
        "same_class_count": counts["SAME_PHYSICAL_CLASS"],
        "different_long_class_count": counts["DIFFERENT_LONG_PERIOD_CLASS"],
        "represented_outside_long_set_count": counts[
            "REPRESENTED_OUTSIDE_LONG_PERIOD_SET"
        ],
        "zero_ic_unsampled_count": counts["ZERO_IC_UNSAMPLED"],
        "long_set_retention": (
            counts["SAME_PHYSICAL_CLASS"] + counts["DIFFERENT_LONG_PERIOD_CLASS"]
        )
        / len(edges),
        "same_class_retention": counts["SAME_PHYSICAL_CLASS"] / len(edges),
        "outside_ledger_category_counts": dict(sorted(outside_counts.items())),
        "undirected_in_set_edge_count": len(undirected_in_set),
        "undirected_same_class_edge_count": len(undirected_same),
        "undirected_cross_class_edge_count": len(undirected_in_set) - len(undirected_same),
        "class_graph_link_count": len(class_graph_rows),
        "connected_class_count": sum(count == 1 for count in component_counts),
        "fragmented_class_count": sum(count > 1 for count in component_counts),
        "maximum_component_count": max(component_counts),
        "component_count_distribution": distribution(component_counts),
        "all_eight_same_class_node_count": sum(
            sum(
                edge["outcome"] == "SAME_PHYSICAL_CLASS"
                for edge in edges
                if edge["source_initial_state_sha256"] == node
            )
            == 8
            for node in state_by_digest
        ),
        "reconciliation_failure_count": 0,
        "reciprocity_failure_count": 0,
    }
    return summary, class_rows, class_graph_rows


def require_exact(label: str, observed: Any, expected: Any) -> None:
    if observed == expected:
        return
    if isinstance(observed, list) and isinstance(expected, list):
        for index, (left, right) in enumerate(zip(observed, expected)):
            if left != right:
                raise RuntimeError(
                    f"HYPERCUBE_RECONCILIATION_FAILED: {label} row {index} differs"
                )
        raise RuntimeError(
            f"HYPERCUBE_RECONCILIATION_FAILED: {label} length differs"
        )
    raise RuntimeError(f"HYPERCUBE_RECONCILIATION_FAILED: {label} differs")


def validate_phase94_replay(
    phase94, phase94_payload, phase93_payload, generated_edges: list[dict[str, Any]]
) -> None:
    expected_edges = phase94_payload["edges"]
    if len(generated_edges) != EXPECTED_PHASE94_EDGE_COUNT:
        raise RuntimeError("HYPERCUBE_RECONCILIATION_FAILED: wrong replay edge count")
    require_exact("edge", generated_edges, expected_edges)
    summary, physical_classes, class_graph = phase94_views(
        phase94, phase93_payload, generated_edges
    )
    checks = {
        "summary": (summary, phase94_payload["summary"]),
        "physical_classes": (physical_classes, phase94_payload["physical_classes"]),
        "class_graph": (class_graph, phase94_payload["class_graph"]),
    }
    for label, (observed, expected) in checks.items():
        require_exact(f"Fase-94 {label}", observed, expected)


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 95 - Frozen length-8 hypercube completion",
        "",
        "## Question",
        "",
        "Are the fragmented physical classes from Fase 94 disconnected inside individual background/rule Q8 cubes, or only split across different cubes that cannot share Hamming edges?",
        "",
        "## Frozen protocol",
        "",
        "- Universe: only background/rule cubes that contain at least one of the 1,829 Fase-93 long-period states.",
        "- Each cube is the standard Q8: 256 absolute length-8 words, degree 8, 2,048 directed and 1,024 undirected Hamming-1 edges.",
        "- Both Fase-90 cohorts use the same 502-word generator. Shorter baseline encodings are required to reproduce an exact length-8 alias before inclusion.",
        "- Every non-zero node is classified by an explicit Stage-A LedgerRecord. Word 00000000 remains an unsimulated boundary.",
        "- No edges are created between different cohorts, rules, or background indices.",
        "- No simulation is executed.",
        "",
        "## Source and replay gates",
        "",
        f"- Long nodes reconciled through exact length-8 aliases: {summary['long_node_count']}",
        f"- Baseline descriptors -> unique long nodes: {summary['baseline_source_descriptor_count']} -> {summary['baseline_unique_long_node_count']}",
        f"- Primitive-length-8 descriptors -> unique long nodes: {summary['primitive_source_descriptor_count']} -> {summary['primitive_unique_long_node_count']}",
        f"- Fase-94 directed edges replayed field by field: {summary['phase94_replayed_edge_count']}",
        f"- Fase-94 replay mismatches: {summary['phase94_replay_mismatch_count']}",
        f"- Ledger/candidate reconciliation failures: {summary['ledger_reconciliation_failure_count']}",
        "",
        "## Complete local Q8 atlas",
        "",
        f"- Cubes reconstructed: {summary['cube_count']}",
        f"- Cubes by cohort: `{json.dumps(summary['cube_count_by_cohort'], sort_keys=True)}`",
        f"- Cubes by rule: `{json.dumps(summary['cube_count_by_rule'], sort_keys=True)}`",
        f"- Nodes: {summary['cube_node_count']}",
        f"- Directed edges: {summary['cube_directed_edge_count']}",
        f"- Undirected edges: {summary['cube_undirected_edge_count']}",
        f"- Long-period occupied nodes: {summary['long_node_count']}",
        f"- Long-period occupancy fraction: {summary['long_node_fraction']:.6f}",
        f"- Node-category distribution: `{json.dumps(summary['node_category_counts'], sort_keys=True)}`",
        "",
        "## Fragmentation decomposition",
        "",
        f"- CONNECTED_SINGLE_CUBE: {summary['fragmentation_label_counts'].get('CONNECTED_SINGLE_CUBE', 0)}",
        f"- CROSS_CUBE_ONLY: {summary['fragmentation_label_counts'].get('CROSS_CUBE_ONLY', 0)}",
        f"- WITHIN_CUBE_FRAGMENTED: {summary['fragmentation_label_counts'].get('WITHIN_CUBE_FRAGMENTED', 0)}",
        f"- MIXED: {summary['fragmentation_label_counts'].get('MIXED', 0)}",
        f"- Classes with any within-cube fragmentation: {summary['classes_with_intracube_fragmentation']}",
        f"- Classes fragmented only by cube separation: {summary['classes_fragmented_only_across_cubes']}",
        f"- Minimum inter-component Hamming distribution: `{json.dumps(summary['minimum_intercomponent_hamming_distribution'], sort_keys=True)}`",
        "",
        "## Largest class occupancies",
        "",
        "| nodes | cubes | components | label | fragmented cubes | min Hamming | rules | T |",
        "|---:|---:|---:|---|---:|---:|---|---|",
    ]
    for row in payload["physical_classes"][:20]:
        minimum = row["minimum_intercomponent_hamming"]
        lines.append(
            f"| {row['node_count']} | {row['cube_count']} | {row['component_count']} | "
            f"{row['fragmentation_label']} | {row['fragmented_cube_count']} | "
            f"{minimum if minimum is not None else '-'} | {row['rules']} | {row['defect_periods']} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"`{payload['status']}`",
            "",
            "This result distinguishes fragmentation inside one frozen local Q8 cube from separation across different background/rule cubes. It is not a universal ECA basin topology.",
            "",
            "## Methodological limits",
            "",
            "- The atlas is complete only for length-8 IC words on positions 124..131 and only for frozen backgrounds that contain observed long-period states.",
            "- Word 00000000 was excluded by the historical generator and is retained as an unsimulated boundary node.",
            "- Short-period and external states carry explicit ledger categories but no long-period physical-class identity.",
            "- No inference is made about WIDTH=256 states outside the central eight-bit subspace.",
            "- No paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.",
            "",
        ]
    )
    return "\n".join(lines)


def run(stage_a_root: Path) -> dict[str, Any]:
    phase94 = load_module("fase95_phase94", PHASE94_SCRIPT)
    phase93 = load_module("fase95_phase93", PHASE93_SCRIPT)
    base = load_module("fase95_base", BASE_PATH)
    core = load_module("fase95_core", CORE_PATH)
    phase94_payload = json.loads(PHASE94_RESULTS.read_text(encoding="utf-8"))
    phase93_payload = json.loads(PHASE93_RESULTS.read_text(encoding="utf-8"))
    phase91_payload = json.loads(PHASE91_RESULTS.read_text(encoding="utf-8"))
    validate_source(phase94_payload, "phase94")
    validate_source(phase93_payload, "phase93")
    validate_source(phase91_payload, "phase91")
    state_rows = phase93_payload["initial_states"]
    phase91_rows = phase91_payload["cases"]
    if len(state_rows) != EXPECTED_LONG_NODE_COUNT:
        raise RuntimeError("Unexpected Fase-93 node count")
    if len(phase93_payload["physical_classes"]) != EXPECTED_PHYSICAL_CLASS_COUNT:
        raise RuntimeError("Unexpected Fase-93 class count")
    baseline_descriptor_count = sum(
        row["cohort"] == "baseline_period_1_2_4" for row in phase91_rows
    )
    primitive_descriptor_count = sum(
        row["cohort"] == "primitive_len8" for row in phase91_rows
    )
    if baseline_descriptor_count != EXPECTED_BASELINE_DESCRIPTOR_COUNT:
        raise RuntimeError("Unexpected baseline source-descriptor count")
    if primitive_descriptor_count != EXPECTED_PRIMITIVE_DESCRIPTOR_COUNT:
        raise RuntimeError("Unexpected primitive source-descriptor count")

    state_by_digest = {row["initial_state_sha256"]: row for row in state_rows}
    state_by_key = {
        (
            int(row["rule"]),
            row["background_t0_absolute"],
            tuple(int(value) for value in row["initial_diff_absolute"]),
        ): row
        for row in state_rows
    }
    source_rows_by_digest: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in phase91_rows:
        derived = phase93.derive_initial_state(row, base)
        source_rows_by_digest[derived["strict_sha256"]].append(row)
    if set(source_rows_by_digest) != set(state_by_digest):
        raise RuntimeError("Fase-91 rows do not reconcile to Fase-93 nodes")

    representatives = {}
    cube_metadata = {}
    for digest, rows in source_rows_by_digest.items():
        locations = {
            (row["cohort"], int(row["rule"]), int(row["background_index"]))
            for row in rows
        }
        if len(locations) != 1:
            raise RuntimeError("One strict state spans multiple frozen cube locations")
        cohort, rule, background_index = next(iter(locations))
        key = cube_key(cohort, rule, background_index)
        source = state_by_digest[digest]
        background_hexes = {
            phase93.derive_initial_state(row, base)["background_t0_absolute"] for row in rows
        }
        if background_hexes != {source["background_t0_absolute"]}:
            raise RuntimeError("Cube background differs from the strict physical state")
        word8 = word8_from_diff(
            source["background_t0_absolute"], source["initial_diff_absolute"]
        )
        background_state = background_state_from_hex(source["background_t0_absolute"])
        alias_diff = base.initial_diff(int(word8, 2), 8, background_state)
        if alias_diff != tuple(int(value) for value in source["initial_diff_absolute"]):
            raise RuntimeError("Length-8 alias does not reproduce the strict initial state")
        representatives[digest] = {
            "cube_key": key,
            "word8": word8,
            "cohort": cohort,
            "rule": rule,
            "background_index": background_index,
        }
        metadata = cube_metadata.setdefault(
            key,
            {
                "cube_key": key,
                "cohort": cohort,
                "rule": rule,
                "background_index": background_index,
                "background_t0_absolute": source["background_t0_absolute"],
            },
        )
        if metadata["background_t0_absolute"] != source["background_t0_absolute"]:
            raise RuntimeError("One cube key maps to multiple absolute backgrounds")

    words = list(base.ic_words())
    word_index = {
        (int(length), word): index for index, (length, _, word) in enumerate(words)
    }
    length8_indices = [word_index[(8, format(value, "08b"))] for value in range(1, 256)]
    if length8_indices != list(range(247, 502)):
        raise RuntimeError("Frozen length-8 IC index range is not 247..501")

    ledger_artifacts = {}
    ledger_bytes = {}
    for cohort, rule in sorted(
        {(row["cohort"], int(row["rule"])) for row in representatives.values()}
    ):
        prefix = stage_a_root / cohort / f"rule_{rule:03d}"
        ledger_path = Path(str(prefix) + ".ledger.bin")
        manifest_path = Path(str(prefix) + ".manifest.json")
        artifact = phase94.validate_ledger_artifact(
            core=core, ledger_path=ledger_path, manifest_path=manifest_path
        )
        ledger_artifacts[(cohort, rule)] = {
            field: value for field, value in artifact.items() if field != "path"
        }
        ledger_bytes[(cohort, rule)] = ledger_path.read_bytes()

    cube_nodes: dict[str, dict[int, dict[str, Any]]] = {}
    category_counts = Counter()
    long_node_locations = {}
    for key, metadata in sorted(cube_metadata.items()):
        cohort = metadata["cohort"]
        rule = int(metadata["rule"])
        background_index = int(metadata["background_index"])
        background_hex = metadata["background_t0_absolute"]
        background_state = background_state_from_hex(background_hex)
        nodes = {}
        for value in range(256):
            word = format(value, "08b")
            initial_diff = base.initial_diff(value, 8, background_state)
            strict_payload = phase93.strict_initial_payload(
                rule=rule,
                background_state=background_state,
                initial_diff=initial_diff,
            )
            strict_digest = phase93.sha256_json(strict_payload)
            long_state = state_by_key.get((rule, background_hex, initial_diff))
            if value == 0:
                if long_state is not None:
                    raise RuntimeError("Zero word unexpectedly belongs to the long set")
                category = "ZERO_IC_BOUNDARY_UNSAMPLED"
                physical_class = None
                ledger = None
            else:
                record = ledger_record_from_bytes(
                    core,
                    ledger_bytes[(cohort, rule)],
                    background_index,
                    word_index[(8, word)],
                )
                ledger = phase94.ledger_detail(core, record)
                if ledger["cap_candidate"]:
                    if long_state is None:
                        raise RuntimeError(
                            "Ledger cap candidate is absent from Fase-93 strict states"
                        )
                    category = "LONG_PERIOD_CAP_CANDIDATE"
                    physical_class = long_state["physical_class_sha256"]
                    if strict_digest != long_state["initial_state_sha256"]:
                        raise RuntimeError("Long-state strict hash mismatch")
                else:
                    if long_state is not None:
                        raise RuntimeError("Long Fase-93 state lacks cap-candidate flag")
                    category = phase94.outside_category(core, record)
                    physical_class = None
            node = {
                "word8": word,
                "strict_initial_state_sha256": strict_digest,
                "initial_diff_absolute": list(initial_diff),
                "category": category,
                "physical_class_sha256": physical_class,
                "ledger": ledger,
            }
            nodes[value] = node
            category_counts[category] += 1
            if physical_class is not None:
                if strict_digest in long_node_locations:
                    raise RuntimeError("One strict long state appears in multiple cubes")
                long_node_locations[strict_digest] = (key, value)
        if len(nodes) != Q8_NODE_COUNT:
            raise RuntimeError("A cube does not contain exactly 256 nodes")
        cube_nodes[key] = nodes
    if set(long_node_locations) != set(state_by_digest):
        raise RuntimeError("Hypercube long nodes do not reconcile to Fase 93")

    baseline_unique_long_count = sum(
        representatives[digest]["cohort"] == "baseline_period_1_2_4"
        for digest in state_by_digest
    )
    generated_phase94_edges = []
    for source in sorted(state_rows, key=lambda row: row["initial_state_sha256"]):
        source_digest = source["initial_state_sha256"]
        key, source_value = long_node_locations[source_digest]
        for position in WINDOW_POSITIONS:
            target = cube_nodes[key][q8_target(source_value, position)]
            if target["category"] == "ZERO_IC_BOUNDARY_UNSAMPLED":
                outcome = "ZERO_IC_UNSAMPLED"
                target_digest = None
                target_class = None
                ledger = None
            elif target["category"] == "LONG_PERIOD_CAP_CANDIDATE":
                target_digest = target["strict_initial_state_sha256"]
                target_class = target["physical_class_sha256"]
                outcome = (
                    "SAME_PHYSICAL_CLASS"
                    if target_class == source["physical_class_sha256"]
                    else "DIFFERENT_LONG_PERIOD_CLASS"
                )
                ledger = target["ledger"]
            else:
                outcome = "REPRESENTED_OUTSIDE_LONG_PERIOD_SET"
                target_digest = None
                target_class = None
                ledger = target["ledger"]
            generated_phase94_edges.append(
                {
                    "source_initial_state_sha256": source_digest,
                    "target_initial_state_sha256": target_digest,
                    "source_physical_class_sha256": source["physical_class_sha256"],
                    "target_physical_class_sha256": target_class,
                    "flip_position": position,
                    "target_word8": target["word8"],
                    "outcome": outcome,
                    "ledger": ledger,
                }
            )
    validate_phase94_replay(
        phase94, phase94_payload, phase93_payload, generated_phase94_edges
    )

    adjacency_directed = Counter()
    adjacency_undirected = Counter()
    cube_rows = []
    class_cube_words: dict[str, dict[str, set[int]]] = defaultdict(
        lambda: defaultdict(set)
    )
    frozen_q8_edges = q8_edges()
    for key, nodes in sorted(cube_nodes.items()):
        directed_long_to_long = 0
        directed_same_class = 0
        for source_value, target_value, _ in frozen_q8_edges:
            source = nodes[source_value]
            target = nodes[target_value]
            adjacency_directed[(source["category"], target["category"])] += 1
            if (
                source["category"] == "LONG_PERIOD_CAP_CANDIDATE"
                and target["category"] == "LONG_PERIOD_CAP_CANDIDATE"
            ):
                directed_long_to_long += 1
                if source["physical_class_sha256"] == target["physical_class_sha256"]:
                    directed_same_class += 1
        for source_value in range(256):
            for bit_index in range(8):
                target_value = source_value ^ (1 << bit_index)
                if source_value < target_value:
                    pair = tuple(
                        sorted(
                            (
                                nodes[source_value]["category"],
                                nodes[target_value]["category"],
                            )
                        )
                    )
                    adjacency_undirected[pair] += 1
        per_cube_categories = Counter(node["category"] for node in nodes.values())
        for value, node in nodes.items():
            if node["physical_class_sha256"] is not None:
                class_cube_words[node["physical_class_sha256"]][key].add(value)
        cube_rows.append(
            {
                **cube_metadata[key],
                "node_count": 256,
                "directed_edge_count": 2048,
                "undirected_edge_count": 1024,
                "category_counts": dict(sorted(per_cube_categories.items())),
                "long_node_count": per_cube_categories["LONG_PERIOD_CAP_CANDIDATE"],
                "directed_long_to_long": directed_long_to_long,
                "directed_same_class": directed_same_class,
            }
        )

    metadata_by_class = {
        row["physical_class_sha256"]: row for row in phase93_payload["physical_classes"]
    }
    physical_class_rows = []
    minimum_hamming_values = []
    for physical_class, by_cube in class_cube_words.items():
        cube_details = []
        all_minimums = []
        for key, words_in_class in sorted(by_cube.items()):
            components = component_words(words_in_class)
            minimum = minimum_component_hamming(components)
            if minimum is not None:
                all_minimums.append(minimum)
                minimum_hamming_values.append(minimum)
            cube_details.append(
                {
                    "cube_key": key,
                    "node_count": len(words_in_class),
                    "component_count": len(components),
                    "component_sizes": [len(component) for component in components],
                    "minimum_intercomponent_hamming": minimum,
                }
            )
        component_counts = [row["component_count"] for row in cube_details]
        label = fragmentation_label(component_counts)
        metadata = metadata_by_class[physical_class]
        phase94_class = next(
            row
            for row in phase94_payload["physical_classes"]
            if row["physical_class_sha256"] == physical_class
        )
        if sum(component_counts) != phase94_class["component_count"]:
            raise RuntimeError("Per-cube components do not reconcile to Fase 94")
        physical_class_rows.append(
            {
                "physical_class_sha256": physical_class,
                "node_count": sum(len(words) for words in by_cube.values()),
                "cube_count": len(by_cube),
                "component_count": sum(component_counts),
                "fragmented_cube_count": sum(count > 1 for count in component_counts),
                "fragmentation_label": label,
                "minimum_intercomponent_hamming": min(all_minimums)
                if all_minimums
                else None,
                "rules": metadata["rules"],
                "defect_periods": metadata["defect_periods"],
                "cubes": cube_details,
            }
        )
    physical_class_rows.sort(
        key=lambda row: (-row["node_count"], row["physical_class_sha256"])
    )
    label_counts = Counter(row["fragmentation_label"] for row in physical_class_rows)
    cross_only = label_counts["CROSS_CUBE_ONLY"]
    within_count = label_counts["WITHIN_CUBE_FRAGMENTED"] + label_counts["MIXED"]
    if within_count and cross_only:
        verdict = "MIXED_FRAGMENTATION_STRUCTURE"
    elif within_count:
        verdict = "INTRACUBE_FRAGMENTATION_CONFIRMED"
    else:
        verdict = "FRAGMENTATION_EXPLAINED_BY_CUBE_SEPARATION"

    cube_count = len(cube_rows)
    summary = {
        "cube_count": cube_count,
        "cube_count_by_cohort": distribution(
            row["cohort"] for row in cube_rows
        ),
        "cube_count_by_rule": distribution(row["rule"] for row in cube_rows),
        "cube_node_count": cube_count * Q8_NODE_COUNT,
        "cube_directed_edge_count": cube_count * Q8_DIRECTED_EDGE_COUNT,
        "cube_undirected_edge_count": cube_count * Q8_UNDIRECTED_EDGE_COUNT,
        "long_node_count": len(long_node_locations),
        "baseline_source_descriptor_count": baseline_descriptor_count,
        "baseline_unique_long_node_count": baseline_unique_long_count,
        "primitive_source_descriptor_count": primitive_descriptor_count,
        "primitive_unique_long_node_count": len(long_node_locations)
        - baseline_unique_long_count,
        "long_node_fraction": len(long_node_locations) / (cube_count * 256),
        "physical_class_count": len(physical_class_rows),
        "node_category_counts": dict(sorted(category_counts.items())),
        "fragmentation_label_counts": dict(sorted(label_counts.items())),
        "classes_with_intracube_fragmentation": within_count,
        "classes_fragmented_only_across_cubes": cross_only,
        "minimum_intercomponent_hamming_distribution": distribution(
            minimum_hamming_values
        ),
        "phase94_replayed_edge_count": len(generated_phase94_edges),
        "phase94_replay_mismatch_count": 0,
        "ledger_reconciliation_failure_count": 0,
    }
    payload = {
        "phase": 95,
        "status": verdict,
        "source_canonical_sha256": EXPECTED_CANONICAL_SHA256,
        "protocol": {
            "width": WIDTH,
            "window_positions": list(WINDOW_POSITIONS),
            "cube": "Q8",
            "nodes_per_cube": Q8_NODE_COUNT,
            "directed_edges_per_cube": Q8_DIRECTED_EDGE_COUNT,
            "undirected_edges_per_cube": Q8_UNDIRECTED_EDGE_COUNT,
            "adjacency": "HAMMING_DISTANCE_1_ONLY",
            "classification_source": "Fase-90 Stage-A complete binary ledgers",
            "zero_word_policy": "UNSAMPLED_BOUNDARY_NO_SIMULATION",
            "simulation_executed": False,
        },
        "ledger_artifacts": [
            ledger_artifacts[key] for key in sorted(ledger_artifacts)
        ],
        "summary": summary,
        "directed_category_adjacency": [
            {"source_category": pair[0], "target_category": pair[1], "count": count}
            for pair, count in sorted(adjacency_directed.items())
        ],
        "undirected_category_adjacency": [
            {"left_category": pair[0], "right_category": pair[1], "count": count}
            for pair, count in sorted(adjacency_undirected.items())
        ],
        "cubes": cube_rows,
        "physical_classes": physical_class_rows,
        "cube_nodes": [
            {
                **cube_metadata[key],
                "nodes": [cube_nodes[key][value] for value in range(256)],
            }
            for key in sorted(cube_nodes)
        ],
        "phase94_replay": {
            "status": "EXACT_FIELD_BY_FIELD_MATCH",
            "edge_count": len(generated_phase94_edges),
            "edges_canonical_sha256": canonical_sha256(generated_phase94_edges),
            "summary_canonical_sha256": canonical_sha256(phase94_payload["summary"]),
            "physical_classes_canonical_sha256": canonical_sha256(
                phase94_payload["physical_classes"]
            ),
            "class_graph_canonical_sha256": canonical_sha256(
                phase94_payload["class_graph"]
            ),
        },
        "methodological_limits": [
            "Complete topology is limited to frozen length-8 IC cubes on positions 124..131.",
            "Only cubes already containing an observed long-period node are reconstructed.",
            "The zero word remains an unsimulated boundary node.",
            "No claim is made about the complete WIDTH=256 basin topology.",
        ],
    }
    atomic_write(RESULTS_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n")
    atomic_write(REPORT_PATH, render_report(payload))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage-a-root",
        type=Path,
        default=Path(
            os.environ.get(
                "ZUSE_PHASE90_STAGE_A",
                str(OUT_DIR / "fase90" / "stage_a"),
            )
        ),
    )
    args = parser.parse_args()
    payload = run(args.stage_a_root.resolve())
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
