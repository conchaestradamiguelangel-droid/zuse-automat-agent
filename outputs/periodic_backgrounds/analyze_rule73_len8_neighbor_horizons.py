#!/usr/bin/env python3
"""Fase 79: neighboring-horizon robustness of rule_73 len-8 T=12 witnesses."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
FASE78_SCRIPT = OUT_DIR / "analyze_rule73_len8_holdout.py"
FASE78_RESULTS = OUT_DIR / "rule73_len8_holdout_results.json"
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
FASE55_SCRIPT = OUT_DIR / "analyze_anf_gradient_census.py"
CHECKPOINT_JSON = OUT_DIR / "rule73_len8_neighbor_horizons_checkpoint.json"
RESULTS_JSON = OUT_DIR / "rule73_len8_neighbor_horizons_results.json"
REPORT_MD = OUT_DIR / "rule73_len8_neighbor_horizons_report.md"

BASELINE_HORIZON = 12
NEIGHBOR_HORIZONS = (10, 14, 16)
ALL_HORIZONS = (10, 12, 14, 16)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def case_key(case: dict[str, Any], horizon: int) -> str:
    return (
        f"r{case['rule']}_bg{case['background']}_T{case['T_local']}"
        f"_w{case['word']}_h{horizon}"
    )


def load_checkpoint() -> dict[str, Any]:
    if not CHECKPOINT_JSON.exists():
        return {"measurements": {}}
    return load_json(CHECKPOINT_JSON)


def save_checkpoint(checkpoint: dict[str, Any]) -> None:
    CHECKPOINT_JSON.write_text(
        json.dumps(checkpoint, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def fit_view(measurement: dict[str, Any], comparable_to_t15) -> dict[str, Any]:
    fit = measurement["active_summary"]["log_monomial_fit"]
    return {
        "horizon": int(measurement["t_window"]),
        "active_count": int(measurement["active_summary"]["count"]),
        "distinct_dist_count": int(
            measurement["active_summary"]["distinct_dist_count"]
        ),
        "reliable": bool(fit["reliable"]),
        "slope": fit["slope"],
        "r2": fit["r2"],
        "comparable": bool(comparable_to_t15(fit)),
        "all_outputs_match_concrete": bool(
            measurement["all_outputs_match_concrete"]
        ),
    }


def select_t12_cases(
    fase78_module,
    fase78_results: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str]]:
    cases, catalog, _preflight = fase78_module.select_cases()
    t12_cases = [case for case in cases if int(case["T_local"]) == 12]
    t12_catalog = [
        row
        for row in catalog
        if int(row["period_T"]) == 12
    ]
    baseline_witnesses = {
        str(item["label"])
        for item in fase78_results["summary"]["witnesses"]
    }
    if len(t12_cases) != 18 or len(baseline_witnesses) != 9:
        raise RuntimeError(
            "Expected 18 T=12 holdout cases and 9 Fase 78 witnesses, got "
            f"{len(t12_cases)} and {len(baseline_witnesses)}"
        )
    return t12_cases, t12_catalog, baseline_witnesses


def classify(summary: dict[str, Any]) -> tuple[str, str]:
    survivors = int(summary["baseline_witness_neighbor_survival_count"])
    if survivors == 0:
        return (
            "RULE73_LEN8_T12_ONLY_PROTOCOL_DEPENDENT",
            (
                "None of the nine Fase 78 witnesses remains comparable at "
                "T_WINDOW=10, 14, or 16. Their signal is restricted to the exact "
                "natural-period horizon T=12 under this protocol."
            ),
        )
    if survivors == int(summary["baseline_witness_count"]):
        return (
            "RULE73_LEN8_NEIGHBOR_HORIZON_ROBUST",
            (
                "All nine Fase 78 witnesses remain comparable at one or more "
                "predeclared neighboring horizons."
            ),
        )
    return (
        "RULE73_LEN8_NEIGHBOR_HORIZON_PARTIAL",
        (
            f"{survivors} of the nine Fase 78 witnesses remain comparable at "
            "one or more predeclared neighboring horizons."
        ),
    )


def fit_text(item: dict[str, Any]) -> str:
    if item["slope"] is None:
        return "insufficient"
    return (
        f"{item['slope']:.6f}/{item['r2']:.6f}/"
        f"{str(item['comparable']).lower()}"
    )


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    lines = [
        "# Fase 79: rule_73 len-8 Neighboring-Horizon Robustness",
        "",
        "## Question",
        "",
        "Do the nine natural-period `rule_73/T=12` witnesses from Fase 78 retain",
        "the unchanged T15-like ANF-gradient signature when measured away from the",
        "exact `T_WINDOW=12` point?",
        "",
        "All 18 `rule_73/T=12` holdout cases are evaluated. The nine Fase 78",
        "witnesses form the primary cohort; the other nine cases are controls.",
        "Horizons `10`, `14`, and `16` were fixed before measurement. Horizon `12`",
        "is reused directly from Fase 78. The Fase 55 `comparable_to_t15()`",
        "predicate is unchanged.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- T=12 cases: `{summary['case_count']}`",
        f"- Baseline Fase 78 witnesses: `{summary['baseline_witness_count']}`",
        (
            "- Baseline witnesses surviving at any neighbor: "
            f"`{summary['baseline_witness_neighbor_survival_count']}`"
        ),
        (
            "- Baseline witnesses surviving by horizon: "
            f"`{summary['baseline_witness_survival_by_horizon']}`"
        ),
        (
            "- Surviving witness labels: "
            f"`{summary['baseline_witness_survivors']}`"
        ),
        (
            "- Baseline-negative controls becoming comparable at neighbors: "
            f"`{summary['control_neighbor_positive_count']}`"
        ),
        (
            "- Control positives by horizon: "
            f"`{summary['control_positive_by_horizon']}`"
        ),
        f"- Packed/concrete discrepancies: `{summary['concrete_mismatch_count']}`",
        "",
        "## Case Table",
        "",
        "| cohort | background | IC | h10 slope/R2/cmp | h12 | h14 | h16 | neighbor survival |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for case in data["cases"]:
        by_horizon = {item["horizon"]: item for item in case["measurements"]}
        lines.append(
            f"| {case['cohort']} | `{case['background']}` | `{case['word']}` | "
            f"{fit_text(by_horizon[10])} | {fit_text(by_horizon[12])} | "
            f"{fit_text(by_horizon[14])} | {fit_text(by_horizon[16])} | "
            f"{case['neighbor_survival_horizons']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "Three of the nine Fase 78 witnesses survive outside the exact 12-step",
            "evaluation point: one at horizon 10 and two at horizon 14. No control",
            "case becomes comparable at any neighboring horizon. The Fase 78 result",
            "is therefore not a pure point resonance at `T_WINDOW=12`.",
            "",
            "The robustness is nevertheless partial and background-conditioned.",
            "Six baseline witnesses do not survive, and no witness remains comparable",
            "at horizon 16. This supports a finite neighboring-horizon band for a",
            "subset of backgrounds, not horizon invariance or a universal law.",
            "",
            "Control cases are included to detect a second failure mode: neighboring",
            "horizons may create new comparable fits among cases that were negative at",
            "their natural period. Such cases are reported separately rather than",
            "counted as witness robustness.",
            "",
            "## Methodological Limits",
            "",
            "- The audit varies measurement horizon, not the physical oscillator or IC.",
            "- It covers one rule and primitive length-8 backgrounds only.",
            "- Survival at a neighboring horizon is evidence of protocol robustness,",
            "  not a universal causal law.",
            "- The thresholds are inherited unchanged from Fase 55.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase78_module = load_module("fase79_rule73_len8_holdout", FASE78_SCRIPT)
    baseline = load_module("fase79_periodic_bg_anf_baseline", BASELINE_SCRIPT)
    fase55 = load_module("fase79_anf_gradient_census", FASE55_SCRIPT)
    fase78_results = load_json(FASE78_RESULTS)
    cases, catalog, baseline_witnesses = select_t12_cases(
        fase78_module,
        fase78_results,
    )
    preflight = {
        "case_count": len(cases),
        "baseline_witness_count": len(baseline_witnesses),
        "control_count": len(cases) - len(baseline_witnesses),
        "baseline_horizon": BASELINE_HORIZON,
        "neighbor_horizons": list(NEIGHBOR_HORIZONS),
        "all_horizons": list(ALL_HORIZONS),
        "threshold_policy": "unchanged Fase 55 comparable_to_t15",
        "horizon_12_source": str(FASE78_RESULTS),
    }
    if preflight_only:
        return {"preflight": preflight, "cases": cases}

    base = baseline.load_base_module()
    popcount16 = np.array(
        [int(value).bit_count() for value in range(1 << 16)],
        dtype=np.uint8,
    )
    checkpoint = load_checkpoint()
    measurements = checkpoint.setdefault("measurements", {})

    fase78_by_label = {
        str(row["label"]): row
        for row in fase78_results["cases"]
        if int(row["T_local"]) == 12
    }
    for case_index, case in enumerate(cases, start=1):
        for horizon in NEIGHBOR_HORIZONS:
            key = case_key(case, horizon)
            if key in measurements:
                print(
                    f"[{case_index}/{len(cases)}] cached {key}",
                    flush=True,
                )
                continue
            print(
                f"[{case_index}/{len(cases)}] analyzing {key}",
                flush=True,
            )
            measurements[key] = baseline.analyze_case(
                base,
                catalog,
                popcount16,
                case,
                horizon,
            )
            save_checkpoint(checkpoint)

    rows = []
    for case in cases:
        views = []
        for horizon in ALL_HORIZONS:
            measurement = (
                fase78_by_label[case["label"]]
                if horizon == BASELINE_HORIZON
                else measurements[case_key(case, horizon)]
            )
            views.append(fit_view(measurement, fase55.comparable_to_t15))
        neighbor_survival = [
            item["horizon"]
            for item in views
            if item["horizon"] in NEIGHBOR_HORIZONS
            and item["comparable"]
        ]
        rows.append(
            {
                "label": case["label"],
                "background": case["background"],
                "word": case["word"],
                "T_local": case["T_local"],
                "cohort": (
                    "baseline_witness"
                    if case["label"] in baseline_witnesses
                    else "baseline_control"
                ),
                "measurements": views,
                "neighbor_survival_horizons": neighbor_survival,
            }
        )

    witness_rows = [row for row in rows if row["cohort"] == "baseline_witness"]
    control_rows = [row for row in rows if row["cohort"] == "baseline_control"]
    summary = {
        "case_count": len(rows),
        "baseline_witness_count": len(witness_rows),
        "baseline_witness_neighbor_survival_count": sum(
            bool(row["neighbor_survival_horizons"]) for row in witness_rows
        ),
        "baseline_witness_survival_by_horizon": {
            str(horizon): sum(
                any(
                    item["horizon"] == horizon and item["comparable"]
                    for item in row["measurements"]
                )
                for row in witness_rows
            )
            for horizon in NEIGHBOR_HORIZONS
        },
        "baseline_witness_survivors": [
            {
                "label": row["label"],
                "horizons": row["neighbor_survival_horizons"],
            }
            for row in witness_rows
            if row["neighbor_survival_horizons"]
        ],
        "control_neighbor_positive_count": sum(
            bool(row["neighbor_survival_horizons"]) for row in control_rows
        ),
        "control_positive_by_horizon": {
            str(horizon): sum(
                any(
                    item["horizon"] == horizon and item["comparable"]
                    for item in row["measurements"]
                )
                for row in control_rows
            )
            for horizon in NEIGHBOR_HORIZONS
        },
        "concrete_mismatch_count": sum(
            not item["all_outputs_match_concrete"]
            for row in rows
            for item in row["measurements"]
        ),
    }
    status, reason = classify(summary)
    data = {
        "phase": 79,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "cases": rows,
    }
    RESULTS_JSON.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(data)
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
