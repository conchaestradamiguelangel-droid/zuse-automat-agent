#!/usr/bin/env python3
"""Fase 67: phase/trajectory decomposition for the rule_109 residual."""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.eca import simulate


OUT_DIR = Path(__file__).resolve().parent
RESULTS_JSON = OUT_DIR / "rule109_phase_trajectory_results.json"
REPORT_MD = OUT_DIR / "rule109_phase_trajectory_report.md"

RULE = 109
WIDTH = 256
BACKGROUND = "1100"
RESIDUAL_WORD = "00000110"
NEGATIVE_WORD = "00111001"
RESIDUAL_T = 8
NEGATIVE_T = 10
RESIDUAL_HORIZON = 80
NEGATIVE_HORIZON = 100
RESIDUAL_CLEAN_START = 16
CONTEXTS = list(range(8))


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


def context_label(context: int) -> str:
    return format(context, "03b")


def context_indices(frame: np.ndarray) -> np.ndarray:
    left = np.roll(frame, 1)
    right = np.roll(frame, -1)
    return ((left << 2) | (frame << 1) | right).astype(np.uint8)


def defect_metrics(defect: np.ndarray, left: int) -> dict[str, Any]:
    active = np.flatnonzero(defect)
    if active.size == 0:
        return {
            "size": 0,
            "span": 0,
            "center_rel": None,
            "active_rel": [],
        }
    return {
        "size": int(active.size),
        "span": int(active[-1] - active[0] + 1),
        "center_rel": float(active.mean() - left),
        "active_rel": [int(idx - left) for idx in active],
    }


def simulate_case(word: str, horizon: int) -> dict[str, Any]:
    initial, left = initial_with_ic(BACKGROUND, word, WIDTH)
    bg_initial = background_state(BACKGROUND, WIDTH)
    frames = simulate(initial, RULE, horizon)
    bg_frames = simulate(bg_initial, RULE, horizon)
    defects = frames ^ bg_frames
    history = []
    for t in range(horizon + 1):
        metrics = defect_metrics(defects[t], left)
        metrics["t"] = t
        history.append(metrics)
    return {
        "word": word,
        "left_index": left,
        "frames": frames,
        "bg_frames": bg_frames,
        "defects": defects,
        "history": history,
    }


def exact_period(defects: np.ndarray, start: int, end: int, max_period: int = 80) -> int | None:
    for period in range(1, min(max_period, end - start + 1) + 1):
        ok = True
        for t in range(start + period, end + 1):
            if not np.array_equal(defects[t], defects[t - period]):
                ok = False
                break
        if ok:
            return period
    return None


def verify_residual_period(defects: np.ndarray) -> dict[str, Any]:
    checks = []
    for t in range(RESIDUAL_CLEAN_START, RESIDUAL_HORIZON - RESIDUAL_T + 1):
        checks.append(bool(np.array_equal(defects[t], defects[t + RESIDUAL_T])))
    return {
        "start": RESIDUAL_CLEAN_START,
        "period": RESIDUAL_T,
        "checked_pairs": len(checks),
        "all_match": all(checks),
        "mismatches": int(sum(1 for value in checks if not value)),
    }


def phase_context_profile(case: dict[str, Any], t: int) -> dict[str, Any]:
    defect = case["defects"][t]
    active = np.flatnonzero(defect)
    source_frame = case["bg_frames"][0] if t == 0 else case["frames"][t - 1]
    contexts = context_indices(source_frame)
    counts = Counter(int(contexts[idx]) for idx in active)
    total = int(active.size)
    return {
        "t": t,
        "phase": t - RESIDUAL_CLEAN_START,
        "counts": {context_label(c): int(counts[c]) for c in CONTEXTS},
        "frequencies": {
            context_label(c): (counts[c] / total if total else 0.0)
            for c in CONTEXTS
        },
        "dominant_contexts": [
            context_label(c)
            for c, count in counts.items()
            if total and count == max(counts.values())
        ] if counts else [],
    }


def phase_snapshots(case: dict[str, Any], start: int, period: int) -> list[dict[str, Any]]:
    rows = []
    for p in range(period):
        t = start + p
        metrics = case["history"][t]
        context = phase_context_profile(case, t)
        rows.append({
            "phase": p,
            "t": t,
            "active_rel": metrics["active_rel"],
            "size": metrics["size"],
            "span": metrics["span"],
            "center_rel": metrics["center_rel"],
            "context_counts": context["counts"],
            "context_frequencies": context["frequencies"],
            "dominant_contexts": context["dominant_contexts"],
        })
    return rows


def l1_frequency(a: dict[str, float], b: dict[str, float]) -> float:
    return float(sum(abs(a[context_label(c)] - b[context_label(c)]) for c in CONTEXTS))


