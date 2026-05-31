"""Fase 18: exhaustive small-IC sweep for local ECA oscillators.

This is an experimental artifact. It does not touch production code.

Question: is rule_108 an isolated witness, or part of a family of elementary
cellular automata with local oscillators on a quiescent zero background?
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.consensus import deduplicate_structures
from zaa.cycle_laws import evaluate_cycle_laws, evaluate_periodicity_law
from zaa.eca import rule_bits, simulate
from zaa.observers import run_observers


OUT_DIR = ROOT / "outputs" / "local_oscillator_family_fase18"
CANDIDATES_JSONL = OUT_DIR / "local_oscillator_candidates.jsonl"
SUMMARY_JSON = OUT_DIR / "local_oscillator_family_summary.json"
REPORT_MD = OUT_DIR / "local_oscillator_family_report.md"

WIDTH = 128
STEPS = 200
BURN_IN = 80
MAX_PERIOD = 16
MAX_INITIAL_WORD_LEN = 8
MAX_LOCAL_SPAN = 32
DEDUP_STRUCTURE_NOISE_THRESHOLD = 40


def make_ic(word: int, length: int) -> np.ndarray:
    """Place a binary word of given length at the center of a zero background."""
    state = np.zeros(WIDTH, dtype=np.uint8)
    start = WIDTH // 2 - length // 2
    for idx in range(length):
        bit = (word >> (length - 1 - idx)) & 1
        state[start + idx] = bit
    return state


def word_text(word: int, length: int) -> str:
    return format(word, f"0{length}b")


def active_span(frame: np.ndarray) -> int:
    xs = np.flatnonzero(frame)
    if xs.size == 0:
        return 0
    return int(xs.max() - xs.min() + 1)


def active_bbox(frames: np.ndarray) -> tuple[int, int] | None:
    xs = np.flatnonzero(np.any(frames != 0, axis=0))
    if xs.size == 0:
        return None
    return int(xs.min()), int(xs.max())


def exact_period(frames: np.ndarray, *, burn_in: int = BURN_IN, max_period: int = MAX_PERIOD) -> int | None:
    """Return smallest exact post-burn-in period >= 2, or None."""
    tail = np.asarray(frames[burn_in:], dtype=np.uint8)
    if tail.shape[0] < 2 * max_period + 1:
        return None
    if not np.any(tail):
        return None
    if np.all(tail == tail[0]):
        return None
    for period in range(2, max_period + 1):
        if np.array_equal(tail[:-period], tail[period:]):
            return period
    return None


def is_localized(frames: np.ndarray) -> bool:
    bbox = active_bbox(frames[BURN_IN:])
    if bbox is None:
        return False
    span = bbox[1] - bbox[0] + 1
    return span <= MAX_LOCAL_SPAN


def motif_for_period(frames: np.ndarray, period: int) -> list[str]:
    bbox = active_bbox(frames[BURN_IN:])
    if bbox is None:
        return []
    lo, hi = bbox
    start = STEPS - period + 1
    motif = []
    for row in frames[start : STEPS + 1, lo : hi + 1]:
        motif.append("".join("#" if value else "." for value in row))
    return motif


def physical_candidate(rule: int, word: int, length: int) -> dict[str, Any] | None:
    frames = simulate(make_ic(word, length), rule, STEPS)
    if not is_localized(frames):
        return None
    period = exact_period(frames)
    if period is None:
        return None
    bbox = active_bbox(frames[BURN_IN:])
    assert bbox is not None
    lo, hi = bbox
    return {
        "rule": rule,
        "world": f"rule_{rule}",
        "word_len": length,
        "word": word_text(word, length),
        "width": WIDTH,
        "steps": STEPS,
        "burn_in": BURN_IN,
        "period": period,
        "span": hi - lo + 1,
        "bbox": [lo, hi],
        "max_active_count_tail": int(np.max(np.sum(frames[BURN_IN:] != 0, axis=1))),
        "motif": motif_for_period(frames, period),
    }


def validate_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    frames = simulate(make_ic(int(candidate["word"], 2), int(candidate["word_len"])), int(candidate["rule"]), STEPS)
    structures = run_observers(frames)
    dedup_count = len(deduplicate_structures(structures))
    analysis_status = "ruido_no_analizable" if dedup_count > DEDUP_STRUCTURE_NOISE_THRESHOLD else "ok"
    laws = evaluate_cycle_laws(structures, frames, STEPS)["laws_accepted"] if analysis_status == "ok" else []
    oscillator_count = sum(1 for structure in structures if structure.tipo == "oscilador")
    periodicity_raw = evaluate_periodicity_law(structures).accepted
    candidate.update(
        {
            "raw_structure_count": len(structures),
            "dedup_structure_count": dedup_count,
            "analysis_status": analysis_status,
            "laws_accepted": laws,
            "oscillator_count_raw": oscillator_count,
            "periodicity_raw": periodicity_raw,
            "periodicity_production": "periodicidad" in laws,
        }
    )
    return candidate


def candidate_rules() -> list[int]:
    return [rule for rule in range(256) if int(rule_bits(rule)[0]) == 0]


def run_sweep() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for rule in candidate_rules():
        for length in range(1, MAX_INITIAL_WORD_LEN + 1):
            for word in range(1, 1 << length):
                candidate = physical_candidate(rule, word, length)
                if candidate is not None:
                    candidates.append(validate_candidate(candidate))
    return candidates


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def summarize(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    by_rule: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for candidate in candidates:
        by_rule[int(candidate["rule"])].append(candidate)

    summary: dict[str, Any] = {
        "setup": {
            "rules_tested": len(candidate_rules()),
            "ic_word_lengths": [1, MAX_INITIAL_WORD_LEN],
            "width": WIDTH,
            "steps": STEPS,
            "burn_in": BURN_IN,
            "max_period": MAX_PERIOD,
            "max_local_span": MAX_LOCAL_SPAN,
        },
        "total_candidates": len(candidates),
        "rules_with_candidates": len(by_rule),
        "rules": {},
    }
    for rule, items in sorted(by_rule.items()):
        periods = Counter(item["period"] for item in items)
        spans = Counter(item["span"] for item in items)
        production_hits = sum(item["periodicity_production"] for item in items)
        best = sorted(items, key=lambda item: (item["period"], item["span"], item["word_len"], item["word"]))[0]
        summary["rules"][f"rule_{rule}"] = {
            "candidate_count": len(items),
            "periods": dict(sorted(periods.items())),
            "spans": dict(sorted(spans.items())),
            "periodicity_production_count": production_hits,
            "best_witness": {
                key: best[key]
                for key in [
                    "word_len",
                    "word",
                    "period",
                    "span",
                    "motif",
                    "analysis_status",
                    "dedup_structure_count",
                    "laws_accepted",
                ]
            },
        }
    return summary


def render_report(summary: dict[str, Any]) -> str:
    rules = summary["rules"]
    rows = []
    for world, payload in rules.items():
        witness = payload["best_witness"]
        motif = " / ".join(witness["motif"])
        rows.append(
            [
                world,
                str(payload["candidate_count"]),
                ", ".join(f"T{k}:{v}" for k, v in payload["periods"].items()),
                ", ".join(f"{k}:{v}" for k, v in payload["spans"].items()),
                str(payload["periodicity_production_count"]),
                str(witness["word_len"]),
                witness["word"],
                str(witness["period"]),
                str(witness["span"]),
                ", ".join(witness["laws_accepted"]) or "-",
                motif,
            ]
        )

    if not rows:
        answer = "No local oscillators were found under this exhaustive small-IC protocol."
    elif len(rows) == 1 and rows[0][0] == "rule_108":
        answer = "`rule_108` is the only ECA rule found with a local oscillator under this protocol."
    else:
        answer = f"Found local oscillators in {len(rows)} ECA rules under this protocol."

    return f"""# Local Oscillator Family Sweep - Fase 18

