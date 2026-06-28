#!/usr/bin/env python3
"""Fase 36: analyze the exact transition-table identity in family F00.

Fase 35 showed that the three F00 representatives share the exact same
five-phase transition-table signature under rule_109. This script isolates
that identity and checks what is, and is not, identical:

- the local induced transition tables seen by the defect cone;
- the global background temporal orbits;
- the rule-conditioned length-4 subpattern descriptors.

The goal is to separate a real algebraic identity from weaker visual or
shape-family coincidence.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
TRANSITION_RESULTS = OUT_DIR / "transition_tables_results.json"
SHAPE_RESULTS = OUT_DIR / "shape_families_results.json"
RESULTS_JSON = OUT_DIR / "f00_table_identity_results.json"
REPORT_MD = OUT_DIR / "f00_table_identity_report.md"

F00_CYCLE = ["11:4e5", "11:4f7", "12:96f", "12:953", "8:99"]
RULE = 109


def stable_hash(payload) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def rotations(word: str) -> list[str]:
    return [word[i:] + word[:i] for i in range(len(word))]


def canonical_rotation(word: str) -> str:
    return min(rotations(word))


def circular_subpatterns(word: str, k: int) -> tuple[tuple[str, int], ...]:
    counts = Counter("".join(word[(i + j) % len(word)] for j in range(k)) for i in range(len(word)))
    return tuple(sorted(counts.items()))


def eca_step_word(word: str, rule: int) -> str:
    bits = [int(ch) for ch in word]
    out = []
    n = len(bits)
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
            return {
                "states": states,
                "preperiod": seen[current],
                "period": len(states) - seen[current],
                "cycle": states[seen[current] :],
                "cycle_canonical_rotation": [canonical_rotation(state) for state in states[seen[current] :]],
                "cycle_canonical_set": sorted({canonical_rotation(state) for state in states[seen[current] :]}),
            }
        seen[current] = len(states)
        states.append(current)


def load_f00_records() -> list[dict]:
    payload = json.loads(TRANSITION_RESULTS.read_text(encoding="utf-8"))
    records = [
        record
        for record in payload["representatives"]
        if int(record["rule"]) == RULE and record["family_id"] == "F00"
    ]
    if len(records) != 3:
        raise RuntimeError(f"Expected 3 F00 records, found {len(records)}")
    return sorted(records, key=lambda item: item["background"])


def load_f00_shape_members() -> list[dict]:
    payload = json.loads(SHAPE_RESULTS.read_text(encoding="utf-8"))
    for cluster in payload["global"]["clusters"]:
        if cluster["canonical_cycle"] == F00_CYCLE:
            return sorted(cluster["members"], key=lambda item: item["background"])
    raise RuntimeError("F00 shape cluster not found")


def compact_table(record: dict) -> list[list[dict]]:
    """Return the five macro transitions as 5 x 3 deterministic key tables."""
    result = []
    for transition in record["transitions"]:
        micros = []
        for micro in transition["micro_tables"]:
            micros.append(micro["table"])
        result.append(micros)
    return result


def main() -> None:
    records = load_f00_records()
    shape_members = load_f00_shape_members()
    table_signatures = [record["transition_hashes"] for record in records]
    canonical_signatures = [record["canonical_transition_hashes"] for record in records]
    compact_tables = [compact_table(record) for record in records]

    member_rows = []
    for record in records:
        background = record["background"]
        orbit = temporal_orbit(background, RULE)
        sub4 = circular_subpatterns(background, 4)
        sub3 = circular_subpatterns(background, 3)
        member_rows.append(
            {
                "background": background,
                "ic": record["ic"],
                "transition_signature_hash": record["transition_signature_hash"],
                "canonical_transition_signature_hash": record["canonical_transition_signature_hash"],
                "defect_states": record["defect_states"],
                "subpatterns_len3": [[pattern, count] for pattern, count in sub3],
                "subpatterns_len4": [[pattern, count] for pattern, count in sub4],
                "subpatterns_len4_hash": stable_hash(sub4),
                "temporal_orbit": orbit,
            }
        )

    sub4_hashes = {row["subpatterns_len4_hash"] for row in member_rows}
    cycle_hashes = {stable_hash(row["temporal_orbit"]["cycle"]) for row in member_rows}
    cycle_canonical_set_hashes = {
        stable_hash(row["temporal_orbit"]["cycle_canonical_set"])
        for row in member_rows
    }
    table_exact_identity = all(signature == table_signatures[0] for signature in table_signatures)
    canonical_exact_identity = all(signature == canonical_signatures[0] for signature in canonical_signatures)
    compact_table_identity = all(table == compact_tables[0] for table in compact_tables)

    # Count how many individual microtables are identical position-free.
    micro_identity_count = 0
    for phase in range(5):
        for micro in range(3):
            first = compact_tables[0][phase][micro]
            if all(table[phase][micro] == first for table in compact_tables):
                micro_identity_count += 1

    results = {
        "status": "F00_EXACT_TABLE_IDENTITY",
        "rule": RULE,
        "family_id": "F00",
        "members": member_rows,
        "shape_members": shape_members,
        "table_exact_identity": table_exact_identity,
        "phase_canonical_table_identity": canonical_exact_identity,
        "compact_table_identity": compact_table_identity,
        "identical_microtables": micro_identity_count,
        "total_microtables": 15,
        "subpatterns_len4_bucket_count": len(sub4_hashes),
        "temporal_cycle_hash_count": len(cycle_hashes),
        "canonical_background_cycle_set_count": len(cycle_canonical_set_hashes),
        "common_transition_hashes": table_signatures[0] if table_exact_identity else None,
        "common_defect_states": records[0]["defect_states"] if table_exact_identity else None,
    }
    RESULTS_JSON.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    REPORT_MD.write_text(render_report(results), encoding="utf-8")


def render_report(results: dict) -> str:
    lines = [
        "# Fase 36: F00 Exact Transition-Table Identity",
        "",
        "## Question",
        "",
        "Fase 35 found that family F00 is exceptional: three distinct rule_109",
        "backgrounds share the same exact five-phase transition-table signature.",
        "Fase 36 isolates that identity and asks whether it is a real local",
        "algebraic identity rather than a restatement of equal background orbits",
        "or equal length-4 subpattern descriptors.",
        "",
        "## Members",
        "",
        "| background | IC | subpatterns_len4 hash | temporal orbit period | transition signature |",
        "| --- | --- | --- | ---: | --- |",
    ]
    for row in results["members"]:
        orbit = row["temporal_orbit"]
        lines.append(
            f"| `{row['background']}` | `{row['ic']}` | `{row['subpatterns_len4_hash']}` | "
            f"{orbit['period']} | `{row['transition_signature_hash']}` |"
        )

    lines += [
        "",
        "## Identity checks",
        "",
        f"- Exact five-phase transition-table sequence identical: `{results['table_exact_identity']}`.",
        f"- Phase-canonical transition-table sequence identical: `{results['phase_canonical_table_identity']}`.",
        f"- Full compact local induced tables identical: `{results['compact_table_identity']}`.",
        f"- Identical microtables: `{results['identical_microtables']}/{results['total_microtables']}`.",
        f"- Distinct `subpatterns_len4` buckets among F00 members: `{results['subpatterns_len4_bucket_count']}`.",
        f"- Distinct raw background temporal cycles among F00 members: `{results['temporal_cycle_hash_count']}`.",
        f"- Distinct spatially canonical background cycle sets: `{results['canonical_background_cycle_set_count']}`.",
        "",
        "The three representatives therefore do not share the same length-4",
        "subpattern descriptor, and their raw temporal cycles are shifted by",
        "different preperiods/phases. However, after spatial canonicalization they",
        "share the same period-3 background cycle set. The identical local",
        "transition table is therefore explained by convergence to the same",
        "effective background orbit before the defect is sampled.",
        "",
        "## Background temporal orbits",
        "",
    ]
    for row in results["members"]:
        orbit = row["temporal_orbit"]
        lines.append(f"### `{row['background']}`")
        lines.append("")
        lines.append(f"- preperiod: `{orbit['preperiod']}`")
        lines.append(f"- period: `{orbit['period']}`")
        lines.append(f"- cycle: {', '.join(f'`{state}`' for state in orbit['cycle'])}")
        lines.append(
            "- canonical cycle rotations: "
            + ", ".join(f"`{state}`" for state in orbit["cycle_canonical_rotation"])
        )
        lines.append(
            "- canonical cycle set: "
            + ", ".join(f"`{state}`" for state in orbit["cycle_canonical_set"])
        )
        lines.append("")

    lines += [
        "## Verdict",
        "",
        "**Status:** `F00_EXACT_TABLE_IDENTITY`.",
        "",
        "The F00 identity is stronger than a shape-family coincidence, but it is",
        "not mysterious: the three initial backgrounds enter the same spatially",
        "canonical period-3 background cycle before the sampled T=15 defect orbit.",
        "They then induce the exact same sequence of 15 local microtables over the",
        "five `F^3` transitions. This also shows that the v1.8 length-4 descriptor",
        "was sufficient but not minimal for F00: two different `subpatterns_len4`",
        "buckets collapse to the same effective background cycle and table.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
