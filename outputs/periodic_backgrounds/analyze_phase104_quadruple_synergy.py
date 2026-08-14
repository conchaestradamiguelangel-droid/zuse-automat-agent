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
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "outputs" / "periodic_backgrounds"
PHASE95_PATH = OUTPUT_DIR / "phase94_hypercube_completion_results.json"
PHASE97_PATH = OUTPUT_DIR / "phase96_bridge_robustness_results.json"
PHASE102_PATH = OUTPUT_DIR / "phase101_cut_coverage_law_results.json"
PHASE103_RESULTS_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_results.json"
PHASE103_MANIFEST_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_manifest.json"
PHASE103_LEDGER_PATH = OUTPUT_DIR / "phase102_pairwise_synergy_ledger.bin"
PHASE104_RESULTS_PATH = OUTPUT_DIR / "phase103_triple_synergy_results.json"
PHASE104_MANIFEST_PATH = OUTPUT_DIR / "phase103_triple_synergy_manifest.json"
PHASE104_LEDGER_PATH = OUTPUT_DIR / "phase103_triple_synergy_ledger.bin"

LEDGER_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_ledger.bin"
MANIFEST_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_manifest.json"
RESULTS_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_results.json"
REPORT_PATH = OUTPUT_DIR / "phase104_quadruple_synergy_report.md"
RUNTIME_DIR = Path.home() / ".codex" / "runtime" / "zuse_phase105"
BENCHMARK_REPORT_PATH = RUNTIME_DIR / "phase105_benchmark_report.json"
BENCHMARK_TEMP_PATH = RUNTIME_DIR / ".phase105_benchmark_ledger.tmp"

EXPECTED_HASHES = {
    "phase95": (
        "1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3",
        "57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429",
    ),
    "phase97": (
        "3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858",
        "85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b",
    ),
    "phase102": (
        "2eae9b4825bb78d9c396a47bfe365c0beedda198de7c8a2a6093fede3423fb2c",
        "3ecad4486d9ac87c5c7efc58726a41dcaacd738d6450ffc6024b3577dbd0b74e",
    ),
    "phase103_results": (
        "9a5c70318085c8d6d1a7ad82a59fb631abda524926288c46cb0da30a7cd47268",
        "152003197716bff38e552b3b51754df6dbfe4c6dc9f93326c3a55de594e5a6c3",
    ),
    "phase103_manifest": (
        "d434a20dd0c66350fadceac6ea4f6e3d73bd9769e51195083efc628ed8170057",
        "580635c42efc2bb042e539f0a1f61d6ae15693d38d77a3333041757be9257ea5",
    ),
    "phase104_results": (
        "7487631d098876d51c24eaba75c30dfa693341833f8c85b8170a75ff647d0200",
        "ce00fc3085c7f19f0193d2d19939b6fa0e196cb8d26bcfc0c189319e4ae667ce",
    ),
    "phase104_manifest": (
        "d76dd7168d8b3a4e4ec9e3637b959b89d2f947ba519ad4521eccd99b27699531",
        "330379eeff1ae5a805b669667cbce8a3ec98a7d63b890ad0395cdbbd35fb1b42",
    ),
}
EXPECTED_PHASE103_LEDGER_SHA = "24de12594fe8b95f6e70be4278b2dfadb7f29f181aef3d7aeea41f9fbe58de52"
EXPECTED_PHASE104_LEDGER_SHA = "b342a58d20aa7ecdc2a2a5ea45037a64739134151db41b562464163b7e93578f"

EXPECTED_CUBE_COUNT = 48
EXPECTED_TARGET_COUNT = 219
EXPECTED_UNIT_AUDIT_COUNT = 43425
EXPECTED_PHASE103_PAIR_COUNT = 404054
EXPECTED_PHASE104_TRIPLE_COUNT = 3061466
EXPECTED_STRATUM_COUNT = 32
EXPECTED_KAPPA_STRATA = 16
EXPECTED_LAMBDA_STRATA = 31
EXPECTED_QUARTET_COUNT = 24362850
EXPECTED_KAPPA_TRIALS = 20638850
EXPECTED_LAMBDA_TRIALS = 19941575
EXPECTED_STRATA_BY_PERIOD = {2: 4, 3: 26, 6: 1, 12: 1}
EXPECTED_QUARTETS_BY_PERIOD = {2: 12734180, 3: 7196769, 6: 4421275, 12: 10626}
EXPECTED_QUARTETS_BY_RULE = {73: 9968820, 109: 14394030}
EXPECTED_KAPPA_BY_PERIOD = {2: 12734180, 3: 3472769, 6: 4421275, 12: 10626}
EXPECTED_LAMBDA_BY_PERIOD = {2: 12734180, 3: 7196769, 12: 10626}
EXPECTED_KAPPA_BY_RULE = {73: 8087220, 109: 12551630}
EXPECTED_LAMBDA_BY_RULE = {73: 9968820, 109: 9972755}
EXPECTED_INTERNAL_EDGE_DISTRIBUTION = {0: 18847049, 1: 4974572, 2: 520726, 3: 19562, 4: 941}
EXPECTED_INTERNAL_EDGES_BY_PERIOD = {
    2: {0: 10270964, 1: 2279012, 2: 179432, 3: 4604, 4: 168},
    3: {0: 5076386, 1: 1846975, 2: 260493, 3: 12253, 4: 662},
    6: {0: 3492398, 1: 845623, 2: 80445, 3: 2699, 4: 110},
    12: {0: 7301, 1: 2962, 2: 356, 3: 6, 4: 1},
}

