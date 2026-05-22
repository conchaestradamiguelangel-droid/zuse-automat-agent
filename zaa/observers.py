"""Fase 1a observers for 1D space-time frames."""

from __future__ import annotations

import itertools

import numpy as np

from .structures import Estructura, classify_track


def _active_positions_by_time(frames: np.ndarray) -> list[list[int]]:
    frames = np.asarray(frames, dtype=np.uint8)
    return [np.flatnonzero(frame).astype(int).tolist() for frame in frames]


def _track_nearest_active(frames: np.ndarray, *, max_jump: int = 2, min_persistence: int = 10) -> list[tuple[tuple[int, int, int], ...]]:
    """Track active cells over time with a small nearest-neighbor heuristic."""
    positions_by_time = _active_positions_by_time(frames)
    active_tracks: list[list[tuple[int, int, int]]] = [[(0, x, 0)] for x in positions_by_time[0]]
    closed: list[list[tuple[int, int, int]]] = []

    for t in range(1, len(positions_by_time)):
        unused = set(positions_by_time[t])
        next_tracks: list[list[tuple[int, int]]] = []
        for track in active_tracks:
            _, last_x, _ = track[-1]
            if not unused:
                closed.append(track)
                continue
            best = min(unused, key=lambda x: abs(x - last_x))
            if abs(best - last_x) <= max_jump:
                unused.remove(best)
                next_tracks.append([*track, (t, best, 0)])
            else:
                closed.append(track)
        for x in sorted(unused):
            next_tracks.append([(t, x, 0)])
        active_tracks = next_tracks

    closed.extend(active_tracks)
    return [tuple(track) for track in closed if len(track) >= min_persistence]


def _is_periodic_local(frames: np.ndarray) -> bool:
    """Detect simple period-2 local oscillation."""
    frames = np.asarray(frames, dtype=np.uint8)
    if frames.shape[0] < 4:
        return False
    return bool(np.array_equal(frames[:-2], frames[2:]) and not np.array_equal(frames[:-1], frames[1:]))


def _static_block_track(frames: np.ndarray) -> tuple[tuple[tuple[int, int, int], ...], int] | None:
    """Return one centroid track for a static active region, if present."""
    frames = np.asarray(frames, dtype=np.uint8)
    if frames.shape[0] < 2 or not np.array_equal(frames[0], frames[-1]):
        return None
    if not np.all(frames == frames[0]):
        return None
    xs = np.flatnonzero(frames[0])
    if xs.size == 0:
        return None
    if xs.size > 1 and not np.all(np.diff(xs) == 1):
        return None
    center = int(np.round(np.mean(xs)))
    return tuple((t, center, 0) for t in range(frames.shape[0])), int(xs.size)


def observar_diferencia_frames(frames: np.ndarray, *, min_persistence: int = 10) -> list[Estructura]:
    """O3: difference/threshold observer with nearest-neighbor tracking."""
    block = _static_block_track(frames)
    if block is not None:
        track, size = block
        return [
            Estructura(0, "bloque", "desplazamiento", track, size, 0.8, "diferencia_frames")
        ]

    tracks = _track_nearest_active(frames, min_persistence=min_persistence)
    structures: list[Estructura] = []
    periodic = _is_periodic_local(frames)
    for idx, track in enumerate(tracks):
        tipo, method = classify_track(track, periodic=periodic)
        structures.append(
            Estructura(
                id=idx,
                tipo=tipo,
                tipo_asignado_por=method,
                posiciones=track,
                tamaño=1,
                confianza=0.75,
                observador="diferencia_frames",
            )
        )
    return structures


def observar_correlacion(frames: np.ndarray, *, min_persistence: int = 10) -> list[Estructura]:
    """O1: simple template observer for synthetic glider/block/oscillator frames."""
    frames = np.asarray(frames, dtype=np.uint8)
    structures: list[Estructura] = []
    block = _static_block_track(frames)
    if block is not None:
        track, size = block
        return [Estructura(0, "bloque", "plantilla", track, size, 0.9, "correlacion")]

    periodic = _is_periodic_local(frames)
    if periodic:
        xs = np.flatnonzero(np.any(frames, axis=0))
        center = int(np.round(np.mean(xs))) if xs.size else 0
        track = tuple((t, center, 0) for t in range(frames.shape[0]))
        structures.append(
            Estructura(0, "oscilador", "plantilla", track, int(xs.size), 0.9, "correlacion")
        )
        return structures

    tracks = _track_nearest_active(frames, min_persistence=min_persistence)
    for idx, track in enumerate(tracks):
        tipo, _ = classify_track(track)
        structures.append(Estructura(idx, tipo, "plantilla", track, 1, 0.85, "correlacion"))
    return structures


def observar_kmeans_patches(frames: np.ndarray, *, min_persistence: int = 10) -> list[Estructura]:
    """O2: lightweight patch observer.

    This is a dependency-free stand-in for k-means over patches. It extracts
    connected active tracks and assigns type by velocity/periodicity, matching
    the final contract while keeping Fase 1a runnable without scikit-learn.
    """
    block = _static_block_track(frames)
    if block is not None:
        track, size = block
        return [Estructura(0, "bloque", "desplazamiento", track, size, 0.75, "kmeans_patches")]

    periodic = _is_periodic_local(frames)
    tracks = _track_nearest_active(frames, min_persistence=min_persistence)
    structures: list[Estructura] = []
    for idx, track in enumerate(tracks):
        tipo, method = classify_track(track, periodic=periodic)
        structures.append(Estructura(idx, tipo, method, track, 1, 0.7, "kmeans_patches"))
    return structures


def run_observers(frames: np.ndarray) -> list[Estructura]:
    """Run the three Fase 1a observers."""
    return list(
        itertools.chain(
            observar_correlacion(frames),
            observar_kmeans_patches(frames),
            observar_diferencia_frames(frames),
        )
    )
