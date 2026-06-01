"""Fase 13b: multi-seed confirmation for rule_109 fragility geometry.

This artifact extends the existing fragility dataset with two fresh rule_109
seeds and updates the position map/report with an explicit verdict.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "outputs" / "fragility_fase10"
RESULTS_JSONL = OUT_DIR / "fragility_results.jsonl"
POSITION_JSON = OUT_DIR / "fragility_position_map.json"
POSITION_MD = OUT_DIR / "fragility_position_map.md"
FRAGILITY_REPORT = OUT_DIR / "fragility_report.md"
LAW_MAP = ROOT / "outputs" / "world_taxonomy" / "law_map.md"

WORLD = "rule_109"
STEPS = 48
WIDTH = 64
ORIGINAL_SEED = 20260554
NEW_SEEDS = [20260601, 20260602]
ALL_SEEDS = [ORIGINAL_SEED, *NEW_SEEDS]

CLUSTER_THRESHOLD = 0.30
CONFIRMATION_BIN_RANGE_THRESHOLD = 0.50
CENTRAL_QUARTILE_MIN = 16
CENTRAL_QUARTILE_MAX = 47
ARTIFACT_SHIFT_THRESHOLD = 16


def load_fragility_module() -> Any:
    module_path = OUT_DIR / "run_fragility.py"
    spec = importlib.util.spec_from_file_location("run_fragility_artifact", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_records() -> list[dict[str, Any]]:
    if not RESULTS_JSONL.exists():
        return []
    return [
        json.loads(line)
        for line in RESULTS_JSONL.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def append_missing_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frag = load_fragility_module()
    existing = {
        (row["world"], int(row["seed"]), int(row["steps"]), int(row["bit_position"]))
        for row in records
    }
    added: list[dict[str, Any]] = []

    for seed in NEW_SEEDS:
        reference_ic = frag.random_initial_state(WIDTH, seed=seed)
        reference = frag.evaluate_ic(WORLD, seed, STEPS, reference_ic)
        reference_signature = tuple(sorted(reference["laws_accepted"]))

        for bit_position in range(WIDTH):
            key = (WORLD, seed, STEPS, bit_position)
            if key in existing:
                continue

            perturbed_ic = reference_ic.copy()
            perturbed_ic[bit_position] = np.uint8(1 - perturbed_ic[bit_position])
            perturbed = frag.evaluate_ic(WORLD, seed, STEPS, perturbed_ic)
            outcome = frag.classify_outcome(reference_signature, perturbed)

            added.append(
                {
                    "world": WORLD,
                    "seed": seed,
                    "steps": STEPS,
                    "bit_position": bit_position,
                    "outcome": outcome,
                    "reference_sig": list(reference_signature),
                    "perturbed_sig": list(perturbed["signature"]),
                    "reference_status": reference["analysis_status"],
                    "perturbed_status": perturbed["analysis_status"],
                    "reference_dedup_structure_count": reference["dedup_structure_count"],
                    "perturbed_dedup_structure_count": perturbed["dedup_structure_count"],
                }
            )

    if added:
        with RESULTS_JSONL.open("a", encoding="utf-8") as handle:
            for row in added:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
    return records + added


def fmt(value: float) -> str:
    return f"{value:.3f}"


def bin_means_from_vec(vec: list[float]) -> list[float]:
    return [mean(vec[i * 8 : (i + 1) * 8]) for i in range(8)]


def top10_from_vec(vec: list[float]) -> list[int]:
    return sorted(range(WIDTH), key=lambda idx: (-vec[idx], idx))[:10]


def peak_bin(bin_means: list[float]) -> int:
    max_value = max(bin_means)
    return next(idx for idx, value in enumerate(bin_means) if value == max_value)


def peak_center(bin_idx: int) -> float:
    return bin_idx * 8 + 3.5


def seed_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    ordered = sorted(items, key=lambda row: int(row["bit_position"]))
    if len(ordered) != WIDTH:
        raise RuntimeError(f"Expected {WIDTH} rows, got {len(ordered)}")

    counts = Counter(row["outcome"] for row in ordered)
    vec = [0.0 if row["outcome"] == "same_sig" else 1.0 for row in ordered]
    bins = bin_means_from_vec(vec)
    pbin = peak_bin(bins)
    pcenter = peak_center(pbin)
    central_peak = CENTRAL_QUARTILE_MIN <= pcenter <= CENTRAL_QUARTILE_MAX

    return {
        "seed": int(ordered[0]["seed"]),
        "steps": int(ordered[0]["steps"]),
        "f_other_sig": counts["other_sig"] / WIDTH,
        "f_silence": counts["silence"] / WIDTH,
        "f_noise": counts["noise"] / WIDTH,
        "f_total": (counts["other_sig"] + counts["silence"] + counts["noise"]) / WIDTH,
        "fragility_vec": vec,
        "bin_means": bins,
        "bin_range": max(bins) - min(bins),
        "top10_positions": top10_from_vec(vec),
        "peak_bin": pbin,
        "peak_center": pcenter,
        "central_peak": central_peak,
        "reference_signature": ordered[0]["reference_sig"],
    }


def rule109_summaries(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        if row.get("world") == WORLD and int(row.get("steps", -1)) == STEPS and int(row.get("seed", -1)) in ALL_SEEDS:
            grouped[int(row["seed"])].append(row)
    missing = [seed for seed in ALL_SEEDS if len(grouped.get(seed, [])) != WIDTH]
    if missing:
        raise RuntimeError(f"Missing complete rule_109 fragility rows for seeds: {missing}")
    return [seed_summary(grouped[seed]) for seed in ALL_SEEDS]


def aggregate_position_entry(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    mean_vec = [
        mean(summary["fragility_vec"][idx] for summary in summaries)
        for idx in range(WIDTH)
    ]
    bins = bin_means_from_vec(mean_vec)
    return {
        "mean_fragility_vec": mean_vec,
        "bin_means": bins,
        "top10_positions": top10_from_vec(mean_vec),
        "left_mean": mean(mean_vec[:32]),
        "right_mean": mean(mean_vec[32:]),
        "bin_range": max(bins) - min(bins),
        "pattern": "clustered" if max(bins) - min(bins) > CLUSTER_THRESHOLD else "dispersed",
        "n_seeds": len(summaries),
        "seeds": [summary["seed"] for summary in summaries],
        "fase13b_seed_summaries": [
            {
                "seed": summary["seed"],
                "f_total": summary["f_total"],
                "f_other_sig": summary["f_other_sig"],
                "f_silence": summary["f_silence"],
                "f_noise": summary["f_noise"],
                "bin_range": summary["bin_range"],
                "peak_bin": summary["peak_bin"],
                "peak_center": summary["peak_center"],
                "central_peak": summary["central_peak"],
            }
            for summary in summaries
        ],
    }


def decide_verdict(summaries: list[dict[str, Any]]) -> dict[str, Any]:
    high_bin_range = [summary for summary in summaries if summary["bin_range"] > CONFIRMATION_BIN_RANGE_THRESHOLD]
    central_peak = [summary for summary in summaries if summary["central_peak"]]
    centers = [summary["peak_center"] for summary in summaries]
    max_shift = max(centers) - min(centers)

    confirmed = len(high_bin_range) >= 2 and len(central_peak) >= 2
    artifact = (not confirmed) or max_shift > ARTIFACT_SHIFT_THRESHOLD

    if confirmed:
        label = "cluster_confirmado"
        text = (
            "Cluster confirmado como propiedad robusta de `rule_109`: al menos "
            "2/3 seeds tienen `bin_range > 0.5` y pico central."
        )
    else:
        label = "artefacto_ic"
        text = (
            "Artefacto IC / no confirmado: el cluster original no persiste bajo "
            "dos seeds frescas con el criterio Fase 13b."
        )

    if max_shift > ARTIFACT_SHIFT_THRESHOLD:
        text += f" El desplazamiento máximo de pico es {max_shift:.1f} posiciones (>16)."

    return {
        "label": label,
        "text": text,
        "confirmed": confirmed,
        "artifact": artifact,
        "n_high_bin_range": len(high_bin_range),
        "n_central_peak": len(central_peak),
        "peak_centers": centers,
        "max_peak_shift": max_shift,
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def render_rule109_section(entry: dict[str, Any], summaries: list[dict[str, Any]], verdict: dict[str, Any]) -> str:
    bin_rows = [
        [str(idx), f"{idx * 8}-{idx * 8 + 7}", fmt(value)]
        for idx, value in enumerate(entry["bin_means"])
    ]
    seed_rows = [
        [
            str(summary["seed"]),
            fmt(summary["f_total"]),
            fmt(summary["f_other_sig"]),
            fmt(summary["f_silence"]),
            fmt(summary["f_noise"]),
            fmt(summary["bin_range"]),
            str(summary["peak_bin"]),
            fmt(summary["peak_center"]),
            "yes" if summary["central_peak"] else "no",
        ]
        for summary in summaries
    ]
    return f"""### rule_109 (3 seeds) - Fase 13b multi-seed confirmation

