#!/usr/bin/env python3
"""Fase 54: robustness test inside the rule_73/rule_109 family."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
RESULTS_JSON = OUT_DIR / "periodic_bg_family_robustness_results.json"
REPORT_MD = OUT_DIR / "periodic_bg_family_robustness_report.md"

REFERENCE_SLOPE = -0.307283
REFERENCE_R2 = 0.998197
SLOPE_TOLERANCE_PERCENT = 10.0

CASES = [
    {
        "label": "rule109_bg1011_T6",
        "role": "same_rule_bg_period_variant",
        "rule": 109,
        "background": "1011",
        "T_local": 6,
        "word": "00001001",
    },
    {
        "label": "rule109_bg1101_T10",
        "role": "same_rule_new_bg",
        "rule": 109,
        "background": "1101",
        "T_local": 10,
        "word": "0001000",
    },
    {
        "label": "rule73_bg0010_T6",
        "role": "rule73_period_variant",
        "rule": 73,
        "background": "0010",
        "T_local": 6,
        "word": "1100111",
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
    delta = slope_delta_percent(fit["slope"])
    return delta is not None and delta <= SLOPE_TOLERANCE_PERCENT


def classify(data: dict[str, Any]) -> tuple[str, str]:
    own_cases = [case for case in data["cases"] if case["t_window"] == case["T_local"]]
    comparable_own = [
        case for case in own_cases
        if comparable_to_t15(case["active_summary"]["log_monomial_fit"])
    ]
    reliable_own = [
        case for case in own_cases
        if case["active_summary"]["log_monomial_fit"]["reliable"]
    ]
    if len(comparable_own) >= 2:
        return (
            "ANF_GRADIENT_FAMILY_73_109_ROBUST",
            "At least two additional rule_73/rule_109 witnesses reproduce a T15-like ANF gradient at their natural periods.",
        )
    if len(comparable_own) == 1:
        return (
            "ANF_GRADIENT_FAMILY_73_109_PARTIAL",
            "One additional rule_73/rule_109 witness reproduces a T15-like ANF gradient at its natural period, but the family-level evidence is mixed.",
        )
    if reliable_own:
        return (
            "ANF_GRADIENT_ISOLATED_WITNESS",
            "The selected rule_73/rule_109 witnesses have enough active support, but none reproduces the T15-like gradient at its natural period.",
        )
    return (
        "ANF_GRADIENT_INSUFFICIENT_SUPPORT",
        "The selected rule_73/rule_109 witnesses do not provide enough reliable active-distance support for a family-level robustness test.",
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
        "# Fase 54: rule_73/rule_109 Family ANF Robustness",
        "",
        "## Question",
        "",
        "Does the ANF gradient documented for the T15 mechanism and the non-T15",
        "`rule_109/T=10` witness extend to additional `rule_73/rule_109`",
        "periodic-background witnesses at their own natural periods?",
        "",
        "This test reuses the exact 25-input bit-sliced Mobius ANF engine from",
        "Fases 52--53. The primary criterion is the natural-period horizon",
        "`T_WINDOW=T_local`; the common 12-step horizon is reported as a secondary",
        "comparison.",
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
        "| label | role | rule | background | IC | T_local | T_WINDOW | span | active | dist | degree | monomials | active log fit |",
        "| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for case in data["cases"]:
        active = case["active_summary"]
        lines.append(
            f"| {case['label']} | {case['role']} | {case['rule']} | `{case['background']}` | "
            f"`{case['word']}` | {case['T_local']} | {case['t_window']} | {case['catalog_span']} | "
            f"{active['count']} | {active['distinct_dist_count']} | {active['degree_range']} | "
            f"{active['monomial_range']} | {fmt_fit(active['log_monomial_fit'])} |"
        )
    lines.extend(
        [
            "",
            "## Natural-Period Reading",
            "",
        ]
    )
    own_cases = [case for case in data["cases"] if case["t_window"] == case["T_local"]]
    for case in own_cases:
        fit = case["active_summary"]["log_monomial_fit"]
        lines.append(f"- `{case['label']}`: {fmt_fit(fit)}.")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The robustness claim is evaluated at each oscillator's own period. A",
            "T15-like slope that appears only at the common 12-step horizon is treated",
            "as secondary evidence, not as proof that the natural-period mechanism",
            "itself obeys the same law.",
            "",
        ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    baseline = load_baseline_module()
    baseline.CASES = CASES
    baseline.verdict = lambda common_cases: ("UNCLASSIFIED", "Fase 54 applies its own classifier.")
    data = baseline.analyze()
    status, reason = classify(data)
    data["status"] = status
    data["verdict_reason"] = reason
    data["reference"] = {
        "slope": REFERENCE_SLOPE,
        "r2": REFERENCE_R2,
        "slope_tolerance_percent": SLOPE_TOLERANCE_PERCENT,
    }
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {status}")


if __name__ == "__main__":
    main()
