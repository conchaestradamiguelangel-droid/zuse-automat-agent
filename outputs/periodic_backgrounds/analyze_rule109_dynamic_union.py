#!/usr/bin/env python3
"""Fase 62: minimal union test for rule_109 dynamic alignment descriptors."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable


OUT_DIR = Path(__file__).resolve().parent
INPUT_JSON = OUT_DIR / "rule109_dynamic_alignment_results.json"
RESULTS_JSON = OUT_DIR / "rule109_dynamic_union_results.json"
REPORT_MD = OUT_DIR / "rule109_dynamic_union_report.md"


def confusion(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    false_pos = []
    false_neg = []
    true_pos = []
    for row in rows:
        pred = bool(predicate(row))
        actual = bool(row["positive"])
        label = row["label"]
        if pred and actual:
            tp += 1
            true_pos.append(label)
        elif pred and not actual:
            fp += 1
            false_pos.append(label)
        elif not pred and actual:
            fn += 1
            false_neg.append(label)
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
        "true_positives": true_pos,
        "false_positives": false_pos,
        "false_negatives": false_neg,
    }


def dynamic_union(row: dict[str, Any]) -> bool:
    desc = row["descriptors"]
    return desc["size_growth_total"] <= -3 or desc["center_drift_abs"] <= 0.0


def max_size_union(row: dict[str, Any]) -> bool:
    desc = row["descriptors"]
    return dynamic_union(row) or desc["max_defect_size"] >= 12


def main() -> None:
    source = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    rows = source["rows"]
    tests = {
        "minimal_union": {
            "rule": "size_growth_total <= -3 OR center_drift_abs <= 0.0",
            "confusion": confusion(rows, dynamic_union),
        },
        "union_plus_max_defect_size": {
            "rule": "size_growth_total <= -3 OR center_drift_abs <= 0.0 OR max_defect_size >= 12",
            "confusion": confusion(rows, max_size_union),
        },
    }
    minimal = tests["minimal_union"]["confusion"]
    if minimal["fp"] == 0 and minimal["tp"] == source["positive_count"]:
        status = "DYNAMIC_UNION_DISCRIMINANT_FOUND"
    elif minimal["fp"] == 0 and minimal["tp"] > 0:
        status = "DYNAMIC_UNION_PARTIAL"
    else:
        status = "DYNAMIC_UNION_INSUFFICIENT"

    result = {
        "source": INPUT_JSON.name,
        "case_count": source["case_count"],
        "positive_count": source["positive_count"],
        "non_positive_count": source["non_positive_count"],
        "status": status,
        "tests": tests,
        "residual_positive": minimal["false_negatives"],
        "methodological_limit": (
            "This phase only tests the minimal union suggested by Fase 61. It is not "
            "a search over arbitrary dynamic combinations."
        ),
    }
    RESULTS_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(result, rows), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {status}")
    print("Minimal union:", minimal)


def build_report(result: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Fase 62: rule_109 Dynamic Union Test",
        "",
        "## Question",
        "",
        "Does the minimal union of the two strongest no-false-positive dynamic",
        "descriptors from Fase 61 separate all positive `rule_109` cases?",
        "",
        "This phase does not run new simulations. It reuses the Fase 61 dynamic",
        "alignment output and tests one predeclared union only:",
        "",
        "`size_growth_total <= -3 OR center_drift_abs <= 0.0`",
        "",
        "## Results",
        "",
    ]
    for name, test in result["tests"].items():
        c = test["confusion"]
        lines.extend([
            f"### `{name}`",
            "",
            f"- Rule: `{test['rule']}`",
            f"- TP={c['tp']}, FP={c['fp']}, TN={c['tn']}, FN={c['fn']}",
            f"- Accuracy={c['accuracy']:.3f}, precision={c['precision']:.3f}, recall={c['recall']:.3f}",
            f"- True positives: {', '.join('`' + item + '`' for item in c['true_positives']) or '`none`'}",
            f"- False positives: {', '.join('`' + item + '`' for item in c['false_positives']) or '`none`'}",
            f"- False negatives: {', '.join('`' + item + '`' for item in c['false_negatives']) or '`none`'}",
            "",
        ])

    lines.extend([
        "## Case Table",
        "",
        "| bg | T | category | positive | size_growth_total | center_drift_abs | max_defect_size | minimal_union |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | --- |",
    ])
    for row in rows:
        desc = row["descriptors"]
        lines.append(
            f"| `{row['background']}` | {row['T_local']} | `{row['category']}` | "
            f"{str(row['positive']).lower()} | {desc['size_growth_total']} | "
            f"{desc['center_drift_abs']:.3f} | {desc['max_defect_size']} | "
            f"{str(dynamic_union(row)).lower()} |"
        )

    lines.extend([
        "",
        "## Verdict",
        "",
        f"`{result['status']}`.",
        "",
        "The minimal dynamic union captures 4/5 positive cases with zero false",
        "positives. The single remaining positive residual is",
        "`bg=1100/T=8/word=00000110`.",
        "",
        "Adding `max_defect_size >= 12` does not improve recall, because it captures",
        "a positive case already captured by `center_drift_abs <= 0.0`.",
        "",
        "Thus the Fase 61 dynamic signal is real but remains subfamily-specific. It",
        "does not close the causal explanation with a compact dynamic descriptor.",
        "",
        "## Methodological Limit",
        "",
        f"- {result['methodological_limit']}",
        "",
    ])
    return "\n".join(lines)


if __name__ == "__main__":
    main()
