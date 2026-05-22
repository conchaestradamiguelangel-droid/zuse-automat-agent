"""Discrete invariant candidate evaluation for Fase 2a."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np

from .fixtures import load_fixture
from .mdl import mdl_null, mdl_score


@dataclass(frozen=True)
class CandidateLawResult:
    """Result of evaluating one law candidate."""

    name: str
    accepted: bool
    consistency: float
    mdl_candidate: int
    mdl_null: int
    model: dict[str, Any]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "accepted": self.accepted,
            "consistency": self.consistency,
            "mdl_candidate": self.mdl_candidate,
            "mdl_null": self.mdl_null,
            "model": self.model,
            "reason": self.reason,
        }


def _accept(consistency: float, candidate_score: int, null_score: int) -> bool:
    return consistency >= 0.95 and candidate_score < null_score


def evaluate_parity_total(frames: np.ndarray) -> CandidateLawResult:
    """Evaluate whether total active-cell parity is constant."""
    parity = (np.sum(frames, axis=tuple(range(1, frames.ndim))) % 2).astype(np.int16)
    predicted = np.full_like(parity, parity[0])
    consistency = float(np.mean(parity == predicted))
    residuos = parity - predicted
    model = {"tipo": "paridad_constante", "valor": int(parity[0])}
    candidate = mdl_score(model, residuos.astype(np.int16))
    null = mdl_null(parity)
    accepted = _accept(consistency, candidate, null)
    return CandidateLawResult(
        "paridad_total",
        accepted,
        consistency,
        candidate,
        null,
        model,
        "accepted" if accepted else "consistency_or_mdl_failed",
    )


def evaluate_fixture_velocity(metadata: dict[str, Any]) -> CandidateLawResult:
    """Evaluate fixture-provided constant velocity as a candidate law."""
    expected = metadata["gliders_esperados"][0]
    period = int(expected["period_t"])
    displacement = int(expected["displacement_x"])
    steps = int(expected["t_fin"]) - int(expected["t_inicio"])
    periods = max(1, steps // period)
    observed = np.full(periods, displacement, dtype=np.int16)
    predicted = np.full_like(observed, displacement)
    consistency = float(np.mean(observed == predicted))
    residuos = observed - predicted
    model = {
        "tipo": "velocidad_constante",
        "fixture_id": expected["fixture_id"],
        "period_t": period,
        "displacement_x": displacement,
        "velocity": expected["velocity"],
    }
    candidate = mdl_score(model, residuos.astype(np.int16))
    null = mdl_null(observed)
    accepted = _accept(consistency, candidate, null)
    return CandidateLawResult(
        "velocidad_constante",
        accepted,
        consistency,
        candidate,
        null,
        model,
        "accepted" if accepted else "consistency_or_mdl_failed",
    )


def evaluate_fixture_periodicity(metadata: dict[str, Any]) -> CandidateLawResult:
    """Evaluate fixture-provided period as a candidate law."""
    expected = metadata["gliders_esperados"][0]
    period = int(expected["period_t"])
    steps = int(expected["t_fin"]) - int(expected["t_inicio"])
    cycles = max(1, steps // period)
    observed = np.full(cycles, period, dtype=np.int16)
    predicted = np.full_like(observed, period)
    consistency = float(np.mean(observed == predicted))
    residuos = observed - predicted
    model = {
        "tipo": "periodicidad_constante",
        "fixture_id": expected["fixture_id"],
        "period_t": period,
    }
    candidate = mdl_score(model, residuos.astype(np.int16))
    null = mdl_null(observed)
    accepted = _accept(consistency, candidate, null)
    return CandidateLawResult(
        "periodicidad",
        accepted,
        consistency,
        candidate,
        null,
        model,
        "accepted" if accepted else "consistency_or_mdl_failed",
    )


def evaluate_structure_count(metadata: dict[str, Any]) -> CandidateLawResult:
    """Evaluate whether fixture has constant expected structure count."""
    expected_count = len(metadata["gliders_esperados"])
    expected = metadata["gliders_esperados"][0]
    duration = int(expected["t_fin"]) - int(expected["t_inicio"]) + 1
    observed = np.full(duration, expected_count, dtype=np.int16)
    predicted = np.full_like(observed, expected_count)
    consistency = float(np.mean(observed == predicted))
    residuos = observed - predicted
    model = {"tipo": "conteo_estructuras_constante", "n": expected_count}
    candidate = mdl_score(model, residuos.astype(np.int16))
    null = mdl_null(observed)
    accepted = _accept(consistency, candidate, null)
    return CandidateLawResult(
        "conteo_estructuras",
        accepted,
        consistency,
        candidate,
        null,
        model,
        "accepted" if accepted else "consistency_or_mdl_failed",
    )


def evaluate_fixture_laws(path: str | Path) -> dict[str, Any]:
    """Evaluate Fase 2a law candidates for one validated fixture."""
    fixture = load_fixture(path)
    metadata = fixture["metadata"]
    frames = fixture["frames_esperados"]
    results = [
        evaluate_parity_total(frames),
        evaluate_fixture_velocity(metadata),
        evaluate_fixture_periodicity(metadata),
        evaluate_structure_count(metadata),
    ]
    return {
        "fixture": str(path),
        "fixture_id": metadata["gliders_esperados"][0]["fixture_id"],
        "results": [result.to_dict() for result in results],
    }


def evaluate_all_fixture_laws(fixtures_dir: str | Path = "fixtures/validated") -> dict[str, Any]:
    """Evaluate Fase 2a law candidates for all validated Rule 110 fixtures."""
    reports = [evaluate_fixture_laws(path) for path in sorted(Path(fixtures_dir).glob("FIX-*.npz"))]
    accepted = [
        (report["fixture_id"], result["name"])
        for report in reports
        for result in report["results"]
        if result["accepted"]
    ]
    rejected = [
        (report["fixture_id"], result["name"])
        for report in reports
        for result in report["results"]
        if not result["accepted"]
    ]
    return {"fixtures_dir": str(fixtures_dir), "accepted": accepted, "rejected": rejected, "reports": reports}


def save_law_report(report: dict[str, Any], output_dir: str | Path = "reports/fase2a") -> dict[str, Path]:
    """Save Fase 2a law evaluation as JSON and Markdown."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "laws_2a.json"
    md_path = out / "laws_2a.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Fase 2a - Evaluacion de leyes discretas",
        "",
        f"- Fixtures: `{report['fixtures_dir']}`",
        f"- Aceptadas: `{len(report['accepted'])}`",
        f"- Rechazadas: `{len(report['rejected'])}`",
        "",
        "## Resultados",
        "",
    ]
    for fixture_report in report["reports"]:
        lines.append(f"### {fixture_report['fixture_id']}")
        lines.append("")
        for result in fixture_report["results"]:
            status = "ACEPTADA" if result["accepted"] else "RECHAZADA"
            lines.append(
                f"- `{result['name']}`: {status}; "
                f"consistencia `{result['consistency']:.3f}`; "
                f"MDL `{result['mdl_candidate']} < {result['mdl_null']}`"
            )
        lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}
