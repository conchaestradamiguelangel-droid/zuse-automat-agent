from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import importlib.util
import itertools
import json
import math
import os
import shutil
import struct
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"
RUNTIME_DIR = Path.home() / ".codex" / "runtime" / "zuse_phase106"
CHECKPOINT_DIR = RUNTIME_DIR / "full_checkpoints"
BENCHMARK_PATH = RUNTIME_DIR / "phase106_benchmark_report.json"

PHASE95_PATH = OUTPUT_DIR / "phase94_hypercube_completion_results.json"
PHASE97_PATH = OUTPUT_DIR / "phase96_bridge_robustness_results.json"
PHASE102_PATH = OUTPUT_DIR / "phase101_cut_coverage_law_results.json"
PAIR_RESULTS_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_results.json"
PAIR_MANIFEST_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_manifest.json"
PAIR_LEDGER_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_ledger.bin"
TRIPLE_RESULTS_PATH = OUTPUT_DIR / "phase103_triple_synergy_results.json"
TRIPLE_MANIFEST_PATH = OUTPUT_DIR / "phase103_triple_synergy_manifest.json"
TRIPLE_LEDGER_PATH = OUTPUT_DIR / "phase103_triple_synergy_ledger.bin"
QUAD_RESULTS_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_results.json"
QUAD_MANIFEST_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_manifest.json"
QUAD_LEDGER_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_ledger.bin"

GEOMETRY_LEDGER_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_ledger.bin"
GEOMETRY_MANIFEST_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_manifest.json"
RESULTS_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_results.json"
REPORT_PATH = OUTPUT_DIR / "phase105_minimal_rescue_motif_report.md"

EXPECTED_JSON_HASHES = {
    PHASE95_PATH: (
        "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3",
        "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429",
    ),
    PHASE97_PATH: (
        "3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858",
        "85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b",
    ),
    PHASE102_PATH: (
        "2eae9b4825bb78d9c396a47bfe365c0beedda198de7c8a2a6093fede3423fb2c",
        "3ecad4486d9ac87c5c7efc58726a41dcaacd738d6450ffc6024b3577dbd0b74e",
    ),
    PAIR_RESULTS_PATH: (
        "9a5c70318085c8d6d1a7ad82a59fb631abda524926288c46cb0da30a7cd47268",
        "152003197716bff38e552b3b51754df6dbfe4c6dc9f93326c3a55de594e5a6c3",
    ),
    PAIR_MANIFEST_PATH: (
        "d434a20dd0c66350fadceac6ea4f6e3d73bd9769e51195083efc628ed8170057",
        "580635c42efc2bb042e539f0a1f61d6ae15693d38d77a3333041757be9257ea5",
    ),
    TRIPLE_RESULTS_PATH: (
        "7487631d098876d51c24eaba75c30dfa693341833f8c85b8170a75ff647d0200",
        "ce00fc3085c7f19f0193d2d19939b6fa0e196cb8d26bcfc0c189319e4ae667ce",
    ),
    TRIPLE_MANIFEST_PATH: (
        "d76dd7168d8b3a4e4ec9e3637b959b89d2f947ba519ad4521eccd99b27699531",
        "330379eeff1ae5a805b669667cbce8a3ec98a7d63b890ad0395cdbbd35fb1b42",
    ),
    QUAD_RESULTS_PATH: (
        "35c83d1bd7be565d9ebb61cafc6b618ce9efdbfb1799bbd72061f08bd9d5f28c",
        "37e9594fb0029d19a4926ac44c0e518ddaf84cf896f784795ca4b734b8d16bf1",
    ),
    QUAD_MANIFEST_PATH: (
        "d45c15586b008663398323a2c9f25c87d76f1d9b8404356a65157d610502075d",
        "59d163738213dad1cba94545322928a8d547ad7da7ced3f7b2679631af559f64",
    ),
}
EXPECTED_LEDGER_HASHES = {
    PAIR_LEDGER_PATH: "24de12594fe8b95f6e70be4278b2dfadb7f29f181aef3d7aeea41f9fbe58de52",
    TRIPLE_LEDGER_PATH: "b342a58d20aa7ecdc2a2a5ea45037a64739134151db41b562464163b7e93578f",
    QUAD_LEDGER_PATH: "530d541e64d538c4e87dc416bda831e7caafa9b827b0068662b9117e8f70dc8a",
}

SOURCE_SPECS = {
    2: {
        "name": "PAIR",
        "ledger": PAIR_LEDGER_PATH,
        "record": struct.Struct("<HBBHBBBB"),
        "expected_records": 404_054,
        "expected_trials": {"kappa": 384_354, "lambda": 372_299},
        "expected_rescues": {"kappa": 454, "lambda": 470},
    },
    3: {
        "name": "TRIPLE",
        "ledger": TRIPLE_LEDGER_PATH,
        "record": struct.Struct("<HBBBHBBB"),
        "expected_records": 3_061_466,
        "expected_trials": {"kappa": 2_745_416, "lambda": 3_031_106},
        "expected_rescues": {"kappa": 180, "lambda": 192},
    },
    4: {
        "name": "QUADRUPLE",
        "ledger": QUAD_LEDGER_PATH,
        "record": struct.Struct("<H"),
        "expected_records": 24_362_850,
        "expected_trials": {"kappa": 20_638_850, "lambda": 19_941_575},
        "expected_rescues": {"kappa": 77, "lambda": 103},
    },
}
EXPECTED_RECORD_COUNT = sum(spec["expected_records"] for spec in SOURCE_SPECS.values())

MOTIF_IDS = {
    "2I": 0,
    "K2": 1,
    "3I": 2,
    "K2+I": 3,
    "P3": 4,
    "4I": 5,
    "K2+2I": 6,
    "2K2": 7,
    "P3+I": 8,
    "P4": 9,
    "K1_3": 10,
    "C4": 11,
}
ID_TO_MOTIF = {value: key for key, value in MOTIF_IDS.items()}
ALLOWED_MOTIFS = {
    2: {"2I", "K2"},
    3: {"3I", "K2+I", "P3"},
    4: {"4I", "K2+2I", "2K2", "P3+I", "P4", "K1_3", "C4"},
}

