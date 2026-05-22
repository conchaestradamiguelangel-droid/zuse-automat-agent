"""PNG visualization for binary space-time frames."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image


def save_frames_png(frames: np.ndarray, path: str | Path, scale: int = 2) -> Path:
    """Save frames as a black/white PNG image."""
    frames = np.asarray(frames, dtype=np.uint8)
    if frames.ndim != 2:
        raise ValueError("frames must have shape (T, W)")
    if scale <= 0:
        raise ValueError("scale must be > 0")

    pixels = (255 - frames * 255).astype(np.uint8)
    image = Image.fromarray(pixels, mode="L")
    if scale != 1:
        image = image.resize((frames.shape[1] * scale, frames.shape[0] * scale), Image.Resampling.NEAREST)

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)
    return output
