#!/usr/bin/env python3
"""Fase 34: targeted T=15 validation on primitive len-9/10 backgrounds.

Fase 33 showed that no unseen length-8 background can test the
`rule + subpatterns_len4 + alignment` descriptor: the length-8 universe is
exhausted. Fase 34 therefore leaves length 8, but only after a preflight found
primitive length-9/10 backgrounds with T_bg=3 under rule_73/rule_109.

This is not a blind all-rule sweep. It tests only:

- rules: 73 and 109
- primitive background necklaces of length 9 and 10 with T_bg=3
- IC words: non-zero binary words of length 1..8 (502 words)
- T=15 mechanism gate: five distinct defect states under F^3 after burn-in
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
PREFLIGHT_JSON = OUT_DIR / "preflight_len9_len10_tbg3_results.json"
RESULTS_JSONL = OUT_DIR / "targeted_len9_len10_t15_results.jsonl"
REPORT_MD = OUT_DIR / "targeted_len9_len10_t15_report.md"

RULES = (73, 109)
LENGTHS = (9, 10)
BACKGROUND_PERIOD = 3
LOCAL_PERIOD = 15
LOCKING_RATIO = LOCAL_PERIOD // BACKGROUND_PERIOD
SAMPLE_START = 81
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


def ic_words() -> list[tuple[int, int, str]]:
    words = []
    for length in range(1, 9):
        for value in range(1, 1 << length):
            words.append((length, value, format(value, f"0{length}b")))
    return words


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def perturbation_orbit(
    base,
    rule: int,
    background_frames: list[tuple[int, ...]],
    word_value: int,
    word_len: int,
) -> list[tuple[int, ...]]:
    diff = base.initial_diff(word_value, word_len, background_frames[0])
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


def signed_ring_delta(start: int, end: int, width: int) -> int:
    delta = (end - start) % width
    if delta > width // 2:
        delta -= width
    return delta


def detect_t15(base, rule: int, background: str, word_len: int, word_value: int) -> dict:
    bg_frames = background_orbit(base, rule, background, FINAL_STEP)
    diff_frames = perturbation_orbit(base, rule, bg_frames, word_value, word_len)
    sample_times = [SAMPLE_START + BACKGROUND_PERIOD * index for index in range(SAMPLE_COUNT)]
    sampled_backgrounds = [bg_frames[time_index] for time_index in sample_times]
    background_phase_exact = all(state == sampled_backgrounds[0] for state in sampled_backgrounds)

    canonical = [canonical_defect(base.WIDTH, diff_frames[time_index]) for time_index in sample_times]
    if any(state is None for state in canonical):
        return {
            "detected_t15": False,
            "reason": "empty_defect_at_sample",
            "background_phase_exact": background_phase_exact,
        }
    states = [state["hex"] for state in canonical if state is not None]
    first_cycle = states[:LOCKING_RATIO]
    cycle_length = minimal_cycle_length(states)
    states_distinct = len(set(first_cycle)) == LOCKING_RATIO
    closes_after_five = states[LOCKING_RATIO] == states[0]
    four_cycles_repeat = all(states[index] == first_cycle[index % LOCKING_RATIO] for index in range(len(states)))

    anchors = [state["anchor"] for state in canonical if state is not None]
    per_local_period_drift = [
        signed_ring_delta(anchors[index], anchors[index + LOCKING_RATIO], base.WIDTH)
        for index in range(len(anchors) - LOCKING_RATIO)
    ]
    stationary = all(delta == 0 for delta in per_local_period_drift)
    detected = all(
        (
            background_phase_exact,
            states_distinct,
            closes_after_five,
            four_cycles_repeat,
            cycle_length == LOCKING_RATIO,
            stationary,
        )
    )
    return {
        "detected_t15": detected,
        "reason": "ok" if detected else "no_t15_cycle",
        "background_phase_exact": background_phase_exact,
        "states_distinct": states_distinct,
        "cycle_length_under_F3": cycle_length,
        "cycle_closes_after_five": closes_after_five,
        "four_cycles_repeat": four_cycles_repeat,
        "stationary_over_local_period": stationary,
        "drift": per_local_period_drift[0] if per_local_period_drift else None,
        "defect_states": first_cycle if detected else None,
        "defect_width_per_state": [state["width"] for state in canonical[:LOCKING_RATIO] if state is not None] if detected else None,
    }


def load_target_backgrounds() -> list[dict]:
    data = json.loads(PREFLIGHT_JSON.read_text(encoding="utf-8"))
    targets = []
    for length in LENGTHS:
        for rule in RULES:
            key = f"len{length}_rule{rule}"
            for rec in data["by_length_rule"][key]["t_bg_3_records"]:
                targets.append(
                    {
                        "length": length,
                        "rule": rule,
                        "background": rec["background"],
                        "background_preperiod": rec["preperiod"],
                        "T_bg": rec["period"],
                    }
                )
    return targets


def main() -> None:
    start = time.perf_counter()
    base = load_len8_module().load_base_module()
    targets = load_target_backgrounds()
    words = ic_words()
    records = []
    processed = 0
    positives = []

    with RESULTS_JSONL.open("w", encoding="utf-8") as fh:
        for target in targets:
            hits_for_target = []
            for word_len, word_value, word in words:
                processed += 1
                result = detect_t15(base, target["rule"], target["background"], word_len, word_value)
                if not result["detected_t15"]:
                    continue
                record = {
                    **target,
                    "word_len": word_len,
                    "word": word,
                    "T_local": LOCAL_PERIOD,
                    "locking_ratio": LOCKING_RATIO,
                    **result,
                }
                hits_for_target.append(record)
                positives.append(record)
                fh.write(json.dumps(record, sort_keys=True) + "\n")
            records.append({**target, "detections": len(hits_for_target)})

    elapsed = time.perf_counter() - start
    summary = summarize(targets, records, positives, processed, elapsed)
    REPORT_MD.write_text(render_report(summary, positives), encoding="utf-8")


def summarize(targets: list[dict], records: list[dict], positives: list[dict], processed: int, elapsed: float) -> dict:
    targets_by_len_rule = Counter((target["length"], target["rule"]) for target in targets)
    detections_by_len_rule = Counter((item["length"], item["rule"]) for item in positives)
    positive_backgrounds = Counter((item["length"], item["rule"], item["background"]) for item in positives)
    unique_positive_backgrounds_by_len_rule = Counter((length, rule) for length, rule, _bg in positive_backgrounds)
    min_witness = {}
    for item in positives:
        key = (item["length"], item["rule"], item["background"])
        prev = min_witness.get(key)
        if prev is None or (item["word_len"], item["word"]) < (prev["word_len"], prev["word"]):
            min_witness[key] = item

    return {
        "status": "T15_EXTERNAL_LEN9_LEN10_FOUND" if positives else "NO_T15_EXTERNAL_LEN9_LEN10",
        "target_backgrounds": len(targets),
        "processed_runs": processed,
        "positive_count": len(positives),
        "elapsed_seconds": elapsed,
        "targets_by_len_rule": {f"len{length}_rule{rule}": count for (length, rule), count in sorted(targets_by_len_rule.items())},
        "detections_by_len_rule": {f"len{length}_rule{rule}": count for (length, rule), count in sorted(detections_by_len_rule.items())},
        "positive_backgrounds_by_len_rule": {
            f"len{length}_rule{rule}": count
            for (length, rule), count in sorted(unique_positive_backgrounds_by_len_rule.items())
        },
        "positive_background_count": len(positive_backgrounds),
        "minimal_witnesses": [
            {
                "length": length,
                "rule": rule,
                "background": background,
                "detection_count": positive_backgrounds[(length, rule, background)],
                "min_word": item["word"],
                "min_word_len": item["word_len"],
                "defect_states": item["defect_states"],
            }
            for (length, rule, background), item in sorted(min_witness.items())
        ],
    }


def render_report(summary: dict, positives: list[dict]) -> str:
    lines = [
        "# Fase 34: Targeted Length-9/10 T=15 Validation",
        "",
        "## Protocol",
        "",
        "- Rules: `rule_73`, `rule_109`.",
        "- Backgrounds: primitive length-9/10 necklaces with `T_bg=3` under the same rule.",
        "- ICs: 502 non-zero binary words of length 1..8.",
        "- Width: inherited from the periodic-background detector (`256`).",
        "- Sample gate: five distinct defect states under `F^3` after burn-in, repeated for four cycles.",
        "",
        "## Summary",
        "",
        f"- Target backgrounds: `{summary['target_backgrounds']}`.",
        f"- Processed runs: `{summary['processed_runs']}`.",
        f"- Positive T=15 detections: `{summary['positive_count']}`.",
        f"- Positive backgrounds: `{summary['positive_background_count']}`.",
        f"- Elapsed seconds: `{summary['elapsed_seconds']:.2f}`.",
        "",
        "| length/rule | target backgrounds | T=15 detections | positive backgrounds |",
        "| --- | ---: | ---: | ---: |",
    ]
    for key in sorted(summary["targets_by_len_rule"]):
        lines.append(
            f"| `{key}` | {summary['targets_by_len_rule'].get(key, 0)} | "
            f"{summary['detections_by_len_rule'].get(key, 0)} | "
            f"{summary['positive_backgrounds_by_len_rule'].get(key, 0)} |"
        )

    lines += ["", "## Minimal witnesses", ""]
    if summary["minimal_witnesses"]:
        lines.append("| length | rule | background | detections | min IC | defect states |")
        lines.append("| ---: | ---: | --- | ---: | --- | --- |")
        for item in summary["minimal_witnesses"][:100]:
            states = ", ".join(f"`{state}`" for state in item["defect_states"])
            lines.append(
                f"| {item['length']} | {item['rule']} | `{item['background']}` | "
                f"{item['detection_count']} | `{item['min_word']}` | {states} |"
            )
    else:
        lines.append("No T=15 witnesses were found.")

    lines += [
        "",
        "## Verdict",
        "",
        f"**Status:** `{summary['status']}`.",
        "",
    ]
    if summary["positive_count"]:
        lines.append(
            "The T=15 mechanism does generalize outside primitive length-8 backgrounds "
            "when the prerequisite `T_bg=3` is preserved. These are genuine external "
            "backgrounds, not rotations of the original representative set."
        )
    else:
        lines.append(
            "No T=15 witnesses were found outside length 8 under this targeted test. "
            "The compact descriptor remains a length-8 result unless a broader "
            "protocol finds new representatives."
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
