#!/usr/bin/env python3
"""Build-time runner for Fase 90. Simulation commands require external authorization."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Iterable


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parent.parent
PROTOCOL_PATH = OUT_DIR / "phase90_global_period_cap_resweep_protocol.json"
CORE_PATH = OUT_DIR / "phase90_resweep_core.py"
BASE_SCRIPT = OUT_DIR / "sweep_periodic_background_oscillators.py"
LEN8_SCRIPT = ROOT / "outputs" / "periodic_backgrounds_len8" / "sweep_len8_periodic_oscillators.py"
DEFAULT_RUNTIME = OUT_DIR / "fase90"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_module("phase90_resweep_core", CORE_PATH)


def exact_dynamics(shapes: list[Any], max_period: int) -> dict[str, Any]:
    if not shapes:
        return {"kind": "NOT_AVAILABLE", "period": 0, "drift": 0}
    for period in range(1, min(max_period, len(shapes) - 1) + 1):
        if all(
            shapes[index].offsets == shapes[index + period].offsets
            and int(shapes[index].min_pos) == int(shapes[index + period].min_pos)
            for index in range(len(shapes) - period)
        ):
            return {"kind": "STATIONARY", "period": period, "drift": 0}
    for period in range(1, min(max_period, len(shapes) - 1) + 1):
        drift = None
        valid = True
        for index in range(len(shapes) - period):
            left = shapes[index]
            right = shapes[index + period]
            if left.offsets != right.offsets:
                valid = False
                break
            observed = int(right.min_pos) - int(left.min_pos)
            if observed == 0:
                valid = False
                break
            if drift is None:
                drift = observed
            elif observed != drift:
                valid = False
                break
        if valid and drift is not None:
            return {"kind": "MOVING", "period": period, "drift": drift}
    return {"kind": "BOUNDED_UNCLASSIFIED", "period": 0, "drift": 0}


def kind_code(kind: str) -> int:
    mapping = {
        "NOT_AVAILABLE": core.Kind.NOT_AVAILABLE,
        "STATIONARY": core.Kind.STATIONARY,
        "MOVING": core.Kind.MOVING,
        "PERIOD1_ALIAS": core.Kind.PERIOD1_ALIAS,
        "BOUNDED_UNCLASSIFIED": core.Kind.BOUNDED_UNCLASSIFIED,
        "ZERO_INITIAL_DEFECT": core.Kind.ZERO_INITIAL_DEFECT,
        "EXTINCT": core.Kind.EXTINCT,
        "SPAN_ESCAPE": core.Kind.SPAN_ESCAPE,
    }
    return int(mapping[kind])


def simulate_source(
    base,
    bg_frames: list[tuple[int, ...]],
    *,
    rule: int,
    word_len: int,
    word_value: int,
    burn_in: int,
    steps: int,
    max_span: int,
) -> dict[str, Any]:
    diff = base.initial_diff(word_value, word_len, bg_frames[0])
    if not diff:
        return {"kind": "ZERO_INITIAL_DEFECT", "shapes": []}
    shapes = []
    for timestamp in range(steps + 1):
        if timestamp >= burn_in:
            shape = base.linear_shape(diff)
            if shape is None:
                return {"kind": "EXTINCT", "shapes": shapes}
            if int(shape.span) > max_span:
                return {"kind": "SPAN_ESCAPE", "shapes": shapes}
            shapes.append(shape)
        if timestamp < steps:
            diff = base.eca_step_diff(
                diff,
                bg_frames[timestamp],
                bg_frames[timestamp + 1],
                rule,
            )
            if not diff and timestamp + 1 < burn_in:
                return {"kind": "EXTINCT", "shapes": []}
    return {"kind": "BOUNDED", "shapes": shapes}


def source_detection(base, shapes: list[Any]) -> tuple[dict[str, Any], list[dict[str, Any]], int]:
    stationary = base.detect_stationary(shapes)
    moving, alias = base.detect_moving(shapes)
    rows = []
    if stationary is not None:
        rows.append(stationary)
        source = {
            "kind": "STATIONARY",
            "period": int(stationary["period_T"]),
            "drift": 0,
        }
    elif moving is not None:
        source = {
            "kind": "MOVING",
            "period": int(moving["period_T"]),
            "drift": int(moving["drift_per_period"]),
        }
    elif alias is not None:
        source = {
            "kind": "PERIOD1_ALIAS",
            "period": 1,
            "drift": int(alias["drift_per_period"]),
        }
    else:
        source = {"kind": "BOUNDED_UNCLASSIFIED", "period": 0, "drift": 0}
    if moving is not None:
        rows.append(moving)
    return source, rows, int(alias is not None)


def build_background_frames(base, background: str, rule: int, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(background)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def cohort_backgrounds(cohort: str, base, len8) -> list[str]:
    if cohort == "baseline_period_1_2_4":
        return list(base.background_words())
    if cohort == "primitive_len8":
        return list(len8.primitive_len8_backgrounds())
    raise ValueError(f"Unknown cohort {cohort}")


def replay_record(
    *,
    cohort: str,
    rule: int,
    background: str,
    word_len: int,
    word: str,
    hit: dict[str, Any],
) -> dict[str, Any]:
    row = {
        "rule": rule,
        "word_len": word_len,
        "word": word,
        **hit,
    }
    if cohort == "baseline_period_1_2_4":
        row["background"] = background
    else:
        row["background_canonical"] = background
    return row


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def stage_paths(runtime: Path, stage: str, cohort: str, rule: int) -> dict[str, Path]:
    directory = runtime / f"stage_{stage.lower()}" / cohort
    prefix = directory / f"rule_{rule:03d}"
    if stage == "A":
        suffixes = {
            "ledger": ".ledger.bin",
            "candidates": ".candidates.jsonl",
            "replay": ".replay.jsonl",
            "manifest": ".manifest.json",
        }
    else:
        suffixes = {
            "long_results": ".long_results.jsonl",
            "manifest": ".manifest.json",
        }
    return {kind: Path(str(prefix) + suffix) for kind, suffix in suffixes.items()}


def temporary_paths(final_paths: dict[str, Path]) -> dict[str, Path]:
    pid = os.getpid()
    return {
        kind: path.with_name(path.name + f".tmp.{pid}")
        for kind, path in final_paths.items()
    }


def analyze_stage_a_unit(
    protocol_path: str,
    runtime_path: str,
    cohort: str,
    rule: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    protocol = core.load_protocol(Path(protocol_path))
    digest = core.protocol_digest(protocol)
    base = load_module(f"fase90_base_{os.getpid()}", BASE_SCRIPT)
    len8 = load_module(f"fase90_len8_{os.getpid()}", LEN8_SCRIPT)
    detector = protocol["detector"]
    steps = int(detector["source"]["steps"])
    burn_in = int(detector["burn_in"])
    max_span = int(detector["max_span"])
    expanded_max = int(detector["stage_a_counterfactual"]["period_range"][1])
    backgrounds = cohort_backgrounds(cohort, base, len8)
    words = list(base.ic_words())
    final_paths = stage_paths(Path(runtime_path), "A", cohort, rule)
    temp_paths = temporary_paths(final_paths)
    temp_paths["ledger"].parent.mkdir(parents=True, exist_ok=True)
    candidates = []
    replay_rows = []
    alias_count = 0
    processed = 0
    with temp_paths["ledger"].open("wb") as ledger:
        for background_index, background in enumerate(backgrounds):
            bg_frames = build_background_frames(base, background, rule, steps)
            for ic_index, (word_len, word_value, word) in enumerate(words):
                processed += 1
                simulation = simulate_source(
                    base,
                    bg_frames,
                    rule=rule,
                    word_len=int(word_len),
                    word_value=int(word_value),
                    burn_in=burn_in,
                    steps=steps,
                    max_span=max_span,
                )
                if simulation["kind"] != "BOUNDED":
                    source = {"kind": simulation["kind"], "period": 0, "drift": 0}
                    expanded = source
                    source_rows = []
                else:
                    source, source_rows, alias = source_detection(base, simulation["shapes"])
                    alias_count += alias
                    expanded = exact_dynamics(simulation["shapes"], expanded_max)
                flags = 0
                bounded = simulation["kind"] == "BOUNDED"
                source_positive = source["kind"] in {"STATIONARY", "MOVING"}
                cap_candidate = (
                    bounded
                    and source["kind"] == "BOUNDED_UNCLASSIFIED"
                    and expanded["kind"] in {"STATIONARY", "MOVING"}
                    and int(expanded["period"]) > 16
                )
                static_t1 = (
                    bounded
                    and source["kind"] == "BOUNDED_UNCLASSIFIED"
                    and expanded["kind"] == "STATIONARY"
                    and int(expanded["period"]) == 1
                )
                if bounded:
                    flags |= core.FLAG_BOUNDED_SOURCE
                if source_positive:
                    flags |= core.FLAG_SOURCE_POSITIVE
                if cap_candidate:
                    flags |= core.FLAG_CAP_CANDIDATE
                if static_t1:
                    flags |= core.FLAG_STATIC_T1
                record = core.LedgerRecord(
                    source_kind=kind_code(source["kind"]),
                    expanded_kind=kind_code(expanded["kind"]),
                    source_period=int(source["period"]),
                    expanded_period=int(expanded["period"]),
                    source_drift=int(source["drift"]),
                    expanded_drift=int(expanded["drift"]),
                    flags=flags,
                )
                ledger.write(record.encode())
                for hit in source_rows:
                    replay_rows.append(
                        replay_record(
                            cohort=cohort,
                            rule=rule,
                            background=background,
                            word_len=int(word_len),
                            word=word,
                            hit=hit,
                        )
                    )
                if cap_candidate:
                    candidates.append(
                        {
                            "cohort": cohort,
                            "rule": rule,
                            "background_index": background_index,
                            "background": background,
                            "ic_index": ic_index,
                            "word_len": int(word_len),
                            "word": word,
                            "stage_a_kind": expanded["kind"],
                            "stage_a_period": int(expanded["period"]),
                            "stage_a_drift": int(expanded["drift"]),
                        }
                    )
        ledger.flush()
        os.fsync(ledger.fileno())
    write_jsonl(temp_paths["candidates"], candidates)
    write_jsonl(temp_paths["replay"], replay_rows)
    artifacts = {}
    for kind in ("ledger", "candidates", "replay"):
        info = core.artifact_info(temp_paths[kind])
        artifacts[kind] = {
            "path": str(final_paths[kind]),
            "size": info["size"],
            "sha256": info["sha256"],
        }
    manifest = {
        "phase": 90,
        "stage": "A",
        "protocol_sha256": digest,
        "cohort": cohort,
        "rule": rule,
        "processed_runs": processed,
        "source_positive_count": len(replay_rows),
        "candidate_count": len(candidates),
        "period1_alias_count": alias_count,
        "ledger_schema": "<BBBBhhB",
        "ledger_schema_version": core.LEDGER_SCHEMA_VERSION,
        "artifacts": artifacts,
    }
    temp_paths["manifest"].write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    manifest_info = core.artifact_info(temp_paths["manifest"])
    return {
        "stage": "A",
        "cohort": cohort,
        "rule": rule,
        "processed_runs": processed,
        "source_positive_count": len(replay_rows),
        "candidate_count": len(candidates),
        "elapsed_seconds": time.perf_counter() - started,
        "manifest": manifest,
        "manifest_temp_path": str(temp_paths["manifest"]),
        "manifest_final_path": str(final_paths["manifest"]),
        "manifest_sha256": manifest_info["sha256"],
        "temp_paths": {kind: str(temp_paths[kind]) for kind in artifacts},
        "final_paths": {kind: str(final_paths[kind]) for kind in artifacts},
    }


def simulate_long_candidate(base, candidate: dict[str, Any], protocol: dict[str, Any], bg_frames) -> dict[str, Any]:
    detector = protocol["detector"]
    burn_in = int(detector["burn_in"])
    max_span = int(detector["max_span"])
    steps = int(detector["stage_b_confirmation"]["steps"])
    tail_start, tail_end = detector["stage_b_confirmation"]["tail_range"]
    max_period = int(detector["stage_b_confirmation"]["period_range"][1])
    simulation = simulate_source(
        base,
        bg_frames,
        rule=int(candidate["rule"]),
        word_len=int(candidate["word_len"]),
        word_value=int(candidate["word"], 2),
        burn_in=burn_in,
        steps=steps,
        max_span=max_span,
    )
    if simulation["kind"] != "BOUNDED":
        diagnostic = {"kind": simulation["kind"], "period": 0, "drift": 0}
    else:
        start_index = int(tail_start) - burn_in
        end_index = int(tail_end) - burn_in + 1
        diagnostic = exact_dynamics(simulation["shapes"][start_index:end_index], max_period)
    same = (
        diagnostic["kind"] == candidate["stage_a_kind"]
        and int(diagnostic["period"]) == int(candidate["stage_a_period"])
        and int(diagnostic["drift"]) == int(candidate["stage_a_drift"])
    )
    if same:
        status = "CONFIRMED_PERIOD_CAP_FALSE_NEGATIVE"
    elif diagnostic["kind"] in {"STATIONARY", "MOVING"}:
        status = "CANDIDATE_LONG_CLASS_MISMATCH"
    else:
        status = "CANDIDATE_NOT_PERSISTENT"
    return {
        **candidate,
        "stage_b_kind": diagnostic["kind"],
        "stage_b_period": int(diagnostic["period"]),
        "stage_b_drift": int(diagnostic["drift"]),
        "confirmation_status": status,
    }


def analyze_stage_b_unit(
    protocol_path: str,
    runtime_path: str,
    cohort: str,
    rule: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    protocol = core.load_protocol(Path(protocol_path))
    digest = core.protocol_digest(protocol)
    base = load_module(f"fase90b_base_{os.getpid()}", BASE_SCRIPT)
    final_a = stage_paths(Path(runtime_path), "A", cohort, rule)
    candidates = [
        json.loads(line)
        for line in final_a["candidates"].read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    by_background = defaultdict(list)
    for candidate in candidates:
        by_background[candidate["background"]].append(candidate)
    steps = int(protocol["detector"]["stage_b_confirmation"]["steps"])
    rows = []
    for background in sorted(by_background):
        bg_frames = build_background_frames(base, background, rule, steps)
        for candidate in by_background[background]:
            rows.append(simulate_long_candidate(base, candidate, protocol, bg_frames))
    final_paths = stage_paths(Path(runtime_path), "B", cohort, rule)
    temp_paths = temporary_paths(final_paths)
    temp_paths["long_results"].parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(temp_paths["long_results"], rows)
    result_info = core.artifact_info(temp_paths["long_results"])
    artifacts = {
        "long_results": {
            "path": str(final_paths["long_results"]),
            "size": result_info["size"],
            "sha256": result_info["sha256"],
        }
    }
    manifest = {
        "phase": 90,
        "stage": "B",
        "protocol_sha256": digest,
        "cohort": cohort,
        "rule": rule,
        "processed_runs": len(candidates),
        "candidate_count": len(candidates),
        "confirmation_counts": dict(
            sorted(
                __import__("collections").Counter(
                    row["confirmation_status"] for row in rows
                ).items()
            )
        ),
        "artifacts": artifacts,
    }
    temp_paths["manifest"].write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "stage": "B",
        "cohort": cohort,
        "rule": rule,
        "processed_runs": len(candidates),
        "source_positive_count": 0,
        "candidate_count": len(candidates),
        "elapsed_seconds": time.perf_counter() - started,
        "manifest": manifest,
        "manifest_temp_path": str(temp_paths["manifest"]),
        "manifest_final_path": str(final_paths["manifest"]),
        "manifest_sha256": core.sha256_file(temp_paths["manifest"]),
        "temp_paths": {"long_results": str(temp_paths["long_results"])},
        "final_paths": {"long_results": str(final_paths["long_results"])},
    }


def publish_worker_result(result: dict[str, Any], connection) -> None:
    for kind in sorted(result["temp_paths"]):
        expected = result["manifest"]["artifacts"][kind]["sha256"]
        core.publish_temp_file(
            Path(result["temp_paths"][kind]),
            Path(result["final_paths"][kind]),
            expected,
        )
    manifest_info = core.publish_temp_file(
        Path(result["manifest_temp_path"]),
        Path(result["manifest_final_path"]),
        result["manifest_sha256"],
    )
    core.complete_unit(
        connection,
        stage=result["stage"],
        cohort=result["cohort"],
        rule=int(result["rule"]),
        processed_runs=int(result["processed_runs"]),
        source_positive_count=int(result["source_positive_count"]),
        candidate_count=int(result["candidate_count"]),
        elapsed_seconds=float(result["elapsed_seconds"]),
        manifest=result["manifest"],
        manifest_info=manifest_info,
    )


def generator_preflight(protocol: dict[str, Any]) -> dict[str, Any]:
    base = load_module("fase90_preflight_base", BASE_SCRIPT)
    len8 = load_module("fase90_preflight_len8", LEN8_SCRIPT)
    words = list(base.ic_words())
    observed = {
        "baseline_backgrounds": len(base.background_words()),
        "len8_backgrounds": len(len8.primitive_len8_backgrounds()),
        "ic_count": len(words),
        "work_units": len(core.work_units(protocol)),
        "global_runs": sum(unit[2] for unit in core.work_units(protocol)),
        "simulation_executed": False,
        "protocol_sha256": core.protocol_digest(protocol),
    }
    expected = {
        "baseline_backgrounds": 15,
        "len8_backgrounds": 30,
        "ic_count": 502,
        "work_units": 512,
        "global_runs": 5_783_040,
        "simulation_executed": False,
    }
    observed["matches_protocol"] = all(observed[key] == value for key, value in expected.items())
    return observed


def selected_units(
    protocol: dict[str, Any], cohort: str | None, start_rule: int, end_rule: int
) -> list[tuple[str, int, int]]:
    return [
        unit
        for unit in core.work_units(protocol)
        if (cohort is None or unit[0] == cohort) and start_rule <= unit[1] <= end_rule
    ]


def run_parallel_stage(
    *,
    protocol_path: Path,
    runtime: Path,
    stage: str,
    units: list[tuple[str, int, int]],
    workers: int,
) -> None:
    protocol = core.load_protocol(protocol_path)
    digest = core.protocol_digest(protocol)
    db_path = runtime / "checkpoint.sqlite"
    core.initialize_checkpoint(db_path, protocol_sha256=digest, units=core.work_units(protocol))
    worker = analyze_stage_a_unit if stage == "A" else analyze_stage_b_unit
    with core.checkpoint_connection(db_path) as connection:
        pending = []
        for cohort, rule, _expected in units:
            if core.claim_unit(connection, stage=stage, cohort=cohort, rule=rule):
                pending.append((cohort, rule))
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(
                    worker,
                    str(protocol_path),
                    str(runtime),
                    cohort,
                    rule,
                ): (cohort, rule)
                for cohort, rule in pending
            }
            for future in as_completed(futures):
                cohort, rule = futures[future]
                try:
                    result = future.result()
                    publish_worker_result(result, connection)
                    print(
                        f"stage={stage} cohort={cohort} rule={rule} "
                        f"processed={result['processed_runs']} candidates={result['candidate_count']}",
                        flush=True,
                    )
                except Exception as exc:
                    core.fail_unit(
                        connection,
                        stage=stage,
                        cohort=cohort,
                        rule=rule,
                        error=repr(exc),
                    )
                    raise


def parse_unit(value: str) -> tuple[str, int]:
    try:
        cohort, raw_rule = value.rsplit(":", 1)
        rule = int(raw_rule)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("Unit must be COHORT:RULE") from exc
    if cohort not in {"baseline_period_1_2_4", "primitive_len8"}:
        raise argparse.ArgumentTypeError(f"Unknown cohort {cohort}")
    if not 0 <= rule <= 255:
        raise argparse.ArgumentTypeError("Rule must be in 0..255")
    return cohort, rule


def run_benchmark(
    *,
    protocol_path: Path,
    runtime: Path,
    units: list[tuple[str, int]],
    workers: int,
    report_path: Path,
) -> dict[str, Any]:
    protocol = core.load_protocol(protocol_path)
    digest = core.protocol_digest(protocol)
    work_root = runtime / "benchmark_work"
    if work_root.exists():
        shutil.rmtree(work_root)
    started = time.perf_counter()
    results = []
    try:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(
                    analyze_stage_a_unit,
                    str(protocol_path),
                    str(work_root),
                    cohort,
                    rule,
                )
                for cohort, rule in units
            ]
            for future in as_completed(futures):
                results.append(future.result())
        wall = time.perf_counter() - started
        processed = sum(int(result["processed_runs"]) for result in results)
        candidates = sum(int(result["candidate_count"]) for result in results)
        candidate_bytes = sum(
            Path(result["temp_paths"]["candidates"]).stat().st_size
            for result in results
        )
        rate = processed / wall if wall else 0.0
        projected_candidates = round(
            int(protocol["global_run_count"]) * candidates / processed
        ) if processed else 0
        projected_candidate_bytes = round(
            int(protocol["global_run_count"]) * candidate_bytes / processed
        ) if processed else 0
        required_disk = core.dynamic_disk_requirement(
            fixed_ledger_bytes=int(protocol["ledger"]["estimated_raw_bytes"]),
            candidate_bytes=projected_candidate_bytes,
            candidate_count=projected_candidates,
        )
        data = {
            "phase": 90,
            "status": "PASS",
            "protocol_sha256": digest,
            "units": [f"{cohort}:{rule}" for cohort, rule in units],
            "workers": workers,
            "processed_runs": processed,
            "candidate_count": candidates,
            "candidate_bytes": candidate_bytes,
            "wall_seconds": wall,
            "wall_rate_runs_per_second": rate,
            "projected_stage_a_wall_seconds": (
                int(protocol["global_run_count"]) / rate if rate else None
            ),
            "projected_candidate_count": projected_candidates,
            "projected_candidate_bytes": projected_candidate_bytes,
            "dynamic_required_free_bytes": required_disk,
            "observed_free_bytes": core.free_disk_bytes(runtime),
            "simulation_executed": True,
            "scientific_thresholds_changed": False,
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        temp_report = report_path.with_name(report_path.name + ".tmp")
        temp_report.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        core.publish_temp_file(temp_report, report_path, core.sha256_file(temp_report))
        return data
    finally:
        if work_root.exists():
            shutil.rmtree(work_root)


def validate_benchmark_report(
    path: Path,
    *,
    protocol_sha256: str,
    workers: int,
    expected_digest: str,
) -> dict[str, Any]:
    if core.sha256_file(path) != expected_digest:
        raise PermissionError("Benchmark report digest mismatch")
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("status") != "PASS":
        raise PermissionError("Benchmark did not pass")
    if report.get("protocol_sha256") != protocol_sha256:
        raise PermissionError("Benchmark protocol mismatch")
    if int(report.get("workers", 0)) != workers:
        raise PermissionError("Requested worker count was not benchmarked")
    if report.get("simulation_executed") is not True:
        raise PermissionError("Benchmark report does not represent an executed pilot")
    return report


def canonical_row_digest(rows: list[dict[str, Any]]) -> str:
    payloads = sorted(core.canonical_json_bytes(row) for row in rows)
    digest = hashlib.sha256()
    for payload in payloads:
        digest.update(len(payload).to_bytes(8, "little"))
        digest.update(payload)
    return digest.hexdigest()


REPLAY_DERIVED_FIELDS = frozenset({"new_T", "new_rule", "new_speed", "speed"})


def replay_identity_row(row: dict[str, Any]) -> dict[str, Any]:
    """Return the physical detector identity, excluding catalog annotations."""
    return {
        key: value
        for key, value in row.items()
        if key not in REPLAY_DERIVED_FIELDS
    }


def unique_replay_identities(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[bytes, dict[str, Any]] = {}
    for row in rows:
        identity = replay_identity_row(row)
        unique[core.canonical_json_bytes(identity)] = identity
    return list(unique.values())


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def historical_replay_gate(protocol: dict[str, Any], runtime: Path) -> dict[str, Any]:
    db_path = runtime / "checkpoint.sqlite"
    require_checkpoint(db_path)
    with core.checkpoint_connection(db_path) as connection:
        incomplete = connection.execute(
            "SELECT COUNT(*) FROM work_units WHERE stage='A' AND status!='COMPLETE'"
        ).fetchone()[0]
    if incomplete:
        raise RuntimeError(f"Stage A has {incomplete} incomplete units")
    source_by_cohort = {
        cohort["name"]: ROOT / cohort["source_catalog"]
        for cohort in protocol["cohorts"]
    }
    comparisons = []
    all_match = True
    for cohort_name, source_path in source_by_cohort.items():
        expected_by_rule = defaultdict(list)
        for row in load_jsonl(source_path):
            expected_by_rule[int(row["rule"])].append(row)
        for rule in range(256):
            actual_path = stage_paths(runtime, "A", cohort_name, rule)["replay"]
            actual_raw = load_jsonl(actual_path)
            expected_raw = expected_by_rule[rule]
            actual = unique_replay_identities(actual_raw)
            expected = unique_replay_identities(expected_raw)
            row = {
                "cohort": cohort_name,
                "rule": rule,
                "expected_raw_count": len(expected_raw),
                "actual_raw_count": len(actual_raw),
                "expected_duplicate_count": len(expected_raw) - len(expected),
                "actual_duplicate_count": len(actual_raw) - len(actual),
                "expected_count": len(expected),
                "actual_count": len(actual),
                "expected_digest": canonical_row_digest(expected),
                "actual_digest": canonical_row_digest(actual),
            }
            row["match"] = (
                row["expected_count"] == row["actual_count"]
                and row["expected_digest"] == row["actual_digest"]
            )
            all_match &= row["match"]
            comparisons.append(row)
    data = {
        "phase": 90,
        "status": "PASS" if all_match else "HISTORICAL_REPLAY_MISMATCH",
        "comparison_basis": "unique_physical_detector_identity",
        "ignored_catalog_annotation_fields": sorted(REPLAY_DERIVED_FIELDS),
        "comparisons": comparisons,
        "expected_raw_total": sum(
            row["expected_raw_count"] for row in comparisons
        ),
        "actual_raw_total": sum(row["actual_raw_count"] for row in comparisons),
        "expected_total": sum(row["expected_count"] for row in comparisons),
        "actual_total": sum(row["actual_count"] for row in comparisons),
    }
    path = runtime / "historical_replay_gate.json"
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return data


def stage_b_plan(protocol: dict[str, Any], runtime: Path) -> dict[str, Any]:
    candidate_paths = [
        stage_paths(runtime, "A", cohort, rule)["candidates"]
        for cohort, rule, _expected in core.work_units(protocol)
    ]
    missing = [str(path) for path in candidate_paths if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing {len(missing)} Stage-A candidate shards")
    candidate_bytes = sum(path.stat().st_size for path in candidate_paths)
    candidate_count = sum(
        1
        for path in candidate_paths
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    )
    fixed = int(protocol["ledger"]["estimated_raw_bytes"])
    required = core.dynamic_disk_requirement(
        fixed_ledger_bytes=fixed,
        candidate_bytes=candidate_bytes,
        candidate_count=candidate_count,
    )
    free = core.free_disk_bytes(runtime)
    model = protocol["cost_model"]
    workers = int(protocol["parallelism"]["recommended_workers"])
    rate = float(model["stage_b_reference_single_worker_rate_runs_per_second"])
    efficiency = float(model["stage_b_worker_efficiency_assumption"])
    return {
        "candidate_count": candidate_count,
        "candidate_bytes": candidate_bytes,
        "required_free_bytes": required,
        "observed_free_bytes": free,
        "disk_gate_pass": free >= required,
        "estimated_wall_seconds": (
            candidate_count / (rate * workers * efficiency) if candidate_count else 0.0
        ),
        "estimate_is_benchmark": False,
    }


def require_replay_pass(runtime: Path) -> dict[str, Any]:
    path = runtime / "historical_replay_gate.json"
    if not path.exists():
        raise PermissionError("Historical replay gate has not been run")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("status") != "PASS":
        raise PermissionError("Historical replay gate did not pass")
    return data


def require_checkpoint(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"Fase 90 checkpoint is not initialized: {path}")


def summarize_long_results(rows: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts = defaultdict(int)
    period_counts = defaultdict(int)
    cohort_counts = defaultdict(int)
    rule_counts = defaultdict(int)
    for row in rows:
        status_counts[row["confirmation_status"]] += 1
        if row["confirmation_status"] == "CONFIRMED_PERIOD_CAP_FALSE_NEGATIVE":
            period_counts[str(int(row["stage_b_period"]))] += 1
            cohort_counts[row["cohort"]] += 1
            rule_counts[str(int(row["rule"]))] += 1
    return {
        "candidate_count": len(rows),
        "confirmation_status_counts": dict(sorted(status_counts.items())),
        "confirmed_count": status_counts["CONFIRMED_PERIOD_CAP_FALSE_NEGATIVE"],
        "confirmed_period_distribution": dict(
            sorted(period_counts.items(), key=lambda item: int(item[0]))
        ),
        "confirmed_cohort_distribution": dict(sorted(cohort_counts.items())),
        "confirmed_rule_distribution": dict(
            sorted(rule_counts.items(), key=lambda item: int(item[0]))
        ),
    }


def finalize_results(protocol: dict[str, Any], runtime: Path) -> dict[str, Any]:
    replay = require_replay_pass(runtime)
    db_path = runtime / "checkpoint.sqlite"
    require_checkpoint(db_path)
    with core.checkpoint_connection(db_path) as connection:
        incomplete = connection.execute(
            "SELECT COUNT(*) FROM work_units WHERE stage='B' AND status!='COMPLETE'"
        ).fetchone()[0]
        stage_a = connection.execute(
            """
            SELECT SUM(processed_runs),SUM(source_positive_count),SUM(candidate_count)
            FROM work_units WHERE stage='A' AND status='COMPLETE'
            """
        ).fetchone()
        verification_errors = core.verify_complete_units(connection)
    if incomplete:
        raise RuntimeError(f"Stage B has {incomplete} incomplete units")
    if verification_errors:
        raise RuntimeError(f"Artifact verification failed: {verification_errors[:3]}")
    rows = []
    for cohort, rule, _expected in core.work_units(protocol):
        path = stage_paths(runtime, "B", cohort, rule)["long_results"]
        rows.extend(load_jsonl(path))
    summary = summarize_long_results(rows)
    if summary["candidate_count"] != int(stage_a[2] or 0):
        raise RuntimeError("Stage-B row count does not match Stage-A candidates")
    status = (
        "GLOBAL_PERIOD_CAP_FALSE_NEGATIVES_CONFIRMED"
        if summary["confirmed_count"]
        else "NO_GLOBAL_PERIOD_CAP_FALSE_NEGATIVES_CONFIRMED"
    )
    data = {
        "phase": 90,
        "status": status,
        "protocol_sha256": core.protocol_digest(protocol),
        "historical_replay_status": replay["status"],
        "processed_runs": int(stage_a[0] or 0),
        "historical_positive_rows_replayed": int(stage_a[1] or 0),
        "summary": summary,
        "methodological_limits": [
            "Recurrence is computationally confirmed through the frozen Stage-B horizon, not proved for arbitrary time.",
            "The result covers only the two frozen historical cohorts.",
            "Completion does not automatically change any paper, DOI, tag, or release.",
        ],
    }
    results_path = runtime / "phase90_global_period_cap_resweep_results.json"
    report_path = runtime / "phase90_global_period_cap_resweep_report.md"
    results_path.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    lines = [
        "# Fase 90: Global Period-Cap Re-sweep",
        "",
        f"Status: `{status}`.",
        "",
        f"- Processed runs: `{data['processed_runs']}`",
        f"- Historical positive rows replayed: `{data['historical_positive_rows_replayed']}`",
        f"- Stage-A candidates: `{summary['candidate_count']}`",
        f"- Stage-B confirmed false negatives: `{summary['confirmed_count']}`",
        f"- Confirmation classes: `{summary['confirmation_status_counts']}`",
        f"- Confirmed periods: `{summary['confirmed_period_distribution']}`",
        f"- Confirmed cohorts: `{summary['confirmed_cohort_distribution']}`",
        f"- Rules with confirmed misses: `{len(summary['confirmed_rule_distribution'])}`",
        "",
        "## Methodological Limits",
        "",
    ]
    lines.extend(f"- {item}" for item in data["methodological_limits"])
    lines.append("")
    report_path.write_text("\n".join(lines), encoding="utf-8")
    return {
        **data,
        "results_path": str(results_path),
        "report_path": str(report_path),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--protocol", type=Path, default=PROTOCOL_PATH)
    parser.add_argument("--runtime", type=Path, default=DEFAULT_RUNTIME)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight")
    init_parser = sub.add_parser("init")
    init_parser.add_argument("--authorization-file", type=Path, required=True)
    benchmark = sub.add_parser("benchmark")
    benchmark.add_argument("--authorization-file", type=Path, required=True)
    benchmark.add_argument("--unit", type=parse_unit, action="append", required=True)
    benchmark.add_argument("--workers", type=int, default=1)
    benchmark.add_argument("--report", type=Path, required=True)
    for name, stage in (("stage-a", "STAGE_A"), ("stage-b", "STAGE_B")):
        command = sub.add_parser(name)
        command.set_defaults(auth_stage=stage)
        command.add_argument("--authorization-file", type=Path, required=True)
        if name == "stage-a":
            command.add_argument("--benchmark-report", type=Path, required=True)
        command.add_argument("--workers", type=int, default=5)
        command.add_argument("--cohort", choices=["baseline_period_1_2_4", "primitive_len8"])
        command.add_argument("--start-rule", type=int, default=0)
        command.add_argument("--end-rule", type=int, default=255)
    sub.add_parser("replay-gate")
    sub.add_parser("stage-b-plan")
    sub.add_parser("status")
    sub.add_parser("verify")
    sub.add_parser("finalize")
    recover = sub.add_parser("recover-stale")
    recover.add_argument("--stale-before-epoch", type=float, required=True)
    args = parser.parse_args()
    protocol = core.load_protocol(args.protocol)
    digest = core.protocol_digest(protocol)

    if args.command == "preflight":
        print(json.dumps(generator_preflight(protocol), indent=2, sort_keys=True))
        return 0
    if args.command == "init":
        core.validate_authorization(
            args.authorization_file,
            expected_protocol_digest=digest,
            expected_stage="INIT",
            max_workers=1,
        )
        core.initialize_checkpoint(
            args.runtime / "checkpoint.sqlite",
            protocol_sha256=digest,
            units=core.work_units(protocol),
        )
        return 0
    if args.command == "benchmark":
        authorization = core.validate_authorization(
            args.authorization_file,
            expected_protocol_digest=digest,
            expected_stage="BENCHMARK",
            max_workers=args.workers,
        )
        allowed = set(authorization.get("allowed_units", []))
        requested = {f"{cohort}:{rule}" for cohort, rule in args.unit}
        if not requested or not requested.issubset(allowed):
            raise PermissionError("Benchmark unit is not explicitly authorized")
        if len(requested) > int(authorization.get("max_units", 0)):
            raise PermissionError("Benchmark exceeds authorized unit count")
        data = run_benchmark(
            protocol_path=args.protocol,
            runtime=args.runtime,
            units=args.unit,
            workers=args.workers,
            report_path=args.report,
        )
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0
    if args.command in {"stage-a", "stage-b"}:
        authorization = core.validate_authorization(
            args.authorization_file,
            expected_protocol_digest=digest,
            expected_stage=args.auth_stage,
            max_workers=args.workers,
        )
        if args.command == "stage-a":
            benchmark_report = validate_benchmark_report(
                args.benchmark_report,
                protocol_sha256=digest,
                workers=args.workers,
                expected_digest=str(authorization.get("benchmark_report_sha256", "")),
            )
            required = max(
                core.dynamic_disk_requirement(
                    fixed_ledger_bytes=int(protocol["ledger"]["estimated_raw_bytes"])
                ),
                int(benchmark_report.get("dynamic_required_free_bytes", 0)),
            )
            if core.free_disk_bytes(args.runtime) < required:
                raise OSError("Stage-A disk gate failed")
        if args.command == "stage-b":
            require_replay_pass(args.runtime)
            plan = stage_b_plan(protocol, args.runtime)
            if int(authorization.get("expected_candidate_count", -1)) != plan["candidate_count"]:
                raise PermissionError("Stage-B authorization candidate count mismatch")
            if not plan["disk_gate_pass"]:
                raise OSError("Stage-B dynamic disk gate failed")
        units = selected_units(protocol, args.cohort, args.start_rule, args.end_rule)
        run_parallel_stage(
            protocol_path=args.protocol,
            runtime=args.runtime,
            stage="A" if args.command == "stage-a" else "B",
            units=units,
            workers=args.workers,
        )
        return 0
    if args.command == "replay-gate":
        print(json.dumps(historical_replay_gate(protocol, args.runtime), indent=2, sort_keys=True))
        return 0
    if args.command == "stage-b-plan":
        print(json.dumps(stage_b_plan(protocol, args.runtime), indent=2, sort_keys=True))
        return 0
    if args.command in {"status", "verify"}:
        require_checkpoint(args.runtime / "checkpoint.sqlite")
        with core.checkpoint_connection(args.runtime / "checkpoint.sqlite") as connection:
            summary = core.checkpoint_summary(connection)
        print(json.dumps(summary, indent=2, sort_keys=True))
        return int(bool(summary["verification_errors"])) if args.command == "verify" else 0
    if args.command == "recover-stale":
        require_checkpoint(args.runtime / "checkpoint.sqlite")
        with core.checkpoint_connection(args.runtime / "checkpoint.sqlite") as connection:
            count = core.requeue_stale_units(
                connection, stale_before=args.stale_before_epoch
            )
        print(json.dumps({"requeued_units": count}, sort_keys=True))
        return 0
    if args.command == "finalize":
        print(json.dumps(finalize_results(protocol, args.runtime), indent=2, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
