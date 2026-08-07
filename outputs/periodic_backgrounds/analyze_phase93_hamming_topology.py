#!/usr/bin/env python3
"""Fase 94: catalog-induced Hamming-1 topology of long-period occupancy."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any, Iterable


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parent.parent
PHASE93_SCRIPT = OUT_DIR / "analyze_phase91_physical_initial_states.py"
PHASE93_RESULTS = OUT_DIR / "phase91_physical_initial_state_results.json"
PHASE91_RESULTS = OUT_DIR / "phase90_long_period_attractor_results.json"
BASE_PATH = OUT_DIR / "sweep_periodic_background_oscillators.py"
CORE_PATH = OUT_DIR / "phase90_resweep_core.py"
RESULTS_PATH = OUT_DIR / "phase93_hamming_topology_results.json"
REPORT_PATH = OUT_DIR / "phase93_hamming_topology_report.md"

EXPECTED_PHASE93_SHA256 = "df555a49a5ad23e55db46427d5a8fb88ee77c9055ff226b0ec6439dc9695dde1"
EXPECTED_PHASE91_SHA256 = "a2ce55599fde30ed425dead579869399c260ba4752d551555933d33a16ff178a"
EXPECTED_NODE_COUNT = 1829
EXPECTED_CLASS_COUNT = 192
EXPECTED_FLIP_COUNT = EXPECTED_NODE_COUNT * 8
IC_COUNT = 502
WIDTH = 256
WINDOW_POSITIONS = tuple(range(WIDTH // 2 - 8 // 2, WIDTH // 2 - 8 // 2 + 8))


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def distribution(values: Iterable[Any]) -> dict[str, int]:
    return {
        str(key): value
        for key, value in sorted(Counter(values).items(), key=lambda item: str(item[0]))
    }


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    with temporary.open("r+b") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def validate_window() -> None:
    if WINDOW_POSITIONS != tuple(range(124, 132)):
        raise RuntimeError(f"Unexpected intervention window: {WINDOW_POSITIONS}")
    if len(WINDOW_POSITIONS) != 8 or len(set(WINDOW_POSITIONS)) != 8:
        raise RuntimeError("Intervention window must contain eight unique positions")


def flip_diff(diff: tuple[int, ...], position: int) -> tuple[int, ...]:
    if position not in WINDOW_POSITIONS:
        raise ValueError(f"Flip position {position} is outside the frozen window")
    source = set(int(value) for value in diff)
    target = source.symmetric_difference({int(position)})
    if len(source.symmetric_difference(target)) != 1:
        raise RuntimeError("Hamming intervention did not change exactly one cell")
    return tuple(sorted(target))


def desired_word8(
    *, background_hex: str, initial_diff: tuple[int, ...]
) -> str:
    background = int(background_hex, 16)
    diff = set(initial_diff)
    return "".join(
        str(((background >> position) & 1) ^ int(position in diff))
        for position in WINDOW_POSITIONS
    )


def ledger_record_at(
    *,
    core,
    ledger_path: Path,
    background_index: int,
    ic_index: int,
):
    if background_index < 0 or ic_index < 0 or ic_index >= IC_COUNT:
        raise ValueError("Ledger address is outside the frozen generator")
    offset = (background_index * IC_COUNT + ic_index) * core.LEDGER_SCHEMA.size
    with ledger_path.open("rb") as handle:
        handle.seek(offset)
        payload = handle.read(core.LEDGER_SCHEMA.size)
    if len(payload) != core.LEDGER_SCHEMA.size:
        raise RuntimeError(f"Incomplete ledger record at byte offset {offset}")
    return core.LedgerRecord.decode(payload)


def validate_ledger_artifact(
    *, core, ledger_path: Path, manifest_path: Path
) -> dict[str, Any]:
    if not ledger_path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError(f"Missing ledger or manifest: {ledger_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("phase") != 90 or manifest.get("stage") != "A":
        raise RuntimeError("Ledger manifest is not a Fase-90 Stage-A manifest")
    artifact = manifest["artifacts"]["ledger"]
    core.validate_artifact(
        ledger_path, int(artifact["size"]), str(artifact["sha256"])
    )
    expected_size = int(manifest["processed_runs"]) * core.LEDGER_SCHEMA.size
    if ledger_path.stat().st_size != expected_size:
        raise RuntimeError("Ledger size does not match processed run count")
    return {
        "cohort": manifest["cohort"],
        "rule": int(manifest["rule"]),
        "processed_runs": int(manifest["processed_runs"]),
        "size": ledger_path.stat().st_size,
        "sha256": core.sha256_file(ledger_path),
        "manifest_sha256": core.sha256_file(manifest_path),
        "path": str(ledger_path),
    }


def ledger_detail(core, record) -> dict[str, Any]:
    return {
        "source_kind": core.Kind(int(record.source_kind)).name,
        "expanded_kind": core.Kind(int(record.expanded_kind)).name,
        "source_period": int(record.source_period),
        "expanded_period": int(record.expanded_period),
        "source_drift": int(record.source_drift),
        "expanded_drift": int(record.expanded_drift),
        "flags": int(record.flags),
        "bounded_source": bool(record.flags & core.FLAG_BOUNDED_SOURCE),
        "source_positive": bool(record.flags & core.FLAG_SOURCE_POSITIVE),
        "cap_candidate": bool(record.flags & core.FLAG_CAP_CANDIDATE),
        "static_t1": bool(record.flags & core.FLAG_STATIC_T1),
    }


def outside_category(core, record) -> str:
    if record.flags & core.FLAG_CAP_CANDIDATE:
        raise RuntimeError("Missing long-period neighbor has cap-candidate flag")
    kind = core.Kind(int(record.source_kind))
    if record.flags & core.FLAG_SOURCE_POSITIVE:
        if kind not in {core.Kind.STATIONARY, core.Kind.MOVING}:
            raise RuntimeError("Source-positive flag has an incompatible kind")
        return "HISTORICAL_SOURCE_POSITIVE"
    if record.flags & core.FLAG_STATIC_T1:
        return "STATIC_T1"
    mapping = {
        core.Kind.ZERO_INITIAL_DEFECT: "ZERO_INITIAL_DEFECT",
        core.Kind.EXTINCT: "EXTINCT",
        core.Kind.SPAN_ESCAPE: "SPAN_ESCAPE",
    }
    if kind in mapping:
        return mapping[kind]
    return "OTHER_EXPLICIT_LEDGER_STATE"


def verify_reciprocity(
    edges: list[dict[str, Any]],
    state_by_digest: dict[str, dict[str, Any]] | None = None,
) -> None:
    internal = {
        (edge["source_initial_state_sha256"], edge["target_initial_state_sha256"], edge["flip_position"])
        for edge in edges
        if edge["target_initial_state_sha256"] is not None
    }
    for source, target, position in internal:
        if (target, source, position) not in internal:
            raise RuntimeError(
                f"Missing reciprocal edge for {source}->{target} at {position}"
            )
        if state_by_digest is not None:
            source_row = state_by_digest[source]
            target_row = state_by_digest[target]
            if int(source_row["rule"]) != int(target_row["rule"]):
                raise RuntimeError("Reciprocal edge changes the ECA rule")
            if source_row["background_t0_absolute"] != target_row["background_t0_absolute"]:
                raise RuntimeError("Reciprocal edge changes the absolute background")
            source_diff = tuple(int(value) for value in source_row["initial_diff_absolute"])
            target_diff = tuple(int(value) for value in target_row["initial_diff_absolute"])
            if flip_diff(target_diff, position) != source_diff:
                raise RuntimeError(
                    f"Reverse flip does not recover source {source} at {position}"
                )


def connected_components(
    nodes: list[str], adjacency: dict[str, set[str]]
) -> list[list[str]]:
    unseen = set(nodes)
    components = []
    while unseen:
        root = min(unseen)
        unseen.remove(root)
        queue = deque([root])
        component = []
        while queue:
            current = queue.popleft()
            component.append(current)
            for neighbor in sorted(adjacency.get(current, set())):
                if neighbor in unseen:
                    unseen.remove(neighbor)
                    queue.append(neighbor)
        components.append(sorted(component))
    return sorted(components, key=lambda values: (-len(values), values[0]))


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 94 - Catalog-induced Hamming-1 topology",
        "",
        "## Question",
        "",
        "Within the frozen observed long-period occupancy, does a one-cell intervention remain in the same attractor, move to another long-period class, or leave the recovered long-period set?",
        "",
        "## Frozen protocol and positive evidence",
        "",
        "- Nodes: exactly the 1,829 strict physical initial states from Fase 93.",
        "- Interventions: one flip at each absolute position 124..131; exactly eight directed flips per node.",
        "- Every non-zero target is addressed in the complete Fase-90 Stage-A binary ledger by cohort, rule, background index, and length-8 IC index.",
        "- Ledger size and SHA-256 are validated against each Stage-A manifest before graph construction.",
        "- Absence is never interpreted as a negative. A represented target outside the long-period set must have an explicit non-candidate LedgerRecord.",
        "- In-set edges require reciprocal cap-candidate evidence and a real reverse edge at the same flipped cell.",
        "- No simulation is executed.",
        "",
        "## Reconciliation",
        "",
        f"- Nodes: {summary['node_count']}",
        f"- Directed interventions: {summary['directed_intervention_count']}",
        f"- Ledger-backed non-zero interventions: {summary['ledger_backed_intervention_count']}",
        f"- Zero-IC unsampled interventions: {summary['zero_ic_unsampled_count']}",
        f"- Reconciliation failures: {summary['reconciliation_failure_count']}",
        f"- Internal reciprocal edge failures: {summary['reciprocity_failure_count']}",
        "",
        "## Directed outcomes",
        "",
        f"- Same physical class: {summary['same_class_count']}",
        f"- Different long-period class: {summary['different_long_class_count']}",
        f"- Represented outside long-period set: {summary['represented_outside_long_set_count']}",
        f"- Zero IC unsampled: {summary['zero_ic_unsampled_count']}",
        f"- Retained anywhere in long-period set: {summary['long_set_retention']:.6f}",
        f"- Retained in the same class: {summary['same_class_retention']:.6f}",
        "",
        "## Explicit ledger outcomes outside the long-period set",
        "",
        f"`{json.dumps(summary['outside_ledger_category_counts'], sort_keys=True)}`",
        "",
        "## Graph structure",
        "",
        f"- Undirected in-set edges: {summary['undirected_in_set_edge_count']}",
        f"- Undirected same-class edges: {summary['undirected_same_class_edge_count']}",
        f"- Undirected cross-class edges: {summary['undirected_cross_class_edge_count']}",
        f"- Weighted class-to-class links: {summary['class_graph_link_count']}",
        f"- Internally connected physical classes: {summary['connected_class_count']}",
        f"- Internally fragmented physical classes: {summary['fragmented_class_count']}",
        f"- Maximum internal component count: {summary['maximum_component_count']}",
        f"- Nodes with all eight flips in the same class: {summary['all_eight_same_class_node_count']}",
        f"- Internal component-count distribution: `{json.dumps(summary['component_count_distribution'], sort_keys=True)}`",
        "",
        "## Largest class occupancies and internal topology",
        "",
        "| nodes | components | same exits | cross exits | ledger exits | zero exits | rules | T |",
        "|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in payload["physical_classes"][:15]:
        lines.append(
            f"| {row['node_count']} | {row['component_count']} | {row['same_class_directed']} | "
            f"{row['different_long_class_directed']} | {row['represented_outside_long_set']} | "
            f"{row['zero_ic_unsampled']} | {row['rules']} | {row['defect_periods']} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"`{payload['status']}`",
            "",
            "This is the catalog-induced Hamming-1 topology of observed long-period occupancy. It is not the complete basin topology of the ECA configuration space.",
            "",
            "## Methodological limits",
            "",
            "- Nodes are restricted to the 1,829 deduplicated long-period states from the two frozen Fase-90 cohorts.",
            "- The intervention window is the fixed central length-8 IC support; flips elsewhere in WIDTH=256 are not tested.",
            "- REPRESENTED_OUTSIDE_LONG_PERIOD_SET is backed by an explicit Stage-A ledger record but is not called negative: it includes short-period positives and other detector outcomes.",
            "- Zero IC was excluded by the historical generator and remains an unsimulated, separately counted boundary.",
            "- No paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.",
            "",
        ]
    )
    return "\n".join(lines)


def run(stage_a_root: Path) -> dict[str, Any]:
    validate_window()
    if sha256_file(PHASE93_RESULTS) != EXPECTED_PHASE93_SHA256:
        raise RuntimeError("Fase-93 source SHA-256 mismatch")
    if sha256_file(PHASE91_RESULTS) != EXPECTED_PHASE91_SHA256:
        raise RuntimeError("Fase-91 source SHA-256 mismatch")
    phase93 = load_module("fase94_phase93", PHASE93_SCRIPT)
    base = load_module("fase94_base", BASE_PATH)
    core = load_module("fase94_core", CORE_PATH)
    phase93_payload = json.loads(PHASE93_RESULTS.read_text(encoding="utf-8"))
    phase91_rows = json.loads(PHASE91_RESULTS.read_text(encoding="utf-8"))["cases"]
    state_rows = phase93_payload["initial_states"]
    if len(state_rows) != EXPECTED_NODE_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_NODE_COUNT} Fase-93 nodes")
    if len(phase93_payload["physical_classes"]) != EXPECTED_CLASS_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_CLASS_COUNT} physical classes")

    state_by_digest = {row["initial_state_sha256"]: row for row in state_rows}
    state_by_key = {
        (
            int(row["rule"]),
            row["background_t0_absolute"],
            tuple(int(value) for value in row["initial_diff_absolute"]),
        ): row
        for row in state_rows
    }
    if len(state_by_digest) != EXPECTED_NODE_COUNT or len(state_by_key) != EXPECTED_NODE_COUNT:
        raise RuntimeError("Fase-93 nodes are not unique")

    representative_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in phase91_rows:
        derived = phase93.derive_initial_state(row, base)
        representative_rows[derived["strict_sha256"]].append(row)
    if set(representative_rows) != set(state_by_digest):
        raise RuntimeError("Fase-91 rows do not reconcile to Fase-93 states")
    representatives = {}
    for digest, rows in representative_rows.items():
        locations = {(row["cohort"], int(row["background_index"])) for row in rows}
        if len(locations) != 1:
            raise RuntimeError("One physical state spans incompatible ledger locations")
        representatives[digest] = rows[0]

    words = list(base.ic_words())
    word_index = {(int(length), word): index for index, (length, _, word) in enumerate(words)}
    ledger_artifacts = {}
    for cohort, rule in sorted(
        {(row["cohort"], int(row["rule"])) for row in representatives.values()}
    ):
        prefix = stage_a_root / cohort / f"rule_{rule:03d}"
        artifact = validate_ledger_artifact(
            core=core,
            ledger_path=Path(str(prefix) + ".ledger.bin"),
            manifest_path=Path(str(prefix) + ".manifest.json"),
        )
        ledger_artifacts[(cohort, rule)] = artifact

    edges = []
    outside_counts = Counter()
    adjacency_same: dict[str, set[str]] = defaultdict(set)
    class_links = Counter()
    for source in sorted(state_rows, key=lambda row: row["initial_state_sha256"]):
        source_digest = source["initial_state_sha256"]
        source_diff = tuple(int(value) for value in source["initial_diff_absolute"])
        if not set(source_diff).issubset(WINDOW_POSITIONS):
            raise RuntimeError("Source defect extends outside the frozen IC window")
        target_digests = set()
        representative = representatives[source_digest]
        ledger_path = Path(
            ledger_artifacts[(representative["cohort"], int(source["rule"]))]["path"]
        )
        for position in WINDOW_POSITIONS:
            target_diff = flip_diff(source_diff, position)
            target_payload = phase93.strict_initial_payload(
                rule=int(source["rule"]),
                background_state=tuple(
                    index
                    for index in range(WIDTH)
                    if (int(source["background_t0_absolute"], 16) >> index) & 1
                ),
                initial_diff=target_diff,
            )
            target_digest = phase93.sha256_json(target_payload)
            if target_digest == source_digest or target_digest in target_digests:
                raise RuntimeError("A node did not produce eight distinct Hamming neighbors")
            target_digests.add(target_digest)
            target = state_by_key.get(
                (int(source["rule"]), source["background_t0_absolute"], target_diff)
            )
            word = desired_word8(
                background_hex=source["background_t0_absolute"],
                initial_diff=target_diff,
            )
            if int(word, 2) == 0:
                if target is not None:
                    raise RuntimeError("Zero IC unexpectedly appears in Fase-93 nodes")
                edges.append(
                    {
                        "source_initial_state_sha256": source_digest,
                        "target_initial_state_sha256": None,
                        "source_physical_class_sha256": source["physical_class_sha256"],
                        "target_physical_class_sha256": None,
                        "flip_position": position,
                        "target_word8": word,
                        "outcome": "ZERO_IC_UNSAMPLED",
                        "ledger": None,
                    }
                )
                continue
            ic_index = word_index[(8, word)]
            record = ledger_record_at(
                core=core,
                ledger_path=ledger_path,
                background_index=int(representative["background_index"]),
                ic_index=ic_index,
            )
            detail = ledger_detail(core, record)
            if target is not None:
                if not detail["cap_candidate"]:
                    raise RuntimeError("Long-period neighbor lacks cap-candidate ledger flag")
                same_class = (
                    target["physical_class_sha256"]
                    == source["physical_class_sha256"]
                )
                outcome = (
                    "SAME_PHYSICAL_CLASS"
                    if same_class
                    else "DIFFERENT_LONG_PERIOD_CLASS"
                )
                if same_class:
                    adjacency_same[source_digest].add(target["initial_state_sha256"])
                else:
                    class_links[
                        tuple(
                            sorted(
                                (
                                    source["physical_class_sha256"],
                                    target["physical_class_sha256"],
                                )
                            )
                        )
                    ] += 1
                target_digest_value = target["initial_state_sha256"]
                target_class = target["physical_class_sha256"]
            else:
                category = outside_category(core, record)
                outside_counts[category] += 1
                outcome = "REPRESENTED_OUTSIDE_LONG_PERIOD_SET"
                target_digest_value = None
                target_class = None
            edges.append(
                {
                    "source_initial_state_sha256": source_digest,
                    "target_initial_state_sha256": target_digest_value,
                    "source_physical_class_sha256": source["physical_class_sha256"],
                    "target_physical_class_sha256": target_class,
                    "flip_position": position,
                    "target_word8": word,
                    "outcome": outcome,
                    "ledger": detail,
                }
            )
        if len(target_digests) != 8:
            raise RuntimeError("A node did not produce exactly eight unique targets")

    if len(edges) != EXPECTED_FLIP_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_FLIP_COUNT} directed interventions")
    verify_reciprocity(edges, state_by_digest)
    counts = Counter(edge["outcome"] for edge in edges)
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
        nodes_by_class[row["physical_class_sha256"]].append(
            row["initial_state_sha256"]
        )
    edge_counts_by_class: dict[str, Counter] = defaultdict(Counter)
    for edge in edges:
        edge_counts_by_class[edge["source_physical_class_sha256"]][edge["outcome"]] += 1
    source_class_metadata = {
        row["physical_class_sha256"]: row
        for row in phase93_payload["physical_classes"]
    }
    class_rows = []
    component_counts = []
    for physical_class, nodes in nodes_by_class.items():
        components = connected_components(nodes, adjacency_same)
        component_count = len(components)
        component_counts.append(component_count)
        counts_for_class = edge_counts_by_class[physical_class]
        metadata = source_class_metadata[physical_class]
        class_rows.append(
            {
                "physical_class_sha256": physical_class,
                "node_count": len(nodes),
                "component_count": component_count,
                "component_sizes": [len(component) for component in components],
                "same_class_directed": counts_for_class["SAME_PHYSICAL_CLASS"],
                "different_long_class_directed": counts_for_class[
                    "DIFFERENT_LONG_PERIOD_CLASS"
                ],
                "represented_outside_long_set": counts_for_class[
                    "REPRESENTED_OUTSIDE_LONG_PERIOD_SET"
                ],
                "zero_ic_unsampled": counts_for_class["ZERO_IC_UNSAMPLED"],
                "rules": metadata["rules"],
                "defect_periods": metadata["defect_periods"],
            }
        )
    class_rows.sort(key=lambda row: (-row["node_count"], row["physical_class_sha256"]))

    class_graph_rows = [
        {
            "left_physical_class_sha256": pair[0],
            "right_physical_class_sha256": pair[1],
            "directed_edge_count": directed_count,
            "undirected_edge_count": directed_count // 2,
        }
        for pair, directed_count in sorted(class_links.items())
    ]
    if any(row["directed_edge_count"] % 2 for row in class_graph_rows):
        raise RuntimeError("Cross-class edge weights are not reciprocal")
    ledger_backed = len(edges) - counts["ZERO_IC_UNSAMPLED"]
    summary = {
        "node_count": len(state_rows),
        "physical_class_count": len(class_rows),
        "directed_intervention_count": len(edges),
        "ledger_backed_intervention_count": ledger_backed,
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
    payload = {
        "phase": 94,
        "status": "LONG_PERIOD_BASIN_TOPOLOGY_MAPPED",
        "source_phase93_results_sha256": sha256_file(PHASE93_RESULTS),
        "source_phase91_results_sha256": sha256_file(PHASE91_RESULTS),
        "protocol": {
            "width": WIDTH,
            "window_positions": list(WINDOW_POSITIONS),
            "flips_per_node": 8,
            "expected_directed_interventions": EXPECTED_FLIP_COUNT,
            "classification_source": "Fase-90 Stage-A complete binary ledgers",
            "absence_implies_negative": False,
            "simulation_executed": False,
        },
        "ledger_artifacts": [
            {
                field: value
                for field, value in ledger_artifacts[key].items()
                if field != "path"
            }
            for key in sorted(ledger_artifacts)
        ],
        "summary": summary,
        "physical_classes": class_rows,
        "class_graph": class_graph_rows,
        "edges": edges,
        "methodological_limits": [
            "Topology is induced by the 1,829 frozen long-period nodes and central eight-cell intervention window.",
            "Represented outside-long-set targets have explicit ledger states but are not called negatives.",
            "Zero IC is outside the historical generator and remains unsimulated.",
            "No claim is made about flips outside positions 124..131 or universal basin topology.",
        ],
    }
    atomic_write(
        RESULTS_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
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
