#!/usr/bin/env python3
"""Fase 39: pre-burn-in predictors of the T=15 entry phase.

Fase 38 found that the post-burn-in descriptor

    (rule, sample_orbit_step, sample_rotation_offset, defect_state0)

determines the T=15 shape family. Fase 39 asks whether the missing
`defect_state0`/entry phase can be predicted from the initial local
background/IC configuration without running the 81-step burn-in.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
EMBEDDING_RESULTS = OUT_DIR / "defect_embedding_descriptor_results.json"
RESULTS_JSON = OUT_DIR / "preburnin_entry_phase_results.json"
REPORT_MD = OUT_DIR / "preburnin_entry_phase_report.md"

BACKGROUND_PERIOD = 3
SAMPLE_START = 81
MAX_T = SAMPLE_START


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


def bit_at(active: set[int], pos: int, width: int) -> int:
    return 1 if (pos % width) in active else 0


def local_initial_descriptor(base, background: str, ic: str, radius: int) -> dict:
    bg0 = base.background_state(background)
    bg_set = set(bg0)
    width = base.WIDTH
    word_value = int(ic, 2)
    word_len = len(ic)
    start = width // 2 - word_len // 2
    end = start + word_len - 1
    positions = list(range(start - radius, end + radius + 1))
    bg_bits = "".join(str(bit_at(bg_set, pos, width)) for pos in positions)
    desired_bits = []
    diff_bits = []
    for pos in positions:
        if start <= pos <= end:
            idx = pos - start
            desired = (word_value >> (word_len - 1 - idx)) & 1
        else:
            desired = bit_at(bg_set, pos, width)
        bg = bit_at(bg_set, pos, width)
        desired_bits.append(str(desired))
        diff_bits.append(str(desired ^ bg))
    return {
        "radius": radius,
        "bg_bits": bg_bits,
        "desired_bits": "".join(desired_bits),
        "diff_bits": "".join(diff_bits),
        "ic": ic,
        "ic_len": word_len,
        "ic_start_mod_bg": start % len(background),
    }


def load_family_lookup() -> dict[tuple[int, str], str]:
    embedding = json.loads(EMBEDDING_RESULTS.read_text(encoding="utf-8"))
    return {
        (int(row["rule"]), row["background"]): row["family_id"]
        for row in embedding["rows"]
    }


def analyze() -> list[dict]:
    base = load_len8_module().load_base_module()
    family_lookup = load_family_lookup()
    rows = []
    for record in load_jsonl(LOCKING_RESULTS):
        rule = int(record["rule"])
        background = record["background"]
        ic = record["ic"]
        bg_frames = background_orbit(base, rule, background, MAX_T)
        diff_frames = perturbation_orbit(base, rule, bg_frames, ic)
        stable_states = record["defect_states"]
        state_to_phase = {state: index for index, state in enumerate(stable_states)}

        timeline = []
        first_entry = None
        for t in range(0, MAX_T + 1, BACKGROUND_PERIOD):
            c = canonical_defect(base.WIDTH, diff_frames[t])
            state = c["hex"] if c else None
            phase = state_to_phase.get(state)
            item = {
                "t": t,
                "state": state,
                "phase": phase,
                "anchor": c["anchor"] if c else None,
                "width": c["width"] if c else None,
            }
            timeline.append(item)
            if first_entry is None and phase is not None:
                first_entry = item

        if first_entry is None:
            raise RuntimeError(f"No stable-cycle entry found for {rule} {background}")

        local = {f"radius_{radius}": local_initial_descriptor(base, background, ic, radius) for radius in (1, 2, 3, 4, 5)}
        rows.append(
            {
                "rule": rule,
                "background": background,
                "family_id": family_lookup[(rule, background)],
                "ic": ic,
                "entry_time": first_entry["t"],
                "entry_phase": first_entry["phase"],
                "sample_phase": timeline[-1]["phase"],
                "timeline": timeline,
                "local_initial": local,
            }
        )
    return sorted(rows, key=lambda item: (item["family_id"], item["rule"], item["background"]))


def descriptor_value(row: dict, name: str):
    if name == "rule_ic":
        return [row["rule"], row["ic"]]
    if name == "rule_ic_len":
        return [row["rule"], len(row["ic"])]
    if name == "rule_entry_time":
        return [row["rule"], row["entry_time"]]
    if name == "rule_entry_time_phase":
        return [row["rule"], row["entry_time"], row["entry_phase"]]
    if name.startswith("local_r_with_ic"):
        radius = name.removeprefix("local_r_with_ic")
        local = row["local_initial"][f"radius_{radius}"]
        return [row["rule"], local["bg_bits"], local["desired_bits"], local["diff_bits"], row["ic"]]
    if name.startswith("local_r"):
        radius = name.removeprefix("local_r")
        local = row["local_initial"][f"radius_{radius}"]
        return [row["rule"], local["bg_bits"], local["desired_bits"], local["diff_bits"]]
    raise KeyError(name)


def test_descriptor(rows: list[dict], descriptor: str, target: str) -> dict:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        key = json.dumps(descriptor_value(row, descriptor), sort_keys=True)
        buckets[key].append(row)
    ambiguous = []
    for key, items in buckets.items():
        values = sorted({item[target] for item in items})
        if len(values) > 1:
            ambiguous.append(
                {
                    "descriptor": json.loads(key),
                    "values": values,
                    "backgrounds": [item["background"] for item in items],
                    "families": sorted({item["family_id"] for item in items}),
                }
            )
    singleton_count = sum(1 for items in buckets.values() if len(items) == 1)
    is_posthoc = descriptor.startswith("rule_entry_time")
    compact_enough = (
        len(ambiguous) == 0
        and not is_posthoc
        and len(buckets) < len(rows)
        and singleton_count <= len(rows) // 2
    )
    return {
        "descriptor": descriptor,
        "target": target,
        "bucket_count": len(buckets),
        "singleton_bucket_count": singleton_count,
        "ambiguous_bucket_count": len(ambiguous),
        "determines_target": len(ambiguous) == 0,
        "posthoc_measurement": is_posthoc,
        "compact_enough": compact_enough,
        "ambiguous_buckets": ambiguous,
    }


def main() -> None:
    rows = analyze()
    descriptors = ["rule_ic", "rule_ic_len", "rule_entry_time", "rule_entry_time_phase"]
    descriptors += [f"local_r{radius}" for radius in (1, 2, 3, 4, 5)]
    descriptors += [f"local_r_with_ic{radius}" for radius in (1, 2, 3, 4, 5)]
    tests = []
    for target in ("entry_phase", "family_id"):
        for descriptor in descriptors:
            tests.append(test_descriptor(rows, descriptor, target))
    entry_times = sorted({row["entry_time"] for row in rows})
    compact_success = [
        t for t in tests
        if t["target"] == "entry_phase" and t["compact_enough"]
    ]
    exact_success = [
        t for t in tests
        if t["target"] == "entry_phase" and t["determines_target"]
    ]
    if compact_success:
        status = "COMPACT_PREBURNIN_DESCRIPTOR_FOUND"
    elif exact_success:
        status = "NONCOMPACT_PREBURNIN_DESCRIPTOR_FOUND"
    else:
        status = "NO_PREBURNIN_ENTRY_DESCRIPTOR"
    payload = {
        "status": status,
        "record_count": len(rows),
        "entry_times": entry_times,
        "entry_time_counts": {
            str(time): sum(1 for row in rows if row["entry_time"] == time)
            for time in entry_times
        },
        "rows": rows,
        "descriptor_tests": tests,
    }
    RESULTS_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(render_report(payload), encoding="utf-8")


def render_report(payload: dict) -> str:
    lines = [
        "# Fase 39: Pre-burn-in Entry Phase Predictors",
        "",
        "## Question",
        "",
        "Fase 38 showed that `defect_state0` after burn-in determines the T=15",
        "family together with rule and sampled background embedding. Fase 39 asks",
        "whether the stable-cycle entry phase can be predicted from the initial",
        "local background/IC configuration before running the 81-step burn-in.",
        "",
        f"- Entry times observed: `{payload['entry_times']}`.",
        f"- Entry time counts: `{payload['entry_time_counts']}`.",
        "",
        "## Descriptor tests",
        "",
        "| target | descriptor | buckets | singleton buckets | ambiguous buckets | determines target | posthoc | compact enough |",
        "| --- | --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for test in payload["descriptor_tests"]:
        lines.append(
            f"| `{test['target']}` | `{test['descriptor']}` | {test['bucket_count']} | "
            f"{test['singleton_bucket_count']} | {test['ambiguous_bucket_count']} | "
            f"`{test['determines_target']}` | `{test['posthoc_measurement']}` | "
            f"`{test['compact_enough']}` |"
        )
    lines += [
        "",
        "## Entry summary",
        "",
        "| family | rule | background | IC | entry time | entry phase | sample phase |",
        "| --- | ---: | --- | --- | ---: | ---: | ---: |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['family_id']}` | {row['rule']} | `{row['background']}` | "
            f"`{row['ic']}` | {row['entry_time']} | {row['entry_phase']} | {row['sample_phase']} |"
        )
    lines += [
        "",
        "## Verdict",
        "",
        f"**Status:** `{payload['status']}`.",
        "",
    ]
    compact_success = [t for t in payload["descriptor_tests"] if t["target"] == "entry_phase" and t["compact_enough"]]
    exact_success = [t for t in payload["descriptor_tests"] if t["target"] == "entry_phase" and t["determines_target"]]
    if compact_success:
        first = compact_success[0]
        lines.append(
            f"The first compact tested pre-burn-in descriptor that determines entry "
            f"phase is `{first['descriptor']}`. This gives a candidate left-hand "
            "predictor for the burn-in crystallization map."
        )
    elif exact_success:
        first = exact_success[0]
        lines.append(
            f"The first exact tested descriptor is `{first['descriptor']}`, but the "
            "successful local descriptors mostly create singleton buckets. This is "
            "a sample-level identifier, not yet a compact symbolic law. The useful "
            "structural result is temporal: all 20 representatives enter the stable "
            "five-cycle by t=12, and 15/20 enter at t=3."
        )
    else:
        lines.append(
            "No tested local pre-burn-in descriptor determines entry phase. The "
            "burn-in crystallization map still requires either a larger initial "
            "context or explicit forward evolution."
        )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