PAIR_FLAGS = {
    "adjacent": 0,
    "kappa_scope": 1,
    "lambda_scope": 2,
    "kappa_a": 3,
    "lambda_a": 4,
    "kappa_b": 5,
    "lambda_b": 6,
    "kappa_required": 7,
    "lambda_required": 8,
}
TRIPLE_FLAGS = {
    "kappa_scope": 2,
    "lambda_scope": 3,
    "kappa_a": 4,
    "lambda_a": 5,
    "kappa_b": 6,
    "lambda_b": 7,
    "kappa_required": 10,
    "lambda_required": 11,
}
QUAD_FLAGS = {
    "kappa_scope": 3,
    "lambda_scope": 4,
    "kappa_a": 5,
    "lambda_a": 6,
    "kappa_b": 7,
    "lambda_b": 8,
    "kappa_required": 9,
    "lambda_required": 10,
}


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


def read_json_gate(path: Path) -> dict[str, Any]:
    raw_expected, canonical_expected = EXPECTED_JSON_HASHES[path]
    if raw_sha256(path) != raw_expected:
        raise RuntimeError(f"Raw SHA-256 mismatch: {path.name}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if canonical_sha256(value) != canonical_expected:
        raise RuntimeError(f"Canonical SHA-256 mismatch: {path.name}")
    return value


def gate_inputs() -> dict[str, Any]:
    values = {path.name: read_json_gate(path) for path in EXPECTED_JSON_HASHES}
    for path, expected in EXPECTED_LEDGER_HASHES.items():
        if raw_sha256(path) != expected:
            raise RuntimeError(f"Ledger SHA-256 mismatch: {path.name}")
    for cardinality, spec in SOURCE_SPECS.items():
        if spec["ledger"].stat().st_size != spec["record"].size * spec["expected_records"]:
            raise RuntimeError(f"Cardinality-{cardinality} ledger size mismatch")
    return values


def upper_edges(cardinality: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(cardinality), 2))


def adjacency_mask(words: tuple[int, ...]) -> int:
    mask = 0
    for bit, (left, right) in enumerate(upper_edges(len(words))):
        if (words[left] ^ words[right]).bit_count() == 1:
            mask |= 1 << bit
    return mask


def permute_mask(mask: int, cardinality: int, permutation: tuple[int, ...]) -> int:
    source_edges = upper_edges(cardinality)
    edge_set = {
        frozenset((left, right))
        for bit, (left, right) in enumerate(source_edges)
        if mask & (1 << bit)
    }
    output = 0
    for bit, (left, right) in enumerate(source_edges):
        if frozenset((permutation[left], permutation[right])) in edge_set:
            output |= 1 << bit
    return output


def build_canonical_mask_tables() -> dict[int, dict[int, int]]:
    tables = {}
    for cardinality in (2, 3, 4):
        width = math.comb(cardinality, 2)
        tables[cardinality] = {
            mask: min(
                permute_mask(mask, cardinality, permutation)
                for permutation in itertools.permutations(range(cardinality))
            )
            for mask in range(1 << width)
        }
    return tables


CANONICAL_MASKS = build_canonical_mask_tables()


def graph_invariants(mask: int, cardinality: int) -> tuple[int, tuple[int, ...], tuple[int, ...]]:
    adjacency = [set() for _ in range(cardinality)]
    edge_count = 0
    for bit, (left, right) in enumerate(upper_edges(cardinality)):
        if mask & (1 << bit):
            adjacency[left].add(right)
            adjacency[right].add(left)
            edge_count += 1
    unseen = set(range(cardinality))
    components = []
    while unseen:
        stack = [unseen.pop()]
        size = 0
        while stack:
            node = stack.pop()
            size += 1
            for target in adjacency[node]:
                if target in unseen:
                    unseen.remove(target)
                    stack.append(target)
        components.append(size)
    return edge_count, tuple(sorted(map(len, adjacency))), tuple(sorted(components))


INVARIANT_TO_MOTIF = {
    (2, 0, (0, 0), (1, 1)): "2I",
    (2, 1, (1, 1), (2,)): "K2",
    (3, 0, (0, 0, 0), (1, 1, 1)): "3I",
    (3, 1, (0, 1, 1), (1, 2)): "K2+I",
    (3, 2, (1, 1, 2), (3,)): "P3",
    (4, 0, (0, 0, 0, 0), (1, 1, 1, 1)): "4I",
    (4, 1, (0, 0, 1, 1), (1, 1, 2)): "K2+2I",
    (4, 2, (1, 1, 1, 1), (2, 2)): "2K2",
    (4, 2, (0, 1, 1, 2), (1, 3)): "P3+I",
    (4, 3, (1, 1, 2, 2), (4,)): "P4",
    (4, 3, (1, 1, 1, 3), (4,)): "K1_3",
    (4, 4, (2, 2, 2, 2), (4,)): "C4",
}


def build_canonical_motif_lookup() -> dict[tuple[int, int], str]:
    output = {}
    for (cardinality, edge_count, degrees, components), motif in INVARIANT_TO_MOTIF.items():
        canonical = {
            CANONICAL_MASKS[cardinality][mask]
            for mask in range(1 << math.comb(cardinality, 2))
            if graph_invariants(mask, cardinality) == (edge_count, degrees, components)
        }
        if len(canonical) != 1:
            raise RuntimeError("Closed motif table is not isomorphically unique")
        key = (cardinality, canonical.pop())
        if key in output:
            raise RuntimeError("Closed motif table has a canonical collision")
        output[key] = motif
    return output


CANONICAL_TO_MOTIF = build_canonical_motif_lookup()


def classify_motif(words: Iterable[int]) -> dict[str, Any]:
    ordered = tuple(map(int, words))
    cardinality = len(ordered)
    if cardinality not in ALLOWED_MOTIFS or len(set(ordered)) != cardinality:
        raise ValueError("Motif words must be unique with cardinality 2..4")
    mask = adjacency_mask(ordered)
    canonical_mask = CANONICAL_MASKS[cardinality][mask]
    edge_count, degrees, components = graph_invariants(mask, cardinality)
    motif = INVARIANT_TO_MOTIF.get((cardinality, edge_count, degrees, components))
    if motif is None or motif not in ALLOWED_MOTIFS[cardinality]:
        raise RuntimeError("Unclassified or non-Q8 motif")
    if CANONICAL_TO_MOTIF.get((cardinality, canonical_mask)) != motif:
        raise RuntimeError("Independent motif classifiers disagree")
    return {
        "motif": motif,
        "motif_id": MOTIF_IDS[motif],
        "edge_count": edge_count,
        "canonical_adjacency_mask": canonical_mask,
        "degree_multiset": list(degrees),
        "component_sizes": list(components),
    }


