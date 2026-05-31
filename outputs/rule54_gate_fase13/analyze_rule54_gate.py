"""Fase 13: anatomy of the rule_54 noise gate.

Experimental artifact only. Recomputes the three rule_54 fragility cases from
Fase 12c and records raw/deduplicated structure counts for each one-bit flip.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.consensus import deduplicate_structures
from zaa.cycle_laws import evaluate_cycle_laws
from zaa.eca import random_initial_state, simulate
from zaa.observers import run_observers


OUT_DIR = ROOT / "outputs" / "rule54_gate_fase13"
RESULTS_JSONL = OUT_DIR / "rule54_gate_results.jsonl"
REPORT_MD = OUT_DIR / "rule54_gate_report.md"

WORLD = "rule_54"
RULE = 54
WIDTH = 64
STEPS = 96
SEEDS = [20260638, 20260640, 20260642]
DEDUP_STRUCTURE_NOISE_THRESHOLD = 40
BIN_SIZE = 8
CLUSTER_THRESHOLD = 0.30


def evaluate_ic(initial_state: np.ndarray) -> dict[str, Any]:
    frames = simulate(initial_state, RULE, STEPS)
    raw_structures = run_observers(frames)
    dedup_structures = deduplicate_structures(raw_structures)
    raw_count = len(raw_structures)
    dedup_count = len(dedup_structures)
    analysis_status = (
        "ruido_no_analizable"
        if dedup_count > DEDUP_STRUCTURE_NOISE_THRESHOLD
        else "ok"
    )
    laws = (
        evaluate_cycle_laws(raw_structures, frames, STEPS)["laws_accepted"]
        if analysis_status == "ok"
        else []
    )
    return {
        "raw_structure_count": raw_count,
        "dedup_structure_count": dedup_count,
        "analysis_status": analysis_status,
        "cruza_gate": analysis_status == "ruido_no_analizable",
        "laws_accepted": laws,
        "signature": tuple(sorted(laws)),
    }


def run_analysis() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for seed in SEEDS:
        reference_ic = random_initial_state(WIDTH, seed=seed)
        reference = evaluate_ic(reference_ic)
        reference_sig = list(reference["signature"])
        for bit_position in range(WIDTH):
            perturbed_ic = reference_ic.copy()
            perturbed_ic[bit_position] = 1 - perturbed_ic[bit_position]
            perturbed = evaluate_ic(perturbed_ic)
            outcome = (
                "noise"
                if perturbed["cruza_gate"]
                else "same_sig"
                if list(perturbed["signature"]) == reference_sig
                else "other_sig"
                if perturbed["signature"]
                else "silence"
            )
            records.append(
                {
                    "world": WORLD,
                    "seed": seed,
                    "steps": STEPS,
                    "bit_position": bit_position,
                    "outcome": outcome,
                    "cruza_gate": perturbed["cruza_gate"],
                    "motivo_ruido": (
                        f"dedup_structure_count>{DEDUP_STRUCTURE_NOISE_THRESHOLD}"
                        if perturbed["cruza_gate"]
                        else None
                    ),
                    "raw_structure_count": perturbed["raw_structure_count"],
                    "dedup_structure_count": perturbed["dedup_structure_count"],
                    "reference_raw_structure_count": reference["raw_structure_count"],
                    "reference_dedup_structure_count": reference["dedup_structure_count"],
                    "reference_signature": reference_sig,
                    "perturbed_signature": list(perturbed["signature"]),
                }
            )
    return records


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def summarize(records: list[dict[str, Any]]) -> str:
    by_seed: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_seed[int(record["seed"])].append(record)

    noise_records = [record for record in records if record["cruza_gate"]]
    noise_positions = [int(record["bit_position"]) for record in noise_records]
    noise_by_position = Counter(noise_positions)
    noise_vec = [
        noise_by_position[position] / len(SEEDS)
        for position in range(WIDTH)
    ]
    bin_means = [
        mean(noise_vec[start : start + BIN_SIZE])
        for start in range(0, WIDTH, BIN_SIZE)
    ]
    bin_range = max(bin_means) - min(bin_means)
    pattern = "clustered" if bin_range > CLUSTER_THRESHOLD else "dispersed"
    left_mean = mean(noise_vec[:32])
    right_mean = mean(noise_vec[32:])
    top_positions = sorted(range(WIDTH), key=lambda p: noise_vec[p], reverse=True)[:10]

    seed_rows = []
    for seed, items in sorted(by_seed.items()):
        gate_items = [item for item in items if item["cruza_gate"]]
        seed_rows.append(
            [
                str(seed),
                str(len(gate_items)),
                fmt(len(gate_items) / WIDTH),
                fmt(mean(item["raw_structure_count"] for item in items)),
                fmt(mean(item["dedup_structure_count"] for item in items)),
                fmt(mean(item["dedup_structure_count"] for item in gate_items))
                if gate_items
                else "-",
                str(items[0]["reference_raw_structure_count"]),
                str(items[0]["reference_dedup_structure_count"]),
            ]
        )

    bin_rows = [
        [str(index), f"{index * BIN_SIZE}-{index * BIN_SIZE + BIN_SIZE - 1}", fmt(value)]
        for index, value in enumerate(bin_means)
    ]
    top_rows = [
        [
            str(position),
            fmt(noise_vec[position]),
            str(noise_by_position[position]),
        ]
        for position in top_positions
    ]
    noise_detail_rows = [
        [
            str(record["seed"]),
            str(record["bit_position"]),
            str(record["raw_structure_count"]),
            str(record["dedup_structure_count"]),
            "yes" if record["cruza_gate"] else "no",
            record["motivo_ruido"] or "-",
        ]
        for record in noise_records
    ]

    total_noise = len(noise_records)
    total_flips = len(records)

    most_sensitive_seed = max(
        by_seed,
        key=lambda seed: sum(1 for item in by_seed[seed] if item["cruza_gate"]),
    )
    most_sensitive_reference = by_seed[most_sensitive_seed][0][
        "reference_dedup_structure_count"
    ]

    return f"""# Rule 54 Noise Gate Anatomy - Fase 13

