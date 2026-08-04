#!/usr/bin/env python3
"""Fase 88: long-horizon dynamics of the two reachable minimal selectors."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
SWEEP_SCRIPT = OUT_DIR / "sweep_periodic_background_oscillators.py"
FASE83_RESULTS = OUT_DIR / "rule73_h11_exact_causal_equivalence_results.json"
FASE85_RESULTS = OUT_DIR / "rule73_h11_input_selector_results.json"
FASE86_RESULTS = OUT_DIR / "rule73_h11_physical_selector_realizability_results.json"
FASE87_SCRIPT = OUT_DIR / "analyze_rule73_h11_selector_reachability.py"
FASE87_RESULTS = OUT_DIR / "rule73_h11_selector_reachability_results.json"
RESULTS_JSON = OUT_DIR / "rule73_h11_selector_branches_results.json"
REPORT_MD = OUT_DIR / "rule73_h11_selector_branches_report.md"

RULE = 73
BURN_IN = 80
SOURCE_STEPS = 300
LONG_STEPS = 1000
TAIL_START = 500
MAX_PERIOD = 120
MAX_SPAN = 32
HORIZON = 11
T6_SELECTOR = 0x0311630
RESCUE_SELECTOR = 0x035AAB0
T6_REFERENCE = ("01101111", 8, "00110101")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def assignment_hex(value: int) -> str:
    return f"0x{value:07x}"


def canonical_cycle(shapes: list[Any], period: int) -> tuple[tuple[int, ...], ...]:
    sequence = tuple(tuple(int(offset) for offset in shape.offsets) for shape in shapes[-period:])
    rotations = [sequence[index:] + sequence[:index] for index in range(period)]
    return min(rotations)


def simulate_long(base, background: str, word: str) -> dict[str, Any]:
    bg_frames = [base.background_state(background)]
    for _ in range(LONG_STEPS):
        bg_frames.append(base.eca_step_state(bg_frames[-1], RULE))
    diff = base.initial_diff(int(word, 2), len(word), bg_frames[0])
    shapes = []
    extinction_time = None
    span_escape_time = None
    for time in range(LONG_STEPS + 1):
        if time >= BURN_IN:
            shape = base.linear_shape(diff)
            if shape is None:
                extinction_time = time
                break
            if int(shape.span) > MAX_SPAN:
                span_escape_time = time
                break
            shapes.append(shape)
        if time < LONG_STEPS:
            diff = base.eca_step_diff(
                diff,
                bg_frames[time],
                bg_frames[time + 1],
                RULE,
            )
    return {
        "background_frames": bg_frames,
        "background_sets": [set(frame) for frame in bg_frames],
        "shapes": shapes,
        "diff_sets": [
            {int(shape.min_pos) + int(offset) for offset in shape.offsets}
            for shape in shapes
        ],
        "extinction_time": extinction_time,
        "span_escape_time": span_escape_time,
        "persistent_bounded": (
            extinction_time is None
            and span_escape_time is None
            and len(shapes) == LONG_STEPS - BURN_IN + 1
        ),
    }


def detect_tail_dynamics(shapes: list[Any]) -> dict[str, Any]:
    tail_index = TAIL_START - BURN_IN
    if len(shapes) <= tail_index + MAX_PERIOD:
        return {"kind": "INSUFFICIENT_TAIL", "period": None, "drift": None}
    tail = shapes[tail_index:]
    for period in range(1, MAX_PERIOD + 1):
        if all(
            tail[index].offsets == tail[index + period].offsets
            and int(tail[index].min_pos) == int(tail[index + period].min_pos)
            for index in range(len(tail) - period)
        ):
            return {"kind": "STATIONARY", "period": period, "drift": 0}
    for period in range(1, MAX_PERIOD + 1):
        drift = None
        valid = True
        for index in range(len(tail) - period):
            left = tail[index]
            right = tail[index + period]
            if left.offsets != right.offsets:
                valid = False
                break
            observed = int(right.min_pos) - int(left.min_pos)
            if observed == 0:
                valid = False
                break
            if drift is None:
                drift = observed
            elif observed != drift:
                valid = False
                break
        if valid and drift is not None:
            return {"kind": "MOVING", "period": period, "drift": drift}
    return {"kind": "APERIODIC_BOUNDED", "period": None, "drift": None}


def long_public_row(
    base,
    phase87,
    background: str,
    word_len: int,
    word: str,
    target_assignment: int,
    reference_boundary: list[dict[str, int]],
    reference_final_background: list[int],
) -> tuple[dict[str, Any], dict[str, Any]]:
    simulated = simulate_long(base, background, word)
    dynamics = detect_tail_dynamics(simulated["shapes"])
    target_occurrences = []
    operator_occurrences = []
    if simulated["persistent_bounded"]:
        for time in range(BURN_IN, LONG_STEPS - HORIZON + 1):
            index = time - BURN_IN
            diff = simulated["diff_sets"][index]
            positions = phase87.choose_positions(diff)
            assignment = phase87.assignment_at(
                simulated["background_sets"][time], diff, positions
            )
            if assignment != target_assignment:
                continue
            target_occurrences.append(time)
            if phase87.operator_matches(
                simulated["background_sets"],
                simulated["diff_sets"],
                time,
                positions,
                reference_boundary,
                reference_final_background,
            ):
                operator_occurrences.append(time)
    cycle_hash = None
    if dynamics["kind"] in {"STATIONARY", "MOVING"}:
        cycle_hash = sha256_json(
            canonical_cycle(simulated["shapes"], int(dynamics["period"]))
        )
    row = {
        "background": background,
        "word_len": word_len,
        "word": word,
        "persistent_bounded": simulated["persistent_bounded"],
        "extinction_time": simulated["extinction_time"],
        "span_escape_time": simulated["span_escape_time"],
        "tail_kind": dynamics["kind"],
        "tail_period": dynamics["period"],
        "tail_drift": dynamics["drift"],
        "max_span": (
            max(int(shape.span) + 1 for shape in simulated["shapes"])
            if simulated["shapes"]
            else 0
        ),
        "target_occurrence_count": len(target_occurrences),
        "operator_target_occurrence_count": len(operator_occurrences),
        "first_target_time": target_occurrences[0] if target_occurrences else None,
        "target_time_differences": sorted(
            {
                right - left
                for left, right in zip(target_occurrences, target_occurrences[1:])
            }
        ),
        "cycle_sha256": cycle_hash,
    }
    return row, simulated


def reference_t6_phases(
    phase87,
    fase85_rows: dict[int, dict[str, Any]],
    differing_bits: list[int],
    simulated: dict[str, Any],
    reference_boundary: list[dict[str, int]],
    reference_final_background: list[int],
) -> list[dict[str, Any]]:
    rows = []
    for phase in range(6):
        time = BURN_IN + phase
        diff = simulated["diff_sets"][phase]
        positions = phase87.choose_positions(diff)
        assignment = phase87.assignment_at(
            simulated["background_sets"][time], diff, positions
        )
        mask = phase87.subcube_mask(assignment, differing_bits)
        same_operator = phase87.operator_matches(
            simulated["background_sets"],
            simulated["diff_sets"],
            time,
            positions,
            reference_boundary,
            reference_final_background,
        )
        fase85_row = fase85_rows.get(assignment)
        shape = simulated["shapes"][phase]
        rows.append(
            {
                "phase": phase,
                "time": time,
                "assignment": assignment,
                "assignment_hex": assignment_hex(assignment),
                "subcube_mask": mask,
                "in_fase85_subcube": mask is not None,
                "same_reference_operator": same_operator,
                "is_bit12_selector": assignment == T6_SELECTOR,
                "fase85_comparable": (
                    bool(fase85_row["comparable_to_t15"])
                    if fase85_row is not None
                    else None
                ),
                "defect_size": len(shape.offsets),
                "defect_span": int(shape.span) + 1,
                "defect_offsets": [int(value) for value in shape.offsets],
            }
        )
    return rows


def classify(t6: dict[str, Any], rescue: dict[str, Any]) -> tuple[str, str]:
    t6_confirmed = (
        t6["reference_long_run"]["tail_kind"] == "STATIONARY"
        and t6["reference_long_run"]["tail_period"] == 6
    )
    rescue_counts = rescue["tail_class_counts"]
    rescue_total = rescue["ic_count"]
    all_t30 = rescue_counts.get("STATIONARY_T30", 0) == rescue_total
    if t6_confirmed and all_t30:
        return (
            "REACHABLE_SELECTORS_ROUTE_TO_T6_AND_T30_ATTRACTORS",
            "The bit-12 selector belongs to a persistent T=6 attractor, while every physical [9,12] rescue preimage belongs to a persistent T=30 attractor outside the original period-search range.",
        )
    if t6_confirmed:
        return (
            "T6_BRANCH_CONFIRMED_RESCUE_DYNAMICS_MIXED",
            "The bit-12 T=6 branch is persistent, but the [9,12] rescue preimages split across more than one long-horizon dynamical class.",
        )
    return (
        "SELECTOR_BRANCHES_INSUFFICIENT",
        "The long-horizon audit does not confirm the predeclared T=6 branch and a common rescue attractor.",
    )


def write_report(data: dict[str, Any]) -> None:
    t6 = data["t6_branch"]
    rescue = data["rescue_branch"]
    lines = [
        "# Fase 88: Long-Horizon Branches of the Reachable h=11 Selectors",
        "",
        "## Question",
        "",
        "What dynamical attractors receive the two minimal selectors that Fase 87",
        "found physically reachable but absent from the stationary T=12 basin?",
        "",
        "## Predeclared Protocol",
        "",
        "- Source cohort: the same 2,008 rule_73 runs from Fases 86-87.",
        "- Long horizon: 1,000 steps; burn-in 80; bounded span <=32.",
        "- Tail recurrence: exact equality over t=500..1000, periods 1..120.",
        "- Stationary recurrence requires equal offsets and absolute position.",
        "- Moving recurrence requires equal offsets and constant non-zero drift.",
        "- The original detector searched only periods 2..16; longer exact periods",
        "  are reported as new diagnostics, not silently relabeled source hits.",
        "- No threshold, paper, DOI, tag, or release is changed.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        "## Branch A: bit-12 selector",
        "",
        f"- Selector: `{assignment_hex(T6_SELECTOR)}`.",
        f"- Reference IC: `{t6['reference_case']['background']}/{t6['reference_case']['word']}`.",
        f"- Long-tail class: `{t6['reference_long_run']['tail_kind']}`.",
        f"- Exact tail period: `{t6['reference_long_run']['tail_period']}`.",
        f"- Target occurrences through t=989: `{t6['reference_long_run']['operator_target_occurrence_count']}`.",
        f"- Source ICs in the same translation-normalized T=6 shape attractor: `{t6['source_basin_ic_count']}`.",
        f"- Backgrounds represented in that basin: `{t6['source_basin_backgrounds']}`.",
        "",
        "### Six-phase cycle at t=80..85",
        "",
        "| phase | assignment | in subcube | reference operator | bit12 selector | Fase85 comparable | defect size | span |",
        "| ---: | --- | --- | --- | --- | --- | ---: | ---: |",
    ]
    for row in t6["cycle_phases"]:
        lines.append(
            f"| {row['phase']} | `{row['assignment_hex']}` | "
            f"{str(row['in_fase85_subcube']).lower()} | "
            f"{str(row['same_reference_operator']).lower()} | "
            f"{str(row['is_bit12_selector']).lower()} | "
            f"{str(row['fase85_comparable']).lower() if row['fase85_comparable'] is not None else 'n/a'} | "
            f"{row['defect_size']} | {row['defect_span']} |"
        )
    lines.extend(
        [
            "",
            "## Branch B: [9,12] rescue",
            "",
            f"- Selector: `{assignment_hex(RESCUE_SELECTOR)}`.",
            f"- Physical ICs audited: `{rescue['ic_count']}`.",
            f"- Long-horizon persistent bounded ICs: `{rescue['persistent_bounded_count']}`.",
            f"- Tail classes: `{rescue['tail_class_counts']}`.",
            f"- Unique translation-normalized cycle hashes: `{rescue['unique_cycle_count']}`.",
            f"- Total exact selector occurrences through t=989: `{rescue['total_operator_target_occurrences']}`.",
            "",
            "| background | IC | tail class | period | drift | max span | selector occurrences | first occurrence |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in rescue["cases"]:
        lines.append(
            f"| `{row['background']}` | `{row['word']}` | {row['tail_kind']} | "
            f"{row['tail_period'] if row['tail_period'] is not None else 'n/a'} | "
            f"{row['tail_drift'] if row['tail_drift'] is not None else 'n/a'} | "
            f"{row['max_span']} | {row['operator_target_occurrence_count']} | "
            f"{row['first_target_time'] if row['first_target_time'] is not None else 'n/a'} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if data["status"] == "REACHABLE_SELECTORS_ROUTE_TO_T6_AND_T30_ATTRACTORS":
        lines.extend(
            [
                "The two reachable selectors do not fail to settle. They select",
                "different persistent attractors: T=6 for the bit-12 branch and",
                "T=30 for the [9,12] rescue branch. The earlier NONSTATIONARY label",
                "for the rescue was relative to the source detector's period cap",
                "of 16, not evidence of genuine aperiodicity.",
            ]
        )
    else:
        lines.append(data["verdict_reason"])
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- The T=6 basin count uses translation-normalized defect-shape cycles;",
            "  it does not assert equality of complete infinite backgrounds.",
            "- Long recurrence is verified to t=1000 and period 120, not proved for",
            "  arbitrary time or periods above 120.",
            "- Rescue ICs are the exact 40 preimages found under the four-background,",
            "  centered len1..8 source protocol.",
            "- The result is local to rule_73 and does not establish a universal",
            "  bifurcation law for cellular automata.",
            "- No paper, DOI, tag, release, or threshold changed.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase83 = load_json(FASE83_RESULTS)
    fase85 = load_json(FASE85_RESULTS)
    fase86 = load_json(FASE86_RESULTS)
    fase87_results = load_json(FASE87_RESULTS)
    differing_bits = list(fase85["preflight"]["differing_bits"])
    fase85_rows = {
        int(row["assignment"]): row for row in fase85["assignments"]
    }
    targets = {row["assignment"]: row for row in fase87_results["targets"]}
    if targets[T6_SELECTOR]["reference_operator_ic_count"] != 1:
        raise RuntimeError("The Fase 87 T=6 selector preimage count changed")
    if targets[RESCUE_SELECTOR]["reference_operator_ic_count"] != 40:
        raise RuntimeError("The Fase 87 rescue preimage count changed")
    reference_boundary = fase83["cases"][0]["boundary_trace"]
    reference_final_background = fase83["cases"][0]["local_final_background"]
    backgrounds = tuple(fase86["preflight"]["backgrounds"])
    preflight = {
        "rule": RULE,
        "source_run_count": 2008,
        "backgrounds": list(backgrounds),
        "t6_selector": assignment_hex(T6_SELECTOR),
        "rescue_selector": assignment_hex(RESCUE_SELECTOR),
        "long_steps": LONG_STEPS,
        "tail_start": TAIL_START,
        "max_period": MAX_PERIOD,
        "max_span": MAX_SPAN,
        "source_detector_period_range": [2, 16],
        "threshold_fitting": False,
    }
    if preflight_only:
        return {"phase": 88, "preflight": preflight}

    base = load_module("fase88_physical_sweep", SWEEP_SCRIPT)
    phase87 = load_module("fase88_reachability", FASE87_SCRIPT)
    words = list(base.ic_words())

    # Reference T=6 branch and its source-protocol shape basin.
    ref_background, ref_word_len, ref_word = T6_REFERENCE
    ref_long_row, ref_long = long_public_row(
        base,
        phase87,
        ref_background,
        ref_word_len,
        ref_word,
        T6_SELECTOR,
        reference_boundary,
        reference_final_background,
    )
    if ref_long_row["tail_kind"] != "STATIONARY" or ref_long_row["tail_period"] != 6:
        raise RuntimeError("The predeclared T=6 branch is not persistent at t=1000")
    ref_cycle = canonical_cycle(ref_long["shapes"], 6)
    ref_cycle_hash = sha256_json(ref_cycle)
    cycle_phases = reference_t6_phases(
        phase87,
        fase85_rows,
        differing_bits,
        ref_long,
        reference_boundary,
        reference_final_background,
    )

    t6_basin_ics = []
    rescue_ics: set[tuple[str, int, str]] = set()
    source_processed = 0
    for background in backgrounds:
        bg_frames = base.background_orbit(RULE, background)
        bg_sets = [set(frame) for frame in bg_frames]
        for word_len, word_value, word in words:
            source_processed += 1
            shapes = base.simulate_diff_shapes(RULE, bg_frames, word_value, word_len)
            if not shapes:
                continue
            stationary = base.detect_stationary(shapes)
            if stationary is not None and int(stationary["period_T"]) == 6:
                if canonical_cycle(shapes, 6) == ref_cycle:
                    t6_basin_ics.append((background, int(word_len), word))

            diff_sets = [phase87.shape_positions(shape) for shape in shapes]
            for time in range(BURN_IN, SOURCE_STEPS - HORIZON + 1):
                index = time - BURN_IN
                diff = diff_sets[index]
                positions = phase87.choose_positions(diff)
                assignment = phase87.assignment_at(bg_sets[time], diff, positions)
                if assignment != RESCUE_SELECTOR:
                    continue
                if phase87.operator_matches(
                    bg_sets,
                    diff_sets,
                    time,
                    positions,
                    reference_boundary,
                    reference_final_background,
                ):
                    rescue_ics.add((background, int(word_len), word))
                    break
    if source_processed != 2008:
        raise RuntimeError(f"Processed {source_processed}, expected 2008")
    if len(rescue_ics) != 40:
        raise RuntimeError(f"Recovered {len(rescue_ics)} rescue ICs, expected 40")

    rescue_rows = []
    for background, word_len, word in sorted(rescue_ics):
        row, _simulated = long_public_row(
            base,
            phase87,
            background,
            word_len,
            word,
            RESCUE_SELECTOR,
            reference_boundary,
            reference_final_background,
        )
        rescue_rows.append(row)
    class_counts = Counter(
        f"{row['tail_kind']}_T{row['tail_period']}"
        if row["tail_period"] is not None
        else row["tail_kind"]
        for row in rescue_rows
    )
    rescue_cycle_hashes = {
        row["cycle_sha256"] for row in rescue_rows if row["cycle_sha256"] is not None
    }

    t6_branch = {
        "selector_hex": assignment_hex(T6_SELECTOR),
        "reference_case": {
            "background": ref_background,
            "word_len": ref_word_len,
            "word": ref_word,
        },
        "reference_long_run": ref_long_row,
        "reference_cycle_sha256": ref_cycle_hash,
        "cycle_phases": cycle_phases,
        "source_basin_ic_count": len(t6_basin_ics),
        "source_basin_backgrounds": sorted({row[0] for row in t6_basin_ics}),
        "source_basin_ics": [
            {"background": bg, "word_len": word_len, "word": word}
            for bg, word_len, word in sorted(t6_basin_ics)
        ],
    }
    rescue_branch = {
        "selector_hex": assignment_hex(RESCUE_SELECTOR),
        "ic_count": len(rescue_rows),
        "persistent_bounded_count": sum(row["persistent_bounded"] for row in rescue_rows),
        "tail_class_counts": dict(sorted(class_counts.items())),
        "unique_cycle_count": len(rescue_cycle_hashes),
        "cycle_sha256": sorted(rescue_cycle_hashes),
        "total_operator_target_occurrences": sum(
            row["operator_target_occurrence_count"] for row in rescue_rows
        ),
        "cases": rescue_rows,
    }
    status, reason = classify(t6_branch, rescue_branch)
    data = {
        "phase": 88,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "t6_branch": t6_branch,
        "rescue_branch": rescue_branch,
    }
    RESULTS_JSON.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    data = run(preflight_only=args.preflight_only)
    if args.preflight_only:
        print(json.dumps(data, indent=2, sort_keys=True))
        return
    print(f"status={data['status']}")
    print(json.dumps(data["t6_branch"], indent=2, sort_keys=True))
    print(json.dumps({
        key: value
        for key, value in data["rescue_branch"].items()
        if key != "cases"
    }, indent=2, sort_keys=True))
    print(f"report={REPORT_MD}")


if __name__ == "__main__":
    main()
