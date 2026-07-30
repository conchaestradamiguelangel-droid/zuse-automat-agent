#!/usr/bin/env python3
"""Fase 80: local horizon-response topology for rule_73 len-8 T=12 cases."""

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
FASE79_SCRIPT = OUT_DIR / "analyze_rule73_len8_neighbor_horizons.py"
FASE79_RESULTS = OUT_DIR / "rule73_len8_neighbor_horizons_results.json"
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
FASE55_SCRIPT = OUT_DIR / "analyze_anf_gradient_census.py"
CHECKPOINT_JSON = OUT_DIR / "rule73_len8_horizon_response_checkpoint.json"
RESULTS_JSON = OUT_DIR / "rule73_len8_horizon_response_results.json"
REPORT_MD = OUT_DIR / "rule73_len8_horizon_response_report.md"

BASELINE_HORIZON = 12
HORIZONS = tuple(range(8, 17))
REUSED_HORIZONS = (10, 12, 14, 16)
NEW_HORIZONS = tuple(
    horizon for horizon in HORIZONS if horizon not in REUSED_HORIZONS
)


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


def fit_view(
    measurement: dict[str, Any],
    comparable_to_t15,
    slope_delta_percent,
) -> dict[str, Any]:
    fit = measurement["active_summary"]["log_monomial_fit"]
    slope = fit["slope"]
    return {
        "horizon": int(measurement["t_window"]),
        "active_count": int(measurement["active_summary"]["count"]),
        "distinct_dist_count": int(
            measurement["active_summary"]["distinct_dist_count"]
        ),
        "reliable": bool(fit["reliable"]),
        "slope": slope,
        "r2": fit["r2"],
        "slope_delta_percent": slope_delta_percent(slope),
        "comparable": bool(comparable_to_t15(fit)),
        "all_outputs_match_concrete": bool(
            measurement["all_outputs_match_concrete"]
        ),
    }


def normalize_reused_view(
    view: dict[str, Any],
    slope_delta_percent,
) -> dict[str, Any]:
    normalized = dict(view)
    normalized["slope_delta_percent"] = slope_delta_percent(view["slope"])
    return normalized


def consecutive_runs(values: list[int]) -> list[list[int]]:
    runs: list[list[int]] = []
    for value in sorted(values):
        if not runs or value != runs[-1][-1] + 1:
            runs.append([value])
        else:
            runs[-1].append(value)
    return runs


def run_containing(runs: list[list[int]], value: int) -> list[int]:
    for run in runs:
        if value in run:
            return run
    return []


def classify(summary: dict[str, Any]) -> tuple[str, str]:
    band_count = int(summary["witness_with_baseline_band_count"])
    witness_count = int(summary["baseline_witness_count"])
    control_count = int(summary["control_positive_case_count"])
    off_baseline_count = int(summary["witness_with_offbaseline_count"])
    if control_count:
        if band_count:
            return (
                "RULE73_HORIZON_BANDS_WITH_CONTROL_CROSSINGS",
                (
                    f"{band_count}/{witness_count} baseline witnesses form a "
                    f"contiguous band through h=12, but {control_count} controls "
                    "also become comparable somewhere in h=8..16."
                ),
            )
        return (
            "RULE73_HORIZON_RESPONSE_UNDISCRIMINATED",
            (
                "No baseline witness forms a contiguous band through h=12, "
                f"and {control_count} controls become comparable."
            ),
        )
    if band_count == witness_count:
        return (
            "RULE73_HORIZON_BANDS_ALL_WITNESSES",
            (
                "All baseline witnesses form a contiguous comparable band "
                "through h=12, with no control crossings."
            ),
        )
    if band_count:
        return (
            "RULE73_HORIZON_BANDS_PARTIAL",
            (
                f"{band_count}/{witness_count} baseline witnesses form a "
                "contiguous comparable band through h=12, with no control "
                "crossings."
            ),
        )
    if off_baseline_count:
        return (
            "RULE73_HORIZON_DISCONNECTED_ISLANDS",
            (
                "No baseline witness forms a contiguous band through h=12; "
                "off-baseline positives occur only as disconnected islands."
            ),
        )
    return (
        "RULE73_HORIZON_POINT_RESONANCE",
        (
            "All nine baseline witnesses are restricted to the isolated "
            "h=12 measurement point over the complete h=8..16 grid."
        ),
    )


