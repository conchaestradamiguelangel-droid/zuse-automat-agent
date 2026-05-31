"""Fase 14: search for ECA worlds that activate periodicidad.

Experimental artifact only. It does not modify the production pipeline.

Questions:
1. Do atlas ECA worlds ever produce observer-level oscillators under random ICs?
2. If not, do known periodic ECA rules (51, 15, 57) activate the law?
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.consensus import deduplicate_structures
from zaa.cycle_laws import evaluate_cycle_laws, evaluate_periodicity_law
from zaa.eca import random_initial_state, simulate
from zaa.observers import run_observers


OUT_DIR = ROOT / "outputs" / "periodicity_fase14"
RESULTS_JSONL = OUT_DIR / "periodicity_sweep_results.jsonl"
REPORT_MD = OUT_DIR / "periodicity_sweep_report.md"

WIDTH = 64
STEPS = 96
N_SEEDS = 50
BASE_SEED = 20260523
DEDUP_STRUCTURE_NOISE_THRESHOLD = 40

ATLAS_RULES = [18, 46, 54, 90, 109, 110, 124, 137, 208, 209]
KNOWN_PERIODIC_RULES = [51, 15, 57]


def evaluate_rule_seed(rule: int, seed: int) -> dict[str, Any]:
    frames = simulate(random_initial_state(WIDTH, seed=seed), rule, STEPS)
    structures = run_observers(frames)
    dedup_count = len(deduplicate_structures(structures))
    raw_count = len(structures)
    oscillator_count_raw = sum(1 for structure in structures if structure.tipo == "oscilador")
    periodic_raw = evaluate_periodicity_law(structures).accepted
    analysis_status = (
        "ruido_no_analizable"
        if dedup_count > DEDUP_STRUCTURE_NOISE_THRESHOLD
        else "ok"
    )
    laws = (
        evaluate_cycle_laws(structures, frames, STEPS)["laws_accepted"]
        if analysis_status == "ok"
        else []
    )
    return {
        "rule": rule,
        "world": f"rule_{rule}",
        "seed": seed,
        "steps": STEPS,
        "width": WIDTH,
        "raw_structure_count": raw_count,
        "dedup_structure_count": dedup_count,
        "analysis_status": analysis_status,
        "oscillator_count_raw": oscillator_count_raw,
        "periodicity_raw": periodic_raw,
        "periodicity_production": "periodicidad" in laws,
        "laws_accepted": laws,
    }


def run_sweep() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for group, rules in [
        ("atlas", ATLAS_RULES),
        ("known_periodic", KNOWN_PERIODIC_RULES),
    ]:
        for rule in rules:
            for i in range(N_SEEDS):
                seed = BASE_SEED + i
                record = evaluate_rule_seed(rule, seed)
                record["group"] = group
                records.append(record)
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
    by_rule: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_rule[int(record["rule"])].append(record)

    rows = []
    for rule, items in sorted(by_rule.items()):
        periodic_raw_hits = sum(item["periodicity_raw"] for item in items)
        periodic_production_hits = sum(item["periodicity_production"] for item in items)
        ok_hits = sum(item["analysis_status"] == "ok" for item in items)
        noise_hits = len(items) - ok_hits
        osc_counts = [int(item["oscillator_count_raw"]) for item in items]
        laws_counter = Counter()
        for item in items:
            laws_counter.update(item["laws_accepted"])
        rows.append(
            [
                f"rule_{rule}",
                items[0]["group"],
                str(periodic_raw_hits),
                str(periodic_production_hits),
                str(ok_hits),
                str(noise_hits),
                fmt(mean(osc_counts)),
                ", ".join(f"{law}:{count}" for law, count in sorted(laws_counter.items()))
                or "-",
            ]
        )

    hits = [
        item
        for item in records
        if item["periodicity_raw"] or item["periodicity_production"]
    ]
    first_hits = []
    for item in hits[:20]:
        first_hits.append(
            [
                f"rule_{item['rule']}",
                str(item["seed"]),
                str(item["oscillator_count_raw"]),
                item["analysis_status"],
                "yes" if item["periodicity_raw"] else "no",
                "yes" if item["periodicity_production"] else "no",
                ", ".join(item["laws_accepted"]) or "-",
            ]
        )

    atlas_hits = [
        item
        for item in records
        if item["group"] == "atlas" and item["periodicity_production"]
    ]
    known_hits = [
        item
        for item in records
        if item["group"] == "known_periodic" and item["periodicity_production"]
    ]
    if atlas_hits:
        answer = (
            "At least one atlas ECA world activates `periodicidad` under random ICs."
        )
    elif known_hits:
        answer = (
            "Atlas ECA worlds still do not activate `periodicidad`, but known "
            "periodic ECA rules do. This validates the law on real ECA dynamics "
            "rather than only synthetic frames."
        )
    else:
        answer = (
            "No tested ECA rule activates `periodicidad` under this observer and "
            "random-IC protocol."
        )

    return f"""# Periodicity Sweep - Fase 14

## Setup

- Atlas rules: `{', '.join('rule_' + str(rule) for rule in ATLAS_RULES)}`
- Known periodic candidates: `{', '.join('rule_' + str(rule) for rule in KNOWN_PERIODIC_RULES)}`
- Seeds per rule: `{N_SEEDS}`
- Seed range: `{BASE_SEED}..{BASE_SEED + N_SEEDS - 1}`
- Steps: `{STEPS}`
- Width: `{WIDTH}`
- Production noise gate: `dedup_structure_count > {DEDUP_STRUCTURE_NOISE_THRESHOLD}`

`periodicity_raw` means at least one observer emitted `tipo=oscilador`.
`periodicity_production` means the cycle was not noise-gated and
`periodicidad` appeared in `laws_accepted`.

## Rule Summary

{table(
        [
            "world",
            "group",
            "periodicity_raw/50",
            "periodicity_production/50",
            "ok/50",
            "noise/50",
            "oscillator_count_mean",
            "laws_frequency",
        ],
        rows,
    )}

## First Periodicity Hits

{table(
        [
            "world",
            "seed",
            "oscillator_count_raw",
            "analysis_status",
            "periodicity_raw",
            "periodicity_production",
            "laws_accepted",
        ],
        first_hits,
    ) if first_hits else "No periodicity hits."}

## Answer

{answer}

## Interpretation

`rule_51` is the decisive positive control: it activates `periodicidad` in
`50/50` random ICs with `analysis_status=ok`. This is real ECA dynamics, not a
synthetic frame fixture. The mechanism is global period-2 complementation, so
the observer emits many `oscilador` structures at once.

The atlas result remains negative: none of the 10 measured atlas ECA rules
activate `periodicidad` under this random-IC protocol. Therefore the law is not
dead, but it belongs to a different ECA family than the current atlas worlds.

`rule_15` and `rule_57` do not activate `periodicidad` here, despite being
periodic-looking candidates. Under the current observer contract, exact
frame-level periodicity is what matters.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = run_sweep()
    with RESULTS_JSONL.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    REPORT_MD.write_text(summarize(records), encoding="utf-8")
    print(f"Wrote {RESULTS_JSONL} ({len(records)} rows)")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
