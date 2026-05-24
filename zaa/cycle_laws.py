"""Cycle-level law evaluation from observed structures."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .metrics import active_transition_rate, gzip_compressibility, shannon_entropy
from .structures import Estructura


# Calibrated 2026-05-24 for rule_30/rule_110 at steps=24, width=64,
# seeds 20260523..20260528. Midpoint between max(rule_110)=0.4147
# and min(rule_30)=0.4557.
_FRONTERA_THRESHOLD_MAX: float = 0.4352

# Calibrated 2026-05-24 on datasets/fase2c_v3.csv using
# temporal_load = steps * gzip_ratio / transition_rate. Best threshold
# over 120 ECA scale samples: accuracy=0.9083, precision_ok=0.8857,
# recall_ok=0.9538.
_TEMPORAL_SCALE_THRESHOLD: float = 19.03


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


def evaluate_complexity_law(frames: np.ndarray) -> CycleLawResult:
    """Accept if frames show high entropy and high cell-transition rate."""
    frames = np.asarray(frames, dtype=np.uint8)
    if frames.ndim == 3:
        frames = frames.reshape(frames.shape[0], -1)
    entropy_mean = float(np.mean([shannon_entropy(frame) for frame in frames]))
    transition_rate = active_transition_rate(frames)
    accepted = entropy_mean > 0.8 and transition_rate > 0.25
    return CycleLawResult(
        "complejidad_alta",
        accepted,
        "complejidad_alta_detectada" if accepted else "complejidad_baja",
        {"entropy_mean": entropy_mean, "transition_rate": transition_rate},
    )


def evaluate_frontera_temporal(
    frames: np.ndarray,
    *,
    threshold_max: float,
    threshold_min: float = 0.28,
) -> CycleLawResult:
    """Accept organized chaos: high entropy below pure-random transition rate."""
    frames_arr = np.asarray(frames, dtype=np.uint8)
    if frames_arr.ndim == 3:
        frames_arr = frames_arr.reshape(frames_arr.shape[0], -1)
    entropy_mean = float(np.mean([shannon_entropy(frame) for frame in frames_arr]))
    transition_rate = active_transition_rate(frames_arr)
    accepted = entropy_mean > 0.8 and threshold_min < transition_rate < threshold_max
    return CycleLawResult(
        "frontera_temporal",
        accepted,
        "caos_organizado" if accepted else "caos_puro_o_sin_entropia",
        {
            "transition_rate": transition_rate,
            "entropy_mean": entropy_mean,
            "threshold_max": threshold_max,
        },
    )


def evaluate_temporal_scale_stability(
    frames: np.ndarray,
    steps: int,
    threshold: float = _TEMPORAL_SCALE_THRESHOLD,
) -> CycleLawResult:
    """Accept if temporal load stays below the calibrated analyzability scale."""
    frames_arr = np.asarray(frames, dtype=np.uint8)
    transition_rate = active_transition_rate(frames_arr)
    gzip_ratio = float(gzip_compressibility(frames_arr))
    if transition_rate == 0.0:
        return CycleLawResult(
            "temporal_scale_stability",
            False,
            "sin_transiciones_temporales",
            {
                "temporal_load": float("inf"),
                "C": threshold,
                "gzip_ratio": gzip_ratio,
                "transition_rate": transition_rate,
            },
        )
    temporal_load = float(steps * gzip_ratio / transition_rate)
    accepted = temporal_load < threshold
    return CycleLawResult(
        "temporal_scale_stability",
        accepted,
        "escala_temporal_estable" if accepted else "escala_temporal_inestable",
        {
            "temporal_load": temporal_load,
            "C": threshold,
            "gzip_ratio": gzip_ratio,
            "transition_rate": transition_rate,
        },
    )


def evaluate_cycle_laws(structures: list[Estructura], frames: np.ndarray, steps: int) -> dict:
    """Evaluate all cycle-level law candidates."""
    results = [
        evaluate_velocity_law(structures),
        evaluate_periodicity_law(structures),
        evaluate_density_law(frames),
        evaluate_structure_count_law(structures),
        evaluate_complexity_law(frames),
        evaluate_frontera_temporal(frames, threshold_max=_FRONTERA_THRESHOLD_MAX),
        evaluate_temporal_scale_stability(frames, steps),
    ]
    return {
        "laws_evaluated": [result.name for result in results],
        "laws_accepted": [result.name for result in results if result.accepted],
        "laws_rejected": [result.name for result in results if not result.accepted],
        "laws_status": "evaluated",
        "details": [result.to_dict() for result in results],
    }
