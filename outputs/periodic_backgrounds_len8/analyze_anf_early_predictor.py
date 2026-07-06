#!/usr/bin/env python3
"""Fase 48: early dynamic ANF predictor for the T=15 epsilon residual.

Fase 47 showed that the complete degree-growth trajectory over t=1..12 predicts
epsilon with high leave-one-representative-out accuracy. Fase 48 asks how much
of that trajectory is needed: can epsilon be predicted before the final cone
layer, or is the full profile required?
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

try:
    from sklearn.tree import DecisionTreeClassifier, export_text
except Exception:  # pragma: no cover
    DecisionTreeClassifier = None
    export_text = None


OUT_DIR = Path(__file__).resolve().parent
SOURCE_JSON = OUT_DIR / "anf_dynamics_results.json"
RESULTS_JSON = OUT_DIR / "anf_early_predictor_results.json"
REPORT_MD = OUT_DIR / "anf_early_predictor_report.md"

CENTER_INDEX = 12
MIN_DIST_FOR_RESIDUAL = 2
HORIZONS = [6, 8, 9, 10, 11, 12]
REFERENCE_K12_LORO = 0.948974358974359


def slope(xs: list[float], ys: list[float]) -> float:
    mx = mean(xs)
    my = mean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom


def accuracy(y_true: list[int], y_pred: list[int]) -> float:
    return sum(int(a == b) for a, b in zip(y_true, y_pred)) / len(y_true)


def majority_label(rows: list[dict[str, Any]]) -> int:
    counts = Counter(int(row["epsilon"]) for row in rows)
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]


def train_value_mapping(rows: list[dict[str, Any]], feature: str) -> tuple[dict[str, int], int]:
    grouped: dict[str, Counter[int]] = defaultdict(Counter)
    for row in rows:
        grouped[str(row[feature])][int(row["epsilon"])] += 1
    default = majority_label(rows)
    mapping = {}
    for value, counts in grouped.items():
        mapping[value] = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return mapping, default


def predict_value_mapping(rows: list[dict[str, Any]], feature: str, mapping: dict[str, int], default: int) -> list[int]:
    return [mapping.get(str(row[feature]), default) for row in rows]


def evaluate_single_feature(rows: list[dict[str, Any]], feature: str) -> dict[str, Any]:
    mapping, default = train_value_mapping(rows, feature)
    y_true = [int(row["epsilon"]) for row in rows]
    y_pred = predict_value_mapping(rows, feature, mapping, default)
    fold_scores = []
    folds = []
    for rep_index in sorted({int(row["rep_index"]) for row in rows}):
        train = [row for row in rows if int(row["rep_index"]) != rep_index]
        test = [row for row in rows if int(row["rep_index"]) == rep_index]
        fold_mapping, fold_default = train_value_mapping(train, feature)
        fold_pred = predict_value_mapping(test, feature, fold_mapping, fold_default)
        fold_true = [int(row["epsilon"]) for row in test]
        fold_acc = accuracy(fold_true, fold_pred)
        fold_scores.append(fold_acc)
        folds.append({"rep_index": rep_index, "n": len(test), "accuracy": fold_acc})
    return {
        "feature": feature,
        "train_accuracy": accuracy(y_true, y_pred),
        "loro_mean_accuracy": mean(fold_scores),
        "loro_std_accuracy": pstdev(fold_scores),
        "mapping_size": len(mapping),
        "folds": folds,
    }


def vectorize(rows: list[dict[str, Any]], feature_names: list[str]) -> list[list[float]]:
    return [[float(row[name]) for name in feature_names] for row in rows]


def evaluate_tree(rows: list[dict[str, Any]], feature_names: list[str]) -> dict[str, Any]:
    if DecisionTreeClassifier is None or export_text is None:
        return {"available": False, "reason": "sklearn.tree.DecisionTreeClassifier is not available"}
    y = [int(row["epsilon"]) for row in rows]
    x = vectorize(rows, feature_names)
    clf = DecisionTreeClassifier(max_depth=3, random_state=0)
    clf.fit(x, y)
    train_pred = [int(value) for value in clf.predict(x)]
    fold_scores = []
    folds = []
    for rep_index in sorted({int(row["rep_index"]) for row in rows}):
        train_rows = [row for row in rows if int(row["rep_index"]) != rep_index]
        test_rows = [row for row in rows if int(row["rep_index"]) == rep_index]
        fold_clf = DecisionTreeClassifier(max_depth=3, random_state=0)
        fold_clf.fit(vectorize(train_rows, feature_names), [int(row["epsilon"]) for row in train_rows])
        fold_pred = [int(value) for value in fold_clf.predict(vectorize(test_rows, feature_names))]
        fold_true = [int(row["epsilon"]) for row in test_rows]
        fold_acc = accuracy(fold_true, fold_pred)
        fold_scores.append(fold_acc)
        folds.append(
            {
                "rep_index": rep_index,
                "n": len(test_rows),
                "accuracy": fold_acc,
                "actual_epsilon_1": sum(fold_true),
                "predicted_epsilon_1": sum(fold_pred),
            }
        )
    importances = [
        {"feature": name, "importance": float(value)}
        for name, value in sorted(zip(feature_names, clf.feature_importances_), key=lambda item: item[1], reverse=True)
        if value > 0
    ]
    return {
        "available": True,
        "train_accuracy": accuracy(y, train_pred),
        "loro_mean_accuracy": mean(fold_scores),
        "loro_std_accuracy": pstdev(fold_scores),
        "folds": folds,
        "tree_text": export_text(clf, feature_names=feature_names),
        "feature_importances": importances,
    }


def first_full_degree(degrees: list[int], expected_degree: int, horizon: int) -> int:
    for t, degree in enumerate(degrees[:horizon], start=1):
        if degree == expected_degree:
            return t
    return horizon + 1


def build_rows_for_horizon(data: dict[str, Any], horizon: int) -> list[dict[str, Any]]:
    rows = []
    for rep_index, rep in enumerate(data["dynamic_rows"]):
        for output in rep["active_outputs"]:
            output_index = int(output["output_index"])
            rel_pos = output_index - CENTER_INDEX
            dist = abs(rel_pos)
            if dist < MIN_DIST_FOR_RESIDUAL:
                continue
            expected_degree = int(output["expected_degree"])
            epsilon = expected_degree - (24 - dist)
            history = output["history"][:horizon]
            degrees = [int(item["degree"]) for item in history]
            monomials = [int(item["monomial_count"]) for item in history]
            logs = [math.log10(max(1, value)) for value in monomials]
            ts = [float(t) for t in range(1, horizon + 1)]
            rows.append(
                {
                    "rep_index": rep_index,
                    "rule": int(rep["rule"]),
                    "background": rep["background"],
                    "family_id": rep["family_id"],
                    "output_index": output_index,
                    "rel_pos": rel_pos,
                    "dist": dist,
                    "defect_phase": output_index % 5,
                    "epsilon": epsilon,
                    f"degree_growth_slope_{horizon}": slope(ts, [float(v) for v in degrees]),
                    f"t_first_full_degree_{horizon}": first_full_degree(degrees, expected_degree, horizon),
                    f"monomial_growth_slope_{horizon}": slope(ts, logs),
                }
            )
    return rows


def verdict(summary: list[dict[str, Any]]) -> str:
    first_hit = None
    for row in summary:
        if row["degree_growth_loro"] >= 0.90:
            first_hit = row["horizon"]
            break
    if first_hit is None:
        return "NO_DYNAMIC_RULE_BY_T12"
    if first_hit <= 9:
        return "EARLY_DYNAMIC_RULE_FOUND"
    if first_hit in (10, 11):
        return "PARTIAL_PROFILE_REQUIRED"
    return "FULL_PROFILE_REQUIRED"


def analyze() -> dict[str, Any]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    horizon_results = []
    all_rows_by_horizon = {}
    for horizon in HORIZONS:
        rows = build_rows_for_horizon(data, horizon)
        degree_feature = f"degree_growth_slope_{horizon}"
        first_feature = f"t_first_full_degree_{horizon}"
        monomial_feature = f"monomial_growth_slope_{horizon}"
        degree_eval = evaluate_single_feature(rows, degree_feature)
        first_eval = evaluate_single_feature(rows, first_feature)
        monomial_eval = evaluate_single_feature(rows, monomial_feature)
        tree_features = [degree_feature, first_feature, monomial_feature, "dist"]
        tree = evaluate_tree(rows, tree_features)
        horizon_results.append(
            {
                "horizon": horizon,
                "record_count": len(rows),
                "degree_growth": degree_eval,
                "t_first_full_degree": first_eval,
                "monomial_growth": monomial_eval,
                "tree": tree,
                "degree_growth_loro": degree_eval["loro_mean_accuracy"],
                "tree_loro": tree.get("loro_mean_accuracy") if tree.get("available") else None,
            }
        )
        all_rows_by_horizon[str(horizon)] = rows
    k12 = next(row for row in horizon_results if row["horizon"] == 12)
    k12_delta = abs(k12["degree_growth_loro"] - REFERENCE_K12_LORO)
    return {
        "status": verdict(horizon_results),
        "source": str(SOURCE_JSON),
        "horizons": HORIZONS,
        "reference_k12_loro": REFERENCE_K12_LORO,
        "k12_loro_delta": k12_delta,
        "k12_reproduces_fase47": k12_delta <= 0.02,
        "horizon_results": horizon_results,
        "rows_by_horizon": all_rows_by_horizon,
        "notes": [
            "degree_growth_slope_K uses only degrees from t=1..K and is future-blind.",
            "t_first_full_degree_K uses expected_degree from Fase 44 and is not fully future-blind.",
        ],
    }


def fmt_pct(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{100.0 * value:.2f}%"


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# Fase 48: Early Dynamic ANF Predictor",
        "",
        "## Question",
        "",
        "Fase 47 found that the complete `degree_growth_slope` over `t=1..12`",
        "predicts epsilon with 94.90% leave-one-representative-out accuracy.",
        "Fase 48 asks how much of that trajectory is necessary.",
        "",
        "## Summary",
        "",
        f"Status: `{result['status']}`.",
        "",
        f"- Source: `{result['source']}`",
        f"- Horizons tested: {result['horizons']}",
        f"- K=12 reproduces Fase 47 within 2 percentage points: `{result['k12_reproduces_fase47']}`",
        f"- K=12 delta from Fase 47 reference: {fmt_pct(result['k12_loro_delta'])}",
        "",
        "Important note: `degree_growth_slope_K` is future-blind and uses only",
        "`t=1..K`. `t_first_full_degree_K` uses the final expected degree from Fase",
        "44 and is therefore not fully future-blind.",
        "",
        "## Horizon table",
        "",
        "| K | degree_growth_slope_K LORO | degree train | monomial slope LORO | t_first_full LORO | tree LORO | tree train |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in result["horizon_results"]:
        lines.append(
            f"| {row['horizon']} | {fmt_pct(row['degree_growth']['loro_mean_accuracy'])} | "
            f"{fmt_pct(row['degree_growth']['train_accuracy'])} | "
            f"{fmt_pct(row['monomial_growth']['loro_mean_accuracy'])} | "
            f"{fmt_pct(row['t_first_full_degree']['loro_mean_accuracy'])} | "
            f"{fmt_pct(row['tree_loro'])} | {fmt_pct(row['tree'].get('train_accuracy') if row['tree'].get('available') else None)} |"
        )
    lines.extend(["", "## Per-horizon tree summaries", ""])
    for row in result["horizon_results"]:
        lines.append(f"### K={row['horizon']}")
        lines.append("")
        tree = row["tree"]
        if not tree.get("available"):
            lines.append(f"Tree unavailable: {tree.get('reason')}.")
        else:
            lines.append(f"- Train accuracy: {fmt_pct(tree['train_accuracy'])}")
            lines.append(f"- LORO mean accuracy: {fmt_pct(tree['loro_mean_accuracy'])}")
            lines.append("- Feature importances:")
            for item in tree["feature_importances"]:
                lines.append(f"  - `{item['feature']}`: {item['importance']:.6f}")
        lines.append("")
    lines.extend(["## Interpretation", ""])
    if result["status"] == "EARLY_DYNAMIC_RULE_FOUND":
        lines.append("A future-blind early dynamic predictor reaches the >=90% gate by K<=9.")
    elif result["status"] == "PARTIAL_PROFILE_REQUIRED":
        lines.append("The >=90% gate is reached before the final layer, but only late in the cone (K=10 or K=11).")
    elif result["status"] == "FULL_PROFILE_REQUIRED":
        lines.append("The >=90% gate is reached only at K=12. The v1.17 result is therefore a full-profile law, not an early predictor.")
    else:
        lines.append("No tested horizon reaches the >=90% gate, including K=12; this would contradict Fase 47 and should be inspected.")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    result = analyze()
    RESULTS_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(result)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {result['status']}")


if __name__ == "__main__":
    main()
