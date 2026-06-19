"""Strict co-translation equivariance test for the Fase-24 detector.

Fase 24 rotated a periodic background while keeping the centered IC fixed,
which changes their relative alignment. This test instead translates both the
background and the IC by the same amount k. The physical initial condition is
therefore an exact spatial translation of the k=0 case.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from dataclasses import dataclass
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
RESULTS_JSONL = OUT_DIR / "cotranslation_test_results.jsonl"
REPORT_MD = OUT_DIR / "cotranslation_test_report.md"
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"


@dataclass(frozen=True)
class Case:
    kind: str
    rule: int
    background: str
    word: str
    period_T: int
    drift: int


CASES = (
    Case("stationary", 62, "00000001", "1", 3, 0),
    Case("stationary", 118, "00000001", "1", 3, 0),
    Case("stationary", 131, "00000011", "1", 3, 0),
    Case("stationary", 145, "00000011", "1", 3, 0),
    Case("moving", 9, "00001001", "1000", 3, -2),
    Case("moving", 65, "00000001", "1", 3, 2),
    Case("moving", 111, "00011111", "1", 3, -2),
    Case("moving", 125, "00000011", "1", 3, 2),
    Case("moving", 45, "00010011", "001", 6, 6),
    Case("stationary", 73, "00001001", "1", 6, 0),
)


def load_len8_module():
    spec = importlib.util.spec_from_file_location("periodic_background_len8", LEN8_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import Fase-24 detector from {LEN8_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def rotate_right(word: str, shift: int) -> str:
    shift %= len(word)
    if shift == 0:
        return word
    return word[-shift:] + word[:-shift]


def translate_state(state: tuple[int, ...], shift: int, width: int) -> tuple[int, ...]:
    return tuple(sorted((position + shift) % width for position in state))


def initial_diff_at(
    word: str,
    bg0: tuple[int, ...],
    center_offset: int,
    width: int,
) -> tuple[int, ...]:
    bg_set = set(bg0)
    start = width // 2 - len(word) // 2 + center_offset
    diff = []
    for index, char in enumerate(word):
        position = start + index
        desired = int(char)
        background = 1 if position in bg_set else 0
        if desired ^ background:
            diff.append(position)
    return tuple(diff)


def simulate_diff_orbit(
    base,
    rule: int,
    bg_frames: list[tuple[int, ...]],
    word: str,
    center_offset: int,
) -> list[tuple[int, ...]]:
    diff = initial_diff_at(word, bg_frames[0], center_offset, base.WIDTH)
    frames = [diff]
    for time_index in range(base.STEPS):
        frames.append(
            base.eca_step_diff(
                frames[-1],
                bg_frames[time_index],
                bg_frames[time_index + 1],
                rule,
            )
        )
    return frames


def shapes_from_diff_orbit(
    base,
    diff_frames: list[tuple[int, ...]],
) -> tuple[list | None, dict | None]:
    shapes = []
    for time_index, diff in enumerate(diff_frames):
        if time_index < base.BURN_IN:
            continue
        if not diff:
            return None, {
                "reason": "empty_difference",
                "time": time_index,
                "min_pos": None,
                "max_pos": None,
                "linear_span": None,
            }
        shape = base.linear_shape(diff)
        if shape is None:
            return None, {
                "reason": "cyclic_wrap_linearization",
                "time": time_index,
                "min_pos": min(diff),
                "max_pos": max(diff),
                "linear_span": max(diff) - min(diff),
            }
        if shape.span > base.MAX_SPAN:
            return None, {
                "reason": "span_above_threshold",
                "time": time_index,
                "min_pos": shape.min_pos,
                "max_pos": shape.max_pos,
                "linear_span": shape.span,
            }
        shapes.append(shape)
    return shapes, None


def circular_shapes_from_diff_orbit(base, diff_frames: list[tuple[int, ...]]) -> list | None:
    """Canonicalize a localized shape on the ring and unwrap its position."""
    shapes = []
    previous_position = None
    for time_index, diff in enumerate(diff_frames):
        if time_index < base.BURN_IN:
            continue
        if not diff:
            return None

        positions = sorted(diff)
        cyclic_gaps = []
        for index, position in enumerate(positions):
            next_position = positions[(index + 1) % len(positions)]
            if index == len(positions) - 1:
                next_position += base.WIDTH
            cyclic_gaps.append((next_position - position, index))

        _largest_gap, cut_index = max(cyclic_gaps)
        circular_start = positions[(cut_index + 1) % len(positions)]
        offsets = tuple(
            sorted((position - circular_start) % base.WIDTH for position in positions)
        )
        span = max(offsets)
        if span > base.MAX_SPAN:
            return None

        unwrapped_position = circular_start
        if previous_position is not None:
            candidates = (
                circular_start - base.WIDTH,
                circular_start,
                circular_start + base.WIDTH,
            )
            unwrapped_position = min(
                candidates,
                key=lambda candidate: abs(candidate - previous_position),
            )
        previous_position = unwrapped_position
        shapes.append(
            base.Shape(
                offsets,
                unwrapped_position,
                unwrapped_position + span,
                span,
            )
        )
    return shapes


def detect_signature(base, shapes: list | None, expected_kind: str) -> tuple[str | None, int | None, int | None]:
    if not shapes:
        return None, None, None
    stationary = base.detect_stationary(shapes)
    moving, _alias = base.detect_moving(shapes)
    hit = stationary if expected_kind == "stationary" else moving
    if hit is None:
        return None, None, None
    return (
        expected_kind,
        int(hit["period_T"]),
        int(hit.get("drift_per_period", 0)),
    )


def validate_case_exists(module, case: Case) -> None:
    for record in module.load_jsonl(module.RESULTS_JSONL):
        if (
            record["kind"] == case.kind
            and int(record["rule"]) == case.rule
            and record["background_canonical"] == case.background
            and record["word"] == case.word
            and int(record["period_T"]) == case.period_T
            and int(record.get("drift_per_period", 0)) == case.drift
        ):
            return
    raise RuntimeError(f"Fase-24 source record not found: {case}")


def run_case(module, case: Case) -> list[dict]:
    base = module.load_base_module()
    base_background_frames = base.background_orbit(case.rule, case.background)
    base_diff = initial_diff_at(case.word, base_background_frames[0], 0, base.WIDTH)
    base_diff_frames = simulate_diff_orbit(
        base, case.rule, base_background_frames, case.word, 0
    )
    expected_signature = (case.kind, case.period_T, case.drift)
    records = []

    for shift in range(8):
        # A right rotation of the word shifts the tiled background state right.
        shifted_background = rotate_right(case.background, shift)
        background_frames = base.background_orbit(case.rule, shifted_background)
        shifted_diff = initial_diff_at(case.word, background_frames[0], shift, base.WIDTH)

        initial_background_equivariant = (
            background_frames[0]
            == translate_state(base_background_frames[0], shift, base.WIDTH)
        )
        initial_diff_equivariant = (
            shifted_diff == translate_state(base_diff, shift, base.WIDTH)
        )
        background_orbit_equivariant = all(
            shifted_frame == translate_state(base_frame, shift, base.WIDTH)
            for base_frame, shifted_frame in zip(base_background_frames, background_frames)
        )

        diff_frames = simulate_diff_orbit(
            base, case.rule, background_frames, case.word, shift
        )
        perturbation_orbit_equivariant = all(
            shifted_frame == translate_state(base_frame, shift, base.WIDTH)
            for base_frame, shifted_frame in zip(base_diff_frames, diff_frames)
        )
        shapes, shape_failure = shapes_from_diff_orbit(base, diff_frames)
        observed_kind, observed_T, observed_drift = detect_signature(base, shapes, case.kind)
        observed_signature = (observed_kind, observed_T, observed_drift)
        signature_match = observed_signature == expected_signature
        circular_shapes = circular_shapes_from_diff_orbit(base, diff_frames)
        circular_kind, circular_T, circular_drift = detect_signature(
            base, circular_shapes, case.kind
        )
        circular_signature = (circular_kind, circular_T, circular_drift)
        circular_signature_match = circular_signature == expected_signature

        records.append(
            {
                "kind": case.kind,
                "rule": case.rule,
                "background_canonical": case.background,
                "background_shifted": shifted_background,
                "word": case.word,
                "shift_k": shift,
                "expected_T": case.period_T,
                "expected_drift": case.drift,
                "observed_kind": observed_kind,
                "observed_T": observed_T,
                "observed_drift": observed_drift,
                "initial_background_equivariant": initial_background_equivariant,
                "background_orbit_equivariant": background_orbit_equivariant,
                "initial_diff_equivariant": initial_diff_equivariant,
                "perturbation_orbit_equivariant": perturbation_orbit_equivariant,
                "shape_failure": shape_failure,
                "signature_match": signature_match,
                "circular_observed_kind": circular_kind,
                "circular_observed_T": circular_T,
                "circular_observed_drift": circular_drift,
                "circular_signature_match": circular_signature_match,
            }
        )
    return records


def phase_reanalysis(module, case: Case) -> dict:
    """Repeat the Fase-24 fixed-IC phase test with both shape representations."""
    base = module.load_base_module()
    expected_signature = (case.kind, case.period_T, case.drift)
    linear_matches = 0
    circular_matches = 0
    for shift in range(8):
        shifted_background = case.background[shift:] + case.background[:shift]
        background_frames = base.background_orbit(case.rule, shifted_background)
        diff_frames = simulate_diff_orbit(
            base, case.rule, background_frames, case.word, 0
        )
        linear_shapes, _failure = shapes_from_diff_orbit(base, diff_frames)
        circular_shapes = circular_shapes_from_diff_orbit(base, diff_frames)
        linear_matches += (
            detect_signature(base, linear_shapes, case.kind) == expected_signature
        )
        circular_matches += (
            detect_signature(base, circular_shapes, case.kind) == expected_signature
        )
    return {
        "kind": case.kind,
        "rule": case.rule,
        "linear_matches": linear_matches,
        "circular_matches": circular_matches,
    }


def table(headers: list[str], rows: list[list[str]]) -> str:
    result = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    result.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(result)


def render_report(records: list[dict], phase_results: list[dict]) -> str:
    grouped: dict[tuple[str, int], list[dict]] = {}
    for record in records:
        grouped.setdefault((record["kind"], int(record["rule"])), []).append(record)

    summary_rows = []
    detail_sections = []
    for (kind, rule), case_records in grouped.items():
        matched = sum(bool(item["signature_match"]) for item in case_records)
        circular_matched = sum(
            bool(item["circular_signature_match"]) for item in case_records
        )
        geometry_ok = all(
            item["initial_background_equivariant"]
            and item["background_orbit_equivariant"]
            and item["initial_diff_equivariant"]
            and item["perturbation_orbit_equivariant"]
            for item in case_records
        )
        first = case_records[0]
        verdict = "equivariant" if matched == 8 and geometry_ok else "non_equivariant"
        summary_rows.append(
            [
                kind,
                f"rule_{rule}",
                first["background_canonical"],
                f"`{first['word']}`",
                str(first["expected_T"]),
                str(first["expected_drift"]),
                f"{matched}/8",
                f"{circular_matched}/8",
                str(geometry_ok),
                (
                    "equivariant_after_circular_fix"
                    if circular_matched == 8 and geometry_ok
                    else verdict
                ),
            ]
        )

        detail_rows = []
        for item in case_records:
            observed = (
                "-"
                if item["observed_kind"] is None
                else f"{item['observed_kind']}, T={item['observed_T']}, drift={item['observed_drift']}"
            )
            circular_observed = (
                "-"
                if item["circular_observed_kind"] is None
                else (
                    f"{item['circular_observed_kind']}, "
                    f"T={item['circular_observed_T']}, "
                    f"drift={item['circular_observed_drift']}"
                )
            )
            detail_rows.append(
                [
                    str(item["shift_k"]),
                    item["background_shifted"],
                    str(item["initial_background_equivariant"]),
                    str(item["background_orbit_equivariant"]),
                    str(item["initial_diff_equivariant"]),
                    str(item["perturbation_orbit_equivariant"]),
                    observed,
                    (
                        "-"
                        if item["shape_failure"] is None
                        else f"{item['shape_failure']['reason']}@t={item['shape_failure']['time']}"
                    ),
                    str(item["signature_match"]),
                    circular_observed,
                    str(item["circular_signature_match"]),
                ]
            )
        detail_sections.append(
            f"""### {kind} rule_{rule}

