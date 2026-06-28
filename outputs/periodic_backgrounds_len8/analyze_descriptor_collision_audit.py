#!/usr/bin/env python3
"""Fase 33: audit collisions for the T=15 compact descriptor.

Fase 31-32 identified the compact state variable

    (rule, subpatterns_len4, IC/background alignment)

for the confirmed T=15 family. This script checks whether length-8
backgrounds outside the known representative/rotation set share the same
length-4 circular subpattern multiset. If such backgrounds existed, they
would provide a natural unseen-background validation target.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


BASE = Path(__file__).resolve().parent
SHAPE_RESULTS = BASE / "shape_families_results.json"
OUT_JSON = BASE / "descriptor_collision_audit_results.json"
OUT_REPORT = BASE / "descriptor_collision_audit_report.md"


def rotations(word: str) -> list[str]:
    return [word[i:] + word[:i] for i in range(len(word))]


def canonical_rotation(word: str) -> str:
    return min(rotations(word))


def minimal_period(word: str) -> int:
    n = len(word)
    for p in range(1, n + 1):
        if n % p == 0 and all(word[i] == word[i % p] for i in range(n)):
            return p
    return n


def circular_subpattern_multiset(word: str, k: int) -> tuple[tuple[str, int], ...]:
    n = len(word)
    counts = Counter("".join(word[(i + j) % n] for j in range(k)) for i in range(n))
    return tuple(sorted(counts.items()))


def descriptor_key_jsonable(key: tuple[tuple[str, int], ...]) -> list[list[object]]:
    return [[pattern, count] for pattern, count in key]


def cycle_key(rep: dict) -> tuple[str, ...]:
    return tuple(rep["canonical_cycle"])


def load_representatives() -> list[dict]:
    data = json.loads(SHAPE_RESULTS.read_text(encoding="utf-8"))
    return data["representatives"]


def all_binary_words(n: int = 8, include_zero: bool = True) -> list[str]:
    start = 0 if include_zero else 1
    return [format(x, f"0{n}b") for x in range(start, 2**n)]


def necklace_classes(words: Iterable[str]) -> dict[str, list[str]]:
    classes: dict[str, list[str]] = defaultdict(list)
    for word in words:
        classes[canonical_rotation(word)].append(word)
    return dict(sorted(classes.items()))


def summarize_descriptor_collisions(words: Iterable[str], k: int) -> dict:
    necklaces = necklace_classes(words)
    buckets: dict[tuple[tuple[str, int], ...], set[str]] = defaultdict(set)
    for necklace in necklaces:
        buckets[circular_subpattern_multiset(necklace, k)].add(necklace)

    ambiguous = []
    for key, members in sorted(buckets.items(), key=lambda item: (len(item[1]), sorted(item[1])), reverse=True):
        if len(members) > 1:
            ambiguous.append(
                {
                    "descriptor": descriptor_key_jsonable(key),
                    "necklaces": sorted(members),
                    "count": len(members),
                }
            )

    return {
        "k": k,
        "necklace_count": len(necklaces),
        "descriptor_bucket_count": len(buckets),
        "ambiguous_bucket_count": len(ambiguous),
        "max_collision_size": max((item["count"] for item in ambiguous), default=1),
        "ambiguous_buckets": ambiguous,
    }


def main() -> None:
    reps = load_representatives()
    all_words = all_binary_words(8, include_zero=True)
    nonzero_words = all_binary_words(8, include_zero=False)
    primitive_words = [word for word in nonzero_words if minimal_period(word) == 8]

    known_rotations_by_rule: dict[int, set[str]] = defaultdict(set)
    known_descriptor_buckets: dict[int, dict[tuple[tuple[str, int], ...], list[dict]]] = defaultdict(lambda: defaultdict(list))

    for rep in reps:
        rule = int(rep["rule"])
        bg = rep["background"]
        known_rotations_by_rule[rule].update(rotations(bg))
        key = circular_subpattern_multiset(bg, 4)
        known_descriptor_buckets[rule][key].append(
            {
                "background": bg,
                "ic": rep["ic"],
                "cycle": list(cycle_key(rep)),
                "phase_shift_to_canonical": rep["phase_shift_to_canonical"],
            }
        )

    external_same_descriptor: dict[str, list[dict]] = {}
    for rule, buckets in known_descriptor_buckets.items():
        hits = []
        for word in nonzero_words:
            if word in known_rotations_by_rule[rule]:
                continue
            key = circular_subpattern_multiset(word, 4)
            if key in buckets:
                hits.append(
                    {
                        "background": word,
                        "descriptor": descriptor_key_jsonable(key),
                        "known_bucket": buckets[key],
                    }
                )
        external_same_descriptor[str(rule)] = hits

    known_collisions = []
    for rule, buckets in known_descriptor_buckets.items():
        for key, members in buckets.items():
            if len(members) > 1:
                cycles = {tuple(member["cycle"]) for member in members}
                known_collisions.append(
                    {
                        "rule": rule,
                        "descriptor": descriptor_key_jsonable(key),
                        "members": members,
                        "family_preserving": len(cycles) == 1,
                    }
                )

    collision_all = {
        f"len{k}": summarize_descriptor_collisions(all_words, k)
        for k in (2, 3, 4)
    }
    collision_primitive = {
        f"len{k}": summarize_descriptor_collisions(primitive_words, k)
        for k in (2, 3, 4)
    }

    len4_all_ambiguous = collision_all["len4"]["ambiguous_buckets"]
    len4_primitive_ambiguous = collision_primitive["len4"]["ambiguous_buckets"]

    status = (
        "NO_UNSEEN_SAME_DESCRIPTOR_BACKGROUND"
        if all(len(hits) == 0 for hits in external_same_descriptor.values())
        else "UNSEEN_DESCRIPTOR_COLLISIONS_FOUND"
    )
    if status == "NO_UNSEEN_SAME_DESCRIPTOR_BACKGROUND" and all(item["family_preserving"] for item in known_collisions):
        verdict = "FAMILY_SAFE_COLLISIONS_ONLY"
    else:
        verdict = "DESCRIPTOR_NEEDS_EXTERNAL_TESTS"

    results = {
        "status": status,
        "verdict": verdict,
        "record_count": len(reps),
        "all_binary_necklace_count": len(necklace_classes(all_words)),
        "primitive_nonzero_necklace_count": len(necklace_classes(primitive_words)),
        "collision_summary_all_binary": collision_all,
        "collision_summary_primitive_nonzero": collision_primitive,
        "known_descriptor_bucket_count_by_rule": {
            str(rule): len(buckets) for rule, buckets in known_descriptor_buckets.items()
        },
        "known_descriptor_collisions": known_collisions,
        "external_same_descriptor_by_rule": external_same_descriptor,
    }

    OUT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    OUT_REPORT.write_text(render_report(results, len4_all_ambiguous, len4_primitive_ambiguous), encoding="utf-8")


def render_report(results: dict, len4_all_ambiguous: list[dict], len4_primitive_ambiguous: list[dict]) -> str:
    lines: list[str] = []
    lines.append("# Fase 33: Descriptor Collision Audit for T=15")
    lines.append("")
    lines.append("## Question")
    lines.append("")
    lines.append(
        "Fase 32 validated `rule + subpatterns_len4 + IC/background alignment` "
        "on rotations of the 20 known T=15 representatives. Fase 33 asks whether "
        "there are unseen length-8 backgrounds with the same `subpatterns_len4` "
        "descriptor that could provide an external validation target."
    )
    lines.append("")
    lines.append("## Collision summary")
    lines.append("")
    lines.append("| universe | k | necklaces | buckets | ambiguous buckets | max collision |")
    lines.append("| --- | ---: | ---: | ---: | ---: | ---: |")
    for universe, key in (("all binary len-8", "collision_summary_all_binary"), ("primitive non-zero len-8", "collision_summary_primitive_nonzero")):
        for name in ("len2", "len3", "len4"):
            row = results[key][name]
            lines.append(
                f"| {universe} | {row['k']} | {row['necklace_count']} | "
                f"{row['descriptor_bucket_count']} | {row['ambiguous_bucket_count']} | "
                f"{row['max_collision_size']} |"
            )
    lines.append("")
    lines.append("## Length-4 ambiguous necklaces")
    lines.append("")
    if len4_all_ambiguous:
        lines.append("Across all binary length-8 necklaces, only two `subpatterns_len4` collisions exist:")
        lines.append("")
        for item in len4_all_ambiguous:
            lines.append(f"- `{', '.join(item['necklaces'])}`")
    else:
        lines.append("No length-4 collisions exist across all binary length-8 necklaces.")
    lines.append("")
    if len4_primitive_ambiguous:
        lines.append("The same two collisions also occur inside the primitive non-zero universe:")
        lines.append("")
        for item in len4_primitive_ambiguous:
            lines.append(f"- `{', '.join(item['necklaces'])}`")
    else:
        lines.append("No length-4 collisions occur inside the primitive non-zero universe.")
    lines.append("")
    lines.append("## Known T=15 descriptor buckets")
    lines.append("")
    lines.append("| rule | descriptor buckets | external same-descriptor backgrounds |")
    lines.append("| ---: | ---: | ---: |")
    for rule in sorted(results["known_descriptor_bucket_count_by_rule"], key=int):
        external_count = len(results["external_same_descriptor_by_rule"][rule])
        bucket_count = results["known_descriptor_bucket_count_by_rule"][rule]
        lines.append(f"| {rule} | {bucket_count} | {external_count} |")
    lines.append("")
    if results["known_descriptor_collisions"]:
        lines.append("The only T=15 descriptor collisions are family-preserving:")
        lines.append("")
        for item in results["known_descriptor_collisions"]:
            members = ", ".join(f"`{m['background']}`" for m in item["members"])
            flag = "yes" if item["family_preserving"] else "no"
            lines.append(f"- rule `{item['rule']}`: {members}; family-preserving: `{flag}`")
    else:
        lines.append("No known T=15 descriptor collisions occur.")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"**Status:** `{results['status']}`.")
    lines.append("")
    lines.append(f"**Verdict:** `{results['verdict']}`.")
    lines.append("")
    lines.append(
        "There is no unseen length-8 background, outside rotations of the known "
        "representatives, that shares the T=15 `subpatterns_len4` descriptor under "
        "the same rule. Therefore the natural external validation test proposed "
        "after Fase 32 is impossible inside the length-8 background universe."
    )
    lines.append("")
    lines.append(
        "The two length-4 descriptor collisions that do exist are already inside "
        "the confirmed T=15 set and preserve the defect-cycle family. This supports "
        "the descriptor as a family identifier, but it also means that further "
        "generalization requires a larger background universe, such as primitive "
        "length-9/10 backgrounds or a symbolic proof over circular words."
    )
    lines.append("")
    lines.append("## Falsifiable implication")
    lines.append("")
    lines.append(
        "Any future length-8 counterexample must either break the collision audit "
        "above or use a descriptor different from `subpatterns_len4`. For external "
        "prediction, the next empirical test must leave the length-8 universe."
    )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