HISTORICAL_CATEGORY = "HISTORICAL_SOURCE_POSITIVE"
AT_LEAST_FOUR = "AT_LEAST_4"
KAPPA = "kappa_v"
LAMBDA = "lambda_e"

LEDGER_RECORD = struct.Struct("<H")
LEDGER_FORMAT = "<H"
FLAG_BITS = {
    "kappa_scope": 3,
    "lambda_scope": 4,
    "kappa_route_a_rescue": 5,
    "lambda_route_a_rescue": 6,
    "kappa_route_b_rescue": 7,
    "lambda_route_b_rescue": 8,
    "internal_edge_required_kappa": 9,
    "internal_edge_required_lambda": 10,
}
RESERVED_BITS = tuple(range(11, 16))
BENCHMARK_SAMPLE_PER_STRATUM = 50000
FULL_RUN_AUTHORIZATION_TEXT = "Autorizo el barrido completo de Fase 105"
FULL_CHECKPOINT_DIR = RUNTIME_DIR / "full_checkpoints"


def load_phase104_module():
    path = OUTPUT_DIR / "analyze_phase103_triple_synergy.py"
    name = "_zuse_phase104_dependency"
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Cannot load Fase-104 dependency")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase104 = load_phase104_module()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(value)).hexdigest()


