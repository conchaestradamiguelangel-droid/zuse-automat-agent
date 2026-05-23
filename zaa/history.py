"""Per-world history for the autonomous discovery loop."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class WorldRecord:
    """Accumulated observations for one world type within a run."""

    visit_count: int = 0
    scores: list[float] = field(default_factory=list)
    noise_count: int = 0

    @property
    def avg_score(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

    @property
    def noise_fraction(self) -> float:
        return self.noise_count / self.visit_count if self.visit_count > 0 else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "visit_count": self.visit_count,
            "avg_score": self.avg_score,
            "noise_fraction": self.noise_fraction,
            "scores": list(self.scores),
        }


def update_history(
    history: dict[str, WorldRecord],
    world_type: str,
    score: float,
    analysis_status: str,
) -> None:
    """Update history for one world after observing a cycle."""
    if world_type not in history:
        history[world_type] = WorldRecord()
    record = history[world_type]
    record.visit_count += 1
    record.scores.append(score)
    if analysis_status == "ruido_no_analizable":
        record.noise_count += 1
