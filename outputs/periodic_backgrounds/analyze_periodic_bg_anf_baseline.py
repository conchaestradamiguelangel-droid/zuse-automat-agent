#!/usr/bin/env python3
"""Fase 52: ANF baseline for wide periodic-background oscillators."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
BASE_SCRIPT = OUT_DIR / "sweep_periodic_background_oscillators.py"
CATALOG_JSONL = OUT_DIR / "periodic_background_oscillator_results.jsonl"
RESULTS_JSON = OUT_DIR / "periodic_bg_anf_baseline_results.json"
REPORT_MD = OUT_DIR / "periodic_bg_anf_baseline_report.md"

WINDOW_CELLS = 25
ASSIGNMENT_COUNT = 1 << WINDOW_CELLS
WORD_COUNT = ASSIGNMENT_COUNT // 64
UINT64_MAX = np.uint64((1 << 64) - 1)
SAMPLE_START = 80
COMMON_T_WINDOW = 12

CASES = [
    {
        "label": "main_rule73_T10",
        "role": "main",
        "rule": 73,
        "background": "0010",
        "T_local": 10,
        "word": "1110111",
    },
    {
        "label": "secondary_rule109_T10",
        "role": "secondary",
        "rule": 109,
        "background": "1011",
        "T_local": 10,
        "word": "00000001",
    },
    {
        "label": "period_control_rule73_T12",
        "role": "period_control",
        "rule": 73,
        "background": "0011",
        "T_local": 12,
        "word": "10001010",
    },
    {
        "label": "low_period_control_rule94_T3",
        "role": "low_period_control",
        "rule": 94,
        "background": "0010",
        "T_local": 3,
        "word": "1000101",
    },
]


def load_base_module():
    spec = importlib.util.spec_from_file_location("periodic_background_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base detector from {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_variable_tables() -> list[np.ndarray]:
    assignments = np.arange(ASSIGNMENT_COUNT, dtype=np.uint32)
    variables = []
    for idx in range(WINDOW_CELLS):
        bits = ((assignments >> idx) & 1).astype(np.uint8)
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


def eca_step_dense(state: list[int], rule: int) -> list[int]:
    width = len(state)
    nxt = []
    for pos, bit in enumerate(state):
        left = state[(pos - 1) % width]
        right = state[(pos + 1) % width]
        key = (left << 2) | (bit << 1) | right
        nxt.append((rule >> key) & 1)
    return nxt


def background_dense(word: str, width: int) -> list[int]:
    return [int(word[pos % len(word)]) for pos in range(width)]


def ic_start(width: int, word: str) -> int:
    return width // 2 - len(word) // 2


def actual_initial_state(base, word: str, background: str) -> list[int]:
    state = background_dense(background, base.WIDTH)
    start = ic_start(base.WIDTH, word)
    for idx, bit in enumerate(word):
        state[start + idx] = int(bit)
    return state


def simulate_dense_frames(base, rule: int, background: str, word: str, steps: int) -> tuple[list[list[int]], list[list[int]]]:
    bg_frames = [background_dense(background, base.WIDTH)]
    actual_frames = [actual_initial_state(base, word, background)]
    for _ in range(steps):
        bg_frames.append(eca_step_dense(bg_frames[-1], rule))
        actual_frames.append(eca_step_dense(actual_frames[-1], rule))
    return bg_frames, actual_frames


def active_diff_indices(bg: list[int], actual: list[int]) -> list[int]:
    return [idx for idx, (a, b) in enumerate(zip(actual, bg)) if a ^ b]


def choose_positions(active_indices: list[int]) -> list[int]:
    if not active_indices:
        center = 128
    else:
        center = (min(active_indices) + max(active_indices)) // 2
    left = center - WINDOW_CELLS // 2
    return list(range(left, left + WINDOW_CELLS))


def bit_from_frame(frame: list[int], global_pos: int) -> int:
    return frame[global_pos % len(frame)]


def concrete_assignment(actual_frame: list[int], positions: list[int]) -> int:
    value = 0
    for idx, global_pos in enumerate(positions):
        if bit_from_frame(actual_frame, global_pos):
            value |= 1 << idx
    return value


def packed_bit(table: np.ndarray, assignment: int) -> int:
    word = assignment >> 6
    offset = np.uint64(assignment & 63)
    return int((table[word] >> offset) & np.uint64(1))


def simulate_packed_cone(
    rule: int,
    bg_frames: list[list[int]],
    actual_frames: list[list[int]],
    positions: list[int],
    t_window: int,
) -> dict[str, Any]:
    zeros = np.zeros(WORD_COUNT, dtype=np.uint64)
    ones = np.full(WORD_COUNT, UINT64_MAX, dtype=np.uint64)
    rows = build_variable_tables()
    for t in range(t_window):
        next_rows = []
        for idx, global_pos in enumerate(positions):
            parents = []
            for delta in (-1, 0, 1):
                local = idx + delta
                if 0 <= local < WINDOW_CELLS:
                    parents.append(rows[local])
                else:
                    fixed_bit = bit_from_frame(actual_frames[SAMPLE_START + t], global_pos + delta)
                    parents.append(ones if fixed_bit else zeros)
            next_rows.append(eca_packed(rule, parents[0], parents[1], parents[2], ones))
        rows = next_rows
    return {"rows": rows, "ones": ones}


def mobius_inplace(bits: np.ndarray) -> None:
    for idx in range(WINDOW_CELLS):
        step = 1 << idx
        block = step << 1
        view = bits.reshape(-1, block)
        view[:, step:block] ^= view[:, :step]


def degree_and_count(coefficients: np.ndarray, popcount16: np.ndarray) -> tuple[int, int, dict[str, int]]:
    total = 0
    degree = -1
    hist: dict[str, int] = {}
    chunk = 1 << 20
    for start in range(0, ASSIGNMENT_COUNT, chunk):
        sub = coefficients[start:start + chunk]
        count = int(sub.sum())
        if not count:
            continue
        total += count
        local = np.nonzero(sub)[0].astype(np.uint32) + np.uint32(start)
        degrees = popcount16[local & np.uint32(0xFFFF)] + popcount16[local >> np.uint32(16)]
        degree = max(degree, int(degrees.max()))
        unique, counts = np.unique(degrees, return_counts=True)
        for deg, deg_count in zip(unique, counts):
            key = str(int(deg))
            hist[key] = hist.get(key, 0) + int(deg_count)
    return degree, total, dict(sorted(hist.items(), key=lambda item: int(item[0])))


def analyze_output_anf(table: np.ndarray, final_bg_bit: int, ones: np.ndarray, popcount16: np.ndarray) -> dict[str, Any]:
    packed = table.copy()
    if final_bg_bit:
        packed ^= ones
    bits = np.unpackbits(packed.view(np.uint8), bitorder="little")[:ASSIGNMENT_COUNT]
    mobius_inplace(bits)
    degree, monomial_count, histogram = degree_and_count(bits, popcount16)
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


def summarize(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    if not outputs:
        return {
            "count": 0,
            "distinct_dist_count": 0,
            "degree_range": None,
            "monomial_range": None,
            "degree_fit": linear_fit([], "degree"),
            "log_monomial_fit": linear_fit([], "log10_monomials"),
        }
    degrees = [row["degree"] for row in outputs]
    monomials = [row["monomial_count"] for row in outputs]
    return {
        "count": len(outputs),
        "distinct_dist_count": len({row["dist"] for row in outputs}),
        "degree_range": [min(degrees), max(degrees)],
        "monomial_range": [min(monomials), max(monomials)],
        "degree_fit": linear_fit(outputs, "degree"),
        "log_monomial_fit": linear_fit(outputs, "log10_monomials"),
    }


def match_catalog_record(catalog: list[dict[str, Any]], case: dict[str, Any]) -> dict[str, Any]:
    matches = [
        row
        for row in catalog
        if row["kind"] == "stationary"
        and row["rule"] == case["rule"]
        and row["background"] == case["background"]
        and row["period_T"] == case["T_local"]
        and row["word"] == case["word"]
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected exactly one catalog match for {case}, found {len(matches)}")
    return matches[0]


def analyze_case(base, catalog, popcount16, case: dict[str, Any], t_window: int) -> dict[str, Any]:
    catalog_record = match_catalog_record(catalog, case)
    steps = SAMPLE_START + t_window
    bg_frames, actual_frames = simulate_dense_frames(base, case["rule"], case["background"], case["word"], steps)
    sample_diff = active_diff_indices(bg_frames[SAMPLE_START], actual_frames[SAMPLE_START])
    final_diff = active_diff_indices(bg_frames[SAMPLE_START + t_window], actual_frames[SAMPLE_START + t_window])
    positions = choose_positions(sample_diff)
    assignment = concrete_assignment(actual_frames[SAMPLE_START], positions)
    simulated = simulate_packed_cone(case["rule"], bg_frames, actual_frames, positions, t_window)
    rows = simulated["rows"]
    ones = simulated["ones"]
    final_bg = bg_frames[SAMPLE_START + t_window]
    final_actual = actual_frames[SAMPLE_START + t_window]
    local_final_diff = [
        bit_from_frame(final_actual, pos) ^ bit_from_frame(final_bg, pos)
        for pos in positions
    ]
    active_indices = [idx for idx, bit in enumerate(local_final_diff) if bit]
    if active_indices:
        center = (min(active_indices) + max(active_indices)) / 2.0
    else:
        center = WINDOW_CELLS // 2

    outputs = []
    for idx, table in enumerate(rows):
        concrete_actual = bit_from_frame(final_actual, positions[idx])
        packed_actual = packed_bit(table, assignment)
        row = analyze_output_anf(table, bit_from_frame(final_bg, positions[idx]), ones, popcount16)
        row.update(
            {
                "output_index": idx,
                "global_pos": positions[idx],
                "dist": abs(idx - center),
                "concrete_final_diff_bit": local_final_diff[idx],
                "concrete_final_actual_bit": concrete_actual,
                "packed_final_actual_bit": packed_actual,
                "concrete_match": concrete_actual == packed_actual,
                "concrete_active": local_final_diff[idx] == 1,
            }
        )
        row["log10_monomials"] = math.log10(row["monomial_count"]) if row["monomial_count"] > 0 else None
        outputs.append(row)

    active_outputs = [row for row in outputs if row["concrete_active"]]
    nonconstant_outputs = [row for row in outputs if row["nonconstant"]]
    return {
        "label": case["label"],
        "role": case["role"],
        "rule": case["rule"],
        "background": case["background"],
        "word": case["word"],
        "T_local": case["T_local"],
        "t_window": t_window,
        "window_cells": WINDOW_CELLS,
        "catalog_span": catalog_record["span"],
        "catalog_motif": catalog_record["motif"],
        "sample_start": SAMPLE_START,
        "sample_diff_global": sample_diff,
        "final_diff_global": final_diff,
        "positions_global": positions,
        "local_final_active_indices": active_indices,
        "all_outputs_match_concrete": all(row["concrete_match"] for row in outputs),
        "active_summary": summarize(active_outputs),
        "nonconstant_summary": summarize(nonconstant_outputs),
        "outputs": outputs,
    }


def fit_is_robust_gradient(summary: dict[str, Any]) -> bool:
    fit = summary["log_monomial_fit"]
    return bool(
        fit["reliable"]
        and fit["slope"] is not None
        and fit["slope"] < 0
        and fit["r2"] is not None
        and fit["r2"] >= 0.95
    )


def verdict(common_cases: list[dict[str, Any]]) -> tuple[str, str]:
    gradients = [fit_is_robust_gradient(case["active_summary"]) for case in common_cases]
    reliable_count = sum(1 for case in common_cases if case["active_summary"]["log_monomial_fit"]["reliable"])
    robust_count = sum(1 for ok in gradients if ok)
    main_case = next(case for case in common_cases if case["role"] == "main")
    if robust_count == len(common_cases):
        return (
            "ANF_GRADIENT_PERIODIC_BG_GENERAL",
            "All periodic-background non-T15 cases show robust active-output log-monomial gradients at the common 12-step horizon.",
        )
    if fit_is_robust_gradient(main_case["active_summary"]) and robust_count >= 2:
        return (
            "ANF_GRADIENT_MECHANISM_DEPENDENT",
            "The main wide periodic-background case shows a robust gradient, but controls do not uniformly match it.",
        )
    if reliable_count and robust_count == 0:
        return (
            "ANF_GRADIENT_T15_SPECIFIC",
            "Wide non-T15 periodic-background cases have enough active support, but none shows a robust T15-like active-output gradient.",
        )
    return (
        "ANF_GRADIENT_MECHANISM_DEPENDENT",
        "Periodic-background cases show mixed or insufficient active-output gradient evidence.",
    )


def analyze() -> dict[str, Any]:
    base = load_base_module()
    catalog = load_jsonl(CATALOG_JSONL)
    popcount16 = np.array([int(i).bit_count() for i in range(1 << 16)], dtype=np.uint8)
    cases = []
    for case in CASES:
        horizons = sorted({case["T_local"], COMMON_T_WINDOW})
        for t_window in horizons:
            cases.append(analyze_case(base, catalog, popcount16, case, t_window))
    common_cases = [case for case in cases if case["t_window"] == COMMON_T_WINDOW]
    status, reason = verdict(common_cases)
    return {
        "status": status,
        "verdict_reason": reason,
        "sample_start": SAMPLE_START,
        "window_cells": WINDOW_CELLS,
        "common_t_window": COMMON_T_WINDOW,
        "case_specs": CASES,
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
        "# Fase 52: Periodic-Background ANF Baseline",
        "",
        "## Question",
        "",
        "Does the `T=15` ANF gradient appear in wide stationary local oscillators",
        "over nontrivial periodic backgrounds with `T_local != 15`?",
        "",
        "The primary verdict uses the common comparison horizon `T_WINDOW=12`,",
        "`WINDOW_CELLS=25`. Each case is also evaluated at its own `T_local` when",
        "`T_local != 12`. The ANF output is the localized XOR defect relative to the",
        "periodic background orbit, matching the `T=15` convention.",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        "## Case table",
        "",
        "| label | role | rule | background | IC | T_local | T_WINDOW | span | active | active dist count | active degree | active monomials | active log fit | nonconstant | nonconstant log fit |",
        "| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- |",
    ]
    for case in data["cases"]:
        active = case["active_summary"]
        nonconstant = case["nonconstant_summary"]
        lines.append(
            f"| {case['label']} | {case['role']} | {case['rule']} | `{case['background']}` | "
            f"`{case['word']}` | {case['T_local']} | {case['t_window']} | {case['catalog_span']} | "
            f"{active['count']} | {active['distinct_dist_count']} | {active['degree_range']} | "
            f"{active['monomial_range']} | {fmt_fit(active['log_monomial_fit'])} | "
            f"{nonconstant['count']} | {fmt_fit(nonconstant['log_monomial_fit'])} |"
        )
    lines.extend(
        [
            "",
            "## Common-horizon reading",
            "",
            "At `T_WINDOW=12`, all four cases have multiple active distance classes,",
            "so unlike Fases 50--51 the gradient test is not blocked by compact active",
            "support. The result therefore probes mechanism specificity rather than",
            "only support width.",
            "",
            "## Motifs",
            "",
        ]
    )
    for case in data["cases"]:
        if case["t_window"] != data["common_t_window"]:
            continue
        lines.extend(
            [
                f"### {case['label']}",
                "",
                "```text",
                *case["catalog_motif"],
                "```",
                "",
                f"Packed/concrete consistency: `{case['all_outputs_match_concrete']}`.",
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
