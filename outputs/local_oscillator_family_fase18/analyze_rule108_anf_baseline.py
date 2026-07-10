#!/usr/bin/env python3
"""Fase 50: ANF baseline for the rule_108 stationary T=2 oscillator."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
RESULTS_JSON = OUT_DIR / "rule108_anf_baseline_results.json"
REPORT_MD = OUT_DIR / "rule108_anf_baseline_report.md"

RULE = 108
IC = "101"
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


def concrete_assignment(window_cells: int, ic: str) -> int:
    center = window_cells // 2
    start = center - len(ic) // 2
    value = 0
    for idx, bit in enumerate(ic):
        if bit == "1":
            value |= 1 << (start + idx)
    return value


def packed_bit(table: np.ndarray, assignment: int) -> int:
    word = assignment >> 6
    offset = np.uint64(assignment & 63)
    return int((table[word] >> offset) & np.uint64(1))


def simulate_packed_cone(rule: int, t_window: int) -> dict[str, Any]:
    window_cells = window_cells_for(t_window)
    word_count = ((1 << window_cells) + 63) // 64
    zeros = np.zeros(word_count, dtype=np.uint64)
    ones = np.full(word_count, np.uint64((1 << 64) - 1), dtype=np.uint64)
    rows = build_variable_tables(window_cells)
    history = {0: rows}
    for t in range(1, t_window + 1):
        next_rows = []
        for idx in range(window_cells):
            left = rows[idx - 1] if idx > 0 else zeros
            center = rows[idx]
            right = rows[idx + 1] if idx < window_cells - 1 else zeros
            next_rows.append(eca_packed(rule, left, center, right, ones))
        rows = next_rows
        history[t] = rows
    return {"rows": rows, "history": history, "ones": ones, "window_cells": window_cells}


def simulate_concrete(rule: int, t_window: int, ic: str) -> list[list[int]]:
    window_cells = window_cells_for(t_window)
    center = window_cells // 2
    start = center - len(ic) // 2
    state = [0] * window_cells
    for idx, bit in enumerate(ic):
        state[start + idx] = int(bit)
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


def mobius_inplace(bits: np.ndarray, window_cells: int) -> None:
    for idx in range(window_cells):
        step = 1 << idx
        block = step << 1
        view = bits.reshape(-1, block)
        view[:, step:block] ^= view[:, :step]


def degree_and_count(coefficients: np.ndarray, window_cells: int) -> tuple[int, int, dict[str, int]]:
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
    degree, monomial_count, histogram = degree_and_count(bits, window_cells)
    return {
        "degree": degree,
        "monomial_count": monomial_count,
        "degree_histogram": histogram,
        "constant_term": int(bits[0]),
        "nonconstant": degree >= 0,
    }


def linear_fit(points: list[dict[str, Any]], y_key: str) -> dict[str, Any]:
    usable = [point for point in points if point.get(y_key) is not None]
    if y_key == "log10_monomials":
        usable = [point for point in usable if point["monomial_count"] > 0]
    distinct_dist = sorted({point["dist"] for point in usable})
    if len(usable) < 2 or len(distinct_dist) < 2:
        return {
            "usable_count": len(usable),
            "distinct_dist_count": len(distinct_dist),
            "reliable": False,
            "intercept": None,
            "slope": None,
            "r2": None,
        }
    xs = [float(point["dist"]) for point in usable]
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
            "distinct_dist_count": 0,
            "degree_range": None,
            "monomial_range": None,
            "degree_fit": linear_fit([], "degree"),
            "log_monomial_fit": linear_fit([], "log10_monomials"),
        }
    monomials = [row["monomial_count"] for row in outputs]
    degrees = [row["degree"] for row in outputs]
    return {
        "count": len(outputs),
        "distinct_dist_count": len({row["dist"] for row in outputs}),
        "degree_range": [min(degrees), max(degrees)],
        "monomial_range": [min(monomials), max(monomials)],
        "degree_fit": linear_fit(outputs, "degree"),
        "log_monomial_fit": linear_fit(outputs, "log10_monomials"),
    }


def analyze_horizon(t_window: int) -> dict[str, Any]:
    packed = simulate_packed_cone(RULE, t_window)
    concrete_frames = simulate_concrete(RULE, t_window, IC)
    window_cells = packed["window_cells"]
    center = window_cells // 2
    assignment = concrete_assignment(window_cells, IC)
    final_concrete = concrete_frames[t_window]
    outputs = []
    for idx, table in enumerate(packed["rows"]):
        row = analyze_output(table, window_cells)
        row.update(
            {
                "output_index": idx,
                "rel_pos": idx - center,
                "dist": abs(idx - center),
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
        "rule": RULE,
        "ic": IC,
        "t_window": t_window,
        "window_cells": window_cells,
        "center_index": center,
        "concrete_frames": ["".join("#" if bit else "." for bit in frame) for frame in concrete_frames],
        "concrete_final_active_count": len(concrete_active),
        "concrete_final_active_indices": [row["output_index"] for row in concrete_active],
        "all_outputs_match_concrete": all(row["concrete_match"] for row in outputs),
        "concrete_active_summary": summarize_outputs(concrete_active),
        "nonconstant_summary": summarize_outputs(nonconstant),
        "outputs": outputs,
    }


def verdict(primary: dict[str, Any]) -> tuple[str, str]:
    active = primary["concrete_active_summary"]
    nonconstant = primary["nonconstant_summary"]
    active_fit = active["log_monomial_fit"]
    nonconstant_fit = nonconstant["log_monomial_fit"]
    if active["distinct_dist_count"] < 3:
        return (
            "ANF_GRADIENT_T15_SPECIFIC",
            "The concrete active T=2 oscillator support spans too few distances for a T=15-like active-output gradient.",
        )
    if active_fit["reliable"] and active_fit["r2"] is not None and active_fit["r2"] >= 0.95 and active_fit["slope"] < 0:
        return (
            "ANF_GRADIENT_LOCAL_OSCILLATOR_GENERAL",
            "The concrete active T=2 oscillator outputs show a robust decreasing log-monomial gradient.",
        )
    if nonconstant_fit["reliable"] and nonconstant_fit["r2"] is not None and nonconstant_fit["r2"] >= 0.95:
        return (
            "ANF_GRADIENT_PERIOD_DEPENDENT",
            "The full nonconstant cone has gradient structure, but it is not expressed on the concrete active oscillator support.",
        )
    return (
        "ANF_GRADIENT_T15_SPECIFIC",
        "Neither the concrete active support nor the full nonconstant cone shows a comparable robust active-output gradient.",
    )


def analyze() -> dict[str, Any]:
    horizons = [analyze_horizon(t) for t in T_WINDOWS]
    primary = next(row for row in horizons if row["t_window"] == PRIMARY_T_WINDOW)
    status, reason = verdict(primary)
    return {
        "status": status,
        "verdict_reason": reason,
        "primary_t_window": PRIMARY_T_WINDOW,
        "control_t_window": CONTROL_T_WINDOW,
        "horizons": horizons,
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
        "# Fase 50: rule_108 T=2 ANF Baseline",
        "",
        "## Question",
        "",
        "Does the ANF gradient observed for the `T=15` mechanism also appear in",
        "the cleanest known stationary local oscillator: `rule_108` on a quiescent",
        "zero background with IC `101` and local period `T=2`?",
        "",
        "The primary horizon is `T_WINDOW=12`, `WINDOW_CELLS=25`: this is a common",
        "comparison horizon against the `T=15` cone, not the minimal T=2 cone.",
        "The secondary control is the minimal `T_WINDOW=2`, `WINDOW_CELLS=5` cone.",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        "## Horizon table",
        "",
        "| T_WINDOW | window cells | final active | active dist count | active degree | active monomials | active log fit | nonconstant count | nonconstant log fit |",
        "| ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- |",
    ]
    for row in data["horizons"]:
        active = row["concrete_active_summary"]
        nonconstant = row["nonconstant_summary"]
        lines.append(
            f"| {row['t_window']} | {row['window_cells']} | {active['count']} | "
            f"{active['distinct_dist_count']} | {active['degree_range']} | "
            f"{active['monomial_range']} | {fmt_fit(active['log_monomial_fit'])} | "
            f"{nonconstant['count']} | {fmt_fit(nonconstant['log_monomial_fit'])} |"
        )
    lines.extend(
        [
            "",
            "## Concrete orbit",
            "",
        ]
    )
    for row in data["horizons"]:
        lines.extend(
            [
                f"### T_WINDOW={row['t_window']}",
                "",
                "```text",
                *row["concrete_frames"],
                "```",
                "",
                f"Packed/concrete consistency: `{row['all_outputs_match_concrete']}`.",
                "",
            ]
        )
    lines.extend(
        [
            "## Interpretation",
            "",
            "The `rule_108` oscillator is a genuine stationary local period-2 witness,",
            "but its concrete active support is extremely small: the final even phase",
            "has two active cells (`#.#`) and the odd phase has three (`###`). Under",
            "the primary 25-cell, 12-step comparison cone, the concrete active outputs",
            "occupy only one distance class from the center. This is not enough support",
            "for a spatial active-output gradient comparable to the `T=15` ANF law.",
            "",
            "The script also reports all nonconstant cone outputs as a diagnostic, but",
            "the scientific verdict is based on the concrete active oscillator support,",
            "matching the active-output convention used in the `T=15` ANF audits.",
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


if __name__ == "__main__":
    main()