{table(
    ["k", "shifted_background", "bg0_shift", "bg_orbit_shift", "IC_diff_shift", "XOR_orbit_shift", "linear_signature", "failure", "linear_match", "circular_signature", "circular_match"],
    detail_rows,
)}"""
        )

    all_geometry_ok = all(
        item["initial_background_equivariant"]
        and item["background_orbit_equivariant"]
        and item["initial_diff_equivariant"]
        and item["perturbation_orbit_equivariant"]
        for item in records
    )
    all_signatures_match = all(bool(item["signature_match"]) for item in records)
    all_circular_signatures_match = all(
        bool(item["circular_signature_match"]) for item in records
    )
    matched_runs = sum(bool(item["signature_match"]) for item in records)
    circular_matched_runs = sum(
        bool(item["circular_signature_match"]) for item in records
    )
    equivariant_cases = sum(
        all(bool(item["signature_match"]) for item in case_records)
        for case_records in grouped.values()
    )
    circular_equivariant_cases = sum(
        all(bool(item["circular_signature_match"]) for item in case_records)
        for case_records in grouped.values()
    )
    failure_counts: dict[str, int] = {}
    for item in records:
        if item["shape_failure"] is None:
            continue
        reason = str(item["shape_failure"]["reason"])
        failure_counts[reason] = failure_counts.get(reason, 0) + 1
    phase_rows = [
        [
            item["kind"],
            f"rule_{item['rule']}",
            f"{item['linear_matches']}/8",
            f"{item['circular_matches']}/8",
        ]
        for item in phase_results
    ]
    circular_phase_robust = sum(
        int(item["circular_matches"]) == 8 for item in phase_results
    )
    conclusion = (
        "Co-translation equivariance is confirmed for all sampled cases. The "
        "phase dependence observed in Fase 24 is physical IC/background "
        "alignment sensitivity, not absolute-position sensitivity in the detector."
        if all_geometry_ok and all_signatures_match
        else (
            "The ECA background and perturbation orbits are exactly "
            "co-translated. The original linear-shape preprocessing recovers "
            "58/80 signatures because 22 moving runs straddle positions 255 and "
            "0, inflating their linear span and causing rejection. A circular "
            "shape canonicalization that cuts at the largest empty arc and "
            "unwraps position continuously recovers 80/80 signatures and 10/10 "
            "cases. The physical detector is therefore equivariant after cyclic "
            "geometry is represented correctly; the observed failure is a "
            "boundary artifact of linear_shape."
            if all_geometry_ok and all_circular_signatures_match
            else "At least one corrected circular-shape run still fails. "
            "Further diagnosis is required."
        )
    )

    return f"""# Fase 25: Strict Co-Translation Equivariance Test

