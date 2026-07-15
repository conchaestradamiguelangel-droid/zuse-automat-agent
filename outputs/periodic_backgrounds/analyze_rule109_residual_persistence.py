#!/usr/bin/env python3
"""Fase 66: long-horizon persistence audit for the rule_109 residual."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.eca import simulate


OUT_DIR = Path(__file__).resolve().parent
RESULTS_JSON = OUT_DIR / "rule109_residual_persistence_results.json"
REPORT_MD = OUT_DIR / "rule109_residual_persistence_report.md"

RULE = 109
BACKGROUND = "1100"
WORD = "00000110"
T_LOCAL = 8
WIDTH = 256
T_WINDOW = 500
SAMPLE_EVERY = 10
RECURRENCE_WINDOW = 100


def background_state(background: str, width: int) -> np.ndarray:
    bits = np.array([int(bit) for bit in background], dtype=np.uint8)
    reps = math.ceil(width / len(bits))
    return np.tile(bits, reps)[:width].astype(np.uint8)


def initial_with_ic(background: str, word: str, width: int) -> tuple[np.ndarray, int]:
    state = background_state(background, width)
    bg_len = len(background)
    left = width // 2
    left -= left % bg_len
    state[left:left + len(word)] = np.array([int(bit) for bit in word], dtype=np.uint8)
    return state, left


def defect_metrics(defect: np.ndarray, left: int) -> dict[str, Any]:
    active = np.flatnonzero(defect)
    if active.size == 0:
        return {
            "defect_size": 0,
            "defect_center": None,
            "defect_center_rel": None,
            "defect_span": 0,
            "active_rel": [],
        }
    center = float(active.mean())
    return {
        "defect_size": int(active.size),
        "defect_center": center,
        "defect_center_rel": float(center - left),
        "defect_span": int(active[-1] - active[0] + 1),
        "active_rel": [int(idx - left) for idx in active],
    }


def find_exact_period(defects: np.ndarray, start: int, end: int) -> int | None:
    """Find the smallest p where defect frames repeat exactly on [start, end]."""
    for period in range(1, (end - start) + 1):
        ok = True
        for t in range(start + period, end + 1):
            if not np.array_equal(defects[t], defects[t - period]):
                ok = False
                break
        if ok:
            return period
    return None


def center_slope(history: list[dict[str, Any]], start: int, end: int) -> float | None:
    points = [
        (row["t"], row["defect_center_rel"])
        for row in history
        if start <= row["t"] <= end and row["defect_center_rel"] is not None
    ]
    if len(points) < 2:
        return None
    x = np.array([p[0] for p in points], dtype=float)
    y = np.array([p[1] for p in points], dtype=float)
    slope, _intercept = np.polyfit(x, y, 1)
    return float(slope)


def classify(history: list[dict[str, Any]], defects: np.ndarray) -> dict[str, Any]:
    sizes = [row["defect_size"] for row in history]
    final_size = sizes[-1]
    collapse_step = next((row["t"] for row in history if row["t"] > 0 and row["defect_size"] == 0), None)
    recurrence_start = T_WINDOW - RECURRENCE_WINDOW
    exact_period = find_exact_period(defects, recurrence_start, T_WINDOW)
    slope = center_slope(history, recurrence_start, T_WINDOW)
    size_tail = sizes[recurrence_start:]
    size_min_tail = min(size_tail)
    size_max_tail = max(size_tail)

    if collapse_step is not None:
        status = "RESIDUAL_IS_TRANSIENT"
        classification = "TRANSIENT"
        interpretation = f"The defect collapses to zero at t={collapse_step}."
    elif slope is not None and abs(slope) >= 0.05 and exact_period is None:
        status = "RESIDUAL_IS_GLIDER"
        classification = "GLIDER"
        interpretation = (
            "The defect persists but its center drifts approximately linearly "
            f"over the last {RECURRENCE_WINDOW} steps."
        )
    elif exact_period is not None:
        status = "RESIDUAL_CONFIRMED_PERSISTENT"
        classification = "PERSISTENT_OSCILLATOR"
        interpretation = (
            f"The defect persists through t={T_WINDOW} and repeats exactly with period {exact_period} "
            f"over the last {RECURRENCE_WINDOW} steps."
        )
    else:
        status = "RESIDUAL_CONFIRMED_PERSISTENT"
        classification = "PERSISTENT_NO_EXACT_PERIOD_FOUND"
        interpretation = (
            f"The defect persists through t={T_WINDOW}, but no exact period was found "
            f"inside the last {RECURRENCE_WINDOW} steps."
        )

    return {
        "status": status,
        "classification": classification,
        "interpretation": interpretation,
        "collapse_step": collapse_step,
        "observed_period_last_100": exact_period,
        "center_slope_last_100": slope,
        "final_size": final_size,
        "tail_size_min": size_min_tail,
        "tail_size_max": size_max_tail,
    }


def sparkline(values: list[int]) -> str:
    ticks = "._:-=+*#"
    if not values:
        return ""
    lo = min(values)
    hi = max(values)
    if lo == hi:
        return ticks[0] * len(values)
    return "".join(ticks[round((value - lo) * (len(ticks) - 1) / (hi - lo))] for value in values)


def build_report(data: dict[str, Any]) -> str:
    sampled = data["sampled_history"]
    sampled_sizes = [row["defect_size"] for row in sampled]
    classification = data["classification"]
    lines = [
        "# Fase 66: rule_109 Residual Persistence Audit",
        "",
        "## Question",
        "",
        "Is `rule_109/bg=1100/T=8/word=00000110` a genuine persistent oscillator,",
        "or a transient that only passed the `HORIZON_ACCEPTABLE` threshold in the",
        "finite Fase 55 window?",
        "",
        "## Setup",
        "",
        f"- Rule: `{RULE}`",
        f"- Background: `{BACKGROUND}`",
        f"- IC word: `{WORD}`",
        f"- Catalog T_local: `{T_LOCAL}`",
        f"- Width: `{WIDTH}`",
        f"- Horizon: `t=0..{T_WINDOW}`",
        "- Defect: `state_with_IC(t) XOR background_only(t)`.",
        "",
        "## Defect Size Trace",
        "",
        f"- Sampled every {SAMPLE_EVERY} steps.",
        f"- Sparkline: `{sparkline(sampled_sizes)}`",
        "",
        "| t | defect_size | defect_span | defect_center_rel |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in sampled:
        center = row["defect_center_rel"]
        center_text = "NA" if center is None else f"{center:.3f}"
        lines.append(
            f"| {row['t']} | {row['defect_size']} | {row['defect_span']} | {center_text} |"
        )

    lines.extend([
        "",
        "## Classification",
        "",
        f"- Classification: `{classification['classification']}`",
        f"- Verdict: `{classification['status']}`",
        f"- Collapse step: `{classification['collapse_step']}`",
        f"- Observed exact period in last 100 steps: `{classification['observed_period_last_100']}`",
        f"- Center slope in last 100 steps: `{classification['center_slope_last_100']}`",
        f"- Final defect size: `{classification['final_size']}`",
        f"- Tail size range: `{classification['tail_size_min']}..{classification['tail_size_max']}`",
        "",
        classification["interpretation"],
        "",
        "## Methodological Limit",
        "",
        "- This phase tests persistence of one residual case only.",
        "- Exact recurrence is measured on the background-subtracted defect frame, not on a canonicalized translated pattern.",
        "- The classification is a preflight for causal interpretation; it does not measure a new ANF gradient.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    initial, left = initial_with_ic(BACKGROUND, WORD, WIDTH)
    bg_initial = background_state(BACKGROUND, WIDTH)
    frames = simulate(initial, RULE, T_WINDOW)
    bg_frames = simulate(bg_initial, RULE, T_WINDOW)
    defects = frames ^ bg_frames

    history = []
    for t in range(T_WINDOW + 1):
        row = {"t": t, **defect_metrics(defects[t], left)}
        history.append(row)

    classification = classify(history, defects)
    sampled_history = [row for row in history if row["t"] % SAMPLE_EVERY == 0]
    data = {
        "phase": 66,
        "rule": RULE,
        "background": BACKGROUND,
        "word": WORD,
        "T_local": T_LOCAL,
        "width": WIDTH,
        "t_window": T_WINDOW,
        "left_index": left,
        "history": history,
        "sampled_history": sampled_history,
        "classification": classification,
    }
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Verdict: {classification['status']}")
    print(f"Classification: {classification['classification']}")


if __name__ == "__main__":
    main()
