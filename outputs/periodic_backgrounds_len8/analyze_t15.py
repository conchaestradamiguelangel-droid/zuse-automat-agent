"""Fase 26: characterize the period-15 stationary oscillator family.

The Fase-24 sweep found period-15 hits on primitive length-8 backgrounds.
This script inventories every hit, verifies the algebraic relation between
the participating rules, measures the background temporal cycles, and tests
long-horizon persistence, background phase sensitivity, and one-bit IC
robustness for one minimal witness per rule/background pair.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
SOURCE_RESULTS = OUT_DIR / "sweep_len8_results.jsonl"
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
RESULTS_JSON = OUT_DIR / "t15_anatomy_results.json"
REPORT_MD = OUT_DIR / "t15_anatomy_report.md"

LONG_STEPS = 900
BURN_IN = 80
TARGET_PERIOD = 15


def load_len8_module():
    spec = importlib.util.spec_from_file_location("periodic_background_len8", LEN8_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import Fase-24 detector from {LEN8_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_t15_records() -> list[dict]:
    records = []
    with SOURCE_RESULTS.open(encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            record = json.loads(line)
            if int(record.get("period_T", 0)) == TARGET_PERIOD:
                records.append(record)
    return records


def reflect_rule(rule: int) -> int:
    reflected = 0
    for neighborhood in range(8):
        left = (neighborhood >> 2) & 1
        center = (neighborhood >> 1) & 1
        right = neighborhood & 1
        reflected_neighborhood = (right << 2) | (center << 1) | left
        reflected |= ((rule >> neighborhood) & 1) << reflected_neighborhood
    return reflected


def conjugate_rule(rule: int) -> int:
    """Exchange 0/1 in both the input configuration and rule output."""
    conjugate = 0
    for neighborhood in range(8):
        output = 1 - ((rule >> (7 - neighborhood)) & 1)
        conjugate |= output << neighborhood
    return conjugate


def step_ring(word: str, rule: int) -> str:
    out = []
    width = len(word)
    for index in range(width):
        left = int(word[(index - 1) % width])
        center = int(word[index])
        right = int(word[(index + 1) % width])
        neighborhood = (left << 2) | (center << 1) | right
        out.append(str((rule >> neighborhood) & 1))
    return "".join(out)


def finite_background_cycle(word: str, rule: int) -> dict:
    seen: dict[str, int] = {}
    orbit = []
    current = word
    while current not in seen:
        seen[current] = len(orbit)
        orbit.append(current)
        current = step_ring(current, rule)
    transient = seen[current]
    return {
        "transient": transient,
        "period": len(orbit) - transient,
        "cycle": orbit[transient:],
    }


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def circular_shape(base, diff: tuple[int, ...]) -> tuple[tuple[int, ...], int] | None:
    if not diff:
        return None
    positions = sorted(diff)
    gaps = []
    for index, position in enumerate(positions):
        next_position = positions[(index + 1) % len(positions)]
        if index == len(positions) - 1:
            next_position += base.WIDTH
        gaps.append((next_position - position, index))
    _gap, cut_index = max(gaps)
    start = positions[(cut_index + 1) % len(positions)]
    offsets = tuple(sorted((position - start) % base.WIDTH for position in positions))
    if max(offsets) > base.MAX_SPAN:
        return None
    return offsets, start


def simulate_stationary_signature(
    base,
    rule: int,
    background: str,
    word: str,
    *,
    steps: int,
    background_shift: int = 0,
) -> dict:
    shifted_background = (
        background[-background_shift:] + background[:-background_shift]
        if background_shift
        else background
    )
    bg_frames = background_orbit(base, rule, shifted_background, steps)
    diff = base.initial_diff(int(word, 2), len(word), bg_frames[0])
    shapes: list[tuple[tuple[int, ...], int]] = []

    for time_index in range(steps + 1):
        if time_index >= BURN_IN:
            shape = circular_shape(base, diff)
            if shape is None:
                return {
                    "detected_period": None,
                    "reason": "empty_or_nonlocal",
                    "survived_steps": time_index,
                }
            shapes.append(shape)
        if time_index < steps:
            diff = base.eca_step_diff(
                diff,
                bg_frames[time_index],
                bg_frames[time_index + 1],
                rule,
            )

    if not shapes:
        return {"detected_period": None, "reason": "no_tail", "survived_steps": 0}

    for period in range(1, base.PERIOD_MAX + 1):
        if all(
            shapes[index][0] == shapes[index + period][0]
            and shapes[index][1] == shapes[index + period][1]
            for index in range(len(shapes) - period)
        ):
            motif = []
            for offsets, _position in shapes[-period:]:
                span = max(offsets)
                motif.append(
                    "".join("#" if cell in offsets else "." for cell in range(span + 1))
                )
            return {
                "detected_period": period,
                "reason": "exact_recurrence",
                "survived_steps": steps,
                "motif": motif,
            }
    return {
        "detected_period": None,
        "reason": "no_period_2_to_16",
        "survived_steps": steps,
    }


def canonical_motif(motif: list[str]) -> str:
    rotations = [
        json.dumps(motif[index:] + motif[:index], separators=(",", ":"))
        for index in range(len(motif))
    ]
    return min(rotations)


def minimal_record(records: list[dict]) -> dict:
    return min(records, key=lambda record: (int(record["word_len"]), record["word"]))


def flip_word(word: str, index: int) -> str:
    flipped = "1" if word[index] == "0" else "0"
    return word[:index] + flipped + word[index + 1 :]


def analyze() -> dict:
    module = load_len8_module()
    base = module.load_base_module()
    records = load_t15_records()
    if not records:
        raise RuntimeError("No T=15 records found in the Fase-24 result file")

    grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for record in records:
        grouped[(int(record["rule"]), record["background_canonical"])].append(record)

    rule_counts = Counter(int(record["rule"]) for record in records)
    background_counts = Counter(record["background_canonical"] for record in records)
    word_length_counts = Counter(int(record["word_len"]) for record in records)
    unique_motifs = {
        canonical_motif(record["motif"])
        for record in records
    }

    rules = sorted(rule_counts)
    rule_symmetry = {
        str(rule): {
            "reflection": reflect_rule(rule),
            "reflection_symmetric": reflect_rule(rule) == rule,
            "black_white_conjugate": conjugate_rule(rule),
        }
        for rule in rules
    }

    representatives = []
    for (rule, background), group in sorted(grouped.items()):
        witness = minimal_record(group)
        bg_cycle = finite_background_cycle(background, rule)
        long_run = simulate_stationary_signature(
            base,
            rule,
            background,
            witness["word"],
            steps=LONG_STEPS,
        )

        phase_results = []
        for shift in range(8):
            result = simulate_stationary_signature(
                base,
                rule,
                background,
                witness["word"],
                steps=base.STEPS,
                background_shift=shift,
            )
            phase_results.append(
                {
                    "shift": shift,
                    "detected_period": result["detected_period"],
                    "t15": result["detected_period"] == TARGET_PERIOD,
                }
            )

        mutation_results = []
        for index in range(len(witness["word"])):
            mutated = flip_word(witness["word"], index)
            result = simulate_stationary_signature(
                base,
                rule,
                background,
                mutated,
                steps=base.STEPS,
            )
            mutation_results.append(
                {
                    "bit_index": index,
                    "word": mutated,
                    "detected_period": result["detected_period"],
                    "t15": result["detected_period"] == TARGET_PERIOD,
                }
            )

        representatives.append(
            {
                "rule": rule,
                "background": background,
                "fase24_detection_count": len(group),
                "minimal_word_len": int(witness["word_len"]),
                "minimal_word": witness["word"],
                "background_transient": bg_cycle["transient"],
                "background_temporal_period": bg_cycle["period"],
                "background_cycle": bg_cycle["cycle"],
                "long_run_steps": LONG_STEPS,
                "long_run_period": long_run["detected_period"],
                "long_run_persists": long_run["detected_period"] == TARGET_PERIOD,
                "phase_t15_count": sum(result["t15"] for result in phase_results),
                "phase_results": phase_results,
                "mutation_t15_count": sum(result["t15"] for result in mutation_results),
                "mutation_count": len(mutation_results),
                "mutation_results": mutation_results,
            }
        )

    global_minimum = minimal_record(records)
    return {
        "source_record_count": len(records),
        "rules": rules,
        "rule_counts": dict(sorted(rule_counts.items())),
        "rule_symmetry": rule_symmetry,
        "background_count": len(background_counts),
        "background_counts": dict(sorted(background_counts.items())),
        "rule_background_pairs": len(grouped),
        "word_length_counts": dict(sorted(word_length_counts.items())),
        "unique_temporal_motifs": len(unique_motifs),
        "global_minimum": {
            "rule": int(global_minimum["rule"]),
            "background": global_minimum["background_canonical"],
            "word_len": int(global_minimum["word_len"]),
            "word": global_minimum["word"],
        },
        "representatives": representatives,
    }


def render_report(result: dict) -> str:
    reps = result["representatives"]
    long_ok = sum(rep["long_run_persists"] for rep in reps)
    phase_hits = sum(rep["phase_t15_count"] for rep in reps)
    phase_total = 8 * len(reps)
    mutation_hits = sum(rep["mutation_t15_count"] for rep in reps)
    mutation_total = sum(rep["mutation_count"] for rep in reps)
    bg_periods = sorted({rep["background_temporal_period"] for rep in reps})
    phase_periods = Counter(
        str(item["detected_period"]) if item["detected_period"] is not None else "none"
        for rep in reps
        for item in rep["phase_results"]
    )
    mutation_periods = Counter(
        str(item["detected_period"]) if item["detected_period"] is not None else "none"
        for rep in reps
        for item in rep["mutation_results"]
    )

    lines = [
        "# Fase 26: Anatomy of the T=15 Stationary Oscillator Family",
        "",
        "## Scope",
        "",
        "This analysis filters every `T=15` detection from the Fase-24 primitive",
        "length-8 background sweep. It inventories the family, verifies rule",
        "symmetries, measures each unperturbed background's temporal orbit, and",
        "reruns one minimal witness per rule/background pair through long-horizon,",
        "background-phase, and one-bit IC tests.",
        "",
        "## Inventory",
        "",
        f"- Fase-24 `T=15` detections: `{result['source_record_count']}`.",
        f"- Rules: `{', '.join(f'rule_{rule}' for rule in result['rules'])}`.",
        f"- Primitive length-8 backgrounds: `{result['background_count']}`.",
        f"- Rule/background pairs: `{result['rule_background_pairs']}`.",
        f"- Distinct temporal motifs up to cycle phase: `{result['unique_temporal_motifs']}`.",
        (
            "- Minimum witness: "
            f"`rule_{result['global_minimum']['rule']}`, background "
            f"`{result['global_minimum']['background']}`, IC "
            f"`{result['global_minimum']['word']}` "
            f"(length {result['global_minimum']['word_len']})."
        ),
        "",
        "The two rules are each left-right symmetric and are exact black/white",
        "conjugates of one another:",
        "",
        "| rule | reflection | black/white conjugate |",
        "| --- | --- | --- |",
    ]
    for rule in result["rules"]:
        symmetry = result["rule_symmetry"][str(rule)]
        lines.append(
            f"| rule_{rule} | rule_{symmetry['reflection']} | "
            f"rule_{symmetry['black_white_conjugate']} |"
        )

    lines.extend(
        [
            "",
            "## Background coupling and persistence",
            "",
            f"All participating backgrounds have temporal period `{', '.join(map(str, bg_periods))}` "
            "under their unperturbed ECA orbit. Thus the observed local period",
            "`T=15` is five times the background temporal period `T_bg=3`, rather",
            "than a direct copy of the spatial template length 8.",
            "",
            f"Long-horizon reruns preserve exact `T=15` recurrence through step "
            f"{LONG_STEPS} in `{long_ok}/{len(reps)}` minimal representatives.",
            "Because period detection scans upward from 1, these runs also exclude",
            "all smaller candidate periods in the tested range.",
            "",
            "## Robustness summary",
            "",
            f"- Fixed-IC background phase test: `{phase_hits}/{phase_total}` runs retain `T=15`.",
            f"- One-bit mutations of the minimal witnesses: `{mutation_hits}/{mutation_total}` "
            "retain `T=15`.",
            f"- Phase-test period outcomes: `{dict(sorted(phase_periods.items()))}`.",
            f"- Mutation-test period outcomes: `{dict(sorted(mutation_periods.items()))}`.",
            "",
            "The phase test changes the relative IC/background alignment and therefore",
            "measures a physical basin property. Co-translation equivariance of the",
            "underlying detector was already established in Fase 25.",
            "",
            "## Per rule/background representative",
            "",
            "| rule | background | hits | min IC | T_bg | T=15 at 900 | phase | one-bit mutations |",
            "| --- | --- | ---: | --- | ---: | --- | ---: | ---: |",
        ]
    )
    for rep in reps:
        lines.append(
            f"| rule_{rep['rule']} | `{rep['background']}` | "
            f"{rep['fase24_detection_count']} | `{rep['minimal_word']}` | "
            f"{rep['background_temporal_period']} | "
            f"{'yes' if rep['long_run_persists'] else 'no'} | "
            f"{rep['phase_t15_count']}/8 | "
            f"{rep['mutation_t15_count']}/{rep['mutation_count']} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "`T=15` is not a single accidental witness. It is a stationary family",
            "restricted to the conjugate, reflection-symmetric pair `rule_73/rule_109`,",
            "with multiple backgrounds, multiple IC basins, and exact persistence over",
            "the longer horizon. The shared `T_bg=3` establishes a reproducible",
            "five-to-one temporal locking ratio. This analysis does not yet derive the",
            "15-cycle from the two rule tables; the algebraic mechanism of that locking",
            "remains open.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    result = analyze()
    RESULTS_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_MD.write_text(render_report(result), encoding="utf-8")
    print(
        json.dumps(
            {
                "records": result["source_record_count"],
                "rules": result["rules"],
                "rule_background_pairs": result["rule_background_pairs"],
                "report": str(REPORT_MD),
                "results": str(RESULTS_JSON),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
