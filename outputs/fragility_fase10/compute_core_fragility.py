"""Fase 15b: core fragility over existing one-bit flip results.

`f_total` measures any law-signature change. `f_core` measures whether the laws
that define a world's category change. This distinguishes stable behavior with
secondary-law churn (rule_51) from true regime changes (rule_137).
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
RESULTS_JSONL = ROOT / "outputs" / "fragility_fase10" / "fragility_results.jsonl"
OUT_JSON = ROOT / "outputs" / "fragility_fase10" / "core_fragility.json"
OUT_MD = ROOT / "outputs" / "fragility_fase10" / "core_fragility_report.md"


CORE_LAWS = {
    # Stable high-richness boundary worlds: core is their six-law frontier set.
    "rule_46": {
        "velocidad_constante",
        "densidad_estable",
        "tipo_unico",
        "complejidad_alta",
        "frontera_temporal",
        "temporal_scale_stability",
    },
    "rule_208": {
        "velocidad_constante",
        "densidad_estable",
        "tipo_unico",
        "complejidad_alta",
        "frontera_temporal",
        "temporal_scale_stability",
    },
    "rule_209": {
        "velocidad_constante",
        "densidad_estable",
        "tipo_unico",
        "complejidad_alta",
        "frontera_temporal",
        "temporal_scale_stability",
    },
    # Global periodicity: periodicidad is the defining behavior. Other laws are
    # secondary descriptors of the same global period-2 dynamics.
    "rule_51": {"periodicidad"},
    # Scale-dependent additive world: temporal_scale_stability is the stable
    # minimal signature at higher scale.
    "rule_90": {"temporal_scale_stability"},
    # Productive multi-regime worlds: core is the reference signature observed
    # for that seed, because no single law defines all ICs in the category.
    # These entries use "__reference__" as a sentinel.
    "rule_18": {"__reference__"},
    "rule_54": {"__reference__"},
    "rule_109": {"__reference__"},
    "rule_110": {"__reference__"},
    "rule_124": {"__reference__"},
    "rule_137": {"__reference__"},
}


def load_records() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in RESULTS_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def core_for_record(record: dict[str, Any]) -> set[str]:
    configured = CORE_LAWS.get(record["world"], {"__reference__"})
    if "__reference__" in configured:
        return set(record["reference_sig"])
    return set(configured)


def core_changed(record: dict[str, Any]) -> bool:
    if record["outcome"] == "noise":
        return True
    if record["outcome"] == "silence":
        return True
    core = core_for_record(record)
    reference = set(record["reference_sig"])
    perturbed = set(record["perturbed_sig"])
    return (reference & core) != (perturbed & core)


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    by_world: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        by_world[record["world"]].append(record)

    summary: dict[str, Any] = {}
    for world, items in sorted(by_world.items()):
        core_changes = sum(core_changed(item) for item in items)
        total_changes = sum(item["outcome"] != "same_sig" for item in items)
        noise_changes = sum(item["outcome"] == "noise" for item in items)
        silence_changes = sum(item["outcome"] == "silence" for item in items)
        core_laws = sorted(CORE_LAWS.get(world, {"__reference__"}))
        if core_laws == ["__reference__"]:
            core_laws_label = "reference_signature_per_seed"
        else:
            core_laws_label = " + ".join(core_laws)
        summary[world] = {
            "world": world,
            "n_flips": len(items),
            "f_total": total_changes / len(items),
            "f_core": core_changes / len(items),
            "f_secondary": max(0.0, (total_changes - core_changes) / len(items)),
            "f_noise": noise_changes / len(items),
            "f_silence": silence_changes / len(items),
            "core_laws": core_laws_label,
        }
    return summary


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def render_markdown(summary: dict[str, Any]) -> str:
    rows = [
        [
            world,
            stats["core_laws"],
            fmt(stats["f_total"]),
            fmt(stats["f_core"]),
            fmt(stats["f_secondary"]),
            fmt(stats["f_noise"]),
        ]
        for world, stats in sorted(summary.items(), key=lambda item: item[1]["f_core"])
    ]
    rule51 = summary.get("rule_51", {})
    rule137 = summary.get("rule_137", {})
    return f"""# Core Fragility - Fase 15b

## Method

`f_total` counts any law-signature change under one-bit flips.

`f_core` counts only changes to the laws that define the world's category or
regime. Noise and silence count as core changes because the defining regime is
lost.

Core-law convention:

- `frontera-rich-estable`: six-law frontier signature.
- `periodicidad-global`: `periodicidad`.
- `multiregimen-productivo`: the reference signature for that seed.
- `rule_90`: `temporal_scale_stability`.

## Core Fragility Table

{table(["world", "core_laws", "f_total", "f_core", "f_secondary", "f_noise"], rows)}

## Interpretation

`rule_51` is the motivating case: `f_total = {fmt(rule51.get('f_total', 0.0))}`,
but `f_core = {fmt(rule51.get('f_core', 0.0))}`. Global periodicity survives
all measured one-bit flips; only secondary laws such as `densidad_estable`
change.

`rule_137` remains a true high-core-fragility world:
`f_core = {fmt(rule137.get('f_core', 0.0))}`. Its defining productive regime
changes under most perturbations.
"""


def main() -> None:
    records = load_records()
    summary = summarize(records)
    OUT_JSON.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    OUT_MD.write_text(render_markdown(summary), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
