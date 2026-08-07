#!/usr/bin/env python3
"""Fase 91: deduplicate the long-period attractors recovered by Fase 90."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Sequence


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parent.parent
RUNNER_PATH = OUT_DIR / "run_phase90_global_period_resweep.py"
BASE_PATH = OUT_DIR / "sweep_periodic_background_oscillators.py"
RESULTS_PATH = OUT_DIR / "phase90_long_period_attractor_results.json"
REPORT_PATH = OUT_DIR / "phase90_long_period_attractor_report.md"

EXPECTED_CASES = 3296
WIDTH = 256
BURN_IN = 80
LONG_STEPS = 1000
TAIL_START = 500
TAIL_END = 1000
MAX_PERIOD = 120


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_rotation(sequence: Sequence[Any]) -> tuple[Any, ...]:
    values = tuple(sequence)
    if not values:
        raise ValueError("Cannot canonicalize an empty cycle")
    return min(values[index:] + values[:index] for index in range(len(values)))


def repeat_cycle(sequence: Sequence[Any], length: int) -> tuple[Any, ...]:
    values = tuple(sequence)
    if not values or length < 1 or length % len(values):
        raise ValueError("Target length must be a positive multiple of cycle length")
    return tuple(values[index % len(values)] for index in range(length))


def reduced_locking_ratio(defect_period: int, background_period: int) -> tuple[int, int]:
    divisor = math.gcd(defect_period, background_period)
    return defect_period // divisor, background_period // divisor


def canonical_defect_cycle(
    defect_cycle: Sequence[Sequence[int]], *, reflected: bool = False
) -> tuple[tuple[int, ...], ...]:
    frames = []
    for frame in defect_cycle:
        offsets = tuple(int(value) for value in frame)
        if reflected:
            maximum = max(offsets)
            offsets = tuple(sorted(maximum - value for value in offsets))
        frames.append(offsets)
    return canonical_rotation(frames)


def morphology_payload(
    *,
    kind: str,
    drift: int,
    defect_period: int,
    background_period: int,
    defect_cycle: Sequence[Sequence[int]],
    reflection_quotient: bool = False,
) -> dict[str, Any]:
    oriented = canonical_defect_cycle(defect_cycle)
    cycle = oriented
    if reflection_quotient:
        reflected = canonical_defect_cycle(defect_cycle, reflected=True)
        cycle = min(oriented, reflected)
    return {
        "kind": kind,
        "drift": int(drift),
        "defect_period": int(defect_period),
        "background_period": int(background_period),
        "locking_ratio": list(reduced_locking_ratio(defect_period, background_period)),
        "defect_cycle": cycle,
    }


def joint_cycle_payload(
    *,
    rule: int,
    kind: str,
    drift: int,
    defect_period: int,
    background_period: int,
    joint_frames: Sequence[tuple[str, Sequence[int]]],
    conjugacy_quotient: bool = False,
) -> dict[str, Any]:
    joint_period = math.lcm(defect_period, background_period)
    if len(joint_frames) != joint_period:
        raise ValueError(
            f"Joint cycle length {len(joint_frames)} != lcm {joint_period}"
        )
    normalized_rule = int(rule)
    frames = tuple((str(bg), tuple(int(v) for v in defect)) for bg, defect in joint_frames)
    if conjugacy_quotient:
        if rule not in {73, 109}:
            raise ValueError("Conjugacy quotient is defined only for rules 73 and 109")
        normalized_rule = 73
        if rule == 109:
            mask = (1 << WIDTH) - 1
            frames = tuple(
                (f"{(int(bg, 16) ^ mask):0{WIDTH // 4}x}", defect)
                for bg, defect in frames
            )
    return {
        "rule": normalized_rule,
        "kind": kind,
        "drift": int(drift),
        "defect_period": int(defect_period),
        "background_period": int(background_period),
        "joint_period": joint_period,
        "locking_ratio": list(reduced_locking_ratio(defect_period, background_period)),
        "joint_cycle": canonical_rotation(frames),
    }


def minimal_exact_period(sequence: Sequence[Any], max_period: int = MAX_PERIOD) -> int | None:
    values = tuple(sequence)
    for period in range(1, min(max_period, len(values) - 1) + 1):
        if all(values[index] == values[index + period] for index in range(len(values) - period)):
            return period
    return None


def state_bits(state: Iterable[int]) -> int:
    value = 0
    for position in state:
        value |= 1 << int(position)
    return value


def relative_background_hex(bits: int, anchor: int) -> str:
    anchor %= WIDTH
    mask = (1 << WIDTH) - 1
    if anchor:
        bits = ((bits >> anchor) | (bits << (WIDTH - anchor))) & mask
    return f"{bits:0{WIDTH // 4}x}"


def stage_b_files(stage_b_root: Path) -> list[Path]:
    return sorted(
        path
        for path in stage_b_root.rglob("*.long_results.jsonl")
        if path.stat().st_size > 0
    )


def load_stage_b_rows(stage_b_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    files = stage_b_files(stage_b_root)
    if not files:
        raise FileNotFoundError(f"No non-empty Stage-B results under {stage_b_root}")
    rows = []
    artifacts = []
    for path in files:
        artifacts.append(
            {
                "path": str(path),
                "size": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
        with path.open("r", encoding="utf-8") as handle:
            rows.extend(json.loads(line) for line in handle if line.strip())
    rows.sort(
        key=lambda row: (
            row["cohort"],
            int(row["rule"]),
            int(row["background_index"]),
            int(row["ic_index"]),
        )
    )
    return rows, artifacts


def input_key(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row["cohort"],
        int(row["rule"]),
        int(row["background_index"]),
        int(row["ic_index"]),
        int(row["word_len"]),
        row["word"],
    )


def build_background(base, rule: int, background: str) -> dict[str, Any]:
    frames = [base.background_state(background)]
    for _ in range(LONG_STEPS):
        frames.append(base.eca_step_state(frames[-1], rule))
    period = minimal_exact_period(frames[TAIL_START : TAIL_END + 1])
    if period is None:
        raise RuntimeError(f"No exact background period <= {MAX_PERIOD}: {rule}/{background}")
    return {
        "frames": frames,
        "bits": [state_bits(frame) for frame in frames],
        "period": period,
    }


def analyze_case(
    row: dict[str, Any], base, runner, background_data: dict[str, Any]
) -> dict[str, Any]:
    simulation = runner.simulate_source(
        base,
        background_data["frames"],
        rule=int(row["rule"]),
        word_len=int(row["word_len"]),
        word_value=int(row["word"], 2),
        burn_in=BURN_IN,
        steps=LONG_STEPS,
        max_span=32,
    )
    if simulation["kind"] != "BOUNDED":
        raise RuntimeError(f"Fase 91 replay is not bounded: {input_key(row)}")
    tail = simulation["shapes"][TAIL_START - BURN_IN : TAIL_END - BURN_IN + 1]
    diagnostic = runner.exact_dynamics(tail, MAX_PERIOD)
    expected = (
        row["stage_b_kind"],
        int(row["stage_b_period"]),
        int(row["stage_b_drift"]),
    )
    observed = (
        diagnostic["kind"],
        int(diagnostic["period"]),
        int(diagnostic["drift"]),
    )
    if observed != expected:
        raise RuntimeError(
            f"Stage-B reconciliation mismatch for {input_key(row)}: {observed} != {expected}"
        )

    defect_period = int(diagnostic["period"])
    background_period = int(background_data["period"])
    joint_period = math.lcm(defect_period, background_period)
    if joint_period > TAIL_END - TAIL_START + 1:
        raise RuntimeError(f"Joint period {joint_period} exceeds the frozen tail")
    start_time = TAIL_END - joint_period + 1
    joint_frames = []
    defect_frames = []
    for timestamp in range(start_time, TAIL_END + 1):
        shape = simulation["shapes"][timestamp - BURN_IN]
        defect = tuple(int(value) for value in shape.offsets)
        background_hex = relative_background_hex(
            background_data["bits"][timestamp], int(shape.min_pos)
        )
        joint_frames.append((background_hex, defect))
        defect_frames.append(defect)

    # The defect period always divides the joint period; keep one minimal defect cycle.
    defect_cycle = defect_frames[-defect_period:]
    physical = joint_cycle_payload(
        rule=int(row["rule"]),
        kind=diagnostic["kind"],
        drift=int(diagnostic["drift"]),
        defect_period=defect_period,
        background_period=background_period,
        joint_frames=joint_frames,
    )
    conjugacy = joint_cycle_payload(
        rule=int(row["rule"]),
        kind=diagnostic["kind"],
        drift=int(diagnostic["drift"]),
        defect_period=defect_period,
        background_period=background_period,
        joint_frames=joint_frames,
        conjugacy_quotient=True,
    )
    morphology = morphology_payload(
        kind=diagnostic["kind"],
        drift=int(diagnostic["drift"]),
        defect_period=defect_period,
        background_period=background_period,
        defect_cycle=defect_cycle,
    )
    reflection = morphology_payload(
        kind=diagnostic["kind"],
        drift=int(diagnostic["drift"]),
        defect_period=defect_period,
        background_period=background_period,
        defect_cycle=defect_cycle,
        reflection_quotient=True,
    )
    return {
        "cohort": row["cohort"],
        "rule": int(row["rule"]),
        "background": row["background"],
        "background_index": int(row["background_index"]),
        "ic_index": int(row["ic_index"]),
        "word_len": int(row["word_len"]),
        "word": row["word"],
        "kind": diagnostic["kind"],
        "defect_period": defect_period,
        "background_period": background_period,
        "joint_period": joint_period,
        "locking_ratio": list(reduced_locking_ratio(defect_period, background_period)),
        "physical_class_sha256": sha256_json(physical),
        "conjugacy_class_sha256": sha256_json(conjugacy),
        "morphology_class_sha256": sha256_json(morphology),
        "reflection_class_sha256": sha256_json(reflection),
    }


def compact_classes(rows: list[dict[str, Any]], field: str) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row[field]].append(row)
    result = []
    for digest, members in grouped.items():
        rules = sorted({int(row["rule"]) for row in members})
        result.append(
            {
                "sha256": digest,
                "alias_count": len(members),
                "rules": rules,
                "defect_periods": sorted({int(row["defect_period"]) for row in members}),
                "background_periods": sorted(
                    {int(row["background_period"]) for row in members}
                ),
                "locking_ratios": sorted(
                    {tuple(row["locking_ratio"]) for row in members}
                ),
                "background_count": len({row["background"] for row in members}),
                "examples": [
                    {
                        "cohort": row["cohort"],
                        "rule": row["rule"],
                        "background": row["background"],
                        "word": row["word"],
                    }
                    for row in members[:3]
                ],
            }
        )
    return sorted(result, key=lambda item: (-item["alias_count"], item["sha256"]))


def distribution(values: Iterable[Any]) -> dict[str, int]:
    return {str(key): value for key, value in sorted(Counter(values).items(), key=lambda x: str(x[0]))}


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 91 - Long-period attractor atlas",
        "",
        "## Question",
        "",
        "Do the 3,296 period-cap misses confirmed by Fase 90 represent distinct physical attractors, or input-condition aliases feeding a smaller set of recurrent cycles?",
        "",
        "## Frozen protocol",
        "",
        "- Input: exactly the 3,296 Stage-B rows confirmed by Fase 90.",
        "- Replay: WIDTH=256, burn-in=80, t=0..1000, exact tail t=500..1000, maximum period 120.",
        "- Abort gate: any kind/period/drift mismatch against Stage B aborts the analysis.",
        "- Strict physical identity is computed from the resulting attractor, never from the input key.",
        "- Joint background/defect cycles are canonicalized over lcm(T_defect,T_background), with one shared temporal rotation.",
        "- Morphology retains the reduced locking ratio; different locking ratios cannot collapse into one morphology class.",
        "- Reflection and rule_73/rule_109 black-white conjugacy are separate quotients, not strict identity.",
        "",
        "## Reconciliation",
        "",
        f"- Source rows: {summary['source_case_count']}",
        f"- Unique physical input keys: {summary['unique_input_count']}",
        f"- Stage-B mismatches: {summary['stage_b_mismatch_count']}",
        f"- Maximum joint period: {summary['maximum_joint_period']}",
        "",
        "## Atlas",
        "",
        f"- Strict physical attractor classes: {summary['physical_class_count']}",
        f"- Input aliases collapsed by strict physical identity: {summary['physical_alias_collapse_count']}",
        f"- Defect morphology classes: {summary['morphology_class_count']}",
        f"- Reflection-quotient morphology classes: {summary['reflection_class_count']}",
        f"- rule_73/rule_109 conjugacy classes: {summary['conjugacy_class_count']}",
        f"- Strict classes with more than one input alias: {summary['multi_alias_physical_class_count']}",
        f"- Largest strict physical basin in this IC census: {summary['largest_physical_alias_count']}",
        f"- Morphology classes spanning both rules: {summary['cross_rule_morphology_class_count']}",
        f"- Conjugacy classes spanning both rules: {summary['cross_rule_conjugacy_class_count']}",
        "",
        "## Period structure",
        "",
        f"- Defect periods: `{json.dumps(summary['defect_period_distribution'], sort_keys=True)}`",
        f"- Background periods: `{json.dumps(summary['background_period_distribution'], sort_keys=True)}`",
        f"- Reduced locking ratios: `{json.dumps(summary['locking_ratio_distribution'], sort_keys=True)}`",
        "",
        "## Largest strict physical classes",
        "",
        "| aliases | rules | T defect | T background | ratio | examples |",
        "|---:|---|---|---|---|---|",
    ]
    for item in payload["physical_classes"][:15]:
        examples = "; ".join(
            f"r{row['rule']}/{row['background']}/{row['word']}" for row in item["examples"]
        )
        lines.append(
            f"| {item['alias_count']} | {item['rules']} | {item['defect_periods']} | "
            f"{item['background_periods']} | {item['locking_ratios']} | {examples} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            "`LONG_PERIOD_ATTRACTOR_ATLAS_BUILT`",
            "",
            "The verdict is descriptive. Collapse counts quantify exact equivalence under the predeclared signatures; they do not by themselves establish a universal law outside the two frozen Fase-90 cohorts.",
            "",
            "## Methodological limits",
            "",
            "- The atlas covers only the 3,296 confirmed period-cap misses from the frozen baseline and primitive-length-8 cohorts.",
            "- Strict identity is translation-invariant but preserves the complete background state relative to the defect and their joint temporal phase.",
            "- Morphology identity is weaker than physical identity and must not be interpreted as proof of the same basin or background-conditioned mechanism.",
            "- No ANF-gradient measurement is performed in this phase.",
            "- No paper, DOI, tag, release, or v1.34 artifact is modified.",
            "",
        ]
    )
    return "\n".join(lines)


def run(stage_b_root: Path) -> dict[str, Any]:
    runner = load_module("fase91_phase90_runner", RUNNER_PATH)
    base = load_module("fase91_base", BASE_PATH)
    source_rows, artifacts = load_stage_b_rows(stage_b_root)
    keys = [input_key(row) for row in source_rows]
    if len(source_rows) != EXPECTED_CASES or len(set(keys)) != EXPECTED_CASES:
        raise RuntimeError(
            f"Expected {EXPECTED_CASES} unique Stage-B rows, got {len(source_rows)} rows and {len(set(keys))} keys"
        )
    if any(
        row.get("confirmation_status") != "CONFIRMED_PERIOD_CAP_FALSE_NEGATIVE"
        for row in source_rows
    ):
        raise RuntimeError("Stage-B source contains a non-confirmed row")

    background_cache = {}
    rows = []
    for source in source_rows:
        cache_key = (int(source["rule"]), source["background"])
        if cache_key not in background_cache:
            background_cache[cache_key] = build_background(base, *cache_key)
        rows.append(analyze_case(source, base, runner, background_cache[cache_key]))

    physical_classes = compact_classes(rows, "physical_class_sha256")
    morphology_classes = compact_classes(rows, "morphology_class_sha256")
    reflection_classes = compact_classes(rows, "reflection_class_sha256")
    conjugacy_classes = compact_classes(rows, "conjugacy_class_sha256")
    summary = {
        "source_case_count": len(source_rows),
        "unique_input_count": len(set(keys)),
        "stage_b_mismatch_count": 0,
        "background_orbit_count": len(background_cache),
        "maximum_joint_period": max(row["joint_period"] for row in rows),
        "physical_class_count": len(physical_classes),
        "physical_alias_collapse_count": len(rows) - len(physical_classes),
        "multi_alias_physical_class_count": sum(
            item["alias_count"] > 1 for item in physical_classes
        ),
        "largest_physical_alias_count": max(item["alias_count"] for item in physical_classes),
        "morphology_class_count": len(morphology_classes),
        "reflection_class_count": len(reflection_classes),
        "conjugacy_class_count": len(conjugacy_classes),
        "cross_rule_morphology_class_count": sum(
            len(item["rules"]) > 1 for item in morphology_classes
        ),
        "cross_rule_conjugacy_class_count": sum(
            len(item["rules"]) > 1 for item in conjugacy_classes
        ),
        "defect_period_distribution": distribution(row["defect_period"] for row in rows),
        "background_period_distribution": distribution(
            row["background_period"] for row in rows
        ),
        "locking_ratio_distribution": distribution(
            ":".join(map(str, row["locking_ratio"])) for row in rows
        ),
        "rule_distribution": distribution(row["rule"] for row in rows),
    }
    payload = {
        "phase": 91,
        "status": "LONG_PERIOD_ATTRACTOR_ATLAS_BUILT",
        "source_stage_b_root": str(stage_b_root),
        "source_artifacts": artifacts,
        "protocol": {
            "width": WIDTH,
            "burn_in": BURN_IN,
            "steps": LONG_STEPS,
            "tail_range": [TAIL_START, TAIL_END],
            "maximum_period": MAX_PERIOD,
            "strict_identity_uses_input_key": False,
            "joint_canonicalization": "lcm(T_defect,T_background), shared temporal rotation",
            "morphology_preserves_locking_ratio": True,
        },
        "summary": summary,
        "physical_classes": physical_classes,
        "morphology_classes": morphology_classes,
        "reflection_classes": reflection_classes,
        "conjugacy_classes": conjugacy_classes,
        "cases": rows,
    }
    RESULTS_PATH.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    REPORT_PATH.write_text(render_report(payload), encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stage-b-root",
        type=Path,
        default=Path(
            os.environ.get(
                "ZUSE_PHASE90_STAGE_B",
                str(OUT_DIR / "fase90" / "stage_b"),
            )
        ),
    )
    args = parser.parse_args()
    payload = run(args.stage_b_root.resolve())
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
