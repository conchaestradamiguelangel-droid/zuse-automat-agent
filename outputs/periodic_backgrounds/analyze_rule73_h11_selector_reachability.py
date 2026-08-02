#!/usr/bin/env python3
"""Fase 87: preimage and basin restrictions for the Fase 85 selectors."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
SWEEP_SCRIPT = OUT_DIR / "sweep_periodic_background_oscillators.py"
FASE83_RESULTS = OUT_DIR / "rule73_h11_exact_causal_equivalence_results.json"
FASE85_RESULTS = OUT_DIR / "rule73_h11_input_selector_results.json"
FASE86_RESULTS = OUT_DIR / "rule73_h11_physical_selector_realizability_results.json"
RESULTS_JSON = OUT_DIR / "rule73_h11_selector_reachability_results.json"
REPORT_MD = OUT_DIR / "rule73_h11_selector_reachability_report.md"

RULE = 73
HORIZON = 11
BURN_IN = 80
LAST_OPERATOR_START = 289
EXPECTED_A = 0x0310630
EXPECTED_B = 0x035B8B0


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


def assignment_hex(value: int) -> str:
    return f"0x{value:07x}"


def shape_positions(shape) -> set[int]:
    return {int(shape.min_pos) + int(offset) for offset in shape.offsets}


def choose_positions(diff: set[int]) -> list[int]:
    center = (min(diff) + max(diff)) // 2 if diff else 128
    return list(range(center - 12, center + 13))


def actual_bit(background: set[int], diff: set[int], position: int) -> int:
    return int((position in background) ^ (position in diff))


def assignment_at(
    background: set[int],
    diff: set[int],
    positions: list[int],
) -> int:
    value = 0
    for index, position in enumerate(positions):
        if actual_bit(background, diff, position):
            value |= 1 << index
    return value


def operator_matches(
    background_sets: list[set[int]],
    diff_sets: list[set[int]],
    time: int,
    positions: list[int],
    reference_boundary: list[dict[str, int]],
    reference_final_background: list[int],
) -> bool:
    trace = []
    for offset in range(HORIZON):
        index = time - BURN_IN + offset
        background = background_sets[time + offset]
        diff = diff_sets[index]
        trace.append(
            {
                "step": offset,
                "left": actual_bit(background, diff, positions[0] - 1),
                "right": actual_bit(background, diff, positions[-1] + 1),
            }
        )
    final_background = [
        int(position in background_sets[time + HORIZON])
        for position in positions
    ]
    return trace == reference_boundary and final_background == reference_final_background


def subcube_mask(assignment: int, differing_bits: list[int]) -> int | None:
    xor_value = assignment ^ EXPECTED_A
    allowed = sum(1 << bit for bit in differing_bits)
    if xor_value & ~allowed:
        return None
    mask = 0
    for index, bit in enumerate(differing_bits):
        if (xor_value >> bit) & 1:
            mask |= 1 << index
    return mask


def affine_invariants(values: set[int], width: int) -> list[dict[str, int]]:
    if not values:
        return []
    first = min(values)
    candidates = []
    for coefficient_mask in range(1, 1 << width):
        parity = (coefficient_mask & first).bit_count() & 1
        if all(
            ((coefficient_mask & value).bit_count() & 1) == parity
            for value in values
        ):
            candidates.append((coefficient_mask, parity))

    basis: dict[int, int] = {}
    selected = []
    for coefficient_mask, parity in sorted(
        candidates,
        key=lambda item: (item[0].bit_count(), item[0], item[1]),
    ):
        reduced = coefficient_mask
        for pivot in sorted(basis, reverse=True):
            if (reduced >> pivot) & 1:
                reduced ^= basis[pivot]
        if reduced == 0:
            continue
        pivot = reduced.bit_length() - 1
        basis[pivot] = reduced
        selected.append(
            {"coefficient_mask": coefficient_mask, "parity": parity}
        )
    return selected


def public_invariants(
    invariants: list[dict[str, int]],
    differing_bits: list[int],
) -> list[dict[str, Any]]:
    output = []
    for row in invariants:
        indices = [
            index
            for index in range(len(differing_bits))
            if (row["coefficient_mask"] >> index) & 1
        ]
        output.append(
            {
                **row,
                "subcube_indices": indices,
                "global_bits": [differing_bits[index] for index in indices],
            }
        )
    return output


def violated_invariants(
    value: int,
    invariants: list[dict[str, Any]],
) -> list[int]:
    return [
        index
        for index, row in enumerate(invariants)
        if ((int(row["coefficient_mask"]) & value).bit_count() & 1)
        != int(row["parity"])
    ]


def classify(targets: list[dict[str, Any]]) -> tuple[str, str]:
    if any(row["stationary_t12_operator_ic_count"] > 0 for row in targets):
        return (
            "MINIMAL_SELECTOR_T12_BASIN_REACHED",
            "At least one minimal selector is reached inside the persistent T=12 reference-operator basin, contradicting the bounded Fase 86 census.",
        )
    if any(row["reference_operator_ic_count"] > 0 for row in targets):
        return (
            "MINIMAL_SELECTORS_EXCLUDED_FROM_T12_BASIN",
            "Minimal selectors have bounded physical preimages under the exact operator but none belongs to the persistent T=12 basin.",
        )
    if any(row["postburn_ic_count"] > 0 for row in targets):
        return (
            "MINIMAL_SELECTORS_REACHED_OUTSIDE_REFERENCE_OPERATOR",
            "Minimal selectors occur in bounded post-burn dynamics, but never with the reference h=11 defect operator.",
        )
    return (
        "MINIMAL_SELECTORS_NO_BOUNDED_PREIMAGE",
        "None of the nine minimal selectors appears at any scanned post-burn phase of the bounded source-protocol trajectories.",
    )


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    lines = [
        "# Fase 87: Preimage and Basin Restrictions of the h=11 Selectors",
        "",
        "## Question",
        "",
        "Why do the nine minimal symbolic selectors of Fase 85 fail to appear",
        "in the physical T=12 census of Fase 86?",
        "",
        "## Predeclared Protocol",
        "",
        "The same 2,008 source-protocol runs are recomputed: rule_73, the four",
        "reference backgrounds, all 502 centered non-zero IC words of length",
        "1..8, width 256, 300 steps, and burn-in 80. Every bounded state from",
        "t=80 through t=289 is aligned on its defect and tested against the nine",
        "minimal selector assignments. The upper limit leaves eleven future",
        "steps available for the exact h=11 operator test.",
        "",
        "The gates are evaluated without threshold fitting:",
        "",
        "1. exact selector appears in any bounded post-burn state;",
        "2. exact selector appears at the original sample phase t=80;",
        "3. exact selector preserves the reference boundary trace and final",
        "   local background, hence the exact defect operator;",
        "4. the source run is a stationary period-12 oscillator.",
        "",
        "Affine GF(2) invariants are computed exactly from reached subcube masks",
        "as a descriptive reachability audit, not fitted as a classifier.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Runs processed: `{summary['processed_runs']}`",
        f"- Bounded source trajectories: `{summary['bounded_run_count']}`",
        f"- Post-burn states scanned: `{summary['postburn_state_count']}`",
        f"- Reference-operator subcube occurrences: `{summary['reference_operator_subcube_occurrence_count']}`",
        f"- Unique all-phase reference-operator subcube masks: `{summary['all_phase_unique_subcube_mask_count']}`",
        f"- Minimal selectors with any bounded post-burn preimage: `{summary['targets_with_postburn_preimage']}/9`",
        f"- Minimal selectors reached at t=80: `{summary['targets_reached_at_t80']}/9`",
        f"- Minimal selectors reached with reference operator: `{summary['targets_reached_with_reference_operator']}/9`",
        f"- Minimal selectors in stationary T=12 reference basin: `{summary['targets_in_t12_reference_basin']}/9`",
        "",
        "## Selector Gate Audit",
        "",
        "| selector | role | changed/reverted bits | post-burn ICs | t=80 ICs | operator ICs | operator IC periods | T12 basin ICs | fixed-phase invariant violations | all-phase invariant violations |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for row in data["targets"]:
        lines.append(
            f"| `{row['assignment_hex']}` | `{row['role']}` | `{row['selector_bits']}` | "
            f"{row['postburn_ic_count']} | {row['t80_ic_count']} | "
            f"{row['reference_operator_ic_count']} | "
            f"`{row['reference_operator_ic_period_counts']}` | "
            f"{row['stationary_t12_operator_ic_count']} | "
            f"`{row['fixed_phase_invariant_violations']}` | "
            f"`{row['all_phase_invariant_violations']}` |"
        )
    lines.extend(
        [
            "",
            "## Exact Affine Reachability Invariants",
            "",
            "### Fixed sample phase t=80, stationary T=12 reference basin",
            "",
            "| id | subcube indices | global input bits | parity |",
            "| ---: | --- | --- | ---: |",
        ]
    )
    for index, row in enumerate(data["fixed_phase_invariants"]):
        lines.append(
            f"| {index} | `{row['subcube_indices']}` | `{row['global_bits']}` | {row['parity']} |"
        )
    if not data["fixed_phase_invariants"]:
        lines.append("| none | none | none | n/a |")
    lines.extend(
        [
            "",
            "### All scanned phases with the reference operator",
            "",
            "| id | subcube indices | global input bits | parity |",
            "| ---: | --- | --- | ---: |",
        ]
    )
    for index, row in enumerate(data["all_phase_invariants"]):
        lines.append(
            f"| {index} | `{row['subcube_indices']}` | `{row['global_bits']}` | {row['parity']} |"
        )
    if not data["all_phase_invariants"]:
        lines.append("| none | none | none | n/a |")
    lines.extend(
        [
            "",
            "Each row means that the XOR of the listed subcube bits has the",
            "reported parity for every reached mask in that cohort.",
            "",
            "## Interpretation",
            "",
        ]
    )
    if data["status"] == "MINIMAL_SELECTORS_NO_BOUNDED_PREIMAGE":
        lines.extend(
            [
                "The exclusion occurs before the T=12 basin or ANF-comparability",
                "test: the allowed centered ICs never generate any minimal selector",
                "at any admissible post-burn phase. Affine invariants explain the",
                "selectors that violate them; selectors satisfying every reported",
                "invariant remain excluded by higher-order or basin-specific",
                "reachability constraints not reducible to those affine relations.",
            ]
        )
    elif data["status"] == "MINIMAL_SELECTORS_REACHED_OUTSIDE_REFERENCE_OPERATOR":
        lines.extend(
            [
                "The selectors have bounded physical preimages, but changing phase",
                "or trajectory also changes the h=11 operator. Their absence in",
                "Fase 86 is therefore an operator/phase restriction, not raw",
                "unreachability from the source IC family.",
            ]
        )
    elif data["status"] == "MINIMAL_SELECTORS_EXCLUDED_FROM_T12_BASIN":
        lines.extend(
            [
                "The exact operator admits physical selector preimages, but those",
                "preimages do not settle into the stationary T=12 basin. The",
                "restriction is dynamical-basin selection rather than local",
                "operator reachability.",
            ]
        )
    else:
        lines.append(data["verdict_reason"])
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- Exhaustive only for four backgrounds, centered non-zero ICs len1..8,",
            "  and bounded trajectories accepted by the original sweep protocol.",
            "- Runs rejected for extinction or span greater than 32 are outside the",
            "  bounded source cohort and are not assigned post-burn preimages.",
            "- Affine invariants summarize observed reachability exactly but do not",
            "  prove a universal conservation law of rule_73.",
            "- Absence here does not exclude longer, shifted, or multi-site ICs.",
            "- No paper, DOI, tag, release, or threshold changed.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase83 = load_json(FASE83_RESULTS)
    fase85 = load_json(FASE85_RESULTS)
    fase86 = load_json(FASE86_RESULTS)
    differing_bits = list(fase85["preflight"]["differing_bits"])
    reference_boundary = fase83["cases"][0]["boundary_trace"]
    reference_final_background = fase83["cases"][0]["local_final_background"]
    backgrounds = tuple(fase86["preflight"]["backgrounds"])

    target_specs = []
    for role, minimum_key, bits_key in (
        ("A_ATOMIC_BREAK", "a_to_noncomparable", "changed_global_bits"),
        ("B_MINIMAL_RESCUE", "b_to_comparable", "reverted_global_bits"),
    ):
        for row in fase85["minimal_interventions"][minimum_key]["rows"]:
            assignment = int(row["assignment_hex"], 16)
            mask = subcube_mask(assignment, differing_bits)
            if mask is None:
                raise RuntimeError("A minimal selector lies outside the Fase 85 subcube")
            target_specs.append(
                {
                    "role": role,
                    "assignment": assignment,
                    "assignment_hex": assignment_hex(assignment),
                    "subcube_mask": mask,
                    "selector_bits": list(row[bits_key]),
                }
            )
    target_specs.sort(key=lambda row: (row["role"], row["assignment"]))
    if len(target_specs) != 9 or len({row["assignment"] for row in target_specs}) != 9:
        raise RuntimeError("Expected nine distinct minimal selector assignments")
    target_by_assignment = {row["assignment"]: row for row in target_specs}

    preflight = {
        "rule": RULE,
        "backgrounds": list(backgrounds),
        "ic_policy": "all non-zero centered binary words length 1..8",
        "processed_run_target": 2008,
        "burn_in": BURN_IN,
        "last_operator_start": LAST_OPERATOR_START,
        "postburn_times": [BURN_IN, LAST_OPERATOR_START],
        "target_count": len(target_specs),
        "gates": [
            "bounded post-burn occurrence",
            "t=80 occurrence",
            "exact reference defect operator",
            "stationary T=12 reference-operator basin",
        ],
        "threshold_fitting": False,
    }
    if preflight_only:
        return {"phase": 87, "preflight": preflight, "targets": target_specs}

    base = load_module("fase87_physical_sweep", SWEEP_SCRIPT)
    words = list(base.ic_words())
    if len(words) != 502:
        raise RuntimeError(f"Expected 502 source ICs, got {len(words)}")

    target_events: dict[int, dict[str, Any]] = {
        assignment: {
            "postburn_ics": set(),
            "t80_ics": set(),
            "reference_operator_ics": set(),
            "reference_operator_ic_periods": {},
            "stationary_t12_operator_ics": set(),
            "postburn_occurrence_count": 0,
            "reference_operator_occurrence_count": 0,
            "example_events": [],
        }
        for assignment in target_by_assignment
    }
    processed = 0
    bounded_runs = 0
    postburn_states = 0
    operator_subcube_occurrences = 0
    all_phase_masks: set[int] = set()

    for background in backgrounds:
        background_frames = base.background_orbit(RULE, background)
        background_sets = [set(frame) for frame in background_frames]
        for word_len, word_value, word in words:
            processed += 1
            shapes = base.simulate_diff_shapes(
                RULE, background_frames, word_value, word_len
            )
            if not shapes:
                continue
            bounded_runs += 1
            diff_sets = [shape_positions(shape) for shape in shapes]
            stationary = base.detect_stationary(shapes)
            stationary_period = (
                int(stationary["period_T"]) if stationary is not None else None
            )
            ic_key = (background, int(word_len), word)
            for time in range(BURN_IN, LAST_OPERATOR_START + 1):
                postburn_states += 1
                diff = diff_sets[time - BURN_IN]
                positions = choose_positions(diff)
                assignment = assignment_at(
                    background_sets[time], diff, positions
                )
                target = target_events.get(assignment)
                if target is not None:
                    target["postburn_occurrence_count"] = int(
                        target["postburn_occurrence_count"]
                    ) + 1
                    target["postburn_ics"].add(ic_key)
                    if time == BURN_IN:
                        target["t80_ics"].add(ic_key)

                mask = subcube_mask(assignment, differing_bits)
                if target is None and mask is None:
                    continue
                same_operator = operator_matches(
                    background_sets,
                    diff_sets,
                    time,
                    positions,
                    reference_boundary,
                    reference_final_background,
                )
                if same_operator and mask is not None:
                    operator_subcube_occurrences += 1
                    all_phase_masks.add(mask)
                if target is None or not same_operator:
                    continue
                target["reference_operator_occurrence_count"] = int(
                    target["reference_operator_occurrence_count"]
                ) + 1
                target["reference_operator_ics"].add(ic_key)
                target["reference_operator_ic_periods"][ic_key] = stationary_period
                if stationary_period == 12:
                    target["stationary_t12_operator_ics"].add(ic_key)
                examples = target["example_events"]
                if len(examples) < 10:
                    examples.append(
                        {
                            "background": background,
                            "word_len": int(word_len),
                            "word": word,
                            "time": time,
                            "stationary_period": stationary_period,
                        }
                    )

    if processed != preflight["processed_run_target"]:
        raise RuntimeError(f"Processed {processed}, expected 2008")

    fixed_phase_masks = {
        subcube_mask(int(row["assignment"]), differing_bits)
        for row in fase86["physical_assignment_groups"]
    }
    if None in fixed_phase_masks:
        raise RuntimeError("Fase 86 contains an assignment outside its subcube")
    fixed_phase_values = {int(value) for value in fixed_phase_masks}
    fixed_invariants = public_invariants(
        affine_invariants(fixed_phase_values, len(differing_bits)),
        differing_bits,
    )
    all_phase_invariants = public_invariants(
        affine_invariants(all_phase_masks, len(differing_bits)),
        differing_bits,
    )

    targets = []
    for spec in target_specs:
        events = target_events[spec["assignment"]]
        period_counts = Counter(
            "NONSTATIONARY" if period is None else str(period)
            for period in events["reference_operator_ic_periods"].values()
        )
        targets.append(
            {
                **spec,
                "postburn_occurrence_count": int(events["postburn_occurrence_count"]),
                "postburn_ic_count": len(events["postburn_ics"]),
                "t80_ic_count": len(events["t80_ics"]),
                "reference_operator_occurrence_count": int(
                    events["reference_operator_occurrence_count"]
                ),
                "reference_operator_ic_count": len(events["reference_operator_ics"]),
                "reference_operator_ic_period_counts": dict(
                    sorted(period_counts.items())
                ),
                "stationary_t12_operator_ic_count": len(
                    events["stationary_t12_operator_ics"]
                ),
                "fixed_phase_invariant_violations": violated_invariants(
                    spec["subcube_mask"], fixed_invariants
                ),
                "all_phase_invariant_violations": violated_invariants(
                    spec["subcube_mask"], all_phase_invariants
                ),
                "example_reference_operator_events": events["example_events"],
            }
        )

    status, reason = classify(targets)
    summary = {
        "processed_runs": processed,
        "bounded_run_count": bounded_runs,
        "postburn_state_count": postburn_states,
        "reference_operator_subcube_occurrence_count": operator_subcube_occurrences,
        "all_phase_unique_subcube_mask_count": len(all_phase_masks),
        "fixed_phase_unique_subcube_mask_count": len(fixed_phase_values),
        "fixed_phase_invariant_count": len(fixed_invariants),
        "all_phase_invariant_count": len(all_phase_invariants),
        "targets_with_postburn_preimage": sum(
            row["postburn_ic_count"] > 0 for row in targets
        ),
        "targets_reached_at_t80": sum(row["t80_ic_count"] > 0 for row in targets),
        "targets_reached_with_reference_operator": sum(
            row["reference_operator_ic_count"] > 0 for row in targets
        ),
        "targets_in_t12_reference_basin": sum(
            row["stationary_t12_operator_ic_count"] > 0 for row in targets
        ),
    }
    data = {
        "phase": 87,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "fixed_phase_reached_masks": sorted(fixed_phase_values),
        "all_phase_reached_masks": sorted(all_phase_masks),
        "fixed_phase_invariants": fixed_invariants,
        "all_phase_invariants": all_phase_invariants,
        "targets": targets,
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
    print(json.dumps(data["summary"], indent=2, sort_keys=True))
    print(f"report={REPORT_MD}")


if __name__ == "__main__":
    main()
