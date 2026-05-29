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
- Seeds are reconstructed from `journal_8c_long.jsonl` because the journal does
  not store seed explicitly. `rule_46`, `rule_208`, and `rule_209` use formal
  profile seeds `20260523..20260525`.
- Fragility = one-bit flips that change outcome / 64.
- Total perturbations in this report: `1216`.
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

## Fragility Components

| world | seed | steps | f_other_sig | f_silence | f_noise | f_total | reference_signature |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule_109 | 20260554 | 48 | 0.250 | 0.000 | 0.000 | 0.250 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability |
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
| rule_90 | 20260567 | 24 | 0.266 | 0.000 | 0.000 | 0.266 | complejidad_alta + densidad_estable + temporal_scale_stability |
| rule_90 | 20260568 | 48 | 0.188 | 0.000 | 0.000 | 0.188 | temporal_scale_stability |
| rule_90 | 20260570 | 48 | 0.062 | 0.000 | 0.000 | 0.062 | temporal_scale_stability |

## Fragility Aggregated by World (mean across seeds)

| world | f_other_sig | f_silence | f_noise | f_total |
| --- | --- | --- | --- | --- |
| rule_109 | 0.250 | 0.000 | 0.000 | 0.250 |
| rule_137 | 0.630 | 0.000 | 0.000 | 0.630 |
| rule_18 | 0.349 | 0.000 | 0.000 | 0.349 |
| rule_208 | 0.000 | 0.000 | 0.000 | 0.000 |
| rule_209 | 0.000 | 0.000 | 0.000 | 0.000 |
| rule_46 | 0.031 | 0.000 | 0.000 | 0.031 |
| rule_90 | 0.172 | 0.000 | 0.000 | 0.172 |

## Fragility Spectrum

| world | category | f_total | pattern |
| --- | --- | --- | --- |
| rule_208 | frontera-rich-estable | 0.000 | - |
| rule_209 | frontera-rich-estable | 0.000 | - |
| rule_46 | frontera-rich-estable | 0.031 | - |
| rule_90 | multiregimen-escala-dependiente | 0.172 | clustered |
| rule_109 | multiregimen-productivo | 0.250 | clustered |
| rule_18 | multiregimen-productivo | 0.349 | clustered |
| rule_137 | multiregimen-productivo | 0.630 | dispersed |

The spectrum is ordered and category-aligned: `frontera-rich-estable` occupies
the low-fragility end, while `multiregimen-productivo` occupies the upper end.
There is no overlap in the measured set.

`rule_208` and `rule_209` both have `f_total = 0.000`. Since they are linked by
the complement symmetry `0 <-> 1`, this suggests complement symmetry preserves
not only the law signature but also the basin width.

## Interpretation

- `rule_109`: total fragility `0.250`, dominated by `other_sig` (`0.250`); perturbations mostly move the IC into other productive law signatures.
- `rule_137`: total fragility `0.630`, dominated by `other_sig` (`0.630`); perturbations mostly move the IC into other productive law signatures.
- `rule_18`: total fragility `0.349`, dominated by `other_sig` (`0.349`); perturbations mostly move the IC into other productive law signatures.
- `rule_208`: total fragility `0.000`; all one-bit perturbations preserve the reference law signature.
- `rule_209`: total fragility `0.000`; all one-bit perturbations preserve the reference law signature.
- `rule_46`: total fragility `0.031`, dominated by `other_sig` (`0.031`); perturbations mostly move the IC into other productive law signatures.
- `rule_90`: total fragility `0.172`, dominated by `other_sig` (`0.172`); perturbations mostly move the IC into other productive law signatures.

## Scientific Question

Is `rule_137` special because it has a fragile basin, or do all multi-regime
worlds have sensitive boundaries?

`rule_137` is the most fragile world in this sample.

Fase 12a extends the same protocol to `frontera-rich-estable` worlds
(`rule_46`, `rule_208`, `rule_209`). These worlds are expected to be more
robust than `rule_137` because their formal profiles have low signature
diversity and nearly invariant six-law signatures.

## Key Finding: frontera-rich-estable Basins Are Wide

The `frontera-rich-estable` worlds are dramatically more robust than `rule_137`: `rule_208` and `rule_209` have `f_total = 0.000`, while `rule_46` has `f_total = 0.031`.

This confirms the pre-run hypothesis: stable high-richness worlds have broad
law-signature basins, unlike `rule_137`, whose signature changes under most
single-bit perturbations.

## Productive Fragility Check

Across all worlds, `f_silence = 0` and `f_noise = 0`. All observed fragility is productive: perturbations either preserve the law signature or move to another non-empty signature.
