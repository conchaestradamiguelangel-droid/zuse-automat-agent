#!/usr/bin/env python3
"""Fase 86: physical realizability census for the Fase 85 input selectors."""

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
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
FASE83_RESULTS = OUT_DIR / "rule73_h11_exact_causal_equivalence_results.json"
FASE84_RESULTS = OUT_DIR / "rule73_h11_causal_equivalence_census_results.json"
FASE85_RESULTS = OUT_DIR / "rule73_h11_input_selector_results.json"
RESULTS_JSON = OUT_DIR / "rule73_h11_physical_selector_realizability_results.json"
REPORT_MD = OUT_DIR / "rule73_h11_physical_selector_realizability_report.md"

RULE = 73
T_LOCAL = 12
HORIZON = 11
SAMPLE_START = 80
EXPECTED_A = 0x0310630
EXPECTED_B = 0x035B8B0
EXPECTED_BACKGROUNDS = (
    "00110111",
    "00111011",
    "00111101",
    "01101111",
)
KNOWN_ENDPOINT_CASES = {
    ("00110111", "111"): EXPECTED_B,
    ("00111011", "011"): EXPECTED_A,
    ("00111101", "101"): EXPECTED_A,
    ("01101111", "1"): EXPECTED_B,
}


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


def local_bits(baseline, frame: list[int], positions: list[int]) -> list[int]:
    return [baseline.bit_from_frame(frame, position) for position in positions]


def boundary_trace(
    baseline,
    actual_frames: list[list[int]],
    positions: list[int],
) -> list[dict[str, int]]:
    trace = []
    for offset in range(HORIZON):
        frame = actual_frames[SAMPLE_START + offset]
        trace.append(
            {
                "step": offset,
                "left": baseline.bit_from_frame(frame, positions[0] - 1),
                "right": baseline.bit_from_frame(frame, positions[-1] + 1),
            }
        )
    return trace


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


def physical_measurement(
    baseline,
    base,
    background: str,
    word_len: int,
    word: str,
    reference_boundary: list[dict[str, int]],
    reference_final_background: list[int],
    fase85_rows: dict[int, dict[str, Any]],
    differing_bits: list[int],
) -> dict[str, Any]:
    steps = SAMPLE_START + HORIZON
    bg_frames, actual_frames = baseline.simulate_dense_frames(
        base,
        RULE,
        background,
        word,
        steps,
    )
    sample_diff = baseline.active_diff_indices(
        bg_frames[SAMPLE_START], actual_frames[SAMPLE_START]
    )
    positions = baseline.choose_positions(sample_diff)
    assignment = baseline.concrete_assignment(actual_frames[SAMPLE_START], positions)
    trace = boundary_trace(baseline, actual_frames, positions)
    final_background = local_bits(
        baseline,
        bg_frames[SAMPLE_START + HORIZON],
        positions,
    )
    final_actual = local_bits(
        baseline,
        actual_frames[SAMPLE_START + HORIZON],
        positions,
    )
    final_defect = [
        actual ^ background_bit
        for actual, background_bit in zip(final_actual, final_background)
    ]
    mask = subcube_mask(assignment, differing_bits)
    fase85_row = fase85_rows.get(assignment)
    same_boundary = trace == reference_boundary
    same_final_background = final_background == reference_final_background
    same_defect_operator = same_boundary and same_final_background
    predicted_final_match = None
    if same_defect_operator and fase85_row is not None:
        predicted_final_match = (
            "".join(str(bit) for bit in final_defect)
            == fase85_row["final_pattern"]
        )
    return {
        "background": background,
        "word_len": word_len,
        "word": word,
        "assignment": assignment,
        "assignment_hex": assignment_hex(assignment),
        "subcube_mask": mask,
        "subcube_mask_binary": (
            f"{mask:0{len(differing_bits)}b}" if mask is not None else None
        ),
        "in_fase85_subcube": mask is not None,
        "same_boundary": same_boundary,
        "same_final_background": same_final_background,
        "same_defect_operator": same_defect_operator,
        "sample_diff_size": len(sample_diff),
        "sample_diff_span": (
            max(sample_diff) - min(sample_diff) + 1 if sample_diff else 0
        ),
        "positions_start": positions[0],
        "final_defect_pattern": "".join(str(bit) for bit in final_defect),
        "fase85_final_pattern_match": predicted_final_match,
        "fase85_comparable": (
            bool(fase85_row["comparable_to_t15"])
            if fase85_row is not None
            else None
        ),
        "fase85_final_class": (
            fase85_row["final_class"] if fase85_row is not None else None
        ),
    }


