"""Fase 20b: long-journal integration test for top frontera candidates.

Runs the normal ZUSE discovery loop over the four strongest newly profiled
frontera-rich candidates without modifying production WORLD_SEQUENCE. The
policy module is scoped to a local four-world sequence inside this artifact.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.discovery import DiscoveryConfig, run_discovery_loop, save_journal  # noqa: E402
from zaa import policy  # noqa: E402


OUT_DIR = ROOT / "outputs" / "frontera_sweep" / "top4_long_journal_fase20b"
JOURNAL = OUT_DIR / "journal_top4_long.jsonl"
STATE = OUT_DIR / "agent_state_top4_long.json"
REPORT = OUT_DIR / "top4_long_report.md"
SUMMARY = OUT_DIR / "top4_long_summary.json"

WORLDS = ["rule_84", "rule_138", "rule_212", "rule_213"]
START_WORLD = WORLDS[0]
CYCLES = 160
STEPS = 24
WIDTH = 64
BASE_SEED = 20260610

DIVERSITY_THRESHOLD = 0.5
NON_EMPTY_RATIO_THRESHOLD = 0.5
NOISE_RATIO_THRESHOLD = 0.5
RICH_LAWS_THRESHOLD = 4.0

LAW_ORDER = [
    "velocidad_constante",
    "periodicidad",
    "densidad_estable",
    "tipo_unico",
    "complejidad_alta",
    "frontera_temporal",
    "temporal_scale_stability",
]


def classify_world(stats: dict[str, Any]) -> str:
    if stats["total_visits"] == 0:
        return "sin-datos"
    if stats["noise_ratio"] > NOISE_RATIO_THRESHOLD:
        return "noise-bounded"
    if stats["peak_diversity"] is not None and stats["peak_diversity"] > DIVERSITY_THRESHOLD:
        if stats["non_empty_ratio"] < NON_EMPTY_RATIO_THRESHOLD:
            return "multiregimen-escala-dependiente"
        return "multiregimen-productivo"
    if stats["mean_laws"] >= RICH_LAWS_THRESHOLD:
        return "frontera-rich-estable"
    return "sin-evidencia-multiregimen"


def load_journal() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in JOURNAL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def signature_label(signature: tuple[str, ...]) -> str:
    return " + ".join(signature) if signature else "EMPTY"


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    by_world: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_world[row["world_type"]].append(row)

    stats_by_world: dict[str, Any] = {}
    for world in WORLDS:
        items = by_world.get(world, [])
        non_empty = [row for row in items if row.get("laws_accepted")]
        noise = [row for row in items if row.get("analysis_status") == "ruido_no_analizable"]
        silence = [
            row
            for row in items
            if row.get("analysis_status") == "ok" and not row.get("laws_accepted")
        ]
        signatures = Counter(tuple(row.get("laws_accepted", [])) for row in non_empty)
        unique_non_empty = len(signatures)
        non_empty_ratio = len(non_empty) / len(items) if items else 0.0
        peak_diversity = unique_non_empty / len(non_empty) if len(non_empty) >= 5 else None
        law_counts = Counter()
        for row in non_empty:
            law_counts.update(row.get("laws_accepted", []))
        stats = {
            "world": world,
            "total_visits": len(items),
            "non_empty_visits": len(non_empty),
            "noise_visits": len(noise),
            "silence_visits": len(silence),
            "non_empty_ratio": non_empty_ratio,
            "noise_ratio": len(noise) / len(items) if items else 0.0,
            "peak_diversity": peak_diversity,
            "mean_laws": mean(len(row.get("laws_accepted", [])) for row in items) if items else 0.0,
            "mean_steps": mean(int(row.get("steps", 0)) for row in items) if items else 0.0,
            "max_steps": max((int(row.get("steps", 0)) for row in items), default=0),
            "mean_dedup": mean(float(row.get("dedup_structure_count", 0)) for row in items) if items else 0.0,
            "max_dedup": max((int(row.get("dedup_structure_count", 0)) for row in items), default=0),
            "law_frequencies": {
                law: {
                    "count": law_counts[law],
                    "rate": law_counts[law] / len(non_empty) if non_empty else 0.0,
                }
                for law in LAW_ORDER
            },
            "dominant_signature": signature_label(signatures.most_common(1)[0][0]) if signatures else "EMPTY",
            "signature_counts": {
                signature_label(signature): count
                for signature, count in signatures.most_common()
            },
            "actions": dict(Counter(row.get("action_taken", "") for row in items)),
            "reasons": dict(Counter(row.get("action_reason", "") for row in items)),
        }
        stats["classification"] = classify_world(stats)
        stats_by_world[world] = stats

    return {
        "config": {
            "worlds": WORLDS,
            "cycles": CYCLES,
            "steps": STEPS,
            "width": WIDTH,
            "base_seed": BASE_SEED,
        },
        "stats_by_world": stats_by_world,
    }


def fmt(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.3f}"


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(summary: dict[str, Any]) -> str:
    stats_by_world = summary["stats_by_world"]
    overview_rows = []
    law_rows = []
    for world, stats in stats_by_world.items():
        overview_rows.append(
            [
                world,
                stats["classification"],
                str(stats["total_visits"]),
                fmt(stats["non_empty_ratio"]),
                fmt(stats["noise_ratio"]),
                fmt(stats["peak_diversity"]),
                fmt(stats["mean_laws"]),
                fmt(stats["mean_steps"]),
                str(stats["max_steps"]),
                stats["dominant_signature"],
            ]
        )
        law_rows.append(
            [
                world,
                *[
                    fmt(stats["law_frequencies"][law]["rate"])
                    for law in LAW_ORDER
                ],
            ]
        )

    class_counts = Counter(stats["classification"] for stats in stats_by_world.values())
    class_rows = [[label, str(count)] for label, count in sorted(class_counts.items())]

    all_stable = all(
        stats["classification"] == "frontera-rich-estable"
        for stats in stats_by_world.values()
    )
    verdict = (
        "All four top candidates remain `frontera-rich-estable` under the "
        "independent long-journal policy run."
        if all_stable
        else "The top candidates do **not** remain `frontera-rich-estable` "
        "under the independent long-journal policy run."
    )
    consequence = (
        "These worlds are suitable candidates for formal atlas integration if "
        "the atlas is expanded beyond the current canonical set."
        if all_stable
        else "The fixed `steps=24` profile should be treated as a frontera "
        "filter, not as atlas-grade stability evidence. These four worlds "
        "should not be promoted to the canonical atlas without a scale-aware "
        "category or additional controlled protocol."
    )

    return f"""# Top-4 Frontera Long Journal - Fase 20b