def active_jaccard(a: list[int], b: list[int]) -> float:
    left = set(a)
    right = set(b)
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return float(len(left & right) / len(left | right))


def compare_periodic_cases(residual_phases: list[dict[str, Any]], negative_phases: list[dict[str, Any]]) -> dict[str, Any]:
    comparisons = []
    for rp in residual_phases:
        best = None
        for np_row in negative_phases:
            dist = l1_frequency(rp["context_frequencies"], np_row["context_frequencies"])
            item = {
                "residual_phase": rp["phase"],
                "negative_phase": np_row["phase"],
                "context_l1": dist,
                "active_jaccard": active_jaccard(rp["active_rel"], np_row["active_rel"]),
                "size_delta": rp["size"] - np_row["size"],
                "span_delta": rp["span"] - np_row["span"],
            }
            if best is None or item["context_l1"] < best["context_l1"]:
                best = item
        comparisons.append(best)
    return {
        "comparison_applicable": True,
        "best_phase_matches": comparisons,
        "max_best_context_l1": max(item["context_l1"] for item in comparisons),
        "min_best_active_jaccard": min(item["active_jaccard"] for item in comparisons),
        "mean_best_context_l1": float(sum(item["context_l1"] for item in comparisons) / len(comparisons)),
        "mean_best_active_jaccard": float(sum(item["active_jaccard"] for item in comparisons) / len(comparisons)),
    }


def classify(negative_period: int | None, residual_verify: dict[str, Any], comparison: dict[str, Any] | None) -> dict[str, Any]:
    if negative_period is None:
        return {
            "status": "T10_APERIODIC",
            "interpretation": (
                "The nearest negative does not show exact recurrence in the checked horizon; "
                "the aggregate-context similarity is therefore between a persistent oscillator and a non-periodic defect trace."
            ),
        }
    if comparison and (comparison["max_best_context_l1"] >= 0.5 or comparison["min_best_active_jaccard"] <= 0.4):
        return {
            "status": "PHASE_DISCRIMINANT_FOUND",
            "interpretation": (
                "Both traces are periodic, but at least one residual phase has no close context-profile match "
                "among negative phases."
            ),
        }
    if residual_verify["all_match"]:
        return {
            "status": "PHASE_UNDISCRIMINATED",
            "interpretation": (
                "Both traces are periodic and residual phases have close aggregate context-profile matches; "
                "phase snapshots alone do not expose a clear discriminator."
            ),
        }
    return {
        "status": "INCONCLUSIVE",
        "interpretation": "Residual recurrence verification failed or comparison could not be classified.",
    }


def fmt_list(values: list[int] | list[str]) -> str:
    if not values:
        return "[]"
    return "[" + ", ".join(str(v) for v in values) + "]"


