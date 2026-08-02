#!/usr/bin/env python3
"""Fase 82: exact recurrence audit of the rule_73 h=11 control geometry."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
FASE78_SCRIPT = OUT_DIR / "analyze_rule73_len8_holdout.py"
FASE78_RESULTS = OUT_DIR / "rule73_len8_holdout_results.json"
FASE79_SCRIPT = OUT_DIR / "analyze_rule73_len8_neighbor_horizons.py"
FASE79_CHECKPOINT = OUT_DIR / "rule73_len8_neighbor_horizons_checkpoint.json"
FASE80_RESULTS = OUT_DIR / "rule73_len8_horizon_response_results.json"
FASE80_CHECKPOINT = OUT_DIR / "rule73_len8_horizon_response_checkpoint.json"
FASE81_SCRIPT = OUT_DIR / "analyze_rule73_h11_anf_geometry.py"
BASELINE_SCRIPT = OUT_DIR / "analyze_periodic_bg_anf_baseline.py"
RESULTS_JSON = OUT_DIR / "rule73_control_signature_grid_results.json"
REPORT_MD = OUT_DIR / "rule73_control_signature_grid_report.md"

FULL_GRID_HORIZONS = tuple(range(8, 17))
EXPECTED_COMPARABLE_BY_HORIZON = {10: 1, 11: 8, 12: 9, 13: 5, 14: 2}
REFERENCE_BACKGROUNDS = ("00111011", "00111101")
REFERENCE_HORIZON = 11
DISTANCE_METRICS = (
    "signed_monomial_tv",
    "radial_monomial_tv",
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


def event_id(event: dict[str, Any]) -> str:
    return f"{event['label']}_h{event['horizon']}"


def measurement_key(event: dict[str, Any]) -> str:
    return (
        f"r73_bg{event['background']}_T{event['T_local']}"
        f"_w{event['word']}_h{event['horizon']}"
    )


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def collect_comparable_events(fase80: dict[str, Any]) -> list[dict[str, Any]]:
    events = []
    for case in fase80["cases"]:
        for measurement in case["measurements"]:
            if not measurement["comparable"]:
                continue
            horizon = int(measurement["horizon"])
            events.append(
                {
                    "label": case["label"],
                    "background": case["background"],
                    "word": case["word"],
                    "T_local": int(case["T_local"]),
                    "cohort": case["cohort"],
                    "horizon": horizon,
                }
            )
    events.sort(key=lambda row: (row["horizon"], row["label"]))
    counts = Counter(event["horizon"] for event in events)
    if len(events) != 25 or dict(sorted(counts.items())) != EXPECTED_COMPARABLE_BY_HORIZON:
        raise RuntimeError(
            "Expected 25 comparable events distributed over h10..h14 as "
            f"{EXPECTED_COMPARABLE_BY_HORIZON}, got {len(events)} and {dict(counts)}"
        )
    return events


def load_raw_measurements(
    events: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    fase78_results = load_json(FASE78_RESULTS)
    fase78_by_label = {
        str(row["label"]): row for row in fase78_results["cases"]
    }
    fase79_checkpoint = (
        load_json(FASE79_CHECKPOINT)["measurements"]
        if FASE79_CHECKPOINT.exists()
        else {}
    )
    fase80_checkpoint = (
        load_json(FASE80_CHECKPOINT)["measurements"]
        if FASE80_CHECKPOINT.exists()
        else {}
    )
    measurements: dict[str, dict[str, Any]] = {}
    sources: dict[str, str] = {}
    missing = []
    for event in events:
        identifier = event_id(event)
        key = measurement_key(event)
        horizon = event["horizon"]
        if horizon == 12 and event["label"] in fase78_by_label:
            measurements[identifier] = fase78_by_label[event["label"]]
            sources[identifier] = "committed Fase 78 result"
        elif horizon in (10, 14) and key in fase79_checkpoint:
            measurements[identifier] = fase79_checkpoint[key]
            sources[identifier] = "local Fase 79 checkpoint"
        elif horizon in (11, 13) and key in fase80_checkpoint:
            measurements[identifier] = fase80_checkpoint[key]
            sources[identifier] = "local Fase 80 checkpoint"
        else:
            missing.append(event)

    if not missing:
        return measurements, sources

    fase78 = load_module("fase82_rule73_len8_holdout", FASE78_SCRIPT)
    fase79 = load_module(
        "fase82_rule73_neighbor_horizons",
        FASE79_SCRIPT,
    )
    baseline = load_module(
        "fase82_periodic_bg_anf_baseline",
        BASELINE_SCRIPT,
    )
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
    for index, event in enumerate(missing, start=1):
        identifier = event_id(event)
        selected = selected_by_label[event["label"]]
        print(
            f"[{index}/{len(missing)}] regenerating {identifier}",
            flush=True,
        )
        measurements[identifier] = baseline.analyze_case(
            base,
            catalog,
            popcount16,
            selected,
            event["horizon"],
        )
        sources[identifier] = "deterministic remeasurement"
    return measurements, sources


def exact_geometry_signature(
    measurement: dict[str, Any],
) -> tuple[tuple[Any, ...], ...]:
    active_rows = [
        row for row in measurement["outputs"] if row["concrete_active"]
    ]
    active_indices = [int(row["output_index"]) for row in active_rows]
    if not active_indices:
        raise RuntimeError(f"No active outputs in {measurement['label']}")
    center_x2 = min(active_indices) + max(active_indices)
    signature = []
    for row in active_rows:
        degree_histogram = tuple(
            sorted(
                (int(degree), int(count))
                for degree, count in row["degree_histogram"].items()
            )
        )
        signature.append(
            (
                2 * int(row["output_index"]) - center_x2,
                int(row["degree"]),
                int(row["monomial_count"]),
                degree_histogram,
            )
        )
    return tuple(sorted(signature, key=lambda item: item[0]))


def reflected_signature(
    signature: tuple[tuple[Any, ...], ...],
) -> tuple[tuple[Any, ...], ...]:
    reflected = [
        (-item[0], item[1], item[2], item[3]) for item in signature
    ]
    return tuple(sorted(reflected, key=lambda item: item[0]))


def reflection_canonical_signature(
    signature: tuple[tuple[Any, ...], ...],
) -> tuple[tuple[Any, ...], ...]:
    reflected = reflected_signature(signature)
    return min(signature, reflected)


def classify(
    reference_ids: set[str],
    oriented_matches: list[dict[str, Any]],
    reflection_matches: list[dict[str, Any]],
) -> tuple[str, str]:
    outside_reflection = [
        row for row in reflection_matches if row["event_id"] not in reference_ids
    ]
    outside_oriented = [
        row for row in oriented_matches if row["event_id"] not in reference_ids
    ]
    witness_matches = [
        row for row in outside_reflection if row["cohort"] == "baseline_witness"
    ]
    if witness_matches:
        return (
            "CONTROL_SIGNATURE_RECURS_IN_WITNESSES",
            (
                "The h=11 control geometry recurs in at least one baseline "
                "witness under oriented or reflection-canonical exact matching."
            ),
        )
    if outside_reflection:
        return (
            "CONTROL_SIGNATURE_RECURS_CONTROL_ONLY",
            (
                "The h=11 control geometry recurs outside the reference pair, "
                "but only in baseline-control events."
            ),
        )
    if outside_oriented:
        raise RuntimeError("Oriented matches must also be reflection matches")
    return (
        "CONTROL_SIGNATURE_UNIQUE_TO_H11_PAIR",
        (
            "The exact h=11 control geometry occurs only in the two reference "
            "controls across all 25 comparable events."
        ),
    )


def short_event(identifier: str) -> str:
    return identifier.replace("rule73_", "")


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    lines = [
        "# Fase 82: rule_73 Control-Signature Recurrence Grid",
        "",
        "## Question",
        "",
        "Does the exact output-resolved ANF geometry shared by the two h=11",
        "control crossings from Fase 81 recur among any of the 25 comparable",
        "measurements in the complete Fase 80 horizon grid?",
        "",
        "The Fase 80 grid covers horizons h=8..16. Comparable measurements occur",
        "only at h=10..14, with counts 1, 8, 9, 5, and 2 respectively. Fase 82",
        "therefore audits 25 comparable events, not every measured grid point.",
        "",
        "## Signature Definition",
        "",
        "Each active output is centered by translation and represented exactly as:",
        "",
        "`(coordinate_x2, degree, monomial_count, complete degree_histogram)`",
        "",
        "The oriented signature is the sorted tuple of these output records. The",
        "reflection-canonical signature is the lexicographically smaller of the",
        "oriented signature and its coordinate-reflected copy. SHA-256 hashes are",
        "deterministic content identifiers only; no cryptographic or post-quantum",
        "security claim is made.",
        "",
        "These signatures do not establish exact ANF polynomial identity because",
        "the analyzer does not retain individual monomial coefficient identities.",
        "",
        "Approximate distances from Fase 81 are reported separately and never used",
        "to rescue an exact non-match.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Comparable events: `{summary['event_count']}`",
        f"- Distinct physical cases: `{summary['distinct_case_count']}`",
        f"- Comparable horizon counts: `{summary['comparable_by_horizon']}`",
        f"- Measurement sources: `{summary['measurement_source_counts']}`",
        f"- Oriented exact matches: `{summary['oriented_match_count']}`",
        f"- Reflection-canonical exact matches: `{summary['reflection_match_count']}`",
        f"- Oriented matches outside reference pair: `{summary['oriented_outside_count']}`",
        f"- Reflection matches outside reference pair: `{summary['reflection_outside_count']}`",
        f"- Concrete mismatches: `{summary['concrete_mismatch_count']}`",
        "",
        "## Reference Signature",
        "",
        f"- Reference events: `{data['reference']['event_ids']}`",
        f"- Oriented SHA-256: `{data['reference']['oriented_sha256']}`",
        f"- Reflection-canonical SHA-256: `{data['reference']['reflection_sha256']}`",
        f"- Reference raw measurements distinct: `{data['reference']['raw_measurements_distinct']}`",
        "",
        "## Exact Oriented Matches",
        "",
        "| event | cohort | horizon | background | IC |",
        "| --- | --- | ---: | --- | --- |",
    ]
    for row in data["oriented_matches"]:
        lines.append(
            f"| {short_event(row['event_id'])} | {row['cohort']} | "
            f"{row['horizon']} | `{row['background']}` | `{row['word']}` |"
        )
    lines.extend(
        [
            "",
            "## Exact Matches Under Reflection",
            "",
            "| event | cohort | horizon | oriented match |",
            "| --- | --- | ---: | --- |",
        ]
    )
    for row in data["reflection_matches"]:
        lines.append(
            f"| {short_event(row['event_id'])} | {row['cohort']} | "
            f"{row['horizon']} | {str(row['oriented_match']).lower()} |"
        )

    lines.extend(
        [
            "",
            "## Approximate Neighbors",
            "",
            "Exact reference members are excluded from these rankings.",
            "",
        ]
    )
    for metric in DISTANCE_METRICS:
        lines.extend(
            [
                f"### {metric}",
                "",
                "| rank | event | cohort | horizon | distance |",
                "| ---: | --- | --- | ---: | ---: |",
            ]
        )
        for rank, row in enumerate(data["approximate_neighbors"][metric], start=1):
            lines.append(
                f"| {rank} | {short_event(row['event_id'])} | "
                f"{row['cohort']} | {row['horizon']} | {row[metric]:.6f} |"
            )
        lines.append("")

    lines.extend(
        [
            "## Complete Comparable Grid",
            "",
            "| event | cohort | source | oriented | reflection | signed TV | radial TV | degree TV | support Jaccard |",
            "| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in data["events"]:
        lines.append(
            f"| {short_event(row['event_id'])} | {row['cohort']} | "
            f"{row['measurement_source']} | "
            f"{str(row['oriented_match']).lower()} | "
            f"{str(row['reflection_match']).lower()} | "
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
    if data["status"] == "CONTROL_SIGNATURE_UNIQUE_TO_H11_PAIR":
        lines.extend(
            [
                "The two Fase 81 controls define a unique exact geometry within",
                "the 25-event comparable grid. Neither translation-oriented nor",
                "reflection-canonical matching finds the signature in a witness or",
                "at another horizon.",
            ]
        )
    elif data["status"] == "CONTROL_SIGNATURE_RECURS_CONTROL_ONLY":
        lines.extend(
            [
                "The geometry recurs, but only among baseline-control events. This",
                "supports a control-associated subtype without making it universal.",
            ]
        )
    else:
        lines.extend(
            [
                "The geometry also occurs in a baseline witness, so exact",
                "output-resolved geometry does not preserve the control subtype.",
            ]
        )
    lines.extend(
        [
            "",
            "## Methodological Limits",
            "",
            "- The grid starts from 18 physical rule_73/T=12 cases. The 25",
            "  comparable events come from 11 of them; repeated horizons are",
            "  not independent oscillators.",
            "- Comparable support is limited to h=10..14 even though the measured",
            "  grid spans h=8..16.",
            "- Exact geometry retains per-output counts and degree histograms, not",
            "  individual ANF monomial identities.",
            "- Approximate rankings are descriptive and have no fitted cutoff.",
            "- The exact signature is high-dimensional; uniqueness in 25 events",
            "  does not estimate out-of-sample discrimination by itself.",
            "- The result remains local to rule_73 and primitive length-8",
            "  backgrounds.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase80 = load_json(FASE80_RESULTS)
    events = collect_comparable_events(fase80)
    preflight = {
        "full_grid_horizons": list(FULL_GRID_HORIZONS),
        "comparable_horizons": sorted(EXPECTED_COMPARABLE_BY_HORIZON),
        "comparable_by_horizon": {
            str(key): value for key, value in EXPECTED_COMPARABLE_BY_HORIZON.items()
        },
        "event_count": len(events),
        "reference_backgrounds": list(REFERENCE_BACKGROUNDS),
        "reference_horizon": REFERENCE_HORIZON,
        "oriented_identity": (
            "exact centered tuple of coordinate_x2, degree, monomial_count, "
            "and complete degree_histogram"
        ),
        "reflection_identity": "lexicographic canonicalization with x -> -x",
        "approximate_metrics": list(DISTANCE_METRICS),
        "threshold_fitting": False,
        "polynomial_identity_claim": False,
        "checkpoint_policy": (
            "reuse local checkpoints when available; deterministically "
            "regenerate missing measurements"
        ),
    }
    if preflight_only:
        return {"preflight": preflight, "events": events}

    fase81 = load_module("fase82_h11_anf_geometry", FASE81_SCRIPT)
    measurements, sources = load_raw_measurements(events)
    rows = []
    for event in events:
        identifier = event_id(event)
        measurement = measurements[identifier]
        if not measurement["all_outputs_match_concrete"]:
            raise RuntimeError(f"Concrete mismatch in {identifier}")
        signature = exact_geometry_signature(measurement)
        reflection_signature = reflection_canonical_signature(signature)
        case_for_profile = dict(event)
        case_for_profile["label"] = identifier
        profile = fase81.profile_case(case_for_profile, measurement)
        rows.append(
            {
                **event,
                "event_id": identifier,
                "measurement_source": sources[identifier],
                "measurement_sha256": sha256_json(measurement),
                "oriented_signature": signature,
                "oriented_sha256": sha256_json(signature),
                "reflection_canonical_signature": reflection_signature,
                "reflection_sha256": sha256_json(reflection_signature),
                "profile": profile,
            }
        )

    references = [
        row
        for row in rows
        if row["horizon"] == REFERENCE_HORIZON
        and row["background"] in REFERENCE_BACKGROUNDS
    ]
    if len(references) != 2:
        raise RuntimeError(f"Expected two h=11 references, got {len(references)}")
    if references[0]["oriented_sha256"] != references[1]["oriented_sha256"]:
        raise RuntimeError("Fase 81 controls no longer share oriented signature")
    if references[0]["reflection_sha256"] != references[1]["reflection_sha256"]:
        raise RuntimeError("Fase 81 controls no longer share reflected signature")
    reference_ids = {row["event_id"] for row in references}
    reference_profile = references[0]["profile"]
    reference_oriented = references[0]["oriented_sha256"]
    reference_reflection = references[0]["reflection_sha256"]

    public_rows = []
    for row in rows:
        distances = fase81.pairwise_row(reference_profile, row["profile"])
        public_rows.append(
            {
                "event_id": row["event_id"],
                "label": row["label"],
                "background": row["background"],
                "word": row["word"],
                "T_local": row["T_local"],
                "cohort": row["cohort"],
                "horizon": row["horizon"],
                "measurement_source": row["measurement_source"],
                "measurement_sha256": row["measurement_sha256"],
                "oriented_sha256": row["oriented_sha256"],
                "reflection_sha256": row["reflection_sha256"],
                "oriented_match": row["oriented_sha256"] == reference_oriented,
                "reflection_match": row["reflection_sha256"] == reference_reflection,
                **{metric: distances[metric] for metric in DISTANCE_METRICS},
            }
        )

    oriented_matches = [row for row in public_rows if row["oriented_match"]]
    reflection_matches = [row for row in public_rows if row["reflection_match"]]
    status, reason = classify(
        reference_ids,
        oriented_matches,
        reflection_matches,
    )
    approximate_neighbors = {}
    for metric in DISTANCE_METRICS:
        candidates = [
            row for row in public_rows if row["event_id"] not in reference_ids
        ]
        candidates.sort(key=lambda row: (row[metric], row["event_id"]))
        approximate_neighbors[metric] = candidates[:5]

    source_counts = Counter(row["measurement_source"] for row in public_rows)
    comparable_counts = Counter(row["horizon"] for row in public_rows)
    oriented_outside = [
        row for row in oriented_matches if row["event_id"] not in reference_ids
    ]
    reflection_outside = [
        row for row in reflection_matches if row["event_id"] not in reference_ids
    ]
    summary = {
        "event_count": len(public_rows),
        "distinct_case_count": len({row["label"] for row in public_rows}),
        "comparable_by_horizon": {
            str(key): comparable_counts[key] for key in sorted(comparable_counts)
        },
        "measurement_source_counts": dict(sorted(source_counts.items())),
        "oriented_match_count": len(oriented_matches),
        "reflection_match_count": len(reflection_matches),
        "oriented_outside_count": len(oriented_outside),
        "reflection_outside_count": len(reflection_outside),
        "concrete_mismatch_count": 0,
    }
    data = {
        "phase": 82,
        "status": status,
        "verdict_reason": reason,
        "preflight": preflight,
        "summary": summary,
        "reference": {
            "event_ids": sorted(reference_ids),
            "oriented_sha256": reference_oriented,
            "reflection_sha256": reference_reflection,
            "raw_measurements_distinct": (
                references[0]["measurement_sha256"]
                != references[1]["measurement_sha256"]
            ),
        },
        "oriented_matches": oriented_matches,
        "reflection_matches": reflection_matches,
        "approximate_neighbors": approximate_neighbors,
        "events": public_rows,
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
