"""Serializable fixtures for validated Rule 110 structures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


def save_fixture(
    path: str | Path,
    *,
    nombre: str,
    fuente: str,
    seed: int,
    ci: np.ndarray,
    frames_esperados: np.ndarray,
    gliders_esperados: list[dict[str, Any]],
) -> Path:
    """Save a complete validation fixture as a compressed NPZ file."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    ci = np.asarray(ci, dtype=np.uint8)
    frames = np.asarray(frames_esperados, dtype=np.uint8)
    metadata = {
        "nombre": nombre,
        "fuente": fuente,
        "seed": seed,
        "W": int(ci.shape[0]),
        "T": int(frames.shape[0]),
        "gliders_esperados": gliders_esperados,
    }
    np.savez_compressed(
        output,
        ci=ci,
        frames_esperados=frames,
        metadata_json=json.dumps(metadata, sort_keys=True),
    )
    return output


def load_fixture(path: str | Path) -> dict[str, Any]:
    """Load a validation fixture saved with save_fixture."""
    with np.load(Path(path), allow_pickle=False) as data:
        metadata = json.loads(str(data["metadata_json"]))
        return {
            "ci": data["ci"].copy(),
            "frames_esperados": data["frames_esperados"].copy(),
            "metadata": metadata,
        }
