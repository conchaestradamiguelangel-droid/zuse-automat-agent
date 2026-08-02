#!/usr/bin/env python3
"""Fase 85: exhaustive 8-bit input-selector intervention at rule_73/h=11."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
FASE55_SCRIPT = OUT_DIR / "analyze_anf_gradient_census.py"
FASE80_RESULTS = OUT_DIR / "rule73_len8_horizon_response_results.json"
FASE83_SCRIPT = OUT_DIR / "analyze_rule73_h11_exact_causal_equivalence.py"
FASE84_SCRIPT = OUT_DIR / "analyze_rule73_h11_causal_equivalence_census.py"
FASE84_RESULTS = OUT_DIR / "rule73_h11_causal_equivalence_census_results.json"
RESULTS_JSON = OUT_DIR / "rule73_h11_input_selector_results.json"
REPORT_MD = OUT_DIR / "rule73_h11_input_selector_report.md"

RULE = 73
T_LOCAL = 12
HORIZON = 11
COMPARABLE_BACKGROUND = "00111011"
NONCOMPARABLE_BACKGROUND = "00110111"
EXPECTED_A = 0x0310630
EXPECTED_B = 0x035B8B0
EXPECTED_DIFFERING_BITS = (7, 9, 10, 11, 12, 13, 15, 18)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def assignment_from_bits(bits: list[int]) -> int:
    return sum(int(bit) << index for index, bit in enumerate(bits))


def bits_from_assignment(value: int, width: int = 25) -> list[int]:
    return [(value >> index) & 1 for index in range(width)]


def assignment_hex(value: int) -> str:
    return f"0x{value:07x}"


def select_endpoints(fase80: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    selected = {}
    for row in fase80["cases"]:
        if row["background"] not in (COMPARABLE_BACKGROUND, NONCOMPARABLE_BACKGROUND):
            continue
        h11 = [item for item in row["measurements"] if int(item["horizon"]) == HORIZON]
        if len(h11) != 1:
            raise RuntimeError(f"Expected one h=11 measurement for {row['label']}")
        selected[row["background"]] = {
            "label": row["label"],
            "role": row["cohort"],
            "cohort": row["cohort"],
            "rule": RULE,
            "background": row["background"],
            "T_local": int(row["T_local"]),
            "word": row["word"],
            "horizon": HORIZON,
            "h11_comparable": bool(h11[0]["comparable"]),
        }
    if set(selected) != {COMPARABLE_BACKGROUND, NONCOMPARABLE_BACKGROUND}:
        raise RuntimeError("Fase 85 endpoints are missing from Fase 80")
    comparable = selected[COMPARABLE_BACKGROUND]
    noncomparable = selected[NONCOMPARABLE_BACKGROUND]
    if not comparable["h11_comparable"] or noncomparable["h11_comparable"]:
        raise RuntimeError("Endpoint labels no longer define comparable/non-comparable")
    return comparable, noncomparable


def eca_local_step(
    state: list[int],
    rule: int,
    left_boundary: int,
    right_boundary: int,
) -> list[int]:
    output = []
    for index, center in enumerate(state):
        left = state[index - 1] if index else left_boundary
        right = state[index + 1] if index + 1 < len(state) else right_boundary
        key = (left << 2) | (center << 1) | right
        output.append((rule >> key) & 1)
    return output


def simulate_assignment(
    initial: list[int],
    boundary_trace: list[dict[str, int]],
) -> list[list[int]]:
    trajectory = [list(initial)]
    for boundary in boundary_trace:
        trajectory.append(
            eca_local_step(
                trajectory[-1],
                RULE,
                int(boundary["left"]),
                int(boundary["right"]),
            )
        )
    return trajectory


def final_defect_from_tables(
    baseline,
    prepared: dict[str, Any],
    assignment: int,
) -> list[int]:
    output = []
    for index, table in enumerate(prepared["rows"]):
        actual_bit = baseline.packed_bit(table, assignment)
        output.append(actual_bit ^ prepared["local_final_background"][index])
    return output


def fit_view(fit: dict[str, Any]) -> dict[str, Any]:
    return {
        "reliable": bool(fit["reliable"]),
        "usable_count": int(fit["usable_count"]),
        "distinct_dist_count": int(fit["distinct_dist_count"]),
        "slope": fit["slope"],
        "r2": fit["r2"],
    }


def evaluate_assignment(
    fase83,
    baseline,
    fase55,
    prepared: dict[str, Any],
    output_stats: list[dict[str, Any]],
    background_trajectory: list[list[int]],
    assignment: int,
    subset_mask: int,
    differing_bits: tuple[int, ...],
    endpoint_a_final: list[int],
    endpoint_b_final: list[int],
    endpoint_a_trajectory: list[list[int]],
    endpoint_b_trajectory: list[list[int]],
) -> dict[str, Any]:
    initial = bits_from_assignment(assignment)
    actual_trajectory = simulate_assignment(initial, prepared["boundary_trace"])
    defect_trajectory = [
        [actual ^ background for actual, background in zip(actual_row, bg_row)]
        for actual_row, bg_row in zip(actual_trajectory, background_trajectory)
    ]
    final_defect = defect_trajectory[-1]
    packed_final = final_defect_from_tables(baseline, prepared, assignment)
    if packed_final != final_defect:
        raise RuntimeError(f"Local/packed mismatch for assignment {assignment_hex(assignment)}")
    active_indices = [index for index, bit in enumerate(final_defect) if bit]
    center = (
        (min(active_indices) + max(active_indices)) / 2.0
        if active_indices
        else 12.0
    )
    active_outputs = []
    for index in active_indices:
        output = dict(output_stats[index])
        output["dist"] = abs(index - center)
        output["log10_monomials"] = (
            math.log10(output["monomial_count"])
            if output["monomial_count"] > 0
            else None
        )
        active_outputs.append(output)
    summary = baseline.summarize(active_outputs)
    fit = summary["log_monomial_fit"]
    comparable = bool(fase55.comparable_to_t15(fit))
    if final_defect == endpoint_a_final:
        final_class = "A_COMPARABLE_PATTERN"
    elif final_defect == endpoint_b_final:
        final_class = "B_NONCOMPARABLE_PATTERN"
    else:
        final_class = "OTHER_PATTERN"
    if actual_trajectory == endpoint_a_trajectory:
        trajectory_class = "A_EXACT_TRAJECTORY"
    elif actual_trajectory == endpoint_b_trajectory:
        trajectory_class = "B_EXACT_TRAJECTORY"
    else:
        trajectory_class = "OTHER_TRAJECTORY"
    changed_bits = [
        differing_bits[index]
        for index in range(len(differing_bits))
        if (subset_mask >> index) & 1
    ]
    reverted_bits = [bit for bit in differing_bits if bit not in changed_bits]
    return {
        "subset_mask": subset_mask,
        "subset_mask_binary": f"{subset_mask:0{len(differing_bits)}b}",
        "assignment": assignment,
        "assignment_hex": assignment_hex(assignment),
        "changed_from_a": len(changed_bits),
        "changed_from_b": len(differing_bits) - len(changed_bits),
        "changed_global_bits": changed_bits,
        "changed_local_coordinates": [bit - 12 for bit in changed_bits],
        "reverted_global_bits": reverted_bits,
        "reverted_local_coordinates": [bit - 12 for bit in reverted_bits],
        "active_indices": active_indices,
        "active_output_count": len(active_indices),
        "final_pattern": "".join(str(bit) for bit in final_defect),
        "final_class": final_class,
        "trajectory_class": trajectory_class,
        "trajectory_sha256": fase83.sha256_json(actual_trajectory),
        "defect_trajectory_sha256": fase83.sha256_json(defect_trajectory),
        "comparable_to_t15": comparable,
        "active_fit": fit_view(fit),
    }


def minimum_rows(
    rows: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    distance_key: str,
    exclude_zero: bool = True,
) -> dict[str, Any]:
    candidates = [row for row in rows if predicate(row)]
    if exclude_zero:
        candidates = [row for row in candidates if int(row[distance_key]) > 0]
    if not candidates:
        return {"distance": None, "count": 0, "rows": []}
    distance = min(int(row[distance_key]) for row in candidates)
    selected = [row for row in candidates if int(row[distance_key]) == distance]
    return {
        "distance": distance,
        "count": len(selected),
        "rows": [
            {
                "subset_mask": row["subset_mask"],
                "subset_mask_binary": row["subset_mask_binary"],
                "assignment_hex": row["assignment_hex"],
                "changed_global_bits": row["changed_global_bits"],
                "changed_local_coordinates": row["changed_local_coordinates"],
                "reverted_global_bits": row["reverted_global_bits"],
                "reverted_local_coordinates": row["reverted_local_coordinates"],
                "active_output_count": row["active_output_count"],
                "final_class": row["final_class"],
                "comparable_to_t15": row["comparable_to_t15"],
            }
            for row in selected
        ],
    }


def inclusion_minimal_masks(
    rows: list[dict[str, Any]],
    predicate: Callable[[dict[str, Any]], bool],
    transform: Callable[[int], int] | None = None,
) -> list[int]:
    transform = transform or (lambda value: value)
    masks = sorted(
        {transform(int(row["subset_mask"])) for row in rows if predicate(row)},
        key=lambda value: (value.bit_count(), value),
    )
    minimal = []
    for mask in masks:
        if any((candidate & mask) == candidate for candidate in minimal):
            continue
        minimal.append(mask)
    return minimal


def mask_bits(mask: int, differing_bits: tuple[int, ...]) -> list[int]:
    return [
        differing_bits[index]
        for index in range(len(differing_bits))
        if (mask >> index) & 1
    ]


def single_bit_audit(
    rows_by_mask: dict[int, dict[str, Any]],
    differing_bits: tuple[int, ...],
) -> list[dict[str, Any]]:
    full_mask = (1 << len(differing_bits)) - 1
    output = []
    for index, global_bit in enumerate(differing_bits):
        from_a = rows_by_mask[1 << index]
        from_b = rows_by_mask[full_mask ^ (1 << index)]
        output.append(
            {
                "global_bit": global_bit,
                "local_coordinate": global_bit - 12,
                "a_value": (EXPECTED_A >> global_bit) & 1,
                "b_value": (EXPECTED_B >> global_bit) & 1,
                "a_flip_final_class": from_a["final_class"],
                "a_flip_active_output_count": from_a["active_output_count"],
                "a_flip_comparable": from_a["comparable_to_t15"],
                "b_revert_final_class": from_b["final_class"],
                "b_revert_active_output_count": from_b["active_output_count"],
                "b_revert_comparable": from_b["comparable_to_t15"],
            }
        )
    return output


def classify(minima: dict[str, Any]) -> tuple[str, str]:
    distances = [
        minima["a_to_noncomparable"]["distance"],
        minima["b_to_comparable"]["distance"],
    ]
    finite = [distance for distance in distances if distance is not None]
    if finite and min(finite) == 1:
        return (
            "SINGLE_BIT_ANF_INPUT_SELECTOR_FOUND",
            "At least one single-bit intervention changes T15 comparability while the causal operator and boundary forcing remain fixed.",
        )
    if finite:
        return (
            "MULTIBIT_ANF_INPUT_SELECTOR_FOUND",
            "Changing T15 comparability requires a multi-bit intervention within the eight-bit endpoint subcube.",
        )
    return (
        "ANF_INPUT_SELECTOR_NOT_RESOLVED",
        "No assignment in the complete eight-bit endpoint subcube changes T15 comparability.",
    )


def compact_minimum(minimum: dict[str, Any], from_endpoint: str) -> str:
    if minimum["distance"] is None:
        return "not found"
    bits_key = (
        "changed_global_bits" if from_endpoint == "A" else "reverted_global_bits"
    )
    bits_label = "changed bits" if from_endpoint == "A" else "reverted bits"
    masks = ", ".join(
        f"{bits_label}={row[bits_key]} (`{row['assignment_hex']}`)"
        for row in minimum["rows"]
    )
    return f"distance {minimum['distance']}: {masks}"


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    minima = data["minimal_interventions"]
    lines = [
        "# Fase 85: rule_73 h=11 Input-Selector Intervention",
        "",
        "## Question",
        "",
        "Which minimal changes between the two 25-bit inputs identified in",
        "Fase 84 select the comparable four-output trajectory or the",
        "non-comparable seven-output trajectory while the exact causal",
        "operator and boundary forcing remain fixed?",
        "",
        "## Predeclared Intervention",
        "",
        f"Endpoint A is `{data['endpoints']['A']['assignment_hex']}` and endpoint B is",
        f"`{data['endpoints']['B']['assignment_hex']}`. They differ at eight variable",
        f"indices `{data['preflight']['differing_bits']}`. Fase 85 exhaustively evaluates",
        "all 2^8 = 256 assignments in the connecting subcube. A subset bit",
        "equal to 1 selects the B allele at that variable; 0 retains A.",
        "",
        "Every assignment is evolved for 11 steps under the same rule_73",
        "boundary trace. The final state is independently read from the complete",
        "packed causal truth tables. T15 comparability reuses the unchanged",
        "Fase 55 `comparable_to_t15()` predicate on the active-output ANF fit.",
        "",
        "Intermediate assignments are controlled symbolic interventions. They",
        "are not claimed to be stationary oscillators already present in the",
        "physical background catalogue.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Assignments evaluated: `{summary['assignment_count']}`",
        f"- Packed/local mismatches: `{summary['packed_local_mismatch_count']}`",
        f"- Comparable assignments: `{summary['comparable_count']}`",
        f"- Non-comparable assignments: `{summary['noncomparable_count']}`",
        f"- Exact A final patterns: `{summary['final_class_counts'].get('A_COMPARABLE_PATTERN', 0)}`",
        f"- Exact B final patterns: `{summary['final_class_counts'].get('B_NONCOMPARABLE_PATTERN', 0)}`",
        f"- Other final patterns: `{summary['final_class_counts'].get('OTHER_PATTERN', 0)}`",
        f"- Exact A trajectories: `{summary['trajectory_class_counts'].get('A_EXACT_TRAJECTORY', 0)}`",
        f"- Exact B trajectories: `{summary['trajectory_class_counts'].get('B_EXACT_TRAJECTORY', 0)}`",
        f"- Other trajectories: `{summary['trajectory_class_counts'].get('OTHER_TRAJECTORY', 0)}`",
        "",
        "## Minimal Interventions",
        "",
        f"- A -> exact B final pattern: {compact_minimum(minima['a_to_b_final'], 'A')}",
        f"- B -> exact A final pattern: {compact_minimum(minima['b_to_a_final'], 'B')}",
        f"- A -> non-comparable: {compact_minimum(minima['a_to_noncomparable'], 'A')}",
        f"- B -> comparable: {compact_minimum(minima['b_to_comparable'], 'B')}",
        "",
        "## Single-Bit Audit",
        "",
        "| bit | local x | A->B allele | active | comparable | B->A allele | active | comparable |",
        "| ---: | ---: | --- | ---: | --- | --- | ---: | --- |",
    ]
    for row in data["single_bit_audit"]:
        lines.append(
            f"| {row['global_bit']} | {row['local_coordinate']} | "
            f"{row['a_flip_final_class']} | {row['a_flip_active_output_count']} | "
            f"{str(row['a_flip_comparable']).lower()} | "
            f"{row['b_revert_final_class']} | {row['b_revert_active_output_count']} | "
            f"{str(row['b_revert_comparable']).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Inclusion-Minimal Selector Sets",
            "",
            "These sets are exact within the eight-bit subcube; no statistical",
            "fit or feature selection is used.",
            "",
            "### From A: inclusion-minimal changes producing non-comparability",
            "",
            "| changed bits | local coordinates |",
            "| --- | --- |",
        ]
    )
    for selector in data["inclusion_minimal"]["a_to_noncomparable"]:
        lines.append(
            f"| `{selector['bits']}` | `{selector['local_coordinates']}` |"
        )
    lines.extend(
        [
            "",
            "### From B: inclusion-minimal reversions restoring comparability",
            "",
            "| reverted bits | local coordinates |",
            "| --- | --- |",
        ]
    )
    for selector in data["inclusion_minimal"]["b_to_comparable"]:
        lines.append(
            f"| `{selector['bits']}` | `{selector['local_coordinates']}` |"
        )
    lines.extend(
        [
            "",
            "## Endpoint Verification",
            "",
            "| endpoint | input | final class | active outputs | comparable | slope | R2 |",
            "| --- | --- | --- | ---: | --- | ---: | ---: |",
        ]
    )
    for endpoint in (data["endpoints"]["A"], data["endpoints"]["B"]):
        fit = endpoint["active_fit"]
        lines.append(
            f"| {endpoint['endpoint']} | `{endpoint['assignment_hex']}` | "
            f"{endpoint['final_class']} | {endpoint['active_output_count']} | "
            f"{str(endpoint['comparable_to_t15']).lower()} | "
            f"{fit['slope']:.6f} | {fit['r2']:.6f} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if data["status"] == "SINGLE_BIT_ANF_INPUT_SELECTOR_FOUND":
        lines.extend(
            [
                "The h=11 ANF crossing is sensitive to at least one atomic input",
                "edit even though rule, horizon, causal operator, final background,",
                "and boundary forcing are unchanged. This isolates the selection",
                "mechanism at input-assignment level rather than rule or operator",
                "level. Exact endpoint trajectories may still require more than",
                "one bit; comparability and endpoint identity are reported",
                "separately. In particular, three assignments reach the exact B",
                "final pattern, but only endpoint B reproduces the exact B",
                "trajectory. Final-state convergence therefore does not imply",
                "full trajectory identity.",
            ]
        )
    else:
        lines.append(data["verdict_reason"])
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- The 256 assignments exhaust only the eight-bit subcube connecting",
            "  two observed inputs; the remaining 17 variables are held fixed.",
            "- Controlled intermediate inputs are valid symbolic interventions",
            "  but are not necessarily stationary oscillators in the source sweep.",
            "- Comparability is the unchanged empirical Fase 55 predicate, not a",
            "  universal physical phase label.",
            "- The result is local to rule_73, T=12, h=11, window 25, and this",
            "  boundary-forcing class.",
            "- No paper, DOI, tag, release, or threshold changed.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase80 = load_json(FASE80_RESULTS)
    fase84_results = load_json(FASE84_RESULTS)
    endpoint_a_case, endpoint_b_case = select_endpoints(fase80)
    endpoint_rows = {
        row["background"]: row
        for row in fase84_results["cases"]
        if row["background"] in (COMPARABLE_BACKGROUND, NONCOMPARABLE_BACKGROUND)
    }
    if set(endpoint_rows) != {COMPARABLE_BACKGROUND, NONCOMPARABLE_BACKGROUND}:
        raise RuntimeError("Fase 84 endpoint rows missing")
    if endpoint_rows[COMPARABLE_BACKGROUND]["concrete_assignment"] != EXPECTED_A:
        raise RuntimeError("Comparable endpoint assignment changed")
    if endpoint_rows[NONCOMPARABLE_BACKGROUND]["concrete_assignment"] != EXPECTED_B:
        raise RuntimeError("Non-comparable endpoint assignment changed")
    xor_value = EXPECTED_A ^ EXPECTED_B
    differing_bits = tuple(
        index for index in range(25) if (xor_value >> index) & 1
    )
    if differing_bits != EXPECTED_DIFFERING_BITS:
        raise RuntimeError(f"Expected differing bits {EXPECTED_DIFFERING_BITS}, got {differing_bits}")
    preflight = {
        "rule": RULE,
        "T_local": T_LOCAL,
        "horizon": HORIZON,
        "window_cells": 25,
        "endpoint_a": assignment_hex(EXPECTED_A),
        "endpoint_b": assignment_hex(EXPECTED_B),
        "xor": assignment_hex(xor_value),
        "hamming_distance": len(differing_bits),
        "differing_bits": list(differing_bits),
        "differing_local_coordinates": [bit - 12 for bit in differing_bits],
        "assignment_count": 1 << len(differing_bits),
        "operator_policy": "fixed exact Fase 84 causal operator",
        "boundary_policy": "fixed Fase 83 left-reference boundary trace",
        "comparability_policy": "unchanged Fase 55 comparable_to_t15",
        "threshold_fitting": False,
    }
    if preflight_only:
        return {"phase": 85, "preflight": preflight}

    fase83 = load_module("fase85_exact_causal_equivalence", FASE83_SCRIPT)
    fase84 = load_module("fase85_causal_equivalence_census", FASE84_SCRIPT)
    fase55 = load_module("fase85_anf_gradient_census", FASE55_SCRIPT)
    baseline = fase83.load_module(
        "fase85_periodic_bg_anf_baseline",
        fase83.BASELINE_SCRIPT,
    )
    base = baseline.load_base_module()
    prepared_a = fase83.prepare_case(baseline, base, endpoint_a_case)
    prepared_b = fase83.prepare_case(baseline, base, endpoint_b_case)
    direct = fase84.direct_map_comparison(prepared_a, prepared_b)
    trajectory_relation = fase84.trajectory_comparison(prepared_a, prepared_b)
    if not direct["causal_map_equal"] or not trajectory_relation["boundary_trace_equal"]:
        raise RuntimeError("Fase 85 endpoints no longer share operator and boundary")
    assignment_a = assignment_from_bits(prepared_a["local_sample_actual"])
    assignment_b = assignment_from_bits(prepared_b["local_sample_actual"])
    if assignment_a != EXPECTED_A or assignment_b != EXPECTED_B:
        raise RuntimeError("Prepared endpoint assignments differ from Fase 84")

    popcount16 = np.array(
        [int(value).bit_count() for value in range(1 << 16)],
        dtype=np.uint8,
    )
    output_stats = []
    for output_index, table in enumerate(prepared_a["rows"]):
        output = baseline.analyze_output_anf(
            table,
            prepared_a["local_final_background"][output_index],
            prepared_a["ones"],
            popcount16,
        )
        output["output_index"] = output_index
        output_stats.append(output)
    background_trajectory = [
        [
            baseline.bit_from_frame(
                prepared_a["bg_frames"][baseline.SAMPLE_START + step],
                position,
            )
            for position in prepared_a["positions"]
        ]
        for step in range(HORIZON + 1)
    ]
    endpoint_a_trajectory = simulate_assignment(
        prepared_a["local_sample_actual"],
        prepared_a["boundary_trace"],
    )
    endpoint_b_trajectory = simulate_assignment(
        prepared_b["local_sample_actual"],
        prepared_a["boundary_trace"],
    )
    endpoint_a_final = final_defect_from_tables(baseline, prepared_a, EXPECTED_A)
    endpoint_b_final = final_defect_from_tables(baseline, prepared_a, EXPECTED_B)

    rows = []
    full_mask = (1 << len(differing_bits)) - 1
    for subset_mask in range(full_mask + 1):
        toggle = 0
        for index, global_bit in enumerate(differing_bits):
            if (subset_mask >> index) & 1:
                toggle |= 1 << global_bit
        assignment = EXPECTED_A ^ toggle
        rows.append(
            evaluate_assignment(
                fase83,
                baseline,
                fase55,
                prepared_a,
                output_stats,
                background_trajectory,
                assignment,
                subset_mask,
                differing_bits,
                endpoint_a_final,
                endpoint_b_final,
                endpoint_a_trajectory,
                endpoint_b_trajectory,
            )
        )
    rows_by_mask = {int(row["subset_mask"]): row for row in rows}
    endpoint_a = dict(rows_by_mask[0])
    endpoint_b = dict(rows_by_mask[full_mask])
    endpoint_a["endpoint"] = "A"
    endpoint_b["endpoint"] = "B"
    if not endpoint_a["comparable_to_t15"] or endpoint_b["comparable_to_t15"]:
        raise RuntimeError("Controlled endpoint comparability does not reproduce Fase 84")

    minima = {
        "a_to_b_final": minimum_rows(
            rows,
            lambda row: row["final_class"] == "B_NONCOMPARABLE_PATTERN",
            "changed_from_a",
        ),
        "b_to_a_final": minimum_rows(
            rows,
            lambda row: row["final_class"] == "A_COMPARABLE_PATTERN",
            "changed_from_b",
        ),
        "a_to_noncomparable": minimum_rows(
            rows,
            lambda row: not row["comparable_to_t15"],
            "changed_from_a",
        ),
        "b_to_comparable": minimum_rows(
            rows,
            lambda row: row["comparable_to_t15"],
            "changed_from_b",
        ),
    }
    inclusion_minimal = {
        "a_to_noncomparable": [
            {
                "mask": mask,
                "bits": mask_bits(mask, differing_bits),
                "local_coordinates": [bit - 12 for bit in mask_bits(mask, differing_bits)],
            }
            for mask in inclusion_minimal_masks(
                rows,
                lambda row: not row["comparable_to_t15"],
            )
        ],
        "b_to_comparable": [
            {
                "reversion_mask": mask,
                "bits": mask_bits(mask, differing_bits),
                "local_coordinates": [bit - 12 for bit in mask_bits(mask, differing_bits)],
            }
            for mask in inclusion_minimal_masks(
                rows,
                lambda row: row["comparable_to_t15"],
                transform=lambda value: full_mask ^ value,
            )
        ],
    }
    status, reason = classify(minima)
    final_counts = Counter(row["final_class"] for row in rows)
    trajectory_counts = Counter(row["trajectory_class"] for row in rows)
    active_counts = Counter(row["active_output_count"] for row in rows)
    summary = {
        "assignment_count": len(rows),
        "packed_local_mismatch_count": 0,
        "comparable_count": sum(row["comparable_to_t15"] for row in rows),
        "noncomparable_count": sum(not row["comparable_to_t15"] for row in rows),
        "final_class_counts": dict(sorted(final_counts.items())),
        "trajectory_class_counts": dict(sorted(trajectory_counts.items())),
        "active_output_count_distribution": dict(sorted(active_counts.items())),
        "distinct_final_pattern_count": len({row["final_pattern"] for row in rows}),
        "distinct_trajectory_count": len({row["trajectory_sha256"] for row in rows}),
        "operator_equal": direct["causal_map_equal"],
        "boundary_equal": trajectory_relation["boundary_trace_equal"],
        "reference_anf_geometry_reproduced": (
            fase83.sha256_json(
                tuple(
                    (
                        2 * int(row["output_index"])
                        - (
                            min(prepared_a["active_indices"])
                            + max(prepared_a["active_indices"])
                        ),
                        int(row["degree"]),
                        int(row["monomial_count"]),
                        tuple(
                            sorted(
                                (int(degree), int(count))
                                for degree, count in row["degree_histogram"].items()
                            )
                        ),
                    )
                    for row in output_stats
                    if row["output_index"] in prepared_a["active_indices"]
                )
            )
            == load_json(fase83.FASE82_RESULTS)["reference"]["oriented_sha256"]
        ),
    }
    data = {
        "phase": 85,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "endpoints": {"A": endpoint_a, "B": endpoint_b},
        "minimal_interventions": minima,
        "inclusion_minimal": inclusion_minimal,
        "single_bit_audit": single_bit_audit(rows_by_mask, differing_bits),
        "assignments": rows,
    }
    RESULTS_JSON.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    data = run(preflight_only=args.preflight_only)
    if args.preflight_only:
        print(json.dumps(data, indent=2, sort_keys=True))
        return
    print(f"status={data['status']}")
    print(json.dumps(data["summary"], indent=2, sort_keys=True))
    print(json.dumps(data["minimal_interventions"], indent=2, sort_keys=True))
    print(f"report={REPORT_MD}")


if __name__ == "__main__":
    main()
