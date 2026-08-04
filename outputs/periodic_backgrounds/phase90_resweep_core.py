#!/usr/bin/env python3
"""Persistence and ledger primitives for the predeclared Fase 90 re-sweep."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import struct
import time
from contextlib import contextmanager
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Any, Iterable, Iterator


LEDGER_SCHEMA = struct.Struct("<BBBBhhB")
LEDGER_SCHEMA_VERSION = 1


class Kind(IntEnum):
    NOT_AVAILABLE = 0
    STATIONARY = 1
    MOVING = 2
    PERIOD1_ALIAS = 3
    BOUNDED_UNCLASSIFIED = 4
    ZERO_INITIAL_DEFECT = 5
    EXTINCT = 6
    SPAN_ESCAPE = 7


FLAG_BOUNDED_SOURCE = 1 << 0
FLAG_SOURCE_POSITIVE = 1 << 1
FLAG_CAP_CANDIDATE = 1 << 2
FLAG_STATIC_T1 = 1 << 3


@dataclass(frozen=True)
class LedgerRecord:
    source_kind: int
    expanded_kind: int
    source_period: int = 0
    expanded_period: int = 0
    source_drift: int = 0
    expanded_drift: int = 0
    flags: int = 0

    def encode(self) -> bytes:
        values = (
            self.source_kind,
            self.expanded_kind,
            self.source_period,
            self.expanded_period,
            self.source_drift,
            self.expanded_drift,
            self.flags,
        )
        for value in values[:4] + values[6:]:
            if not 0 <= int(value) <= 255:
                raise ValueError(f"Unsigned ledger value out of range: {value}")
        for value in values[4:6]:
            if not -32768 <= int(value) <= 32767:
                raise ValueError(f"Drift out of int16 range: {value}")
        return LEDGER_SCHEMA.pack(*values)

    @classmethod
    def decode(cls, payload: bytes) -> "LedgerRecord":
        if len(payload) != LEDGER_SCHEMA.size:
            raise ValueError(
                f"Ledger record must be {LEDGER_SCHEMA.size} bytes, got {len(payload)}"
            )
        return cls(*LEDGER_SCHEMA.unpack(payload))


def iter_ledger(path: Path) -> Iterator[LedgerRecord]:
    size = path.stat().st_size
    if size % LEDGER_SCHEMA.size:
        raise ValueError(
            f"Ledger size {size} is not divisible by record size {LEDGER_SCHEMA.size}"
        )
    with path.open("rb") as handle:
        while payload := handle.read(LEDGER_SCHEMA.size):
            yield LedgerRecord.decode(payload)


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def protocol_digest(protocol: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(protocol))


def load_protocol(path: Path) -> dict[str, Any]:
    protocol = json.loads(path.read_text(encoding="utf-8"))
    if int(protocol.get("phase", -1)) != 90:
        raise ValueError("Not a Fase 90 protocol")
    if int(protocol.get("schema_version", -1)) != 1:
        raise ValueError("Unsupported Fase 90 protocol schema")
    if int(protocol["ledger"]["bytes_per_run"]) != LEDGER_SCHEMA.size:
        raise ValueError("Protocol ledger size does not match decoder")
    return protocol


def work_units(protocol: dict[str, Any]) -> list[tuple[str, int, int]]:
    units = []
    for cohort in protocol["cohorts"]:
        per_rule = int(cohort["background_count"]) * int(cohort["ic_count"])
        for rule in range(int(cohort["rule_count"])):
            units.append((str(cohort["name"]), rule, per_rule))
    return units


def artifact_info(path: Path) -> dict[str, Any]:
    return {
        "path": str(path),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def validate_artifact(path: Path, size: int, digest: str) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)
    observed_size = path.stat().st_size
    if observed_size != int(size):
        raise ValueError(f"Size mismatch for {path}: {observed_size} != {size}")
    observed_digest = sha256_file(path)
    if observed_digest != digest:
        raise ValueError(f"Digest mismatch for {path}: {observed_digest} != {digest}")


def publish_temp_file(temp_path: Path, final_path: Path, expected_digest: str) -> dict[str, Any]:
    """Validate then replace a shard; failure leaves the prior final file untouched."""
    if not temp_path.is_file():
        raise FileNotFoundError(temp_path)
    if sha256_file(temp_path) != expected_digest:
        raise ValueError(f"Temporary artifact digest mismatch: {temp_path}")
    final_path.parent.mkdir(parents=True, exist_ok=True)
    # Windows rejects fsync on a read-only descriptor in some Python builds.
    with temp_path.open("r+b") as handle:
        os.fsync(handle.fileno())
    os.replace(temp_path, final_path)
    info = artifact_info(final_path)
    if info["sha256"] != expected_digest:
        raise ValueError(f"Published artifact digest mismatch: {final_path}")
    return info


def free_disk_bytes(path: Path) -> int:
    existing = path
    while not existing.exists() and existing != existing.parent:
        existing = existing.parent
    return int(shutil.disk_usage(existing).free)


def dynamic_disk_requirement(
    *,
    fixed_ledger_bytes: int,
    candidate_bytes: int = 0,
    candidate_count: int = 0,
    estimated_long_row_bytes: int = 640,
    safety_factor: float = 3.0,
    absolute_floor_bytes: int = 5 * 1024**3,
) -> int:
    measured_projection = safety_factor * (
        fixed_ledger_bytes
        + candidate_bytes
        + candidate_count * estimated_long_row_bytes
    )
    return max(int(absolute_floor_bytes), int(measured_projection))


def validate_authorization(
    path: Path,
    *,
    expected_protocol_digest: str,
    expected_stage: str,
    max_workers: int,
    now: float | None = None,
) -> dict[str, Any]:
    authorization = json.loads(path.read_text(encoding="utf-8"))
    if authorization.get("phase") != 90:
        raise PermissionError("Authorization is not for Fase 90")
    if authorization.get("approved") is not True:
        raise PermissionError("Authorization is not approved")
    if authorization.get("protocol_sha256") != expected_protocol_digest:
        raise PermissionError("Authorization protocol digest mismatch")
    if authorization.get("stage") != expected_stage:
        raise PermissionError("Authorization stage mismatch")
    if not str(authorization.get("authorized_by", "")).strip():
        raise PermissionError("Authorization has no author")
    allowed_workers = int(authorization.get("max_workers", 0))
    if max_workers < 1 or max_workers > allowed_workers:
        raise PermissionError(
            f"Requested workers {max_workers} exceed authorization {allowed_workers}"
        )
    current = time.time() if now is None else now
    expires_at = float(authorization.get("expires_at_epoch", 0))
    if expires_at <= current:
        raise PermissionError("Authorization is expired")
    return authorization


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS work_units (
    stage TEXT NOT NULL,
    cohort TEXT NOT NULL,
    rule INTEGER NOT NULL,
    expected_runs INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING',
    attempts INTEGER NOT NULL DEFAULT 0,
    started_at REAL,
    completed_at REAL,
    processed_runs INTEGER NOT NULL DEFAULT 0,
    source_positive_count INTEGER NOT NULL DEFAULT 0,
    candidate_count INTEGER NOT NULL DEFAULT 0,
    elapsed_seconds REAL NOT NULL DEFAULT 0,
    manifest_path TEXT,
    manifest_size INTEGER,
    manifest_sha256 TEXT,
    error TEXT,
    PRIMARY KEY (stage, cohort, rule)
);
CREATE TABLE IF NOT EXISTS artifacts (
    stage TEXT NOT NULL,
    cohort TEXT NOT NULL,
    rule INTEGER NOT NULL,
    kind TEXT NOT NULL,
    path TEXT NOT NULL,
    size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    PRIMARY KEY (stage, cohort, rule, kind),
    FOREIGN KEY (stage, cohort, rule)
      REFERENCES work_units(stage, cohort, rule)
);
"""


