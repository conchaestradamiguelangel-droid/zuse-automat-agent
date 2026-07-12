#!/usr/bin/env python3
"""Fase 56: rule_109 symmetry and orbit-structure audit."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
CENSUS_JSON = OUT_DIR / "anf_gradient_census_results.json"
REPORT_MD = OUT_DIR / "rule109_symmetry_report.md"
RESULTS_JSON = OUT_DIR / "rule109_symmetry_results.json"

POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}
MONOMIAL_NAMES = ["1", "L", "C", "LC", "R", "LR", "CR", "LCR"]


def rotations(word: str) -> list[str]:
    return [word[idx:] + word[:idx] for idx in range(len(word))]


def canonical_rotation(word: str) -> str:
    return min(rotations(word))


def complement(word: str) -> str:
    return "".join("1" if bit == "0" else "0" for bit in word)


def eca_truth_values(rule: int) -> list[int]:
    # Index order matches ANF monomials: bit0=L, bit1=C, bit2=R.
    values = []
    for idx in range(8):
        left = idx & 1
        center = (idx >> 1) & 1
        right = (idx >> 2) & 1
        eca_key = (left << 2) | (center << 1) | right
        values.append((rule >> eca_key) & 1)
    return values


def mobius_coefficients(values: list[int]) -> list[int]:
    coeffs = values[:]
    n = 3
    for bit in range(n):
        step = 1 << bit
        for mask in range(1 << n):
            if mask & step:
                coeffs[mask] ^= coeffs[mask ^ step]
    return coeffs


def rule_anf(rule: int) -> dict[str, Any]:
    values = eca_truth_values(rule)
    coeffs = mobius_coefficients(values)
    monomials = [MONOMIAL_NAMES[idx] for idx, coeff in enumerate(coeffs) if coeff]
    return {
        "rule": rule,
        "truth_values_LCR_index": values,
        "coefficients": coeffs,
        "monomials": monomials,
        "expression": " XOR ".join(monomials) if monomials else "0",
        "has_center_alone": "C" in monomials,
        "has_lr_without_center": "LR" in monomials,
        "center_monomials": [mono for mono in monomials if "C" in mono],
    }


def load_census() -> dict[str, Any]:
    return json.loads(CENSUS_JSON.read_text(encoding="utf-8"))


def build_case_index(cases: list[dict[str, Any]]) -> dict[tuple[int, str, int], dict[str, Any]]:
    return {(case["rule"], case["background"], case["T_local"]): case for case in cases}


def summarize_related_cases(case: dict[str, Any], index: dict[tuple[int, str, int], dict[str, Any]]) -> dict[str, Any]:
    rule = case["rule"]
    period = case["T_local"]
    bg = case["background"]
    rotation_rows = []
    for rot in rotations(bg):
        related = index.get((rule, rot, period))
        rotation_rows.append(
            {
                "background": rot,
                "present": related is not None,
                "category": related["category"] if related else None,
                "word": related["word"] if related else None,
            }
        )
    comp = complement(bg)
    comp_case = index.get((rule, comp, period))
    return {
        "case": case,
        "canonical_rotation": canonical_rotation(bg),
        "rotations": rotation_rows,
        "complement": {
            "background": comp,
            "present": comp_case is not None,
            "category": comp_case["category"] if comp_case else None,
            "word": comp_case["word"] if comp_case else None,
        },
    }


def cross_rule_rows(positive_cases: list[dict[str, Any]], index: dict[tuple[int, str, int], dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for case in positive_cases:
        if case["rule"] != 109:
            continue
        counterpart = index.get((73, case["background"], case["T_local"]))
        rows.append(
            {
                "rule109_case": case,
                "rule73_present": counterpart is not None,
                "rule73_category": counterpart["category"] if counterpart else None,
                "rule73_word": counterpart["word"] if counterpart else None,
            }
        )
    return rows


def classify_orbit(positive_related: list[dict[str, Any]]) -> str:
    positives = [row for row in positive_related if row["case"]["category"] in POSITIVE_CATEGORIES]
    if not positives:
        return "NOT_SUPPORTED"
    by_orbit = Counter(row["canonical_rotation"] for row in positives)
    most_common_count = by_orbit.most_common(1)[0][1]
    if most_common_count == len(positives):
        return "CYCLIC_ORBIT_SUPPORTED"
    if most_common_count >= max(2, len(positives) // 2):
        return "PARTIAL"
    return "NOT_SUPPORTED"


def classify_rule_anf(anf73: dict[str, Any], anf109: dict[str, Any]) -> str:
    ok109 = (
        not anf109["has_center_alone"]
        and not anf109["has_lr_without_center"]
        and {"LC", "CR", "LCR"}.issubset(set(anf109["monomials"]))
    )
    different73 = anf73["has_center_alone"] and anf73["has_lr_without_center"]
    return "RULE109_CENTER_MEDIATED_CONFIRMED" if ok109 and different73 else "NOT_CONFIRMED"


def classify_cross_rule(rows: list[dict[str, Any]]) -> str:
    present_rows = [row for row in rows if row["rule73_present"]]
    if not present_rows:
        return "NO_SHARED_BACKGROUND_CASES"
    if all(row["rule73_category"] not in POSITIVE_CATEGORIES for row in present_rows):
        return "RULE109_SPECIFIC_ON_SHARED_BACKGROUNDS"
    return "NOT_RULE_SPECIFIC"


def classify_overall(orbit_status: str, rule_anf_status: str, cross_rule_status: str) -> str:
    if (
        rule_anf_status == "RULE109_CENTER_MEDIATED_CONFIRMED"
        and cross_rule_status == "RULE109_SPECIFIC_ON_SHARED_BACKGROUNDS"
        and orbit_status in {"CYCLIC_ORBIT_SUPPORTED", "PARTIAL"}
    ):
        return "RULE109_SYMMETRY_MECHANISM_CANDIDATE"
    if rule_anf_status == "NOT_CONFIRMED" and cross_rule_status == "NOT_RULE_SPECIFIC":
        return "INCONCLUSIVE"
    return "MIXED_EVIDENCE"


def analyze() -> dict[str, Any]:
    census = load_census()
    cases = census["case_summaries"]
    index = build_case_index(cases)
    positive_cases = [case for case in cases if case["category"] in POSITIVE_CATEGORIES]
    positive_related = [summarize_related_cases(case, index) for case in positive_cases]
    anf73 = rule_anf(73)
    anf109 = rule_anf(109)
    cross_rows = cross_rule_rows(positive_cases, index)
    orbit_status = classify_orbit(positive_related)
    rule_anf_status = classify_rule_anf(anf73, anf109)
    cross_rule_status = classify_cross_rule(cross_rows)
    overall_status = classify_overall(orbit_status, rule_anf_status, cross_rule_status)
    return {
        "source": str(CENSUS_JSON.name),
        "positive_categories": sorted(POSITIVE_CATEGORIES),
        "positive_cases": positive_cases,
        "positive_related": positive_related,
        "rule_anf": {
            "rule_73": anf73,
            "rule_109": anf109,
        },
        "cross_rule_rows": cross_rows,
        "statuses": {
            "orbit_symmetry_status": orbit_status,
            "rule_anf_status": rule_anf_status,
            "cross_rule_status": cross_rule_status,
            "overall_status": overall_status,
        },
    }


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Fase 56: rule_109 Symmetry and Orbit Structure Audit",
        "",
        "## Question",
        "",
        "Why do the non-T15 ANF-gradient witnesses found in Fase 55 concentrate in",
        "`rule_109` rather than spreading across the full `rule_73/rule_109` family",
        "or the external rules in the catalog?",
        "",
        "This audit performs no new ANF simulation. It uses the Fase 55 census JSON",
        "and analyzes background rotations/complements, rule-level ANF, and direct",
        "cross-rule comparisons.",
        "",
        "## Status",
        "",
    ]
    for key, value in data["statuses"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Positive Cases from Fase 55",
            "",
            "| case | category | canonical rotation | complement in census |",
            "| --- | --- | --- | --- |",
        ]
    )
    for row in data["positive_related"]:
        case = row["case"]
        comp = row["complement"]
        comp_text = (
            f"`{comp['background']}` -> `{comp['category']}`"
            if comp["present"]
            else f"`{comp['background']}` -> absent"
        )
        lines.append(
            f"| `rule_{case['rule']}/bg={case['background']}/T={case['T_local']}/word={case['word']}` | "
            f"`{case['category']}` | `{row['canonical_rotation']}` | {comp_text} |"
        )
    lines.extend(
        [
            "",
            "## Rotation Orbits",
            "",
        ]
    )
    for row in data["positive_related"]:
        case = row["case"]
        lines.append(f"### `rule_{case['rule']}/bg={case['background']}/T={case['T_local']}`")
        for rot in row["rotations"]:
            if rot["present"]:
                lines.append(f"- `{rot['background']}`: `{rot['category']}` (word `{rot['word']}`)")
            else:
                lines.append(f"- `{rot['background']}`: absent from census")
        lines.append("")
    anf73 = data["rule_anf"]["rule_73"]
    anf109 = data["rule_anf"]["rule_109"]
    lines.extend(
        [
            "## Rule-Level ANF",
            "",
            "| rule | ANF expression | center alone? | LR without center? | center monomials |",
            "| ---: | --- | --- | --- | --- |",
            f"| 73 | `{anf73['expression']}` | `{anf73['has_center_alone']}` | `{anf73['has_lr_without_center']}` | `{anf73['center_monomials']}` |",
            f"| 109 | `{anf109['expression']}` | `{anf109['has_center_alone']}` | `{anf109['has_lr_without_center']}` | `{anf109['center_monomials']}` |",
            "",
            "`rule_109` has no isolated center monomial and no `LR` monomial without",
            "the center. Its center dependence appears only through interactions",
            "(`LC`, `CR`, `LCR`). By contrast, `rule_73` contains `C` alone and `LR`",
            "without the center.",
            "",
            "## Cross-Rule Comparisons",
            "",
            "| rule_109 positive case | matching rule_73 case |",
            "| --- | --- |",
        ]
    )
    for row in data["cross_rule_rows"]:
        case = row["rule109_case"]
        if row["rule73_present"]:
            rhs = f"`rule_73/bg={case['background']}/T={case['T_local']}/word={row['rule73_word']}` -> `{row['rule73_category']}`"
        else:
            rhs = "absent from census"
        lines.append(
            f"| `rule_109/bg={case['background']}/T={case['T_local']}/word={case['word']}` -> `{case['category']}` | {rhs} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The cyclic-orbit evidence is partial: several witnesses lie in the rotation",
            "orbit of `0011`, but the `rule_109/bg=1011/T10` baseline belongs to a",
            "different rotation orbit. The algebraic contrast is sharper: `rule_109`",
            "mediates center dependence through neighbor interactions, whereas",
            "`rule_73` has direct center and neighbor-only terms. The cross-rule table",
            "shows that where matching `rule_73` cases exist on the same backgrounds",
            "and periods, they do not become positive witnesses.",
            "",
            "This supports a rule_109-specific mechanism candidate, but it is not a",
            "closed proof: background orbit structure and rule-level ANF both appear",
            "relevant.",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    data = analyze()
    write_report(data)
    print(f"Wrote {REPORT_MD}")
    print(f"Wrote {RESULTS_JSON}")
    for key, value in data["statuses"].items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
