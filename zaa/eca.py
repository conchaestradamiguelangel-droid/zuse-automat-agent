"""Elementary cellular automata engine."""

from __future__ import annotations

import numpy as np


def rule_bits(rule: int) -> np.ndarray:
    """Return the 8-bit lookup table for an elementary CA rule."""
    if not 0 <= rule <= 255:
        raise ValueError("ECA rule must be in [0, 255]")
    return np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)


def step(state: np.ndarray, rule: int) -> np.ndarray:
    """Advance one ECA step with periodic boundary conditions."""
    state = np.asarray(state, dtype=np.uint8)
    if state.ndim != 1:
        raise ValueError("state must be a 1D array")
    return step_with_bits(state, rule_bits(rule))


def step_with_bits(state: np.ndarray, bits: np.ndarray) -> np.ndarray:
    """Advance one ECA step with a precomputed 8-bit lookup table."""
    state = np.asarray(state, dtype=np.uint8)
    bits = np.asarray(bits, dtype=np.uint8)
    if state.ndim != 1:
        raise ValueError("state must be a 1D array")
    if bits.shape != (8,):
        raise ValueError("bits must have shape (8,)")
    left = np.roll(state, 1)
    right = np.roll(state, -1)
    idx = (left << 2) | (state << 1) | right
    return bits[idx]


def simulate(initial_state: np.ndarray, rule: int, steps: int) -> np.ndarray:
    """Return frames with shape (steps + 1, width), including t=0."""
    if steps < 0:
        raise ValueError("steps must be >= 0")
    state = np.asarray(initial_state, dtype=np.uint8)
    if state.ndim != 1:
        raise ValueError("initial_state must be a 1D array")

    frames = np.empty((steps + 1, state.size), dtype=np.uint8)
    frames[0] = state
    current = state
    bits = rule_bits(rule)
    for t in range(1, steps + 1):
        current = step_with_bits(current, bits)
        frames[t] = current
    return frames


def random_initial_state(width: int, seed: int | None = None, density: float = 0.5) -> np.ndarray:
    """Create a reproducible random binary initial condition."""
    if width <= 0:
        raise ValueError("width must be > 0")
    if not 0.0 <= density <= 1.0:
        raise ValueError("density must be in [0, 1]")
    rng = np.random.default_rng(seed)
    return (rng.random(width) < density).astype(np.uint8)


def single_seed_initial_state(width: int, index: int | None = None) -> np.ndarray:
    """Create a deterministic single active-cell initial condition."""
    if width <= 0:
        raise ValueError("width must be > 0")
    if index is None:
        index = width // 2
    state = np.zeros(width, dtype=np.uint8)
    state[index % width] = 1
    return state
