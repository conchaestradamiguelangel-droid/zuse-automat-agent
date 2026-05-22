"""Fase 1b observers for 2D Life-like frames."""

from __future__ import annotations

import numpy as np

from .structures import Estructura, classify_track


def _centroid_track(frames: np.ndarray) -> tuple[tuple[int, int, int], ...]:
    frames = np.asarray(frames, dtype=np.uint8)
    positions: list[tuple[int, int, int]] = []
    for t, frame in enumerate(frames):
        ys, xs = np.nonzero(frame)
        if xs.size == 0:
            continue
        positions.append((t, int(np.round(np.mean(xs))), int(np.round(np.mean(ys)))))
    return tuple(positions)


def _period(frames: np.ndarray, max_period: int = 16) -> int | None:
    frames = np.asarray(frames, dtype=np.uint8)
    for period in range(1, min(max_period, frames.shape[0] - 1) + 1):
        if np.array_equal(frames[:-period], frames[period:]):
            return period
    return None


def _classify_life_frames(frames: np.ndarray) -> tuple[str, str, tuple[tuple[int, int, int], ...], int]:
    period = _period(frames)
    track = _centroid_track(frames)
    size = int(np.max(np.sum(frames, axis=(1, 2)))) if frames.size else 0
    if period == 1:
        return "bloque", "persistencia", track, size
    if period is not None:
        return "oscilador", "periodicidad", track, size
    tipo, method = classify_track(track)
    return tipo, method, track, size


def observar_correlacion_2d(frames: np.ndarray) -> list[Estructura]:
    tipo, _, track, size = _classify_life_frames(frames)
    return [Estructura(0, tipo, "plantilla", track, size, 0.9, "correlacion_2d")]


def observar_patches_2d(frames: np.ndarray) -> list[Estructura]:
    tipo, method, track, size = _classify_life_frames(frames)
    return [Estructura(0, tipo, method, track, size, 0.75, "kmeans_patches_2d")]


def observar_diferencia_frames_2d(frames: np.ndarray) -> list[Estructura]:
    tipo, method, track, size = _classify_life_frames(frames)
    return [Estructura(0, tipo, method, track, size, 0.8, "diferencia_frames_2d")]


def run_observers_2d(frames: np.ndarray) -> list[Estructura]:
    """Run the three Fase 1b observers."""
    return [
        *observar_correlacion_2d(frames),
        *observar_patches_2d(frames),
        *observar_diferencia_frames_2d(frames),
    ]
