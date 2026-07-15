#!/usr/bin/env python3
"""Fase 63: algebraic interventions around rule_109.

This phase tests four minimal ANF edits of rule_109:

    rule_109 = 1 XOR L XOR LC XOR R XOR CR XOR LCR

The goal is not to sweep all ECA rules again, but to ask whether the specific
residual bg=1100/T=8/word=00000110 can be probed by local algebraic
interventions.  The script first performs a cheap preflight:

1. verify the intended local ANF edits;
2. check whether the synthetic rules are already present in the Fase 55
   periodic-background catalog;
3. run a minimal oscillator sweep for each synthetic rule on bg=1100 only.

If stationary oscillators are found, it reuses the exact ANF baseline engine
from Fases 52--55 on the strongest comparable witness for each synthetic rule.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
SWEEP_SCRIPT = OUT_DIR / "sweep_periodic_background_oscillators.py"
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
CATALOG_JSONL = OUT_DIR / "periodic_background_oscillator_results.jsonl"
RESULTS_JSON = OUT_DIR / "rule109_algebraic_intervention_results.json"
REPORT_MD = OUT_DIR / "rule109_algebraic_intervention_report.md"

TARGET_BACKGROUND = "1100"
TARGET_CASE = {
    "rule": 109,
    "background": "1100",
    "T_local": 8,
    "word": "00000110",
    "category": "HORIZON_ACCEPTABLE",
    "role": "residual_target",
}

REFERENCE_SLOPE = -0.307283
SLOPE_TOLERANCE_PERCENT = 10.0
COMMON_T_WINDOW = 12
MIN_COMPARABLE_SPAN = 11

INTERVENTIONS = [
    {
        "name": "remove_LC",
        "rule": 173,
        "operation": "remove monomial LC from rule_109",
        "expected_monomials": ["1", "L", "R", "CR", "LCR"],
    },
    {
        "name": "remove_CR",
        "rule": 229,
        "operation": "remove monomial CR from rule_109",
        "expected_monomials": ["1", "L", "LC", "R", "LCR"],
    },
    {
        "name": "add_C",
        "rule": 161,
        "operation": "add isolated C monomial to rule_109",
        "expected_monomials": ["1", "L", "C", "LC", "R", "CR", "LCR"],
    },
    {
        "name": "add_LR",
        "rule": 205,
        "operation": "add LR monomial without center to rule_109",
        "expected_monomials": ["1", "L", "LC", "LR", "R", "CR", "LCR"],
    },
]

MONOMIALS = [
    ("1", 0),
    ("R", 1),
    ("C", 2),
    ("CR", 3),
    ("L", 4),
    ("LR", 5),
    ("LC", 6),
    ("LCR", 7),
]


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def rule_truth_table(rule: int) -> list[int]:
    return [(rule >> idx) & 1 for idx in range(8)]


def anf_coefficients_3var(rule: int) -> list[int]:
    coeffs = rule_truth_table(rule)
    coeffs = coeffs[:]
    for bit in range(3):
        step = 1 << bit
        for mask in range(8):
            if mask & step:
                coeffs[mask] ^= coeffs[mask ^ step]
    return coeffs


def monomial_names(rule: int) -> list[str]:
    coeffs = anf_coefficients_3var(rule)
    return [name for name, mask in MONOMIALS if coeffs[mask]]


def classify_center_structure(names: list[str]) -> dict[str, Any]:
    c_alone = "C" in names
    lr_no_center = "LR" in names
    center_interactions = [name for name in ("LC", "CR", "LCR") if name in names]
    center_mediated = not c_alone and not lr_no_center
    strict_center_mediated = center_mediated and bool(center_interactions)
    return {
        "C_alone": c_alone,
        "LR_no_center": lr_no_center,
        "center_interactions": center_interactions,
        "center_mediated": center_mediated,
        "strict_center_mediated": strict_center_mediated,
    }


def catalog_presence(catalog: list[dict[str, Any]], rule: int) -> dict[str, Any]:
    rows = [row for row in catalog if row.get("rule") == rule]
    stationary = [row for row in rows if row.get("kind") == "stationary"]
    fase55_census = [
        row for row in stationary
        if row.get("period_T") not in {2, 15}
        and row.get("span", 0) >= MIN_COMPARABLE_SPAN
    ]
    return {
        "present": bool(rows),
        "row_count": len(rows),
        "stationary_count": len(stationary),
        "fase55_census_present": bool(fase55_census),
        "fase55_census_count": len(fase55_census),
        "backgrounds": sorted({row.get("background") for row in rows}),
        "periods": sorted({row.get("period_T") for row in rows if "period_T" in row}),
    }


def sweep_rule_on_background(rule: int, background: str) -> dict[str, Any]:
    sweep = import_module(SWEEP_SCRIPT, "periodic_background_sweep_fase63")
    bg_frames = sweep.background_orbit(rule, background)
    stationary_hits = []
    moving_hits = []
    aliases = []
    processed = 0
    for word_len, word_value, word in sweep.ic_words():
        processed += 1
        shapes = sweep.simulate_diff_shapes(rule, bg_frames, word_value, word_len)
        if not shapes:
            continue
        stationary = sweep.detect_stationary(shapes)
        moving, alias = sweep.detect_moving(shapes)
        if stationary is not None:
            stationary_hits.append(
                {
                    "rule": rule,
                    "background": background,
                    "word_len": word_len,
                    "word": word,
                    **stationary,
                }
            )
        if moving is not None:
            moving_hits.append(
                {
                    "rule": rule,
                    "background": background,
                    "word_len": word_len,
                    "word": word,
                    **moving,
                }
            )
        if alias is not None:
            aliases.append(
                {
                    "rule": rule,
                    "background": background,
                    "word_len": word_len,
                    "word": word,
                    **alias,
                }
            )
    stationary_hits.sort(key=lambda row: (-row["span"], row["period_T"], row["word_len"], row["word"]))
    moving_hits.sort(key=lambda row: (row["period_T"], row["word_len"], row["word"]))
    return {
        "processed_ic_words": processed,
        "stationary_hits": stationary_hits,
        "moving_hits": moving_hits,
        "alias_count": len(aliases),
    }


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


def measure_synthetic_witness(hit: dict[str, Any]) -> dict[str, Any]:
    baseline = import_module(BASELINE_SCRIPT, "periodic_bg_anf_baseline_fase63")
    base = baseline.load_base_module()
    popcount16 = np.array([int(i).bit_count() for i in range(1 << 16)], dtype=np.uint8)
    synthetic_catalog = [hit]
    case = {
        "label": f"rule{hit['rule']}_bg{hit['background']}_T{hit['period_T']}_w{hit['word']}",
        "role": "synthetic_intervention",
        "rule": hit["rule"],
        "background": hit["background"],
        "T_local": hit["period_T"],
        "word": hit["word"],
    }
    measurements = []
    for t_window in sorted({case["T_local"], COMMON_T_WINDOW}):
        result = baseline.analyze_case(base, synthetic_catalog, popcount16, case, t_window)
        fit = result["active_summary"]["log_monomial_fit"]
        result["comparable_to_t15"] = comparable_to_t15(fit)
        result["slope_delta_percent"] = slope_delta_percent(fit["slope"])
        measurements.append(result)
    return {
        "case": case,
        "catalog_record": hit,
        "measurements": measurements,
    }


def classify_status(interventions: list[dict[str, Any]]) -> tuple[str, str]:
    comparable = []
    stationary_any = []
    no_stationary = []
    for item in interventions:
        hits = item["bg1100_sweep"]["stationary_hits"]
        if hits:
            stationary_any.append(item["name"])
        else:
            no_stationary.append(item["name"])
        for measured in item.get("anf_measurements", []):
            if any(row["comparable_to_t15"] for row in measured["measurements"]):
                comparable.append(item["name"])
                break
    if comparable:
        return (
            "ALGEBRAIC_INTERVENTION_WITNESS_FOUND",
            "At least one minimal ANF intervention has a bg=1100 stationary witness with a T15-like ANF gradient.",
        )
    if stationary_any:
        return (
            "ALGEBRAIC_INTERVENTION_NO_GRADIENT",
            "Some minimal ANF interventions have bg=1100 stationary witnesses, but none reproduces a T15-like gradient.",
        )
    return (
        "ALGEBRAIC_INTERVENTION_PREFLIGHT_BLOCKED",
        "None of the four minimal ANF interventions has a stationary oscillator on bg=1100 in the minimal sweep, so the residual intervention test cannot be run directly.",
    )


def build_report(data: dict[str, Any]) -> str:
    lines = [
        "# Fase 63: rule_109 Algebraic Intervention Preflight",
        "",
        "## Question",
        "",
        "Do minimal local-ANF edits around `rule_109` create or destroy the",
        "`rule_109/bg=1100/T=8/word=00000110` residual mechanism?",
        "",
        "This phase first verifies the four algebraic interventions and then runs",
        "a minimal oscillator preflight on `bg=1100`. ANF cone measurements are",
        "only executed for synthetic rules that actually have stationary",
        "oscillators on that background.",
        "",
        "## Status",
        "",
        f"`{data['status']}`",
        "",
        data["verdict_reason"],
        "",
        "## Local ANF interventions",
        "",
        "| name | rule | operation | ANF monomials | expected ok | center mediated | strict | raw catalog | Fase 55 census |",
        "| --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in data["interventions"]:
        lines.append(
            f"| {item['name']} | {item['rule']} | {item['operation']} | "
            f"`{' XOR '.join(item['anf_monomials'])}` | {str(item['expected_ok']).lower()} | "
            f"{str(item['center_structure']['center_mediated']).lower()} | "
            f"{str(item['center_structure']['strict_center_mediated']).lower()} | "
            f"{str(item['catalog_presence']['present']).lower()} | "
            f"{str(item['catalog_presence']['fase55_census_present']).lower()} |"
        )
    lines.extend(
        [
            "",
            "## bg=1100 preflight",
            "",
            "| name | rule | processed ICs | stationary hits | max span | periods | comparable hits measured |",
            "| --- | ---: | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for item in data["interventions"]:
        hits = item["bg1100_sweep"]["stationary_hits"]
        periods = sorted({hit["period_T"] for hit in hits})
        max_span = max((hit["span"] for hit in hits), default=0)
        measured_count = len(item.get("anf_measurements", []))
        lines.append(
            f"| {item['name']} | {item['rule']} | {item['bg1100_sweep']['processed_ic_words']} | "
            f"{len(hits)} | {max_span} | {periods} | {measured_count} |"
        )
    lines.extend(["", "## Measured synthetic witnesses", ""])
    any_measured = False
    for item in data["interventions"]:
        for measured in item.get("anf_measurements", []):
            any_measured = True
            lines.append(f"### {item['name']} / rule_{item['rule']} / `{measured['case']['word']}`")
            lines.append("")
            lines.append("| T_WINDOW | active | dist classes | slope | R^2 | delta vs T15 | comparable |")
            lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | --- |")
            for row in measured["measurements"]:
                fit = row["active_summary"]["log_monomial_fit"]
                slope = "NA" if fit["slope"] is None else f"{fit['slope']:.6f}"
                r2 = "NA" if fit["r2"] is None else f"{fit['r2']:.6f}"
                delta = "NA" if row["slope_delta_percent"] is None else f"{row['slope_delta_percent']:.2f}%"
                lines.append(
                    f"| {row['t_window']} | {row['active_summary']['count']} | "
                    f"{row['active_summary']['distinct_dist_count']} | {slope} | {r2} | "
                    f"{delta} | {str(row['comparable_to_t15']).lower()} |"
                )
            lines.append("")
    if not any_measured:
        lines.append("No stationary bg=1100 synthetic witness passed the measurement preflight.")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "This is a targeted intervention preflight, not an exhaustive search over",
            "all center-mediated rules. If a synthetic rule lacks a stationary",
            "`bg=1100` oscillator, the residual cannot be tested directly under the",
            "same periodic-background protocol. Such a failure is still informative:",
            "it means the minimal algebraic edit destroys the comparable oscillator",
            "support before the ANF-gradient question can even be asked.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    catalog = load_jsonl(CATALOG_JSONL)
    interventions = []
    for spec in INTERVENTIONS:
        names = monomial_names(spec["rule"])
        item = {
            **spec,
            "truth_table": rule_truth_table(spec["rule"]),
            "anf_monomials": names,
            "expected_ok": set(names) == set(spec["expected_monomials"]),
            "center_structure": classify_center_structure(names),
            "catalog_presence": catalog_presence(catalog, spec["rule"]),
        }
        sweep = sweep_rule_on_background(spec["rule"], TARGET_BACKGROUND)
        item["bg1100_sweep"] = sweep
        strong_hits = [
            hit for hit in sweep["stationary_hits"]
            if hit["span"] >= MIN_COMPARABLE_SPAN
        ]
        if strong_hits:
            item["anf_measurements"] = [measure_synthetic_witness(strong_hits[0])]
        else:
            item["anf_measurements"] = []
        interventions.append(item)

    status, reason = classify_status(interventions)
    data = {
        "phase": 63,
        "status": status,
        "verdict_reason": reason,
        "target_case": TARGET_CASE,
        "reference": {
            "slope": REFERENCE_SLOPE,
            "slope_tolerance_percent": SLOPE_TOLERANCE_PERCENT,
            "common_t_window": COMMON_T_WINDOW,
            "min_comparable_span": MIN_COMPARABLE_SPAN,
        },
        "interventions": interventions,
    }
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {status}")


if __name__ == "__main__":
    main()
