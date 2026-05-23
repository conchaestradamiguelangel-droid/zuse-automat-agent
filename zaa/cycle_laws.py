"""Cycle-level law evaluation from observed structures."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .structures import Estructura


@dataclass(frozen=True)
class CycleLawResult:
    """Result of one cycle-level law evaluation."""

    name: str
    accepted: bool
    reason: str
    evidence: dict

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "accepted": self.accepted,
            "reason": self.reason,
            "evidence": self.evidence,
        }


def evaluate_velocity_law(structures: list[Estructura]) -> CycleLawResult:
    """Accept if >= 50% of moving structures have approximately linear x(t)."""
    tested = 0
    passing_count = 0
    max_velocity = 0.0
    for structure in structures:
        if len(structure.posiciones) < 4:
            continue
        ts = np.array([pos[0] for pos in structure.posiciones], dtype=np.float64)
        xs = np.array([pos[1] for pos in structure.posiciones], dtype=np.float64)
        a, b = np.polyfit(ts, xs, 1)
        residuals = xs - (a * ts + b)
        normalized = float(np.std(residuals) / (np.max(xs) - np.min(xs) + 1e-9))
        velocity = abs(float(a))
        max_velocity = max(max_velocity, velocity)
        if velocity > 0.05:
            tested += 1
            if normalized < 0.15:
                passing_count += 1

    passing_fraction = passing_count / tested if tested > 0 else 0.0
    accepted = tested > 0 and passing_fraction >= 0.5
    return CycleLawResult(
        "velocidad_constante",
        accepted,
        "velocidad_constante_detectada" if accepted else "sin_movimiento_lineal",
        {
            "n_structures_tested": tested,
            "passing_count": passing_count,
            "passing_fraction": passing_fraction,
            "max_velocity": max_velocity,
        },
    )


def evaluate_periodicity_law(structures: list[Estructura]) -> CycleLawResult:
    """Accept if at least one observed structure is an oscillator."""
    oscillator_count = sum(1 for structure in structures if structure.tipo == "oscilador")
    accepted = oscillator_count > 0
    return CycleLawResult(
        "periodicidad",
        accepted,
        "oscilador_detectado" if accepted else "sin_osciladores",
        {"oscillator_count": oscillator_count},
    )


def evaluate_density_law(frames: np.ndarray) -> CycleLawResult:
    """Accept if frame density is stable over time."""
    frames = np.asarray(frames, dtype=np.uint8)
    if frames.ndim == 3:
        frames = frames.reshape(frames.shape[0], -1)
    densities = np.mean(frames, axis=tuple(range(1, frames.ndim)))
    density_mean = float(np.mean(densities))
    density_cv = float(np.std(densities) / (density_mean + 1e-9))
    accepted = density_cv < 0.15
    return CycleLawResult(
        "densidad_estable",
        accepted,
        "densidad_estable" if accepted else "densidad_variable",
        {"density_mean": density_mean, "density_cv": density_cv},
    )


def evaluate_structure_count_law(structures: list[Estructura]) -> CycleLawResult:
    """Accept if only one structure type is present."""
    tipos_presentes = sorted({structure.tipo for structure in structures})
    accepted = len(tipos_presentes) == 1
    return CycleLawResult(
        "tipo_unico",
        accepted,
        "tipo_unico_dominante" if accepted else "tipos_multiples",
        {"tipos_presentes": tipos_presentes, "n_tipos": len(tipos_presentes)},
    )


def evaluate_cycle_laws(structures: list[Estructura], frames: np.ndarray) -> dict:
    """Evaluate all cycle-level law candidates."""
    results = [
        evaluate_velocity_law(structures),
        evaluate_periodicity_law(structures),
        evaluate_density_law(frames),
        evaluate_structure_count_law(structures),
    ]
    return {
        "laws_evaluated": [result.name for result in results],
        "laws_accepted": [result.name for result in results if result.accepted],
        "laws_rejected": [result.name for result in results if not result.accepted],
        "laws_status": "evaluated",
        "details": [result.to_dict() for result in results],
    }
