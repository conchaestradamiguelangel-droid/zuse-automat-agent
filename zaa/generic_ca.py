"""Generic 1D cellular automata engine.

This module supports local lookup tables and Python callables for k-state,
radius-r one-dimensional cellular automata. It intentionally does not enumerate
rule spaces.
"""

from __future__ import annotations

from collections.abc import Callable

import numpy as np


LocalRule = Callable[[np.ndarray], int]


def table_size(states: int, radius: int) -> int:
    """Return the number of local neighborhoods for k states and radius r."""
    if states < 2:
        raise ValueError("states must be >= 2")
    if radius < 0:
        raise ValueError("radius must be >= 0")
    return states ** (2 * radius + 1)


def neighborhood_indices(state: np.ndarray, states: int, radius: int) -> np.ndarray:
    """Compute base-k neighborhood indices with leftmost cell as most significant."""
    state = np.asarray(state, dtype=np.int64)
    if state.ndim != 1:
        raise ValueError("state must be a 1D array")
    if np.any(state < 0) or np.any(state >= states):
        raise ValueError("state contains values outside [0, states)")

    idx = np.zeros(state.shape[0], dtype=np.int64)
    for offset in range(-radius, radius + 1):
        idx *= states
        idx += np.roll(state, -offset)
    return idx


def step_table(state: np.ndarray, table: np.ndarray, *, states: int, radius: int) -> np.ndarray:
    """Advance one step using a local lookup table."""
    state = np.asarray(state, dtype=np.int64)
    table = np.asarray(table, dtype=np.int64)
    expected = table_size(states, radius)
    if table.shape != (expected,):
        raise ValueError(f"table must have shape ({expected},)")
    if np.any(table < 0) or np.any(table >= states):
        raise ValueError("table contains values outside [0, states)")

    idx = neighborhood_indices(state, states, radius)
    return table[idx].astype(np.uint8)


def step_callable(state: np.ndarray, rule: LocalRule, *, states: int, radius: int) -> np.ndarray:
    """Advance one step using a Python callable local rule."""
    state = np.asarray(state, dtype=np.uint8)
    if state.ndim != 1:
        raise ValueError("state must be a 1D array")
    if np.any(state >= states):
        raise ValueError("state contains values outside [0, states)")

    width = state.shape[0]
    out = np.empty(width, dtype=np.uint8)
    for x in range(width):
        neighborhood = np.array([state[(x + offset) % width] for offset in range(-radius, radius + 1)], dtype=np.uint8)
        value = int(rule(neighborhood))
        if value < 0 or value >= states:
            raise ValueError("callable rule returned a value outside [0, states)")
        out[x] = value
    return out


def simulate_table(initial_state: np.ndarray, table: np.ndarray, *, states: int, radius: int, steps: int) -> np.ndarray:
    """Simulate a generic 1D CA with a lookup table."""
    if steps < 0:
        raise ValueError("steps must be >= 0")
    state = np.asarray(initial_state, dtype=np.uint8)
    frames = np.empty((steps + 1, state.shape[0]), dtype=np.uint8)
    frames[0] = state
    current = state
    for t in range(1, steps + 1):
        current = step_table(current, table, states=states, radius=radius)
        frames[t] = current
    return frames


def simulate_callable(initial_state: np.ndarray, rule: LocalRule, *, states: int, radius: int, steps: int) -> np.ndarray:
    """Simulate a generic 1D CA with a Python callable local rule."""
    if steps < 0:
        raise ValueError("steps must be >= 0")
    state = np.asarray(initial_state, dtype=np.uint8)
    frames = np.empty((steps + 1, state.shape[0]), dtype=np.uint8)
    frames[0] = state
    current = state
    for t in range(1, steps + 1):
        current = step_callable(current, rule, states=states, radius=radius)
        frames[t] = current
    return frames


def eca_rule_table(rule: int) -> np.ndarray:
    """Return a generic lookup table equivalent to an elementary CA rule."""
    if not 0 <= rule <= 255:
        raise ValueError("ECA rule must be in [0, 255]")
    return np.array([(rule >> i) & 1 for i in range(8)], dtype=np.uint8)
