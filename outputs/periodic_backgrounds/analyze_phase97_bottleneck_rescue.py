#!/usr/bin/env python3
"""Fase 98: map which state families rescue F1 unit bottlenecks."""

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
PHASE97_PATH = OUT_DIR / "phase96_bridge_robustness_results.json"
PHASE97_RUNNER = OUT_DIR / "analyze_phase96_bridge_robustness.py"
RESULTS_PATH = OUT_DIR / "phase97_bottleneck_rescue_results.json"
REPORT_PATH = OUT_DIR / "phase97_bottleneck_rescue_report.md"

EXPECTED_PHASE95_RAW_SHA256 = (
    "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3"
)
EXPECTED_PHASE95_CANONICAL_SHA256 = (
    "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429"
)
EXPECTED_PHASE97_RAW_SHA256 = (
    "3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858"
)
EXPECTED_PHASE97_CANONICAL_SHA256 = (
    "85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b"
)

EXPECTED_CUBE_COUNT = 48
EXPECTED_INTERSECTION_COUNT = 272
EXPECTED_PAIR_COUNT = 979
EXPECTED_F1_PAIR_COUNT = 627
EXPECTED_F1_TARGET_COUNT = 219
EXPECTED_F1_CONTROL_COUNT = 408
EXPECTED_F2_PAIR_COUNT = 350
EXPECTED_F3_PAIR_COUNT = 2

F1_LEVEL_NAME = "F1_ALL_LONG_PERIOD"
F2_LEVEL_NAME = "F2_ALL_CONFIRMED_PERSISTENT"
F3_LEVEL_NAME = "F3_ALL_LEDGER_BACKED_NONZERO"
F2_CATEGORIES = ("HISTORICAL_SOURCE_POSITIVE", "STATIC_T1")
F3_CATEGORIES = ("EXTINCT", "SPAN_ESCAPE", "ZERO_INITIAL_DEFECT")
METRICS = ("kappa_v", "lambda_e")


def load_phase97_core():
    name = "phase98_phase97_core"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, PHASE97_RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase97 = load_phase97_core()


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


def powerset(categories: tuple[str, ...]) -> list[tuple[str, ...]]:
    return [
        tuple(subset)
        for size in range(len(categories) + 1)
        for subset in itertools.combinations(categories, size)
    ]


def subset_key(categories: Iterable[str]) -> str:
    values = tuple(categories)
    return "EMPTY" if not values else "+".join(values)


def connectivity_values(
    allowed: set[int], component_a: list[int], component_b: list[int]
) -> dict[str, int]:
    vertex = phase97.vertex_connectivity_profile(allowed, component_a, component_b)
    edge = phase97.edge_connectivity_profile(allowed, component_a, component_b)
    if vertex["kappa_v"] > edge["lambda_e"]:
        raise RuntimeError("Undirected connectivity inequality failed")
    return {"kappa_v": vertex["kappa_v"], "lambda_e": edge["lambda_e"]}


def evaluate_category_subsets(
    base_allowed: set[int],
    category_words: dict[str, set[int]],
    categories: tuple[str, ...],
    component_a: list[int],
    component_b: list[int],
    *,
    known_values: dict[tuple[str, ...], dict[str, int]] | None = None,
) -> list[dict[str, Any]]:
    known_values = known_values or {}
    rows = []
    for subset in powerset(categories):
        if subset in known_values:
            values = known_values[subset]
        else:
            allowed = set(base_allowed)
            for category in subset:
                allowed.update(category_words.get(category, set()))
            values = connectivity_values(allowed, component_a, component_b)
        rows.append({"categories": list(subset), **values})
    return rows


