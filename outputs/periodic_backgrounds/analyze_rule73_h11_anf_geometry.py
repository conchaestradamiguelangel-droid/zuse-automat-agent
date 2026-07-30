#!/usr/bin/env python3
"""Fase 81: output-resolved ANF geometry of rule_73 h=11 crossings."""

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
FASE78_SCRIPT = OUT_DIR / "analyze_rule73_len8_holdout.py"
FASE78_RESULTS = OUT_DIR / "rule73_len8_holdout_results.json"
FASE79_SCRIPT = OUT_DIR / "analyze_rule73_len8_neighbor_horizons.py"
FASE80_RESULTS = OUT_DIR / "rule73_len8_horizon_response_results.json"
FASE80_CHECKPOINT = OUT_DIR / "rule73_len8_horizon_response_checkpoint.json"
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
FASE55_SCRIPT = OUT_DIR / "analyze_anf_gradient_census.py"
RESULTS_JSON = OUT_DIR / "rule73_h11_anf_geometry_results.json"
REPORT_MD = OUT_DIR / "rule73_h11_anf_geometry_report.md"

HORIZON = 11
SEPARATION_METRICS = (
    "signed_monomial_tv",
    "radial_monomial_tv",
)
DIAGNOSTIC_METRICS = (
    "signed_degree_tv",
    "support_jaccard",
)


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


def measurement_key(case: dict[str, Any]) -> str:
    return (
        f"r73_bg{case['background']}_T{case['T_local']}"
        f"_w{case['word']}_h{HORIZON}"
    )


def transformed_orbit_relations(left: str, right: str) -> list[dict[str, Any]]:
    complement = "".join("1" if bit == "0" else "0" for bit in left)
    seeds = {
        "rotation": left,
        "reflection_rotation": left[::-1],
        "complement_rotation": complement,
        "reflection_complement_rotation": complement[::-1],
    }
    relations = []
    for transform, seed in seeds.items():
        for shift in range(len(seed)):
            candidate = seed[shift:] + seed[:shift]
            if candidate == right:
                relations.append(
                    {
                        "transform": transform,
                        "shift": shift,
                    }
                )
    return relations


def canonical_hash(value: Any) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def load_h11_measurements(
    h11_cases: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], str]:
    if FASE80_CHECKPOINT.exists():
        checkpoint = load_json(FASE80_CHECKPOINT)["measurements"]
        return (
            {
                case["label"]: checkpoint[measurement_key(case)]
                for case in h11_cases
            },
            "reused Fase 80 checkpoint",
        )

    fase78 = load_module("fase81_rule73_len8_holdout", FASE78_SCRIPT)
    fase79 = load_module(
        "fase81_rule73_neighbor_horizons",
        FASE79_SCRIPT,
    )
    baseline = load_module(
        "fase81_periodic_bg_anf_baseline",
        BASELINE_SCRIPT,
    )
    fase78_results = load_json(FASE78_RESULTS)
    selected_cases, catalog, _witnesses = fase79.select_t12_cases(
        fase78,
        fase78_results,
    )
    selected_by_label = {case["label"]: case for case in selected_cases}
    base = baseline.load_base_module()
    popcount16 = np.array(
        [int(value).bit_count() for value in range(1 << 16)],
        dtype=np.uint8,
    )
    measurements = {}
    for index, case in enumerate(h11_cases, start=1):
        selected = selected_by_label[case["label"]]
        print(
            f"[{index}/{len(h11_cases)}] regenerating {case['label']} h=11",
            flush=True,
        )
        measurements[case["label"]] = baseline.analyze_case(
            base,
            catalog,
            popcount16,
            selected,
            HORIZON,
        )
    return measurements, "deterministic h=11 remeasurement"


def normalize(values: dict[int, float]) -> dict[int, float]:
    total = sum(values.values())
    if total <= 0:
        return {key: 0.0 for key in values}
    return {key: value / total for key, value in values.items()}


def aggregate_radial(profile: dict[int, float]) -> dict[int, float]:
    radial: dict[int, float] = {}
    for coordinate, value in profile.items():
        radial[abs(coordinate)] = radial.get(abs(coordinate), 0.0) + value
    return radial


def total_variation(
    left: dict[int, float],
    right: dict[int, float],
) -> float:
    keys = set(left) | set(right)
    return 0.5 * sum(
        abs(left.get(key, 0.0) - right.get(key, 0.0))
        for key in keys
    )


def jaccard_distance(left: set[int], right: set[int]) -> float:
    union = left | right
    if not union:
        return 0.0
    return 1.0 - (len(left & right) / len(union))


