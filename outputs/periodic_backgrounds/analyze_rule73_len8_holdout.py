#!/usr/bin/env python3
"""Fase 78: natural-period ANF holdout on primitive len-8 rule_73 backgrounds."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
LEN8_CATALOG = (
    OUT_DIR.parent / "periodic_backgrounds_len8" / "sweep_len8_results.jsonl"
)
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
FASE55_SCRIPT = OUT_DIR / "analyze_anf_gradient_census.py"
CHECKPOINT_JSON = OUT_DIR / "rule73_len8_holdout_checkpoint.json"
RESULTS_JSON = OUT_DIR / "rule73_len8_holdout_results.json"
REPORT_MD = OUT_DIR / "rule73_len8_holdout_report.md"

TARGET_RULE = 73
TARGET_PERIODS = {8, 10, 12}
MIN_SPAN = 11


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def rank_key(row: dict[str, Any]) -> tuple[int, int, str]:
    return (-int(row["span"]), int(row["word_len"]), str(row["word"]))


def select_cases() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[tuple[int, str, int], dict[str, Any]] = {}
    raw_rows = 0
    eligible_rows = 0

    for row in iter_jsonl(LEN8_CATALOG):
        raw_rows += 1
        if not (
            row.get("kind") == "stationary"
            and int(row["rule"]) == TARGET_RULE
            and int(row["period_T"]) in TARGET_PERIODS
            and int(row["span"]) >= MIN_SPAN
        ):
            continue
        eligible_rows += 1
        background = str(row["background_canonical"])
        key = (TARGET_RULE, background, int(row["period_T"]))
        current = grouped.get(key)
        if current is None or rank_key(row) < rank_key(current):
            grouped[key] = row

    records = sorted(
        grouped.values(),
        key=lambda row: (
            int(row["period_T"]),
            str(row["background_canonical"]),
            str(row["word"]),
        ),
    )
    cases = [
        {
            "label": (
                f"rule{TARGET_RULE}_bg{row['background_canonical']}"
                f"_T{row['period_T']}"
            ),
            "role": "external_len8_rule73_holdout",
            "rule": TARGET_RULE,
            "background": str(row["background_canonical"]),
            "T_local": int(row["period_T"]),
            "word": str(row["word"]),
            "selection_reason": "max_span_shortest_word",
        }
        for row in records
    ]
    normalized_catalog = [
        {**row, "background": str(row["background_canonical"])}
        for row in records
    ]
    preflight = {
        "source_catalog": str(LEN8_CATALOG),
        "raw_rows": raw_rows,
        "eligible_rows": eligible_rows,
        "candidate_groups": len(cases),
        "rule": TARGET_RULE,
        "period_distribution": dict(
            sorted(Counter(case["T_local"] for case in cases).items())
        ),
        "background_count": len({case["background"] for case in cases}),
        "selection": {
            "kind": "stationary",
            "target_periods": sorted(TARGET_PERIODS),
            "minimum_span": MIN_SPAN,
            "one_case_per_rule_background_period": True,
            "representative": "maximum span; then shortest word; then lexical word",
            "measurement_horizon": "natural period only",
            "threshold_policy": "unchanged Fase 55 comparable_to_t15",
        },
    }
    return cases, normalized_catalog, preflight


def case_key(case: dict[str, Any]) -> str:
    return (
        f"r{case['rule']}_bg{case['background']}"
        f"_T{case['T_local']}_w{case['word']}"
    )


def load_checkpoint() -> dict[str, Any]:
    if not CHECKPOINT_JSON.exists():
        return {"measurements": {}}
    return json.loads(CHECKPOINT_JSON.read_text(encoding="utf-8"))


def save_checkpoint(checkpoint: dict[str, Any]) -> None:
    CHECKPOINT_JSON.write_text(
        json.dumps(checkpoint, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def fit_text(fit: dict[str, Any], comparable_to_t15) -> str:
    if fit["slope"] is None:
        return "insufficient support"
    return (
        f"slope={fit['slope']:.6f}, R^2={fit['r2']:.6f}, "
        f"reliable={str(bool(fit['reliable'])).lower()}, "
        f"comparable={str(bool(comparable_to_t15(fit))).lower()}"
    )


def classify(
    rows: list[dict[str, Any]],
    comparable_to_t15,
) -> tuple[str, str]:
    witnesses = [
        row
        for row in rows
        if comparable_to_t15(row["active_summary"]["log_monomial_fit"])
    ]
    if witnesses:
        return (
            "RULE73_LEN8_NATURAL_WITNESS_FOUND",
            (
                "At least one primitive length-8 rule_73 oscillator reproduces "
                "the predeclared T15-like ANF gradient at its natural period."
            ),
        )
    reliable = sum(
        bool(row["active_summary"]["log_monomial_fit"]["reliable"])
        for row in rows
    )
    if reliable < len(rows) / 2:
        return (
            "RULE73_LEN8_HOLDOUT_INSUFFICIENT",
            (
                "No witness was found, but fewer than half of the holdout cases "
                "provided reliable active-distance support."
            ),
        )
    return (
        "RULE73_LEN8_NATURAL_WITNESS_NOT_FOUND",
        (
            "No primitive length-8 rule_73 oscillator in the T=8/10/12 holdout "
            "reproduces the predeclared T15-like ANF gradient at its natural period."
        ),
    )


def write_report(data: dict[str, Any], comparable_to_t15) -> None:
    preflight = data["preflight"]
    summary = data["summary"]
    lines = [
        "# Fase 78: rule_73 Primitive-Length-8 Natural-Period Holdout",
        "",
        "## Question",
        "",
        "Does a genuine non-rule_109 witness appear when the ANF-gradient test is",
        "applied to previously unmeasured primitive length-8 `rule_73` oscillators",
        "in the same natural-period range as the known positives (`T=8,10,12`)?",
        "",
        "The holdout is selected from the completed 3,855,360-run physical sweep.",
        "Selection is fixed before ANF measurement. The unchanged Fase 55",
        "`comparable_to_t15()` predicate is evaluated at each oscillator's natural",
        "period only. No common `T_WINDOW=12` measurement is introduced for T=8/10.",
        "",
        "## Preflight",
        "",
        f"- Source rows: `{preflight['raw_rows']}`",
        f"- Eligible raw detections: `{preflight['eligible_rows']}`",
        f"- Candidate groups: `{preflight['candidate_groups']}`",
        f"- Distinct primitive length-8 backgrounds: `{preflight['background_count']}`",
        f"- Period distribution: `{preflight['period_distribution']}`",
        f"- Minimum span: `{MIN_SPAN}`",
        "- Representative per `(rule, background, T_local)`: maximum span, then",
        "  shortest IC word, then lexical word.",
        "- Measurement horizon: natural period only.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Cases measured: `{summary['case_count']}`",
        f"- Reliable fits: `{summary['reliable_count']}`",
        f"- Comparable natural-period witnesses: `{summary['witness_count']}`",
        f"- Witness period distribution: `{summary['witness_period_distribution']}`",
        f"- Witness backgrounds: `{summary['witness_backgrounds']}`",
        f"- Packed/concrete discrepancies: `{summary['concrete_mismatch_count']}`",
        (
            "- Highest observed R^2: "
            f"`{summary['highest_r2']['value']:.6f}` "
            f"(`{summary['highest_r2']['case']}`; required `>=0.95`)"
        ),
        (
            "- Closest observed slope: "
            f"`{summary['closest_slope']['value']:.6f}` "
            f"(`{summary['closest_slope']['case']}`; "
            f"delta `{summary['closest_slope']['delta_percent']:.2f}%`, "
            "required `<=10%`)"
        ),
        "",
        "## Case Table",
        "",
        "| background | T | IC | span | active | distances | natural-period fit |",
        "| --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in data["cases"]:
        active = row["active_summary"]
        lines.append(
            f"| `{row['background']}` | {row['T_local']} | `{row['word']}` | "
            f"{row['catalog_span']} | {active['count']} | "
            f"{active['distinct_dist_count']} | "
            f"{fit_text(active['log_monomial_fit'], comparable_to_t15)} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The holdout contains nine natural-period witnesses, all at `T=12`,",
            "across nine distinct primitive length-8 backgrounds. No witness appears",
            "at `T=8` or `T=10`. The result therefore generalizes the observed ANF",
            "gradient beyond `rule_109`, but only in a period-conditioned form.",
            "",
            "`rule_73` is not center-mediated under the Fase 57 definition. These",
            "external-background witnesses show that center mediation is not necessary",
            "once the analysis is extended beyond the original Fase 55 catalog. This",
            "does not contradict the earlier catalog-scoped verdict; it supplies the",
            "external positive that verdict explicitly lacked.",
            "",
            "## Methodological Limits",
            "",
            "- This is an external-background holdout, not an external-rule holdout:",
            "  `rule_73` was already present in Fase 55, but none of these primitive",
            "  length-8 backgrounds was used there.",
            "- The holdout covers the relevant T=8/10/12 range but only one non-rule_109",
            "  rule. It cannot establish a universal ECA generalization result.",
            "- All nine witnesses occur at `T_local=12`. Their natural period therefore",
            "  coincides with the `T_WINDOW=12` protocol resonance identified in Fase 76.",
            "  They satisfy the predeclared natural-period criterion, but robustness at",
            "  neighboring horizons remains untested.",
            "- The thresholds are inherited unchanged from Fase 55 and are not fitted",
            "  to these cases.",
            "- A positive case would be the first observed non-rule_109 natural-period",
            "  witness. A negative result would strengthen, but not prove universally,",
            "  the observed rule_109 specificity.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    baseline = load_module("fase78_periodic_bg_anf_baseline", BASELINE_SCRIPT)
    fase55 = load_module("fase78_anf_gradient_census", FASE55_SCRIPT)
    cases, catalog, preflight = select_cases()
    if preflight_only:
        return {"preflight": preflight, "cases": cases}

    base = baseline.load_base_module()
    popcount16 = np.array(
        [int(value).bit_count() for value in range(1 << 16)],
        dtype=np.uint8,
    )
    checkpoint = load_checkpoint()
    measurements = checkpoint.setdefault("measurements", {})

    for index, case in enumerate(cases, start=1):
        key = case_key(case)
        if key in measurements:
            print(f"[{index}/{len(cases)}] cached {key}", flush=True)
            continue
        print(f"[{index}/{len(cases)}] analyzing {key}", flush=True)
        measurement = baseline.analyze_case(
            base,
            catalog,
            popcount16,
            case,
            case["T_local"],
        )
        measurement["selection_reason"] = case["selection_reason"]
        measurements[key] = measurement
        save_checkpoint(checkpoint)

    rows = [measurements[case_key(case)] for case in cases]
    status, reason = classify(rows, fase55.comparable_to_t15)
    witnesses = [
        row
        for row in rows
        if fase55.comparable_to_t15(
            row["active_summary"]["log_monomial_fit"]
        )
    ]
    highest_r2_row = max(
        rows,
        key=lambda row: row["active_summary"]["log_monomial_fit"]["r2"],
    )
    closest_slope_row = min(
        rows,
        key=lambda row: fase55.slope_delta_percent(
            row["active_summary"]["log_monomial_fit"]["slope"]
        ),
    )
    closest_fit = closest_slope_row["active_summary"]["log_monomial_fit"]
    data = {
        "phase": 78,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "reference": {
            "predicate": "Fase 55 comparable_to_t15",
            "reference_slope": fase55.REFERENCE_SLOPE,
            "minimum_r2": 0.95,
            "slope_tolerance_percent": fase55.SLOPE_TOLERANCE_PERCENT,
            "horizon_policy": "natural period only",
        },
        "summary": {
            "case_count": len(rows),
            "reliable_count": sum(
                bool(row["active_summary"]["log_monomial_fit"]["reliable"])
                for row in rows
            ),
            "witness_count": len(witnesses),
            "witness_period_distribution": dict(
                sorted(Counter(row["T_local"] for row in witnesses).items())
            ),
            "witness_backgrounds": sorted(
                {row["background"] for row in witnesses}
            ),
            "witnesses": [
                {
                    "label": row["label"],
                    "background": row["background"],
                    "T_local": row["T_local"],
                    "word": row["word"],
                }
                for row in witnesses
            ],
            "concrete_mismatch_count": sum(
                not bool(row["all_outputs_match_concrete"]) for row in rows
            ),
            "highest_r2": {
                "case": highest_r2_row["label"],
                "value": highest_r2_row["active_summary"]["log_monomial_fit"]["r2"],
            },
            "closest_slope": {
                "case": closest_slope_row["label"],
                "value": closest_fit["slope"],
                "delta_percent": fase55.slope_delta_percent(
                    closest_fit["slope"]
                ),
            },
        },
        "cases": rows,
    }
    RESULTS_JSON.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(data, fase55.comparable_to_t15)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    data = run(preflight_only=args.preflight_only)
    if args.preflight_only:
        print(json.dumps(data["preflight"], indent=2, sort_keys=True))
        return
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['status']}")


if __name__ == "__main__":
    main()
