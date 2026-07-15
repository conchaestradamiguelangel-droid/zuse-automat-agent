#!/usr/bin/env python3
"""Fase 64: Hamming-1 truth-table neighborhood of rule_109 on bg=1100.

Fase 63 showed that whole-monomial ANF edits around rule_109 destroy
stationary oscillator support on bg=1100.  This phase tests the finest
possible local intervention on an ECA rule: flip one truth-table bit.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
FASE63_SCRIPT = OUT_DIR / "analyze_rule109_algebraic_intervention.py"
RESULTS_JSON = OUT_DIR / "rule109_hamming1_results.json"
REPORT_MD = OUT_DIR / "rule109_hamming1_report.md"

RULE = 109
TARGET_BACKGROUND = "1100"


def import_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def bit_string(rule: int) -> str:
    return format(rule, "08b")


def hamming_neighbors() -> list[dict[str, Any]]:
    return [
        {
            "bit_flipped": bit,
            "rule": RULE ^ (1 << bit),
            "rule_binary": bit_string(RULE ^ (1 << bit)),
        }
        for bit in range(8)
    ]


def classify_status(neighbors: list[dict[str, Any]]) -> tuple[str, str]:
    with_stationary = [row for row in neighbors if row["stationary_count"] > 0]
    if with_stationary:
        measured = [row for row in with_stationary if row.get("anf_measurements")]
        if measured:
            return (
                "HAMMING1_WITNESSES_FOUND",
                "At least one Hamming-1 neighbor has a bg=1100 stationary oscillator and was measured by the ANF-gradient protocol.",
            )
        return (
            "HAMMING1_STATIONARY_SUPPORT_FOUND",
            "At least one Hamming-1 neighbor has bg=1100 stationary support, but ANF measurement was not available.",
        )
    return (
        "HAMMING1_ALL_BLOCKED",
        "None of the eight Hamming-1 neighbors has a stationary oscillator on bg=1100 in the minimal sweep.",
    )


def build_report(data: dict[str, Any]) -> str:
    lines = [
        "# Fase 64: rule_109 Hamming-1 Neighborhood on bg=1100",
        "",
        "## Question",
        "",
        "Do any one-bit truth-table perturbations of `rule_109` preserve",
        "stationary oscillator support on the residual background `bg=1100`?",
        "",
        "Fase 63 tested whole-monomial ANF edits. Those edits are algebraically",
        "natural but flip multiple truth-table bits at once. Fase 64 instead uses",
        "the atomic ECA intervention: `rule_i = 109 XOR (1 << i)` for `i=0..7`.",
        "",
        "## Status",
        "",
        f"`{data['status']}`",
        "",
        data["verdict_reason"],
        "",
        "## Hamming-1 table",
        "",
        "| bit flipped | rule | binary | ANF monomials | center mediated | raw catalog | Fase 55 census | stationary hits | moving hits | aliases | max span | periods | measured |",
        "| ---: | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |",
    ]
    for row in data["neighbors"]:
        periods = sorted({hit["period_T"] for hit in row["stationary_hits"]})
        lines.append(
            f"| {row['bit_flipped']} | {row['rule']} | `{row['rule_binary']}` | "
            f"`{' XOR '.join(row['anf_monomials'])}` | "
            f"{str(row['center_structure']['center_mediated']).lower()} | "
            f"{str(row['catalog_presence']['present']).lower()} | "
            f"{str(row['catalog_presence']['fase55_census_present']).lower()} | "
            f"{row['stationary_count']} | {row['moving_count']} | {row['alias_count']} | "
            f"{row['max_span']} | {periods} | {len(row.get('anf_measurements', []))} |"
        )

    measured_any = any(row.get("anf_measurements") for row in data["neighbors"])
    lines.extend(["", "## ANF measurements", ""])
    if not measured_any:
        lines.extend([
            "No Hamming-1 neighbor produced a stationary bg=1100 witness, so no",
            "cone-ANF gradient measurement was run.",
            "",
        ])
    else:
        for row in data["neighbors"]:
            for measured in row.get("anf_measurements", []):
                lines.append(f"### bit {row['bit_flipped']} / rule_{row['rule']} / `{measured['case']['word']}`")
                lines.append("")
                lines.append("| T_WINDOW | active | dist classes | slope | R^2 | delta vs T15 | comparable |")
                lines.append("| ---: | ---: | ---: | ---: | ---: | ---: | --- |")
                for item in measured["measurements"]:
                    fit = item["active_summary"]["log_monomial_fit"]
                    slope = "NA" if fit["slope"] is None else f"{fit['slope']:.6f}"
                    r2 = "NA" if fit["r2"] is None else f"{fit['r2']:.6f}"
                    delta = "NA" if item["slope_delta_percent"] is None else f"{item['slope_delta_percent']:.2f}%"
                    lines.append(
                        f"| {item['t_window']} | {item['active_summary']['count']} | "
                        f"{item['active_summary']['distinct_dist_count']} | {slope} | {r2} | "
                        f"{delta} | {str(item['comparable_to_t15']).lower()} |"
                    )
                lines.append("")

    lines.extend([
        "## Interpretation",
        "",
        "This phase tests whether the Fase 63 block was caused by intervention",
        "granularity. If even Hamming-1 neighbors lack stationary support, the",
        "`rule_109/bg=1100` oscillator is locally isolated in truth-table space",
        "under the current periodic-background detector. If a neighbor survives",
        "only as a compact low-period oscillator, it is support-preserving in a",
        "weak sense but not a comparable replacement for the wide residual",
        "mechanism.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    f63 = import_module(FASE63_SCRIPT, "rule109_fase63_helpers")
    catalog = f63.load_jsonl(f63.CATALOG_JSONL)
    neighbors = []
    for spec in hamming_neighbors():
        monomials = f63.monomial_names(spec["rule"])
        sweep = f63.sweep_rule_on_background(spec["rule"], TARGET_BACKGROUND)
        measurements = [f63.measure_synthetic_witness(sweep["stationary_hits"][0])] if sweep["stationary_hits"] else []
        row = {
            **spec,
            "background": TARGET_BACKGROUND,
            "anf_monomials": monomials,
            "center_structure": f63.classify_center_structure(monomials),
            "catalog_presence": f63.catalog_presence(catalog, spec["rule"]),
            "processed_ic_words": sweep["processed_ic_words"],
            "stationary_count": len(sweep["stationary_hits"]),
            "moving_count": len(sweep["moving_hits"]),
            "alias_count": sweep["alias_count"],
            "max_span": max((hit["span"] for hit in sweep["stationary_hits"]), default=0),
            "stationary_hits": sweep["stationary_hits"],
            "moving_hits": sweep["moving_hits"],
            "anf_measurements": measurements,
        }
        neighbors.append(row)

    status, reason = classify_status(neighbors)
    data = {
        "phase": 64,
        "status": status,
        "verdict_reason": reason,
        "base_rule": RULE,
        "base_rule_binary": bit_string(RULE),
        "background": TARGET_BACKGROUND,
        "neighbors": neighbors,
    }
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {status}")


if __name__ == "__main__":
    main()