Bin fragility (8 bins x 8 positions, mean across 3 seeds):

{markdown_table(["Bin", "Positions", "Mean fragility"], bin_rows)}

Per-seed comparison:

{markdown_table(
        [
            "seed",
            "f_total",
            "f_other_sig",
            "f_silence",
            "f_noise",
            "bin_range",
            "peak_bin",
            "peak_center",
            "central_peak",
        ],
        seed_rows,
    )}

Top 10 fragile positions: {entry["top10_positions"]}

Left half (0-31) mean: {fmt(entry["left_mean"])} | Right half (32-63) mean: {fmt(entry["right_mean"])}

Pattern: {entry["pattern"]} (bin_range = {fmt(entry["bin_range"])})

Fase 13b verdict: **{verdict["label"]}**. {verdict["text"]}
"""


def replace_rule109_section(text: str, new_section: str) -> str:
    start_marker = "### rule_109"
    next_marker = "\n### rule_110"
    start = text.index(start_marker)
    end = text.index(next_marker, start)
    return text[:start] + new_section.rstrip() + "\n" + text[end:]


def replace_cross_world_rule109(text: str, entry: dict[str, Any]) -> str:
    old_prefix = "| rule_109 |"
    lines = text.splitlines()
    replacement = (
        f"| rule_109 | {fmt(entry['left_mean'])} | {fmt(entry['right_mean'])} | "
        f"{fmt(entry['bin_range'])} | {entry['pattern']} |"
    )
    for idx, line in enumerate(lines):
        if line.startswith(old_prefix):
            lines[idx] = replacement
            break
    return "\n".join(lines) + "\n"


def update_position_artifacts(entry: dict[str, Any], summaries: list[dict[str, Any]], verdict: dict[str, Any]) -> None:
    data = json.loads(POSITION_JSON.read_text(encoding="utf-8"))
    data[WORLD] = entry | {"fase13b_verdict": verdict}
    POSITION_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    text = POSITION_MD.read_text(encoding="utf-8")
    text = replace_rule109_section(text, render_rule109_section(entry, summaries, verdict))
    text = replace_cross_world_rule109(text, entry)
    POSITION_MD.write_text(text, encoding="utf-8")


def update_fragility_report(summaries: list[dict[str, Any]], verdict: dict[str, Any]) -> None:
    text = FRAGILITY_REPORT.read_text(encoding="utf-8")
    marker = "\n## Two Fragility Mechanisms\n"
    seed_rows = [
        [
            str(summary["seed"]),
            fmt(summary["f_total"]),
            fmt(summary["f_other_sig"]),
            fmt(summary["f_silence"]),
            fmt(summary["f_noise"]),
            fmt(summary["bin_range"]),
            str(summary["peak_bin"]),
            "yes" if summary["central_peak"] else "no",
        ]
        for summary in summaries
    ]
    section = f"""
