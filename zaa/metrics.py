"""Metrics for ECA space-time frames."""

from __future__ import annotations

import gzip
import math

import numpy as np


def shannon_entropy(frame: np.ndarray) -> float:
    """Binary Shannon entropy in bits for one frame."""
    values, counts = np.unique(np.asarray(frame, dtype=np.uint8), return_counts=True)
    total = counts.sum()
    if total == 0:
        return 0.0
    probs = counts.astype(np.float64) / total
    return float(-np.sum(probs * np.log2(probs)))


def gzip_compressibility(data: np.ndarray) -> float:
    """Compressed-size ratio using gzip as a Kolmogorov proxy."""
    raw = np.asarray(data, dtype=np.uint8).tobytes()
    if not raw:
        return 0.0
    return len(gzip.compress(raw, compresslevel=9)) / len(raw)


def temporal_mutual_information(a: np.ndarray, b: np.ndarray) -> float:
    """Mutual information in bits between two binary frames."""
    a = np.asarray(a, dtype=np.uint8).ravel()
    b = np.asarray(b, dtype=np.uint8).ravel()
    if a.shape != b.shape:
        raise ValueError("frames must have the same shape")

    joint = np.zeros((2, 2), dtype=np.float64)
    for x, y in zip(a, b, strict=True):
        joint[int(x), int(y)] += 1.0
    joint /= joint.sum()
    px = joint.sum(axis=1)
    py = joint.sum(axis=0)

    mi = 0.0
    for x in range(2):
        for y in range(2):
            pxy = joint[x, y]
            if pxy > 0 and px[x] > 0 and py[y] > 0:
                mi += pxy * math.log2(pxy / (px[x] * py[y]))
    return float(mi)


def active_transition_rate(frames: np.ndarray) -> float:
    """Mean fraction of cells that change between consecutive frames."""
    frames = np.asarray(frames, dtype=np.uint8)
    if frames.shape[0] < 2:
        return 0.0
    changes = frames[1:] != frames[:-1]
    return float(np.mean(changes))


def summarize_frames(frames: np.ndarray) -> dict[str, float]:
    """Compute the Fase 0a metrics for one simulated universe."""
    frames = np.asarray(frames, dtype=np.uint8)
    entropies = np.array([shannon_entropy(frame) for frame in frames], dtype=np.float64)
    if frames.shape[0] >= 2:
        mis = np.array(
            [temporal_mutual_information(frames[t], frames[t + 1]) for t in range(frames.shape[0] - 1)],
            dtype=np.float64,
        )
    else:
        mis = np.array([0.0], dtype=np.float64)

    return {
        "entropy_mean": float(np.mean(entropies)),
        "entropy_var": float(np.var(entropies)),
        "gzip_ratio": float(gzip_compressibility(frames)),
        "mutual_info_mean": float(np.mean(mis)),
        "density_mean": float(np.mean(frames)),
        "transition_rate": active_transition_rate(frames),
    }
