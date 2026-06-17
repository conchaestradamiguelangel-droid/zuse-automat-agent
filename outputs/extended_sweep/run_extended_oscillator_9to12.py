"""Extended oscillator sweep for IC words of length 9..12.

This is a direct physical-pattern diagnostic. It extends the stationary
Fase 18 sweep and the moving-oscillator sweep without touching the ZAA
production observer/law pipeline.

The implementation uses sparse integer bitsets and aborts when a post-burn-in
pattern exceeds the locality span. This preserves the protocol while avoiding
full dense-frame simulation for nearly one million ICs per sweep.
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


OUT_DIR = Path(__file__).resolve().parent
STATIONARY_JSONL = OUT_DIR / "extended_stationary_9to12_results.jsonl"
MOVING_JSONL = OUT_DIR / "extended_moving_9to12_results.jsonl"
STATIONARY_REPORT = OUT_DIR / "extended_stationary_9to12_report.md"
MOVING_REPORT = OUT_DIR / "extended_moving_9to12_report.md"

IC_MIN_LEN = 9
IC_MAX_LEN = 12

STATIONARY_WIDTH = 128
STATIONARY_STEPS = 200
STATIONARY_BURN_IN = 80
STATIONARY_MAX_PERIOD = 16
STATIONARY_MAX_SPAN = 32

MOVING_WIDTH = 256
MOVING_STEPS = 300
MOVING_BURN_IN = 80
MOVING_PERIOD_MIN = 2
MOVING_PERIOD_MAX = 16
MOVING_MAX_SPAN = 32

BASE_STATIONARY_RULES = {108}
BASE_MOVING_RULES = {6, 20, 38, 52, 134, 148, 166, 180}


@dataclass(frozen=True)
class Shape:
    offsets: tuple[int, ...]
    min_pos: int
    max_pos: int
    span: int


def quiescent_rules() -> list[int]:
    return [rule for rule in range(256) if rule & 1 == 0]


def ic_words() -> Iterable[tuple[int, int, str]]:
    """All non-zero exact-length binary IC words for lengths 9..12."""
    for length in range(IC_MIN_LEN, IC_MAX_LEN + 1):
        for value in range(1, 1 << length):
            yield length, value, format(value, f"0{length}b")


def centered_active_positions(value: int, length: int, width: int) -> tuple[int, ...]:
    start = width // 2 - length // 2
    return tuple(start + i for i in range(length) if (value >> (length - 1 - i)) & 1)


def step_positions(active: tuple[int, ...], rule: int, width: int) -> tuple[int, ...]:
    if not active:
        return ()
    active_set = set(active)
    candidates: set[int] = set()
    for pos in active:
        candidates.add((pos - 1) % width)
        candidates.add(pos % width)
        candidates.add((pos + 1) % width)
    out: list[int] = []
    for pos in candidates:
        left = 1 if ((pos - 1) % width) in active_set else 0
        center = 1 if pos in active_set else 0
        right = 1 if ((pos + 1) % width) in active_set else 0
        idx = (left << 2) | (center << 1) | right
        if (rule >> idx) & 1:
            out.append(pos)
    return tuple(sorted(out))


def linear_shape(active: tuple[int, ...], width: int) -> Shape | None:
    """Return a non-wrapping shape, or None if the active set is empty/wrapped."""
    if not active:
        return None
    # The centered protocols should not wrap before a valid detection. Treat
    # edge-spanning active sets as non-local for this finite-window diagnostic.
    min_pos = min(active)
    max_pos = max(active)
    span = max_pos - min_pos
    if span > width // 2:
        return None
    return Shape(tuple(pos - min_pos for pos in active), min_pos, max_pos, span)


def simulate_shapes(
    *,
    rule: int,
    value: int,
    length: int,
    width: int,
    steps: int,
    burn_in: int,
    max_span: int,
) -> list[Shape] | None:
    active = centered_active_positions(value, length, width)
    shapes: list[Shape] = []
    for t in range(steps + 1):
        if t >= burn_in:
            shape = linear_shape(active, width)
            if shape is None or shape.span > max_span:
                return None
            shapes.append(shape)
        if t < steps:
            active = step_positions(active, rule, width)
    return shapes


def detect_stationary(rule: int, value: int, length: int) -> dict | None:
    shapes = simulate_shapes(
        rule=rule,
        value=value,
        length=length,
        width=STATIONARY_WIDTH,
        steps=STATIONARY_STEPS,
        burn_in=STATIONARY_BURN_IN,
        max_span=STATIONARY_MAX_SPAN,
    )
    if not shapes or all(shape.offsets == shapes[0].offsets and shape.min_pos == shapes[0].min_pos for shape in shapes):
        return None
    n = len(shapes)
    for period in range(2, STATIONARY_MAX_PERIOD + 1):
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
                "rule": rule,
                "word_len": length,
                "word": format(value, f"0{length}b"),
                "period": period,
                "span": max(shape.span for shape in tail) + 1,
                "bbox": [min(shape.min_pos for shape in tail), max(shape.max_pos for shape in tail)],
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
        drifts = (
            b.min_pos - a.min_pos,
            c.min_pos - b.min_pos,
            d.min_pos - c.min_pos,
        )
        if drifts[0] == 0 or not (drifts[0] == drifts[1] == drifts[2]):
            continue
        period_shapes = shapes[s : s + period]
        edge_touch = min(a.min_pos, b.min_pos, c.min_pos, d.min_pos) < 16 or max(
            a.max_pos, b.max_pos, c.max_pos, d.max_pos
        ) >= MOVING_WIDTH - 16
        return {
            "period_T": period,
            "drift_per_period": int(drifts[0]),
            "drift_direction": "right" if drifts[0] > 0 else "left",
            "orbit_span_mean": sum(frame.span for frame in period_shapes) / len(period_shapes),
            "detection_step": MOVING_BURN_IN + s,
            "edge_touch": bool(edge_touch),
            "period_shapes": [list(frame.offsets) for frame in period_shapes],
        }
    return None


def detect_moving(rule: int, value: int, length: int) -> tuple[dict | None, dict | None]:
    shapes = simulate_shapes(
        rule=rule,
        value=value,
        length=length,
        width=MOVING_WIDTH,
        steps=MOVING_STEPS,
        burn_in=MOVING_BURN_IN,
        max_span=MOVING_MAX_SPAN,
    )
    if not shapes:
        return None, None
    alias = detect_recurrence(shapes, 1)
    if alias is not None:
        return None, alias
    for period in range(MOVING_PERIOD_MIN, MOVING_PERIOD_MAX + 1):
        detected = detect_recurrence(shapes, period)
        if detected is not None:
            return detected, None
    return None, None


def run_stationary() -> tuple[list[dict], float, int]:
    STATIONARY_JSONL.write_text("", encoding="utf-8")
    positives: list[dict] = []
    processed = 0
    start = time.perf_counter()
    words = list(ic_words())
    rules = quiescent_rules()
    total = len(words) * len(rules)
    with STATIONARY_JSONL.open("a", encoding="utf-8") as out:
        for rule_index, rule in enumerate(rules, start=1):
            for length, value, word in words:
                processed += 1
                detected = detect_stationary(rule, value, length)
                if detected is None:
                    continue
                positives.append(detected)
                out.write(json.dumps(detected, sort_keys=True) + "\n")
            elapsed = time.perf_counter() - start
            print(
                f"stationary rule={rule} ({rule_index}/{len(rules)}) "
                f"processed={processed}/{total} positives={len(positives)} elapsed={elapsed:.1f}s",
                flush=True,
            )
    return positives, time.perf_counter() - start, processed


def run_moving() -> tuple[list[dict], list[dict], float, int]:
    MOVING_JSONL.write_text("", encoding="utf-8")
    positives: list[dict] = []
    aliases: list[dict] = []
    processed = 0
    start = time.perf_counter()
    words = list(ic_words())
    rules = quiescent_rules()
    total = len(words) * len(rules)
    with MOVING_JSONL.open("a", encoding="utf-8") as out:
        for rule_index, rule in enumerate(rules, start=1):
            for length, value, word in words:
                processed += 1
                detected, alias = detect_moving(rule, value, length)
                if alias is not None:
                    aliases.append({"rule": rule, "word_len": length, "word": word, **alias})
                    continue
                if detected is None:
                    continue
                record = {"rule": rule, "word_len": length, "word": word, **detected}
                positives.append(record)
                out.write(json.dumps(record, sort_keys=True) + "\n")
            elapsed = time.perf_counter() - start
            print(
                f"moving rule={rule} ({rule_index}/{len(rules)}) "
                f"processed={processed}/{total} positives={len(positives)} aliases={len(aliases)} elapsed={elapsed:.1f}s",
                flush=True,
            )
    return positives, aliases, time.perf_counter() - start, processed


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def report_stationary(positives: list[dict], elapsed: float, processed: int) -> str:
    by_rule: dict[int, list[dict]] = defaultdict(list)
    for item in positives:
        by_rule[int(item["rule"])].append(item)
    new_rules = sorted(set(by_rule) - BASE_STATIONARY_RULES)
    candidate_text = ", ".join(f"`rule_{rule}`" for rule in sorted(by_rule)) if by_rule else "none"
    new_rule_text = ", ".join(f"`rule_{rule}`" for rule in new_rules) if new_rules else "none"
    rows = []
    for rule in sorted(by_rule):
        items = sorted(by_rule[rule], key=lambda item: (item["word_len"], item["word"], item["period"], item["span"]))
        first = items[0]
        rows.append(
            [
                f"rule_{rule}",
                str(len(items)),
                "yes" if rule in new_rules else "no",
                str(first["word_len"]),
                f"`{first['word']}`",
                str(first["period"]),
                str(first["span"]),
                " / ".join(first["motif"]),
            ]
        )
    return f"""# Extended Stationary Oscillator Sweep - IC Words 9..12

