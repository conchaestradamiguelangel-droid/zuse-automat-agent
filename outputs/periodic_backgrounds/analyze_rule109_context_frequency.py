#!/usr/bin/env python3
"""Fase 65: context-frequency audit for selected rule_109 cases.

The audit compares the local ECA contexts used by active defect cells in the
remaining rule_109 residual against positive witnesses and bg=1100 negatives.
It evolves the IC-over-background state and the pure periodic background in
parallel, then measures defect(t) = state(t) XOR background(t).
"""

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
SOURCE_JSON = OUT_DIR / "rule109_t8_alignment_results.json"
RESULTS_JSON = OUT_DIR / "rule109_context_frequency_results.json"
REPORT_MD = OUT_DIR / "rule109_context_frequency_report.md"

RULE = 109
WIDTH = 256
T_WINDOW = 50
CONTEXTS = list(range(8))

POSITIVE_KEYS = [
    ("0011", 12, "10010100"),
    ("0110", 8, "0000011"),
    ("1011", 10, "00000001"),
    ("1100", 8, "00000110"),
    ("1100", 12, "00101001"),
]

NEGATIVE_CONTROL_KEYS = [
    ("1100", 3, "00001110"),
    ("1100", 6, "00100110"),
    ("1100", 10, "00111001"),
]

RESIDUAL_KEY = ("1100", 8, "00000110")


def background_state(background: str, width: int) -> np.ndarray:
    bits = np.array([int(bit) for bit in background], dtype=np.uint8)
    reps = math.ceil(width / len(bits))
    return np.tile(bits, reps)[:width].astype(np.uint8)


def initial_with_ic(background: str, word: str, width: int) -> tuple[np.ndarray, int]:
    state = background_state(background, width)
    bg_len = len(background)
    left = width // 2
    left -= left % bg_len
    word_bits = np.array([int(bit) for bit in word], dtype=np.uint8)
    state[left:left + len(word_bits)] = word_bits
    return state, left


def context_indices(frame: np.ndarray) -> np.ndarray:
    left = np.roll(frame, 1)
    right = np.roll(frame, -1)
    return ((left << 2) | (frame << 1) | right).astype(np.uint8)


def context_label(context: int) -> str:
    return format(context, "03b")


def load_catalog_cases() -> dict[tuple[str, int, str], dict[str, Any]]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    cases = {}
    for row in data["all_rule109_context"]:
        key = (row["background"], int(row["T_local"]), row["word"])
        cases[key] = row
    return cases


def select_cases() -> list[dict[str, Any]]:
    catalog = load_catalog_cases()
    selected: list[dict[str, Any]] = []
    for key in POSITIVE_KEYS:
        row = dict(catalog[key])
        row["group"] = "positive"
        selected.append(row)
    for key in NEGATIVE_CONTROL_KEYS:
        row = dict(catalog[key])
        row["group"] = "negative_control"
        selected.append(row)
    return selected


def simulate_context_usage(case: dict[str, Any]) -> dict[str, Any]:
    initial, left = initial_with_ic(case["background"], case["word"], WIDTH)
    bg_initial = background_state(case["background"], WIDTH)
    frames = simulate(initial, RULE, T_WINDOW)
    bg_frames = simulate(bg_initial, RULE, T_WINDOW)

    counts: Counter[int] = Counter()
    per_t: list[dict[str, Any]] = []
    active_total = 0

    for t in range(T_WINDOW + 1):
        defect = frames[t] ^ bg_frames[t]
        active = np.flatnonzero(defect)
        if t == 0:
            source_frame = bg_frames[0]
        else:
            source_frame = frames[t - 1]
        contexts = context_indices(source_frame)
        step_counts = Counter(int(contexts[idx]) for idx in active)
        counts.update(step_counts)
        active_total += int(active.size)
        per_t.append({
            "t": t,
            "active_count": int(active.size),
            "context_counts": {context_label(k): int(v) for k, v in sorted(step_counts.items())},
        })

    frequencies = {
        context_label(context): (counts[context] / active_total if active_total else 0.0)
        for context in CONTEXTS
    }
    raw_counts = {
        context_label(context): int(counts[context])
        for context in CONTEXTS
    }
    used_contexts = [context_label(context) for context in CONTEXTS if counts[context] > 0]

    return {
        "rule": RULE,
        "background": case["background"],
        "T_local": int(case["T_local"]),
        "word": case["word"],
        "category": case["category"],
        "group": case["group"],
        "label": f"bg={case['background']}/T={case['T_local']}/word={case['word']}",
        "left_index": left,
        "total_active_defect_cells": active_total,
        "context_counts": raw_counts,
        "context_frequencies": frequencies,
        "used_contexts": used_contexts,
        "per_t": per_t,
    }


def context_set(rows: list[dict[str, Any]], predicate) -> set[str]:
    contexts: set[str] = set()
    for row in rows:
        if predicate(row):
            contexts.update(row["used_contexts"])
    return contexts