def connect_checkpoint(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=30)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=FULL")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript(SCHEMA_SQL)
    return connection


@contextmanager
def checkpoint_connection(path: Path):
    """Close SQLite explicitly; Connection.__exit__ commits but does not close."""
    connection = connect_checkpoint(path)
    try:
        yield connection
    finally:
        connection.close()


def initialize_checkpoint(
    path: Path,
    *,
    protocol_sha256: str,
    units: Iterable[tuple[str, int, int]],
) -> None:
    with checkpoint_connection(path) as connection, connection:
        existing = connection.execute(
            "SELECT value FROM metadata WHERE key='protocol_sha256'"
        ).fetchone()
        if existing is not None and existing["value"] != protocol_sha256:
            raise ValueError("Checkpoint belongs to a different protocol")
        connection.execute(
            "INSERT OR IGNORE INTO metadata(key,value) VALUES('protocol_sha256',?)",
            (protocol_sha256,),
        )
        connection.execute(
            "INSERT OR IGNORE INTO metadata(key,value) VALUES('ledger_schema_version',?)",
            (str(LEDGER_SCHEMA_VERSION),),
        )
        for cohort, rule, expected_runs in units:
            for stage in ("A", "B"):
                connection.execute(
                    """
                    INSERT OR IGNORE INTO work_units(stage,cohort,rule,expected_runs)
                    VALUES(?,?,?,?)
                    """,
                    (stage, cohort, rule, expected_runs if stage == "A" else 0),
                )


