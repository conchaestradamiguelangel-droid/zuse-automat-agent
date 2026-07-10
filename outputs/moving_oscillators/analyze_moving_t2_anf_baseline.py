#!/usr/bin/env python3
"""Fase 51: ANF baseline for moving T=2 gliders."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
CATALOG_JSONL = OUT_DIR / "moving_oscillator_results.jsonl"
RESULTS_JSON = OUT_DIR / "moving_t2_anf_baseline_results.json"
REPORT_MD = OUT_DIR / "moving_t2_anf_baseline_report.md"

RIGHT_DRIFT_RULES = (20, 52, 148, 180)
PRIMARY_SHAPES = [[0], [0, 1]]
CONTROL_SHAPES = [[0, 1], [0]]
PRIMARY_T_WINDOW = 12
CONTROL_T_WINDOW = 2
T_WINDOWS = (PRIMARY_T_WINDOW, CONTROL_T_WINDOW)


def window_cells_for(t_window: int) -> int:
    return 2 * t_window + 1


def build_variable_tables(window_cells: int) -> list[np.ndarray]:
    assignment_count = 1 << window_cells
    word_count = (assignment_count + 63) // 64
    padded_count = word_count * 64
    assignments = np.arange(assignment_count, dtype=np.uint32)
    variables = []
    for idx in range(window_cells):
        bits = np.zeros(padded_count, dtype=np.uint8)
        bits[:assignment_count] = ((assignments >> idx) & 1).astype(np.uint8)
        variables.append(np.packbits(bits, bitorder="little").view(np.uint64).copy())
    return variables


def eca_packed(rule: int, left: np.ndarray, center: np.ndarray, right: np.ndarray, ones: np.ndarray) -> np.ndarray:
    out = np.zeros_like(left)
    for idx in range(8):
        if not ((rule >> idx) & 1):
            continue
        term = ones.copy()
        term &= left if (idx & 4) else ~left
        term &= center if (idx & 2) else ~center
        term &= right if (idx & 1) else ~right
        out ^= term
    return out


def packed_bit(table: np.ndarray, assignment: int) -> int:
    word = assignment >> 6
    offset = np.uint64(assignment & 63)
    return int((table[word] >> offset) & np.uint64(1))


def mobius_inplace(bits: np.ndarray, window_cells: int) -> None:
    for idx in range(window_cells):
        step = 1 << idx
        block = step << 1
        view = bits.reshape(-1, block)
        view[:, step:block] ^= view[:, :step]


def degree_and_count(coefficients: np.ndarray) -> tuple[int, int, dict[str, int]]:
    total = 0
    degree = -1
    hist: dict[str, int] = {}
    nonzero = np.nonzero(coefficients)[0].astype(np.uint32)
    if nonzero.size == 0:
        return degree, total, hist
    degrees = np.array([int(value).bit_count() for value in nonzero], dtype=np.uint8)
    degree = int(degrees.max())
    total = int(nonzero.size)
    unique, counts = np.unique(degrees, return_counts=True)
    for deg, count in zip(unique, counts):
        hist[str(int(deg))] = int(count)
    return degree, total, hist


def analyze_output(table: np.ndarray, window_cells: int) -> dict[str, Any]:
    bits = np.unpackbits(table.view(np.uint8), bitorder="little")[: 1 << window_cells]
    mobius_inplace(bits, window_cells)
    degree, monomial_count, histogram = degree_and_count(bits)
    return {
        "degree": degree,
        "monomial_count": monomial_count,
        "degree_histogram": histogram,
        "constant_term": int(bits[0]),
        "nonconstant": degree >= 0,
    }


def load_catalog() -> list[dict[str, Any]]:
    rows = []
    with CATALOG_JSONL.open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def select_representatives(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for rule in RIGHT_DRIFT_RULES:
        rule_rows = [
            row
            for row in rows
            if row["rule"] == rule
            and row["period_T"] == 2
            and row["drift_direction"] == "right"
            and row["drift_per_period"] == 2
            and not row.get("edge_touch", False)
        ]
        for variant, shapes in (("primary_min_ic", PRIMARY_SHAPES), ("two_cell_phase_control", CONTROL_SHAPES)):
            candidates = [row for row in rule_rows if row["period_shapes"] == shapes]
            if not candidates:
                continue
            chosen = sorted(candidates, key=lambda row: (len(row["ic_word"]), row["ic_word"]))[0]
            selected.append({**chosen, "variant": variant})
    return selected


def placement(record: dict[str, Any], t_window: int, window_cells: int) -> dict[str, Any]:
    periods = t_window // record["period_T"]
    expected_drift = record["drift_per_period"] * periods
    final_reference = max(window_cells // 2, expected_drift + len(record["ic_word"]) // 2)
    initial_reference = final_reference - expected_drift
    initial_start = initial_reference - len(record["ic_word"]) // 2
    if initial_start < 0 or initial_start + len(record["ic_word"]) > window_cells:
        raise ValueError(
            f"Cannot place IC {record['ic_word']} for rule {record['rule']} "
            f"in {window_cells} cells at T={t_window}"
        )
    return {
        "periods": periods,
        "expected_drift": expected_drift,
        "final_reference": final_reference,
        "initial_reference": initial_reference,
        "initial_start": initial_start,
    }


def concrete_assignment(window_cells: int, ic_word: str, initial_start: int) -> int:
    value = 0
    for idx, bit in enumerate(ic_word):
        if bit == "1":
            value |= 1 << (initial_start + idx)
    return value


def simulate_concrete(rule: int, window_cells: int, ic_word: str, initial_start: int, t_window: int) -> list[list[int]]:
    state = [0] * window_cells
    for idx, bit in enumerate(ic_word):
        state[initial_start + idx] = int(bit)
    frames = [state]
    for _ in range(t_window):
        prev = frames[-1]
        nxt = []
        for idx, bit in enumerate(prev):
            left = prev[idx - 1] if idx > 0 else 0
            right = prev[idx + 1] if idx < window_cells - 1 else 0
            key = (left << 2) | (bit << 1) | right
            nxt.append((rule >> key) & 1)
        frames.append(nxt)
    return frames


def simulate_packed_cone(rule: int, window_cells: int, t_window: int) -> list[np.ndarray]:
    word_count = ((1 << window_cells) + 63) // 64
    zeros = np.zeros(word_count, dtype=np.uint64)
    ones = np.full(word_count, np.uint64((1 << 64) - 1), dtype=np.uint64)
    rows = build_variable_tables(window_cells)
    for _ in range(t_window):
        next_rows = []
        for idx in range(window_cells):
            left = rows[idx - 1] if idx > 0 else zeros
            center = rows[idx]
            right = rows[idx + 1] if idx < window_cells - 1 else zeros
            next_rows.append(eca_packed(rule, left, center, right, ones))
        rows = next_rows
    return rows


def linear_fit(points: list[dict[str, Any]], y_key: str, x_key: str = "dist2") -> dict[str, Any]:
    usable = [point for point in points if point.get(y_key) is not None]
    if y_key == "log10_monomials":
        usable = [point for point in usable if point["monomial_count"] > 0]
    distinct_dist = sorted({point[x_key] for point in usable})
    if len(usable) < 2 or len(distinct_dist) < 2:
        return {
            "usable_count": len(usable),
            "distinct_dist_count": len(distinct_dist),
            "reliable": False,
            "intercept": None,
            "slope": None,
            "r2": None,
        }
    xs = [float(point[x_key]) for point in usable]
    ys = [float(point[y_key]) for point in usable]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    ss_xx = sum((x - x_mean) ** 2 for x in xs)
    ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    slope = ss_xy / ss_xx if ss_xx else 0.0
    intercept = y_mean - slope * x_mean
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot else 1.0
    return {
        "usable_count": len(usable),
        "distinct_dist_count": len(distinct_dist),
        "reliable": len(usable) >= 4 and len(distinct_dist) >= 3,
        "intercept": intercept,
        "slope": slope,
        "r2": r2,
    }


def summarize_outputs(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    if not outputs:
        return {
            "count": 0,
            "distinct_dist2_count": 0,
            "degree_range": None,
            "monomial_range": None,
            "degree_fit": linear_fit([], "degree"),
            "log_monomial_fit": linear_fit([], "log10_monomials"),
        }
    monomials = [row["monomial_count"] for row in outputs]
    degrees = [row["degree"] for row in outputs]
    return {
        "count": len(outputs),
        "distinct_dist2_count": len({row["dist2"] for row in outputs}),
        "degree_range": [min(degrees), max(degrees)],
        "monomial_range": [min(monomials), max(monomials)],
        "degree_fit": linear_fit(outputs, "degree"),
        "log_monomial_fit": linear_fit(outputs, "log10_monomials"),
    }


def frame_to_text(frame: list[int]) -> str:
    return "".join("#" if bit else "." for bit in frame)


def analyze_case(record: dict[str, Any], t_window: int) -> dict[str, Any]:
    window_cells = window_cells_for(t_window)
    place = placement(record, t_window, window_cells)
    rows = simulate_packed_cone(record["rule"], window_cells, t_window)
    frames = simulate_concrete(record["rule"], window_cells, record["ic_word"], place["initial_start"], t_window)
    assignment = concrete_assignment(window_cells, record["ic_word"], place["initial_start"])
    final_concrete = frames[-1]
    active_indices = [idx for idx, bit in enumerate(final_concrete) if bit]
    if active_indices:
        x_left = min(active_indices)
        x_right = max(active_indices)
        center2 = x_left + x_right
    else:
        x_left = None
        x_right = None
        center2 = 2 * place["final_reference"]

    outputs = []
    for idx, table in enumerate(rows):
        row = analyze_output(table, window_cells)
        row.update(
            {
                "output_index": idx,
                "dist2": abs(2 * idx - center2),
                "concrete_final_bit": final_concrete[idx],
                "packed_final_bit": packed_bit(table, assignment),
            }
        )
        row["concrete_match"] = row["concrete_final_bit"] == row["packed_final_bit"]
        row["concrete_active"] = row["concrete_final_bit"] == 1
        row["log10_monomials"] = math.log10(row["monomial_count"]) if row["monomial_count"] > 0 else None
        outputs.append(row)

    concrete_active = [row for row in outputs if row["concrete_active"]]
    nonconstant = [row for row in outputs if row["nonconstant"]]
    return {
        "rule": record["rule"],
        "variant": record["variant"],
        "ic_word": record["ic_word"],
        "period_T": record["period_T"],
        "period_shapes": record["period_shapes"],
        "drift_per_period": record["drift_per_period"],
        "drift_direction": record["drift_direction"],
        "t_window": t_window,
        "window_cells": window_cells,
        "placement": place,
        "final_active_indices": active_indices,
        "final_support_left": x_left,
        "final_support_right": x_right,
        "final_support_center2": center2,
        "concrete_frames": [frame_to_text(frame) for frame in frames],
        "all_outputs_match_concrete": all(row["concrete_match"] for row in outputs),
        "concrete_active_summary": summarize_outputs(concrete_active),
        "nonconstant_summary": summarize_outputs(nonconstant),
        "outputs": outputs,
    }


def fit_is_gradient(summary: dict[str, Any]) -> bool:
    fit = summary["log_monomial_fit"]
    return bool(
        fit["reliable"]
        and fit["r2"] is not None
        and fit["r2"] >= 0.95
        and fit["slope"] is not None
        and fit["slope"] < 0
    )


def verdict(cases: list[dict[str, Any]]) -> tuple[str, str]:
    primary_cases = [
        case for case in cases if case["t_window"] == PRIMARY_T_WINDOW and case["variant"] == "primary_min_ic"
    ]
    control_cases = [
        case for case in cases if case["t_window"] == PRIMARY_T_WINDOW and case["variant"] == "two_cell_phase_control"
    ]
    primary_support = [case["concrete_active_summary"]["distinct_dist2_count"] for case in primary_cases]
    control_support = [case["concrete_active_summary"]["distinct_dist2_count"] for case in control_cases]
    primary_gradients = [fit_is_gradient(case["concrete_active_summary"]) for case in primary_cases]
    control_gradients = [fit_is_gradient(case["concrete_active_summary"]) for case in control_cases]

    if primary_gradients and all(primary_gradients):
        return (
            "ANF_GRADIENT_MOVING_T2_PRESENT",
            "All primary right-moving T=2 gliders show a robust active-output ANF gradient under the 25-cell, 12-step comoving cone.",
        )
    if control_gradients and all(control_gradients):
        return (
            "ANF_GRADIENT_PERIOD_DEPENDENT",
            "The minimal one-cell phase is too small, but the two-cell phase control shows a robust active-output gradient.",
        )
    if max(primary_support + control_support, default=0) < 3:
        return (
            "ANF_GRADIENT_T15_SPECIFIC",
            "Right-moving T=2 glider active supports span too few comoving distance classes for a T=15-like active-output ANF gradient.",
        )
    return (
        "ANF_GRADIENT_T15_SPECIFIC",
        "Neither primary nor two-cell T=2 glider phases show a robust decreasing active-output log-monomial gradient.",
    )


def analyze() -> dict[str, Any]:
    catalog = load_catalog()
    representatives = select_representatives(catalog)
    cases = []
    for record in representatives:
        for t_window in T_WINDOWS:
            cases.append(analyze_case(record, t_window))
    status, reason = verdict(cases)
    return {
        "status": status,
        "verdict_reason": reason,
        "rules": list(RIGHT_DRIFT_RULES),
        "primary_t_window": PRIMARY_T_WINDOW,
        "control_t_window": CONTROL_T_WINDOW,
        "representatives": representatives,
        "cases": cases,
    }


def fmt_fit(fit: dict[str, Any]) -> str:
    if fit["slope"] is None:
        return "not enough support"
    reliable = "yes" if fit["reliable"] else "no"
    return (
        f"slope={fit['slope']:.6f}, intercept={fit['intercept']:.6f}, "
        f"R^2={fit['r2']:.6f}, reliable={reliable}"
    )


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Fase 51: Moving T=2 Glider ANF Baseline",
        "",
        "## Question",
        "",
        "Does the `T=15` ANF gradient appear in moving local oscillators with",
        "`T_local=2`? Fase 51 tests the four right-moving mirror representatives",
        "`rule_20`, `rule_52`, `rule_148`, and `rule_180` from the moving",
        "oscillator catalog.",
        "",
        "The primary horizon is `T_WINDOW=12`, `WINDOW_CELLS=25`: this is a common",
        "comparison horizon against the `T=15` cone, not the minimal T=2 cone.",
        "The secondary control is the minimal `T_WINDOW=2`, `WINDOW_CELLS=5` cone.",
        "Distances are measured in a comoving frame from the final concrete glider",
        "support using `dist2 = abs(2*output_index - (x_left + x_right))`.",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        "## Case table",
        "",
        "| rule | variant | IC | T_WINDOW | window | drift | final active | active dist2 count | active degree | active monomials | active log fit | nonconstant count | nonconstant log fit |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- | ---: | --- | --- | --- | ---: | --- |",
    ]
    for case in data["cases"]:
        active = case["concrete_active_summary"]
        nonconstant = case["nonconstant_summary"]
        lines.append(
            f"| {case['rule']} | {case['variant']} | `{case['ic_word']}` | "
            f"{case['t_window']} | {case['window_cells']} | {case['placement']['expected_drift']} | "
            f"{case['final_active_indices']} | {active['distinct_dist2_count']} | "
            f"{active['degree_range']} | {active['monomial_range']} | "
            f"{fmt_fit(active['log_monomial_fit'])} | {nonconstant['count']} | "
            f"{fmt_fit(nonconstant['log_monomial_fit'])} |"
        )
    lines.extend(
        [
            "",
            "## Concrete frames",
            "",
        ]
    )
    for case in data["cases"]:
        if case["t_window"] != PRIMARY_T_WINDOW:
            continue
        lines.extend(
            [
                f"### rule_{case['rule']} {case['variant']} IC `{case['ic_word']}`",
                "",
                "```text",
                *case["concrete_frames"],
                "```",
                "",
                f"Packed/concrete consistency: `{case['all_outputs_match_concrete']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "The right-moving T=2 gliders are less spatially trivial than the stationary",
            "`rule_108` oscillator, but their concrete active supports remain too small",
            "under the comoving active-output convention. The one-cell phase returns one",
            "active output at the 12-step horizon; the two-cell phase control returns two",
            "adjacent active outputs. Thus the active support occupies too few comoving",
            "distance classes to support a T=15-like spatial ANF gradient.",
            "",
            "The nonconstant cone diagnostics are reported for transparency, but the",
            "scientific verdict follows the active-output convention used throughout the",
            "`T=15` ANF audits.",
            "",
        ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = analyze()
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['status']}")


if __name__ == "__main__":
    main()
