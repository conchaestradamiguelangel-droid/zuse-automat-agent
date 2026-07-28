#!/usr/bin/env python3
"""Fase 77: natural-period ANF census on new period-8-background rules.

The primitive length-8 background sweep found four stationary-oscillator
rules absent from the Fase 55 census. This audit measures every comparable
wide group from those rules at its natural period, using the unchanged
Fase 55 T15-comparability predicate.
"""

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
LEN8_DIR = OUT_DIR.parent / "periodic_backgrounds_len8"
LEN8_CATALOG = LEN8_DIR / "sweep_len8_results.jsonl"
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
FASE55_SCRIPT = OUT_DIR / "analyze_anf_gradient_census.py"
CHECKPOINT_JSON = OUT_DIR / "external_len8_anf_census_checkpoint.json"
RESULTS_JSON = OUT_DIR / "external_len8_anf_census_results.json"
REPORT_MD = OUT_DIR / "external_len8_anf_census_report.md"

FASE55_RULES = {54, 73, 94, 109, 133, 147}
EXCLUDED_PERIODS = {2, 15}
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


def candidate_record(row: dict[str, Any]) -> bool:
    return bool(
        row.get("kind") == "stationary"
        and int(row["rule"]) not in FASE55_RULES
        and int(row["period_T"]) not in EXCLUDED_PERIODS
        and int(row["span"]) >= MIN_SPAN
    )


def rank_key(row: dict[str, Any]) -> tuple[int, int, str]:
    return (-int(row["span"]), int(row["word_len"]), str(row["word"]))


