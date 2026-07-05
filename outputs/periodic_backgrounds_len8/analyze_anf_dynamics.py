#!/usr/bin/env python3
"""Fase 47: dynamic ANF features for the T=15 epsilon residual.

Fase 46 showed that epsilon in

    degree = 24 - abs(rel_pos) + epsilon

is not predicted by static rule/background/family/position features. Fase 47
tests whether epsilon is predicted by the temporal growth profile of the ANF
inside the 25-cell, 12-step causal cone.

This script reuses the exact bit-packed truth-table simulation from Fase 44, but
computes ANF degree and monomial count at every cone layer t=1..12 for the final
active outputs. It then evaluates the same leave-one-representative-out protocol
used in Fase 46.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

import numpy as np

try:
    from sklearn.tree import DecisionTreeClassifier, export_text
except Exception:  # pragma: no cover
    DecisionTreeClassifier = None
    export_text = None


OUT_DIR = Path(__file__).resolve().parent
BASE_SCRIPT = OUT_DIR.parent / "periodic_backgrounds" / "sweep_periodic_background_oscillators.py"
SOURCE_JSON = OUT_DIR / "anf_degree_results.json"
RESULTS_JSON = OUT_DIR / "anf_dynamics_results.json"
REPORT_MD = OUT_DIR / "anf_dynamics_report.md"
CHECKPOINT_JSON = OUT_DIR / "anf_dynamics_checkpoint.json"

T_WINDOW = 12
WINDOW_CELLS = 25
CENTER_INDEX = 12
ASSIGNMENT_COUNT = 1 << WINDOW_CELLS
WORD_COUNT = ASSIGNMENT_COUNT // 64
UINT64_MAX = np.uint64((1 << 64) - 1)
MIN_DIST_FOR_RESIDUAL = 2


def load_base_module():
    spec = importlib.util.spec_from_file_location("periodic_background_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base detector from {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def bit_from_state(active: set[int], pos: int, width: int) -> int:
    return 1 if (pos % width) in active else 0


def ic_start(width: int, ic: str) -> int:
    return width // 2 - len(ic) // 2


def cone_positions(base, ic: str) -> list[int]:
    start = ic_start(base.WIDTH, ic)
    center = start + (len(ic) - 1) // 2
    left = center - T_WINDOW
    return list(range(left, left + WINDOW_CELLS))


def build_variable_tables() -> list[np.ndarray]:
    assignments = np.arange(ASSIGNMENT_COUNT, dtype=np.uint32)
    variables = []
    for idx in range(WINDOW_CELLS):
        bits = ((assignments >> idx) & 1).astype(np.uint8)
        variables.append(np.packbits(bits, bitorder="little").view(np.uint64).copy())
    return variables


def eca_packed(rule: int, left: np.ndarray, center: np.ndarray, right: np.ndarray, ones: np.ndarray) -> np.ndarray:
    out = np.zeros_like(left)
    for idx in range(8):
        if not ((rule >> idx) & 1):
            continue
        term = ones.copy()
        term &= left if (idx & 4) else ~left
        term &= center if (idx & 2) else ~center
        term &= right if (idx & 1) else ~right
        out ^= term
    return out


def mobius_inplace(bits: np.ndarray) -> None:
    for idx in range(WINDOW_CELLS):
        step = 1 << idx
        block = step << 1
        view = bits.reshape(-1, block)
        view[:, step:block] ^= view[:, :step]


def degree_and_count(coefficients: np.ndarray, popcount16: np.ndarray) -> tuple[int, int]:
    total = 0
    degree = -1
    chunk = 1 << 20
    for start in range(0, ASSIGNMENT_COUNT, chunk):
        sub = coefficients[start:start + chunk]
        count = int(sub.sum())
        if not count:
            continue
        total += count
        local = np.nonzero(sub)[0].astype(np.uint32) + np.uint32(start)
        degrees = popcount16[local & np.uint32(0xFFFF)] + popcount16[local >> np.uint32(16)]
        degree = max(degree, int(degrees.max()))
    return degree, total


def analyze_output_anf(table: np.ndarray, bg_bit: int, ones: np.ndarray, popcount16: np.ndarray) -> dict[str, int]:
    packed = table.copy()
    if bg_bit:
        packed ^= ones
    bits = np.unpackbits(packed.view(np.uint8), bitorder="little")
    mobius_inplace(bits)
    degree, monomial_count = degree_and_count(bits, popcount16)
    return {
        "degree": degree,
        "monomial_count": monomial_count,
        "constant_term": int(bits[0]),
    }


def simulate_dynamic_representative(base, variables, popcount16, source_row: dict[str, Any]) -> dict[str, Any]:
    rule = int(source_row["rule"])
    background = str(source_row["background"])
    ic = str(source_row["ic"])
    active_indices = [int(output["output_index"]) for output in source_row["active_outputs"]]
    expected_by_idx = {int(output["output_index"]): output for output in source_row["active_outputs"]}

    zeros = np.zeros(WORD_COUNT, dtype=np.uint64)
    ones = np.full(WORD_COUNT, UINT64_MAX, dtype=np.uint64)
    positions = cone_positions(base, ic)
    bg_frames = background_orbit(base, rule, background, T_WINDOW)
    rows = variables
    histories: dict[int, list[dict[str, int]]] = {idx: [] for idx in active_indices}

    started = time.perf_counter()
    for t in range(1, T_WINDOW + 1):
        bg_now = set(bg_frames[t - 1])
        next_rows = []
        for idx, global_pos in enumerate(positions):
            parents = []
            for delta in (-1, 0, 1):
                local = idx + delta
                if 0 <= local < WINDOW_CELLS:
                    parents.append(rows[local])
                else:
                    parents.append(ones if bit_from_state(bg_now, global_pos + delta, base.WIDTH) else zeros)
            next_rows.append(eca_packed(rule, parents[0], parents[1], parents[2], ones))
        rows = next_rows

        bg_t = set(bg_frames[t])
        for idx in active_indices:
            result = analyze_output_anf(
                rows[idx],
                bit_from_state(bg_t, positions[idx], base.WIDTH),
                ones,
                popcount16,
            )
            result["t"] = t
            histories[idx].append(result)

    mismatches = []
    active_outputs = []
    for idx in active_indices:
        final = histories[idx][-1]
        expected = expected_by_idx[idx]
        if int(final["degree"]) != int(expected["degree"]) or int(final["monomial_count"]) != int(expected["monomial_count"]):
            mismatches.append(
                {
                    "output_index": idx,
                    "expected_degree": int(expected["degree"]),
                    "actual_degree": int(final["degree"]),
                    "expected_monomial_count": int(expected["monomial_count"]),
                    "actual_monomial_count": int(final["monomial_count"]),
                }
            )
        active_outputs.append(
            {
                "output_index": idx,
                "expected_degree": int(expected["degree"]),
                "expected_monomial_count": int(expected["monomial_count"]),
                "history": histories[idx],
            }
        )

    return {
        "rule": rule,
        "background": background,
        "family_id": source_row["family_id"],
        "ic": ic,
        "active_outputs": active_outputs,
        "mismatches": mismatches,
        "runtime_seconds": time.perf_counter() - started,
    }


def load_checkpoint(path: Path) -> dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {"rows": []}


def save_checkpoint(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def slope(xs: list[float], ys: list[float]) -> float:
    mx = mean(xs)
    my = mean(ys)
    denom = sum((x - mx) ** 2 for x in xs)
    if denom == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / denom


def first_index(values: list[int], predicate) -> int:
    for idx, value in enumerate(values, start=1):
        if predicate(value):
            return idx
    return T_WINDOW + 1


def build_feature_rows(dynamic_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rep_index, rep in enumerate(dynamic_rows):
        by_idx = {int(output["output_index"]): output for output in rep["active_outputs"]}
        for output in rep["active_outputs"]:
            output_index = int(output["output_index"])
            rel_pos = output_index - CENTER_INDEX
            dist = abs(rel_pos)
            if dist < MIN_DIST_FOR_RESIDUAL:
                continue
            history = output["history"]
            degrees = [int(item["degree"]) for item in history]
            monomials = [int(item["monomial_count"]) for item in history]
            logs = [math.log10(value + 1) for value in monomials]
            degree_final = int(output["expected_degree"])
            epsilon = degree_final - (24 - dist)
            t_first_full_degree = first_index(degrees, lambda value: value == degree_final)
            t_first_nonzero = first_index(monomials, lambda value: value > 0)
            t_first_degree_ge_20 = first_index(degrees, lambda value: value >= 20)
            degree_growth_slope = slope([float(t) for t in range(1, T_WINDOW + 1)], [float(v) for v in degrees])
            monomial_growth_slope = slope([float(t) for t in range(1, T_WINDOW + 1)], logs)
            max_degree_jump = max(degrees[i] - degrees[i - 1] for i in range(1, len(degrees)))

            mirror_idx = 24 - output_index
            mirror = by_idx.get(mirror_idx)
            if mirror is not None:
                mirror_history = mirror["history"]
                mirror_degrees = [int(item["degree"]) for item in mirror_history]
                mirror_logs = [math.log10(int(item["monomial_count"]) + 1) for item in mirror_history]
                mirror_degree_final = int(mirror["expected_degree"])
                mirror_t_first = first_index(mirror_degrees, lambda value: value == mirror_degree_final)
                lr_degree_diff_final = degree_final - mirror_degree_final
                lr_t_first_diff = t_first_full_degree - mirror_t_first
                lr_slope_diff = degree_growth_slope - slope([float(t) for t in range(1, T_WINDOW + 1)], [float(v) for v in mirror_degrees])
                lr_log_slope_diff = monomial_growth_slope - slope([float(t) for t in range(1, T_WINDOW + 1)], mirror_logs)
                mirror_active = 1
            else:
                lr_degree_diff_final = 0
                lr_t_first_diff = 0
                lr_slope_diff = 0.0
                lr_log_slope_diff = 0.0
                mirror_active = 0

            rows.append(
                {
                    "rep_index": rep_index,
                    "rule": int(rep["rule"]),
                    "rule_binary": 0 if int(rep["rule"]) == 73 else 1,
                    "background": rep["background"],
                    "family_id": rep["family_id"],
                    "family_int": int(str(rep["family_id"])[1:]),
                    "ic": rep["ic"],
                    "output_index": output_index,
                    "rel_pos": rel_pos,
                    "dist": dist,
                    "sign_code": -1 if rel_pos < 0 else (1 if rel_pos > 0 else 0),
                    "defect_phase": output_index % 5,
                    "epsilon": epsilon,
                    "degree_final": degree_final,
                    "degree_at_t3": degrees[2],
                    "degree_at_t6": degrees[5],
                    "degree_at_t9": degrees[8],
                    "t_first_full_degree": t_first_full_degree,
                    "t_first_nonzero": t_first_nonzero,
                    "t_first_degree_ge_20": t_first_degree_ge_20,
                    "degree_growth_slope": degree_growth_slope,
                    "max_degree_jump": max_degree_jump,
                    "log10_monomials_at_t3": logs[2],
                    "log10_monomials_at_t6": logs[5],
                    "log10_monomials_at_t9": logs[8],
                    "monomial_growth_slope": monomial_growth_slope,
                    "mirror_active": mirror_active,
                    "lr_degree_diff_final": lr_degree_diff_final,
                    "lr_t_first_diff": lr_t_first_diff,
                    "lr_slope_diff": lr_slope_diff,
                    "lr_log_slope_diff": lr_log_slope_diff,
                    "degree_series": degrees,
                    "monomial_series": monomials,
                }
            )
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
    loro_scores: list[float] = []
    folds = []
    for rep_index in sorted({int(row["rep_index"]) for row in rows}):
        train = [row for row in rows if int(row["rep_index"]) != rep_index]
        test = [row for row in rows if int(row["rep_index"]) == rep_index]
        fold_mapping, fold_default = train_value_mapping(train, feature)
        fold_pred = predict_value_mapping(test, feature, fold_mapping, fold_default)
        fold_true = [int(row["epsilon"]) for row in test]
        fold_acc = accuracy(fold_true, fold_pred)
        loro_scores.append(fold_acc)
        folds.append({"rep_index": rep_index, "n": len(test), "accuracy": fold_acc})
    return {
        "feature": feature,
        "train_accuracy": accuracy(y_true, y_pred),
        "loro_mean_accuracy": mean(loro_scores),
        "loro_std_accuracy": pstdev(loro_scores),
        "mapping": mapping,
        "default": default,
        "folds": folds,
    }


NUMERIC_FEATURES = [
    "dist",
    "defect_phase",
    "degree_at_t3",
    "degree_at_t6",
    "degree_at_t9",
    "t_first_full_degree",
    "t_first_nonzero",
    "t_first_degree_ge_20",
    "degree_growth_slope",
    "max_degree_jump",
    "log10_monomials_at_t3",
    "log10_monomials_at_t6",
    "log10_monomials_at_t9",
    "monomial_growth_slope",
    "mirror_active",
    "lr_degree_diff_final",
    "lr_t_first_diff",
    "lr_slope_diff",
    "lr_log_slope_diff",
]


def vectorize(rows: list[dict[str, Any]], reference_rows: list[dict[str, Any]] | None = None) -> tuple[list[list[float]], list[str]]:
    names = NUMERIC_FEATURES[:]
    return [[float(row[name]) for name in names] for row in rows], names


def evaluate_tree(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if DecisionTreeClassifier is None or export_text is None:
        return {"available": False, "reason": "sklearn.tree.DecisionTreeClassifier is not available"}
    y = [int(row["epsilon"]) for row in rows]
    x, feature_names = vectorize(rows)
    clf = DecisionTreeClassifier(max_depth=3, random_state=0)
    clf.fit(x, y)
    train_pred = [int(value) for value in clf.predict(x)]
    fold_scores = []
    folds = []
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
        folds.append(
            {
                "rep_index": rep_index,
                "n": len(test_rows),
                "accuracy": fold_acc,
                "actual_epsilon_1": sum(test_y),
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
        "max_depth": 3,
        "train_accuracy": accuracy(y, train_pred),
        "loro_mean_accuracy": mean(fold_scores),
        "loro_std_accuracy": pstdev(fold_scores),
        "folds": folds,
        "tree_text": export_text(clf, feature_names=feature_names),
        "feature_importances": importances,
    }


def verdict(simple_tests: list[dict[str, Any]], tree: dict[str, Any]) -> str:
    best_simple = max(test["loro_mean_accuracy"] for test in simple_tests)
    tree_acc = tree.get("loro_mean_accuracy", 0.0) if tree.get("available") else 0.0
    best = max(best_simple, tree_acc)
    if best >= 0.90:
        return "EPSILON_DYNAMIC_RULE_FOUND"
    if best >= 0.70:
        return "EPSILON_DYNAMIC_PARTIAL_PREDICTOR"
    return "EPSILON_DYNAMICALLY_RESIDUAL"


def run_dynamic(checkpoint_path: Path, limit_reps: int | None = None) -> dict[str, Any]:
    source = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    source_rows = source["rows"]
    if limit_reps is not None:
        source_rows = source_rows[:limit_reps]
    checkpoint = load_checkpoint(checkpoint_path)
    done = {(int(row["rule"]), row["background"]) for row in checkpoint["rows"]}
    base = load_base_module()
    variables = build_variable_tables()
    popcount16 = np.array([int(value).bit_count() for value in range(1 << 16)], dtype=np.uint8)
    for source_row in source_rows:
        key = (int(source_row["rule"]), source_row["background"])
        if key in done:
            continue
        row = simulate_dynamic_representative(base, variables, popcount16, source_row)
        checkpoint["rows"].append(row)
        save_checkpoint(checkpoint_path, checkpoint)
        print(
            f"rep {len(checkpoint['rows'])}/{len(source_rows)} "
            f"rule={row['rule']} bg={row['background']} "
            f"runtime={row['runtime_seconds']:.1f}s mismatches={len(row['mismatches'])}",
            flush=True,
        )
    return checkpoint


def analyze(checkpoint_path: Path, limit_reps: int | None = None) -> dict[str, Any]:
    checkpoint = run_dynamic(checkpoint_path, limit_reps=limit_reps)
    rows = checkpoint["rows"]
    feature_rows = build_feature_rows(rows)
    simple_features = [
        "dist",
        "defect_phase",
        "degree_at_t3",
        "degree_at_t6",
        "degree_at_t9",
        "t_first_full_degree",
        "t_first_degree_ge_20",
        "degree_growth_slope",
        "max_degree_jump",
        "log10_monomials_at_t6",
        "monomial_growth_slope",
        "lr_degree_diff_final",
        "lr_t_first_diff",
        "lr_slope_diff",
        "lr_log_slope_diff",
    ]
    simple_tests = [evaluate_single_feature(feature_rows, feature) for feature in simple_features]
    tree = evaluate_tree(feature_rows)
    eps_counts = Counter(int(row["epsilon"]) for row in feature_rows)
    mismatch_rows = [m for row in rows for m in row["mismatches"]]
    status = "ANF_DYNAMIC_MISMATCH_FOUND" if mismatch_rows else verdict(simple_tests, tree)
    return {
        "status": status,
        "source": str(SOURCE_JSON),
        "checkpoint": str(checkpoint_path),
        "record_count": len(feature_rows),
        "rep_count": len(rows),
        "epsilon_counts": dict(sorted(eps_counts.items())),
        "baseline_majority_accuracy": max(eps_counts.values()) / sum(eps_counts.values()) if eps_counts else None,
        "mismatch_count": len(mismatch_rows),
        "mismatches": mismatch_rows,
        "simple_tests": simple_tests,
        "decision_tree": tree,
        "records": feature_rows,
        "dynamic_rows": rows,
    }


def fmt_pct(value: float) -> str:
    return f"{100.0 * value:.2f}%"


def write_report(result: dict[str, Any], report_path: Path) -> None:
    lines = [
        "# Fase 47: Dynamic ANF Features for the T=15 Epsilon Residual",
        "",
        "## Question",
        "",
        "Fase 46 found no static predictor for the epsilon residual in",
        "`degree = 24 - abs(rel_pos) + epsilon`. Fase 47 tests whether epsilon",
        "is predicted by the temporal ANF growth profile inside the 25-cell,",
        "12-step causal cone.",
        "",
        "## Summary",
        "",
        f"Status: `{result['status']}`.",
        "",
        f"- Representatives: {result['rep_count']}",
        f"- Records analyzed (`dist>=2`): {result['record_count']}",
        f"- Epsilon counts: {result['epsilon_counts']}",
        f"- Majority baseline: {fmt_pct(result['baseline_majority_accuracy']) if result['baseline_majority_accuracy'] is not None else 'n/a'}",
        f"- t=12 verification mismatches against Fase 44: {result['mismatch_count']}",
        "",
        "## Single-feature predictors",
        "",
        "| feature | train acc | leave-one-rep-out mean | std |",
        "| --- | ---: | ---: | ---: |",
    ]
    for test in sorted(result["simple_tests"], key=lambda row: row["loro_mean_accuracy"], reverse=True):
        lines.append(
            f"| `{test['feature']}` | {fmt_pct(test['train_accuracy'])} | "
            f"{fmt_pct(test['loro_mean_accuracy'])} | {fmt_pct(test['loro_std_accuracy'])} |"
        )
    tree = result["decision_tree"]
    lines.extend(["", "## Decision tree, max_depth=3", ""])
    if not tree.get("available"):
        lines.append(f"Decision tree unavailable: {tree.get('reason')}.")
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
        lines.extend(["", "### Tree", "", "```text", tree["tree_text"].rstrip(), "```"])
        lines.extend(["", "### Leave-one-rep-out folds", "", "| rep | n | accuracy | actual eps=1 | predicted eps=1 |", "| ---: | ---: | ---: | ---: | ---: |"])
        for fold in tree["folds"]:
            lines.append(
                f"| {fold['rep_index']} | {fold['n']} | {fmt_pct(fold['accuracy'])} | "
                f"{fold['actual_epsilon_1']} | {fold['predicted_epsilon_1']} |"
            )

    lines.extend(["", "## Interpretation", ""])
    if result["mismatch_count"]:
        lines.append("The dynamic ANF recomputation did not match Fase 44 at t=12; inspect mismatches before interpreting predictors.")
    elif result["status"] == "EPSILON_DYNAMIC_RULE_FOUND":
        lines.append("Dynamic ANF features meet the >=90% leave-one-representative-out gate.")
        lines.append(
            "The strongest feature is the full `degree_growth_slope` over t=1..12. "
            "This should be interpreted as a dynamic full-profile law of ANF growth, "
            "not as a static pre-computation shortcut: the feature uses the complete "
            "temporal degree trajectory through the final cone layer."
        )
    elif result["status"] == "EPSILON_DYNAMIC_PARTIAL_PREDICTOR":
        lines.append("Dynamic ANF features improve on static features but do not reach the >=90% rule gate.")
    else:
        lines.append("Dynamic ANF features do not reach 70% leave-one-representative-out accuracy. Under this feature class, epsilon remains dynamically residual.")
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-reps", type=int, default=None)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT_JSON)
    parser.add_argument("--results", type=Path, default=RESULTS_JSON)
    parser.add_argument("--report", type=Path, default=REPORT_MD)
    args = parser.parse_args()
    result = analyze(args.checkpoint, limit_reps=args.limit_reps)
    args.results.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_report(result, args.report)
    print(f"Wrote {args.results}")
    print(f"Wrote {args.report}")
    print(f"Status: {result['status']}")


if __name__ == "__main__":
    main()
