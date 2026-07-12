#!/usr/bin/env python3
"""Fase 59: alignment descriptors for the rule_109/T=8 residual.

This phase uses existing Fase 55 census cases only. The verdict is based on the
three rule_109/T=8 cases:

- bg=0011, word=1000010  -> NEGATIVE
- bg=0110, word=0000011  -> HORIZON_ACCEPTABLE
- bg=1100, word=00000110 -> HORIZON_ACCEPTABLE

No ECA or ANF simulation is run.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
CENSUS_JSON = OUT_DIR / "anf_gradient_census_results.json"
RESULTS_JSON = OUT_DIR / "rule109_t8_alignment_results.json"
REPORT_MD = OUT_DIR / "rule109_t8_alignment_report.md"

POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}
ORBIT_0011_PHASES = {
    "0011": 0,
    "0110": 1,
    "1100": 2,
    "1001": 3,
}


def load_census() -> dict[str, Any]:
    return json.loads(CENSUS_JSON.read_text(encoding="utf-8"))


def rotations(word: str) -> list[str]:
    return [word[idx:] + word[:idx] for idx in range(len(word))]


def canonical_rotation(word: str) -> str:
    return min(rotations(word))


def periodic_bits(background: str, length: int, start: int = 0) -> str:
    return "".join(background[(start + idx) % len(background)] for idx in range(length))


def active_positions(word: str) -> list[int]:
    return [idx for idx, bit in enumerate(word) if bit == "1"]


def bits_at_positions(bits: str, positions: list[int]) -> str:
    return "".join(bits[idx] for idx in positions)


def xor_bits(a: str, b: str) -> str:
    if len(a) != len(b):
        raise ValueError(f"length mismatch: {len(a)} != {len(b)}")
    return "".join("1" if x != y else "0" for x, y in zip(a, b))


def support_offsets(positions: list[int], period: int = 4) -> list[int]:
    return sorted({pos % period for pos in positions})


def circular_span(positions: list[int]) -> int | None:
    if not positions:
        return None
    return max(positions) - min(positions) + 1


def describe_case(case: dict[str, Any]) -> dict[str, Any]:
    bg = case["background"]
    word = case["word"]
    bg_window = periodic_bits(bg, len(word))
    ic_positions = active_positions(word)
    bg_at_ic = bits_at_positions(bg_window, ic_positions)
    xor_defect = xor_bits(word, bg_window)
    defect_positions = active_positions(xor_defect)
    return {
        **case,
        "positive": case["category"] in POSITIVE_CATEGORIES,
        "bg_phase_in_0011_orbit": ORBIT_0011_PHASES.get(bg),
        "canonical_background": canonical_rotation(bg),
        "ic_length": len(word),
        "ic_active_bits": ic_positions,
        "ic_active_offsets_mod4": support_offsets(ic_positions),
        "ic_support_size": len(ic_positions),
        "ic_span": circular_span(ic_positions),
        "background_window": bg_window,
        "bg_at_ic": bg_at_ic,
        "bg_at_ic_ones": bg_at_ic.count("1"),
        "xor_defect": xor_defect,
        "defect_active_bits": defect_positions,
        "defect_phase_offset": support_offsets(defect_positions),
        "defect_support_size": len(defect_positions),
        "defect_span": circular_span(defect_positions),
        "defect_weight_by_mod4": dict(Counter(pos % 4 for pos in defect_positions)),
        "ic_weight_by_mod4": dict(Counter(pos % 4 for pos in ic_positions)),
    }


def descriptor_values(rows: list[dict[str, Any]], keys: list[str]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key in keys:
        values = {}
        for row in rows:
            value = row[key]
            if isinstance(value, list):
                value = tuple(value)
            elif isinstance(value, dict):
                value = tuple(sorted(value.items()))
            values[row["background"]] = value
        neg_values = {values[row["background"]] for row in rows if not row["positive"]}
        pos_values = {values[row["background"]] for row in rows if row["positive"]}
        separates = len(neg_values) == 1 and neg_values.isdisjoint(pos_values)
        pos_constant = len(pos_values) == 1
        out[key] = {
            "values_by_background": values,
            "negative_values": sorted(map(str, neg_values)),
            "positive_values": sorted(map(str, pos_values)),
            "negative_separated_from_positive": separates,
            "positive_constant": pos_constant,
        }
    return out


def analyze() -> dict[str, Any]:
    census = load_census()
    all_rule109 = [case for case in census["case_summaries"] if case["rule"] == 109]
    t8_cases = [
        describe_case(case)
        for case in all_rule109
        if case["T_local"] == 8 and case["background"] in {"0011", "0110", "1100"}
    ]
    t8_cases.sort(key=lambda row: row["background"])
    all_rule109_described = [describe_case(case) for case in all_rule109]
    keys = [
        "bg_phase_in_0011_orbit",
        "ic_length",
        "ic_active_bits",
        "ic_active_offsets_mod4",
        "ic_support_size",
        "ic_span",
        "background_window",
        "bg_at_ic",
        "bg_at_ic_ones",
        "xor_defect",
        "defect_active_bits",
        "defect_phase_offset",
        "defect_support_size",
        "defect_span",
        "defect_weight_by_mod4",
    ]
    descriptors = descriptor_values(t8_cases, keys)
    separating = [
        key
        for key, summary in descriptors.items()
        if summary["negative_separated_from_positive"] and summary["positive_constant"]
    ]
    partial = [
        key
        for key, summary in descriptors.items()
        if summary["negative_separated_from_positive"] and not summary["positive_constant"]
    ]
    if separating:
        status = "ALIGNMENT_DISCRIMINANT_FOUND"
    elif partial:
        status = "ALIGNMENT_PARTIAL"
    else:
        status = "ALIGNMENT_INSUFFICIENT"
    return {
        "source": str(CENSUS_JSON.name),
        "target_cases": t8_cases,
        "all_rule109_context": all_rule109_described,
        "descriptor_summaries": descriptors,
        "separating_descriptors": separating,
        "partial_descriptors": partial,
        "status": status,
        "methodological_limit": (
            "The verdict is based on three T=8 cases only. Any discriminator is "
            "a hypothesis that must be validated on broader rule_109 cases before "
            "being promoted to a causal law."
        ),
    }


def format_value(value: Any) -> str:
    if isinstance(value, list):
        return "[" + ", ".join(map(str, value)) + "]"
    if isinstance(value, dict):
        return "{" + ", ".join(f"{k}:{v}" for k, v in sorted(value.items())) + "}"
    return str(value)


def write_report(data: dict[str, Any]) -> None:
    lines = [
        "# Fase 59: rule_109/T=8 Background-IC Alignment Audit",
        "",
        "## Question",
        "",
        "What alignment descriptor separates `rule_109/bg=0011/T=8` (`NEGATIVE`)",
        "from `rule_109/bg=0110/T=8` and `rule_109/bg=1100/T=8`",
        "(`HORIZON_ACCEPTABLE`)?",
        "",
        "This phase uses existing Fase 55 census cases only. It runs no new ECA",
        "or ANF simulation.",
        "",
        "## Target Cases",
        "",
        "| background | category | IC word | bg phase | IC active | bg@IC | xor defect | defect support | defect offsets mod 4 |",
        "| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |",
    ]
    for row in data["target_cases"]:
        lines.append(
            f"| `{row['background']}` | `{row['category']}` | `{row['word']}` | "
            f"{row['bg_phase_in_0011_orbit']} | `{format_value(row['ic_active_bits'])}` | "
            f"`{row['bg_at_ic']}` | `{row['xor_defect']}` | {row['defect_support_size']} | "
            f"`{format_value(row['defect_phase_offset'])}` |"
        )
    lines.extend(["", "## Descriptor Scan", ""])
    for key, summary in data["descriptor_summaries"].items():
        marker = ""
        if key in data["separating_descriptors"]:
            marker = " -> DISCRIMINANT"
        elif key in data["partial_descriptors"]:
            marker = " -> PARTIAL"
        values = ", ".join(
            f"{bg}:{format_value(value)}" for bg, value in summary["values_by_background"].items()
        )
        lines.append(f"- `{key}`{marker}: {values}")
    lines.extend(["", "## Verdict", "", f"`{data['status']}`.", ""])
    if data["status"] == "ALIGNMENT_DISCRIMINANT_FOUND":
        lines.append("The following descriptors separate the negative case from both positives:")
        for key in data["separating_descriptors"]:
            lines.append(f"- `{key}`")
        lines.append("")
        lines.append(
            "The exact shared discriminator in this three-case audit is IC "
            "placement: both positive cases use adjacent active IC bits at "
            "offsets `(1, 2)` with span 2, while the negative case uses separated "
            "bits at offsets `(0, 1)` with span 6."
        )
        lines.append("")
        lines.append(
            "Background-subtracted descriptors (`xor_defect`, "
            "`defect_phase_offset`, and defect weights) also separate the "
            "negative case from the positives, but the two positives do not share "
            "one identical defect value. They therefore remain partial alignment "
            "evidence rather than the exact rule at this stage."
        )
    elif data["status"] == "ALIGNMENT_PARTIAL":
        lines.append(
            "Some descriptors separate the negative value from positive values, "
            "but the positives do not share a single value. This is partial "
            "evidence, not a rule."
        )
    else:
        lines.append(
            "The tested static alignment descriptors do not separate the three "
            "T=8 cases. A dynamic alignment audit would be needed."
        )
    lines.extend(["", "## Methodological Limit", "", f"- {data['methodological_limit']}", ""])
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = analyze()
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['status']}")
    if data["separating_descriptors"]:
        print("Separating descriptors:", ", ".join(data["separating_descriptors"]))


if __name__ == "__main__":
    main()