def raw_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized_source_sha256(path: Path) -> str:
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def read_and_gate(path: Path, expected: tuple[str, str]) -> dict[str, Any]:
    raw = raw_sha256(path)
    if raw != expected[0]:
        raise RuntimeError(f"Raw SHA mismatch for {path.name}: {raw}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    canonical = canonical_sha256(payload)
    if canonical != expected[1]:
        raise RuntimeError(f"Canonical SHA mismatch for {path.name}: {canonical}")
    return payload


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    with temporary.open("wb") as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def ordered_words_sha256(words: tuple[int, ...]) -> str:
    return hashlib.sha256(json.dumps(list(words), separators=(",", ":")).encode("ascii")).hexdigest()


def historical_words_for(cube: dict[str, Any], period: int) -> tuple[int, ...]:
    words = tuple(
        index
        for index, node in enumerate(cube["nodes"])
        if node["category"] == HISTORICAL_CATEGORY
        and node.get("ledger") is not None
        and int(node["ledger"]["source_period"]) == period
    )
    if words != tuple(sorted(set(words))):
        raise RuntimeError("Historical words are not sorted and unique")
    return words


def build_flags(values: dict[str, bool], internal_edge_count: int) -> int:
    if not 0 <= internal_edge_count <= 4:
        raise ValueError("Internal-edge count does not fit the declared range")
    mask = internal_edge_count
    for name, bit in FLAG_BITS.items():
        if values.get(name, False):
            mask |= 1 << bit
    if mask & sum(1 << bit for bit in RESERVED_BITS):
        raise RuntimeError("Reserved ledger bit became active")
    return mask


def minimal_label(scope: bool, rescue_count: int) -> str:
    if not scope:
        return "NOT_APPLICABLE_NOT_AT_LEAST_FOUR"
    return "EXACTLY_4" if rescue_count else "AT_LEAST_5"


def validate_phase104_replay(results: dict[str, Any], manifest: dict[str, Any]) -> None:
    if raw_sha256(PHASE104_LEDGER_PATH) != EXPECTED_PHASE104_LEDGER_SHA:
        raise RuntimeError("Fase-104 ledger digest mismatch")
    if manifest["ledger_sha256"] != EXPECTED_PHASE104_LEDGER_SHA:
        raise RuntimeError("Fase-104 manifest ledger digest mismatch")
    old = struct.Struct(manifest["record_format"])
    bits = {name: int(bit) for name, bit in manifest["flag_bits"].items()}
    unresolved = {
        int(row["stratum_index"]): row
        for row in results["strata"]
        if row["kappa_minimal_cardinality"] == AT_LEAST_FOUR
        or row["lambda_minimal_cardinality"] == AT_LEAST_FOUR
    }
    counts = Counter()
    with PHASE104_LEDGER_PATH.open("rb") as handle:
        while raw := handle.read(old.size):
            if len(raw) != old.size:
                raise RuntimeError("Truncated Fase-104 ledger")
            stratum_index, _a, _b, _c, flags, *_rest = old.unpack(raw)
            decoded = {name: bool(flags & (1 << bit)) for name, bit in bits.items()}
            counts["records"] += 1
            if decoded["kappa_route_a_rescue"] != decoded["kappa_route_b_rescue"]:
                counts["route_disagreements"] += 1
            if decoded["lambda_route_a_rescue"] != decoded["lambda_route_b_rescue"]:
                counts["route_disagreements"] += 1
            if not decoded["kappa_scope"] and any(
                decoded[name]
                for name in (
                    "kappa_route_a_rescue",
                    "kappa_route_b_rescue",
                    "internal_edge_required_kappa",
                    "three_node_vertex_coverage",
                )
            ):
                counts["out_of_scope"] += 1
            if not decoded["lambda_scope"] and any(
                decoded[name]
                for name in (
                    "lambda_route_a_rescue",
                    "lambda_route_b_rescue",
                    "internal_edge_required_lambda",
                    "three_node_edge_coverage",
                )
            ):
                counts["out_of_scope"] += 1
            if decoded["kappa_route_b_rescue"]:
                counts["kappa_rescues"] += 1
            if decoded["lambda_route_b_rescue"]:
                counts["lambda_rescues"] += 1
            source = unresolved.get(int(stratum_index))
            if source is not None:
                if source["kappa_minimal_cardinality"] == AT_LEAST_FOUR and decoded["kappa_route_b_rescue"]:
                    raise RuntimeError("Fase-104 unresolved kappa stratum contains a rescue")
                if source["lambda_minimal_cardinality"] == AT_LEAST_FOUR and decoded["lambda_route_b_rescue"]:
                    raise RuntimeError("Fase-104 unresolved lambda stratum contains a rescue")
    expected = {"records": EXPECTED_PHASE104_TRIPLE_COUNT, "kappa_rescues": 180, "lambda_rescues": 192}
    for name, value in expected.items():
        if counts[name] != value:
            raise RuntimeError(f"Fase-104 replay mismatch for {name}")
    if counts["route_disagreements"] or counts["out_of_scope"]:
        raise RuntimeError("Fase-104 clean-ledger replay failed")


def load_inputs() -> tuple[dict[str, Any], ...]:
    phase95 = read_and_gate(PHASE95_PATH, EXPECTED_HASHES["phase95"])
    phase97 = read_and_gate(PHASE97_PATH, EXPECTED_HASHES["phase97"])
    phase102 = read_and_gate(PHASE102_PATH, EXPECTED_HASHES["phase102"])
    phase103 = read_and_gate(PHASE103_RESULTS_PATH, EXPECTED_HASHES["phase103_results"])
    phase103_manifest = read_and_gate(PHASE103_MANIFEST_PATH, EXPECTED_HASHES["phase103_manifest"])
    phase104_results = read_and_gate(PHASE104_RESULTS_PATH, EXPECTED_HASHES["phase104_results"])
    phase104_manifest = read_and_gate(PHASE104_MANIFEST_PATH, EXPECTED_HASHES["phase104_manifest"])
    if raw_sha256(PHASE103_LEDGER_PATH) != EXPECTED_PHASE103_LEDGER_SHA:
        raise RuntimeError("Fase-103 clean-ledger digest mismatch")
    if phase103_manifest["ledger_sha256"] != EXPECTED_PHASE103_LEDGER_SHA:
        raise RuntimeError("Fase-103 manifest digest mismatch")
    phase104.validate_phase103_replay(phase103, phase103_manifest)
    if len(phase102["audit_records"]) != EXPECTED_UNIT_AUDIT_COUNT or any(
        not row["law_match"]
        or bool(row["vertex_direct"]) != bool(row["vertex_phase100"])
        or bool(row["edge_direct"]) != bool(row["edge_phase100"])
        for row in phase102["audit_records"]
    ):
        raise RuntimeError("Fase-102 unit replay mismatch")
    validate_phase104_replay(phase104_results, phase104_manifest)
    return phase95, phase97, phase102, phase103, phase104_results


def build_tasks(inputs: tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    phase95, phase97, phase102, phase103, phase104_results = inputs
    cubes = {cube["cube_key"]: cube for cube in phase95["cube_nodes"]}
    pairs = {(row["cube_key"], int(row["pair_index"])): row for row in phase97["component_pairs"]}
    audits = {(row["cube_key"], int(row["pair_index"])): row for row in phase102["target_cut_audits"]}
    phase103_strata = {int(row["stratum_index"]): row for row in phase103["strata"]}
    unresolved = [
        row
        for row in phase104_results["strata"]
        if row["kappa_minimal_cardinality"] == AT_LEAST_FOUR
        or row["lambda_minimal_cardinality"] == AT_LEAST_FOUR
    ]
    unresolved.sort(key=lambda row: (row["cube_key"], int(row["pair_index"]), int(row["period"])))
    contexts: dict[tuple[str, int], dict[str, Any]] = {}
    tasks = []
    for index, source in enumerate(unresolved):
        key = (source["cube_key"], int(source["pair_index"]))
        if key not in contexts:
            pair = pairs[key]
            contexts[key] = phase104.phase103.build_context(cubes[key[0]], pair, pair["physical_class_sha256"], audits[key])
        context = contexts[key]
        period = int(source["period"])
        words = historical_words_for(cubes[key[0]], period)
        if len(words) != int(source["node_count"]):
            raise RuntimeError("Historical word denominator mismatch")
        prior = phase103_strata[int(source["phase103_stratum_index"])]
        kappa_scope = source["kappa_minimal_cardinality"] == AT_LEAST_FOUR
        lambda_scope = source["lambda_minimal_cardinality"] == AT_LEAST_FOUR
        tasks.append(
            {
                "stratum_index": index,
                "phase104_stratum_index": int(source["stratum_index"]),
                "cube_key": source["cube_key"],
                "pair_index": int(source["pair_index"]),
                "rule": int(source["rule"]),
                "background_index": int(source["background_index"]),
                "period": period,
                "historical_words": words,
                "ordered_words_sha256": ordered_words_sha256(words),
                "kappa_scope": kappa_scope,
                "lambda_scope": lambda_scope,
                "group_kappa_rescues": prior["relations"][KAPPA] == "COLLECTIVE_ONLY_PERIOD_RESCUE",
                "group_lambda_rescues": prior["relations"][LAMBDA] == "COLLECTIVE_ONLY_PERIOD_RESCUE",
                "context": {
                    "component_a": context["component_a"],
                    "component_b": context["component_b"],
                    "adjacency": context["adjacency"],
                    "critical_vertices": context["critical_vertices"],
                    "critical_edges": context["critical_edges"],
                },
            }
        )
    validate_preflight(tasks)
    return tasks


def validate_preflight(tasks: list[dict[str, Any]]) -> None:
    if len(tasks) != EXPECTED_STRATUM_COUNT:
        raise RuntimeError("Fase-105 stratum denominator mismatch")
    if sum(task["kappa_scope"] for task in tasks) != EXPECTED_KAPPA_STRATA:
        raise RuntimeError("Fase-105 kappa denominator mismatch")
    if sum(task["lambda_scope"] for task in tasks) != EXPECTED_LAMBDA_STRATA:
        raise RuntimeError("Fase-105 lambda denominator mismatch")
    quartets_period = Counter()
    quartets_rule = Counter()
    kappa_period = Counter()
    lambda_period = Counter()
    kappa_rule = Counter()
    lambda_rule = Counter()
    for task in tasks:
        count = math.comb(len(task["historical_words"]), 4)
        quartets_period[task["period"]] += count
        quartets_rule[task["rule"]] += count
        if task["kappa_scope"]:
            kappa_period[task["period"]] += count
            kappa_rule[task["rule"]] += count
        if task["lambda_scope"]:
            lambda_period[task["period"]] += count
            lambda_rule[task["rule"]] += count
    checks = (
        (dict(sorted(Counter(task["period"] for task in tasks).items())), EXPECTED_STRATA_BY_PERIOD),
        (dict(sorted(quartets_period.items())), EXPECTED_QUARTETS_BY_PERIOD),
        (dict(sorted(quartets_rule.items())), EXPECTED_QUARTETS_BY_RULE),
        (dict(sorted(kappa_period.items())), EXPECTED_KAPPA_BY_PERIOD),
        (dict(sorted(lambda_period.items())), EXPECTED_LAMBDA_BY_PERIOD),
        (dict(sorted(kappa_rule.items())), EXPECTED_KAPPA_BY_RULE),
        (dict(sorted(lambda_rule.items())), EXPECTED_LAMBDA_BY_RULE),
    )
    if any(actual != expected for actual, expected in checks):
        raise RuntimeError("Fase-105 preflight distribution mismatch")


def process_stratum(task: dict[str, Any], limit: int | None = None) -> dict[str, Any]:
    words = tuple(task["historical_words"])
    combinations = itertools.combinations(words, 4)
    if limit is not None:
        combinations = itertools.islice(combinations, limit)
    ledger = bytearray()
    distribution = Counter()
    rescues_kappa = Counter()
    rescues_lambda = Counter()
    required_kappa = required_lambda = 0
    route_disagreements = monotonicity_failures = 0
    examples_kappa: list[list[int]] = []
    examples_lambda: list[list[int]] = []
    context = task["context"]
    for quartet in combinations:
        adjacency, new_edges, internal_edges = phase104.add_nodes(context["adjacency"], quartet)
        internal_count = len(internal_edges)
        if internal_count > 4:
            raise RuntimeError("Q8 quartet has more than four internal edges")
        distribution[internal_count] += 1
        route_a = phase104.direct_cut_audit(
            adjacency,
            context["component_a"],
            context["component_b"],
            context["critical_vertices"],
            context["critical_edges"],
            quartet,
            new_edges,
            kappa_scope=task["kappa_scope"],
            lambda_scope=task["lambda_scope"],
        )
        route_b_kappa = (
            phase104.phase103.vertex_connectivity_two(adjacency, context["component_a"], context["component_b"])
            if task["kappa_scope"]
            else False
        )
        route_b_lambda = (
            phase104.phase103.edge_connectivity_two(adjacency, context["component_a"], context["component_b"])
            if task["lambda_scope"]
            else False
        )
        route_disagreements += int(route_a["kappa_rescue"] != route_b_kappa)
        route_disagreements += int(route_a["lambda_rescue"] != route_b_lambda)
        kappa_required = phase104.internal_edge_required(
            adjacency,
            context["component_a"],
            context["component_b"],
            internal_edges,
            metric=KAPPA,
            rescue=route_b_kappa,
        )
        lambda_required = phase104.internal_edge_required(
            adjacency,
            context["component_a"],
            context["component_b"],
            internal_edges,
            metric=LAMBDA,
            rescue=route_b_lambda,
        )
        if route_b_kappa:
            rescues_kappa[internal_count] += 1
            required_kappa += int(kappa_required)
            if len(examples_kappa) < 20:
                examples_kappa.append(list(quartet))
        if route_b_lambda:
            rescues_lambda[internal_count] += 1
            required_lambda += int(lambda_required)
            if len(examples_lambda) < 20:
                examples_lambda.append(list(quartet))
        if route_b_kappa and not task["group_kappa_rescues"]:
            monotonicity_failures += 1
        if route_b_lambda and not task["group_lambda_rescues"]:
            monotonicity_failures += 1
        flags = build_flags(
            {
                "kappa_scope": task["kappa_scope"],
                "lambda_scope": task["lambda_scope"],
                "kappa_route_a_rescue": route_a["kappa_rescue"],
                "lambda_route_a_rescue": route_a["lambda_rescue"],
                "kappa_route_b_rescue": route_b_kappa,
                "lambda_route_b_rescue": route_b_lambda,
                "internal_edge_required_kappa": kappa_required,
                "internal_edge_required_lambda": lambda_required,
            },
            internal_count,
        )
        ledger.extend(LEDGER_RECORD.pack(flags))
    processed = len(ledger) // LEDGER_RECORD.size
    expected = min(math.comb(len(words), 4), limit) if limit is not None else math.comb(len(words), 4)
    if processed != expected or route_disagreements or monotonicity_failures:
        raise RuntimeError("Quartet worker reconciliation failed")
    return {
        "stratum_index": int(task["stratum_index"]),
        "processed": processed,
        "ledger": bytes(ledger),
        "distribution": dict(distribution),
        "kappa_rescues": dict(rescues_kappa),
        "lambda_rescues": dict(rescues_lambda),
        "required_kappa": required_kappa,
        "required_lambda": required_lambda,
        "kappa_examples": examples_kappa,
        "lambda_examples": examples_lambda,
    }


def benchmark_tasks(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selectors = [
        max(tasks, key=lambda task: len(task["historical_words"])),
        max((task for task in tasks if task["period"] == 2 and task["rule"] == 73), key=lambda task: len(task["historical_words"])),
        max((task for task in tasks if task["period"] == 2 and task["rule"] == 109), key=lambda task: len(task["historical_words"])),
        max((task for task in tasks if task["period"] == 3), key=lambda task: len(task["historical_words"])),
        next(task for task in tasks if task["period"] == 12),
    ]
    if len({task["stratum_index"] for task in selectors}) != len(selectors):
        raise RuntimeError("Benchmark selectors are not unique")
    return selectors


def task_identity(task: dict[str, Any]) -> str:
    payload = {
        "stratum_index": int(task["stratum_index"]),
        "phase104_stratum_index": int(task["phase104_stratum_index"]),
        "cube_key": task["cube_key"],
        "pair_index": int(task["pair_index"]),
        "period": int(task["period"]),
        "ordered_words_sha256": task["ordered_words_sha256"],
        "kappa_scope": bool(task["kappa_scope"]),
        "lambda_scope": bool(task["lambda_scope"]),
    }
    return canonical_sha256(payload)


def checkpoint_paths(task: dict[str, Any]) -> tuple[Path, Path]:
    stem = f"stratum_{int(task['stratum_index']):03d}"
    return FULL_CHECKPOINT_DIR / f"{stem}.bin", FULL_CHECKPOINT_DIR / f"{stem}.json"


def save_checkpoint(task: dict[str, Any], row: dict[str, Any]) -> None:
    binary_path, metadata_path = checkpoint_paths(task)
    ledger = row["ledger"]
    metadata = {key: value for key, value in row.items() if key != "ledger"}
    metadata.update(
        {
            "ledger_sha256": hashlib.sha256(ledger).hexdigest(),
            "ledger_size": len(ledger),
            "task_identity": task_identity(task),
            "runner_sha256": normalized_source_sha256(Path(__file__)),
            "phase104_ledger_sha256": EXPECTED_PHASE104_LEDGER_SHA,
        }
    )
    atomic_write(binary_path, ledger)
    atomic_write(
        metadata_path,
        json.dumps(metadata, indent=2, sort_keys=True).encode("utf-8") + b"\n",
    )


def load_checkpoint(task: dict[str, Any]) -> dict[str, Any] | None:
    binary_path, metadata_path = checkpoint_paths(task)
    if not binary_path.exists() and not metadata_path.exists():
        return None
    if not binary_path.exists() or not metadata_path.exists():
        raise RuntimeError("Incomplete Fase-105 checkpoint pair")
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    ledger = binary_path.read_bytes()
    checks = (
        metadata["task_identity"] == task_identity(task),
        metadata["runner_sha256"] == normalized_source_sha256(Path(__file__)),
        metadata["phase104_ledger_sha256"] == EXPECTED_PHASE104_LEDGER_SHA,
        int(metadata["ledger_size"]) == len(ledger),
        metadata["ledger_sha256"] == hashlib.sha256(ledger).hexdigest(),
        int(metadata["processed"]) == math.comb(len(task["historical_words"]), 4),
    )
    if not all(checks):
        raise RuntimeError("Fase-105 checkpoint validation failed")
    metadata.pop("ledger_sha256")
    metadata.pop("ledger_size")
    metadata.pop("task_identity")
    metadata.pop("runner_sha256")
    metadata.pop("phase104_ledger_sha256")
    metadata["ledger"] = ledger
    return metadata


def run_benchmark(tasks: list[dict[str, Any]], workers: int) -> dict[str, Any]:
    selected = benchmark_tasks(tasks)
    started = time.perf_counter()
    completed: dict[int, dict[str, Any]] = {}
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_stratum, task, BENCHMARK_SAMPLE_PER_STRATUM): task
            for task in selected
        }
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            completed[int(row["stratum_index"])] = row
    wall_seconds = time.perf_counter() - started
    ledger = b"".join(completed[int(task["stratum_index"])]["ledger"] for task in selected)
    atomic_write(BENCHMARK_TEMP_PATH, ledger)
    temp_sha = raw_sha256(BENCHMARK_TEMP_PATH)
    processed = sum(row["processed"] for row in completed.values())
    rate = processed / wall_seconds
    projected = EXPECTED_QUARTET_COUNT / rate
    required_free = max(500 * 1024 * 1024, EXPECTED_QUARTET_COUNT * LEDGER_RECORD.size * 4)
    free = shutil.disk_usage(RUNTIME_DIR).free
    report = {
        "phase": 105,
        "status": "PASS" if free >= required_free else "FAIL_INSUFFICIENT_DISK",
        "workers": workers,
        "processed_records": processed,
        "wall_seconds": wall_seconds,
        "wall_rate_records_per_second": rate,
        "projected_full_wall_seconds": projected,
        "projected_full_wall_seconds_with_25pct_margin": projected * 1.25,
        "full_record_count": EXPECTED_QUARTET_COUNT,
        "full_ledger_bytes": EXPECTED_QUARTET_COUNT * LEDGER_RECORD.size,
        "observed_free_bytes": free,
        "required_free_bytes": required_free,
        "temporary_ledger_sha256": temp_sha,
        "runner_sha256": normalized_source_sha256(Path(__file__)),
        "source_hashes": {key: {"raw": value[0], "canonical": value[1]} for key, value in EXPECTED_HASHES.items()},
        "phase103_ledger_sha256": EXPECTED_PHASE103_LEDGER_SHA,
        "phase104_ledger_sha256": EXPECTED_PHASE104_LEDGER_SHA,
        "selected_strata": [
            {
                "stratum_index": int(task["stratum_index"]),
                "period": int(task["period"]),
                "rule": int(task["rule"]),
                "node_count": len(task["historical_words"]),
                "ordered_words": list(task["historical_words"]),
                "ordered_words_sha256": task["ordered_words_sha256"],
                "processed": completed[int(task["stratum_index"])]["processed"],
            }
            for task in selected
        ],
        "full_run_executed": False,
        "simulation_executed": False,
    }
    atomic_write(BENCHMARK_REPORT_PATH, json.dumps(report, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    BENCHMARK_TEMP_PATH.unlink(missing_ok=True)
    return report


def validate_full_authorization(path: Path, benchmark_path: Path, workers: int) -> dict[str, Any]:
    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    authorization = json.loads(path.read_text(encoding="utf-8"))
    if benchmark["status"] != "PASS" or int(benchmark["workers"]) != workers:
        raise RuntimeError("Benchmark does not authorize this worker count")
    if benchmark["runner_sha256"] != normalized_source_sha256(Path(__file__)):
        raise RuntimeError("Runner changed after benchmark")
    if authorization.get("authorization") != FULL_RUN_AUTHORIZATION_TEXT:
        raise RuntimeError("Full-run authorization text mismatch")
    if authorization.get("benchmark_report_sha256") != raw_sha256(benchmark_path):
        raise RuntimeError("Authorization is not tied to this benchmark report")
    if int(authorization.get("workers", 0)) != workers:
        raise RuntimeError("Authorization worker count mismatch")
    if int(authorization.get("expected_record_count", 0)) != EXPECTED_QUARTET_COUNT:
        raise RuntimeError("Authorization denominator mismatch")
    path.unlink()
    return benchmark


def build_segments(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    offset = 0
    segments = []
    for task in tasks:
        count = math.comb(len(task["historical_words"]), 4)
        segments.append(
            {
                "stratum_index": int(task["stratum_index"]),
                "record_offset": offset,
                "record_count": count,
                "ordered_words": list(task["historical_words"]),
                "ordered_words_sha256": task["ordered_words_sha256"],
                "combination_order": "PYTHON_ITERTOOLS_COMBINATIONS_R4_LEXICOGRAPHIC",
            }
        )
        offset += count
    if offset != EXPECTED_QUARTET_COUNT:
        raise RuntimeError("Manifest segment denominator mismatch")
    return segments


def run_full(tasks: list[dict[str, Any]], workers: int) -> dict[str, Any]:
    completed: dict[int, dict[str, Any]] = {}
    checkpoint_reused = 0
    pending = []
    for task in tasks:
        checkpoint = load_checkpoint(task)
        if checkpoint is None:
            pending.append(task)
        else:
            completed[int(task["stratum_index"])] = checkpoint
            checkpoint_reused += 1
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(process_stratum, task): task for task in pending}
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            save_checkpoint(futures[future], row)
            completed[int(row["stratum_index"])] = row
            print(f"completed {len(completed)}/{len(tasks)} strata", flush=True)
    if len(completed) != len(tasks):
        raise RuntimeError("Fase-105 checkpoint/worker denominator mismatch")
    ledger = b"".join(completed[index]["ledger"] for index in range(len(tasks)))
    if len(ledger) != EXPECTED_QUARTET_COUNT * LEDGER_RECORD.size:
        raise RuntimeError("Final ledger size mismatch")
    distribution = Counter()
    internal_edges_by_period: dict[int, Counter] = {}
    quartets_by_period = Counter()
    quartets_by_rule = Counter()
    kappa_trials_by_period = Counter()
    lambda_trials_by_period = Counter()
    kappa_trials_by_rule = Counter()
    lambda_trials_by_rule = Counter()
    kappa_rescues_by_period = Counter()
    lambda_rescues_by_period = Counter()
    kappa_rescues_by_rule = Counter()
    lambda_rescues_by_rule = Counter()
    kappa_rescues_by_internal_edge_count = Counter()
    lambda_rescues_by_internal_edge_count = Counter()
    strata = []
    for task in tasks:
        row = completed[int(task["stratum_index"])]
        local_distribution = Counter({int(k): int(v) for k, v in row["distribution"].items()})
        distribution.update(local_distribution)
        internal_edges_by_period.setdefault(int(task["period"]), Counter()).update(local_distribution)
        kappa_count = sum(row["kappa_rescues"].values())
        lambda_count = sum(row["lambda_rescues"].values())
        quartets_by_period[int(task["period"])] += int(row["processed"])
        quartets_by_rule[int(task["rule"])] += int(row["processed"])
        if task["kappa_scope"]:
            kappa_trials_by_period[int(task["period"])] += int(row["processed"])
            kappa_trials_by_rule[int(task["rule"])] += int(row["processed"])
            kappa_rescues_by_period[int(task["period"])] += kappa_count
            kappa_rescues_by_rule[int(task["rule"])] += kappa_count
            kappa_rescues_by_internal_edge_count.update(row["kappa_rescues"])
        if task["lambda_scope"]:
            lambda_trials_by_period[int(task["period"])] += int(row["processed"])
            lambda_trials_by_rule[int(task["rule"])] += int(row["processed"])
            lambda_rescues_by_period[int(task["period"])] += lambda_count
            lambda_rescues_by_rule[int(task["rule"])] += lambda_count
            lambda_rescues_by_internal_edge_count.update(row["lambda_rescues"])
        strata.append(
            {
                "stratum_index": int(task["stratum_index"]),
                "phase104_stratum_index": int(task["phase104_stratum_index"]),
                "cube_key": task["cube_key"],
                "pair_index": int(task["pair_index"]),
                "rule": int(task["rule"]),
                "background_index": int(task["background_index"]),
                "period": int(task["period"]),
                "node_count": len(task["historical_words"]),
                "quartet_count": int(row["processed"]),
                "kappa_scope": bool(task["kappa_scope"]),
                "lambda_scope": bool(task["lambda_scope"]),
                "kappa_quartet_rescue_count": kappa_count,
                "lambda_quartet_rescue_count": lambda_count,
                "kappa_minimal_cardinality": minimal_label(task["kappa_scope"], kappa_count),
                "lambda_minimal_cardinality": minimal_label(task["lambda_scope"], lambda_count),
                "internal_edge_distribution": {i: int(local_distribution[i]) for i in range(5)},
                "kappa_rescues_by_internal_edge_count": {i: int(row["kappa_rescues"].get(i, 0)) for i in range(5)},
                "lambda_rescues_by_internal_edge_count": {i: int(row["lambda_rescues"].get(i, 0)) for i in range(5)},
                "internal_edge_required_kappa_count": int(row["required_kappa"]),
                "internal_edge_required_lambda_count": int(row["required_lambda"]),
                "kappa_rescuing_quartet_examples": row["kappa_examples"],
                "lambda_rescuing_quartet_examples": row["lambda_examples"],
            }
        )
    complete_distribution = {i: int(distribution[i]) for i in range(5)}
    if complete_distribution != EXPECTED_INTERNAL_EDGE_DISTRIBUTION:
        raise RuntimeError("Final geometry distribution mismatch")
    checks = (
        (dict(sorted(quartets_by_period.items())), EXPECTED_QUARTETS_BY_PERIOD),
        (dict(sorted(quartets_by_rule.items())), EXPECTED_QUARTETS_BY_RULE),
        (dict(sorted(kappa_trials_by_period.items())), EXPECTED_KAPPA_BY_PERIOD),
        (dict(sorted(lambda_trials_by_period.items())), EXPECTED_LAMBDA_BY_PERIOD),
        (dict(sorted(kappa_trials_by_rule.items())), EXPECTED_KAPPA_BY_RULE),
        (dict(sorted(lambda_trials_by_rule.items())), EXPECTED_LAMBDA_BY_RULE),
    )
    if any(actual != expected for actual, expected in checks):
        raise RuntimeError("Final denominator aggregation mismatch")
    for period, expected in EXPECTED_INTERNAL_EDGES_BY_PERIOD.items():
        actual = {edge_count: int(internal_edges_by_period[period][edge_count]) for edge_count in range(5)}
        if actual != expected:
            raise RuntimeError(f"Final geometry mismatch for T={period}")
    ledger_sha = hashlib.sha256(ledger).hexdigest()
    summary = {
        "quartet_stratum_count": len(strata),
        "kappa_stratum_count": EXPECTED_KAPPA_STRATA,
        "lambda_stratum_count": EXPECTED_LAMBDA_STRATA,
        "quartet_intervention_count": EXPECTED_QUARTET_COUNT,
        "kappa_trial_count": EXPECTED_KAPPA_TRIALS,
        "lambda_trial_count": EXPECTED_LAMBDA_TRIALS,
        "kappa_exactly_four_strata": sum(row["kappa_minimal_cardinality"] == "EXACTLY_4" for row in strata),
        "kappa_at_least_five_strata": sum(row["kappa_minimal_cardinality"] == "AT_LEAST_5" for row in strata),
        "lambda_exactly_four_strata": sum(row["lambda_minimal_cardinality"] == "EXACTLY_4" for row in strata),
        "lambda_at_least_five_strata": sum(row["lambda_minimal_cardinality"] == "AT_LEAST_5" for row in strata),
        "kappa_quartet_rescue_count": sum(row["kappa_quartet_rescue_count"] for row in strata),
        "lambda_quartet_rescue_count": sum(row["lambda_quartet_rescue_count"] for row in strata),
        "internal_edge_distribution": complete_distribution,
        "kappa_rescues_by_period": dict(sorted(kappa_rescues_by_period.items())),
        "lambda_rescues_by_period": dict(sorted(lambda_rescues_by_period.items())),
        "kappa_rescues_by_rule": dict(sorted(kappa_rescues_by_rule.items())),
        "lambda_rescues_by_rule": dict(sorted(lambda_rescues_by_rule.items())),
        "kappa_rescues_by_internal_edge_count": {i: int(kappa_rescues_by_internal_edge_count[i]) for i in range(5)},
        "lambda_rescues_by_internal_edge_count": {i: int(lambda_rescues_by_internal_edge_count[i]) for i in range(5)},
        "internal_edge_required_kappa_count": sum(row["internal_edge_required_kappa_count"] for row in strata if row["kappa_scope"]),
        "internal_edge_required_lambda_count": sum(row["internal_edge_required_lambda_count"] for row in strata if row["lambda_scope"]),
        "route_disagreement_count": 0,
        "monotonicity_failure_count": 0,
        "ledger_record_count": EXPECTED_QUARTET_COUNT,
        "ledger_record_size": LEDGER_RECORD.size,
        "ledger_size": len(ledger),
        "ledger_sha256": ledger_sha,
        "workers": workers,
        "checkpoint_reused_count": checkpoint_reused,
        "simulation_executed": False,
    }
    result = {
        "phase": 105,
        "status": "QUADRUPLE_SYNERGY_ATLAS_BUILT",
        "sources": {key: {"raw_sha256": value[0], "canonical_sha256": value[1]} for key, value in EXPECTED_HASHES.items()}
        | {"phase103_ledger_sha256": EXPECTED_PHASE103_LEDGER_SHA, "phase104_ledger_sha256": EXPECTED_PHASE104_LEDGER_SHA},
        "protocol": {
            "simulation_executed": False,
            "quartet_order": "IMPLICIT_STRATUM_SEGMENTS_PLUS_LEXICOGRAPHIC_COMBINATIONS",
            "route_a": "DIRECT_EXHAUSTIVE_REMOVAL",
            "route_b": "FRESH_INTEGER_MAX_FLOW_CAP_2",
            "threshold_scan_executed": False,
            "metric_denominators_separate": True,
        },
        "summary": summary,
        "strata": strata,
        "preflight": {
            "strata_by_period": dict(sorted(Counter(row["period"] for row in strata).items())),
            "quartets_by_period": dict(sorted(quartets_by_period.items())),
            "quartets_by_rule": dict(sorted(quartets_by_rule.items())),
            "kappa_trials_by_period": dict(sorted(kappa_trials_by_period.items())),
            "lambda_trials_by_period": dict(sorted(lambda_trials_by_period.items())),
            "kappa_trials_by_rule": dict(sorted(kappa_trials_by_rule.items())),
            "lambda_trials_by_rule": dict(sorted(lambda_trials_by_rule.items())),
            "internal_edges_by_period": {
                period: {edge_count: int(counter[edge_count]) for edge_count in range(5)}
                for period, counter in sorted(internal_edges_by_period.items())
            },
        },
        "methodological_limits": [
            "EXACTLY_4 is proven only where all interventions of cardinality one through three fail.",
            "AT_LEAST_5 is a lower bound; quintets and larger subsets are not enumerated.",
            "Period labels index frozen historical-node strata and are not interpreted causally.",
            "The atlas is restricted to 32 unresolved strata in the frozen Q8 catalogue.",
        ],
    }
    manifest = {
        "phase": 105,
        "ledger_file": LEDGER_PATH.name,
        "byte_order": "little-endian",
        "record_format": LEDGER_FORMAT,
        "record_size": LEDGER_RECORD.size,
        "record_count": EXPECTED_QUARTET_COUNT,
        "ledger_size": len(ledger),
        "ledger_sha256": ledger_sha,
        "flag_bits": FLAG_BITS,
        "reserved_bits": list(RESERVED_BITS),
        "internal_edge_count_bits": "0..2",
        "segments": build_segments(tasks),
        "decoder": "decode_phase104_quadruple_synergy_ledger.py",
    }
    atomic_write(LEDGER_PATH, ledger)
    atomic_write(MANIFEST_PATH, json.dumps(manifest, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    atomic_write(RESULTS_PATH, json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    report = (
        "# Rule 73/109 quadruple historical synergy atlas - Fase 105\n\n"
        f"- Strata: `{len(strata)}`\n"
        f"- Quartets: `{EXPECTED_QUARTET_COUNT}`\n"
        f"- Kappa exactly 4 / at least 5: `{summary['kappa_exactly_four_strata']}` / `{summary['kappa_at_least_five_strata']}`\n"
        f"- Lambda exactly 4 / at least 5: `{summary['lambda_exactly_four_strata']}` / `{summary['lambda_at_least_five_strata']}`\n"
        f"- Ledger SHA-256: `{ledger_sha}`\n\n"
        "## Verdict\n\n`QUADRUPLE_SYNERGY_ATLAS_BUILT`\n"
    )
    atomic_write(REPORT_PATH, report.encode("utf-8"))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fase-105 quartet-synergy runner")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--benchmark", action="store_true")
    mode.add_argument("--full", action="store_true")
    parser.add_argument("--workers", type=int, default=5)
    parser.add_argument("--authorization", type=Path)
    parser.add_argument("--benchmark-report", type=Path, default=BENCHMARK_REPORT_PATH)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.workers < 1:
        raise ValueError("workers must be positive")
    inputs = load_inputs()
    tasks = build_tasks(inputs)
    if args.preflight:
        print(json.dumps({"strata": len(tasks), "quartets": EXPECTED_QUARTET_COUNT, "simulation_executed": False, "full_run_executed": False}, indent=2))
        return 0
    if args.benchmark:
        report = run_benchmark(tasks, args.workers)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if args.authorization is None:
        raise RuntimeError("Full run requires a one-shot authorization file")
    validate_full_authorization(args.authorization, args.benchmark_report, args.workers)
    result = run_full(tasks, args.workers)
    print(json.dumps(result["summary"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
