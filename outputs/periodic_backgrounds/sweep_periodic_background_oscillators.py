"""Search local oscillators on non-zero periodic ECA backgrounds.

This is a direct physical-pattern diagnostic, not a ZAA observer/law run.

Unlike the quiescent-zero sweeps, this script measures the *difference* between
an IC-perturbed run and the unperturbed periodic-background orbit. A hit is
therefore a localized perturbation that repeats or travels relative to its
background, not a globally periodic background being mislabeled as a particle.
"""

from __future__ import annotations

import argparse
import json
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


OUT_DIR = Path(__file__).resolve().parent
RESULTS_JSONL = OUT_DIR / "periodic_background_oscillator_results.jsonl"
REPORT_MD = OUT_DIR / "periodic_background_oscillator_report.md"

WIDTH = 256
STEPS = 300
BURN_IN = 80
MAX_SPAN = 32
PERIOD_MIN = 2
PERIOD_MAX = 16
IC_MAX_LEN = 8
BACKGROUND_PERIODS = (1, 2, 4)

BASE_STATIONARY_RULES = {108}
BASE_MOVING_RULES = {6, 20, 38, 52, 134, 148, 166, 180}


@dataclass(frozen=True)
class Shape:
    offsets: tuple[int, ...]
    min_pos: int
    max_pos: int
    span: int


def eca_step_state(state: tuple[int, ...], rule: int) -> tuple[int, ...]:
    active = set(state)
    out = []
    for pos in range(WIDTH):
        left = 1 if ((pos - 1) % WIDTH) in active else 0
        center = 1 if pos in active else 0
        right = 1 if ((pos + 1) % WIDTH) in active else 0
        idx = (left << 2) | (center << 1) | right
        if (rule >> idx) & 1:
            out.append(pos)
    return tuple(out)


def eca_step_diff(diff: tuple[int, ...], bg_now: tuple[int, ...], bg_next: tuple[int, ...], rule: int) -> tuple[int, ...]:
    """Sparse update of perturbation difference relative to background orbit."""
    if not diff:
        return ()
    diff_set = set(diff)
    bg_set = set(bg_now)
    bg_next_set = set(bg_next)
    candidates = set()
    for pos in diff:
        candidates.add((pos - 1) % WIDTH)
        candidates.add(pos % WIDTH)
        candidates.add((pos + 1) % WIDTH)
    out = []
    for pos in candidates:
        def bit_at(x: int) -> int:
            return (1 if x in bg_set else 0) ^ (1 if x in diff_set else 0)

        left = bit_at((pos - 1) % WIDTH)
        center = bit_at(pos)
        right = bit_at((pos + 1) % WIDTH)
        idx = (left << 2) | (center << 1) | right
        actual_next = (rule >> idx) & 1
        background_next = 1 if pos in bg_next_set else 0
        if actual_next ^ background_next:
            out.append(pos)
    return tuple(sorted(out))


def background_words() -> list[str]:
    """Unique non-zero tiled backgrounds with exact template lengths 1, 2, and 4."""
    seen: set[tuple[int, ...]] = set()
    words: list[str] = []
    for length in BACKGROUND_PERIODS:
        for value in range(1, 1 << length):
            word = format(value, f"0{length}b")
            active = tuple(i for i in range(WIDTH) if word[i % length] == "1")
            if active in seen:
                continue
            seen.add(active)
            words.append(word)
    return words


def background_state(word: str) -> tuple[int, ...]:
    return tuple(i for i in range(WIDTH) if word[i % len(word)] == "1")


def background_orbit(rule: int, word: str) -> list[tuple[int, ...]]:
    frames = [background_state(word)]
    current = frames[0]
    for _ in range(STEPS):
        current = eca_step_state(current, rule)
        frames.append(current)
    return frames


def ic_words() -> Iterable[tuple[int, int, str]]:
    for length in range(1, IC_MAX_LEN + 1):
        for value in range(1, 1 << length):
            yield length, value, format(value, f"0{length}b")


def initial_diff(word_value: int, word_len: int, bg0: tuple[int, ...]) -> tuple[int, ...]:
    bg_set = set(bg0)
    start = WIDTH // 2 - word_len // 2
    diff = []
    for idx in range(word_len):
        pos = start + idx
        desired = (word_value >> (word_len - 1 - idx)) & 1
        background = 1 if pos in bg_set else 0
        if desired ^ background:
            diff.append(pos)
    return tuple(diff)


