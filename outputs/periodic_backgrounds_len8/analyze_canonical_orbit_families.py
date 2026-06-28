#!/usr/bin/env python3
"""Fase 37: canonical background orbit vs T=15 shape families.

Fase 36 explained the F00 table identity by convergence to the same spatially
canonical period-3 background orbit. Fase 37 checks whether that background
orbit alone generalizes to all 20 minimal T=15 representatives.

This script tests whether every shape family corresponds exactly to one
rule-conditioned canonical period-3 background orbit. It does not yet encode
the IC/background alignment variable.
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
SHAPE_RESULTS = OUT_DIR / "shape_families_results.json"
RESULTS_JSON = OUT_DIR / "canonical_orbit_family_results.json"
REPORT_MD = OUT_DIR / "canonical_orbit_family_report.md"


def stable_hash(payload) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def rotations(word: str) -> list[str]:
    return [word[i:] + word[:i] for i in range(len(word))]


def canonical_rotation(word: str) -> str:
    return min(rotations(word))


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
            canonical_cycle_set = sorted({canonical_rotation(state) for state in cycle})
            canonical_cycle_sequence = [canonical_rotation(state) for state in cycle]
            return {
                "preperiod": preperiod,
                "period": len(cycle),
                "cycle": cycle,
                "canonical_cycle_sequence": canonical_cycle_sequence,
                "canonical_cycle_set": canonical_cycle_set,
                "canonical_cycle_set_hash": stable_hash(canonical_cycle_set),
                "canonical_cycle_sequence_hash": stable_hash(canonical_cycle_sequence),
            }
        seen[current] = len(states)
        states.append(current)


def load_family_mapping() -> list[dict]:
    payload = json.loads(SHAPE_RESULTS.read_text(encoding="utf-8"))
    rows = []
    for index, cluster in enumerate(payload["global"]["clusters"]):
        family_id = f"F{index:02d}"
        for member in cluster["members"]:
            rule = int(member["rule"])
            background = member["background"]
            orbit = temporal_orbit(background, rule)
            rows.append(
                {
                    "family_id": family_id,
                    "family_size": cluster["size"],
                    "rule": rule,
                    "background": background,
                    "ic": member["ic"],
                    "phase_shift_to_canonical": member["phase_shift_to_canonical"],
                    "temporal_orbit_canonical_from_fase30": member["temporal_orbit_canonical"],
                    "orbit": orbit,
                    "rule_orbit_key": f"{rule}:{orbit['canonical_cycle_set_hash']}",
                }
            )
    return sorted(rows, key=lambda item: (item["family_id"], item["rule"], item["background"]))


def analyze(rows: list[dict]) -> dict:
    by_family: dict[str, list[dict]] = defaultdict(list)
    by_rule_orbit: dict[str, list[dict]] = defaultdict(list)
    by_orbit_only: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_family[row["family_id"]].append(row)
        by_rule_orbit[row["rule_orbit_key"]].append(row)
        by_orbit_only[row["orbit"]["canonical_cycle_set_hash"]].append(row)

    family_rows = []
    for family_id, items in sorted(by_family.items()):
        keys = sorted({item["rule_orbit_key"] for item in items})
        orbit_sets = sorted({tuple(item["orbit"]["canonical_cycle_set"]) for item in items})
        family_rows.append(
            {
                "family_id": family_id,
                "members": len(items),
                "rules": sorted({item["rule"] for item in items}),
                "rule_orbit_key_count": len(keys),
                "rule_orbit_keys": keys,
                "canonical_orbit_set_count": len(orbit_sets),
                "canonical_orbit_sets": [list(item) for item in orbit_sets],
                "one_rule_orbit": len(keys) == 1,
                "backgrounds": [item["background"] for item in items],
            }
        )

    orbit_rows = []
    for key, items in sorted(by_rule_orbit.items()):
        families = sorted({item["family_id"] for item in items})
        orbit_rows.append(
            {
                "rule_orbit_key": key,
                "members": len(items),
                "families": families,
                "family_count": len(families),
                "backgrounds": [item["background"] for item in items],
                "rules": sorted({item["rule"] for item in items}),
                "one_family": len(families) == 1,
            }
        )

    orbit_only_rows = []
    for key, items in sorted(by_orbit_only.items()):
        orbit_only_rows.append(
            {
                "orbit_hash": key,
                "members": len(items),
                "rules": sorted({item["rule"] for item in items}),
                "families": sorted({item["family_id"] for item in items}),
                "family_count": len({item["family_id"] for item in items}),
                "backgrounds": [item["background"] for item in items],
            }
        )

    all_family_one_orbit = all(row["one_rule_orbit"] for row in family_rows)
    all_orbit_one_family = all(row["one_family"] for row in orbit_rows)
    if all_family_one_orbit and all_orbit_one_family:
        status = "ONE_FAMILY_PER_RULE_CANONICAL_ORBIT"
    elif all_orbit_one_family:
        status = "ORBIT_REFINES_FAMILY"
    else:
        status = "CANONICAL_ORBIT_NOT_ENOUGH"

    return {
        "status": status,
        "family_rows": family_rows,
        "orbit_rows": orbit_rows,
        "orbit_only_rows": orbit_only_rows,
        "all_family_one_orbit": all_family_one_orbit,
        "all_orbit_one_family": all_orbit_one_family,
        "family_count": len(by_family),
        "rule_orbit_count": len(by_rule_orbit),
        "orbit_only_count": len(by_orbit_only),
    }


def main() -> None:
    rows = load_family_mapping()
    analysis = analyze(rows)
    payload = {
        "status": analysis["status"],
        "record_count": len(rows),
        "rows": rows,
        "analysis": analysis,
    }
    RESULTS_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(render_report(payload), encoding="utf-8")


def render_report(payload: dict) -> str:
    analysis = payload["analysis"]
    lines = [
        "# Fase 37: Canonical Background Orbit vs T=15 Families",
        "",
        "## Question",
        "",
        "Fase 36 explained the F00 table identity by convergence to the same",
        "spatially canonical period-3 background orbit. Fase 37 tests whether this",
        "generalizes to all 20 minimal T=15 representatives.",
        "",
        "Candidate background invariant:",
        "",
        "```text",
        "(rule, canonical_period3_orbit)",
        "```",
        "",
        "## Family -> rule/orbit mapping",
        "",
        "| family | members | rules | rule/orbit keys | one rule/orbit | backgrounds |",
        "| --- | ---: | --- | ---: | --- | --- |",
    ]
    for row in analysis["family_rows"]:
        lines.append(
            f"| `{row['family_id']}` | {row['members']} | "
            f"`{', '.join(str(rule) for rule in row['rules'])}` | "
            f"{row['rule_orbit_key_count']} | `{row['one_rule_orbit']}` | "
            f"{', '.join(f'`{bg}`' for bg in row['backgrounds'])} |"
        )

    lines += [
        "",
        "## Rule/orbit -> family mapping",
        "",
        "| rule/orbit key | members | families | one family | backgrounds |",
        "| --- | ---: | --- | --- | --- |",
    ]
    for row in analysis["orbit_rows"]:
        lines.append(
            f"| `{row['rule_orbit_key']}` | {row['members']} | "
            f"`{', '.join(row['families'])}` | `{row['one_family']}` | "
            f"{', '.join(f'`{bg}`' for bg in row['backgrounds'])} |"
        )

    split_families = [row for row in analysis["family_rows"] if not row["one_rule_orbit"]]
    ambiguous_orbits = [row for row in analysis["orbit_rows"] if not row["one_family"]]

    lines += [
        "",
        "## Summary",
        "",
        f"- Records: `{payload['record_count']}`.",
        f"- Shape families: `{analysis['family_count']}`.",
        f"- Rule-conditioned canonical orbit keys: `{analysis['rule_orbit_count']}`.",
        f"- Canonical orbit sets ignoring rule: `{analysis['orbit_only_count']}`.",
        f"- Families with more than one rule/orbit key: `{len(split_families)}`.",
        f"- Rule/orbit keys mapping to more than one family: `{len(ambiguous_orbits)}`.",
        "",
        "## Verdict",
        "",
        f"**Status:** `{analysis['status']}`.",
        "",
    ]
    if analysis["status"] == "ONE_FAMILY_PER_RULE_CANONICAL_ORBIT":
        lines.append(
            "Every shape family corresponds to exactly one rule-conditioned canonical "
            "period-3 background orbit, and every such orbit maps back to exactly "
            "one family. The canonical background orbit is therefore an exact "
            "family identifier for the 20 minimal representatives."
        )
    elif analysis["status"] == "ORBIT_REFINES_FAMILY":
        lines.append(
            "Every rule-conditioned canonical orbit maps to one family, but at "
            "least one shape family contains multiple distinct orbits. The orbit "
            "is sufficient to predict family but not minimal."
        )
    else:
        lines.append(
            "The rule-conditioned canonical background orbit is not sufficient "
            "by itself. It collapses the 20 representatives to two keys, one for "
            "`rule_73` and one for `rule_109`, while those keys map to many shape "
            "families. Therefore the missing information is not the asymptotic "
            "background orbit but the IC/background alignment and local embedding "
            "of the defect inside that orbit."
        )

    if split_families:
        lines += [
            "",
            "Families split by rule/orbit key:",
        ]
        for row in split_families:
            lines.append(f"- `{row['family_id']}` -> {', '.join(row['rule_orbit_keys'])}")
    if ambiguous_orbits:
        lines += [
            "",
            "Ambiguous rule/orbit keys:",
        ]
        for row in ambiguous_orbits:
            lines.append(f"- `{row['rule_orbit_key']}` -> {', '.join(row['families'])}")

    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
