"""Fase 11a: full ECA sweep for frontera_temporal candidates.

Experimental artifact only. Uses the production discovery cycle evaluator over
all elementary cellular automata rules with a small canonical seed set.

Outputs:
    outputs/frontera_sweep/sweep_results.jsonl
    outputs/frontera_sweep/candidate_rules.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.discovery import DiscoveryConfig, run_cycle  # noqa: E402


OUT_DIR = ROOT / "outputs" / "frontera_sweep"
RESULTS_JSONL = OUT_DIR / "sweep_results.jsonl"
CANDIDATES_MD = OUT_DIR / "candidate_rules.md"

RULES = range(256)
SEEDS = [20260523, 20260524, 20260525]
STEPS = 24
WIDTH = 64
FRONTERA_MIN_HITS = 2

ECA_CLASS = {
    18: "class-3 (moving wave fronts)",
    30: "class-3 (chaotic)",
    54: "class-4",
    90: "class-3 (additive/XOR)",
    109: "class-4",
    110: "class-4",
    137: "class-4",
    150: "class-3 (additive)",
}


def result_row(rule_id: int, seed: int, result: dict[str, Any]) -> dict[str, Any]:
    laws = result.get("laws_accepted", [])
    metrics = result.get("metrics", {})
    return {
        "rule_id": rule_id,
        "world_type": f"rule_{rule_id}",
        "seed": seed,
        "steps": result.get("steps"),
        "width": result.get("width"),
        "analysis_status": result.get("analysis_status"),
        "analysis_ok": result.get("analysis_status") == "ok",
        "structure_count": result.get("structure_count"),
        "dedup_structure_count": result.get("dedup_structure_count"),
        "inflation_ratio": result.get("inflation_ratio"),
        "dominant_type": result.get("dominant_type"),
        "laws_accepted": laws,
        "n_laws_accepted": len(laws),
        "frontera_temporal": "frontera_temporal" in laws,
        "other_laws_count": len([law for law in laws if law != "frontera_temporal"]),
        "metrics": {
            "entropy_mean": metrics.get("entropy_mean"),
            "entropy_var": metrics.get("entropy_var"),
            "gzip_ratio": metrics.get("gzip_ratio"),
            "mutual_info_mean": metrics.get("mutual_info_mean"),
            "density_mean": metrics.get("density_mean"),
            "transition_rate": metrics.get("transition_rate"),
        },
    }


def run_sweep() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rule_id in RULES:
        for seed in SEEDS:
            result = run_cycle(
                DiscoveryConfig(f"rule_{rule_id}", steps=STEPS, width=WIDTH, seed=seed),
                0,
            )
            rows.append(result_row(rule_id, seed, result))
    return rows


def aggregate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_rule: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_rule[int(row["rule_id"])].append(row)

    aggregates: list[dict[str, Any]] = []
    for rule_id, items in sorted(by_rule.items()):
        laws_freq = Counter()
        for item in items:
            laws_freq.update(item["laws_accepted"])
        other_laws_freq = {
            law: count / len(items)
            for law, count in sorted(laws_freq.items())
            if law != "frontera_temporal"
        }
        frontera_hits = sum(1 for item in items if item["frontera_temporal"])
        rich_frontera_hits = sum(
            1
            for item in items
            if item["frontera_temporal"] and item["other_laws_count"] >= 2
        )
        aggregates.append(
            {
                "rule_id": rule_id,
                "world_type": f"rule_{rule_id}",
                "eca_class": ECA_CLASS.get(rule_id, "unknown"),
                "frontera_temporal_hits": frontera_hits,
                "frontera_temporal_rate": frontera_hits / len(items),
                "rich_frontera_hits": rich_frontera_hits,
                "rich_frontera_rate": rich_frontera_hits / len(items),
                "mean_n_laws": mean(item["n_laws_accepted"] for item in items),
                "ok_rate": sum(item["analysis_ok"] for item in items) / len(items),
                "noise_rate": sum(not item["analysis_ok"] for item in items) / len(items),
                "mean_transition_rate": mean(
                    float(item["metrics"]["transition_rate"] or 0.0) for item in items
                ),
                "mean_entropy": mean(
                    float(item["metrics"]["entropy_mean"] or 0.0) for item in items
                ),
                "other_laws_freq": other_laws_freq,
            }
        )
    return aggregates


def fmt(value: float) -> str:
    return f"{value:.3f}"


def law_freq_label(freq: dict[str, float]) -> str:
    if not freq:
        return "-"
    return ", ".join(f"{law}:{rate:.2f}" for law, rate in freq.items())


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_report(aggregates: list[dict[str, Any]]) -> str:
    candidates = [
        row
        for row in aggregates
        if row["frontera_temporal_hits"] >= FRONTERA_MIN_HITS
    ]
    candidates = sorted(
        candidates,
        key=lambda row: (-row["frontera_temporal_rate"], -row["mean_n_laws"], row["rule_id"]),
    )
    rich_candidates = [
        row
        for row in candidates
        if row["rich_frontera_hits"] >= FRONTERA_MIN_HITS
    ]

    candidate_rows = [
        [
            str(row["rule_id"]),
            row["eca_class"],
            fmt(row["frontera_temporal_rate"]),
            f"{row['frontera_temporal_hits']}/3",
            fmt(row["mean_n_laws"]),
            fmt(row["rich_frontera_rate"]),
            fmt(row["ok_rate"]),
            fmt(row["mean_transition_rate"]),
            law_freq_label(row["other_laws_freq"]),
        ]
        for row in candidates
    ]
    rich_rows = [
        [
            str(row["rule_id"]),
            row["eca_class"],
            fmt(row["frontera_temporal_rate"]),
            fmt(row["mean_n_laws"]),
            law_freq_label(row["other_laws_freq"]),
        ]
        for row in rich_candidates
    ]

    return f"""# Frontera Temporal ECA Sweep — Fase 11a

