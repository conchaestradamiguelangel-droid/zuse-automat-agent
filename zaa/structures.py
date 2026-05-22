"""Common structure contract for observers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


StructureType = Literal["glider", "oscilador", "bloque", "desconocido"]
AssignmentMethod = Literal["plantilla", "velocidad_centroide", "periodicidad", "desplazamiento", "persistencia"]
Position = tuple[int, int, int]


@dataclass(frozen=True)
class Estructura:
    """Unified structure object emitted by all observers."""

    id: int
    tipo: StructureType
    tipo_asignado_por: AssignmentMethod
    posiciones: tuple[Position, ...]
    tamaño: int
    confianza: float
    observador: str

    def to_dict(self) -> dict:
        """Return a JSON-friendly representation."""
        return asdict(self)


def centroid_velocity(posiciones: tuple[Position, ...]) -> tuple[float, float]:
    """Estimate (vx, vy) from first and last positions."""
    if len(posiciones) < 2:
        return 0.0, 0.0
    t0, x0, y0 = posiciones[0]
    t1, x1, y1 = posiciones[-1]
    dt = t1 - t0
    if dt == 0:
        return 0.0, 0.0
    return (x1 - x0) / dt, (y1 - y0) / dt


def classify_track(posiciones: tuple[Position, ...], *, periodic: bool = False) -> tuple[StructureType, AssignmentMethod]:
    """Classify a synthetic 1D track by displacement and periodicity."""
    if periodic:
        return "oscilador", "periodicidad"
    if len(posiciones) < 2:
        return "desconocido", "persistencia"
    vx, vy = centroid_velocity(posiciones)
    if abs(vx) > 0.05 or abs(vy) > 0.05:
        return "glider", "velocidad_centroide"
    return "bloque", "desplazamiento"