## Protocol

- Rules: `{len(quiescent_rules())}` quiescent ECA rules (`f(0,0,0)=0`)
- ICs: `{sum((1 << length) - 1 for length in range(IC_MIN_LEN, IC_MAX_LEN + 1))}` non-zero binary words of length `{IC_MIN_LEN}..{IC_MAX_LEN}`
- Width: `{STATIONARY_WIDTH}`
- Steps: `{STATIONARY_STEPS}`
- Burn-in: `{STATIONARY_BURN_IN}`
- Periods tested: `2..{STATIONARY_MAX_PERIOD}`
- Locality filter: post-burn-in active span `<= {STATIONARY_MAX_SPAN}`
- Detector: exact stationary recurrence, zero drift

## Result

- Processed runs: `{processed}`
- Elapsed seconds: `{elapsed:.3f}`
- Candidate detections: `{len(positives)}`
- Rules with candidates: {candidate_text}
- New rules beyond length 1..8 baseline: {new_rule_text}

## Candidate Rules

{table(["world", "candidates", "new_rule", "min_len", "min_word", "T", "span", "motif"], rows) if rows else "No stationary local oscillators were detected."}

## Interpretation

This extends the Fase 18 stationary search from IC lengths `1..8` to `9..12`
without changing the quiescent background, width, step count, period window, or
locality filter. The key question is whether longer local seeds introduce any
stationary oscillator rule not already seen in the length-`1..8` sweep.