def pack_geometry(motif_id: int, edge_count: int) -> int:
    if motif_id not in ID_TO_MOTIF or not 0 <= edge_count <= 4:
        raise ValueError("Invalid geometry record")
    return motif_id | (edge_count << 4)


def unpack_geometry(value: int) -> dict[str, Any]:
    if value & 0x80:
        raise ValueError("Geometry ledger reserved bit is nonzero")
    motif_id = value & 0x0F
    if motif_id not in ID_TO_MOTIF:
        raise ValueError("Unknown motif id")
    return {
        "motif_id": motif_id,
        "motif": ID_TO_MOTIF[motif_id],
        "edge_count": (value >> 4) & 0x07,
    }


def source_flags(cardinality: int) -> dict[str, int]:
    return {2: PAIR_FLAGS, 3: TRIPLE_FLAGS, 4: QUAD_FLAGS}[cardinality]


def reconcile_metric_flags(*, scope: bool, route_a: bool, route_b: bool, required: bool) -> str:
    if route_a != route_b or (required and (not scope or not route_a)):
        raise RuntimeError("Source scope/route/requirement reconciliation failed")
    if route_a and not scope:
        return "OUT_OF_SCOPE_DIAGNOSTIC"
    if scope and route_a:
        return "SCOPED_RESCUE"
    return "NONRESCUE"


def build_tasks(values: dict[str, Any]) -> list[dict[str, Any]]:
    pair_results = values[PAIR_RESULTS_PATH.name]
    triple_results = values[TRIPLE_RESULTS_PATH.name]
    quad_manifest = values[QUAD_MANIFEST_PATH.name]
    tasks: list[dict[str, Any]] = []
    geometry_offset = 0
    for cardinality, rows, count_key in (
        (2, pair_results["strata"], "pair_count"),
        (3, triple_results["strata"], "triple_count"),
    ):
        source_offset = 0
        for row in sorted(rows, key=lambda item: int(item["stratum_index"])):
            count = int(row[count_key])
            tasks.append(
                {
                    "cardinality": cardinality,
                    "source_name": SOURCE_SPECS[cardinality]["name"],
                    "stratum_index": int(row["stratum_index"]),
                    "source_record_offset": source_offset,
                    "record_count": count,
                    "geometry_record_offset": geometry_offset,
                }
            )
            source_offset += count
            geometry_offset += count
        if source_offset != SOURCE_SPECS[cardinality]["expected_records"]:
            raise RuntimeError(f"Cardinality-{cardinality} task count mismatch")
    source_offset = 0
    for segment in quad_manifest["segments"]:
        count = int(segment["record_count"])
        if int(segment["record_offset"]) != source_offset:
            raise RuntimeError("Quadruple source offsets are not contiguous")
        tasks.append(
            {
                "cardinality": 4,
                "source_name": "QUADRUPLE",
                "stratum_index": int(segment["stratum_index"]),
                "source_record_offset": source_offset,
                "record_count": count,
                "geometry_record_offset": geometry_offset,
                "ordered_words": list(map(int, segment["ordered_words"])),
                "ordered_words_sha256": segment["ordered_words_sha256"],
            }
        )
        source_offset += count
        geometry_offset += count
    if source_offset != SOURCE_SPECS[4]["expected_records"] or geometry_offset != EXPECTED_RECORD_COUNT:
        raise RuntimeError("Global task count mismatch")
    return tasks


def iter_task_records(task: dict[str, Any], limit: int | None = None) -> Iterator[dict[str, Any]]:
    cardinality = int(task["cardinality"])
    spec = SOURCE_SPECS[cardinality]
    record = spec["record"]
    count = int(task["record_count"] if limit is None else min(limit, task["record_count"]))
    if cardinality == 4:
        combinations = itertools.islice(
            itertools.combinations(task["ordered_words"], 4), count
        )
        with spec["ledger"].open("rb") as handle:
            handle.seek(int(task["source_record_offset"]) * record.size)
            for local_index, words in enumerate(combinations):
                raw = handle.read(record.size)
                if len(raw) != record.size:
                    raise RuntimeError("Truncated quadruple ledger")
                (flags,) = record.unpack(raw)
                yield {"local_index": local_index, "words": tuple(words), "flags": flags}
        return
    with spec["ledger"].open("rb") as handle:
        handle.seek(int(task["source_record_offset"]) * record.size)
        for local_index in range(count):
            raw = handle.read(record.size)
            if len(raw) != record.size:
                raise RuntimeError(f"Truncated cardinality-{cardinality} ledger")
            values = record.unpack(raw)
            if int(values[0]) != int(task["stratum_index"]):
                raise RuntimeError("Source stratum index mismatch")
            words = tuple(map(int, values[1 : 1 + cardinality]))
            flags = int(values[1 + cardinality])
            yield {"local_index": local_index, "words": words, "flags": flags}


def classify_task(task_and_limit: tuple[dict[str, Any], int | None]) -> dict[str, Any]:
    task, limit = task_and_limit
    cardinality = int(task["cardinality"])
    output = bytearray()
    distribution = Counter()
    for row in iter_task_records(task, limit):
        geometry = classify_motif(row["words"])
        source_edge_count = {
            2: int(bool(row["flags"] & 1)),
            3: row["flags"] & 0b11,
            4: row["flags"] & 0b111,
        }[cardinality]
        if source_edge_count != geometry["edge_count"]:
            raise RuntimeError("Outcome-blind geometry disagrees with source edge count")
        output.append(pack_geometry(geometry["motif_id"], geometry["edge_count"]))
        distribution[geometry["motif"]] += 1
    return {
        "cardinality": cardinality,
        "stratum_index": int(task["stratum_index"]),
        "processed": len(output),
        "geometry": bytes(output),
        "distribution": dict(sorted(distribution.items())),
    }


