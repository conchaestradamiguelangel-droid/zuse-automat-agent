"""Generate the Fase 9a world taxonomy and law coverage map.

Input:
    outputs/experiments_2026-05-27/journal_8c_long.jsonl

Output:
    outputs/world_taxonomy/law_map.md

This is an experimental/documentation artifact. It does not import or modify
production policy code.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
JOURNAL = ROOT / "outputs" / "experiments_2026-05-27" / "journal_8c_long.jsonl"
OUT = ROOT / "outputs" / "world_taxonomy" / "law_map.md"

DIVERSITY_THRESHOLD = 0.5
NON_EMPTY_RATIO_THRESHOLD = 0.5
NOISE_RATIO_THRESHOLD = 0.5

LAW_COLUMNS = [
    ("vel", "velocidad_constante"),
    ("per", "periodicidad"),
    ("den", "densidad_estable"),
    ("tipo", "tipo_unico"),
    ("compl", "complejidad_alta"),
    ("front", "frontera_temporal"),
    ("tss", "temporal_scale_stability"),
]

ECA_CLASS = {
    "rule_18": "class-3 (moving wave fronts)",
    "rule_30": "class-3 (chaotic)",
    "rule_54": "class-4",
    "rule_90": "class-3 (additive/XOR)",
    "rule_109": "class-4",
    "rule_110": "class-4",
    "rule_137": "class-4",
    "rule_150": "class-3 (additive)",
}

WORLD_FIELD_CANDIDATES = ["world_type", "world_rule", "world_id", "world", "rule"]


def load_rows() -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in JOURNAL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def detect_world_field(sample_rows: list[dict[str, Any]]) -> str:
    keys = set().union(*(row.keys() for row in sample_rows))
    for candidate in WORLD_FIELD_CANDIDATES:
        if candidate in keys:
            return candidate
    raise KeyError(
        "No world identifier field found. "
        f"Tried {WORLD_FIELD_CANDIDATES}; available keys: {sorted(keys)}"
    )


def n_laws(row: dict[str, Any]) -> int:
    if "n_laws_accepted" in row:
        return int(row["n_laws_accepted"])
    return len(row.get("laws_accepted", []))


def is_analysis_ok(row: dict[str, Any]) -> bool:
    if "analysis_ok" in row:
        return bool(row["analysis_ok"])
    return row.get("analysis_status") == "ok"


def signature_label(signature: tuple[str, ...] | None) -> str:
    if not signature:
        return "-"
    return " + ".join(signature)


def classify_world(stats: dict[str, Any]) -> str:
    if stats["total_visits"] == 0:
        return "sin-datos"
    noise_ratio = stats["noise_visits"] / stats["total_visits"]
    if noise_ratio > NOISE_RATIO_THRESHOLD:
        return "noise-bounded"
    if stats["peak_diversity"] is not None and stats["peak_diversity"] > DIVERSITY_THRESHOLD:
        if stats["non_empty_ratio"] < NON_EMPTY_RATIO_THRESHOLD:
            return "multiregimen-escala-dependiente"
        else:
            return "multiregimen-productivo"
    return "sin-evidencia-multiregimen"


def compute_stats(rows: list[dict[str, Any]], world_field: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[world_field])].append(row)

    stats_by_world: dict[str, dict[str, Any]] = {}
    for world, world_rows in sorted(grouped.items()):
        total_visits = len(world_rows)
        non_empty_rows = [row for row in world_rows if row.get("laws_accepted", [])]
        noise_visits = sum(row.get("analysis_status") == "ruido_no_analizable" for row in world_rows)
        silence_visits = sum(is_analysis_ok(row) and not row.get("laws_accepted", []) for row in world_rows)
        # The journal emits the world's known state before the current decision.
        # In the clean 8c journal this is stored as world_peak_diversity_prev
        # / world_signature_diversity_prev, not law_signature_diversity.
        diversity_values = [
            row.get("world_peak_diversity_prev", row.get("law_signature_diversity"))
            for row in world_rows
            if row.get("world_peak_diversity_prev", row.get("law_signature_diversity")) is not None
        ]
        signatures = Counter(tuple(row.get("laws_accepted", [])) for row in non_empty_rows)
        dominant_signature = signatures.most_common(1)[0][0] if signatures else None
        law_counts = Counter()
        for row in non_empty_rows:
            law_counts.update(row.get("laws_accepted", []))

        stats = {
            "world": world,
            "eca_class": ECA_CLASS.get(world, "unknown"),
            "total_visits": total_visits,
            "non_empty_visits": len(non_empty_rows),
            "noise_visits": noise_visits,
            "silence_visits": silence_visits,
            "mean_laws": mean(n_laws(row) for row in world_rows) if world_rows else 0.0,
            "peak_diversity": max(diversity_values) if diversity_values else None,
            "non_empty_ratio": len(non_empty_rows) / total_visits if total_visits else 0.0,
            "noise_ratio": noise_visits / total_visits if total_visits else 0.0,
            "dominant_signature": dominant_signature,
            "law_counts": law_counts,
        }
        stats["category"] = classify_world(stats)
        stats_by_world[world] = stats
    return stats_by_world


def law_cell(stats: dict[str, Any], law_name: str) -> str:
    non_empty_visits = stats["non_empty_visits"]
    if non_empty_visits == 0:
        return "?"
    dominant = stats["dominant_signature"] or ()
    count = stats["law_counts"].get(law_name, 0)
    frequency = count / non_empty_visits
    if law_name in dominant or frequency >= 0.5:
        return "✓"
    if count > 0:
        return "·"
    return "-"


def fmt_float(value: float | None, digits: int = 3) -> str:
    if value is None:
        return "-"
    return f"{value:.{digits}f}"


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_markdown(stats_by_world: dict[str, dict[str, Any]], world_field: str, schema_keys: list[str]) -> str:
    classification_rows: list[list[str]] = []
    matrix_rows: list[list[str]] = []
    for world, stats in stats_by_world.items():
        classification_rows.append(
            [
                world,
                stats["eca_class"],
                stats["category"],
                str(stats["total_visits"]),
                fmt_float(stats["non_empty_ratio"]),
                fmt_float(stats["noise_ratio"]),
                fmt_float(stats["peak_diversity"]),
                fmt_float(stats["mean_laws"]),
                signature_label(stats["dominant_signature"]),
            ]
        )
        matrix_rows.append(
            [world] + [law_cell(stats, law_name) for _, law_name in LAW_COLUMNS]
        )

    law_legend = "\n".join(
        f"- `{short}` = `{full}`" for short, full in LAW_COLUMNS
    )
    schema_excerpt = ", ".join(schema_keys)

    return f"""# World Taxonomy and Law Map

