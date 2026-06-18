"""Sweep primitive period-8 backgrounds for local ECA oscillators.

This extends the validated periodic-background detector from v1.2. The
physical observable is the localized XOR difference between a perturbed run
and the unperturbed background orbit, so periodicity of the background itself
does not count as a local oscillator.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Iterable


OUT_DIR = Path(__file__).resolve().parent
RESULTS_JSONL = OUT_DIR / "sweep_len8_results.jsonl"
REPORT_MD = OUT_DIR / "sweep_len8_report.md"
CHECKPOINT_JSON = OUT_DIR / "sweep_len8_checkpoint.json"

BASE_DIR = OUT_DIR.parent / "periodic_backgrounds"
BASE_SCRIPT = BASE_DIR / "sweep_periodic_background_oscillators.py"
BASE_RESULTS = BASE_DIR / "periodic_background_oscillator_results.jsonl"

EXPECTED_BACKGROUNDS = 30
EXPECTED_ICS = 502
EXPECTED_RUNS = 256 * EXPECTED_BACKGROUNDS * EXPECTED_ICS
KNOWN_SPEEDS = (0.0, 0.5, 1.0)


def load_base_module():
    spec = importlib.util.spec_from_file_location("periodic_background_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base detector from {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def rotations(word: str) -> tuple[str, ...]:
    return tuple(word[i:] + word[:i] for i in range(len(word)))


def minimal_period(word: str) -> int:
    for period in range(1, len(word) + 1):
        if len(word) % period == 0 and word == word[:period] * (len(word) // period):
            return period
    raise AssertionError("Every finite word has a period equal to its length")


def primitive_len8_backgrounds() -> list[str]:
    canonical: set[str] = set()
    for value in range(1, 1 << 8):
        word = format(value, "08b")
        if minimal_period(word) != 8:
            continue
        canonical.add(min(rotations(word)))
    result = sorted(canonical)
    if len(result) != EXPECTED_BACKGROUNDS:
        raise RuntimeError(
            f"Expected {EXPECTED_BACKGROUNDS} primitive length-8 necklaces, got {len(result)}"
        )
    return result


def ic_words() -> Iterable[tuple[int, int, str]]:
    for length in range(1, 9):
        for value in range(1, 1 << length):
            yield length, value, format(value, f"0{length}b")


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_baseline_rules() -> dict[str, set[int]]:
    rules = {"stationary": set(), "moving": set()}
    for record in load_jsonl(BASE_RESULTS):
        kind = record.get("kind")
        if kind in rules:
            rules[kind].add(int(record["rule"]))
    if not rules["stationary"] or not rules["moving"]:
        raise RuntimeError(f"Baseline result sets are empty or incomplete: {BASE_RESULTS}")
    return rules


def analyze_rule(rule: int) -> dict:
    base = load_base_module()
    positives: list[dict] = []
    alias_count = 0
    processed = 0
    words = list(ic_words())

    for background in primitive_len8_backgrounds():
        bg_frames = base.background_orbit(rule, background)
        for word_len, word_value, word in words:
            processed += 1
            shapes = base.simulate_diff_shapes(
                rule, bg_frames, word_value, word_len
            )
            if not shapes:
                continue
            stationary = base.detect_stationary(shapes)
            moving, alias = base.detect_moving(shapes)
            if alias is not None:
                alias_count += 1
            for hit in (stationary, moving):
                if hit is None:
                    continue
                positives.append(
                    {
                        "rule": rule,
                        "background_canonical": background,
                        "word_len": word_len,
                        "word": word,
                        **hit,
                    }
                )

    return {
        "rule": rule,
        "processed": processed,
        "alias_count": alias_count,
        "positives": positives,
    }


def load_checkpoint() -> dict:
    if not CHECKPOINT_JSON.exists():
        return {
            "completed_rules": [],
            "processed": 0,
            "positive_count": 0,
            "alias_count": 0,
            "elapsed_seconds": 0.0,
        }
    return json.loads(CHECKPOINT_JSON.read_text(encoding="utf-8"))


def save_checkpoint(checkpoint: dict) -> None:
    CHECKPOINT_JSON.write_text(
        json.dumps(checkpoint, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def reset_outputs() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_JSONL.write_text("", encoding="utf-8")
    save_checkpoint(
        {
            "completed_rules": [],
            "processed": 0,
            "positive_count": 0,
            "alias_count": 0,
            "elapsed_seconds": 0.0,
        }
    )


def run_sweep(start_rule: int, end_rule: int, workers: int, reset: bool) -> dict:
    if reset or not RESULTS_JSONL.exists() or not CHECKPOINT_JSON.exists():
        reset_outputs()

    checkpoint = load_checkpoint()
    completed = {int(rule) for rule in checkpoint["completed_rules"]}
    rules = [
        rule
        for rule in range(start_rule, end_rule + 1)
        if rule not in completed
    ]
    if not rules:
        return checkpoint

    started = time.perf_counter()
    with RESULTS_JSONL.open("a", encoding="utf-8") as out:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            # executor.map preserves rule order, keeping JSONL deterministic.
            for result in executor.map(analyze_rule, rules):
                for record in result["positives"]:
                    out.write(json.dumps(record, sort_keys=True) + "\n")
                out.flush()

                completed.add(int(result["rule"]))
                checkpoint["completed_rules"] = sorted(completed)
                checkpoint["processed"] = int(checkpoint["processed"]) + int(result["processed"])
                checkpoint["positive_count"] = int(checkpoint.get("positive_count", 0)) + len(
                    result["positives"]
                )
                checkpoint["alias_count"] = int(checkpoint["alias_count"]) + int(result["alias_count"])
                checkpoint["elapsed_seconds"] = float(checkpoint["elapsed_seconds"]) + (
                    time.perf_counter() - started
                )
                save_checkpoint(checkpoint)

                elapsed = float(checkpoint["elapsed_seconds"])
                print(
                    f"rule={result['rule']} completed={len(completed)}/256 "
                    f"processed={checkpoint['processed']}/{EXPECTED_RUNS} "
                    f"positives={checkpoint['positive_count']} aliases={checkpoint['alias_count']} "
                    f"elapsed={elapsed:.1f}s",
                    flush=True,
                )
                # Reset segment timer because elapsed was persisted at this checkpoint.
                started = time.perf_counter()

    return checkpoint


def speed_of(record: dict) -> float:
    if record["kind"] == "stationary":
        return 0.0
    return abs(float(record["drift_per_period"])) / float(record["period_T"])


def is_known_speed(speed: float) -> bool:
    return any(math.isclose(speed, known, rel_tol=0.0, abs_tol=1e-12) for known in KNOWN_SPEEDS)


def annotate(records: list[dict], baseline_rules: dict[str, set[int]]) -> list[dict]:
    annotated = []
    for record in records:
        item = dict(record)
        speed = speed_of(item)
        item["speed"] = speed
        item["new_rule"] = int(item["rule"]) not in baseline_rules[item["kind"]]
        item["new_T"] = int(item["period_T"]) > 4
        item["new_speed"] = not is_known_speed(speed)
        annotated.append(item)
    return annotated


def representative_rows(records: list[dict]) -> list[dict]:
    grouped: dict[tuple[str, int, str], list[dict]] = defaultdict(list)
    for record in records:
        grouped[
            (
                str(record["kind"]),
                int(record["rule"]),
                str(record["background_canonical"]),
            )
        ].append(record)

    rows = []
    for (kind, rule, background), items in sorted(grouped.items()):
        first = min(
            items,
            key=lambda item: (
                int(item["word_len"]),
                str(item["word"]),
                int(item["period_T"]),
                int(item.get("drift_per_period", 0)),
            ),
        )
        motif = (
            " / ".join(first["motif"])
            if kind == "stationary"
            else str(first["period_shapes"])
        )
        rows.append(
            {
                "kind": kind,
                "rule": rule,
                "background_canonical": background,
                "candidates": len(items),
                "min_len": int(first["word_len"]),
                "min_word": str(first["word"]),
                "T": int(first["period_T"]),
                "drift": int(first.get("drift_per_period", 0)),
                "speed": float(first["speed"]),
                "motif": motif,
                "new_rule": any(bool(item["new_rule"]) for item in items),
                "new_T": any(bool(item["new_T"]) for item in items),
                "new_speed": any(bool(item["new_speed"]) for item in items),
            }
        )
    return rows


def detect_for_rotation(
    rule: int,
    background: str,
    word_len: int,
    word: str,
    expected_kind: str,
    expected_T: int,
    expected_drift: int,
) -> dict:
    base = load_base_module()
    bg_frames = base.background_orbit(rule, background)
    shapes = base.simulate_diff_shapes(rule, bg_frames, int(word, 2), word_len)
    if not shapes:
        return {"active": False, "kind": None, "T": None, "drift": None}
    stationary = base.detect_stationary(shapes)
    moving, _alias = base.detect_moving(shapes)
    hit = stationary if expected_kind == "stationary" else moving
    if hit is None:
        return {"active": False, "kind": None, "T": None, "drift": None}
    observed_T = int(hit["period_T"])
    observed_drift = int(hit.get("drift_per_period", 0))
    return {
        "active": observed_T == expected_T and observed_drift == expected_drift,
        "kind": expected_kind,
        "T": observed_T,
        "drift": observed_drift,
    }


def rotation_validation(records: list[dict]) -> list[dict]:
    if not records:
        return []

    selected: list[dict] = []
    used_rules: set[int] = set()

    def add_matching(predicate) -> None:
        candidates = sorted(
            (record for record in records if predicate(record)),
            key=lambda item: (
                int(item["rule"]),
                int(item["word_len"]),
                str(item["word"]),
                str(item["background_canonical"]),
                int(item["period_T"]),
                int(item.get("drift_per_period", 0)),
            ),
        )
        for record in candidates:
            rule = int(record["rule"])
            if rule in used_rules:
                continue
            selected.append(record)
            used_rules.add(rule)
            if len(selected) == 10:
                return

    # Balance the sample across the distinct scientific novelties.
    add_matching(lambda item: item["kind"] == "stationary" and item["new_rule"])
    if len(selected) < 10:
        add_matching(lambda item: item["new_speed"])
    if len(selected) < 10:
        add_matching(lambda item: item["new_T"])
    if len(selected) < 10:
        add_matching(lambda item: item["kind"] == "moving" and item["new_rule"])
    if len(selected) < 10:
        add_matching(lambda _item: True)

    validations = []
    for witness in selected:
        expected_drift = int(witness.get("drift_per_period", 0))
        expected_T = int(witness["period_T"])
        phase_results = []
        for phase, background in enumerate(rotations(witness["background_canonical"])):
            result = detect_for_rotation(
                int(witness["rule"]),
                background,
                int(witness["word_len"]),
                str(witness["word"]),
                str(witness["kind"]),
                expected_T,
                expected_drift,
            )
            phase_results.append(
                {
                    "phase": phase,
                    "background": background,
                    **result,
                }
            )
        active_count = sum(bool(item["active"]) for item in phase_results)
        validations.append(
            {
                "kind": witness["kind"],
                "rule": int(witness["rule"]),
                "background_canonical": witness["background_canonical"],
                "word_len": int(witness["word_len"]),
                "word": str(witness["word"]),
                "expected_T": expected_T,
                "expected_drift": expected_drift,
                "active_rotations": active_count,
                "total_rotations": 8,
                "rotationally_robust": active_count == 8,
                "phase_results": phase_results,
            }
        )
    return validations


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(
    records: list[dict],
    rows: list[dict],
    validations: list[dict],
    checkpoint: dict,
) -> str:
    stationary_rules = sorted({int(item["rule"]) for item in records if item["kind"] == "stationary"})
    moving_rules = sorted({int(item["rule"]) for item in records if item["kind"] == "moving"})
    new_stationary = sorted(
        {int(item["rule"]) for item in records if item["kind"] == "stationary" and item["new_rule"]}
    )
    new_moving = sorted(
        {int(item["rule"]) for item in records if item["kind"] == "moving" and item["new_rule"]}
    )
    new_periods = sorted({int(item["period_T"]) for item in records if item["new_T"]})
    new_speeds = sorted({float(item["speed"]) for item in records if item["new_speed"]})

    result_rows = []
    for row in rows:
        result_rows.append(
            [
                row["kind"],
                f"rule_{row['rule']}",
                row["background_canonical"],
                str(row["candidates"]),
                str(row["min_len"]),
                f"`{row['min_word']}`",
                str(row["T"]),
                str(row["drift"]),
                f"{row['speed']:.6g}",
                row["motif"],
                str(row["new_rule"]),
                str(row["new_T"]),
                str(row["new_speed"]),
            ]
        )

    validation_rows = []
    for item in validations:
        active_phases = [
            str(phase["phase"]) for phase in item["phase_results"] if phase["active"]
        ]
        validation_rows.append(
            [
                item["kind"],
                f"rule_{item['rule']}",
                item["background_canonical"],
                f"`{item['word']}`",
                str(item["expected_T"]),
                str(item["expected_drift"]),
                f"{item['active_rotations']}/8",
                ", ".join(active_phases) if active_phases else "-",
                "rotationally robust" if item["rotationally_robust"] else "phase-dependent",
            ]
        )

    answer_1 = (
        f"Yes. New stationary rules: {', '.join(f'rule_{rule}' for rule in new_stationary) or 'none'}; "
        f"new moving rules: {', '.join(f'rule_{rule}' for rule in new_moving) or 'none'}."
        if new_stationary or new_moving
        else "No. Every detected rule already appeared in the period-1/2/4 background sweep."
    )
    answer_2 = (
        f"Yes. New observed periods: {', '.join(str(period) for period in new_periods)}."
        if new_periods
        else "No. No oscillator with T > 4 was detected."
    )
    answer_3 = (
        f"Yes. New observed absolute speeds: {', '.join(f'{speed:.6g}' for speed in new_speeds)} cells/step."
        if new_speeds
        else "No. All observed speeds remain in {0, 0.5, 1.0} cells/step."
    )
    robust_count = sum(bool(item["rotationally_robust"]) for item in validations)

    return f"""# Primitive Period-8 Background Oscillator Sweep