def build_report(data: dict[str, Any]) -> str:
    lines = [
        "# Fase 67: rule_109 Phase-Trajectory Audit",
        "",
        "## Question",
        "",
        "At which internal phase, if any, does the persistent residual",
        "`rule_109/bg=1100/T=8/word=00000110` differ qualitatively from the nearest",
        "negative case `rule_109/bg=1100/T=10/word=00111001`?",
        "",
        "## Setup",
        "",
        f"- Rule: `{RULE}`",
        f"- Background: `{BACKGROUND}`",
        f"- Width: `{WIDTH}`",
        "- Defect: `state_with_IC(t) XOR background_only(t)`.",
        "",
        "## Part A: Residual Period-8 Snapshots",
        "",
        f"- Residual evolved to `t={RESIDUAL_HORIZON}`.",
        f"- Period check: `defect(t) == defect(t+8)` for `t >= {RESIDUAL_CLEAN_START}`.",
        f"- Checked pairs: `{data['residual_period_check']['checked_pairs']}`.",
        f"- Mismatches: `{data['residual_period_check']['mismatches']}`.",
        "",
        "| phase | t | size | span | center_rel | active positions | dominant contexts |",
        "| ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in data["residual_phases"]:
        center = "NA" if row["center_rel"] is None else f"{row['center_rel']:.3f}"
        lines.append(
            f"| {row['phase']} | {row['t']} | {row['size']} | {row['span']} | {center} | "
            f"`{fmt_list(row['active_rel'])}` | `{fmt_list(row['dominant_contexts'])}` |"
        )

    lines.extend([
        "",
        "## Part B: Negative T=10 Defect Trace",
        "",
        f"- Negative evolved to `t={NEGATIVE_HORIZON}`.",
        f"- Exact period detected after t=20: `{data['negative_period_after_20']}`.",
        "",
        "| t | defect_size | defect_span | center_rel |",
        "| ---: | ---: | ---: | ---: |",
    ])
    for row in data["negative_sampled_history"]:
        center = "NA" if row["center_rel"] is None else f"{row['center_rel']:.3f}"
        lines.append(f"| {row['t']} | {row['size']} | {row['span']} | {center} |")

    if data["negative_phases"]:
        lines.extend([
            "",
            "### Negative Period Snapshots",
            "",
            "| phase | t | size | span | center_rel | active positions | dominant contexts |",
            "| ---: | ---: | ---: | ---: | ---: | --- | --- |",
        ])
        for row in data["negative_phases"]:
            center = "NA" if row["center_rel"] is None else f"{row['center_rel']:.3f}"
            lines.append(
                f"| {row['phase']} | {row['t']} | {row['size']} | {row['span']} | {center} | "
                f"`{fmt_list(row['active_rel'])}` | `{fmt_list(row['dominant_contexts'])}` |"
            )

    lines.extend([
        "",
        "## Part C: Residual Context Frequencies by Phase",
        "",
        "| phase | 000 | 001 | 010 | 011 | 100 | 101 | 110 | 111 |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in data["residual_phases"]:
        freqs = row["context_frequencies"]
        lines.append(
            f"| {row['phase']} | "
            + " | ".join(f"{freqs[context_label(c)]:.3f}" for c in CONTEXTS)
            + " |"
        )

    if data["comparison"] and data["comparison"]["comparison_applicable"]:
        lines.extend([
            "",
            "## Part D: Periodic Phase Comparison",
            "",
            "| residual phase | nearest negative phase | context L1 | active Jaccard | size delta | span delta |",
            "| ---: | ---: | ---: | ---: | ---: | ---: |",
        ])
        for row in data["comparison"]["best_phase_matches"]:
            lines.append(
                f"| {row['residual_phase']} | {row['negative_phase']} | "
                f"{row['context_l1']:.3f} | {row['active_jaccard']:.3f} | "
                f"{row['size_delta']} | {row['span_delta']} |"
            )
        lines.extend([
            "",
            f"- Mean best phase L1: `{data['comparison']['mean_best_context_l1']:.3f}`",
            f"- Max best phase L1: `{data['comparison']['max_best_context_l1']:.3f}`",
            f"- Mean best active Jaccard: `{data['comparison']['mean_best_active_jaccard']:.3f}`",
            f"- Min best active Jaccard: `{data['comparison']['min_best_active_jaccard']:.3f}`",
        ])
    else:
        lines.extend([
            "",
            "## Part D: Comparison",
            "",
            "`COMPARISON_NOT_APPLICABLE`: the nearest negative does not show a stable exact period in the checked window.",
        ])

    verdict = data["verdict"]
    lines.extend([
        "",
        "## Verdict",
        "",
        f"`{verdict['status']}`.",
        "",
        verdict["interpretation"],
        "",
        "## Methodological Limit",
        "",
        "- This phase compares one positive residual with one nearest negative control.",
        "- Context profiles by phase are still aggregate profiles inside each frame; they do not yet model causal-state transitions.",
        "- If the result is `T10_APERIODIC`, the next audit should compare periodic residual structure against phase-symbol traces across all 17 rule_109 cases.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    residual = simulate_case(RESIDUAL_WORD, RESIDUAL_HORIZON)
    negative = simulate_case(NEGATIVE_WORD, NEGATIVE_HORIZON)

    residual_check = verify_residual_period(residual["defects"])
    residual_phases = phase_snapshots(residual, RESIDUAL_CLEAN_START, RESIDUAL_T)

    negative_period = exact_period(negative["defects"], 20, NEGATIVE_HORIZON, max_period=40)
    negative_sampled = [row for row in negative["history"] if row["t"] % 5 == 0]
    negative_phases = None
    comparison = None
    if negative_period is not None:
        negative_phases = phase_snapshots(negative, NEGATIVE_HORIZON - negative_period + 1, negative_period)
        comparison = compare_periodic_cases(residual_phases, negative_phases)

    verdict = classify(negative_period, residual_check, comparison)
    data = {
        "phase": 67,
        "rule": RULE,
        "background": BACKGROUND,
        "residual_word": RESIDUAL_WORD,
        "negative_word": NEGATIVE_WORD,
        "width": WIDTH,
        "defect_definition": "state_with_IC(t) XOR background_only(t)",
        "residual_period_check": residual_check,
        "residual_phases": residual_phases,
        "negative_period_after_20": negative_period,
        "negative_sampled_history": negative_sampled,
        "negative_phases": negative_phases,
        "comparison": comparison,
        "verdict": verdict,
    }
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Verdict: {verdict['status']}")
    print(f"Negative period: {negative_period}")


if __name__ == "__main__":
    main()
