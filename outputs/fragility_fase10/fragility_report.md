# Basin Fragility Diagnostic - Fase 10a/12a

## Setup

- IC width: `64`
- Worlds and canonical steps:
  - `rule_137`: `steps=48`
  - `rule_18`: `steps=24`
  - `rule_109`: `steps=48`
  - `rule_90`: `steps=96`
  - `rule_46`: `steps=24`
  - `rule_208`: `steps=24`
  - `rule_209`: `steps=24`
  - `rule_54`: `steps=96`
  - `rule_110`: `steps=24`
  - `rule_124`: `steps=24`
  - `rule_51`: `steps=96`
- Seeds are reconstructed from `journal_8c_long.jsonl` because the journal does
  not store seed explicitly. `rule_46`, `rule_208`, and `rule_209` use formal
  profile seeds `20260523..20260525`.
- Fragility = one-bit flips that change outcome / 64.
- Total perturbations in this report: `1984`.
- Components:
  - `f_other_sig`: flip produces a different non-empty law signature.
  - `f_silence`: flip produces `analysis_ok=True` and `laws_accepted=[]`.
  - `f_noise`: flip produces `analysis_status=ruido_no_analizable`.
  - `f_total`: sum of the three previous components.

Selected cases:

- `rule_137`: seed 20260633 @ steps 48, seed 20260635 @ steps 48, seed 20260673 @ steps 48
- `rule_18`: seed 20260564 @ steps 24, seed 20260566 @ steps 24, seed 20260643 @ steps 24
- `rule_109`: seed 20260554 @ steps 48
- `rule_90`: seed 20260568 @ steps 48, seed 20260570 @ steps 48, seed 20260567 @ steps 24
- `rule_46`: seed 20260523 @ steps 24, seed 20260524 @ steps 24, seed 20260525 @ steps 24
- `rule_208`: seed 20260523 @ steps 24, seed 20260524 @ steps 24, seed 20260525 @ steps 24
- `rule_209`: seed 20260523 @ steps 24, seed 20260524 @ steps 24, seed 20260525 @ steps 24
- `rule_54`: seed 20260638 @ steps 96, seed 20260640 @ steps 96, seed 20260642 @ steps 96
- `rule_110`: seed 20260547 @ steps 24, seed 20260549 @ steps 24, seed 20260613 @ steps 24
- `rule_124`: seed 20260550 @ steps 24, seed 20260552 @ steps 24, seed 20260617 @ steps 24
- `rule_51`: seed 20260523 @ steps 96, seed 20260524 @ steps 96, seed 20260525 @ steps 96

## Fragility Components

| world | seed | steps | f_other_sig | f_silence | f_noise | f_total | reference_signature |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule_109 | 20260554 | 48 | 0.250 | 0.000 | 0.000 | 0.250 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability |
| rule_110 | 20260547 | 24 | 0.203 | 0.000 | 0.000 | 0.203 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + velocidad_constante |
| rule_110 | 20260549 | 24 | 0.359 | 0.000 | 0.000 | 0.359 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + velocidad_constante |
| rule_110 | 20260613 | 24 | 0.406 | 0.000 | 0.000 | 0.406 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability |
| rule_124 | 20260550 | 24 | 0.234 | 0.000 | 0.000 | 0.234 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability |
| rule_124 | 20260552 | 24 | 0.125 | 0.000 | 0.000 | 0.125 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability |
| rule_124 | 20260617 | 24 | 0.312 | 0.000 | 0.000 | 0.312 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability |
| rule_137 | 20260633 | 48 | 0.812 | 0.000 | 0.000 | 0.812 | complejidad_alta + frontera_temporal |
| rule_137 | 20260635 | 48 | 0.219 | 0.000 | 0.000 | 0.219 | complejidad_alta + densidad_estable + frontera_temporal |
| rule_137 | 20260673 | 48 | 0.859 | 0.000 | 0.000 | 0.859 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_18 | 20260564 | 24 | 0.281 | 0.000 | 0.000 | 0.281 | temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_18 | 20260566 | 24 | 0.188 | 0.000 | 0.000 | 0.188 | complejidad_alta + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_18 | 20260643 | 24 | 0.578 | 0.000 | 0.000 | 0.578 | complejidad_alta + temporal_scale_stability + velocidad_constante |
| rule_208 | 20260523 | 24 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_208 | 20260524 | 24 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_208 | 20260525 | 24 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_209 | 20260523 | 24 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_209 | 20260524 | 24 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_209 | 20260525 | 24 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_46 | 20260523 | 24 | 0.062 | 0.000 | 0.000 | 0.062 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_46 | 20260524 | 24 | 0.016 | 0.000 | 0.000 | 0.016 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_46 | 20260525 | 24 | 0.016 | 0.000 | 0.000 | 0.016 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante |
| rule_51 | 20260523 | 96 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + periodicidad + temporal_scale_stability + tipo_unico |
| rule_51 | 20260524 | 96 | 0.000 | 0.000 | 0.000 | 0.000 | complejidad_alta + densidad_estable + periodicidad + temporal_scale_stability + tipo_unico |
| rule_51 | 20260525 | 96 | 0.578 | 0.000 | 0.000 | 0.578 | complejidad_alta + periodicidad + temporal_scale_stability + tipo_unico |
| rule_54 | 20260638 | 96 | 0.391 | 0.000 | 0.219 | 0.609 | complejidad_alta + temporal_scale_stability + velocidad_constante |
| rule_54 | 20260640 | 96 | 0.344 | 0.000 | 0.281 | 0.625 | complejidad_alta + temporal_scale_stability + velocidad_constante |
| rule_54 | 20260642 | 96 | 0.281 | 0.000 | 0.625 | 0.906 | complejidad_alta + temporal_scale_stability |
| rule_90 | 20260567 | 24 | 0.266 | 0.000 | 0.000 | 0.266 | complejidad_alta + densidad_estable + temporal_scale_stability |
| rule_90 | 20260568 | 48 | 0.188 | 0.000 | 0.000 | 0.188 | temporal_scale_stability |
| rule_90 | 20260570 | 48 | 0.062 | 0.000 | 0.000 | 0.062 | temporal_scale_stability |

