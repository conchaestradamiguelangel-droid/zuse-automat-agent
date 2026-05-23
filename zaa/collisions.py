"""Mechanical collision grammar for synthetic structures.

Fase 2b starts here as a controlled pipeline. These helpers do not infer real
Rule 110 collisions yet; they build and validate pre->post tables from known
synthetic events.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .fixtures import load_fixture
from .observers import observar_regiones_rule110


@dataclass(frozen=True)
class Collision:
    """A synthetic pre->post collision event."""

    tipo_a: str
    tipo_b: str
    resultado: str
    t: int
    x: int

    @property
    def key(self) -> tuple[str, str]:
        """Return an order-independent pair key."""
        return tuple(sorted((self.tipo_a, self.tipo_b)))


def synthetic_collisions(repetitions: int = 20) -> list[Collision]:
    """Generate controlled synthetic collision events with known outcomes."""
    if repetitions <= 0:
        raise ValueError("repetitions must be > 0")

    specs = [
        ("glider", "glider", "oscilador"),
        ("glider", "bloque", "glider"),
        ("oscilador", "glider", "bloque"),
        ("bloque", "bloque", "bloque"),
    ]
    events: list[Collision] = []
    for rep in range(repetitions):
        for idx, (tipo_a, tipo_b, resultado) in enumerate(specs):
            events.append(
                Collision(
                    tipo_a=tipo_a,
                    tipo_b=tipo_b,
                    resultado=resultado,
                    t=rep * 10 + idx,
                    x=32 + idx,
                )
            )
    return events


def collision_table(collisions: Iterable[Collision]) -> dict[tuple[str, str], Counter[str]]:
    """Group collisions by pair type and count post-collision outcomes."""
    table: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for collision in collisions:
        table[collision.key][collision.resultado] += 1
    return dict(table)


def dominant_results(table: dict[tuple[str, str], Counter[str]]) -> dict[tuple[str, str], tuple[str, int]]:
    """Return the dominant outcome and count for each pre-collision pair."""
    dominant: dict[tuple[str, str], tuple[str, int]] = {}
    for key, outcomes in table.items():
        result, count = outcomes.most_common(1)[0]
        dominant[key] = (result, count)
    return dominant


def consistency_table(table: dict[tuple[str, str], Counter[str]]) -> dict[tuple[str, str], float]:
    """Compute dominant-outcome frequency for each table entry."""
    consistency: dict[tuple[str, str], float] = {}
    for key, outcomes in table.items():
        total = sum(outcomes.values())
        if total == 0:
            consistency[key] = 0.0
            continue
        _, dominant_count = outcomes.most_common(1)[0]
        consistency[key] = dominant_count / total
    return consistency


def validate_consistency(
    table: dict[tuple[str, str], Counter[str]],
    *,
    threshold: float = 0.95,
) -> dict[tuple[str, str], bool]:
    """Validate table entries against a consistency threshold."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be in [0, 1]")
    return {
        key: value >= threshold
        for key, value in consistency_table(table).items()
    }


def _track_positions_by_time(structure) -> dict[int, int]:
    return {t: x for t, x, _ in structure.posiciones}


def detect_collision_candidates_rule110(frames, *, max_distance: int = 6) -> list[Collision]:
    """Detect candidate convergence events between coherent Rule 110 tracks."""
    structures = observar_regiones_rule110(frames)
    candidates: list[Collision] = []
    seen: set[tuple[int, int, int]] = set()
    for i, first in enumerate(structures):
        first_pos = _track_positions_by_time(first)
        for j, second in enumerate(structures[i + 1 :], start=i + 1):
            second_pos = _track_positions_by_time(second)
            common_times = sorted(set(first_pos) & set(second_pos))
            for t in common_times:
                distance = abs(first_pos[t] - second_pos[t])
                if distance <= max_distance:
                    key = (i, j, t)
                    if key in seen:
                        continue
                    seen.add(key)
                    candidates.append(
                        Collision(
                            tipo_a=first.tipo,
                            tipo_b=second.tipo,
                            resultado="candidato_pendiente",
                            t=t,
                            x=int(round((first_pos[t] + second_pos[t]) / 2)),
                        )
                    )
                    break
    return candidates


def run_collision_detection_rule110(fixtures_dir: str | Path = "fixtures/validated") -> dict:
    """Run Rule 110 collision-candidate detection over validated fixtures."""
    results: dict[str, list[Collision]] = {}
    total = 0
    for path in sorted(Path(fixtures_dir).glob("FIX-*.npz")):
        fixture = load_fixture(path)
        fixture_id = fixture["metadata"]["gliders_esperados"][0]["fixture_id"]
        collisions = detect_collision_candidates_rule110(fixture["frames_esperados"])
        results[fixture_id] = collisions
        total += len(collisions)
    report = {"fixtures": results, "total": total}
    if total == 0:
        report["gap"] = "sin_colisiones_en_fixtures_actuales"
    return report
