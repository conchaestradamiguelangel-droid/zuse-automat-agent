#!/usr/bin/env python3
"""Fase 58: period/horizon discriminator for rule_109 center-mediated cases.

The phase uses the Fase 55 census only. It restricts attention to the 17
`rule_109` catalog cases, all of which share the center-mediated local ANF
structure identified in Fases 56-57, and tests whether period/horizon features
separate ANF-gradient witnesses from non-witnesses.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Callable


OUT_DIR = Path(__file__).resolve().parent
CENSUS_JSON = OUT_DIR / "anf_gradient_census_results.json"
RESULTS_JSON = OUT_DIR / "rule109_period_horizon_results.json"
REPORT_MD = OUT_DIR / "rule109_period_horizon_report.md"

POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}
COMMON_T_WINDOW = 12


def load_census() -> dict[str, Any]:
    return json.loads(CENSUS_JSON.read_text(encoding="utf-8"))


def rotations(word: str) -> list[str]:
    return [word[idx:] + word[:idx] for idx in range(len(word))]


def canonical_rotation(word: str) -> str:
    return min(rotations(word))


def complement(word: str) -> str:
    return "".join("1" if bit == "0" else "0" for bit in word)


def enrich_case(case: dict[str, Any]) -> dict[str, Any]:
    t_local = int(case["T_local"])
    bg = case["background"]
    category = case["category"]
    positive = category in POSITIVE_CATEGORIES
    ratio = COMMON_T_WINDOW / t_local
    return {
        **case,
        "positive": positive,
        "t_window_common": COMMON_T_WINDOW,
        "oversampling_ratio": ratio,
        "ratio_le_1_5": ratio <= 1.5,
        "ratio_le_1_2": ratio <= 1.2,
        "ratio_eq_1": ratio == 1.0,
        "canonical_background": canonical_rotation(bg),
        "background_complement": complement(bg),
        "background_int": int(bg, 2),
        "background_weight": bg.count("1"),
        "background_is_rotation_of_0011": canonical_rotation(bg) == "0011",
        "background_is_1011_orbit": canonical_rotation(bg) == "0111",
    }


def confusion(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    false_pos = []
    false_neg = []
    for row in rows:
        pred = predicate(row)
        actual = row["positive"]
        if pred and actual:
            tp += 1
        elif pred and not actual:
            fp += 1
            false_pos.append(row)
        elif not pred and actual:
            fn += 1
            false_neg.append(row)
        else:
            tn += 1
    total = len(rows)
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "perfect": fp == 0 and fn == 0,
        "false_positive_labels": [case_label(row) for row in false_pos],
        "false_negative_labels": [case_label(row) for row in false_neg],
    }


def case_label(row: dict[str, Any]) -> str:
    return f"bg={row['background']}/T={row['T_local']}/word={row['word']}/{row['category']}"


def evaluate_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rules: list[tuple[str, Callable[[dict[str, Any]], bool]]] = []
    t_values = sorted({row["T_local"] for row in rows})
    ratio_values = sorted({row["oversampling_ratio"] for row in rows})
    bgs = sorted({row["background"] for row in rows})
    canon_bgs = sorted({row["canonical_background"] for row in rows})

    for threshold in t_values:
        rules.append((f"T_local >= {threshold}", lambda row, threshold=threshold: row["T_local"] >= threshold))
        rules.append((f"T_local == {threshold}", lambda row, threshold=threshold: row["T_local"] == threshold))
    for threshold in ratio_values:
        rules.append(
            (
                f"oversampling_ratio <= {threshold:.3f}",
                lambda row, threshold=threshold: row["oversampling_ratio"] <= threshold,
            )
        )
        rules.append(
            (
                f"oversampling_ratio == {threshold:.3f}",
                lambda row, threshold=threshold: abs(row["oversampling_ratio"] - threshold) < 1e-12,
            )
        )
    for bg in bgs:
        rules.append((f"background == {bg}", lambda row, bg=bg: row["background"] == bg))
    for canonical in canon_bgs:
        rules.append(
            (
                f"canonical_background == {canonical}",
                lambda row, canonical=canonical: row["canonical_background"] == canonical,
            )
        )

    # Small two-condition rules: period/horizon plus background/orbit.
    period_preds = [
        (f"T_local >= {threshold}", lambda row, threshold=threshold: row["T_local"] >= threshold)
        for threshold in t_values
    ] + [
        (
            f"oversampling_ratio <= {threshold:.3f}",
            lambda row, threshold=threshold: row["oversampling_ratio"] <= threshold,
        )
        for threshold in ratio_values
    ]
    bg_preds = [
        (f"background != {bg}", lambda row, bg=bg: row["background"] != bg)
        for bg in bgs
    ] + [
        (
            f"canonical_background == {canonical}",
            lambda row, canonical=canonical: row["canonical_background"] == canonical,
        )
        for canonical in canon_bgs
    ]
    for (name_a, pred_a), (name_b, pred_b) in [(a, b) for a in period_preds for b in bg_preds]:
        rules.append((f"{name_a} AND {name_b}", lambda row, pred_a=pred_a, pred_b=pred_b: pred_a(row) and pred_b(row)))

    scored = []
    for name, pred in rules:
        scored.append({"rule": name, **confusion(rows, pred)})
    scored.sort(key=lambda row: (not row["perfect"], -row["accuracy"], row["fp"] + row["fn"], row["rule"]))
    return scored


def analyze() -> dict[str, Any]:
    census = load_census()
    rows = [enrich_case(case) for case in census["case_summaries"] if case["rule"] == 109]
    rows.sort(key=lambda row: (row["background"], row["T_local"], row["word"]))
    categories_by_period = defaultdict(Counter)
    categories_by_ratio = defaultdict(Counter)
    categories_by_background = defaultdict(Counter)
    for row in rows:
        categories_by_period[row["T_local"]][row["category"]] += 1
        categories_by_ratio[f"{row['oversampling_ratio']:.3f}"][row["category"]] += 1
        categories_by_background[row["background"]][row["category"]] += 1
    rules = evaluate_rules(rows)
    period_only_rules = [row for row in rules if ("background" not in row["rule"] and "canonical" not in row["rule"])]
    perfect_rules = [row for row in rules if row["perfect"]]
    perfect_period_only = [row for row in period_only_rules if row["perfect"]]
    if perfect_period_only:
        status = "PERIOD_HORIZON_SUFFICIENT"
    elif perfect_rules:
        status = "PERIOD_HORIZON_PLUS_BACKGROUND_SUFFICIENT"
    else:
        status = "PERIOD_HORIZON_PARTIAL_DISCRIMINANT"
    return {
        "source": str(CENSUS_JSON.name),
        "positive_categories": sorted(POSITIVE_CATEGORIES),
        "common_t_window": COMMON_T_WINDOW,
        "rule109_case_count": len(rows),
        "positive_count": sum(1 for row in rows if row["positive"]),
        "negative_count": sum(1 for row in rows if not row["positive"]),
        "rows": rows,
        "categories_by_period": {str(k): dict(v) for k, v in sorted(categories_by_period.items())},
        "categories_by_ratio": {k: dict(v) for k, v in sorted(categories_by_ratio.items())},
        "categories_by_background": {k: dict(v) for k, v in sorted(categories_by_background.items())},
        "best_rules": rules[:20],
        "best_period_only_rules": period_only_rules[:12],
        "perfect_rules": perfect_rules,
        "perfect_period_only_rules": perfect_period_only,
        "status": status,
    }


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Fase 58: rule_109 Period/Horizon Discriminator",
        "",
        "## Question",
        "",
        "Given the Fase 57 result that center-mediated local ANF is necessary but",
        "not sufficient, can period/horizon features separate the 5 positive",
        "`rule_109` ANF-gradient witnesses from the 12 non-positive center-mediated",
        "cases?",
        "",
        "This phase uses only the Fase 55 census. It runs no new ECA or ANF",
        "simulation.",
        "",
        "## Dataset",
        "",
        f"- `rule_109` catalog cases: {data['rule109_case_count']}",
        f"- Positive cases (`NATURAL_PERIOD_STRONG` or `HORIZON_ACCEPTABLE`): {data['positive_count']}",
        f"- Non-positive cases: {data['negative_count']}",
        f"- Common horizon: `T_WINDOW={data['common_t_window']}`",
        "",
        "## Case Table",
        "",
        "| background | T_local | ratio 12/T | category | positive | word |",
        "| --- | ---: | ---: | --- | --- | --- |",
    ]
    for row in data["rows"]:
        lines.append(
            f"| `{row['background']}` | {row['T_local']} | {row['oversampling_ratio']:.3f} | "
            f"`{row['category']}` | `{row['positive']}` | `{row['word']}` |"
        )
    lines.extend(["", "## Period and Horizon Stratification", ""])
    lines.append("By `T_local`:")
    lines.append("")
    for period, counts in data["categories_by_period"].items():
        lines.append(f"- `T={period}`: `{counts}`")
    lines.append("")
    lines.append("By oversampling ratio `12/T_local`:")
    lines.append("")
    for ratio, counts in data["categories_by_ratio"].items():
        lines.append(f"- `{ratio}`: `{counts}`")
    lines.extend(["", "## Rule Search", ""])
    lines.append("Best period/horizon-only rules:")
    lines.append("")
    for rule in data["best_period_only_rules"][:8]:
        lines.append(
            f"- `{rule['rule']}`: acc={rule['accuracy']:.3f}, "
            f"TP={rule['tp']}, FP={rule['fp']}, TN={rule['tn']}, FN={rule['fn']}"
        )
    lines.append("")
    if data["perfect_period_only_rules"]:
        lines.append("A period/horizon-only rule separates the cases perfectly:")
        for rule in data["perfect_period_only_rules"]:
            lines.append(f"- `{rule['rule']}`")
    else:
        lines.append("No period/horizon-only rule separates positives from non-positives perfectly.")
    lines.extend(["", "Best overall small rules:", ""])
    for rule in data["best_rules"][:8]:
        lines.append(
            f"- `{rule['rule']}`: acc={rule['accuracy']:.3f}, "
            f"TP={rule['tp']}, FP={rule['fp']}, TN={rule['tn']}, FN={rule['fn']}"
        )
    lines.extend(["", "## Verdict", "", f"`{data['status']}`.", ""])
    if data["status"] == "PERIOD_HORIZON_SUFFICIENT":
        lines.append(
            "Period/horizon features alone provide the second condition after center mediation."
        )
    elif data["status"] == "PERIOD_HORIZON_PLUS_BACKGROUND_SUFFICIENT":
        lines.append(
            "Period/horizon features are necessary but not complete. A background/orbit"
            " condition is required to separate the residual cases."
        )
    else:
        lines.append(
            "Period/horizon is informative but incomplete. The remaining residual likely"
            " depends on background, IC, or alignment features."
        )
    lines.extend(
        [
            "",
            "The key residual is whether `T_local >= 8` or `12/T_local <= 1.5` is",
            "enough. It is not: `rule_109/bg=0011/T=8` is non-positive despite",
            "meeting that horizon threshold, while `bg=0110/T=8` and `bg=1100/T=8`",
            "are positive. Thus the second condition is not period/horizon alone.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = analyze()
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['status']}")


if __name__ == "__main__":
    main()
