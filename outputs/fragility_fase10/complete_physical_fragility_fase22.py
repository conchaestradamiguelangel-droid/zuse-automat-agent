"""Fase 22: complete fragility for remaining physical atlas worlds.

This artifact fills the atlas fragility gap for worlds that have a genuine
initial condition to perturb:

- ECA noise-bounded worlds: rule_30, rule_150.
- Life controls: life_blinker, life_block, life_glider.

Synthetic controls are intentionally not measured here: they are generated
frame programs rather than dynamical systems evolved from a perturbable IC.
Their atlas fragility is reported as n/a rather than inventing a physical
one-bit perturbation protocol.
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
from zaa.life2d import life_fixture, simulate_life
from zaa.observers import run_observers
from zaa.observers2d import run_observers_2d


JOURNAL = ROOT / "outputs" / "experiments_2026-05-27" / "journal_8c_long.jsonl"
OUT_DIR = ROOT / "outputs" / "fragility_fase10"
OUT_JSONL = OUT_DIR / "fragility_completion_fase22_results.jsonl"
OUT_JSON = OUT_DIR / "fragility_completion_fase22_summary.json"
OUT_MD = OUT_DIR / "fragility_completion_fase22_report.md"

BASE_SEED = 20260523
DEDUP_STRUCTURE_NOISE_THRESHOLD = 40
ECA_WIDTH = 64
LIFE_WIDTH = 32
LIFE_HEIGHT = 32
LIFE_STEPS = 24
MAX_ECA_CASES = 3

ECA_WORLDS = ("rule_30", "rule_150")
LIFE_WORLDS = ("life_blinker", "life_block", "life_glider")
SYNTHETIC_NA = ("synthetic_bloque", "synthetic_glider", "synthetic_oscilador")


def load_journal() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in JOURNAL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def annotate_used_seeds(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current_seed = BASE_SEED
    annotated: list[dict[str, Any]] = []
    for row in sorted(rows, key=lambda item: int(item["cycle_id"])):
        copy = dict(row)
        copy["reconstructed_used_seed"] = current_seed + int(row["cycle_id"])
        annotated.append(copy)
        if row.get("action_taken") == "repeat_vary_seed":
            current_seed += 1
    return annotated


def select_eca_cases(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, int]]]:
    selected: dict[str, list[dict[str, int]]] = {}
    for world in ECA_WORLDS:
        productive = [
            row
            for row in rows
            if row.get("world_type") == world and row.get("laws_accepted", [])
        ]
        by_seed: dict[int, dict[str, int]] = {}
        for row in sorted(productive, key=lambda item: (int(item["steps"]), int(item["cycle_id"]))):
            seed = int(row["reconstructed_used_seed"])
            by_seed.setdefault(seed, {"seed": seed, "steps": int(row["steps"])})
            if len(by_seed) >= MAX_ECA_CASES:
                break
        selected[world] = list(by_seed.values())
    return selected


def evaluate_frames(frames: np.ndarray, steps: int) -> dict[str, Any]:
    if frames.ndim == 2:
        structures = run_observers(frames)
    elif frames.ndim == 3:
        structures = run_observers_2d(frames)
    else:
        raise ValueError(f"unsupported frame shape: {frames.shape}")

    dedup_count = len(deduplicate_structures(structures))
    status = "ruido_no_analizable" if dedup_count > DEDUP_STRUCTURE_NOISE_THRESHOLD else "ok"
    laws = evaluate_cycle_laws(structures, frames, steps)["laws_accepted"] if status == "ok" else []
    return {
        "analysis_status": status,
        "analysis_ok": status == "ok",
        "laws_accepted": laws,
        "signature": tuple(sorted(laws)),
        "dedup_structure_count": dedup_count,
    }


def classify_outcome(reference_signature: tuple[str, ...], result: dict[str, Any]) -> str:
    if result["analysis_status"] == "ruido_no_analizable":
        return "noise"
    if not result["laws_accepted"] and result["analysis_ok"]:
        return "silence"
    if tuple(sorted(result["laws_accepted"])) == reference_signature:
        return "same_sig"
    return "other_sig"


def eca_reference_ic(seed: int) -> np.ndarray:
    return random_initial_state(ECA_WIDTH, seed=seed)


def run_eca_case(world: str, seed: int, steps: int) -> list[dict[str, Any]]:
    rule = int(world.removeprefix("rule_"))
    reference_ic = eca_reference_ic(seed)
    reference = evaluate_frames(simulate(reference_ic, rule, steps), steps)
    reference_signature = tuple(sorted(reference["laws_accepted"]))

    records: list[dict[str, Any]] = []
    for bit_position in range(ECA_WIDTH):
        perturbed_ic = reference_ic.copy()
        perturbed_ic[bit_position] = 1 - perturbed_ic[bit_position]
        perturbed = evaluate_frames(simulate(perturbed_ic, rule, steps), steps)
        records.append(
            {
                "world": world,
                "seed": seed,
                "steps": steps,
                "protocol": "eca_single_bit",
                "bit_position": bit_position,
                "position": [bit_position],
                "outcome": classify_outcome(reference_signature, perturbed),
                "reference_sig": list(reference_signature),
                "perturbed_sig": list(perturbed["signature"]),
                "reference_status": reference["analysis_status"],
                "perturbed_status": perturbed["analysis_status"],
                "reference_dedup_structure_count": reference["dedup_structure_count"],
                "perturbed_dedup_structure_count": perturbed["dedup_structure_count"],
            }
        )
    return records


def life_kind(world: str) -> str:
    return world.removeprefix("life_")


def run_life_case(world: str) -> list[dict[str, Any]]:
    kind = life_kind(world)
    reference_ic = life_fixture(kind, height=LIFE_HEIGHT, width=LIFE_WIDTH)
    reference = evaluate_frames(simulate_life(reference_ic, LIFE_STEPS), LIFE_STEPS)
    reference_signature = tuple(sorted(reference["laws_accepted"]))

    records: list[dict[str, Any]] = []
    bit_position = 0
    for y in range(LIFE_HEIGHT):
        for x in range(LIFE_WIDTH):
            perturbed_ic = reference_ic.copy()
            perturbed_ic[y, x] = 1 - perturbed_ic[y, x]
            perturbed = evaluate_frames(simulate_life(perturbed_ic, LIFE_STEPS), LIFE_STEPS)
            records.append(
                {
                    "world": world,
                    "seed": "fixture",
                    "steps": LIFE_STEPS,
                    "protocol": "life_2d_single_cell",
                    "bit_position": bit_position,
                    "position": [y, x],
                    "outcome": classify_outcome(reference_signature, perturbed),
                    "reference_sig": list(reference_signature),
                    "perturbed_sig": list(perturbed["signature"]),
                    "reference_status": reference["analysis_status"],
                    "perturbed_status": perturbed["analysis_status"],
                    "reference_dedup_structure_count": reference["dedup_structure_count"],
                    "perturbed_dedup_structure_count": perturbed["dedup_structure_count"],
                }
            )
            bit_position += 1
    return records


def summarize_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_case: dict[tuple[str, str, int], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_case[(record["world"], str(record["seed"]), int(record["steps"]))].append(record)

    cases: list[dict[str, Any]] = []
    for (world, seed, steps), items in sorted(by_case.items()):
        counts = Counter(item["outcome"] for item in items)
        n = len(items)
        cases.append(
            {
                "world": world,
                "seed": seed,
                "steps": steps,
                "n_flips": n,
                "f_other_sig": counts["other_sig"] / n,
                "f_silence": counts["silence"] / n,
                "f_noise": counts["noise"] / n,
                "f_total": (counts["other_sig"] + counts["silence"] + counts["noise"]) / n,
                "f_core": (counts["other_sig"] + counts["silence"] + counts["noise"]) / n,
                "reference_signature": items[0]["reference_sig"],
                "reference_status": items[0]["reference_status"],
                "reference_dedup_structure_count": items[0]["reference_dedup_structure_count"],
                "counts": dict(counts),
            }
        )

    by_world: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for case in cases:
        by_world[case["world"]].append(case)

    worlds: dict[str, Any] = {}
    for world, items in sorted(by_world.items()):
        worlds[world] = {
            "world": world,
            "n_cases": len(items),
            "n_flips": sum(item["n_flips"] for item in items),
            "f_other_sig": mean(item["f_other_sig"] for item in items),
            "f_silence": mean(item["f_silence"] for item in items),
            "f_noise": mean(item["f_noise"] for item in items),
            "f_total": mean(item["f_total"] for item in items),
            "f_core": mean(item["f_core"] for item in items),
            "reference_signatures": sorted(
                {" + ".join(item["reference_signature"]) if item["reference_signature"] else "EMPTY" for item in items}
            ),
        }

    for world in SYNTHETIC_NA:
        worlds[world] = {
            "world": world,
            "n_cases": 0,
            "n_flips": 0,
            "f_other_sig": None,
            "f_silence": None,
            "f_noise": None,
            "f_total": None,
            "f_core": None,
            "reference_signatures": [],
            "note": "n/a: synthetic frame generator, no physical IC perturbation protocol",
        }

    return {"cases": cases, "worlds": worlds}


def fmt(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.3f}"


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(summary: dict[str, Any]) -> str:
    case_rows = [
        [
            case["world"],
            str(case["seed"]),
            str(case["steps"]),
            str(case["n_flips"]),
            fmt(case["f_other_sig"]),
            fmt(case["f_silence"]),
            fmt(case["f_noise"]),
            fmt(case["f_total"]),
            " + ".join(case["reference_signature"]) if case["reference_signature"] else "EMPTY",
        ]
        for case in summary["cases"]
    ]
    world_rows = [
        [
            world,
            str(stats["n_cases"]),
            str(stats["n_flips"]),
            fmt(stats["f_total"]),
            fmt(stats["f_core"]),
            fmt(stats["f_noise"]),
            "; ".join(stats["reference_signatures"]) if stats["reference_signatures"] else "n/a",
        ]
        for world, stats in sorted(summary["worlds"].items())
    ]
    return f"""# Fragility Completion - Fase 22

