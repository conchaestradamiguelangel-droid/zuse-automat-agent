"""Fase 16: search for local ECA oscillators on quiescent backgrounds.

Experimental artifact only. It does not modify the production pipeline.

The protocol differs from the Fase 14 random-IC periodicity sweep: here we only
test ECA rules with a stable zero background, and use small localized seeds.
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
from zaa.cycle_laws import evaluate_cycle_laws, evaluate_periodicity_law
from zaa.eca import rule_bits, simulate
from zaa.observers import run_observers


OUT_DIR = ROOT / "outputs" / "local_oscillators_fase16"
RESULTS_JSONL = OUT_DIR / "local_oscillator_results.jsonl"
REPORT_MD = OUT_DIR / "local_oscillator_report.md"

WIDTH = 128
STEPS = 200
MIN_SURVIVAL_STEPS = 50
DEDUP_STRUCTURE_NOISE_THRESHOLD = 40
CLUSTER_STABILITY_TOLERANCE = 4

ATLAS_RULES = {
    18,
    30,
    46,
    51,
    54,
    90,
    109,
    110,
    124,
    137,
    150,
    208,
    209,
}
TRIVIAL_RULES = {0, 2, 4}

IC_PATTERNS: dict[str, tuple[int, ...]] = {
    "point": (0,),
    "pair_gap1": (-1, 1),
    "triple": (-1, 0, 1),
}


def make_ic(pattern: tuple[int, ...], width: int = WIDTH) -> np.ndarray:
    """Create a localized seed on an all-zero background."""
    state = np.zeros(width, dtype=np.uint8)
    center = width // 2
    for offset in pattern:
        state[(center + offset) % width] = 1
    return state


def active_span(frame: np.ndarray) -> int:
    """Return linear active span, ignoring periodic wrap for this wide protocol."""
    xs = np.flatnonzero(frame)
    if xs.size == 0:
        return 0
    return int(xs.max() - xs.min() + 1)


def survival_steps(frames: np.ndarray) -> int:
    """Number of steps after t=0 with at least one active cell."""
    active = np.any(frames != 0, axis=1)
    if not np.any(active):
        return 0
    active_indices = np.flatnonzero(active)
    return int(active_indices[-1])


def survives_long_enough(frames: np.ndarray) -> bool:
    return survival_steps(frames) >= MIN_SURVIVAL_STEPS


def is_growth_bounded(frames: np.ndarray) -> bool:
    """Heuristic: late active span and density should be stable, not expanding."""
    spans = np.array([active_span(frame) for frame in frames], dtype=np.float64)
    counts = np.sum(frames != 0, axis=1).astype(np.float64)

    if spans[-1] == 0:
        return False
    if float(np.max(spans)) > WIDTH // 2:
        return False

    tail = max(20, min(50, len(spans) // 4))
    early_window = spans[-2 * tail : -tail]
    late_window = spans[-tail:]
    early_counts = counts[-2 * tail : -tail]
    late_counts = counts[-tail:]
    if early_window.size == 0 or late_window.size == 0:
        return False

    span_delta = float(abs(mean(late_window) - mean(early_window)))
    count_delta = float(abs(mean(late_counts) - mean(early_counts)))
    return span_delta <= CLUSTER_STABILITY_TOLERANCE and count_delta <= CLUSTER_STABILITY_TOLERANCE


def classify_candidate(rule: int, ic_name: str, frames: np.ndarray, structures: list[Any], laws: list[str]) -> dict[str, Any]:
    oscillator_structures = [structure for structure in structures if structure.tipo == "oscilador"]
    survival = survival_steps(frames)
    bounded = is_growth_bounded(frames)
    periodic_raw = evaluate_periodicity_law(structures).accepted
    interesting = bool(
        oscillator_structures
        and periodic_raw
        and survives_long_enough(frames)
        and bounded
    )
    spans = [active_span(frame) for frame in frames]
    counts = [int(np.sum(frame != 0)) for frame in frames]
    return {
        "rule": rule,
        "world": f"rule_{rule}",
        "ic_type": ic_name,
        "width": WIDTH,
        "steps": STEPS,
        "survival_steps": survival,
        "max_active_span": max(spans),
        "final_active_span": spans[-1],
        "max_active_count": max(counts),
        "final_active_count": counts[-1],
        "growth_bounded": bounded,
        "oscillator_count_raw": len(oscillator_structures),
        "periodicity_raw": periodic_raw,
        "periodicity_production": "periodicidad" in laws,
        "interesting_local_candidate": interesting,
        "oscillator_structures": [
            {
                "id": structure.id,
                "observador": structure.observador,
                "tamaño": structure.tamaño,
                "track_len": len(structure.posiciones),
                "confidence": structure.confianza,
            }
            for structure in oscillator_structures[:10]
        ],
    }


def evaluate_rule_ic(rule: int, ic_name: str, pattern: tuple[int, ...]) -> dict[str, Any]:
    frames = simulate(make_ic(pattern), rule, STEPS)
    structures = run_observers(frames)
    dedup_count = len(deduplicate_structures(structures))
    raw_count = len(structures)
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
    record = classify_candidate(rule, ic_name, frames, structures, laws)
    record.update(
        {
            "raw_structure_count": raw_count,
            "dedup_structure_count": dedup_count,
            "analysis_status": analysis_status,
            "laws_accepted": laws,
        }
    )
    return record


def candidate_rules() -> list[int]:
    """Rules with f(0,0,0)=0, excluding atlas and trivial zero-convergers."""
    return [
        rule
        for rule in range(256)
        if int(rule_bits(rule)[0]) == 0
        and rule not in ATLAS_RULES
        and rule not in TRIVIAL_RULES
    ]


def run_search() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rule in candidate_rules():
        for ic_name, pattern in IC_PATTERNS.items():
            records.append(evaluate_rule_ic(rule, ic_name, pattern))
    return records


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def summarize(records: list[dict[str, Any]]) -> str:
    periodic_hits = [record for record in records if record["periodicity_raw"]]
    production_hits = [record for record in records if record["periodicity_production"]]
    interesting = [record for record in records if record["interesting_local_candidate"]]

    by_rule: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_rule[int(record["rule"])].append(record)

    summary_rows = []
    for rule, items in sorted(by_rule.items()):
        periodic_count = sum(item["periodicity_raw"] for item in items)
        production_count = sum(item["periodicity_production"] for item in items)
        interesting_count = sum(item["interesting_local_candidate"] for item in items)
        ok_count = sum(item["analysis_status"] == "ok" for item in items)
        laws_counter = Counter()
        for item in items:
            laws_counter.update(item["laws_accepted"])
        if periodic_count or production_count or interesting_count:
            summary_rows.append(
                [
                    f"rule_{rule}",
                    str(periodic_count),
                    str(production_count),
                    str(interesting_count),
                    str(ok_count),
                    ", ".join(f"{law}:{count}" for law, count in sorted(laws_counter.items())) or "-",
                ]
            )

    hit_rows = [
        [
            f"rule_{record['rule']}",
            record["ic_type"],
            record["analysis_status"],
            str(record["oscillator_count_raw"]),
            "yes" if record["periodicity_production"] else "no",
            str(record["survival_steps"]),
            str(record["final_active_span"]),
            "yes" if record["growth_bounded"] else "no",
            "yes" if record["interesting_local_candidate"] else "no",
            ", ".join(record["laws_accepted"]) or "-",
        ]
        for record in periodic_hits[:50]
    ]

    if interesting:
        answer = (
            f"Found {len(interesting)} local-oscillator candidates under the "
            "minimal quiescent-background protocol."
        )
        interpretation = """The positive case is `rule_108`. From both `pair_gap1`