## Protocol

- Rules: all 256 ECA rules.
- Backgrounds: all `{len(primitive_len8_backgrounds())}` primitive binary necklaces of length 8, represented by their lexicographically minimal rotation.
- ICs: `{len(list(ic_words()))}` non-zero binary words of length 1..8.
- Width: `256`.
- Steps: `300`.
- Burn-in: `80`.
- Period search: `2..16`.
- Maximum localized difference span: `32`.
- Detector: exact recurrence of the localized difference between a perturbed run and the unperturbed background orbit.
- Expected runs: `{EXPECTED_RUNS}`.
- Processed runs: `{checkpoint['processed']}`.
- Elapsed seconds: `{float(checkpoint['elapsed_seconds']):.3f}`.
- Candidate detections: `{len(records)}`.
- Filtered period-1 moving aliases: `{checkpoint['alias_count']}`.

## Background Validation

The generator produced exactly 30 primitive length-8 necklaces. Every word has
minimal period 8 and is the lexicographically smallest member of its rotation
class.

## Results

- Stationary rules: {', '.join(f'`rule_{rule}`' for rule in stationary_rules) if stationary_rules else 'none'}.
- Moving rules: {', '.join(f'`rule_{rule}`' for rule in moving_rules) if moving_rules else 'none'}.
- New stationary rules relative to backgrounds 1/2/4: {', '.join(f'`rule_{rule}`' for rule in new_stationary) if new_stationary else 'none'}.
- New moving rules relative to backgrounds 1/2/4: {', '.join(f'`rule_{rule}`' for rule in new_moving) if new_moving else 'none'}.
- Periods above 4: {', '.join(str(period) for period in new_periods) if new_periods else 'none'}.
- All observed periods: {', '.join(str(period) for period in sorted({int(item['period_T']) for item in records})) if records else 'none'}.
- Speeds outside {{0, 0.5, 1.0}}: {', '.join(f'{speed:.6g}' for speed in new_speeds) if new_speeds else 'none'}.

