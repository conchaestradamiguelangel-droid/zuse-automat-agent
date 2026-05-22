"""Observer consensus utilities."""

from __future__ import annotations

from collections import Counter

from .structures import Estructura, StructureType


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