Source journal: `outputs/experiments_2026-05-27/journal_8c_long.jsonl`

Schema check: world field detected as `{world_field}`. First-row keys include:
`{schema_excerpt}`.

## Taxonomy

This taxonomy separates three mechanisms that looked similar before Fase 8:

- **multi-regimen-productivo**: the world has real law-signature diversity and
  most visits produce at least one accepted law.
- **multi-regimen-escala-dependiente**: the world has real non-empty signature
  diversity, but most visits are silent at the explored scale.
- **noise-bounded**: the world fails before law evaluation at high scale because
  `analysis_status == "ruido_no_analizable"`.
- **sin-evidencia-multiregimen**: no sufficient evidence of multi-regime behavior
  in this journal.

Mechanical distinction:

- `rule_90` style silence is post-analysis: `analysis_ok=True`, structures exist,
  but `laws_accepted=[]`.
- `rule_150` style failure is pre-analysis: the deduplicated structure gate marks
  the cycle as `ruido_no_analizable`, so laws are not evaluated.

Thresholds used:

- `DIVERSITY_THRESHOLD = {DIVERSITY_THRESHOLD}`
- `NON_EMPTY_RATIO_THRESHOLD = {NON_EMPTY_RATIO_THRESHOLD}`
- `NOISE_RATIO_THRESHOLD = {NOISE_RATIO_THRESHOLD}`

