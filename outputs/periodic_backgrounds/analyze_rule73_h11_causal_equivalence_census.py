#!/usr/bin/env python3
"""Fase 84: full h=11 recurrence census of the Fase 83 causal operator."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
FASE80_RESULTS = OUT_DIR / "rule73_len8_horizon_response_results.json"
FASE83_SCRIPT = OUT_DIR / "analyze_rule73_h11_exact_causal_equivalence.py"
FASE83_RESULTS = OUT_DIR / "rule73_h11_exact_causal_equivalence_results.json"
RESULTS_JSON = OUT_DIR / "rule73_h11_causal_equivalence_census_results.json"
REPORT_MD = OUT_DIR / "rule73_h11_causal_equivalence_census_report.md"

RULE = 73
T_LOCAL = 12
HORIZON = 11
REFERENCE_BACKGROUNDS = ("00111011", "00111101")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def select_h11_cohort(fase80: dict[str, Any]) -> list[dict[str, Any]]:
    cases = []
    for row in fase80["cases"]:
        measurements = [
            item for item in row["measurements"] if int(item["horizon"]) == HORIZON
        ]
        if len(measurements) != 1:
            raise RuntimeError(f"Expected one h=11 measurement for {row['label']}")
        cases.append(
            {
                "label": row["label"],
                "role": row["cohort"],
                "cohort": row["cohort"],
                "rule": RULE,
                "background": row["background"],
                "T_local": int(row["T_local"]),
                "word": row["word"],
                "horizon": HORIZON,
                "h11_comparable": bool(measurements[0]["comparable"]),
            }
        )
    cases.sort(key=lambda item: item["background"])
    if len(cases) != 18:
        raise RuntimeError(f"Expected 18 h=11 cases, got {len(cases)}")
    if any(case["T_local"] != T_LOCAL for case in cases):
        raise RuntimeError("Fase 84 cohort must contain only T_local=12 cases")
    if sum(case["h11_comparable"] for case in cases) != 8:
        raise RuntimeError("Expected 8 comparable and 10 non-comparable h=11 cases")
    return cases


def defect_table(prepared: dict[str, Any], output_index: int) -> np.ndarray:
    table = prepared["rows"][output_index].copy()
    if prepared["local_final_background"][output_index]:
        table ^= prepared["ones"]
    return table


def map_hashes(fase83, prepared: dict[str, Any]) -> dict[str, Any]:
    actual_rows = [fase83.sha256_u64(table) for table in prepared["rows"]]
    defect_rows = [
        fase83.sha256_u64(defect_table(prepared, index))
        for index in range(len(prepared["rows"]))
    ]
    actual_map = fase83.sha256_json(tuple(actual_rows))
    defect_map = fase83.sha256_json(tuple(defect_rows))
    return {
        "actual_row_sha256": actual_rows,
        "defect_row_sha256": defect_rows,
        "actual_map_sha256": actual_map,
        "defect_map_sha256": defect_map,
        "causal_map_sha256": fase83.sha256_json((actual_map, defect_map)),
    }


def normalized_positions(values: list[int], origin: int) -> list[int]:
    return [int(value) - origin for value in values]


def direct_map_comparison(
    left: dict[str, Any],
    right: dict[str, Any],
) -> dict[str, Any]:
    actual_equal = [
        bool(np.array_equal(left_table, right_table))
        for left_table, right_table in zip(left["rows"], right["rows"])
    ]
    defect_equal = [
        bool(
            np.array_equal(
                defect_table(left, index),
                defect_table(right, index),
            )
        )
        for index in range(len(left["rows"]))
    ]
    return {
        "actual_equal_count": sum(actual_equal),
        "defect_equal_count": sum(defect_equal),
        "actual_map_equal": all(actual_equal),
        "defect_map_equal": all(defect_equal),
        "causal_map_equal": all(actual_equal) and all(defect_equal),
    }


def trajectory_comparison(
    reference: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    translation = candidate["positions"][0] - reference["positions"][0]
    positions_translate = all(
        right - left == translation
        for left, right in zip(reference["positions"], candidate["positions"])
    )
    reference_sample = normalized_positions(
        reference["sample_diff"],
        reference["positions"][0],
    )
    candidate_sample = normalized_positions(
        candidate["sample_diff"],
        candidate["positions"][0],
    )
    reference_final = normalized_positions(
        reference["final_diff"],
        reference["positions"][0],
    )
    candidate_final = normalized_positions(
        candidate["final_diff"],
        candidate["positions"][0],
    )
    return {
        "translation": translation,
        "positions_translate": positions_translate,
        "sample_defect_translate": reference_sample == candidate_sample,
        "final_defect_translate": reference_final == candidate_final,
        "boundary_trace_equal": (
            reference["boundary_trace"] == candidate["boundary_trace"]
        ),
        "local_sample_actual_equal": (
            reference["local_sample_actual"] == candidate["local_sample_actual"]
        ),
        "local_sample_background_equal": (
            reference["local_sample_background"]
            == candidate["local_sample_background"]
        ),
        "local_final_actual_equal": (
            reference["local_final_actual"] == candidate["local_final_actual"]
        ),
        "local_final_background_equal": (
            reference["local_final_background"]
            == candidate["local_final_background"]
        ),
        "local_final_diff_equal": (
            reference["local_final_diff"] == candidate["local_final_diff"]
        ),
    }


def full_equivalence_hash(
    fase83,
    prepared: dict[str, Any],
    hashes: dict[str, Any],
) -> str:
    origin = prepared["positions"][0]
    signature = (
        hashes["causal_map_sha256"],
        tuple(
            (int(row["step"]), int(row["left"]), int(row["right"]))
            for row in prepared["boundary_trace"]
        ),
        tuple(int(bit) for bit in prepared["local_sample_actual"]),
        tuple(normalized_positions(prepared["sample_diff"], origin)),
        tuple(normalized_positions(prepared["final_diff"], origin)),
    )
    return fase83.sha256_json(signature)


def full_fase83_match(
    map_comparison: dict[str, Any],
    trajectory: dict[str, Any],
) -> bool:
    return bool(
        map_comparison["causal_map_equal"]
        and trajectory["positions_translate"]
        and trajectory["sample_defect_translate"]
        and trajectory["final_defect_translate"]
        and trajectory["boundary_trace_equal"]
        and trajectory["local_sample_actual_equal"]
    )


def make_public_row(
    case: dict[str, Any],
    prepared: dict[str, Any],
    hashes: dict[str, Any],
    direct: dict[str, Any],
    trajectory: dict[str, Any],
    reference_ids: set[str],
    full_signature_sha256: str,
) -> dict[str, Any]:
    concrete_assignment = sum(
        int(bit) << index
        for index, bit in enumerate(prepared["local_sample_actual"])
    )
    return {
        "label": case["label"],
        "background": case["background"],
        "word": case["word"],
        "cohort": case["cohort"],
        "h11_comparable": case["h11_comparable"],
        "is_reference": case["label"] in reference_ids,
        "active_indices": prepared["active_indices"],
        "concrete_assignment": concrete_assignment,
        "concrete_assignment_hex": f"0x{concrete_assignment:07x}",
        "translation_from_reference": trajectory["translation"],
        "actual_map_sha256": hashes["actual_map_sha256"],
        "defect_map_sha256": hashes["defect_map_sha256"],
        "causal_map_sha256": hashes["causal_map_sha256"],
        "full_equivalence_sha256": full_signature_sha256,
        "actual_map_match": direct["actual_map_equal"],
        "defect_map_match": direct["defect_map_equal"],
        "causal_map_match": direct["causal_map_equal"],
        "actual_equal_count": direct["actual_equal_count"],
        "defect_equal_count": direct["defect_equal_count"],
        "boundary_trace_match": trajectory["boundary_trace_equal"],
        "sample_defect_translate": trajectory["sample_defect_translate"],
        "final_defect_translate": trajectory["final_defect_translate"],
        "full_fase83_match": full_fase83_match(direct, trajectory),
        "concrete_mismatch_count": len(prepared["concrete_mismatch_indices"]),
    }


def signature_groups(rows: list[dict[str, Any]], field: str) -> list[list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for row in rows:
        grouped[row[field]].append(row["label"])
    return sorted(
        [sorted(labels) for labels in grouped.values() if len(labels) > 1],
        key=lambda labels: (labels[0], len(labels), labels),
    )


def direct_verify_groups(
    fase83,
    baseline,
    base,
    cases_by_label: dict[str, dict[str, Any]],
    groups: list[list[str]],
    map_kind: str,
) -> list[dict[str, Any]]:
    verified = []
    for labels in groups:
        reference = fase83.prepare_case(
            baseline,
            base,
            cases_by_label[labels[0]],
        )
        comparisons = []
        for label in labels[1:]:
            candidate = fase83.prepare_case(
                baseline,
                base,
                cases_by_label[label],
            )
            direct = direct_map_comparison(reference, candidate)
            if map_kind == "actual":
                equal = direct["actual_map_equal"]
            elif map_kind == "causal":
                equal = direct["causal_map_equal"]
            else:
                raise ValueError(f"Unknown map kind: {map_kind}")
            comparisons.append(
                {
                    "left": labels[0],
                    "right": label,
                    "direct_equal": equal,
                    **direct,
                }
            )
            if not equal:
                raise RuntimeError(
                    f"Hash group failed direct {map_kind} verification: "
                    f"{labels[0]} vs {label}"
                )
        verified.append(
            {
                "labels": labels,
                "map_kind": map_kind,
                "direct_verified": all(row["direct_equal"] for row in comparisons),
                "comparisons": comparisons,
            }
        )
    return verified


def direct_verify_full_groups(
    fase83,
    baseline,
    base,
    cases_by_label: dict[str, dict[str, Any]],
    groups: list[list[str]],
) -> list[dict[str, Any]]:
    verified = []
    for labels in groups:
        reference = fase83.prepare_case(
            baseline,
            base,
            cases_by_label[labels[0]],
        )
        comparisons = []
        for label in labels[1:]:
            candidate = fase83.prepare_case(
                baseline,
                base,
                cases_by_label[label],
            )
            direct = direct_map_comparison(reference, candidate)
            trajectory = trajectory_comparison(reference, candidate)
            equal = full_fase83_match(direct, trajectory)
            comparisons.append(
                {
                    "left": labels[0],
                    "right": label,
                    "direct_equal": equal,
                    **direct,
                    **trajectory,
                }
            )
            if not equal:
                raise RuntimeError(
                    "Hash group failed direct full-equivalence verification: "
                    f"{labels[0]} vs {label}"
                )
        verified.append(
            {
                "labels": labels,
                "map_kind": "full_equivalence",
                "direct_verified": all(row["direct_equal"] for row in comparisons),
                "comparisons": comparisons,
            }
        )
    return verified


def classify(
    rows: list[dict[str, Any]],
    reference_ids: set[str],
    full_groups: list[list[str]],
) -> tuple[str, str]:
    outside = [row for row in rows if row["label"] not in reference_ids]
    full_matches = [row for row in outside if row["full_fase83_match"]]
    causal_matches = [row for row in outside if row["causal_map_match"]]
    actual_only = [
        row
        for row in outside
        if row["actual_map_match"] and not row["defect_map_match"]
    ]
    if full_matches:
        return (
            "FASE83_EQUIVALENCE_RECURS_OUTSIDE_PAIR",
            "At least one additional h=11 case reproduces the exact causal maps, translated defect trajectory, and boundary forcing of the Fase 83 pair.",
        )
    external_full_groups = [
        group
        for group in full_groups
        if not set(group) & reference_ids and len(group) > 1
    ]
    reference_operator_labels = {
        row["label"] for row in rows if row["causal_map_match"]
    }
    external_same_operator_groups = [
        group
        for group in external_full_groups
        if set(group).issubset(reference_operator_labels)
    ]
    if external_same_operator_groups:
        return (
            "REFERENCE_OPERATOR_SPLITS_TRANSLATION_EQUIVALENCE_SUBTYPES",
            "The four-case reference operator class splits into two exact translated-trajectory subtypes: the original comparable pair and an external non-comparable pair.",
        )
    if causal_matches:
        return (
            "EXACT_OPERATOR_RECURS_WITHOUT_FULL_TRAJECTORY_EQUIVALENCE",
            "The exact actual and defect operators recur outside the pair, but the complete translated trajectory/boundary relation does not.",
        )
    if actual_only:
        return (
            "ACTUAL_OPERATOR_RECURS_DEFECT_MAP_DIFFERS",
            "The actual-state operator recurs outside the pair, but background subtraction produces a different defect operator.",
        )
    return (
        "FASE83_EQUIVALENCE_UNIQUE_FULL_H11_COHORT",
        "The exact Fase 83 causal equivalence occurs only in the two reference controls across all 18 h=11 cases.",
    )


def short_label(label: str) -> str:
    return label.replace("rule73_", "").replace("_T12", "")


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    lines = [
        "# Fase 84: rule_73 h=11 Exact Causal-Equivalence Census",
        "",
        "## Question",
        "",
        "Does the exact finite-horizon causal equivalence established for",
        "the two Fase 83 controls recur anywhere else in the complete",
        "rule_73/T=12 length-8 cohort at h=11?",
        "",
        "Fase 82 audited only 25 comparable events, including eight h=11",
        "cases. Fase 84 audits all 18 physical cases at h=11, including the",
        "ten cases that did not cross the T15-comparability threshold.",
        "",
        "## Predeclared Exact Test",
        "",
        "Each case is aligned by translation of its 25 local variables.",
        "For every output, the complete packed actual-state truth table and",
        "the background-subtracted defect truth table are compared directly",
        "against the left Fase 83 reference. No distance or threshold is fitted.",
        "",
        "An exact operator match requires all 25 actual tables and all 25 defect",
        "tables to be identical. A full Fase 83 recurrence additionally requires",
        "the translated sample/final defects and the 11-step boundary trace to",
        "match. Since Mobius inversion is bijective, identical defect truth",
        "tables imply identical ANF polynomials without recomputing coefficients.",
        "",
        "Hashes index candidate classes, but every repeated class is re-simulated",
        "and checked by direct array equality.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Physical h=11 cases: `{summary['case_count']}`",
        f"- Comparable cases: `{summary['comparable_count']}`",
        f"- Non-comparable cases: `{summary['noncomparable_count']}`",
        f"- Exact causal-map matches including references: `{summary['causal_match_count']}`",
        f"- Matches to original full subtype including references: `{summary['full_match_count']}`",
        f"- Matches to original full subtype outside reference pair: `{summary['full_outside_count']}`",
        f"- Exact operator matches outside reference pair: `{summary['causal_outside_count']}`",
        f"- Actual-only matches outside reference pair: `{summary['actual_only_outside_count']}`",
        f"- Duplicate exact causal classes in full cohort: `{summary['duplicate_causal_class_count']}`",
        f"- Duplicate full translation-equivalence classes: `{summary['duplicate_full_equivalence_class_count']}`",
        f"- Members of duplicate full-equivalence classes: `{summary['duplicate_full_equivalence_member_count']}`",
        f"- Size of reference causal-operator class: `{summary['reference_operator_class_size']}`",
        f"- Full trajectory subtypes inside reference operator class: `{summary['reference_operator_full_subtype_count']}`",
        f"- Concrete mismatches: `{summary['concrete_mismatch_count']}`",
        f"- Fase 83 reference hashes reproduced: `{summary['fase83_hashes_reproduced']}`",
        "",
        "## Complete h=11 Cohort",
        "",
        "| case | cohort | comparable | input | active outputs | actual rows | defect rows | causal match | boundary | full match |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in data["cases"]:
        lines.append(
            f"| {short_label(row['label'])} | {row['cohort']} | "
            f"{str(row['h11_comparable']).lower()} | `{row['concrete_assignment_hex']}` | "
            f"{len(row['active_indices'])} | "
            f"{row['actual_equal_count']}/25 | {row['defect_equal_count']}/25 | "
            f"{str(row['causal_map_match']).lower()} | "
            f"{str(row['boundary_trace_match']).lower()} | "
            f"{str(row['full_fase83_match']).lower()} |"
        )
    lines.extend(
        [
            "",
            "## Exact Duplicate Classes",
            "",
        ]
    )
    if not data["duplicate_causal_classes"]:
        lines.append("No exact causal-map class contains more than one case.")
    else:
        for index, group in enumerate(data["duplicate_causal_classes"], start=1):
            labels = ", ".join(f"`{short_label(label)}`" for label in group["labels"])
            lines.append(
                f"- Class {index}: {labels}; direct verification = "
                f"`{group['direct_verified']}`"
            )
    lines.extend(
        [
            "",
            "## Exact Translation-Equivalence Classes",
            "",
        ]
    )
    if not data["duplicate_full_equivalence_classes"]:
        lines.append("No full translation-equivalence class contains more than one case.")
    else:
        for index, group in enumerate(
            data["duplicate_full_equivalence_classes"],
            start=1,
        ):
            labels = ", ".join(f"`{short_label(label)}`" for label in group["labels"])
            lines.append(
                f"- Subtype {index}: {labels}; direct verification = "
                f"`{group['direct_verified']}`"
            )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if data["status"] == "REFERENCE_OPERATOR_SPLITS_TRANSLATION_EQUIVALENCE_SUBTYPES":
        lines.extend(
            [
                "The Fase 83 operator is not unique to the original pair. It is",
                "shared by four controls, but their realized defect trajectories",
                "split into two exact translation-equivalence subtypes. The",
                "original pair has four active outputs and crosses the scalar",
                "threshold; the external pair has seven active outputs and does",
                "not. Operator identity is therefore not sufficient for the",
                "h=11 crossing: the concrete 25-bit symbolic assignment selects the",
                "trajectory subtype.",
            ]
        )
    elif data["status"] == "FASE83_EQUIVALENCE_UNIQUE_FULL_H11_COHORT":
        lines.extend(
            [
                "The local causal operator identified in Fase 83 remains unique",
                "to its two translated controls even after adding all ten h=11",
                "non-crossing cases. Its uniqueness is therefore not an artifact",
                "of restricting Fase 82 to measurements that passed the scalar",
                "T15-comparability threshold.",
            ]
        )
    else:
        lines.append(data["verdict_reason"])
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- The census is complete only for the 18 rule_73/T=12 primitive",
            "  length-8 cases already fixed by Fases 78-80 at h=11.",
            "- It does not test other rules, local periods, background lengths,",
            "  window widths, or horizons.",
            "- Repeated causal operators are exact finite-horizon equivalences;",
            "  they do not imply global equivalence of infinite backgrounds.",
            "- A unique high-dimensional operator in n=18 does not estimate",
            "  out-of-sample prevalence or predictive accuracy.",
            "- No paper, DOI, tag, release, or classification threshold changed.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase80 = load_json(FASE80_RESULTS)
    cases = select_h11_cohort(fase80)
    reference_ids = {
        case["label"]
        for case in cases
        if case["background"] in REFERENCE_BACKGROUNDS
    }
    preflight = {
        "rule": RULE,
        "T_local": T_LOCAL,
        "horizon": HORIZON,
        "case_count": len(cases),
        "comparable_count": sum(case["h11_comparable"] for case in cases),
        "noncomparable_count": sum(not case["h11_comparable"] for case in cases),
        "reference_backgrounds": list(REFERENCE_BACKGROUNDS),
        "actual_operator_test": "direct equality of all 25 packed truth tables",
        "defect_operator_test": "direct equality of all 25 background-subtracted truth tables",
        "full_equivalence_test": "causal operator plus translated sample/final defect and boundary trace",
        "threshold_fitting": False,
    }
    if preflight_only:
        return {"phase": 84, "preflight": preflight, "cases": cases}

    fase83 = importlib.util.spec_from_file_location(
        "fase84_exact_causal_equivalence",
        FASE83_SCRIPT,
    )
    if fase83 is None or fase83.loader is None:
        raise RuntimeError(f"Cannot import {FASE83_SCRIPT}")
    fase83_module = importlib.util.module_from_spec(fase83)
    sys.modules[fase83.name] = fase83_module
    fase83.loader.exec_module(fase83_module)
    baseline = fase83_module.load_module(
        "fase84_periodic_bg_anf_baseline",
        fase83_module.BASELINE_SCRIPT,
    )
    base = baseline.load_base_module()
    reference_case = next(
        case for case in cases if case["background"] == REFERENCE_BACKGROUNDS[0]
    )
    reference = fase83_module.prepare_case(baseline, base, reference_case)
    reference_hashes = map_hashes(fase83_module, reference)

    rows = []
    for index, case in enumerate(cases, start=1):
        print(f"[{index}/{len(cases)}] {case['label']}", flush=True)
        prepared = (
            reference
            if case["label"] == reference_case["label"]
            else fase83_module.prepare_case(baseline, base, case)
        )
        hashes = map_hashes(fase83_module, prepared)
        full_signature = full_equivalence_hash(
            fase83_module,
            prepared,
            hashes,
        )
        direct = direct_map_comparison(reference, prepared)
        trajectory = trajectory_comparison(reference, prepared)
        rows.append(
            make_public_row(
                case,
                prepared,
                hashes,
                direct,
                trajectory,
                reference_ids,
                full_signature,
            )
        )

    actual_groups = signature_groups(rows, "actual_map_sha256")
    causal_groups = signature_groups(rows, "causal_map_sha256")
    full_groups = signature_groups(rows, "full_equivalence_sha256")
    cases_by_label = {case["label"]: case for case in cases}
    verified_actual = direct_verify_groups(
        fase83_module,
        baseline,
        base,
        cases_by_label,
        actual_groups,
        "actual",
    )
    verified_causal = direct_verify_groups(
        fase83_module,
        baseline,
        base,
        cases_by_label,
        causal_groups,
        "causal",
    )
    verified_full = direct_verify_full_groups(
        fase83_module,
        baseline,
        base,
        cases_by_label,
        full_groups,
    )

    fase83_results = load_json(FASE83_RESULTS)
    expected_actual = [
        row["left_sha256"]
        for row in fase83_results["comparison"]["actual_truth_rows"]
    ]
    expected_defect = [
        row["left_sha256"]
        for row in fase83_results["comparison"]["defect_truth_rows"]
    ]
    hashes_reproduced = (
        reference_hashes["actual_row_sha256"] == expected_actual
        and reference_hashes["defect_row_sha256"] == expected_defect
    )
    if not hashes_reproduced:
        raise RuntimeError("Fase 83 reference hashes were not reproduced")

    status, reason = classify(rows, reference_ids, full_groups)
    outside = [row for row in rows if row["label"] not in reference_ids]
    reference_row = next(row for row in rows if row["label"] == reference_case["label"])
    reference_operator_rows = [
        row
        for row in rows
        if row["causal_map_sha256"] == reference_row["causal_map_sha256"]
    ]
    reference_operator_full_signatures = {
        row["full_equivalence_sha256"] for row in reference_operator_rows
    }
    summary = {
        "case_count": len(rows),
        "comparable_count": sum(row["h11_comparable"] for row in rows),
        "noncomparable_count": sum(not row["h11_comparable"] for row in rows),
        "causal_match_count": sum(row["causal_map_match"] for row in rows),
        "full_match_count": sum(row["full_fase83_match"] for row in rows),
        "full_outside_count": sum(row["full_fase83_match"] for row in outside),
        "causal_outside_count": sum(row["causal_map_match"] for row in outside),
        "actual_only_outside_count": sum(
            row["actual_map_match"] and not row["defect_map_match"] for row in outside
        ),
        "duplicate_actual_class_count": len(actual_groups),
        "duplicate_causal_class_count": len(causal_groups),
        "duplicate_full_equivalence_class_count": len(full_groups),
        "duplicate_full_equivalence_member_count": sum(
            len(group) for group in full_groups
        ),
        "reference_operator_class_size": len(reference_operator_rows),
        "reference_operator_full_subtype_count": len(
            reference_operator_full_signatures
        ),
        "direct_actual_classes_verified": all(
            group["direct_verified"] for group in verified_actual
        ),
        "direct_causal_classes_verified": all(
            group["direct_verified"] for group in verified_causal
        ),
        "direct_full_equivalence_classes_verified": all(
            group["direct_verified"] for group in verified_full
        ),
        "concrete_mismatch_count": sum(row["concrete_mismatch_count"] for row in rows),
        "fase83_hashes_reproduced": hashes_reproduced,
        "active_output_count_distribution": dict(
            sorted(Counter(len(row["active_indices"]) for row in rows).items())
        ),
    }
    data = {
        "phase": 84,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "reference_ids": sorted(reference_ids),
        "reference_hashes": reference_hashes,
        "cases": rows,
        "duplicate_actual_classes": verified_actual,
        "duplicate_causal_classes": verified_causal,
        "duplicate_full_equivalence_classes": verified_full,
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