def public_group(
    assignment: int,
    rows: list[dict[str, Any]],
    differing_bits: list[int],
    endpoint_assignments: set[int],
    atomic_break_assignments: set[int],
    rescue_assignments: set[int],
) -> dict[str, Any]:
    first = rows[0]
    tags = []
    if assignment in endpoint_assignments:
        tags.append("ENDPOINT")
    if assignment in atomic_break_assignments:
        tags.append("A_ATOMIC_BREAK")
    if assignment in rescue_assignments:
        tags.append("B_MINIMAL_RESCUE")
    if not tags:
        tags.append("NONENDPOINT_SUBCUBE")
    physical_cases = sorted(
        {
            (row["background"], int(row["word_len"]), row["word"])
            for row in rows
        }
    )
    mask = int(first["subcube_mask"])
    changed_from_a = [
        bit for index, bit in enumerate(differing_bits) if (mask >> index) & 1
    ]
    reverted_from_b = [bit for bit in differing_bits if bit not in changed_from_a]
    return {
        "assignment": assignment,
        "assignment_hex": assignment_hex(assignment),
        "tags": tags,
        "changed_from_a_bits": changed_from_a,
        "reverted_from_b_bits": reverted_from_b,
        "distance_from_a": len(changed_from_a),
        "distance_from_b": len(reverted_from_b),
        "fase85_comparable": first["fase85_comparable"],
        "fase85_final_class": first["fase85_final_class"],
        "physical_case_count": len(physical_cases),
        "physical_cases": [
            {"background": bg, "word_len": word_len, "word": word}
            for bg, word_len, word in physical_cases
        ],
    }


