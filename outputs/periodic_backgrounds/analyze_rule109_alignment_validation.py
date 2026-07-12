#!/usr/bin/env python3
"""Fase 60: validate the Fase 59 IC-alignment discriminator on all rule_109 cases.

This script uses the existing Fase 59 descriptor table, which already contains
the 17 rule_109 cases from the Fase 55 census. It runs no ECA or ANF simulation.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
INPUT_JSON = ROOT / "outputs" / "periodic_backgrounds" / "rule109_t8_alignment_results.json"
RESULTS_JSON = ROOT / "outputs" / "periodic_backgrounds" / "rule109_alignment_validation_results.json"
REPORT_MD = ROOT / "outputs" / "periodic_backgrounds" / "rule109_alignment_validation_report.md"

POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}
DESCRIPTORS = [
    "ic_span",
    "ic_active_bits",
    "ic_active_offsets_mod4",
    "ic_support_size",
    "bg_phase_in_0011_orbit",
    "bg_at_ic_ones",
    "defect_support_size",
    "defect_phase_offset",
    "defect_span",
]
LOOKUP_LIKE_DESCRIPTORS = {"ic_active_bits"}


def normalize(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(normalize(v) for v in value)
    if isinstance(value, dict):
        return tuple(sorted((k, normalize(v)) for k, v in value.items()))
    return value


def format_value(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, tuple):
        return "(" + ", ".join(format_value(v) for v in value) + ")"
    return str(value)


def confusion(rows: list[dict[str, Any]], predicate) -> dict[str, int | float]:
    tp = fp = tn = fn = 0
    for row in rows:
        predicted = bool(predicate(row))
        actual = bool(row["positive"])
        if predicted and actual:
            tp += 1
        elif predicted and not actual:
            fp += 1
        elif not predicted and actual:
            fn += 1
        else:
            tn += 1
    total = tp + fp + tn + fn
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "recall": tp / (tp + fn) if (tp + fn) else 0.0,
        "precision": tp / (tp + fp) if (tp + fp) else 0.0,
    }


def evaluate_descriptor(rows: list[dict[str, Any]], key: str) -> dict[str, Any]:
    by_value: dict[Any, Counter] = defaultdict(Counter)
    for row in rows:
        value = normalize(row.get(key))
        label = "positive" if row["positive"] else "non_positive"
        by_value[value][label] += 1

    positive_values = {
        normalize(row.get(key))
        for row in rows
        if row["positive"]
    }
    non_positive_values = {
        normalize(row.get(key))
        for row in rows
        if not row["positive"]
    }
    overlap = positive_values & non_positive_values

    category_rule = confusion(rows, lambda row: normalize(row.get(key)) in positive_values)
    result: dict[str, Any] = {
        "descriptor": key,
        "positive_values": sorted(format_value(v) for v in positive_values),
        "non_positive_values": sorted(format_value(v) for v in non_positive_values),
        "overlap_values": sorted(format_value(v) for v in overlap),
        "perfect_set_rule": not overlap,
        "positive_value_rule": category_rule,
        "value_counts": {
            format_value(value): dict(counter)
            for value, counter in sorted(by_value.items(), key=lambda item: format_value(item[0]))
        },
    }

    if all(isinstance(row.get(key), (int, float)) for row in rows if row.get(key) is not None):
        values = sorted({row[key] for row in rows if row.get(key) is not None})
        threshold_rules = []
        for threshold in values:
            threshold_rules.append({
                "rule": f"{key} <= {threshold}",
                **confusion(rows, lambda row, t=threshold: row.get(key) is not None and row[key] <= t),
            })
            threshold_rules.append({
                "rule": f"{key} >= {threshold}",
                **confusion(rows, lambda row, t=threshold: row.get(key) is not None and row[key] >= t),
            })
        result["best_threshold_rules"] = sorted(
            threshold_rules,
            key=lambda item: (item["accuracy"], item["recall"], item["precision"]),
            reverse=True,
        )[:5]
    return result


def main() -> None:
    data = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    rows = data["all_rule109_context"]
    for row in rows:
        row["positive"] = row["category"] in POSITIVE_CATEGORIES

    descriptor_results = [evaluate_descriptor(rows, key) for key in DESCRIPTORS]
    perfect = [item["descriptor"] for item in descriptor_results if item["perfect_set_rule"]]
    compact_perfect = [
        item["descriptor"]
        for item in descriptor_results
        if item["perfect_set_rule"] and item["descriptor"] not in LOOKUP_LIKE_DESCRIPTORS
    ]

    f59_rule = confusion(
        rows,
        lambda row: row["ic_span"] == 2 and tuple(row["ic_active_offsets_mod4"]) == (1, 2),
    )
    f59_t8_rule = confusion(
        [row for row in rows if row["T_local"] == 8],
        lambda row: row["ic_span"] == 2 and tuple(row["ic_active_offsets_mod4"]) == (1, 2),
    )

    if compact_perfect:
        status = "ALIGNMENT_COMPACT_GLOBAL_DISCRIMINANT_FOUND"
    elif perfect:
        status = "ALIGNMENT_LOOKUP_ONLY"
    elif f59_t8_rule["tp"] == 2 and f59_t8_rule["fp"] == 0 and f59_t8_rule["fn"] == 0:
        status = "ALIGNMENT_T8_LOCAL_ONLY"
    else:
        status = "ALIGNMENT_NOT_VALIDATED"

    output = {
        "source": INPUT_JSON.name,
        "case_count": len(rows),
        "positive_count": sum(1 for row in rows if row["positive"]),
        "non_positive_count": sum(1 for row in rows if not row["positive"]),
        "status": status,
        "descriptor_results": descriptor_results,
        "perfect_descriptors": perfect,
        "compact_perfect_descriptors": compact_perfect,
        "lookup_like_descriptors": sorted(LOOKUP_LIKE_DESCRIPTORS),
        "f59_rule_all_rule109": f59_rule,
        "f59_rule_t8_only": f59_t8_rule,
        "methodological_limit": (
            "The validation is restricted to the 17 rule_109 cases already present "
            "in the Fase 55 census. It does not establish a universal ECA law."
        ),
    }
    RESULTS_JSON.write_text(json.dumps(output, indent=2, sort_keys=True), encoding="utf-8")
    write_report(output, rows)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {status}")


def write_report(data: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines: list[str] = [
        "# Fase 60: rule_109 Alignment Discriminator Validation",
        "",
        "## Question",
        "",
        "Does the Fase 59 `rule_109/T=8` IC-placement discriminator generalize",
        "to all 17 `rule_109` cases in the Fase 55 census?",
        "",
        "This validation uses existing descriptor data only. It runs no new ECA",
        "or ANF simulation.",
        "",
        "## Dataset",
        "",
        f"- Rule_109 cases: {data['case_count']}",
        f"- Positive cases: {data['positive_count']}",
        f"- Non-positive cases: {data['non_positive_count']}",
        "",
        "| bg | T | category | word | ic_span | ic_offsets_mod4 | positive |",
        "| --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['background']}` | {row['T_local']} | `{row['category']}` | "
            f"`{row['word']}` | {row['ic_span']} | "
            f"`{tuple(row['ic_active_offsets_mod4'])}` | {str(row['positive']).lower()} |"
        )

    lines.extend([
        "",
        "## Fase 59 Rule Re-test",
        "",
        "Fase 59 found the exact local rule for the three T=8 cases:",
        "",
        "`ic_span == 2` and `ic_active_offsets_mod4 == (1, 2)`.",
        "",
        "On T=8 only:",
        (
            f"- TP={data['f59_rule_t8_only']['tp']}, FP={data['f59_rule_t8_only']['fp']}, "
            f"TN={data['f59_rule_t8_only']['tn']}, FN={data['f59_rule_t8_only']['fn']}, "
            f"accuracy={data['f59_rule_t8_only']['accuracy']:.3f}"
        ),
        "",
        "On all 17 rule_109 cases:",
        (
            f"- TP={data['f59_rule_all_rule109']['tp']}, FP={data['f59_rule_all_rule109']['fp']}, "
            f"TN={data['f59_rule_all_rule109']['tn']}, FN={data['f59_rule_all_rule109']['fn']}, "
            f"accuracy={data['f59_rule_all_rule109']['accuracy']:.3f}"
        ),
        "",
        "## Descriptor Validation",
        "",
    ])

    for item in data["descriptor_results"]:
        lines.append(f"### `{item['descriptor']}`")
        lines.append("")
        lines.append(f"- Perfect set rule: `{str(item['perfect_set_rule']).lower()}`")
        lines.append(f"- Positive values: {', '.join('`' + v + '`' for v in item['positive_values'])}")
        lines.append(f"- Overlap values: {', '.join('`' + v + '`' for v in item['overlap_values']) or '`none`'}")
        rule = item["positive_value_rule"]
        lines.append(
            f"- Predict-positive-if-value-seen-in-positive: TP={rule['tp']}, FP={rule['fp']}, "
            f"TN={rule['tn']}, FN={rule['fn']}, accuracy={rule['accuracy']:.3f}"
        )
        if "best_threshold_rules" in item:
            best = item["best_threshold_rules"][0]
            lines.append(
                f"- Best threshold: `{best['rule']}` -> TP={best['tp']}, FP={best['fp']}, "
                f"TN={best['tn']}, FN={best['fn']}, accuracy={best['accuracy']:.3f}"
            )
        lines.append("")

    lines.extend([
        "## Verdict",
        "",
        f"`{data['status']}`.",
        "",
        f"- Perfect descriptors: {', '.join('`' + v + '`' for v in data['perfect_descriptors']) or '`none`'}",
        f"- Compact perfect descriptors: {', '.join('`' + v + '`' for v in data['compact_perfect_descriptors']) or '`none`'}",
        "",
        "The exact IC-active-bit pattern separates the 17 cases, but this is a",
        "lookup-like descriptor tied to the selected IC word for each catalog",
        "group. It is useful as an audit result, but it is not yet a compact",
        "causal rule.",
        "",
        "The Fase 59 IC-placement discriminator is exact for the three T=8 cases,",
        "but it does not generalize to all 17 `rule_109` cases. In particular,",
        "positive and non-positive cases share `ic_span` values 1, 2, and 6.",
        "",
        "Therefore coarse IC placement is a local T=8 discriminator, not a",
        "standalone global causal condition for the rule_109 gradient.",
        "",
        "## Methodological Limit",
        "",
        f"- {data['methodological_limit']}",
        "",
    ])
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