## Setup

- Worlds: `{', '.join(WORLDS)}`
- Cycles: `{CYCLES}`
- Initial steps: `{STEPS}`
- Width: `{WIDTH}`
- Base seed: `{BASE_SEED}`
- Journal: `outputs/frontera_sweep/top4_long_journal_fase20b/journal_top4_long.jsonl`
- State: `outputs/frontera_sweep/top4_long_journal_fase20b/agent_state_top4_long.json`

The script runs the normal ZUSE discovery loop with a local four-world
`WORLD_SEQUENCE` override. No production code or atlas sequence is modified.

## Classification Summary

{table(["classification", "count"], class_rows)}

## World Summary

{table(
        [
            "world",
            "classification",
            "visits",
            "non_empty_ratio",
            "noise_ratio",
            "peak_diversity",
            "mean_laws",
            "mean_steps",
            "max_steps",
            "dominant_signature",
        ],
        overview_rows,
    )}

## Law Frequency Rates

Rates are computed over non-empty visits.

{table(["world", *LAW_ORDER], law_rows)}

## Interpretation

{verdict}

This upgrades the Fase 20a result from a fixed six-seed profile to an
independent policy-run check for the four strongest additional candidates.
{consequence}
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if JOURNAL.exists():
        JOURNAL.unlink()
    if STATE.exists():
        STATE.unlink()

    original_sequence = list(policy.WORLD_SEQUENCE)
    try:
        policy.WORLD_SEQUENCE[:] = WORLDS
        config = DiscoveryConfig(
            START_WORLD,
            steps=STEPS,
            width=WIDTH,
            seed=BASE_SEED,
            cycles=CYCLES,
            state_file=str(STATE),
        )
        results = run_discovery_loop(config)
        save_journal(results, JOURNAL)
    finally:
        policy.WORLD_SEQUENCE[:] = original_sequence

    summary = analyze(load_journal())
    SUMMARY.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(render_report(summary), encoding="utf-8")

    print(f"journal={JOURNAL}")
    print(f"summary={SUMMARY}")
    for world, stats in summary["stats_by_world"].items():
        print(
            f"{world}: {stats['classification']} visits={stats['total_visits']} "
            f"mean_laws={stats['mean_laws']:.3f} peak_div={stats['peak_diversity']}"
        )


if __name__ == "__main__":
    main()
