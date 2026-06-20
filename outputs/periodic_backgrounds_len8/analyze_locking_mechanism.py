"""Fase 27: test the five-state mechanism behind the T=15 locking ratio.

Fase 26 established that every T=15 representative lives over a background
with temporal period three. This script samples the localized XOR defect once
per background period, after the transient, and asks whether the induced F^3
operator has a minimal five-state cycle.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
ANATOMY_RESULTS = OUT_DIR / "t15_anatomy_results.json"
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
RESULTS_JSONL = OUT_DIR / "locking_mechanism_results.jsonl"
REPORT_MD = OUT_DIR / "locking_mechanism_report.md"

BACKGROUND_PERIOD = 3
LOCAL_PERIOD = 15
LOCKING_RATIO = LOCAL_PERIOD // BACKGROUND_PERIOD
SAMPLE_START = 81
F3_CYCLES = 4
SAMPLE_COUNT = LOCKING_RATIO * F3_CYCLES + 1
FINAL_STEP = SAMPLE_START + BACKGROUND_PERIOD * (SAMPLE_COUNT - 1)


def load_len8_module():
    spec = importlib.util.spec_from_file_location("periodic_background_len8", LEN8_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import Fase-24 detector from {LEN8_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_representatives() -> list[dict]:
    payload = json.loads(ANATOMY_RESULTS.read_text(encoding="utf-8"))
    representatives = payload["representatives"]
    if len(representatives) != 20:
        raise RuntimeError(f"Expected 20 Fase-26 representatives, got {len(representatives)}")
    return representatives


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def perturbation_orbit(
    base,
    rule: int,
    background_frames: list[tuple[int, ...]],
    word: str,
) -> list[tuple[int, ...]]:
    diff = base.initial_diff(int(word, 2), len(word), background_frames[0])
    frames = [diff]
    for time_index in range(len(background_frames) - 1):
        diff = base.eca_step_diff(
            diff,
            background_frames[time_index],
            background_frames[time_index + 1],
            rule,
        )
        frames.append(diff)
    return frames


def canonical_defect(width: int, diff: tuple[int, ...]) -> dict:
    """Represent a localized ring state by cutting its largest empty arc."""
    if not diff:
        raise RuntimeError("Cannot canonicalize an empty defect")

    positions = sorted(diff)
    gaps = []
    for index, position in enumerate(positions):
        next_position = positions[(index + 1) % len(positions)]
        if index == len(positions) - 1:
            next_position += width
        gaps.append((next_position - position, index))

    _largest_gap, cut_index = max(gaps)
    anchor = positions[(cut_index + 1) % len(positions)]
    offsets = tuple(sorted((position - anchor) % width for position in positions))
    active_width = max(offsets) + 1
    value = sum(1 << offset for offset in offsets)
    hex_digits = max(1, (active_width + 3) // 4)
    return {
        "anchor": anchor,
        "offsets": offsets,
        "width": active_width,
        "hex": f"{active_width}:{value:0{hex_digits}x}",
    }


def signed_ring_delta(start: int, end: int, width: int) -> int:
    delta = (end - start) % width
    if delta > width // 2:
        delta -= width
    return delta


def minimal_cycle_length(states: list[str]) -> int | None:
    """Return the smallest period that explains the complete sampled sequence."""
    for period in range(1, LOCKING_RATIO + 1):
        if all(states[index] == states[index % period] for index in range(len(states))):
            return period
    return None


def analyze_representative(base, representative: dict) -> dict:
    rule = int(representative["rule"])
    background = representative["background"]
    word = representative["minimal_word"]
    bg_frames = background_orbit(base, rule, background, FINAL_STEP)
    diff_frames = perturbation_orbit(base, rule, bg_frames, word)
    sample_times = [
        SAMPLE_START + BACKGROUND_PERIOD * index
        for index in range(SAMPLE_COUNT)
    ]

    sampled_backgrounds = [bg_frames[time_index] for time_index in sample_times]
    background_phase_exact = all(
        state == sampled_backgrounds[0] for state in sampled_backgrounds
    )

    canonical = [
        canonical_defect(base.WIDTH, diff_frames[time_index])
        for time_index in sample_times
    ]
    state_sequence = [state["hex"] for state in canonical]
    raw_sequence = [diff_frames[time_index] for time_index in sample_times]
    first_cycle = state_sequence[:LOCKING_RATIO]

    states_distinct = len(set(first_cycle)) == LOCKING_RATIO
    closes_after_five = state_sequence[LOCKING_RATIO] == state_sequence[0]
    four_cycles_repeat = all(
        state_sequence[index] == first_cycle[index % LOCKING_RATIO]
        for index in range(len(state_sequence))
    )
    raw_four_cycles_repeat = all(
        raw_sequence[index] == raw_sequence[index % LOCKING_RATIO]
        for index in range(len(raw_sequence))
    )
    cycle_length = minimal_cycle_length(state_sequence)

    anchors = [state["anchor"] for state in canonical]
    per_f3_drift = [
        signed_ring_delta(anchors[index], anchors[index + 1], base.WIDTH)
        for index in range(len(anchors) - 1)
    ]
    per_local_period_drift = [
        signed_ring_delta(anchors[index], anchors[index + LOCKING_RATIO], base.WIDTH)
        for index in range(len(anchors) - LOCKING_RATIO)
    ]
    stationary = all(delta == 0 for delta in per_local_period_drift)

    transition_map: dict[str, str] = {}
    transition_consistent = True
    for source, target in zip(state_sequence, state_sequence[1:]):
        previous = transition_map.setdefault(source, target)
        if previous != target:
            transition_consistent = False

    cycle_confirmed = all(
        (
            background_phase_exact,
            states_distinct,
            closes_after_five,
            four_cycles_repeat,
            raw_four_cycles_repeat,
            cycle_length == LOCKING_RATIO,
            transition_consistent,
            stationary,
        )
    )

    collision = None
    if not states_distinct:
        seen: dict[str, int] = {}
        for index, state in enumerate(first_cycle):
            if state in seen:
                collision = [seen[state], index]
                break
            seen[state] = index

    return {
        "rule": rule,
        "background": background,
        "ic": word,
        "sample_start": SAMPLE_START,
        "sample_times": sample_times,
        "T_bg": BACKGROUND_PERIOD,
        "T_local": LOCAL_PERIOD,
        "locking_ratio": LOCKING_RATIO,
        "drift": per_local_period_drift[0] if per_local_period_drift else None,
        "per_f3_drift": per_f3_drift[:LOCKING_RATIO],
        "defect_states": first_cycle,
        "defect_width_per_state": [
            state["width"] for state in canonical[:LOCKING_RATIO]
        ],
        "states_distinct": states_distinct,
        "cycle_minimal": cycle_length == LOCKING_RATIO,
        "cycle_length_under_F3": cycle_length,
        "cycle_closes_after_five": closes_after_five,
        "four_cycles_repeat": four_cycles_repeat,
        "raw_four_cycles_repeat": raw_four_cycles_repeat,
        "background_phase_exact": background_phase_exact,
        "transition_consistent": transition_consistent,
        "stationary_over_local_period": stationary,
        "collision": collision,
        "cycle_confirmed": cycle_confirmed,
    }


def render_report(records: list[dict]) -> str:
    confirmed = sum(record["cycle_confirmed"] for record in records)
    minimal = sum(record["cycle_minimal"] for record in records)
    distinct = sum(record["states_distinct"] for record in records)
    bg_exact = sum(record["background_phase_exact"] for record in records)
    raw_repeat = sum(record["raw_four_cycles_repeat"] for record in records)
    transitions = sum(record["transition_consistent"] for record in records)
    stationary = sum(record["stationary_over_local_period"] for record in records)

    lines = [
        "# Fase 27: Five-State Locking Mechanism under F^3",
        "",
        "## Hypothesis",
        "",
        "Fase 26 found `T_local=15` over backgrounds with temporal period",
        "`T_bg=3`. Fase 27 tests whether sampling the localized XOR defect once",
        "per background period induces a minimal five-state cycle under the",
        "three-step evolution operator `F^3`.",
        "",
        "Sampling begins at `t=81`, after the established burn-in, rather than at",
        "`t=0` where IC nucleation transients could obscure the asymptotic cycle.",
        f"Each representative is sampled through `t={FINAL_STEP}`, covering",
        f"`{F3_CYCLES}` complete five-state cycles.",
        "",
        "## Summary",
        "",
        f"- Representatives: `{len(records)}`.",
        f"- Background phase exact under every `F^3` sample: `{bg_exact}/{len(records)}`.",
        f"- Five first-cycle states distinct: `{distinct}/{len(records)}`.",
        f"- Minimal cycle length under `F^3` equals 5: `{minimal}/{len(records)}`.",
        f"- Four canonical cycles repeat exactly: `{confirmed}/{len(records)}`.",
        f"- Four raw-position cycles repeat exactly: `{raw_repeat}/{len(records)}`.",
        f"- Deterministic state transitions consistent: `{transitions}/{len(records)}`.",
        f"- Stationary over every local period: `{stationary}/{len(records)}`.",
        "",
        (
            "**Verdict:** "
            + (
                "`5-cycle under F^3 confirmed universally`."
                if confirmed == len(records)
                else f"`gate failed in {len(records) - confirmed} representative(s)`."
            )
        ),
        "",
        "## Per Representative",
        "",
        "| rule | background | IC | distinct | minimal | 4 cycles | raw repeat | drift | confirmed |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for record in records:
        lines.append(
            f"| rule_{record['rule']} | `{record['background']}` | "
            f"`{record['ic']}` | {record['states_distinct']} | "
            f"{record['cycle_minimal']} | {record['four_cycles_repeat']} | "
            f"{record['raw_four_cycles_repeat']} | {record['drift']} | "
            f"{record['cycle_confirmed']} |"
        )

    failed = [record for record in records if not record["cycle_confirmed"]]
    if failed:
        lines.extend(["", "## Failures", ""])
        for record in failed:
            lines.append(
                f"- rule_{record['rule']} / `{record['background']}`: "
                f"collision={record['collision']}, "
                f"cycle_length={record['cycle_length_under_F3']}, "
                f"background_phase_exact={record['background_phase_exact']}, "
                f"transition_consistent={record['transition_consistent']}."
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "A confirmed result establishes the finite-state mechanism of the measured",
            "locking ratio: after the background returns to the same temporal phase",
            "every three ECA steps, the localized defect advances by one node in a",
            "minimal five-state cycle. Five applications of `F^3` are therefore",
            "required to return the complete background-plus-defect state, yielding",
            "`T_local = 5 * T_bg = 15`.",
            "",
            "This is a computational state-cycle derivation. It does not yet reduce",
            "the five nodes to a closed-form symbolic identity over the rule table.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    module = load_len8_module()
    base = module.load_base_module()
    records = [
        analyze_representative(base, representative)
        for representative in load_representatives()
    ]

    RESULTS_JSONL.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    REPORT_MD.write_text(render_report(records), encoding="utf-8")
    print(
        json.dumps(
            {
                "representatives": len(records),
                "cycle_confirmed": sum(record["cycle_confirmed"] for record in records),
                "results": str(RESULTS_JSONL),
                "report": str(REPORT_MD),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