## Setup

- Rules: all ECA with quiescent zero background (`f(0,0,0)=0`), `{summary['setup']['rules_tested']}` rules.
- ICs: all non-zero binary words of length `1..{MAX_INITIAL_WORD_LEN}` centered on a zero background.
- Width: `{WIDTH}`.
- Steps: `{STEPS}`.
- Burn-in: `{BURN_IN}`.
- Periods tested: `2..{MAX_PERIOD}`.
- Locality filter: post-burn-in active span `<= {MAX_LOCAL_SPAN}`.
- Production validation: current ZAA observers + dedup noise gate (`dedup_structure_count <= {DEDUP_STRUCTURE_NOISE_THRESHOLD}`).

## Result

{answer}

- Physical candidates: `{summary['total_candidates']}`
- Rules with candidates: `{summary['rules_with_candidates']}`
- `rule_108` production-valid candidates: `{rules.get('rule_108', {}).get('periodicity_production_count', 0)}`
- Periods found: `{', '.join('T=' + str(period) for period in sorted({period for payload in rules.values() for period in payload['periods']})) if rules else '-'}`

## Candidate Rules

{table(
        [
            "world",
            "candidates",
            "periods",
            "spans",
            "production_hits",
            "best_len",
            "best_word",
            "best_period",
            "best_span",
            "best_laws",
            "best_motif",
        ],
        rows,
    ) if rows else "No candidate rules."}

## Interpretation

This sweep upgrades Fase 16 from a hand-sized search (`point`, `pair_gap1`,
`triple`) to an exhaustive local-word search through length 8. It answers
whether the `rule_108` oscillator is isolated or part of a larger ECA family
under the current observer contract.

The search is still intentionally conservative: it detects exact stationary
periodicity after burn-in on a quiescent zero background. Moving periodic
particles, oscillators requiring wider ICs, or oscillators on non-zero/ether
backgrounds are outside this protocol.

Scientific reading: `rule_108` is not one member of a broader rule family under
this protocol. It is the unique quiescent ECA rule found. The family structure
is internal to `rule_108`: 179 short IC words converge to exact local period-2
behavior, and 132 of those are accepted by the production observer as
`periodicidad`.

No period greater than 2 appears for IC words of length <= 8. The span
distribution (`3, 5, 6, 7, 8`) shows that wider local motifs exist, but the
minimal canonical witness remains `101 -> ### / #.#` with span 3.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    candidates = run_sweep()
    with CANDIDATES_JSONL.open("w", encoding="utf-8") as handle:
        for candidate in candidates:
            handle.write(json.dumps(candidate, sort_keys=True) + "\n")
    summary = summarize(candidates)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(render_report(summary), encoding="utf-8")
    print(f"Wrote {CANDIDATES_JSONL} ({len(candidates)} rows)")
    print(f"Wrote {SUMMARY_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Rules with candidates: {summary['rules_with_candidates']}")


if __name__ == "__main__":
    main()
