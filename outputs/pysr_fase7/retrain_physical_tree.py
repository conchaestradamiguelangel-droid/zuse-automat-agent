"""Fase 8c retrain: physical features -> n_laws_accepted.

Uses the clean post-8c journal with 15 worlds.  This deliberately excludes
world-history features; the model only sees current-cycle physical metrics.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
JOURNAL = ROOT / "outputs" / "experiments_2026-05-27" / "journal_8c_long.jsonl"
OUT = ROOT / "outputs" / "pysr_fase7"
OUT_JSON = OUT / "retrain_physical_tree_8c.json"

PHYSICAL_FEATURES = [
    "dedup_structure_count",
    "inflation_ratio",
    "entropy_mean",
    "entropy_var",
    "gzip_ratio",
    "mutual_info_mean",
    "density_mean",
    "transition_rate",
    "analysis_ok",
    "steps",
]


def _num(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    if isinstance(value, bool):
        return float(int(value))
    return float(value)


def load_rows() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in JOURNAL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_matrix(rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray]:
    x_rows: list[list[float]] = []
    y: list[float] = []
    for row in rows:
        metrics = row.get("metrics", {})
        feature = {
            "dedup_structure_count": _num(row.get("dedup_structure_count")),
            "inflation_ratio": _num(row.get("inflation_ratio")),
            "entropy_mean": _num(metrics.get("entropy_mean")),
            "entropy_var": _num(metrics.get("entropy_var")),
            "gzip_ratio": _num(metrics.get("gzip_ratio")),
            "mutual_info_mean": _num(metrics.get("mutual_info_mean")),
            "density_mean": _num(metrics.get("density_mean")),
            "transition_rate": _num(metrics.get("transition_rate")),
            "analysis_ok": float(row.get("analysis_status") == "ok"),
            "steps": _num(row.get("steps")),
        }
        x_rows.append([feature[name] for name in PHYSICAL_FEATURES])
        y.append(float(len(row.get("laws_accepted", []))))
    return np.array(x_rows, dtype=np.float64), np.array(y, dtype=np.float64)


def per_world_summary(rows: list[dict[str, Any]], predictions: np.ndarray) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[tuple[dict[str, Any], float]]] = defaultdict(list)
    for row, pred in zip(rows, predictions, strict=True):
        grouped[row.get("world_type", "?")].append((row, float(pred)))

    summary: dict[str, dict[str, Any]] = {}
    for world, items in sorted(grouped.items()):
        actual = np.array([len(row.get("laws_accepted", [])) for row, _ in items], dtype=float)
        pred = np.array([p for _, p in items], dtype=float)
        statuses = Counter(row.get("analysis_status") for row, _ in items)
        signatures = Counter(tuple(row.get("laws_accepted", [])) for row, _ in items)
        summary[world] = {
            "n": len(items),
            "status": dict(statuses),
            "actual_mean": float(np.mean(actual)),
            "pred_mean": float(np.mean(pred)),
            "actual_values": actual.astype(int).tolist(),
            "pred_values": [round(float(v), 3) for v in pred.tolist()],
            "signatures": {
                "|".join(sig) if sig else "EMPTY": count
                for sig, count in signatures.most_common()
            },
        }
    return summary


def main() -> None:
    from sklearn.metrics import mean_squared_error, r2_score
    from sklearn.tree import DecisionTreeRegressor, export_text

    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    x, y = build_matrix(rows)

    tree = DecisionTreeRegressor(max_depth=4, random_state=42)
    tree.fit(x, y)
    pred = tree.predict(x)

    r2 = float(r2_score(y, pred))
    rmse = float(mean_squared_error(y, pred) ** 0.5)
    tree_text = export_text(tree, feature_names=PHYSICAL_FEATURES)
    importances = {
        name: float(value)
        for name, value in sorted(
            zip(PHYSICAL_FEATURES, tree.feature_importances_, strict=True),
            key=lambda item: item[1],
            reverse=True,
        )
    }
    world_summary = per_world_summary(rows, pred)
    depth_scan: list[dict[str, Any]] = []
    for depth in [2, 3, 4, 5, 6, 8]:
        candidate = DecisionTreeRegressor(max_depth=depth, random_state=42)
        candidate.fit(x, y)
        candidate_pred = candidate.predict(x)
        depth_scan.append(
            {
                "max_depth": depth,
                "r2": float(r2_score(y, candidate_pred)),
                "rmse": float(mean_squared_error(y, candidate_pred) ** 0.5),
            }
        )

    print(f"Journal: {JOURNAL}")
    print(f"Rows: {len(rows)}")
    print(f"Target n_laws_accepted: min={int(np.min(y))} max={int(np.max(y))} mean={np.mean(y):.3f} std={np.std(y):.3f}")
    print(f"DecisionTreeRegressor(max_depth=4): R2={r2:.6f} RMSE={rmse:.6f}")
    print("\nFeature importance:")
    for name, value in importances.items():
        print(f"  {name:<24} {value:.6f}")
    print("\nTree:")
    print(tree_text)
    print("\nPer-world focus:")
    for world in ["rule_18", "rule_90", "rule_150", "rule_106", "rule_137", "rule_54", "rule_109"]:
        if world not in world_summary:
            continue
        s = world_summary[world]
        print(
            f"  {world:<8} n={s['n']:>2} actual_mean={s['actual_mean']:.3f} "
            f"pred_mean={s['pred_mean']:.3f} status={s['status']}"
        )
        print(f"    signatures={s['signatures']}")
    print("\nDepth scan:")
    for row in depth_scan:
        print(f"  depth={row['max_depth']:<2} R2={row['r2']:.6f} RMSE={row['rmse']:.6f}")

    OUT_JSON.write_text(
        json.dumps(
            {
                "journal": str(JOURNAL.relative_to(ROOT)),
                "rows": len(rows),
                "features": PHYSICAL_FEATURES,
                "target": "n_laws_accepted",
                "tree": {
                    "model": "DecisionTreeRegressor(max_depth=4, random_state=42)",
                    "r2": r2,
                    "rmse": rmse,
                    "feature_importance": importances,
                    "tree_text": tree_text,
                },
                "depth_scan": depth_scan,
                "world_summary": world_summary,
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    print(f"\nSaved: {OUT_JSON}")


if __name__ == "__main__":
    main()
