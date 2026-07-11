#!/usr/bin/env python3
"""Fase 55: census of non-T15 ANF-gradient witnesses."""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
CATALOG_JSONL = OUT_DIR / "periodic_background_oscillator_results.jsonl"
RESULTS_JSON = OUT_DIR / "anf_gradient_census_results.json"
REPORT_MD = OUT_DIR / "anf_gradient_census_report.md"
CHECKPOINT_JSON = OUT_DIR / "anf_gradient_census_checkpoint.json"

REFERENCE_SLOPE = -0.307283
REFERENCE_R2 = 0.998197
SLOPE_TOLERANCE_PERCENT = 10.0
MIN_SPAN = 11
COMMON_T_WINDOW = 12
EXCLUDED_PERIODS = {2, 15}

ALREADY_TESTED_WORDS: dict[tuple[int, str, int], str] = {
    (73, "0010", 10): "1110111",
    (109, "1011", 10): "00000001",
    (73, "0011", 12): "10001010",
    (94, "0010", 3): "1000101",
    (109, "1011", 6): "00001001",
    (109, "1101", 10): "0001000",
    (73, "0010", 6): "1100111",
}


def load_baseline_module():
    spec = importlib.util.spec_from_file_location("periodic_bg_anf_baseline", BASELINE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import baseline script from {BASELINE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def complete_stationary_records(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    required = {"rule", "background", "period_T", "span", "word", "word_len", "kind"}
    return [
        row for row in rows
        if required.issubset(row)
        and row["kind"] == "stationary"
        and row["period_T"] not in EXCLUDED_PERIODS
    ]


def pick_catalog_record(records: list[dict[str, Any]], key: tuple[int, str, int]) -> tuple[dict[str, Any], str]:
    tested_word = ALREADY_TESTED_WORDS.get(key)
    if tested_word is not None:
        tested = [row for row in records if row["word"] == tested_word]
        if not tested:
            raise RuntimeError(f"Already-tested word {tested_word!r} missing for {key}")
        return tested[0], "already_tested_exact_word"
    ranked = sorted(records, key=lambda row: (-row["span"], row["word_len"], row["word"]))
    return ranked[0], "max_span_shortest_word"


def select_cases(catalog: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    grouped: dict[tuple[int, str, int], list[dict[str, Any]]] = {}
    for row in complete_stationary_records(catalog):
        key = (row["rule"], row["background"], row["period_T"])
        grouped.setdefault(key, []).append(row)

    selected = []
    for key, records in grouped.items():
        max_span = max(row["span"] for row in records)
        if max_span < MIN_SPAN:
            continue
        record, reason = pick_catalog_record(records, key)
        selected.append(
            {
                "label": f"rule{record['rule']}_bg{record['background']}_T{record['period_T']}",
                "role": "already_tested" if key in ALREADY_TESTED_WORDS else "census",
                "rule": record["rule"],
                "background": record["background"],
                "T_local": record["period_T"],
                "word": record["word"],
                "already_tested": key in ALREADY_TESTED_WORDS,
                "selection_reason": reason,
                "catalog_group_size": len(records),
                "catalog_max_span": max_span,
            }
        )
    selected.sort(key=lambda case: (case["rule"], case["background"], case["T_local"], case["word"]))
    preflight = {
        "raw_rows": len(catalog),
        "complete_stationary_rows": len(complete_stationary_records(catalog)),
        "candidate_groups": len(selected),
        "period_distribution": dict(sorted(Counter(case["T_local"] for case in selected).items())),
        "rule_distribution": dict(sorted(Counter(case["rule"] for case in selected).items())),
        "already_tested_count": sum(1 for case in selected if case["already_tested"]),
    }
    return selected, preflight


def case_key(case: dict[str, Any], t_window: int) -> str:
    return f"r{case['rule']}_bg{case['background']}_T{case['T_local']}_w{case['word']}_h{t_window}"


def load_checkpoint() -> dict[str, Any]:
    if not CHECKPOINT_JSON.exists():
        return {"measurements": {}}
    return json.loads(CHECKPOINT_JSON.read_text(encoding="utf-8"))


def save_checkpoint(checkpoint: dict[str, Any]) -> None:
    CHECKPOINT_JSON.write_text(json.dumps(checkpoint, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def slope_delta_percent(slope: float | None) -> float | None:
    if slope is None:
        return None
    return abs(abs(slope) - abs(REFERENCE_SLOPE)) / abs(REFERENCE_SLOPE) * 100.0


def comparable_to_t15(fit: dict[str, Any]) -> bool:
    if not fit["reliable"] or fit["slope"] is None or fit["r2"] is None:
        return False
    if fit["slope"] >= 0 or fit["r2"] < 0.95:
        return False
    delta = slope_delta_percent(fit["slope"])
    return delta is not None and delta <= SLOPE_TOLERANCE_PERCENT


def classify_case(natural: dict[str, Any], common: dict[str, Any]) -> str:
    natural_fit = natural["active_summary"]["log_monomial_fit"]
    common_fit = common["active_summary"]["log_monomial_fit"]
    if comparable_to_t15(natural_fit):
        return "NATURAL_PERIOD_STRONG"
    if comparable_to_t15(common_fit):
        if natural["T_local"] >= 8:
            return "HORIZON_ACCEPTABLE"
        return "HORIZON_ARTIFACT"
    if not natural_fit["reliable"]:
        return "INSUFFICIENT_SUPPORT"
    return "NEGATIVE"


def classify_status(case_summaries: list[dict[str, Any]]) -> tuple[str, str]:
    new_cases = [case for case in case_summaries if not case["already_tested"]]
    if any(case["category"] == "NATURAL_PERIOD_STRONG" for case in new_cases):
        return (
            "NEW_NATURAL_PERIOD_WITNESS_FOUND",
            "At least one previously untested non-T15 oscillator reproduces a T15-like gradient at its natural period.",
        )
    if any(case["category"] == "HORIZON_ACCEPTABLE" for case in new_cases):
        return (
            "NEW_HORIZON_ACCEPTABLE_WITNESS_FOUND",
            "At least one previously untested non-T15 oscillator reproduces a T15-like gradient at the common 12-step horizon with T_local >= 8.",
        )
    if new_cases:
        insufficient = sum(1 for case in new_cases if case["category"] == "INSUFFICIENT_SUPPORT")
        if insufficient > len(new_cases) / 2:
            return (
                "INSUFFICIENT_CATALOG_COVERAGE",
                "Most previously untested candidates lack reliable natural-period active-distance support.",
            )
    return (
        "RULE109_T10_ISOLATED",
        "No previously untested candidate exceeds the natural-period or acceptable-horizon witness thresholds.",
    )


def run_census() -> dict[str, Any]:
    baseline = load_baseline_module()
    catalog = load_jsonl(CATALOG_JSONL)
    selected, preflight = select_cases(catalog)
    print(f"Candidate groups: {preflight['candidate_groups']}")
    print(f"Period distribution: {preflight['period_distribution']}")
    print(f"Rule distribution: {preflight['rule_distribution']}")
    print("Selected cases:")
    for case in selected:
        flag = " already_tested" if case["already_tested"] else ""
        print(
            f"  rule={case['rule']} bg={case['background']} T={case['T_local']} "
            f"span={case['catalog_max_span']} word={case['word']}{flag}"
        )

    base = baseline.load_base_module()
    popcount16 = np.array([int(i).bit_count() for i in range(1 << 16)], dtype=np.uint8)
    checkpoint = load_checkpoint()
    measurements = checkpoint.setdefault("measurements", {})
    for idx, case in enumerate(selected, start=1):
        horizons = sorted({case["T_local"], COMMON_T_WINDOW})
        for t_window in horizons:
            key = case_key(case, t_window)
            if key in measurements:
                print(f"[{idx}/{len(selected)}] cached {key}")
                continue
            print(f"[{idx}/{len(selected)}] analyzing {key}")
            result = baseline.analyze_case(base, catalog, popcount16, case, t_window)
            result["already_tested"] = case["already_tested"]
            result["selection_reason"] = case["selection_reason"]
            measurements[key] = result
            save_checkpoint(checkpoint)

    case_summaries = []
    all_measurements = []
    for case in selected:
        natural = measurements[case_key(case, case["T_local"])]
        common = measurements[case_key(case, COMMON_T_WINDOW)]
        category = classify_case(natural, common)
        case_summaries.append(
            {
                "label": case["label"],
                "rule": case["rule"],
                "background": case["background"],
                "T_local": case["T_local"],
                "word": case["word"],
                "already_tested": case["already_tested"],
                "selection_reason": case["selection_reason"],
                "category": category,
                "natural_key": case_key(case, case["T_local"]),
                "common_key": case_key(case, COMMON_T_WINDOW),
            }
        )
        all_measurements.extend([natural])
        if case["T_local"] != COMMON_T_WINDOW:
            all_measurements.append(common)

    status, reason = classify_status(case_summaries)
    return {
        "status": status,
        "verdict_reason": reason,
        "reference": {
            "slope": REFERENCE_SLOPE,
            "r2": REFERENCE_R2,
            "slope_tolerance_percent": SLOPE_TOLERANCE_PERCENT,
        },
        "selection": {
            "min_span": MIN_SPAN,
            "excluded_periods": sorted(EXCLUDED_PERIODS),
            "common_t_window": COMMON_T_WINDOW,
            "already_tested_words": {
                f"{rule}/{background}/T{period}": word
                for (rule, background, period), word in sorted(ALREADY_TESTED_WORDS.items())
            },
        },
        "preflight": preflight,
        "case_summaries": case_summaries,
        "measurements": all_measurements,
    }


def fmt_fit(fit: dict[str, Any]) -> str:
    if fit["slope"] is None:
        return "not enough support"
    delta = slope_delta_percent(fit["slope"])
    delta_text = "n/a" if delta is None else f"{delta:.2f}%"
    comparable = "yes" if comparable_to_t15(fit) else "no"
    reliable = "yes" if fit["reliable"] else "no"
    return (
        f"slope={fit['slope']:.6f}, R^2={fit['r2']:.6f}, "
        f"delta={delta_text}, reliable={reliable}, comparable={comparable}"
    )


def write_report(data: dict[str, Any]) -> None:
    counts = Counter(case["category"] for case in data["case_summaries"])
    new_counts = Counter(case["category"] for case in data["case_summaries"] if not case["already_tested"])
    by_key = {
        case_key(measurement, measurement["t_window"]): measurement
        for measurement in data["measurements"]
    }
    lines = [
        "# Fase 55: Non-T15 ANF Gradient Census",
        "",
        "## Question",
        "",
        "Across the periodic-background oscillator catalog, how many non-T15 cases",
        "with wide support reproduce the T15-like ANF gradient at their natural",
        "period, and how many only do so at the common 12-step horizon?",
        "",
        "The census excludes `T_local=2` compact baselines and `T_local=15` cases,",
        f"keeps groups with `span >= {MIN_SPAN}`, and evaluates one IC per",
        "`(rule, background, T_local)` group. Already-tested groups use their exact",
        "previous ICs as consistency baselines; new groups use max span, then",
        "shortest word as the tie-breaker.",
        "",
        "Reference: T15 Fase 45 slope `-0.307283`, R^2 `0.998197`.",
        "",
        "## Preflight",
        "",
        f"- Candidate groups: {data['preflight']['candidate_groups']}",
        f"- Already-tested groups: {data['preflight']['already_tested_count']}",
        f"- Period distribution: `{data['preflight']['period_distribution']}`",
        f"- Rule distribution: `{data['preflight']['rule_distribution']}`",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"All categories: `{dict(sorted(counts.items()))}`",
        "",
        f"Previously untested categories: `{dict(sorted(new_counts.items()))}`",
        "",
        "## Case Table",
        "",
        "| case | tested | category | natural-period fit | common-horizon fit |",
        "| --- | --- | --- | --- | --- |",
    ]
    for summary in data["case_summaries"]:
        natural = by_key[summary["natural_key"]]
        common = by_key[summary["common_key"]]
        natural_fit = natural["active_summary"]["log_monomial_fit"]
        common_fit = common["active_summary"]["log_monomial_fit"]
        tested = "yes" if summary["already_tested"] else "no"
        label = f"rule_{summary['rule']}/bg={summary['background']}/T={summary['T_local']}/word={summary['word']}"
        lines.append(
            f"| `{label}` | {tested} | `{summary['category']}` | "
            f"{fmt_fit(natural_fit)} | {fmt_fit(common_fit)} |"
        )
    lines.extend(
        [
            "",
            "## Category Definitions",
            "",
            "- `NATURAL_PERIOD_STRONG`: reliable and comparable at `T_WINDOW=T_local`.",
            "- `HORIZON_ACCEPTABLE`: reliable and comparable at `T_WINDOW=12` with `T_local >= 8`.",
            "- `HORIZON_ARTIFACT`: comparable at `T_WINDOW=12` with `T_local <= 6`.",
            "- `INSUFFICIENT_SUPPORT`: natural-period fit is not reliable.",
            "- `NEGATIVE`: reliable natural-period fit but not comparable at either threshold.",
            "",
        ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = run_census()
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['status']}")


if __name__ == "__main__":
    main()