def representative_sample(tasks: list[dict[str, Any]], cardinality: int, target: int = 180_000) -> list[tuple[dict[str, Any], int]]:
    candidates = [task for task in tasks if int(task["cardinality"]) == cardinality]
    step = max(1, len(candidates) // 17)
    while math.gcd(step, len(candidates)) != 1:
        step += 1
    positions = []
    position = 0
    for _ in candidates:
        positions.append(position)
        position = (position + step) % len(candidates)
    selected = []
    remaining = target
    for index, position in enumerate(positions):
        if remaining <= 0 and len(selected) >= 5:
            break
        task = candidates[position]
        slots_left = max(1, min(5 - len(selected), len(positions) - index))
        limit = min(int(task["record_count"]), max(1, math.ceil(max(remaining, 1) / slots_left)))
        selected.append((task, limit))
        remaining -= limit
    return selected


def validate_join_sample(sample: list[tuple[dict[str, Any], int]], rows: list[dict[str, Any]]) -> tuple[int, float]:
    started = time.perf_counter()
    processed = 0
    for (task, limit), classified in zip(sample, rows, strict=True):
        geometry = classified["geometry"]
        for row, packed in zip(iter_task_records(task, limit), geometry, strict=True):
            decoded = unpack_geometry(packed)
            if decoded["edge_count"] != adjacency_mask(row["words"]).bit_count():
                raise RuntimeError("Benchmark join geometry mismatch")
            processed += 1
    return processed, time.perf_counter() - started


def benchmark_mechanisms(values: dict[str, Any], tasks: list[dict[str, Any]], target_per_cardinality: int = 2) -> dict[str, Any]:
    started = time.perf_counter()
    phase102_module, contexts = build_context_lookup(values)
    audited = 0
    by_cardinality = Counter()
    for cardinality in (2, 3, 4):
        for task in tasks:
            if int(task["cardinality"]) != cardinality:
                continue
            stratum, base = source_stratum(values, cardinality, int(task["stratum_index"]))
            flags_map = source_flags(cardinality)
            context = contexts[(base["cube_key"], int(base["pair_index"]))]
            for row in iter_task_records(task):
                for metric in ("kappa", "lambda"):
                    in_scope = bool(row["flags"] & (1 << flags_map[f"{metric}_scope"]))
                    if in_scope and row["flags"] & (1 << flags_map[f"{metric}_a"]):
                        audit = audit_rescue_set(phase102_module, context, row["words"], metric)
                        if not audit["full_rescue"]:
                            raise RuntimeError("Benchmark mechanism replay failed")
                        audited += 1
                        by_cardinality[cardinality] += 1
                        if by_cardinality[cardinality] >= target_per_cardinality:
                            break
                if by_cardinality[cardinality] >= target_per_cardinality:
                    break
            if by_cardinality[cardinality] >= target_per_cardinality:
                break
    wall = time.perf_counter() - started
    expected_audits = sum(
        sum(spec["expected_rescues"].values()) for spec in SOURCE_SPECS.values()
    )
    rate = audited / wall
    return {
        "audited_rescue_metric_records": audited,
        "wall_seconds": wall,
        "audits_per_second": rate,
        "projected_full_seconds": expected_audits / rate,
        "expected_full_audit_count": expected_audits,
        "by_cardinality": dict(sorted(by_cardinality.items())),
    }


def run_benchmark(values: dict[str, Any], tasks: list[dict[str, Any]], workers: int) -> dict[str, Any]:
    if not 1 <= workers <= 16:
        raise ValueError("workers must be between 1 and 16")
    by_cardinality = {}
    total_wall = 0.0
    total_processed = 0
    projected_geometry = 0.0
    projected_join = 0.0
    for cardinality in (2, 3, 4):
        sample = representative_sample(tasks, cardinality)
        started = time.perf_counter()
        with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
            rows = list(executor.map(classify_task, sample))
        wall = time.perf_counter() - started
        processed = sum(row["processed"] for row in rows)
        rate = processed / wall
        projected = SOURCE_SPECS[cardinality]["expected_records"] / rate
        join_processed, join_wall = validate_join_sample(sample, rows)
        join_rate = join_processed / join_wall
        join_projected = SOURCE_SPECS[cardinality]["expected_records"] / join_rate
        aggregate = Counter()
        for row in rows:
            aggregate.update(row["distribution"])
        by_cardinality[str(cardinality)] = {
            "processed_records": processed,
            "wall_seconds": wall,
            "records_per_second": rate,
            "projected_full_seconds": projected,
            "join_records_per_second": join_rate,
            "projected_join_seconds": join_projected,
            "sample_strata": [row[0]["stratum_index"] for row in sample],
            "motif_distribution": dict(sorted(aggregate.items())),
        }
        total_wall += wall
        total_processed += processed
        projected_geometry += projected
        projected_join += join_projected
    mechanism_benchmark = benchmark_mechanisms(values, tasks)
    projected_total = projected_geometry + projected_join + mechanism_benchmark["projected_full_seconds"]
    available = shutil.disk_usage(RUNTIME_DIR.parent if RUNTIME_DIR.parent.exists() else ROOT).free
    required = max(500 * 1024 * 1024, EXPECTED_RECORD_COUNT * 5)
    report = {
        "status": "PASS" if available >= required else "INSUFFICIENT_DISK",
        "phase": 106,
        "mode": "BENCHMARK_ONLY",
        "workers": workers,
        "runner_sha256": normalized_source_sha256(Path(__file__)),
        "processed_records": total_processed,
        "wall_seconds": total_wall,
        "projected_full_seconds": projected_total,
        "projected_full_seconds_with_25pct_margin": projected_total * 1.25,
        "full_record_count": EXPECTED_RECORD_COUNT,
        "full_geometry_ledger_bytes": EXPECTED_RECORD_COUNT,
        "observed_free_bytes": available,
        "required_free_bytes": required,
        "by_cardinality": by_cardinality,
        "mechanism_benchmark": mechanism_benchmark,
        "projection_components": {
            "geometry_pass_seconds": projected_geometry,
            "outcome_join_seconds": projected_join,
            "rescue_mechanism_audit_seconds": mechanism_benchmark["projected_full_seconds"],
        },
        "input_hashes": input_hash_payload(),
        "full_run_executed": False,
        "simulation_executed": False,
    }
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    atomic_write(BENCHMARK_PATH, json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    return report


def input_hash_payload() -> dict[str, Any]:
    return {
        path.name: {"raw": hashes[0], "canonical": hashes[1]}
        for path, hashes in EXPECTED_JSON_HASHES.items()
    } | {path.name: {"sha256": digest} for path, digest in EXPECTED_LEDGER_HASHES.items()}


def checkpoint_paths(task: dict[str, Any]) -> tuple[Path, Path]:
    stem = f"n{task['cardinality']}_s{int(task['stratum_index']):03d}"
    return CHECKPOINT_DIR / f"{stem}.bin", CHECKPOINT_DIR / f"{stem}.json"


def checkpoint_identity(task: dict[str, Any]) -> dict[str, Any]:
    return {
        "cardinality": int(task["cardinality"]),
        "stratum_index": int(task["stratum_index"]),
        "source_record_offset": int(task["source_record_offset"]),
        "record_count": int(task["record_count"]),
        "geometry_record_offset": int(task["geometry_record_offset"]),
        "source_ledger_sha256": EXPECTED_LEDGER_HASHES[SOURCE_SPECS[int(task["cardinality"])]["ledger"]],
        "runner_sha256": normalized_source_sha256(Path(__file__)),
    }


def save_checkpoint(task: dict[str, Any], row: dict[str, Any]) -> None:
    binary_path, metadata_path = checkpoint_paths(task)
    data = row["geometry"]
    metadata = checkpoint_identity(task) | {
        "processed": int(row["processed"]),
        "geometry_sha256": hashlib.sha256(data).hexdigest(),
        "distribution": row["distribution"],
    }
    atomic_write(binary_path, data)
    atomic_write(metadata_path, json.dumps(metadata, indent=2, sort_keys=True).encode("utf-8") + b"\n")


def load_checkpoint(task: dict[str, Any]) -> dict[str, Any] | None:
    binary_path, metadata_path = checkpoint_paths(task)
    if not binary_path.exists() or not metadata_path.exists():
        return None
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        identity = checkpoint_identity(task)
        if any(metadata.get(key) != value for key, value in identity.items()):
            return None
        data = binary_path.read_bytes()
        if len(data) != int(task["record_count"]) or hashlib.sha256(data).hexdigest() != metadata["geometry_sha256"]:
            return None
        return {
            "cardinality": int(task["cardinality"]),
            "stratum_index": int(task["stratum_index"]),
            "processed": len(data),
            "geometry": data,
            "distribution": metadata["distribution"],
        }
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return None


def validate_full_authorization(path: Path, benchmark_path: Path, workers: int) -> dict[str, Any]:
    benchmark_digest = raw_sha256(benchmark_path)
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    authorization = json.loads(path.read_text(encoding="utf-8"))
    expected_text = (
        f"Autorizo el barrido completo de Fase 106 con {workers} workers, "
        f"ligado al benchmark SHA-256 {benchmark_digest}."
    )
    checks = (
        benchmark.get("status") == "PASS",
        int(benchmark.get("workers", -1)) == workers,
        benchmark.get("runner_sha256") == normalized_source_sha256(Path(__file__)),
        int(benchmark.get("full_record_count", -1)) == EXPECTED_RECORD_COUNT,
        authorization.get("authorization") == expected_text,
        authorization.get("benchmark_report_sha256") == benchmark_digest,
        int(authorization.get("workers", -1)) == workers,
        int(authorization.get("expected_record_count", -1)) == EXPECTED_RECORD_COUNT,
    )
    if not all(checks):
        raise RuntimeError("Full-run authorization or benchmark binding mismatch")
    return authorization


def load_phase102_module():
    path = OUTPUT_DIR / "analyze_phase102_pairwise_synergy.py"
    spec = importlib.util.spec_from_file_location("phase106_phase102", path)
    module = importlib.util.module_from_spec(spec)
    if spec.loader is None:
        raise RuntimeError("Cannot load Fase-102 module")
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def add_words(base: dict[int, set[int]], words: tuple[int, ...], *, internal_edges: bool) -> tuple[dict[int, set[int]], tuple[tuple[int, int], ...], tuple[tuple[int, int], ...]]:
    adjacency = {node: set(targets) for node, targets in base.items()}
    selected = set(words)
    for word in words:
        if word in adjacency:
            raise RuntimeError("Intervention word already belongs to F1")
        adjacency[word] = set()
    new_edges = set()
    internal = set()
    for word in words:
        for bit in range(8):
            target = word ^ (1 << bit)
            if target not in adjacency or target == word:
                continue
            edge = tuple(sorted((word, target)))
            if target in selected:
                internal.add(edge)
                if not internal_edges:
                    continue
            new_edges.add(edge)
            adjacency[word].add(target)
            adjacency[target].add(word)
    return adjacency, tuple(sorted(new_edges)), tuple(sorted(internal))


def cut_audit(phase102: Any, context: dict[str, Any], adjacency: dict[int, set[int]], words: tuple[int, ...], new_edges: tuple[tuple[int, int], ...]) -> dict[str, Any]:
    vertex_states = [
        phase102.terminals_connected(adjacency, context["component_a"], context["component_b"], removed_vertex=cut)
        for cut in context["critical_vertices"]
    ]
    edge_states = [
        phase102.terminals_connected(adjacency, context["component_a"], context["component_b"], removed_edge=cut)
        for cut in context["critical_edges"]
    ]
    new_vertex_separators = [
        word
        for word in words
        if not phase102.terminals_connected(adjacency, context["component_a"], context["component_b"], removed_vertex=word)
    ]
    new_edge_separators = [
        list(edge)
        for edge in new_edges
        if not phase102.terminals_connected(adjacency, context["component_a"], context["component_b"], removed_edge=edge)
    ]
    return {
        "vertex_cut_states": vertex_states,
        "edge_cut_states": edge_states,
        "uncovered_original_vertices": vertex_states.count(False),
        "uncovered_original_edges": edge_states.count(False),
        "new_vertex_separators": new_vertex_separators,
        "new_edge_separators": new_edge_separators,
        "kappa_rescue": all(vertex_states) and not new_vertex_separators,
        "lambda_rescue": all(edge_states) and not new_edge_separators,
    }


def remove_edge_copy(adjacency: dict[int, set[int]], edge: tuple[int, int]) -> dict[int, set[int]]:
    output = {node: set(targets) for node, targets in adjacency.items()}
    output[edge[0]].discard(edge[1])
    output[edge[1]].discard(edge[0])
    return output


def classify_cut_mechanisms(individual: list[list[bool]], external: list[bool], full: list[bool]) -> list[str]:
    if not (len(external) == len(full) and all(len(row) == len(full) for row in individual)):
        raise RuntimeError("Cut-mechanism dimensions disagree")
    output = []
    for index in range(len(full)):
        if any(row[index] for row in individual):
            output.append("INDIVIDUAL")
        elif external[index]:
            output.append("DISTRIBUTED_EXTERNAL")
        elif full[index]:
            output.append("INTERNAL_EDGE_ENABLED")
        else:
            output.append("UNCOVERED")
    return output


def audit_rescue_set(phase102: Any, context: dict[str, Any], words: tuple[int, ...], metric: str) -> dict[str, Any]:
    full_graph, full_new_edges, internal = add_words(context["adjacency"], words, internal_edges=True)
    external_graph, external_new_edges, _ = add_words(context["adjacency"], words, internal_edges=False)
    full = cut_audit(phase102, context, full_graph, words, full_new_edges)
    external = cut_audit(phase102, context, external_graph, words, external_new_edges)
    individual_audits = []
    for word in words:
        graph, edges, _ = add_words(context["adjacency"], (word,), internal_edges=False)
        individual_audits.append(cut_audit(phase102, context, graph, (word,), edges))
    cut_key = "vertex_cut_states" if metric == "kappa" else "edge_cut_states"
    rescue_key = "kappa_rescue" if metric == "kappa" else "lambda_rescue"
    uncovered_key = "uncovered_original_vertices" if metric == "kappa" else "uncovered_original_edges"
    separator_key = "new_vertex_separators" if metric == "kappa" else "new_edge_separators"
    mechanisms = classify_cut_mechanisms(
        [audit[cut_key] for audit in individual_audits], external[cut_key], full[cut_key]
    )
    flow_function = phase102.vertex_connectivity_two if metric == "kappa" else phase102.edge_connectivity_two
    full_flow_rescue = flow_function(full_graph, context["component_a"], context["component_b"])
    external_flow_rescue = flow_function(external_graph, context["component_a"], context["component_b"])
    if full_flow_rescue != full[rescue_key] or external_flow_rescue != external[rescue_key]:
        raise RuntimeError("Direct-cut and max-flow routes disagree")
    edge_removals = []
    for edge in internal:
        reduced = remove_edge_copy(full_graph, edge)
        reduced_new_edges = tuple(item for item in full_new_edges if item != edge)
        audit = cut_audit(phase102, context, reduced, words, reduced_new_edges)
        flow_rescue = flow_function(reduced, context["component_a"], context["component_b"])
        if flow_rescue != audit[rescue_key]:
            raise RuntimeError("Per-edge direct-cut and max-flow routes disagree")
        edge_removals.append(
            {
                "edge": list(edge),
                "covers_all_original_cuts": audit[uncovered_key] == 0,
                "rescue": bool(audit[rescue_key]),
                "max_flow_rescue": bool(flow_rescue),
                "uncovered_original_cut_count": int(audit[uncovered_key]),
                "new_separator_count": len(audit[separator_key]),
            }
        )
    return {
        "metric": metric,
        "full_rescue": bool(full[rescue_key]),
        "external_rescue": bool(external[rescue_key]),
        "covers_all_original_cuts": full[uncovered_key] == 0,
        "cut_mechanism_counts": dict(sorted(Counter(mechanisms).items())),
        "cut_mechanisms": mechanisms,
        "new_separator_count": len(full[separator_key]),
        "internal_edges": [list(edge) for edge in internal],
        "per_internal_edge_removal": edge_removals,
        "mechanism_label": (
            "EXTERNAL_ATTACHMENT_RESCUE"
            if external[rescue_key]
            else "INTERNAL_EDGE_DEPENDENT_RESCUE"
        ),
        "internal_edge_required": any(not row["rescue"] for row in edge_removals),
    }


def build_context_lookup(values: dict[str, Any]) -> tuple[Any, dict[tuple[str, int], dict[str, Any]]]:
    phase102_module = load_phase102_module()
    phase95 = values[PHASE95_PATH.name]
    phase97 = values[PHASE97_PATH.name]
    phase102_results = values[PHASE102_PATH.name]
    pair_results = values[PAIR_RESULTS_PATH.name]
    cubes = {row["cube_key"]: row for row in phase95["cube_nodes"]}
    pairs = {(row["cube_key"], int(row["pair_index"])): row for row in phase97["component_pairs"]}
    audits = {(row["cube_key"], int(row["pair_index"])): row for row in phase102_results["target_cut_audits"]}
    contexts = {}
    for stratum in pair_results["strata"]:
        key = (stratum["cube_key"], int(stratum["pair_index"]))
        if key in contexts:
            continue
        pair = pairs[key]
        contexts[key] = phase102_module.build_context(
            cubes[key[0]], pair, pair["physical_class_sha256"], audits[key]
        )
    return phase102_module, contexts


def source_stratum(values: dict[str, Any], cardinality: int, index: int) -> tuple[dict[str, Any], dict[str, Any]]:
    pair_strata = values[PAIR_RESULTS_PATH.name]["strata"]
    if cardinality == 2:
        return pair_strata[index], pair_strata[index]
    triple = values[TRIPLE_RESULTS_PATH.name]["strata"][index]
    if cardinality == 3:
        return triple, pair_strata[int(triple["phase103_stratum_index"])]
    quad = values[QUAD_RESULTS_PATH.name]["strata"][index]
    triple = values[TRIPLE_RESULTS_PATH.name]["strata"][int(quad["phase104_stratum_index"])]
    return quad, pair_strata[int(triple["phase103_stratum_index"])]


def validate_minimality(values: dict[str, Any], cardinality: int, stratum: dict[str, Any], metric: str) -> None:
    prefix = "kappa" if metric == "kappa" else "lambda"
    if cardinality == 2:
        if stratum[f"{prefix}_minimal_cardinality"] != "EXACTLY_2":
            raise RuntimeError("Pair rescue violates singleton minimality")
        return
    if cardinality == 3:
        pair = values[PAIR_RESULTS_PATH.name]["strata"][int(stratum["phase103_stratum_index"])]
        if int(pair[f"{prefix}_pair_rescue_count"]) != 0 or stratum[f"{prefix}_minimal_cardinality"] != "EXACTLY_3":
            raise RuntimeError("Triple rescue violates lower-cardinality replay")
        return
    triple = values[TRIPLE_RESULTS_PATH.name]["strata"][int(stratum["phase104_stratum_index"])]
    pair = values[PAIR_RESULTS_PATH.name]["strata"][int(triple["phase103_stratum_index"])]
    if (
        int(pair[f"{prefix}_pair_rescue_count"]) != 0
        or int(triple[f"{prefix}_triple_rescue_count"]) != 0
        or stratum[f"{prefix}_minimal_cardinality"] != "EXACTLY_4"
    ):
        raise RuntimeError("Quadruple rescue violates lower-cardinality replay")


def aggregate_full(values: dict[str, Any], tasks: list[dict[str, Any]], geometry_path: Path) -> dict[str, Any]:
    phase102_module, contexts = build_context_lookup(values)
    geometry_distribution: dict[int, Counter] = {2: Counter(), 3: Counter(), 4: Counter()}
    outcomes: dict[int, dict[str, dict[str, Counter]]] = {
        n: {metric: defaultdict(Counter) for metric in ("kappa", "lambda")}
        for n in (2, 3, 4)
    }
    mechanism_audits = []
    reconciliation_failures = []
    diagnostic_out_of_scope_routes: dict[int, Counter] = {
        2: Counter(),
        3: Counter(),
        4: Counter(),
    }
    global_index = 0
    with geometry_path.open("rb") as geometry_handle:
        for task in tasks:
            cardinality = int(task["cardinality"])
            flags_map = source_flags(cardinality)
            stratum, base_pair_stratum = source_stratum(values, cardinality, int(task["stratum_index"]))
            context_key = (base_pair_stratum["cube_key"], int(base_pair_stratum["pair_index"]))
            context = contexts[context_key]
            for row in iter_task_records(task):
                raw_geometry = geometry_handle.read(1)
                if len(raw_geometry) != 1:
                    raise RuntimeError("Geometry ledger is truncated")
                geometry = unpack_geometry(raw_geometry[0])
                if geometry["edge_count"] != adjacency_mask(row["words"]).bit_count():
                    raise RuntimeError("Geometry join mismatch")
                geometry_distribution[cardinality][geometry["motif"]] += 1
                flags = int(row["flags"])
                manifest_name = {
                    2: PAIR_MANIFEST_PATH.name,
                    3: TRIPLE_MANIFEST_PATH.name,
                    4: QUAD_MANIFEST_PATH.name,
                }[cardinality]
                allowed_bits = set(map(int, values[manifest_name]["flag_bits"].values())) | (
                    {0} if cardinality == 2 else {0, 1} if cardinality == 3 else {0, 1, 2}
                )
                reserved_mask = flags & ~sum(1 << bit for bit in allowed_bits)
                if reserved_mask:
                    raise RuntimeError("Source ledger has nonzero reserved/out-of-scope bits")
                for metric in ("kappa", "lambda"):
                    scope = bool(flags & (1 << flags_map[f"{metric}_scope"]))
                    route_a = bool(flags & (1 << flags_map[f"{metric}_a"]))
                    route_b = bool(flags & (1 << flags_map[f"{metric}_b"]))
                    required = bool(flags & (1 << flags_map[f"{metric}_required"]))
                    flag_status = reconcile_metric_flags(
                        scope=scope,
                        route_a=route_a,
                        route_b=route_b,
                        required=required,
                    )
                    if flag_status == "OUT_OF_SCOPE_DIAGNOSTIC":
                        diagnostic_out_of_scope_routes[cardinality][metric] += 1
                    bucket = outcomes[cardinality][metric][geometry["motif"]]
                    bucket["records"] += 1
                    if scope:
                        bucket["trials"] += 1
                    if flag_status == "SCOPED_RESCUE":
                        bucket["rescues"] += 1
                        if required:
                            bucket["internal_edge_required"] += 1
                        validate_minimality(values, cardinality, stratum, metric)
                        audit = audit_rescue_set(phase102_module, context, row["words"], metric)
                        if not audit["full_rescue"] or audit["internal_edge_required"] != required:
                            reconciliation_failures.append(
                                {"global_index": global_index, "metric": metric, "reason": "mechanism_replay"}
                            )
                        mechanism_audits.append(
                            {
                                "global_record_index": global_index,
                                "cardinality": cardinality,
                                "stratum_index": int(task["stratum_index"]),
                                "cube_key": stratum["cube_key"],
                                "pair_index": int(stratum["pair_index"]),
                                "rule": int(stratum["rule"]),
                                "period": int(stratum["period"]),
                                "words": list(row["words"]),
                                "motif": geometry["motif"],
                                "source_internal_edge_required": required,
                                **audit,
                            }
                        )
                global_index += 1
        if geometry_handle.read(1):
            raise RuntimeError("Geometry ledger has trailing bytes")
    if global_index != EXPECTED_RECORD_COUNT or reconciliation_failures:
        raise RuntimeError("Full reconciliation failed")
    serialized_outcomes = {}
    for cardinality in (2, 3, 4):
        serialized_outcomes[str(cardinality)] = {}
        for metric in ("kappa", "lambda"):
            rows = {}
            total_trials = total_rescues = 0
            for motif, counts in sorted(outcomes[cardinality][metric].items()):
                record = dict(counts)
                record["outcome_label"] = (
                    "MOTIF_OUTCOME_HETEROGENEOUS"
                    if record.get("rescues", 0) and record.get("rescues", 0) < record.get("trials", 0)
                    else "RESCUE_ONLY" if record.get("rescues", 0) else "NONRESCUE_ONLY"
                )
                rows[motif] = record
                total_trials += record.get("trials", 0)
                total_rescues += record.get("rescues", 0)
            spec = SOURCE_SPECS[cardinality]
            if total_trials != spec["expected_trials"][metric] or total_rescues != spec["expected_rescues"][metric]:
                raise RuntimeError("Source summary replay mismatch")
            serialized_outcomes[str(cardinality)][metric] = {
                "trial_count": total_trials,
                "rescue_count": total_rescues,
                "by_motif": rows,
            }
    return {
        "geometry_distribution": {
            str(n): dict(sorted(counts.items())) for n, counts in geometry_distribution.items()
        },
        "outcomes": serialized_outcomes,
        "mechanism_audits": mechanism_audits,
        "diagnostic_out_of_scope_route_true": {
            str(n): dict(sorted(counts.items()))
            for n, counts in diagnostic_out_of_scope_routes.items()
        },
        "reconciliation_failure_count": 0,
    }


def build_geometry_manifest(tasks: list[dict[str, Any]], ledger: bytes) -> dict[str, Any]:
    return {
        "phase": 106,
        "byte_order": "not-applicable-single-byte",
        "record_format": "uint8",
        "record_size": 1,
        "record_count": len(ledger),
        "ledger_size": len(ledger),
        "ledger_sha256": hashlib.sha256(ledger).hexdigest(),
        "encoding": {"bits_0_3": "motif_id", "bits_4_6": "internal_edge_count", "bit_7": "reserved_zero"},
        "motif_ids": MOTIF_IDS,
        "segments": [
            {
                key: task[key]
                for key in (
                    "cardinality",
                    "source_name",
                    "stratum_index",
                    "source_record_offset",
                    "record_count",
                    "geometry_record_offset",
                )
            }
            for task in tasks
        ],
        "source_hashes": input_hash_payload(),
        "outcome_blind_geometry_pass": True,
    }


def render_report(result: dict[str, Any]) -> str:
    lines = [
        "# Fase 106 - Minimal rescue motif atlas",
        "",
        f"**Verdict:** `{result['status']}`",
        "",
        "No cellular-automaton simulations were executed. Geometry was frozen before outcomes were joined.",
        "",
        "## Frozen denominators",
        "",
        "| Cardinality | Metric | Trials | Minimal rescues |",
        "|---:|---|---:|---:|",
    ]
    for cardinality in (2, 3, 4):
        for metric in ("kappa", "lambda"):
            row = result["atlas"]["outcomes"][str(cardinality)][metric]
            lines.append(f"| {cardinality} | {metric} | {row['trial_count']} | {row['rescue_count']} |")
    lines += [
        "",
        "## Methodological limits",
        "",
        "- Motif classes are exact unlabeled induced Hamming-1 graphs; edge count alone is never used as the class.",
        "- Motif/outcome heterogeneity is retained and never repaired by post-hoc class merging.",
        "- Cut coverage, full rescue, and internal-edge dependence are separate reported quantities.",
        "- Every internal edge has an explicit removal audit: coverage, rescue, uncovered cuts, and new separators.",
        "- Results remain limited to the frozen 48 Q8 cubes and cardinalities 2-4.",
        "- The sparse motif/cut representation is QUBO-compatible data, not a quantum algorithm or advantage claim.",
    ]
    return "\n".join(lines) + "\n"


def run_full(values: dict[str, Any], tasks: list[dict[str, Any]], workers: int, authorization_path: Path) -> dict[str, Any]:
    validate_full_authorization(authorization_path, BENCHMARK_PATH, workers)
    authorization_path.unlink()
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    rows: dict[tuple[int, int], dict[str, Any]] = {}
    missing = []
    for task in tasks:
        loaded = load_checkpoint(task)
        if loaded is None:
            missing.append(task)
        else:
            rows[(int(task["cardinality"]), int(task["stratum_index"]))] = loaded
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(classify_task, (task, None)): task for task in missing}
        for future in concurrent.futures.as_completed(futures):
            task = futures[future]
            row = future.result()
            save_checkpoint(task, row)
            rows[(int(task["cardinality"]), int(task["stratum_index"]))] = row
    geometry = b"".join(
        rows[(int(task["cardinality"]), int(task["stratum_index"]))]["geometry"]
        for task in tasks
    )
    if len(geometry) != EXPECTED_RECORD_COUNT:
        raise RuntimeError("Geometry ledger length mismatch")
    staging = RUNTIME_DIR / "staging"
    staging.mkdir(parents=True, exist_ok=True)
    staging_ledger = staging / GEOMETRY_LEDGER_PATH.name
    atomic_write(staging_ledger, geometry)
    manifest = build_geometry_manifest(tasks, geometry)
    atlas = aggregate_full(values, tasks, staging_ledger)
    result = {
        "phase": 106,
        "status": "MINIMAL_RESCUE_MOTIF_ATLAS_BUILT",
        "protocol": {
            "simulation_executed": False,
            "threshold_scan_executed": False,
            "geometry_frozen_before_outcome_join": True,
            "cardinalities_mixed_in_rates": False,
            "quantum_execution": False,
            "quantum_advantage_claimed": False,
        },
        "sources": input_hash_payload(),
        "geometry_manifest_sha256": canonical_sha256(manifest),
        "atlas": atlas,
    }
    report = render_report(result)
    staged_manifest = staging / GEOMETRY_MANIFEST_PATH.name
    staged_results = staging / RESULTS_PATH.name
    staged_report = staging / REPORT_PATH.name
    atomic_write(staged_manifest, json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    atomic_write(staged_results, json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    atomic_write(staged_report, report.encode("utf-8"))
    for source, target in (
        (staging_ledger, GEOMETRY_LEDGER_PATH),
        (staged_manifest, GEOMETRY_MANIFEST_PATH),
        (staged_results, RESULTS_PATH),
        (staged_report, REPORT_PATH),
    ):
        os.replace(source, target)
    shutil.rmtree(CHECKPOINT_DIR, ignore_errors=True)
    shutil.rmtree(staging, ignore_errors=True)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fase 106 minimal-rescue motif atlas")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--benchmark", action="store_true")
    modes.add_argument("--full", action="store_true")
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--authorization", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    values = gate_inputs()
    tasks = build_tasks(values)
    if args.preflight:
        print(json.dumps({"phase": 106, "task_count": len(tasks), "record_count": EXPECTED_RECORD_COUNT, "simulation_executed": False}, sort_keys=True))
        return 0
    if args.benchmark:
        print(json.dumps(run_benchmark(values, tasks, args.workers), indent=2, sort_keys=True))
        return 0
    if args.authorization is None:
        raise RuntimeError("--authorization is required for --full")
    result = run_full(values, tasks, args.workers, args.authorization)
    print(json.dumps(result["atlas"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
