#!/usr/bin/env python3
"""Fase 69: aligned snapshot-transition audit for rule_109.

Fase 68 compressed every frame to a scalar-ish symbol. This phase keeps the
spatial defect shape itself. To avoid confusing translation with shape, every
defect snapshot is represented in two aligned forms:

* center aligned: doubled coordinates relative to the defect bounding-box
  center, i.e. rel2 = 2*x - (left + right).
* left aligned: coordinates relative to the leftmost active defect cell.

Transitions are pairs of aligned shapes from t to t+1.
"""

from __future__ import annotations

import json
import math
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.eca import simulate


OUT_DIR = Path(__file__).resolve().parent
SOURCE_JSON = OUT_DIR / "rule109_period_horizon_results.json"
RESULTS_JSON = OUT_DIR / "rule109_snapshot_transition_results.json"
REPORT_MD = OUT_DIR / "rule109_snapshot_transition_report.md"

RULE = 109
WIDTH = 256
HORIZON = 100
BURN_IN = 20
POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}
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
    state[left:left + len(word)] = np.array([int(bit) for bit in word], dtype=np.uint8)
    return state, left


def load_cases() -> list[dict[str, Any]]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    rows = [row for row in data["rows"] if int(row["rule"]) == RULE]
    rows.sort(key=lambda row: (row["background"], int(row["T_local"]), row["word"]))
    return rows


def case_label(case: dict[str, Any]) -> str:
    return f"bg={case['background']}/T={case['T_local']}/word={case['word']}/{case['category']}"


def active_positions(defect: np.ndarray) -> tuple[int, ...]:
    return tuple(int(idx) for idx in np.flatnonzero(defect))


def center_aligned_shape(active: tuple[int, ...]) -> tuple[int, ...]:
    if not active:
        return ()
    left = active[0]
    right = active[-1]
    return tuple((2 * idx) - (left + right) for idx in active)


def left_aligned_shape(active: tuple[int, ...]) -> tuple[int, ...]:
    if not active:
        return ()
    left = active[0]
    return tuple(idx - left for idx in active)


def shape_span(active: tuple[int, ...]) -> int:
    if not active:
        return 0
    return active[-1] - active[0] + 1


