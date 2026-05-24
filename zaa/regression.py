"""Symbolic regression interface for Fase 2c. No hard dependencies."""

from __future__ import annotations

from typing import Any


FEATURE_KEYS: list[str] = [
    "transition_rate",
    "entropy_mean",
    "density_mean",
    "gzip_ratio",
    "structure_count",
    "mutual_info_mean",
]
TARGET_KEY: str = "law_frontera_temporal"


def fit_tree(samples: list[dict[str, Any]], max_depth: int = 3) -> dict[str, Any]:
    """Fit a decision tree as a symbolic proxy. Requires sklearn."""
    try:
        from sklearn.tree import DecisionTreeClassifier, export_text
    except ImportError:
        return {"error": "sklearn_not_installed", "install": "pip install scikit-learn"}

    ok = [sample for sample in samples if sample.get("analysis_status") == "ok"]
    if not ok:
        return {"error": "no_ok_samples"}

    x_values = [[float(sample.get(key, 0.0)) for key in FEATURE_KEYS] for sample in ok]
    y_values = [int(sample.get(TARGET_KEY, 0)) for sample in ok]

    clf = DecisionTreeClassifier(max_depth=max_depth, random_state=42)
    clf.fit(x_values, y_values)
    return {
        "method": "decision_tree",
        "accuracy": float(clf.score(x_values, y_values)),
        "feature_importances": dict(zip(FEATURE_KEYS, clf.feature_importances_.tolist())),
        "tree_text": export_text(clf, feature_names=FEATURE_KEYS),
    }


def fit_pysr(samples: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    """Fit PySR if installed. Returns error dict otherwise."""
    try:
        from pysr import PySRRegressor
    except ImportError:
        return {"error": "pysr_not_installed", "install": "pip install pysr"}

    ok = [sample for sample in samples if sample.get("analysis_status") == "ok"]
    if not ok:
        return {"error": "no_ok_samples"}

    import numpy as np

    x_values = np.array([[float(sample.get(key, 0.0)) for key in FEATURE_KEYS] for sample in ok])
    y_values = np.array([float(sample.get(TARGET_KEY, 0.0)) for sample in ok])

    defaults: dict[str, Any] = {
        "niterations": 40,
        "binary_operators": ["+", "*", "-", "/"],
        "unary_operators": [],
    }
    defaults.update(kwargs)
    model = PySRRegressor(**defaults)
    model.fit(x_values, y_values)
    best = model.get_best()
    return {
        "method": "pysr",
        "equation": str(best["equation"]),
        "loss": float(best["loss"]),
        "complexity": int(best["complexity"]),
    }
