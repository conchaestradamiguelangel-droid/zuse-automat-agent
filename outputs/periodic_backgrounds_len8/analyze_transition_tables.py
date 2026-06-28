#!/usr/bin/env python3
"""Fase 35: explicit transition tables for the T=15 five-cycle.

For each of the 20 minimal T=15 representatives, this script reconstructs the
localized XOR-defect orbit and records the induced local transitions used by
the three-step macro-map F^3. It then asks whether those transition-table
signatures coincide with the 13 defect-cycle shape families from Fase 30.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


OUT_DIR = Path(__file__).resolve().parent
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
SHAPE_RESULTS = OUT_DIR / "shape_families_results.json"
RESULTS_JSON = OUT_DIR / "transition_tables_results.json"
REPORT_MD = OUT_DIR / "transition_tables_report.md"

BACKGROUND_PERIOD = 3
LOCKING_RATIO = 5
SAMPLE_START = 81
PADDING = 3


def load_len8_module():
    spec = importlib.util.spec_from_file_location("periodic_background_len8", LEN8_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import detector from {LEN8_SCRIPT}")
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


def rotations(sequence: list[str]) -> list[list[str]]:
    return [sequence[index:] + sequence[:index] for index in range(len(sequence))]


def canonical_sequence(sequence: list[str]) -> list[str]:
    return min(rotations(sequence))


def stable_hash(payload) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def circular_subpattern_multiset(word: str, k: int = 4) -> tuple[tuple[str, int], ...]:
    counts = Counter("".join(word[(i + j) % len(word)] for j in range(k)) for i in range(len(word)))
    return tuple(sorted(counts.items()))


def eca_output(rule: int, left: int, center: int, right: int) -> int:
    return (rule >> ((left << 2) | (center << 1) | right)) & 1


def state_set(frame: tuple[int, ...]) -> set[int]:
    return set(frame)


def bit_at(active: set[int], pos: int, width: int) -> int:
    return 1 if (pos % width) in active else 0


def neighborhood_bits(active: set[int], pos: int, width: int) -> str:
    return "".join(str(bit_at(active, pos + delta, width)) for delta in (-1, 0, 1))


def localized_window(diff: tuple[int, ...], width: int, padding: int = PADDING) -> list[int]:
    """Return a circular localized window around the active defect span."""
    if not diff:
        return []
    positions = sorted(diff)
    gaps = []
    for index, position in enumerate(positions):
        next_position = positions[(index + 1) % len(positions)]
        if index == len(positions) - 1:
            next_position += width
        gaps.append((next_position - position, index))
    _largest_gap, cut_index = max(gaps)
    anchor = positions[(cut_index + 1) % len(positions)]
    offsets = sorted((position - anchor) % width for position in positions)
    active_width = max(offsets) + 1
    return [(anchor + offset) % width for offset in range(-padding, active_width + padding)]


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def perturbation_orbit(base, rule: int, background_frames: list[tuple[int, ...]], word: str) -> list[tuple[int, ...]]:
    diff = base.initial_diff(int(word, 2), len(word), background_frames[0])
    frames = [diff]
    for time_index in range(len(background_frames) - 1):
        diff = base.eca_step_diff(
            diff,
            background_frames[time_index],
            background_frames[time_index + 1],
            rule,
        )
        frames.append(diff)
    return frames


def shape_family_map() -> dict[tuple[int, str], dict]:
    payload = json.loads(SHAPE_RESULTS.read_text(encoding="utf-8"))
    mapping: dict[tuple[int, str], dict] = {}
    for index, cluster in enumerate(payload["global"]["clusters"]):
        family_id = f"F{index:02d}"
        for member in cluster["members"]:
            mapping[(int(member["rule"]), member["background"])] = {
                "family_id": family_id,
                "family_size": cluster["size"],
                "family_cycle": cluster["canonical_cycle"],
                "phase_shift_to_canonical": member["phase_shift_to_canonical"],
            }
    return mapping


def induced_micro_table(
    rule: int,
    width: int,
    bg: tuple[int, ...],
    diff: tuple[int, ...],
    diff_next: tuple[int, ...],
) -> dict:
    bg_active = state_set(bg)
    diff_active = state_set(diff)
    diff_next_active = state_set(diff_next)
    entries: dict[str, set[int]] = defaultdict(set)
    role_counts = Counter()
    for pos in localized_window(diff, width):
        b = neighborhood_bits(bg_active, pos, width)
        d = neighborhood_bits(diff_active, pos, width)
        output = bit_at(diff_next_active, pos, width)
        key = f"b{b}|d{d}"
        entries[key].add(output)
        role_counts["defect" if bit_at(diff_active, pos, width) else "boundary"] += 1

        # Sanity check against the induced rule delta_f(b,d)=f(b xor d) xor f(b).
        b_bits = [int(ch) for ch in b]
        d_bits = [int(ch) for ch in d]
        x_bits = [bb ^ dd for bb, dd in zip(b_bits, d_bits)]
        expected = eca_output(rule, *x_bits) ^ eca_output(rule, *b_bits)
        if expected != output:
            raise RuntimeError(
                f"Induced rule mismatch at pos={pos}, rule={rule}, key={key}: "
                f"expected {expected}, got {output}"
            )
    deterministic = all(len(values) == 1 for values in entries.values())
    table = {key: sorted(values) for key, values in sorted(entries.items())}
    return {
        "entry_count": len(table),
        "deterministic": deterministic,
        "table": table,
        "table_hash": stable_hash(table),
        "role_counts": dict(sorted(role_counts.items())),
    }


def macro_transition_table(
    rule: int,
    width: int,
    bg_frames: list[tuple[int, ...]],
    diff_frames: list[tuple[int, ...]],
    start_time: int,
) -> dict:
    micro = []
    for step in range(BACKGROUND_PERIOD):
        t = start_time + step
        micro.append(
            induced_micro_table(
                rule,
                width,
                bg_frames[t],
                diff_frames[t],
                diff_frames[t + 1],
            )
        )
    aggregate_keys = sorted({key for item in micro for key in item["table"]})
    payload = {
        "micro_hashes": [item["table_hash"] for item in micro],
        "micro_entry_counts": [item["entry_count"] for item in micro],
        "aggregate_keys": aggregate_keys,
        "deterministic": all(item["deterministic"] for item in micro),
    }
    return {
        **payload,
        "macro_hash": stable_hash(payload),
        "micro_tables": micro,
    }


def analyze_representative(base, representative: dict, family_info: dict) -> dict:
    rule = int(representative["rule"])
    background = representative["background"]
    ic = representative["ic"]
    bg_frames = background_orbit(base, rule, background, SAMPLE_START + BACKGROUND_PERIOD * LOCKING_RATIO + 1)
    diff_frames = perturbation_orbit(base, rule, bg_frames, ic)

    transitions = []
    for phase in range(LOCKING_RATIO):
        transitions.append(
            macro_transition_table(
                rule,
                base.WIDTH,
                bg_frames,
                diff_frames,
                SAMPLE_START + BACKGROUND_PERIOD * phase,
            )
        )

    transition_hashes = [item["macro_hash"] for item in transitions]
    canonical_transition_hashes = canonical_sequence(transition_hashes)
    full_signature = {
        "transition_hashes": transition_hashes,
        "canonical_transition_hashes": canonical_transition_hashes,
        "micro_hashes": [[micro["table_hash"] for micro in item["micro_tables"]] for item in transitions],
    }
    return {
        "rule": rule,
        "background": background,
        "ic": ic,
        "family_id": family_info["family_id"],
        "family_size": family_info["family_size"],
        "defect_states": representative["defect_states"],
        "subpatterns_len4": [[pattern, count] for pattern, count in circular_subpattern_multiset(background, 4)],
        "transition_hashes": transition_hashes,
        "canonical_transition_hashes": canonical_transition_hashes,
        "transition_signature_hash": stable_hash(transition_hashes),
        "canonical_transition_signature_hash": stable_hash(canonical_transition_hashes),
        "full_signature_hash": stable_hash(full_signature),
        "transition_entry_counts": [item["micro_entry_counts"] for item in transitions],
        "deterministic": all(item["deterministic"] for item in transitions),
        "transitions": transitions,
    }


def compare_groups(records: list[dict]) -> dict:
    by_family: dict[str, list[dict]] = defaultdict(list)
    by_bucket: dict[str, list[dict]] = defaultdict(list)
    for record in records:
        by_family[record["family_id"]].append(record)
        bucket_key = json.dumps([record["rule"], record["subpatterns_len4"]], sort_keys=True)
        by_bucket[bucket_key].append(record)

    family_rows = []
    for family_id, items in sorted(by_family.items()):
        exact = {tuple(item["transition_hashes"]) for item in items}
        canonical = {tuple(item["canonical_transition_hashes"]) for item in items}
        family_rows.append(
            {
                "family_id": family_id,
                "members": len(items),
                "exact_sequence_count": len(exact),
                "phase_canonical_count": len(canonical),
                "same_exact_table": len(exact) == 1,
                "same_up_to_phase_rotation": len(canonical) == 1,
                "backgrounds": [item["background"] for item in items],
                "rules": sorted({item["rule"] for item in items}),
            }
        )

    bucket_rows = []
    for key, items in sorted(by_bucket.items(), key=lambda pair: (len(pair[1]), pair[0]), reverse=True):
        if len(items) < 2:
            continue
        canonical = {tuple(item["canonical_transition_hashes"]) for item in items}
        bucket_rows.append(
            {
                "bucket": json.loads(key),
                "members": len(items),
                "phase_canonical_count": len(canonical),
                "same_up_to_phase_rotation": len(canonical) == 1,
                "families": sorted({item["family_id"] for item in items}),
                "backgrounds": [item["background"] for item in items],
            }
        )

    canonical_to_families: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for item in records:
        canonical_to_families[tuple(item["canonical_transition_hashes"])].add(item["family_id"])
    cross_family_collisions = [
        {
            "canonical_transition_hashes": list(signature),
            "families": sorted(families),
        }
        for signature, families in canonical_to_families.items()
        if len(families) > 1
    ]

    all_family_safe = all(row["same_up_to_phase_rotation"] for row in family_rows)
    all_bucket_safe = all(row["same_up_to_phase_rotation"] for row in bucket_rows)
    no_cross_family_collision = not cross_family_collisions
    if all_family_safe and no_cross_family_collision:
        verdict = "TABLE_IS_FAMILY"
    elif no_cross_family_collision:
        verdict = "TABLE_REFINES_FAMILY"
    else:
        verdict = "NO_TABLE_FAMILY_IDENTITY"

    return {
        "verdict": verdict,
        "family_rows": family_rows,
        "bucket_rows": bucket_rows,
        "cross_family_collisions": cross_family_collisions,
        "all_family_safe": all_family_safe,
        "all_bucket_safe": all_bucket_safe,
        "no_cross_family_collision": no_cross_family_collision,
    }


def main() -> None:
    base = load_len8_module().load_base_module()
    families = shape_family_map()
    representatives = load_jsonl(LOCKING_RESULTS)

    records = []
    for rep in representatives:
        key = (int(rep["rule"]), rep["background"])
        if key not in families:
            raise RuntimeError(f"No Fase-30 family for {key}")
        records.append(analyze_representative(base, rep, families[key]))

    comparison = compare_groups(records)
    results = {
        "status": comparison["verdict"],
        "record_count": len(records),
        "family_count": len({record["family_id"] for record in records}),
        "representatives": records,
        "comparison": comparison,
    }
    RESULTS_JSON.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(render_report(results), encoding="utf-8")


def render_report(results: dict) -> str:
    comparison = results["comparison"]
    lines = [
        "# Fase 35: Explicit Transition Tables for the T=15 Five-Cycle",
        "",
        "## Question",
        "",
        "For each of the 20 minimal T=15 representatives, build the explicit",
        "local transition-table signature used by the three-step macro-map F^3,",
        "then test whether those signatures coincide with the 13 Fase-30 shape",
        "families.",
        "",
        "## Representative signatures",
        "",
        "| rule | background | family | signature | phase-canonical signature |",
        "| ---: | --- | --- | --- | --- |",
    ]
    for record in sorted(results["representatives"], key=lambda item: (item["family_id"], item["rule"], item["background"])):
        lines.append(
            f"| {record['rule']} | `{record['background']}` | `{record['family_id']}` | "
            f"`{record['transition_signature_hash']}` | "
            f"`{record['canonical_transition_signature_hash']}` |"
        )

    lines += [
        "",
        "## Within-family comparison",
        "",
        "| family | members | exact sequences | phase-canonical sequences | same up to phase rotation |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in comparison["family_rows"]:
        lines.append(
            f"| `{row['family_id']}` | {row['members']} | {row['exact_sequence_count']} | "
            f"{row['phase_canonical_count']} | `{row['same_up_to_phase_rotation']}` |"
        )

    lines += [
        "",
        "## Descriptor-bucket comparison",
        "",
    ]
    if comparison["bucket_rows"]:
        lines.append("| rule/subpatterns_len4 bucket members | families | same up to phase rotation | backgrounds |")
        lines.append("| ---: | --- | --- | --- |")
        for row in comparison["bucket_rows"]:
            lines.append(
                f"| {row['members']} | `{', '.join(row['families'])}` | "
                f"`{row['same_up_to_phase_rotation']}` | "
                f"{', '.join(f'`{bg}`' for bg in row['backgrounds'])} |"
            )
    else:
        lines.append("No rule-conditioned `subpatterns_len4` bucket contains more than one representative.")

    lines += [
        "",
        "## Cross-family comparison",
        "",
    ]
    if comparison["cross_family_collisions"]:
        lines.append("At least one phase-canonical transition-table signature is shared across families:")
        for item in comparison["cross_family_collisions"]:
            lines.append(f"- `{item['canonical_transition_hashes']}` -> {', '.join(item['families'])}")
    else:
        lines.append("No phase-canonical transition-table signature is shared across different families.")

    lines += [
        "",
        "## Verdict",
        "",
        f"**Status:** `{results['status']}`.",
        "",
    ]
    if results["status"] == "TABLE_IS_FAMILY":
        lines.append(
            "The explicit F^3 transition-table signature is identical up to phase "
            "rotation within every shape family and distinct across families. The "
            "transition table is therefore an exact family identifier for the 20 "
            "minimal representatives."
        )
    elif results["status"] == "TABLE_REFINES_FAMILY":
        lines.append(
            "No transition-table signature is shared across families, but at least "
            "one family splits into multiple table signatures. The table refines "
            "the Fase-30 shape-family partition."
        )
    else:
        lines.append(
            "Transition-table signatures do not align cleanly with the Fase-30 "
            "shape families."
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
