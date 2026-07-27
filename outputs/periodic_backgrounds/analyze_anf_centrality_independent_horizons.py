#!/usr/bin/env python3
"""Fase 74: independent horizon audit for ANF centrality candidates.

Fase 73 showed that adding T_local >= 8 to exact ANF centrality removes the
eight Fase 72 false positives. That split is descriptively correct, but partly
circular because T_local >= 8 is already part of the Fase 55 category
definition for HORIZON_ACCEPTABLE versus HORIZON_ARTIFACT.

This phase therefore remeasures the 13 exact-centrality candidates at horizons
8, 12, 16, and 20, and asks whether central T15-comparable ANF geometry
persists without using T_local as a classifier.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
CENSUS_SCRIPT = OUT_DIR / "analyze_anf_gradient_census.py"
CENSUS_JSON = OUT_DIR / "anf_gradient_census_results.json"
GLOBAL_JSON = OUT_DIR / "anf_centrality_global_results.json"
RESULTS_JSON = OUT_DIR / "anf_centrality_independent_horizon_results.json"
REPORT_MD = OUT_DIR / "anf_centrality_independent_horizon_report.md"
CHECKPOINT_JSON = OUT_DIR / "anf_centrality_independent_horizon_checkpoint.json"

HORIZONS = [8, 12, 16, 20]
POSITIVE_CATEGORIES = {"NATURAL_PERIOD_STRONG", "HORIZON_ACCEPTABLE"}


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def case_key(row: dict[str, Any]) -> tuple[int, str, int, str]:
    return (int(row["rule"]), str(row["background"]), int(row["T_local"]), str(row["word"]))


def case_label(row: dict[str, Any]) -> str:
    return f"rule={row['rule']}/bg={row['background']}/T={row['T_local']}/word={row['word']}/{row['category']}"


def load_checkpoint() -> dict[str, Any]:
    if CHECKPOINT_JSON.exists():
        return load_json(CHECKPOINT_JSON)
    return {"measurements": {}}


def active_outputs(measurement: dict[str, Any]) -> list[dict[str, Any]]:
    return [row for row in measurement["outputs"] if row["concrete_active"]]


def max_active_dist(measurement: dict[str, Any]) -> float | None:
    active = active_outputs(measurement)
    if not active:
        return None
    max_active = max(active, key=lambda row: int(row["monomial_count"]))
    return float(max_active["dist"])


def central_t15_like(measurement: dict[str, Any], census_module) -> bool:
    dist = max_active_dist(measurement)
    fit = measurement["active_summary"]["log_monomial_fit"]
    return dist is not None and abs(dist) < 1e-9 and bool(census_module.comparable_to_t15(fit))


def measurement_summary(case: dict[str, Any], measurement: dict[str, Any], census_module) -> dict[str, Any]:
    active = active_outputs(measurement)
    fit = measurement["active_summary"]["log_monomial_fit"]
    dist = max_active_dist(measurement)
    return {
        "horizon": int(measurement["t_window"]),
        "active_count": len(active),
        "distinct_dist_count": fit["distinct_dist_count"],
        "slope": fit["slope"],
        "r2": fit["r2"],
        "reliable": fit["reliable"],
        "max_active_monomial_dist": dist,
        "central_t15_like": central_t15_like(measurement, census_module),
        "concrete_match": bool(measurement["all_outputs_match_concrete"]),
        "category": case["category"],
        "positive": case["category"] in POSITIVE_CATEGORIES,
    }


def select_centrality_candidates(global_results: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = [
        row for row in global_results["rows"]
        if row["max_active_monomial_dist"] is not None
        and abs(float(row["max_active_monomial_dist"])) < 1e-9
    ]
    candidates.sort(key=lambda row: (row["positive"] is False, row["rule"], row["background"], row["T_local"], row["word"]))
    return candidates


def census_cases_by_key(census: dict[str, Any]) -> dict[tuple[int, str, int, str], dict[str, Any]]:
    return {case_key(row): row for row in census["case_summaries"]}


def checkpoint_key(case: dict[str, Any], horizon: int) -> str:
    return f"r{case['rule']}_bg{case['background']}_T{case['T_local']}_w{case['word']}_h{horizon}"


def measure_candidates() -> dict[str, Any]:
    baseline = load_module("periodic_bg_anf_baseline", BASELINE_SCRIPT)
    census_module = load_module("anf_gradient_census", CENSUS_SCRIPT)
    census = load_json(CENSUS_JSON)
    global_results = load_json(GLOBAL_JSON)
    candidates = select_centrality_candidates(global_results)
    case_lookup = census_cases_by_key(census)

    catalog = baseline.load_jsonl(baseline.CATALOG_JSONL)
    base = baseline.load_base_module()
    popcount16 = np.array([int(i).bit_count() for i in range(1 << 16)], dtype=np.uint8)
    checkpoint = load_checkpoint()
    measurements = checkpoint.setdefault("measurements", {})

    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        key = case_key(candidate)
        census_case = case_lookup[key]
        case_for_baseline = {
            "label": f"rule{census_case['rule']}_bg{census_case['background']}_T{census_case['T_local']}",
            "role": census_case.get("role", "census"),
            "rule": census_case["rule"],
            "background": census_case["background"],
            "T_local": census_case["T_local"],
            "word": census_case["word"],
        }
        row = {
            "label": case_label(census_case),
            "rule": int(census_case["rule"]),
            "background": str(census_case["background"]),
            "T_local": int(census_case["T_local"]),
            "word": str(census_case["word"]),
            "category": str(census_case["category"]),
            "positive": str(census_case["category"]) in POSITIVE_CATEGORIES,
            "horizons": {},
        }
        for horizon in HORIZONS:
            mkey = checkpoint_key(census_case, horizon)
            if mkey not in measurements:
                print(f"Measuring {mkey}")
                measurements[mkey] = baseline.analyze_case(base, catalog, popcount16, case_for_baseline, horizon)
                save_json(CHECKPOINT_JSON, checkpoint)
            row["horizons"][str(horizon)] = measurement_summary(census_case, measurements[mkey], census_module)
        row["central_t15_like_horizons"] = [
            horizon for horizon in HORIZONS
            if row["horizons"][str(horizon)]["central_t15_like"]
        ]
        row["central_t15_like_count"] = len(row["central_t15_like_horizons"])
        row["persistent_all_horizons"] = row["central_t15_like_count"] == len(HORIZONS)
        row["persistent_independent_horizons"] = all(
            row["horizons"][str(horizon)]["central_t15_like"]
            for horizon in HORIZONS
            if horizon != 12
        )
        rows.append(row)

    return build_results(rows)


def confusion(rows: list[dict[str, Any]], predicate) -> dict[str, Any]:
    tp = fp = tn = fn = 0
    false_pos: list[str] = []
    false_neg: list[str] = []
    for row in rows:
        pred = bool(predicate(row))
        actual = bool(row["positive"])
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


def build_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    horizon_rules = {
        f"horizon_{horizon}_central_t15_like": confusion(
            rows, lambda row, horizon=horizon: row["horizons"][str(horizon)]["central_t15_like"]
        )
        for horizon in HORIZONS
    }
    persistence_rules = {
        "all_horizons_central_t15_like": confusion(rows, lambda row: row["persistent_all_horizons"]),
        "independent_horizons_8_16_20_central_t15_like": confusion(
            rows, lambda row: row["persistent_independent_horizons"]
        ),
        "at_least_3_horizons_central_t15_like": confusion(
            rows, lambda row: row["central_t15_like_count"] >= 3
        ),
    }
    all_rules = {**horizon_rules, **persistence_rules}
    rules_with_tp = {name: rule for name, rule in all_rules.items() if rule["tp"] > 0}
    if rules_with_tp:
        best_rule_name, best_rule = max(
            rules_with_tp.items(),
            key=lambda item: (item[1]["fp"] == 0, item[1]["tp"], item[1]["accuracy"], item[1]["recall"]),
        )
    else:
        best_rule_name, best_rule = max(
            all_rules.items(),
            key=lambda item: (item[1]["accuracy"], -item[1]["fp"], item[1]["recall"]),
        )

    if persistence_rules["independent_horizons_8_16_20_central_t15_like"]["perfect"]:
        status = "CENTRALITY_INDEPENDENT_HORIZONS_CONFIRMED"
        interpretation = (
            "Central T15-like ANF geometry persists across independent horizons and separates positives from "
            "centrality artefacts without using T_local>=8 as a classifier."
        )
    elif any(rule["fp"] == 0 and rule["tp"] > 0 for rule in {**horizon_rules, **persistence_rules}.values()):
        status = "CENTRALITY_INDEPENDENT_HORIZONS_PARTIAL"
        interpretation = (
            "Independent horizons provide a non-circular partial signal, but not a complete separator."
        )
    else:
        status = "CENTRALITY_HORIZON_DEPENDENT"
        interpretation = (
            "The central T15-like signal appears only at the original common horizon 12 for both positives "
            "and centrality artefacts. It does not survive as an independent-horizon discriminator; Fase 73 "
            "remains a descriptive consistency check rather than a non-circular validation."
        )

    return {
        "phase": 74,
        "source": {
            "census": CENSUS_JSON.name,
            "global_centrality": GLOBAL_JSON.name,
        },
        "horizons": HORIZONS,
        "rows": rows,
        "horizon_rules": horizon_rules,
        "persistence_rules": persistence_rules,
        "summary": {
            "status": status,
            "interpretation": interpretation,
            "candidate_count": len(rows),
            "positive_count": sum(1 for row in rows if row["positive"]),
            "non_positive_count": sum(1 for row in rows if not row["positive"]),
            "category_counts": dict(Counter(row["category"] for row in rows)),
            "horizon_positive_counts": {
                str(horizon): sum(
                    1 for row in rows
                    if row["horizons"][str(horizon)]["central_t15_like"] and row["positive"]
                )
                for horizon in HORIZONS
            },
            "horizon_artifact_counts": {
                str(horizon): sum(
                    1 for row in rows
                    if row["horizons"][str(horizon)]["central_t15_like"] and not row["positive"]
                )
                for horizon in HORIZONS
            },
            "best_rule_name": best_rule_name,
            "best_rule": best_rule,
            "positive_persistence_counts": [
                {
                    "label": row["label"],
                    "central_t15_like_count": row["central_t15_like_count"],
                    "central_t15_like_horizons": row["central_t15_like_horizons"],
                }
                for row in rows if row["positive"]
            ],
            "artifact_persistence_counts": [
                {
                    "label": row["label"],
                    "central_t15_like_count": row["central_t15_like_count"],
                    "central_t15_like_horizons": row["central_t15_like_horizons"],
                }
                for row in rows if not row["positive"]
            ],
        },
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def confusion_line(row: dict[str, Any]) -> str:
    return (
        f"TP={row['tp']} FP={row['fp']} TN={row['tn']} FN={row['fn']} "
        f"acc={row['accuracy']:.3f} prec={row['precision']:.3f} rec={row['recall']:.3f}"
    )


def write_report(data: dict[str, Any]) -> None:
    lines: list[str] = [
        "# Fase 74 - Independent Horizon Audit for ANF Centrality",
        "",
        "## Question",
        "",
        "Does exact ANF centrality remain a discriminator when the horizon is varied,",
        "without reusing `T_local>=8` as the classifier that originally split",
        "`HORIZON_ACCEPTABLE` from `HORIZON_ARTIFACT`?",
        "",
        "The audit remeasures the 13 Fase 72 centrality candidates at horizons",
        "`8`, `12`, `16`, and `20`. A case is marked `central_t15_like` at a",
        "horizon only when both conditions hold:",
        "",
        "- `max_active_monomial_dist == 0`",
        "- the active-output log-monomial fit is comparable to the T15 baseline",
        "  under the same slope/R^2 rule used by Fase 55",
        "",
        "## Candidate Table",
        "",
        "| case | cat | pos | T | h8 | h12 | h16 | h20 | count |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in data["rows"]:
        cells = []
        for horizon in data["horizons"]:
            hrow = row["horizons"][str(horizon)]
            cells.append("yes" if hrow["central_t15_like"] else "no")
        lines.append(
            f"| {row['label']} | {row['category']} | {row['positive']} | {row['T_local']} | "
            f"{cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} | {row['central_t15_like_count']} |"
        )

    lines.extend([
        "",
        "## Rule Tests",
        "",
        "| rule | confusion |",
        "|---|---:|",
    ])
    for name, row in data["horizon_rules"].items():
        lines.append(f"| {name} | {confusion_line(row)} |")
    for name, row in data["persistence_rules"].items():
        lines.append(f"| {name} | {confusion_line(row)} |")

    lines.extend([
        "",
        "Horizon-wise central T15-like counts:",
        "",
        "| horizon | positives | artefacts |",
        "|---:|---:|---:|",
    ])
    for horizon in data["horizons"]:
        lines.append(
            f"| {horizon} | {data['summary']['horizon_positive_counts'][str(horizon)]} | "
            f"{data['summary']['horizon_artifact_counts'][str(horizon)]} |"
        )

    lines.extend([
        "",
        "## Persistence Counts",
        "",
        "Positive candidates:",
        "",
    ])
    for row in data["summary"]["positive_persistence_counts"]:
        lines.append(f"- {row['label']}: {row['central_t15_like_count']}/4 horizons {row['central_t15_like_horizons']}")
    lines.extend(["", "Centrality artefacts:", ""])
    for row in data["summary"]["artifact_persistence_counts"]:
        lines.append(f"- {row['label']}: {row['central_t15_like_count']}/4 horizons {row['central_t15_like_horizons']}")

    lines.extend([
        "",
        "## Verdict",
        "",
        f"`{data['summary']['status']}`.",
        "",
        data["summary"]["interpretation"],
        "",
        f"Best rule: `{data['summary']['best_rule_name']}` -> {confusion_line(data['summary']['best_rule'])}.",
        "",
        "## Methodological Limit",
        "",
        "- This is still limited to the 13 exact-centrality candidates from Fase 72.",
        "- Positives outside rule_109 remain untestable because the Fase 55 census contains none.",
        "- The audit avoids using `T_local>=8` as a classifier, but still evaluates against",
        "  the Fase 55 category labels for bookkeeping.",
        "- Recomputing larger horizons is not a universal ECA proof; it is a non-circular",
        "  stress test of the Fase 73 descriptive split.",
        "",
    ])
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = measure_candidates()
    save_json(RESULTS_JSON, data)
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['summary']['status']}")
    print(f"Best: {data['summary']['best_rule_name']} -> {confusion_line(data['summary']['best_rule'])}")


if __name__ == "__main__":
    main()
