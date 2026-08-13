#!/usr/bin/env python3
"""Fase 99: decompose historical bottleneck rescue by source period."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


OUT_DIR = Path(__file__).resolve().parent
PHASE95_PATH = OUT_DIR / "phase94_hypercube_completion_results.json"
PHASE98_PATH = OUT_DIR / "phase97_bottleneck_rescue_results.json"
PHASE98_RUNNER = OUT_DIR / "analyze_phase97_bottleneck_rescue.py"
RESULTS_PATH = OUT_DIR / "phase98_historical_period_rescue_results.json"
REPORT_PATH = OUT_DIR / "phase98_historical_period_rescue_report.md"

EXPECTED_PHASE95_RAW_SHA256 = (
    "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3"
)
EXPECTED_PHASE95_CANONICAL_SHA256 = (
    "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429"
)
EXPECTED_PHASE98_RAW_SHA256 = (
    "0e0037a8cfef81e0f190275636977189d1d4d46db009a909cbc017e0a7693297"
)
EXPECTED_PHASE98_CANONICAL_SHA256 = (
    "42eeed0fe5f8d4f75013bfd9d29466a7fc6600bf4bce1b1b82ae30707d3cb387"
)

EXPECTED_HISTORICAL_NODE_COUNT = 9_096
EXPECTED_PERIODS = (2, 3, 5, 6, 8, 10, 12, 15)
EXPECTED_TARGET_COUNT = 219
EXPECTED_CONTROL_COUNT = 408
EXPECTED_RULE_TARGET_COUNTS = {73: 103, 109: 116}
EXPECTED_AVAILABLE_COUNT_DISTRIBUTION = {3: 38, 4: 140, 5: 21, 7: 20}
EXPECTED_PROFILE_COUNT = 5_776
EXPECTED_COVER_RELATION_COUNT = 15_576
METRICS = ("kappa_v", "lambda_e")
HISTORICAL_CATEGORY = "HISTORICAL_SOURCE_POSITIVE"


def load_phase98_core():
    name = "phase99_phase98_core"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, PHASE98_RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase98 = load_phase98_core()
phase97 = phase98.phase97


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    with temporary.open("r+b") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def distribution(values: Iterable[Any]) -> dict[str, int]:
    counts = Counter(str(value) for value in values)
    return dict(sorted(counts.items()))


def powerset(values: tuple[int, ...]) -> list[tuple[int, ...]]:
    return [
        tuple(subset)
        for size in range(len(values) + 1)
        for subset in itertools.combinations(values, size)
    ]


def minimal_rescuing_period_sets(
    profiles: list[dict[str, Any]], metric: str
) -> list[list[int]]:
    rescued = [
        frozenset(row["periods"])
        for row in profiles
        if int(row[metric]) >= 2
    ]
    minimal = [
        subset
        for subset in rescued
        if not any(other < subset for other in rescued)
    ]
    return [
        sorted(subset)
        for subset in sorted(minimal, key=lambda row: (len(row), sorted(row)))
    ]


def classify_minimal_period_sets(minimal_sets: list[list[int]]) -> str:
    if not minimal_sets:
        return "NO_PERIOD_SUBSET_RESCUE"
    singleton_count = sum(len(row) == 1 for row in minimal_sets)
    interaction_count = sum(len(row) >= 2 for row in minimal_sets)
    if singleton_count == 1 and interaction_count == 0:
        return "UNIQUE_SINGLETON_RESCUE"
    if singleton_count >= 2 and interaction_count == 0:
        return "MULTIPLE_SINGLETON_ALTERNATIVES"
    if singleton_count == 0 and interaction_count >= 1:
        return "INTERACTION_REQUIRED"
    if singleton_count >= 1 and interaction_count >= 1:
        return "MIXED_SINGLETON_AND_INTERACTION_MINIMA"
    raise RuntimeError("Unclassified period-minimal family")


def period_roles(
    available_periods: tuple[int, ...], minimal_sets: list[list[int]]
) -> dict[str, dict[str, bool]]:
    sets = [set(row) for row in minimal_sets]
    return {
        str(period): {
            "individually_sufficient": {period} in sets,
            "necessary_for_rescue": bool(sets)
            and all(period in row for row in sets),
            "interaction_only": (
                any(period in row and len(row) >= 2 for row in sets)
                and {period} not in sets
            ),
            "unused_in_minimal_rescue": not any(period in row for row in sets),
        }
        for period in available_periods
    }


def validate_cover_monotonicity(
    profiles: list[dict[str, Any]], available_periods: tuple[int, ...]
) -> tuple[int, int]:
    by_subset = {frozenset(row["periods"]): row for row in profiles}
    expected = 1 << len(available_periods)
    if len(by_subset) != expected:
        raise RuntimeError("Period subset omission or duplication")
    relation_count = 0
    failures = 0
    for subset, source in by_subset.items():
        for period in available_periods:
            if period in subset:
                continue
            target = by_subset[subset | {period}]
            relation_count += 1
            for metric in METRICS:
                if int(source[metric]) > int(target[metric]):
                    failures += 1
    return relation_count, failures


def read_and_gate(path: Path, expected_raw: str, expected_canonical: str):
    raw = path.read_bytes()
    raw_sha = sha256_bytes(raw)
    if raw_sha != expected_raw:
        raise RuntimeError(f"Raw SHA mismatch for {path.name}: {raw_sha}")
    payload = json.loads(raw)
    canonical_sha = canonical_sha256(payload)
    if canonical_sha != expected_canonical:
        raise RuntimeError(f"Canonical SHA mismatch for {path.name}: {canonical_sha}")
    return payload


def validate_historical_metadata(phase95: dict[str, Any]) -> dict[int, int]:
    periods = Counter()
    count = 0
    for cube in phase95["cube_nodes"]:
        for node in cube["nodes"]:
            if node["category"] != HISTORICAL_CATEGORY:
                continue
            count += 1
            ledger = node["ledger"]
            source_period = ledger.get("source_period")
            if (
                ledger.get("source_kind") != "STATIONARY"
                or ledger.get("expanded_kind") != "STATIONARY"
                or ledger.get("source_drift") != 0
                or ledger.get("expanded_drift") != 0
                or source_period != ledger.get("expanded_period")
                or source_period not in EXPECTED_PERIODS
                or not isinstance(source_period, int)
            ):
                raise RuntimeError("Historical-node period metadata gate failed")
            periods[source_period] += 1
    if count != EXPECTED_HISTORICAL_NODE_COUNT:
        raise RuntimeError("Historical-node denominator mismatch")
    if tuple(sorted(periods)) != EXPECTED_PERIODS:
        raise RuntimeError("Historical period support mismatch")
    return dict(sorted(periods.items()))


def validate_phase98_replay(phase98_data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = phase98_data["pairs"]
    targets = [row for row in rows if row["role"] == "F1_UNIT_BOTTLENECK_TARGET"]
    controls = [row for row in rows if row["role"] == "F1_REDUNDANT_CONTROL"]
    if len(targets) != EXPECTED_TARGET_COUNT or len(controls) != EXPECTED_CONTROL_COUNT:
        raise RuntimeError("Fase-98 target/control denominator mismatch")
    rule_counts = Counter(int(row["rule"]) for row in targets)
    if dict(rule_counts) != EXPECTED_RULE_TARGET_COUNTS:
        raise RuntimeError("Fase-98 rule denominator mismatch")
    for row in targets:
        if row["f1"] != {"kappa_v": 1, "lambda_e": 1}:
            raise RuntimeError("Fase-98 F1 target replay failed")
        if row["vertex_f2_label"] != "RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY":
            raise RuntimeError("Fase-98 vertex label replay failed")
        if row["edge_f2_label"] != "RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY":
            raise RuntimeError("Fase-98 edge label replay failed")
        if row["f2_minimal_rescuing_sets"] != {
            "kappa_v": [[HISTORICAL_CATEGORY]],
            "lambda_e": [[HISTORICAL_CATEGORY]],
        }:
            raise RuntimeError("Fase-98 minimal-set replay failed")
        evaluations = {
            tuple(item["categories"]): {
                metric: int(item[metric]) for metric in METRICS
            }
            for item in row["f2_subset_evaluations"]
        }
        if evaluations[tuple()] != row["f1"]:
            raise RuntimeError("Fase-98 empty-subset replay failed")
        if evaluations[(HISTORICAL_CATEGORY,)] != row["f2"]:
            raise RuntimeError("Fase-98 historical singleton replay failed")
        if evaluations[("STATIC_T1",)] != row["f1"]:
            raise RuntimeError("Fase-98 STATIC_T1 replay failed")
    return targets


def build_payload(phase95: dict[str, Any], phase98_data: dict[str, Any]):
    historical_global_counts = validate_historical_metadata(phase95)
    targets = validate_phase98_replay(phase98_data)
    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    target_rows = []
    available_count_distribution = Counter()
    total_profile_count = 0
    total_cover_relations = 0
    total_monotonicity_failures = 0

    for source in targets:
        cube = cubes[source["cube_key"]]
        nodes = cube["nodes"]
        physical_class = source["physical_class_sha256"]
        component_a = [int(word, 2) for word in source["left_component_words"]]
        component_b = [int(word, 2) for word in source["right_component_words"]]
        levels = phase97.node_levels(nodes, physical_class)
        allowed_f1 = phase97.allowed_words(levels, 1)
        allowed_f3 = phase97.allowed_words(levels, 3)

        replay_f1 = phase98.connectivity_values(allowed_f1, component_a, component_b)
        replay_f3 = phase98.connectivity_values(allowed_f3, component_a, component_b)
        if replay_f1 != source["f1"] or replay_f3 != source["f3"]:
            raise RuntimeError(f"Fase-98 F1/F3 value replay failed at pair {source['pair_index']}")

        period_words: dict[int, set[int]] = defaultdict(set)
        for word, node in enumerate(nodes):
            if node["category"] == HISTORICAL_CATEGORY:
                period_words[int(node["ledger"]["source_period"])].add(word)
        available_periods = tuple(sorted(period_words))
        available_count_distribution[len(available_periods)] += 1
        subsets = powerset(available_periods)
        profiles = []
        for subset in subsets:
            if not subset:
                values = dict(source["f1"])
            elif subset == available_periods:
                values = dict(source["f2"])
            else:
                allowed = set(allowed_f1)
                for period in subset:
                    allowed.update(period_words[period])
                values = phase98.connectivity_values(allowed, component_a, component_b)
            profiles.append(
                {
                    "periods": list(subset),
                    "historical_node_count": sum(
                        len(period_words[period]) for period in subset
                    ),
                    **values,
                }
            )

        if profiles[0] != {
            "periods": [],
            "historical_node_count": 0,
            **source["f1"],
        }:
            raise RuntimeError("Empty period-set extreme gate failed")
        if any(profiles[-1][metric] != source["f2"][metric] for metric in METRICS):
            raise RuntimeError("Full period-set extreme gate failed")
        if profiles[-1]["historical_node_count"] != sum(
            len(words) for words in period_words.values()
        ):
            raise RuntimeError("Full period-set node-count gate failed")

        cover_count, failures = validate_cover_monotonicity(
            profiles, available_periods
        )
        total_profile_count += len(profiles)
        total_cover_relations += cover_count
        total_monotonicity_failures += failures
        if failures:
            raise RuntimeError("Period-subset monotonicity gate failed")

        minimal = {
            metric: minimal_rescuing_period_sets(profiles, metric)
            for metric in METRICS
        }
        if any(not minimal[metric] for metric in METRICS):
            raise RuntimeError("Full historical period set failed to rescue")
        metric_details = {}
        for metric in METRICS:
            metric_details[metric] = {
                "label": classify_minimal_period_sets(minimal[metric]),
                "minimal_rescuing_period_sets": minimal[metric],
                "minimal_cardinality": min(len(row) for row in minimal[metric]),
                "singleton_sufficient_periods": sorted(
                    row[0] for row in minimal[metric] if len(row) == 1
                ),
                "necessary_periods": sorted(
                    int(period)
                    for period, role in period_roles(
                        available_periods, minimal[metric]
                    ).items()
                    if role["necessary_for_rescue"]
                ),
                "period_roles": period_roles(available_periods, minimal[metric]),
            }

        target_rows.append(
            {
                "pair_index": source["pair_index"],
                "physical_class_sha256": physical_class,
                "cube_key": source["cube_key"],
                "cohort": source["cohort"],
                "rule": source["rule"],
                "background_index": source["background_index"],
                "left_component_words": source["left_component_words"],
                "right_component_words": source["right_component_words"],
                "available_periods": list(available_periods),
                "historical_node_count_by_period": {
                    str(period): len(period_words[period])
                    for period in available_periods
                },
                "subset_profile_count": len(profiles),
                "cover_relation_count": cover_count,
                "subset_profiles": profiles,
                "metrics": metric_details,
            }
        )

    if dict(available_count_distribution) != EXPECTED_AVAILABLE_COUNT_DISTRIBUTION:
        raise RuntimeError("Available-period count distribution mismatch")
    if total_profile_count != EXPECTED_PROFILE_COUNT:
        raise RuntimeError("Period subset profile denominator mismatch")
    if total_cover_relations != EXPECTED_COVER_RELATION_COUNT:
        raise RuntimeError("Period cover-relation denominator mismatch")
    if total_monotonicity_failures:
        raise RuntimeError("Period monotonicity failures remain")

    period_availability_counts = {
        str(period): sum(period in row["available_periods"] for row in target_rows)
        for period in EXPECTED_PERIODS
    }
    aggregate_by_metric = {}
    for metric in METRICS:
        label_counts = distribution(row["metrics"][metric]["label"] for row in target_rows)
        singleton_counts = {
            str(period): sum(
                period in row["metrics"][metric]["singleton_sufficient_periods"]
                for row in target_rows
            )
            for period in EXPECTED_PERIODS
        }
        necessary_counts = {
            str(period): sum(
                period in row["metrics"][metric]["necessary_periods"]
                for row in target_rows
            )
            for period in EXPECTED_PERIODS
        }
        role_counts = {
            str(period): {
                role: sum(
                    str(period) in row["metrics"][metric]["period_roles"]
                    and row["metrics"][metric]["period_roles"][str(period)][role]
                    for row in target_rows
                )
                for role in (
                    "individually_sufficient",
                    "necessary_for_rescue",
                    "interaction_only",
                    "unused_in_minimal_rescue",
                )
            }
            for period in EXPECTED_PERIODS
        }
        aggregate_by_metric[metric] = {
            "label_counts_over_219": label_counts,
            "minimal_cardinality_distribution": distribution(
                row["metrics"][metric]["minimal_cardinality"] for row in target_rows
            ),
            "singleton_sufficient_counts": singleton_counts,
            "singleton_support_by_availability": {
                str(period): {
                    "available_target_count": period_availability_counts[str(period)],
                    "singleton_sufficient_count": singleton_counts[str(period)],
                }
                for period in EXPECTED_PERIODS
            },
            "necessary_counts": necessary_counts,
            "period_role_counts": role_counts,
        }

    by_rule = {}
    for rule in sorted(EXPECTED_RULE_TARGET_COUNTS):
        rows = [row for row in target_rows if int(row["rule"]) == rule]
        by_rule[str(rule)] = {
            "target_count": len(rows),
            "kappa_label_counts": distribution(
                row["metrics"]["kappa_v"]["label"] for row in rows
            ),
            "lambda_label_counts": distribution(
                row["metrics"]["lambda_e"]["label"] for row in rows
            ),
        }

    summary = {
        "historical_node_count": EXPECTED_HISTORICAL_NODE_COUNT,
        "historical_node_count_by_period": {
            str(key): value for key, value in historical_global_counts.items()
        },
        "target_count": len(target_rows),
        "excluded_control_count": EXPECTED_CONTROL_COUNT,
        "available_period_count_distribution": {
            str(key): value for key, value in sorted(available_count_distribution.items())
        },
        "period_availability_counts_over_219": period_availability_counts,
        "subset_profile_count": total_profile_count,
        "cover_relation_count": total_cover_relations,
        "monotonicity_failure_count": total_monotonicity_failures,
        "aggregate_by_metric": aggregate_by_metric,
        "by_rule": by_rule,
        "phase98_replay_status": "EXACT_TARGET_AND_EXTREME_REPLAY",
        "reconciliation_failure_count": 0,
        "simulation_executed": False,
        "external_ledger_read": False,
    }
    return {
        "phase": 99,
        "status": "HISTORICAL_PERIOD_RESCUE_ATLAS_BUILT",
        "sources": {
            "phase95_raw_sha256": EXPECTED_PHASE95_RAW_SHA256,
            "phase95_canonical_sha256": EXPECTED_PHASE95_CANONICAL_SHA256,
            "phase98_raw_sha256": EXPECTED_PHASE98_RAW_SHA256,
            "phase98_canonical_sha256": EXPECTED_PHASE98_CANONICAL_SHA256,
        },
        "protocol": {
            "universe": "219_F1_UNIT_BOTTLENECK_TARGETS",
            "period_source": "DISTINCT_LEDGER_SOURCE_PERIOD_AMONG_HISTORICAL_NODES_PER_CUBE",
            "period_support": list(EXPECTED_PERIODS),
            "subset_method": "EXHAUSTIVE_AVAILABLE_PERIOD_POWERSET",
            "minimality": "ALL_INCLUSION_MINIMAL_RESCUING_PERIOD_SETS",
            "graph": "UNDIRECTED_Q8_HAMMING_1_INTERVENTION_GRAPH",
            "abundance_control": "NOT_PERFORMED_COUNTS_REPORTED_AS_CONFOUNDER",
            "simulation_executed": False,
            "external_ledger_read": False,
        },
        "summary": summary,
        "targets": target_rows,
        "methodological_limits": [
            "Only 219 F1 unit-bottleneck targets in 48 frozen Q8 cubes are analyzed.",
            "Source period groups can differ greatly in node abundance; no matched-size control is performed.",
            "Period grouping does not separate distinct morphologies sharing one period.",
            "Topological sufficiency is not temporal traversal or period causality.",
            "No claim is made about universal WIDTH=256 basin connectivity.",
        ],
    }


def render_report(
    payload: dict[str, Any], output_raw_sha256: str, output_canonical_sha256: str
) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 99 - Historical rescue decomposition by source period",
        "",
        "## Question",
        "",
        "Which historical stationary source-period families are sufficient or jointly required to rescue the 219 F1 unit bottlenecks?",
        "",
        "## Frozen inputs and gates",
        "",
        f"- Fase-95 raw/canonical: `{payload['sources']['phase95_raw_sha256']}` / `{payload['sources']['phase95_canonical_sha256']}`",
        f"- Fase-98 raw/canonical: `{payload['sources']['phase98_raw_sha256']}` / `{payload['sources']['phase98_canonical_sha256']}`",
        f"- Fase-99 result raw/canonical: `{output_raw_sha256}` / `{output_canonical_sha256}`",
        f"- Replay: `{summary['phase98_replay_status']}`",
        f"- Reconciliation/monotonicity failures: {summary['reconciliation_failure_count']}/{summary['monotonicity_failure_count']}",
        "",
        "## Denominators",
        "",
        f"- Historical nodes gated: {summary['historical_node_count']}",
        f"- Targets: {summary['target_count']}; excluded controls: {summary['excluded_control_count']}",
        f"- Available-period counts: `{json.dumps(summary['available_period_count_distribution'], sort_keys=True)}`",
        f"- Subset profiles / cover relations: {summary['subset_profile_count']} / {summary['cover_relation_count']}",
        "",
        "## Historical abundance",
        "",
        f"- Global nodes by period: `{json.dumps(summary['historical_node_count_by_period'], sort_keys=True)}`",
        f"- Target-cube availability by period: `{json.dumps(summary['period_availability_counts_over_219'], sort_keys=True)}`",
        "",
        "These counts expose abundance as a confounder; they are not causal weights.",
        "",
        "## Rescue signatures",
        "",
    ]
    for metric, row in summary["aggregate_by_metric"].items():
        lines.extend(
            [
                f"### {metric}",
                "",
                f"- Labels: `{json.dumps(row['label_counts_over_219'], sort_keys=True)}`",
                f"- Minimal cardinality: `{json.dumps(row['minimal_cardinality_distribution'], sort_keys=True)}`",
                f"- Singleton sufficient: `{json.dumps(row['singleton_sufficient_counts'], sort_keys=True)}`",
                f"- Singleton sufficient / available: `{json.dumps(row['singleton_support_by_availability'], sort_keys=True)}`",
                f"- Necessary: `{json.dumps(row['necessary_counts'], sort_keys=True)}`",
                f"- Roles: `{json.dumps(row['period_role_counts'], sort_keys=True)}`",
                "",
            ]
        )
    lines.extend(
        [
            "## By rule",
            "",
            "| rule | targets | kappa labels | lambda labels |",
            "|---:|---:|---|---|",
        ]
    )
    for rule, row in summary["by_rule"].items():
        lines.append(
            f"| {rule} | {row['target_count']} | "
            f"{json.dumps(row['kappa_label_counts'], sort_keys=True)} | "
            f"{json.dumps(row['lambda_label_counts'], sort_keys=True)} |"
        )
    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"`{payload['status']}`",
            "",
            "## Methodological limits",
            "",
        ]
    )
    lines.extend(f"- {row}" for row in payload["methodological_limits"])
    lines.append("")
    return "\n".join(lines)


def run() -> dict[str, Any]:
    phase95 = read_and_gate(
        PHASE95_PATH,
        EXPECTED_PHASE95_RAW_SHA256,
        EXPECTED_PHASE95_CANONICAL_SHA256,
    )
    phase98_data = read_and_gate(
        PHASE98_PATH,
        EXPECTED_PHASE98_RAW_SHA256,
        EXPECTED_PHASE98_CANONICAL_SHA256,
    )
    first = build_payload(phase95, phase98_data)
    second = build_payload(phase95, phase98_data)
    if canonical_json_bytes(first) != canonical_json_bytes(second):
        raise RuntimeError("Deterministic second-build gate failed")
    result_text = json.dumps(first, indent=2, sort_keys=True) + "\n"
    output_raw_sha = sha256_bytes(result_text.encode("utf-8"))
    output_canonical_sha = canonical_sha256(first)
    atomic_write(RESULTS_PATH, result_text)
    atomic_write(REPORT_PATH, render_report(first, output_raw_sha, output_canonical_sha))
    return first


def main() -> None:
    payload = run()
    print(json.dumps(payload["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
