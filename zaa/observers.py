"""Fase 1a observers for 1D space-time frames."""

from __future__ import annotations

import itertools

import numpy as np

from .ether import diff_from_pure_ether
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


def _is_periodic_local(frames: np.ndarray, *, max_period: int = 16) -> bool:
    """Detect local oscillation with a small exact period."""
    frames = np.asarray(frames, dtype=np.uint8)
    if frames.shape[0] < 4:
        return False
    changed = any(not np.array_equal(frames[:-p], frames[p:]) for p in range(1, min(max_period, frames.shape[0] - 1) + 1))
    if not changed:
        return False
    for period in range(2, min(max_period, frames.shape[0] - 1) + 1):
        if np.array_equal(frames[:-period], frames[period:]):
            return True
    return False


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


def filter_structures_by_start_frame(
    structures: list[Estructura],
    max_start_frame: int,
) -> list[Estructura]:
    """Diagnostic anti-ether filter: keep structures born before a frame threshold."""
    return [
        structure
        for structure in structures
        if structure.posiciones and structure.posiciones[0][0] < max_start_frame
    ]


def find_connected_regions_1d(frame: np.ndarray) -> list[dict]:
    """Find contiguous active regions in a binary 1D frame."""
    frame = np.asarray(frame, dtype=np.uint8)
    if frame.ndim != 1:
        raise ValueError("frame must be a 1D array")

    regions: list[dict] = []
    start: int | None = None
    for idx, value in enumerate(frame):
        if value and start is None:
            start = idx
        elif not value and start is not None:
            cells = list(range(start, idx))
            regions.append({"center_x": int(round((start + idx - 1) / 2)), "width": len(cells), "cells": cells})
            start = None

    if start is not None:
        cells = list(range(start, frame.shape[0]))
        regions.append(
            {
                "center_x": int(round((start + frame.shape[0] - 1) / 2)),
                "width": len(cells),
                "cells": cells,
            }
        )
    return regions


def track_regions_1d(
    defect_frames: np.ndarray,
    *,
    min_persistence: int = 5,
    max_jump: int = 4,
    max_tracks_before_merge: int = 5,
) -> list[list[tuple[int, int, int]]]:
    """Track connected 1D defect regions by centroid proximity."""
    defect_frames = np.asarray(defect_frames, dtype=np.uint8)
    if defect_frames.ndim != 2:
        raise ValueError("defect_frames must have shape (T, W)")

    active_tracks: list[list[tuple[int, int, int]]] = []
    closed_tracks: list[list[tuple[int, int, int]]] = []

    for t, frame in enumerate(defect_frames):
        regions = find_connected_regions_1d(frame)
        unused = set(range(len(regions)))
        next_tracks: list[list[tuple[int, int, int]]] = []

        for track in active_tracks:
            _, last_x, _ = track[-1]
            if not unused:
                closed_tracks.append(track)
                continue
            best_idx = min(unused, key=lambda idx: abs(regions[idx]["center_x"] - last_x))
            region = regions[best_idx]
            if abs(region["center_x"] - last_x) <= max_jump:
                unused.remove(best_idx)
                next_tracks.append([*track, (t, int(region["center_x"]), int(region["width"]))])
            else:
                closed_tracks.append(track)

        for idx in sorted(unused):
            region = regions[idx]
            next_tracks.append([(t, int(region["center_x"]), int(region["width"]))])

        active_tracks = next_tracks

    closed_tracks.extend(active_tracks)
    tracks = [track for track in closed_tracks if len(track) >= min_persistence]
    if len(tracks) <= max_tracks_before_merge:
        return tracks

    aggregate: list[tuple[int, int, int]] = []
    for t, frame in enumerate(defect_frames):
        xs = np.flatnonzero(frame)
        if xs.size == 0:
            continue
        left = int(xs.min())
        right = int(xs.max())
        aggregate.append((t, int(round((left + right) / 2)), right - left + 1))
    if len(aggregate) >= min_persistence:
        return [aggregate]
    return tracks


def observar_regiones_rule110(frames: np.ndarray, *, min_persistence: int = 5) -> list[Estructura]:
    """Observe Rule 110 structures as connected tracks over ether-diff frames."""
    tracks = track_regions_1d(diff_from_pure_ether(frames), min_persistence=min_persistence)
    structures: list[Estructura] = []
    for idx, track in enumerate(tracks):
        posiciones = tuple((t, x, 0) for t, x, _ in track)
        tipo, method = classify_track(posiciones)
        widths = [width for _, _, width in track]
        if tipo == "bloque" and len(set(widths)) > 1:
            tipo = "glider"
            method = "persistencia"
        avg_width = int(round(float(np.mean(widths))))
        structures.append(
            Estructura(
                id=idx,
                tipo=tipo,
                tipo_asignado_por=method,
                posiciones=posiciones,
                tamaño=max(1, avg_width),
                confianza=0.8,
                observador="regiones_rule110",
            )
        )
    return structures
