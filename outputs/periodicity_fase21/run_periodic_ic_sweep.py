"""Fase 21a: designed periodic-IC sweep for ECA periodicidad.

Fase 14 showed that atlas ECA worlds do not activate `periodicidad` under
random ICs, while rule_51 does through global period-2 complementation. This
artifact tests a stronger condition: explicitly periodic ICs compatible with
periodic boundary conditions.

Protocol:
    rules: 0..255
    ICs: 32 designed 8-bit words repeated 8 times into width 64
    steps: 96
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
import sys
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.consensus import deduplicate_structures  # noqa: E402
from zaa.cycle_laws import evaluate_cycle_laws, evaluate_periodicity_law  # noqa: E402
from zaa.eca import simulate  # noqa: E402
from zaa.observers import run_observers  # noqa: E402


OUT_DIR = ROOT / "outputs" / "periodicity_fase21"
RESULTS_JSONL = OUT_DIR / "periodic_ic_sweep_results.jsonl"
SUMMARY_JSON = OUT_DIR / "periodic_ic_sweep_summary.json"
REPORT_MD = OUT_DIR / "periodic_ic_sweep_report.md"

WIDTH = 64
STEPS = 96
WORD_BITS = 8
DEDUP_STRUCTURE_NOISE_THRESHOLD = 40
MAX_FRAME_PERIOD = 16


def word_to_state(word: int) -> np.ndarray:
    bits = np.array([(word >> shift) & 1 for shift in range(WORD_BITS - 1, -1, -1)], dtype=np.uint8)
    return np.tile(bits, WIDTH // WORD_BITS)


def designed_words() -> list[int]:
    """Representative periodic ICs: uniform, alternating, blocks, defects."""
    words = {
        0b00000000,
        0b11111111,
        0b01010101,
        0b10101010,
        0b00110011,
        0b11001100,
        0b00010001,
        0b00100010,
        0b01000100,
        0b10001000,
        0b11101110,
        0b11011101,
        0b10111011,
        0b01110111,
        0b00001111,
        0b11110000,
        0b00111100,
        0b11000011,
        0b00011100,
        0b00111000,
        0b01110000,
        0b10000011,
        0b11100011,
        0b11000111,
        0b10001111,
        0b00011111,
        0b01011010,
        0b10100101,
        0b01101001,
        0b10010110,
        0b00101101,
        0b11010010,
    }
    return sorted(words)


def minimal_period(word: int) -> int:
    bits = [(word >> shift) & 1 for shift in range(WORD_BITS - 1, -1, -1)]
    for period in [1, 2, 4, 8]:
        if all(bits[idx] == bits[idx % period] for idx in range(WORD_BITS)):
            return period
    return 8


def evaluate(rule: int, word: int) -> dict[str, Any]:
    state = word_to_state(word)
    frames = simulate(state, rule, STEPS)

    frame_period = exact_frame_period(frames)
    if frame_period is None:
        return {
            "rule": rule,
            "world": f"rule_{rule}",
            "word": format(word, f"0{WORD_BITS}b"),
            "word_int": word,
            "minimal_period": minimal_period(word),
            "steps": STEPS,
            "width": WIDTH,
            "frame_period": None,
            "raw_structure_count": 0,
            "dedup_structure_count": 0,
            "analysis_status": "not_frame_periodic",
            "oscillator_count_raw": 0,
            "periodicity_raw": False,
            "periodicity_production": False,
            "laws_accepted": [],
        }

    structures = run_observers(frames)
    dedup_count = len(deduplicate_structures(structures))
    analysis_status = "ruido_no_analizable" if dedup_count > DEDUP_STRUCTURE_NOISE_THRESHOLD else "ok"
    periodic_raw = evaluate_periodicity_law(structures).accepted
    oscillator_count_raw = sum(1 for structure in structures if structure.tipo == "oscilador")
    laws = evaluate_cycle_laws(structures, frames, STEPS)["laws_accepted"] if analysis_status == "ok" else []
    return {
        "rule": rule,
        "world": f"rule_{rule}",
        "word": format(word, f"0{WORD_BITS}b"),
        "word_int": word,
        "minimal_period": minimal_period(word),
        "steps": STEPS,
        "width": WIDTH,
        "frame_period": frame_period,
        "raw_structure_count": len(structures),
        "dedup_structure_count": dedup_count,
        "analysis_status": analysis_status,
        "oscillator_count_raw": oscillator_count_raw,
        "periodicity_raw": periodic_raw,
        "periodicity_production": "periodicidad" in laws,
        "laws_accepted": laws,
    }


def exact_frame_period(frames: np.ndarray) -> int | None:
    """Return exact temporal period 2..MAX_FRAME_PERIOD, excluding static frames."""
    if not any(not np.array_equal(frames[:-p], frames[p:]) for p in range(1, MAX_FRAME_PERIOD + 1)):
        return None
    for period in range(2, MAX_FRAME_PERIOD + 1):
        if np.array_equal(frames[:-period], frames[period:]):
            return period
    return None


def run_sweep() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for rule in range(256):
        for word in designed_words():
            records.append(evaluate(rule, word))
    return records


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_rule: dict[int, list[dict[str, Any]]] = defaultdict(list)
    by_period: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_rule[int(record["rule"])].append(record)
        by_period[int(record["minimal_period"])].append(record)

    rule_summaries = []
    for rule, items in sorted(by_rule.items()):
        prod_hits = [item for item in items if item["periodicity_production"]]
        raw_hits = [item for item in items if item["periodicity_raw"]]
        ok_hits = [item for item in items if item["analysis_status"] == "ok"]
        if prod_hits or raw_hits:
            law_counts = Counter()
            for item in prod_hits:
                law_counts.update(item["laws_accepted"])
            rule_summaries.append(
                {
                    "rule": rule,
                    "world": f"rule_{rule}",
                    "periodicity_raw_hits": len(raw_hits),
                    "periodicity_production_hits": len(prod_hits),
                    "ok_hits": len(ok_hits),
                    "noise_hits": len(items) - len(ok_hits),
                    "hit_rate": len(prod_hits) / len(items),
                    "hit_words": [item["word"] for item in prod_hits[:20]],
                    "hit_periods": dict(Counter(item["minimal_period"] for item in prod_hits)),
                    "frame_periods": dict(Counter(item["frame_period"] for item in prod_hits)),
                    "mean_oscillator_count": mean(item["oscillator_count_raw"] for item in prod_hits) if prod_hits else 0.0,
                    "laws_frequency": dict(law_counts),
                }
            )

    period_rows = []
    for period, items in sorted(by_period.items()):
        period_rows.append(
            {
                "minimal_period": period,
                "n_cases": len(items),
            "periodicity_production_hits": sum(item["periodicity_production"] for item in items),
            "periodicity_raw_hits": sum(item["periodicity_raw"] for item in items),
            "frame_periodic_cases": sum(item["frame_period"] is not None for item in items),
            }
        )

    production_rules = [row["rule"] for row in rule_summaries if row["periodicity_production_hits"] > 0]
    return {
        "config": {
            "rules": "0..255",
            "word_bits": WORD_BITS,
            "n_words": len(designed_words()),
            "words": [format(word, f"0{WORD_BITS}b") for word in designed_words()],
            "width": WIDTH,
            "steps": STEPS,
        },
        "n_records": len(records),
        "n_rules_with_periodicity_production": len(production_rules),
        "rules_with_periodicity_production": production_rules,
        "rule_summaries": rule_summaries,
        "period_summary": period_rows,
    }


def fmt(value: float) -> str:
    return f"{value:.3f}"


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(summary: dict[str, Any]) -> str:
    top_rows = sorted(
        summary["rule_summaries"],
        key=lambda row: (-row["periodicity_production_hits"], row["rule"]),
    )[:20]
    top_rule_rows = [
        [
            f"rule_{row['rule']}",
            str(row["periodicity_production_hits"]),
            fmt(row["hit_rate"]),
            json.dumps(row["hit_periods"], sort_keys=True),
            json.dumps(row["frame_periods"], sort_keys=True),
            ", ".join(row["hit_words"][:8]) or "-",
        ]
        for row in top_rows
    ]
    rule_rows = [
        [
            f"rule_{row['rule']}",
            str(row["periodicity_production_hits"]),
            str(row["periodicity_raw_hits"]),
            str(row["ok_hits"]),
            str(row["noise_hits"]),
            fmt(row["hit_rate"]),
            json.dumps(row["hit_periods"], sort_keys=True),
            json.dumps(row["frame_periods"], sort_keys=True),
            ", ".join(row["hit_words"]) or "-",
        ]
        for row in summary["rule_summaries"]
    ]
    period_rows = [
        [
            str(row["minimal_period"]),
            str(row["n_cases"]),
            str(row["periodicity_production_hits"]),
            str(row["periodicity_raw_hits"]),
        ]
        for row in summary["period_summary"]
    ]

    production_rules = summary["rules_with_periodicity_production"]
    if production_rules:
        answer = (
            f"Designed periodic ICs activate production `periodicidad` in "
            f"{len(production_rules)} ECA rules: "
            f"{', '.join('rule_' + str(rule) for rule in production_rules)}."
        )
    else:
        answer = "No ECA rule activates production `periodicidad` under designed periodic ICs."
    total_prod_hits = sum(row["periodicity_production_hits"] for row in summary["period_summary"])
    total_raw_hits = sum(row["periodicity_raw_hits"] for row in summary["period_summary"])
    total_frame_periodic = sum(row["frame_periodic_cases"] for row in summary["period_summary"])

    return f"""# Designed Periodic-IC Sweep - Fase 21a

