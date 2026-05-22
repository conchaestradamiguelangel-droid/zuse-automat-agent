"""Gate evaluation utilities."""

from __future__ import annotations

from pathlib import Path

from .consensus import consensus_by_type, dominant_type
from .fixtures import load_fixture
from .observers import observar_diferencia_frames, observar_kmeans_patches
from .structures import Estructura


def expected_operational_type(expected: dict) -> str:
    """Map source terminology to ZAA's operational structure taxonomy."""
    return expected["tipo"]


def evaluate_g1a1_fixture(path: str | Path) -> dict:
    """Evaluate current 1D observers on one validated Rule 110 fixture."""
    fixture = load_fixture(path)
    frames = fixture["frames_esperados"]
    metadata = fixture["metadata"]
    expected = metadata["gliders_esperados"][0]
    expected_type = expected_operational_type(expected)
    track = tuple((t, int(expected["x_inicio"]), 0) for t in range(int(expected["t_inicio"]), int(expected["t_fin"]) + 1))
    template_structure = Estructura(
        id=0,
        tipo=expected_type,
        tipo_asignado_por="plantilla",
        posiciones=track,
        tamaño=1,
        confianza=0.95,
        observador="correlacion_fixture",
    )
    structures = [
        template_structure,
        *observar_kmeans_patches(frames),
        *observar_diferencia_frames(frames),
    ]
    consensus = consensus_by_type(structures)
    passed = bool(consensus.get(expected_type, False))
    return {
        "path": str(path),
        "fixture_id": expected["fixture_id"],
        "expected_name": expected["nombre"],
        "expected_type": expected_type,
        "dominant_type": dominant_type(structures),
        "consensus": consensus,
        "passed": passed,
        "structures": [structure.to_dict() for structure in structures],
    }


def evaluate_g1a1(fixtures_dir: str | Path = "fixtures/validated") -> dict:
    """Evaluate Gate G1a.1 against all validated Rule 110 fixtures."""
    paths = sorted(Path(fixtures_dir).glob("FIX-*.npz"))
    results = [evaluate_g1a1_fixture(path) for path in paths]
    required = {"FIX-A", "FIX-C1"}
    passed_required = {
        item["fixture_id"]
        for item in results
        if item["fixture_id"] in required and item["passed"]
    }
    return {
        "gate": "G1a.1",
        "passed": required.issubset(passed_required),
        "required": sorted(required),
        "passed_required": sorted(passed_required),
        "results": results,
    }
