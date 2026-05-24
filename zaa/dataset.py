"""Dataset builder for Fase 2c symbolic regression."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .discovery import DiscoveryConfig, run_cycle


WORLD_SPECS: list[tuple[str, int, int]] = [
    ("rule_30", 24, 64),
    ("rule_110", 24, 64),
    ("synthetic_glider", 24, 64),
    ("synthetic_oscilador", 24, 64),
    ("synthetic_bloque", 24, 64),
    ("life_glider", 24, 64),
    ("life_blinker", 24, 64),
    ("life_block", 24, 64),
    ("rule_124", 24, 64),  # mirror de rule_110, 6/6 frontera_temporal positive
    ("rule_137", 24, 64),  # low density positive, breaks density_mean shortcut
    ("rule_109", 24, 64),  # borderline lower transition rate, 5/6 positive
    ("rule_54", 24, 64),  # high mutual info negative, breaks MI shortcut
]
N_SEEDS = 6
BASE_SEED = 20260523

METRIC_KEYS: list[str] = [
    "entropy_mean",
    "entropy_var",
    "gzip_ratio",
    "mutual_info_mean",
    "density_mean",
    "transition_rate",
]


def _law_accepted(details: list[dict], name: str) -> int:
    """Return 1 if named law is accepted in the details list, 0 otherwise."""
    for law in details:
        if law["name"] == name:
            return int(law["accepted"])
    return 0


def build_sample(world_type: str, steps: int, width: int, seed: int) -> dict[str, Any]:
    """Run one cycle and return a flat feature dict."""
    result = run_cycle(DiscoveryConfig(world_type=world_type, steps=steps, width=width, seed=seed), 0)
    sample: dict[str, Any] = {
        "world_type": world_type,
        "steps": steps,
        "width": width,
        "seed": seed,
        "analysis_status": result["analysis_status"],
        "structure_count": result["structure_count"],
        "dominant_type": result["dominant_type"],
    }
    for key in METRIC_KEYS:
        sample[key] = result["metrics"].get(key, 0.0)
    details = result.get("details", [])
    for law in (
        "velocidad_constante",
        "periodicidad",
        "densidad_estable",
        "tipo_unico",
        "complejidad_alta",
        "frontera_temporal",
        "temporal_scale_stability",
    ):
        sample[f"law_{law}"] = _law_accepted(details, law)
    return sample


def build_dataset(
    world_specs: list[tuple[str, int, int]] | None = None,
    n_seeds: int = N_SEEDS,
    base_seed: int = BASE_SEED,
) -> list[dict[str, Any]]:
    """Build dataset across all world specs and seeds."""
    specs = world_specs if world_specs is not None else WORLD_SPECS
    return [
        build_sample(world_type, steps, width, base_seed + i)
        for world_type, steps, width in specs
        for i in range(n_seeds)
    ]


def save_csv(samples: list[dict[str, Any]], path: str | Path) -> Path:
    """Save dataset as CSV. Column order follows first sample."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    if not samples:
        output.write_text("", encoding="utf-8")
        return output
    keys: list[str] = list(dict.fromkeys(key for sample in samples for key in sample))
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, extrasaction="ignore", restval="")
        writer.writeheader()
        writer.writerows(samples)
    return output


def save_jsonl(samples: list[dict[str, Any]], path: str | Path) -> Path:
    """Save dataset as JSONL."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, sort_keys=True) + "\n")
    return output
