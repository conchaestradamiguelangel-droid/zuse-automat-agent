"""Transparent heuristic policy for autonomous exploration."""

from __future__ import annotations

from dataclasses import dataclass

from .history import WorldRecord


WORLD_SEQUENCE = [
    "synthetic_glider",
    "synthetic_oscilador",
    "synthetic_bloque",
    "life_glider",
    "life_blinker",
    "life_block",
    "rule_30",
    "rule_110",
    "rule_124",
    "rule_109",
    "rule_137",
    "rule_54",
]
BLOCKED_WORLDS = ["rule110_real"]
MAX_STEPS_DEFAULT = 400
MAX_REPEATS_DEFAULT = 1


@dataclass(frozen=True)
class PolicyState:
    """State visible to the heuristic policy."""

    world_type: str
    analysis_status: str
    structure_count: int
    laws_accepted: list[str]
    dominant_type: str
    steps: int
    seed: int
    repeats_in_current_world: int
    is_new_law_signature: bool = False
    score: float | None = None


@dataclass(frozen=True)
class PolicyDecision:
    """One transparent policy decision."""

    action: str
    next_world: str
    next_steps: int
    next_seed: int
    reason: str
    score: float


def _next_world(current: str) -> str:
    """Return next world in the fixed exploration sequence."""
    if current not in WORLD_SEQUENCE:
        return WORLD_SEQUENCE[0]
    idx = WORLD_SEQUENCE.index(current)
    return WORLD_SEQUENCE[(idx + 1) % len(WORLD_SEQUENCE)]


def compute_score(state: PolicyState, prev_dominant: str | None) -> float:
    """Compute logging-only score for the previous cycle."""
    score = float(len(state.laws_accepted))
    if state.analysis_status == "ruido_no_analizable":
        score -= 1.0
    if prev_dominant is not None and state.dominant_type != prev_dominant:
        score += 0.5
    return score


def _would_hit_noise_boundary(proposed_steps: int, world_record: WorldRecord | None) -> bool:
    """Return True if proposed_steps would hit or exceed the known noise boundary."""
    return (
        world_record is not None
        and world_record.first_noise_steps > 0
        and proposed_steps >= world_record.first_noise_steps
    )


def decide(
    state: PolicyState,
    prev_dominant: str | None = None,
    prev_score: float = 0.0,
    max_steps: int = MAX_STEPS_DEFAULT,
    max_repeats: int = MAX_REPEATS_DEFAULT,
    world_record: WorldRecord | None = None,
) -> PolicyDecision:
    """Choose the next exploration action using explicit if/else rules."""
    score = compute_score(state, prev_dominant) if state.score is None else state.score

    if state.world_type in BLOCKED_WORLDS:
        return PolicyDecision(
            "skip_rule110_real",
            _next_world(state.world_type),
            state.steps,
            state.seed,
            "world_bloqueado",
            score,
        )

    if (
        world_record is not None
        and world_record.noise_fraction >= 0.75
        and world_record.visit_count >= 2
    ):
        return PolicyDecision(
            "change_world",
            _next_world(state.world_type),
            state.steps,
            state.seed,
            "mundo_consistentemente_ruidoso",
            score,
        )

    if state.analysis_status == "ruido_no_analizable":
        return PolicyDecision(
            "change_world",
            _next_world(state.world_type),
            state.steps,
            state.seed,
            "ruido_no_analizable",
            score,
        )

    if state.structure_count == 0:
        if state.steps < max_steps:
            proposed = min(state.steps * 2, max_steps)
            if _would_hit_noise_boundary(proposed, world_record):
                return PolicyDecision(
                    "change_world",
                    _next_world(state.world_type),
                    state.steps,
                    state.seed,
                    "noise_boundary_alcanzado",
                    score,
                )
            return PolicyDecision(
                "increase_steps",
                state.world_type,
                proposed,
                state.seed,
                "sin_estructuras_aumentar_steps",
                score,
            )
        return PolicyDecision(
            "change_world",
            _next_world(state.world_type),
            state.steps,
            state.seed,
            "sin_estructuras_max_steps_alcanzado",
            score,
        )

    if state.is_new_law_signature and state.repeats_in_current_world < max_repeats:
        return PolicyDecision(
            "repeat_vary_seed",
            state.world_type,
            state.steps,
            state.seed + 1,
            "firma_leyes_nueva_explorar_mas",
            score,
        )

    if (
        not state.is_new_law_signature
        and len(state.laws_accepted) >= 2
        and state.repeats_in_current_world == 0
        and state.steps < max_steps
    ):
        proposed = min(state.steps * 2, max_steps)
        if _would_hit_noise_boundary(proposed, world_record):
            return PolicyDecision(
                "change_world",
                _next_world(state.world_type),
                state.steps,
                state.seed,
                "noise_boundary_alcanzado",
                score,
            )
        return PolicyDecision(
            "increase_steps",
            state.world_type,
            proposed,
            state.seed,
            "firma_conocida_buscar_escala",
            score,
        )

    if (
        len(state.laws_accepted) >= 2
        and state.repeats_in_current_world < max_repeats
        and score > prev_score
    ):
        return PolicyDecision(
            "repeat_vary_seed",
            state.world_type,
            state.steps,
            state.seed + 1,
            "leyes_aceptadas_explorar_mas",
            score,
        )

    if len(state.laws_accepted) < 2 and state.steps < max_steps:
        proposed = min(state.steps * 2, max_steps)
        if _would_hit_noise_boundary(proposed, world_record):
            return PolicyDecision(
                "change_world",
                _next_world(state.world_type),
                state.steps,
                state.seed,
                "noise_boundary_alcanzado",
                score,
            )
        return PolicyDecision(
            "increase_steps",
            state.world_type,
            proposed,
            state.seed,
            "pocas_leyes_aumentar_steps",
            score,
        )

    return PolicyDecision(
        "change_world",
        _next_world(state.world_type),
        state.steps,
        state.seed,
        "max_repeats_o_max_steps_alcanzado",
        score,
    )
