from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"

MOTIF_RESULTS_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_results.json"
PARTITION_RESULTS_PATH = OUTPUT_DIR / "phase109_fixed_budget_hamming_partition_results.json"
RESULTS_PATH = OUTPUT_DIR / "phase110_internal_loio_a_g_results.json"
MANIFEST_PATH = OUTPUT_DIR / "phase110_internal_loio_a_g_manifest.json"
REPORT_PATH = OUTPUT_DIR / "phase110_internal_loio_a_g_report.md"

EXPECTED_JSON_HASHES = {
    MOTIF_RESULTS_PATH: (
        "9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24",
        "982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353",
    ),
    PARTITION_RESULTS_PATH: (
        "ba5cf94330ce5c27c6b7c4420f910c637debac1273b9b25d3ad4fd787c141d04",
        "dcf3d5847af14b3128e88dac765e491900340ddf4587b50281f42ac8ade147b1",
    ),
}

EXTERNAL = "EXTERNAL_ATTACHMENT_RESCUE"
INTERNAL = "INTERNAL_EDGE_DEPENDENT_RESCUE"
LABELS = (EXTERNAL, INTERNAL)
THRESHOLDS = tuple(range(3, 10))
EXPECTED_RESCUES = 223
EXPECTED_INSTANCES = 101
EXPECTED_COMPOSITION = {"only_external": 6, "only_internal": 71, "mixed": 24}
STATUS = "INTERNAL_LOIO_CLASSIFICATION_POTENTIAL_A_G_VERIFIED"

