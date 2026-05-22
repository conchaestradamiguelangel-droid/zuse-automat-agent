"""Synthetic 1D frames for observer development."""

from __future__ import annotations

import numpy as np


def moving_point(*, steps: int = 24, width: int = 64, start: int = 8, velocity: int = 1) -> np.ndarray:
    """Return frames with one active cell moving at constant integer velocity."""
    frames = np.zeros((steps, width), dtype=np.uint8)
    for t in range(steps):
        frames[t, (start + velocity * t) % width] = 1
    return frames


def static_block(*, steps: int = 24, width: int = 64, start: int = 24, size: int = 4) -> np.ndarray:
    """Return frames with a persistent static active block."""
    frames = np.zeros((steps, width), dtype=np.uint8)
    for t in range(steps):
        for dx in range(size):
            frames[t, (start + dx) % width] = 1
    return frames


def oscillator(*, steps: int = 24, width: int = 64, center: int = 32) -> np.ndarray:
    """Return frames with a local period-2 oscillator."""
    frames = np.zeros((steps, width), dtype=np.uint8)
    for t in range(steps):
        if t % 2 == 0:
            frames[t, center - 1] = 1
            frames[t, center + 1] = 1
        else:
            frames[t, center] = 1
    return frames
