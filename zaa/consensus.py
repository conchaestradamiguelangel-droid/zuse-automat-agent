"""Observer consensus utilities."""

from __future__ import annotations

from collections import Counter

from .structures import Estructura, StructureType


def _mean_overlap_distance(left: Estructura, right: Estructura) -> float | None:
    left_by_frame = {t: x for t, x, _ in left.posiciones}
    right_by_frame = {t: x for t, x, _ in right.posiciones}
    common_frames = sorted(set(left_by_frame) & set(right_by_frame))
    if not common_frames:
        return None
    return sum(abs(left_by_frame[t] - right_by_frame[t]) for t in common_frames) / len(common_frames)


def deduplicate_structures(
    structures: list[Estructura],
    *,
    max_gap: int = 2,
) -> list[Estructura]:
    """Reduce observer output to one representative per physical structure."""
    ordered = sorted(
        structures,
        key=lambda structure: (structure.confianza, len(structure.posiciones)),
        reverse=True,
    )
    clusters: list[list[Estructura]] = []

    for structure in ordered:
        best_cluster: list[Estructura] | None = None
        best_distance: float | None = None
        for cluster in clusters:
            distances = [
                distance
                for candidate in cluster
                if (distance := _mean_overlap_distance(structure, candidate)) is not None
            ]
            if not distances:
                continue
            distance = min(distances)
            if distance <= max_gap and (best_distance is None or distance < best_distance):
                best_cluster = cluster
                best_distance = distance
        if best_cluster is None:
            clusters.append([structure])
        else:
            best_cluster.append(structure)

    return [cluster[0] for cluster in clusters]


def consensus_by_type(structures: list[Estructura], *, min_observers: int = 2) -> dict[StructureType, bool]:
    """Return whether each type has support from at least min_observers."""
    observers_by_type: dict[StructureType, set[str]] = {}
    for structure in structures:
        observers_by_type.setdefault(structure.tipo, set()).add(structure.observador)
    return {tipo: len(observers) >= min_observers for tipo, observers in observers_by_type.items()}


def dominant_type(structures: list[Estructura]) -> StructureType:
    """Return the most common emitted structure type."""
    if not structures:
        return "desconocido"
    counts = Counter(structure.tipo for structure in structures)
    return counts.most_common(1)[0][0]