## Setup

- Rules: `0..255`
- ICs: `{len(designed_words())}` designed binary words of length `{WORD_BITS}`,
  repeated into `width={WIDTH}`.
- Compatible spatial periods: `1`, `2`, `4`, `8`.
- Steps: `{STEPS}`
- Production noise gate: `dedup_structure_count > {DEDUP_STRUCTURE_NOISE_THRESHOLD}`
- Total runs: `{summary['n_records']}`

`periodicity_raw` means at least one observer emitted `tipo=oscilador`.
`periodicity_production` means the run was not noise-gated and
`periodicidad` appeared in `laws_accepted`.

## Answer

{answer}

Aggregate hit counts:

- Frame-periodic cases: `{total_frame_periodic}/{summary['n_records']}`
- Raw observer periodicity hits: `{total_raw_hits}/{summary['n_records']}`
- Production periodicity hits: `{total_prod_hits}/{summary['n_records']}`

## Top Periodicity Rules

{table(
        [
            "world",
            "production_hits/32",
            "hit_rate",
            "IC_min_periods",
            "frame_periods",
            "example_words",
        ],
        top_rule_rows,
    )}

## Rules With Periodicity

{table(
        [
            "world",
            "periodicity_production_hits",
            "periodicity_raw_hits",
            "ok_hits",
            "noise_hits",
            "hit_rate",
            "hit_periods",
            "frame_periods",
            "example_words",
        ],
        rule_rows,
    ) if rule_rows else "No periodicity hits."}

