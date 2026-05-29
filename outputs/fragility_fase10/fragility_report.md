# Basin Fragility Diagnostic — Fase 10a

## Setup

- IC width: `64`
- Worlds and canonical steps:
  - `rule_137`: `steps=48`
  - `rule_18`: `steps=24`
  - `rule_109`: `steps=48`
  - `rule_90`: `steps=96`
- Seeds are reconstructed from `journal_8c_long.jsonl` because the journal does
  not store seed explicitly.
- Fragility = one-bit flips that change outcome / 64.
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
| rule_90 | 20260567 | 24 | 0.266 | 0.000 | 0.000 | 0.266 | complejidad_alta + densidad_estable + temporal_scale_stability |
| rule_90 | 20260568 | 48 | 0.188 | 0.000 | 0.000 | 0.188 | temporal_scale_stability |
| rule_90 | 20260570 | 48 | 0.062 | 0.000 | 0.000 | 0.062 | temporal_scale_stability |

## Fragility Aggregated by World (mean across seeds)

| world | f_other_sig | f_silence | f_noise | f_total |
| --- | --- | --- | --- | --- |
| rule_109 | 0.250 | 0.000 | 0.000 | 0.250 |
| rule_137 | 0.630 | 0.000 | 0.000 | 0.630 |
| rule_18 | 0.349 | 0.000 | 0.000 | 0.349 |
| rule_90 | 0.172 | 0.000 | 0.000 | 0.172 |

## Interpretation

- `rule_109`: total fragility `0.250`, dominated by `other_sig` (`0.250`); perturbations mostly move the IC into other productive law signatures.
- `rule_137`: total fragility `0.630`, dominated by `other_sig` (`0.630`); perturbations mostly move the IC into other productive law signatures.
- `rule_18`: total fragility `0.349`, dominated by `other_sig` (`0.349`); perturbations mostly move the IC into other productive law signatures.
- `rule_90`: total fragility `0.172`, dominated by `other_sig` (`0.172`); perturbations mostly move the IC into other productive law signatures.

## Scientific Question

Is `rule_137` special because it has a fragile basin, or do all multi-regime
worlds have sensitive boundaries?

`rule_137` is the most fragile world in this sample.