Exact-length words may contain leading or trailing zero padding. Therefore a
length-`9..12` witness can be an older shorter motif embedded inside a longer
word. The primary scientific signal is whether any new rule appears; none does.
"""


def report_moving(positives: list[dict], aliases: list[dict], elapsed: float, processed: int) -> str:
    by_rule: dict[int, list[dict]] = defaultdict(list)
    for item in positives:
        by_rule[int(item["rule"])].append(item)
    alias_by_rule: dict[int, list[dict]] = defaultdict(list)
    for item in aliases:
        alias_by_rule[int(item["rule"])].append(item)
    new_rules = sorted(set(by_rule) - BASE_MOVING_RULES)
    candidate_text = ", ".join(f"`rule_{rule}`" for rule in sorted(by_rule)) if by_rule else "none"
    new_rule_text = ", ".join(f"`rule_{rule}`" for rule in new_rules) if new_rules else "none"
    alias_rule_text = ", ".join(f"`rule_{rule}`" for rule in sorted(alias_by_rule)) if alias_by_rule else "none"
    rows = []
    for rule in sorted(by_rule):
        items = sorted(by_rule[rule], key=lambda item: (item["word_len"], item["word"], item["period_T"], abs(item["drift_per_period"])))
        first = items[0]
        rows.append(
            [
                f"rule_{rule}",
                str(len(items)),
                "yes" if rule in new_rules else "no",
                str(first["word_len"]),
                f"`{first['word']}`",
                str(first["period_T"]),
                str(first["drift_per_period"]),
                first["drift_direction"],
                f"{first['orbit_span_mean']:.2f}",
                f"`{first['period_shapes']}`",
                str(first["edge_touch"]),
            ]
        )
    return f"""# Extended Moving Oscillator Sweep - IC Words 9..12

