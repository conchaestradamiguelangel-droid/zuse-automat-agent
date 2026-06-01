# Fragility Completion - Fase 22

## Scope

This run completes one-bit fragility for remaining atlas worlds with a genuine
perturbable initial condition:

- ECA: `rule_30`, `rule_150`.
- 2D Life controls: `life_blinker`, `life_block`, `life_glider`.

The three synthetic controls are marked `n/a`: they are frame generators, not
dynamical systems evolved from an IC. Assigning them `f_total` would invent a
perturbation protocol outside the atlas physics.

For these remaining controls, `f_core` is set equal to `f_total`: there is no
separate category-defining core law beyond the measured reference signature.

## Per-Case Results

| world | seed | steps | n_flips | f_other_sig | f_silence | f_noise | f_total | reference_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| life_blinker | fixture | 24 | 1024 | 1.000 | 0.000 | 0.000 | 1.000 | densidad_estable + periodicidad + tipo_unico |
| life_block | fixture | 24 | 1024 | 0.016 | 0.000 | 0.000 | 0.016 | densidad_estable + tipo_unico |
| life_glider | fixture | 24 | 1024 | 0.032 | 0.000 | 0.000 | 0.032 | densidad_estable + tipo_unico + velocidad_constante |
| rule_150 | 20260577 | 24 | 64 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + densidad_estable + temporal_scale_stability |
| rule_150 | 20260578 | 48 | 64 | 0.047 | 0.000 | 0.000 | 0.047 | complejidad_alta + densidad_estable + temporal_scale_stability |
| rule_30 | 20260544 | 24 | 64 | 0.016 | 0.000 | 0.000 | 0.016 | complejidad_alta + densidad_estable + temporal_scale_stability |
| rule_30 | 20260546 | 24 | 64 | 0.031 | 0.000 | 0.000 | 0.031 | complejidad_alta + densidad_estable + temporal_scale_stability |
| rule_30 | 20260610 | 24 | 64 | 0.016 | 0.000 | 0.000 | 0.016 | complejidad_alta + densidad_estable + temporal_scale_stability |

## Aggregated by World

| world | n_cases | n_flips | f_total | f_core | f_noise | reference_signatures |
| --- | --- | --- | --- | --- | --- | --- |
| life_blinker | 1 | 1024 | 1.000 | 1.000 | 0.000 | densidad_estable + periodicidad + tipo_unico |
| life_block | 1 | 1024 | 0.016 | 0.016 | 0.000 | densidad_estable + tipo_unico |
| life_glider | 1 | 1024 | 0.032 | 0.032 | 0.000 | densidad_estable + tipo_unico + velocidad_constante |
| rule_150 | 2 | 128 | 0.023 | 0.023 | 0.000 | complejidad_alta + densidad_estable + temporal_scale_stability |
| rule_30 | 3 | 192 | 0.021 | 0.021 | 0.000 | complejidad_alta + densidad_estable + temporal_scale_stability |
| synthetic_bloque | 0 | 0 | n/a | n/a | n/a | n/a |
| synthetic_glider | 0 | 0 | n/a | n/a | n/a | n/a |
| synthetic_oscilador | 0 | 0 | n/a | n/a | n/a | n/a |

## Interpretation

`rule_30` and `rule_150` are noise-bounded worlds in the long journal, so this
diagnostic measures their productive pockets rather than their noisy visits.
Both are therefore reported as conditional fragility at the selected productive
steps/seeds.

Life controls are physical 2D CA worlds with a well-defined one-cell
perturbation protocol over the full 32x32 initial grid. Their fragility values
are directly comparable as fixture-level robustness scores, but not as ECA
one-dimensional bit-position spectra.

Synthetic controls remain outside basin-fragility measurement by design.