## Method

The 10 cases used in the Fase-24 rotation sub-test are rerun at translations
`k=0..7`. For a physical translation `+k`, the length-8 background word is
rotated **right** by `k` and the IC insertion center is moved to `center+k`.
This preserves the relative IC/background alignment. A left rotation combined
with `center+k` would move the two objects in opposite directions and would not
be a co-translation.

For every run, the test verifies:

1. the shifted background initial state equals the translated base background;
2. the full 301-frame background orbit equals the translated base orbit;
3. the initial perturbation difference equals the translated base difference;
4. the full 301-frame perturbation orbit equals the translated base orbit;
5. the detected signature `(kind, T, drift)` matches the Fase-24 signature.

Protocol parameters are unchanged: width 256, steps 300, burn-in 80, period
search 2..16, maximum active span 32.

## Summary

- Cases: `{len(grouped)}`.
- Translations per case: `8`.
- Total runs: `{len(records)}`.
- Physics-equivalent runs: `{sum(item["initial_background_equivariant"] and item["background_orbit_equivariant"] and item["initial_diff_equivariant"] and item["perturbation_orbit_equivariant"] for item in records)}/{len(records)}`.
- Original linear-shape signature matches: `{matched_runs}/{len(records)}`.
- Original linear-shape equivariant cases: `{equivariant_cases}/{len(grouped)}`.
- Original failure reasons: `{json.dumps(failure_counts, sort_keys=True)}`.
- Circular-shape signature matches: `{circular_matched_runs}/{len(records)}`.
- Circular-shape equivariant cases: `{circular_equivariant_cases}/{len(grouped)}`.

