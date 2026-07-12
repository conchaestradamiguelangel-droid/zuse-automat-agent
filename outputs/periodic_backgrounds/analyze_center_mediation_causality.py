#!/usr/bin/env python3
"""Fase 57: causal audit of the rule_109 center-mediated ANF candidate.

This phase does not run new ECA/ANF simulations. It computes the local ANF
structure of all 256 ECA rules, joins that rule-level classification to the
Fase 55 periodic-background ANF-gradient census, and tests whether the
center-mediated structure is necessary and/or sufficient inside that finite
catalog.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
CENSUS_JSON = OUT_DIR / "anf_gradient_census_results.json"
RESULTS_JSON = OUT_DIR / "center_mediation_causality_results.json"
REPORT_MD = OUT_DIR / "center_mediation_causality_report.md"

MONOMIAL_NAMES = ["1", "L", "C", "LC", "R", "LR", "CR", "LCR"]
POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}


def eca_truth_values(rule: int) -> list[int]:
    """Truth values indexed by ANF mask: bit0=L, bit1=C, bit2=R."""
    values = []
    for mask in range(8):
        left = mask & 1
        center = (mask >> 1) & 1
        right = (mask >> 2) & 1
        eca_key = (left << 2) | (center << 1) | right
        values.append((rule >> eca_key) & 1)
    return values


def mobius_coefficients(values: list[int]) -> list[int]:
    coeffs = values[:]
    for bit in range(3):
        step = 1 << bit
        for mask in range(8):
            if mask & step:
                coeffs[mask] ^= coeffs[mask ^ step]
    return coeffs


def rule_anf(rule: int) -> dict[str, Any]:
    values = eca_truth_values(rule)
    coeffs = mobius_coefficients(values)
    monomials = [MONOMIAL_NAMES[idx] for idx, coeff in enumerate(coeffs) if coeff]
    monomial_set = set(monomials)
    c_interactions = sorted(m for m in monomials if "C" in m and m != "C")
    c_alone = "C" in monomial_set
    lr_no_center = "LR" in monomial_set
    center_mediated = (not c_alone) and (not lr_no_center)
    strict_center_mediated = center_mediated and bool(c_interactions)
    return {
        "rule": rule,
        "truth_values_LCR_index": values,
        "coefficients": coeffs,
        "monomials": monomials,
        "expression": " XOR ".join(monomials) if monomials else "0",
        "C_alone": c_alone,
        "LR_no_center": lr_no_center,
        "center_interactions": c_interactions,
        "center_mediated": center_mediated,
        "strict_center_mediated": strict_center_mediated,
    }


def load_census() -> dict[str, Any]:
    return json.loads(CENSUS_JSON.read_text(encoding="utf-8"))


def summarize_catalog(cases: list[dict[str, Any]], anf_by_rule: dict[int, dict[str, Any]]) -> dict[str, Any]:
    catalog_rules = sorted({case["rule"] for case in cases})
    by_rule: dict[int, dict[str, Any]] = {}
    for rule in catalog_rules:
        rule_cases = [case for case in cases if case["rule"] == rule]
        positive_cases = [case for case in rule_cases if case["category"] in POSITIVE_CATEGORIES]
        by_rule[rule] = {
            "rule": rule,
            "case_count": len(rule_cases),
            "category_counts": dict(Counter(case["category"] for case in rule_cases)),
            "positive_count": len(positive_cases),
            "positive_cases": positive_cases,
            "anf": anf_by_rule[rule],
        }
    return {
        "catalog_rules": catalog_rules,
        "by_rule": by_rule,
        "rule_counts": dict(Counter(case["rule"] for case in cases)),
        "category_counts": dict(Counter(case["category"] for case in cases)),
    }


def classify_need_and_sufficiency(cases: list[dict[str, Any]], anf_by_rule: dict[int, dict[str, Any]]) -> dict[str, Any]:
    positive_cases = [case for case in cases if case["category"] in POSITIVE_CATEGORIES]
    negative_cases = [case for case in cases if case["category"] not in POSITIVE_CATEGORIES]
    positive_non_mediated = [
        case for case in positive_cases if not anf_by_rule[case["rule"]]["center_mediated"]
    ]
    mediated_negative = [
        case for case in negative_cases if anf_by_rule[case["rule"]]["center_mediated"]
    ]
    strict_mediated_negative = [
        case for case in negative_cases if anf_by_rule[case["rule"]]["strict_center_mediated"]
    ]
    positives_all_center_mediated = len(positive_non_mediated) == 0
    all_center_mediated_cases_positive = len(mediated_negative) == 0
    necessity_status = (
        "CENTER_MEDIATION_NECESSARY_IN_CATALOG"
        if positives_all_center_mediated
        else "CENTER_MEDIATION_NOT_NECESSARY_IN_CATALOG"
    )
    sufficiency_status = (
        "CENTER_MEDIATION_SUFFICIENT_IN_CATALOG"
        if all_center_mediated_cases_positive
        else "CENTER_MEDIATION_NOT_SUFFICIENT_IN_CATALOG"
    )
    if positives_all_center_mediated and all_center_mediated_cases_positive:
        overall_status = "CAUSAL_CANDIDATE_NECESSARY_AND_SUFFICIENT_IN_CATALOG"
    elif positives_all_center_mediated and not all_center_mediated_cases_positive:
        overall_status = "CAUSAL_CANDIDATE_NECESSARY_NOT_SUFFICIENT"
    elif not positives_all_center_mediated:
        overall_status = "FALSIFIED_AS_NECESSARY"
    else:
        overall_status = "CORRELATION_ONLY"
    return {
        "positive_categories": sorted(POSITIVE_CATEGORIES),
        "positive_case_count": len(positive_cases),
        "negative_case_count": len(negative_cases),
        "positive_non_center_mediated": positive_non_mediated,
        "center_mediated_negative_cases": mediated_negative,
        "strict_center_mediated_negative_cases": strict_mediated_negative,
        "necessity_status": necessity_status,
        "sufficiency_status": sufficiency_status,
        "overall_status": overall_status,
        "methodological_limits": [
            "Necessity and sufficiency are evaluated only inside the Fase 55 catalog.",
            "Sufficiency is empirical over observed catalog cases, not universal over all ECA worlds.",
            "A closed causal proof would require intervention or synthetic-rule construction.",
        ],
    }


def analyze() -> dict[str, Any]:
    census = load_census()
    cases = census["case_summaries"]
    anf_all_rules = {rule: rule_anf(rule) for rule in range(256)}
    catalog = summarize_catalog(cases, anf_all_rules)
    causal = classify_need_and_sufficiency(cases, anf_all_rules)
    center_mediated_rules = [rule for rule, anf in anf_all_rules.items() if anf["center_mediated"]]
    strict_center_mediated_rules = [
        rule for rule, anf in anf_all_rules.items() if anf["strict_center_mediated"]
    ]
    return {
        "source": str(CENSUS_JSON.name),
        "definition": {
            "C_alone": "C appears as isolated ANF monomial",
            "LR_no_center": "LR appears as ANF monomial without C",
            "center_mediated": "C_alone is false AND LR_no_center is false",
            "strict_center_mediated": "center_mediated is true and C appears in at least one interaction monomial",
        },
        "all_rules": {
            "count": 256,
            "center_mediated_count": len(center_mediated_rules),
            "strict_center_mediated_count": len(strict_center_mediated_rules),
            "center_mediated_rules": center_mediated_rules,
            "strict_center_mediated_rules": strict_center_mediated_rules,
            "anf": {str(rule): anf for rule, anf in anf_all_rules.items()},
        },
        "catalog": catalog,
        "causal_tests": causal,
    }


def case_label(case: dict[str, Any]) -> str:
    return f"rule_{case['rule']}/bg={case['background']}/T={case['T_local']}/word={case['word']}"


def write_report(data: dict[str, Any]) -> None:
    catalog = data["catalog"]
    causal = data["causal_tests"]
    lines = [
        "# Fase 57: Center-Mediated ANF Causality Audit",
        "",
        "## Question",
        "",
        "Is the center-mediated local ANF structure identified in Fase 56 necessary",
        "and/or sufficient for the ANF-gradient witnesses found in the Fase 55",
        "periodic-background catalog, or is it only correlated with them?",
        "",
        "This phase runs no new ECA or cone simulations. It computes the 3-variable",
        "ANF of all 256 ECA rules and joins that rule-level classification to the",
        "existing Fase 55 census.",
        "",
        "## Definition",
        "",
        "- `C_alone`: the isolated `C` monomial appears.",
        "- `LR_no_center`: the `LR` monomial appears without the center.",
        "- `center_mediated`: `C_alone=False` and `LR_no_center=False`.",
        "- `strict_center_mediated`: `center_mediated=True` and at least one center",
        "  interaction monomial exists.",
        "",
        "## 256-Rule Summary",
        "",
        f"- ECA rules analyzed: {data['all_rules']['count']}",
        f"- `center_mediated=True`: {data['all_rules']['center_mediated_count']} rules",
        f"- `strict_center_mediated=True`: {data['all_rules']['strict_center_mediated_count']} rules",
        "",
        "## Catalog Rule Table",
        "",
        "| rule | expression | C_alone | LR_no_center | center_mediated | strict | cases | positives | categories |",
        "| --- | --- | --- | --- | --- | --- | ---: | ---: | --- |",
    ]
    for rule in catalog["catalog_rules"]:
        row = catalog["by_rule"][rule]
        anf = row["anf"]
        cats = ", ".join(f"{key}:{value}" for key, value in sorted(row["category_counts"].items()))
        lines.append(
            f"| `{rule}` | `{anf['expression']}` | `{anf['C_alone']}` | "
            f"`{anf['LR_no_center']}` | `{anf['center_mediated']}` | "
            f"`{anf['strict_center_mediated']}` | {row['case_count']} | "
            f"{row['positive_count']} | {cats} |"
        )
    lines.extend(
        [
            "",
            "## Necessity Test",
            "",
            f"- Positive cases: {causal['positive_case_count']}",
            f"- Positive cases with `center_mediated=False`: {len(causal['positive_non_center_mediated'])}",
            f"- Status: `{causal['necessity_status']}`",
            "",
        ]
    )
    if causal["positive_non_center_mediated"]:
        for case in causal["positive_non_center_mediated"]:
            lines.append(f"- Counterexample: `{case_label(case)}` -> `{case['category']}`")
        lines.append("")
    else:
        lines.append("All positive witnesses in the catalog occur in rules classified as `center_mediated=True`.")
        lines.append("")
    lines.extend(
        [
            "## Sufficiency Test",
            "",
            f"- Non-positive cases: {causal['negative_case_count']}",
            f"- Non-positive cases with `center_mediated=True`: {len(causal['center_mediated_negative_cases'])}",
            f"- Non-positive cases with `strict_center_mediated=True`: {len(causal['strict_center_mediated_negative_cases'])}",
            f"- Status: `{causal['sufficiency_status']}`",
            "",
            "Representative non-positive center-mediated cases:",
            "",
        ]
    )
    for case in causal["center_mediated_negative_cases"][:12]:
        lines.append(f"- `{case_label(case)}` -> `{case['category']}`")
    if len(causal["center_mediated_negative_cases"]) > 12:
        lines.append(f"- ... {len(causal['center_mediated_negative_cases']) - 12} more")
    lines.extend(
        [
            "",
            "## Overall Verdict",
            "",
            f"`{causal['overall_status']}`.",
            "",
            "Interpretation: center mediation is necessary for the positive witnesses",
            "inside the Fase 55 catalog, but it is not sufficient. Several",
            "center-mediated rules or cases do not become ANF-gradient witnesses.",
            "Therefore, the Fase 56 candidate survives as a necessary structural",
            "condition in the catalog, but not as a complete causal explanation.",
            "",
            "## Methodological Limits",
            "",
        ]
    )
    for limit in causal["methodological_limits"]:
        lines.append(f"- {limit}")
    lines.append("")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = analyze()
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['causal_tests']['overall_status']}")


if __name__ == "__main__":
    main()
