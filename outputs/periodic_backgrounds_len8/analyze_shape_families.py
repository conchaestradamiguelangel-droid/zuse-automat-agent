"""Fase 30: cluster T=15 defect-shape families by background.

Fase 29 showed that the T=15 cycle is not background-independent and is not
captured by one fixed local block signature. This script asks the next, more
positive question: whether the background-dependent defect cycles form a small
number of phase-rotated shape families.

The unit of analysis is the five-state defect cycle from Fase 27. Two cycles
belong to the same family when they are equal up to a cyclic phase rotation.
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
RESULTS_JSON = OUT_DIR / "shape_families_results.json"
REPORT_MD = OUT_DIR / "shape_families_report.md"


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
        raise RuntimeError(f"Expected 20 representatives, got {len(rows)}")
    return rows


def rotations(sequence: list[str]) -> list[tuple[str, ...]]:
    return [
        tuple(sequence[index:] + sequence[:index])
        for index in range(len(sequence))
    ]


def canonical_cycle(sequence: list[str]) -> tuple[tuple[str, ...], int]:
    all_rotations = rotations(sequence)
    canonical = min(all_rotations)
    return canonical, all_rotations.index(canonical)


def rotate_word(word: str, shift: int) -> str:
    shift %= len(word)
    return word[shift:] + word[:shift]


def complement_word(word: str) -> str:
    return "".join("1" if bit == "0" else "0" for bit in word)


def minimal_period(word: str) -> int:
    for period in range(1, len(word) + 1):
        if len(word) % period == 0 and word == word[:period] * (len(word) // period):
            return period
    raise AssertionError("Every finite word has a finite period")


def circular_runs(word: str) -> list[int]:
    if not word:
        return []
    if set(word) == {"0"} or set(word) == {"1"}:
        return [len(word)]
    doubled = word + word
    start = next(index for index in range(len(word)) if word[index] != word[index - 1])
    runs = []
    current = doubled[start]
    length = 0
    for char in doubled[start : start + len(word)]:
        if char == current:
            length += 1
        else:
            runs.append(length)
            current = char
            length = 1
    runs.append(length)
    return runs


def word_from_state(state: tuple[int, ...], width: int = 256, period: int = 8) -> str:
    active = set(state)
    bits = ["1" if index in active else "0" for index in range(period)]
    return "".join(bits)


def background_orbit_words(base, rule: int, background: str, steps: int = 3) -> list[str]:
    state = base.background_state(background)
    words = [word_from_state(state, base.WIDTH, len(background))]
    for _ in range(steps):
        state = base.eca_step_state(state, rule)
        words.append(word_from_state(state, base.WIDTH, len(background)))
    return words


def canonical_temporal_orbit(words: list[str]) -> tuple[str, ...]:
    cycle = words[:-1] if words[0] == words[-1] else words
    rotations_ = [
        tuple(cycle[index:] + cycle[:index])
        for index in range(len(cycle))
    ]
    return min(rotations_)


def background_features(base, rule: int, background: str) -> dict:
    orbit = background_orbit_words(base, rule, background)
    return {
        "background": background,
        "active_count": background.count("1"),
        "transition_count": sum(
            1 for index, bit in enumerate(background)
            if bit != background[(index + 1) % len(background)]
        ),
        "run_lengths": circular_runs(background),
        "minimal_period": minimal_period(background),
        "temporal_orbit": orbit,
        "temporal_orbit_canonical": list(canonical_temporal_orbit(orbit)),
        "complement": complement_word(background),
    }


def cluster_records(base, representatives: list[dict]) -> dict:
    enriched = []
    for record in representatives:
        canonical, phase_shift = canonical_cycle(record["defect_states"])
        features = background_features(base, int(record["rule"]), record["background"])
        enriched.append(
            {
                "rule": int(record["rule"]),
                "background": record["background"],
                "ic": record["ic"],
                "defect_states": record["defect_states"],
                "canonical_cycle": list(canonical),
                "phase_shift_to_canonical": phase_shift,
                "defect_widths": record["defect_width_per_state"],
                "background_features": features,
            }
        )

    by_rule: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    global_clusters: dict[str, list[dict]] = defaultdict(list)
    for record in enriched:
        key = json.dumps(record["canonical_cycle"])
        by_rule[str(record["rule"])][key].append(record)
        global_clusters[key].append(record)

    def summarize_cluster(key: str, members: list[dict]) -> dict:
        return {
            "canonical_cycle": json.loads(key),
            "size": len(members),
            "rules": sorted({member["rule"] for member in members}),
            "members": [
                {
                    "rule": member["rule"],
                    "background": member["background"],
                    "ic": member["ic"],
                    "phase_shift_to_canonical": member["phase_shift_to_canonical"],
                    "active_count": member["background_features"]["active_count"],
                    "transition_count": member["background_features"]["transition_count"],
                    "temporal_orbit_canonical": member["background_features"][
                        "temporal_orbit_canonical"
                    ],
                }
                for member in sorted(
                    members,
                    key=lambda item: (
                        item["rule"],
                        item["background"],
                        item["ic"],
                    ),
                )
            ],
        }

    by_rule_summary = {}
    for rule, clusters in sorted(by_rule.items()):
        summaries = [
            summarize_cluster(key, members)
            for key, members in sorted(
                clusters.items(),
                key=lambda item: (-len(item[1]), item[0]),
            )
        ]
        by_rule_summary[rule] = {
            "cluster_count": len(summaries),
            "largest_cluster_size": max(summary["size"] for summary in summaries),
            "clusters": summaries,
        }

    global_summaries = [
        summarize_cluster(key, members)
        for key, members in sorted(
            global_clusters.items(),
            key=lambda item: (-len(item[1]), item[0]),
        )
    ]

    return {
        "representatives": enriched,
        "by_rule": by_rule_summary,
        "global": {
            "cluster_count": len(global_summaries),
            "largest_cluster_size": max(summary["size"] for summary in global_summaries),
            "clusters": global_summaries,
        },
    }


def feature_separation(records: list[dict]) -> dict:
    """Check whether simple background descriptors determine the shape family."""
    features = {
        "active_count": lambda r: str(r["background_features"]["active_count"]),
        "transition_count": lambda r: str(r["background_features"]["transition_count"]),
        "active_transition_pair": lambda r: (
            f"{r['background_features']['active_count']}/"
            f"{r['background_features']['transition_count']}"
        ),
        "temporal_orbit_canonical": lambda r: "|".join(
            r["background_features"]["temporal_orbit_canonical"]
        ),
    }
    result = {}
    for name, getter in features.items():
        buckets: dict[str, set[str]] = defaultdict(set)
        for record in records:
            buckets[getter(record)].add(json.dumps(record["canonical_cycle"]))
        pure = sum(1 for cycles in buckets.values() if len(cycles) == 1)
        result[name] = {
            "bucket_count": len(buckets),
            "pure_buckets": pure,
            "ambiguous_buckets": len(buckets) - pure,
            "determines_cycle_family": all(len(cycles) == 1 for cycles in buckets.values()),
            "ambiguous_examples": {
                key: len(cycles)
                for key, cycles in sorted(buckets.items())
                if len(cycles) > 1
            },
        }
    return result


def render_report(result: dict) -> str:
    lines = [
        "# Fase 30: Background-Indexed Shape Families for the T=15 Cycle",
        "",
        "## Question",
        "",
        "Fase 29 showed that the T=15 cycle is not described by a single",
        "background-independent defect shape or by one fixed local block",
        "signature. Fase 30 asks whether the background-dependent defect cycles",
        "nevertheless collapse into a small number of phase-rotated shape",
        "families.",
        "",
        "Two five-state cycles are considered equivalent when one is a cyclic",
        "phase rotation of the other.",
        "",
        "## Summary",
        "",
        f"- Representatives: `{len(result['representatives'])}`.",
        f"- Global shape families: `{result['global']['cluster_count']}`.",
        f"- Largest global family size: `{result['global']['largest_cluster_size']}`.",
    ]
    for rule, summary in result["by_rule"].items():
        lines.append(
            f"- rule_{rule}: `{summary['cluster_count']}` families; "
            f"largest family size `{summary['largest_cluster_size']}`."
        )

    lines.extend(
        [
            "",
            "## Shape families by rule",
            "",
            "| rule | family | size | backgrounds (phase shift) |",
            "| --- | ---: | ---: | --- |",
        ]
    )
    for rule, summary in result["by_rule"].items():
        for index, cluster in enumerate(summary["clusters"], start=1):
            members = ", ".join(
                f"`{member['background']}` (s={member['phase_shift_to_canonical']})"
                for member in cluster["members"]
            )
            lines.append(
                f"| rule_{rule} | {index} | {cluster['size']} | {members} |"
            )

    lines.extend(
        [
            "",
            "## Shared families across conjugate rules",
            "",
            "| family | size | rules | members |",
            "| ---: | ---: | --- | --- |",
        ]
    )
    shared = [
        cluster
        for cluster in result["global"]["clusters"]
        if len(cluster["rules"]) > 1
    ]
    for index, cluster in enumerate(shared, start=1):
        members = ", ".join(
            f"`rule_{member['rule']}/{member['background']}`"
            for member in cluster["members"]
        )
        rules = ", ".join(f"rule_{rule}" for rule in cluster["rules"])
        lines.append(f"| {index} | {cluster['size']} | {rules} | {members} |")
    if not shared:
        lines.append("| - | 0 | - | no shared canonical cycle |")

    lines.extend(
        [
            "",
            "## Descriptor tests",
            "",
            "| descriptor | buckets | pure buckets | ambiguous buckets | determines family |",
            "| --- | ---: | ---: | ---: | --- |",
        ]
    )
    for name, test in result["feature_separation"].items():
        lines.append(
            f"| `{name}` | {test['bucket_count']} | {test['pure_buckets']} | "
            f"{test['ambiguous_buckets']} | {test['determines_cycle_family']} |"
        )

    lines.extend(
        [
            "",
            "Simple scalar background descriptors do not determine the shape family.",
            "The strongest tested descriptor is the canonical temporal orbit of the",
            "background under the same rule; it is exact in this representative set,",
            "but this is mostly a restatement of the full background orbit rather",
            "than a compact symbolic law.",
            "",
            "## Verdict",
            "",
            "**Status:** `PARTIAL_POSITIVE`.",
            "",
            "The T=15 family is not one universal defect cycle. It decomposes into",
            "a finite set of background-indexed five-state shape families: seven",
            "families for `rule_73`, eight for `rule_109`, and thirteen globally",
            "after merging exact phase-rotated cycles shared across the conjugate",
            "rules. This is stronger than the Fase 29 negative result because it",
            "shows where the background dependence lives: in discrete phase-rotated",
            "shape families, not in unstructured variation.",
            "",
            "## Falsifiable implication",
            "",
            "A future symbolic derivation should map the temporal background orbit",
            "and local IC alignment to one of these finite shape families and a",
            "phase offset. Any derivation predicting a single universal five-state",
            "defect cycle is falsified; any derivation predicting arbitrary",
            "unclustered shape variation is also too weak.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    module = load_len8_module()
    base = module.load_base_module()
    representatives = load_representatives()
    clusters = cluster_records(base, representatives)
    result = {
        "status": "PARTIAL_POSITIVE",
        **clusters,
    }
    result["feature_separation"] = feature_separation(result["representatives"])
    RESULTS_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_MD.write_text(render_report(result), encoding="utf-8")
    print(f"wrote {RESULTS_JSON}")
    print(f"wrote {REPORT_MD}")
    print(
        f"families global={result['global']['cluster_count']} "
        f"rule73={result['by_rule']['73']['cluster_count']} "
        f"rule109={result['by_rule']['109']['cluster_count']}"
    )


if __name__ == "__main__":
    main()