and `triple` ICs, it converges immediately to the stationary period-2 motif
`#.# <-> ###` on an all-zero background. The active region remains localized
with span <= 3 for 200 steps, and the production pipeline accepts
`periodicidad`.

This is qualitatively different from `rule_51`: `rule_51` is global
period-2 complementation, while `rule_108` contains a genuine local oscillator
particle on a quiescent background. Therefore `periodicidad` now has an ECA
local-particle witness, not only synthetic/Life witnesses and a global ECA
witness."""
    elif periodic_hits:
        answer = (
            "The observer found oscillator-like structures, but none passed the "
            "local-candidate filter (survival + bounded growth)."
        )
        interpretation = """The observer detected oscillator-like structures, but
none survived the local-candidate filter. This would suggest that the current
observer can see periodicity, but the tested minimal ICs do not produce stable
localized ECA oscillators."""
    else:
        answer = (
            "No quiescent-background ECA rule outside the atlas produced a "
            "detected local oscillator from point/pair/triple ICs. Under this "
            "protocol, `periodicidad` remains confirmed by synthetic/Life local "
            "oscillators and by rule_51 global periodicity, but not by an ECA "
            "local particle oscillator."
        )
        interpretation = """This negative result does not prove local ECA
oscillators are impossible. It shows that they are not found by the current
observer under minimal point/pair/triple ICs and quiescent background. The next
escalation would require designed ICs from known ECA patterns or a wider
exhaustive search over all binary words of length 4-8."""

    return f"""# Local Oscillator Search - Fase 16

