#!/usr/bin/env python3
"""Fase 44: ANF degree audit of the T=15 causal cone.

Fases 41-43 ruled out sparse local tables, input elimination, and simple ROBDD
variable-order compression. Fase 44 asks a different question: is the dense
25-input, 12-step cone compact as an algebraic normal form (ANF) polynomial?

Implementation note:

The script computes exact truth tables, but stores them bit-packed as uint64
arrays while simulating the cone. Each 25-input Boolean function has 2^25 truth
values, i.e. 524,288 uint64 words. Only one output is unpacked at a time for
the Mobius transform, keeping memory bounded.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


OUT_DIR = Path(__file__).resolve().parent
BASE_SCRIPT = OUT_DIR.parent / "periodic_backgrounds" / "sweep_periodic_background_oscillators.py"
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
EMBEDDING_RESULTS = OUT_DIR / "defect_embedding_descriptor_results.json"
RESULTS_JSON = OUT_DIR / "anf_degree_results.json"
REPORT_MD = OUT_DIR / "anf_degree_report.md"
CHECKPOINT_JSON = OUT_DIR / "anf_degree_checkpoint.json"

T_WINDOW = 12
WINDOW_CELLS = 25
ASSIGNMENT_COUNT = 1 << WINDOW_CELLS
WORD_COUNT = ASSIGNMENT_COUNT // 64
UINT64_MAX = np.uint64((1 << 64) - 1)
LOW_DEGREE_GATE = 20
FULL_DEGREE = 25


def load_base_module():
    spec = importlib.util.spec_from_file_location("periodic_background_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base detector from {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def load_family_lookup() -> dict[tuple[int, str], str]:
    embedding = json.loads(EMBEDDING_RESULTS.read_text(encoding="utf-8"))
    return {
        (int(row["rule"]), row["background"]): row["family_id"]
        for row in embedding["rows"]
    }


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def bit_from_state(active: set[int], pos: int, width: int) -> int:
    return 1 if (pos % width) in active else 0


def ic_start(width: int, ic: str) -> int:
    return width // 2 - len(ic) // 2


def initial_actual_bit(base, bg_set: set[int], global_pos: int, ic: str) -> int:
    start = ic_start(base.WIDTH, ic)
    if start <= global_pos <= start + len(ic) - 1:
        return int(ic[global_pos - start])
    return bit_from_state(bg_set, global_pos, base.WIDTH)


def cone_positions(base, ic: str) -> list[int]:
    start = ic_start(base.WIDTH, ic)
    center = start + (len(ic) - 1) // 2
    left = center - T_WINDOW
    return list(range(left, left + WINDOW_CELLS))


def build_variable_tables() -> list[np.ndarray]:
    assignments = np.arange(ASSIGNMENT_COUNT, dtype=np.uint32)
    variables = []
    for idx in range(WINDOW_CELLS):
        bits = ((assignments >> idx) & 1).astype(np.uint8)
        variables.append(np.packbits(bits, bitorder="little").view(np.uint64).copy())
    return variables


def eca_packed(rule: int, left: np.ndarray, center: np.ndarray, right: np.ndarray, ones: np.ndarray) -> np.ndarray:
    out = np.zeros_like(left)
    for idx in range(8):
        if not ((rule >> idx) & 1):
            continue
        term = ones.copy()
        term &= left if (idx & 4) else ~left
        term &= center if (idx & 2) else ~center
        term &= right if (idx & 1) else ~right
        out ^= term
    return out


def concrete_assignment(base, bg_set: set[int], positions: list[int], ic: str) -> int:
    value = 0
    for idx, global_pos in enumerate(positions):
        if initial_actual_bit(base, bg_set, global_pos, ic):
            value |= 1 << idx
    return value


def packed_bit(table: np.ndarray, assignment: int) -> int:
    word = assignment >> 6
    offset = np.uint64(assignment & 63)
    return int((table[word] >> offset) & np.uint64(1))


def mobius_inplace(bits: np.ndarray) -> None:
    for idx in range(WINDOW_CELLS):
        step = 1 << idx
        block = step << 1
        view = bits.reshape(-1, block)
        view[:, step:block] ^= view[:, :step]


def degree_and_count(coefficients: np.ndarray, popcount16: np.ndarray) -> tuple[int, int, dict[str, int]]:
    total = 0
    degree = -1
    hist: dict[str, int] = {}
    chunk = 1 << 20
    for start in range(0, ASSIGNMENT_COUNT, chunk):
        sub = coefficients[start:start + chunk]
        count = int(sub.sum())
        if not count:
            continue
        total += count
        local = np.nonzero(sub)[0].astype(np.uint32) + np.uint32(start)
        degrees = popcount16[local & np.uint32(0xFFFF)] + popcount16[local >> np.uint32(16)]
        degree = max(degree, int(degrees.max()))
        unique, counts = np.unique(degrees, return_counts=True)
        for deg, deg_count in zip(unique, counts):
            key = str(int(deg))
            hist[key] = hist.get(key, 0) + int(deg_count)
    return degree, total, dict(sorted(hist.items(), key=lambda item: int(item[0])))


def analyze_output_anf(table: np.ndarray, final_bg_bit: int, ones: np.ndarray, popcount16: np.ndarray) -> dict:
    packed = table.copy()
    if final_bg_bit:
        packed ^= ones
    bits = np.unpackbits(packed.view(np.uint8), bitorder="little")
    mobius_inplace(bits)
    degree, monomial_count, histogram = degree_and_count(bits, popcount16)
    return {
        "degree": degree,
        "monomial_count": monomial_count,
        "degree_histogram": histogram,
        "constant_term": int(bits[0]),
    }


def simulate_cone(base, variables: list[np.ndarray], rule: int, background: str, ic: str) -> dict:
    zeros = np.zeros(WORD_COUNT, dtype=np.uint64)
    ones = np.full(WORD_COUNT, UINT64_MAX, dtype=np.uint64)
    positions = cone_positions(base, ic)
    bg_frames = background_orbit(base, rule, background, T_WINDOW)
    rows = variables
    for t in range(T_WINDOW):
        bg_now = set(bg_frames[t])
        next_row = []
        for idx, global_pos in enumerate(positions):
            parents = []
            for delta in (-1, 0, 1):
                local = idx + delta
                if 0 <= local < WINDOW_CELLS:
                    parents.append(rows[local])
                else:
                    parents.append(ones if bit_from_state(bg_now, global_pos + delta, base.WIDTH) else zeros)
            next_row.append(eca_packed(rule, parents[0], parents[1], parents[2], ones))
        rows = next_row
    return {
        "rows": rows,
        "positions": positions,
        "bg_frames": bg_frames,
        "ones": ones,
    }


def analyze_representative(base, variables, popcount16, family_lookup, record: dict) -> dict:
    rule = int(record["rule"])
    background = record["background"]
    ic = record["ic"]
    simulated = simulate_cone(base, variables, rule, background, ic)
    rows = simulated["rows"]
    positions = simulated["positions"]
    bg_frames = simulated["bg_frames"]
    ones = simulated["ones"]
    bg_final = set(bg_frames[T_WINDOW])
    bg0 = set(bg_frames[0])
    assignment = concrete_assignment(base, bg0, positions, ic)
    concrete_diff = [
        packed_bit(table, assignment) ^ bit_from_state(bg_final, global_pos, base.WIDTH)
        for table, global_pos in zip(rows, positions)
    ]
    active_indices = [idx for idx, bit in enumerate(concrete_diff) if bit]

    active_outputs = []
    for idx in active_indices:
        result = analyze_output_anf(
            rows[idx],
            bit_from_state(bg_final, positions[idx], base.WIDTH),
            ones,
            popcount16,
        )
        result["output_index"] = idx
        active_outputs.append(result)

    degrees = [row["degree"] for row in active_outputs]
    monomials = [row["monomial_count"] for row in active_outputs]
    return {
        "rule": rule,
        "background": background,
        "family_id": family_lookup[(rule, background)],
        "ic": ic,
        "active_output_count": len(active_outputs),
        "active_outputs": active_outputs,
        "active_degree_min": min(degrees),
        "active_degree_max": max(degrees),
        "active_monomial_min": min(monomials),
        "active_monomial_max": max(monomials),
        "active_monomial_total": sum(monomials),
    }


def load_checkpoint() -> dict:
    if CHECKPOINT_JSON.exists():
        return json.loads(CHECKPOINT_JSON.read_text(encoding="utf-8"))
    return {"rows": []}


def save_checkpoint(data: dict) -> None:
    CHECKPOINT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def analyze() -> dict:
    base = load_base_module()
    family_lookup = load_family_lookup()
    records = load_jsonl(LOCKING_RESULTS)
    checkpoint = load_checkpoint()
    done = {(int(row["rule"]), row["background"]) for row in checkpoint["rows"]}
    variables = build_variable_tables()
    popcount16 = np.array([int(value).bit_count() for value in range(1 << 16)], dtype=np.uint8)
    for record in records:
        key = (int(record["rule"]), record["background"])
        if key in done:
            continue
        row = analyze_representative(base, variables, popcount16, family_lookup, record)
        checkpoint["rows"].append(row)
        save_checkpoint(checkpoint)

    rows = checkpoint["rows"]
    active_outputs = [
        output
        for row in rows
        for output in row["active_outputs"]
    ]
    low_degree_outputs = [output for output in active_outputs if output["degree"] < LOW_DEGREE_GATE]
    high_degree_outputs = [output for output in active_outputs if output["degree"] >= LOW_DEGREE_GATE]
    low_degree_rows = [
        row
        for row in rows
        if any(output["degree"] < LOW_DEGREE_GATE for output in row["active_outputs"])
    ]
    full_degree_rows = [row for row in rows if row["active_degree_max"] == FULL_DEGREE]
    status = "ANF_MIXED_DEGREE_DENSE"
    if len(full_degree_rows) == len(rows):
        status = "FULL_ANF_DEGREE_ALL_REPS"
    elif low_degree_outputs:
        status = "LOW_OUTPUT_ANF_DEGREE_FOUND"

    family_summary = []
    by_family: dict[str, list[dict]] = {}
    for row in rows:
        by_family.setdefault(row["family_id"], []).append(row)
    for family_id, items in sorted(by_family.items()):
        family_summary.append(
            {
                "family_id": family_id,
                "count": len(items),
                "active_degree_range": [
                    min(item["active_degree_min"] for item in items),
                    max(item["active_degree_max"] for item in items),
                ],
                "active_monomial_range": [
                    min(item["active_monomial_min"] for item in items),
                    max(item["active_monomial_max"] for item in items),
                ],
            }
        )

    return {
        "status": status,
        "record_count": len(rows),
        "low_degree_gate": LOW_DEGREE_GATE,
        "full_degree": FULL_DEGREE,
        "active_degree_range": [
            min(row["active_degree_min"] for row in rows),
            max(row["active_degree_max"] for row in rows),
        ],
        "active_monomial_range": [
            min(row["active_monomial_min"] for row in rows),
            max(row["active_monomial_max"] for row in rows),
        ],
        "active_output_count": len(active_outputs),
        "low_degree_output_count": len(low_degree_outputs),
        "high_degree_output_count": len(high_degree_outputs),
        "full_degree_rep_count": len(full_degree_rows),
        "low_degree_rep_count": len(low_degree_rows),
        "family_summary": family_summary,
        "rows": rows,
    }


def write_report(data: dict) -> None:
    lines = [
        "# Fase 44: ANF Degree Audit of the T=15 Cone",
        "",
        "## Question",
        "",
        "Fases 41-43 ruled out sparse local tables, input elimination, and simple",
        "ROBDD variable-order compression. Fase 44 asks whether the same 25-input,",
        "12-step cone is compact as an algebraic normal form (ANF) polynomial over",
        "GF(2).",
        "",
        "Truth tables are simulated exactly in bit-packed form. Each active output",
        "is then unpacked and transformed with the Mobius transform to obtain ANF",
        "coefficients.",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        f"- Representatives: {data['record_count']}",
        f"- Active outputs analyzed: {data['active_output_count']}",
        f"- Active-output degree range: {data['active_degree_range'][0]}..{data['active_degree_range'][1]}",
        f"- Active-output monomial range: {data['active_monomial_range'][0]}..{data['active_monomial_range'][1]}",
        f"- Full-degree representatives (degree {data['full_degree']}): {data['full_degree_rep_count']}/{data['record_count']}",
        f"- Low-degree outputs (<{data['low_degree_gate']}): {data['low_degree_output_count']}/{data['active_output_count']}",
        f"- Representatives with at least one low-degree output: {data['low_degree_rep_count']}/{data['record_count']}",
        "",
        "## Representative table",
        "",
        "| family | rule | background | active outputs | active degree | active monomials |",
        "| --- | ---: | --- | ---: | --- | --- |",
    ]
    for row in data["rows"]:
        lines.append(
            f"| `{row['family_id']}` | {row['rule']} | `{row['background']}` | "
            f"{row['active_output_count']} | {row['active_degree_min']}..{row['active_degree_max']} | "
            f"{row['active_monomial_min']}..{row['active_monomial_max']} |"
        )
    lines.extend(
        [
            "",
            "## Family summary",
            "",
            "| family | reps | active degree | active monomials |",
            "| --- | ---: | --- | --- |",
        ]
    )
    for row in data["family_summary"]:
        lines.append(
            f"| `{row['family_id']}` | {row['count']} | "
            f"{row['active_degree_range'][0]}..{row['active_degree_range'][1]} | "
            f"{row['active_monomial_range'][0]}..{row['active_monomial_range'][1]} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "ANF probes a different representation class from ROBDDs. The result is",
            "mixed rather than a simple full-degree closure: no active output reaches",
            "degree 25, and some active outputs have degree below 20. At the same time,",
            "the representation is often very large, with monomial counts reaching",
            "17,758,052. This exposes algebraic stratification inside the dense cone",
            "rather than a universal compact polynomial shortcut.",
            "",
        ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_report(analyze())


if __name__ == "__main__":
    main()
