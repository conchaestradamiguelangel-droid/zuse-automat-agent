"""Per-world history for the autonomous discovery loop."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass
class WorldRecord:
    """Accumulated observations for one world type within a run."""

    visit_count: int = 0
    scores: list[float] = field(default_factory=list)
    noise_count: int = 0
    law_signatures: list[frozenset[str]] = field(default_factory=list)
    params_tried: list[tuple[int, int, tuple[str, ...]]] = field(default_factory=list)
    max_ok_steps: int = 0
    first_noise_steps: int = 0
    peak_signature_diversity: float = 0.0
    has_multiregime_evidence: bool = False

    @property
    def avg_score(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

    @property
    def noise_fraction(self) -> float:
        return self.noise_count / self.visit_count if self.visit_count > 0 else 0.0

    @property
    def unique_law_signature_count(self) -> int:
        return len({sig for sig in self.law_signatures if sig})

    @property
    def non_empty_signature_visit_count(self) -> int:
        return sum(1 for sig in self.law_signatures if sig)

    @property
    def law_signature_diversity(self) -> float | None:
        non_empty_visits = self.non_empty_signature_visit_count
        if non_empty_visits < 5:
            return None
        return self.unique_law_signature_count / non_empty_visits

    @property
    def score_variance(self) -> float | None:
        if len(self.scores) < 2:
            return None
        avg = self.avg_score
        return sum((score - avg) ** 2 for score in self.scores) / len(self.scores)

    @property
    def is_multiregime_candidate(self) -> bool:
        diversity = self.law_signature_diversity
        return (
            diversity is not None
            and diversity > 0.5
            and self.noise_fraction < 0.20
            and self.non_empty_signature_visit_count >= 5
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "visit_count": self.visit_count,
            "scores": list(self.scores),
            "noise_count": self.noise_count,
            "law_signatures": [sorted(sig) for sig in self.law_signatures],
            "avg_score": self.avg_score,
            "noise_fraction": self.noise_fraction,
            "unique_law_signature_count": self.unique_law_signature_count,
            "non_empty_signature_visit_count": self.non_empty_signature_visit_count,
            "law_signature_diversity": self.law_signature_diversity,
            "score_variance": self.score_variance,
            "is_multiregime_candidate": self.is_multiregime_candidate,
            "peak_signature_diversity": self.peak_signature_diversity,
            "has_multiregime_evidence": self.has_multiregime_evidence,
            "params_tried": [(p[0], p[1], list(p[2])) for p in self.params_tried],
            "max_ok_steps": self.max_ok_steps,
            "first_noise_steps": self.first_noise_steps,
        }


def update_history(
    history: dict[str, WorldRecord],
    world_type: str,
    score: float,
    analysis_status: str,
    law_signature: tuple[str, ...] = (),
    steps: int = 0,
    width: int = 0,
) -> None:
    """Update history for one world after observing a cycle."""
    if world_type not in history:
        history[world_type] = WorldRecord()
    record = history[world_type]
    record.visit_count += 1
    record.scores.append(score)
    if analysis_status == "ok":
        record.max_ok_steps = max(record.max_ok_steps, steps)
    if analysis_status == "ruido_no_analizable":
        record.noise_count += 1
        if record.first_noise_steps == 0 or steps < record.first_noise_steps:
            record.first_noise_steps = steps
    record.law_signatures.append(frozenset(law_signature))
    record.params_tried.append((steps, width, law_signature))
    diversity = record.law_signature_diversity
    if diversity is not None and record.noise_fraction < 0.20:
        record.peak_signature_diversity = max(record.peak_signature_diversity, diversity)
        if record.peak_signature_diversity > 0.5:
            record.has_multiregime_evidence = True


def save_agent_state(
    world_history: dict[str, WorldRecord],
    seen_law_signatures: set[tuple[str, ...]],
    path: str | Path,
) -> Path:
    """Persist world history and known signatures to JSON."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    state = {
        "schema_version": 1,
        "seen_law_signatures": sorted([list(sig) for sig in seen_law_signatures]),
        "world_history": {wt: record.to_dict() for wt, record in world_history.items()},
    }
    output.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return output


def load_agent_state(
    path: str | Path,
) -> tuple[dict[str, WorldRecord], set[tuple[str, ...]]]:
    """Load world history and known signatures from JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    seen_law_signatures = {tuple(sig) for sig in data.get("seen_law_signatures", [])}
    world_history: dict[str, WorldRecord] = {}
    for wt, rd in data.get("world_history", {}).items():
        world_history[wt] = WorldRecord(
            visit_count=rd["visit_count"],
            scores=list(rd["scores"]),
            noise_count=rd.get("noise_count", 0),
            law_signatures=[frozenset(sig) for sig in rd.get("law_signatures", [])],
            params_tried=[
                (p[0], p[1], tuple(p[2])) for p in rd.get("params_tried", [])
            ],
            max_ok_steps=rd.get("max_ok_steps", 0),
            first_noise_steps=rd.get("first_noise_steps", 0),
            peak_signature_diversity=rd.get("peak_signature_diversity", 0.0),
            has_multiregime_evidence=rd.get("has_multiregime_evidence", False),
        )
    return world_history, seen_law_signatures
