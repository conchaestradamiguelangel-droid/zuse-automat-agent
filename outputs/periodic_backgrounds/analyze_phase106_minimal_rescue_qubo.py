from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import itertools
import json
import math
import os
import struct
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"
RUNTIME_DIR = Path.home() / ".codex" / "runtime" / "zuse_phase107"
BENCHMARK_PATH = RUNTIME_DIR / "phase107_benchmark_report.json"

PHASE106_RESULTS_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_results.json"
PHASE106_MANIFEST_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_manifest.json"
PHASE106_LEDGER_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_ledger.bin"
PAIR_RESULTS_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_results.json"
PAIR_MANIFEST_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_manifest.json"
PAIR_LEDGER_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_ledger.bin"
TRIPLE_RESULTS_PATH = OUTPUT_DIR / "phase103_triple_synergy_results.json"
TRIPLE_MANIFEST_PATH = OUTPUT_DIR / "phase103_triple_synergy_manifest.json"
TRIPLE_LEDGER_PATH = OUTPUT_DIR / "phase103_triple_synergy_ledger.bin"
QUAD_RESULTS_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_results.json"
QUAD_MANIFEST_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_manifest.json"

MODELS_PATH = OUTPUT_DIR / "phase106_minimal_rescue_qubo_models.jsonl"
MANIFEST_PATH = OUTPUT_DIR / "phase106_minimal_rescue_qubo_manifest.json"
RESULTS_PATH = OUTPUT_DIR / "phase106_minimal_rescue_qubo_results.json"
REPORT_PATH = OUTPUT_DIR / "phase106_minimal_rescue_qubo_report.md"

EXPECTED_DIRECT_JSON_HASHES = {
    PHASE106_RESULTS_PATH: (
        "9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24",
        "982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353",
    ),
    PHASE106_MANIFEST_PATH: (
        "d092aa050942967b4da15651841e20a4d6521f57a209f676695c17a9c5d4bdc2",
        "45135b64e6936865298a203d03493aeffe8911b50b564af8a9e6d886bc14ba6c",
    ),
}
EXPECTED_DIRECT_LEDGER_HASH = (
    "987d8b54447bdd3919fdc5d41b7b36246bee534ed5c2a5462b6dbbfd61b16588"
)
EXPECTED_INSTANCE_COUNT = 265
EXPECTED_HYPEREDGE_COUNT = 1_476
EXPECTED_X_COUNT = 17_624
EXPECTED_VARIABLE_COUNT = 19_100
EXPECTED_ZZ_COUNT = 10_077
EXPECTED_ZX_COUNT = 3_684
EXPECTED_BY_CARDINALITY_METRIC = {
    (2, "kappa"): (69, 454),
    (2, "lambda"): (68, 470),
    (3, "kappa"): (41, 180),
    (3, "lambda"): (40, 192),
    (4, "kappa"): (16, 77),
    (4, "lambda"): (31, 103),
}

PAIR_RECORD = struct.Struct("<HBBHBBBB")
TRIPLE_RECORD = struct.Struct("<HBBBHBBB")


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


