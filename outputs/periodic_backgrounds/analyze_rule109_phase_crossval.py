#!/usr/bin/env python3
"""Fase 67b: cross-validation of phase-dominant contexts in rule_109 positives."""

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
RESULTS_JSON = OUT_DIR / "rule109_phase_crossval_results.json"
REPORT_MD = OUT_DIR / "rule109_phase_crossval_report.md"

RULE = 109
WIDTH = 256
HORIZON = 80
BACKGROUND = "1100"
CONTEXTS = list(range(8))
TARGET_CONTEXT = "100"
TARGET_CONTEXTS = ["011", "100", "111"]

POSITIVES = [
    {"background": "0011", "T_local": 12, "word": "10010100", "category": "NATURAL_PERIOD_STRONG"},
    {"background": "0110", "T_local": 8, "word": "0000011", "category": "HORIZON_ACCEPTABLE"},
    {"background": "1011", "T_local": 10, "word": "00000001", "category": "HORIZON_ACCEPTABLE"},
    {"background": "1100", "T_local": 8, "word": "00000110", "category": "HORIZON_ACCEPTABLE_RESIDUAL"},
    {"background": "1100", "T_local": 12, "word": "00101001", "category": "NATURAL_PERIOD_STRONG"},
]

NEGATIVE_CONTROLS = [
    {"background": "1100", "T_local": 3, "word": "00001110", "category": "NEGATIVE"},
    {"background": "1100", "T_local": 6, "word": "00100110", "category": "NEGATIVE"},
    {"background": "1100", "T_local": 10, "word": "00111001", "category": "NEGATIVE"},
]


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


def exact_period(defects: np.ndarray, start: int, end: int, max_period: int = 40) -> int | None:
    for period in range(1, min(max_period, end - start + 1) + 1):
        ok = True
        for t in range(start + period, end + 1):
            if not np.array_equal(defects[t], defects[t - period]):
                ok = False
                break
        if ok:
            return period
    return None


def active_positions(defect: np.ndarray, left: int) -> list[int]:
    return [int(idx - left) for idx in np.flatnonzero(defect)]


def phase_profile(frames: np.ndarray, bg_frames: np.ndarray, defects: np.ndarray, t: int, left: int, phase: int) -> dict[str, Any]:
    active = np.flatnonzero(defects[t])
    source_frame = bg_frames[0] if t == 0 else frames[t - 1]
    contexts = context_indices(source_frame)
    counts = Counter(int(contexts[idx]) for idx in active)
    total = int(active.size)
    max_count = max(counts.values()) if counts else 0
    dominant = [context_label(c) for c, count in sorted(counts.items()) if count == max_count and count > 0]
    frequencies = {
        context_label(c): (counts[c] / total if total else 0.0)
        for c in CONTEXTS
    }
    return {
        "phase": phase,
        "t": t,
        "size": total,
        "active_rel": active_positions(defects[t], left),
        "counts": {context_label(c): int(counts[c]) for c in CONTEXTS},
        "frequencies": frequencies,
        "dominant_contexts": dominant,
        "target_context_frequency": frequencies[TARGET_CONTEXT],
        "target_is_dominant": TARGET_CONTEXT in dominant,
        "target_is_unique_dominant": dominant == [TARGET_CONTEXT],
    }


def simulate_case(case: dict[str, Any], group: str) -> dict[str, Any]:
    initial, left = initial_with_ic(case["background"], case["word"], WIDTH)
    bg_initial = background_state(case["background"], WIDTH)
    frames = simulate(initial, RULE, HORIZON)
    bg_frames = simulate(bg_initial, RULE, HORIZON)
    defects = frames ^ bg_frames
    period = exact_period(defects, 20, HORIZON)
    if period is None:
        start = HORIZON - case["T_local"] + 1
        phase_count = case["T_local"]
        period_verified = False
    else:
        start = HORIZON - period + 1
        phase_count = period
        period_verified = True

    phases = [
        phase_profile(frames, bg_frames, defects, start + phase, left, phase)
        for phase in range(phase_count)
    ]
    target_dominant_phases = [row["phase"] for row in phases if row["target_is_dominant"]]
    target_unique_phases = [row["phase"] for row in phases if row["target_is_unique_dominant"]]
    return {
        "group": group,
        "rule": RULE,
        "background": case["background"],
        "T_local": case["T_local"],
        "word": case["word"],
        "category": case["category"],
        "label": f"bg={case['background']}/T={case['T_local']}/word={case['word']}",
        "period_after_20": period,
        "period_verified": period_verified,
        "phase_start_t": start,
        "phase_count": phase_count,
        "phases": phases,
        "target_dominant_phases": target_dominant_phases,
        "target_unique_phases": target_unique_phases,
        "has_target_dominant": bool(target_dominant_phases),
        "has_target_unique_dominant": bool(target_unique_phases),
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in rows if row["group"] == "positive"]
    negatives = [row for row in rows if row["group"] == "negative_control"]
    context_summaries = {}
    for context in TARGET_CONTEXTS:
        positive_with_context = [
            row["label"]
            for row in positives
            if any(context in phase["dominant_contexts"] for phase in row["phases"])
        ]
        positive_with_unique_context = [
            row["label"]
            for row in positives
            if any(phase["dominant_contexts"] == [context] for phase in row["phases"])
        ]
        negative_with_context = [
            row["label"]
            for row in negatives
            if any(context in phase["dominant_contexts"] for phase in row["phases"])
        ]
        negative_with_unique_context = [
            row["label"]
            for row in negatives
            if any(phase["dominant_contexts"] == [context] for phase in row["phases"])
        ]
        context_summaries[context] = {
            "positive_dominant_count": len(positive_with_context),
            "positive_dominant": positive_with_context,
            "positive_unique_count": len(positive_with_unique_context),
            "positive_unique": positive_with_unique_context,
            "negative_dominant_count": len(negative_with_context),
            "negative_dominant": negative_with_context,
            "negative_unique_count": len(negative_with_unique_context),
            "negative_unique": negative_with_unique_context,
        }

    positive_with_target = context_summaries[TARGET_CONTEXT]["positive_dominant"]
    positive_with_unique = context_summaries[TARGET_CONTEXT]["positive_unique"]
    negative_with_target = context_summaries[TARGET_CONTEXT]["negative_dominant"]
    negative_with_unique = context_summaries[TARGET_CONTEXT]["negative_unique"]

    count = len(positive_with_target)
    if count >= 3:
        status = "PHASE_CROSSVAL_CONSISTENT"
        interpretation = f"Context {TARGET_CONTEXT} is dominant in {count}/5 positives."
    elif count == 2:
        status = "PHASE_CROSSVAL_PARTIAL"
        interpretation = f"Context {TARGET_CONTEXT} is dominant in only 2/5 positives."
    else:
        status = "PHASE_CROSSVAL_NEGATIVE"
        interpretation = f"Context {TARGET_CONTEXT} is dominant in fewer than 2 positives."

    if negative_with_target:
        interpretation += " It also appears as dominant in at least one negative control, so it is not a clean positive-only discriminator."
    return {
        "status": status,
        "target_context": TARGET_CONTEXT,
        "target_contexts": TARGET_CONTEXTS,
        "context_summaries": context_summaries,
        "positive_with_target_dominant_count": count,
        "positive_with_target_dominant": positive_with_target,
        "positive_with_target_unique_count": len(positive_with_unique),
        "positive_with_target_unique": positive_with_unique,
        "negative_with_target_dominant_count": len(negative_with_target),
        "negative_with_target_dominant": negative_with_target,
        "negative_with_target_unique_count": len(negative_with_unique),
        "negative_with_target_unique": negative_with_unique,
        "interpretation": interpretation,
    }


