"""Bit-packed ECA engine for fast long runs."""

from __future__ import annotations

import numpy as np


def array_to_int(state: np.ndarray) -> int:
    """Pack a binary 1D state into a Python integer."""
    state = np.asarray(state, dtype=np.uint8).ravel()
    value = 0
    for i, bit in enumerate(state):
        if int(bit):
            value |= 1 << i
    return value


def int_to_array(value: int, width: int) -> np.ndarray:
    """Unpack a Python integer into a binary 1D state."""
    return np.array([(value >> i) & 1 for i in range(width)], dtype=np.uint8)


def _rot_left(value: int, width: int, mask: int) -> int:
    return ((value << 1) & mask) | (value >> (width - 1))


def _rot_right(value: int, width: int) -> int:
    return (value >> 1) | ((value & 1) << (width - 1))


def packed_step(state: int, rule: int, width: int) -> int:
    """Advance one ECA step on a bit-packed state."""
    if not 0 <= rule <= 255:
        raise ValueError("ECA rule must be in [0, 255]")
    if width <= 0:
        raise ValueError("width must be > 0")

    mask = (1 << width) - 1
    center = state & mask
    left = _rot_left(center, width, mask)
    right = _rot_right(center, width)

    next_state = 0
    not_left = (~left) & mask
    not_center = (~center) & mask
    not_right = (~right) & mask

    for pattern in range(8):
        if (rule >> pattern) & 1:
            left_match = left if (pattern & 4) else not_left
            center_match = center if (pattern & 2) else not_center
            right_match = right if (pattern & 1) else not_right
            next_state |= left_match & center_match & right_match
    return next_state & mask


def packed_step_rule110(state: int, width: int) -> int:
    """Specialized packed step for Rule 110."""
    if width <= 0:
        raise ValueError("width must be > 0")
    mask = (1 << width) - 1
    center = state & mask
    left = _rot_left(center, width, mask)
    right = _rot_right(center, width)
    not_left = (~left) & mask
    not_center = (~center) & mask
    not_right = (~right) & mask
    return ((not_left & center) | (not_center & right) | (left & center & not_right)) & mask


def run_packed(state: int, rule: int, width: int, steps: int) -> int:
    """Run many ECA steps and return only the final packed state."""
    current = state
    if rule == 110:
        for _ in range(steps):
            current = packed_step_rule110(current, width)
        return current
    for _ in range(steps):
        current = packed_step(current, rule, width)
    return current