def read_direct_json_gate(path: Path) -> dict[str, Any]:
    expected_raw, expected_canonical = EXPECTED_DIRECT_JSON_HASHES[path]
    if raw_sha256(path) != expected_raw:
        raise RuntimeError(f"Raw SHA-256 mismatch: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if canonical_sha256(value) != expected_canonical:
        raise RuntimeError(f"Canonical SHA-256 mismatch: {path.name}")
    return value


def validate_embedded_sources(phase106: dict[str, Any]) -> dict[str, dict[str, str]]:
    verified: dict[str, dict[str, str]] = {}
    for name, expected in sorted(phase106["sources"].items()):
        path = OUTPUT_DIR / name
        if not path.exists():
            raise RuntimeError(f"Embedded source is missing: {name}")
        actual_raw = raw_sha256(path)
        if "sha256" in expected:
            if actual_raw != expected["sha256"]:
                raise RuntimeError(f"Embedded ledger SHA-256 mismatch: {name}")
            verified[name] = {"sha256": actual_raw}
            continue
        if actual_raw != expected["raw"]:
            raise RuntimeError(f"Embedded raw SHA-256 mismatch: {name}")
        value = json.loads(path.read_text(encoding="utf-8"))
        actual_canonical = canonical_sha256(value)
        if actual_canonical != expected["canonical"]:
            raise RuntimeError(f"Embedded canonical SHA-256 mismatch: {name}")
        verified[name] = {"raw": actual_raw, "canonical": actual_canonical}
    return verified


def ordered_words_sha256(words: tuple[int, ...]) -> str:
    payload = json.dumps(list(words), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def canonical_hyperedge(words: Iterable[int], cardinality: int | None = None) -> tuple[int, ...]:
    canonical = tuple(sorted(map(int, words)))
    if len(set(canonical)) != len(canonical):
        raise RuntimeError("Hyperedge contains duplicate words")
    if cardinality is not None and len(canonical) != cardinality:
        raise RuntimeError("Hyperedge cardinality mismatch")
    return canonical


def source_key(row: dict[str, Any]) -> tuple[str, int, int]:
    return str(row["cube_key"]), int(row["pair_index"]), int(row["period"])


def explicit_ledger_candidates(
    results: dict[str, Any],
    ledger_path: Path,
    record: struct.Struct,
    cardinality: int,
    count_key: str,
) -> dict[tuple[str, int, int], dict[str, Any]]:
    output: dict[tuple[str, int, int], dict[str, Any]] = {}
    rows = sorted(results["strata"], key=lambda row: int(row["stratum_index"]))
    with ledger_path.open("rb") as handle:
        for row in rows:
            words_seen: set[int] = set()
            previous: tuple[int, ...] | None = None
            count = int(row[count_key])
            for _ in range(count):
                raw = handle.read(record.size)
                if len(raw) != record.size:
                    raise RuntimeError("Candidate ledger is truncated")
                values = record.unpack(raw)
                if int(values[0]) != int(row["stratum_index"]):
                    raise RuntimeError("Candidate ledger stratum mismatch")
                words = tuple(map(int, values[1 : 1 + cardinality]))
                if words != canonical_hyperedge(words, cardinality):
                    raise RuntimeError("Source combinations are not internally canonical")
                if previous is not None and words <= previous:
                    raise RuntimeError("Source combinations are not strictly lexicographic")
                previous = words
                words_seen.update(words)
            ordered = tuple(sorted(words_seen))
            if len(ordered) != int(row["node_count"]):
                raise RuntimeError("Candidate node count mismatch")
            if math.comb(len(ordered), cardinality) != count:
                raise RuntimeError("Candidate combination coverage mismatch")
            key = source_key(row)
            if key in output:
                raise RuntimeError("Duplicate candidate stratum")
            output[key] = {
                "ordered_words": ordered,
                "node_count": len(ordered),
                "rule": int(row["rule"]),
                "background_index": int(row["background_index"]),
                "source_stratum_index": int(row["stratum_index"]),
            }
        if handle.read(1):
            raise RuntimeError("Candidate ledger has trailing records")
    return output


def quad_candidates(
    results: dict[str, Any], manifest: dict[str, Any]
) -> dict[tuple[str, int, int], dict[str, Any]]:
    rows = {int(row["stratum_index"]): row for row in results["strata"]}
    output: dict[tuple[str, int, int], dict[str, Any]] = {}
    for segment in manifest["segments"]:
        index = int(segment["stratum_index"])
        row = rows[index]
        words = tuple(map(int, segment["ordered_words"]))
        if words != tuple(sorted(set(words))):
            raise RuntimeError("Quadruple ordered_words are not canonical")
        if ordered_words_sha256(words) != segment["ordered_words_sha256"]:
            raise RuntimeError("Quadruple ordered_words SHA-256 mismatch")
        if len(words) != int(row["node_count"]):
            raise RuntimeError("Quadruple node count mismatch")
        if math.comb(len(words), 4) != int(segment["record_count"]):
            raise RuntimeError("Quadruple combination coverage mismatch")
        key = source_key(row)
        if key in output:
            raise RuntimeError("Duplicate quadruple candidate stratum")
        output[key] = {
            "ordered_words": words,
            "node_count": len(words),
            "rule": int(row["rule"]),
            "background_index": int(row["background_index"]),
            "source_stratum_index": index,
        }
    return output


def gate_inputs() -> dict[str, Any]:
    phase106 = read_direct_json_gate(PHASE106_RESULTS_PATH)
    phase106_manifest = read_direct_json_gate(PHASE106_MANIFEST_PATH)
    if raw_sha256(PHASE106_LEDGER_PATH) != EXPECTED_DIRECT_LEDGER_HASH:
        raise RuntimeError("Phase 106 geometry ledger SHA-256 mismatch")
    if phase106["geometry_manifest_sha256"] != canonical_sha256(phase106_manifest):
        raise RuntimeError("Phase 106 manifest linkage mismatch")
    embedded = validate_embedded_sources(phase106)
    pair_results = json.loads(PAIR_RESULTS_PATH.read_text(encoding="utf-8"))
    triple_results = json.loads(TRIPLE_RESULTS_PATH.read_text(encoding="utf-8"))
    quad_results = json.loads(QUAD_RESULTS_PATH.read_text(encoding="utf-8"))
    quad_manifest = json.loads(QUAD_MANIFEST_PATH.read_text(encoding="utf-8"))
    candidates = {
        2: explicit_ledger_candidates(
            pair_results, PAIR_LEDGER_PATH, PAIR_RECORD, 2, "pair_count"
        ),
        3: explicit_ledger_candidates(
            triple_results, TRIPLE_LEDGER_PATH, TRIPLE_RECORD, 3, "triple_count"
        ),
        4: quad_candidates(quad_results, quad_manifest),
    }
    return {
        "phase106": phase106,
        "phase106_manifest": phase106_manifest,
        "embedded_sources": embedded,
        "candidates": candidates,
    }


def build_instances(values: dict[str, Any]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, int, int, str], list[dict[str, Any]]] = defaultdict(list)
    for audit in values["phase106"]["atlas"]["mechanism_audits"]:
        if not audit["full_rescue"] or not audit["covers_all_original_cuts"]:
            raise RuntimeError("Phase 106 audit is not a verified rescue")
        key = (
            str(audit["cube_key"]),
            int(audit["pair_index"]),
            int(audit["period"]),
            str(audit["metric"]),
        )
        groups[key].append(audit)
    instances: list[dict[str, Any]] = []
    for key, audits in sorted(groups.items()):
        cardinalities = {int(audit["cardinality"]) for audit in audits}
        if len(cardinalities) != 1:
            raise RuntimeError("Instance mixes minimal cardinalities")
        cardinality = cardinalities.pop()
        candidate_key = key[:3]
        source = values["candidates"][cardinality].get(candidate_key)
        if source is None:
            raise RuntimeError("Missing candidate universe")
        hyperedges = tuple(
            sorted(canonical_hyperedge(audit["words"], cardinality) for audit in audits)
        )
        if len(set(hyperedges)) != len(hyperedges):
            raise RuntimeError("Duplicate canonical hyperedge")
        candidate_set = set(source["ordered_words"])
        if any(not set(edge).issubset(candidate_set) for edge in hyperedges):
            raise RuntimeError("Hyperedge lies outside candidate universe")
        if {int(audit["rule"]) for audit in audits} != {source["rule"]}:
            raise RuntimeError("Rule mismatch between rescue and candidates")
        instances.append(
            {
                "instance_key": "|".join(map(str, key)),
                "cube_key": key[0],
                "pair_index": key[1],
                "period": key[2],
                "metric": key[3],
                "rule": source["rule"],
                "background_index": source["background_index"],
                "source_stratum_index": source["source_stratum_index"],
                "cardinality": cardinality,
                "ordered_words": list(source["ordered_words"]),
                "hyperedges": [list(edge) for edge in hyperedges],
            }
        )
    validate_instance_population(instances)
    return instances


def validate_instance_population(instances: list[dict[str, Any]]) -> None:
    if len(instances) != EXPECTED_INSTANCE_COUNT:
        raise RuntimeError("QUBO instance count mismatch")
    if len({row["instance_key"] for row in instances}) != len(instances):
        raise RuntimeError("Duplicate QUBO instance key")
    x_count = hyperedge_count = zz_count = zx_count = 0
    variable_counts = []
    for row in instances:
        cardinality = int(row["cardinality"])
        metric = str(row["metric"])
        edge_count = len(row["hyperedges"])
        x_count += len(row["ordered_words"])
        hyperedge_count += edge_count
        zz_count += math.comb(edge_count, 2)
        zx_count += cardinality * edge_count
        variable_counts.append(len(row["ordered_words"]) + edge_count)
    actual_by = {
        key: (
            sum(1 for row in instances if (row["cardinality"], row["metric"]) == key),
            sum(
                len(row["hyperedges"])
                for row in instances
                if (row["cardinality"], row["metric"]) == key
            ),
        )
        for key in EXPECTED_BY_CARDINALITY_METRIC
    }
    if actual_by != EXPECTED_BY_CARDINALITY_METRIC:
        raise RuntimeError("Cardinality/metric population mismatch")
    if (
        x_count != EXPECTED_X_COUNT
        or hyperedge_count != EXPECTED_HYPEREDGE_COUNT
        or x_count + hyperedge_count != EXPECTED_VARIABLE_COUNT
        or zz_count != EXPECTED_ZZ_COUNT
        or zx_count != EXPECTED_ZX_COUNT
        or min(variable_counts) != 9
        or max(variable_counts) != 172
    ):
        raise RuntimeError("QUBO preflight population mismatch")


def add_qubo_term(qubo: dict[tuple[int, int], int], left: int, right: int, value: int) -> None:
    key = (left, right) if left <= right else (right, left)
    qubo[key] = qubo.get(key, 0) + int(value)
    if qubo[key] == 0:
        del qubo[key]


def build_qubo(instance: dict[str, Any]) -> dict[str, Any]:
    words = tuple(map(int, instance["ordered_words"]))
    hyperedges = tuple(tuple(map(int, edge)) for edge in instance["hyperedges"])
    cardinality = int(instance["cardinality"])
    penalty = cardinality + 1
    word_index = {word: index for index, word in enumerate(words)}
    z_offset = len(words)
    qubo: dict[tuple[int, int], int] = {}
    for index in range(len(words)):
        add_qubo_term(qubo, index, index, 1)
    for h_index, edge in enumerate(hyperedges):
        z_index = z_offset + h_index
        add_qubo_term(qubo, z_index, z_index, penalty * (cardinality - 1))
        for word in edge:
            add_qubo_term(qubo, z_index, word_index[word], -penalty)
    for left, right in itertools.combinations(range(len(hyperedges)), 2):
        add_qubo_term(qubo, z_offset + left, z_offset + right, 2 * penalty)
    model = {
        "instance_key": instance["instance_key"],
        "cube_key": instance["cube_key"],
        "pair_index": instance["pair_index"],
        "period": instance["period"],
        "metric": instance["metric"],
        "rule": instance["rule"],
        "background_index": instance["background_index"],
        "source_stratum_index": instance["source_stratum_index"],
        "cardinality": cardinality,
        "penalty": penalty,
        "constant": penalty,
        "ground_energy": cardinality,
        "ground_state_degeneracy": len(hyperedges),
        "variables": {
            "x_words": list(words),
            "z_hyperedges": [list(edge) for edge in hyperedges],
            "x_count": len(words),
            "z_count": len(hyperedges),
            "total_count": len(words) + len(hyperedges),
        },
        "qubo_upper": [[left, right, value] for (left, right), value in sorted(qubo.items())],
        "certificate": {
            "zero_z_lower_bound": penalty,
            "single_z_missing_node_net_cost": penalty - 1,
            "multiple_z_one_hot_lower_bound": penalty,
            "extra_node_cost": 1,
            "no_spurious_ground_states": True,
        },
    }
    validate_model(model)
    return model


def factorized_energy(model: dict[str, Any], x_active: set[int], z_active: set[int]) -> int:
    words = model["variables"]["x_words"]
    hyperedges = model["variables"]["z_hyperedges"]
    penalty = int(model["penalty"])
    energy = len(x_active) + penalty * (1 - len(z_active)) ** 2
    for h_index in z_active:
        edge = hyperedges[h_index]
        energy += penalty * sum(words.index(word) not in x_active for word in edge)
    return int(energy)


def expanded_energy(model: dict[str, Any], x_active: set[int], z_active: set[int]) -> int:
    x_count = int(model["variables"]["x_count"])
    active = set(x_active) | {x_count + index for index in z_active}
    energy = int(model["constant"])
    for left, right, value in model["qubo_upper"]:
        if left in active and right in active:
            energy += int(value)
    return energy


def validate_model(model: dict[str, Any]) -> None:
    x_count = int(model["variables"]["x_count"])
    hyperedges = model["variables"]["z_hyperedges"]
    cardinality = int(model["cardinality"])
    penalty = cardinality + 1
    coefficients = {(left, right): value for left, right, value in model["qubo_upper"]}
    if len(coefficients) != len(model["qubo_upper"]):
        raise RuntimeError("Duplicate QUBO coefficient")
    if any(left > right or value == 0 for (left, right), value in coefficients.items()):
        raise RuntimeError("Invalid sparse QUBO entry")
    for index in range(x_count):
        if coefficients.get((index, index)) != 1:
            raise RuntimeError("Invalid x linear coefficient")
    for h_index, edge in enumerate(hyperedges):
        z_index = x_count + h_index
        if coefficients.get((z_index, z_index)) != penalty * (cardinality - 1):
            raise RuntimeError("Invalid z linear coefficient")
        for word in edge:
            x_index = model["variables"]["x_words"].index(word)
            if coefficients.get((x_index, z_index)) != -penalty:
                raise RuntimeError("Invalid z-x coefficient")
    for left, right in itertools.combinations(range(len(hyperedges)), 2):
        if coefficients.get((x_count + left, x_count + right)) != 2 * penalty:
            raise RuntimeError("Invalid z-z coefficient")
    if any(left < x_count and right < x_count and left != right for left, right in coefficients):
        raise RuntimeError("Unexpected x-x coupling")
    ground_energy = int(model["ground_energy"])
    for h_index, edge in enumerate(hyperedges):
        active_x = {model["variables"]["x_words"].index(word) for word in edge}
        factored = factorized_energy(model, active_x, {h_index})
        expanded = expanded_energy(model, active_x, {h_index})
        if factored != ground_energy or expanded != ground_energy:
            raise RuntimeError("Known ground assignment energy mismatch")
        missing = set(active_x)
        missing.remove(min(missing))
        if factorized_energy(model, missing, {h_index}) != expanded_energy(model, missing, {h_index}):
            raise RuntimeError("Missing-node route disagreement")
    if factorized_energy(model, set(), set()) != expanded_energy(model, set(), set()):
        raise RuntimeError("Zero assignment route disagreement")
    if len(hyperedges) >= 2:
        union = {
            model["variables"]["x_words"].index(word)
            for edge in hyperedges[:2]
            for word in edge
        }
        if factorized_energy(model, union, {0, 1}) != expanded_energy(model, union, {0, 1}):
            raise RuntimeError("Multiple-z route disagreement")


def compile_models(instances: list[dict[str, Any]], workers: int) -> list[dict[str, Any]]:
    if workers <= 0:
        raise ValueError("workers must be positive")
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        models = list(executor.map(build_qubo, instances))
    return sorted(models, key=lambda model: model["instance_key"])


def summarize(models: list[dict[str, Any]]) -> dict[str, Any]:
    by = Counter()
    totals = Counter()
    for model in models:
        key = f"n{model['cardinality']}_{model['metric']}"
        by[key] += 1
        totals["x_variables"] += model["variables"]["x_count"]
        totals["z_variables"] += model["variables"]["z_count"]
        totals["variables"] += model["variables"]["total_count"]
        totals["ground_states"] += model["ground_state_degeneracy"]
        totals["nonzero_terms"] += len(model["qubo_upper"])
    return {
        "instance_count": len(models),
        "by_cardinality_metric": dict(sorted(by.items())),
        "x_variable_count": totals["x_variables"],
        "z_variable_count": totals["z_variables"],
        "total_variable_count_across_independent_models": totals["variables"],
        "ground_state_count": totals["ground_states"],
        "nonzero_qubo_term_count": totals["nonzero_terms"],
        "variable_count_range": [
            min(model["variables"]["total_count"] for model in models),
            max(model["variables"]["total_count"] for model in models),
        ],
        "all_certificates_pass": all(
            model["certificate"]["no_spurious_ground_states"] for model in models
        ),
    }


def benchmark_sample(instances: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(
        instances,
        key=lambda row: (
            row["cardinality"],
            row["metric"],
            len(row["hyperedges"]),
            row["instance_key"],
        ),
    )
    indices = {round(index * (len(ordered) - 1) / 74) for index in range(75)}
    return [ordered[index] for index in sorted(indices)]


def run_benchmark(
    values: dict[str, Any],
    instances: list[dict[str, Any]],
    workers: int,
    preflight_seconds: float,
) -> dict[str, Any]:
    sample = benchmark_sample(instances)
    started = time.perf_counter()
    models = compile_models(sample, workers)
    elapsed = time.perf_counter() - started
    payload_bytes = sum(len(canonical_json_bytes(model)) + 1 for model in models)
    projected_compile_seconds = elapsed * len(instances) / len(sample)
    projected_total_seconds = preflight_seconds + projected_compile_seconds
    report = {
        "phase": 107,
        "status": "PASS",
        "mode": "BENCHMARK_ONLY",
        "workers": workers,
        "runner_sha256": normalized_source_sha256(Path(__file__)),
        "sample_instance_count": len(sample),
        "sample_seconds": elapsed,
        "sample_payload_bytes": payload_bytes,
        "preflight_seconds": preflight_seconds,
        "projected_compile_seconds": projected_compile_seconds,
        "projected_full_seconds": projected_total_seconds,
        "projected_full_seconds_with_25pct_margin": projected_total_seconds * 1.25,
        "expected_instance_count": len(instances),
        "expected_hyperedge_count": sum(len(row["hyperedges"]) for row in instances),
        "expected_x_count": sum(len(row["ordered_words"]) for row in instances),
        "sample_summary": summarize(models),
        "full_run_executed": False,
        "simulation_executed": False,
        "quantum_execution": False,
        "source_result_sha256": raw_sha256(PHASE106_RESULTS_PATH),
    }
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write(BENCHMARK_PATH, json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return report


def validate_full_authorization(path: Path, benchmark_path: Path, workers: int) -> dict[str, Any]:
    benchmark_digest = raw_sha256(benchmark_path)
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    authorization = json.loads(path.read_text(encoding="utf-8"))
    expected_text = (
        f"Autorizo la compilacion completa de Fase 107 con {workers} workers, "
        f"ligada al benchmark SHA-256 {benchmark_digest}."
    )
    checks = (
        benchmark.get("status") == "PASS",
        benchmark.get("workers") == workers,
        benchmark.get("runner_sha256") == normalized_source_sha256(Path(__file__)),
        benchmark.get("expected_instance_count") == EXPECTED_INSTANCE_COUNT,
        authorization.get("authorization") == expected_text,
        authorization.get("benchmark_report_sha256") == benchmark_digest,
        authorization.get("workers") == workers,
        authorization.get("expected_instance_count") == EXPECTED_INSTANCE_COUNT,
    )
    if not all(checks):
        raise RuntimeError("Full-run authorization or benchmark binding mismatch")
    return authorization


def build_report(summary: dict[str, Any], models_sha256: str) -> str:
    return "\n".join(
        [
            "# Fase 107 - Exact minimal-rescue QUBO compilation",
            "",
            "**Verdict:** `EXACT_MINIMAL_RESCUE_QUBO_COMPILATION_VERIFIED`",
            "",
            f"- Independent QUBO models: {summary['instance_count']}",
            f"- Certified ground states: {summary['ground_state_count']}",
            f"- Variables accumulated across independent models: {summary['total_variable_count_across_independent_models']}",
            f"- Variables per model: {summary['variable_count_range'][0]}..{summary['variable_count_range'][1]}",
            f"- Sparse nonzero QUBO terms: {summary['nonzero_qubo_term_count']}",
            f"- Models JSONL SHA-256: `{models_sha256}`",
            "",
            "## Methodological limits",
            "",
            "- The QUBOs compile already enumerated minimal rescues; they do not discover new rescues.",
            "- The certified objective uses unit node costs only.",
            "- No quantum hardware, annealer, heuristic solver, or CA simulation was executed.",
            "- QUBO compatibility is not evidence of quantum speedup or practical advantage.",
            "- Results remain limited to the 265 frozen target-period-metric instances.",
            "",
        ]
    )


def run_full(values: dict[str, Any], instances: list[dict[str, Any]], workers: int, authorization_path: Path) -> dict[str, Any]:
    validate_full_authorization(authorization_path, BENCHMARK_PATH, workers)
    authorization_path.unlink()
    models = compile_models(instances, workers)
    summary = summarize(models)
    if (
        summary["instance_count"] != EXPECTED_INSTANCE_COUNT
        or summary["ground_state_count"] != EXPECTED_HYPEREDGE_COUNT
        or summary["x_variable_count"] != EXPECTED_X_COUNT
        or summary["total_variable_count_across_independent_models"] != EXPECTED_VARIABLE_COUNT
        or not summary["all_certificates_pass"]
    ):
        raise RuntimeError("Final QUBO summary reconciliation failed")
    models_bytes = b"".join(canonical_json_bytes(model) + b"\n" for model in models)
    models_sha256 = hashlib.sha256(models_bytes).hexdigest()
    manifest = {
        "phase": 107,
        "format": "canonical-jsonl-one-model-per-line",
        "qubo_convention": "E=constant+sum_i(Qii*bi)+sum_i<j(Qij*bi*bj)",
        "integer_coefficients": True,
        "model_count": len(models),
        "models_file": MODELS_PATH.name,
        "models_size": len(models_bytes),
        "models_sha256": models_sha256,
        "variable_order": "x ascending word, then z ascending canonical hyperedge tuple",
        "source_result_sha256": raw_sha256(PHASE106_RESULTS_PATH),
        "source_result_canonical_sha256": canonical_sha256(values["phase106"]),
    }
    results = {
        "phase": 107,
        "status": "EXACT_MINIMAL_RESCUE_QUBO_COMPILATION_VERIFIED",
        "summary": summary,
        "protocol": {
            "unit_cost_only": True,
            "symbolic_global_certificate": True,
            "factorized_and_expanded_routes": True,
            "simulation_executed": False,
            "quantum_execution": False,
            "quantum_advantage_claimed": False,
            "new_rescue_discovery_claimed": False,
        },
        "sources": {
            "phase106_results_raw": raw_sha256(PHASE106_RESULTS_PATH),
            "phase106_results_canonical": canonical_sha256(values["phase106"]),
            "phase106_manifest_raw": raw_sha256(PHASE106_MANIFEST_PATH),
            "phase106_manifest_canonical": canonical_sha256(values["phase106_manifest"]),
            "phase106_ledger": raw_sha256(PHASE106_LEDGER_PATH),
            "embedded_source_count": len(values["embedded_sources"]),
        },
        "manifest_canonical_sha256": canonical_sha256(manifest),
    }
    report = build_report(summary, models_sha256)
    atomic_write(MODELS_PATH, models_bytes)
    atomic_write(MANIFEST_PATH, json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    atomic_write(RESULTS_PATH, json.dumps(results, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    atomic_write(REPORT_PATH, report.encode("utf-8"))
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Fase 107 exact minimal-rescue QUBO compiler")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--benchmark", action="store_true")
    mode.add_argument("--full", action="store_true")
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--authorization", type=Path)
    args = parser.parse_args()
    preflight_started = time.perf_counter()
    values = gate_inputs()
    instances = build_instances(values)
    preflight_seconds = time.perf_counter() - preflight_started
    if args.preflight:
        print(json.dumps({"instance_count": len(instances), "full_run_executed": False}, indent=2))
        return
    if args.benchmark:
        print(
            json.dumps(
                run_benchmark(values, instances, args.workers, preflight_seconds),
                indent=2,
                sort_keys=True,
            )
        )
        return
    if args.authorization is None:
        raise RuntimeError("--authorization is required for --full")
    print(json.dumps(run_full(values, instances, args.workers, args.authorization), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
