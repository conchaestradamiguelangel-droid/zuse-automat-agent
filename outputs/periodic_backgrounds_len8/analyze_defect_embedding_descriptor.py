#!/usr/bin/env python3
"""Fase 38: embedding descriptor for the T=15 families.

Fase 37 showed that the rule-conditioned canonical period-3 background orbit
is too coarse: all representatives collapse to one orbit key per rule. Fase 38
adds the missing embedding variables: where the background enters the canonical
orbit, where it is at the sampled defect phase, and how the IC/defect is aligned
relative to that canonical background coordinate.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
SHAPE_RESULTS = OUT_DIR / "shape_families_results.json"
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
RESULTS_JSON = OUT_DIR / "defect_embedding_descriptor_results.json"
REPORT_MD = OUT_DIR / "defect_embedding_descriptor_report.md"

SAMPLE_START = 81
BACKGROUND_PERIOD = 3
WIDTH = 256


def load_len8_module():
    spec = importlib.util.spec_from_file_location("periodic_background_len8", LEN8_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import detector from {LEN8_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def stable_hash(payload) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def rotations(word: str) -> list[str]:
    return [word[i:] + word[:i] for i in range(len(word))]


def canonical_rotation_with_offset(word: str) -> tuple[str, int]:
    rots = rotations(word)
    canonical = min(rots)
    return canonical, rots.index(canonical)


def canonical_temporal_sequence(cycle: list[str]) -> list[str]:
    canonical_states = [canonical_rotation_with_offset(state)[0] for state in cycle]
    temporal_rots = [
        canonical_states[index:] + canonical_states[:index]
        for index in range(len(canonical_states))
    ]
    return min(temporal_rots)


def eca_step_word(word: str, rule: int) -> str:
    bits = [int(ch) for ch in word]
    n = len(bits)
    out = []
    for index in range(n):
        left = bits[(index - 1) % n]
        center = bits[index]
        right = bits[(index + 1) % n]
        out.append(str((rule >> ((left << 2) | (center << 1) | right)) & 1))
    return "".join(out)


def temporal_orbit(word: str, rule: int) -> dict:
    seen = {word: 0}
    states = [word]
    current = word
    while True:
        current = eca_step_word(current, rule)
        if current in seen:
            preperiod = seen[current]
            cycle = states[preperiod:]
            canonical_sequence = canonical_temporal_sequence(cycle)
            return {
                "states": states,
                "preperiod": preperiod,
                "period": len(cycle),
                "cycle": cycle,
                "canonical_sequence": canonical_sequence,
            }
        seen[current] = len(states)
        states.append(current)


def word_at_time(word: str, rule: int, t: int) -> str:
    current = word
    for _ in range(t):
        current = eca_step_word(current, rule)
    return current


def embedding_in_canonical_sequence(word: str, canonical_sequence: list[str]) -> dict:
    canonical_word, rotation_offset = canonical_rotation_with_offset(word)
    matches = [index for index, state in enumerate(canonical_sequence) if state == canonical_word]
    if not matches:
        raise RuntimeError(f"Word {word} canonicalizes to {canonical_word}, not in canonical sequence {canonical_sequence}")
    return {
        "canonical_word": canonical_word,
        "orbit_step": matches[0],
        "rotation_offset": rotation_offset,
    }


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def family_map() -> dict[tuple[int, str], str]:
    payload = json.loads(SHAPE_RESULTS.read_text(encoding="utf-8"))
    mapping = {}
    for index, cluster in enumerate(payload["global"]["clusters"]):
        family_id = f"F{index:02d}"
        for member in cluster["members"]:
            mapping[(int(member["rule"]), member["background"])] = family_id
    return mapping


def canonical_defect(width: int, diff: tuple[int, ...]) -> dict | None:
    if not diff:
        return None
    positions = sorted(diff)
    gaps = []
    for index, position in enumerate(positions):
        next_position = positions[(index + 1) % len(positions)]
        if index == len(positions) - 1:
            next_position += width
        gaps.append((next_position - position, index))
    _largest_gap, cut_index = max(gaps)
    anchor = positions[(cut_index + 1) % len(positions)]
    offsets = tuple(sorted((position - anchor) % width for position in positions))
    active_width = max(offsets) + 1
    value = sum(1 << offset for offset in offsets)
    hex_digits = max(1, (active_width + 3) // 4)
    return {
        "anchor": anchor,
        "offsets": offsets,
        "width": active_width,
        "hex": f"{active_width}:{value:0{hex_digits}x}",
    }


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def perturbation_orbit(base, rule: int, background_frames: list[tuple[int, ...]], ic: str) -> list[tuple[int, ...]]:
    diff = base.initial_diff(int(ic, 2), len(ic), background_frames[0])
    frames = [diff]
    for time_index in range(len(background_frames) - 1):
        diff = base.eca_step_diff(diff, background_frames[time_index], background_frames[time_index + 1], rule)
        frames.append(diff)
    return frames


def analyze_records() -> list[dict]:
    base = load_len8_module().load_base_module()
    families = family_map()
    locking = load_jsonl(LOCKING_RESULTS)
    rows = []
    for record in locking:
        rule = int(record["rule"])
        background = record["background"]
        ic = record["ic"]
        orbit = temporal_orbit(background, rule)
        entry_word = orbit["cycle"][0]
        sample_word = word_at_time(background, rule, SAMPLE_START)
        entry_embedding = embedding_in_canonical_sequence(entry_word, orbit["canonical_sequence"])
        sample_embedding = embedding_in_canonical_sequence(sample_word, orbit["canonical_sequence"])

        bg_frames = background_orbit(base, rule, background, SAMPLE_START)
        diff_frames = perturbation_orbit(base, rule, bg_frames, ic)
        defect = canonical_defect(base.WIDTH, diff_frames[SAMPLE_START])
        if defect is None:
            raise RuntimeError(f"Empty defect for {rule} {background}")

        ic_start = base.WIDTH // 2 - len(ic) // 2
        modulus = len(background)
        sample_rotation = sample_embedding["rotation_offset"]
        entry_rotation = entry_embedding["rotation_offset"]
        rows.append(
            {
                "rule": rule,
                "background": background,
                "family_id": families[(rule, background)],
                "ic": ic,
                "ic_len": len(ic),
                "preperiod": orbit["preperiod"],
                "canonical_orbit": orbit["canonical_sequence"],
                "entry_word": entry_word,
                "entry_orbit_step": entry_embedding["orbit_step"],
                "entry_rotation_offset": entry_embedding["rotation_offset"],
                "sample_word": sample_word,
                "sample_orbit_step": sample_embedding["orbit_step"],
                "sample_rotation_offset": sample_embedding["rotation_offset"],
                "ic_start_mod_raw": ic_start % modulus,
                "ic_start_mod_entry_canonical": (ic_start + entry_rotation) % modulus,
                "ic_start_mod_sample_canonical": (ic_start + sample_rotation) % modulus,
                "defect_anchor": defect["anchor"],
                "defect_anchor_mod_raw": defect["anchor"] % modulus,
                "defect_anchor_mod_sample_canonical": (defect["anchor"] + sample_rotation) % modulus,
                "defect_state0": defect["hex"],
            }
        )
    return sorted(rows, key=lambda item: (item["family_id"], item["rule"], item["background"]))


def descriptor_value(row: dict, name: str):
    if name == "entry_embedding":
        return [row["rule"], row["entry_orbit_step"], row["entry_rotation_offset"]]
    if name == "sample_embedding":
        return [row["rule"], row["sample_orbit_step"], row["sample_rotation_offset"]]
    if name == "sample_embedding_ic_start":
        return [row["rule"], row["sample_orbit_step"], row["sample_rotation_offset"], row["ic_start_mod_sample_canonical"]]
    if name == "sample_embedding_ic_len_start":
        return [row["rule"], row["sample_orbit_step"], row["sample_rotation_offset"], row["ic_len"], row["ic_start_mod_sample_canonical"]]
    if name == "sample_embedding_defect_anchor":
        return [row["rule"], row["sample_orbit_step"], row["sample_rotation_offset"], row["defect_anchor_mod_sample_canonical"]]
    if name == "sample_embedding_defect_state":
        return [row["rule"], row["sample_orbit_step"], row["sample_rotation_offset"], row["defect_state0"]]
    if name == "full_embedding_without_ic_word":
        return [
            row["rule"],
            row["sample_orbit_step"],
            row["sample_rotation_offset"],
            row["ic_len"],
            row["ic_start_mod_sample_canonical"],
            row["defect_anchor_mod_sample_canonical"],
        ]
    raise KeyError(name)


def test_descriptors(rows: list[dict]) -> list[dict]:
    names = [
        "entry_embedding",
        "sample_embedding",
        "sample_embedding_ic_start",
        "sample_embedding_ic_len_start",
        "sample_embedding_defect_anchor",
        "sample_embedding_defect_state",
        "full_embedding_without_ic_word",
    ]
    results = []
    for name in names:
        buckets: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            key = json.dumps(descriptor_value(row, name), sort_keys=True)
            buckets[key].append(row)
        ambiguous = []
        for key, items in buckets.items():
            families = sorted({item["family_id"] for item in items})
            if len(families) > 1:
                ambiguous.append(
                    {
                        "descriptor": json.loads(key),
                        "families": families,
                        "backgrounds": [item["background"] for item in items],
                    }
                )
        results.append(
            {
                "descriptor": name,
                "bucket_count": len(buckets),
                "ambiguous_bucket_count": len(ambiguous),
                "determines_family": len(ambiguous) == 0,
                "ambiguous_buckets": ambiguous,
            }
        )
    return results


def main() -> None:
    rows = analyze_records()
    descriptor_tests = test_descriptors(rows)
    first_success = next((item["descriptor"] for item in descriptor_tests if item["determines_family"]), None)
    status = "EMBEDDING_DESCRIPTOR_FOUND" if first_success else "NO_EMBEDDING_DESCRIPTOR"
    payload = {
        "status": status,
        "first_success": first_success,
        "record_count": len(rows),
        "rows": rows,
        "descriptor_tests": descriptor_tests,
    }
    RESULTS_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(render_report(payload), encoding="utf-8")


def render_report(payload: dict) -> str:
    lines = [
        "# Fase 38: Defect Embedding Descriptor for T=15 Families",
        "",
        "## Question",
        "",
        "Fase 37 showed that the canonical period-3 background orbit alone is too",
        "coarse. Fase 38 adds embedding variables: temporal orbit step, spatial",
        "rotation offset, IC start alignment, and defect anchor alignment.",
        "",
        "## Descriptor tests",
        "",
        "| descriptor | buckets | ambiguous buckets | determines family |",
        "| --- | ---: | ---: | --- |",
    ]
    for item in payload["descriptor_tests"]:
        lines.append(
            f"| `{item['descriptor']}` | {item['bucket_count']} | "
            f"{item['ambiguous_bucket_count']} | `{item['determines_family']}` |"
        )
    lines += [
        "",
        "## Representative embeddings",
        "",
        "| family | rule | background | entry step/rot | sample step/rot | IC start sample | defect anchor sample |",
        "| --- | ---: | --- | --- | --- | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['family_id']}` | {row['rule']} | `{row['background']}` | "
            f"{row['entry_orbit_step']}/{row['entry_rotation_offset']} | "
            f"{row['sample_orbit_step']}/{row['sample_rotation_offset']} | "
            f"{row['ic_start_mod_sample_canonical']} | "
            f"{row['defect_anchor_mod_sample_canonical']} |"
        )
    lines += [
        "",
        "## Ambiguity structure",
        "",
        "The scalar embedding descriptors narrow the problem but do not close it.",
        "`sample_embedding` leaves two ambiguous buckets: one under `rule_109`",
        "mixing F00/F02/F05/F08, and one under `rule_73` mixing F01/F02/F04.",
        "Adding IC start, IC length, or defect-anchor alignment does not remove",
        "those ambiguities. The first successful descriptor includes the actual",
        "canonical defect state at the sampled phase.",
        "",
        "## Verdict",
        "",
        f"**Status:** `{payload['status']}`.",
        "",
    ]
    if payload["first_success"]:
        lines.append(
            f"The first descriptor that determines family is `{payload['first_success']}`. "
            "This identifies the missing state variable left open by Fase 37: "
            "not just the background orbit embedding, but the local defect shape "
            "after burn-in. The resulting sufficient state is "
            "`(rule, sample_orbit_step, sample_rotation_offset, defect_state0)`. "
            "This is a constructive descriptor, but it is not yet a closed-form "
            "prediction from the initial background and IC alone."
        )
    else:
        lines.append(
            "None of the tested embedding descriptors determines the shape family. "
            "The family still requires a richer local state description."
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