def select_cases() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[tuple[int, str, int], dict[str, Any]] = {}
    raw_rows = 0
    stationary_rows = 0
    eligible_rows = 0

    for row in iter_jsonl(LEN8_CATALOG):
        raw_rows += 1
        if row.get("kind") == "stationary":
            stationary_rows += 1
        if not candidate_record(row):
            continue
        eligible_rows += 1
        background = str(row["background_canonical"])
        key = (int(row["rule"]), background, int(row["period_T"]))
        current = grouped.get(key)
        if current is None or rank_key(row) < rank_key(current):
            grouped[key] = row

    selected_records = sorted(
        grouped.values(),
        key=lambda row: (
            int(row["rule"]),
            str(row["background_canonical"]),
            int(row["period_T"]),
            str(row["word"]),
        ),
    )
    cases = [
        {
            "label": (
                f"rule{row['rule']}_bg{row['background_canonical']}"
                f"_T{row['period_T']}"
            ),
            "role": "external_len8_natural_period",
            "rule": int(row["rule"]),
            "background": str(row["background_canonical"]),
            "T_local": int(row["period_T"]),
            "word": str(row["word"]),
            "selection_reason": "max_span_shortest_word",
        }
        for row in selected_records
    ]
    normalized_catalog = [
        {
            **row,
            "background": str(row["background_canonical"]),
        }
        for row in selected_records
    ]
    preflight = {
        "source_catalog": str(LEN8_CATALOG),
        "raw_rows": raw_rows,
        "stationary_rows": stationary_rows,
        "eligible_rows": eligible_rows,
        "candidate_groups": len(cases),
        "rules": sorted({case["rule"] for case in cases}),
        "rule_distribution": dict(
            sorted(Counter(case["rule"] for case in cases).items())
        ),
        "period_distribution": dict(
            sorted(Counter(case["T_local"] for case in cases).items())
        ),
        "selection": {
            "kind": "stationary",
            "excluded_fase55_rules": sorted(FASE55_RULES),
            "excluded_periods": sorted(EXCLUDED_PERIODS),
            "minimum_span": MIN_SPAN,
            "one_case_per_rule_background_period": True,
            "representative": "maximum span; then shortest word; then lexical word",
            "measurement_horizon": "natural period only",
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


def classify_status(
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
            "EXTERNAL_NATURAL_PERIOD_WITNESS_FOUND",
            (
                "At least one stationary oscillator from a rule absent from the "
                "Fase 55 census reproduces the predeclared T15-like ANF gradient "
                "at its own natural period."
            ),
        )
    reliable = sum(
        bool(row["active_summary"]["log_monomial_fit"]["reliable"])
        for row in rows
    )
    if reliable < len(rows) / 2:
        return (
            "EXTERNAL_NATURAL_PERIOD_COVERAGE_INSUFFICIENT",
            (
                "No external witness was found, but fewer than half of the "
                "candidate groups supplied reliable active-distance support."
            ),
        )
    return (
        "EXTERNAL_NATURAL_PERIOD_WITNESS_NOT_FOUND",
        (
            "No stationary oscillator from the four new period-8-background "
            "rules reproduces the predeclared T15-like ANF gradient at its own "
            "natural period."
        ),
    )


def fit_text(fit: dict[str, Any], comparable_to_t15) -> str:
    if fit["slope"] is None:
        return "insufficient support"
    return (
        f"slope={fit['slope']:.6f}, R^2={fit['r2']:.6f}, "
        f"reliable={str(bool(fit['reliable'])).lower()}, "
        f"comparable={str(bool(comparable_to_t15(fit))).lower()}"
    )


def write_report(data: dict[str, Any], comparable_to_t15) -> None:
    preflight = data["preflight"]
    summary = data["summary"]
    lines = [
        "# Fase 77: External Natural-Period ANF Census on Primitive Period-8 Backgrounds",
        "",
        "## Question",
        "",
        "Does the unchanged Fase 55 `comparable_to_t15()` predicate identify a",
        "genuine natural-period ANF-gradient witness in stationary oscillators from",
        "rules absent from the original six-rule census?",
        "",
        "This phase creates an external holdout from the already completed",
        "3,855,360-run primitive period-8 background sweep. Candidate selection was",
        "fixed before ANF measurement. Only the natural oscillator period is measured;",
        "`T_WINDOW=12` is deliberately excluded after Fases 74-76 established its",
        "protocol resonance.",
        "",
        "## Preflight",
        "",
        f"- Source rows: `{preflight['raw_rows']}`",
        f"- Stationary rows: `{preflight['stationary_rows']}`",
        f"- Eligible raw detections: `{preflight['eligible_rows']}`",
        f"- Candidate groups: `{preflight['candidate_groups']}`",
        f"- New rules: `{preflight['rules']}`",
        f"- Rule distribution: `{preflight['rule_distribution']}`",
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
        f"- Witness rules: `{summary['witness_rules']}`",
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
        "| rule | background | T | IC | span | active | distances | natural-period fit |",
        "| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |",
    ]
    for row in data["cases"]:
        active = row["active_summary"]
        lines.append(
            f"| {row['rule']} | `{row['background']}` | {row['T_local']} | "
            f"`{row['word']}` | {row['catalog_span']} | {active['count']} | "
            f"{active['distinct_dist_count']} | "
            f"{fit_text(active['log_monomial_fit'], comparable_to_t15)} |"
        )
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- This is an external-background census over four newly observed rules,",
            "  not an exhaustive new sweep of every possible background and IC length.",
            "- All selected external candidates have natural period 3. The phase can",
            "  detect a natural-period witness, but it does not add external positive",
            "  coverage at periods 8, 10, or 12.",
            "- The T15 comparison thresholds are inherited unchanged from Fase 55.",
            "  No threshold is fitted to these results.",
            "- A negative result supports rule_109 specificity within the two completed",
            "  background catalogs; it is not a universal impossibility theorem.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    baseline = load_module("fase77_periodic_bg_anf_baseline", BASELINE_SCRIPT)
    fase55 = load_module("fase77_anf_gradient_census", FASE55_SCRIPT)
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
    status, reason = classify_status(rows, fase55.comparable_to_t15)
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
    closest_slope_fit = closest_slope_row["active_summary"]["log_monomial_fit"]
    data = {
        "phase": 77,
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
            "witness_rules": sorted({row["rule"] for row in witnesses}),
            "concrete_mismatch_count": sum(
                not bool(row["all_outputs_match_concrete"]) for row in rows
            ),
            "highest_r2": {
                "case": highest_r2_row["label"],
                "value": highest_r2_row["active_summary"]["log_monomial_fit"]["r2"],
            },
            "closest_slope": {
                "case": closest_slope_row["label"],
                "value": closest_slope_fit["slope"],
                "delta_percent": fase55.slope_delta_percent(
                    closest_slope_fit["slope"]
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
