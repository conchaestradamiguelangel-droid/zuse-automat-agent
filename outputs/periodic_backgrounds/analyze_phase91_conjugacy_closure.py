#!/usr/bin/env python3
"""Fase 92: complete the exact rule_73/rule_109 black-white conjugacy audit."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parent.parent
PHASE91_SCRIPT = OUT_DIR / "analyze_phase90_long_period_attractors.py"
PHASE91_RESULTS = OUT_DIR / "phase90_long_period_attractor_results.json"
RUNNER_PATH = OUT_DIR / "run_phase90_global_period_resweep.py"
BASE_PATH = OUT_DIR / "sweep_periodic_background_oscillators.py"
LEN8_PATH = ROOT / "outputs" / "periodic_backgrounds_len8" / "sweep_len8_periodic_oscillators.py"
RESULTS_PATH = OUT_DIR / "phase91_conjugacy_closure_results.json"
REPORT_PATH = OUT_DIR / "phase91_conjugacy_closure_report.md"

EXPECTED_CASES = 3296
WIDTH = 256
BURN_IN = 80
LONG_STEPS = 1000
TAIL_START = 500
TAIL_END = 1000
MAX_PERIOD = 120
MAX_SPAN = 32


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def conjugate_rule(rule: int) -> int:
    result = 0
    for neighborhood in range(8):
        output = 1 - ((int(rule) >> (7 - neighborhood)) & 1)
        result |= output << neighborhood
    return result


def complement_word(word: str) -> str:
    if not word or any(bit not in "01" for bit in word):
        raise ValueError(f"Not a binary word: {word!r}")
    return "".join("1" if bit == "0" else "0" for bit in word)


def complement_state(state: tuple[int, ...]) -> tuple[int, ...]:
    active = set(state)
    return tuple(position for position in range(WIDTH) if position not in active)


def phase91_input_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["cohort"],
        int(row["rule"]),
        int(row["background_index"]),
        int(row["ic_index"]),
        int(row["word_len"]),
        row["word"],
    )


def trajectory_digest_update(digest, timestamp: int, diff: tuple[int, ...]) -> None:
    digest.update(int(timestamp).to_bytes(2, "little", signed=False))
    digest.update(len(diff).to_bytes(2, "little", signed=False))
    for position in diff:
        digest.update(int(position).to_bytes(2, "little", signed=False))


def coverage_status(
    *, background_present: bool, ic_present: bool, partner_present: bool
) -> tuple[str, str]:
    if background_present and ic_present:
        if not partner_present:
            raise RuntimeError("Represented conjugate input is missing from Fase 91")
        return "PARTNER_PRESENT", "OBSERVED_CATALOG_PAIR"
    if not background_present and not ic_present:
        return (
            "BACKGROUND_PHASE_AND_ZERO_IC_OMITTED",
            "CONSTRUCTED_PHASE_PLUS_ZERO_IC",
        )
    if not background_present:
        return "BACKGROUND_PHASE_OMITTED", "CONSTRUCTED_PHASE_COMPLEMENT"
    return "ZERO_IC_OMITTED", "CONSTRUCTED_ZERO_IC"


def build_background_frames(base, rule: int, background: str) -> list[tuple[int, ...]]:
    frames = [base.background_state(background)]
    for _ in range(LONG_STEPS):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def verify_background_conjugacy(
    original: list[tuple[int, ...]], transformed: list[tuple[int, ...]]
) -> None:
    if len(original) != len(transformed):
        raise RuntimeError("Background trajectory lengths differ")
    for timestamp, (left, right) in enumerate(zip(original, transformed)):
        if complement_state(left) != right:
            raise RuntimeError(f"Background conjugacy mismatch at t={timestamp}")


def simulate_conjugate_pair(
    *,
    base,
    runner,
    original_rule: int,
    original_background_frames: list[tuple[int, ...]],
    transformed_rule: int,
    transformed_background_frames: list[tuple[int, ...]],
    original_word: str,
    transformed_word: str,
) -> dict[str, Any]:
    word_len = len(original_word)
    if len(transformed_word) != word_len:
        raise ValueError("Conjugate IC must preserve word length")
    left = base.initial_diff(
        int(original_word, 2), word_len, original_background_frames[0]
    )
    right = base.initial_diff(
        int(transformed_word, 2), word_len, transformed_background_frames[0]
    )
    left_shapes = []
    right_shapes = []
    digest = hashlib.sha256()
    for timestamp in range(LONG_STEPS + 1):
        if left != right:
            raise RuntimeError(f"Defect conjugacy mismatch at t={timestamp}")
        trajectory_digest_update(digest, timestamp, left)
        if timestamp >= BURN_IN:
            left_shape = base.linear_shape(left)
            right_shape = base.linear_shape(right)
            if left_shape is None or right_shape is None:
                raise RuntimeError(f"Conjugate defect unavailable at t={timestamp}")
            if int(left_shape.span) > MAX_SPAN or int(right_shape.span) > MAX_SPAN:
                raise RuntimeError(f"Conjugate defect escaped max span at t={timestamp}")
            if left_shape != right_shape:
                raise RuntimeError(f"Conjugate shape mismatch at t={timestamp}")
            left_shapes.append(left_shape)
            right_shapes.append(right_shape)
        if timestamp < LONG_STEPS:
            left = base.eca_step_diff(
                left,
                original_background_frames[timestamp],
                original_background_frames[timestamp + 1],
                original_rule,
            )
            right = base.eca_step_diff(
                right,
                transformed_background_frames[timestamp],
                transformed_background_frames[timestamp + 1],
                transformed_rule,
            )
    left_tail = left_shapes[TAIL_START - BURN_IN : TAIL_END - BURN_IN + 1]
    right_tail = right_shapes[TAIL_START - BURN_IN : TAIL_END - BURN_IN + 1]
    left_dynamics = runner.exact_dynamics(left_tail, MAX_PERIOD)
    right_dynamics = runner.exact_dynamics(right_tail, MAX_PERIOD)
    if left_dynamics != right_dynamics:
        raise RuntimeError(
            f"Conjugate tail dynamics differ: {left_dynamics} != {right_dynamics}"
        )
    return {
        "original_shapes": left_shapes,
        "transformed_shapes": right_shapes,
        "dynamics": left_dynamics,
        "defect_trajectory_sha256": digest.hexdigest(),
    }


def attractor_hashes(
    *,
    phase91,
    rule: int,
    background_frames: list[tuple[int, ...]],
    shapes: list[Any],
    defect_period: int,
    background_period: int,
    kind: str,
    drift: int,
) -> tuple[str, str]:
    joint_period = __import__("math").lcm(defect_period, background_period)
    start_time = TAIL_END - joint_period + 1
    bits = [phase91.state_bits(frame) for frame in background_frames]
    joint_frames = []
    for timestamp in range(start_time, TAIL_END + 1):
        shape = shapes[timestamp - BURN_IN]
        joint_frames.append(
            (
                phase91.relative_background_hex(bits[timestamp], int(shape.min_pos)),
                tuple(int(value) for value in shape.offsets),
            )
        )
    strict_payload = phase91.joint_cycle_payload(
        rule=rule,
        kind=kind,
        drift=drift,
        defect_period=defect_period,
        background_period=background_period,
        joint_frames=joint_frames,
    )
    conjugacy_payload = phase91.joint_cycle_payload(
        rule=rule,
        kind=kind,
        drift=drift,
        defect_period=defect_period,
        background_period=background_period,
        joint_frames=joint_frames,
        conjugacy_quotient=True,
    )
    return phase91.sha256_json(strict_payload), phase91.sha256_json(conjugacy_payload)


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    with temporary.open("r+b") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def distribution(values) -> dict[str, int]:
    return {
        str(key): value
        for key, value in sorted(Counter(values).items(), key=lambda item: str(item[0]))
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 92 - Exact rule_73/rule_109 conjugacy closure",
        "",
        "## Question",
        "",
        "Are the rule-specific classes in the Fase-91 atlas genuine dynamical asymmetries, or occupancy gaps caused by canonical background-phase sampling and exclusion of the zero IC?",
        "",
        "## Predeclared protocol",
        "",
        "- Input: exactly the 3,296 versioned Fase-91 cases.",
        "- Transform: rule_73 <-> rule_109, bitwise-complemented background with the exact original phase, and bitwise-complemented IC with the same length.",
        "- Zero IC is allowed only in the diagnostic constructed stratum.",
        "- Coverage metadata never controls simulation or the abort gate.",
        "- Physical gate: background complementarity and defect equality at every t=0..1000, equal kind/period/drift, and equal conjugacy-class hash.",
        "- A single physical mismatch aborts before results are published.",
        "",
        "## Physical closure",
        "",
        f"- Source cases: {summary['source_case_count']}",
        f"- Exact trajectory matches: {summary['exact_trajectory_match_count']}",
        f"- Physical mismatches: {summary['physical_mismatch_count']}",
        f"- Fase-91 conjugacy classes: {summary['source_conjugacy_class_count']}",
        f"- Classes spanning both rules after constructed closure: {summary['closed_conjugacy_class_count']}",
        f"- Classes still rule-specific after closure: {summary['unclosed_conjugacy_class_count']}",
        "",
        "## Evidence strata",
        "",
        "| stratum | input rows | role |",
        "|---|---:|---|",
        f"| OBSERVED_CATALOG_PAIR | {summary['evidence_stratum_counts'].get('OBSERVED_CATALOG_PAIR', 0)} | Direct counterpart already present in the frozen catalog |",
        f"| CONSTRUCTED_PHASE_COMPLEMENT | {summary['evidence_stratum_counts'].get('CONSTRUCTED_PHASE_COMPLEMENT', 0)} | Exact deterministic complement absent only because one canonical background phase was sampled |",
        f"| CONSTRUCTED_PHASE_PLUS_ZERO_IC | {summary['evidence_stratum_counts'].get('CONSTRUCTED_PHASE_PLUS_ZERO_IC', 0)} | Diagnostic exact complement absent by both phase sampling and zero-IC exclusion |",
        f"| CONSTRUCTED_ZERO_IC | {summary['evidence_stratum_counts'].get('CONSTRUCTED_ZERO_IC', 0)} | Diagnostic zero-IC complement with represented background phase |",
        "",
        f"- Distinct observed catalog pair orbits: {summary['observed_catalog_pair_orbit_count']}",
        f"- Rows excluded from real catalog-coverage claims because the conjugate IC is zero: {summary['zero_ic_diagnostic_count']}",
        "",
        "## Coverage status",
        "",
        f"`{json.dumps(summary['coverage_status_counts'], sort_keys=True)}`",
        "",
        "## Verdict",
        "",
        f"`{payload['status']}`",
        "",
        "All constructed comparisons are deterministic symmetry validations. Only the observed catalog-pair stratum measures direct frozen-catalog coverage; constructed rows are not independent statistical observations.",
        "",
        "## Methodological limits",
        "",
        "- Only 160/3,296 input rows have their exact conjugate already present in the frozen catalog; these form 80 bidirectional pair orbits.",
        "- The remaining comparisons complete a known exact ECA symmetry and quantify sampling occupancy. They do not add independent statistical power or establish behavior outside the two frozen cohorts.",
        "- The 40 zero-IC complements are reported separately and excluded from direct catalog-coverage claims.",
        "- No ANF-gradient measurement is performed.",
        "- No paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.",
        "",
    ]
    return "\n".join(lines)


def run() -> dict[str, Any]:
    phase91 = load_module("fase92_phase91", PHASE91_SCRIPT)
    runner = load_module("fase92_phase90_runner", RUNNER_PATH)
    base = load_module("fase92_base", BASE_PATH)
    len8 = load_module("fase92_len8", LEN8_PATH)
    source_payload = json.loads(PHASE91_RESULTS.read_text(encoding="utf-8"))
    source_rows = source_payload["cases"]
    if len(source_rows) != EXPECTED_CASES:
        raise RuntimeError(f"Expected {EXPECTED_CASES} Fase-91 cases")
    source_keys = {phase91_input_key(row): row for row in source_rows}
    if len(source_keys) != EXPECTED_CASES:
        raise RuntimeError("Fase-91 source keys are not unique")

    words = list(base.ic_words())
    word_index = {(int(length), word): index for index, (length, _, word) in enumerate(words)}
    backgrounds = {
        "baseline_period_1_2_4": list(base.background_words()),
        "primitive_len8": list(len8.primitive_len8_backgrounds()),
    }
    background_index = {
        cohort: {word: index for index, word in enumerate(values)}
        for cohort, values in backgrounds.items()
    }
    background_cache: dict[tuple[int, str], list[tuple[int, ...]]] = {}
    verified_background_pairs: set[tuple[tuple[int, str], tuple[int, str]]] = set()

    def get_background(rule: int, word: str) -> list[tuple[int, ...]]:
        key = (rule, word)
        if key not in background_cache:
            background_cache[key] = build_background_frames(base, rule, word)
        return background_cache[key]

    rows = []
    augmented_rules: dict[str, set[int]] = defaultdict(set)
    observed_pair_ids = set()
    for source in source_rows:
        rule = int(source["rule"])
        transformed_rule = conjugate_rule(rule)
        if {rule, transformed_rule} != {73, 109}:
            raise RuntimeError(f"Unexpected conjugate rule pair: {rule}/{transformed_rule}")
        transformed_background = complement_word(source["background"])
        transformed_word = complement_word(source["word"])
        bg_index = background_index[source["cohort"]].get(transformed_background)
        ic_index = word_index.get((int(source["word_len"]), transformed_word))
        background_present = bg_index is not None
        ic_present = ic_index is not None
        partner_key = None
        partner_present = False
        if background_present and ic_present:
            partner_key = (
                source["cohort"],
                transformed_rule,
                bg_index,
                ic_index,
                int(source["word_len"]),
                transformed_word,
            )
            partner_present = partner_key in source_keys
        status, stratum = coverage_status(
            background_present=background_present,
            ic_present=ic_present,
            partner_present=partner_present,
        )
        if partner_present:
            observed_pair_ids.add(tuple(sorted((phase91_input_key(source), partner_key))))

        original_frames = get_background(rule, source["background"])
        transformed_frames = get_background(transformed_rule, transformed_background)
        background_pair = tuple(
            sorted(
                (
                    (rule, source["background"]),
                    (transformed_rule, transformed_background),
                )
            )
        )
        if background_pair not in verified_background_pairs:
            verify_background_conjugacy(original_frames, transformed_frames)
            verified_background_pairs.add(background_pair)
        simulation = simulate_conjugate_pair(
            base=base,
            runner=runner,
            original_rule=rule,
            original_background_frames=original_frames,
            transformed_rule=transformed_rule,
            transformed_background_frames=transformed_frames,
            original_word=source["word"],
            transformed_word=transformed_word,
        )
        dynamics = simulation["dynamics"]
        observed_dynamics = (
            dynamics["kind"],
            int(dynamics["period"]),
            int(dynamics["drift"]),
        )
        expected_dynamics = (
            source["kind"],
            int(source["defect_period"]),
            0,
        )
        if observed_dynamics != expected_dynamics:
            raise RuntimeError(
                f"Fase-91 dynamics mismatch for {phase91_input_key(source)}: "
                f"{observed_dynamics} != {expected_dynamics}"
            )
        background_period = int(source["background_period"])
        original_strict, original_conjugacy = attractor_hashes(
            phase91=phase91,
            rule=rule,
            background_frames=original_frames,
            shapes=simulation["original_shapes"],
            defect_period=int(dynamics["period"]),
            background_period=background_period,
            kind=dynamics["kind"],
            drift=int(dynamics["drift"]),
        )
        transformed_strict, transformed_conjugacy = attractor_hashes(
            phase91=phase91,
            rule=transformed_rule,
            background_frames=transformed_frames,
            shapes=simulation["transformed_shapes"],
            defect_period=int(dynamics["period"]),
            background_period=background_period,
            kind=dynamics["kind"],
            drift=int(dynamics["drift"]),
        )
        expected_conjugacy = source["conjugacy_class_sha256"]
        if original_strict != source["physical_class_sha256"]:
            raise RuntimeError("Original strict class no longer matches Fase 91")
        if not (
            original_conjugacy == transformed_conjugacy == expected_conjugacy
        ):
            raise RuntimeError("Conjugacy-class hash mismatch")

        augmented_rules[expected_conjugacy].update((rule, transformed_rule))
        rows.append(
            {
                "cohort": source["cohort"],
                "rule": rule,
                "background": source["background"],
                "word": source["word"],
                "transformed_rule": transformed_rule,
                "transformed_background": transformed_background,
                "transformed_word": transformed_word,
                "transformed_ic_is_zero": not ic_present,
                "coverage_status": status,
                "evidence_stratum": stratum,
                "partner_present_in_frozen_catalog": partner_present,
                "defect_period": int(dynamics["period"]),
                "background_period": background_period,
                "defect_trajectory_sha256": simulation["defect_trajectory_sha256"],
                "source_physical_class_sha256": original_strict,
                "transformed_physical_class_sha256": transformed_strict,
                "conjugacy_class_sha256": expected_conjugacy,
                "exact_background_complement": True,
                "exact_defect_trajectory_match": True,
                "exact_dynamics_match": True,
                "exact_conjugacy_hash_match": True,
            }
        )

    source_class_count = len({row["conjugacy_class_sha256"] for row in source_rows})
    closed = sum(rules == {73, 109} for rules in augmented_rules.values())
    summary = {
        "source_case_count": len(source_rows),
        "exact_trajectory_match_count": len(rows),
        "physical_mismatch_count": 0,
        "source_conjugacy_class_count": source_class_count,
        "closed_conjugacy_class_count": closed,
        "unclosed_conjugacy_class_count": source_class_count - closed,
        "coverage_status_counts": distribution(row["coverage_status"] for row in rows),
        "evidence_stratum_counts": distribution(row["evidence_stratum"] for row in rows),
        "observed_catalog_pair_orbit_count": len(observed_pair_ids),
        "zero_ic_diagnostic_count": sum(row["transformed_ic_is_zero"] for row in rows),
        "background_trajectory_count": len(background_cache),
        "defect_period_distribution": distribution(row["defect_period"] for row in rows),
    }
    verdict = (
        "CONJUGACY_CLOSURE_CONFIRMED_SAMPLING_ASYMMETRY"
        if len(rows) == EXPECTED_CASES
        and closed == source_class_count
        and summary["physical_mismatch_count"] == 0
        else "CONJUGACY_CLOSURE_MISMATCH"
    )
    payload = {
        "phase": 92,
        "status": verdict,
        "source_phase91_results_sha256": hashlib.sha256(
            PHASE91_RESULTS.read_bytes()
        ).hexdigest(),
        "protocol": {
            "width": WIDTH,
            "burn_in": BURN_IN,
            "steps": LONG_STEPS,
            "tail_range": [TAIL_START, TAIL_END],
            "maximum_period": MAX_PERIOD,
            "catalog_absence_controls_abort_gate": False,
            "zero_ic_is_diagnostic_only": True,
            "comparison": "exact backgrounds and defects at every t=0..1000",
        },
        "summary": summary,
        "cases": rows,
        "methodological_limits": [
            "Only OBSERVED_CATALOG_PAIR rows are direct frozen-catalog coverage evidence.",
            "Constructed complements validate an exact symmetry deterministically; they are not independent statistical observations.",
            "Zero-IC complements are diagnostic and excluded from direct coverage claims.",
            "The audit is limited to the two frozen Fase-90 cohorts.",
        ],
    }
    results_text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    report_text = render_report(payload)
    atomic_write(RESULTS_PATH, results_text)
    atomic_write(REPORT_PATH, report_text)
    return payload


def main() -> None:
    payload = run()
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
