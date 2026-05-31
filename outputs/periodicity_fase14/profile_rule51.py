"""Fase 15a: formal profile for rule_51 global periodicity."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import mean
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.discovery import DiscoveryConfig, run_cycle


OUT_DIR = ROOT / "outputs" / "periodicity_fase14"
OUT_JSON = OUT_DIR / "rule51_profile.json"
OUT_MD = OUT_DIR / "rule51_profile.md"

RULE = 51
WORLD = "rule_51"
SEEDS = list(range(20260523, 20260529))
STEPS = 96
WIDTH = 64

LAW_ORDER = [
    "velocidad_constante",
    "periodicidad",
    "densidad_estable",
    "tipo_unico",
    "complejidad_alta",
    "frontera_temporal",
    "temporal_scale_stability",
]


def frequency_class(count: int) -> str:
    if count >= 4:
        return "core"
    if count >= 2:
        return "present"
    if count == 1:
        return "trace"
    return "absent"


def run_profile() -> dict[str, Any]:
    rows = []
    for seed in SEEDS:
        result = run_cycle(
            DiscoveryConfig(WORLD, steps=STEPS, width=WIDTH, seed=seed),
            0,
        )
        laws = result.get("laws_accepted", [])
        rows.append(
            {
                "seed": seed,
                "analysis_status": result.get("analysis_status"),
                "analysis_ok": result.get("analysis_status") == "ok",
                "structure_count": result.get("structure_count"),
                "dedup_structure_count": result.get("dedup_structure_count"),
                "inflation_ratio": result.get("inflation_ratio"),
                "dominant_type": result.get("dominant_type"),
                "laws_accepted": laws,
                "n_laws_accepted": len(laws),
                "metrics": result.get("metrics", {}),
            }
        )

    law_counts = Counter()
    signatures = Counter()
    for row in rows:
        law_counts.update(row["laws_accepted"])
        signatures.update([tuple(row["laws_accepted"])])

    non_empty_visits = sum(bool(row["laws_accepted"]) for row in rows)
    noise_visits = sum(row["analysis_status"] == "ruido_no_analizable" for row in rows)
    unique_non_empty = len({tuple(row["laws_accepted"]) for row in rows if row["laws_accepted"]})
    peak_diversity = unique_non_empty / non_empty_visits if non_empty_visits >= 5 else None

    return {
        WORLD: {
            "rule_id": RULE,
            "steps": STEPS,
            "width": WIDTH,
            "seeds": SEEDS,
            "classification": "periodicidad-global",
            "total_visits": len(rows),
            "ok_visits": sum(row["analysis_ok"] for row in rows),
            "noise_visits": noise_visits,
            "non_empty_visits": non_empty_visits,
            "non_empty_ratio": non_empty_visits / len(rows),
            "peak_diversity": peak_diversity,
            "mean_n_laws": mean(row["n_laws_accepted"] for row in rows),
            "mean_dedup_structure_count": mean(row["dedup_structure_count"] for row in rows),
            "mean_transition_rate": mean(float(row["metrics"].get("transition_rate") or 0.0) for row in rows),
            "mean_entropy": mean(float(row["metrics"].get("entropy_mean") or 0.0) for row in rows),
            "law_frequencies": {
                law: {
                    "count": law_counts[law],
                    "rate": law_counts[law] / len(rows),
                    "class": frequency_class(law_counts[law]),
                }
                for law in LAW_ORDER
            },
            "signatures": {
                " + ".join(sig) if sig else "EMPTY": count
                for sig, count in signatures.most_common()
            },
            "rows": rows,
        }
    }


def fmt(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.3f}"


def table(headers: list[str], body: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def render_markdown(profile: dict[str, Any]) -> str:
    item = profile[WORLD]
    law_rows = [
        [
            law,
            f"{item['law_frequencies'][law]['count']}/6",
            item["law_frequencies"][law]["class"],
        ]
        for law in LAW_ORDER
    ]
    return f"""# Rule 51 Global Periodicity Profile - Fase 15a

Protocol: `steps={STEPS}`, `width={WIDTH}`, seeds `20260523..20260528`.

`rule_51` is `f(a,b,c) = NOT b`: every cell complements itself each step,
independent of neighbors. The resulting period-2 behavior is global and
deterministic for every IC.

## Overview

- Classification: `periodicidad-global`
- ok: `{item['ok_visits']}/6`
- mean_n_laws: `{fmt(item['mean_n_laws'])}`
- peak_diversity: `{fmt(item['peak_diversity'])}`
- mean_dedup_structure_count: `{fmt(item['mean_dedup_structure_count'])}`
- mean_transition_rate: `{fmt(item['mean_transition_rate'])}`
- mean_entropy: `{fmt(item['mean_entropy'])}`

## Law Frequencies

{table(["law", "count", "class"], law_rows)}

## Signatures

{json.dumps(item["signatures"], indent=2, ensure_ascii=False)}

## Interpretation

This validates `periodicidad` on real ECA dynamics, but not as a local particle
oscillator. It is global frame-level period-2 complementation. The current
observer correctly detects periodicity, but the physical mechanism is distinct
from `synthetic_oscilador` or `life_blinker`.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    profile = run_profile()
    OUT_JSON.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(render_markdown(profile), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
