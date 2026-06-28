"""Fase 32: rotation generalization test for the compact T=15 descriptor.

Fase 31 found that `rule + subpatterns_len4` separates the observed shape
families. That descriptor is invariant under circular rotation of an 8-bit
background. Fase 32 tests the resulting prediction:

For each minimal T=15 representative, all seven non-trivial rotations of the
background should map to the same phase-rotated defect-cycle family.

Two modes are tested:

* fixed_ic: the IC word remains centered as in the original sweep.
* cotranslated_ic: the IC placement is shifted with the background rotation,
  preserving local IC/background alignment.

The distinction matters because earlier phases showed strong fixed-IC phase
dependence. A descriptor that only works under co-translation is physically
meaningful but requires IC/background alignment as an explicit state variable.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
SHAPE_RESULTS = OUT_DIR / "shape_families_results.json"
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
RESULTS_JSONL = OUT_DIR / "rotation_generalization_results.jsonl"
REPORT_MD = OUT_DIR / "rotation_generalization_report.md"

SAMPLE_START = 81
BACKGROUND_PERIOD = 3
LOCKING_RATIO = 5
F3_CYCLES = 4
SAMPLE_COUNT = LOCKING_RATIO * F3_CYCLES + 1
FINAL_STEP = SAMPLE_START + BACKGROUND_PERIOD * (SAMPLE_COUNT - 1)


def load_len8_module():
    spec = importlib.util.spec_from_file_location("periodic_background_len8", LEN8_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import detector from {LEN8_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_representatives() -> list[dict]:
    payload = json.loads(SHAPE_RESULTS.read_text(encoding="utf-8"))
    records = []
    for representative in payload["representatives"]:
        records.append(
            {
                "rule": int(representative["rule"]),
                "background": representative["background"],
                "ic": representative["ic"],
                "canonical_cycle": representative["canonical_cycle"],
            }
        )
    return records


def rotate_word(word: str, shift: int) -> str:
    shift %= len(word)
    return word[shift:] + word[:shift]


def rotations(sequence: list[str]) -> list[tuple[str, ...]]:
    return [
        tuple(sequence[index:] + sequence[:index])
        for index in range(len(sequence))
    ]


def canonical_cycle(sequence: list[str]) -> tuple[str, ...]:
    return min(rotations(sequence))


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def initial_diff_at(
    base,
    word_value: int,
    word_len: int,
    bg0: tuple[int, ...],
    start_offset: int,
) -> tuple[int, ...]:
    bg_set = set(bg0)
    start = base.WIDTH // 2 - word_len // 2 + start_offset
    diff = []
    for index in range(word_len):
        position = (start + index) % base.WIDTH
        desired = (word_value >> (word_len - 1 - index)) & 1
        background = 1 if position in bg_set else 0
        if desired ^ background:
            diff.append(position)
    return tuple(sorted(diff))


def perturbation_orbit(
    base,
    rule: int,
    background_frames: list[tuple[int, ...]],
    word: str,
    start_offset: int,
) -> list[tuple[int, ...]]:
    diff = initial_diff_at(base, int(word, 2), len(word), background_frames[0], start_offset)
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


def canonical_defect(width: int, diff: tuple[int, ...]) -> dict | None:
    if not diff:
        return None
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


def minimal_cycle_length(states: list[str]) -> int | None:
    for period in range(1, LOCKING_RATIO + 1):
        if all(states[index] == states[index % period] for index in range(len(states))):
            return period
    return None


def analyze_run(
    base,
    rule: int,
    background: str,
    ic: str,
    start_offset: int,
    expected_cycle: list[str],
) -> dict:
    bg_frames = background_orbit(base, rule, background, FINAL_STEP)
    diff_frames = perturbation_orbit(base, rule, bg_frames, ic, start_offset)
    sample_times = [
        SAMPLE_START + BACKGROUND_PERIOD * index
        for index in range(SAMPLE_COUNT)
    ]

    sampled_backgrounds = [bg_frames[time_index] for time_index in sample_times]
    background_phase_exact = all(
        state == sampled_backgrounds[0] for state in sampled_backgrounds
    )

    canonical = [canonical_defect(base.WIDTH, diff_frames[t]) for t in sample_times]
    if any(state is None for state in canonical):
        return {
            "detected_t15": False,
            "reason": "empty_defect_at_sample",
            "background_phase_exact": background_phase_exact,
            "family_match": False,
        }

    state_sequence = [state["hex"] for state in canonical if state is not None]
    first_cycle = state_sequence[:LOCKING_RATIO]
    cycle_length = minimal_cycle_length(state_sequence)
    states_distinct = len(set(first_cycle)) == LOCKING_RATIO
    closes_after_five = state_sequence[LOCKING_RATIO] == state_sequence[0]
    four_cycles_repeat = all(
        state_sequence[index] == first_cycle[index % LOCKING_RATIO]
        for index in range(len(state_sequence))
    )
    detected_t15 = (
        background_phase_exact
        and states_distinct
        and closes_after_five
        and four_cycles_repeat
        and cycle_length == LOCKING_RATIO
    )
    observed_cycle = list(canonical_cycle(first_cycle)) if detected_t15 else None
    expected_canonical = list(canonical_cycle(expected_cycle))
    family_match = bool(detected_t15 and observed_cycle == expected_canonical)
    return {
        "detected_t15": detected_t15,
        "reason": "ok" if detected_t15 else "no_t15_cycle",
        "background_phase_exact": background_phase_exact,
        "states_distinct": states_distinct,
        "cycle_length_under_F3": cycle_length,
        "observed_canonical_cycle": observed_cycle,
        "expected_canonical_cycle": expected_canonical,
        "family_match": family_match,
    }


def run_tests() -> list[dict]:
    module = load_len8_module()
    base = module.load_base_module()
    records = []
    for representative in load_representatives():
        for shift in range(1, 8):
            rotated_background = rotate_word(representative["background"], shift)
            for mode, start_offset in (
                ("fixed_ic", 0),
                ("cotranslated_ic", -shift),
            ):
                result = analyze_run(
                    base,
                    representative["rule"],
                    rotated_background,
                    representative["ic"],
                    start_offset,
                    representative["canonical_cycle"],
                )
                records.append(
                    {
                        "rule": representative["rule"],
                        "background_original": representative["background"],
                        "background_rotated": rotated_background,
                        "rotation": shift,
                        "ic": representative["ic"],
                        "mode": mode,
                        "start_offset": start_offset,
                        **result,
                    }
                )
    return records


def summarize(records: list[dict]) -> dict:
    summary = {}
    for mode in ("fixed_ic", "cotranslated_ic"):
        selected = [record for record in records if record["mode"] == mode]
        by_rule = {}
        for rule in (73, 109):
            rule_records = [record for record in selected if record["rule"] == rule]
            by_rule[str(rule)] = {
                "runs": len(rule_records),
                "detected_t15": sum(record["detected_t15"] for record in rule_records),
                "family_match": sum(record["family_match"] for record in rule_records),
            }
        summary[mode] = {
            "runs": len(selected),
            "detected_t15": sum(record["detected_t15"] for record in selected),
            "family_match": sum(record["family_match"] for record in selected),
            "by_rule": by_rule,
        }
    return summary


def render_report(records: list[dict]) -> str:
    summary = summarize(records)
    lines = [
        "# Fase 32: Rotation Generalization Test for `rule + subpatterns_len4`",
        "",
        "## Question",
        "",
        "Fase 31 found that `rule + subpatterns_len4` separates the 13 observed",
        "T=15 shape families. Because the length-4 circular subpattern multiset",
        "is invariant under rotation of the length-8 background, Fase 32 tests",
        "whether the predicted family is preserved across all seven non-trivial",
        "background rotations.",
        "",
        "Two modes are tested:",
        "",
        "- `fixed_ic`: rotate the background but leave the IC centered.",
        "- `cotranslated_ic`: rotate the background and shift IC placement by",
        "  `-rotation`, preserving local IC/background alignment.",
        "",
        "## Summary",
        "",
        "| mode | runs | T=15 detections | family matches |",
        "| --- | ---: | ---: | ---: |",
    ]
    for mode, data in summary.items():
        lines.append(
            f"| `{mode}` | {data['runs']} | {data['detected_t15']} | {data['family_match']} |"
        )
    lines.extend(
        [
            "",
            "## By rule",
            "",
            "| mode | rule | runs | T=15 detections | family matches |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for mode, data in summary.items():
        for rule, rule_data in data["by_rule"].items():
            lines.append(
                f"| `{mode}` | {rule} | {rule_data['runs']} | "
                f"{rule_data['detected_t15']} | {rule_data['family_match']} |"
            )

    fixed = summary["fixed_ic"]
    cotranslated = summary["cotranslated_ic"]
    if fixed["family_match"] == fixed["runs"]:
        verdict = "ROTATION_INVARIANT_DESCRIPTOR_CONFIRMED"
        reading = (
            "The descriptor survives rotation even with fixed centered ICs. "
            "`rule + subpatterns_len4` is a strong candidate for a physical "
            "shape-family descriptor."
        )
    elif cotranslated["family_match"] == cotranslated["runs"]:
        verdict = "ALIGNMENT_CONDITIONED_DESCRIPTOR_CONFIRMED"
        reading = (
            "The descriptor survives exactly when IC/background alignment is "
            "preserved. The compact state variable is therefore not background "
            "alone but `(rule, subpatterns_len4, IC-background alignment)`."
        )
    else:
        verdict = "DESCRIPTOR_ROTATION_GENERALIZATION_FAILED"
        reading = (
            "Even co-translated rotations fail to preserve all T=15 families. "
            "`rule + subpatterns_len4` separates the minimal representatives but "
            "does not generalize across rotations."
        )

    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"**Status:** `{verdict}`.",
            "",
            reading,
            "",
            "## Falsifiable implication",
            "",
            "If `rule + subpatterns_len4` is a genuine compact descriptor, every",
            "rotation of a background with preserved IC/background alignment must",
            "produce the same phase-rotated defect-cycle family. Any failed",
            "co-translated match falsifies the descriptor as stated.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    records = run_tests()
    with RESULTS_JSONL.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    REPORT_MD.write_text(render_report(records), encoding="utf-8")
    print(f"wrote {RESULTS_JSONL}")
    print(f"wrote {REPORT_MD}")
    print(json.dumps(summarize(records), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
