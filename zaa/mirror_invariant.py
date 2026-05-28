"""Fase 6a/6b - mirror-invariant observer diagnostic.

Purpose: measure how much tipo_unico changes when a 1D CA initial
condition is reflected left-right. Reflection is a symmetry of the
integer lattice, and maps some ECA rules to exact mirror rules
(for example Rule 110 <-> Rule 124).

Conclusion after Fase 6b: tipo_unico in the production pipeline is an
observer-dependent exploratory signal, not a mirror-invariant physical
property. Linreg classification, Hungarian assignment, and local
velocity-predicted tracking were tested diagnostically and rejected:
they degraded other worlds more than they fixed rule_137.

This module is DIAGNOSTIC ONLY. Do not integrate variants into the
production pipeline without revalidating the full 7-law map.

Public API
----------
mirror_state(state)                    flip a 1D state
classify_track_linreg(pos, periodic)   linear-regression velocity variant
observar_regiones_rule110_linreg(f)    drop-in replacement that uses linreg
tipo_unico_result(frames, linreg)      run tipo_unico for a frame stack
run_mirror_consistency_test(...)       batch diagnostic over many seeds
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np

from .cycle_laws import evaluate_structure_count_law
from .eca import random_initial_state, simulate
from .observers import observar_regiones_rule110
from .rule110_fixtures import ether_state
from .structures import Estructura, StructureType


# ── Low-level helpers ─────────────────────────────────────────────────────────

def mirror_state(state: np.ndarray) -> np.ndarray:
    """Return a left-right-flipped copy of a 1D binary state."""
    return np.asarray(state, dtype=np.uint8)[::-1].copy()


def _linreg_velocity(posiciones: tuple) -> float:
    """Estimate centroid velocity via linear regression over all track points."""
    if len(posiciones) < 2:
        return 0.0
    ts = np.array([p[0] for p in posiciones], dtype=np.float64)
    xs = np.array([p[1] for p in posiciones], dtype=np.float64)
    if ts[-1] == ts[0]:
        return 0.0
    a, _ = np.polyfit(ts, xs, 1)
    return float(a)


def classify_track_linreg(
    posiciones: tuple,
    *,
    periodic: bool = False,
    threshold: float = 0.05,
) -> tuple[StructureType, Literal["velocidad_linreg", "periodicidad", "desplazamiento_linreg", "persistencia"]]:
    """Velocity-based track classification using linear regression.

    Drop-in replacement for classify_track (structures.py).  Using
    linear regression over all track points is more robust than the
    first-last centroid used by the production classifier, and avoids
    some tracking fragmentation artefacts under IC reflection.

    Threshold remains 0.05 to keep the same effective calibration.
    """
    if periodic:
        return "oscilador", "periodicidad"
    if len(posiciones) < 2:
        return "desconocido", "persistencia"
    vx = _linreg_velocity(posiciones)
    if abs(vx) > threshold:
        return "glider", "velocidad_linreg"
    return "bloque", "desplazamiento_linreg"


def observar_regiones_rule110_linreg(
    frames: np.ndarray,
    *,
    min_persistence: int = 5,
) -> list[Estructura]:
    """Rule 110 region observer that classifies tracks via linear regression.

    Identical pipeline to observar_regiones_rule110 except that
    classify_track_linreg replaces classify_track in the final step.
    Uses the same ether-diff, region-tracking, and width-variation
    fallback as the production observer.
    """
    from .ether import diff_from_pure_ether
    from .observers import track_regions_1d

    tracks = track_regions_1d(diff_from_pure_ether(frames), min_persistence=min_persistence)
    structures: list[Estructura] = []
    for idx, track in enumerate(tracks):
        posiciones = tuple((t, x, 0) for t, x, _ in track)
        tipo, method = classify_track_linreg(posiciones)
        widths = [width for _, _, width in track]
        if tipo == "bloque" and len(set(widths)) > 1:
            tipo = "glider"
            method = "persistencia"
        avg_width = int(round(float(np.mean(widths))))
        structures.append(
            Estructura(
                id=idx,
                tipo=tipo,
                tipo_asignado_por=method,
                posiciones=posiciones,
                tamaño=max(1, avg_width),
                confianza=0.8,
                observador="regiones_rule110_linreg",
            )
        )
    return structures


# ── tipo_unico evaluation — mirrors the full agent pipeline ──────────────────
#
# The agent path: run_observers → deduplicate → noise gate → evaluate_cycle_laws
# We replicate this exactly so diagnostic results match the law table in memory.

_DEDUP_THRESHOLD = 40


def _tipo_unico_via_run_observers(frames: np.ndarray) -> bool | None:
    """tipo_unico via the production observer pipeline (no linreg).

    Returns None if the dedup noise gate fires (ruido_no_analizable),
    else True/False as the agent would record.
    """
    from .consensus import deduplicate_structures
    from .observers import run_observers

    structures = run_observers(frames)
    dedup = deduplicate_structures(structures)
    if len(dedup) > _DEDUP_THRESHOLD:
        return None  # noisy — agent skips tipo_unico evaluation
    return evaluate_structure_count_law(structures).accepted


def _tipo_unico_via_run_observers_linreg(frames: np.ndarray) -> bool | None:
    """tipo_unico via the agent pipeline but with classify_track replaced by
    classify_track_linreg for all observers.

    Uses a temporary monkey-patch confined to the call duration.
    Returns None if noise gate fires.
    """
    import zaa.observers as _obs_mod
    import zaa.structures as _struct_mod
    from .consensus import deduplicate_structures
    from .observers import run_observers

    original_ct_struct = _struct_mod.classify_track
    original_ct_obs    = _obs_mod.classify_track

    _struct_mod.classify_track = classify_track_linreg  # type: ignore[assignment]
    _obs_mod.classify_track    = classify_track_linreg  # type: ignore[assignment]
    try:
        structures = run_observers(frames)
    finally:
        _struct_mod.classify_track = original_ct_struct
        _obs_mod.classify_track    = original_ct_obs

    dedup = deduplicate_structures(structures)
    if len(dedup) > _DEDUP_THRESHOLD:
        return None
    return evaluate_structure_count_law(structures).accepted


def tipo_unico_result(
    frames: np.ndarray,
    *,
    use_linreg: bool = False,
) -> bool | None:
    """Return tipo_unico result using the full agent pipeline.

    Returns None when the noise gate (dedup > 40) fires — consistent with
    how the agent records tipo_unico=False for noisy runs.
    Set use_linreg=True to use the classify_track_linreg variant.
    """
    if use_linreg:
        return _tipo_unico_via_run_observers_linreg(frames)
    return _tipo_unico_via_run_observers(frames)


# ── Per-seed result ────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class SeedMirrorResult:
    """tipo_unico outcome for one seed in both orientations.

    None-valued results from the noise gate are normalised to False
    before storage (consistent with agent behaviour).
    """

    seed: int
    rule: int
    normal: bool          # production classifier, normal IC
    mirror: bool          # production classifier, mirrored IC
    consistent: bool      # normal == mirror (production)
    normal_linreg: bool   # linreg classifier, normal IC
    mirror_linreg: bool   # linreg classifier, mirrored IC
    consistent_linreg: bool  # normal_linreg == mirror_linreg


def _evaluate_seed(rule: int, seed: int, steps: int, width: int) -> SeedMirrorResult:
    ci = random_initial_state(width, seed=seed)
    ci_mirror = mirror_state(ci)

    frames        = simulate(ci, rule, steps)
    frames_mirror = simulate(ci_mirror, rule, steps)

    # None (noise) → False: matches agent's behaviour when run skips tipo_unico
    def _to_bool(v: bool | None) -> bool:
        return False if v is None else v

    tu_normal = _to_bool(tipo_unico_result(frames))
    tu_mirror = _to_bool(tipo_unico_result(frames_mirror))
    tu_n_lr   = _to_bool(tipo_unico_result(frames,        use_linreg=True))
    tu_m_lr   = _to_bool(tipo_unico_result(frames_mirror, use_linreg=True))

    return SeedMirrorResult(
        seed=seed,
        rule=rule,
        normal=tu_normal,
        mirror=tu_mirror,
        consistent=(tu_normal == tu_mirror),
        normal_linreg=tu_n_lr,
        mirror_linreg=tu_m_lr,
        consistent_linreg=(tu_n_lr == tu_m_lr),
    )


# ── Batch diagnostic ──────────────────────────────────────────────────────────

@dataclass(frozen=True)
class MirrorConsistencyReport:
    """Summary of mirror-consistency for one rule over n_seeds."""

    rule: int
    n_seeds: int
    steps: int
    width: int
    # production classifier
    tipo_unico_normal_count: int
    tipo_unico_mirror_count: int
    inconsistent_count: int
    inconsistency_rate: float
    # linreg variant
    tipo_unico_normal_linreg_count: int
    tipo_unico_mirror_linreg_count: int
    inconsistent_linreg_count: int
    inconsistency_rate_linreg: float
    # per-seed detail
    results: tuple[SeedMirrorResult, ...]

    def summary_line(self) -> str:
        return (
            f"rule={self.rule:3d}  n={self.n_seeds:3d}  "
            f"prod(normal/mirror/incons): {self.tipo_unico_normal_count:3d}/{self.tipo_unico_mirror_count:3d}/{self.inconsistent_count:3d} "
            f"({100*self.inconsistency_rate:.1f}%)  "
            f"linreg: {self.tipo_unico_normal_linreg_count:3d}/{self.tipo_unico_mirror_linreg_count:3d}/{self.inconsistent_linreg_count:3d} "
            f"({100*self.inconsistency_rate_linreg:.1f}%)"
        )


def run_mirror_consistency_test(
    rule: int,
    *,
    n_seeds: int = 60,
    steps: int = 24,
    width: int = 64,
    base_seed: int = 20260523,
) -> MirrorConsistencyReport:
    """Run the mirror-consistency diagnostic for one rule.

    For each of n_seeds random ICs, evaluates tipo_unico with:
      - the production classifier (classify_track, first-last velocity)
      - the linreg variant (classify_track_linreg, regression velocity)
    in both normal and mirrored orientations.

    Returns a MirrorConsistencyReport with per-seed detail and summary
    statistics.  The 'inconsistency_rate' is the fraction of seeds where
    tipo_unico(normal_IC) != tipo_unico(mirrored_IC).
    """
    results: list[SeedMirrorResult] = []
    for i in range(n_seeds):
        seed = base_seed + i
        results.append(_evaluate_seed(rule, seed, steps, width))

    tu_n  = sum(r.normal  for r in results)
    tu_m  = sum(r.mirror  for r in results)
    incon = sum(not r.consistent for r in results)

    tu_n_lr  = sum(r.normal_linreg  for r in results)
    tu_m_lr  = sum(r.mirror_linreg  for r in results)
    incon_lr = sum(not r.consistent_linreg for r in results)

    return MirrorConsistencyReport(
        rule=rule,
        n_seeds=n_seeds,
        steps=steps,
        width=width,
        tipo_unico_normal_count=tu_n,
        tipo_unico_mirror_count=tu_m,
        inconsistent_count=incon,
        inconsistency_rate=incon / n_seeds if n_seeds else 0.0,
        tipo_unico_normal_linreg_count=tu_n_lr,
        tipo_unico_mirror_linreg_count=tu_m_lr,
        inconsistent_linreg_count=incon_lr,
        inconsistency_rate_linreg=incon_lr / n_seeds if n_seeds else 0.0,
        results=tuple(results),
    )


# ── Rule-110/124 pair sanity check ────────────────────────────────────────────

def check_rule110_124_mirror_pair(
    seed: int,
    *,
    steps: int = 24,
    width: int = 64,
) -> dict:
    """Verify that rule_110 and rule_124 are exact spatial mirrors for one seed.

    rule_124(a,b,c) == rule_110(c,b,a) by definition (Wolfram equivalence class).
    For an IC that is the spatial mirror of another, the frame stacks should be
    exact mirrors frame-by-frame.

    Returns a dict with frame-equivalence stats and tipo_unico comparison.
    """
    ci = random_initial_state(width, seed=seed)
    ci_mirror = mirror_state(ci)

    frames_110        = simulate(ci,        110, steps)
    frames_110_mirror = simulate(ci_mirror, 110, steps)
    frames_124        = simulate(ci,        124, steps)
    frames_124_mirror = simulate(ci_mirror, 124, steps)

    # rule_110(IC) should equal mirror of rule_124(mirror(IC))
    frames_124_mirror_flipped = np.flip(frames_124_mirror, axis=1)
    frame_equiv_110_vs_mirror124 = int(
        np.sum([
            np.array_equal(frames_110[t], frames_124_mirror_flipped[t])
            for t in range(steps + 1)
        ])
    )

    tu_110         = tipo_unico_result(frames_110)
    tu_124         = tipo_unico_result(frames_124)
    tu_110_lr      = tipo_unico_result(frames_110, use_linreg=True)
    tu_124_lr      = tipo_unico_result(frames_124, use_linreg=True)

    return {
        "seed": seed,
        "frame_equivalence_110_vs_mirror124": frame_equiv_110_vs_mirror124,
        "total_frames": steps + 1,
        "mirror_exact": frame_equiv_110_vs_mirror124 == steps + 1,
        "tipo_unico_110_prod": tu_110,
        "tipo_unico_124_prod": tu_124,
        "consistent_prod": tu_110 == tu_124,
        "tipo_unico_110_linreg": tu_110_lr,
        "tipo_unico_124_linreg": tu_124_lr,
        "consistent_linreg": tu_110_lr == tu_124_lr,
    }