def symmetric_difference_size(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    return len(set(a) ^ set(b))


def exact_period(values: list[Any], start: int = BURN_IN, max_period: int = 40) -> int | None:
    end = len(values) - 1
    for period in range(1, min(max_period, end - start + 1) + 1):
        ok = True
        for idx in range(start + period, end + 1):
            if values[idx] != values[idx - period]:
                ok = False
                break
        if ok:
            return period
    return None


def analyze_case(case: dict[str, Any]) -> dict[str, Any]:
    initial, ic_left = initial_with_ic(case["background"], case["word"], WIDTH)
    bg_initial = background_state(case["background"], WIDTH)
    frames = simulate(initial, RULE, HORIZON)
    bg_frames = simulate(bg_initial, RULE, HORIZON)
    defects = frames ^ bg_frames

    active_series: list[tuple[int, ...]] = []
    center_shapes: list[tuple[int, ...]] = []
    left_shapes: list[tuple[int, ...]] = []
    sizes: list[int] = []
    spans: list[int] = []
    centers: list[float | None] = []
    for t in range(HORIZON + 1):
        active = active_positions(defects[t])
        active_series.append(active)
        center_shapes.append(center_aligned_shape(active))
        left_shapes.append(left_aligned_shape(active))
        sizes.append(len(active))
        spans.append(shape_span(active))
        centers.append(float(sum(active) / len(active) - ic_left) if active else None)

    center_transitions = list(zip(center_shapes[BURN_IN:-1], center_shapes[BURN_IN + 1:]))
    left_transitions = list(zip(left_shapes[BURN_IN:-1], left_shapes[BURN_IN + 1:]))
    center_step_diff = [
        symmetric_difference_size(center_shapes[t], center_shapes[t + 1])
        for t in range(BURN_IN, HORIZON)
    ]
    left_step_diff = [
        symmetric_difference_size(left_shapes[t], left_shapes[t + 1])
        for t in range(BURN_IN, HORIZON)
    ]

    category = case["category"]
    positive = category in POSITIVE_CATEGORIES
    key = (case["background"], int(case["T_local"]), case["word"])
    return {
        "label": case_label(case),
        "background": case["background"],
        "T_local": int(case["T_local"]),
        "word": case["word"],
        "category": category,
        "positive": positive,
        "is_residual": key == RESIDUAL_KEY,
        "ic_left": ic_left,
        "period_abs": exact_period(active_series),
        "period_center_shape": exact_period(center_shapes),
        "period_left_shape": exact_period(left_shapes),
        "unique_center_shapes": len(set(center_shapes[BURN_IN:])),
        "unique_left_shapes": len(set(left_shapes[BURN_IN:])),
        "unique_center_transitions": len(set(center_transitions)),
        "unique_left_transitions": len(set(left_transitions)),
        "mean_center_step_diff": sum(center_step_diff) / len(center_step_diff),
        "mean_left_step_diff": sum(left_step_diff) / len(left_step_diff),
        "max_center_step_diff": max(center_step_diff),
        "max_left_step_diff": max(left_step_diff),
        "tail_sizes": sizes[BURN_IN:],
        "tail_spans": spans[BURN_IN:],
        "tail_centers": centers[BURN_IN:],
        "center_shapes_tail": [list(shape) for shape in center_shapes[BURN_IN:]],
        "left_shapes_tail": [list(shape) for shape in left_shapes[BURN_IN:]],
        "center_transition_tokens": [transition_token(a, b) for a, b in center_transitions],
        "left_transition_tokens": [transition_token(a, b) for a, b in left_transitions],
    }


def transition_token(a: tuple[int, ...], b: tuple[int, ...]) -> str:
    return f"{shape_token(a)}->{shape_token(b)}"


def shape_token(shape: tuple[int, ...]) -> str:
    if not shape:
        return "empty"
    return ",".join(str(value) for value in shape)


def confusion(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    false_pos: list[str] = []
    false_neg: list[str] = []
    for row in rows:
        pred = predicate(row)
        actual = row["positive"]
        if pred and actual:
            tp += 1
        elif pred and not actual:
            fp += 1
            false_pos.append(row["label"])
        elif not pred and actual:
            fn += 1
            false_neg.append(row["label"])
        else:
            tn += 1
    total = len(rows)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": precision,
        "recall": recall,
        "perfect": fp == 0 and fn == 0,
        "false_positive_labels": false_pos,
        "false_negative_labels": false_neg,
    }


def scan_numeric_thresholds(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = [
        "period_abs",
        "period_center_shape",
        "period_left_shape",
        "unique_center_shapes",
        "unique_left_shapes",
        "unique_center_transitions",
        "unique_left_transitions",
        "mean_center_step_diff",
        "mean_left_step_diff",
        "max_center_step_diff",
        "max_left_step_diff",
        "positive_only_center_transition_count",
        "positive_only_left_transition_count",
    ]
    scans: list[dict[str, Any]] = []
    for metric in metrics:
        values = sorted({row[metric] for row in rows if row.get(metric) is not None})
        for threshold in values:
            scans.append({
                "rule": f"{metric} >= {threshold}",
                "metric": metric,
                "direction": ">=",
                "threshold": threshold,
                **confusion(rows, lambda row, metric=metric, threshold=threshold: row.get(metric) is not None and row[metric] >= threshold),
            })
            scans.append({
                "rule": f"{metric} <= {threshold}",
                "metric": metric,
                "direction": "<=",
                "threshold": threshold,
                **confusion(rows, lambda row, metric=metric, threshold=threshold: row.get(metric) is not None and row[metric] <= threshold),
            })
    scans.sort(key=lambda row: (not row["perfect"], row["fp"], -row["tp"], -row["accuracy"], row["fn"], row["rule"]))
    return scans


def enrich_transition_sets(rows: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in rows if row["positive"]]
    negatives = [row for row in rows if not row["positive"]]
    center_positive_sets = [set(row["center_transition_tokens"]) for row in positives]
    left_positive_sets = [set(row["left_transition_tokens"]) for row in positives]
    center_negative_union = set().union(*(set(row["center_transition_tokens"]) for row in negatives))
    left_negative_union = set().union(*(set(row["left_transition_tokens"]) for row in negatives))
    center_all_positive = set.intersection(*center_positive_sets) if center_positive_sets else set()
    left_all_positive = set.intersection(*left_positive_sets) if left_positive_sets else set()

    residual = next(row for row in rows if row["is_residual"])
    other_rows = [row for row in rows if not row["is_residual"]]
    center_other_union = set().union(*(set(row["center_transition_tokens"]) for row in other_rows))
    left_other_union = set().union(*(set(row["left_transition_tokens"]) for row in other_rows))

    for row in rows:
        center_set = set(row["center_transition_tokens"])
        left_set = set(row["left_transition_tokens"])
        row["positive_only_center_transition_count"] = len(center_set - center_negative_union)
        row["positive_only_left_transition_count"] = len(left_set - left_negative_union)
        row["residual_center_transition_overlap"] = len(center_set & set(residual["center_transition_tokens"]))
        row["residual_left_transition_overlap"] = len(left_set & set(residual["left_transition_tokens"]))

    return {
        "center_transitions_in_all_positives": sorted(center_all_positive),
        "left_transitions_in_all_positives": sorted(left_all_positive),
        "center_transitions_in_all_positives_no_negatives": sorted(center_all_positive - center_negative_union),
        "left_transitions_in_all_positives_no_negatives": sorted(left_all_positive - left_negative_union),
        "residual_center_unique_transitions": sorted(set(residual["center_transition_tokens"]) - center_other_union),
        "residual_left_unique_transitions": sorted(set(residual["left_transition_tokens"]) - left_other_union),
    }


def summarize(rows: list[dict[str, Any]], transition_summary: dict[str, Any], scans: list[dict[str, Any]]) -> dict[str, Any]:
    perfect = [row for row in scans if row["perfect"]]
    no_fp = [row for row in scans if row["fp"] == 0 and row["tp"] > 0]
    best_no_fp = max(no_fp, key=lambda row: (row["tp"], row["accuracy"], row["precision"]), default=None)
    best_accuracy = max(scans, key=lambda row: (row["accuracy"], row["precision"], row["recall"]))
    residual = next(row for row in rows if row["is_residual"])

    has_global_transition = bool(
        transition_summary["center_transitions_in_all_positives_no_negatives"]
        or transition_summary["left_transitions_in_all_positives_no_negatives"]
    )
    if perfect:
        status = "SNAPSHOT_TRANSITION_SEPARATES"
        interpretation = "At least one aligned snapshot-transition metric separates all positives from all non-positives."
    elif has_global_transition:
        status = "SNAPSHOT_TRANSITION_SHARED_POSITIVE_SIGNAL"
        interpretation = "At least one exact aligned transition is shared by all positives and absent from all non-positives."
    elif residual["positive_only_center_transition_count"] > 0 or residual["positive_only_left_transition_count"] > 0:
        status = "SNAPSHOT_TRANSITION_RESIDUAL_SPECIFIC"
        interpretation = "No global separator was found, but the residual contains aligned transitions absent from all non-positive cases."
    elif best_no_fp and best_no_fp["tp"] >= 3:
        status = "SNAPSHOT_TRANSITION_PARTIAL"
        interpretation = "Aligned spatial-transition descriptors provide high-precision partial separation, but do not capture all positives."
    else:
        status = "SNAPSHOT_TRANSITION_NEGATIVE"
        interpretation = "Aligned spatial-transition descriptors do not expose a clean positive or residual-specific signal."

    return {
        "status": status,
        "positive_count": sum(1 for row in rows if row["positive"]),
        "negative_count": sum(1 for row in rows if not row["positive"]),
        "perfect_rules": perfect,
        "best_no_false_positive_rule": best_no_fp,
        "best_accuracy_rule": best_accuracy,
        "transition_summary": transition_summary,
        "residual_label": residual["label"],
        "residual_positive_only_center_transition_count": residual["positive_only_center_transition_count"],
        "residual_positive_only_left_transition_count": residual["positive_only_left_transition_count"],
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def build_report(data: dict[str, Any]) -> str:
    summary = data["summary"]
    lines = [
        "# Fase 69: rule_109 Aligned Snapshot-Transition Audit",
        "",
        "## Question",
        "",
        "Do richer spatial or spatiotemporal representations of the defect separate",
        "the five positive `rule_109` ANF-gradient witnesses from the twelve",
        "non-positive `rule_109` cases, especially the residual",
        "`bg=1100/T=8/word=00000110`?",
        "",
        "This phase does not touch the paper. It tests the next research direction",
        "after v1.32: keeping the spatial defect shape instead of compressing each",
        "frame to scalar temporal summaries.",
        "",
        "## Alignment Protocol",
        "",
        "Distances between snapshots are only meaningful after alignment. This",
        "report therefore uses two explicit shape representations:",
        "",
        "- `center_aligned`: doubled coordinates relative to the defect bounding-box",
        "  center, `rel2 = 2*x - (left + right)`.",
        "- `left_aligned`: coordinates relative to the leftmost active defect cell.",
        "",
        "The center alignment is the primary shape comparison. The left alignment is",
        "a control to catch cases where edge anchoring matters.",
        "",
        "## Method",
        "",
        f"- Rule: `{RULE}`",
        f"- Width: `{WIDTH}`",
        f"- Horizon: `t=0..{HORIZON}`",
        f"- Burn-in for transition sets: `t >= {BURN_IN}`",
        "- Defect: `state_with_IC(t) XOR background_only(t)`.",
        "- Transition token: `(aligned_shape(t), aligned_shape(t+1))`.",
        "",
        "## Case Metrics",
        "",
        "| case | positive | period abs | period center | center shapes | center trans | pos-only center trans | mean center diff |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in data["rows"]:
        lines.append(
            f"| `{row['label']}` | `{row['positive']}` | {fmt(row['period_abs'])} | "
            f"{fmt(row['period_center_shape'])} | {row['unique_center_shapes']} | "
            f"{row['unique_center_transitions']} | {row['positive_only_center_transition_count']} | "
            f"{row['mean_center_step_diff']:.3f} |"
        )

    transition_summary = summary["transition_summary"]
    lines.extend([
        "",
        "## Exact Transition Set Tests",
        "",
        f"- Center-aligned transitions shared by all positives: `{len(transition_summary['center_transitions_in_all_positives'])}`.",
        f"- Center-aligned transitions shared by all positives and no negatives: `{len(transition_summary['center_transitions_in_all_positives_no_negatives'])}`.",
        f"- Left-aligned transitions shared by all positives: `{len(transition_summary['left_transitions_in_all_positives'])}`.",
        f"- Left-aligned transitions shared by all positives and no negatives: `{len(transition_summary['left_transitions_in_all_positives_no_negatives'])}`.",
        f"- Residual center-aligned transitions absent from every other case: `{len(transition_summary['residual_center_unique_transitions'])}`.",
        f"- Residual left-aligned transitions absent from every other case: `{len(transition_summary['residual_left_unique_transitions'])}`.",
        "",
    ])
    if transition_summary["residual_center_unique_transitions"]:
        lines.extend([
            "First residual-unique center transitions:",
            "",
        ])
        for token in transition_summary["residual_center_unique_transitions"][:5]:
            lines.append(f"- `{token}`")
        lines.append("")

    lines.extend([
        "## Numeric Threshold Scan",
        "",
        f"- Perfect rules: `{len(summary['perfect_rules'])}`.",
    ])
    best_no_fp = summary["best_no_false_positive_rule"]
    if best_no_fp:
        lines.append(
            f"- Best no-false-positive rule: `{best_no_fp['rule']}` "
            f"(TP={best_no_fp['tp']}, FP={best_no_fp['fp']}, TN={best_no_fp['tn']}, FN={best_no_fp['fn']}, "
            f"precision={best_no_fp['precision']:.3f}, recall={best_no_fp['recall']:.3f})."
        )
    best_accuracy = summary["best_accuracy_rule"]
    lines.append(
        f"- Best accuracy rule: `{best_accuracy['rule']}` "
        f"(TP={best_accuracy['tp']}, FP={best_accuracy['fp']}, TN={best_accuracy['tn']}, FN={best_accuracy['fn']}, "
        f"accuracy={best_accuracy['accuracy']:.3f})."
    )

    lines.extend([
        "",
        "Top scanned rules:",
        "",
    ])
    for row in data["threshold_scan"][:10]:
        lines.append(
            f"- `{row['rule']}`: TP={row['tp']}, FP={row['fp']}, TN={row['tn']}, FN={row['fn']}, "
            f"acc={row['accuracy']:.3f}, precision={row['precision']:.3f}, recall={row['recall']:.3f}"
        )

    lines.extend([
        "",
        "## Verdict",
        "",
        f"`{summary['status']}`.",
        "",
        summary["interpretation"],
        "",
        "## Methodological Limit",
        "",
        "- This phase compares aligned defect snapshots, not full causal cones.",
        "- Exact transition equality is strict; near-matches may require edit-distance graph methods in a later phase.",
        "- Center alignment removes translation but may also erase drift information; left alignment is included as a control.",
        "- No paper or DOI metadata is changed by this phase.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    rows = [analyze_case(case) for case in load_cases()]
    transition_summary = enrich_transition_sets(rows)
    scans = scan_numeric_thresholds(rows)
    summary = summarize(rows, transition_summary, scans)
    data = {
        "phase": 69,
        "source": SOURCE_JSON.name,
        "rule": RULE,
        "width": WIDTH,
        "horizon": HORIZON,
        "burn_in": BURN_IN,
        "positive_categories": sorted(POSITIVE_CATEGORIES),
        "alignment": {
            "center_aligned": "rel2 = 2*x - (left + right)",
            "left_aligned": "rel = x - left",
        },
        "rows": rows,
        "threshold_scan": scans,
        "summary": summary,
    }
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {summary['status']}")


if __name__ == "__main__":
    main()