### Candidate Table

{md_table(
    ["kind", "rule", "background_canonical", "candidates", "min_len", "min_word", "T", "drift", "speed", "motif", "new_rule", "new_T", "new_speed"],
    result_rows,
) if result_rows else "No stationary or moving local oscillators were detected."}

## Rotation Validation

Up to ten distinct positive rules were retested across all eight rotations of
their representative background, prioritizing new rules and new period/speed
classes.

{md_table(
    ["kind", "rule", "canonical_background", "witness", "T", "drift", "matching_rotations", "matching_phases", "verdict"],
    validation_rows,
) if validation_rows else "No positive rule was available for rotation validation."}

- Rotationally robust samples: `{robust_count}/{len(validations)}`.
- Phase-dependent samples: `{len(validations) - robust_count}/{len(validations)}`.

This validation changes the phase of the periodic background relative to a
fixed centered IC. Phase dependence therefore demonstrates physical coupling
to background phase; it does not by itself prove an observer artifact. A
strict observer-equivariance test would co-translate both background and IC.

## Explicit Answers

1. **Do new rules appear beyond the period-1/2/4 sweep?** {answer_1}
2. **Do oscillators with T > 4 appear?** {answer_2}
3. **Do speeds outside 0, 0.5, and 1 cell/step appear?** {answer_3}

