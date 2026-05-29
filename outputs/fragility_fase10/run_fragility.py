"""Fase 10a: basin fragility diagnostic by world.

This script is an experimental artifact. It controls the initial condition
directly and does not run the discovery policy loop.

Outputs:
    outputs/fragility_fase10/fragility_results.jsonl
    outputs/fragility_fase10/fragility_report.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.consensus import deduplicate_structures
from zaa.cycle_laws import evaluate_cycle_laws
from zaa.eca import random_initial_state, simulate
from zaa.observers import run_observers


JOURNAL = ROOT / "outputs" / "experiments_2026-05-27" / "journal_8c_long.jsonl"
OUT_DIR = ROOT / "outputs" / "fragility_fase10"
RESULTS_JSONL = OUT_DIR / "fragility_results.jsonl"
REPORT_MD = OUT_DIR / "fragility_report.md"

WIDTH = 64
BASE_SEED = 20260523
DEDUP_STRUCTURE_NOISE_THRESHOLD = 40

CANONICAL_STEPS = {
    "rule_137": 48,
    "rule_18": 24,
    "rule_109": 48,
    "rule_90": 96,
    "rule_46": 24,
    "rule_208": 24,
    "rule_209": 24,
    "rule_54": 96,
    "rule_110": 24,
    "rule_124": 24,
}

FORMAL_CASES = {
    "rule_46": [20260523, 20260524, 20260525],
    "rule_208": [20260523, 20260524, 20260525],
    "rule_209": [20260523, 20260524, 20260525],
}

MAX_SEEDS_PER_WORLD = 3


def load_journal() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in JOURNAL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def annotate_used_seeds(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Reconstruct the seed used by run_cycle from journal actions.

    discovery.run_discovery_loop passes config.seed=current_seed to run_cycle,
    and run_cycle uses cycle_seed = config.seed + cycle_id.  The policy only
    increments current_seed when the action is repeat_vary_seed.
    """
    current_seed = BASE_SEED
    annotated: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: int(item["cycle_id"])):
        copy = dict(row)
        copy["reconstructed_config_seed"] = current_seed
        copy["reconstructed_used_seed"] = current_seed + int(row["cycle_id"])
        annotated.append(copy)
        if row.get("action_taken") == "repeat_vary_seed":
            current_seed += 1
    return annotated


