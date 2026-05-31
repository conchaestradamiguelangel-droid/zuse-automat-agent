"""Fase 17: formal atlas profile for rule_108 local oscillator.

Experimental/documentation artifact only. It does not modify production code.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from zaa.consensus import deduplicate_structures
from zaa.cycle_laws import evaluate_cycle_laws
from zaa.eca import simulate
from zaa.observers import run_observers


OUT_DIR = ROOT / "outputs" / "profile_fase17"
PROFILE_JSON = OUT_DIR / "rule108_seed_profile.json"
FRAGILITY_JSON = OUT_DIR / "rule108_fragility.json"

RULE = 108
WORLD = "rule_108"
WIDTH = 128
STEPS = 200
SEEDS = list(range(20260523, 20260529))
DEDUP_STRUCTURE_NOISE_THRESHOLD = 40

IC_PATTERNS: dict[str, tuple[int, ...]] = {
    "point": (0,),
    "pair_gap1": (-1, 1),
    "triple": (-1, 0, 1),
}
CANONICAL_IC = "pair_gap1"
CORE_LAWS = {"periodicidad", "tipo_unico"}
LAW_ORDER = [
    "velocidad_constante",
    "periodicidad",
    "densidad_estable",
    "tipo_unico",
    "complejidad_alta",
    "frontera_temporal",
    "temporal_scale_stability",
]


def make_ic(pattern_name: str) -> np.ndarray:
    state = np.zeros(WIDTH, dtype=np.uint8)
    center = WIDTH // 2
    for offset in IC_PATTERNS[pattern_name]:
        state[(center + offset) % WIDTH] = 1
    return state


def active_span(frame: np.ndarray) -> int:
    xs = np.flatnonzero(frame)
    if xs.size == 0:
        return 0
    return int(xs.max() - xs.min() + 1)


def signature(laws: list[str]) -> tuple[str, ...]:
    return tuple(sorted(laws))


def core_signature(laws: list[str]) -> tuple[str, ...]:
    return tuple(sorted(set(laws) & CORE_LAWS))


def evaluate_ic(initial_state: np.ndarray) -> dict[str, Any]:
    frames = simulate(initial_state, RULE, STEPS)
    structures = run_observers(frames)
    dedup_count = len(deduplicate_structures(structures))
    raw_count = len(structures)
    analysis_status = (
        "ruido_no_analizable"
        if dedup_count > DEDUP_STRUCTURE_NOISE_THRESHOLD
        else "ok"
    )
    law_report = (
        evaluate_cycle_laws(structures, frames, STEPS)
        if analysis_status == "ok"
        else {"laws_accepted": [], "details": []}
    )
    type_counts = Counter(structure.tipo for structure in structures)
    dominant_type = type_counts.most_common(1)[0][0] if type_counts else None
    spans = [active_span(frame) for frame in frames]
    return {
        "analysis_status": analysis_status,
        "analysis_ok": analysis_status == "ok",
        "raw_structure_count": raw_count,
        "dedup_structure_count": dedup_count,
        "dominant_type": dominant_type,
        "type_counts": dict(type_counts),
        "laws_accepted": law_report["laws_accepted"],
        "details": law_report.get("details", []),
        "signature": list(signature(law_report["laws_accepted"])),
        "core_signature": list(core_signature(law_report["laws_accepted"])),
        "final_active_span": spans[-1],
        "max_active_span": max(spans),
        "final_active_count": int(np.sum(frames[-1] != 0)),
        "max_active_count": int(np.max(np.sum(frames != 0, axis=1))),
    }


def frequency_class(count: int) -> str:
    if count >= 4:
        return "core"
    if count >= 2:
        return "present"
    if count == 1:
        return "trace"
    return "absent"


def profile_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for seed in SEEDS:
        for ic_type in ("point", CANONICAL_IC, "triple"):
            result = evaluate_ic(make_ic(ic_type))
            rows.append(
                {
                    "seed": seed,
                    "ic_type": ic_type,
                    "steps": STEPS,
                    "width": WIDTH,
                    **result,
                }
            )
    return rows


def formal_profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    canonical_rows = [row for row in rows if row["ic_type"] == CANONICAL_IC]
    law_counts = Counter()
    signatures = Counter()
    for row in canonical_rows:
        law_counts.update(row["laws_accepted"])
        signatures.update([tuple(row["laws_accepted"])])
    non_empty_visits = sum(bool(row["laws_accepted"]) for row in canonical_rows)
    noise_visits = sum(row["analysis_status"] == "ruido_no_analizable" for row in canonical_rows)
    unique_non_empty = len({tuple(row["laws_accepted"]) for row in canonical_rows if row["laws_accepted"]})
    peak_diversity = unique_non_empty / non_empty_visits if non_empty_visits >= 5 else None
    return {
        WORLD: {
            "rule_id": RULE,
            "classification": "oscilador-local",
            "ic_type": CANONICAL_IC,
            "control_ic_type": "point",
            "motif": "#.# <-> ###",
            "steps": STEPS,
            "width": WIDTH,
            "seeds": SEEDS,
            "total_visits": len(canonical_rows),
            "ok_visits": sum(row["analysis_ok"] for row in canonical_rows),
            "noise_visits": noise_visits,
            "non_empty_visits": non_empty_visits,
            "non_empty_ratio": non_empty_visits / len(canonical_rows),
            "peak_diversity": peak_diversity,
            "mean_n_laws": mean(len(row["laws_accepted"]) for row in canonical_rows),
            "mean_dedup_structure_count": mean(row["dedup_structure_count"] for row in canonical_rows),
            "mean_final_active_span": mean(row["final_active_span"] for row in canonical_rows),
            "law_frequencies": {
                law: {
                    "count": law_counts[law],
                    "rate": law_counts[law] / len(canonical_rows),
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
    }


def classify_pattern(vec: list[int]) -> dict[str, Any]:
    bin_means = [
        mean(vec[start : start + 8])
        for start in range(0, WIDTH, 8)
    ]
    left_mean = mean(vec[: WIDTH // 2])
    right_mean = mean(vec[WIDTH // 2 :])
    bin_range = max(bin_means) - min(bin_means)
    pattern = "clustered" if bin_range > 0.3 else "dispersed"
    top_positions = sorted(range(WIDTH), key=lambda idx: vec[idx], reverse=True)[:10]
    return {
        "bin_means": bin_means,
        "left_mean": left_mean,
        "right_mean": right_mean,
        "bin_range": bin_range,
        "pattern": pattern,
        "top10_positions": top_positions,
    }


def fragility_profile() -> dict[str, Any]:
    reference_ic = make_ic(CANONICAL_IC)
    reference = evaluate_ic(reference_ic)
    reference_sig = signature(reference["laws_accepted"])
    reference_core = core_signature(reference["laws_accepted"])
    rows: list[dict[str, Any]] = []
    total_vec: list[int] = []
    core_vec: list[int] = []

    for bit_position in range(WIDTH):
        perturbed = reference_ic.copy()
        perturbed[bit_position] = 1 - perturbed[bit_position]
        result = evaluate_ic(perturbed)
        perturbed_sig = signature(result["laws_accepted"])
        perturbed_core = core_signature(result["laws_accepted"])
        total_changed = (
            result["analysis_status"] == "ruido_no_analizable"
            or perturbed_sig != reference_sig
        )
        core_changed = (
            result["analysis_status"] == "ruido_no_analizable"
            or perturbed_core != reference_core
        )
        total_vec.append(1 if total_changed else 0)
        core_vec.append(1 if core_changed else 0)
        rows.append(
            {
                "world": WORLD,
                "seed": SEEDS[0],
                "ic_type": CANONICAL_IC,
                "steps": STEPS,
                "width": WIDTH,
                "bit_position": bit_position,
                "analysis_status": result["analysis_status"],
                "reference_signature": list(reference_sig),
                "perturbed_signature": list(perturbed_sig),
                "reference_core_signature": list(reference_core),
                "perturbed_core_signature": list(perturbed_core),
                "total_changed": total_changed,
                "core_changed": core_changed,
                "dedup_structure_count": result["dedup_structure_count"],
                "laws_accepted": result["laws_accepted"],
            }
        )

    total_map = classify_pattern(total_vec)
    core_map = classify_pattern(core_vec)
    return {
        WORLD: {
            "rule_id": RULE,
            "ic_type": CANONICAL_IC,
            "seed": SEEDS[0],
            "steps": STEPS,
            "width": WIDTH,
            "core_laws": sorted(CORE_LAWS),
            "reference_signature": list(reference_sig),
            "reference_core_signature": list(reference_core),
            "f_total": mean(total_vec),
            "f_core": mean(core_vec),
            "f_silence": sum(1 for row in rows if row["analysis_status"] == "ok" and not row["laws_accepted"]) / WIDTH,
            "f_noise": sum(1 for row in rows if row["analysis_status"] == "ruido_no_analizable") / WIDTH,
            "total_fragility_vec": total_vec,
            "core_fragility_vec": core_vec,
            "fragility_pattern": total_map["pattern"],
            "core_fragility_pattern": core_map["pattern"],
            "total_position_map": total_map,
            "core_position_map": core_map,
            "rows": rows,
        }
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = profile_rows()
    profile = formal_profile(rows)
    fragility = fragility_profile()
    PROFILE_JSON.write_text(json.dumps(profile, indent=2, sort_keys=True), encoding="utf-8")
    FRAGILITY_JSON.write_text(json.dumps(fragility, indent=2, sort_keys=True), encoding="utf-8")
    item = profile[WORLD]
    frag = fragility[WORLD]
    print(f"Wrote {PROFILE_JSON}")
    print(f"Wrote {FRAGILITY_JSON}")
    print(f"rule_108 periodicidad canonical: {item['law_frequencies']['periodicidad']['count']}/6")
    print(f"rule_108 dedup mean: {item['mean_dedup_structure_count']:.3f}")
    print(f"rule_108 f_total={frag['f_total']:.3f} f_core={frag['f_core']:.3f} pattern={frag['fragility_pattern']}")


if __name__ == "__main__":
    main()
