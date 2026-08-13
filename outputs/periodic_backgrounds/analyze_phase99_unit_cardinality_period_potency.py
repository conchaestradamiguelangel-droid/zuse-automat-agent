#!/usr/bin/env python3
"""Fase 100: audit historical-period potency at unit node cardinality."""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import os
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


OUT_DIR = Path(__file__).resolve().parent
PHASE95_PATH = OUT_DIR / "phase94_hypercube_completion_results.json"
PHASE99_PATH = OUT_DIR / "phase98_historical_period_rescue_results.json"
PHASE99_RUNNER = OUT_DIR / "analyze_phase98_historical_period_rescue.py"
RESULTS_PATH = OUT_DIR / "phase99_unit_cardinality_period_potency_results.json"
REPORT_PATH = OUT_DIR / "phase99_unit_cardinality_period_potency_report.md"

EXPECTED_PHASE95_RAW_SHA256 = (
    "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3"
)
EXPECTED_PHASE95_CANONICAL_SHA256 = (
    "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429"
)
EXPECTED_PHASE99_RAW_SHA256 = (
    "df46d597fbb73a0cd5d048047c3c54a98ca479d9a0ff3a8d0bb6528392f46170"
)
EXPECTED_PHASE99_CANONICAL_SHA256 = (
    "98b075368ed7129d229bfe8bbf8aeac19d8d7e2958b2df1f344672623e5efc62"
)

EXPECTED_CUBE_COUNT = 48
EXPECTED_HISTORICAL_NODE_COUNT = 9_096
EXPECTED_TARGET_COUNT = 219
EXPECTED_CONTROL_COUNT = 408
EXPECTED_PROFILE_COUNT = 5_776
EXPECTED_PERIODS = (2, 3, 5, 6, 8, 10, 12, 15)
EXPECTED_EXPOSURES_BY_PERIOD = {
    2: 4_071,
    3: 11_656,
    5: 250,
    6: 22_644,
    8: 263,
    10: 273,
    12: 3_362,
    15: 906,
}
EXPECTED_STRATA_BY_PERIOD = {
    2: 41,
    3: 206,
    5: 28,
    6: 219,
    8: 41,
    10: 33,
    12: 211,
    15: 140,
}
EXPECTED_EXPOSURE_COUNT = 43_425
EXPECTED_STRATUM_COUNT = 919
EXPECTED_COMPARISON_COUNT = 1_584
EXPECTED_RULE_TARGET_COUNTS = {73: 103, 109: 116}
METRICS = ("kappa_v", "lambda_e")
HISTORICAL_CATEGORY = "HISTORICAL_SOURCE_POSITIVE"


def load_phase99_core():
    name = "phase100_phase99_core"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, PHASE99_RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase99 = load_phase99_core()
phase98 = phase99.phase98
phase97 = phase99.phase97


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
    return dict(sorted(Counter(str(value) for value in values).items()))


def fraction_payload(numerator: int, denominator: int) -> dict[str, Any]:
    if denominator <= 0:
        raise ValueError("Fraction denominator must be positive")
    value = Fraction(numerator, denominator)
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": round(float(value), 12),
    }


def mean_fraction_payload(values: list[tuple[int, int]]) -> dict[str, Any]:
    if not values:
        raise ValueError("Cannot average an empty fraction family")
    total = sum((Fraction(a, b) for a, b in values), Fraction(0, 1))
    mean = total / len(values)
    return {
        "numerator": mean.numerator,
        "denominator": mean.denominator,
        "decimal": round(float(mean), 12),
        "stratum_count": len(values),
    }


def compare_fractions(
    left_numerator: int,
    left_denominator: int,
    right_numerator: int,
    right_denominator: int,
) -> str:
    left_cross = left_numerator * right_denominator
    right_cross = right_numerator * left_denominator
    if left_cross > right_cross:
        return "LEFT_HIGHER"
    if left_cross < right_cross:
        return "RIGHT_HIGHER"
    return "TIE"