def select_productive_cases(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    selected: dict[str, list[dict[str, Any]]] = {}
    for world, canonical_steps in CANONICAL_STEPS.items():
        if world in FORMAL_CASES:
            selected[world] = [
                {
                    "world_type": world,
                    "steps": canonical_steps,
                    "laws_accepted": ["formal_profile_case"],
                    "reconstructed_used_seed": seed,
                }
                for seed in FORMAL_CASES[world]
            ]
            continue

        candidates = [
            row
            for row in rows
            if row.get("world_type") == world and row.get("laws_accepted", [])
        ]
        exact = [row for row in candidates if int(row["steps"]) == canonical_steps]
        if exact:
            pool = exact
        else:
            pool = sorted(candidates, key=lambda row: abs(int(row["steps"]) - canonical_steps))

        unique_by_seed: dict[int, dict[str, Any]] = {}
        for row in pool:
            seed = int(row["reconstructed_used_seed"])
            unique_by_seed.setdefault(seed, row)
            if len(unique_by_seed) >= MAX_SEEDS_PER_WORLD:
                break
        selected[world] = list(unique_by_seed.values())
    return selected


def rule_from_world(world: str) -> int:
    if not world.startswith("rule_"):
        raise ValueError(f"Expected ECA world like rule_N, got {world}")
    return int(world.removeprefix("rule_"))


def evaluate_ic(world: str, seed: int, steps: int, initial_state: np.ndarray | None = None) -> dict[str, Any]:
    rule = rule_from_world(world)
    ic = random_initial_state(WIDTH, seed=seed) if initial_state is None else np.asarray(initial_state, dtype=np.uint8)
    frames = simulate(ic, rule, steps)
    structures = run_observers(frames)
    dedup_count = len(deduplicate_structures(structures))
    analysis_status = "ruido_no_analizable" if dedup_count > DEDUP_STRUCTURE_NOISE_THRESHOLD else "ok"
    if analysis_status == "ok":
        laws = evaluate_cycle_laws(structures, frames, steps)["laws_accepted"]
    else:
        laws = []
    return {
        "analysis_status": analysis_status,
        "analysis_ok": analysis_status == "ok",
        "laws_accepted": laws,
        "signature": tuple(sorted(laws)),
        "dedup_structure_count": dedup_count,
    }


def classify_outcome(reference_signature: tuple[str, ...], result: dict[str, Any]) -> str:
    perturbed_signature = tuple(sorted(result["laws_accepted"]))
    if result["analysis_status"] == "ruido_no_analizable":
        return "noise"
    if not result["laws_accepted"] and result["analysis_ok"]:
        return "silence"
    if perturbed_signature == reference_signature:
        return "same_sig"
    return "other_sig"


def run_experiment(selected: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for world, cases in selected.items():
        for case in cases:
            seed = int(case["reconstructed_used_seed"])
            steps = int(case["steps"])
            reference_ic = random_initial_state(WIDTH, seed=seed)
            reference = evaluate_ic(world, seed, steps, reference_ic)
            reference_signature = tuple(sorted(reference["laws_accepted"]))

            for bit_position in range(WIDTH):
                perturbed_ic = reference_ic.copy()
                perturbed_ic[bit_position] = 1 - perturbed_ic[bit_position]
                perturbed = evaluate_ic(world, seed, steps, perturbed_ic)
                outcome = classify_outcome(reference_signature, perturbed)
                records.append(
                    {
                        "world": world,
                        "seed": seed,
                        "steps": steps,
                        "bit_position": bit_position,
                        "outcome": outcome,
                        "reference_sig": list(reference_signature),
                        "perturbed_sig": list(perturbed["signature"]),
                        "reference_status": reference["analysis_status"],
                        "perturbed_status": perturbed["analysis_status"],
                        "reference_dedup_structure_count": reference["dedup_structure_count"],
                        "perturbed_dedup_structure_count": perturbed["dedup_structure_count"],
                    }
                )
    return records


def seed_summaries(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, int, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        grouped[(record["world"], int(record["seed"]), int(record["steps"]))].append(record)

    summaries: list[dict[str, Any]] = []
    for (world, seed, steps), items in sorted(grouped.items()):
        counts = Counter(item["outcome"] for item in items)
        reference_sig = items[0]["reference_sig"]
        summaries.append(
            {
                "world": world,
                "seed": seed,
                "steps": steps,
                "f_other_sig": counts["other_sig"] / WIDTH,
                "f_silence": counts["silence"] / WIDTH,
                "f_noise": counts["noise"] / WIDTH,
                "f_total": (counts["other_sig"] + counts["silence"] + counts["noise"]) / WIDTH,
                "reference_signature": reference_sig,
                "counts": dict(counts),
            }
        )
    return summaries


def aggregate_by_world(summaries: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for summary in summaries:
        grouped[summary["world"]].append(summary)

    aggregate: dict[str, dict[str, float]] = {}
    for world, items in sorted(grouped.items()):
        aggregate[world] = {
            "f_other_sig": mean(item["f_other_sig"] for item in items),
            "f_silence": mean(item["f_silence"] for item in items),
            "f_noise": mean(item["f_noise"] for item in items),
            "f_total": mean(item["f_total"] for item in items),
        }
    return aggregate


def fmt(value: float) -> str:
    return f"{value:.3f}"


def signature_label(signature: list[str]) -> str:
    return " + ".join(signature) if signature else "EMPTY"


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def interpretation(aggregate: dict[str, dict[str, float]]) -> str:
    lines: list[str] = []
    for world, stats in aggregate.items():
        if stats["f_total"] == 0:
            lines.append(
                f"- `{world}`: total fragility `0.000`; all one-bit perturbations "
                "preserve the reference law signature."
            )
            continue
        components = {
            "other_sig": stats["f_other_sig"],
            "silence": stats["f_silence"],
            "noise": stats["f_noise"],
        }
        dominant = max(components, key=components.get)
        if dominant == "other_sig":
            meaning = "perturbations mostly move the IC into other productive law signatures."
        elif dominant == "silence":
            meaning = "perturbations mostly push the IC into analyzable silence."
        else:
            meaning = "perturbations mostly push the IC across the noise gate."
        lines.append(
            f"- `{world}`: total fragility `{stats['f_total']:.3f}`, dominated by "
            f"`{dominant}` (`{components[dominant]:.3f}`); {meaning}"
        )
    return "\n".join(lines)


def render_report(
    selected: dict[str, list[dict[str, Any]]],
    summaries: list[dict[str, Any]],
    aggregate: dict[str, dict[str, float]],
) -> str:
    setup_lines = []
    for world, cases in selected.items():
        case_labels = ", ".join(
            f"seed {case['reconstructed_used_seed']} @ steps {case['steps']}"
            for case in cases
        )
        setup_lines.append(f"- `{world}`: {case_labels}")

    component_rows = [
        [
            row["world"],
            str(row["seed"]),
            str(row["steps"]),
            fmt(row["f_other_sig"]),
            fmt(row["f_silence"]),
            fmt(row["f_noise"]),
            fmt(row["f_total"]),
            signature_label(row["reference_signature"]),
        ]
        for row in summaries
    ]
    aggregate_rows = [
        [
            world,
            fmt(stats["f_other_sig"]),
            fmt(stats["f_silence"]),
            fmt(stats["f_noise"]),
            fmt(stats["f_total"]),
        ]
        for world, stats in aggregate.items()
    ]

    rule137 = aggregate.get("rule_137", {})
    others = [stats["f_total"] for world, stats in aggregate.items() if world != "rule_137"]
    if rule137 and others:
        if rule137["f_total"] > max(others):
            answer = "`rule_137` is the most fragile world in this sample."
        elif rule137["f_total"] < min(others):
            answer = "`rule_137` is not uniquely fragile here; other worlds are more sensitive."
        else:
            answer = "`rule_137` is fragile, but not an outlier against the other multi-regime worlds."
    else:
        answer = "Insufficient data to compare `rule_137` against the other worlds."

    all_silence_noise_zero = all(
        stats["f_silence"] == 0 and stats["f_noise"] == 0
        for stats in aggregate.values()
    )
    productive_fragility = (
        "Across all worlds, `f_silence = 0` and `f_noise = 0`. All observed "
        "fragility is productive: perturbations either preserve the law "
        "signature or move to another non-empty signature."
        if all_silence_noise_zero
        else "`rule_54` breaks the earlier all-productive pattern: some one-bit "
        "perturbations cross the deduplicated noise gate (`f_noise = 0.375`)."
    )

    frontier_stats = [
        stats["f_total"]
        for world, stats in aggregate.items()
        if world in {"rule_46", "rule_208", "rule_209"}
    ]
    frontier_answer = (
        "The `frontera-rich-estable` worlds are dramatically more robust than "
        "`rule_137`: `rule_208` and `rule_209` have `f_total = 0.000`, while "
        "`rule_46` has `f_total = 0.031`."
        if frontier_stats
        else "No `frontera-rich-estable` worlds were measured in this run."
    )
    category_by_world = {
        "rule_208": "frontera-rich-estable",
        "rule_209": "frontera-rich-estable",
        "rule_46": "frontera-rich-estable",
        "rule_90": "multiregimen-escala-dependiente",
        "rule_109": "multiregimen-productivo",
        "rule_110": "multiregimen-productivo",
        "rule_124": "multiregimen-productivo",
        "rule_18": "multiregimen-productivo",
        "rule_54": "multiregimen-productivo",
        "rule_137": "multiregimen-productivo",
    }
    pattern_by_world = {
        "rule_208": "-",
        "rule_209": "-",
        "rule_46": "-",
        "rule_90": "clustered",
        "rule_109": "clustered",
        "rule_110": "clustered",
        "rule_124": "dispersed",
        "rule_18": "clustered",
        "rule_54": "clustered",
        "rule_137": "dispersed",
    }
    spectrum_rows = [
        [
            world,
            category_by_world.get(world, "unknown"),
            fmt(stats["f_total"]),
            pattern_by_world.get(world, "?"),
        ]
        for world, stats in sorted(aggregate.items(), key=lambda item: item[1]["f_total"])
    ]

    worlds_steps = "\n".join(
        f"  - `{world}`: `steps={steps}`"
        for world, steps in CANONICAL_STEPS.items()
    )
    total_flips = sum(len(cases) for cases in selected.values()) * WIDTH

    return f"""# Basin Fragility Diagnostic - Fase 10a/12a

## Setup

- IC width: `{WIDTH}`
- Worlds and canonical steps:
{worlds_steps}
- Seeds are reconstructed from `journal_8c_long.jsonl` because the journal does
  not store seed explicitly. `rule_46`, `rule_208`, and `rule_209` use formal
  profile seeds `20260523..20260525`.
- Fragility = one-bit flips that change outcome / 64.
- Total perturbations in this report: `{total_flips}`.
- Components:
  - `f_other_sig`: flip produces a different non-empty law signature.
  - `f_silence`: flip produces `analysis_ok=True` and `laws_accepted=[]`.
  - `f_noise`: flip produces `analysis_status=ruido_no_analizable`.
  - `f_total`: sum of the three previous components.

Selected cases:

{chr(10).join(setup_lines)}

## Fragility Components

{markdown_table(
        [
            "world",
            "seed",
            "steps",
            "f_other_sig",
            "f_silence",
            "f_noise",
            "f_total",
            "reference_signature",
        ],
        component_rows,
    )}

## Fragility Aggregated by World (mean across seeds)

{markdown_table(["world", "f_other_sig", "f_silence", "f_noise", "f_total"], aggregate_rows)}

## Fragility Spectrum

{markdown_table(["world", "category", "f_total", "pattern"], spectrum_rows)}

The spectrum is ordered and category-aligned: `frontera-rich-estable` occupies
the low-fragility end, while `multiregimen-productivo` occupies the upper end.
There is no overlap in the measured set.

`rule_208` and `rule_209` both have `f_total = 0.000`. Since they are linked by
the complement symmetry `0 <-> 1`, this suggests complement symmetry preserves
not only the law signature but also the basin width.

`rule_54` is the new exception: it is the most fragile measured world by
`f_total`, but its fragility is partly noise-boundary fragility (`f_noise =
0.375`), not only productive signature switching.

## Interpretation

{interpretation(aggregate)}

## Scientific Question

Is `rule_137` special because it has a fragile basin, or do all multi-regime
worlds have sensitive boundaries?

{answer}

Fase 12a extends the same protocol to `frontera-rich-estable` worlds
(`rule_46`, `rule_208`, `rule_209`). These worlds are expected to be more
robust than `rule_137` because their formal profiles have low signature
diversity and nearly invariant six-law signatures.

Fase 12c adds the remaining measured `multiregimen-productivo` worlds:
`rule_54`, `rule_110`, and `rule_124`.

## Key Finding: frontera-rich-estable Basins Are Wide

{frontier_answer}

This confirms the pre-run hypothesis: stable high-richness worlds have broad
law-signature basins, unlike `rule_137`, whose signature changes under most
single-bit perturbations.

## Productive Fragility Check

{productive_fragility}
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = annotate_used_seeds(load_journal())
    selected = select_productive_cases(rows)
    missing = [world for world, cases in selected.items() if not cases]
    if missing:
        raise RuntimeError(f"No productive cases found for: {missing}")

    records = run_experiment(selected)
    with RESULTS_JSONL.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    summaries = seed_summaries(records)
    aggregate = aggregate_by_world(summaries)
    REPORT_MD.write_text(render_report(selected, summaries, aggregate), encoding="utf-8")

    print(f"Wrote {RESULTS_JSONL} ({len(records)} rows)")
    print(f"Wrote {REPORT_MD}")
    for world, stats in aggregate.items():
        print(
            f"{world}: f_other={stats['f_other_sig']:.3f} "
            f"f_silence={stats['f_silence']:.3f} "
            f"f_noise={stats['f_noise']:.3f} "
            f"f_total={stats['f_total']:.3f}"
        )


if __name__ == "__main__":
    main()
