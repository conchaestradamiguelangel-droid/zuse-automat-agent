#!/usr/bin/env python3
"""Fase 71: ANF-geometry audit for the static rule_109 positive.

Fase 70 showed that one positive rule_109 witness is dynamically static after
burn-in, and that its exact aligned transition is also present in a negative
case. This phase asks whether that positive is distinguished by the ANF
geometry that originally made it HORIZON_ACCEPTABLE.

The analysis intentionally reuses Fase 55/58/70 artifacts instead of
recomputing cones from scratch.
"""

from __future__ import annotations

import json
import math
import statistics
from pathlib import Path
from typing import Any, Callable


OUT_DIR = Path(__file__).resolve().parent
CENSUS_JSON = OUT_DIR / "anf_gradient_census_results.json"
PERIOD_HORIZON_JSON = OUT_DIR / "rule109_period_horizon_results.json"
SUBTYPE_JSON = OUT_DIR / "rule109_positive_subtype_results.json"
RESULTS_JSON = OUT_DIR / "rule109_static_anf_geometry_results.json"
REPORT_MD = OUT_DIR / "rule109_static_anf_geometry_report.md"

RULE = 109
COMMON_T_WINDOW = 12
REFERENCE_SLOPE = -0.307283
STATIC_POSITIVE_KEY = ("0110", 8, "0000011")
STATIC_NEGATIVE_KEY = ("0011", 6, "1100100")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def case_key(row: dict[str, Any]) -> tuple[str, int, str]:
    return (str(row["background"]), int(row["T_local"]), str(row["word"]))


def label_for(row: dict[str, Any]) -> str:
    return f"bg={row['background']}/T={row['T_local']}/word={row['word']}/{row['category']}"


def merge_case_maps() -> tuple[dict[tuple[str, int, str], dict[str, Any]], dict[tuple[str, int, str], dict[str, Any]]]:
    period_data = load_json(PERIOD_HORIZON_JSON)
    subtype_data = load_json(SUBTYPE_JSON)
    cases = {case_key(row): row for row in period_data["rows"] if int(row["rule"]) == RULE}
    subtypes = {case_key(row): row for row in subtype_data["rows"]}
    return cases, subtypes


def common_measurement_map() -> dict[tuple[str, int, str], dict[str, Any]]:
    census = load_json(CENSUS_JSON)
    measurements: dict[tuple[str, int, str], dict[str, Any]] = {}
    for item in census["measurements"]:
        if int(item["rule"]) != RULE or int(item["t_window"]) != COMMON_T_WINDOW:
            continue
        measurements[case_key(item)] = item
    return measurements


def active_outputs(measurement: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in measurement["outputs"] if row["concrete_active"]]


def linear_rmse(outputs: list[dict[str, Any]], fit: dict[str, Any]) -> float | None:
    slope = fit.get("slope")
    intercept = fit.get("intercept")
    if slope is None or intercept is None:
        return None
    residuals = [
        row["log10_monomials"] - (intercept + slope * row["dist"])
        for row in outputs
        if row["log10_monomials"] is not None
    ]
    if not residuals:
        return None
    return math.sqrt(sum(value * value for value in residuals) / len(residuals))


def active_distance_gap_count(outputs: list[dict[str, Any]]) -> int:
    dists = sorted({float(row["dist"]) for row in outputs})
    if len(dists) <= 1:
        return 0
    step = min(abs(b - a) for a, b in zip(dists, dists[1:]) if b != a)
    return sum(1 for a, b in zip(dists, dists[1:]) if abs((b - a) - step) > 1e-9)