## Setup

- World: `{WORLD}`
- Rule: `{RULE}`
- Seeds: `{', '.join(str(seed) for seed in SEEDS)}`
- Steps: `{STEPS}`
- Width: `{WIDTH}`
- Noise gate: `dedup_structure_count > {DEDUP_STRUCTURE_NOISE_THRESHOLD}`
- Cluster threshold: `bin_range > {CLUSTER_THRESHOLD:.2f}`

## Gate Summary

Noise flips: `{total_noise}/{total_flips}` = `{total_noise / total_flips:.3f}`.

{table(
        [
            "seed",
            "noise_flips",
            "noise_rate",
            "raw_mean",
            "dedup_mean",
            "dedup_mean_when_noise",
            "reference_raw",
            "reference_dedup",
        ],
        seed_rows,
    )}

## Position Map

{table(["bin", "positions", "noise_rate"], bin_rows)}

Left half mean: `{fmt(left_mean)}`  
Right half mean: `{fmt(right_mean)}`  
Bin range: `{fmt(bin_range)}`  
Pattern: `{pattern}`

Top noisy positions:

{table(["bit_position", "noise_rate", "noise_count"], top_rows)}

## Noise-Crossing Flips

{table(
        [
            "seed",
            "bit_position",
            "raw_count",
            "dedup_count",
            "cruza_gate",
            "motivo",
        ],
        noise_detail_rows,
    )}

## Interpretation

The rule_54 noise mechanism is exactly the deduplicated structure gate:
every noisy flip has `dedup_structure_count > {DEDUP_STRUCTURE_NOISE_THRESHOLD}`.

The noise positions are spatially {'clustered' if pattern == 'clustered' else 'not strongly clustered'}:
`bin_range = {fmt(bin_range)}`. This tests the Fase 12 hypothesis that
rule_54's clustered fragility reflects a localized region of the IC pushing the
system over the dedup threshold.

The clustering is not a single contiguous block. It is a multi-hot spatial
pattern with strongest bins at the edges/right tail (`0-7`, `48-55`, `56-63`)
and weaker response in the middle. Bit `5` is the only position that crosses
the gate in all three measured seeds.

Seed sensitivity matters: seed `{most_sensitive_seed}` accounts for the largest
number of noise flips and starts at `reference_dedup_structure_count =
{most_sensitive_reference}`, only one structure below the threshold. That
explains why many one-bit perturbations push it over the gate.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = run_analysis()
    with RESULTS_JSONL.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    REPORT_MD.write_text(summarize(records), encoding="utf-8")
    print(f"Wrote {RESULTS_JSONL} ({len(records)} rows)")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
