"""Rule 110 fixture candidate generation.

The generated files are candidates, not validated fixtures. They must be
reviewed visually before being moved to fixtures/validated/.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np

from .eca import simulate
from .fixtures import save_fixture
from .visualize import save_frames_png


ETHER_F1_1 = "11111000100110"
SOURCE_REGULAR_LANGUAGE = (
    "Martinez, McIntosh, Seck Tuoh Mora, Chapa Vergara, "
    "Determining a regular language by glider-based structures called phases fi_1 in Rule 110, "
    "Journal of Cellular Automata 3(3), 231-270, 2008; "
    "phase strings mirrored at comunidad.escom.ipn.mx/genaro/rule110/listPhasesR110.txt"
)


@dataclass(frozen=True)
class Rule110FixtureSpec:
    """Source-level specification for one Rule 110 fixture candidate."""

    fixture_id: str
    nombre: str
    glider: str
    phase: str
    pattern: str
    period_t: int
    displacement_x: int
    width: int = 256
    steps: int = 96
    insert_at: int = 112
    seed: int = 20260523
    source: str = SOURCE_REGULAR_LANGUAGE
    auto_align: bool = True


FIXTURE_SPECS = (
    Rule110FixtureSpec("FIX-A", "Glider A candidate", "A", "f1_1", "111110", 3, 2),
    Rule110FixtureSpec("FIX-B", "Glider B candidate", "B", "f1_1", "11111010", 4, -2),
    Rule110FixtureSpec("FIX-C1", "Glider C1 candidate", "C1", "A,f1_1", "111110000", 7, 0),
)


def bits(text: str) -> np.ndarray:
    """Convert a string of 0/1 characters to uint8 bits."""
    if any(ch not in "01" for ch in text):
        raise ValueError("bit string must contain only 0 and 1")
    return np.array([int(ch) for ch in text], dtype=np.uint8)


def ether_state(width: int, *, phase_shift: int = 0) -> np.ndarray:
    """Create a finite periodic Rule 110 ether row."""
    ether = bits(ETHER_F1_1)
    tiled = np.resize(ether, width + len(ether))
    return tiled[phase_shift : phase_shift + width].astype(np.uint8)


def build_initial_condition(spec: Rule110FixtureSpec) -> np.ndarray:
    """Build a finite ether background with one glider phase string inserted."""
    ci = ether_state(spec.width)
    pattern = bits(spec.pattern)
    end = spec.insert_at + pattern.shape[0]
    if end > spec.width:
        raise ValueError("pattern does not fit in fixture width")
    ci[spec.insert_at:end] = pattern
    return ci


def align_candidate(spec: Rule110FixtureSpec) -> Rule110FixtureSpec:
    """Pick the insertion phase that maximizes difference from pure ether."""
    if not spec.auto_align:
        return spec
    best_diff = -1
    best_shift = 0
    for shift in range(len(ETHER_F1_1)):
        candidate = Rule110FixtureSpec(
            spec.fixture_id,
            spec.nombre,
            spec.glider,
            spec.phase,
            spec.pattern,
            spec.period_t,
            spec.displacement_x,
            width=spec.width,
            steps=spec.steps,
            insert_at=spec.insert_at + shift,
            seed=spec.seed,
            source=spec.source,
            auto_align=False,
        )
        frames = simulate(build_initial_condition(candidate), 110, spec.steps)
        diff = difference_from_ether(frames)
        if diff > best_diff:
            best_diff = diff
            best_shift = shift
    return Rule110FixtureSpec(
        spec.fixture_id,
        spec.nombre,
        spec.glider,
        spec.phase,
        spec.pattern,
        spec.period_t,
        spec.displacement_x,
        width=spec.width,
        steps=spec.steps,
        insert_at=spec.insert_at + best_shift,
        seed=spec.seed,
        source=spec.source,
        auto_align=False,
    )


def difference_from_ether(frames: np.ndarray) -> int:
    """Count cells differing from pure ether evolution with the same first row."""
    width = frames.shape[1]
    pure_ether = simulate(ether_state(width), 110, frames.shape[0] - 1)
    return int(np.count_nonzero(frames != pure_ether))


def expected_glider_metadata(spec: Rule110FixtureSpec) -> list[dict]:
    """Return expected metadata to be confirmed by visual validation."""
    kinematics = "moving"
    if spec.displacement_x == 0 and spec.period_t > 1:
        kinematics = "stationary_periodic"
    return [
        {
            "fixture_id": spec.fixture_id,
            "tipo": "glider",
            "kinematics": kinematics,
            "nombre": spec.glider,
            "phase": spec.phase,
            "period_t": spec.period_t,
            "displacement_x": spec.displacement_x,
            "velocity": spec.displacement_x / spec.period_t,
            "t_inicio": 0,
            "t_fin": spec.steps,
            "x_inicio": spec.insert_at,
            "fixture_status": "candidate_not_validated",
            "validation_status": "pending_human_visual_review",
        }
    ]


def generate_candidate(spec: Rule110FixtureSpec, output_dir: str | Path = "fixtures/pending") -> dict[str, Path]:
    """Generate one pending fixture NPZ and preview PNG."""
    original_insert_at = spec.insert_at
    spec = align_candidate(spec)
    out = Path(output_dir)
    ci = build_initial_condition(spec)
    frames = simulate(ci, 110, spec.steps)
    diff_cells = difference_from_ether(frames)
    npz_path = out / f"{spec.fixture_id}.npz"
    png_path = out / f"{spec.fixture_id}.png"
    save_fixture(
        npz_path,
        nombre=spec.nombre,
        fuente=spec.source,
        seed=spec.seed,
        ci=ci,
        frames_esperados=frames,
        gliders_esperados=expected_glider_metadata(spec),
    )
    # Store a sidecar text summary for quick human triage without loading NPZ.
    summary_path = out / f"{spec.fixture_id}.txt"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(
        "\n".join(
            [
                f"fixture_id={spec.fixture_id}",
                f"nombre={spec.nombre}",
                f"glider={spec.glider}",
                f"phase={spec.phase}",
                f"pattern={spec.pattern}",
                f"period_t={spec.period_t}",
                f"displacement_x={spec.displacement_x}",
                f"original_insert_at={original_insert_at}",
                f"chosen_insert_at={spec.insert_at}",
                f"difference_from_pure_ether_cells={diff_cells}",
                "status=candidate_not_validated",
                "next_step=human_visual_review_before_moving_to_fixtures/validated",
                "",
            ]
        ),
        encoding="utf-8",
    )
    save_frames_png(frames, png_path, scale=2)
    return {"npz": npz_path, "png": png_path, "summary": summary_path}


def generate_all_candidates(output_dir: str | Path = "fixtures/pending") -> list[dict[str, Path]]:
    """Generate all pending Rule 110 fixture candidates."""
    return [generate_candidate(spec, output_dir=output_dir) for spec in FIXTURE_SPECS]


def promote_candidate_to_validated(
    pending_path: str | Path,
    validated_dir: str | Path = "fixtures/validated",
    *,
    validation_status: str = "validated_computational",
) -> Path:
    """Promote one pending NPZ fixture to validated status.

    The pending NPZ is removed after the validated NPZ is written.
    """
    pending = Path(pending_path)
    validated = Path(validated_dir)
    validated.mkdir(parents=True, exist_ok=True)
    target = validated / pending.name

    with np.load(pending, allow_pickle=False) as data:
        ci = data["ci"].copy()
        frames = data["frames_esperados"].copy()
        metadata = json.loads(str(data["metadata_json"]))

    metadata["fixture_status"] = validation_status
    metadata["validation_status"] = validation_status
    for glider in metadata.get("gliders_esperados", []):
        glider["fixture_status"] = validation_status
        glider["validation_status"] = validation_status

    np.savez_compressed(
        target,
        ci=ci,
        frames_esperados=frames,
        metadata_json=json.dumps(metadata, sort_keys=True),
    )
    pending.unlink()
    return target


def promote_all_candidates(
    pending_dir: str | Path = "fixtures/pending",
    validated_dir: str | Path = "fixtures/validated",
) -> list[Path]:
    """Promote all pending Rule 110 fixture candidates to validated fixtures."""
    pending = Path(pending_dir)
    return [
        promote_candidate_to_validated(path, validated_dir=validated_dir)
        for path in sorted(pending.glob("FIX-*.npz"))
    ]


def normalize_validated_fixture_taxonomy(path: str | Path) -> Path:
    """Normalize validated fixture metadata after taxonomy decisions."""
    fixture = Path(path)
    with np.load(fixture, allow_pickle=False) as data:
        ci = data["ci"].copy()
        frames = data["frames_esperados"].copy()
        metadata = json.loads(str(data["metadata_json"]))

    for glider in metadata.get("gliders_esperados", []):
        displacement = glider.get("displacement_x", 0)
        period = glider.get("period_t", 1)
        glider["tipo"] = "glider"
        glider["kinematics"] = "stationary_periodic" if displacement == 0 and period > 1 else "moving"

    np.savez_compressed(
        fixture,
        ci=ci,
        frames_esperados=frames,
        metadata_json=json.dumps(metadata, sort_keys=True),
    )
    return fixture


def normalize_all_validated_fixture_taxonomy(validated_dir: str | Path = "fixtures/validated") -> list[Path]:
    """Normalize taxonomy metadata for all validated Rule 110 fixtures."""
    return [
        normalize_validated_fixture_taxonomy(path)
        for path in sorted(Path(validated_dir).glob("FIX-*.npz"))
    ]
