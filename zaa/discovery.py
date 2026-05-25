"""Mechanical discovery loop for controlled worlds."""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
import json
from pathlib import Path

import numpy as np

from .consensus import consensus_by_type, deduplicate_structures, dominant_type
from .cycle_laws import evaluate_cycle_laws
from .eca import simulate, single_seed_initial_state
from .history import WorldRecord, load_agent_state, save_agent_state, update_history
from .life2d import life_fixture, simulate_life
from .metrics import summarize_frames
from .observers import run_observers
from .observers2d import run_observers_2d
from .policy import PolicyState, compute_score, decide
from .synthetic import moving_point, oscillator, static_block


DEDUP_STRUCTURE_NOISE_THRESHOLD = 40


@dataclass(frozen=True)
class DiscoveryConfig:
    """Configuration for one controlled discovery loop."""

    world_type: str
    steps: int = 24
    width: int = 64
    height: int = 32
    seed: int = 20260523
    cycles: int = 5
    state_file: str | None = None


def build_world(config: DiscoveryConfig, cycle_seed: int | None = None) -> np.ndarray:
    """Build frames for a controlled world."""
    if cycle_seed is None:
        cycle_seed = config.seed
    if config.world_type == "synthetic_glider":
        start = (cycle_seed % (config.width // 2)) + 4
        velocity = 1 + (cycle_seed % 2)
        frames = moving_point(steps=config.steps + 1, width=config.width, start=start, velocity=velocity)
        if cycle_seed % 2:
            frames |= moving_point(
                steps=config.steps + 1,
                width=config.width,
                start=(start + 7) % config.width,
                velocity=velocity,
            )
        return frames
    if config.world_type == "synthetic_oscilador":
        center = (cycle_seed % (config.width - 8)) + 4
        return oscillator(steps=config.steps + 1, width=config.width, center=center)
    if config.world_type == "synthetic_bloque":
        start = (cycle_seed % (config.width // 2)) + 4
        return static_block(steps=config.steps + 1, width=config.width, start=start)
    if config.world_type == "life_glider":
        return simulate_life(life_fixture("glider", height=config.height, width=config.width), config.steps)
    if config.world_type == "life_blinker":
        return simulate_life(life_fixture("blinker", height=config.height, width=config.width), config.steps)
    if config.world_type == "life_block":
        return simulate_life(life_fixture("block", height=config.height, width=config.width), config.steps)
    if config.world_type.startswith("rule_"):
        rule = int(config.world_type.removeprefix("rule_"))
        from .eca import random_initial_state

        return simulate(random_initial_state(config.width, seed=cycle_seed), rule, config.steps)
    raise ValueError(f"unknown world_type: {config.world_type}")


def _serializable_consensus(consensus: dict) -> dict[str, bool]:
    return {str(key): bool(value) for key, value in consensus.items()}


def run_cycle(config: DiscoveryConfig, cycle_id: int) -> dict:
    """Run one mechanical discovery cycle."""
    cycle_seed = config.seed + cycle_id
    frames = build_world(config, cycle_seed)
    if frames.ndim == 2:
        structures = run_observers(frames)
        metric_frames = frames
    elif frames.ndim == 3:
        structures = run_observers_2d(frames)
        metric_frames = frames.reshape(frames.shape[0], -1)
    else:
        raise ValueError("frames must be 2D or 3D")

    structure_count = len(structures)
    deduplicated_structures = deduplicate_structures(structures)
    dedup_structure_count = len(deduplicated_structures)
    consensus = consensus_by_type(structures)
    analysis_status = "ruido_no_analizable" if dedup_structure_count > DEDUP_STRUCTURE_NOISE_THRESHOLD else "ok"
    if analysis_status == "ok":
        law_report = evaluate_cycle_laws(structures, frames, config.steps)
    else:
        law_report = {
            "laws_evaluated": [],
            "laws_accepted": [],
            "laws_rejected": [],
            "laws_status": "skipped_noise",
            "details": [],
        }
    return {
        "cycle_id": cycle_id,
        "world_type": config.world_type,
        "steps": config.steps,
        "width": config.width,
        "structure_count": structure_count,
        "dedup_structure_count": dedup_structure_count,
        "inflation_ratio": structure_count / max(1, dedup_structure_count),
        "dominant_type": dominant_type(structures),
        "analysis_status": analysis_status,
        "consensus": _serializable_consensus(consensus),
        "metrics": summarize_frames(metric_frames),
        "timestamp": datetime.now(UTC).isoformat(),
        **law_report,
    }


def run_discovery_loop(config: DiscoveryConfig) -> list[dict]:
    """Run N autonomous discovery cycles."""
    if config.cycles <= 0:
        raise ValueError("cycles must be > 0")

    current_world = config.world_type
    current_steps = config.steps
    current_seed = config.seed
    repeats_in_current_world = 0
    scale_attempts_in_current_world = 0
    prev_dominant = None
    prev_score = 0.0
    results: list[dict] = []
    world_steps: dict[str, int] = {}
    state_path = Path(config.state_file) if config.state_file else None
    if state_path and state_path.exists() and state_path.stat().st_size > 0:
        world_history, seen_law_signatures = load_agent_state(state_path)
    else:
        world_history: dict[str, WorldRecord] = {}
        seen_law_signatures: set[tuple[str, ...]] = set()

    for cycle_id in range(config.cycles):
        cycle_config = DiscoveryConfig(
            world_type=current_world,
            steps=current_steps,
            width=config.width,
            height=config.height,
            seed=current_seed,
            cycles=config.cycles,
            state_file=config.state_file,
        )
        result = run_cycle(cycle_config, cycle_id)

        law_signature = tuple(sorted(result["laws_accepted"]))
        is_new_law_signature = (
            result["analysis_status"] == "ok"
            and law_signature not in seen_law_signatures
        )

        record_prev = world_history.get(current_world)
        world_visit_count = record_prev.visit_count if record_prev is not None else 0
        world_avg_score_prev = record_prev.avg_score if record_prev is not None else 0.0

        policy_state = PolicyState(
            world_type=current_world,
            analysis_status=result["analysis_status"],
            structure_count=result["structure_count"],
            laws_accepted=result["laws_accepted"],
            dominant_type=result["dominant_type"],
            steps=current_steps,
            seed=current_seed,
            repeats_in_current_world=repeats_in_current_world,
            is_new_law_signature=is_new_law_signature,
        )

        score = compute_score(policy_state, prev_dominant)
        update_history(
            world_history,
            current_world,
            score,
            result["analysis_status"],
            law_signature,
            current_steps,
            config.width,
        )
        if result["analysis_status"] == "ok":
            seen_law_signatures.add(law_signature)

        decision = decide(
            replace(policy_state, score=score),
            prev_dominant,
            prev_score,
            world_record=world_history.get(current_world),
        )
        result["action_taken"] = decision.action
        result["action_reason"] = decision.reason
        result["score"] = decision.score
        result["world_visit_count"] = world_visit_count
        result["world_avg_score_prev"] = world_avg_score_prev
        result["law_signature"] = list(law_signature)
        result["is_new_law_signature"] = is_new_law_signature
        result["scale_attempt_count"] = scale_attempts_in_current_world
        results.append(result)

        prev_dominant = result["dominant_type"]
        prev_score = decision.score
        if decision.next_world != current_world:
            scale_attempts_in_current_world = 0
        elif decision.reason == "firma_conocida_buscar_escala":
            scale_attempts_in_current_world += 1
        repeats_in_current_world = repeats_in_current_world + 1 if decision.action == "repeat_vary_seed" else 0
        world_steps[current_world] = decision.next_steps if decision.next_world == current_world else current_steps
        if decision.next_world != current_world:
            restored = world_steps.get(decision.next_world, config.steps)
            next_record = world_history.get(decision.next_world)
            if next_record is not None and next_record.first_noise_steps > 0:
                restored = min(restored, next_record.first_noise_steps - 1)
            current_steps = restored
        else:
            current_steps = decision.next_steps
        current_world = decision.next_world
        current_seed = decision.next_seed

    if config.state_file:
        save_agent_state(world_history, seen_law_signatures, config.state_file)
    return results


def save_journal(results: list[dict], path: str | Path) -> Path:
    """Append discovery results as JSONL."""
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        for result in results:
            handle.write(json.dumps(result, sort_keys=True) + "\n")
    return output
