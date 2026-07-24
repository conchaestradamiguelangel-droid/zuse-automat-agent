#!/usr/bin/env python3
"""Fase 70: dynamic-subtype audit for positive rule_109 witnesses.

Fase 69 found a high-precision spatial-transition signal that captures four
of five positive rule_109 witnesses. The missed positive is unusual: its
aligned defect shape is static after burn-in. This phase asks whether the
positive class is dynamically homogeneous or whether it contains at least two
subtypes.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
SOURCE_JSON = OUT_DIR / "rule109_snapshot_transition_results.json"
RESULTS_JSON = OUT_DIR / "rule109_positive_subtype_results.json"
REPORT_MD = OUT_DIR / "rule109_positive_subtype_report.md"

DYNAMIC_POSITIVE_MIN_UNIQUE_TRANSITIONS = 8


def load_phase69() -> dict[str, Any]:
    return json.loads(SOURCE_JSON.read_text(encoding="utf-8"))


def subtype_for(row: dict[str, Any]) -> str:
    if not row["positive"]:
        return "NON_POSITIVE"
    if (
        row["period_center_shape"] == 1
        and row["unique_center_transitions"] == 1
        and row["mean_center_step_diff"] == 0.0
    ):
        return "STATIC_POSITIVE"
    if row["positive_only_center_transition_count"] >= DYNAMIC_POSITIVE_MIN_UNIQUE_TRANSITIONS:
        return "DYNAMIC_POSITIVE"
    return "UNCLASSIFIED_POSITIVE"


def transition_overlap(rows: list[dict[str, Any]], target: dict[str, Any]) -> list[dict[str, Any]]:
    target_tokens = set(target["center_transition_tokens"])
    overlaps: list[dict[str, Any]] = []
    for row in rows:
        if row["label"] == target["label"]:
            continue
        shared = sorted(target_tokens & set(row["center_transition_tokens"]))
        if shared:
            overlaps.append({
                "label": row["label"],
                "positive": row["positive"],
                "category": row["category"],
                "period_center_shape": row["period_center_shape"],
                "mean_center_step_diff": row["mean_center_step_diff"],
                "shared_center_transitions": shared,
            })
    return overlaps


def build_results(data: dict[str, Any]) -> dict[str, Any]:
    rows = data["rows"]
    enriched: list[dict[str, Any]] = []
    subtype_counts: dict[str, int] = defaultdict(int)
    for row in rows:
        subtype = subtype_for(row)
        subtype_counts[subtype] += 1
        enriched.append({
            "label": row["label"],
            "background": row["background"],
            "T_local": row["T_local"],
            "word": row["word"],
            "category": row["category"],
            "positive": row["positive"],
            "subtype": subtype,
            "period_center_shape": row["period_center_shape"],
            "unique_center_transitions": row["unique_center_transitions"],
            "positive_only_center_transition_count": row["positive_only_center_transition_count"],
            "mean_center_step_diff": row["mean_center_step_diff"],
            "max_center_step_diff": row["max_center_step_diff"],
            "tail_size_values": sorted(set(row["tail_sizes"])),
            "tail_span_values": sorted(set(row["tail_spans"])),
        })

    positives = [row for row in rows if row["positive"]]
    static_positives = [row for row in positives if subtype_for(row) == "STATIC_POSITIVE"]
    dynamic_positives = [row for row in positives if subtype_for(row) == "DYNAMIC_POSITIVE"]
    unclassified_positives = [row for row in positives if subtype_for(row) == "UNCLASSIFIED_POSITIVE"]

    static_overlap = []
    for row in static_positives:
        static_overlap.append({
            "label": row["label"],
            "overlaps": transition_overlap(rows, row),
        })

    dynamic_rows = [
        row for row in enriched
        if row["positive_only_center_transition_count"] >= DYNAMIC_POSITIVE_MIN_UNIQUE_TRANSITIONS
    ]
    static_signature_rows = [
        row for row in enriched
        if (
            row["period_center_shape"] == 1
            and row["unique_center_transitions"] == 1
            and row["mean_center_step_diff"] == 0.0
        )
    ]

    if len(dynamic_positives) == 4 and len(static_positives) == 1 and not unclassified_positives:
        status = "POSITIVE_DYNAMIC_SUBTYPES_CONFIRMED"
        interpretation = (
            "The five positive rule_109 witnesses are not dynamically homogeneous: "
            "four are transition-rich positives and one is a static/degenerate positive."
        )
    elif static_positives or dynamic_positives:
        status = "POSITIVE_DYNAMIC_SUBTYPES_PARTIAL"
        interpretation = "The positive set shows subtype structure, but at least one positive remains unclassified."
    else:
        status = "POSITIVE_DYNAMIC_SUBTYPES_NOT_CONFIRMED"
        interpretation = "The positive set does not split cleanly under the Phase 69 transition descriptors."

    return {
        "phase": 70,
        "source": SOURCE_JSON.name,
        "dynamic_positive_min_unique_transitions": DYNAMIC_POSITIVE_MIN_UNIQUE_TRANSITIONS,
        "subtype_counts": dict(sorted(subtype_counts.items())),
        "positive_labels_by_subtype": {
            subtype: [row["label"] for row in enriched if row["subtype"] == subtype and row["positive"]]
            for subtype in ["DYNAMIC_POSITIVE", "STATIC_POSITIVE", "UNCLASSIFIED_POSITIVE"]
        },
        "dynamic_rule_rows": dynamic_rows,
        "static_signature_rows": static_signature_rows,
        "static_positive_transition_overlap": static_overlap,
        "rows": enriched,
        "summary": {
            "status": status,
            "positive_count": len(positives),
            "dynamic_positive_count": len(dynamic_positives),
            "static_positive_count": len(static_positives),
            "unclassified_positive_count": len(unclassified_positives),
            "static_signature_total_count": len(static_signature_rows),
            "static_signature_positive_count": sum(1 for row in static_signature_rows if row["positive"]),
            "static_signature_negative_count": sum(1 for row in static_signature_rows if not row["positive"]),
            "interpretation": interpretation,
        },
    }


def fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def build_report(results: dict[str, Any]) -> str:
    summary = results["summary"]
    lines = [
        "# Fase 70: rule_109 Positive Dynamic-Subtype Audit",
        "",
        "## Question",
        "",
        "Are the five positive `rule_109` ANF-gradient witnesses dynamically",
        "homogeneous, or did Fase 69 expose two different positive subtypes?",
        "",
        "This phase reuses the Fase 69 aligned snapshot-transition data. It does",
        "not touch the paper, DOI metadata, tags, or release state.",
        "",
        "## Subtype Rule",
        "",
        "- `DYNAMIC_POSITIVE`: positive case with",
        f"  `positive_only_center_transition_count >= {DYNAMIC_POSITIVE_MIN_UNIQUE_TRANSITIONS}`.",
        "- `STATIC_POSITIVE`: positive case with `period_center_shape=1`,",
        "  `unique_center_transitions=1`, and `mean_center_step_diff=0.0`.",
        "- `UNCLASSIFIED_POSITIVE`: positive case not captured by either rule.",
        "",
        "## Positive Cases",
        "",
        "| case | subtype | period center | unique center transitions | pos-only center transitions | mean center diff | tail sizes | tail spans |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in results["rows"]:
        if not row["positive"]:
            continue
        lines.append(
            f"| `{row['label']}` | `{row['subtype']}` | {fmt(row['period_center_shape'])} | "
            f"{row['unique_center_transitions']} | {row['positive_only_center_transition_count']} | "
            f"{fmt(row['mean_center_step_diff'])} | `{row['tail_size_values']}` | `{row['tail_span_values']}` |"
        )

    lines.extend([
        "",
        "## Subtype Counts",
        "",
    ])
    for key, value in results["subtype_counts"].items():
        lines.append(f"- `{key}`: `{value}`")

    lines.extend([
        "",
        "## Static Signature Control",
        "",
        "The static-positive signature is not by itself a global positive",
        "classifier. It appears in one positive and one non-positive case:",
        "",
        "| case | positive | subtype | period center | mean center diff |",
        "| --- | --- | --- | ---: | ---: |",
    ])
    for row in results["static_signature_rows"]:
        lines.append(
            f"| `{row['label']}` | `{row['positive']}` | `{row['subtype']}` | "
            f"{fmt(row['period_center_shape'])} | {fmt(row['mean_center_step_diff'])} |"
        )

    if results["static_positive_transition_overlap"]:
        lines.extend([
            "",
            "Static-positive transition overlap:",
            "",
        ])
        for item in results["static_positive_transition_overlap"]:
            lines.append(f"- `{item['label']}` overlaps with:")
            for overlap in item["overlaps"]:
                tokens = "; ".join(f"`{token}`" for token in overlap["shared_center_transitions"])
                lines.append(f"  - `{overlap['label']}` via {tokens}")

    lines.extend([
        "",
        "## Dynamic Rule Check",
        "",
        f"The Phase 69 high-precision dynamic rule (`positive_only_center_transition_count >= {DYNAMIC_POSITIVE_MIN_UNIQUE_TRANSITIONS}`)",
        "captures the transition-rich subtype only:",
        "",
        "| case | positive | subtype | pos-only center transitions |",
        "| --- | --- | --- | ---: |",
    ])
    for row in results["dynamic_rule_rows"]:
        lines.append(
            f"| `{row['label']}` | `{row['positive']}` | `{row['subtype']}` | "
            f"{row['positive_only_center_transition_count']} |"
        )

    lines.extend([
        "",
        "## Verdict",
        "",
        f"`{summary['status']}`.",
        "",
        summary["interpretation"],
        "",
        "The missed positive from Fase 69 is not a failure of alignment. It is a",
        "static/degenerate positive whose exact transition token is also present",
        "in a negative case. The dynamic positives and the static positive should",
        "therefore be treated as separate mechanistic subfamilies in later work.",
        "",
        "## Methodological Limit",
        "",
        "- This is a subtype audit over the same 17-case rule_109 catalogue.",
        "- It reuses exact aligned transitions from Fase 69; near-match graph",
        "  structure is still untested.",
        "- The static subtype is not claimed as a causal law. It is a warning that",
        "  `positive` is not dynamically homogeneous.",
        "- No paper or DOI metadata is changed by this phase.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    data = load_phase69()
    results = build_results(data)
    RESULTS_JSON.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(results), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {results['summary']['status']}")


if __name__ == "__main__":
    main()