def claim_unit(
    connection: sqlite3.Connection,
    *,
    stage: str,
    cohort: str,
    rule: int,
    now: float | None = None,
) -> bool:
    timestamp = time.time() if now is None else now
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute(
            "SELECT status FROM work_units WHERE stage=? AND cohort=? AND rule=?",
            (stage, cohort, rule),
        ).fetchone()
        if row is None:
            raise KeyError((stage, cohort, rule))
        if row["status"] not in {"PENDING", "FAILED"}:
            connection.rollback()
            return False
        connection.execute(
            """
            UPDATE work_units
            SET status='RUNNING', attempts=attempts+1, started_at=?, error=NULL
            WHERE stage=? AND cohort=? AND rule=?
            """,
            (timestamp, stage, cohort, rule),
        )
        connection.commit()
        return True
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise


def fail_unit(
    connection: sqlite3.Connection,
    *,
    stage: str,
    cohort: str,
    rule: int,
    error: str,
) -> None:
    with connection:
        connection.execute(
            """
            UPDATE work_units SET status='FAILED', error=?
            WHERE stage=? AND cohort=? AND rule=?
            """,
            (error, stage, cohort, rule),
        )


def complete_unit(
    connection: sqlite3.Connection,
    *,
    stage: str,
    cohort: str,
    rule: int,
    processed_runs: int,
    source_positive_count: int,
    candidate_count: int,
    elapsed_seconds: float,
    manifest: dict[str, Any],
    manifest_info: dict[str, Any],
) -> None:
    artifacts = manifest.get("artifacts", {})
    for item in artifacts.values():
        validate_artifact(Path(item["path"]), int(item["size"]), item["sha256"])
    validate_artifact(
        Path(manifest_info["path"]),
        int(manifest_info["size"]),
        manifest_info["sha256"],
    )
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute(
            "SELECT status,expected_runs FROM work_units WHERE stage=? AND cohort=? AND rule=?",
            (stage, cohort, rule),
        ).fetchone()
        if row is None or row["status"] != "RUNNING":
            raise ValueError("Unit must be RUNNING before completion")
        if stage == "A" and int(row["expected_runs"]) != int(processed_runs):
            raise ValueError("Processed count does not match expected work-unit size")
        for kind, item in artifacts.items():
            connection.execute(
                """
                INSERT OR REPLACE INTO artifacts(stage,cohort,rule,kind,path,size,sha256)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    stage,
                    cohort,
                    rule,
                    kind,
                    item["path"],
                    int(item["size"]),
                    item["sha256"],
                ),
            )
        connection.execute(
            """
            UPDATE work_units
            SET status='COMPLETE', completed_at=?, processed_runs=?,
                source_positive_count=?, candidate_count=?, elapsed_seconds=?,
                manifest_path=?, manifest_size=?, manifest_sha256=?, error=NULL
            WHERE stage=? AND cohort=? AND rule=?
            """,
            (
                time.time(),
                processed_runs,
                source_positive_count,
                candidate_count,
                elapsed_seconds,
                manifest_info["path"],
                int(manifest_info["size"]),
                manifest_info["sha256"],
                stage,
                cohort,
                rule,
            ),
        )
        connection.commit()
    except Exception:
        if connection.in_transaction:
            connection.rollback()
        raise


def requeue_stale_units(
    connection: sqlite3.Connection,
    *,
    stale_before: float,
) -> int:
    with connection:
        cursor = connection.execute(
            """
            UPDATE work_units
            SET status='PENDING', error='requeued_stale_running_unit'
            WHERE status='RUNNING' AND started_at < ?
            """,
            (stale_before,),
        )
    return int(cursor.rowcount)


def verify_complete_units(connection: sqlite3.Connection) -> list[str]:
    errors = []
    rows = connection.execute(
        "SELECT * FROM work_units WHERE status='COMPLETE' ORDER BY stage,cohort,rule"
    ).fetchall()
    for row in rows:
        unit = f"{row['stage']}:{row['cohort']}:{row['rule']}"
        try:
            validate_artifact(
                Path(row["manifest_path"]),
                int(row["manifest_size"]),
                row["manifest_sha256"],
            )
            artifacts = connection.execute(
                "SELECT * FROM artifacts WHERE stage=? AND cohort=? AND rule=?",
                (row["stage"], row["cohort"], row["rule"]),
            ).fetchall()
            if not artifacts:
                raise ValueError("No artifacts registered")
            for artifact in artifacts:
                validate_artifact(
                    Path(artifact["path"]),
                    int(artifact["size"]),
                    artifact["sha256"],
                )
        except Exception as exc:  # verification must report every corrupt unit
            errors.append(f"{unit}: {exc}")
    return errors


def checkpoint_summary(connection: sqlite3.Connection) -> dict[str, Any]:
    rows = connection.execute(
        """
        SELECT stage,status,COUNT(*) AS units,SUM(processed_runs) AS processed,
               SUM(source_positive_count) AS positives,SUM(candidate_count) AS candidates
        FROM work_units GROUP BY stage,status ORDER BY stage,status
        """
    ).fetchall()
    return {
        "groups": [dict(row) for row in rows],
        "verification_errors": verify_complete_units(connection),
    }
