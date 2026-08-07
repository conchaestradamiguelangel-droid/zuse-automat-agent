#!/usr/bin/env python3
"""Fase 93: deduplicate Fase-91 inputs by exact physical initial state."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parent.parent
BASE_PATH = OUT_DIR / "sweep_periodic_background_oscillators.py"
SOURCE_PATH = OUT_DIR / "phase90_long_period_attractor_results.json"
RESULTS_PATH = OUT_DIR / "phase91_physical_initial_state_results.json"
REPORT_PATH = OUT_DIR / "phase91_physical_initial_state_report.md"

EXPECTED_SOURCE_SHA256 = "a2ce55599fde30ed425dead579869399c260ba4752d551555933d33a16ff178a"
EXPECTED_INPUT_COUNT = 3296
EXPECTED_PHYSICAL_CLASS_COUNT = 192
WIDTH = 256


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def state_bits(state: Iterable[int]) -> int:
    value = 0
    for position in state:
        value |= 1 << int(position)
    return value


def absolute_background_hex(state: Iterable[int]) -> str:
    return f"{state_bits(state):0{WIDTH // 4}x}"


def complement_background_hex(value: str) -> str:
    return f"{(int(value, 16) ^ ((1 << WIDTH) - 1)):0{WIDTH // 4}x}"


def manual_initial_diff(
    *, word: str, word_len: int, background_state: tuple[int, ...]
) -> tuple[int, ...]:
    if len(word) != word_len:
        raise ValueError("word_len does not match the frozen word")
    background = set(background_state)
    start = WIDTH // 2 - word_len // 2
    diff = []
    for offset, bit in enumerate(word):
        position = start + offset
        desired = int(bit)
        background_bit = int(position in background)
        if desired ^ background_bit:
            diff.append(position)
    return tuple(diff)


def strict_initial_payload(
    *, rule: int, background_state: tuple[int, ...], initial_diff: tuple[int, ...]
) -> dict[str, Any]:
    # Absolute cell coordinates are intentionally preserved. No rotation,
    # translation, reflection, or temporal canonicalization is permitted here.
    return {
        "width": WIDTH,
        "rule": int(rule),
        "background_t0_absolute": absolute_background_hex(background_state),
        "initial_diff_absolute": tuple(int(position) for position in initial_diff),
        "position_policy": "ABSOLUTE_FIXED_GRID_NO_CANONICALIZATION",
    }


def conjugacy_initial_payload(
    *, rule: int, background_state: tuple[int, ...], initial_diff: tuple[int, ...]
) -> dict[str, Any]:
    if rule not in {73, 109}:
        raise ValueError("The conjugacy quotient is defined only for rules 73/109")
    background_hex = absolute_background_hex(background_state)
    if rule == 109:
        background_hex = complement_background_hex(background_hex)
    return {
        "width": WIDTH,
        "normalized_rule": 73,
        "background_t0_absolute": background_hex,
        "initial_diff_absolute": tuple(int(position) for position in initial_diff),
        "position_policy": "ABSOLUTE_FIXED_GRID_CONJUGACY_QUOTIENT",
    }


def derive_initial_state(row: dict[str, Any], base) -> dict[str, Any]:
    background_state = base.background_state(row["background"])
    base_diff = base.initial_diff(
        int(row["word"], 2), int(row["word_len"]), background_state
    )
    manual_diff = manual_initial_diff(
        word=row["word"],
        word_len=int(row["word_len"]),
        background_state=background_state,
    )
    if base_diff != manual_diff:
        raise RuntimeError(
            "Frozen absolute IC placement differs from WIDTH//2-word_len//2"
        )
    strict = strict_initial_payload(
        rule=int(row["rule"]),
        background_state=background_state,
        initial_diff=manual_diff,
    )
    conjugacy = conjugacy_initial_payload(
        rule=int(row["rule"]),
        background_state=background_state,
        initial_diff=manual_diff,
    )
    return {
        "strict_sha256": sha256_json(strict),
        "conjugacy_sha256": sha256_json(conjugacy),
        "background_t0_absolute": strict["background_t0_absolute"],
        "initial_diff_absolute": list(manual_diff),
    }


def validate_determinism(groups: dict[str, list[dict[str, Any]]]) -> None:
    for digest, rows in groups.items():
        final_classes = {row["physical_class_sha256"] for row in rows}
        if len(final_classes) != 1:
            raise RuntimeError(
                "INITIAL_STATE_DETERMINISM_VIOLATION: "
                f"{digest} maps to {sorted(final_classes)}"
            )


def distribution(values: Iterable[Any]) -> dict[str, int]:
    return {
        str(key): value
        for key, value in sorted(Counter(values).items(), key=lambda item: str(item[0]))
    }


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    with temporary.open("r+b") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def build_class_rows(
    source_rows: list[dict[str, Any]],
    initial_groups: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    raw_by_class: dict[str, list[dict[str, Any]]] = defaultdict(list)
    unique_by_class: dict[str, list[tuple[str, list[dict[str, Any]]]]] = defaultdict(list)
    for row in source_rows:
        raw_by_class[row["physical_class_sha256"]].append(row)
    for digest, rows in initial_groups.items():
        unique_by_class[rows[0]["physical_class_sha256"]].append((digest, rows))
    classes = []
    for final_class in sorted(raw_by_class):
        raw_rows = raw_by_class[final_class]
        unique_states = unique_by_class[final_class]
        classes.append(
            {
                "physical_class_sha256": final_class,
                "rules": sorted({int(row["rule"]) for row in raw_rows}),
                "defect_periods": sorted(
                    {int(row["defect_period"]) for row in raw_rows}
                ),
                "raw_input_count": len(raw_rows),
                "unique_initial_state_count": len(unique_states),
                "encoding_alias_count": len(raw_rows) - len(unique_states),
                "maximum_encodings_per_initial_state": max(
                    len(rows) for _, rows in unique_states
                ),
                "examples": [
                    {
                        "rule": row["rule"],
                        "background": row["background"],
                        "word": row["word"],
                    }
                    for row in raw_rows[:3]
                ],
            }
        )
    return sorted(
        classes,
        key=lambda row: (-row["unique_initial_state_count"], row["physical_class_sha256"]),
    )


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 93 - Physical initial-state deduplication",
        "",
        "## Question",
        "",
        "How much of the apparent long-period basin occupancy in Fase 91 is due to distinct physical initial states, and how much is due to multiple word-length/padding encodings of the same state?",
        "",
        "## Frozen identity",
        "",
        "- Source: the versioned Fase-91 JSON with its exact predeclared SHA-256.",
        "- Strict initial identity: rule, complete background state at t=0, and absolute initial defect positions on WIDTH=256.",
        "- Placement: start = WIDTH//2 - word_len//2, checked independently against the historical initial_diff implementation.",
        "- No translation, rotation, reflection, or temporal canonicalization is used.",
        "- Final class is read directly from the verified Fase-91 physical_class_sha256 field; no dynamics or attractor hash is recomputed.",
        "- Gate: one strict initial state mapping to multiple final physical classes aborts with INITIAL_STATE_DETERMINISM_VIOLATION.",
        "",
        "## Reconciliation",
        "",
        f"- Raw Fase-91 input rows: {summary['raw_input_count']}",
        f"- Strict physical initial states: {summary['unique_initial_state_count']}",
        f"- Encoding aliases removed: {summary['encoding_alias_count']}",
        f"- Determinism conflicts: {summary['determinism_conflict_count']}",
        f"- Final physical attractor classes retained: {summary['physical_class_count']}",
        "",
        "## Observed long-period basin occupancy",
        "",
        f"- Largest raw descriptor occupancy: {summary['largest_raw_input_occupancy']}",
        f"- Largest deduplicated physical-state occupancy: {summary['largest_unique_state_occupancy']}",
        f"- Singleton physical classes after deduplication: {summary['singleton_physical_class_count']}",
        f"- Maximum encodings of one physical initial state: {summary['maximum_encoding_multiplicity']}",
        f"- Encoding multiplicity distribution: `{json.dumps(summary['encoding_multiplicity_distribution'], sort_keys=True)}`",
        f"- Strict initial states under the separate rule_73/rule_109 conjugacy quotient: {summary['conjugacy_initial_state_count']}",
        "",
        "## Largest deduplicated occupancies",
        "",
        "| unique states | raw inputs | encoding aliases | rules | T defect | examples |",
        "|---:|---:|---:|---|---|---|",
    ]
    for row in payload["physical_classes"][:15]:
        examples = "; ".join(
            f"r{item['rule']}/{item['background']}/{item['word']}"
            for item in row["examples"]
        )
        lines.append(
            f"| {row['unique_initial_state_count']} | {row['raw_input_count']} | "
            f"{row['encoding_alias_count']} | {row['rules']} | {row['defect_periods']} | {examples} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"`{payload['status']}`",
            "",
            "Fase-91 raw alias counts are not basin volumes. The deduplicated counts quantify observed long-period basin occupancy only within the frozen protocol and candidate set.",
            "",
            "## Methodological limits",
            "",
            "- The 3,296 cases remain restricted to the two frozen Fase-90 cohorts: baseline_period_1_2_4 and primitive_len8.",
            "- Only confirmed long-period detector misses are included; short-period positives, negatives, and zero ICs are outside this occupancy denominator.",
            "- Deduplicated occupancy is not a universal basin volume in the complete ECA configuration space.",
            "- The conjugacy quotient is reported separately and never replaces strict physical identity.",
            "- No simulation, ANF measurement, paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.",
            "",
        ]
    )
    return "\n".join(lines)


def run() -> dict[str, Any]:
    source_sha256 = sha256_file(SOURCE_PATH)
    if source_sha256 != EXPECTED_SOURCE_SHA256:
        raise RuntimeError(
            f"Fase-91 source SHA mismatch: {source_sha256} != {EXPECTED_SOURCE_SHA256}"
        )
    base = load_module("fase93_base", BASE_PATH)
    source_payload = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))
    source_rows = source_payload["cases"]
    if len(source_rows) != EXPECTED_INPUT_COUNT:
        raise RuntimeError(f"Expected {EXPECTED_INPUT_COUNT} source rows")
    physical_classes = {row["physical_class_sha256"] for row in source_rows}
    if len(physical_classes) != EXPECTED_PHYSICAL_CLASS_COUNT:
        raise RuntimeError(
            f"Expected {EXPECTED_PHYSICAL_CLASS_COUNT} physical classes"
        )

    initial_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    conjugacy_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    initial_state_records = {}
    for row in source_rows:
        derived = derive_initial_state(row, base)
        strict_digest = derived["strict_sha256"]
        initial_groups[strict_digest].append(row)
        conjugacy_groups[derived["conjugacy_sha256"]].append(row)
        initial_state_records.setdefault(
            strict_digest,
            {
                "initial_state_sha256": strict_digest,
                "conjugacy_initial_state_sha256": derived["conjugacy_sha256"],
                "background_t0_absolute": derived["background_t0_absolute"],
                "initial_diff_absolute": derived["initial_diff_absolute"],
                "physical_class_sha256": row["physical_class_sha256"],
                "rule": int(row["rule"]),
                "encoding_count": 0,
                "encodings": [],
            },
        )
        record = initial_state_records[strict_digest]
        record["encoding_count"] += 1
        if len(record["encodings"]) < 8:
            record["encodings"].append(
                {
                    "cohort": row["cohort"],
                    "background": row["background"],
                    "word_len": int(row["word_len"]),
                    "word": row["word"],
                }
            )
    validate_determinism(initial_groups)
    class_rows = build_class_rows(source_rows, initial_groups)
    multiplicities = [len(rows) for rows in initial_groups.values()]
    summary = {
        "raw_input_count": len(source_rows),
        "unique_initial_state_count": len(initial_groups),
        "encoding_alias_count": len(source_rows) - len(initial_groups),
        "determinism_conflict_count": 0,
        "physical_class_count": len(class_rows),
        "largest_raw_input_occupancy": max(
            row["raw_input_count"] for row in class_rows
        ),
        "largest_unique_state_occupancy": max(
            row["unique_initial_state_count"] for row in class_rows
        ),
        "singleton_physical_class_count": sum(
            row["unique_initial_state_count"] == 1 for row in class_rows
        ),
        "maximum_encoding_multiplicity": max(multiplicities),
        "encoding_multiplicity_distribution": distribution(multiplicities),
        "conjugacy_initial_state_count": len(conjugacy_groups),
        "cohort_distribution": distribution(row["cohort"] for row in source_rows),
        "rule_distribution": distribution(row["rule"] for row in source_rows),
    }
    payload = {
        "phase": 93,
        "status": "PHYSICAL_INITIAL_STATE_BASINS_DEDUPLICATED",
        "source_phase91_results_sha256": source_sha256,
        "protocol": {
            "width": WIDTH,
            "placement": "start = WIDTH//2 - word_len//2",
            "strict_identity": [
                "rule",
                "background_state_t0_absolute",
                "initial_diff_absolute",
            ],
            "canonicalization_applied": False,
            "final_class_source": "existing Fase-91 physical_class_sha256 field",
            "simulation_executed": False,
        },
        "summary": summary,
        "physical_classes": class_rows,
        "initial_states": sorted(
            initial_state_records.values(), key=lambda row: row["initial_state_sha256"]
        ),
        "methodological_limits": [
            "Only the frozen baseline_period_1_2_4 and primitive_len8 Fase-90 cohorts are included.",
            "Only confirmed long-period detector misses contribute to the occupancy denominator.",
            "Observed long-period basin occupancy is not universal basin volume.",
        ],
    }
    atomic_write(
        RESULTS_PATH, json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    atomic_write(REPORT_PATH, render_report(payload))
    return payload


def main() -> None:
    payload = run()
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
