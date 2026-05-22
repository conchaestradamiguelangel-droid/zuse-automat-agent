"""Conway/Game-of-Life style 2D cellular automata."""

from __future__ import annotations

import numpy as np


def life_step(state: np.ndarray, *, birth: tuple[int, ...] = (3,), survive: tuple[int, ...] = (2, 3)) -> np.ndarray:
    """Advance one Life-like B/S step with periodic boundaries."""
    state = np.asarray(state, dtype=np.uint8)
    if state.ndim != 2:
        raise ValueError("state must be a 2D array")
    neighbors = np.zeros_like(state, dtype=np.uint8)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            neighbors += np.roll(np.roll(state, dy, axis=0), dx, axis=1)

    alive = state == 1
    born = (~alive) & np.isin(neighbors, birth)
    kept = alive & np.isin(neighbors, survive)
    return (born | kept).astype(np.uint8)


def simulate_life(initial_state: np.ndarray, steps: int) -> np.ndarray:
    """Return Life frames with shape (steps + 1, H, W), including t=0."""
    if steps < 0:
        raise ValueError("steps must be >= 0")
    state = np.asarray(initial_state, dtype=np.uint8)
    if state.ndim != 2:
        raise ValueError("initial_state must be a 2D array")
    frames = np.empty((steps + 1, *state.shape), dtype=np.uint8)
    frames[0] = state
    current = state
    for t in range(1, steps + 1):
        current = life_step(current)
        frames[t] = current
    return frames


def empty_grid(height: int = 32, width: int = 32) -> np.ndarray:
    """Create an empty Life grid."""
    if height <= 0 or width <= 0:
        raise ValueError("height and width must be > 0")
    return np.zeros((height, width), dtype=np.uint8)


def place_pattern(grid: np.ndarray, pattern: np.ndarray, *, y: int, x: int) -> np.ndarray:
    """Return a copy of grid with pattern placed at top-left (y, x)."""
    out = np.array(grid, dtype=np.uint8, copy=True)
    pattern = np.asarray(pattern, dtype=np.uint8)
    h, w = pattern.shape
    out[y : y + h, x : x + w] = pattern
    return out


def block_pattern() -> np.ndarray:
    return np.array([[1, 1], [1, 1]], dtype=np.uint8)


def blinker_pattern() -> np.ndarray:
    return np.array([[1, 1, 1]], dtype=np.uint8)


def glider_pattern() -> np.ndarray:
    return np.array([[0, 1, 0], [0, 0, 1], [1, 1, 1]], dtype=np.uint8)


def life_fixture(kind: str, *, height: int = 32, width: int = 32) -> np.ndarray:
    """Create a known Life initial condition: block, blinker, or glider."""
    grid = empty_grid(height, width)
    if kind == "block":
        return place_pattern(grid, block_pattern(), y=height // 2, x=width // 2)
    if kind == "blinker":
        return place_pattern(grid, blinker_pattern(), y=height // 2, x=width // 2 - 1)
    if kind == "glider":
        return place_pattern(grid, glider_pattern(), y=height // 4, x=width // 4)
    raise ValueError("kind must be one of: block, blinker, glider")