def linear_shape(diff: tuple[int, ...]) -> Shape | None:
    if not diff:
        return None
    min_pos = min(diff)
    max_pos = max(diff)
    span = max_pos - min_pos
    if span > WIDTH // 2:
        return None
    return Shape(tuple(pos - min_pos for pos in diff), min_pos, max_pos, span)


def simulate_diff_shapes(rule: int, bg_frames: list[tuple[int, ...]], word_value: int, word_len: int) -> list[Shape] | None:
    diff = initial_diff(word_value, word_len, bg_frames[0])
    if not diff:
        return None
    shapes: list[Shape] = []
    for t in range(STEPS + 1):
        if t >= BURN_IN:
            shape = linear_shape(diff)
            if shape is None or shape.span > MAX_SPAN:
                return None
            shapes.append(shape)
        if t < STEPS:
            diff = eca_step_diff(diff, bg_frames[t], bg_frames[t + 1], rule)
            if not diff and t >= BURN_IN:
                return None
    return shapes


def detect_stationary(shapes: list[Shape]) -> dict | None:
    if all(shape.offsets == shapes[0].offsets and shape.min_pos == shapes[0].min_pos for shape in shapes):
        return None
    n = len(shapes)
    for period in range(PERIOD_MIN, PERIOD_MAX + 1):
        ok = True
        for i in range(n - period):
            a = shapes[i]
            b = shapes[i + period]
            if a.offsets != b.offsets or a.min_pos != b.min_pos:
                ok = False
                break
        if ok:
            tail = shapes[-period:]
            return {
                "kind": "stationary",
                "period_T": period,
                "span": max(shape.span for shape in tail) + 1,
                "motif": ["".join("#" if i in shape.offsets else "." for i in range(shape.span + 1)) for shape in tail],
            }
    return None


def detect_recurrence(shapes: list[Shape], period: int) -> dict | None:
    n = len(shapes)
    for s in range(0, n - 3 * period):
        a = shapes[s]
        b = shapes[s + period]
        c = shapes[s + 2 * period]
        d = shapes[s + 3 * period]
        if not (a.offsets == b.offsets == c.offsets == d.offsets):
            continue
        drifts = (b.min_pos - a.min_pos, c.min_pos - b.min_pos, d.min_pos - c.min_pos)
        if drifts[0] == 0 or not (drifts[0] == drifts[1] == drifts[2]):
            continue
        period_shapes = shapes[s : s + period]
        return {
            "kind": "moving",
            "period_T": period,
            "drift_per_period": int(drifts[0]),
            "drift_direction": "right" if drifts[0] > 0 else "left",
            "orbit_span_mean": sum(shape.span for shape in period_shapes) / len(period_shapes),
            "period_shapes": [list(shape.offsets) for shape in period_shapes],
            "edge_touch": min(a.min_pos, b.min_pos, c.min_pos, d.min_pos) < 16
            or max(a.max_pos, b.max_pos, c.max_pos, d.max_pos) >= WIDTH - 16,
        }
    return None