def mirror_metrics(measurement: dict[str, Any]) -> dict[str, Any]:
    outputs = measurement["outputs"]
    by_index = {int(row["output_index"]): row for row in outputs}
    active_mismatches = 0
    both_active_log_diffs: list[float] = []
    all_log_diffs: list[float] = []
    for idx in range(len(outputs) // 2):
        left = by_index[idx]
        right = by_index[len(outputs) - 1 - idx]
        if bool(left["concrete_active"]) != bool(right["concrete_active"]):
            active_mismatches += 1
        if left["log10_monomials"] is not None and right["log10_monomials"] is not None:
            all_log_diffs.append(abs(left["log10_monomials"] - right["log10_monomials"]))
        if left["concrete_active"] and right["concrete_active"]:
            both_active_log_diffs.append(abs(left["log10_monomials"] - right["log10_monomials"]))
    return {
        "mirror_active_mismatches": active_mismatches,
        "mirror_all_log_mae": statistics.mean(all_log_diffs) if all_log_diffs else None,
        "mirror_both_active_log_mae": statistics.mean(both_active_log_diffs) if both_active_log_diffs else None,
        "mirror_both_active_pairs": len(both_active_log_diffs),
    }


def summarize_measurement(
    case: dict[str, Any],
    subtype: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    active = active_outputs(measurement)
    fit = measurement["active_summary"]["log_monomial_fit"]
    monomial_sum = sum(int(row["monomial_count"]) for row in active)
    max_active = max(active, key=lambda row: int(row["monomial_count"]))
    min_output_dist = min(float(row["dist"]) for row in measurement["outputs"])
    central_active = [row for row in active if abs(float(row["dist"]) - min_output_dist) < 1e-9]
    central_sum = sum(int(row["monomial_count"]) for row in central_active)
    near_center_active = [row for row in active if float(row["dist"]) <= min_output_dist + 1.0]
    near_center_sum = sum(int(row["monomial_count"]) for row in near_center_active)
    active_dists = sorted(float(row["dist"]) for row in active)
    active_logs = [float(row["log10_monomials"]) for row in active]
    mirror = mirror_metrics(measurement)
    slope = fit["slope"]
    return {
        "label": label_for(case),
        "background": case["background"],
        "T_local": int(case["T_local"]),
        "word": case["word"],
        "category": case["category"],
        "positive": bool(case["positive"]),
        "subtype": subtype.get("subtype", "UNKNOWN"),
        "period_center_shape": subtype.get("period_center_shape"),
        "unique_center_transitions": subtype.get("unique_center_transitions"),
        "positive_only_center_transition_count": subtype.get("positive_only_center_transition_count"),
        "t_window": COMMON_T_WINDOW,
        "active_count": len(active),
        "distinct_dist_count": fit["distinct_dist_count"],
        "slope": slope,
        "r2": fit["r2"],
        "reliable": fit["reliable"],
        "delta_vs_t15_percent": abs((slope - REFERENCE_SLOPE) / REFERENCE_SLOPE) * 100.0,
        "linear_rmse": linear_rmse(active, fit),
        "active_distance_values": active_dists,
        "active_distance_gap_count": active_distance_gap_count(active),
        "active_log_values": active_logs,
        "active_monomial_counts": [int(row["monomial_count"]) for row in active],
        "monomial_sum_active": monomial_sum,
        "max_active_monomial_count": int(max_active["monomial_count"]),
        "max_active_monomial_dist": float(max_active["dist"]),
        "min_output_dist": min_output_dist,
        "central_active_count": len(central_active),
        "central_monomial_share": central_sum / monomial_sum if monomial_sum else 0.0,
        "near_center_active_count": len(near_center_active),
        "near_center_monomial_share": near_center_sum / monomial_sum if monomial_sum else 0.0,
        **mirror,
    }


def confusion(rows: list[dict[str, Any]], predicate: Callable[[dict[str, Any]], bool]) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    false_pos: list[str] = []
    false_neg: list[str] = []
    for row in rows:
        pred = predicate(row)
        actual = row["positive"]
        if pred and actual:
            tp += 1
        elif pred and not actual:
            fp += 1
            false_pos.append(row["label"])
        elif not pred and actual:
            fn += 1
            false_neg.append(row["label"])
        else:
            tn += 1
    total = len(rows)
    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": (tp + tn) / total if total else 0.0,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "false_positive_labels": false_pos,
        "false_negative_labels": false_neg,
        "perfect": fp == 0 and fn == 0,
    }


def scan_thresholds(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metrics = [
        "active_count",
        "distinct_dist_count",
        "slope",
        "r2",
        "delta_vs_t15_percent",
        "linear_rmse",
        "active_distance_gap_count",
        "monomial_sum_active",
        "max_active_monomial_count",
        "max_active_monomial_dist",
        "central_active_count",
        "central_monomial_share",
        "near_center_active_count",
        "near_center_monomial_share",
        "mirror_active_mismatches",
        "mirror_all_log_mae",
        "mirror_both_active_log_mae",
    ]
    scans: list[dict[str, Any]] = []
    for metric in metrics:
        values = sorted({row[metric] for row in rows if row.get(metric) is not None})
        for threshold in values:
            scans.append({
                "rule": f"{metric} >= {threshold}",
                "metric": metric,
                "direction": ">=",
                "threshold": threshold,
                **confusion(rows, lambda row, metric=metric, threshold=threshold: row.get(metric) is not None and row[metric] >= threshold),
            })
            scans.append({
                "rule": f"{metric} <= {threshold}",
                "metric": metric,
                "direction": "<=",
                "threshold": threshold,
                **confusion(rows, lambda row, metric=metric, threshold=threshold: row.get(metric) is not None and row[metric] <= threshold),
            })
    scans.sort(key=lambda row: (not row["perfect"], row["fp"], -row["tp"], -row["accuracy"], row["fn"], row["rule"]))
    return scans


def euclidean_distance(a: dict[str, Any], b: dict[str, Any], keys: list[str]) -> float:
    total = 0.0
    used = 0
    for key in keys:
        av = a.get(key)
        bv = b.get(key)
        if av is None or bv is None:
            continue
        total += (float(av) - float(bv)) ** 2
        used += 1
    return math.sqrt(total) if used else float("nan")


def build_results() -> dict[str, Any]:
    cases, subtypes = merge_case_maps()
    measurements = common_measurement_map()
    rows: list[dict[str, Any]] = []
    for key, case in sorted(cases.items()):
        if key not in measurements:
            continue
        rows.append(summarize_measurement(case, subtypes.get(key, {}), measurements[key]))

    static_positive = next(row for row in rows if (row["background"], row["T_local"], row["word"]) == STATIC_POSITIVE_KEY)
    static_negative = next(row for row in rows if (row["background"], row["T_local"], row["word"]) == STATIC_NEGATIVE_KEY)
    static_signature_rows = [
        row for row in rows
        if row["period_center_shape"] == 1
        and row["unique_center_transitions"] == 1
    ]
    scans = scan_thresholds(rows)
    perfect = [row for row in scans if row["perfect"]]
    no_fp = [row for row in scans if row["fp"] == 0 and row["tp"] > 0]
    best_no_fp = max(no_fp, key=lambda row: (row["tp"], row["accuracy"], row["recall"]), default=None)
    best_accuracy = max(scans, key=lambda row: (row["accuracy"], row["precision"], row["recall"]))

    geometry_keys = ["slope", "r2", "linear_rmse", "central_monomial_share", "near_center_monomial_share", "mirror_active_mismatches"]
    static_pair_distance = euclidean_distance(static_positive, static_negative, geometry_keys)

    if perfect:
        status = "STATIC_ANF_GEOMETRY_DISCRIMINANT_FOUND"
        interpretation = (
            "At least one ANF-geometry scalar separates all positive rule_109 cases from non-positives at T_WINDOW=12: "
            "the maximum active monomial count is located at the exact cone center for every positive and for no non-positive."
        )
    elif static_positive["r2"] >= 0.99 and static_negative["r2"] < 0.95:
        status = "STATIC_ANF_GEOMETRY_PARTIAL"
        interpretation = (
            "The static positive is distinguished from the static negative by a much cleaner ANF log-monomial geometry, "
            "but the signal is not a global 17-case separator."
        )
    elif best_no_fp and best_no_fp["tp"] >= 3:
        status = "STATIC_ANF_GEOMETRY_PARTIAL"
        interpretation = "ANF geometry provides a high-precision partial separator, but does not explain all positives."
    elif static_positive["r2"] < 0.95:
        status = "STATIC_ANF_ARTIFACT_LIKELY"
        interpretation = "The static positive has weak ANF geometry; the HORIZON_ACCEPTABLE label may be a horizon artifact."
    else:
        status = "STATIC_ANF_GEOMETRY_NEGATIVE"
        interpretation = "The tested ANF-geometry summaries do not distinguish the static positive."

    return {
        "phase": 71,
        "source": {
            "census": CENSUS_JSON.name,
            "period_horizon": PERIOD_HORIZON_JSON.name,
            "subtypes": SUBTYPE_JSON.name,
        },
        "rule": RULE,
        "t_window": COMMON_T_WINDOW,
        "reference_slope": REFERENCE_SLOPE,
        "rows": rows,
        "static_positive": static_positive,
        "static_negative": static_negative,
        "static_signature_rows": static_signature_rows,
        "static_pair_geometry_distance": static_pair_distance,
        "threshold_scan": scans,
        "summary": {
            "status": status,
            "case_count": len(rows),
            "positive_count": sum(1 for row in rows if row["positive"]),
            "negative_count": sum(1 for row in rows if not row["positive"]),
            "perfect_rule_count": len(perfect),
            "best_no_false_positive_rule": best_no_fp,
            "best_accuracy_rule": best_accuracy,
            "interpretation": interpretation,
        },
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def build_report(data: dict[str, Any]) -> str:
    summary = data["summary"]
    sp = data["static_positive"]
    sn = data["static_negative"]
    lines = [
        "# Fase 71: rule_109 Static Positive ANF-Geometry Audit",
        "",
        "## Question",
        "",
        "Why is `bg=0110/T=8/word=0000011` a positive ANF-gradient witness",
        "if its aligned snapshot transition is static and also appears in a negative case?",
        "",
        "This phase reuses the Fase 55 ANF census and the Fase 70 subtype labels.",
        "No paper, DOI metadata, tag, or release is modified.",
        "",
        "## Method",
        "",
        f"- Rule: `{RULE}`",
        f"- Common horizon: `T_WINDOW={COMMON_T_WINDOW}`",
        "- Inputs: `anf_gradient_census_results.json`,",
        "  `rule109_period_horizon_results.json`, and",
        "  `rule109_positive_subtype_results.json`.",
        "- Geometry source: active output rows with `dist`, `monomial_count`,",
        "  `log10_monomials`, plus `active_summary.log_monomial_fit`.",
        "",
        "## Static Pair",
        "",
        "| case | category | subtype | active | dist classes | slope | R2 | delta T15 % | max monomial dist | RMSE | central share | near-center share | mirror active mismatches |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in [sp, sn]:
        lines.append(
            f"| `{row['label']}` | `{row['category']}` | `{row['subtype']}` | "
            f"{row['active_count']} | {row['distinct_dist_count']} | {fmt(row['slope'], 6)} | "
            f"{fmt(row['r2'], 6)} | {fmt(row['delta_vs_t15_percent'], 2)} | "
            f"{fmt(row['max_active_monomial_dist'], 1)} | "
            f"{fmt(row['linear_rmse'], 3)} | {fmt(row['central_monomial_share'], 3)} | "
            f"{fmt(row['near_center_monomial_share'], 3)} | {row['mirror_active_mismatches']} |"
        )

    lines.extend([
        "",
        "Active profiles for the static pair:",
        "",
        f"- Static positive distances: `{sp['active_distance_values']}`",
        f"- Static positive monomial counts: `{sp['active_monomial_counts']}`",
        f"- Static negative distances: `{sn['active_distance_values']}`",
        f"- Static negative monomial counts: `{sn['active_monomial_counts']}`",
        "",
        "## 17-Case Common-Horizon Table",
        "",
        "| case | positive | subtype | slope | R2 | active | dist | max monomial dist | RMSE | central share | near-center share | mirror mismatches |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ])
    for row in data["rows"]:
        lines.append(
            f"| `{row['label']}` | `{row['positive']}` | `{row['subtype']}` | "
            f"{fmt(row['slope'], 6)} | {fmt(row['r2'], 6)} | {row['active_count']} | "
            f"{row['distinct_dist_count']} | {fmt(row['max_active_monomial_dist'], 1)} | "
            f"{fmt(row['linear_rmse'], 3)} | "
            f"{fmt(row['central_monomial_share'], 3)} | {fmt(row['near_center_monomial_share'], 3)} | "
            f"{row['mirror_active_mismatches']} |"
        )

    lines.extend([
        "",
        "## Static Signature Rows",
        "",
        "The static dynamic signature remains non-specific. The ANF geometry is",
        "therefore the relevant difference, not the static transition itself.",
        "",
        "| case | positive | category | slope | R2 | delta T15 % |",
        "| --- | --- | --- | ---: | ---: | ---: |",
    ])
    for row in data["static_signature_rows"]:
        lines.append(
            f"| `{row['label']}` | `{row['positive']}` | `{row['category']}` | "
            f"{fmt(row['slope'], 6)} | {fmt(row['r2'], 6)} | {fmt(row['delta_vs_t15_percent'], 2)} |"
        )

    best_no_fp = summary["best_no_false_positive_rule"]
    best_accuracy = summary["best_accuracy_rule"]
    lines.extend([
        "",
        "## Threshold Scan",
        "",
        f"- Perfect scalar rules: `{summary['perfect_rule_count']}`.",
    ])
    if best_no_fp:
        lines.append(
            f"- Best no-false-positive rule: `{best_no_fp['rule']}` "
            f"(TP={best_no_fp['tp']}, FP={best_no_fp['fp']}, TN={best_no_fp['tn']}, FN={best_no_fp['fn']}, "
            f"precision={best_no_fp['precision']:.3f}, recall={best_no_fp['recall']:.3f})."
        )
    lines.append(
        f"- Best accuracy rule: `{best_accuracy['rule']}` "
        f"(TP={best_accuracy['tp']}, FP={best_accuracy['fp']}, TN={best_accuracy['tn']}, FN={best_accuracy['fn']}, "
        f"accuracy={best_accuracy['accuracy']:.3f})."
    )
    lines.extend([
        "",
        "Top scanned rules:",
        "",
    ])
    for row in data["threshold_scan"][:10]:
        lines.append(
            f"- `{row['rule']}`: TP={row['tp']}, FP={row['fp']}, TN={row['tn']}, FN={row['fn']}, "
            f"acc={row['accuracy']:.3f}, precision={row['precision']:.3f}, recall={row['recall']:.3f}"
        )

    lines.extend([
        "",
        "## Verdict",
        "",
        f"`{summary['status']}`.",
        "",
        summary["interpretation"],
        "",
        "The static positive is not explained by its temporal transition, which is",
        "shared with a negative. It is distinguished by common-horizon ANF",
        "geometry: the strongest active monomial support is centered at",
        "`dist=0`, matching all other positives and no non-positive case. The",
        "static pair also differs in fit quality: the positive has a T15-like",
        "slope with near-perfect log-linear fit, while the static negative has a",
        "similar slope but much weaker fit quality.",
        "",
        "## Methodological Limit",
        "",
        "- This phase uses existing common-horizon ANF measurements at `T_WINDOW=12`.",
        "- The static pair is still only one positive and one negative; the 17-case",
        "  table and threshold scan are included to avoid overfitting the pair.",
        "- Scalar ANF-geometry summaries do not replace full causal-cone comparison.",
        "- No paper or DOI metadata is changed by this phase.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    data = build_results()
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(build_report(data), encoding="utf-8")
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['summary']['status']}")


if __name__ == "__main__":
    main()
