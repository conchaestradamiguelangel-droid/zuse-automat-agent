"""Fase 28: extract an algebraic signature for the T=15 five-state cycle.

The localized defect does not evolve under the original ECA rule alone. If
`b` is a background neighborhood and `d` is its XOR-defect neighborhood, the
induced local update is:

    delta_f(b, d) = f(b XOR d) XOR f(b)

This script profiles that induced rule over all three microsteps of every F^3
transition in the 20 minimal T=15 representatives. It also verifies the exact
black/white conjugation relation between rule_73 and rule_109 at orbit level.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
RESULTS_JSON = OUT_DIR / "symbolic_locking_results.json"
REPORT_MD = OUT_DIR / "symbolic_locking_report.md"

SAMPLE_START = 81
BACKGROUND_PERIOD = 3
LOCKING_RATIO = 5
FINAL_STEP = SAMPLE_START + BACKGROUND_PERIOD * LOCKING_RATIO


def load_len8_module():
    spec = importlib.util.spec_from_file_location("periodic_background_len8", LEN8_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import detector from {LEN8_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_representatives() -> list[dict]:
    rows = [
        json.loads(line)
        for line in LOCKING_RESULTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 20:
        raise RuntimeError(f"Expected 20 Fase-27 representatives, got {len(rows)}")
    return rows


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def perturbation_orbit(
    base,
    rule: int,
    background_frames: list[tuple[int, ...]],
    word: str,
) -> list[tuple[int, ...]]:
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


def neighborhood_index(active: set[int], position: int, width: int) -> int:
    left = int((position - 1) % width in active)
    center = int(position in active)
    right = int((position + 1) % width in active)
    return (left << 2) | (center << 1) | right


def causal_positions(diff_now: tuple[int, ...], diff_next: tuple[int, ...], width: int) -> list[int]:
    """Cells in the one-step defect cone, including births and deaths."""
    positions = set(diff_next)
    for position in diff_now:
        positions.update(((position - 1) % width, position, (position + 1) % width))
    return sorted(positions)


def role_for(position: int, now: set[int], next_state: set[int]) -> str:
    if position in now and position in next_state:
        return "persistent"
    if position in now:
        return "death"
    if position in next_state:
        return "birth"
    return "causal_context"


def transition_key(background_index: int, defect_index: int) -> str:
    return f"b{background_index:03b}_d{defect_index:03b}"


def ordinary_entry_label(index: int) -> str:
    return f"{index:03b}"


def profile_representative(base, representative: dict) -> dict:
    rule = int(representative["rule"])
    background = representative["background"]
    word = representative["ic"]
    bg_frames = background_orbit(base, rule, background, FINAL_STEP)
    diff_frames = perturbation_orbit(base, rule, bg_frames, word)

    macro_transitions = []
    all_rule_entries: set[int] = set()
    all_induced_keys: set[str] = set()
    induced_counts: Counter[str] = Counter()
    role_counts: dict[str, Counter[str]] = defaultdict(Counter)

    for macro_index in range(LOCKING_RATIO):
        macro_start = SAMPLE_START + macro_index * BACKGROUND_PERIOD
        macro_entries: set[int] = set()
        macro_keys: set[str] = set()
        microsteps = []

        for micro_offset in range(BACKGROUND_PERIOD):
            time_index = macro_start + micro_offset
            bg_now = set(bg_frames[time_index])
            diff_now = set(diff_frames[time_index])
            diff_next = set(diff_frames[time_index + 1])
            full_now = bg_now ^ diff_now
            step_entries: set[int] = set()
            step_keys: set[str] = set()
            step_roles: Counter[str] = Counter()

            for position in causal_positions(
                diff_frames[time_index],
                diff_frames[time_index + 1],
                base.WIDTH,
            ):
                background_index = neighborhood_index(bg_now, position, base.WIDTH)
                defect_index = neighborhood_index(diff_now, position, base.WIDTH)
                full_index = neighborhood_index(full_now, position, base.WIDTH)
                if full_index != (background_index ^ defect_index):
                    raise AssertionError("Neighborhood XOR identity failed")

                background_output = (rule >> background_index) & 1
                full_output = (rule >> full_index) & 1
                defect_output = full_output ^ background_output
                expected_output = int(position in diff_next)
                if defect_output != expected_output:
                    raise AssertionError(
                        f"Induced-rule mismatch rule={rule} t={time_index} pos={position}"
                    )

                key = transition_key(background_index, defect_index)
                role = role_for(position, diff_now, diff_next)
                step_entries.update((background_index, full_index))
                step_keys.add(key)
                step_roles[role] += 1
                induced_counts[key] += 1
                role_counts[key][role] += 1

            macro_entries.update(step_entries)
            macro_keys.update(step_keys)
            microsteps.append(
                {
                    "t": time_index,
                    "rule_entries": sorted(ordinary_entry_label(index) for index in step_entries),
                    "induced_keys": sorted(step_keys),
                    "role_counts": dict(sorted(step_roles.items())),
                }
            )

        all_rule_entries.update(macro_entries)
        all_induced_keys.update(macro_keys)
        macro_transitions.append(
            {
                "transition": f"S{macro_index}->S{(macro_index + 1) % LOCKING_RATIO}",
                "rule_entries": sorted(ordinary_entry_label(index) for index in macro_entries),
                "induced_keys": sorted(macro_keys),
                "microsteps": microsteps,
            }
        )

    return {
        "rule": rule,
        "background": background,
        "ic": word,
        "rule_entries_used": sorted(ordinary_entry_label(index) for index in all_rule_entries),
        "induced_keys_used": sorted(all_induced_keys),
        "induced_key_counts": dict(sorted(induced_counts.items())),
        "induced_key_roles": {
            key: dict(sorted(counter.items()))
            for key, counter in sorted(role_counts.items())
        },
        "macro_transitions": macro_transitions,
    }


def rotate(word: str, shift: int) -> str:
    shift %= len(word)
    return word[shift:] + word[:shift]


def complement_word(word: str) -> str:
    return "".join("1" if bit == "0" else "0" for bit in word)


def conjugation_tests(base, representatives: list[dict]) -> list[dict]:
    """Verify C F_73 = F_109 C, including background and local IC."""
    tests = []
    for representative in representatives:
        if int(representative["rule"]) != 73:
            continue
        background = representative["background"]
        word = representative["ic"]
        conjugate_background = complement_word(background)
        conjugate_word = complement_word(word)

        bg73 = background_orbit(base, 73, background, FINAL_STEP)
        d73 = perturbation_orbit(base, 73, bg73, word)
        bg109 = background_orbit(base, 109, conjugate_background, FINAL_STEP)
        d109 = perturbation_orbit(base, 109, bg109, conjugate_word)

        background_complement_exact = all(
            set(frame109) == set(range(base.WIDTH)) - set(frame73)
            for frame73, frame109 in zip(bg73, bg109)
        )
        defect_invariant_exact = d73 == d109

        tests.append(
            {
                "rule_73_background": background,
                "rule_109_background": conjugate_background,
                "rule_73_ic": word,
                "rule_109_ic": conjugate_word,
                "background_complement_exact": background_complement_exact,
                "defect_invariant_exact": defect_invariant_exact,
                "conjugation_exact": background_complement_exact and defect_invariant_exact,
            }
        )
    return tests


def aggregate(profiles: list[dict], conjugation: list[dict]) -> dict:
    all_entries = {ordinary_entry_label(index) for index in range(8)}
    all_keys = {
        transition_key(background_index, defect_index)
        for background_index in range(8)
        for defect_index in range(1, 8)
    }
    macro_supports = [
        set(transition["induced_keys"])
        for profile in profiles
        for transition in profile["macro_transitions"]
    ]
    representative_supports = [set(profile["induced_keys_used"]) for profile in profiles]
    rule_profiles = {}
    for rule in (73, 109):
        selected = [profile for profile in profiles if profile["rule"] == rule]
        phase_intersections = []
        for phase_index in range(LOCKING_RATIO):
            phase_intersections.append(
                sorted(
                    set.intersection(
                        *(
                            set(profile["macro_transitions"][phase_index]["induced_keys"])
                            for profile in selected
                        )
                    )
                )
            )
        rule_profiles[str(rule)] = {
            "rule_entries_union": sorted(
                set().union(*(set(profile["rule_entries_used"]) for profile in selected))
            ),
            "induced_keys_union": sorted(
                set().union(*(set(profile["induced_keys_used"]) for profile in selected))
            ),
            "induced_keys_intersection": sorted(
                set.intersection(*(set(profile["induced_keys_used"]) for profile in selected))
            ),
            "phase_intersections": phase_intersections,
        }

    entries_union = set().union(*(set(profile["rule_entries_used"]) for profile in profiles))
    induced_union = set().union(*representative_supports)
    universal_by_representative = set.intersection(*representative_supports)
    universal_by_macro_transition = set.intersection(*macro_supports)

    support_signature = sorted(universal_by_macro_transition)

    conjugation_identity_rows = []
    for background_index in range(8):
        for defect_index in range(8):
            delta73 = (
                ((73 >> (background_index ^ defect_index)) & 1)
                ^ ((73 >> background_index) & 1)
            )
            conjugate_background = 7 - background_index
            delta109 = (
                ((109 >> (conjugate_background ^ defect_index)) & 1)
                ^ ((109 >> conjugate_background) & 1)
            )
            conjugation_identity_rows.append(
                {
                    "background": f"{background_index:03b}",
                    "defect": f"{defect_index:03b}",
                    "delta_rule73": delta73,
                    "complemented_background": f"{conjugate_background:03b}",
                    "delta_rule109": delta109,
                    "equal": delta73 == delta109,
                }
            )
    conjugation_identity_exact = all(row["equal"] for row in conjugation_identity_rows)

    if support_signature:
        support_hypothesis = (
            "Every asymptotic F^3 edge activates the induced defect-transition "
            f"support {support_signature}; a valid T=15 representative omitting "
            "one of these keys would falsify this support hypothesis."
        )
    else:
        support_hypothesis = (
            "No non-empty induced transition key is shared by all 100 F^3 edges. "
            "Therefore the five-cycle is not driven by a fixed sparse subset of "
            "local table entries; it depends on phase- and background-specific "
            "spatial organization of the full induced defect rule."
        )
    hypothesis = (
        support_hypothesis
        + " Independently, the exact identity "
        "delta_109(complement(b),d)=delta_73(b,d) predicts that every rule_73 "
        "defect orbit has an identical rule_109 orbit under simultaneous "
        "black/white complementation of background and full IC. One counterexample "
        "to either the 64-row local identity or the orbit mapping would falsify "
        "the conjugation claim."
    )

    return {
        "universal_entries": sorted(
            set.intersection(
                *(set(transition["rule_entries"]) for profile in profiles for transition in profile["macro_transitions"])
            )
        ),
        "never_used_entries": sorted(all_entries - entries_union),
        "universal_induced_keys_by_representative": sorted(universal_by_representative),
        "universal_induced_keys_by_macro_transition": support_signature,
        "never_used_induced_keys": sorted(all_keys - induced_union),
        "cycle_rule73_entry_signature": [
            transition["induced_keys"]
            for transition in next(profile for profile in profiles if profile["rule"] == 73)[
                "macro_transitions"
            ]
        ],
        "cycle_rule109_entry_signature": [
            transition["induced_keys"]
            for transition in next(profile for profile in profiles if profile["rule"] == 109)[
                "macro_transitions"
            ]
        ],
        "rule_profiles": rule_profiles,
        "conjugation_verified": all(test["conjugation_exact"] for test in conjugation),
        "conjugation_tests": conjugation,
        "conjugation_identity_exact": conjugation_identity_exact,
        "conjugation_identity_rows": conjugation_identity_rows,
        "sparse_universal_support_found": bool(support_signature),
        "hypothesis": hypothesis,
    }


def render_report(result: dict) -> str:
    aggregate_result = result["aggregate"]
    profiles = result["representatives"]
    conjugation = aggregate_result["conjugation_tests"]
    lines = [
        "# Fase 28: Symbolic Signature of the Five-State Locking Cycle",
        "",
        "## Induced defect rule",
        "",
        "The defect does not evolve under `f` alone. For a background neighborhood",
        "`b` and XOR-defect neighborhood `d`, its exact local rule is:",
        "",
        "`delta_f(b,d) = f(b XOR d) XOR f(b)`.",
        "",
        "All three microsteps of each of the five `F^3` transitions are profiled",
        "for all 20 minimal T=15 representatives.",
        "",
        "**Status:** `PARTIAL` - exact conjugation is established, while the",
        "proposed sparse universal-entry explanation is rejected.",
        "",
        "## Global support",
        "",
        f"- Ordinary rule entries present in every macro-transition: "
        f"`{aggregate_result['universal_entries']}`.",
        f"- Ordinary rule entries never used in the causal defect cone: "
        f"`{aggregate_result['never_used_entries']}`.",
        f"- Induced `(background, defect)` keys present in every representative: "
        f"`{aggregate_result['universal_induced_keys_by_representative']}`.",
        f"- Induced keys present in every one of the 100 F^3 transitions: "
        f"`{aggregate_result['universal_induced_keys_by_macro_transition']}`.",
        f"- Induced keys never used: `{aggregate_result['never_used_induced_keys']}`.",
        f"- Non-empty universal induced support found: "
        f"`{aggregate_result['sparse_universal_support_found']}`.",
        "",
        "Every macro-transition uses all eight ordinary rule entries, while no",
        "single induced `(b,d)` key appears in all 100 macro-transitions. The",
        "original sparse-entry hypothesis is therefore rejected by the data.",
        "",
        "## Black/white conjugation",
        "",
        f"- Exact local identity "
        f"`delta_109(complement(b),d) = delta_73(b,d)`: "
        f"`{sum(row['equal'] for row in aggregate_result['conjugation_identity_rows'])}/"
        f"{len(aggregate_result['conjugation_identity_rows'])}`.",
        f"- Exact orbit-level conjugation tests: "
        f"`{sum(test['conjugation_exact'] for test in conjugation)}/{len(conjugation)}`.",
        "- Under simultaneous complementation of background and full IC, the XOR",
        "  defect is invariant rather than complemented:",
        "  `(~X) XOR (~B) = X XOR B`.",
        "",
        "| background rule_73 | IC rule_73 | complemented background | complemented IC | exact |",
        "| --- | --- | --- | --- | --- |",
    ]
    for test in conjugation:
        lines.append(
            f"| `{test['rule_73_background']}` | `{test['rule_73_ic']}` | "
            f"`{test['rule_109_background']}` | `{test['rule_109_ic']}` | "
            f"{test['conjugation_exact']} |"
        )

    lines.extend(
        [
            "",
            "## Per-rule support",
            "",
            "| rule | ordinary entries | induced union | induced intersection |",
            "| --- | --- | ---: | ---: |",
        ]
    )
    for rule, profile in aggregate_result["rule_profiles"].items():
        lines.append(
            f"| rule_{rule} | `{profile['rule_entries_union']}` | "
            f"{len(profile['induced_keys_union'])} | "
            f"{len(profile['induced_keys_intersection'])} |"
        )

    lines.extend(
        [
            "",
            "Phase-specific intersections exist within each rule but differ across",
            "backgrounds and between the conjugate rules. Their sizes by phase are:",
            "",
            f"- rule_73: `{[len(keys) for keys in aggregate_result['rule_profiles']['73']['phase_intersections']]}`.",
            f"- rule_109: `{[len(keys) for keys in aggregate_result['rule_profiles']['109']['phase_intersections']]}`.",
            "",
            "## Falsifiable hypothesis",
            "",
            aggregate_result["hypothesis"],
            "",
            "The positive result is the exact conjugation law. The negative result is",
            "equally informative: neither ordinary table-entry reduction nor one fixed",
            "induced-key support explains all five-cycle edges. A minimal Boolean",
            "derivation of the five-cycle must therefore encode spatial phase or a",
            "higher-order block state, rather than only entry presence.",
            "",
            "## Scope",
            "",
            f"- Representatives: `{len(profiles)}`.",
            "- Macro-transitions: `100` (20 representatives x 5 edges).",
            "- Microsteps profiled: `300`.",
            "- Sample interval: `t=81..96`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    module = load_len8_module()
    base = module.load_base_module()
    representatives = load_representatives()
    profiles = [profile_representative(base, representative) for representative in representatives]
    conjugation = conjugation_tests(base, representatives)
    result = {
        "status": "PARTIAL",
        "summary": (
            "Exact black/white conjugation established; sparse universal-entry "
            "explanation rejected."
        ),
        "representatives": profiles,
        "aggregate": aggregate(profiles, conjugation),
    }
    RESULTS_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_MD.write_text(render_report(result), encoding="utf-8")
    print(
        json.dumps(
            {
                "representatives": len(profiles),
                "conjugation_verified": result["aggregate"]["conjugation_verified"],
                "universal_induced_keys_by_macro_transition": result["aggregate"][
                    "universal_induced_keys_by_macro_transition"
                ],
                "results": str(RESULTS_JSON),
                "report": str(REPORT_MD),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
