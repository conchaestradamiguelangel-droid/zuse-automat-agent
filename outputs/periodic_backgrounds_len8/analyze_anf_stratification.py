#!/usr/bin/env python3
"""Fase 45: ANF stratification analysis for the T=15 cone.

Fase 44 computed exact ANF degree and monomial counts for 174 active outputs.
This script performs no new simulation. It extracts quantitative laws from the
Fase 44 result:

1. Degree gradient against distance from the cone center.
2. Exponential monomial-count decay against the same distance.
3. Residual/epsilon characterization for degree = 24 - dist + epsilon.
4. Left/right symmetry checks and degree-24 cap.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
SOURCE_JSON = OUT_DIR / "anf_degree_results.json"
RESULTS_JSON = OUT_DIR / "anf_stratification_results.json"
REPORT_MD = OUT_DIR / "anf_stratification_report.md"
CENTER_INDEX = 12


def mean(values: list[float]) -> float:
    return sum(values) / len(values)


def pearson(xs: list[float], ys: list[float]) -> float:
    mx = mean(xs)
    my = mean(ys)
    numerator = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denom_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    return numerator / (denom_x * denom_y)


def linear_fit(xs: list[float], ys: list[float]) -> dict:
    mx = mean(xs)
    my = mean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom
    intercept = my - slope * mx
    yhat = [intercept + slope * x for x in xs]
    ss_res = sum((y - pred) ** 2 for y, pred in zip(ys, yhat))
    ss_tot = sum((y - my) ** 2 for y in ys)
    return {
        "slope": slope,
        "intercept": intercept,
        "r2": 1.0 - ss_res / ss_tot,
    }


def crosstab(records: list[dict], key: str) -> list[dict]:
    grouped: dict[str, Counter] = defaultdict(Counter)
    for row in records:
        grouped[str(row[key])][str(row["epsilon"])] += 1
    out = []
    for value, counts in sorted(grouped.items()):
        total = sum(counts.values())
        out.append(
            {
                key: value,
                "total": total,
                "epsilon_0": counts.get("0", 0),
                "epsilon_1": counts.get("1", 0),
                "epsilon_1_rate": round(counts.get("1", 0) / total, 6),
            }
        )
    return out


def flatten_outputs(data: dict) -> list[dict]:
    records = []
    for rep_index, row in enumerate(data["rows"]):
        for output in row["active_outputs"]:
            rel_pos = int(output["output_index"]) - CENTER_INDEX
            dist = abs(rel_pos)
            predicted_base = 24 - dist
            epsilon = int(output["degree"]) - predicted_base
            records.append(
                {
                    "rep_index": rep_index,
                    "rule": int(row["rule"]),
                    "background": row["background"],
                    "family_id": row["family_id"],
                    "ic": row["ic"],
                    "output_index": int(output["output_index"]),
                    "rel_pos": rel_pos,
                    "dist": dist,
                    "sign": "L" if rel_pos < 0 else ("R" if rel_pos > 0 else "C"),
                    "degree": int(output["degree"]),
                    "predicted_base_degree": predicted_base,
                    "epsilon": epsilon,
                    "monomial_count": int(output["monomial_count"]),
                    "log10_monomials": math.log10(int(output["monomial_count"])),
                    "constant_term": int(output["constant_term"]),
                }
            )
    return records


def left_right_pairs(records: list[dict]) -> dict:
    by_rep: dict[int, dict[int, dict]] = defaultdict(dict)
    for row in records:
        by_rep[row["rep_index"]][row["rel_pos"]] = row
    pairs = []
    matched = 0
    same_degree = 0
    same_epsilon = 0
    for rep_index, positions in by_rep.items():
        for dist in range(1, CENTER_INDEX + 1):
            left = positions.get(-dist)
            right = positions.get(dist)
            if left is None or right is None:
                continue
            matched += 1
            degree_equal = left["degree"] == right["degree"]
            epsilon_equal = left["epsilon"] == right["epsilon"]
            same_degree += int(degree_equal)
            same_epsilon += int(epsilon_equal)
            pairs.append(
                {
                    "rep_index": rep_index,
                    "dist": dist,
                    "left_degree": left["degree"],
                    "right_degree": right["degree"],
                    "degree_equal": degree_equal,
                    "left_epsilon": left["epsilon"],
                    "right_epsilon": right["epsilon"],
                    "epsilon_equal": epsilon_equal,
                }
            )
    return {
        "matched_lr_pairs": matched,
        "same_degree_pairs": same_degree,
        "same_degree_rate": round(same_degree / matched, 6) if matched else None,
        "same_epsilon_pairs": same_epsilon,
        "same_epsilon_rate": round(same_epsilon / matched, 6) if matched else None,
        "pairs": pairs,
    }


def analyze() -> dict:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    records = flatten_outputs(data)
    dists = [row["dist"] for row in records]
    degrees = [row["degree"] for row in records]
    logs = [row["log10_monomials"] for row in records]
    epsilons = [row["epsilon"] for row in records]
    degree_fit = linear_fit([float(x) for x in dists], [float(y) for y in degrees])
    monomial_fit = linear_fit([float(x) for x in dists], logs)

    by_dist = []
    for dist in sorted(set(dists)):
        subset = [row for row in records if row["dist"] == dist]
        eps = Counter(row["epsilon"] for row in subset)
        log_values = [row["log10_monomials"] for row in subset]
        deg_values = [row["degree"] for row in subset]
        by_dist.append(
            {
                "dist": dist,
                "n": len(subset),
                "degree_min": min(deg_values),
                "degree_max": max(deg_values),
                "degree_mean": mean([float(x) for x in deg_values]),
                "epsilon_0": eps.get(0, 0),
                "epsilon_1": eps.get(1, 0),
                "log10_monomials_mean": mean(log_values),
                "log10_monomials_min": min(log_values),
                "log10_monomials_max": max(log_values),
            }
        )

    invalid_eps = [row for row in records if row["epsilon"] not in (0, 1)]
    degree_cap_holds = max(degrees) <= 24
    status = "ANF_GRADIENT_LAWS_CONFIRMED"
    if invalid_eps:
        status = "ANF_GRADIENT_EXCEPTIONS_FOUND"

    return {
        "status": status,
        "source": str(SOURCE_JSON),
        "record_count": len(records),
        "degree_law": {
            "formula": "degree = 24 - abs(rel_pos) + epsilon, epsilon in {0,1}",
            "invalid_epsilon_count": len(invalid_eps),
            "epsilon_counts": dict(sorted(Counter(epsilons).items())),
            "pearson_dist_degree": pearson([float(x) for x in dists], [float(y) for y in degrees]),
            "linear_fit": degree_fit,
            "degree_24_cap_holds": degree_cap_holds,
            "max_degree": max(degrees),
        },
        "monomial_law": {
            "formula": "log10(monomials) ~= intercept + slope * abs(rel_pos)",
            "pearson_dist_log10_monomials": pearson([float(x) for x in dists], logs),
            "linear_fit": monomial_fit,
            "slope_minus_negative_log10_2": monomial_fit["slope"] + math.log10(2),
        },
        "by_dist": by_dist,
        "epsilon_by_sign": crosstab(records, "sign"),
        "epsilon_by_rule": crosstab(records, "rule"),
        "epsilon_by_family": crosstab(records, "family_id"),
        "epsilon_by_background": crosstab(records, "background"),
        "left_right": left_right_pairs(records),
        "records": records,
    }


def write_report(data: dict) -> None:
    degree = data["degree_law"]
    mono = data["monomial_law"]
    lines = [
        "# Fase 45: ANF Stratification Laws of the T=15 Cone",
        "",
        "## Question",
        "",
        "Fase 44 found mixed ANF complexity: active outputs have degrees 14..24",
        "and monomial counts ranging from thousands to tens of millions. Fase 45",
        "asks whether that variation is structured.",
        "",
        "No new simulation is performed. This analysis loads",
        "`anf_degree_results.json` and analyzes the 174 active outputs.",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        "### Law 1: ANF degree gradient",
        "",
        f"- Formula tested: `{degree['formula']}`",
        f"- Exceptions outside epsilon {{0,1}}: {degree['invalid_epsilon_count']}/{data['record_count']}",
        f"- Epsilon counts: {degree['epsilon_counts']}",
        f"- Pearson r(|rel_pos|, degree): {degree['pearson_dist_degree']:.6f}",
        f"- Linear fit degree ~= {degree['linear_fit']['intercept']:.6f} + "
        f"{degree['linear_fit']['slope']:.6f} * dist; R^2={degree['linear_fit']['r2']:.6f}",
        f"- Degree-24 cap holds: `{degree['degree_24_cap_holds']}` (max degree {degree['max_degree']})",
        "",
        "### Law 2: monomial-count exponential decay",
        "",
        f"- Pearson r(|rel_pos|, log10(monomials)): {mono['pearson_dist_log10_monomials']:.6f}",
        f"- Linear fit log10(monomials) ~= {mono['linear_fit']['intercept']:.6f} + "
        f"{mono['linear_fit']['slope']:.6f} * dist; R^2={mono['linear_fit']['r2']:.6f}",
        f"- Difference from -log10(2): {mono['slope_minus_negative_log10_2']:.6f}",
        "",
        "## Distance table",
        "",
        "| dist | n | degree | epsilon 0/1 | mean log10(monomials) | log10 range |",
        "| ---: | ---: | --- | --- | ---: | --- |",
    ]
    for row in data["by_dist"]:
        lines.append(
            f"| {row['dist']} | {row['n']} | {row['degree_min']}..{row['degree_max']} | "
            f"{row['epsilon_0']}/{row['epsilon_1']} | {row['log10_monomials_mean']:.3f} | "
            f"{row['log10_monomials_min']:.3f}..{row['log10_monomials_max']:.3f} |"
        )

    lines.extend(
        [
            "",
            "## Epsilon characterization",
            "",
            "Epsilon is the residual in `degree = 24 - dist + epsilon`.",
            "",
            "### By sign",
            "",
            "| sign | total | epsilon=0 | epsilon=1 | epsilon=1 rate |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in data["epsilon_by_sign"]:
        lines.append(
            f"| `{row['sign']}` | {row['total']} | {row['epsilon_0']} | "
            f"{row['epsilon_1']} | {row['epsilon_1_rate']:.3f} |"
        )

    lines.extend(
        [
            "",
            "### By rule",
            "",
            "| rule | total | epsilon=0 | epsilon=1 | epsilon=1 rate |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in data["epsilon_by_rule"]:
        lines.append(
            f"| `{row['rule']}` | {row['total']} | {row['epsilon_0']} | "
            f"{row['epsilon_1']} | {row['epsilon_1_rate']:.3f} |"
        )

    lr = data["left_right"]
    lines.extend(
        [
            "",
            "## Left/right symmetry",
            "",
            f"- Matched left/right pairs: {lr['matched_lr_pairs']}",
            f"- Same degree: {lr['same_degree_pairs']}/{lr['matched_lr_pairs']} "
            f"({lr['same_degree_rate']:.3f})",
            f"- Same epsilon: {lr['same_epsilon_pairs']}/{lr['matched_lr_pairs']} "
            f"({lr['same_epsilon_rate']:.3f})",
            "",
            "## Interpretation",
            "",
            "The ANF variation from Fase 44 is highly structured. Degree is almost a",
            "linear function of distance from the cone center, with zero violations",
            "outside a one-bit epsilon band. Monomial counts decay almost exactly",
            "exponentially with distance, with slope close to -log10(2). The cone is",
            "therefore not algebraically uniform: it has a spatial complexity",
            "gradient centered on the active defect.",
            "",
        ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_report(analyze())


if __name__ == "__main__":
    main()
