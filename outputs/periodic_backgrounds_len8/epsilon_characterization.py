#!/usr/bin/env python3
"""Fase 46: characterize the epsilon residual in the T=15 ANF gradient.

Fase 45 established the exact empirical law

    degree = 24 - abs(rel_pos) + epsilon, epsilon in {0,1}

for 174 active outputs. This script asks whether epsilon has a compact
predictor from features already available in the deterministic outputs.

The analysis deliberately excludes dist=0 and dist=1 because epsilon=0 there
in all known records; including those rows would inflate accuracy without
explaining the residual.
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
except Exception:  # pragma: no cover - report handles missing sklearn
    DecisionTreeClassifier = None
    export_text = None


OUT_DIR = Path(__file__).resolve().parent
SOURCE_JSON = OUT_DIR / "anf_stratification_results.json"
RESULTS_JSON = OUT_DIR / "epsilon_results.json"
REPORT_MD = OUT_DIR / "epsilon_report.md"

SAMPLE_START = 81
CENTER_INDEX = 12
MIN_DIST_FOR_RESIDUAL = 2


def circular_bits(word: str, start: int, length: int) -> str:
    n = len(word)
    return "".join(word[(start + offset) % n] for offset in range(length))


def circular_centered_bits(word: str, center: int, radius: int) -> str:
    n = len(word)
    return "".join(word[(center + offset) % n] for offset in range(-radius, radius + 1))


def bits_to_int(bits: str) -> int:
    return int(bits, 2)


def encode_sign(sign: str) -> int:
    return {"L": -1, "C": 0, "R": 1}[sign]


def encode_family(family_id: str) -> int:
    if family_id.startswith("F"):
        return int(family_id[1:])
    return int(family_id)


def load_records() -> list[dict[str, Any]]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for row in data["records"]:
        dist = abs(int(row["rel_pos"]))
        epsilon = int(row["epsilon"])
        if dist < MIN_DIST_FOR_RESIDUAL:
            continue
        bg = str(row["background"])
        output_index = int(row["output_index"])
        sample_pos = (SAMPLE_START + output_index) % len(bg)
        previous_pos = (SAMPLE_START + output_index - 1) % len(bg)
        background_bit = int(bg[sample_pos])
        previous_background_bit = int(bg[previous_pos])
        local_bg_2mer = circular_bits(bg, sample_pos, 2)
        local_bg_3mer = circular_centered_bits(bg, sample_pos, 1)
        enriched = {
            **row,
            "epsilon": epsilon,
            "dist": dist,
            "rule_binary": 0 if int(row["rule"]) == 73 else 1,
            "sign_code": encode_sign(str(row["sign"])),
            "background_bit": background_bit,
            "local_bg_2mer": local_bg_2mer,
            "local_bg_2mer_int": bits_to_int(local_bg_2mer),
            "local_bg_3mer": local_bg_3mer,
            "local_bg_3mer_int": bits_to_int(local_bg_3mer),
            "family_int": encode_family(str(row["family_id"])),
            "defect_phase": output_index % 5,
            "bg_transition": abs(background_bit - previous_background_bit),
            "sample_pos_mod_bg": sample_pos,
        }
        rows.append(enriched)
    return rows


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
    mapping: dict[str, int] = {}
    for value, counts in grouped.items():
        mapping[value] = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0][0]
    return mapping, default


def predict_value_mapping(rows: list[dict[str, Any]], feature: str, mapping: dict[str, int], default: int) -> list[int]:
    return [mapping.get(str(row[feature]), default) for row in rows]


def evaluate_single_feature(rows: list[dict[str, Any]], feature: str) -> dict[str, Any]:
    mapping, default = train_value_mapping(rows, feature)
    y_true = [int(row["epsilon"]) for row in rows]
    y_pred = predict_value_mapping(rows, feature, mapping, default)
    loro_scores: list[float] = []
    fold_details = []
    for rep_index in sorted({int(row["rep_index"]) for row in rows}):
        train = [row for row in rows if int(row["rep_index"]) != rep_index]
        test = [row for row in rows if int(row["rep_index"]) == rep_index]
        fold_mapping, fold_default = train_value_mapping(train, feature)
        fold_pred = predict_value_mapping(test, feature, fold_mapping, fold_default)
        fold_true = [int(row["epsilon"]) for row in test]
        fold_acc = accuracy(fold_true, fold_pred)
        loro_scores.append(fold_acc)
        fold_details.append(
            {
                "rep_index": rep_index,
                "n": len(test),
                "accuracy": fold_acc,
            }
        )
    return {
        "feature": feature,
        "train_accuracy": accuracy(y_true, y_pred),
        "loro_mean_accuracy": mean(loro_scores),
        "loro_std_accuracy": pstdev(loro_scores),
        "mapping": mapping,
        "default": default,
        "folds": fold_details,
    }


NUMERIC_FEATURES = [
    "rule_binary",
    "rel_pos",
    "dist",
    "sign_code",
    "background_bit",
    "local_bg_2mer_int",
    "local_bg_3mer_int",
    "family_int",
    "defect_phase",
    "bg_transition",
    "sample_pos_mod_bg",
]

CATEGORICAL_FEATURES = [
    "rule",
    "sign",
    "background_bit",
    "local_bg_2mer",
    "local_bg_3mer",
    "family_id",
    "defect_phase",
    "bg_transition",
]


def one_hot_feature_names(rows: list[dict[str, Any]]) -> list[str]:
    names = [f"num:{name}" for name in NUMERIC_FEATURES]
    for feature in CATEGORICAL_FEATURES:
        values = sorted({str(row[feature]) for row in rows})
        names.extend(f"cat:{feature}={value}" for value in values)
    return names


def vectorize(rows: list[dict[str, Any]], reference_rows: list[dict[str, Any]] | None = None) -> tuple[list[list[float]], list[str]]:
    ref = reference_rows if reference_rows is not None else rows
    names = [f"num:{name}" for name in NUMERIC_FEATURES]
    categories: list[tuple[str, list[str]]] = []
    for feature in CATEGORICAL_FEATURES:
        values = sorted({str(row[feature]) for row in ref})
        categories.append((feature, values))
        names.extend(f"cat:{feature}={value}" for value in values)

    vectors: list[list[float]] = []
    for row in rows:
        vector: list[float] = [float(row[name]) for name in NUMERIC_FEATURES]
        for feature, values in categories:
            row_value = str(row[feature])
            vector.extend(1.0 if row_value == value else 0.0 for value in values)
        vectors.append(vector)
    return vectors, names


def evaluate_tree(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if DecisionTreeClassifier is None or export_text is None:
        return {
            "available": False,
            "reason": "sklearn.tree.DecisionTreeClassifier is not available",
        }

    y = [int(row["epsilon"]) for row in rows]
    x, feature_names = vectorize(rows)
    clf = DecisionTreeClassifier(max_depth=3, random_state=0)
    clf.fit(x, y)
    train_pred = [int(value) for value in clf.predict(x)]

    fold_scores: list[float] = []
    fold_details = []
    all_fold_predictions = []
    for rep_index in sorted({int(row["rep_index"]) for row in rows}):
        train_rows = [row for row in rows if int(row["rep_index"]) != rep_index]
        test_rows = [row for row in rows if int(row["rep_index"]) == rep_index]
        train_x, train_names = vectorize(train_rows)
        test_x, _ = vectorize(test_rows, reference_rows=train_rows)
        train_y = [int(row["epsilon"]) for row in train_rows]
        test_y = [int(row["epsilon"]) for row in test_rows]
        fold_clf = DecisionTreeClassifier(max_depth=3, random_state=0)
        fold_clf.fit(train_x, train_y)
        fold_pred = [int(value) for value in fold_clf.predict(test_x)]
        fold_acc = accuracy(test_y, fold_pred)
        fold_scores.append(fold_acc)
        fold_details.append(
            {
                "rep_index": rep_index,
                "n": len(test_rows),
                "accuracy": fold_acc,
                "actual_epsilon_1": sum(test_y),
                "predicted_epsilon_1": sum(fold_pred),
            }
        )
        for row, pred in zip(test_rows, fold_pred):
            all_fold_predictions.append(
                {
                    "rep_index": int(row["rep_index"]),
                    "output_index": int(row["output_index"]),
                    "epsilon": int(row["epsilon"]),
                    "prediction": pred,
                    "correct": pred == int(row["epsilon"]),
                }
            )

    importances = [
        {"feature": name, "importance": float(value)}
        for name, value in sorted(
            zip(feature_names, clf.feature_importances_),
            key=lambda item: item[1],
            reverse=True,
        )
        if value > 0
    ]

    return {
        "available": True,
        "max_depth": 3,
        "train_accuracy": accuracy(y, train_pred),
        "loro_mean_accuracy": mean(fold_scores),
        "loro_std_accuracy": pstdev(fold_scores),
        "folds": fold_details,
        "tree_text": export_text(clf, feature_names=feature_names),
        "feature_importances": importances,
        "fold_predictions": sorted(all_fold_predictions, key=lambda row: (row["rep_index"], row["output_index"])),
    }


def verdict(simple_tests: list[dict[str, Any]], tree: dict[str, Any]) -> str:
    best_simple = max(test["loro_mean_accuracy"] for test in simple_tests)
    tree_acc = tree.get("loro_mean_accuracy", 0.0) if tree.get("available") else 0.0
    best = max(best_simple, tree_acc)
    if best >= 0.90:
        return "EPSILON_RULE_FOUND"
    if best >= 0.70:
        return "EPSILON_PARTIAL_PREDICTOR"
    return "EPSILON_REMAINS_RESIDUAL"


def analyze() -> dict[str, Any]:
    rows = load_records()
    simple_feature_names = [
        "background_bit",
        "bg_transition",
        "local_bg_2mer",
        "local_bg_3mer",
        "family_id",
        "defect_phase",
        "rule",
        "sign",
        "dist",
    ]
    simple_tests = [evaluate_single_feature(rows, feature) for feature in simple_feature_names]
    tree = evaluate_tree(rows)
    eps_counts = Counter(int(row["epsilon"]) for row in rows)
    result = {
        "status": verdict(simple_tests, tree),
        "source": str(SOURCE_JSON),
        "sample_start": SAMPLE_START,
        "center_index": CENTER_INDEX,
        "dist_filter": f"dist >= {MIN_DIST_FOR_RESIDUAL}",
        "record_count": len(rows),
        "rep_count": len({int(row["rep_index"]) for row in rows}),
        "epsilon_counts": dict(sorted(eps_counts.items())),
        "baseline_majority_accuracy": max(eps_counts.values()) / sum(eps_counts.values()),
        "simple_tests": simple_tests,
        "decision_tree": tree,
        "records": rows,
    }
    return result


def fmt_pct(value: float) -> str:
    return f"{100.0 * value:.2f}%"


def write_report(result: dict[str, Any]) -> None:
    lines: list[str] = [
        "# Fase 46: Epsilon Residual Characterization",
        "",
        "## Question",
        "",
        "Fase 45 established `degree = 24 - abs(rel_pos) + epsilon`,",
        "with `epsilon in {0,1}` and zero exceptions over 174 active outputs.",
        "Fase 46 asks whether the residual epsilon has a compact predictor.",
        "",
        "Rows with `dist=0` and `dist=1` are excluded because `epsilon=0` there",
        "in all known cases; keeping them would inflate accuracy without explaining",
        "the residual.",
        "",
        "## Summary",
        "",
        f"Status: `{result['status']}`.",
        "",
        f"- Source: `{result['source']}`",
        f"- Filter: `{result['dist_filter']}`",
        f"- Records analyzed: {result['record_count']}",
        f"- Representatives: {result['rep_count']}",
        f"- Epsilon counts: {result['epsilon_counts']}",
        f"- Majority baseline: {fmt_pct(result['baseline_majority_accuracy'])}",
        "",
        "## Simple single-feature predictors",
        "",
        "| feature | train acc | leave-one-rep-out mean | std | mapping |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for test in sorted(result["simple_tests"], key=lambda row: row["loro_mean_accuracy"], reverse=True):
        lines.append(
            "| {feature} | {train} | {loro} | {std} | `{mapping}` |".format(
                feature=test["feature"],
                train=fmt_pct(test["train_accuracy"]),
                loro=fmt_pct(test["loro_mean_accuracy"]),
                std=fmt_pct(test["loro_std_accuracy"]),
                mapping=test["mapping"],
            )
        )

    tree = result["decision_tree"]
    lines.extend(["", "## Decision tree, max_depth=3", ""])
    if not tree.get("available"):
        lines.append(f"DecisionTreeClassifier unavailable: {tree.get('reason')}.")
    else:
        lines.extend(
            [
                f"- Train accuracy: {fmt_pct(tree['train_accuracy'])}",
                f"- Leave-one-rep-out mean accuracy: {fmt_pct(tree['loro_mean_accuracy'])}",
                f"- Leave-one-rep-out std: {fmt_pct(tree['loro_std_accuracy'])}",
                "",
                "### Feature importances",
                "",
                "| feature | importance |",
                "| --- | ---: |",
            ]
        )
        for row in tree["feature_importances"]:
            lines.append(f"| `{row['feature']}` | {row['importance']:.6f} |")
        lines.extend(["", "### Tree", "", "```text", tree["tree_text"].rstrip(), "```", "", "### Leave-one-rep-out folds", "", "| rep | n | accuracy | actual eps=1 | predicted eps=1 |", "| ---: | ---: | ---: | ---: | ---: |"])
        for fold in tree["folds"]:
            lines.append(
                f"| {fold['rep_index']} | {fold['n']} | {fmt_pct(fold['accuracy'])} | {fold['actual_epsilon_1']} | {fold['predicted_epsilon_1']} |"
            )

    lines.extend(["", "## Interpretation", ""])
    if result["status"] == "EPSILON_RULE_FOUND":
        lines.append("A compact predictor meets the >=90% leave-one-rep-out gate.")
    elif result["status"] == "EPSILON_PARTIAL_PREDICTOR":
        lines.append(
            "A partial predictor exists, but it does not reach the >=90% gate required "
            "for a compact epsilon rule."
        )
    else:
        lines.append(
            "No tested feature set reaches 70% leave-one-rep-out accuracy. The epsilon "
            "bit remains a residual under the current local/background/family features."
        )
    lines.append(
        "This result does not refute the ANF gradient law; it separates the strong "
        "`24 - dist` backbone from the still-unexplained one-bit residual."
    )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    result = analyze()
    RESULTS_JSON.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    write_report(result)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {result['status']}")


if __name__ == "__main__":
    main()