def profile_case(
    case: dict[str, Any],
    measurement: dict[str, Any],
) -> dict[str, Any]:
    active_rows = [
        row for row in measurement["outputs"] if row["concrete_active"]
    ]
    active_indices = [int(row["output_index"]) for row in active_rows]
    if not active_indices:
        raise RuntimeError(f"No active outputs for {case['label']}")
    center_x2 = min(active_indices) + max(active_indices)

    monomial_raw: dict[int, float] = {}
    degree_raw: dict[int, float] = {}
    support: set[int] = set()
    output_rows = []
    for row in active_rows:
        coordinate_x2 = 2 * int(row["output_index"]) - center_x2
        monomial_count = float(row["monomial_count"])
        degree = float(row["degree"])
        monomial_raw[coordinate_x2] = (
            monomial_raw.get(coordinate_x2, 0.0) + monomial_count
        )
        degree_raw[coordinate_x2] = (
            degree_raw.get(coordinate_x2, 0.0) + degree
        )
        support.add(coordinate_x2)
        output_rows.append(
            {
                "output_index": int(row["output_index"]),
                "coordinate_x2": coordinate_x2,
                "distance": abs(coordinate_x2) / 2.0,
                "degree": int(row["degree"]),
                "monomial_count": int(row["monomial_count"]),
            }
        )

    signed_monomial = normalize(monomial_raw)
    radial_monomial = aggregate_radial(signed_monomial)
    signed_degree = normalize(degree_raw)
    symmetry_error = sum(
        abs(
            signed_monomial.get(distance, 0.0)
            - signed_monomial.get(-distance, 0.0)
        )
        for distance in {abs(value) for value in support if value != 0}
    )
    weighted_radial_distance = sum(
        probability * abs(coordinate_x2) / 2.0
        for coordinate_x2, probability in signed_monomial.items()
    )
    max_mass = max(signed_monomial.values())
    max_monomial_coordinates = sorted(
        coordinate
        for coordinate, value in signed_monomial.items()
        if value == max_mass
    )
    return {
        "label": case["label"],
        "background": case["background"],
        "word": case["word"],
        "cohort": case["cohort"],
        "horizon": HORIZON,
        "active_output_count": len(active_rows),
        "active_span": max(active_indices) - min(active_indices) + 1,
        "center_x2": center_x2,
        "center_monomial_mass": signed_monomial.get(0, 0.0),
        "weighted_radial_distance": weighted_radial_distance,
        "symmetry_error": symmetry_error,
        "max_monomial_coordinates_x2": max_monomial_coordinates,
        "signed_monomial_profile": {
            str(key): value for key, value in sorted(signed_monomial.items())
        },
        "radial_monomial_profile": {
            str(key): value for key, value in sorted(radial_monomial.items())
        },
        "signed_degree_profile": {
            str(key): value for key, value in sorted(signed_degree.items())
        },
        "active_support_x2": sorted(support),
        "outputs": sorted(
            output_rows,
            key=lambda row: row["coordinate_x2"],
        ),
        "measurement_sha256": canonical_hash(measurement),
    }


def int_key_profile(profile: dict[str, float]) -> dict[int, float]:
    return {int(key): float(value) for key, value in profile.items()}