def minimal_rescuing_subsets(
    evaluations: list[dict[str, Any]], metric: str
) -> list[list[str]]:
    rescued = [
        frozenset(row["categories"])
        for row in evaluations
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


def classify_f2(minimal_sets: list[list[str]]) -> str:
    normalized = {frozenset(row) for row in minimal_sets}
    historical = frozenset({"HISTORICAL_SOURCE_POSITIVE"})
    static = frozenset({"STATIC_T1"})
    both = historical | static
    if not normalized:
        return "NOT_RESCUED_IN_F2"
    if normalized == {historical}:
        return "RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY"
    if normalized == {static}:
        return "RESCUED_BY_STATIC_T1_ONLY"
    if normalized == {historical, static}:
        return "EITHER_F2_CATEGORY_SUFFICIENT"
    if normalized == {both}:
        return "BOTH_F2_CATEGORIES_REQUIRED"
    raise RuntimeError(f"Unexpected F2 minimal-set family: {minimal_sets}")


def f3_category_roles(
    minimal_sets: list[list[str]], categories: tuple[str, ...] = F3_CATEGORIES
) -> dict[str, dict[str, bool]]:
    sets = [set(row) for row in minimal_sets]
    if not sets:
        return {
            category: {
                "necessary_for_rescue": False,
                "individually_sufficient": False,
                "interaction_only": False,
            }
            for category in categories
        }
    return {
        category: {
            "necessary_for_rescue": all(category in row for row in sets),
            "individually_sufficient": {category} in sets,
            "interaction_only": (
                any(category in row and len(row) >= 2 for row in sets)
                and {category} not in sets
            ),
        }
        for category in categories
    }


def f2_joint_status(vertex_label: str, edge_label: str) -> str:
    vertex = vertex_label != "NOT_RESCUED_IN_F2"
    edge = edge_label != "NOT_RESCUED_IN_F2"
    if vertex and edge:
        return "BOTH_RESCUED"
    if vertex:
        return "VERTEX_ONLY_RESCUED"
    if edge:
        return "EDGE_ONLY_RESCUED"
    return "NEITHER_RESCUED_IN_F2"


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


def validate_phase97_denominators(phase95: dict[str, Any], phase97_data: dict[str, Any]):
    if len(phase95["cube_nodes"]) != EXPECTED_CUBE_COUNT:
        raise RuntimeError("Fase-95 cube denominator mismatch")
    if len(phase97_data["intersections"]) != EXPECTED_INTERSECTION_COUNT:
        raise RuntimeError("Fase-97 intersection denominator mismatch")
    rows = phase97_data["component_pairs"]
    if len(rows) != EXPECTED_PAIR_COUNT:
        raise RuntimeError("Fase-97 pair denominator mismatch")
    counts = Counter(row["earliest_any_path_level"] for row in rows)
    expected = {
        F1_LEVEL_NAME: EXPECTED_F1_PAIR_COUNT,
        F2_LEVEL_NAME: EXPECTED_F2_PAIR_COUNT,
        F3_LEVEL_NAME: EXPECTED_F3_PAIR_COUNT,
    }
    if dict(counts) != expected:
        raise RuntimeError("Fase-97 closure-stratum mismatch")
    f1_rows = [row for row in rows if row["earliest_any_path_level"] == F1_LEVEL_NAME]
    targets = [
        row
        for row in f1_rows
        if row["g_min"]["kappa_v"] == row["g_min"]["lambda_e"] == 1
    ]
    controls = [
        row
        for row in f1_rows
        if row["g_min"]["kappa_v"] >= 2 and row["g_min"]["lambda_e"] >= 2
    ]
    if len(targets) != EXPECTED_F1_TARGET_COUNT:
        raise RuntimeError("Fase-97 F1 target denominator mismatch")
    if len(controls) != EXPECTED_F1_CONTROL_COUNT:
        raise RuntimeError("Fase-97 F1 control denominator mismatch")
    if len(targets) + len(controls) != len(f1_rows):
        raise RuntimeError("Fase-97 contains mixed F1 metric states")
    if any(
        row["g_f3"]["kappa_v"] < 2 or row["g_f3"]["lambda_e"] < 2
        for row in rows
    ):
        raise RuntimeError("Fase-97 G_F3 redundancy replay failed")
    return f1_rows


def build_payload(phase95: dict[str, Any], phase97_data: dict[str, Any]):
    f1_rows = validate_phase97_denominators(phase95, phase97_data)
    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    output_rows = []
    target_rows = []
    control_rows = []
    monotonicity_failures = 0

    for source in f1_rows:
        cube = cubes[source["cube_key"]]
        nodes = cube["nodes"]
        physical_class = source["physical_class_sha256"]
        levels = phase97.node_levels(nodes, physical_class)
        component_a = [int(word, 2) for word in source["left_component_words"]]
        component_b = [int(word, 2) for word in source["right_component_words"]]
        allowed_f1 = phase97.allowed_words(levels, 1)
        allowed_f2 = phase97.allowed_words(levels, 2)
        allowed_f3 = phase97.allowed_words(levels, 3)

        replay_f1 = phase97.graph_profile(
            allowed_f1,
            component_a,
            component_b,
            nodes,
            physical_class,
            run_span_tests=False,
        )
        replay_f3 = phase97.graph_profile(
            allowed_f3,
            component_a,
            component_b,
            nodes,
            physical_class,
            run_span_tests=True,
        )
        if replay_f1 != source["g_min"] or replay_f3 != source["g_f3"]:
            raise RuntimeError(f"Fase-97 field replay mismatch at pair {source['pair_index']}")

        values_f1 = {metric: replay_f1[metric] for metric in METRICS}
        values_f2 = connectivity_values(allowed_f2, component_a, component_b)
        values_f3 = {metric: replay_f3[metric] for metric in METRICS}
        for metric in METRICS:
            if not values_f1[metric] <= values_f2[metric] <= values_f3[metric]:
                monotonicity_failures += 1
        if monotonicity_failures:
            raise RuntimeError("F1/F2/F3 monotonicity gate failed")

        is_target = values_f1["kappa_v"] == values_f1["lambda_e"] == 1
        base = {
            "pair_index": source["pair_index"],
            "physical_class_sha256": physical_class,
            "cube_key": source["cube_key"],
            "cohort": cube["cohort"],
            "rule": cube["rule"],
            "background_index": cube["background_index"],
            "left_component_words": source["left_component_words"],
            "right_component_words": source["right_component_words"],
            "f1": values_f1,
            "f2": values_f2,
            "f3": values_f3,
            "role": "F1_UNIT_BOTTLENECK_TARGET" if is_target else "F1_REDUNDANT_CONTROL",
        }
        if not is_target:
            row = {
                **base,
                "vertex_f2_label": "ALREADY_REDUNDANT_F1",
                "edge_f2_label": "ALREADY_REDUNDANT_F1",
                "f2_joint_status": "ALREADY_REDUNDANT_F1",
                "f2_subset_evaluations": "NOT_APPLICABLE_CONTROL",
                "f3_subset_evaluations": "NOT_APPLICABLE_CONTROL",
            }
            control_rows.append(row)
            output_rows.append(row)
            continue

        category_words = {
            category: {
                word for word, node in enumerate(nodes) if node["category"] == category
            }
            for category in F2_CATEGORIES + F3_CATEGORIES
        }
        f2_known = {
            tuple(): values_f1,
            tuple(F2_CATEGORIES): values_f2,
        }
        f2_evaluations = evaluate_category_subsets(
            allowed_f1,
            category_words,
            F2_CATEGORIES,
            component_a,
            component_b,
            known_values=f2_known,
        )
        f2_minimal = {
            metric: minimal_rescuing_subsets(f2_evaluations, metric)
            for metric in METRICS
        }
        labels = {metric: classify_f2(f2_minimal[metric]) for metric in METRICS}

        f3_details: dict[str, Any] = {}
        metrics_needing_f3 = [
            metric for metric in METRICS if labels[metric] == "NOT_RESCUED_IN_F2"
        ]
        f3_evaluations = None
        if metrics_needing_f3:
            f3_known = {
                tuple(): values_f2,
                tuple(F3_CATEGORIES): values_f3,
            }
            f3_evaluations = evaluate_category_subsets(
                allowed_f2,
                category_words,
                F3_CATEGORIES,
                component_a,
                component_b,
                known_values=f3_known,
            )
        for metric in METRICS:
            if metric not in metrics_needing_f3:
                f3_details[metric] = {
                    "status": "NOT_APPLICABLE_ALREADY_RESCUED_F2",
                    "minimal_rescuing_sets": [],
                    "category_roles": "NOT_APPLICABLE_ALREADY_RESCUED_F2",
                }
                continue
            minimal = minimal_rescuing_subsets(f3_evaluations, metric)
            if not minimal:
                raise RuntimeError("Full F3 failed to rescue a F1 unit bottleneck")
            f3_details[metric] = {
                "status": "RESCUED_IN_F3",
                "minimal_rescuing_sets": minimal,
                "category_roles": f3_category_roles(minimal),
            }

        row = {
            **base,
            "vertex_f2_label": labels["kappa_v"],
            "edge_f2_label": labels["lambda_e"],
            "f2_joint_status": f2_joint_status(
                labels["kappa_v"], labels["lambda_e"]
            ),
            "f2_subset_evaluations": f2_evaluations,
            "f2_minimal_rescuing_sets": f2_minimal,
            "f3_subset_evaluations": (
                f3_evaluations
                if f3_evaluations is not None
                else "NOT_APPLICABLE_ALL_METRICS_RESCUED_F2"
            ),
            "f3_rescue": f3_details,
        }
        target_rows.append(row)
        output_rows.append(row)

    if len(target_rows) != EXPECTED_F1_TARGET_COUNT:
        raise RuntimeError("Final target denominator mismatch")
    if len(control_rows) != EXPECTED_F1_CONTROL_COUNT:
        raise RuntimeError("Final control denominator mismatch")

    f3_role_counts = {
        metric: {
            category: {
                role: sum(
                    row["f3_rescue"][metric]["status"] == "RESCUED_IN_F3"
                    and row["f3_rescue"][metric]["category_roles"][category][role]
                    for row in target_rows
                )
                for role in (
                    "necessary_for_rescue",
                    "individually_sufficient",
                    "interaction_only",
                )
            }
            for category in F3_CATEGORIES
        }
        for metric in METRICS
    }
    f3_evaluated_counts = {
        metric: sum(
            row["f3_rescue"][metric]["status"] == "RESCUED_IN_F3"
            for row in target_rows
        )
        for metric in METRICS
    }
    by_rule = {}
    for rule in sorted({row["rule"] for row in output_rows}):
        rule_targets = [row for row in target_rows if row["rule"] == rule]
        rule_controls = [row for row in control_rows if row["rule"] == rule]
        by_rule[str(rule)] = {
            "target_count": len(rule_targets),
            "control_count": len(rule_controls),
            "vertex_f2_label_counts": distribution(
                row["vertex_f2_label"] for row in rule_targets
            ),
            "edge_f2_label_counts": distribution(
                row["edge_f2_label"] for row in rule_targets
            ),
        }

    singleton_rescue_counts = {
        metric: {
            category: sum(
                next(
                    evaluation[metric]
                    for evaluation in row["f2_subset_evaluations"]
                    if evaluation["categories"] == [category]
                )
                >= 2
                for row in target_rows
            )
            for category in F2_CATEGORIES
        }
        for metric in METRICS
    }
    historical_matches_full_f2 = {
        metric: sum(
            next(
                evaluation[metric]
                for evaluation in row["f2_subset_evaluations"]
                if evaluation["categories"] == ["HISTORICAL_SOURCE_POSITIVE"]
            )
            == row["f2"][metric]
            for row in target_rows
        )
        for metric in METRICS
    }

    summary = {
        "f1_pair_count": len(output_rows),
        "f1_unit_bottleneck_target_count": len(target_rows),
        "f1_redundant_control_count": len(control_rows),
        "excluded_f2_origin_pair_count": EXPECTED_F2_PAIR_COUNT,
        "excluded_f3_origin_pair_count": EXPECTED_F3_PAIR_COUNT,
        "vertex_f2_label_counts_over_219": distribution(
            row["vertex_f2_label"] for row in target_rows
        ),
        "edge_f2_label_counts_over_219": distribution(
            row["edge_f2_label"] for row in target_rows
        ),
        "f2_joint_status_counts_over_219": distribution(
            row["f2_joint_status"] for row in target_rows
        ),
        "f2_singleton_rescue_counts_over_219": singleton_rescue_counts,
        "historical_singleton_exact_full_f2_match_counts": historical_matches_full_f2,
        "target_kappa_v_distribution": {
            level: distribution(row[level]["kappa_v"] for row in target_rows)
            for level in ("f1", "f2", "f3")
        },
        "target_lambda_e_distribution": {
            level: distribution(row[level]["lambda_e"] for row in target_rows)
            for level in ("f1", "f2", "f3")
        },
        "control_kappa_v_distribution": {
            level: distribution(row[level]["kappa_v"] for row in control_rows)
            for level in ("f1", "f2", "f3")
        },
        "control_lambda_e_distribution": {
            level: distribution(row[level]["lambda_e"] for row in control_rows)
            for level in ("f1", "f2", "f3")
        },
        "f3_category_role_counts_over_targets": f3_role_counts,
        "f3_evaluated_target_count_by_metric": f3_evaluated_counts,
        "by_rule": by_rule,
        "phase97_replay_status": "EXACT_F1_AND_F3_FIELD_REPLAY",
        "monotonicity_failure_count": monotonicity_failures,
        "reconciliation_failure_count": 0,
        "simulation_executed": False,
        "external_ledger_read": False,
    }
    return {
        "phase": 98,
        "status": "BOTTLENECK_RESCUE_FILTRATION_MAPPED",
        "sources": {
            "phase95_raw_sha256": EXPECTED_PHASE95_RAW_SHA256,
            "phase95_canonical_sha256": EXPECTED_PHASE95_CANONICAL_SHA256,
            "phase97_raw_sha256": EXPECTED_PHASE97_RAW_SHA256,
            "phase97_canonical_sha256": EXPECTED_PHASE97_CANONICAL_SHA256,
        },
        "protocol": {
            "universe": "627_FIRST_CLOSING_F1_PAIRS",
            "targets": "219_F1_KAPPA_AND_LAMBDA_UNIT_BOTTLENECKS",
            "controls": "408_ALREADY_REDUNDANT_F1_PAIRS",
            "f2_subsets": [list(row) for row in powerset(F2_CATEGORIES)],
            "f3_subsets": [list(row) for row in powerset(F3_CATEGORIES)],
            "minimality": "ALL_INCLUSION_MINIMAL_RESCUING_SUBSETS",
            "graph": "UNDIRECTED_Q8_HAMMING_1_INTERVENTION_GRAPH",
            "zero_word_policy": "EXCLUDED",
            "simulation_executed": False,
            "external_ledger_read": False,
        },
        "summary": summary,
        "pairs": output_rows,
        "methodological_limits": [
            "Only the 627 first-closing F1 pairs in the 48 frozen Q8 cubes are eligible.",
            "Rescue counts use 219 targets; 408 controls are never mixed into that denominator.",
            "Category subsets identify topological sufficiency/necessity, not temporal causality.",
            "The zero word and all F4 claims remain excluded.",
            "No claim is made about universal WIDTH=256 basin connectivity.",
        ],
    }


def render_report(
    payload: dict[str, Any], output_raw_sha256: str, output_canonical_sha256: str
) -> str:
    summary = payload["summary"]
    lines = [
        "# Fase 98 - F1 bottleneck rescue filtration",
        "",
        "## Question",
        "",
        "Which F2/F3 state families remove the 219 unit bottlenecks observed among the 627 first-closing F1 component pairs?",
        "",
        "## Frozen inputs and gates",
        "",
        f"- Fase-95 raw/canonical: `{payload['sources']['phase95_raw_sha256']}` / `{payload['sources']['phase95_canonical_sha256']}`",
        f"- Fase-97 raw/canonical: `{payload['sources']['phase97_raw_sha256']}` / `{payload['sources']['phase97_canonical_sha256']}`",
        f"- Fase-98 result raw/canonical: `{output_raw_sha256}` / `{output_canonical_sha256}`",
        f"- Replay: `{summary['phase97_replay_status']}`",
        f"- Monotonicity/reconciliation failures: {summary['monotonicity_failure_count']}/{summary['reconciliation_failure_count']}",
        "",
        "## Denominators",
        "",
        f"- Eligible first-closing F1 pairs: {summary['f1_pair_count']}",
        f"- Unit-bottleneck targets: {summary['f1_unit_bottleneck_target_count']}",
        f"- Already-redundant controls: {summary['f1_redundant_control_count']}",
        f"- Excluded pairs born at F2/F3: {summary['excluded_f2_origin_pair_count']}/{summary['excluded_f3_origin_pair_count']}",
        "",
        "Targets and controls are never mixed into one rescue percentage.",
        "",
        "## F2 rescue over 219 targets",
        "",
        f"- Vertex labels: `{json.dumps(summary['vertex_f2_label_counts_over_219'], sort_keys=True)}`",
        f"- Edge labels: `{json.dumps(summary['edge_f2_label_counts_over_219'], sort_keys=True)}`",
        f"- Joint status: `{json.dumps(summary['f2_joint_status_counts_over_219'], sort_keys=True)}`",
        f"- Singleton rescue counts: `{json.dumps(summary['f2_singleton_rescue_counts_over_219'], sort_keys=True)}`",
        f"- Historical singleton exactly matches full F2: `{json.dumps(summary['historical_singleton_exact_full_f2_match_counts'], sort_keys=True)}`",
        "",
        "## Connectivity evolution",
        "",
        f"- Target kappa_v F1/F2/F3: `{json.dumps(summary['target_kappa_v_distribution'], sort_keys=True)}`",
        f"- Target lambda_e F1/F2/F3: `{json.dumps(summary['target_lambda_e_distribution'], sort_keys=True)}`",
        f"- Control kappa_v F1/F2/F3: `{json.dumps(summary['control_kappa_v_distribution'], sort_keys=True)}`",
        f"- Control lambda_e F1/F2/F3: `{json.dumps(summary['control_lambda_e_distribution'], sort_keys=True)}`",
        "",
        "## F3 category roles over targets not rescued in F2",
        "",
        f"- Evaluated targets by metric: `{json.dumps(summary['f3_evaluated_target_count_by_metric'], sort_keys=True)}`",
        "- A zero here means NOT_APPLICABLE because F2 already rescued the metric; it is not a tested F3 failure.",
        "",
    ]
    for metric, categories in summary["f3_category_role_counts_over_targets"].items():
        lines.append(f"- {metric}: `{json.dumps(categories, sort_keys=True)}`")
    lines.extend(
        [
            "",
            "## By rule",
            "",
            "| rule | targets | controls | vertex F2 labels | edge F2 labels |",
            "|---:|---:|---:|---|---|",
        ]
    )
    for rule, row in summary["by_rule"].items():
        lines.append(
            f"| {rule} | {row['target_count']} | {row['control_count']} | "
            f"{json.dumps(row['vertex_f2_label_counts'], sort_keys=True)} | "
            f"{json.dumps(row['edge_f2_label_counts'], sort_keys=True)} |"
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
    phase97_data = read_and_gate(
        PHASE97_PATH,
        EXPECTED_PHASE97_RAW_SHA256,
        EXPECTED_PHASE97_CANONICAL_SHA256,
    )
    first = build_payload(phase95, phase97_data)
    second = build_payload(phase95, phase97_data)
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
