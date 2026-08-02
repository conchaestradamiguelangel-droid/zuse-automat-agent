#!/usr/bin/env python3
"""Fase 83: exact causal-map audit of the rule_73 h=11 control pair."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
FASE80_RESULTS = OUT_DIR / "rule73_len8_horizon_response_results.json"
FASE82_RESULTS = OUT_DIR / "rule73_control_signature_grid_results.json"
RESULTS_JSON = OUT_DIR / "rule73_h11_exact_causal_equivalence_results.json"
REPORT_MD = OUT_DIR / "rule73_h11_exact_causal_equivalence_report.md"

REFERENCE_BACKGROUNDS = ("00111011", "00111101")
REFERENCE_HORIZON = 11
EXPECTED_ACTIVE_INDICES = (9, 13, 14, 15)
RULE = 73


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
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_u64(values: np.ndarray) -> str:
    canonical = values.astype("<u8", copy=False)
    return hashlib.sha256(canonical.tobytes(order="C")).hexdigest()


def sha256_bits(bits: np.ndarray) -> str:
    packed = np.packbits(bits, bitorder="little")
    return hashlib.sha256(packed.tobytes(order="C")).hexdigest()


def select_reference_cases(fase80: dict[str, Any]) -> list[dict[str, Any]]:
    selected = []
    for case in fase80["cases"]:
        if case["background"] not in REFERENCE_BACKGROUNDS:
            continue
        h11 = [
            row
            for row in case["measurements"]
            if int(row["horizon"]) == REFERENCE_HORIZON
        ]
        if len(h11) != 1 or not h11[0]["comparable"]:
            raise RuntimeError(f"Reference is not a unique h=11 crossing: {case['label']}")
        selected.append(
            {
                "label": case["label"],
                "role": "baseline_control",
                "cohort": case["cohort"],
                "rule": RULE,
                "background": case["background"],
                "T_local": int(case["T_local"]),
                "word": case["word"],
                "horizon": REFERENCE_HORIZON,
            }
        )
    selected.sort(key=lambda row: row["background"])
    if [row["background"] for row in selected] != list(REFERENCE_BACKGROUNDS):
        raise RuntimeError(f"Expected reference backgrounds {REFERENCE_BACKGROUNDS}")
    return selected


def local_bits(baseline, frame: list[int], positions: list[int]) -> list[int]:
    return [baseline.bit_from_frame(frame, position) for position in positions]


def boundary_trace(
    baseline,
    actual_frames: list[list[int]],
    positions: list[int],
    horizon: int,
) -> list[dict[str, int]]:
    trace = []
    for offset in range(horizon):
        frame = actual_frames[baseline.SAMPLE_START + offset]
        trace.append(
            {
                "step": offset,
                "left": baseline.bit_from_frame(frame, positions[0] - 1),
                "right": baseline.bit_from_frame(frame, positions[-1] + 1),
            }
        )
    return trace


def prepare_case(baseline, base, case: dict[str, Any]) -> dict[str, Any]:
    steps = baseline.SAMPLE_START + case["horizon"]
    bg_frames, actual_frames = baseline.simulate_dense_frames(
        base,
        case["rule"],
        case["background"],
        case["word"],
        steps,
    )
    sample_index = baseline.SAMPLE_START
    final_index = sample_index + case["horizon"]
    sample_diff = baseline.active_diff_indices(
        bg_frames[sample_index],
        actual_frames[sample_index],
    )
    positions = baseline.choose_positions(sample_diff)
    final_diff = baseline.active_diff_indices(
        bg_frames[final_index],
        actual_frames[final_index],
    )
    local_final_diff = [
        baseline.bit_from_frame(actual_frames[final_index], position)
        ^ baseline.bit_from_frame(bg_frames[final_index], position)
        for position in positions
    ]
    active_indices = [index for index, bit in enumerate(local_final_diff) if bit]
    simulated = baseline.simulate_packed_cone(
        case["rule"],
        bg_frames,
        actual_frames,
        positions,
        case["horizon"],
    )
    assignment = baseline.concrete_assignment(
        actual_frames[sample_index],
        positions,
    )
    concrete_mismatches = []
    for index, table in enumerate(simulated["rows"]):
        packed_bit = baseline.packed_bit(table, assignment)
        concrete_bit = baseline.bit_from_frame(
            actual_frames[final_index],
            positions[index],
        )
        if packed_bit != concrete_bit:
            concrete_mismatches.append(index)
    if concrete_mismatches:
        raise RuntimeError(
            f"Packed/concrete mismatch in {case['label']}: {concrete_mismatches}"
        )
    return {
        "case": case,
        "bg_frames": bg_frames,
        "actual_frames": actual_frames,
        "positions": positions,
        "sample_diff": sample_diff,
        "final_diff": final_diff,
        "local_sample_actual": local_bits(
            baseline,
            actual_frames[sample_index],
            positions,
        ),
        "local_sample_background": local_bits(
            baseline,
            bg_frames[sample_index],
            positions,
        ),
        "local_final_actual": local_bits(
            baseline,
            actual_frames[final_index],
            positions,
        ),
        "local_final_background": local_bits(
            baseline,
            bg_frames[final_index],
            positions,
        ),
        "local_final_diff": local_final_diff,
        "active_indices": active_indices,
        "concrete_mismatch_indices": concrete_mismatches,
        "boundary_trace": boundary_trace(
            baseline,
            actual_frames,
            positions,
            case["horizon"],
        ),
        "rows": simulated["rows"],
        "ones": simulated["ones"],
    }


def anf_support(
    baseline,
    table: np.ndarray,
    final_background_bit: int,
    ones: np.ndarray,
    popcount16: np.ndarray,
) -> dict[str, Any]:
    defect_table = table.copy()
    if final_background_bit:
        defect_table ^= ones
    coefficients = np.unpackbits(
        defect_table.view(np.uint8),
        bitorder="little",
    )[: baseline.ASSIGNMENT_COUNT]
    baseline.mobius_inplace(coefficients)
    degree, monomial_count, degree_histogram = baseline.degree_and_count(
        coefficients,
        popcount16,
    )
    return {
        "coefficients": coefficients,
        "sha256": sha256_bits(coefficients),
        "degree": degree,
        "monomial_count": monomial_count,
        "degree_histogram": degree_histogram,
    }


def compare_cases(baseline, left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_positions = left["positions"]
    right_positions = right["positions"]
    translation = right_positions[0] - left_positions[0]
    positions_translate = all(
        right_pos - left_pos == translation
        for left_pos, right_pos in zip(left_positions, right_positions)
    )
    sample_diff_translates = [
        position + translation for position in left["sample_diff"]
    ] == right["sample_diff"]
    final_diff_translates = [
        position + translation for position in left["final_diff"]
    ] == right["final_diff"]

    actual_truth_rows = []
    defect_truth_rows = []
    for index, (left_table, right_table) in enumerate(zip(left["rows"], right["rows"])):
        left_actual_hash = sha256_u64(left_table)
        right_actual_hash = sha256_u64(right_table)
        actual_equal = bool(np.array_equal(left_table, right_table))

        left_defect = left_table.copy()
        if left["local_final_background"][index]:
            left_defect ^= left["ones"]
        right_defect = right_table.copy()
        if right["local_final_background"][index]:
            right_defect ^= right["ones"]
        defect_equal = bool(np.array_equal(left_defect, right_defect))
        actual_truth_rows.append(
            {
                "output_index": index,
                "left_sha256": left_actual_hash,
                "right_sha256": right_actual_hash,
                "equal": actual_equal,
            }
        )
        defect_truth_rows.append(
            {
                "output_index": index,
                "left_sha256": sha256_u64(left_defect),
                "right_sha256": sha256_u64(right_defect),
                "equal": defect_equal,
            }
        )

    active_indices = tuple(left["active_indices"])
    if active_indices != tuple(right["active_indices"]):
        raise RuntimeError("Reference controls no longer share local active support")
    if active_indices != EXPECTED_ACTIVE_INDICES:
        raise RuntimeError(
            f"Expected active indices {EXPECTED_ACTIVE_INDICES}, got {active_indices}"
        )

    popcount16 = np.array(
        [int(value).bit_count() for value in range(1 << 16)],
        dtype=np.uint8,
    )
    center_x2 = min(active_indices) + max(active_indices)
    active_anf = []
    left_geometry = []
    right_geometry = []
    for index in active_indices:
        left_anf = anf_support(
            baseline,
            left["rows"][index],
            left["local_final_background"][index],
            left["ones"],
            popcount16,
        )
        right_anf = anf_support(
            baseline,
            right["rows"][index],
            right["local_final_background"][index],
            right["ones"],
            popcount16,
        )
        difference_count = int(
            np.count_nonzero(left_anf["coefficients"] ^ right_anf["coefficients"])
        )
        coordinate_x2 = 2 * index - center_x2
        left_histogram = tuple(
            sorted((int(key), int(value)) for key, value in left_anf["degree_histogram"].items())
        )
        right_histogram = tuple(
            sorted((int(key), int(value)) for key, value in right_anf["degree_histogram"].items())
        )
        left_geometry.append(
            (coordinate_x2, left_anf["degree"], left_anf["monomial_count"], left_histogram)
        )
        right_geometry.append(
            (coordinate_x2, right_anf["degree"], right_anf["monomial_count"], right_histogram)
        )
        active_anf.append(
            {
                "output_index": index,
                "coordinate_x2": coordinate_x2,
                "left_sha256": left_anf["sha256"],
                "right_sha256": right_anf["sha256"],
                "exact_equal": difference_count == 0,
                "symmetric_difference_count": difference_count,
                "degree": left_anf["degree"],
                "monomial_count": left_anf["monomial_count"],
                "degree_histogram": left_anf["degree_histogram"],
                "summary_equal": (
                    left_anf["degree"] == right_anf["degree"]
                    and left_anf["monomial_count"] == right_anf["monomial_count"]
                    and left_anf["degree_histogram"] == right_anf["degree_histogram"]
                ),
            }
        )
        del left_anf["coefficients"]
        del right_anf["coefficients"]

    fase82 = load_json(FASE82_RESULTS)
    expected_geometry_hash = fase82["reference"]["oriented_sha256"]
    left_geometry_hash = sha256_json(tuple(left_geometry))
    right_geometry_hash = sha256_json(tuple(right_geometry))
    return {
        "translation": translation,
        "positions_translate": positions_translate,
        "sample_diff_translates": sample_diff_translates,
        "final_diff_translates": final_diff_translates,
        "local_sample_actual_equal": left["local_sample_actual"] == right["local_sample_actual"],
        "local_sample_background_equal": (
            left["local_sample_background"] == right["local_sample_background"]
        ),
        "local_final_actual_equal": left["local_final_actual"] == right["local_final_actual"],
        "local_final_background_equal": (
            left["local_final_background"] == right["local_final_background"]
        ),
        "local_final_diff_equal": left["local_final_diff"] == right["local_final_diff"],
        "boundary_trace_equal": left["boundary_trace"] == right["boundary_trace"],
        "actual_truth_rows": actual_truth_rows,
        "defect_truth_rows": defect_truth_rows,
        "active_anf": active_anf,
        "geometry_hashes": {
            "expected_fase82": expected_geometry_hash,
            "left": left_geometry_hash,
            "right": right_geometry_hash,
            "both_match_fase82": (
                left_geometry_hash == expected_geometry_hash
                and right_geometry_hash == expected_geometry_hash
            ),
        },
    }


def classify(comparison: dict[str, Any]) -> tuple[str, str]:
    all_actual = all(row["equal"] for row in comparison["actual_truth_rows"])
    all_defect = all(row["equal"] for row in comparison["defect_truth_rows"])
    active_exact = all(row["exact_equal"] for row in comparison["active_anf"])
    aligned = (
        comparison["positions_translate"]
        and comparison["sample_diff_translates"]
        and comparison["final_diff_translates"]
    )
    boundary_explains = comparison["boundary_trace_equal"]
    if aligned and all_actual and all_defect and active_exact and boundary_explains:
        return (
            "EXACT_CAUSAL_MAP_TRANSLATION_EQUIVALENCE",
            "After a one-cell translation, both controls have identical boundary forcing, all 25 causal truth tables, and exact active-output ANF supports.",
        )
    if active_exact:
        return (
            "ACTIVE_ANF_POLYNOMIALS_IDENTICAL",
            "The four active-output ANF supports are identical, but the complete causal map or its boundary explanation differs.",
        )
    if any(row["exact_equal"] for row in comparison["active_anf"]):
        return (
            "ACTIVE_ANF_POLYNOMIAL_IDENTITY_PARTIAL",
            "Only a subset of corresponding active outputs has identical ANF support.",
        )
    return (
        "GEOMETRY_ONLY_NOT_POLYNOMIAL",
        "The controls share output-resolved degree/count geometry but not exact active-output ANF supports.",
    )


def public_case(prepared: dict[str, Any]) -> dict[str, Any]:
    case = prepared["case"]
    return {
        "label": case["label"],
        "background": case["background"],
        "word": case["word"],
        "T_local": case["T_local"],
        "horizon": case["horizon"],
        "positions_global": prepared["positions"],
        "sample_diff_global": prepared["sample_diff"],
        "final_diff_global": prepared["final_diff"],
        "active_indices": prepared["active_indices"],
        "concrete_mismatch_indices": prepared["concrete_mismatch_indices"],
        "local_sample_actual": prepared["local_sample_actual"],
        "local_sample_background": prepared["local_sample_background"],
        "local_final_actual": prepared["local_final_actual"],
        "local_final_background": prepared["local_final_background"],
        "local_final_diff": prepared["local_final_diff"],
        "boundary_trace": prepared["boundary_trace"],
    }


def write_report(data: dict[str, Any]) -> None:
    comparison = data["comparison"]
    left, right = data["cases"]
    summary = data["summary"]
    lines = [
        "# Fase 83: rule_73 h=11 Exact Causal Equivalence",
        "",
        "## Question",
        "",
        "Do the two h=11 controls from Fases 81-82 share the same exact",
        "ANF polynomials after their 25-cell input windows are aligned by",
        "translation, or only the same output-level degree/count geometry?",
        "",
        "## Predeclared Correspondence",
        "",
        "Variables are named by their local input coordinate `-12..12`.",
        "No variable permutation is fitted. The right-hand case must be an",
        "exact physical translation of the left-hand 25-cell window. The",
        "four active outputs are then compared at the same local indices.",
        "",
        "For each corresponding active output, the full 2^25-entry defect",
        "truth table is transformed by Mobius inversion. Equality means zero",
        "coefficient differences across all 2^25 possible monomials. SHA-256",
        "is used only as a reproducible content identifier.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Physical translation: `{comparison['translation']}` cell",
        f"- Positions translate exactly: `{comparison['positions_translate']}`",
        f"- Sample defects translate exactly: `{comparison['sample_diff_translates']}`",
        f"- Final defects translate exactly: `{comparison['final_diff_translates']}`",
        f"- Boundary forcing traces identical: `{comparison['boundary_trace_equal']}`",
        f"- Actual causal truth tables identical: `{summary['actual_truth_equal_count']}/25`",
        f"- Defect causal truth tables identical: `{summary['defect_truth_equal_count']}/25`",
        f"- Exact active-output ANF matches: `{summary['active_anf_equal_count']}/4`",
        f"- Total differing active ANF coefficients: `{summary['active_anf_difference_count']}`",
        f"- Fase 82 geometry hash reproduced: `{comparison['geometry_hashes']['both_match_fase82']}`",
        "",
        "## Reference Pair",
        "",
        "| side | background | IC | global input window | active local outputs |",
        "| --- | --- | --- | --- | --- |",
        f"| left | `{left['background']}` | `{left['word']}` | `{left['positions_global'][0]}..{left['positions_global'][-1]}` | `{left['active_indices']}` |",
        f"| right | `{right['background']}` | `{right['word']}` | `{right['positions_global'][0]}..{right['positions_global'][-1]}` | `{right['active_indices']}` |",
        "",
        "## Exact Active-Output ANF Audit",
        "",
        "| x2 | output | degree | monomials | exact | coefficient differences | SHA-256 |",
        "| ---: | ---: | ---: | ---: | --- | ---: | --- |",
    ]
    for row in comparison["active_anf"]:
        lines.append(
            f"| {row['coordinate_x2']} | {row['output_index']} | {row['degree']} | "
            f"{row['monomial_count']} | {str(row['exact_equal']).lower()} | "
            f"{row['symmetric_difference_count']} | `{row['left_sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Boundary Forcing",
            "",
            "The packed causal calculation starts from the same 25 symbolic",
            "variables in both cases. Its only case-specific inputs are the",
            "left and right boundary bits injected at each step. Their traces",
            "are listed below.",
            "",
            "| step | left boundary | right boundary |",
            "| ---: | ---: | ---: |",
        ]
    )
    for row in left["boundary_trace"]:
        lines.append(f"| {row['step']} | {row['left']} | {row['right']} |")
    lines.extend(
        [
            "",
            "## Local-State Diagnostics",
            "",
            f"- Symbolic-window concrete samples equal: `{comparison['local_sample_actual_equal']}`",
            f"- Background samples equal: `{comparison['local_sample_background_equal']}`",
            f"- Final actual windows equal: `{comparison['local_final_actual_equal']}`",
            f"- Final background windows equal: `{comparison['local_final_background_equal']}`",
            f"- Final defect windows equal: `{comparison['local_final_diff_equal']}`",
            "",
            "These concrete-state equalities are diagnostics only. Exact causal",
            "map equality is decided by the complete symbolic truth tables and",
            "ANF coefficient supports, not by one realized trajectory.",
            "",
            "## Interpretation",
            "",
        ]
    )
    if data["status"] == "EXACT_CAUSAL_MAP_TRANSLATION_EQUIVALENCE":
        lines.extend(
            [
                "The Fase 82 geometry match is not merely a collision of counts",
                "and degree histograms. Once translated by one cell, the two",
                "controls implement the same finite-horizon causal operator.",
                "Identical boundary forcing explains why the same rule acting on",
                "the same symbolic variables produces identical truth tables and",
                "therefore identical ANF polynomials.",
            ]
        )
    else:
        lines.append(data["verdict_reason"])
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- This is an exact audit of one pair, one rule, one local period,",
            "  one input-window width, and horizon h=11.",
            "- Translation equivalence at finite horizon does not imply that the",
            "  two infinite periodic backgrounds are globally symmetry-related.",
            "- The result explains the Fase 81-82 pair but does not estimate how",
            "  frequently such local causal equivalences occur outside this pair.",
            "- SHA-256 is a content checksum; equality was also checked directly",
            "  by zero coefficient-wise symmetric difference.",
            "- No classification threshold was fitted and no paper or release",
            "  metadata was changed.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase80 = load_json(FASE80_RESULTS)
    cases = select_reference_cases(fase80)
    preflight = {
        "reference_backgrounds": list(REFERENCE_BACKGROUNDS),
        "horizon": REFERENCE_HORIZON,
        "window_cells": 25,
        "variable_alignment": "same local offsets -12..12 after physical translation",
        "active_output_correspondence": "same local output index",
        "exact_test": "zero coefficient differences over all 2^25 ANF coefficients",
        "threshold_fitting": False,
        "scope": "one h=11 control pair",
    }
    if preflight_only:
        return {"phase": 83, "preflight": preflight, "cases": cases}

    baseline = load_module("fase83_periodic_bg_anf_baseline", BASELINE_SCRIPT)
    base = baseline.load_base_module()
    prepared = [prepare_case(baseline, base, case) for case in cases]
    comparison = compare_cases(baseline, prepared[0], prepared[1])
    status, reason = classify(comparison)
    public_cases = [public_case(item) for item in prepared]
    summary = {
        "actual_truth_equal_count": sum(
            1 for row in comparison["actual_truth_rows"] if row["equal"]
        ),
        "defect_truth_equal_count": sum(
            1 for row in comparison["defect_truth_rows"] if row["equal"]
        ),
        "active_anf_equal_count": sum(
            1 for row in comparison["active_anf"] if row["exact_equal"]
        ),
        "active_anf_difference_count": sum(
            row["symmetric_difference_count"] for row in comparison["active_anf"]
        ),
        "concrete_mismatch_count": sum(
            len(item["concrete_mismatch_indices"]) for item in prepared
        ),
    }
    data = {
        "phase": 83,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "cases": public_cases,
        "comparison": comparison,
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