## Setup

- Rules: `0..255`
- Seeds: `{SEEDS}`
- Steps: `{STEPS}`
- Width: `{WIDTH}`
- Candidate threshold: `frontera_temporal` accepted in at least `{FRONTERA_MIN_HITS}/3` seeds.
- Sort: `frontera_temporal_rate DESC`, then `mean_n_laws DESC`.

`frontera_temporal` is evaluated on the full `steps=24` frame stack. There is no
subcycle sampling.

## Candidate Rules

{markdown_table(
        [
            "rule_id",
            "eca_class",
            "frontera_temporal_rate",
            "hits",
            "mean_n_laws",
            "rich_frontera_rate",
            "ok_rate",
            "mean_transition_rate",
            "other_laws_freq",
        ],
        candidate_rows,
    ) if candidate_rows else "No candidate rules found."}

## Rich Frontera Candidates

Rules where `frontera_temporal` appears and co-appears with at least two other
laws in at least `{FRONTERA_MIN_HITS}/3` seeds.

{markdown_table(
        ["rule_id", "eca_class", "frontera_temporal_rate", "mean_n_laws", "other_laws_freq"],
        rich_rows,
    ) if rich_rows else "No rich frontera candidates found."}

## Interpretation

This sweep searches for worlds where `frontera_temporal` is not merely a rare
isolated trigger, but part of a productive law signature. Candidate rules should
be considered for deeper discovery only when the frontera signal co-occurs with
multiple other laws.
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = run_sweep()
    with RESULTS_JSONL.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    aggregates = aggregate(rows)
    CANDIDATES_MD.write_text(render_report(aggregates), encoding="utf-8")
    candidates = [row for row in aggregates if row["frontera_temporal_hits"] >= FRONTERA_MIN_HITS]
    rich = [row for row in candidates if row["rich_frontera_hits"] >= FRONTERA_MIN_HITS]
    print(f"Wrote {RESULTS_JSONL} ({len(rows)} rows)")
    print(f"Wrote {CANDIDATES_MD}")
    print(f"candidate_rules={len(candidates)} rich_candidates={len(rich)}")
    for row in sorted(candidates, key=lambda r: (-r["frontera_temporal_rate"], -r["mean_n_laws"], r["rule_id"]))[:20]:
        print(
            f"rule_{row['rule_id']}: frontera={row['frontera_temporal_hits']}/3 "
            f"mean_laws={row['mean_n_laws']:.2f} rich={row['rich_frontera_hits']}/3"
        )


if __name__ == "__main__":
    main()
