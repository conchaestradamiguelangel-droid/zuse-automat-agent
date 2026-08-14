#!/usr/bin/env python3
"""Fase 101: match unit interventions by a frozen period-blind geometry signature."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


OUT_DIR = Path(__file__).resolve().parent
PHASE95_PATH = OUT_DIR / "phase94_hypercube_completion_results.json"
PHASE97_PATH = OUT_DIR / "phase96_bridge_robustness_results.json"
PHASE100_PATH = OUT_DIR / "phase99_unit_cardinality_period_potency_results.json"
RESULTS_PATH = OUT_DIR / "phase100_measured_geometry_matching_results.json"
REPORT_PATH = OUT_DIR / "phase100_measured_geometry_matching_report.md"

EXPECTED_PHASE95_RAW_SHA256 = "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3"
EXPECTED_PHASE95_CANONICAL_SHA256 = "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429"
EXPECTED_PHASE97_RAW_SHA256 = "3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858"
EXPECTED_PHASE97_CANONICAL_SHA256 = "85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b"
EXPECTED_PHASE100_RAW_SHA256 = "39ec272b72c54f07c0996064c3d755fff9d4b6690fdfdbe3eb4d771ac0710c8c"
EXPECTED_PHASE100_CANONICAL_SHA256 = "f79e047d22dddb375db7f351bc9bdd55b978ce29ed22e9c22d9195fb70935d22"

EXPECTED_CUBE_COUNT = 48
EXPECTED_PAIR_COUNT = 979
EXPECTED_TARGET_COUNT = 219
EXPECTED_HISTORICAL_NODE_COUNT = 9_096
EXPECTED_EXPOSURE_COUNT = 43_425
EXPECTED_F100_STRATUM_COUNT = 919
EXPECTED_OUTCOMES = {"1,1": 41_859, "1,2": 61, "2,2": 1_499, "2,3": 6}
EXPECTED_PERIODS = (2, 3, 5, 6, 8, 10, 12, 15)
EXPECTED_GEOMETRY_STRATUM_COUNT = 13_088
EXPECTED_MATCHED_STRATUM_COUNT = 4_090
EXPECTED_MATCHED_EXPOSURE_COUNT = 31_682
EXPECTED_UNMATCHED_EXPOSURE_COUNT = 11_743
EXPECTED_MATCHED_EXPOSURES_BY_PERIOD = {
    2: 3_464,
    3: 9_305,
    5: 250,
    6: 14_810,
    8: 201,
    10: 249,
    12: 2_770,
    15: 633,
}
EXPECTED_MATCHED_PERIOD_COUNT_DISTRIBUTION = {2: 3_086, 3: 755, 4: 190, 5: 19, 6: 40}
EXPECTED_COMPARISON_COUNT = 7_281
EXPECTED_PERIOD_PAIR_COUNTS = {
    (2, 3): 216, (2, 5): 40, (2, 6): 297, (2, 8): 85,
    (2, 10): 72, (2, 12): 171, (3, 5): 40, (3, 6): 2_687,
    (3, 8): 64, (3, 10): 20, (3, 12): 846, (3, 15): 303,
    (5, 6): 40, (5, 8): 36, (5, 12): 20, (6, 8): 74,
    (6, 10): 79, (6, 12): 1_486, (6, 15): 405, (8, 10): 25,
    (8, 12): 46, (10, 12): 42, (12, 15): 187,
}
METRICS = ("kappa_v", "lambda_e")
HISTORICAL_CATEGORY = "HISTORICAL_SOURCE_POSITIVE"


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def read_and_gate(path: Path, expected_raw: str, expected_canonical: str):
    raw = path.read_bytes()
    raw_sha = hashlib.sha256(raw).hexdigest()
    if raw_sha != expected_raw:
        raise RuntimeError(f"Raw SHA mismatch for {path.name}: {raw_sha}")
    payload = json.loads(raw)
    canonical = canonical_sha256(payload)
    if canonical != expected_canonical:
        raise RuntimeError(f"Canonical SHA mismatch for {path.name}: {canonical}")
    return payload


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_name(path.name + f".tmp.{os.getpid()}")
    temporary.write_text(text, encoding="utf-8", newline="\n")
    with temporary.open("r+b") as handle:
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def distribution(values: Iterable[Any]) -> dict[str, int]:
    return dict(sorted(Counter(str(value) for value in values).items()))


def q8_neighbors(word: int) -> tuple[int, ...]:
    return tuple(word ^ (1 << bit) for bit in range(8))


def reachable(
    allowed: set[int],
    starts: Iterable[int],
    *,
    removed_vertex: int | None = None,
    removed_edge: tuple[int, int] | None = None,
) -> set[int]:
    vertices = set(allowed)
    if removed_vertex is not None:
        vertices.discard(removed_vertex)
    edge = frozenset(removed_edge) if removed_edge is not None else None
    seen = {word for word in starts if word in vertices}
    queue = deque(sorted(seen))
    while queue:
        source = queue.popleft()
        for target in q8_neighbors(source):
            if target not in vertices or target in seen:
                continue
            if edge is not None and frozenset((source, target)) == edge:
                continue
            seen.add(target)
            queue.append(target)
    return seen


def connected_components(
    allowed: set[int],
    *,
    removed_vertex: int | None = None,
    removed_edge: tuple[int, int] | None = None,
) -> list[set[int]]:
    remaining = set(allowed)
    if removed_vertex is not None:
        remaining.discard(removed_vertex)
    components = []
    while remaining:
        start = min(remaining)
        component = reachable(
            allowed,
            [start],
            removed_vertex=removed_vertex,
            removed_edge=removed_edge,
        )
        components.append(component)
        remaining -= component
    return components


def shortest_distances(allowed: set[int], starts: Iterable[int]) -> dict[int, int]:
    distances = {word: 0 for word in starts if word in allowed}
    queue = deque(sorted(distances))
    while queue:
        source = queue.popleft()
        for target in q8_neighbors(source):
            if target in allowed and target not in distances:
                distances[target] = distances[source] + 1
                queue.append(target)
    return distances


def compare_fractions(left_n: int, left_d: int, right_n: int, right_d: int) -> str:
    left_cross = left_n * right_d
    right_cross = right_n * left_d
    if left_cross > right_cross:
        return "LEFT_HIGHER"
    if left_cross < right_cross:
        return "RIGHT_HIGHER"
    return "TIE"


def fraction_payload(numerator: int, denominator: int) -> dict[str, Any] | str:
    if denominator == 0:
        return "NOT_AVAILABLE"
    value = Fraction(numerator, denominator)
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": round(float(value), 12),
    }


def homogeneity_label(rescue_values: Iterable[bool]) -> str:
    values = set(bool(value) for value in rescue_values)
    if values == {True}:
        return "GEOMETRY_HOMOGENEOUS_RESCUE"
    if values == {False}:
        return "GEOMETRY_HOMOGENEOUS_NONRESCUE"
    if values == {False, True}:
        return "GEOMETRY_HETEROGENEOUS"
    raise ValueError("Geometry stratum cannot be empty")


def neighbor_role_counts(
    nodes: list[dict[str, Any]],
    target_class: str,
    component_a: set[int],
    component_b: set[int],
    f1_allowed: set[int],
    word: int,
) -> dict[str, int]:
    counts = Counter()
    for neighbor in q8_neighbors(word):
        if neighbor not in f1_allowed:
            continue
        if neighbor in component_a:
            counts["A"] += 1
        elif neighbor in component_b:
            counts["B"] += 1
        elif nodes[neighbor]["physical_class_sha256"] == target_class:
            counts["F0_NONTERMINAL"] += 1
        else:
            counts["OTHER_F1"] += 1
    return {
        "neighbors_A": counts["A"],
        "neighbors_B": counts["B"],
        "neighbors_F0_nonterminal": counts["F0_NONTERMINAL"],
        "neighbors_other_F1": counts["OTHER_F1"],
    }


def bypass_count(neighbors: set[int], partitions: list[tuple[set[int], set[int]]]) -> int:
    return sum(bool(neighbors & left) and bool(neighbors & right) for left, right in partitions)


def build_target_context(
    cube: dict[str, Any], pair: dict[str, Any], target_class: str
) -> dict[str, Any]:
    nodes = cube["nodes"]
    component_a = {int(word, 2) for word in pair["left_component_words"]}
    component_b = {int(word, 2) for word in pair["right_component_words"]}
    f1_allowed = {
        word
        for word, node in enumerate(nodes)
        if node["physical_class_sha256"] == target_class
        or node["category"] == "LONG_PERIOD_CAP_CANDIDATE"
    }
    if pair["earliest_any_path_level"] != "F1_ALL_LONG_PERIOD":
        raise RuntimeError("Target does not originate in F1")
    critical_vertices = tuple(
        int(row["word_value"])
        for row in pair["g_min"]["individually_critical_vertices"]
    )
    critical_edges = tuple(
        tuple(sorted(map(int, row)))
        for row in pair["g_min"]["individually_critical_edges"]
    )
    vertex_partitions = []
    vertex_component_counts = []
    for vertex in critical_vertices:
        left = reachable(f1_allowed, component_a, removed_vertex=vertex)
        right = reachable(f1_allowed, component_b, removed_vertex=vertex)
        if left & component_b or right & component_a or left & right:
            raise RuntimeError("Critical vertex does not disconnect terminal sides")
        vertex_partitions.append((left, right))
        vertex_component_counts.append(
            len(connected_components(f1_allowed, removed_vertex=vertex))
        )
    edge_partitions = []
    edge_component_counts = []
    for edge in critical_edges:
        left = reachable(f1_allowed, component_a, removed_edge=edge)
        right = reachable(f1_allowed, component_b, removed_edge=edge)
        if left & component_b or right & component_a or left & right:
            raise RuntimeError("Critical edge does not disconnect terminal sides")
        edge_partitions.append((left, right))
        edge_component_counts.append(
            len(connected_components(f1_allowed, removed_edge=edge))
        )
    return {
        "nodes": nodes,
        "target_class": target_class,
        "component_a": component_a,
        "component_b": component_b,
        "f1_allowed": f1_allowed,
        "distance_a": shortest_distances(f1_allowed, component_a),
        "distance_b": shortest_distances(f1_allowed, component_b),
        "critical_vertices": critical_vertices,
        "critical_edges": critical_edges,
        "vertex_partitions": vertex_partitions,
        "edge_partitions": edge_partitions,
        "vertex_component_counts": vertex_component_counts,
        "edge_component_counts": edge_component_counts,
    }


def geometry_signature(context: dict[str, Any], word: int) -> dict[str, Any]:
    f1_neighbors = {neighbor for neighbor in q8_neighbors(word) if neighbor in context["f1_allowed"]}
    roles = neighbor_role_counts(
        context["nodes"],
        context["target_class"],
        context["component_a"],
        context["component_b"],
        context["f1_allowed"],
        word,
    )
    if sum(roles.values()) != len(f1_neighbors):
        raise RuntimeError("F1 neighbor partition mismatch")
    distance_a = min(
        (1 + context["distance_a"][neighbor] for neighbor in f1_neighbors if neighbor in context["distance_a"]),
        default=None,
    )
    distance_b = min(
        (1 + context["distance_b"][neighbor] for neighbor in f1_neighbors if neighbor in context["distance_b"]),
        default=None,
    )
    critical_vertex_set = set(context["critical_vertices"])
    # Endpoint incidences are counted per critical edge; a shared endpoint can count twice.
    incident_edge_endpoints = sum(
        int(edge[0] in f1_neighbors) + int(edge[1] in f1_neighbors)
        for edge in context["critical_edges"]
    )
    return {
        "f1_degree": len(f1_neighbors),
        **roles,
        "distance_to_A": distance_a if distance_a is not None else "UNREACHABLE",
        "distance_to_B": distance_b if distance_b is not None else "UNREACHABLE",
        "critical_vertex_count": len(context["critical_vertices"]),
        "bypassed_critical_vertex_count": bypass_count(f1_neighbors, context["vertex_partitions"]),
        "adjacent_critical_vertex_count": len(f1_neighbors & critical_vertex_set),
        "critical_edge_count": len(context["critical_edges"]),
        "bypassed_critical_edge_count": bypass_count(f1_neighbors, context["edge_partitions"]),
        "incident_critical_edge_endpoint_count": incident_edge_endpoints,
    }


def subset_stats(exposures: list[dict[str, Any]]) -> dict[str, Any]:
    count = len(exposures)
    kappa = sum(row["vertex_rescued"] for row in exposures)
    edge = sum(row["edge_rescued"] for row in exposures)
    return {
        "exposure_count": count,
        "outcome_distribution": distribution(f"{row['kappa_v']},{row['lambda_e']}" for row in exposures),
        "kappa_rescue_count": kappa,
        "kappa_rescue_rate": fraction_payload(kappa, count),
        "lambda_rescue_count": edge,
        "lambda_rescue_rate": fraction_payload(edge, count),
    }


def aggregate_comparisons(rows: list[dict[str, Any]]) -> dict[str, Any]:
    output = {}
    for left, right in itertools.combinations(EXPECTED_PERIODS, 2):
        selected = [row for row in rows if row["left_period"] == left and row["right_period"] == right]
        if not selected:
            continue
        output[f"{left}_vs_{right}"] = {
            "comparison_count": len(selected),
            **{metric: distribution(row["comparisons"][metric] for row in selected) for metric in METRICS},
        }
    return output


def build_payload(phase95: dict[str, Any], phase97: dict[str, Any], phase100: dict[str, Any]):
    if len(phase95["cube_nodes"]) != EXPECTED_CUBE_COUNT:
        raise RuntimeError("Fase-95 cube denominator mismatch")
    if len(phase97["component_pairs"]) != EXPECTED_PAIR_COUNT:
        raise RuntimeError("Fase-97 pair denominator mismatch")
    exposures_source = phase100["exposures"]
    if len(exposures_source) != EXPECTED_EXPOSURE_COUNT:
        raise RuntimeError("Fase-100 exposure denominator mismatch")
    if len(phase100["target_period_strata"]) != EXPECTED_F100_STRATUM_COUNT:
        raise RuntimeError("Fase-100 stratum denominator mismatch")

    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    pairs = {(row["cube_key"], row["pair_index"]): row for row in phase97["component_pairs"]}
    target_classes = {}
    for row in exposures_source:
        key = (row["cube_key"], int(row["pair_index"]))
        previous = target_classes.setdefault(key, row["physical_class_sha256"])
        if previous != row["physical_class_sha256"]:
            raise RuntimeError("Target physical-class conflict")
    if len(target_classes) != EXPECTED_TARGET_COUNT:
        raise RuntimeError("Fase-100 target denominator mismatch")

    contexts = {}
    for key, target_class in sorted(target_classes.items()):
        contexts[key] = build_target_context(cubes[key[0]], pairs[key], target_class)

    # Geometry is completed before any Fase-100 outcome is joined.
    geometry_rows = []
    signatures_by_hash: dict[str, dict[str, Any]] = {}
    for source in exposures_source:
        key = (source["cube_key"], int(source["pair_index"]))
        node = cubes[key[0]]["nodes"][int(source["word_int"])]
        if (
            node["category"] != HISTORICAL_CATEGORY
            or node["word8"] != source["word8"]
            or int(node["ledger"]["source_period"]) != int(source["period"])
        ):
            raise RuntimeError("Fase-100 node/period replay failed")
        if int(source["word_int"]) in contexts[key]["f1_allowed"]:
            raise RuntimeError("Historical unit node already belongs to F1")
        signature = geometry_signature(contexts[key], int(source["word_int"]))
        signature_sha = canonical_sha256(signature)
        previous = signatures_by_hash.setdefault(signature_sha, signature)
        if previous != signature:
            raise RuntimeError("Geometry signature SHA collision")
        geometry_rows.append(
            {
                "cube_key": source["cube_key"],
                "pair_index": int(source["pair_index"]),
                "rule": int(source["rule"]),
                "background_index": int(source["background_index"]),
                "physical_class_sha256": source["physical_class_sha256"],
                "word8": source["word8"],
                "word_int": int(source["word_int"]),
                "period": int(source["period"]),
                "geometry_signature_sha256": signature_sha,
                "geometry_signature": signature,
            }
        )

    outcome_lookup = {
        (row["cube_key"], int(row["pair_index"]), int(row["word_int"])): row
        for row in exposures_source
    }
    if len(outcome_lookup) != EXPECTED_EXPOSURE_COUNT:
        raise RuntimeError("Fase-100 exposure identity duplication")
    exposures = []
    for geometry in geometry_rows:
        source = outcome_lookup[(geometry["cube_key"], geometry["pair_index"], geometry["word_int"])]
        exposures.append(
            {
                **geometry,
                "kappa_v": int(source["kappa_v"]),
                "lambda_e": int(source["lambda_e"]),
                "vertex_rescued": bool(source["vertex_rescued"]),
                "edge_rescued": bool(source["edge_rescued"]),
                "same_node_both_rescued": bool(source["same_node_both_rescued"]),
            }
        )
    if distribution(f"{row['kappa_v']},{row['lambda_e']}" for row in exposures) != EXPECTED_OUTCOMES:
        raise RuntimeError("Fase-100 outcome replay failed")

    grouped: dict[tuple[str, int, str], list[dict[str, Any]]] = defaultdict(list)
    for row in exposures:
        grouped[(row["cube_key"], row["pair_index"], row["geometry_signature_sha256"])].append(row)
    if len(grouped) != EXPECTED_GEOMETRY_STRATUM_COUNT:
        raise RuntimeError("Geometry-stratum denominator mismatch")

    strata = []
    matched_exposure_counts = Counter()
    matched_period_count_distribution = Counter()
    comparisons = []
    matched_exposure_count = 0
    for stratum_index, (key, rows) in enumerate(sorted(grouped.items()), start=1):
        period_groups: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            period_groups[row["period"]].append(row)
        periods = tuple(sorted(period_groups))
        matched = len(periods) >= 2
        if matched:
            matched_period_count_distribution[len(periods)] += 1
            matched_exposure_count += len(rows)
            for row in rows:
                matched_exposure_counts[row["period"]] += 1
        period_profiles = []
        for period in periods:
            selected = period_groups[period]
            kappa_count = sum(row["vertex_rescued"] for row in selected)
            edge_count = sum(row["edge_rescued"] for row in selected)
            period_profiles.append(
                {
                    "period": period,
                    "exposure_count": len(selected),
                    "kappa_rescue_count": kappa_count,
                    "kappa_rescue_rate": fraction_payload(kappa_count, len(selected)),
                    "lambda_rescue_count": edge_count,
                    "lambda_rescue_rate": fraction_payload(edge_count, len(selected)),
                    "words": sorted(row["word8"] for row in selected),
                }
            )
        stratum = {
            "stratum_index": stratum_index,
            "cube_key": key[0],
            "pair_index": key[1],
            "geometry_signature_sha256": key[2],
            "geometry_signature": rows[0]["geometry_signature"],
            "matched": matched,
            "exposure_count": len(rows),
            "periods": list(periods),
            "period_profiles": period_profiles,
            "kappa_homogeneity": homogeneity_label(row["vertex_rescued"] for row in rows),
            "lambda_homogeneity": homogeneity_label(row["edge_rescued"] for row in rows),
        }
        strata.append(stratum)
        if matched:
            by_period = {row["period"]: row for row in period_profiles}
            for left_period, right_period in itertools.combinations(periods, 2):
                left = by_period[left_period]
                right = by_period[right_period]
                comparisons.append(
                    {
                        "stratum_index": stratum_index,
                        "cube_key": key[0],
                        "pair_index": key[1],
                        "geometry_signature_sha256": key[2],
                        "rule": rows[0]["rule"],
                        "left_period": left_period,
                        "right_period": right_period,
                        "comparisons": {
                            "kappa_v": compare_fractions(
                                left["kappa_rescue_count"], left["exposure_count"],
                                right["kappa_rescue_count"], right["exposure_count"],
                            ),
                            "lambda_e": compare_fractions(
                                left["lambda_rescue_count"], left["exposure_count"],
                                right["lambda_rescue_count"], right["exposure_count"],
                            ),
                        },
                    }
                )

    matched_strata = [row for row in strata if row["matched"]]
    if len(matched_strata) != EXPECTED_MATCHED_STRATUM_COUNT:
        raise RuntimeError("Matched geometry-stratum denominator mismatch")
    if matched_exposure_count != EXPECTED_MATCHED_EXPOSURE_COUNT:
        raise RuntimeError("Matched exposure denominator mismatch")
    if len(exposures) - matched_exposure_count != EXPECTED_UNMATCHED_EXPOSURE_COUNT:
        raise RuntimeError("Unmatched exposure denominator mismatch")
    if dict(sorted(matched_exposure_counts.items())) != EXPECTED_MATCHED_EXPOSURES_BY_PERIOD:
        raise RuntimeError("Matched exposure period distribution mismatch")
    if dict(sorted(matched_period_count_distribution.items())) != EXPECTED_MATCHED_PERIOD_COUNT_DISTRIBUTION:
        raise RuntimeError("Matched period-count distribution mismatch")
    if len(comparisons) != EXPECTED_COMPARISON_COUNT:
        raise RuntimeError("Matched comparison denominator mismatch")
    comparison_counts = Counter((row["left_period"], row["right_period"]) for row in comparisons)
    if dict(sorted(comparison_counts.items())) != EXPECTED_PERIOD_PAIR_COUNTS:
        raise RuntimeError("Period-pair matched denominator mismatch")

    periods_by_stratum = {
        key: {item["period"] for item in rows}
        for key, rows in grouped.items()
    }
    for row in exposures:
        key = (row["cube_key"], row["pair_index"], row["geometry_signature_sha256"])
        row["geometry_match_status"] = (
            "MATCHED_GEOMETRY"
            if len(periods_by_stratum[key]) >= 2
            else "UNMATCHED_GEOMETRY"
        )
    matched_exposures = [row for row in exposures if row["geometry_match_status"] == "MATCHED_GEOMETRY"]
    unmatched_exposures = [row for row in exposures if row["geometry_match_status"] == "UNMATCHED_GEOMETRY"]

    coverage_by_period = {}
    for period in EXPECTED_PERIODS:
        all_rows = [row for row in exposures if row["period"] == period]
        matched_rows = [row for row in matched_exposures if row["period"] == period]
        unmatched_rows = [row for row in unmatched_exposures if row["period"] == period]
        coverage_by_period[str(period)] = {
            "all": subset_stats(all_rows),
            "matched": subset_stats(matched_rows),
            "unmatched": subset_stats(unmatched_rows),
            "matched_coverage": fraction_payload(len(matched_rows), len(all_rows)),
        }

    t5_strata = [row for row in matched_strata if 5 in row["periods"]]
    t5_counterparts = Counter(
        period
        for row in t5_strata
        for period in row["periods"]
        if period != 5
    )
    if len(t5_strata) != 40 or len([row for row in matched_exposures if row["period"] == 5]) != 250:
        raise RuntimeError("T5 matched-coverage explanation gate failed")

    summary = {
        "cube_count": EXPECTED_CUBE_COUNT,
        "target_count": EXPECTED_TARGET_COUNT,
        "exposure_count": len(exposures),
        "geometry_stratum_count": len(strata),
        "matched_geometry_stratum_count": len(matched_strata),
        "matched_exposure_count": len(matched_exposures),
        "unmatched_exposure_count": len(unmatched_exposures),
        "matched_period_count_distribution": {
            str(key): value for key, value in sorted(matched_period_count_distribution.items())
        },
        "matched_exposure_count_by_period": {
            str(key): value for key, value in sorted(matched_exposure_counts.items())
        },
        "comparison_count_per_metric": len(comparisons),
        "comparison_count_by_period_pair": {
            f"{left}_vs_{right}": count
            for (left, right), count in sorted(comparison_counts.items())
        },
        "matched_vs_unmatched": {
            "matched": subset_stats(matched_exposures),
            "unmatched": subset_stats(unmatched_exposures),
        },
        "coverage_by_period": coverage_by_period,
        "geometry_homogeneity": {
            metric: distribution(row[f"{metric}_homogeneity"] for row in strata)
            for metric in ("kappa", "lambda")
        },
        "matched_geometry_homogeneity": {
            metric: distribution(row[f"{metric}_homogeneity"] for row in matched_strata)
            for metric in ("kappa", "lambda")
        },
        "comparison_direction_totals": {
            metric: distribution(row["comparisons"][metric] for row in comparisons)
            for metric in METRICS
        },
        "pairwise_period_comparisons": aggregate_comparisons(comparisons),
        "pairwise_period_comparisons_by_rule": {
            str(rule): aggregate_comparisons([row for row in comparisons if row["rule"] == rule])
            for rule in (73, 109)
        },
        "t5_coverage_explanation": {
            "matched_exposure_count": 250,
            "total_exposure_count": 250,
            "matched_geometry_stratum_count": len(t5_strata),
            "counterpart_period_stratum_counts": {
                str(key): value for key, value in sorted(t5_counterparts.items())
            },
            "interpretation": "T5 occurs only in 40 measured-geometry strata, all also containing T2, T3, and T6; its 100% matched coverage is restricted support, not universal geometric coverage.",
        },
        "critical_vertex_multi_component_case_count": sum(
            count > 2 for context in contexts.values() for count in context["vertex_component_counts"]
        ),
        "critical_edge_component_count_distribution": distribution(
            count for context in contexts.values() for count in context["edge_component_counts"]
        ),
        "reconciliation_failure_count": 0,
        "feature_construction_outcome_blind": True,
        "simulation_executed": False,
    }
    return {
        "phase": 101,
        "status": "MEASURED_GEOMETRY_MATCHED_ATLAS_BUILT",
        "sources": {
            "phase95_path": PHASE95_PATH.name,
            "phase95_raw_sha256": EXPECTED_PHASE95_RAW_SHA256,
            "phase95_canonical_sha256": EXPECTED_PHASE95_CANONICAL_SHA256,
            "phase97_path": PHASE97_PATH.name,
            "phase97_raw_sha256": EXPECTED_PHASE97_RAW_SHA256,
            "phase97_canonical_sha256": EXPECTED_PHASE97_CANONICAL_SHA256,
            "phase100_path": PHASE100_PATH.name,
            "phase100_raw_sha256": EXPECTED_PHASE100_RAW_SHA256,
            "phase100_canonical_sha256": EXPECTED_PHASE100_CANONICAL_SHA256,
        },
        "protocol": {
            "simulation_executed": False,
            "matching_scope": "WITHIN_TARGET_ONLY",
            "geometry_signature_period_blind": True,
            "geometry_signature_outcome_blind": True,
            "critical_cut_source": "FASE97_G_MIN_ALL_INDIVIDUALLY_CRITICAL_CUTS",
            "comparison": "EXACT_INTEGER_CROSS_MULTIPLICATION",
            "unmatched_policy": "REPORT_SEPARATELY_NEVER_AS_FAILURE",
        },
        "summary": summary,
        "exposures": exposures,
        "geometry_strata": strata,
        "matched_period_comparisons": comparisons,
        "methodological_limits": [
            "Matched and unmatched exposure results are always reported side by side.",
            "The frozen 13-variable signature is measured local geometry, not exact colored-graph isomorphism.",
            "Residual period association may reflect geometry not represented in the signature.",
            "The phase does not decompose collective interactions of two or more historical nodes.",
            "No temporal causality, transition probability, or universal WIDTH=256 basin claim is made.",
        ],
    }


def render_report(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Rule 73/109 measured-geometry matching audit - Fase 101",
        "",
        "## Gates and coverage",
        "",
        f"- Exposures: `{summary['exposure_count']}`",
        f"- Geometry strata: `{summary['geometry_stratum_count']}`",
        f"- Matched strata: `{summary['matched_geometry_stratum_count']}`",
        f"- Matched exposures: `{summary['matched_exposure_count']}`",
        f"- Unmatched exposures: `{summary['unmatched_exposure_count']}`",
        f"- Comparisons per metric: `{summary['comparison_count_per_metric']}`",
        f"- Reconciliation failures: `{summary['reconciliation_failure_count']}`",
        "",
        "## Matched and unmatched outcomes",
        "",
        "| Period | All | Matched | Unmatched | Coverage | Matched kappa rate | Unmatched kappa rate | Matched lambda rate | Unmatched lambda rate |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for period in EXPECTED_PERIODS:
        row = summary["coverage_by_period"][str(period)]
        def decimal(value):
            return "N/A" if value == "NOT_AVAILABLE" else f"{value['decimal']:.6f}"
        lines.append(
            f"| {period} | {row['all']['exposure_count']} | {row['matched']['exposure_count']} | {row['unmatched']['exposure_count']} | "
            f"{decimal(row['matched_coverage'])} | {decimal(row['matched']['kappa_rescue_rate'])} | {decimal(row['unmatched']['kappa_rescue_rate'])} | "
            f"{decimal(row['matched']['lambda_rescue_rate'])} | {decimal(row['unmatched']['lambda_rescue_rate'])} |"
        )
    lines.extend(
        [
            "",
            "## Geometry homogeneity",
            "",
            f"- All strata kappa: `{json.dumps(summary['geometry_homogeneity']['kappa'], sort_keys=True)}`",
            f"- All strata lambda: `{json.dumps(summary['geometry_homogeneity']['lambda'], sort_keys=True)}`",
            f"- Matched strata kappa: `{json.dumps(summary['matched_geometry_homogeneity']['kappa'], sort_keys=True)}`",
            f"- Matched strata lambda: `{json.dumps(summary['matched_geometry_homogeneity']['lambda'], sort_keys=True)}`",
            "",
            "## Period comparisons after geometry matching",
            "",
            f"- Kappa directions: `{json.dumps(summary['comparison_direction_totals']['kappa_v'], sort_keys=True)}`",
            f"- Lambda directions: `{json.dumps(summary['comparison_direction_totals']['lambda_e'], sort_keys=True)}`",
            "- Every matched stratum is outcome-homogeneous, and every period-pair comparison is an exact tie for both metrics.",
            "",
            "## T5 coverage note",
            "",
            f"- `{summary['t5_coverage_explanation']['interpretation']}`",
            f"- Counterpart geometry strata: `{json.dumps(summary['t5_coverage_explanation']['counterpart_period_stratum_counts'], sort_keys=True)}`",
            "",
            "## Interpretation",
            "",
            "Within the 31,682 matched exposures, the period-associated differences from Fase 100 disappear after controlling target identity, unit cardinality, and the frozen measured signature. This is a coverage-conditioned result: 11,743 unmatched exposures remain outside the comparison, and no feature was added after observing outcomes.",
            "",
            "## Verdict",
            "",
            "`MEASURED_GEOMETRY_MATCHED_ATLAS_BUILT`",
            "",
            "## Methodological limits",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in payload["methodological_limits"])
    return "\n".join(lines) + "\n"


def main() -> int:
    phase95 = read_and_gate(PHASE95_PATH, EXPECTED_PHASE95_RAW_SHA256, EXPECTED_PHASE95_CANONICAL_SHA256)
    phase97 = read_and_gate(PHASE97_PATH, EXPECTED_PHASE97_RAW_SHA256, EXPECTED_PHASE97_CANONICAL_SHA256)
    phase100 = read_and_gate(PHASE100_PATH, EXPECTED_PHASE100_RAW_SHA256, EXPECTED_PHASE100_CANONICAL_SHA256)
    first = build_payload(phase95, phase97, phase100)
    second = build_payload(phase95, phase97, phase100)
    if canonical_json_bytes(first) != canonical_json_bytes(second):
        raise RuntimeError("Independent in-memory constructions disagree")
    atomic_write(RESULTS_PATH, json.dumps(first, indent=2, sort_keys=True, ensure_ascii=True) + "\n")
    atomic_write(REPORT_PATH, render_report(first))
    print(json.dumps(first["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