## Fragility Aggregated by World (mean across seeds)

| world | f_other_sig | f_silence | f_noise | f_total |
| --- | --- | --- | --- | --- |
| rule_109 | 0.307 | 0.000 | 0.000 | 0.307 |
| rule_110 | 0.323 | 0.000 | 0.000 | 0.323 |
| rule_124 | 0.224 | 0.000 | 0.000 | 0.224 |
| rule_137 | 0.630 | 0.000 | 0.000 | 0.630 |
| rule_18 | 0.349 | 0.000 | 0.000 | 0.349 |
| rule_208 | 0.000 | 0.000 | 0.000 | 0.000 |
| rule_209 | 0.000 | 0.000 | 0.000 | 0.000 |
| rule_46 | 0.031 | 0.000 | 0.000 | 0.031 |
| rule_51 | 0.193 | 0.000 | 0.000 | 0.193 |
| rule_54 | 0.339 | 0.000 | 0.375 | 0.714 |
| rule_90 | 0.172 | 0.000 | 0.000 | 0.172 |

## Fragility Spectrum

| world | category | f_total | pattern |
| --- | --- | --- | --- |
| rule_208 | frontera-rich-estable | 0.000 | - |
| rule_209 | frontera-rich-estable | 0.000 | - |
| rule_46 | frontera-rich-estable | 0.031 | - |
| rule_90 | multiregimen-escala-dependiente | 0.172 | clustered |
| rule_51 | periodicidad-global | 0.193 | dispersed |
| rule_124 | multiregimen-productivo | 0.224 | dispersed |
| rule_109 | multiregimen-productivo | 0.307 | clustered |
| rule_110 | multiregimen-productivo | 0.323 | clustered |
| rule_18 | multiregimen-productivo | 0.349 | clustered |
| rule_137 | multiregimen-productivo | 0.630 | dispersed |
| rule_54 | multiregimen-productivo | 0.714 | clustered |

The spectrum is category-aligned at the extremes: `frontera-rich-estable`
occupies the low-fragility end, while `multiregimen-productivo` occupies the
upper end. `periodicidad-global` (`rule_51`) sits in the middle: periodicity is
robust, but the full law signature can still change.

`rule_208` and `rule_209` both have `f_total = 0.000`. Since they are linked by
the complement symmetry `0 <-> 1`, this suggests complement symmetry preserves
not only the law signature but also the basin width.

`rule_54` is the new ECA mechanism exception: it is highly fragile by
`f_total`, but its fragility is partly noise-boundary fragility (`f_noise =
0.375`), not only productive signature switching.

`rule_51` disproves the naive prediction `f_total ~= 0`: global periodicity
survives all flips, but the complete law signature changes when
`densidad_estable` toggles.

## Interpretation

- `rule_109`: total fragility `0.307`, dominated by `other_sig` (`0.307`); perturbations mostly move the IC into other productive law signatures. This is the Fase 13b multi-seed mean, superseding the original single-seed estimate (`0.250`).
- `rule_110`: total fragility `0.323`, dominated by `other_sig` (`0.323`); perturbations mostly move the IC into other productive law signatures.
- `rule_124`: total fragility `0.224`, dominated by `other_sig` (`0.224`); perturbations mostly move the IC into other productive law signatures.
- `rule_137`: total fragility `0.630`, dominated by `other_sig` (`0.630`); perturbations mostly move the IC into other productive law signatures.
- `rule_18`: total fragility `0.349`, dominated by `other_sig` (`0.349`); perturbations mostly move the IC into other productive law signatures.
- `rule_208`: total fragility `0.000`; all one-bit perturbations preserve the reference law signature.
- `rule_209`: total fragility `0.000`; all one-bit perturbations preserve the reference law signature.
- `rule_46`: total fragility `0.031`, dominated by `other_sig` (`0.031`); perturbations mostly move the IC into other productive law signatures.
- `rule_51`: total fragility `0.193`, dominated by `other_sig` (`0.193`); perturbations mostly move the IC into other productive law signatures.
- `rule_54`: total fragility `0.714`, dominated by `noise` (`0.375`); perturbations mostly push the IC across the noise gate.
- `rule_90`: total fragility `0.172`, dominated by `other_sig` (`0.172`); perturbations mostly move the IC into other productive law signatures.