FORBIDDEN_PREDICTORS = {
    "minimum_vertex_cut",
    "minimum_edge_cut",
    "individually_critical_vertices",
    "individually_critical_edges",
    "kappa_v",
    "lambda_e",
    "robustness_label",
    "edge_disjoint_path_count",
    "internally_vertex_disjoint_path_count",
    "cut_mechanisms",
    "cut_mechanism_counts",
    "external_rescue",
    "per_internal_edge_removal",
    "source_internal_edge_required",
    "full_rescue",
    "covers_all_original_cuts",
    "new_separator_count",
    "A_V",
    "A_R",
    "internal_edge_required",
}
PREDICTORS = {"A_G"}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def raw_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalized_source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def read_gated_json(path: Path) -> tuple[dict[str, Any], dict[str, str]]:
    expected_raw, expected_canonical = EXPECTED_JSON_HASHES[path]
    actual_raw = raw_sha256(path)
    if actual_raw != expected_raw:
        raise RuntimeError(f"Raw SHA-256 mismatch: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    actual_canonical = canonical_sha256(value)
    if actual_canonical != expected_canonical:
        raise RuntimeError(f"Canonical SHA-256 mismatch: {path.name}")
    return value, {"raw": actual_raw, "canonical": actual_canonical}


def fraction_payload(value: Fraction | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "numerator": value.numerator,
        "denominator": value.denominator,
        "decimal": float(value),
    }


def canonical_words(words: Iterable[int]) -> tuple[int, ...]:
    ordered = tuple(sorted(map(int, words)))
    if len(ordered) != 2 or ordered[0] == ordered[1]:
        raise RuntimeError("Invalid K2 rescue words")
    return ordered


def load_census(
    motif_results: dict[str, Any], partition_results: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    motif: dict[tuple[str, tuple[int, ...]], str] = {}
    for source in motif_results["atlas"]["mechanism_audits"]:
        if source["motif"] != "K2":
            continue
        instance_key = "|".join(
            (
                str(source["cube_key"]),
                str(int(source["pair_index"])),
                str(int(source["period"])),
                str(source["metric"]),
            )
        )
        identity = (instance_key, canonical_words(source["words"]))
        if identity in motif:
            raise RuntimeError("Duplicate K2 identity in motif source")
        motif[identity] = str(source["mechanism_label"])

    partition: dict[tuple[str, tuple[int, ...]], dict[str, Any]] = {}
    for source in partition_results["supplementary_full_census_pairs"]:
        identity = (str(source["instance_key"]), canonical_words(source["words"]))
        if identity in partition:
            raise RuntimeError("Duplicate K2 identity in partition source")
        partition[identity] = source

    if len(motif) != EXPECTED_RESCUES or len(partition) != EXPECTED_RESCUES:
        raise RuntimeError("Unexpected K2 rescue count")
    if set(motif) != set(partition):
        raise RuntimeError("Incomplete K2 identity join")

    rows: list[dict[str, Any]] = []
    mismatches = 0
    for identity in sorted(motif):
        instance_key, words = identity
        source = partition[identity]
        label = motif[identity]
        if label not in LABELS or source["mechanism_label"] != label:
            mismatches += 1
        rows.append(
            {
                "instance_key": instance_key,
                "words": list(words),
                "A_G": int(source["A_G"]),
                "mechanism_label": label,
            }
        )
    if mismatches:
        raise RuntimeError("Mechanism mismatch between certified sources")
    if PREDICTORS & FORBIDDEN_PREDICTORS or PREDICTORS != {"A_G"}:
        raise RuntimeError("Forbidden predictor entered the model")
    return rows, {"identity_count": len(rows), "mechanism_mismatches": mismatches}


def group_rows(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["instance_key"]].append(row)
    if len(groups) != EXPECTED_INSTANCES:
        raise RuntimeError("Unexpected instance count")
    for group in groups.values():
        group.sort(key=lambda row: tuple(row["words"]))
    return dict(groups)


def instance_composition(groups: dict[str, list[dict[str, Any]]]) -> dict[str, int]:
    counts = Counter()
    for group in groups.values():
        labels = {row["mechanism_label"] for row in group}
        if labels == {EXTERNAL}:
            counts["only_external"] += 1
        elif labels == {INTERNAL}:
            counts["only_internal"] += 1
        elif labels == set(LABELS):
            counts["mixed"] += 1
        else:
            raise RuntimeError("Unexpected instance label composition")
    output = {key: counts[key] for key in EXPECTED_COMPOSITION}
    if output != EXPECTED_COMPOSITION:
        raise RuntimeError("Unexpected 6+71+24 instance composition")
    return output


def predict(a_g: int, threshold: int) -> str:
    return EXTERNAL if int(a_g) >= int(threshold) else INTERNAL


def weighted_sensitivities(
    rows_with_predictions: Iterable[tuple[dict[str, Any], str, Fraction]],
) -> tuple[dict[str, Fraction], Fraction]:
    totals = {label: Fraction(0) for label in LABELS}
    correct = {label: Fraction(0) for label in LABELS}
    for row, prediction, weight in rows_with_predictions:
        label = row["mechanism_label"]
        totals[label] += weight
        if prediction == label:
            correct[label] += weight
    if any(totals[label] == 0 for label in LABELS):
        raise RuntimeError("A class is absent from weighted evaluation")
    sensitivities = {label: correct[label] / totals[label] for label in LABELS}
    return sensitivities, sum(sensitivities.values(), Fraction(0)) / 2


def threshold_scores(
    groups: dict[str, list[dict[str, Any]]], train_keys: list[str]
) -> list[dict[str, Any]]:
    n_instances = len(train_keys)
    scored: list[dict[str, Any]] = []
    for threshold in THRESHOLDS:
        weighted_rows = []
        for key in train_keys:
            group = groups[key]
            weight = Fraction(1, n_instances * len(group))
            weighted_rows.extend(
                (row, predict(row["A_G"], threshold), weight) for row in group
            )
        sensitivities, balanced = weighted_sensitivities(weighted_rows)
        minimum = min(sensitivities.values())
        gap = abs(sensitivities[EXTERNAL] - sensitivities[INTERNAL])
        scored.append(
            {
                "threshold": threshold,
                "sensitivities": sensitivities,
                "balanced_accuracy": balanced,
                "minimum_sensitivity": minimum,
                "sensitivity_gap": gap,
            }
        )
    return scored


def choose_threshold(scores: list[dict[str, Any]]) -> dict[str, Any]:
    return max(
        scores,
        key=lambda row: (
            row["balanced_accuracy"],
            row["minimum_sensitivity"],
            -row["sensitivity_gap"],
            -row["threshold"],
        ),
    )


def training_majority(
    groups: dict[str, list[dict[str, Any]]], train_keys: list[str]
) -> tuple[str, dict[str, Fraction]]:
    totals = {label: Fraction(0) for label in LABELS}
    n_instances = len(train_keys)
    for key in train_keys:
        group = groups[key]
        weight = Fraction(1, n_instances * len(group))
        for row in group:
            totals[row["mechanism_label"]] += weight
    majority = EXTERNAL if totals[EXTERNAL] > totals[INTERNAL] else INTERNAL
    return majority, totals


def nullable_fold_sensitivity(group: list[dict[str, Any]], label: str, threshold: int):
    selected = [row for row in group if row["mechanism_label"] == label]
    if not selected:
        return None
    hits = sum(predict(row["A_G"], threshold) == label for row in selected)
    return Fraction(hits, len(selected))


def run_loio(
    groups: dict[str, list[dict[str, Any]]], fold_order: Iterable[str]
) -> list[dict[str, Any]]:
    all_keys = set(groups)
    folds: list[dict[str, Any]] = []
    for held_key in fold_order:
        train_keys = sorted(all_keys - {held_key})
        scores = threshold_scores(groups, train_keys)
        chosen = choose_threshold(scores)
        baseline, baseline_totals = training_majority(groups, train_keys)
        if baseline != INTERNAL:
            raise RuntimeError("Training baseline is not INTERNAL")
        held_group = groups[held_key]
        predictions = [
            {
                "words": row["words"],
                "A_G": row["A_G"],
                "actual": row["mechanism_label"],
                "predicted": predict(row["A_G"], chosen["threshold"]),
                "baseline_predicted": baseline,
            }
            for row in held_group
        ]
        composition = Counter(row["mechanism_label"] for row in held_group)
        folds.append(
            {
                "held_out_instance": held_key,
                "threshold": chosen["threshold"],
                "training_balanced_accuracy": fraction_payload(
                    chosen["balanced_accuracy"]
                ),
                "training_sensitivity_external": fraction_payload(
                    chosen["sensitivities"][EXTERNAL]
                ),
                "training_sensitivity_internal": fraction_payload(
                    chosen["sensitivities"][INTERNAL]
                ),
                "baseline_class": baseline,
                "baseline_training_class_weights": {
                    label: fraction_payload(value)
                    for label, value in baseline_totals.items()
                },
                "held_out_composition": {
                    EXTERNAL: composition[EXTERNAL],
                    INTERNAL: composition[INTERNAL],
                },
                "held_out_sensitivity_external": fraction_payload(
                    nullable_fold_sensitivity(held_group, EXTERNAL, chosen["threshold"])
                ),
                "held_out_sensitivity_internal": fraction_payload(
                    nullable_fold_sensitivity(held_group, INTERNAL, chosen["threshold"])
                ),
                "predictions": predictions,
            }
        )
    return folds


def confusion(prediction_rows: list[dict[str, Any]], field: str) -> dict[str, Any]:
    matrix = {
        actual: {predicted: 0 for predicted in LABELS} for actual in LABELS
    }
    for row in prediction_rows:
        matrix[row["actual"]][row[field]] += 1
    sens_ext = Fraction(matrix[EXTERNAL][EXTERNAL], sum(matrix[EXTERNAL].values()))
    sens_int = Fraction(matrix[INTERNAL][INTERNAL], sum(matrix[INTERNAL].values()))
    accuracy = Fraction(
        matrix[EXTERNAL][EXTERNAL] + matrix[INTERNAL][INTERNAL],
        len(prediction_rows),
    )
    return {
        "matrix_actual_by_predicted": matrix,
        "sensitivity_external": fraction_payload(sens_ext),
        "sensitivity_internal": fraction_payload(sens_int),
        "balanced_accuracy": fraction_payload((sens_ext + sens_int) / 2),
        "accuracy": fraction_payload(accuracy),
    }


def aggregate_weighted(
    groups: dict[str, list[dict[str, Any]]],
    prediction_rows: list[dict[str, Any]],
    field: str,
) -> dict[str, Any]:
    selected_keys = sorted({row["instance_key"] for row in prediction_rows})
    n_instances = len(selected_keys)
    by_identity = {
        (row["instance_key"], tuple(row["words"])): row for row in prediction_rows
    }
    weighted_rows = []
    for key in selected_keys:
        group = groups[key]
        weight = Fraction(1, n_instances * len(group))
        for source in group:
            result = by_identity[(key, tuple(source["words"]))]
            weighted_rows.append((source, result[field], weight))
    sensitivities, balanced = weighted_sensitivities(weighted_rows)
    return {
        "instance_count": n_instances,
        "rescue_count": len(prediction_rows),
        "weight_rule": f"1/({n_instances}*n_i)",
        "sensitivity_external": fraction_payload(sensitivities[EXTERNAL]),
        "sensitivity_internal": fraction_payload(sensitivities[INTERNAL]),
        "balanced_accuracy": fraction_payload(balanced),
    }


def collect_predictions(folds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for fold in folds:
        for prediction in fold["predictions"]:
            rows.append({"instance_key": fold["held_out_instance"], **prediction})
    return sorted(rows, key=lambda row: (row["instance_key"], tuple(row["words"])))


def subgroup_summary(
    groups: dict[str, list[dict[str, Any]]], predictions: list[dict[str, Any]], mixed: bool
) -> dict[str, Any]:
    selected_keys = {
        key
        for key, group in groups.items()
        if ({row["mechanism_label"] for row in group} == set(LABELS)) == mixed
    }
    selected = [row for row in predictions if row["instance_key"] in selected_keys]
    return {
        "weighted": aggregate_weighted(groups, selected, "predicted"),
        "raw": confusion(selected, "predicted"),
    }


def analyze() -> tuple[dict[str, Any], dict[str, Any]]:
    payloads = {}
    source_hashes = {}
    for path in EXPECTED_JSON_HASHES:
        payloads[path], source_hashes[path.name] = read_gated_json(path)
    rows, join_audit = load_census(
        payloads[MOTIF_RESULTS_PATH], payloads[PARTITION_RESULTS_PATH]
    )
    groups = group_rows(rows)
    composition = instance_composition(groups)

    ordered_keys = sorted(groups)
    folds = run_loio(groups, ordered_keys)
    reverse_folds = run_loio(groups, reversed(ordered_keys))
    ordered_signature = {fold["held_out_instance"]: fold for fold in folds}
    reverse_signature = {fold["held_out_instance"]: fold for fold in reverse_folds}
    if ordered_signature != reverse_signature:
        raise RuntimeError("LOIO result depends on fold evaluation order")

    predictions = collect_predictions(folds)
    if len(predictions) != EXPECTED_RESCUES:
        raise RuntimeError("Unexpected out-of-fold prediction count")
    weighted = aggregate_weighted(groups, predictions, "predicted")
    baseline_weighted = aggregate_weighted(
        groups, predictions, "baseline_predicted"
    )
    improvement = (
        Fraction(
            weighted["balanced_accuracy"]["numerator"],
            weighted["balanced_accuracy"]["denominator"],
        )
        - Fraction(
            baseline_weighted["balanced_accuracy"]["numerator"],
            baseline_weighted["balanced_accuracy"]["denominator"],
        )
    )
    histogram = Counter(fold["threshold"] for fold in folds)

    results = {
        "phase": 111,
        "artifact_prefix": "phase110",
        "status": STATUS,
        "scope": {
            "outcome_data_seen_during_feature_design": True,
            "feature_selection_nested_within_loio": False,
            "external_validation": False,
            "prospective_validation": False,
            "causal_claim": False,
            "population_generalization": False,
            "auditor_replacement_authorized": False,
            "new_simulation_or_sweep": False,
        },
        "design": {
            "feature": "A_G",
            "thresholds": list(THRESHOLDS),
            "prediction_rule": "EXTERNAL iff A_G >= threshold",
            "fold_count": len(folds),
            "training_instance_count_per_fold": 100,
            "training_weight_rule": "1/(100*n_i)",
            "evaluation_weight_rule": "1/(101*n_i)",
            "arithmetic": "exact_fractions",
            "tie_break": [
                "maximum_balanced_accuracy",
                "maximum_minimum_sensitivity",
                "minimum_absolute_sensitivity_gap",
                "smallest_threshold",
            ],
            "baseline": "equal-instance-weighted training majority; tie INTERNAL",
        },
        "source_audit": {
            "join": join_audit,
            "rescue_count": len(rows),
            "instance_count": len(groups),
            "instance_composition": composition,
            "fold_order_invariance_failures": 0,
            "training_class_loss_folds": 0,
            "non_internal_baseline_folds": 0,
            "forbidden_predictors": sorted(FORBIDDEN_PREDICTORS),
            "predictors_used": sorted(PREDICTORS),
        },
        "threshold_distribution": {
            str(threshold): histogram[threshold] for threshold in THRESHOLDS
        },
        "aggregate": {
            "classifier_weighted": weighted,
            "classifier_unweighted": confusion(predictions, "predicted"),
            "baseline_weighted": baseline_weighted,
            "baseline_unweighted": confusion(predictions, "baseline_predicted"),
            "weighted_balanced_accuracy_improvement": fraction_payload(improvement),
        },
        "subgroups": {
            "mixed_24_instances": subgroup_summary(groups, predictions, True),
            "monolabel_77_instances": subgroup_summary(groups, predictions, False),
        },
        "folds": folds,
        "out_of_fold_predictions": predictions,
        "sources": source_hashes,
    }
    return results, source_hashes


def render_report(results: dict[str, Any]) -> str:
    aggregate = results["aggregate"]
    weighted = aggregate["classifier_weighted"]
    baseline = aggregate["baseline_weighted"]
    unweighted = aggregate["classifier_unweighted"]
    confusion_raw = aggregate["classifier_unweighted"]["matrix_actual_by_predicted"]
    mixed = results["subgroups"]["mixed_24_instances"]["weighted"]
    monolabel = results["subgroups"]["monolabel_77_instances"]["weighted"]
    lines = [
        "# Fase 111 — Potencial clasificatorio interno LOIO de A_G",
        "",
        f"**Veredicto:** `{results['status']}`",
        "",
        "## Auditoría",
        "",
        "- Rescates K2: 223 en 101 instancias.",
        "- Composición: 6 solo externas, 71 solo internas y 24 mixtas.",
        "- Folds LOIO: 101; todos conservan ambas clases en entrenamiento.",
        "- Baseline de entrenamiento: INTERNAL en 101/101 folds.",
        "- Discrepancias de identidad, mecanismo u orden de folds: 0.",
        "",
        "## Resultado agregado fuera de fold",
        "",
        f"- Sensibilidad externa ponderada: {weighted['sensitivity_external']['decimal']:.6f}.",
        f"- Sensibilidad interna ponderada: {weighted['sensitivity_internal']['decimal']:.6f}.",
        f"- Balanced accuracy ponderada: {weighted['balanced_accuracy']['decimal']:.6f}.",
        f"- Balanced accuracy cruda secundaria: {unweighted['balanced_accuracy']['decimal']:.6f}.",
        f"- Baseline balanced accuracy ponderada: {baseline['balanced_accuracy']['decimal']:.6f}.",
        "- Mejora sobre baseline: "
        f"{aggregate['weighted_balanced_accuracy_improvement']['decimal']:.6f}.",
        "- Matriz cruda (filas reales, columnas predichas): "
        f"EXT=[{confusion_raw[EXTERNAL][EXTERNAL]}, {confusion_raw[EXTERNAL][INTERNAL]}], "
        f"INT=[{confusion_raw[INTERNAL][EXTERNAL]}, {confusion_raw[INTERNAL][INTERNAL]}].",
        "",
        "## Subgrupos descriptivos",
        "",
        "- 24 instancias mixtas: sensibilidad externa ponderada "
        f"{mixed['sensitivity_external']['decimal']:.6f}, sensibilidad interna "
        f"{mixed['sensitivity_internal']['decimal']:.6f}, BA_w "
        f"{mixed['balanced_accuracy']['decimal']:.6f}.",
        "- 77 instancias monoclase: sensibilidad externa ponderada "
        f"{monolabel['sensitivity_external']['decimal']:.6f}, sensibilidad interna "
        f"{monolabel['sensitivity_internal']['decimal']:.6f}, BA_w "
        f"{monolabel['balanced_accuracy']['decimal']:.6f}.",
        "",
        "## Umbrales elegidos",
        "",
    ]
    for threshold, count in results["threshold_distribution"].items():
        lines.append(f"- t={threshold}: {count} folds.")
    lines.extend(
        [
            "",
            "## Límites",
            "",
            "Este es un análisis interno del mismo censo usado para elegir A_G. La selección "
            "de la característica no está anidada en LOIO. No constituye validación externa "
            "o prospectiva, no estima sin sesgo el rendimiento futuro y no autoriza sustituir "
            "las auditorías exactas. No se afirma causalidad ni generalización poblacional.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(results: dict[str, Any], sources: dict[str, Any]) -> None:
    atomic_write(
        RESULTS_PATH,
        json.dumps(results, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        + b"\n",
    )
    atomic_write(REPORT_PATH, render_report(results).encode("utf-8"))
    runner = Path(__file__).resolve()
    manifest = {
        "phase": 111,
        "artifact_prefix": "phase110",
        "status": results["status"],
        "runner": runner.name,
        "runner_normalized_sha256": normalized_source_sha256(runner),
        "sources": sources,
        "outputs": {
            RESULTS_PATH.name: {
                "raw": raw_sha256(RESULTS_PATH),
                "canonical": canonical_sha256(results),
            },
            REPORT_PATH.name: {"raw": raw_sha256(REPORT_PATH)},
        },
    }
    atomic_write(
        MANIFEST_PATH,
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
        + b"\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    results, sources = analyze()
    if not args.check_only:
        write_outputs(results, sources)
    print(results["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