def detect_moving(shapes: list[Shape]) -> tuple[dict | None, dict | None]:
    alias = detect_recurrence(shapes, 1)
    if alias is not None:
        alias["kind"] = "period1_alias"
        return None, alias
    for period in range(PERIOD_MIN, PERIOD_MAX + 1):
        hit = detect_recurrence(shapes, period)
        if hit is not None:
            return hit, None
    return None, None


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def run_sweep(start_rule: int = 0, end_rule: int = 255, append: bool = False) -> tuple[list[dict], int, float, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    if not append:
        RESULTS_JSONL.write_text("", encoding="utf-8")
    positives: list[dict] = []
    aliases: list[dict] = []
    processed = 0
    start = time.perf_counter()
    rules = list(range(start_rule, end_rule + 1))
    backgrounds = background_words()
    words = list(ic_words())
    total = len(rules) * len(backgrounds) * len(words)
    with RESULTS_JSONL.open("a", encoding="utf-8") as out:
        for rule_index, rule in enumerate(rules, start=1):
            for background in backgrounds:
                bg_frames = background_orbit(rule, background)
                for word_len, word_value, word in words:
                    processed += 1
                    shapes = simulate_diff_shapes(rule, bg_frames, word_value, word_len)
                    if not shapes:
                        continue
                    stationary = detect_stationary(shapes)
                    moving, alias = detect_moving(shapes)
                    if alias is not None:
                        aliases.append({"rule": rule, "background": background, "word_len": word_len, "word": word, **alias})
                    for hit in (stationary, moving):
                        if hit is None:
                            continue
                        record = {"rule": rule, "background": background, "word_len": word_len, "word": word, **hit}
                        positives.append(record)
                        out.write(json.dumps(record, sort_keys=True) + "\n")
            elapsed = time.perf_counter() - start
            print(
                f"rule={rule} ({rule_index}/{len(rules)}) processed={processed}/{total} "
                f"positives={len(positives)} aliases={len(aliases)} elapsed={elapsed:.1f}s",
                flush=True,
            )
    return positives, len(aliases), time.perf_counter() - start, processed


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(positives: list[dict], elapsed: float, processed: int, alias_note: str = "") -> str:
    by_kind_rule: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for item in positives:
        by_kind_rule[(item["kind"], int(item["rule"]))].append(item)
    stationary_rules = sorted(rule for kind, rule in by_kind_rule if kind == "stationary")
    moving_rules = sorted(rule for kind, rule in by_kind_rule if kind == "moving")
    new_stationary = sorted(set(stationary_rules) - BASE_STATIONARY_RULES)
    new_moving = sorted(set(moving_rules) - BASE_MOVING_RULES)

    rows = []
    for (kind, rule), items in sorted(by_kind_rule.items(), key=lambda pair: (pair[0][0], pair[0][1])):
        first = sorted(items, key=lambda item: (len(item["background"]), item["background"], item["word_len"], item["word"], item["period_T"]))[0]
        descriptor = " / ".join(first.get("motif", [])) if kind == "stationary" else str(first.get("period_shapes"))
        rows.append(
            [
                kind,
                f"rule_{rule}",
                str(len(items)),
                first["background"],
                str(first["word_len"]),
                f"`{first['word']}`",
                str(first["period_T"]),
                str(first.get("drift_per_period", 0)),
                descriptor,
            ]
        )

    alias_line = alias_note or "Period-1 moving-particle aliases are filtered before strict moving-oscillator detection; they are not counted as candidates in this report."
    return f"""# Periodic-Background Oscillator Sweep

## Protocol

- Rules: all 256 ECA rules.
- Backgrounds: unique non-zero tiled backgrounds with template length 1, 2, or 4 (`{len(background_words())}` backgrounds).
- ICs: `{len(list(ic_words()))}` non-zero binary words of length 1..8, replacing the centered background window.
- Width: `{WIDTH}`.
- Steps: `{STEPS}`.
- Burn-in: `{BURN_IN}`.
- Period search: `{PERIOD_MIN}..{PERIOD_MAX}`.
- Max perturbation span: `{MAX_SPAN}`.
- Detector: exact recurrence of the localized difference between perturbed run and unperturbed background orbit.

## Result

- Processed runs: `{processed}`
- Elapsed seconds: `{elapsed:.3f}`
- Candidate detections: `{len(positives)}`
- Stationary rules: {', '.join(f'`rule_{rule}`' for rule in stationary_rules) if stationary_rules else 'none'}
- Moving rules: {', '.join(f'`rule_{rule}`' for rule in moving_rules) if moving_rules else 'none'}
- New stationary rules beyond zero-background baseline: {', '.join(f'`rule_{rule}`' for rule in new_stationary) if new_stationary else 'none'}
- New moving rules beyond zero-background baseline: {', '.join(f'`rule_{rule}`' for rule in new_moving) if new_moving else 'none'}
- Alias handling: {alias_line}

## Candidate Rules

{table(["kind", "world", "candidates", "background", "min_len", "min_word", "T", "drift", "motif_or_shapes"], rows) if rows else "No local oscillator perturbations were detected."}

## Interpretation

This opens a different protocol from the quiescent-zero sweeps. Hits are local
perturbations measured relative to a periodic background orbit, so global
background periodicity alone does not count as a local oscillator.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-rule", type=int, default=0)
    parser.add_argument("--end-rule", type=int, default=255)
    parser.add_argument("--append", action="store_true")
    parser.add_argument("--processed-offset", type=int, default=0)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    elapsed = 0.0
    processed = args.processed_offset
    if not args.report_only:
        _new_positives, _alias_count, elapsed, segment_processed = run_sweep(
            start_rule=args.start_rule,
            end_rule=args.end_rule,
            append=args.append,
        )
        processed += segment_processed
    positives = load_jsonl(RESULTS_JSONL)
    alias_note = "Period-1 moving-particle aliases were filtered during detection; alias counts are not central to this periodic-background report."
    REPORT_MD.write_text(render_report(positives, elapsed, processed, alias_note=alias_note), encoding="utf-8")
    print()
    print(REPORT_MD.read_text(encoding="utf-8"))
    print(f"RESULTS_JSONL: {RESULTS_JSONL}")
    print(f"REPORT_MD: {REPORT_MD}")


if __name__ == "__main__":
    main()