def pairwise_row(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    signed_left = int_key_profile(left["signed_monomial_profile"])
    signed_right = int_key_profile(right["signed_monomial_profile"])
    radial_left = int_key_profile(left["radial_monomial_profile"])
    radial_right = int_key_profile(right["radial_monomial_profile"])
    degree_left = int_key_profile(left["signed_degree_profile"])
    degree_right = int_key_profile(right["signed_degree_profile"])
    return {
        "left": left["label"],
        "right": right["label"],
        "left_cohort": left["cohort"],
        "right_cohort": right["cohort"],
        "signed_monomial_tv": total_variation(
            signed_left,
            signed_right,
        ),
        "radial_monomial_tv": total_variation(
            radial_left,
            radial_right,
        ),
        "signed_degree_tv": total_variation(
            degree_left,
            degree_right,
        ),
        "support_jaccard": jaccard_distance(
            set(left["active_support_x2"]),
            set(right["active_support_x2"]),
        ),
    }


def pair_value(
    rows: list[dict[str, Any]],
    left: str,
    right: str,
    metric: str,
) -> float:
    for row in rows:
        if {row["left"], row["right"]} == {left, right}:
            return float(row[metric])
    raise KeyError(f"Missing pair {left}, {right}")


def nearest_neighbors(
    profiles: list[dict[str, Any]],
    pairwise: list[dict[str, Any]],
    metric: str,
) -> list[dict[str, Any]]:
    by_label = {row["label"]: row for row in profiles}
    result = []
    for profile in profiles:
        candidates = [
            {
                "label": other["label"],
                "cohort": other["cohort"],
                "distance": pair_value(
                    pairwise,
                    profile["label"],
                    other["label"],
                    metric,
                ),
            }
            for other in profiles
            if other["label"] != profile["label"]
        ]
        candidates.sort(key=lambda row: (row["distance"], row["label"]))
        nearest = candidates[0]
        result.append(
            {
                "label": profile["label"],
                "cohort": profile["cohort"],
                "metric": metric,
                "nearest_label": nearest["label"],
                "nearest_cohort": by_label[nearest["label"]]["cohort"],
                "distance": nearest["distance"],
            }
        )
    return result


def control_separation_test(
    profiles: list[dict[str, Any]],
    pairwise: list[dict[str, Any]],
    metric: str,
) -> dict[str, Any]:
    controls = [
        row for row in profiles if row["cohort"] == "baseline_control"
    ]
    witnesses = [
        row for row in profiles if row["cohort"] == "baseline_witness"
    ]
    if len(controls) != 2:
        raise RuntimeError(f"Expected two controls, got {len(controls)}")
    control_distance = pair_value(
        pairwise,
        controls[0]["label"],
        controls[1]["label"],
        metric,
    )
    nearest_witness = {}
    for control in controls:
        distances = [
            {
                "label": witness["label"],
                "distance": pair_value(
                    pairwise,
                    control["label"],
                    witness["label"],
                    metric,
                ),
            }
            for witness in witnesses
        ]
        distances.sort(key=lambda row: (row["distance"], row["label"]))
        nearest_witness[control["label"]] = distances[0]
    strictly_separated = all(
        control_distance < item["distance"]
        for item in nearest_witness.values()
    )
    return {
        "metric": metric,
        "control_pair": [controls[0]["label"], controls[1]["label"]],
        "control_control_distance": control_distance,
        "nearest_witness_by_control": nearest_witness,
        "mutual_nearest_and_strictly_separated": strictly_separated,
    }


def classify(
    separation_tests: list[dict[str, Any]],
) -> tuple[str, str]:
    passed = [
        row["metric"]
        for row in separation_tests
        if row["mutual_nearest_and_strictly_separated"]
    ]
    if len(passed) == len(SEPARATION_METRICS):
        return (
            "H11_CONTROL_GEOMETRY_CLUSTER_FOUND",
            (
                "The two h=11 controls form a strictly separated mutual pair "
                "under both predeclared monomial-geometry distances."
            ),
        )
    if passed:
        return (
            "H11_CONTROL_GEOMETRY_PARTIAL",
            (
                "The two h=11 controls separate only under "
                f"{passed}, not under both predeclared geometries."
            ),
        )
    return (
        "H11_CONTROL_GEOMETRY_UNDISCRIMINATED",
        (
            "The two h=11 controls overlap the witness neighborhood under "
            "both predeclared monomial-geometry distances."
        ),
    )


def short_label(label: str) -> str:
    marker = "_bg"
    if marker not in label:
        return label
    return "bg" + label.split(marker, 1)[1].split("_T", 1)[0]


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    lines = [
        "# Fase 81: rule_73 h=11 Output-Resolved ANF Geometry",
        "",
        "## Question",
        "",
        "Are the two Fase 80 controls that cross the T15-comparability threshold",
        "at `h=11` geometrically distinct from the six baseline witnesses that are",
        "also comparable at `h=11`?",
        "",
        "This phase reuses the committed Fase 80 cohort and its deterministic h=11",
        "measurements. No threshold is fitted. Each active output is aligned to the",
        "center of the final defect and represented by normalized monomial mass,",
        "normalized degree mass, and active support.",
        "",
        "The separation test was fixed before inspecting pairwise distances. The",
        "two controls count as a geometric subtype only if they are a strictly",
        "separated mutual pair under both signed and radial monomial total-variation",
        "distance. Degree and support distances are diagnostics, not rescue criteria.",
        "",
        "The analyzer stores output-wise degree and monomial counts, not individual",
        "ANF coefficient identities. The claim is therefore about output-resolved",
        "ANF geometry, not polynomial identity.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- h=11 comparable cases: `{summary['case_count']}`",
        f"- Baseline witnesses: `{summary['witness_count']}`",
        f"- Baseline controls: `{summary['control_count']}`",
        (
            "- Separation metrics passed: "
            f"`{summary['separation_metrics_passed']}`"
        ),
        (
            "- Control-pair distances: "
            f"`{summary['control_pair_distances']}`"
        ),
        (
            "- Control raw measurements have distinct hashes: "
            f"`{summary['control_measurements_distinct']}`"
        ),
        f"- Measurement source: `{data['measurement_source']}`",
        f"- Concrete mismatches: `{summary['concrete_mismatch_count']}`",
        "",
        "## Case Geometry",
        "",
        "| cohort | background | active outputs | span | center mass | weighted radius | symmetry error | max-mass x2 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in data["profiles"]:
        lines.append(
            f"| {row['cohort']} | `{row['background']}` | "
            f"{row['active_output_count']} | {row['active_span']} | "
            f"{row['center_monomial_mass']:.6f} | "
            f"{row['weighted_radial_distance']:.6f} | "
            f"{row['symmetry_error']:.6f} | "
            f"{row['max_monomial_coordinates_x2']} |"
        )

    lines.extend(
        [
            "",
            "## Predeclared Separation Tests",
            "",
            "| metric | control-control | nearest witness from control 1 | nearest witness from control 2 | separated |",
            "| --- | ---: | --- | --- | --- |",
        ]
    )
    for test in data["separation_tests"]:
        controls = test["control_pair"]
        first = test["nearest_witness_by_control"][controls[0]]
        second = test["nearest_witness_by_control"][controls[1]]
        lines.append(
            f"| {test['metric']} | "
            f"{test['control_control_distance']:.6f} | "
            f"{short_label(first['label'])} ({first['distance']:.6f}) | "
            f"{short_label(second['label'])} ({second['distance']:.6f}) | "
            f"{str(test['mutual_nearest_and_strictly_separated']).lower()} |"
        )

    lines.extend(
        [
            "",
            "## Coarse Symmetry Audit",
            "",
            (
                "- Background orbit relations: "
                f"`{data['control_symmetry_audit']['background_relations']}`"
            ),
            (
                "- IC orbit relations: "
                f"`{data['control_symmetry_audit']['word_relations']}`"
            ),
            "",
            "The control ICs are cyclic variants, but their length-8 backgrounds",
            "are not related by rotation, reflection, complement, or reflected",
            "complement. Their identical output-resolved profiles are therefore",
            "not explained by the coarse background orbit.",
            "",
            "## Nearest Neighbors",
            "",
            "| metric | case | cohort | nearest | nearest cohort | distance |",
            "| --- | --- | --- | --- | --- | ---: |",
        ]
    )
    for row in data["nearest_neighbors"]:
        lines.append(
            f"| {row['metric']} | {short_label(row['label'])} | "
            f"{row['cohort']} | {short_label(row['nearest_label'])} | "
            f"{row['nearest_cohort']} | {row['distance']:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Pairwise Distances",
            "",
            "| left | right | cohorts | signed monomial TV | radial monomial TV | signed degree TV | support Jaccard |",
            "| --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in data["pairwise"]:
        lines.append(
            f"| {short_label(row['left'])} | {short_label(row['right'])} | "
            f"{row['left_cohort']}/{row['right_cohort']} | "
            f"{row['signed_monomial_tv']:.6f} | "
            f"{row['radial_monomial_tv']:.6f} | "
            f"{row['signed_degree_tv']:.6f} | "
            f"{row['support_jaccard']:.6f} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if data["status"] == "H11_CONTROL_GEOMETRY_CLUSTER_FOUND":
        lines.extend(
            [
                "The scalar fit equality at h=11 hides a distinct output-resolved",
                "geometry: the controls form their own compact pair under both",
                "signed and radial monomial mass.",
            ]
        )
    elif data["status"] == "H11_CONTROL_GEOMETRY_PARTIAL":
        lines.extend(
            [
                "The controls share one geometric projection but overlap witnesses",
                "in the other. Their h=11 crossing is only partially distinguishable",
                "at output-resolved ANF resolution.",
            ]
        )
    else:
        lines.extend(
            [
                "The controls do not form a separate geometric subtype. Their h=11",
                "crossing overlaps the witness neighborhood even after retaining",
                "signed and radial output structure.",
            ]
        )
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- The comparison contains six witnesses and two controls from one rule,",
            "  one local period, and one horizon.",
            "- The criterion tests a predeclared cluster relation; it does not fit a",
            "  classifier or estimate out-of-sample accuracy.",
            "- Profiles retain output-wise counts and degrees but not monomial",
            "  coefficient identities.",
            "- A positive cluster would be a hypothesis about the h=11 crossing, not",
            "  a universal ECA mechanism.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase55 = load_module("fase81_anf_gradient_census", FASE55_SCRIPT)
    fase80 = load_json(FASE80_RESULTS)
    h11_cases = []
    for case in fase80["cases"]:
        measurement = next(
            item
            for item in case["measurements"]
            if int(item["horizon"]) == HORIZON
        )
        if measurement["comparable"]:
            h11_cases.append(case)
    witness_count = sum(
        row["cohort"] == "baseline_witness" for row in h11_cases
    )
    control_count = sum(
        row["cohort"] == "baseline_control" for row in h11_cases
    )
    preflight = {
        "horizon": HORIZON,
        "case_count": len(h11_cases),
        "witness_count": witness_count,
        "control_count": control_count,
        "separation_metrics": list(SEPARATION_METRICS),
        "diagnostic_metrics": list(DIAGNOSTIC_METRICS),
        "criterion": (
            "controls must be mutual and strictly separated nearest neighbors "
            "under both signed and radial monomial TV"
        ),
        "threshold_fitting": False,
        "source": str(FASE80_RESULTS),
        "measurement_policy": (
            "reuse Fase 80 checkpoint when available; otherwise regenerate "
            "the eight h=11 measurements deterministically"
        ),
    }
    if len(h11_cases) != 8 or witness_count != 6 or control_count != 2:
        raise RuntimeError(
            "Expected 8 h=11 comparable cases split 6 witnesses / 2 controls"
        )
    if preflight_only:
        return {"preflight": preflight, "cases": h11_cases}
    measurements, measurement_source = load_h11_measurements(h11_cases)

    profiles = []
    concrete_mismatch_count = 0
    for case in h11_cases:
        measurement = measurements[case["label"]]
        fit = measurement["active_summary"]["log_monomial_fit"]
        if not fase55.comparable_to_t15(fit):
            raise RuntimeError(
                f"Measured case is not h=11 comparable: {case['label']}"
            )
        concrete_mismatch_count += int(
            not measurement["all_outputs_match_concrete"]
        )
        profiles.append(profile_case(case, measurement))

    pairwise = [
        pairwise_row(profiles[left], profiles[right])
        for left in range(len(profiles))
        for right in range(left + 1, len(profiles))
    ]
    nearest = [
        item
        for metric in (*SEPARATION_METRICS, *DIAGNOSTIC_METRICS)
        for item in nearest_neighbors(profiles, pairwise, metric)
    ]
    separation_tests = [
        control_separation_test(profiles, pairwise, metric)
        for metric in SEPARATION_METRICS
    ]
    control_profiles = [
        row for row in profiles if row["cohort"] == "baseline_control"
    ]
    control_symmetry_audit = {
        "backgrounds": [
            control_profiles[0]["background"],
            control_profiles[1]["background"],
        ],
        "words": [
            control_profiles[0]["word"],
            control_profiles[1]["word"],
        ],
        "background_relations": transformed_orbit_relations(
            control_profiles[0]["background"],
            control_profiles[1]["background"],
        ),
        "word_relations": transformed_orbit_relations(
            control_profiles[0]["word"],
            control_profiles[1]["word"],
        ),
    }
    control_pair_row = next(
        row
        for row in pairwise
        if row["left_cohort"] == "baseline_control"
        and row["right_cohort"] == "baseline_control"
    )
    status, reason = classify(separation_tests)
    summary = {
        "case_count": len(profiles),
        "witness_count": witness_count,
        "control_count": control_count,
        "pair_count": len(pairwise),
        "separation_metrics_passed": [
            row["metric"]
            for row in separation_tests
            if row["mutual_nearest_and_strictly_separated"]
        ],
        "control_pair_distances": {
            metric: control_pair_row[metric]
            for metric in (*SEPARATION_METRICS, *DIAGNOSTIC_METRICS)
        },
        "control_measurements_distinct": (
            control_profiles[0]["measurement_sha256"]
            != control_profiles[1]["measurement_sha256"]
        ),
        "concrete_mismatch_count": concrete_mismatch_count,
    }
    data = {
        "phase": 81,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "measurement_source": measurement_source,
        "profiles": profiles,
        "control_symmetry_audit": control_symmetry_audit,
        "separation_tests": separation_tests,
        "nearest_neighbors": nearest,
        "pairwise": pairwise,
    }
    RESULTS_JSON.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(data)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    data = run(preflight_only=args.preflight_only)
    if args.preflight_only:
        print(json.dumps(data["preflight"], indent=2, sort_keys=True))
        return
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['status']}")


if __name__ == "__main__":
    main()