def classify(
    known_endpoints_confirmed: bool,
    groups: list[dict[str, Any]],
) -> tuple[str, str]:
    if not known_endpoints_confirmed:
        return (
            "PHYSICAL_REFERENCE_CLASS_NOT_REPRODUCED",
            "The source physical protocol did not reproduce every known endpoint, so selector realizability cannot be interpreted.",
        )
    minimal = [
        row
        for row in groups
        if "A_ATOMIC_BREAK" in row["tags"] or "B_MINIMAL_RESCUE" in row["tags"]
    ]
    if minimal:
        return (
            "PHYSICAL_MINIMAL_SELECTORS_REALIZED",
            "At least one predeclared minimal symbolic selector is reached by a persistent physical T=12 oscillator under the source protocol.",
        )
    nonendpoints = [row for row in groups if "ENDPOINT" not in row["tags"]]
    if nonendpoints:
        return (
            "PHYSICAL_NONENDPOINT_SUBCUBE_REALIZED",
            "Persistent physical oscillators reach non-endpoint assignments in the Fase 85 subcube, but none is a predeclared minimal selector.",
        )
    return (
        "PHYSICAL_ENDPOINTS_ONLY_REACHED",
        "The source protocol reproduces the physical endpoints but reaches no non-endpoint assignment in the Fase 85 subcube.",
    )


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    lines = [
        "# Fase 86: Physical Realizability of the h=11 Input Selectors",
        "",
        "## Question",
        "",
        "Do the controlled symbolic input selectors isolated in Fase 85 occur",
        "as persistent physical stationary oscillators under the original",
        "periodic-background sweep protocol?",
        "",
        "## Predeclared Protocol",
        "",
        "- Rule: `73`.",
        f"- Physical backgrounds: `{list(data['preflight']['backgrounds'])}`.",
        "- ICs: all 502 non-zero centered binary words of length 1..8 per background.",
        "- Total physical runs: `2008`.",
        "- Original detector: width 256, 300 steps, burn-in 80, stationary period 12.",
        "- Local audit: sample t=80, h=11, 25 cells.",
        "- Exact operator gate: reference boundary trace and local final-background",
        "  vector must both match Fases 83-85.",
        "  For a deterministic radius-1 rule, the same local rule and boundary",
        "  trace induce the same actual-state map; the same final-background",
        "  vector then induces the same background-subtracted defect map.",
        "- No comparability threshold is changed or fitted.",
        "",
        "A symbolic assignment counts as physically realized only when a source-protocol",
        "IC produces a persistent T=12 stationary oscillator, the exact reference defect",
        "operator is preserved, the t=80 assignment lies in the eight-bit Fase 85",
        "subcube, and the physical h=11 final defect equals the symbolic prediction.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Runs processed: `{summary['processed_runs']}`",
        f"- Stationary oscillators of any period: `{summary['stationary_any_period_count']}`",
        f"- Stationary T=12 runs: `{summary['stationary_t12_count']}`",
        f"- T=12 runs with the exact reference defect operator: `{summary['reference_operator_t12_count']}`",
        f"- Raw physical hits in the Fase 85 subcube: `{summary['physical_subcube_raw_count']}`",
        f"- Unique physically reached subcube assignments: `{summary['physical_subcube_unique_count']}`",
        f"- Unique non-endpoint assignments reached: `{summary['physical_nonendpoint_unique_count']}`",
        f"- Minimal A-side atomic breaks reached: `{summary['physical_atomic_break_unique_count']}`",
        f"- Minimal B-side rescues reached: `{summary['physical_rescue_unique_count']}`",
        f"- Physical/symbolic final-pattern mismatches: `{summary['physical_symbolic_mismatch_count']}`",
        f"- Four known endpoint cases confirmed: `{str(summary['known_endpoints_confirmed']).lower()}`",
        "",
        "## Physically Reached Fase 85 Assignments",
        "",
        "| assignment | changes from A | reversions from B | role | comparable | physical ICs |",
        "| --- | --- | --- | --- | --- | ---: |",
    ]
    for row in data["physical_assignment_groups"]:
        lines.append(
            f"| `{row['assignment_hex']}` | `{row['changed_from_a_bits']}` | "
            f"`{row['reverted_from_b_bits']}` | `{','.join(row['tags'])}` | "
            f"{str(row['fase85_comparable']).lower()} | "
            f"{row['physical_case_count']} |"
        )
    if not data["physical_assignment_groups"]:
        lines.append("| none | none | none | none | n/a | 0 |")
    lines.extend(
        [
            "",
            "## Physical IC Evidence",
            "",
            "The complete alias list is stored in the JSON results. This compact",
            "table gives one deterministic representative per reached assignment.",
            "",
            "| assignment | representative background/IC | aliases | backgrounds |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for group in data["physical_assignment_groups"]:
        case = group["physical_cases"][0]
        backgrounds = sorted(
            {item["background"] for item in group["physical_cases"]}
        )
        lines.append(
            f"| `{group['assignment_hex']}` | `{case['background']}/{case['word']}` "
            f"(len {case['word_len']}) | {group['physical_case_count']} | "
            f"`{backgrounds}` |"
        )
    if not data["physical_assignment_groups"]:
        lines.append("| none | none | 0 | none |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if data["status"] == "PHYSICAL_MINIMAL_SELECTORS_REALIZED":
        lines.extend(
            [
                "At least one minimal selector from the controlled symbolic subcube",
                "is dynamically reachable by the original physical protocol. This",
                "links the Fase 85 intervention to a persistent oscillator rather than",
                "to a formally valid but unreachable local assignment.",
            ]
        )
    elif data["status"] == "PHYSICAL_NONENDPOINT_SUBCUBE_REALIZED":
        lines.extend(
            [
                "The physical dynamics enters the symbolic subcube beyond its two",
                "endpoints, but it does not realize either predeclared minimal selector.",
                "Reachability is therefore broader than the observed endpoint pair but",
                "does not yet validate the atomic selector claim physically.",
            ]
        )
    elif data["status"] == "PHYSICAL_ENDPOINTS_ONLY_REACHED":
        lines.extend(
            [
                "The physical source protocol reaches the two observed endpoint",
                "assignments but none of the 254 controlled intermediate assignments.",
                "Fase 85 remains a valid symbolic intervention result, while its",
                "minimal selectors are not physically realized in this bounded census.",
            ]
        )
    else:
        lines.append(data["verdict_reason"])
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- The physical census is exhaustive only for four backgrounds and the",
            "  original centered non-zero IC words of length 1..8.",
            "- Failure to reach a selector does not prove that no longer, shifted, or",
            "  multi-site physical perturbation can realize it.",
            "- Success establishes reachability for rule_73/T12/h11/window25, not a",
            "  universal selector law for cellular automata.",
            "- Physical aliases are reported separately from unique t=80 assignments.",
            "- No paper, DOI, tag, release, or classification threshold changed.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase83 = load_json(FASE83_RESULTS)
    fase84 = load_json(FASE84_RESULTS)
    fase85 = load_json(FASE85_RESULTS)
    reference_case = fase83["cases"][0]
    reference_boundary = reference_case["boundary_trace"]
    reference_final_background = reference_case["local_final_background"]
    reference_backgrounds = tuple(
        sorted(
            row["background"]
            for row in fase84["cases"]
            if row["causal_map_match"]
        )
    )
    if reference_backgrounds != EXPECTED_BACKGROUNDS:
        raise RuntimeError(
            f"Reference physical backgrounds changed: {reference_backgrounds}"
        )
    differing_bits = list(fase85["preflight"]["differing_bits"])
    fase85_rows = {
        int(row["assignment"]): row for row in fase85["assignments"]
    }
    if len(fase85_rows) != 256:
        raise RuntimeError("Fase 85 assignment census is incomplete")
    endpoint_assignments = {EXPECTED_A, EXPECTED_B}
    atomic_break_assignments = {
        int(row["assignment_hex"], 16)
        for row in fase85["minimal_interventions"]["a_to_noncomparable"]["rows"]
    }
    rescue_assignments = {
        int(row["assignment_hex"], 16)
        for row in fase85["minimal_interventions"]["b_to_comparable"]["rows"]
    }
    preflight = {
        "rule": RULE,
        "T_local": T_LOCAL,
        "horizon": HORIZON,
        "sample_start": SAMPLE_START,
        "window_cells": 25,
        "backgrounds": list(reference_backgrounds),
        "ic_policy": "all non-zero centered binary words length 1..8",
        "ic_count_per_background": 502,
        "processed_run_target": 4 * 502,
        "physical_gate": "original stationary detector, exact period 12",
        "operator_gate": "reference boundary trace and local final background",
        "subcube_gate": "only the eight differing Fase 85 bits may vary",
        "threshold_fitting": False,
    }
    if preflight_only:
        return {"phase": 86, "preflight": preflight}

    base = load_module("fase86_physical_sweep", SWEEP_SCRIPT)
    baseline = load_module("fase86_anf_baseline", BASELINE_SCRIPT)
    words = list(base.ic_words())
    if len(words) != 502:
        raise RuntimeError(f"Expected 502 source ICs, got {len(words)}")

    processed = 0
    stationary_any = 0
    stationary_period_counts: Counter[int] = Counter()
    t12_rows = []
    for background in reference_backgrounds:
        bg_frames = base.background_orbit(RULE, background)
        for word_len, word_value, word in words:
            processed += 1
            shapes = base.simulate_diff_shapes(
                RULE, bg_frames, word_value, word_len
            )
            if not shapes:
                continue
            stationary = base.detect_stationary(shapes)
            if stationary is None:
                continue
            stationary_any += 1
            period = int(stationary["period_T"])
            stationary_period_counts[period] += 1
            if period != T_LOCAL:
                continue
            measured = physical_measurement(
                baseline,
                base,
                background,
                word_len,
                word,
                reference_boundary,
                reference_final_background,
                fase85_rows,
                differing_bits,
            )
            measured["period_T"] = period
            measured["stationary_span"] = int(stationary["span"])
            t12_rows.append(measured)

    if processed != preflight["processed_run_target"]:
        raise RuntimeError(f"Processed {processed}, expected 2008")

    reference_operator_rows = [
        row for row in t12_rows if row["same_defect_operator"]
    ]
    subcube_rows = [
        row
        for row in reference_operator_rows
        if row["in_fase85_subcube"]
    ]
    mismatches = [
        row for row in subcube_rows if row["fase85_final_pattern_match"] is not True
    ]
    if mismatches:
        raise RuntimeError(
            "Physical/symbolic final mismatch: "
            + ", ".join(
                f"{row['background']}/{row['word']}" for row in mismatches
            )
        )

    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in subcube_rows:
        grouped[int(row["assignment"])].append(row)
    groups = [
        public_group(
            assignment,
            sorted(
                group_rows,
                key=lambda row: (
                    row["background"], row["word_len"], row["word"]
                ),
            ),
            differing_bits,
            endpoint_assignments,
            atomic_break_assignments,
            rescue_assignments,
        )
        for assignment, group_rows in sorted(grouped.items())
    ]

    known_endpoint_matches = []
    for (background, word), expected_assignment in sorted(KNOWN_ENDPOINT_CASES.items()):
        matches = [
            row
            for row in subcube_rows
            if row["background"] == background
            and row["word"] == word
            and row["assignment"] == expected_assignment
        ]
        known_endpoint_matches.append(
            {
                "background": background,
                "word": word,
                "expected_assignment_hex": assignment_hex(expected_assignment),
                "confirmed": len(matches) == 1,
            }
        )
    known_endpoints_confirmed = all(
        row["confirmed"] for row in known_endpoint_matches
    )
    status, reason = classify(known_endpoints_confirmed, groups)
    summary = {
        "processed_runs": processed,
        "stationary_any_period_count": stationary_any,
        "stationary_period_counts": {
            str(period): count
            for period, count in sorted(stationary_period_counts.items())
        },
        "stationary_t12_count": len(t12_rows),
        "reference_operator_t12_count": len(reference_operator_rows),
        "physical_subcube_raw_count": len(subcube_rows),
        "physical_subcube_unique_count": len(groups),
        "physical_nonendpoint_unique_count": sum(
            "ENDPOINT" not in row["tags"] for row in groups
        ),
        "physical_atomic_break_unique_count": sum(
            "A_ATOMIC_BREAK" in row["tags"] for row in groups
        ),
        "physical_rescue_unique_count": sum(
            "B_MINIMAL_RESCUE" in row["tags"] for row in groups
        ),
        "physical_symbolic_mismatch_count": len(mismatches),
        "known_endpoints_confirmed": known_endpoints_confirmed,
    }
    data = {
        "phase": 86,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "known_endpoint_checks": known_endpoint_matches,
        "physical_assignment_groups": groups,
        "stationary_t12_cases": sorted(
            t12_rows,
            key=lambda row: (row["background"], row["word_len"], row["word"]),
        ),
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