## Fase 13b: rule_109 Multi-Seed Confirmation

Fase 13b reran `rule_109` at `steps=48`, `width=64` with two fresh seeds
(`20260601`, `20260602`) and compared them against the original seed
`20260554`.

{markdown_table(["seed", "f_total", "f_other_sig", "f_silence", "f_noise", "bin_range", "peak_bin", "central_peak"], seed_rows)}

Verdict: **{verdict["label"]}**. {verdict["text"]}

"""
    if "## Fase 13b: rule_109 Multi-Seed Confirmation" in text:
        start = text.index("## Fase 13b: rule_109 Multi-Seed Confirmation")
        end = text.index(marker, start)
        text = text[:start] + section.lstrip() + text[end:]
    else:
        text = text.replace(marker, "\n" + section + marker.lstrip(), 1)
    FRAGILITY_REPORT.write_text(text, encoding="utf-8")


def annotate_law_map_if_artifact(verdict: dict[str, Any]) -> None:
    if verdict["label"] != "artefacto_ic":
        return
    text = LAW_MAP.read_text(encoding="utf-8")
    note = (
        "\nNote: `rule_109` fragility geometry is IC-dependent after Fase 13b; "
        "`f_total=0.250` remains the original seed value and should be treated "
        "as preliminary until a replacement aggregate is adopted.\n"
    )
    if "rule_109` fragility geometry is IC-dependent" in text:
        return
    marker = "\n## Law Coverage Matrix\n"
    text = text.replace(marker, note + marker, 1)
    LAW_MAP.write_text(text, encoding="utf-8")


def main() -> None:
    records = load_records()
    all_records = append_missing_records(records)
    summaries = rule109_summaries(all_records)
    entry = aggregate_position_entry(summaries)
    verdict = decide_verdict(summaries)
    update_position_artifacts(entry, summaries, verdict)
    update_fragility_report(summaries, verdict)
    annotate_law_map_if_artifact(verdict)
    print(json.dumps({"summaries": summaries, "aggregate": entry, "verdict": verdict}, indent=2))


if __name__ == "__main__":
    main()