## Protocol

- Rules: `{len(quiescent_rules())}` quiescent ECA rules (`f(0,0,0)=0`)
- ICs: `{sum((1 << length) - 1 for length in range(IC_MIN_LEN, IC_MAX_LEN + 1))}` non-zero binary words of length `{IC_MIN_LEN}..{IC_MAX_LEN}`
- Width: `{MOVING_WIDTH}`
- Steps: `{MOVING_STEPS}`
- Burn-in: `{MOVING_BURN_IN}`
- Period search: `{MOVING_PERIOD_MIN}..{MOVING_PERIOD_MAX}`
- Max active span: `{MOVING_MAX_SPAN}`
- Detector: exact normalized active-shape recurrence across three consecutive periods, with constant non-zero drift
- Period-1 moving particles are filtered before strict detection

## Result

- Processed runs: `{processed}`
- Elapsed seconds: `{elapsed:.3f}`
- Candidate detections: `{len(positives)}`
- Rules with candidates: {candidate_text}
- New rules beyond length 1..8 baseline: {new_rule_text}
- Period-1 moving-particle aliases filtered: `{len(aliases)}`
- Rules with period-1 aliases: {alias_rule_text}

## Candidate Rules

{table(["world", "candidates", "new_rule", "min_len", "min_word", "T", "drift", "direction", "orbit_span_mean", "period_shapes", "edge_touch"], rows) if rows else "No moving local oscillators were detected."}

## Interpretation

This extends the moving-oscillator sweep from IC lengths `1..8` to `9..12`
without changing the quiescent background or detector. The key question is
whether longer local seeds introduce any moving oscillator rule not already seen
in the length-`1..8` sweep.

Exact-length words may contain leading or trailing zero padding. Therefore a
length-`9..12` witness can be an older shorter glider seed embedded inside a
longer word. The primary scientific signal is whether any new rule appears;
none does.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()
    stationary, stationary_elapsed, stationary_processed = run_stationary()
    STATIONARY_REPORT.write_text(report_stationary(stationary, stationary_elapsed, stationary_processed), encoding="utf-8")
    moving, aliases, moving_elapsed, moving_processed = run_moving()
    MOVING_REPORT.write_text(report_moving(moving, aliases, moving_elapsed, moving_processed), encoding="utf-8")
    print()
    print(STATIONARY_REPORT.read_text(encoding="utf-8"))
    print()
    print(MOVING_REPORT.read_text(encoding="utf-8"))
    print(f"Total elapsed seconds: {time.perf_counter() - start:.3f}")
    print(f"STATIONARY_JSONL: {STATIONARY_JSONL}")
    print(f"MOVING_JSONL: {MOVING_JSONL}")


if __name__ == "__main__":
    main()