def fmt(values: list[Any]) -> str:
    if not values:
        return "none"
    return ", ".join(f"`{value}`" for value in values)


def build_report(data: dict[str, Any]) -> str:
    summary = data["summary"]
    lines = [
        "# Fase 67b: rule_109 Phase Cross-Validation",
        "",
        "## Question",
        "",
        "Do the dominant contexts from the residual's discriminant phases generalize",
        "across the five positive `rule_109` witnesses?",
        "",
        "The primary target context is `100`, because Fase 67 found it as the unique",
        "dominant context in residual phase 3, which had the strongest spatial",
        "separation from the nearest negative phase (`active Jaccard = 0.182`).",
        "The report also checks `011` and `111`, the dominant contexts from residual",
        "phases 0 and 7.",
        "",
        "## Dataset",
        "",
        f"- Positives: {len([row for row in data['rows'] if row['group'] == 'positive'])}",
        f"- Negative controls: {len([row for row in data['rows'] if row['group'] == 'negative_control'])}",
        f"- Horizon: `t=0..{HORIZON}`",
        "- Defect: `state_with_IC(t) XOR background_only(t)`.",
        "",
        "## Case Summary",
        "",
        "| group | case | period | target dominant phases | target unique phases |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in data["rows"]:
        lines.append(
            f"| `{row['group']}` | `{row['label']}` | {row['period_after_20']} | "
            f"{fmt(row['target_dominant_phases'])} | {fmt(row['target_unique_phases'])} |"
        )

    lines.extend([
        "",
        "## Verdict",
        "",
        f"`{summary['status']}`.",
        "",
        f"- Positive cases with `100` dominant: {summary['positive_with_target_dominant_count']}/5",
        f"- Positive cases with `100` uniquely dominant: {summary['positive_with_target_unique_count']}/5",
        f"- Negative controls with `100` dominant: {summary['negative_with_target_dominant_count']}/3",
        f"- Negative controls with `100` uniquely dominant: {summary['negative_with_target_unique_count']}/3",
        "",
        "## Target Context Summary",
        "",
        "| context | positives dominant | positives unique | negatives dominant | negatives unique |",
        "| --- | ---: | ---: | ---: | ---: |",
    ])
    for context in TARGET_CONTEXTS:
        item = summary["context_summaries"][context]
        lines.append(
            f"| `{context}` | {item['positive_dominant_count']}/5 | "
            f"{item['positive_unique_count']}/5 | {item['negative_dominant_count']}/3 | "
            f"{item['negative_unique_count']}/3 |"
        )

    lines.extend([
        "",
        summary["interpretation"],
        "",
        "## Methodological Limit",
        "",
        "- This is a cross-check of one phase-level context, not a full causal-state model.",
        "- Dominance is computed within each phase frame, not across phase transitions.",
        "- A partial or negative result here motivates Fase 68: phase-symbol / causal-state analysis over all 17 rule_109 cases.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    rows = [simulate_case(case, "positive") for case in POSITIVES]
    rows.extend(simulate_case(case, "negative_control") for case in NEGATIVE_CONTROLS)
    summary = summarize(rows)
    data = {
        "phase": "67b",
        "rule": RULE,
        "width": WIDTH,
        "target_context": TARGET_CONTEXT,
        "positive_cases": POSITIVES,
        "negative_controls": NEGATIVE_CONTROLS,
        "rows": rows,
        "summary": summary,
    }
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {summary['status']}")


if __name__ == "__main__":
    main()