def classify_group_relation(group_value: int, individual_rescue_count: int) -> str:
    group_rescued = int(group_value) >= 2
    individual_rescued = int(individual_rescue_count) > 0
    if not group_rescued and individual_rescued:
        return "MONOTONICITY_CONTRADICTION"
    if group_rescued and individual_rescued:
        return "SINGLE_NODE_EXPLAINS_GROUP_RESCUE"
    if group_rescued:
        return "COLLECTIVE_ONLY_PERIOD_RESCUE"
    return "NONRESCUING_PERIOD_CONTROL"


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


def validate_phase99_replay(data: dict[str, Any]) -> list[dict[str, Any]]:
    summary = data["summary"]
    if (
        summary["historical_node_count"] != EXPECTED_HISTORICAL_NODE_COUNT
        or summary["target_count"] != EXPECTED_TARGET_COUNT
        or summary["excluded_control_count"] != EXPECTED_CONTROL_COUNT
        or summary["subset_profile_count"] != EXPECTED_PROFILE_COUNT
        or summary["reconciliation_failure_count"] != 0
        or summary["monotonicity_failure_count"] != 0
    ):
        raise RuntimeError("Fase-99 summary replay failed")
    targets = data["targets"]
    if len(targets) != EXPECTED_TARGET_COUNT:
        raise RuntimeError("Fase-99 target denominator mismatch")
    if Counter(int(row["rule"]) for row in targets) != Counter(
        EXPECTED_RULE_TARGET_COUNTS
    ):
        raise RuntimeError("Fase-99 rule denominator mismatch")
    profile_count = sum(len(row["subset_profiles"]) for row in targets)
    if profile_count != EXPECTED_PROFILE_COUNT:
        raise RuntimeError("Fase-99 profile replay failed")
    return targets


def group_profile(target: dict[str, Any], period: int) -> dict[str, Any]:
    matches = [
        row for row in target["subset_profiles"] if row["periods"] == [period]
    ]
    if len(matches) != 1:
        raise RuntimeError("Missing or duplicate singleton period profile")
    return matches[0]


def aggregate_period_rows(
    strata: list[dict[str, Any]], exposures: list[dict[str, Any]]
) -> dict[str, Any]:
    output = {}
    for period in EXPECTED_PERIODS:
        period_strata = [row for row in strata if row["period"] == period]
        period_exposures = [row for row in exposures if row["period"] == period]
        metric_payload = {}
        for metric, count_key in (
            ("kappa_v", "vertex_rescue_count"),
            ("lambda_e", "edge_rescue_count"),
        ):
            rescue_count = sum(int(row[metric]) >= 2 for row in period_exposures)
            fractions = [
                (int(row[count_key]), int(row["node_count"]))
                for row in period_strata
            ]
            metric_payload[metric] = {
                "rescue_count": rescue_count,
                "micro_rate": fraction_payload(rescue_count, len(period_exposures)),
                "macro_mean_rate": mean_fraction_payload(fractions),
                "strata_with_individual_rescue": sum(a > 0 for a, _ in fractions),
                "relation_counts": distribution(
                    row["relations"][metric] for row in period_strata
                ),
            }
        both_count = sum(row["same_node_both_rescued"] for row in period_exposures)
        output[str(period)] = {
            "exposure_count": len(period_exposures),
            "stratum_count": len(period_strata),
            "same_node_both_rescue_count": both_count,
            "metrics": metric_payload,
        }
    return output


def aggregate_comparisons(
    comparisons: list[dict[str, Any]], *, rule: int | None = None
) -> dict[str, Any]:
    rows = comparisons if rule is None else [row for row in comparisons if row["rule"] == rule]
    output: dict[str, Any] = {}
    for left, right in itertools.combinations(EXPECTED_PERIODS, 2):
        selected = [
            row
            for row in rows
            if row["left_period"] == left and row["right_period"] == right
        ]
        if not selected:
            continue
        output[f"{left}_vs_{right}"] = {
            "comparison_count": len(selected),
            **{
                metric: distribution(row["comparisons"][metric] for row in selected)
                for metric in METRICS
            },
        }
    return output