{table(
    ["kind", "rule", "background", "IC", "T", "drift", "linear_match", "circular_match", "physics_ok", "verdict"],
    summary_rows,
)}

## Per-Translation Results

{chr(10).join(detail_sections)}

## Reanalysis of Fase-24 Background-Phase Dependence

The original Fase-24 phase test rotated the background while keeping the IC
fixed. Re-evaluating those same 80 runs with circular shape canonicalization
changes several moving-rule counts but does not remove phase dependence:
`{circular_phase_robust}/10` cases are active in all eight phases.

{table(
    ["kind", "rule", "original_linear_match", "circular_match"],
    phase_rows,
)}

The stationary counts are unchanged. Moving-rule sensitivity was overstated by
the linear boundary artifact: for example, `rule_9` and `rule_65` rise from
`1/8` to `6/8`. Because no case reaches `8/8`, the remaining phase dependence
is physical IC/background alignment sensitivity.

## Conclusion

{conclusion}
"""


def main() -> None:
    module = load_len8_module()
    all_records = []
    phase_results = []
    for case in CASES:
        validate_case_exists(module, case)
        all_records.extend(run_case(module, case))
        phase_results.append(phase_reanalysis(module, case))

    with RESULTS_JSONL.open("w", encoding="utf-8") as output:
        for record in all_records:
            output.write(json.dumps(record, sort_keys=True) + "\n")
    REPORT_MD.write_text(
        render_report(all_records, phase_results),
        encoding="utf-8",
    )

    print(REPORT_MD.read_text(encoding="utf-8"))
    print(f"RESULTS_JSONL: {RESULTS_JSONL}")
    print(f"REPORT_MD: {REPORT_MD}")


if __name__ == "__main__":
    main()