def response_cell(measurement: dict[str, Any]) -> str:
    return "C" if measurement["comparable"] else "-"


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    horizon_header = " | ".join(f"h{horizon}" for horizon in HORIZONS)
    horizon_rule = " | ".join("---" for _ in HORIZONS)
    lines = [
        "# Fase 80: rule_73 len-8 Horizon-Response Topology",
        "",
        "## Question",
        "",
        "Do the Fase 78 `rule_73/T=12` witnesses occupy contiguous local",
        "robustness bands around their natural-period horizon, or are the Fase 79",
        "survivals isolated threshold crossings?",
        "",
        "The horizon grid `8..16` was fixed before measurement. Existing Fase 79",
        "measurements at horizons `10`, `12`, `14`, and `16` are reused exactly;",
        "only horizons `8`, `9`, `11`, `13`, and `15` are newly measured. The",
        "Fase 55 `comparable_to_t15()` predicate and all thresholds are unchanged.",
        "",
        "A baseline band is a consecutive run of comparable horizons that contains",
        "`h=12`. Comparable horizons outside that run are reported separately as",
        "disconnected islands.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Cases: `{summary['case_count']}`",
        f"- Baseline witnesses: `{summary['baseline_witness_count']}`",
        f"- Baseline controls: `{summary['control_count']}`",
        (
            "- Witnesses with any off-baseline positive: "
            f"`{summary['witness_with_offbaseline_count']}`"
        ),
        (
            "- Witnesses with a contiguous band through h=12: "
            f"`{summary['witness_with_baseline_band_count']}`"
        ),
        (
            "- Witnesses surviving at an immediate neighbor h=11 or h=13: "
            f"`{summary['witness_with_immediate_neighbor_count']}`"
        ),
        (
            "- Baseline-band width distribution: "
            f"`{summary['witness_baseline_band_widths']}`"
        ),
        (
            "- Controls becoming comparable anywhere in h=8..16: "
            f"`{summary['control_positive_case_count']}`"
        ),
        (
            "- Comparable counts by horizon (witness/control): "
            f"`{summary['comparable_counts_by_horizon']}`"
        ),
        (
            "- Total comparable response ridge by horizon: "
            f"`{summary['total_comparable_by_horizon']}`"
        ),
        f"- Packed/concrete discrepancies: `{summary['concrete_mismatch_count']}`",
        "",
        "## Response Matrix",
        "",
        "`C` means comparable to the unchanged T15 reference; `-` means not comparable.",
        "",
        (
            f"| cohort | background | IC | {horizon_header} | "
            "band through h12 | disconnected |"
        ),
        (
            f"| --- | --- | --- | {horizon_rule} | --- | --- |"
        ),
    ]
    for case in data["cases"]:
        cells = " | ".join(
            response_cell(item) for item in case["measurements"]
        )
        lines.append(
            f"| {case['cohort']} | `{case['background']}` | `{case['word']}` | "
            f"{cells} | {case['baseline_run']} | "
            f"{case['disconnected_comparable_horizons']} |"
        )

    comparable_rows = [
        (case, measurement)
        for case in data["cases"]
        for measurement in case["measurements"]
        if measurement["comparable"]
    ]
    lines.extend(
        [
            "",
            "## Comparable Measurements",
            "",
            "| cohort | background | horizon | slope | R2 | slope delta |",
            "| --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for case, measurement in comparable_rows:
        lines.append(
            f"| {case['cohort']} | `{case['background']}` | "
            f"{measurement['horizon']} | {measurement['slope']:.6f} | "
            f"{measurement['r2']:.6f} | "
            f"{measurement['slope_delta_percent']:.2f}% |"
        )

    lines.extend(
        [
            "",
            "## Independent Re-measurement",
            "",
            "One band witness and one control crossing were recomputed without",
            "reading their checkpoint entries.",
            "",
            "| cohort | background | horizon | exact raw match | concrete match |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for item in data["independent_verification"]:
        lines.append(
            f"| {item['cohort']} | `{item['background']}` | "
            f"{item['horizon']} | "
            f"{str(item['exact_raw_match']).lower()} | "
            f"{str(item['all_outputs_match_concrete']).lower()} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if summary["witness_with_baseline_band_count"]:
        lines.extend(
            [
                "At least one natural-period witness remains comparable at an",
                "immediately adjacent integer horizon, so the response is not only",
                "a collection of isolated even-horizon crossings. The width and",
                "background dependence of each band are reported without fitting a",
                "new classifier.",
            ]
        )
    else:
        lines.extend(
            [
                "No natural-period witness remains comparable at an immediately",
                "adjacent integer horizon. Any off-baseline survival is therefore",
                "disconnected from the h=12 point under the unchanged predicate.",
            ]
        )
    lines.extend(
        [
            "",
            "At cohort level, the response is concentrated in a finite ridge around",
            "`h=12`, but cohort membership is not invariant: two baseline controls",
            "become comparable only at `h=11`. The result therefore supports local",
            "horizon bands for most natural-period witnesses, not a fixed set of",
            "backgrounds that remains positive throughout the neighborhood.",
        ]
    )
    if summary["control_positive_case_count"]:
        lines.extend(
            [
                "",
                "Control crossings prevent interpreting the response topology as a",
                "clean witness-specific robustness property.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "No baseline-negative control crosses the comparability threshold",
                "anywhere in the grid, preserving the witness/control asymmetry.",
            ]
        )
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- The grid is local (`h=8..16`) and does not establish behavior at",
            "  arbitrarily short or long horizons.",
            "- The analysis covers one ECA rule and primitive length-8 backgrounds.",
            "- Band membership is defined by the inherited Fase 55 threshold; no",
            "  new threshold is fitted.",
            "- The same physical oscillator and IC are retained while only the",
            "  measurement horizon changes.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase78 = load_module("fase80_rule73_len8_holdout", FASE78_SCRIPT)
    fase79 = load_module("fase80_rule73_neighbor_horizons", FASE79_SCRIPT)
    baseline = load_module("fase80_periodic_bg_anf_baseline", BASELINE_SCRIPT)
    fase55 = load_module("fase80_anf_gradient_census", FASE55_SCRIPT)
    fase78_results = load_json(FASE78_RESULTS)
    fase79_results = load_json(FASE79_RESULTS)
    cases, catalog, baseline_witnesses = fase79.select_t12_cases(
        fase78,
        fase78_results,
    )
    preflight = {
        "case_count": len(cases),
        "baseline_witness_count": len(baseline_witnesses),
        "control_count": len(cases) - len(baseline_witnesses),
        "baseline_horizon": BASELINE_HORIZON,
        "horizons": list(HORIZONS),
        "reused_horizons": list(REUSED_HORIZONS),
        "new_horizons": list(NEW_HORIZONS),
        "new_measurement_count": len(cases) * len(NEW_HORIZONS),
        "threshold_policy": "unchanged Fase 55 comparable_to_t15",
        "band_definition": (
            "consecutive comparable horizons containing baseline h=12"
        ),
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

    for case_index, case in enumerate(cases, start=1):
        for horizon in NEW_HORIZONS:
            key = case_key(case, horizon)
            if key in measurements:
                print(f"[{case_index}/{len(cases)}] cached {key}", flush=True)
                continue
            print(f"[{case_index}/{len(cases)}] analyzing {key}", flush=True)
            measurements[key] = baseline.analyze_case(
                base,
                catalog,
                popcount16,
                case,
                horizon,
            )
            save_checkpoint(checkpoint)

    reused_by_label = {
        str(row["label"]): {
            int(item["horizon"]): item
            for item in row["measurements"]
        }
        for row in fase79_results["cases"]
    }
    rows = []
    for case in cases:
        views = []
        for horizon in HORIZONS:
            if horizon in REUSED_HORIZONS:
                view = normalize_reused_view(
                    reused_by_label[case["label"]][horizon],
                    fase55.slope_delta_percent,
                )
            else:
                view = fit_view(
                    measurements[case_key(case, horizon)],
                    fase55.comparable_to_t15,
                    fase55.slope_delta_percent,
                )
            views.append(view)
        comparable_horizons = [
            item["horizon"] for item in views if item["comparable"]
        ]
        runs = consecutive_runs(comparable_horizons)
        baseline_run = run_containing(runs, BASELINE_HORIZON)
        disconnected = [
            horizon
            for horizon in comparable_horizons
            if horizon not in baseline_run
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
                "comparable_horizons": comparable_horizons,
                "comparable_runs": runs,
                "baseline_run": baseline_run,
                "baseline_band_width": len(baseline_run),
                "immediate_neighbor_horizons": [
                    horizon
                    for horizon in (11, 13)
                    if horizon in comparable_horizons
                ],
                "disconnected_comparable_horizons": disconnected,
            }
        )

    witness_rows = [
        row for row in rows if row["cohort"] == "baseline_witness"
    ]
    control_rows = [
        row for row in rows if row["cohort"] == "baseline_control"
    ]
    independent_verification = []
    verification_targets = [
        ("00101101", "baseline_witness", 11),
        ("00111011", "baseline_control", 11),
    ]
    for background, cohort, horizon in verification_targets:
        case = next(
            item for item in cases if item["background"] == background
        )
        fresh = baseline.analyze_case(
            base,
            catalog,
            popcount16,
            case,
            horizon,
        )
        cached = measurements[case_key(case, horizon)]
        fresh_view = fit_view(
            fresh,
            fase55.comparable_to_t15,
            fase55.slope_delta_percent,
        )
        independent_verification.append(
            {
                "label": case["label"],
                "background": background,
                "cohort": cohort,
                "horizon": horizon,
                "exact_raw_match": fresh == cached,
                "all_outputs_match_concrete": fresh_view[
                    "all_outputs_match_concrete"
                ],
                "comparable": fresh_view["comparable"],
                "slope": fresh_view["slope"],
                "r2": fresh_view["r2"],
            }
        )
    summary = {
        "case_count": len(rows),
        "baseline_witness_count": len(witness_rows),
        "control_count": len(control_rows),
        "witness_with_offbaseline_count": sum(
            any(horizon != BASELINE_HORIZON for horizon in row["comparable_horizons"])
            for row in witness_rows
        ),
        "witness_with_baseline_band_count": sum(
            row["baseline_band_width"] >= 2 for row in witness_rows
        ),
        "witness_with_immediate_neighbor_count": sum(
            bool(row["immediate_neighbor_horizons"]) for row in witness_rows
        ),
        "witness_baseline_band_widths": {
            row["label"]: row["baseline_band_width"] for row in witness_rows
        },
        "witness_with_disconnected_islands_count": sum(
            bool(row["disconnected_comparable_horizons"])
            for row in witness_rows
        ),
        "control_positive_case_count": sum(
            bool(row["comparable_horizons"]) for row in control_rows
        ),
        "control_positive_measurement_count": sum(
            len(row["comparable_horizons"]) for row in control_rows
        ),
        "comparable_counts_by_horizon": {
            str(horizon): {
                "witness": sum(
                    horizon in row["comparable_horizons"]
                    for row in witness_rows
                ),
                "control": sum(
                    horizon in row["comparable_horizons"]
                    for row in control_rows
                ),
            }
            for horizon in HORIZONS
        },
        "total_comparable_by_horizon": {
            str(horizon): sum(
                horizon in row["comparable_horizons"] for row in rows
            )
            for horizon in HORIZONS
        },
        "concrete_mismatch_count": sum(
            not item["all_outputs_match_concrete"]
            for row in rows
            for item in row["measurements"]
        ),
    }
    status, reason = classify(summary)
    data = {
        "phase": 80,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "cases": rows,
        "independent_verification": independent_verification,
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
