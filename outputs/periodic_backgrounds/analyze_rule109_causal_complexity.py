#!/usr/bin/env python3
"""Fase 68: causal-state proxy audit for the 17 rule_109 cases.

The phase measures complexity of the temporal sequence of the defect, not the
complexity of individual frames. Each time step becomes a compact symbol:

    (dominant local context around active defect cells, defect-size bucket)

The resulting sequence is scored with transition entropy, number of unique
transitions, Lempel-Ziv complexity, and detected symbolic period.
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
RESULTS_JSON = OUT_DIR / "rule109_causal_complexity_results.json"
REPORT_MD = OUT_DIR / "rule109_causal_complexity_report.md"

RULE = 109
WIDTH = 256
HORIZON = 100
POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}
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


def context_indices(frame: np.ndarray) -> np.ndarray:
    left = np.roll(frame, 1)
    right = np.roll(frame, -1)
    return ((left << 2) | (frame << 1) | right).astype(np.uint8)


def context_label(context: int | None) -> str:
    return "none" if context is None else format(context, "03b")


def size_bucket(size: int) -> str:
    if size == 0:
        return "0"
    if size <= 3:
        return "1-3"
    if size <= 6:
        return "4-6"
    if size <= 9:
        return "7-9"
    return "10+"


def dominant_context(frame: np.ndarray, active: np.ndarray) -> tuple[str, dict[str, int]]:
    if active.size == 0:
        return "none", {context_label(context): 0 for context in CONTEXTS}
    contexts = context_indices(frame)
    counts = Counter(int(contexts[idx]) for idx in active)
    max_count = max(counts.values())
    winners = sorted(context for context, count in counts.items() if count == max_count)
    # Deterministic tie handling: keep the first numeric context. This keeps the
    # symbol sequence compact while preserving exact counts in the JSON.
    winner = winners[0]
    return context_label(winner), {context_label(context): int(counts[context]) for context in CONTEXTS}


def symbol_period(symbols: list[str], start: int = 20, max_period: int = 40) -> int | None:
    end = len(symbols) - 1
    for period in range(1, min(max_period, end - start + 1) + 1):
        ok = True
        for idx in range(start + period, end + 1):
            if symbols[idx] != symbols[idx - period]:
                ok = False
                break
        if ok:
            return period
    return None


def entropy(counts: Counter[Any]) -> float:
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    value = 0.0
    for count in counts.values():
        p = count / total
        value -= p * math.log2(p)
    return value


def lz_complexity(symbols: list[str]) -> int:
    """Simple exhaustive LZ76 phrase count over a list of discrete symbols."""
    phrases: set[tuple[str, ...]] = set()
    idx = 0
    count = 0
    n = len(symbols)
    while idx < n:
        phrase = (symbols[idx],)
        end = idx + 1
        while phrase in phrases and end < n:
            end += 1
            phrase = tuple(symbols[idx:end])
        phrases.add(phrase)
        count += 1
        idx = end
    return count


def load_rule109_cases() -> list[dict[str, Any]]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    rows = [row for row in data["rows"] if int(row["rule"]) == RULE]
    rows.sort(key=lambda row: (row["background"], int(row["T_local"]), row["word"]))
    return rows


def analyze_case(case: dict[str, Any]) -> dict[str, Any]:
    initial, left = initial_with_ic(case["background"], case["word"], WIDTH)
    bg_initial = background_state(case["background"], WIDTH)
    frames = simulate(initial, RULE, HORIZON)
    bg_frames = simulate(bg_initial, RULE, HORIZON)

    symbols: list[str] = []
    step_rows: list[dict[str, Any]] = []
    for t in range(HORIZON + 1):
        defect = frames[t] ^ bg_frames[t]
        active = np.flatnonzero(defect)
        source_frame = bg_frames[0] if t == 0 else frames[t - 1]
        dominant, context_counts = dominant_context(source_frame, active)
        bucket = size_bucket(int(active.size))
        symbol = f"{dominant}|{bucket}"
        symbols.append(symbol)
        step_rows.append(
            {
                "t": t,
                "defect_size": int(active.size),
                "dominant_context": dominant,
                "size_bucket": bucket,
                "symbol": symbol,
                "context_counts": context_counts,
            }
        )

    transitions = list(zip(symbols[:-1], symbols[1:]))
    transition_counts = Counter(transitions)
    symbol_counts = Counter(symbols)
    period = symbol_period(symbols)
    category = case["category"]
    positive = category in POSITIVE_CATEGORIES
    return {
        "rule": RULE,
        "background": case["background"],
        "T_local": int(case["T_local"]),
        "word": case["word"],
        "category": category,
        "positive": positive,
        "label": case_label(case),
        "symbol_sequence": symbols,
        "steps": step_rows,
        "symbol_entropy": entropy(symbol_counts),
        "bigram_entropy": entropy(transition_counts),
        "unique_symbols": len(symbol_counts),
        "unique_transitions": len(transition_counts),
        "lz_complexity": lz_complexity(symbols),
        "period_detected": period,
    }


def case_label(case: dict[str, Any]) -> str:
    return f"bg={case['background']}/T={case['T_local']}/word={case['word']}/{case['category']}"


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


def threshold_scan(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = ["bigram_entropy", "unique_transitions", "lz_complexity", "period_detected", "unique_symbols"]
    candidates: list[dict[str, Any]] = []
    for metric in metrics:
        values = sorted({row[metric] for row in rows if row[metric] is not None})
        for threshold in values:
            candidates.append(
                {
                    "rule": f"{metric} >= {threshold}",
                    "metric": metric,
                    "direction": ">=",
                    "threshold": threshold,
                    **confusion(rows, lambda row, metric=metric, threshold=threshold: row[metric] is not None and row[metric] >= threshold),
                }
            )
            candidates.append(
                {
                    "rule": f"{metric} <= {threshold}",
                    "metric": metric,
                    "direction": "<=",
                    "threshold": threshold,
                    **confusion(rows, lambda row, metric=metric, threshold=threshold: row[metric] is not None and row[metric] <= threshold),
                }
            )
    candidates.sort(
        key=lambda row: (
            not row["perfect"],
            row["fp"],
            -row["tp"],
            -row["accuracy"],
            -row["precision"],
            row["fn"],
            row["rule"],
        )
    )
    return candidates


def summarize(rows: list[dict[str, Any]], scans: list[dict[str, Any]]) -> dict[str, Any]:
    positives = [row for row in rows if row["positive"]]
    negatives = [row for row in rows if not row["positive"]]
    perfect = [row for row in scans if row["perfect"]]
    no_fp = [row for row in scans if row["fp"] == 0 and row["tp"] > 0]
    non_period_scans = [row for row in scans if row["metric"] != "period_detected"]
    non_period_no_fp = [row for row in non_period_scans if row["fp"] == 0 and row["tp"] > 0]
    best_accuracy = max(scans, key=lambda row: row["accuracy"])
    best_no_fp = max(no_fp, key=lambda row: (row["tp"], row["accuracy"], row["precision"]), default=None)
    best_non_period_accuracy = max(non_period_scans, key=lambda row: row["accuracy"])
    best_non_period_no_fp = max(
        non_period_no_fp,
        key=lambda row: (row["tp"], row["accuracy"], row["precision"]),
        default=None,
    )

    perfect_non_period = [row for row in perfect if row["metric"] != "period_detected"]
    if perfect_non_period:
        status = "COMPLEXITY_SEPARATES"
        interpretation = "At least one transition-complexity metric separates all positives from all non-positives."
    elif best_non_period_no_fp and best_non_period_no_fp["tp"] >= 3:
        status = "COMPLEXITY_PARTIAL"
        interpretation = (
            "Transition-complexity metrics provide high-precision partial separation, "
            "but do not capture all positives."
        )
    elif best_non_period_accuracy["accuracy"] >= 0.85 and best_non_period_accuracy["tp"] >= 3:
        status = "COMPLEXITY_PARTIAL"
        interpretation = "Complexity metrics improve over the majority baseline but do not provide a clean separator."
    else:
        status = "COMPLEXITY_NEGATIVE"
        interpretation = (
            "The selected transition-complexity metrics do not provide a new discriminator. "
            "The best no-false-positive rule is symbolic period >= 12, which recapitulates "
            "the earlier period/horizon result rather than adding a new causal-state signal."
        )

    metric_ranges = {}
    for metric in ["bigram_entropy", "unique_transitions", "lz_complexity", "period_detected", "unique_symbols"]:
        pos_values = [row[metric] for row in positives if row[metric] is not None]
        neg_values = [row[metric] for row in negatives if row[metric] is not None]
        metric_ranges[metric] = {
            "positive_values": pos_values,
            "negative_values": neg_values,
            "positive_min": min(pos_values) if pos_values else None,
            "positive_max": max(pos_values) if pos_values else None,
            "negative_min": min(neg_values) if neg_values else None,
            "negative_max": max(neg_values) if neg_values else None,
        }

    return {
        "status": status,
        "positive_count": len(positives),
        "negative_count": len(negatives),
        "majority_baseline_accuracy": len(negatives) / len(rows),
        "perfect_rules": perfect,
        "perfect_non_period_rules": perfect_non_period,
        "best_no_false_positive_rule": best_no_fp,
        "best_non_period_no_false_positive_rule": best_non_period_no_fp,
        "best_accuracy_rule": best_accuracy,
        "best_non_period_accuracy_rule": best_non_period_accuracy,
        "metric_ranges": metric_ranges,
        "interpretation": interpretation,
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def build_report(data: dict[str, Any]) -> str:
    summary = data["summary"]
    lines = [
        "# Fase 68: rule_109 Causal-Complexity Proxy Audit",
        "",
        "## Question",
        "",
        "Do temporal transition-complexity descriptors of the defect separate the",
        "five positive `rule_109` ANF-gradient witnesses from the twelve",
        "non-positive `rule_109` cases?",
        "",
        "This phase is a small, executable proxy for causal-state/CSSR analysis. It",
        "does not reconstruct full causal states. Instead, it converts each time",
        "step into a phase symbol and measures the complexity of the resulting",
        "symbol-transition sequence.",
        "",
        "## Method",
        "",
        f"- Rule: `{RULE}`",
        f"- Width: `{WIDTH}`",
        f"- Horizon: `t=0..{HORIZON}`",
        "- Defect: `state_with_IC(t) XOR background_only(t)`.",
        "- Step symbol: `(dominant_context(t), defect_size_bucket(t))`.",
        "- Size buckets: `0`, `1-3`, `4-6`, `7-9`, `10+`.",
        "- Metrics: `bigram_entropy`, `unique_transitions`, `lz_complexity`, `period_detected`, `unique_symbols`.",
        "",
        "## Case Metrics",
        "",
        "| case | positive | bigram entropy | unique transitions | LZ | symbolic period | unique symbols |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in data["rows"]:
        lines.append(
            f"| `{row['label']}` | `{row['positive']}` | {row['bigram_entropy']:.3f} | "
            f"{row['unique_transitions']} | {row['lz_complexity']} | "
            f"{row['period_detected']} | {row['unique_symbols']} |"
        )

    lines.extend([
        "",
        "## Threshold Scan",
        "",
        f"- Majority baseline accuracy: {summary['majority_baseline_accuracy']:.3f}",
        f"- Perfect complexity rules: {len(summary['perfect_rules'])}",
        f"- Perfect non-period complexity rules: {len(summary['perfect_non_period_rules'])}",
        "",
    ])
    best_no_fp = summary["best_no_false_positive_rule"]
    if best_no_fp:
        lines.extend([
            "Best no-false-positive rule:",
            "",
            f"- `{best_no_fp['rule']}`: TP={best_no_fp['tp']}, FP={best_no_fp['fp']}, "
            f"TN={best_no_fp['tn']}, FN={best_no_fp['fn']}, "
            f"accuracy={best_no_fp['accuracy']:.3f}, precision={best_no_fp['precision']:.3f}, recall={best_no_fp['recall']:.3f}",
            "",
        ])
    best_acc = summary["best_accuracy_rule"]
    lines.extend([
        "Best accuracy rule:",
        "",
        f"- `{best_acc['rule']}`: TP={best_acc['tp']}, FP={best_acc['fp']}, "
        f"TN={best_acc['tn']}, FN={best_acc['fn']}, "
        f"accuracy={best_acc['accuracy']:.3f}, precision={best_acc['precision']:.3f}, recall={best_acc['recall']:.3f}",
        "",
        "Best non-period complexity rule:",
        "",
    ])
    best_non_period = summary["best_non_period_accuracy_rule"]
    lines.extend([
        f"- `{best_non_period['rule']}`: TP={best_non_period['tp']}, FP={best_non_period['fp']}, "
        f"TN={best_non_period['tn']}, FN={best_non_period['fn']}, "
        f"accuracy={best_non_period['accuracy']:.3f}, precision={best_non_period['precision']:.3f}, recall={best_non_period['recall']:.3f}",
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
        "## Metric Ranges",
        "",
        "| metric | positive range | negative range |",
        "| --- | --- | --- |",
    ])
    for metric, item in summary["metric_ranges"].items():
        lines.append(
            f"| `{metric}` | {fmt(item['positive_min'])}..{fmt(item['positive_max'])} | "
            f"{fmt(item['negative_min'])}..{fmt(item['negative_max'])} |"
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
        "- This is a causal-state proxy, not a full CSSR reconstruction.",
        "- The symbolization intentionally compresses each frame to dominant context plus size bucket.",
        "- A positive separator here would be a guide for CSSR, not a universal proof.",
        "- A negative or partial result means the discriminant may live in richer spatial patterns or longer histories than these symbols encode.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    cases = load_rule109_cases()
    rows = [analyze_case(case) for case in cases]
    scans = threshold_scan(rows)
    summary = summarize(rows, scans)
    data = {
        "phase": 68,
        "source": SOURCE_JSON.name,
        "rule": RULE,
        "width": WIDTH,
        "horizon": HORIZON,
        "positive_categories": sorted(POSITIVE_CATEGORIES),
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