def contexts_in_every(rows: list[dict[str, Any]]) -> set[str]:
    if not rows:
        return set()
    current = set(rows[0]["used_contexts"])
    for row in rows[1:]:
        current &= set(row["used_contexts"])
    return current


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in rows if row["group"] == "positive"]
    negatives = [row for row in rows if row["group"] == "negative_control"]
    residual = next(
        row for row in rows
        if (row["background"], row["T_local"], row["word"]) == RESIDUAL_KEY
    )
    other_positives = [row for row in positives if row is not residual]

    pos_all = contexts_in_every(positives)
    neg_any = context_set(negatives, lambda row: True)
    all_any = context_set(rows, lambda row: True)
    residual_set = set(residual["used_contexts"])
    other_pos_any = context_set(other_positives, lambda row: True)
    other_pos_all = contexts_in_every(other_positives)

    positive_all_negative_none = sorted(pos_all - neg_any)
    residual_only_vs_other_positives = sorted(residual_set - other_pos_any)
    other_positive_only_vs_residual = sorted(other_pos_all - residual_set)
    never_used = sorted(set(context_label(c) for c in CONTEXTS) - all_any)
    residual_distances = sorted(
        [
            {
                "label": row["label"],
                "group": row["group"],
                "category": row["category"],
                "l1_distance": frequency_l1(residual, row),
            }
            for row in rows
            if row is not residual
        ],
        key=lambda item: item["l1_distance"],
    )

    if positive_all_negative_none:
        status = "CONTEXT_DISCRIMINANT_FOUND"
        interpretation = "At least one context appears in every positive case and in no negative control."
    elif residual_only_vs_other_positives or other_positive_only_vs_residual or never_used:
        status = "CONTEXT_PARTIAL"
        interpretation = (
            "Context usage does not fully separate positives from negative controls, "
            "but it exposes partial residual-specific or intervention-relevant structure."
        )
    else:
        status = "CONTEXT_UNDISCRIMINATED"
        interpretation = "The selected context-frequency descriptors do not expose a clear pattern."

    intervention_status = (
        "CONTEXT_INTERVENTION_CANDIDATE" if never_used else "NO_UNUSED_CONTEXT_INTERVENTION_CANDIDATE"
    )

    return {
        "positive_all_negative_none": positive_all_negative_none,
        "residual_only_vs_other_positives": residual_only_vs_other_positives,
        "other_positive_all_absent_from_residual": other_positive_only_vs_residual,
        "never_used_contexts": never_used,
        "positive_contexts_all": sorted(pos_all),
        "negative_contexts_any": sorted(neg_any),
        "all_used_contexts": sorted(all_any),
        "residual_frequency_l1_distances": residual_distances,
        "status": status,
        "intervention_status": intervention_status,
        "interpretation": interpretation,
    }


def frequency_l1(left: dict[str, Any], right: dict[str, Any]) -> float:
    return float(
        sum(
            abs(left["context_frequencies"][context_label(context)] - right["context_frequencies"][context_label(context)])
            for context in CONTEXTS
        )
    )


def build_report(data: dict[str, Any]) -> str:
    lines = [
        "# Fase 65: rule_109 Context-Frequency Audit",
        "",
        "## Question",
        "",
        "Which local contexts `(L,C,R)` are used by active defect cells in the",
        "residual `rule_109/bg=1100/T=8/word=00000110`, compared with the other",
        "positive rule_109 witnesses and the bg=1100 negative controls?",
        "",
        "## Method",
        "",
        f"- Rule: `{RULE}`",
        f"- Width: `{WIDTH}`",
        f"- Horizon: `t=0..{T_WINDOW}`",
        "- Defect: `state_with_IC(t) XOR background_only(t)`.",
        "- Context index: `(L << 2) | (C << 1) | R`, so contexts are `000` through `111`.",
        "- For active defect cells at `t>0`, contexts are read from `state_with_IC(t-1)`.",
        "- For `t=0`, contexts are read from the pure background frame.",
        "",
        "## Context Frequency Table",
        "",
        "| case | group | category | total active cells | 000 | 001 | 010 | 011 | 100 | 101 | 110 | 111 |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in data["rows"]:
        freq = row["context_frequencies"]
        lines.append(
            f"| `{row['label']}` | `{row['group']}` | `{row['category']}` | {row['total_active_defect_cells']} | "
            + " | ".join(f"{freq[context_label(c)]:.3f}" for c in CONTEXTS)
            + " |"
        )

    summary = data["summary"]
    lines.extend([
        "",
        "## Separation Tests",
        "",
        f"- Contexts in every positive and no negative control: {fmt_list(summary['positive_all_negative_none'])}",
        f"- Contexts used by the residual and by no other positive: {fmt_list(summary['residual_only_vs_other_positives'])}",
        f"- Contexts used by every other positive but absent from the residual: {fmt_list(summary['other_positive_all_absent_from_residual'])}",
        f"- Contexts never used by any selected defect cell: {fmt_list(summary['never_used_contexts'])}",
        "",
        "## Residual Frequency Neighbours",
        "",
        "| rank | case | group | category | L1 distance from residual |",
        "| ---: | --- | --- | --- | ---: |",
    ])
    for rank, item in enumerate(summary["residual_frequency_l1_distances"], start=1):
        lines.append(
            f"| {rank} | `{item['label']}` | `{item['group']}` | `{item['category']}` | "
            f"{item['l1_distance']:.3f} |"
        )

    lines.extend([
        "",
        "## Verdict",
        "",
        f"- Context status: `{summary['status']}`",
        f"- Intervention status: `{summary['intervention_status']}`",
        "",
        summary["interpretation"],
        "",
        "## Methodological Limit",
        "",
        "- The negative set is deliberately narrow: three bg=1100 negative controls.",
        "- A context absent from these 8 cases is only a candidate for safe intervention, not a proof of global safety.",
        "- This phase measures context usage, not ANF gradients for new rules.",
        "",
    ])
    return "\n".join(lines)


def fmt_list(values: list[str]) -> str:
    if not values:
        return "none"
    return ", ".join(f"`{value}`" for value in values)


def main() -> None:
    cases = select_cases()
    rows = [simulate_context_usage(case) for case in cases]
    summary = summarize(rows)
    data = {
        "phase": 65,
        "source": SOURCE_JSON.name,
        "rule": RULE,
        "width": WIDTH,
        "t_window": T_WINDOW,
        "rows": rows,
        "summary": summary,
    }
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {summary['status']}")
    print(f"Intervention status: {summary['intervention_status']}")


if __name__ == "__main__":
    main()