## Scope

This run completes one-bit fragility for remaining atlas worlds with a genuine
perturbable initial condition:

- ECA: `rule_30`, `rule_150`.
- 2D Life controls: `life_blinker`, `life_block`, `life_glider`.

The three synthetic controls are marked `n/a`: they are frame generators, not
dynamical systems evolved from an IC. Assigning them `f_total` would invent a
perturbation protocol outside the atlas physics.

For these remaining controls, `f_core` is set equal to `f_total`: there is no
separate category-defining core law beyond the measured reference signature.

## Per-Case Results

{table(["world", "seed", "steps", "n_flips", "f_other_sig", "f_silence", "f_noise", "f_total", "reference_signature"], case_rows)}

## Aggregated by World

{table(["world", "n_cases", "n_flips", "f_total", "f_core", "f_noise", "reference_signatures"], world_rows)}

## Interpretation

`rule_30` and `rule_150` are noise-bounded worlds in the long journal, so this
diagnostic measures their productive pockets rather than their noisy visits.
Both are therefore reported as conditional fragility at the selected productive
steps/seeds.

Life controls are physical 2D CA worlds with a well-defined one-cell
perturbation protocol over the full 32x32 initial grid. Their fragility values
are directly comparable as fixture-level robustness scores, but not as ECA
one-dimensional bit-position spectra.

Synthetic controls remain outside basin-fragility measurement by design.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = annotate_used_seeds(load_journal())
    selected = select_eca_cases(rows)

    records: list[dict[str, Any]] = []
    for world, cases in selected.items():
        if not cases:
            raise RuntimeError(f"No productive cases found for {world}")
        for case in cases:
            records.extend(run_eca_case(world, case["seed"], case["steps"]))
    for world in LIFE_WORLDS:
        records.extend(run_life_case(world))

    OUT_JSONL.write_text(
        "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
        encoding="utf-8",
    )
    summary = summarize_records(records)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(render_report(summary), encoding="utf-8")
    print(f"Wrote {OUT_JSONL}")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    for world, stats in sorted(summary["worlds"].items()):
        print(
            f"{world:22s} n={stats['n_flips']:4d} "
            f"f_total={fmt(stats['f_total'])} f_noise={fmt(stats['f_noise'])}"
        )


if __name__ == "__main__":
    main()
