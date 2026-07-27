#!/usr/bin/env python3
"""Fase 73: second filter for ANF centrality false positives.

Fase 72 showed that `max_active_monomial_dist == 0` is perfect inside
rule_109 but creates eight false positives in the full Fase 55 census. This
phase tests the cheapest explanation first: the false positives are all short
period / oversampled horizon artefacts, while the five true positives have
T_local >= 8 under the common T_WINDOW=12.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable


OUT_DIR = Path(__file__).resolve().parent
SOURCE_JSON = OUT_DIR / "anf_centrality_global_results.json"
RESULTS_JSON = OUT_DIR / "anf_centrality_horizon_filter_results.json"
REPORT_MD = OUT_DIR / "anf_centrality_horizon_filter_report.md"

COMMON_T_WINDOW = 12
CENTRALITY_METRIC = "max_active_monomial_dist"
POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}


def load_phase72() -> dict[str, Any]:
    return json.loads(SOURCE_JSON.read_text(encoding="utf-8"))


def enrich_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["oversampling_ratio"] = COMMON_T_WINDOW / int(row["T_local"]) if int(row["T_local"]) else None
        item["centrality_candidate"] = (
            row.get(CENTRALITY_METRIC) is not None
            and float(row[CENTRALITY_METRIC]) <= 0.0
        )
        item["horizon_sufficient_T8"] = int(row["T_local"]) >= 8
        item["horizon_ratio_le_1_5"] = item["oversampling_ratio"] is not None and item["oversampling_ratio"] <= 1.5
        item["centrality_and_T8"] = item["centrality_candidate"] and item["horizon_sufficient_T8"]
        item["centrality_and_ratio_le_1_5"] = item["centrality_candidate"] and item["horizon_ratio_le_1_5"]
        enriched.append(item)
    return enriched


def confusion(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    false_pos: list[str] = []
    false_neg: list[str] = []
    for row in rows:
        pred = predicate(row)
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
    total = len(rows)
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "perfect": fp == 0 and fn == 0,
        "false_positive_labels": false_pos,
        "false_negative_labels": false_neg,
    }


def scan_rules(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scans: list[dict[str, Any]] = []
    t_values = sorted({int(row["T_local"]) for row in rows})
    ratio_values = sorted({float(row["oversampling_ratio"]) for row in rows if row["oversampling_ratio"] is not None})
    r2_values = sorted({float(row["r2"]) for row in rows if row.get("r2") is not None})
    dist_count_values = sorted({int(row["distinct_dist_count"]) for row in rows if row.get("distinct_dist_count") is not None})

    for t in t_values:
        scans.append({
            "rule": f"centrality AND T_local >= {t}",
            "family": "centrality_horizon",
            **confusion(rows, lambda row, t=t: row["centrality_candidate"] and int(row["T_local"]) >= t),
        })
        scans.append({
            "rule": f"centrality AND T_local <= {t}",
            "family": "centrality_horizon",
            **confusion(rows, lambda row, t=t: row["centrality_candidate"] and int(row["T_local"]) <= t),
        })
    for ratio in ratio_values:
        scans.append({
            "rule": f"centrality AND oversampling_ratio <= {ratio}",
            "family": "centrality_horizon",
            **confusion(rows, lambda row, ratio=ratio: row["centrality_candidate"] and row["oversampling_ratio"] <= ratio),
        })
        scans.append({
            "rule": f"centrality AND oversampling_ratio >= {ratio}",
            "family": "centrality_horizon",
            **confusion(rows, lambda row, ratio=ratio: row["centrality_candidate"] and row["oversampling_ratio"] >= ratio),
        })
    for r2 in r2_values:
        scans.append({
            "rule": f"centrality AND R2 >= {r2}",
            "family": "centrality_fit",
            **confusion(rows, lambda row, r2=r2: row["centrality_candidate"] and row["r2"] >= r2),
        })
    for count in dist_count_values:
        scans.append({
            "rule": f"centrality AND distinct_dist_count >= {count}",
            "family": "centrality_support",
            **confusion(rows, lambda row, count=count: row["centrality_candidate"] and row["distinct_dist_count"] >= count),
        })

    scans.sort(key=lambda row: (not row["perfect"], row["fp"], -row["tp"], -row["accuracy"], row["fn"], row["rule"]))
    return scans


def category_by_group(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        grouped[str(row[key])][str(row["category"])] += 1
    return {group: dict(counter) for group, counter in sorted(grouped.items())}


def build_results() -> dict[str, Any]:
    phase72 = load_phase72()
    rows = enrich_rows(phase72["rows"])
    centrality_rows = [row for row in rows if row["centrality_candidate"]]
    true_positives = [row for row in centrality_rows if row["positive"]]
    centrality_false_positives = [row for row in centrality_rows if not row["positive"]]
    scans = scan_rules(rows)
    perfect_rules = [row for row in scans if row["perfect"]]
    best_accuracy = max(scans, key=lambda row: (row["accuracy"], row["precision"], row["recall"]))
    centrality_only = confusion(rows, lambda row: row["centrality_candidate"])
    centrality_and_T8 = confusion(rows, lambda row: row["centrality_candidate"] and row["T_local"] >= 8)
    centrality_and_ratio = confusion(rows, lambda row: row["centrality_candidate"] and row["oversampling_ratio"] <= 1.5)

    if centrality_and_T8["perfect"] and centrality_and_ratio["perfect"]:
        status = "CENTRALITY_HORIZON_FILTER_RECAPITULATES_LABEL"
        interpretation = (
            "The horizon split is descriptively exact, but partially circular: "
            "T_local>=8 is already part of the HORIZON_ACCEPTABLE label definition."
        )
    elif perfect_rules:
        status = "CENTRALITY_SECOND_FILTER_FOUND"
        interpretation = "A second scalar filter separates centrality-real positives from centrality-spurious cases."
    elif centrality_and_T8["fp"] == 0 and centrality_and_T8["tp"] > 0:
        status = "CENTRALITY_HORIZON_FILTER_PARTIAL"
        interpretation = "The horizon filter removes false positives but misses at least one positive."
    else:
        status = "CENTRALITY_HORIZON_FILTER_NEGATIVE"
        interpretation = "Horizon/period does not explain the centrality false positives."

    return {
        "phase": 73,
        "source": SOURCE_JSON.name,
        "t_window": COMMON_T_WINDOW,
        "rows": rows,
        "centrality_rows": centrality_rows,
        "centrality_true_positives": true_positives,
        "centrality_false_positives": centrality_false_positives,
        "threshold_scan": scans,
        "summary": {
            "status": status,
            "case_count": len(rows),
            "positive_count": sum(1 for row in rows if row["positive"]),
            "centrality_candidate_count": len(centrality_rows),
            "centrality_false_positive_count": len(centrality_false_positives),
            "centrality_only": centrality_only,
            "centrality_and_T8": centrality_and_T8,
            "centrality_and_ratio_le_1_5": centrality_and_ratio,
            "perfect_rule_count": len(perfect_rules),
            "best_accuracy_rule": best_accuracy,
            "centrality_category_by_rule": category_by_group(centrality_rows, "rule"),
            "interpretation": interpretation,
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


def case_table(rows: list[dict[str, Any]]) -> list[str]:
    lines = [
        "| case | positive | T | ratio | category | R2 | slope | dist classes | max dist |",
        "| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        lines.append(
            f"| `{row['label']}` | `{row['positive']}` | {row['T_local']} | "
            f"{fmt(row['oversampling_ratio'], 3)} | `{row['category']}` | "
            f"{fmt(row['r2'], 6)} | {fmt(row['slope'], 6)} | "
            f"{row['distinct_dist_count']} | {fmt(row['max_active_monomial_dist'], 1)} |"
        )
    return lines


def build_report(data: dict[str, Any]) -> str:
    summary = data["summary"]
    lines = [
        "# Fase 73: ANF Centrality Horizon Filter",
        "",
        "## Question",
        "",
        "Can the eight external false positives from Fase 72 be explained as",
        "short-period / oversampled-horizon artefacts?",
        "",
        "This phase tests the cheap second filter first: combine ANF centrality",
        "(`max_active_monomial_dist=0`) with the same sufficient-horizon threshold",
        "used by the Fase 55 category definition.",
        "",
        "## Centrality Candidates",
        "",
        "These are all cases with `max_active_monomial_dist=0` in the full Fase 55",
        "census.",
        "",
    ]
    lines.extend(case_table(data["centrality_rows"]))
    lines.extend([
        "",
        "## Period/Horizon Split",
        "",
        f"- Centrality only: `{confusion_line(summary['centrality_only'])}`",
        f"- Centrality + `T_local >= 8`: `{confusion_line(summary['centrality_and_T8'])}`",
        f"- Centrality + `12/T_local <= 1.5`: `{confusion_line(summary['centrality_and_ratio_le_1_5'])}`",
        "",
        "The centrality false positives are all short-period cases:",
        "",
    ])
    fp_periods = Counter(row["T_local"] for row in data["centrality_false_positives"])
    for period, count in sorted(fp_periods.items()):
        lines.append(f"- `T_local={period}`: `{count}` false positives")

    lines.extend([
        "",
        "The true positives are all sufficient-horizon cases:",
        "",
    ])
    tp_periods = Counter(row["T_local"] for row in data["centrality_true_positives"])
    for period, count in sorted(tp_periods.items()):
        lines.append(f"- `T_local={period}`: `{count}` true positives")

    best = summary["best_accuracy_rule"]
    lines.extend([
        "",
        "## Threshold Scan",
        "",
        f"- Perfect rules: `{summary['perfect_rule_count']}`.",
        f"- Best accuracy rule: `{best['rule']}` ({confusion_line(best)}).",
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
        f"`{summary['status']}`.",
        "",
        summary["interpretation"],
        "",
        "The Fase 72 centrality false positives are not random failures of the",
        "centrality metric. They are short-period centrality cases: six have",
        "`T_local=3` and two have `T_local=6`. Adding `T_local>=8` removes all",
        "eight false positives while preserving all five observed positives, but",
        "this should not be read as an independent statistical discovery because",
        "`T_local>=8` is exactly the threshold used by `classify_case()` to split",
        "`HORIZON_ACCEPTABLE` from `HORIZON_ARTIFACT` when the common-horizon",
        "ANF fit is comparable to T15.",
        "",
        "## Methodological Limit",
        "",
        "- This is still a validation over the Fase 55 census, not all ECA rules.",
        "- The `T_local>=8` filter is partially circular with the Fase 55 category",
        "  definition and should be treated as a descriptive consistency check.",
        "- All observed positives remain rule_109 cases, so external recall is not",
        "  tested.",
        "- The filter is evaluated at common horizon `T_WINDOW=12`; natural-period",
        "  centrality would be a separate audit.",
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
    print(f"Status: {data['summary']['status']}")


if __name__ == "__main__":
    main()
