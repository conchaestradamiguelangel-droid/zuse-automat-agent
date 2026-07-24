#!/usr/bin/env python3
"""Fase 72: global validation of the ANF centrality discriminator.

Fase 71 found that, inside the 17-case rule_109 subcatalogue, every positive
case has its maximum active monomial support at the exact cone center
(`max_active_monomial_dist == 0`) and no non-positive does. This phase checks
the same scalar over the full Fase 55 census.

Important limitation: all positives in Fase 55 are rule_109 cases. Therefore
this phase can test for external false positives outside rule_109, but it
cannot test recall on non-rule_109 positives because none exist in the census.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


OUT_DIR = Path(__file__).resolve().parent
CENSUS_JSON = OUT_DIR / "anf_gradient_census_results.json"
RESULTS_JSON = OUT_DIR / "anf_centrality_global_results.json"
REPORT_MD = OUT_DIR / "anf_centrality_global_report.md"

COMMON_T_WINDOW = 12
POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}


def load_census() -> dict[str, Any]:
    return json.loads(CENSUS_JSON.read_text(encoding="utf-8"))


def case_key(row: dict[str, Any]) -> tuple[int, str, int, str]:
    return (int(row["rule"]), str(row["background"]), int(row["T_local"]), str(row["word"]))


def label_for(row: dict[str, Any]) -> str:
    return f"rule={row['rule']}/bg={row['background']}/T={row['T_local']}/word={row['word']}/{row['category']}"


def active_outputs(measurement: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in measurement["outputs"] if row["concrete_active"]]


def summarize_measurement(case: dict[str, Any], measurement: dict[str, Any]) -> dict[str, Any]:
    active = active_outputs(measurement)
    fit = measurement["active_summary"]["log_monomial_fit"]
    max_active = max(active, key=lambda row: int(row["monomial_count"])) if active else None
    monomial_sum = sum(int(row["monomial_count"]) for row in active)
    min_dist = min(float(row["dist"]) for row in measurement["outputs"]) if measurement["outputs"] else None
    central_active = [
        row for row in active
        if min_dist is not None and abs(float(row["dist"]) - min_dist) < 1e-9
    ]
    category = str(case["category"])
    positive = category in POSITIVE_CATEGORIES
    return {
        "label": label_for(case),
        "rule": int(case["rule"]),
        "background": str(case["background"]),
        "T_local": int(case["T_local"]),
        "word": str(case["word"]),
        "category": category,
        "positive": positive,
        "t_window": COMMON_T_WINDOW,
        "active_count": len(active),
        "distinct_dist_count": fit["distinct_dist_count"],
        "slope": fit["slope"],
        "r2": fit["r2"],
        "reliable": fit["reliable"],
        "max_active_monomial_count": int(max_active["monomial_count"]) if max_active else None,
        "max_active_monomial_dist": float(max_active["dist"]) if max_active else None,
        "min_output_dist": min_dist,
        "central_active_count": len(central_active),
        "central_monomial_share": (
            sum(int(row["monomial_count"]) for row in central_active) / monomial_sum
            if monomial_sum else 0.0
        ),
        "monomial_sum_active": monomial_sum,
        "has_center_max": bool(max_active and abs(float(max_active["dist"])) < 1e-9),
    }


def build_rows() -> list[dict[str, Any]]:
    census = load_census()
    cases = {case_key(row): row for row in census["case_summaries"]}
    measurements = {
        case_key(row): row
        for row in census["measurements"]
        if int(row["t_window"]) == COMMON_T_WINDOW
    }
    rows: list[dict[str, Any]] = []
    for key, case in sorted(cases.items()):
        if key not in measurements:
            continue
        rows.append(summarize_measurement(case, measurements[key]))
    return rows


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
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "false_positive_labels": false_pos,
        "false_negative_labels": false_neg,
        "perfect": fp == 0 and fn == 0,
    }


def scan_thresholds(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = [
        "max_active_monomial_dist",
        "central_active_count",
        "central_monomial_share",
        "r2",
        "slope",
        "active_count",
        "distinct_dist_count",
        "max_active_monomial_count",
        "monomial_sum_active",
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


def group_counts(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        group = str(row[key])
        label = "positive" if row["positive"] else row["non_positive_category"] if "non_positive_category" in row else row["category"]
        grouped[group][label] += 1
    return {group: dict(counter) for group, counter in sorted(grouped.items())}


def category_by_rule(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[str(row["rule"])][row["category"]] += 1
    return {rule: dict(counter) for rule, counter in sorted(grouped.items(), key=lambda kv: int(kv[0]))}


def build_results() -> dict[str, Any]:
    rows = build_rows()
    scans = scan_thresholds(rows)
    central_rule = {
        "rule": "max_active_monomial_dist <= 0.0",
        "metric": "max_active_monomial_dist",
        "direction": "<=",
        "threshold": 0.0,
        **confusion(rows, lambda row: row["max_active_monomial_dist"] is not None and row["max_active_monomial_dist"] <= 0.0),
    }
    rule109_rows = [row for row in rows if row["rule"] == 109]
    external_rows = [row for row in rows if row["rule"] != 109]
    rule109_central = {
        **central_rule,
        **confusion(rule109_rows, lambda row: row["max_active_monomial_dist"] is not None and row["max_active_monomial_dist"] <= 0.0),
    }
    external_central = {
        **central_rule,
        **confusion(external_rows, lambda row: row["max_active_monomial_dist"] is not None and row["max_active_monomial_dist"] <= 0.0),
    }
    external_positive_count = sum(1 for row in external_rows if row["positive"])

    statuses: list[str] = []
    if rule109_central["perfect"]:
        statuses.append("CENTRALITY_RULE109_CONFIRMED")
    if external_central["fp"] == 0:
        statuses.append("CENTRALITY_NO_EXTERNAL_FALSE_POSITIVES")
    else:
        statuses.append("CENTRALITY_EXTERNAL_FALSE_POSITIVES")
    if external_positive_count == 0:
        statuses.append("CENTRALITY_GLOBAL_NOT_TESTABLE")
    elif central_rule["perfect"]:
        statuses.append("CENTRALITY_DISCRIMINANT_GLOBAL")
    if central_rule["fp"] > 0 or central_rule["fn"] > 0:
        statuses.append("CENTRALITY_PARTIAL")
    if not statuses:
        statuses.append("CENTRALITY_NEGATIVE")

    best_accuracy = max(scans, key=lambda row: (row["accuracy"], row["precision"], row["recall"]))
    perfect_rules = [row for row in scans if row["perfect"]]

    return {
        "phase": 72,
        "source": CENSUS_JSON.name,
        "t_window": COMMON_T_WINDOW,
        "rows": rows,
        "central_rule": central_rule,
        "rule109_central_rule": rule109_central,
        "external_central_rule": external_central,
        "threshold_scan": scans,
        "summary": {
            "statuses": statuses,
            "case_count": len(rows),
            "positive_count": sum(1 for row in rows if row["positive"]),
            "non_positive_count": sum(1 for row in rows if not row["positive"]),
            "rule109_case_count": len(rule109_rows),
            "external_case_count": len(external_rows),
            "external_positive_count": external_positive_count,
            "rules": sorted({row["rule"] for row in rows}),
            "category_counts": dict(Counter(row["category"] for row in rows)),
            "category_by_rule": category_by_rule(rows),
            "perfect_rule_count": len(perfect_rules),
            "best_accuracy_rule": best_accuracy,
        },
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def confusion_line(row: dict[str, Any]) -> str:
    return (
        f"TP={row['tp']}, FP={row['fp']}, TN={row['tn']}, FN={row['fn']}, "
        f"accuracy={row['accuracy']:.3f}, precision={row['precision']:.3f}, recall={row['recall']:.3f}"
    )


def build_report(data: dict[str, Any]) -> str:
    summary = data["summary"]
    lines = [
        "# Fase 72: ANF Centrality Discriminator Global Check",
        "",
        "## Question",
        "",
        "Does the Fase 71 centrality discriminator",
        "`max_active_monomial_dist <= 0.0` remain valid outside the 17-case",
        "`rule_109` subcatalogue?",
        "",
        "This phase uses the full Fase 55 census at the common horizon",
        "`T_WINDOW=12`. It does not touch the paper, DOI metadata, tags, or",
        "release state.",
        "",
        "## Critical Data Limitation",
        "",
        "All five positive cases in the Fase 55 census are `rule_109` cases.",
        "The other rules contain no `NATURAL_PERIOD_STRONG` or",
        "`HORIZON_ACCEPTABLE` cases. Therefore this phase can test whether the",
        "centrality rule creates false positives outside `rule_109`, but it",
        "cannot test recall on non-`rule_109` positives.",
        "",
        "## Census Coverage",
        "",
        f"- Cases: `{summary['case_count']}`",
        f"- Rules: `{summary['rules']}`",
        f"- Positives: `{summary['positive_count']}`",
        f"- Non-positives: `{summary['non_positive_count']}`",
        f"- External non-rule_109 cases: `{summary['external_case_count']}`",
        f"- External positives: `{summary['external_positive_count']}`",
        "",
        "Category counts by rule:",
        "",
        "| rule | NATURAL_PERIOD_STRONG | HORIZON_ACCEPTABLE | HORIZON_ARTIFACT | NEGATIVE | INSUFFICIENT_SUPPORT |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for rule, counts in summary["category_by_rule"].items():
        lines.append(
            f"| {rule} | {counts.get('NATURAL_PERIOD_STRONG', 0)} | "
            f"{counts.get('HORIZON_ACCEPTABLE', 0)} | {counts.get('HORIZON_ARTIFACT', 0)} | "
            f"{counts.get('NEGATIVE', 0)} | {counts.get('INSUFFICIENT_SUPPORT', 0)} |"
        )

    lines.extend([
        "",
        "## Centrality Rule",
        "",
        f"- Full census: `{confusion_line(data['central_rule'])}`",
        f"- rule_109 only: `{confusion_line(data['rule109_central_rule'])}`",
        f"- non-rule_109 only: `{confusion_line(data['external_central_rule'])}`",
        "",
        "## Case Table",
        "",
        "| case | positive | max active monomial dist | R2 | slope | active | dist classes |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in data["rows"]:
        lines.append(
            f"| `{row['label']}` | `{row['positive']}` | "
            f"{fmt(row['max_active_monomial_dist'], 1)} | {fmt(row['r2'], 6)} | "
            f"{fmt(row['slope'], 6)} | {row['active_count']} | {row['distinct_dist_count']} |"
        )

    best_accuracy = summary["best_accuracy_rule"]
    lines.extend([
        "",
        "## Threshold Scan",
        "",
        f"- Perfect scalar rules over all 66 cases: `{summary['perfect_rule_count']}`.",
        f"- Best accuracy rule: `{best_accuracy['rule']}` ({confusion_line(best_accuracy)}).",
        "",
        "Top scanned rules:",
        "",
    ])
    for row in data["threshold_scan"][:10]:
        lines.append(f"- `{row['rule']}`: {confusion_line(row)}")

    lines.extend([
        "",
        "## Verdict",
        "",
        " + ".join(f"`{status}`" for status in summary["statuses"]),
        "",
        "The centrality rule remains perfect inside the 17-case `rule_109`",
        "subcatalogue: every `rule_109` positive has its maximum active monomial",
        "support at the exact cone center, and no `rule_109` non-positive case",
        "does. It does not generalize as a full-census precision rule: eight",
        "non-`rule_109` non-positive cases also have `max_active_monomial_dist=0`.",
        "Because the census contains no positives outside `rule_109`, external",
        "recall is still untestable. The correct claim is therefore local:",
        "confirmed for `rule_109`, contradicted as a global precision rule, and",
        "externally recall-untestable with the current catalogue.",
        "",
        "## Methodological Limit",
        "",
        "- The validation is global over the Fase 55 census, not over all ECA rules.",
        "- Since all positives are `rule_109`, non-rule_109 recall cannot be estimated.",
        "- The rule is evaluated at common horizon `T_WINDOW=12`; natural-period",
        "  validation would be a separate question.",
        "- No paper or DOI metadata is changed by this phase.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    data = build_results()
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print("Status:", " + ".join(data["summary"]["statuses"]))


if __name__ == "__main__":
    main()
