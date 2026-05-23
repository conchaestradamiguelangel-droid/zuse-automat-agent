"""Mechanical discovery loop for controlled worlds."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import json
from pathlib import Path

import numpy as np

from .consensus import consensus_by_type, dominant_type
from .eca import simulate, single_seed_initial_state
from .life2d import life_fixture, simulate_life
from .metrics import summarize_frames
from .observers import run_observers
from .observers2d import run_observers_2d
from .synthetic import moving_point, oscillator, static_block


@dataclass(frozen=True)
class DiscoveryConfig:
    """Configuration for one controlled discovery loop."""

    world_type: str
    steps: int = 24
    width: int = 64
    height: int = 32
    seed: int = 20260523
    cycles: int = 5


def build_world(config: DiscoveryConfig) -> np.ndarray:
    """Build frames for a controlled world."""
    if config.world_type == "synthetic_glider":
        return moving_point(steps=config.steps + 1, width=config.width)
    if config.world_type == "synthetic_oscilador":
        return oscillator(steps=config.steps + 1, width=config.width)
    if config.world_type == "synthetic_bloque":
        return static_block(steps=config.steps + 1, width=config.width)
    if config.world_type == "life_glider":
        return simulate_life(life_fixture("glider", height=config.height, width=config.width), config.steps)
    if config.world_type == "life_blinker":
        return simulate_life(life_fixture("blinker", height=config.height, width=config.width), config.steps)
    if config.world_type == "life_block":
        return simulate_life(life_fixture("block", height=config.height, width=config.width), config.steps)
    if config.world_type.startswith("rule_"):
        rule = int(config.world_type.removeprefix("rule_"))
        return simulate(single_seed_initial_state(config.width), rule, config.steps)
    raise ValueError(f"unknown world_type: {config.world_type}")


def _serializable_consensus(consensus: dict) -> dict[str, bool]:
    return {str(key): bool(value) for key, value in consensus.items()}


def run_cycle(config: DiscoveryConfig, cycle_id: int) -> dict:
    """Run one mechanical discovery cycle."""
    frames = build_world(config)
    if frames.ndim == 2:
        structures = run_observers(frames)
        metric_frames = frames
    elif frames.ndim == 3:
        structures = run_observers_2d(frames)
        metric_frames = frames[:, 0, :]
    else:
        raise ValueError("frames must be 2D or 3D")

    consensus = consensus_by_type(structures)
    return {
        "cycle_id": cycle_id,
        "world_type": config.world_type,
        "steps": config.steps,
        "width": config.width,
        "structure_count": len(structures),
        "dominant_type": dominant_type(structures),
        "consensus": _serializable_consensus(consensus),
        "metrics": summarize_frames(metric_frames),
        "timestamp": datetime.now(UTC).isoformat(),
    }


def run_discovery_loop(config: DiscoveryConfig) -> list[dict]:
    """Run N discovery cycles."""
    if config.cycles <= 0:
        raise ValueError("cycles must be > 0")
    return [run_cycle(config, cycle_id) for cycle_id in range(config.cycles)]


def save_journal(results: list[dict], path: str | Path) -> Path:
    """Append discovery results as JSONL."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result, sort_keys=True) + "\n")
    return output
