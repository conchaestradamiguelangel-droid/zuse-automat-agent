#!/usr/bin/env python3
"""Fase 53: external-family ANF gradient test."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
RESULTS_JSON = OUT_DIR / "periodic_bg_external_family_results.json"
REPORT_MD = OUT_DIR / "periodic_bg_external_family_report.md"

REFERENCE_SLOPE = -0.307283
REFERENCE_R2 = 0.998197
SLOPE_TOLERANCE = 0.10

CASES = [
    {
        "label": "external_rule54_T4",
        "role": "external_main",
        "rule": 54,
        "background": "0010",
        "T_local": 4,
        "word": "1000001",
    },
    {
        "label": "external_rule94_T6",
        "role": "period_control",
        "rule": 94,
        "background": "0001",
        "T_local": 6,
        "word": "0100010",
    },
    {
        "label": "external_rule133_T6",
        "role": "family_control",
        "rule": 133,
        "background": "1011",
        "T_local": 6,
        "word": "100100",
    },
]


def load_baseline_module():
    spec = importlib.util.spec_from_file_location("periodic_bg_anf_baseline", BASELINE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import baseline script from {BASELINE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def slope_delta_percent(slope: float | None) -> float | None:
    if slope is None:
        return None
    return abs(abs(slope) - abs(REFERENCE_SLOPE)) / abs(REFERENCE_SLOPE) * 100.0


def comparable_to_t15(fit: dict[str, Any]) -> bool:
    if not fit["reliable"] or fit["slope"] is None or fit["r2"] is None:
        return False
    if fit["slope"] >= 0 or fit["r2"] < 0.95:
        return False
    return slope_delta_percent(fit["slope"]) <= SLOPE_TOLERANCE * 100.0


def classify(data: dict[str, Any]) -> tuple[str, str]:
    own_cases = {case["label"]: case for case in data["cases"] if case["t_window"] == case["T_local"]}
    common_cases = {case["label"]: case for case in data["cases"] if case["t_window"] == data["common_t_window"]}
    own_comparable = [
        label for label, case in own_cases.items()
        if comparable_to_t15(case["active_summary"]["log_monomial_fit"])
    ]
    common_comparable = [
        label for label, case in common_cases.items()
        if comparable_to_t15(case["active_summary"]["log_monomial_fit"])
    ]
    if own_comparable:
        return (
            "ANF_GRADIENT_GENERAL_PERIODIC_BG",
            "At least one non-73/109 periodic-background oscillator reproduces a T15-like ANF gradient at its own natural period.",
        )
    if common_comparable:
        return (
            "ANF_GRADIENT_HORIZON_ARTIFACT",
            "External rules only reproduce T15-like gradients after oversampling to the common 12-step horizon, not at their own period.",
        )
    return (
        "ANF_GRADIENT_FAMILY_73_109",
        "None of the external non-73/109 candidates reproduces the T15-like ANF gradient at its own period or at the common horizon.",
    )


def fmt_fit(fit: dict[str, Any]) -> str:
    if fit["slope"] is None:
        return "not enough support"
    delta = slope_delta_percent(fit["slope"])
    delta_text = "n/a" if delta is None else f"{delta:.2f}%"
    reliable = "yes" if fit["reliable"] else "no"
    comparable = "yes" if comparable_to_t15(fit) else "no"
    return (
        f"slope={fit['slope']:.6f}, R^2={fit['r2']:.6f}, "
        f"delta_vs_T15={delta_text}, reliable={reliable}, comparable={comparable}"
    )


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Fase 53: External-Family Periodic Background ANF Test",
        "",
        "## Question",
        "",
        "Does the T15-like ANF gradient appear in periodic-background oscillators",
        "outside the `rule_73/rule_109` family, and does it appear at the natural",
        "period rather than only after oversampling to `T_WINDOW=12`?",
        "",
        "All cases use the same 25-input bit-sliced Mobius ANF engine as Fase 52.",
        "The selected ICs are the shortest catalog witnesses at the maximum wide",
        "support (`span=11`) for each `(rule, background, T_local)` group.",
        "",
        "Reference: T15 Fase 45 slope `-0.307283`, R^2 `0.998197`.",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        "## Case Table",
        "",
        "| label | rule | background | IC | T_local | T_WINDOW | active | dist | degree | monomials | active log fit |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for case in data["cases"]:
        active = case["active_summary"]
        lines.append(
            f"| {case['label']} | {case['rule']} | `{case['background']}` | `{case['word']}` | "
            f"{case['T_local']} | {case['t_window']} | {active['count']} | "
            f"{active['distinct_dist_count']} | {active['degree_range']} | "
            f"{active['monomial_range']} | {fmt_fit(active['log_monomial_fit'])} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The distinction between natural-period and common-horizon measurements is",
            "central. A gradient that appears only at `T_WINDOW=12` is treated as a",
            "horizon effect, not as direct evidence that the oscillator's own period",
            "has the same algebraic law as the T15 mechanism.",
            "",
        ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    baseline = load_baseline_module()
    baseline.CASES = CASES
    baseline.verdict = lambda common_cases: ("UNCLASSIFIED", "Fase 53 applies its own classifier.")
    data = baseline.analyze()
    status, reason = classify(data)
    data["status"] = status
    data["verdict_reason"] = reason
    data["reference"] = {
        "slope": REFERENCE_SLOPE,
        "r2": REFERENCE_R2,
        "slope_tolerance_percent": SLOPE_TOLERANCE * 100.0,
    }
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {status}")


if __name__ == "__main__":
    main()
