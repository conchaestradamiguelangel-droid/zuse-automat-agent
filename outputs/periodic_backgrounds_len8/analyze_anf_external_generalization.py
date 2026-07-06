#!/usr/bin/env python3
"""Fase 49: ANF gradient generalization on external len-9/10 T=15 backgrounds."""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
ANF44_SCRIPT = OUT_DIR / "analyze_anf_degree.py"
TARGETED_SCRIPT = OUT_DIR / "targeted_len9_len10_t15.py"
TARGETED_JSONL = OUT_DIR / "targeted_len9_len10_t15_results.jsonl"
RESULTS_JSON = OUT_DIR / "anf_external_generalization_results.json"
REPORT_MD = OUT_DIR / "anf_external_generalization_report.md"
CHECKPOINT_JSON = OUT_DIR / "anf_external_generalization_checkpoint.json"

T_WINDOW = 12
WINDOW_CELLS = 25
CENTER_INDEX = 12
LEN8_INTERCEPT = 7.241925
LEN8_SLOPE_MAG = 0.307283
SLOPE_TOLERANCE = 0.10
INTERCEPT_TOLERANCE = 0.05
PARTIAL_EXCEPTION_RATE = 0.05


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def minimal_external_witnesses() -> list[dict[str, Any]]:
    positives = [row for row in load_jsonl(TARGETED_JSONL) if row.get("detected_t15")]
    by_key: dict[tuple[int, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in positives:
        by_key[(int(row["length"]), int(row["rule"]), row["background"])].append(row)

    witnesses = []
    for key, rows in sorted(by_key.items()):
        selected = min(rows, key=lambda item: (int(item["word_len"]), item["word"]))
        widths = sorted({width for row in rows for width in row.get("defect_width_per_state", [])})
        witnesses.append(
            {
                "length": key[0],
                "rule": key[1],
                "background": key[2],
                "ic": selected["word"],
                "word_len": int(selected["word_len"]),
                "detection_count": len(rows),
                "defect_widths_observed": widths,
                "defect_states": selected.get("defect_states"),
                "background_preperiod": selected.get("background_preperiod"),
                "T_bg": selected.get("T_bg"),
                "T_local": selected.get("T_local"),
            }
        )
    return witnesses


def replay_t15(targeted, base, row: dict[str, Any]) -> dict[str, Any]:
    word_value = int(row["ic"], 2)
    result = targeted.detect_t15(
        base,
        int(row["rule"]),
        row["background"],
        int(row["word_len"]),
        word_value,
    )
    return {
        "detected_t15": bool(result.get("detected_t15")),
        "reason": result.get("reason"),
        "background_phase_exact": bool(result.get("background_phase_exact")),
        "cycle_length_under_F3": result.get("cycle_length_under_F3"),
        "states_distinct": result.get("states_distinct"),
        "cycle_closes_after_five": result.get("cycle_closes_after_five"),
        "four_cycles_repeat": result.get("four_cycles_repeat"),
        "stationary_over_local_period": result.get("stationary_over_local_period"),
        "drift": result.get("drift"),
        "defect_width_per_state": result.get("defect_width_per_state"),
    }


def unpack_coefficients(table: np.ndarray, final_bg_bit: int, ones: np.ndarray, anf44) -> dict[str, Any]:
    packed = table.copy()
    if final_bg_bit:
        packed ^= ones
    bits = np.unpackbits(packed.view(np.uint8), bitorder="little")
    anf44.mobius_inplace(bits)
    popcount16 = np.array([int(value).bit_count() for value in range(1 << 16)], dtype=np.uint8)
    degree, monomial_count, histogram = anf44.degree_and_count(bits, popcount16)
    return {
        "degree": degree,
        "monomial_count": monomial_count,
        "degree_histogram": histogram,
        "constant_term": int(bits[0]),
    }


def analyze_witness(anf44, variables, base, witness: dict[str, Any]) -> dict[str, Any]:
    rule = int(witness["rule"])
    background = witness["background"]
    ic = witness["ic"]
    simulated = anf44.simulate_cone(base, variables, rule, background, ic)
    rows = simulated["rows"]
    positions = simulated["positions"]
    bg_frames = simulated["bg_frames"]
    ones = simulated["ones"]
    bg_final = set(bg_frames[T_WINDOW])
    bg0 = set(bg_frames[0])
    assignment = anf44.concrete_assignment(base, bg0, positions, ic)
    concrete_diff = [
        anf44.packed_bit(table, assignment) ^ anf44.bit_from_state(bg_final, global_pos, base.WIDTH)
        for table, global_pos in zip(rows, positions)
    ]
    active_indices = [idx for idx, bit in enumerate(concrete_diff) if bit]

    active_outputs = []
    for idx in active_indices:
        result = unpack_coefficients(
            rows[idx],
            anf44.bit_from_state(bg_final, positions[idx], base.WIDTH),
            ones,
            anf44,
        )
        dist = abs(idx - CENTER_INDEX)
        epsilon = result["degree"] - (24 - dist)
        result.update(
            {
                "output_index": idx,
                "rel_pos": idx - CENTER_INDEX,
                "dist": dist,
                "epsilon": epsilon,
                "epsilon_in_band": epsilon in (0, 1),
            }
        )
        active_outputs.append(result)

    degrees = [row["degree"] for row in active_outputs]
    monomials = [row["monomial_count"] for row in active_outputs]
    epsilons = [row["epsilon"] for row in active_outputs]
    return {
        **witness,
        "active_output_count": len(active_outputs),
        "active_outputs": active_outputs,
        "active_degree_range": [min(degrees), max(degrees)] if degrees else None,
        "active_monomial_range": [min(monomials), max(monomials)] if monomials else None,
        "epsilon_range": [min(epsilons), max(epsilons)] if epsilons else None,
        "epsilon_exceptions": sum(epsilon not in (0, 1) for epsilon in epsilons),
    }


def linear_fit(xs: list[float], ys: list[float]) -> dict[str, float]:
    n = len(xs)
    x_mean = sum(xs) / n
    y_mean = sum(ys) / n
    ss_xx = sum((x - x_mean) ** 2 for x in xs)
    ss_xy = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    slope = ss_xy / ss_xx if ss_xx else 0.0
    intercept = y_mean - slope * x_mean
    ss_tot = sum((y - y_mean) ** 2 for y in ys)
    ss_res = sum((y - (intercept + slope * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot else 1.0
    return {
        "intercept": intercept,
        "slope": slope,
        "slope_magnitude": abs(slope),
        "r2": r2,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    outputs = [out for row in rows for out in row["active_outputs"]]
    exceptions = [out for out in outputs if not out["epsilon_in_band"]]
    xs = [float(out["dist"]) for out in outputs if out["monomial_count"] > 0]
    ys = [math.log10(float(out["monomial_count"])) for out in outputs if out["monomial_count"] > 0]
    fit = linear_fit(xs, ys)
    slope_delta_fraction = abs(fit["slope_magnitude"] - LEN8_SLOPE_MAG) / LEN8_SLOPE_MAG
    intercept_delta_fraction = abs(fit["intercept"] - LEN8_INTERCEPT) / LEN8_INTERCEPT
    exception_rate = len(exceptions) / len(outputs) if outputs else 1.0

    if (
        not exceptions
        and slope_delta_fraction <= SLOPE_TOLERANCE
        and intercept_delta_fraction <= INTERCEPT_TOLERANCE
    ):
        status = "ANF_GRADIENT_GENERALIZES"
    elif exception_rate <= PARTIAL_EXCEPTION_RATE or fit["r2"] >= 0.95:
        status = "PARTIAL_GENERALIZATION"
    else:
        status = "LEN8_SPECIFIC_ANF_GRADIENT"

    by_length_rule = Counter(f"len{row['length']}_rule{row['rule']}" for row in rows)
    epsilon_counts = Counter(str(out["epsilon"]) for out in outputs)
    return {
        "status": status,
        "record_count": len(rows),
        "active_output_count": len(outputs),
        "epsilon_exception_count": len(exceptions),
        "epsilon_exception_rate": exception_rate,
        "epsilon_counts": dict(sorted(epsilon_counts.items(), key=lambda item: int(item[0]))),
        "active_degree_range": [min(out["degree"] for out in outputs), max(out["degree"] for out in outputs)],
        "active_monomial_range": [
            min(out["monomial_count"] for out in outputs),
            max(out["monomial_count"] for out in outputs),
        ],
        "fit_log10_monomials_vs_dist": fit,
        "len8_reference": {
            "intercept": LEN8_INTERCEPT,
            "slope_magnitude": LEN8_SLOPE_MAG,
            "r2": 0.998197,
        },
        "slope_delta_fraction_vs_len8": slope_delta_fraction,
        "intercept_delta_fraction_vs_len8": intercept_delta_fraction,
        "records_by_length_rule": dict(sorted(by_length_rule.items())),
        "rows": rows,
    }


def load_checkpoint() -> dict[str, Any]:
    if CHECKPOINT_JSON.exists():
        return json.loads(CHECKPOINT_JSON.read_text(encoding="utf-8"))
    return {"rows": []}


def save_checkpoint(data: dict[str, Any]) -> None:
    CHECKPOINT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def analyze() -> dict[str, Any]:
    anf44 = load_module(ANF44_SCRIPT, "anf44_external")
    targeted = load_module(TARGETED_SCRIPT, "targeted_external")
    base = anf44.load_base_module()
    variables = anf44.build_variable_tables()
    witnesses = minimal_external_witnesses()
    checkpoint = load_checkpoint()
    done = {(int(row["length"]), int(row["rule"]), row["background"]) for row in checkpoint["rows"]}

    for witness in witnesses:
        key = (int(witness["length"]), int(witness["rule"]), witness["background"])
        if key in done:
            continue
        replay = replay_t15(targeted, base, witness)
        row = {**witness, "pre_anf_replay": replay}
        if replay["detected_t15"]:
            row = analyze_witness(anf44, variables, base, row)
        else:
            row.update({"active_output_count": 0, "active_outputs": [], "epsilon_exceptions": None})
        checkpoint["rows"].append(row)
        save_checkpoint(checkpoint)

    verified_rows = [row for row in checkpoint["rows"] if row.get("pre_anf_replay", {}).get("detected_t15")]
    data = summarize(verified_rows)
    data["target_background_count"] = len(witnesses)
    data["verified_background_count"] = len(verified_rows)
    data["failed_replay_count"] = len(witnesses) - len(verified_rows)
    return data


def pct(value: float) -> str:
    return f"{100.0 * value:.2f}%"


def write_report(data: dict[str, Any]) -> None:
    fit = data["fit_log10_monomials_vs_dist"]
    lines = [
        "# Fase 49: External ANF Gradient Generalization",
        "",
        "## Question",
        "",
        "Fases 44-45 established the ANF degree gradient on the original length-8",
        "`T=15` representatives. Fase 49 tests whether the same structure appears",
        "on the external length-9/10 `T=15` backgrounds found in Fase 34.",
        "",
        "The analysis reuses the exact 25-input, 12-step bit-packed cone and Mobius",
        "ANF transform from Fase 44. The external backgrounds are not rotations of",
        "the original length-8 set.",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        f"- Target external backgrounds: {data['target_background_count']}",
        f"- Replay-verified T=15 backgrounds: {data['verified_background_count']}",
        f"- Failed replay backgrounds: {data['failed_replay_count']}",
        f"- Active outputs analyzed: {data['active_output_count']}",
        f"- Active degree range: {data['active_degree_range'][0]}..{data['active_degree_range'][1]}",
        f"- Active monomial range: {data['active_monomial_range'][0]}..{data['active_monomial_range'][1]}",
        f"- Epsilon counts: `{data['epsilon_counts']}`",
        f"- Epsilon-band exceptions: {data['epsilon_exception_count']} ({pct(data['epsilon_exception_rate'])})",
        "",
        "## Log-monomial fit",
        "",
        "`log10(monomials) = a + slope * dist`",
        "",
        f"- External intercept `a`: {fit['intercept']:.6f}",
        f"- External slope: {fit['slope']:.6f}",
        f"- External slope magnitude: {fit['slope_magnitude']:.6f}",
        f"- External R^2: {fit['r2']:.6f}",
        f"- Length-8 reference intercept: {data['len8_reference']['intercept']:.6f}",
        f"- Length-8 reference slope magnitude: {data['len8_reference']['slope_magnitude']:.6f}",
        f"- Intercept delta vs length-8: {pct(data['intercept_delta_fraction_vs_len8'])}",
        f"- Slope delta vs length-8: {pct(data['slope_delta_fraction_vs_len8'])}",
        "",
        "## Representative table",
        "",
        "| length | rule | background | IC | detections | replay | active outputs | degree | epsilon | monomials |",
        "| ---: | ---: | --- | --- | ---: | --- | ---: | --- | --- | --- |",
    ]
    for row in data["rows"]:
        lines.append(
            f"| {row['length']} | {row['rule']} | `{row['background']}` | `{row['ic']}` | "
            f"{row['detection_count']} | `{row['pre_anf_replay']['detected_t15']}` | "
            f"{row['active_output_count']} | {row['active_degree_range'][0]}..{row['active_degree_range'][1]} | "
            f"{row['epsilon_range'][0]}..{row['epsilon_range'][1]} | "
            f"{row['active_monomial_range'][0]}..{row['active_monomial_range'][1]} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        ]
    )
    if data["status"] == "ANF_GRADIENT_GENERALIZES":
        lines.extend(
            [
                "The ANF gradient generalizes to the external length-9/10 `T=15`",
                "backgrounds under the tested criteria. The epsilon band remains exact",
                "and the log-monomial slope stays within the predefined tolerance of the",
                "length-8 reference.",
            ]
        )
    elif data["status"] == "PARTIAL_GENERALIZATION":
        lines.extend(
            [
                "The external backgrounds preserve part of the ANF-gradient structure,",
                "but not all strict length-8 criteria simultaneously. This is evidence",
                "for a qualitative generalization rather than an exact constant-level",
                "extension of the length-8 law.",
            ]
        )
    else:
        lines.extend(
            [
                "The external backgrounds do not preserve the length-8 ANF-gradient",
                "structure under the tested criteria. The law should be treated as",
                "length-8-specific until a different variable-length formulation is",
                "found.",
            ]
        )
    lines.extend(
        [
            "",
            "Note: the Fase 34 external witnesses have varying active defect widths,",
            "so Fase 49 does not assume a constant visual defect width. The 25-cell",
            "cone is fixed by the radius-1, 12-step causal horizon.",
            "",
        ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_report(analyze())
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")


if __name__ == "__main__":
    main()
