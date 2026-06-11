"""Search for moving local oscillators in quiescent ECA rules.

This is a direct physical-pattern diagnostic. It deliberately does not use the
ZAA observer, dedup, or cycle-law pipeline.
"""

from __future__ import annotations

import json
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from zaa.eca import rule_bits, step_with_bits


WIDTH = 256
STEPS = 300
BURN_IN = 80
MAX_SPAN = 32
PERIOD_MIN = 2
PERIOD_MAX = 16
IC_MAX_LEN = 8

OUT_DIR = Path(__file__).resolve().parent
RESULTS_PATH = OUT_DIR / "moving_oscillator_results.jsonl"
REPORT_PATH = OUT_DIR / "moving_oscillator_report.md"


@dataclass(frozen=True)
class FrameShape:
    offsets: tuple[int, ...]
    min_pos: int
    max_pos: int
    centroid: float
    span: int


def quiescent_rules() -> list[int]:
    """ECA rules where f(0,0,0)=0."""
    return [rule for rule in range(256) if rule & 1 == 0]


def ic_words(max_len: int = IC_MAX_LEN) -> Iterable[str]:
    """All non-zero binary words of exact length 1..max_len."""
    for length in range(1, max_len + 1):
        for value in range(1, 2**length):
            yield format(value, f"0{length}b")


def centered_initial_state(word: str, width: int = WIDTH) -> np.ndarray:
    state = np.zeros(width, dtype=np.uint8)
    start = width // 2 - len(word) // 2
    for i, bit in enumerate(word):
        if bit == "1":
            state[start + i] = 1
    return state


def simulate(initial_state: np.ndarray, rule: int, steps: int = STEPS) -> np.ndarray:
    frames = np.empty((steps + 1, initial_state.size), dtype=np.uint8)
    frames[0] = initial_state
    current = initial_state
    bits = rule_bits(rule)
    for t in range(1, steps + 1):
        current = step_with_bits(current, bits)
        frames[t] = current
    return frames


def extract_shapes(frames: np.ndarray) -> list[FrameShape] | None:
    shapes: list[FrameShape] = []
    spans: list[int] = []
    for frame in frames[BURN_IN:]:
        active = np.flatnonzero(frame)
        if active.size == 0:
            return None
        min_pos = int(active[0])
        max_pos = int(active[-1])
        span = max_pos - min_pos
        if span > MAX_SPAN:
            return None
        offsets = tuple(int(x - min_pos) for x in active)
        shapes.append(
            FrameShape(
                offsets=offsets,
                min_pos=min_pos,
                max_pos=max_pos,
                centroid=float(np.mean(active)),
                span=span,
            )
        )
        spans.append(span)
    if spans and all(span == 0 for span in spans):
        return None
    return shapes


def detect_recurrence(shapes: list[FrameShape], period: int) -> dict | None:
    n = len(shapes)
    # Need four phase-aligned frames to prove three consistent drifts.
    for s in range(0, n - 3 * period):
        a = shapes[s]
        b = shapes[s + period]
        c = shapes[s + 2 * period]
        d = shapes[s + 3 * period]
        if not (a.offsets == b.offsets == c.offsets == d.offsets):
            continue

        drifts = (
            b.min_pos - a.min_pos,
            c.min_pos - b.min_pos,
            d.min_pos - c.min_pos,
        )
        if drifts[0] == 0 or not (drifts[0] == drifts[1] == drifts[2]):
            continue
        if abs(drifts[0]) < 1:
            continue

        span_mean = float(np.mean([a.span, b.span, c.span, d.span]))
        edge_touch = min(a.min_pos, b.min_pos, c.min_pos, d.min_pos) < 16 or max(
            a.max_pos, b.max_pos, c.max_pos, d.max_pos
        ) >= WIDTH - 16
        period_frames = shapes[s : s + period]
        return {
            "period_T": period,
            "drift_per_period": int(drifts[0]),
            "drift_direction": "right" if drifts[0] > 0 else "left",
            "span_mean": span_mean,
            "orbit_span_mean": float(np.mean([frame.span for frame in period_frames])),
            "detection_step": BURN_IN + s,
            "edge_touch": bool(edge_touch),
            "shape_offsets": list(a.offsets),
            "period_shapes": [list(frame.offsets) for frame in period_frames],
        }
    return None


def detect_moving_oscillator(shapes: list[FrameShape]) -> tuple[dict | None, dict | None]:
    """Return a strict moving oscillator and optional period-1 alias.

    Period-1 moving particles/gliders trivially recur at T=2, T=3, etc. They
    are useful controls but not internal-period moving oscillators, so they are
    filtered before the T=2..16 search.
    """
    period1_alias = detect_recurrence(shapes, 1)
    if period1_alias is not None:
        return None, period1_alias
    for period in range(PERIOD_MIN, PERIOD_MAX + 1):
        detected = detect_recurrence(shapes, period)
        if detected is not None:
            return detected, None
    return None, None


