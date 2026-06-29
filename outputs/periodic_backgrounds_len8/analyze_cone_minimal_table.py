#!/usr/bin/env python3
"""Fase 41: minimal table/circuit audit for the T=15 causal cone.

Fase 40 showed that a strict 25-cell cone simulated for 12 steps recovers the
post-burn-in defect state for all 20 minimal T=15 representatives. Fase 41
turns that cone into a formal object: the induced local table actually used
inside the cone and the causal dependency subgraph needed to produce the final
localized defect.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
BASE_SCRIPT = OUT_DIR.parent / "periodic_backgrounds" / "sweep_periodic_background_oscillators.py"
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
EMBEDDING_RESULTS = OUT_DIR / "defect_embedding_descriptor_results.json"
RESULTS_JSON = OUT_DIR / "cone_minimal_table_results.json"
REPORT_MD = OUT_DIR / "cone_minimal_table_report.md"

T_WINDOW = 12
WINDOW_CELLS = 2 * T_WINDOW + 1
SAMPLE_START = 81
BACKGROUND_PERIOD = 3


def load_base_module():
    spec = importlib.util.spec_from_file_location("periodic_background_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base detector from {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def perturbation_orbit(base, rule: int, background_frames: list[tuple[int, ...]], ic: str) -> list[tuple[int, ...]]:
    diff = base.initial_diff(int(ic, 2), len(ic), background_frames[0])
    frames = [diff]
    for time_index in range(len(background_frames) - 1):
        diff = base.eca_step_diff(diff, background_frames[time_index], background_frames[time_index + 1], rule)
        frames.append(diff)
    return frames


def canonical_defect(width: int, diff: tuple[int, ...]) -> dict | None:
    if not diff:
        return None
    positions = sorted(diff)
    gaps = []
    for index, position in enumerate(positions):
        next_position = positions[(index + 1) % len(positions)]
        if index == len(positions) - 1:
            next_position += width
        gaps.append((next_position - position, index))
    _largest_gap, cut_index = max(gaps)
    anchor = positions[(cut_index + 1) % len(positions)]
    offsets = tuple(sorted((position - anchor) % width for position in positions))
    active_width = max(offsets) + 1
    value = sum(1 << offset for offset in offsets)
    hex_digits = max(1, (active_width + 3) // 4)
    return {
        "anchor": anchor,
        "offsets": offsets,
        "width": active_width,
        "hex": f"{active_width}:{value:0{hex_digits}x}",
    }


def bit_from_state(active: set[int], pos: int, width: int) -> int:
    return 1 if (pos % width) in active else 0


def ic_start(width: int, ic: str) -> int:
    return width // 2 - len(ic) // 2


def initial_actual_bit(base, bg_set: set[int], global_pos: int, ic: str) -> int:
    start = ic_start(base.WIDTH, ic)
    if start <= global_pos <= start + len(ic) - 1:
        idx = global_pos - start
        return int(ic[idx])
    return bit_from_state(bg_set, global_pos, base.WIDTH)


def rule_output(rule: int, left: int, center: int, right: int) -> int:
    idx = (left << 2) | (center << 1) | right
    return (rule >> idx) & 1


def triple_to_index(bits: tuple[int, int, int]) -> int:
    return (bits[0] << 2) | (bits[1] << 1) | bits[2]


def bits_to_str(bits: tuple[int, ...]) -> str:
    return "".join(str(bit) for bit in bits)


def load_family_lookup() -> dict[tuple[int, str], str]:
    embedding = json.loads(EMBEDDING_RESULTS.read_text(encoding="utf-8"))
    return {
        (int(row["rule"]), row["background"]): row["family_id"]
        for row in embedding["rows"]
    }


def simulate_center_cone(base, rule: int, background: str, ic: str) -> dict:
    """Return actual/bg/diff traces and induced table usage for the t=12 center cone."""

    width = base.WIDTH
    bg_frames = background_orbit(base, rule, background, T_WINDOW)
    start = ic_start(width, ic)
    center = start + (len(ic) - 1) // 2
    left = center - T_WINDOW
    right = center + T_WINDOW
    global_positions = list(range(left, right + 1))
    bg0 = set(bg_frames[0])
    actual_rows: list[list[int]] = [
        [initial_actual_bit(base, bg0, pos, ic) for pos in global_positions]
    ]
    induced_keys_by_step: list[set[str]] = []
    ordinary_entries_by_step: list[set[int]] = []
    update_records = []

    for time_index in range(T_WINDOW):
        bg_now = set(bg_frames[time_index])
        bg_next = set(bg_frames[time_index + 1])
        actual = actual_rows[-1]
        next_actual = []
        step_induced: set[str] = set()
        step_entries: set[int] = set()
        for local_index, global_pos in enumerate(global_positions):
            triples_actual = []
            triples_bg = []
            triples_diff = []
            for delta in (-1, 0, 1):
                neighbor_local = local_index + delta
                neighbor_global = global_pos + delta
                bg_bit = bit_from_state(bg_now, neighbor_global, width)
                if 0 <= neighbor_local < len(global_positions):
                    actual_bit = actual[neighbor_local]
                else:
                    actual_bit = bg_bit
                triples_actual.append(actual_bit)
                triples_bg.append(bg_bit)
                triples_diff.append(actual_bit ^ bg_bit)
            actual_triple = tuple(triples_actual)
            bg_triple = tuple(triples_bg)
            diff_triple = tuple(triples_diff)
            out_actual = rule_output(rule, *actual_triple)
            out_diff = out_actual ^ bit_from_state(bg_next, global_pos, width)
            key = f"b{bits_to_str(bg_triple)}_d{bits_to_str(diff_triple)}->{out_diff}"
            step_induced.add(key)
            step_entries.add(triple_to_index(actual_triple))
            update_records.append(
                {
                    "t": time_index,
                    "local_pos": local_index,
                    "global_pos": global_pos % width,
                    "background": bits_to_str(bg_triple),
                    "defect": bits_to_str(diff_triple),
                    "actual": bits_to_str(actual_triple),
                    "ordinary_entry": triple_to_index(actual_triple),
                    "output_defect": out_diff,
                    "key": key,
                }
            )
            next_actual.append(out_actual)
        actual_rows.append(next_actual)
        induced_keys_by_step.append(step_induced)
        ordinary_entries_by_step.append(step_entries)

    bg_sets = [set(frame) for frame in bg_frames]
    diff_rows = []
    for t, actual in enumerate(actual_rows):
        bg_set = bg_sets[t]
        diff_rows.append(
            [
                actual_bit ^ bit_from_state(bg_set, global_pos, width)
                for actual_bit, global_pos in zip(actual, global_positions)
            ]
        )
    final_diff_positions = [
        global_pos % width
        for global_pos, bit in zip(global_positions, diff_rows[-1])
        if bit
    ]
    final_canonical = canonical_defect(width, tuple(sorted(final_diff_positions)))

    return {
        "left": left,
        "right": right,
        "center": center,
        "global_positions": [pos % width for pos in global_positions],
        "actual_rows": actual_rows,
        "diff_rows": diff_rows,
        "final_canonical": final_canonical,
        "induced_keys_by_step": [sorted(keys) for keys in induced_keys_by_step],
        "ordinary_entries_by_step": [sorted(entries) for entries in ordinary_entries_by_step],
        "update_records": update_records,
    }


def backward_dependency(target_positions: set[int], include_all_outputs: bool) -> dict:
    """Return the causal dependency closure inside the 25-cell cone.

    Positions are local indices 0..24. Boundary dependencies outside this range
    are background constants and are counted separately, not as variables.
    """

    needed_by_time: dict[int, set[int]] = defaultdict(set)
    needed_by_time[T_WINDOW] = set(range(WINDOW_CELLS)) if include_all_outputs else set(target_positions)
    boundary_constants = 0
    update_nodes = 0
    for t in range(T_WINDOW, 0, -1):
        for pos in needed_by_time[t]:
            update_nodes += 1
            for parent in (pos - 1, pos, pos + 1):
                if 0 <= parent < WINDOW_CELLS:
                    needed_by_time[t - 1].add(parent)
                else:
                    boundary_constants += 1
    total_nodes = sum(len(v) for v in needed_by_time.values())
    return {
        "initial_variables": len(needed_by_time[0]),
        "update_nodes": update_nodes,
        "total_internal_nodes": total_nodes,
        "boundary_constant_reads": boundary_constants,
        "needed_by_time": {str(t): sorted(v) for t, v in sorted(needed_by_time.items())},
    }


def analyze() -> dict:
    base = load_base_module()
    family_lookup = load_family_lookup()
    rows = []
    for record in load_jsonl(LOCKING_RESULTS):
        rule = int(record["rule"])
        background = record["background"]
        ic = record["ic"]
        stable_states = list(record["defect_states"])
        state_to_phase = {state: index for index, state in enumerate(stable_states)}
        trace = simulate_center_cone(base, rule, background, ic)
        final_state = trace["final_canonical"]["hex"] if trace["final_canonical"] else None
        final_phase = state_to_phase.get(final_state)
        steps_to_sample = (SAMPLE_START - T_WINDOW) // BACKGROUND_PERIOD
        projected_phase = None if final_phase is None else (final_phase + steps_to_sample) % len(stable_states)
        projected_state = None if projected_phase is None else stable_states[projected_phase]

        active_final_local = {
            index
            for index, bit in enumerate(trace["diff_rows"][-1])
            if bit
        }
        all_induced_keys = sorted({key for step in trace["induced_keys_by_step"] for key in step})
        all_entries = sorted({entry for step in trace["ordinary_entries_by_step"] for entry in step})
        active_dep = backward_dependency(active_final_local, include_all_outputs=False)
        full_dep = backward_dependency(active_final_local, include_all_outputs=True)

        rows.append(
            {
                "rule": rule,
                "background": background,
                "family_id": family_lookup[(rule, background)],
                "ic": ic,
                "final_state_t12": final_state,
                "final_phase_t12": final_phase,
                "projected_state_t81": projected_state,
                "projected_matches_sample": projected_state == stable_states[0],
                "active_final_local_positions": sorted(active_final_local),
                "active_final_count": len(active_final_local),
                "induced_key_count": len(all_induced_keys),
                "induced_keys": all_induced_keys,
                "ordinary_entry_count": len(all_entries),
                "ordinary_entries": all_entries,
                "induced_keys_by_step_count": [len(step) for step in trace["induced_keys_by_step"]],
                "ordinary_entries_by_step_count": [len(step) for step in trace["ordinary_entries_by_step"]],
                "active_dependency": active_dep,
                "full_dependency": full_dep,
                "active_dependency_compression_vs_cone_nodes": (WINDOW_CELLS * (T_WINDOW + 1)) / active_dep["total_internal_nodes"],
                "active_dependency_compression_vs_full_sim": (256 * 81) / active_dep["total_internal_nodes"],
                "full_dependency_compression_vs_full_sim": (256 * 81) / full_dep["total_internal_nodes"],
                "induced_table_signature": "|".join(all_induced_keys),
                "ordinary_entry_signature": ",".join(str(entry) for entry in all_entries),
            }
        )
    rows = sorted(rows, key=lambda item: (item["family_id"], item["rule"], item["background"]))

    by_family: dict[str, list[dict]] = defaultdict(list)
    by_rule: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_family[row["family_id"]].append(row)
        by_rule[str(row["rule"])].append(row)

    family_summary = []
    for family_id, items in sorted(by_family.items()):
        family_summary.append(
            {
                "family_id": family_id,
                "member_count": len(items),
                "table_signature_count": len({item["induced_table_signature"] for item in items}),
                "ordinary_signature_count": len({item["ordinary_entry_signature"] for item in items}),
                "active_dependency_shapes": sorted({tuple(item["active_dependency"]["needed_by_time"].get("0", [])) for item in items}),
                "members": [
                    {
                        "rule": item["rule"],
                        "background": item["background"],
                        "ic": item["ic"],
                        "induced_key_count": item["induced_key_count"],
                        "active_initial_variables": item["active_dependency"]["initial_variables"],
                    }
                    for item in items
                ],
            }
        )

    key_counts = [row["induced_key_count"] for row in rows]
    active_initial_counts = [row["active_dependency"]["initial_variables"] for row in rows]
    active_node_counts = [row["active_dependency"]["total_internal_nodes"] for row in rows]
    all_use_all_entries = all(row["ordinary_entry_count"] == 8 for row in rows)
    all_need_all_inputs = all(row["active_dependency"]["initial_variables"] == WINDOW_CELLS for row in rows)
    dense_induced_tables = min(key_counts) >= 49
    if max(active_node_counts) < WINDOW_CELLS * (T_WINDOW + 1) and all_need_all_inputs and all_use_all_entries:
        status = "STRUCTURAL_CONE_REDUCTION_ONLY"
    elif max(active_node_counts) < WINDOW_CELLS * (T_WINDOW + 1):
        status = "LOCAL_CIRCUIT_REDUCTION_FOUND"
    else:
        status = "NO_INTERNAL_CONE_REDUCTION"

    return {
        "status": status,
        "record_count": len(rows),
        "t_window": T_WINDOW,
        "window_cells": WINDOW_CELLS,
        "full_sim_cell_steps": 256 * 81,
        "cone_nodes": WINDOW_CELLS * (T_WINDOW + 1),
        "ordinary_rule_entries_all_used_in_all_representatives": all_use_all_entries,
        "active_outputs_need_all_25_inputs": all_need_all_inputs,
        "induced_tables_dense": dense_induced_tables,
        "induced_key_count_range": [min(key_counts), max(key_counts)],
        "active_initial_variable_range": [min(active_initial_counts), max(active_initial_counts)],
        "active_internal_node_range": [min(active_node_counts), max(active_node_counts)],
        "family_summary": family_summary,
        "rows": rows,
    }


def write_report(data: dict) -> None:
    lines = [
        "# Fase 41: Minimal Table/Circuit Audit for the T=15 Cone",
        "",
        "## Question",
        "",
        "Fase 40 showed that a strict 25-cell cone simulated for 12 steps",
        "recovers `defect_state0` in 20/20 minimal T=15 representatives. Fase 41",
        "asks whether that cone has a smaller formal representation: fewer induced",
        "local table entries, fewer ordinary ECA rule entries, or a pruned causal",
        "dependency graph for the final localized defect.",
        "",
        "## Global summary",
        "",
        f"- Representatives: {data['record_count']}.",
        f"- Cone size: {data['window_cells']} cells x {data['t_window']} steps.",
        f"- Cone space-time nodes including t=0: {data['cone_nodes']}.",
        f"- Full simulation baseline: {data['full_sim_cell_steps']} cell-steps.",
        f"- Induced key count range: {data['induced_key_count_range'][0]}..{data['induced_key_count_range'][1]} of 64 possible `(b,d)->d_next` keys.",
        f"- Active-output initial variable range: {data['active_initial_variable_range'][0]}..{data['active_initial_variable_range'][1]} of 25 cone inputs.",
        f"- Active-output internal node range: {data['active_internal_node_range'][0]}..{data['active_internal_node_range'][1]} of {data['cone_nodes']} cone nodes.",
        f"- All ordinary ECA rule entries used in every representative: `{data['ordinary_rule_entries_all_used_in_all_representatives']}`.",
        f"- Active outputs need all 25 initial cone inputs: `{data['active_outputs_need_all_25_inputs']}`.",
        f"- Induced tables are dense (minimum 49/64 keys): `{data['induced_tables_dense']}`.",
        "",
        "The full 25-bit final vector has no causal pruning under this model: it",
        "requires the full 25-cell-by-13-layer cone. The reductions below refer to",
        "the active localized defect support, not to proving that every final zero",
        "bit is zero.",
        "",
        "## Representative table",
        "",
        "| family | rule | background | IC | induced keys | ordinary entries | active final bits | active input vars | active nodes | compression vs full |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in data["rows"]:
        lines.append(
            f"| `{row['family_id']}` | {row['rule']} | `{row['background']}` | `{row['ic']}` | "
            f"{row['induced_key_count']} | {row['ordinary_entry_count']} | {row['active_final_count']} | "
            f"{row['active_dependency']['initial_variables']} | {row['active_dependency']['total_internal_nodes']} | "
            f"{row['active_dependency_compression_vs_full_sim']:.1f}x |"
        )

    lines.extend(
        [
            "",
            "## Family table signatures",
            "",
            "| family | members | induced table signatures | ordinary signatures |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for item in data["family_summary"]:
        lines.append(
            f"| `{item['family_id']}` | {item['member_count']} | {item['table_signature_count']} | {item['ordinary_signature_count']} |"
        )

    lines.extend(["", "## Verdict", "", f"**Status:** `{data['status']}`.", ""])
    if data["status"] == "STRUCTURAL_CONE_REDUCTION_ONLY":
        lines.extend(
            [
                "Fase 41 finds a structural circuit reduction, but not a sparse",
                "truth-table or input-variable reduction. All eight ordinary ECA",
                "rule entries are used in every representative, the induced",
                "`(b,d)->d_next` tables are dense (49..62 of 64 keys), and the",
                "active localized output still depends on all 25 initial cone",
                "inputs. The only reduction is internal: computing the active final",
                "defect support uses 234..310 internal cone nodes instead of all",
                "325 nodes. Thus Fase 40's 25-cell cone is close to minimal at the",
                "input level; the next symbolic target is not a smaller support, but",
                "a Boolean simplification of the dense 25-input, 12-step circuit.",
            ]
        )
    elif data["status"] == "LOCAL_CIRCUIT_REDUCTION_FOUND":
        lines.extend(
            [
                "The 25-cell cone is reducible as a causal circuit for the active",
                "localized output: computing only the final active defect support",
                "requires fewer internal nodes than the full 25-cell-by-13-layer cone.",
                "This is not yet a closed-form Boolean minimization. The ordinary ECA",
                "truth table remains fully active in every representative, so the",
                "reduction is structural/circuit-level rather than a sparse rule-table",
                "shortcut.",
            ]
        )
    else:
        lines.extend(
            [
                "No smaller causal subgraph was found inside the cone. The Fase 40",
                "25-cell computation would then be minimal under this dependency model.",
            ]
        )
    lines.append("")
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_report(analyze())


if __name__ == "__main__":
    main()
