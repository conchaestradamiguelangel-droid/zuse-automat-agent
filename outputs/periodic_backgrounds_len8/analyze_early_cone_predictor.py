#!/usr/bin/env python3
"""Fase 40: early causal-cone predictor for the T=15 entry state.

Fase 39 showed that the T=15 representatives enter the stable five-cycle early,
but did not find a compact algebraic pre-burn-in descriptor. Fase 40 asks a
different question: whether a short local causal-cone simulation can recover
the same stable-cycle state information without running the full 256-cell,
81-step background/defect simulation.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
BASE_SCRIPT = OUT_DIR.parent / "periodic_backgrounds" / "sweep_periodic_background_oscillators.py"
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
EMBEDDING_RESULTS = OUT_DIR / "defect_embedding_descriptor_results.json"
RESULTS_JSON = OUT_DIR / "early_cone_predictor_results.json"
REPORT_MD = OUT_DIR / "early_cone_predictor_report.md"

WINDOWS = (3, 6, 9, 12)
SAMPLE_START = 81
BACKGROUND_PERIOD = 3


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


def bit_from_state(active: set[int], pos: int, width: int) -> int:
    return 1 if (pos % width) in active else 0


def ic_start(width: int, ic: str) -> int:
    return width // 2 - len(ic) // 2


def initial_actual_bit(base, bg_set: set[int], global_pos: int, ic: str) -> int:
    start = ic_start(base.WIDTH, ic)
    if start <= global_pos <= start + len(ic) - 1:
        idx = global_pos - start
        return int(ic[idx])
    return bit_from_state(bg_set, global_pos, base.WIDTH)


def rule_output(rule: int, left: int, center: int, right: int) -> int:
    idx = (left << 2) | (center << 1) | right
    return (rule >> idx) & 1


def local_cone_diff(base, rule: int, background: str, ic: str, t_window: int, mode: str) -> dict:
    """Simulate only the initial perturbation cone.

    `mode="span"` uses the full IC span plus a radius-t_window causal margin.
    `mode="center"` uses a strict 2*t_window+1 window around the IC center.
    Boundary cells just outside the local window are supplied by the unperturbed
    background orbit, which is exact because the perturbation cannot reach them
    within t_window steps.
    """

    bg_frames = background_orbit(base, rule, background, t_window)
    width = base.WIDTH
    start = ic_start(width, ic)
    end = start + len(ic) - 1
    if mode == "span":
        left = start - t_window
        right = end + t_window
    elif mode == "center":
        center = start + (len(ic) - 1) // 2
        left = center - t_window
        right = center + t_window
    else:
        raise ValueError(mode)
    positions = list(range(left, right + 1))
    bg0 = set(bg_frames[0])
    actual = [initial_actual_bit(base, bg0, pos, ic) for pos in positions]

    for time_index in range(t_window):
        bg_now = set(bg_frames[time_index])
        next_actual = []
        for local_index, global_pos in enumerate(positions):
            if local_index == 0:
                left_bit = bit_from_state(bg_now, global_pos - 1, width)
            else:
                left_bit = actual[local_index - 1]
            center_bit = actual[local_index]
            if local_index == len(positions) - 1:
                right_bit = bit_from_state(bg_now, global_pos + 1, width)
            else:
                right_bit = actual[local_index + 1]
            next_actual.append(rule_output(rule, left_bit, center_bit, right_bit))
        actual = next_actual

    bg_final = set(bg_frames[t_window])
    diff_positions = [
        global_pos % width
        for global_pos, actual_bit in zip(positions, actual)
        if actual_bit ^ bit_from_state(bg_final, global_pos, width)
    ]
    canon = canonical_defect(width, tuple(sorted(diff_positions)))
    return {
        "mode": mode,
        "t_window": t_window,
        "window_cells": len(positions),
        "left": left,
        "right": right,
        "state": canon["hex"] if canon else None,
        "anchor": canon["anchor"] if canon else None,
        "width": canon["width"] if canon else None,
    }


def load_family_lookup() -> dict[tuple[int, str], str]:
    embedding = json.loads(EMBEDDING_RESULTS.read_text(encoding="utf-8"))
    return {
        (int(row["rule"]), row["background"]): row["family_id"]
        for row in embedding["rows"]
    }


def analyze() -> dict:
    base = load_base_module()
    family_lookup = load_family_lookup()
    rows = []
    for record in load_jsonl(LOCKING_RESULTS):
        rule = int(record["rule"])
        background = record["background"]
        ic = record["ic"]
        stable_states = list(record["defect_states"])
        state_to_phase = {state: index for index, state in enumerate(stable_states)}

        bg_frames = background_orbit(base, rule, background, SAMPLE_START)
        full_frames = perturbation_orbit(base, rule, bg_frames, ic)
        timeline = []
        first_entry = None
        for t in range(0, SAMPLE_START + 1, BACKGROUND_PERIOD):
            canon = canonical_defect(base.WIDTH, full_frames[t])
            state = canon["hex"] if canon else None
            phase = state_to_phase.get(state)
            timeline.append({"t": t, "state": state, "phase": phase})
            if first_entry is None and phase is not None:
                first_entry = timeline[-1]
        if first_entry is None:
            raise RuntimeError(f"No stable entry for {rule} {background} {ic}")

        sample_state = timeline[-1]["state"]
        sample_phase = timeline[-1]["phase"]
        full_state_by_time = {item["t"]: item["state"] for item in timeline}
        cone_results = []
        for mode in ("span", "center"):
            for t_window in WINDOWS:
                cone = local_cone_diff(base, rule, background, ic, t_window, mode)
                cone_phase = state_to_phase.get(cone["state"])
                if cone_phase is None:
                    projected_phase = None
                    projected_state = None
                else:
                    steps_to_sample = (SAMPLE_START - t_window) // BACKGROUND_PERIOD
                    projected_phase = (cone_phase + steps_to_sample) % len(stable_states)
                    projected_state = stable_states[projected_phase]
                cone.update(
                    {
                        "cone_phase": cone_phase,
                        "matches_full_state_at_t": cone["state"] == full_state_by_time[t_window],
                        "matches_entry_state": cone["state"] == first_entry["state"],
                        "matches_sample_state_direct": cone["state"] == sample_state,
                        "projected_phase_to_sample": projected_phase,
                        "projected_state_to_sample": projected_state,
                        "matches_sample_state_projected": projected_state == sample_state,
                        "compression_ratio": (base.WIDTH * SAMPLE_START)
                        / (cone["window_cells"] * t_window),
                    }
                )
                cone_results.append(cone)

        rows.append(
            {
                "rule": rule,
                "background": background,
                "family_id": family_lookup[(rule, background)],
                "ic": ic,
                "ic_len": len(ic),
                "entry_time_full": first_entry["t"],
                "entry_phase_full": first_entry["phase"],
                "entry_state_full": first_entry["state"],
                "sample_phase_full": sample_phase,
                "sample_state_full": sample_state,
                "cone_results": cone_results,
            }
        )

    rows = sorted(rows, key=lambda item: (item["family_id"], item["rule"], item["background"]))
    summaries = []
    for mode in ("span", "center"):
        for t_window in WINDOWS:
            subset = [
                cone
                for row in rows
                for cone in row["cone_results"]
                if cone["mode"] == mode and cone["t_window"] == t_window
            ]
            stable_hits = sum(cone["cone_phase"] is not None for cone in subset)
            full_t_matches = sum(cone["matches_full_state_at_t"] for cone in subset)
            entry_matches = sum(cone["matches_entry_state"] for cone in subset)
            projected_matches = sum(cone["matches_sample_state_projected"] for cone in subset)
            direct_sample_matches = sum(cone["matches_sample_state_direct"] for cone in subset)
            compression_values = [cone["compression_ratio"] for cone in subset]
            summaries.append(
                {
                    "mode": mode,
                    "t_window": t_window,
                    "stable_hits": stable_hits,
                    "full_t_matches": full_t_matches,
                    "entry_matches": entry_matches,
                    "projected_sample_matches": projected_matches,
                    "direct_sample_matches": direct_sample_matches,
                    "compression_ratio_min": min(compression_values),
                    "compression_ratio_max": max(compression_values),
                    "predictor_success": projected_matches == len(rows),
                }
            )

    family_descriptor_tests = []
    for mode in ("span", "center"):
        for t_window in WINDOWS:
            buckets: dict[str, set[str]] = defaultdict(set)
            for row in rows:
                cone = next(
                    c
                    for c in row["cone_results"]
                    if c["mode"] == mode and c["t_window"] == t_window
                )
                key = json.dumps([row["rule"], cone["state"]], sort_keys=True)
                buckets[key].add(row["family_id"])
            ambiguous = {
                key: sorted(values)
                for key, values in buckets.items()
                if len(values) > 1
            }
            family_descriptor_tests.append(
                {
                    "mode": mode,
                    "t_window": t_window,
                    "descriptor": "(rule, cone_state)",
                    "bucket_count": len(buckets),
                    "ambiguous_bucket_count": len(ambiguous),
                    "determines_family": not ambiguous,
                    "ambiguous_buckets": ambiguous,
                }
            )

    success = [item for item in summaries if item["predictor_success"]]
    if success:
        status = "EARLY_CONE_PREDICTOR_FOUND"
        best = min(
            success,
            key=lambda item: (item["t_window"], -item["compression_ratio_min"]),
        )
    else:
        status = "NO_EARLY_CONE_COMPRESSION"
        best = None

    return {
        "status": status,
        "record_count": len(rows),
        "windows": list(WINDOWS),
        "sample_start": SAMPLE_START,
        "best_predictor": best,
        "summaries": summaries,
        "family_descriptor_tests": family_descriptor_tests,
        "rows": rows,
    }


def write_report(data: dict) -> None:
    lines = [
        "# Fase 40: Early Causal-Cone Predictor",
        "",
        "## Question",
        "",
        "Fase 39 found no compact algebraic pre-burn-in predictor of the",
        "`T=15` entry phase. Fase 40 tests a weaker but constructive hypothesis:",
        "can the post-burn-in stable-cycle state be recovered by simulating only",
        "the local causal cone of the initial IC for `t = 3, 6, 9, 12`, rather",
        "than the full 256-cell system through the 81-step burn-in?",
        "",
        "Two local windows are tested:",
        "",
        "- `span`: the full IC span plus a causal margin of `t` cells on each side;",
        "- `center`: the strict `2t+1` window around the IC center.",
        "",
        "When a cone state lands on one of the five stable-cycle states, its phase",
        "is projected forward to `t=81` before comparison with `defect_state0`.",
        "",
        "## Summary",
        "",
        "| mode | t_window | stable hits | full-t matches | entry matches | projected sample matches | direct sample matches | compression range | success |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for row in data["summaries"]:
        lines.append(
            "| {mode} | {t_window} | {stable_hits}/20 | {full_t_matches}/20 | {entry_matches}/20 | "
            "{projected_sample_matches}/20 | {direct_sample_matches}/20 | "
            "{compression_ratio_min:.1f}x..{compression_ratio_max:.1f}x | `{predictor_success}` |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Family fallback",
            "",
            "| mode | t_window | descriptor | buckets | ambiguous buckets | determines family |",
            "| --- | ---: | --- | ---: | ---: | --- |",
        ]
    )
    for row in data["family_descriptor_tests"]:
        lines.append(
            "| {mode} | {t_window} | `{descriptor}` | {bucket_count} | "
            "{ambiguous_bucket_count} | `{determines_family}` |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Representative table",
            "",
            "| family | rule | background | IC | entry t | entry phase | span t=3 | span t=6 | span t=9 | span t=12 |",
            "| --- | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- |",
        ]
    )
    for row in data["rows"]:
        cells = []
        for t_window in WINDOWS:
            cone = next(
                c
                for c in row["cone_results"]
                if c["mode"] == "span" and c["t_window"] == t_window
            )
            if cone["cone_phase"] is None:
                text = "not stable"
            elif cone["matches_sample_state_projected"]:
                text = f"phase {cone['cone_phase']} -> ok"
            else:
                text = f"phase {cone['cone_phase']} -> miss"
            cells.append(text)
        lines.append(
            f"| `{row['family_id']}` | {row['rule']} | `{row['background']}` | "
            f"`{row['ic']}` | {row['entry_time_full']} | {row['entry_phase_full']} | "
            f"{' | '.join(cells)} |"
        )

    lines.extend(["", "## Verdict", "", f"**Status:** `{data['status']}`.", ""])
    if data["best_predictor"] is not None:
        best = data["best_predictor"]
        lines.extend(
            [
                "The early causal-cone predictor succeeds. The smallest successful",
                f"configuration is `{best['mode']}` at `t={best['t_window']}`, with a",
                f"compression range of {best['compression_ratio_min']:.1f}x..{best['compression_ratio_max']:.1f}x relative to the full",
                "256 x 81 simulation. This converts the negative Fase 39 result",
                "into a constructive causal compression: no compact closed-form",
                "descriptor was found, but the relevant state can be recovered by",
                "a short local simulation.",
            ]
        )
    else:
        lines.extend(
            [
                "No tested causal-cone window recovers `defect_state0` for all 20",
                "representatives. This would strengthen the Fase 39 irreducibility",
                "boundary, because even short local simulation would be insufficient",
                "under the tested window definitions.",
            ]
        )
    lines.append("")
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_report(analyze())


if __name__ == "__main__":
    main()
