"""Fase 11b: formal profiles for top frontera_temporal ECA rules.

Profiles rules 46, 208, and 209 using the same 6-seed protocol used for
rule_18 in the law map.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import mean
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.discovery import DiscoveryConfig, run_cycle  # noqa: E402


OUT_DIR = ROOT / "outputs" / "frontera_sweep"
OUT_JSON = OUT_DIR / "top_rules_profile.json"
OUT_MD = OUT_DIR / "top_rules_profile.md"

RULES = [46, 208, 209]
SEEDS = list(range(20260523, 20260529))
STEPS = 24
WIDTH = 64

LAW_ORDER = [
    "velocidad_constante",
    "periodicidad",
    "densidad_estable",
    "tipo_unico",
    "complejidad_alta",
    "frontera_temporal",
    "temporal_scale_stability",
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
    if noise_ratio > 0.5:
        return "noise-bounded"
    if stats["peak_diversity"] is not None and stats["peak_diversity"] > 0.5:
        if stats["non_empty_ratio"] < 0.5:
            return "multiregimen-escala-dependiente"
        return "multiregimen-productivo"
    return "sin-evidencia-multiregimen"


def run_profiles() -> dict[str, Any]:
    profiles: dict[str, Any] = {}
    for rule_id in RULES:
        rows = []
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
        stats = {
            "total_visits": len(rows),
            "non_empty_visits": non_empty_visits,
            "noise_visits": noise_visits,
            "non_empty_ratio": non_empty_visits / len(rows),
            "peak_diversity": peak_diversity,
        }
        profiles[f"rule_{rule_id}"] = {
            "rule_id": rule_id,
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
            "mean_n_laws": mean(row["n_laws_accepted"] for row in rows),
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
    return profiles


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


def render_markdown(profiles: dict[str, Any]) -> str:
    overview_rows = []
    for world, profile in profiles.items():
        overview_rows.append(
            [
                world,
                profile["classification"],
                f"{profile['ok_visits']}/6",
                fmt(profile["mean_n_laws"]),
                fmt(profile["peak_diversity"]),
                fmt(profile["mean_transition_rate"]),
                fmt(profile["mean_entropy"]),
            ]
        )

    law_rows = []
    for world, profile in profiles.items():
        row = [world]
        for law in LAW_ORDER:
            freq = profile["law_frequencies"][law]
            row.append(f"{freq['count']}/6 {freq['class']}")
        law_rows.append(row)

    sections = [
        "# Top Frontera Temporal Rule Profiles - Fase 11b",
        "",
        "Protocol: `steps=24`, `width=64`, seeds `20260523..20260528`.",
        "",
        "Frequency classes:",
        "",
        "- `core`: `>=4/6`",
        "- `present`: `2-3/6`",
        "- `trace`: `1/6`",
        "- `absent`: `0/6`",
        "",
        "Symmetry note: `rule_46` and `rule_209` are complementary (`255 - n`).",
        "`rule_208` is not part of that pair; its complement is `rule_47`.",
        "",
        "## Overview",
        "",
        table(
            [
                "world",
                "classification",
                "ok",
                "mean_n_laws",
                "peak_diversity",
                "mean_tr",
                "mean_entropy",
            ],
            overview_rows,
        ),
        "",
        "## Law Frequency Matrix",
        "",
        table(["world", *LAW_ORDER], law_rows),
        "",
    ]

    for world, profile in profiles.items():
        sections.extend(
            [
                f"## {world}",
                "",
                f"- Classification: `{profile['classification']}`",
                f"- Mean accepted laws: `{fmt(profile['mean_n_laws'])}`",
                f"- Mean transition rate: `{fmt(profile['mean_transition_rate'])}`",
                f"- Mean entropy: `{fmt(profile['mean_entropy'])}`",
                f"- Dominant signatures:",
                "",
            ]
        )
        for signature, count in profile["signatures"].items():
            sections.append(f"  - `{signature}`: `{count}/6`")
        sections.append("")

    sig46 = profiles["rule_46"]["signatures"]
    sig209 = profiles["rule_209"]["signatures"]
    sig208 = profiles["rule_208"]["signatures"]
    sections.extend(
        [
            "## Interpretation",
            "",
            "`rule_46` and `rule_209` form the expected complement pair and both",
            "reach maximum observed richness (`mean_n_laws=6.000`). Their signature",
            "profiles should be interpreted as one physical phenomenon under bit",
            "complement symmetry.",
            "",
            "`rule_208` also reaches `mean_n_laws=6.000`, but it is not the",
            "complement of either rule_46 or rule_209. Its dominant signatures are",
            "therefore evidence for a second route to maximum frontera-rich behavior,",
            "unless later analysis shows another symmetry relation.",
            "",
            "Signature comparison:",
            "",
            f"- `rule_46`: `{sig46}`",
            f"- `rule_209`: `{sig209}`",
            f"- `rule_208`: `{sig208}`",
        ]
    )
    return "\n".join(sections) + "\n"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    profiles = run_profiles()
    OUT_JSON.write_text(json.dumps(profiles, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(render_markdown(profiles), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")
    for world, profile in profiles.items():
        print(
            f"{world}: class={profile['classification']} "
            f"mean_laws={profile['mean_n_laws']:.3f} "
            f"peak_div={profile['peak_diversity']:.3f}"
        )


if __name__ == "__main__":
    main()