def run_sweep() -> tuple[list[dict], list[dict], float, int]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text("", encoding="utf-8")

    rules = quiescent_rules()
    words = list(ic_words())
    total_runs = len(rules) * len(words)
    positives: list[dict] = []
    aliases: list[dict] = []
    processed = 0
    start = time.perf_counter()

    with RESULTS_PATH.open("a", encoding="utf-8") as out:
        for rule_index, rule in enumerate(rules, start=1):
            for word in words:
                processed += 1
                initial = centered_initial_state(word)
                frames = simulate(initial, rule)
                shapes = extract_shapes(frames)
                if shapes is None:
                    continue
                detected, alias = detect_moving_oscillator(shapes)
                if alias is not None:
                    aliases.append({"rule": rule, "ic_word": word, **alias})
                    continue
                if detected is None:
                    continue
                record = {
                    "rule": rule,
                    "ic_word": word,
                    **detected,
                }
                positives.append(record)
                out.write(json.dumps(record, sort_keys=True) + "\n")
                out.flush()
            elapsed = time.perf_counter() - start
            print(
                f"processed_rules={rule_index}/{len(rules)} "
                f"processed_runs={processed}/{total_runs} "
                f"positives={len(positives)} period1_aliases={len(aliases)} elapsed={elapsed:.1f}s",
                flush=True,
            )

    return positives, aliases, time.perf_counter() - start, processed


def report(positives: list[dict], aliases: list[dict], elapsed: float, processed: int) -> str:
    total_expected = len(quiescent_rules()) * len(list(ic_words()))
    by_rule: dict[int, list[dict]] = defaultdict(list)
    for item in positives:
        by_rule[int(item["rule"])].append(item)
    alias_by_rule: dict[int, list[dict]] = defaultdict(list)
    for item in aliases:
        alias_by_rule[int(item["rule"])].append(item)

    lines = [
        "# Moving Oscillator Sweep",
        "",
        "Direct physical search for local oscillators that repeat after a period",
        "while translating by a fixed non-zero displacement.",
        "",
        "## Protocol",
        "",
        f"- Rules: {len(quiescent_rules())} quiescent ECA rules (`f(0,0,0)=0`)",
        f"- ICs: {len(list(ic_words()))} non-zero binary words of length 1..{IC_MAX_LEN}",
        "  (502 exact-length non-zero words; 510 is the inclusive count before",
        "  excluding the all-zero word at each length.)",
        f"- Width: {WIDTH}",
        f"- Steps: {STEPS}",
        f"- Burn-in: {BURN_IN}",
        f"- Period search: {PERIOD_MIN}..{PERIOD_MAX}",
        f"- Max active span: {MAX_SPAN}",
        "- Detector: exact normalized active shape recurrence across three",
        "  consecutive periods, with constant non-zero drift.",
        "- Period-1 moving particles are filtered before the T=2..16 search,",
        "  because otherwise they alias as trivial moving oscillators at every",
        "  multiple period.",
        "",
        "## Results",
        "",
        f"- Total expected runs: {total_expected}",
        f"- Processed runs: {processed}",
        f"- Elapsed seconds: {elapsed:.3f}",
        f"- Candidate detections: {len(positives)}",
        f"- Rules with candidates: {sorted(by_rule)}",
        f"- Period-1 moving-particle aliases filtered: {len(aliases)}",
        f"- Rules with period-1 aliases: {sorted(alias_by_rule)}",
        "",
    ]

    if positives:
        lines.extend(
            [
                "| rule | candidates | minimal IC | T | drift | direction | orbit_span_mean | period_shapes | edge_touch |",
                "| --- | ---: | --- | ---: | ---: | --- | ---: | --- | --- |",
            ]
        )
        for rule in sorted(by_rule):
            candidates = sorted(
                by_rule[rule],
                key=lambda item: (len(item["ic_word"]), item["ic_word"], item["period_T"], abs(item["drift_per_period"])),
            )
            first = candidates[0]
            lines.append(
                f"| {rule} | {len(candidates)} | `{first['ic_word']}` | "
                f"{first['period_T']} | {first['drift_per_period']} | "
                f"{first['drift_direction']} | {first['orbit_span_mean']:.2f} | "
                f"`{first['period_shapes']}` | "
                f"{first['edge_touch']} |"
            )
        lines.append("")
    else:
        lines.append("No moving local oscillators were detected under this protocol.")
        lines.append("")

    moving_rules = sorted(by_rule)
    moving_text = ", ".join(f"`rule_{rule}`" for rule in moving_rules) if moving_rules else "ninguna"
    alias_text = ", ".join(f"`rule_{rule}`" for rule in sorted(alias_by_rule)) if alias_by_rule else "none"
    conclusion = (
        "moving oscillators exist in ECA under this protocol"
        if moving_rules
        else "no moving oscillators were found under this protocol"
    )
    lines.extend(
        [
            "## Comparison With Fase 18",
            "",
            "- Fase 18 (stationary local oscillator): only `rule_108` produced",
            "  stationary local period-2 oscillators under the quiescent protocol.",
            f"- Fase moving: {moving_text}.",
            f"- Period-1 moving particles/gliders filtered before strict detection: {alias_text}.",
            f"- Conclusion: {conclusion}.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    positives, aliases, elapsed, processed = run_sweep()
    text = report(positives, aliases, elapsed, processed)
    REPORT_PATH.write_text(text, encoding="utf-8")
    print()
    print(text)
    print(f"RESULTS_JSONL: {RESULTS_PATH}")
    print(f"REPORT_MD: {REPORT_PATH}")


if __name__ == "__main__":
    main()