Classification function:

```python
def classify_world(stats):
    if stats['total_visits'] == 0:
        return "sin-datos"
    noise_ratio = stats['noise_visits'] / stats['total_visits']
    if noise_ratio > NOISE_RATIO_THRESHOLD:
        return "noise-bounded"
    if stats['peak_diversity'] is not None and stats['peak_diversity'] > DIVERSITY_THRESHOLD:
        if stats['non_empty_ratio'] < NON_EMPTY_RATIO_THRESHOLD:
            return "multiregimen-escala-dependiente"
        else:
            return "multiregimen-productivo"
    return "sin-evidencia-multiregimen"
```

## World Classification Table

{table(
        [
            "world",
            "eca_class",
            "category",
            "total_visits",
            "non_empty_ratio",
            "noise_ratio",
            "peak_diversity",
            "mean_laws",
            "dominant_signature",
        ],
        classification_rows,
    )}

## Law Coverage Matrix

Law columns:

{law_legend}

Cell states:

- `✓`: law appears in the dominant signature or in at least 50% of non-empty visits.
- `·`: law appears in at least one non-empty visit but in less than 50%.
- `-`: non-empty visits exist and the law never appears.
- `?`: no non-empty visits.

{table(["world"] + [short for short, _ in LAW_COLUMNS], matrix_rows)}

## Notable World Profiles

### rule_18 — multi-régimen productivo (class-3 moving structures)

Formal map protocol: `steps=24`, `width=64`, seeds `20260523..20260528`.
Result: `6/6 ok`, deduplicated structures `8..13`, temporal load about
`7.2..7.55`, and high transition rate about `0.52..0.57`.

Core laws:

- `complejidad_alta`: `6/6`
- `temporal_scale_stability`: `6/6`
- `velocidad_constante`: `5/6`
- `tipo_unico`: `4/6`

Dominant formal signature:
`velocidad_constante + tipo_unico + complejidad_alta + temporal_scale_stability`
in `4/6` seeds.

Interpretation: rule_18 is an alternate route to law richness, not the same
class-4 route as rule_110/rule_137. It combines stable temporal scale with
moving, relatively homogeneous wave-front structures.

### rule_90 — multi-régimen escala-dependiente (XOR/additive)

In the 200-cycle post-8c journal, rule_90 has `analysis_status == ok` in all
visits and reaches `steps=400`, but high-scale visits are mostly silent:
structures exist, the analysis runs, and `laws_accepted=[]`.

This is post-analysis silence, not noise. The agent should not spend
multi-regime repeats on silent cycles, and Fase 8c enforces that.

Interpretation: rule_90 has real early non-empty signatures, but the additive
XOR dynamics become too regular or too algebraic for the current seven laws at
high scale.

### rule_150 — noise-bounded (additive)

rule_150 produces a stable non-empty signature at low scale:
`densidad_estable + complejidad_alta + temporal_scale_stability`.

At higher scale it crosses the deduplicated structure gate and becomes
`ruido_no_analizable`. This is pre-analysis failure, unlike rule_90. The agent
handles it by changing world once the noise boundary is observed.
"""


def main() -> None:
    rows = load_rows()
    sample_rows = rows[:3]
    schema_keys = sorted(sample_rows[0].keys()) if sample_rows else []
    print("Schema sample keys:")
    for i, row in enumerate(sample_rows, start=1):
        print(f"  row {i}: {sorted(row.keys())}")
    world_field = detect_world_field(sample_rows)
    print(f"Detected world field: {world_field}")

    stats_by_world = compute_stats(rows, world_field)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render_markdown(stats_by_world, world_field, schema_keys), encoding="utf-8")
    print(f"Generated: {OUT}")
    print(f"Worlds: {len(stats_by_world)}")


if __name__ == "__main__":
    main()