def build_payload(phase95: dict[str, Any], phase99_data: dict[str, Any]):
    if len(phase95["cube_nodes"]) != EXPECTED_CUBE_COUNT:
        raise RuntimeError("Fase-95 cube denominator mismatch")
    global_period_counts = phase99.validate_historical_metadata(phase95)
    targets = validate_phase99_replay(phase99_data)
    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    exposures: list[dict[str, Any]] = []
    strata: list[dict[str, Any]] = []
    comparisons: list[dict[str, Any]] = []
    exposure_counts = Counter()
    stratum_counts = Counter()
    reconciliation_failures = 0
    monotonicity_failures = 0

    for target in targets:
        cube = cubes[target["cube_key"]]
        nodes = cube["nodes"]
        physical_class = target["physical_class_sha256"]
        component_a = [int(word, 2) for word in target["left_component_words"]]
        component_b = [int(word, 2) for word in target["right_component_words"]]
        levels = phase97.node_levels(nodes, physical_class)
        allowed_f1 = phase97.allowed_words(levels, 1)
        base_payload = {"allowed_words": sorted(allowed_f1)}
        base_values = phase98.connectivity_values(allowed_f1, component_a, component_b)
        if base_values != {"kappa_v": 1, "lambda_e": 1}:
            raise RuntimeError("F1 unit-bottleneck replay failed")

        period_words: dict[int, set[int]] = defaultdict(set)
        for word, node in enumerate(nodes):
            if int(node["word8"], 2) != word:
                raise RuntimeError("Cube word/index reconciliation failed")
            if node["category"] == HISTORICAL_CATEGORY:
                period = int(node["ledger"]["source_period"])
                period_words[period].add(word)

        expected_counts = {
            int(period): int(count)
            for period, count in target["historical_node_count_by_period"].items()
        }
        actual_counts = {period: len(words) for period, words in period_words.items()}
        if actual_counts != expected_counts:
            raise RuntimeError("Target-period word reconciliation failed")

        target_strata: list[dict[str, Any]] = []
        for period in sorted(period_words):
            words = period_words[period]
            full_profile = group_profile(target, period)
            full_allowed = set(allowed_f1) | words
            replay_full = phase98.connectivity_values(
                full_allowed, component_a, component_b
            )
            if any(replay_full[metric] != full_profile[metric] for metric in METRICS):
                raise RuntimeError("Full-period profile replay failed")

            period_exposures = []
            for word in sorted(words):
                node = nodes[word]
                if node["category"] != HISTORICAL_CATEGORY or word in allowed_f1:
                    raise RuntimeError("Unit historical-node membership gate failed")
                allowed_unit = set(allowed_f1)
                allowed_unit.add(word)
                if len(allowed_unit) != len(allowed_f1) + 1:
                    raise RuntimeError("Unit intervention cardinality gate failed")
                if not allowed_unit <= full_allowed:
                    raise RuntimeError("Unit/full-period subgraph gate failed")
                restored = set(allowed_unit)
                restored.remove(word)
                if canonical_sha256({"allowed_words": sorted(restored)}) != canonical_sha256(
                    base_payload
                ):
                    raise RuntimeError("Unit intervention reversal gate failed")
                values = phase98.connectivity_values(
                    allowed_unit, component_a, component_b
                )
                if any(values[metric] > replay_full[metric] for metric in METRICS):
                    monotonicity_failures += 1
                    raise RuntimeError("Unit/full-period monotonicity contradiction")
                row = {
                    "pair_index": target["pair_index"],
                    "physical_class_sha256": physical_class,
                    "cube_key": target["cube_key"],
                    "rule": int(target["rule"]),
                    "background_index": int(target["background_index"]),
                    "period": period,
                    "word8": node["word8"],
                    "word_int": word,
                    **values,
                    "vertex_rescued": values["kappa_v"] >= 2,
                    "edge_rescued": values["lambda_e"] >= 2,
                    "same_node_both_rescued": (
                        values["kappa_v"] >= 2 and values["lambda_e"] >= 2
                    ),
                }
                exposures.append(row)
                period_exposures.append(row)
                exposure_counts[period] += 1

            vertex_count = sum(row["vertex_rescued"] for row in period_exposures)
            edge_count = sum(row["edge_rescued"] for row in period_exposures)
            both_count = sum(row["same_node_both_rescued"] for row in period_exposures)
            relations = {
                "kappa_v": classify_group_relation(
                    replay_full["kappa_v"], vertex_count
                ),
                "lambda_e": classify_group_relation(
                    replay_full["lambda_e"], edge_count
                ),
            }
            if "MONOTONICITY_CONTRADICTION" in relations.values():
                monotonicity_failures += 1
                raise RuntimeError("Group/unit monotonicity contradiction")
            stratum = {
                "pair_index": target["pair_index"],
                "physical_class_sha256": physical_class,
                "cube_key": target["cube_key"],
                "rule": int(target["rule"]),
                "background_index": int(target["background_index"]),
                "period": period,
                "node_count": len(period_exposures),
                "group_values": replay_full,
                "vertex_rescue_count": vertex_count,
                "edge_rescue_count": edge_count,
                "same_node_both_rescue_count": both_count,
                "vertex_rescue_fraction": fraction_payload(
                    vertex_count, len(period_exposures)
                ),
                "edge_rescue_fraction": fraction_payload(
                    edge_count, len(period_exposures)
                ),
                "same_node_both_fraction": fraction_payload(
                    both_count, len(period_exposures)
                ),
                "vertex_rescuing_words": [
                    row["word8"] for row in period_exposures if row["vertex_rescued"]
                ],
                "edge_rescuing_words": [
                    row["word8"] for row in period_exposures if row["edge_rescued"]
                ],
                "same_node_both_rescuing_words": [
                    row["word8"]
                    for row in period_exposures
                    if row["same_node_both_rescued"]
                ],
                "relations": relations,
            }
            strata.append(stratum)
            target_strata.append(stratum)
            stratum_counts[period] += 1

        for left, right in itertools.combinations(target_strata, 2):
            if left["period"] >= right["period"]:
                raise RuntimeError("Target-period comparison ordering failed")
            comparisons.append(
                {
                    "pair_index": target["pair_index"],
                    "cube_key": target["cube_key"],
                    "rule": int(target["rule"]),
                    "left_period": left["period"],
                    "right_period": right["period"],
                    "comparisons": {
                        "kappa_v": compare_fractions(
                            left["vertex_rescue_count"],
                            left["node_count"],
                            right["vertex_rescue_count"],
                            right["node_count"],
                        ),
                        "lambda_e": compare_fractions(
                            left["edge_rescue_count"],
                            left["node_count"],
                            right["edge_rescue_count"],
                            right["node_count"],
                        ),
                    },
                }
            )

    if dict(sorted(exposure_counts.items())) != EXPECTED_EXPOSURES_BY_PERIOD:
        reconciliation_failures += 1
        raise RuntimeError("Unit exposure denominator mismatch")
    if dict(sorted(stratum_counts.items())) != EXPECTED_STRATA_BY_PERIOD:
        reconciliation_failures += 1
        raise RuntimeError("Target-period stratum denominator mismatch")
    if len(exposures) != EXPECTED_EXPOSURE_COUNT:
        raise RuntimeError("Total unit exposure denominator mismatch")
    if len(strata) != EXPECTED_STRATUM_COUNT:
        raise RuntimeError("Total stratum denominator mismatch")
    if len(comparisons) != EXPECTED_COMPARISON_COUNT:
        raise RuntimeError("Within-target comparison denominator mismatch")

    period_aggregates = aggregate_period_rows(strata, exposures)
    global_relation_counts = {
        metric: distribution(row["relations"][metric] for row in strata)
        for metric in METRICS
    }
    vertex_rescue_count = sum(row["vertex_rescued"] for row in exposures)
    edge_rescue_count = sum(row["edge_rescued"] for row in exposures)
    same_node_both_count = sum(
        row["same_node_both_rescued"] for row in exposures
    )
    unit_connectivity_distribution = distribution(
        f"{row['kappa_v']},{row['lambda_e']}" for row in exposures
    )
    by_rule = {}
    for rule in sorted(EXPECTED_RULE_TARGET_COUNTS):
        rule_strata = [row for row in strata if row["rule"] == rule]
        rule_exposures = [row for row in exposures if row["rule"] == rule]
        by_rule[str(rule)] = {
            "target_count": EXPECTED_RULE_TARGET_COUNTS[rule],
            "exposure_count": len(rule_exposures),
            "stratum_count": len(rule_strata),
            "period_aggregates": aggregate_period_rows(rule_strata, rule_exposures),
            "pairwise_period_comparisons": aggregate_comparisons(
                comparisons, rule=rule
            ),
        }

    payload = {
        "phase": 100,
        "status": "UNIT_CARDINALITY_PERIOD_POTENCY_MAPPED",
        "sources": {
            "phase95_path": PHASE95_PATH.name,
            "phase95_raw_sha256": EXPECTED_PHASE95_RAW_SHA256,
            "phase95_canonical_sha256": EXPECTED_PHASE95_CANONICAL_SHA256,
            "phase99_path": PHASE99_PATH.name,
            "phase99_raw_sha256": EXPECTED_PHASE99_RAW_SHA256,
            "phase99_canonical_sha256": EXPECTED_PHASE99_CANONICAL_SHA256,
        },
        "protocol": {
            "simulation_executed": False,
            "graph": "UNDIRECTED_Q8_HAMMING1",
            "unit_intervention_cardinality": 1,
            "terminal_policy": "FULL_F0_COMPONENTS_NONREMOVABLE",
            "zero_word_included": False,
            "periods": list(EXPECTED_PERIODS),
            "fraction_comparison": "EXACT_INTEGER_CROSS_MULTIPLICATION",
            "abundance_control": "UNIT_CARDINALITY_ONLY",
        },
        "summary": {
            "cube_count": EXPECTED_CUBE_COUNT,
            "historical_physical_node_count": EXPECTED_HISTORICAL_NODE_COUNT,
            "historical_physical_node_count_by_period": {
                str(key): value for key, value in global_period_counts.items()
            },
            "target_count": EXPECTED_TARGET_COUNT,
            "excluded_control_count": EXPECTED_CONTROL_COUNT,
            "exposure_count": len(exposures),
            "exposure_count_by_period": {
                str(key): value for key, value in sorted(exposure_counts.items())
            },
            "stratum_count": len(strata),
            "stratum_count_by_period": {
                str(key): value for key, value in sorted(stratum_counts.items())
            },
            "within_target_comparison_count": len(comparisons),
            "reconciliation_failure_count": reconciliation_failures,
            "monotonicity_failure_count": monotonicity_failures,
            "unit_connectivity_distribution": unit_connectivity_distribution,
            "vertex_rescue_exposure_count": vertex_rescue_count,
            "edge_rescue_exposure_count": edge_rescue_count,
            "same_node_both_rescue_exposure_count": same_node_both_count,
            "vertex_only_rescue_exposure_count": sum(
                row["vertex_rescued"] and not row["edge_rescued"]
                for row in exposures
            ),
            "edge_only_rescue_exposure_count": sum(
                row["edge_rescued"] and not row["vertex_rescued"]
                for row in exposures
            ),
            "global_relation_counts": global_relation_counts,
            "period_aggregates": period_aggregates,
            "pairwise_period_comparisons": aggregate_comparisons(comparisons),
            "by_rule": by_rule,
            "phase99_replay_status": "EXACT_TARGET_STRATUM_AND_GROUP_REPLAY",
            "simulation_executed": False,
        },
        "exposures": exposures,
        "target_period_strata": strata,
        "within_target_period_comparisons": comparisons,
        "methodological_limits": [
            "Unit cardinality removes the immediate advantage of adding more nodes, but not geometric placement.",
            "Collective rescue by two or more nodes is not decomposed in this phase.",
            "Period labels are associated metadata, not demonstrated temporal causes.",
            "The atlas is limited to 219 bottlenecks in 48 frozen Q8 cubes.",
            "No WIDTH=256 basin probability or temporal transition probability is estimated.",
        ],
    }
    return payload


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Rule 73/109 unit-cardinality historical-period potency - Fase 100",
        "",
        "## Protocol",
        "",
        "Each historical node is added alone to the pair-specific F1 graph. The analysis uses exact Q8 max-flow connectivity and performs no CA simulation.",
        "",
        "## Gates",
        "",
        f"- Frozen cubes: `{summary['cube_count']}`",
        f"- Physical historical nodes: `{summary['historical_physical_node_count']}`",
        f"- Unit target-node exposures: `{summary['exposure_count']}`",
        f"- Target-period strata: `{summary['stratum_count']}`",
        f"- Within-target period comparisons per metric: `{summary['within_target_comparison_count']}`",
        f"- Reconciliation failures: `{summary['reconciliation_failure_count']}`",
        f"- Monotonicity failures: `{summary['monotonicity_failure_count']}`",
        f"- Fase-99 replay: `{summary['phase99_replay_status']}`",
        "",
        "## Global partition",
        "",
        f"- Unit connectivity `(kappa_v,lambda_e)`: `{json.dumps(summary['unit_connectivity_distribution'], sort_keys=True)}`",
        f"- Same-node rescue of both metrics: `{summary['same_node_both_rescue_exposure_count']}`",
        f"- Edge-only rescues: `{summary['edge_only_rescue_exposure_count']}`",
        f"- Vertex-only rescues: `{summary['vertex_only_rescue_exposure_count']}`",
        f"- kappa group relations: `{json.dumps(summary['global_relation_counts']['kappa_v'], sort_keys=True)}`",
        f"- lambda group relations: `{json.dumps(summary['global_relation_counts']['lambda_e'], sort_keys=True)}`",
        "",
        "## Period potency",
        "",
        "| Period | Exposures | Strata | kappa rescues | kappa micro | kappa strata hit | lambda rescues | lambda micro | lambda strata hit |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for period in EXPECTED_PERIODS:
        row = summary["period_aggregates"][str(period)]
        kappa = row["metrics"]["kappa_v"]
        edge = row["metrics"]["lambda_e"]
        lines.append(
            "| {p} | {e} | {s} | {kr} | {km:.6f} | {ks} | {er} | {em:.6f} | {es} |".format(
                p=period,
                e=row["exposure_count"],
                s=row["stratum_count"],
                kr=kappa["rescue_count"],
                km=kappa["micro_rate"]["decimal"],
                ks=kappa["strata_with_individual_rescue"],
                er=edge["rescue_count"],
                em=edge["micro_rate"]["decimal"],
                es=edge["strata_with_individual_rescue"],
            )
        )
    lines.extend(
        [
            "",
            "## Relation to full-period groups",
            "",
        ]
    )
    for period in EXPECTED_PERIODS:
        row = summary["period_aggregates"][str(period)]
        lines.append(f"### T={period}")
        lines.append("")
        for metric in METRICS:
            counts = row["metrics"][metric]["relation_counts"]
            lines.append(f"- `{metric}`: `{json.dumps(counts, sort_keys=True)}`")
        lines.append("")
    lines.extend(
        [
            "## Interpretation",
            "",
            "The micro and macro rates quantify one-node topological potency associated with each period. They do not establish period causality. Collective-only strata identify full-period rescue that cannot be attributed to any one node in isolation.",
            "",
            "## Verdict",
            "",
            "`UNIT_CARDINALITY_PERIOD_POTENCY_MAPPED`",
            "",
            "## Methodological limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["methodological_limits"])
    return "\n".join(lines) + "\n"


def main() -> int:
    phase95 = read_and_gate(
        PHASE95_PATH, EXPECTED_PHASE95_RAW_SHA256, EXPECTED_PHASE95_CANONICAL_SHA256
    )
    phase99_data = read_and_gate(
        PHASE99_PATH, EXPECTED_PHASE99_RAW_SHA256, EXPECTED_PHASE99_CANONICAL_SHA256
    )
    first = build_payload(phase95, phase99_data)
    second = build_payload(phase95, phase99_data)
    if canonical_json_bytes(first) != canonical_json_bytes(second):
        raise RuntimeError("Independent in-memory constructions disagree")
    results_text = json.dumps(first, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    report_text = render_report(first)
    atomic_write(RESULTS_PATH, results_text)
    atomic_write(REPORT_PATH, report_text)
    print(json.dumps(first["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
