"""Rule 110 ether utilities."""

from __future__ import annotations

import numpy as np

from .eca import simulate
from .rule110_fixtures import ether_state


def pure_ether_frames(width: int, steps: int) -> np.ndarray:
    """Simulate pure Rule 110 ether for a finite periodic universe."""
    if width <= 0:
        raise ValueError("width must be > 0")
    if steps < 0:
        raise ValueError("steps must be >= 0")
    return simulate(ether_state(width), 110, steps)


def diff_from_pure_ether(frames: np.ndarray) -> np.ndarray:
    """Return binary defect frames: cells differing from pure ether evolution."""
    frames = np.asarray(frames, dtype=np.uint8)
    if frames.ndim != 2:
        raise ValueError("Rule 110 frames must have shape (T, W)")
    ether = pure_ether_frames(frames.shape[1], frames.shape[0] - 1)
    return (frames != ether).astype(np.uint8)


def defect_activity_ratio(frames: np.ndarray) -> float:
    """Fraction of active cells in the ether-difference representation."""
    defect = diff_from_pure_ether(frames)
    return float(np.mean(defect))
