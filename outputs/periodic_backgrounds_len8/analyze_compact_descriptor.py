"""Fase 31: compact descriptors for T=15 shape-family prediction.

Fase 30 found that the 20 minimal T=15 representatives collapse into 13
phase-rotated shape families. The full temporal background orbit determines
the family, but that is close to restating background identity. This script
tests shorter descriptors of the circular length-8 background and asks whether
any of them predict the global shape family without ambiguity.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
SHAPE_RESULTS = OUT_DIR / "shape_families_results.json"
RESULTS_JSON = OUT_DIR / "compact_descriptor_results.json"
REPORT_MD = OUT_DIR / "compact_descriptor_report.md"


def rotations(word: str) -> list[str]:
    return [word[index:] + word[:index] for index in range(len(word))]


def canonical_rotation(word: str) -> tuple[str, int]:
    all_rotations = rotations(word)
    canonical = min(all_rotations)
    return canonical, all_rotations.index(canonical)


def circular_subpattern_counts(word: str, length: int) -> tuple[int, ...]:
    counts = Counter(
        "".join(word[(index + offset) % len(word)] for offset in range(length))
        for index in range(len(word))
    )
    return tuple(counts.get(format(value, f"0{length}b"), 0) for value in range(1 << length))


def circular_runs(word: str) -> tuple[int, ...]:
    if set(word) in ({"0"}, {"1"}):
        return (len(word),)
    start = next(index for index in range(len(word)) if word[index] != word[index - 1])
    doubled = word + word
    runs = []
    current = doubled[start]
    run_len = 0
    for bit in doubled[start : start + len(word)]:
        if bit == current:
            run_len += 1
        else:
            runs.append(run_len)
            current = bit
            run_len = 1
    runs.append(run_len)
    return tuple(runs)


def flatten_orbit_prefix(orbit: list[str], k: int) -> str:
    repeated = "".join(orbit)
    while len(repeated) < k:
        repeated += "".join(orbit)
    return repeated[:k]


def cycle_key(cycle: list[str]) -> str:
    return json.dumps(cycle, separators=(",", ":"))


def load_records() -> list[dict]:
    payload = json.loads(SHAPE_RESULTS.read_text(encoding="utf-8"))
    global_clusters = payload["global"]["clusters"]
    family_id_by_cycle = {
        cycle_key(cluster["canonical_cycle"]): f"F{index:02d}"
        for index, cluster in enumerate(global_clusters, start=1)
    }

    records = []
    for representative in payload["representatives"]:
        background = representative["background"]
        canonical_bg, canonical_shift = canonical_rotation(background)
        features = representative["background_features"]
        family_id = family_id_by_cycle[cycle_key(representative["canonical_cycle"])]
        records.append(
            {
                "rule": int(representative["rule"]),
                "background": background,
                "ic": representative["ic"],
                "family_id": family_id,
                "canonical_cycle": representative["canonical_cycle"],
                "canonical_background": canonical_bg,
                "canonical_shift": canonical_shift,
                "temporal_orbit": features["temporal_orbit"],
                "temporal_orbit_canonical": features["temporal_orbit_canonical"],
                "active_count": int(features["active_count"]),
                "transition_count": int(features["transition_count"]),
                "run_lengths": tuple(features["run_lengths"]),
                "phase_shift_to_canonical": int(representative["phase_shift_to_canonical"]),
            }
        )
    return records


def descriptor_values(record: dict) -> dict[str, object]:
    word = record["background"]
    run_lengths = circular_runs(word)
    sorted_run_lengths = tuple(sorted(run_lengths))
    orbit = record["temporal_orbit"]
    orbit_canonical = record["temporal_orbit_canonical"]
    descriptors: dict[str, object] = {
        "subpatterns_len2": circular_subpattern_counts(word, 2),
        "subpatterns_len3": circular_subpattern_counts(word, 3),
        "subpatterns_len4": circular_subpattern_counts(word, 4),
        "parity": word.count("1") % 2,
        "run_lengths_circular": run_lengths,
        "run_lengths_sorted": sorted_run_lengths,
        "run_count": len(run_lengths),
        "first_one_pos": word.find("1"),
        "orbit_prefix_8": flatten_orbit_prefix(orbit, 8),
        "orbit_prefix_16": flatten_orbit_prefix(orbit, 16),
        "orbit_prefix_24": flatten_orbit_prefix(orbit, 24),
        "orbit_canonical_prefix_8": flatten_orbit_prefix(orbit_canonical, 8),
        "orbit_canonical_prefix_16": flatten_orbit_prefix(orbit_canonical, 16),
        "orbit_canonical_prefix_24": flatten_orbit_prefix(orbit_canonical, 24),
    }
    return descriptors


def analyze_descriptor(records: list[dict], descriptor_name: str, scope: str) -> dict:
    if scope == "global":
        selected = records
    elif scope == "rule_conditioned":
        selected = records
    else:
        rule = int(scope)
        selected = [record for record in records if record["rule"] == rule]

    buckets: dict[str, set[str]] = defaultdict(set)
    members: dict[str, list[str]] = defaultdict(list)
    for record in selected:
        value = descriptor_values(record)[descriptor_name]
        if scope == "rule_conditioned":
            key = json.dumps([record["rule"], value], sort_keys=True)
        else:
            key = json.dumps(value, sort_keys=True)
        buckets[key].add(record["family_id"])
        members[key].append(f"rule_{record['rule']}/{record['background']}->{record['family_id']}")

    ambiguous = {
        key: {
            "family_count": len(families),
            "families": sorted(families),
            "members": members[key],
        }
        for key, families in sorted(buckets.items())
        if len(families) > 1
    }
    return {
        "scope": scope,
        "descriptor": descriptor_name,
        "bucket_count": len(buckets),
        "pure_buckets": sum(1 for families in buckets.values() if len(families) == 1),
        "ambiguous_buckets": len(ambiguous),
        "determines_family": not ambiguous,
        "ambiguous_examples": ambiguous,
    }


def descriptor_table(records: list[dict]) -> dict:
    names = list(descriptor_values(records[0]).keys())
    return {
        scope: [analyze_descriptor(records, name, scope) for name in names]
        for scope in ("global", "rule_conditioned", "73", "109")
    }


def numeric_feature_vector(record: dict) -> tuple[list[float], list[str]]:
    word = record["background"]
    descriptors = descriptor_values(record)
    names: list[str] = []
    values: list[float] = []

    def add(name: str, value: float) -> None:
        names.append(name)
        values.append(float(value))

    add("rule", record["rule"])
    add("active_count", record["active_count"])
    add("transition_count", record["transition_count"])
    add("run_count", descriptors["run_count"])
    add("parity", descriptors["parity"])
    add("first_one_pos", descriptors["first_one_pos"])
    add("canonical_shift", record["canonical_shift"])
    add("phase_shift_to_canonical", record["phase_shift_to_canonical"])

    for length in (2, 3, 4):
        for value, count in enumerate(descriptors[f"subpatterns_len{length}"]):
            add(f"sub{length}_{format(value, f'0{length}b')}", count)

    runs = list(descriptors["run_lengths_sorted"])
    for index in range(8):
        add(f"sorted_run_{index}", runs[index] if index < len(runs) else 0)

    for k in (8, 16, 24):
        prefix = descriptors[f"orbit_prefix_{k}"]
        for index, bit in enumerate(prefix):
            add(f"orbit{k}_bit_{index}", int(bit))

    return values, names


def decision_tree(records: list[dict]) -> dict:
    try:
        from sklearn.tree import DecisionTreeClassifier, export_text
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "available": False,
            "error": str(exc),
        }

    vectors = []
    feature_names: list[str] | None = None
    targets = []
    for record in records:
        vector, names = numeric_feature_vector(record)
        if feature_names is None:
            feature_names = names
        vectors.append(vector)
        targets.append(record["family_id"])

    clf = DecisionTreeClassifier(max_depth=4, random_state=0)
    clf.fit(vectors, targets)
    accuracy = float(clf.score(vectors, targets))
    depth = int(clf.get_depth())
    importances = [
        {
            "feature": name,
            "importance": float(importance),
        }
        for name, importance in sorted(
            zip(feature_names or [], clf.feature_importances_),
            key=lambda item: (-item[1], item[0]),
        )
        if importance > 0
    ]
    tree_text = export_text(clf, feature_names=feature_names or [])
    symbolic_rule = None
    if accuracy == 1.0 and depth <= 3:
        symbolic_rule = (
            "The max-depth-4 decision tree collapses to a perfect tree with "
            f"effective depth {depth}. Its non-zero split features are "
            + ", ".join(item["feature"] for item in importances)
            + "."
        )
    return {
        "available": True,
        "accuracy": accuracy,
        "effective_depth": depth,
        "node_count": int(clf.tree_.node_count),
        "feature_importances": importances,
        "tree_text": tree_text,
        "symbolic_rule": symbolic_rule,
        "compact_descriptor_found_by_tree": accuracy == 1.0 and depth <= 3,
    }


def verdict(table: dict, tree: dict) -> str:
    exact_global = [
        row["descriptor"]
        for row in table["global"]
        if row["determines_family"]
    ]
    compact_global = [
        name
        for name in exact_global
        if name
        not in {
            "orbit_prefix_24",
            "orbit_canonical_prefix_24",
        }
    ]
    exact_rule_conditioned = [
        row["descriptor"]
        for row in table["rule_conditioned"]
        if row["determines_family"]
    ]
    compact_rule_conditioned = [
        name
        for name in exact_rule_conditioned
        if name
        not in {
            "orbit_prefix_24",
            "orbit_canonical_prefix_24",
        }
    ]
    if compact_global or compact_rule_conditioned:
        return "COMPACT_DESCRIPTOR_FOUND"
    if tree.get("compact_descriptor_found_by_tree"):
        return "COMPACT_DESCRIPTOR_FOUND"
    return "NO_COMPACT_DESCRIPTOR"


def render_report(result: dict) -> str:
    lines = [
        "# Fase 31: Compact Descriptor Search for T=15 Shape Families",
        "",
        "## Question",
        "",
        "Fase 30 showed that the 20 minimal T=15 representatives collapse into",
        "13 phase-rotated defect-cycle shape families. Fase 31 asks whether a",
        "short descriptor of the circular length-8 background predicts that",
        "family without using the full temporal orbit as identity.",
        "",
        "## Descriptor separation",
        "",
        "| scope | descriptor | buckets | ambiguous | determines family |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for scope in ("global", "rule_conditioned", "73", "109"):
        for row in result["descriptor_tests"][scope]:
            lines.append(
                f"| {scope} | `{row['descriptor']}` | {row['bucket_count']} | "
                f"{row['ambiguous_buckets']} | {row['determines_family']} |"
            )

    exact_global = [
        row["descriptor"]
        for row in result["descriptor_tests"]["global"]
        if row["determines_family"]
    ]
    exact_rule_conditioned = [
        row["descriptor"]
        for row in result["descriptor_tests"]["rule_conditioned"]
        if row["determines_family"]
    ]
    lines.extend(
        [
            "",
            "## Decision tree",
            "",
        ]
    )
    tree = result["decision_tree"]
    if not tree.get("available"):
        lines.append(f"`sklearn` unavailable: {tree.get('error')}")
    else:
        lines.extend(
            [
                f"- Training accuracy on the 20 representatives: `{tree['accuracy']:.3f}`.",
                f"- Effective depth: `{tree['effective_depth']}`.",
                f"- Node count: `{tree['node_count']}`.",
                "",
                "Non-zero feature importances:",
                "",
            ]
        )
        for item in tree["feature_importances"]:
            lines.append(f"- `{item['feature']}`: `{item['importance']:.3f}`")
        lines.extend(
            [
                "",
                "Tree:",
                "",
                "```text",
                tree["tree_text"].rstrip(),
                "```",
            ]
        )
        if tree["symbolic_rule"]:
            lines.extend(["", "Natural-language extraction:", "", tree["symbolic_rule"]])

    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"**Status:** `{result['verdict']}`.",
            "",
        ]
    )
    if exact_global:
        lines.append(
            "The following background-only descriptors determine the global family: "
            + ", ".join(f"`{name}`" for name in exact_global)
            + "."
        )
    else:
        lines.append("No tested background-only descriptor determines the global family.")

    if exact_rule_conditioned:
        lines.append(
            "Conditioned on the ECA rule, the following descriptors determine the "
            "global family: "
            + ", ".join(f"`rule + {name}`" for name in exact_rule_conditioned)
            + "."
        )
        if "subpatterns_len4" in exact_rule_conditioned:
            lines.append(
                "The shortest non-orbit candidate is therefore "
                "`rule + subpatterns_len4`: the circular multiset of length-4 "
                "background words, with the rule identity supplied."
            )
    else:
        lines.append("No tested rule-conditioned descriptor determines the global family.")

    if result["verdict"] == "COMPACT_DESCRIPTOR_FOUND":
        lines.append(
            "A compact rule-conditioned descriptor candidate exists. It should be"
            " tested on a larger representative set before being treated as a"
            " symbolic law."
        )
    else:
        lines.append(
            "No compact background-only descriptor was found among circular"
            " subpattern multisets, parity, circular runs, first-one position,"
            " or short temporal orbit prefixes. The current best exact"
            " background-only descriptor remains the full temporal background"
            " orbit, which is not yet a compact symbolic law."
        )

    lines.extend(
        [
            "",
            "## Falsifiable implication",
            "",
            "A global background-only derivation based only on length-2..4 circular",
            "subpattern counts, parity, run lengths, or short orbit prefixes is",
            "falsified if it predicts one family per descriptor bucket, because",
            "the ambiguous global buckets listed in `compact_descriptor_results.json`",
            "contain multiple shape families. A rule-conditioned derivation based",
            "on the length-4 circular subpattern multiset remains viable and is",
            "the next compact symbolic target to test.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    records = load_records()
    table = descriptor_table(records)
    tree = decision_tree(records)
    result = {
        "status": "OK",
        "record_count": len(records),
        "family_count": len({record["family_id"] for record in records}),
        "records": records,
        "descriptor_tests": table,
        "decision_tree": tree,
    }
    result["verdict"] = verdict(table, tree)
    RESULTS_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_MD.write_text(render_report(result), encoding="utf-8")
    print(f"wrote {RESULTS_JSON}")
    print(f"wrote {REPORT_MD}")
    print(f"verdict={result['verdict']}")


if __name__ == "__main__":
    main()
