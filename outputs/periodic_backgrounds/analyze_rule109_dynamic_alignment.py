#!/usr/bin/env python3
"""Fase 61: dynamic defect-alignment audit for the 17 rule_109 cases.

This phase simulates the existing Fase 55 rule_109 catalog cases for a common
12-step horizon. For each case it evolves both the IC-over-background state and
the pure periodic background under rule_109, then measures their XOR defect.
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.eca import simulate


OUT_DIR = Path(__file__).resolve().parent
INPUT_JSON = OUT_DIR / "rule109_alignment_validation_results.json"
RESULTS_JSON = OUT_DIR / "rule109_dynamic_alignment_results.json"
REPORT_MD = OUT_DIR / "rule109_dynamic_alignment_report.md"

RULE = 109
WIDTH = 256
COMMON_T_WINDOW = 12
POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}
DYNAMIC_DESCRIPTORS = [
    "growth_rate_early",
    "compactness_mean",
    "span_at_t6",
    "defect_size_final",
    "compactness_at_t6",
    "defect_monotone",
    "max_defect_size",
    "max_defect_span",
    "center_drift_abs",
    "size_growth_total",
    "span_growth_total",
]


def load_cases() -> list[dict[str, Any]]:
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    rows = data["descriptor_results"]
    del rows
    source = json.loads((OUT_DIR / "rule109_t8_alignment_results.json").read_text(encoding="utf-8"))
    cases = source["all_rule109_context"]
    for case in cases:
        case["positive"] = case["category"] in POSITIVE_CATEGORIES
    return cases


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


def defect_metrics(defect: np.ndarray, left: int) -> dict[str, Any]:
    active = np.flatnonzero(defect)
    size = int(active.size)
    if size == 0:
        return {
            "size": 0,
            "span": 0,
            "compactness": 0.0,
            "center": None,
            "center_rel": None,
            "active_rel": [],
        }
    span = int(active[-1] - active[0] + 1)
    center = float(active.mean())
    return {
        "size": size,
        "span": span,
        "compactness": float(size / span),
        "center": center,
        "center_rel": float(center - left),
        "active_rel": [int(idx - left) for idx in active],
    }


def simulate_case(case: dict[str, Any]) -> dict[str, Any]:
    initial, left = initial_with_ic(case["background"], case["word"], WIDTH)
    bg_initial = background_state(case["background"], WIDTH)
    frames = simulate(initial, RULE, COMMON_T_WINDOW)
    bg_frames = simulate(bg_initial, RULE, COMMON_T_WINDOW)

    history = []
    for t in range(COMMON_T_WINDOW + 1):
        defect = frames[t] ^ bg_frames[t]
        metrics = defect_metrics(defect, left)
        metrics["t"] = t
        history.append(metrics)

    sizes = [row["size"] for row in history]
    spans = [row["span"] for row in history]
    compactness = [row["compactness"] for row in history]
    centers = [row["center_rel"] for row in history]
    centers_non_null = [float(c) for c in centers if c is not None]

    size_t1 = sizes[1]
    growth_rate_early = float(sizes[3] / size_t1) if size_t1 else None
    defect_monotone = all(sizes[idx] <= sizes[idx + 1] for idx in range(1, COMMON_T_WINDOW))
    center_drift_abs = (
        float(abs(centers_non_null[-1] - centers_non_null[0]))
        if len(centers_non_null) >= 2
        else None
    )

    descriptors = {
        "growth_rate_early": growth_rate_early,
        "compactness_mean": float(sum(compactness[1:]) / COMMON_T_WINDOW),
        "span_at_t6": spans[6],
        "defect_size_final": sizes[12],
        "compactness_at_t6": compactness[6],
        "defect_monotone": defect_monotone,
        "max_defect_size": max(sizes[1:]),
        "max_defect_span": max(spans[1:]),
        "center_drift_abs": center_drift_abs,
        "size_growth_total": sizes[12] - sizes[1],
        "span_growth_total": spans[12] - spans[1],
    }

    return {
        "rule": RULE,
        "background": case["background"],
        "T_local": case["T_local"],
        "word": case["word"],
        "category": case["category"],
        "positive": case["positive"],
        "left_index": left,
        "width": WIDTH,
        "history": history,
        "descriptors": descriptors,
    }


def confusion(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    false_pos = []
    false_neg = []
    for row in rows:
        pred = bool(predicate(row))
        actual = bool(row["positive"])
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
    total = tp + fp + tn + fn
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": tp / (tp + fp) if (tp + fp) else 0.0,
        "recall": tp / (tp + fn) if (tp + fn) else 0.0,
        "false_positives": false_pos,
        "false_negatives": false_neg,
    }


def descriptor_value(row: dict[str, Any], key: str) -> Any:
    return row["descriptors"][key]


def evaluate_descriptor(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    values = sorted({descriptor_value(row, key) for row in rows if descriptor_value(row, key) is not None})
    rules = []
    if all(isinstance(value, bool) for value in values):
        rules.append({
            "rule": f"{key} == True",
            **confusion(rows, lambda row: descriptor_value(row, key) is True),
        })
        rules.append({
            "rule": f"{key} == False",
            **confusion(rows, lambda row: descriptor_value(row, key) is False),
        })
    else:
        for threshold in values:
            rules.append({
                "rule": f"{key} <= {threshold}",
                **confusion(rows, lambda row, t=threshold: descriptor_value(row, key) is not None and descriptor_value(row, key) <= t),
            })
            rules.append({
                "rule": f"{key} >= {threshold}",
                **confusion(rows, lambda row, t=threshold: descriptor_value(row, key) is not None and descriptor_value(row, key) >= t),
            })
    rules = sorted(
        rules,
        key=lambda item: (item["fp"] == 0 and item["fn"] == 0, item["fp"] == 0, item["accuracy"], item["recall"], item["precision"]),
        reverse=True,
    )
    return {
        "descriptor": key,
        "best_rules": rules[:8],
        "perfect_rules": [rule for rule in rules if rule["fp"] == 0 and rule["fn"] == 0],
        "no_false_positive_rules": [rule for rule in rules if rule["fp"] == 0 and rule["tp"] > 0],
    }


def build_report(data: dict[str, Any]) -> str:
    lines = [
        "# Fase 61: rule_109 Dynamic Alignment Audit",
        "",
        "## Question",
        "",
        "Do positive and non-positive `rule_109` catalog cases differ in how the",
        "background-subtracted defect evolves over the common horizon `t=1..12`?",
        "",
        "Unlike Fases 59-60, this phase runs new ECA simulations. For each case it",
        "evolves both the IC-over-background state and the pure periodic background",
        "under rule_109, then measures their XOR defect.",
        "",
        "## Dataset",
        "",
        f"- Cases: {data['case_count']}",
        f"- Positives: {data['positive_count']}",
        f"- Non-positives: {data['non_positive_count']}",
        f"- Width: {WIDTH}",
        f"- Horizon: {COMMON_T_WINDOW}",
        "",
        "| bg | T | category | word | size@1 | size@12 | span@6 | compact@6 | growth_early | monotone |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in data["rows"]:
        desc = row["descriptors"]
        h = row["history"]
        growth = desc["growth_rate_early"]
        growth_txt = "NA" if growth is None else f"{growth:.3f}"
        lines.append(
            f"| `{row['background']}` | {row['T_local']} | `{row['category']}` | `{row['word']}` | "
            f"{h[1]['size']} | {h[12]['size']} | {desc['span_at_t6']} | "
            f"{desc['compactness_at_t6']:.3f} | {growth_txt} | {str(desc['defect_monotone']).lower()} |"
        )

    lines.extend(["", "## Descriptor Separation", ""])
    for item in data["descriptor_tests"]:
        best = item["best_rules"][0] if item["best_rules"] else None
        lines.append(f"### `{item['descriptor']}`")
        lines.append("")
        if item["perfect_rules"]:
            lines.append("- Perfect separating rule(s):")
            for rule in item["perfect_rules"][:3]:
                lines.append(f"  - `{rule['rule']}`")
        else:
            lines.append("- Perfect separating rule(s): none")
        if item["no_false_positive_rules"]:
            lines.append("- No-false-positive rule(s):")
            for rule in item["no_false_positive_rules"][:3]:
                lines.append(
                    f"  - `{rule['rule']}` -> TP={rule['tp']}, FP={rule['fp']}, "
                    f"TN={rule['tn']}, FN={rule['fn']}, accuracy={rule['accuracy']:.3f}"
                )
                captured = [
                    row["label"]
                    for row in data["rows"]
                    if row["positive"] and eval_rule_for_report(row, rule["rule"])
                ]
                if captured:
                    lines.append(f"    - Captures: {', '.join('`' + label + '`' for label in captured)}")
        else:
            lines.append("- No-false-positive rule(s): none")
        if best:
            lines.append(
                f"- Best rule: `{best['rule']}` -> TP={best['tp']}, FP={best['fp']}, "
                f"TN={best['tn']}, FN={best['fn']}, accuracy={best['accuracy']:.3f}"
            )
        lines.append("")

    lines.extend([
        "## Verdict",
        "",
        f"`{data['status']}`.",
        "",
        data["interpretation"],
        "",
        "## Methodological Limit",
        "",
        "- The audit is restricted to the 17 `rule_109` cases in the existing Fase 55 catalog.",
        "- It does not establish a universal law over all rule_109 backgrounds or all ECA rules.",
        "- The pure background is evolved under rule_109 in parallel with the IC state; the defect is measured as `state(t) XOR background(t)`.",
        "",
    ])
    return "\n".join(lines)


def eval_rule_for_report(row: dict[str, Any], rule: str) -> bool:
    """Evaluate report-only threshold strings generated by evaluate_descriptor."""
    key, op, raw_value = rule.split(" ", 2)
    value = row["descriptors"][key]
    if raw_value == "True":
        threshold: Any = True
    elif raw_value == "False":
        threshold = False
    else:
        threshold = float(raw_value)
    if op == "<=":
        return value is not None and value <= threshold
    if op == ">=":
        return value is not None and value >= threshold
    if op == "==":
        return value == threshold
    raise ValueError(f"unsupported rule operator: {rule}")


def main() -> None:
    cases = load_cases()
    rows = []
    for case in cases:
        simulated = simulate_case(case)
        simulated["label"] = f"bg={simulated['background']}/T={simulated['T_local']}/word={simulated['word']}"
        rows.append(simulated)

    descriptor_tests = [evaluate_descriptor(rows, key) for key in DYNAMIC_DESCRIPTORS]
    perfect = [
        (item["descriptor"], rule)
        for item in descriptor_tests
        for rule in item["perfect_rules"]
    ]
    nfp = [
        (item["descriptor"], rule)
        for item in descriptor_tests
        for rule in item["no_false_positive_rules"]
    ]
    if perfect:
        status = "DYNAMIC_DISCRIMINANT_FOUND"
        interpretation = "At least one dynamic descriptor separates all 5 positives from all 12 non-positives."
    elif nfp:
        status = "DYNAMIC_PARTIAL"
        interpretation = (
            "Dynamic descriptors provide partial high-precision signal: at least one threshold has no false "
            "positives, but no tested descriptor separates all positives from all non-positives."
        )
    else:
        status = "DYNAMIC_INSUFFICIENT"
        interpretation = "No tested dynamic descriptor provides a no-false-positive separation of the positives."

    data = {
        "source": INPUT_JSON.name,
        "case_count": len(rows),
        "positive_count": sum(1 for row in rows if row["positive"]),
        "non_positive_count": sum(1 for row in rows if not row["positive"]),
        "status": status,
        "interpretation": interpretation,
        "rows": rows,
        "descriptor_tests": descriptor_tests,
    }
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {status}")
    if perfect:
        print("Perfect rules:", [(key, rule["rule"]) for key, rule in perfect[:5]])
    elif nfp:
        print("No-false-positive rules:", [(key, rule["rule"], rule["tp"]) for key, rule in nfp[:5]])


if __name__ == "__main__":
    main()