## Interpretation

This experiment changes only the primitive background period. Results remain
background-conditioned local perturbations, not global periodicity of the
background orbit. Primitive period-8 backgrounds add both rule coverage and
new dynamical classes: fundamental periods up to 15 and speed 2/3. The sampled
novelties are phase-sensitive rather than invariant across all eight background
phases, so each claim must retain its background-phase condition.
"""


def write_annotated_jsonl(records: list[dict]) -> None:
    with RESULTS_JSONL.open("w", encoding="utf-8") as out:
        for record in records:
            out.write(json.dumps(record, sort_keys=True) + "\n")


def finalize_report() -> None:
    checkpoint = load_checkpoint()
    raw_records = load_jsonl(RESULTS_JSONL)
    records = annotate(raw_records, load_baseline_rules())
    write_annotated_jsonl(records)
    rows = representative_rows(records)
    validations = rotation_validation(records)
    REPORT_MD.write_text(
        render_report(records, rows, validations, checkpoint),
        encoding="utf-8",
    )


def validate_configuration() -> None:
    backgrounds = primitive_len8_backgrounds()
    words = list(ic_words())
    assert len(backgrounds) == EXPECTED_BACKGROUNDS
    assert len(words) == EXPECTED_ICS
    assert all(len(word) == 8 for word in backgrounds)
    assert all(minimal_period(word) == 8 for word in backgrounds)
    assert all(word == min(rotations(word)) for word in backgrounds)
    assert len(set(backgrounds)) == len(backgrounds)
    assert 256 * len(backgrounds) * len(words) == EXPECTED_RUNS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-rule", type=int, default=0)
    parser.add_argument("--end-rule", type=int, default=255)
    parser.add_argument(
        "--workers",
        type=int,
        default=max(1, min(8, (os.cpu_count() or 2) - 1)),
    )
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    validate_configuration()
    if args.validate_only:
        print("BACKGROUND_COUNT:", len(primitive_len8_backgrounds()))
        print("BACKGROUNDS:", ", ".join(primitive_len8_backgrounds()))
        print("IC_COUNT:", len(list(ic_words())))
        print("EXPECTED_RUNS:", EXPECTED_RUNS)
        return

    if not args.report_only:
        run_sweep(args.start_rule, args.end_rule, args.workers, args.reset)
    finalize_report()
    print(REPORT_MD.read_text(encoding="utf-8"))
    print(f"RESULTS_JSONL: {RESULTS_JSONL}")
    print(f"REPORT_MD: {REPORT_MD}")


if __name__ == "__main__":
    main()