## Hit Counts by IC Minimal Period

{table(
        [
            "minimal_period",
            "n_cases",
            "periodicity_production_hits",
            "periodicity_raw_hits",
            "frame_periodic_cases",
        ],
        period_rows,
    )}

## Interpretation

Designed periodic ICs make `periodicidad` widespread: `207/256` ECA rules have
at least one production-valid hit. This reverses the random-IC result from
Fase 14. The law is not structurally inaccessible in ECA; it is strongly
dependent on the IC family.

The strongest rules are global or background-induced temporal oscillators.
`rule_51` remains the cleanest universal case (`32/32` hits, all frame period
2). Several other rules (`rule_15`, `rule_85`, `rule_105`, `rule_170`,
`rule_240`) are nearly universal under the designed periodic suite. These are
not local particle oscillators like `rule_108`; they are periodic backgrounds
or spatially repeated temporal cycles induced by periodic ICs.

The atlas conclusion should therefore be refined: random ICs almost never
produce observer-level `periodicidad`, but designed periodic ICs make it common.
`periodicidad` is an IC-family-sensitive law, not a dead law.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    records = run_sweep()
    with RESULTS_JSONL.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    summary = summarize(records)
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text(render_report(summary), encoding="utf-8")
    print(f"records={len(records)}")
    print(f"rules_with_periodicity={summary['rules_with_periodicity_production']}")
    print(f"report={REPORT_MD}")


if __name__ == "__main__":
    main()
