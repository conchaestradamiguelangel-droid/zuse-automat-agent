"""SQLite storage for Fase 0a simulations."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any


SCHEMA = """
CREATE TABLE IF NOT EXISTS universes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule INTEGER NOT NULL,
    ci_index INTEGER NOT NULL,
    seed INTEGER NOT NULL,
    width INTEGER NOT NULL,
    steps INTEGER NOT NULL,
    metrics_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Open a database connection and ensure the schema exists."""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(SCHEMA)
    conn.commit()
    return conn


def insert_universe(
    conn: sqlite3.Connection,
    *,
    rule: int,
    ci_index: int,
    seed: int,
    width: int,
    steps: int,
    metrics: dict[str, Any],
) -> int:
    """Insert one simulated universe and return its row id."""
    cur = conn.execute(
        """
        INSERT INTO universes (rule, ci_index, seed, width, steps, metrics_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (rule, ci_index, seed, width, steps, json.dumps(metrics, sort_keys=True)),
    )
    conn.commit()
    return int(cur.lastrowid)


def count_universes(conn: sqlite3.Connection) -> int:
    """Return number of stored universes."""
    cur = conn.execute("SELECT COUNT(*) FROM universes")
    return int(cur.fetchone()[0])