## Scientific Question

Is `rule_137` special because it has a fragile basin, or do all multi-regime
worlds have sensitive boundaries?

`rule_137` is fragile, but not an outlier against the other multi-regime worlds.

Fase 12a extends the same protocol to `frontera-rich-estable` worlds
(`rule_46`, `rule_208`, `rule_209`). These worlds are expected to be more
robust than `rule_137` because their formal profiles have low signature
diversity and nearly invariant six-law signatures.

Fase 12c adds the remaining measured `multiregimen-productivo` worlds:
`rule_54`, `rule_110`, and `rule_124`.

Fase 15a adds `rule_51` as `periodicidad-global`.

## Key Finding: frontera-rich-estable Basins Are Wide

The `frontera-rich-estable` worlds are dramatically more robust than `rule_137`: `rule_208` and `rule_209` have `f_total = 0.000`, while `rule_46` has `f_total = 0.031`.

This confirms the pre-run hypothesis: stable high-richness worlds have broad
law-signature basins, unlike `rule_137`, whose signature changes under most
single-bit perturbations.


## Fase 13b: rule_109 Multi-Seed Confirmation

Fase 13b reran `rule_109` at `steps=48`, `width=64` with two fresh seeds
(`20260601`, `20260602`) and compared them against the original seed
`20260554`.

| seed | f_total | f_other_sig | f_silence | f_noise | bin_range | peak_bin | central_peak |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20260554 | 0.250 | 0.250 | 0.000 | 0.000 | 0.875 | 1 | no |
| 20260601 | 0.469 | 0.469 | 0.000 | 0.000 | 0.750 | 3 | yes |
| 20260602 | 0.203 | 0.203 | 0.000 | 0.000 | 0.625 | 3 | yes |

Mean across the three seeds: `f_total = 0.307`, entirely productive
(`f_silence = 0.000`, `f_noise = 0.000`). The aggregate position map remains
clustered (`bin_range = 0.500`), with strongest overlap in positions `24-31`.

Verdict: **cluster_confirmado**. Cluster confirmado como propiedad robusta de `rule_109`: al menos 2/3 seeds tienen `bin_range > 0.5` y pico central.

## Two Fragility Mechanisms

Ten of eleven measured worlds in the original ECA fragility set still have
`f_noise = 0`; `rule_54` is the exception with `f_noise = 0.375`. This
qualifies the earlier Fase 10 finding: productive fragility is the dominant
mechanism, but `rule_54` defines a second mechanism, noise-boundary fragility.

- Productive basin switching: `rule_137` (`f_noise = 0.000`, dispersed) has
  many productive attractors available.
- Noise-boundary fragility: `rule_54` (`f_noise = 0.375`, clustered) sits close
  to the deduplicated structure threshold and can fall into noise under local
  perturbation.

## Fase 22: Physical Atlas Completion

Fase 22 measured the remaining atlas worlds with genuine perturbable initial
conditions: `rule_30`, `rule_150`, `life_blinker`, `life_block`, and
`life_glider`.

The three synthetic controls (`synthetic_bloque`, `synthetic_glider`,
`synthetic_oscilador`) remain `n/a` by design: they are frame generators, not
dynamical systems evolved from an IC. Assigning them `f_total` would invent a
new perturbation protocol.

| world | protocol | n_flips | f_total | f_core | f_noise | interpretation |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `rule_30` | ECA productive pockets | 192 | 0.021 | 0.021 | 0.000 | robust when measured inside non-empty visits |
| `rule_150` | ECA productive pockets | 128 | 0.023 | 0.023 | 0.000 | robust when measured inside non-empty visits |
| `life_block` | 2D one-cell flips | 1024 | 0.016 | 0.016 | 0.000 | stable Life fixture |
| `life_glider` | 2D one-cell flips | 1024 | 0.032 | 0.032 | 0.000 | stable Life fixture |
| `life_blinker` | 2D one-cell flips | 1024 | 1.000 | 1.000 | 0.000 | exact oscillator fixture disrupted by any extra cell |

The result closes the physical fragility atlas: all non-synthetic worlds now
have measured `f_total` and `f_core`. The surprise is `life_blinker`: its
fixture is physically simple but signature-fragile, because any additional cell
breaks the exact periodic reference signature under the 2D observer protocol.