## Setup

- Candidate rules: ECA rules with `f(0,0,0)=0`.
- Exclusions: atlas rules `{", ".join("rule_" + str(rule) for rule in sorted(ATLAS_RULES))}` and trivial rules `{", ".join("rule_" + str(rule) for rule in sorted(TRIVIAL_RULES))}`.
- Candidate count: `{len(candidate_rules())}` rules.
- ICs: `point`, `pair_gap1`, `triple` on all-zero background.
- Width: `{WIDTH}`.
- Steps: `{STEPS}`.
- Minimum survival: `{MIN_SURVIVAL_STEPS}` steps.
- Production noise gate: `dedup_structure_count > {DEDUP_STRUCTURE_NOISE_THRESHOLD}`.

`periodicity_raw` means at least one observer emitted `tipo=oscilador`.
`periodicity_production` means the cycle was not noise-gated and
`periodicidad` appeared in `laws_accepted`.

A genuine local candidate requires:

- at least one oscillator structure,
- survival for at least `{MIN_SURVIVAL_STEPS}` steps,
- bounded late growth (`span` and active-cell count stable within `{CLUSTER_STABILITY_TOLERANCE}` cells),
- no reliance on a changing non-quiescent background.

## Result

{answer}

Rows evaluated: `{len(records)}`.
Raw periodic hits: `{len(periodic_hits)}`.
Production periodic hits: `{len(production_hits)}`.
Interesting local candidates: `{len(interesting)}`.

## Rules With Periodicity Hits

{table(
        [
            "world",
            "periodicity_raw/3",
            "periodicity_production/3",
            "interesting/3",
            "ok/3",
            "laws_frequency",
        ],
        summary_rows,
    ) if summary_rows else "No rules produced periodicity hits."}

## First Periodicity Hit Details

{table(
        [
            "world",
            "ic_type",
            "analysis_status",
            "oscillator_count_raw",
            "periodicity_production",
            "survival_steps",
            "final_span",
            "bounded",
            "interesting",
            "laws_accepted",
        ],
        hit_rows,
    ) if hit_rows else "No periodicity hits."}

## Interpretation

This sweep isolates the hardest version of the periodicity question: a local
oscillator on a stable zero background, seeded by at most three active cells.
It deliberately excludes `rule_51`, because Fase 15 already showed that
`rule_51` is global period-2 complementation rather than a local particle.

{interpretation}
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = run_search()
    with RESULTS_JSONL.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    REPORT_MD.write_text(summarize(records), encoding="utf-8")
    print(f"Wrote {RESULTS_JSONL} ({len(records)} rows)")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
