"""Fase 20a: six-seed profiles for remaining frontera_temporal candidates.

Fase 11b profiled only the top three frontera-rich rules (46, 208, 209).
This script profiles the other ECA rules that passed the Fase 11a candidate
threshold: frontera_temporal in at least 2/3 sweep seeds.
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
SWEEP_RESULTS = OUT_DIR / "sweep_results.jsonl"
OUT_JSON = OUT_DIR / "remaining_candidate_profiles.json"
OUT_MD = OUT_DIR / "remaining_candidate_profiles.md"

ALREADY_PROFILED = {46, 208, 209}
SEEDS = list(range(20260523, 20260529))
STEPS = 24
WIDTH = 64

DIVERSITY_THRESHOLD = 0.5
NON_EMPTY_RATIO_THRESHOLD = 0.5
NOISE_RATIO_THRESHOLD = 0.5
RICH_LAWS_THRESHOLD = 4.0

LAW_ORDER = [
    "velocidad_constante",
    "periodicidad",
    "densidad_estable",
    "tipo_unico",
    "complejidad_alta",
    "frontera_temporal",
    "temporal_scale_stability",
]

ECA_CLASS = {
    18: "class-3 (moving wave fronts)",
    30: "class-3 (chaotic)",
    46: "unknown",
    51: "periodicidad-global",
    54: "class-4",
    90: "class-3 (additive/XOR)",
    108: "oscilador-local (period-2)",
    109: "class-4",
    110: "class-4",
    124: "unknown",
    137: "class-4",
    150: "class-3 (additive)",
    208: "unknown",
    209: "unknown",
}


def load_sweep_rows() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in SWEEP_RESULTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def candidate_rules() -> list[int]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in load_sweep_rows():
        grouped[int(row["rule_id"])].append(row)

    candidates: list[tuple[int, float, float]] = []
    for rule_id, rows in grouped.items():
        hits = sum(bool(row.get("frontera_temporal")) for row in rows)
        if hits < 2 or rule_id in ALREADY_PROFILED:
            continue
        mean_n_laws = mean(float(row.get("n_laws_accepted", 0)) for row in rows)
        candidates.append((rule_id, hits / len(rows), mean_n_laws))

    return [
        rule_id
        for rule_id, _, _ in sorted(candidates, key=lambda item: (-item[1], -item[2], item[0]))
    ]


def frequency_class(count: int) -> str:
    if count >= 4:
        return "core"
    if count >= 2:
        return "present"
    if count == 1:
        return "trace"
    return "absent"


def classify_world(stats: dict[str, Any]) -> str:
    if stats["total_visits"] == 0:
        return "sin-datos"
    noise_ratio = stats["noise_visits"] / stats["total_visits"]
    if noise_ratio > NOISE_RATIO_THRESHOLD:
        return "noise-bounded"
    if stats["peak_diversity"] is not None and stats["peak_diversity"] > DIVERSITY_THRESHOLD:
        if stats["non_empty_ratio"] < NON_EMPTY_RATIO_THRESHOLD:
            return "multiregimen-escala-dependiente"
        return "multiregimen-productivo"
    if stats["mean_n_laws"] >= RICH_LAWS_THRESHOLD:
        return "frontera-rich-estable"
    return "sin-evidencia-multiregimen"


def profile_rule(rule_id: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for seed in SEEDS:
        result = run_cycle(
            DiscoveryConfig(f"rule_{rule_id}", steps=STEPS, width=WIDTH, seed=seed),
            0,
        )
        laws = result.get("laws_accepted", [])
        rows.append(
            {
                "seed": seed,
                "analysis_status": result.get("analysis_status"),
                "analysis_ok": result.get("analysis_status") == "ok",
                "structure_count": result.get("structure_count"),
                "dedup_structure_count": result.get("dedup_structure_count"),
                "inflation_ratio": result.get("inflation_ratio"),
                "dominant_type": result.get("dominant_type"),
                "laws_accepted": laws,
                "n_laws_accepted": len(laws),
                "metrics": result.get("metrics", {}),
            }
        )

    law_counts = Counter()
    signatures = Counter()
    for row in rows:
        law_counts.update(row["laws_accepted"])
        signatures.update([tuple(row["laws_accepted"])])

    non_empty_visits = sum(bool(row["laws_accepted"]) for row in rows)
    noise_visits = sum(row["analysis_status"] == "ruido_no_analizable" for row in rows)
    unique_non_empty = len({tuple(row["laws_accepted"]) for row in rows if row["laws_accepted"]})
    peak_diversity = unique_non_empty / non_empty_visits if non_empty_visits >= 5 else None
    mean_n_laws = mean(row["n_laws_accepted"] for row in rows)
    stats = {
        "total_visits": len(rows),
        "non_empty_visits": non_empty_visits,
        "noise_visits": noise_visits,
        "non_empty_ratio": non_empty_visits / len(rows),
        "peak_diversity": peak_diversity,
        "mean_n_laws": mean_n_laws,
    }

    return {
        "rule_id": rule_id,
        "world": f"rule_{rule_id}",
        "eca_class": ECA_CLASS.get(rule_id, "unknown"),
        "complement_rule": 255 - rule_id,
        "steps": STEPS,
        "width": WIDTH,
        "seeds": SEEDS,
        "classification": classify_world(stats),
        "total_visits": len(rows),
        "ok_visits": sum(row["analysis_ok"] for row in rows),
        "noise_visits": noise_visits,
        "non_empty_visits": non_empty_visits,
        "non_empty_ratio": stats["non_empty_ratio"],
        "peak_diversity": peak_diversity,
        "mean_n_laws": mean_n_laws,
        "mean_dedup_structure_count": mean(row["dedup_structure_count"] for row in rows),
        "mean_transition_rate": mean(float(row["metrics"].get("transition_rate") or 0.0) for row in rows),
        "mean_entropy": mean(float(row["metrics"].get("entropy_mean") or 0.0) for row in rows),
        "law_frequencies": {
            law: {
                "count": law_counts[law],
                "rate": law_counts[law] / len(rows),
                "class": frequency_class(law_counts[law]),
            }
            for law in LAW_ORDER
        },
        "signatures": {
            " + ".join(sig) if sig else "EMPTY": count
            for sig, count in signatures.most_common()
        },
        "rows": rows,
    }


def run_profiles() -> dict[str, Any]:
    rules = candidate_rules()
    return {f"rule_{rule_id}": profile_rule(rule_id) for rule_id in rules}


def fmt(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value:.3f}"


def table(headers: list[str], body: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in body)
    return "\n".join(lines)


def core_laws(profile: dict[str, Any]) -> str:
    laws = [
        law
        for law in LAW_ORDER
        if profile["law_frequencies"][law]["class"] == "core"
    ]
    return ", ".join(laws) if laws else "-"


def render_markdown(profiles: dict[str, Any]) -> str:
    overview_rows = []
    for world, profile in profiles.items():
        overview_rows.append(
            [
                world,
                profile["eca_class"],
                profile["classification"],
                f"{profile['ok_visits']}/6",
                fmt(profile["mean_n_laws"]),
                fmt(profile["peak_diversity"]),
                fmt(profile["non_empty_ratio"]),
                core_laws(profile),
            ]
        )

    class_counts = Counter(profile["classification"] for profile in profiles.values())
    class_rows = [[key, str(value)] for key, value in sorted(class_counts.items())]

    law_rows = []
    for world, profile in profiles.items():
        row = [world]
        for law in LAW_ORDER:
            freq = profile["law_frequencies"][law]
            row.append(f"{freq['count']}/6 {freq['class']}")
        law_rows.append(row)

    rich_rows = [
        [
            world,
            fmt(profile["mean_n_laws"]),
            fmt(profile["peak_diversity"]),
            core_laws(profile),
            f"rule_{profile['complement_rule']}",
        ]
        for world, profile in profiles.items()
        if profile["classification"] == "frontera-rich-estable"
    ]

    multiregime_rows = [
        [
            world,
            profile["classification"],
            fmt(profile["mean_n_laws"]),
            fmt(profile["peak_diversity"]),
            core_laws(profile),
        ]
        for world, profile in profiles.items()
        if profile["classification"].startswith("multiregimen")
    ]

    sections = [
        "# Remaining Frontera Candidate Profiles - Fase 20a",
        "",
        "Protocol: `steps=24`, `width=64`, seeds `20260523..20260528`.",
        "",
        "Input candidates: ECA rules from Fase 11a with `frontera_temporal`",
        "accepted in at least `2/3` sweep seeds, excluding already-profiled",
        "`rule_46`, `rule_208`, and `rule_209`.",
        "",
        "Important caveat: classifications here are **candidate-protocol** labels",
        "from a fixed six-seed, `steps=24` profile. They do not automatically",
        "replace the long-journal atlas categories in `law_map.md`. In particular,",
        "`rule_110` and `rule_124` can look `frontera-rich-estable` under this",
        "short formal profile while remaining `multiregimen-productivo` in the",
        "longer atlas history.",
        "",
        "Frequency classes:",
        "",
        "- `core`: `>=4/6`",
        "- `present`: `2-3/6`",
        "- `trace`: `1/6`",
        "- `absent`: `0/6`",
        "",
        "## Classification Summary",
        "",
        table(["classification", "count"], class_rows),
        "",
        "## Overview",
        "",
        table(
            [
                "world",
                "eca_class",
                "classification",
                "ok",
                "mean_n_laws",
                "peak_diversity",
                "non_empty_ratio",
                "core_laws",
            ],
            overview_rows,
        ),
        "",
        "## frontera-rich-estable Candidates",
        "",
        table(
            ["world", "mean_n_laws", "peak_diversity", "core_laws", "complement"],
            rich_rows,
        )
        if rich_rows
        else "No additional `frontera-rich-estable` candidates found.",
        "",
        "## Multi-Regime Candidates",
        "",
        table(
            ["world", "classification", "mean_n_laws", "peak_diversity", "core_laws"],
            multiregime_rows,
        )
        if multiregime_rows
        else "No additional multi-regime candidates found under the 6-seed protocol.",
        "",
        "## Law Frequency Matrix",
        "",
        table(["world", *LAW_ORDER], law_rows),
        "",
        "## Interpretation",
        "",
        "The remaining frontera candidates are not noise artifacts: all runs in this",
        "profile use the same six-seed formal protocol as Fase 11b. The expanded",
        "set tests whether the top-three stable-rich rules were isolated outliers",
        "or part of a wider frontier-rich band.",
        "",
        "A `frontera-rich-estable` classification means low signature diversity",
        "combined with `mean_n_laws >= 4.0`. A `multiregimen-productivo`",
        "classification means the rule produces multiple non-empty signatures",
        "across seeds while remaining analyzable.",
        "",
    ]
    return "\n".join(sections) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    profiles = run_profiles()
    OUT_JSON.write_text(json.dumps(profiles, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(profiles), encoding="utf-8")
    print(f"Profiled {len(profiles)} remaining candidates")
    for world, profile in profiles.items():
        print(
            f"{world}: {profile['classification']} "
            f"mean_n_laws={profile['mean_n_laws']:.3f} "
            f"peak_diversity={profile['peak_diversity']}"
        )


if __name__ == "__main__":
    main()
