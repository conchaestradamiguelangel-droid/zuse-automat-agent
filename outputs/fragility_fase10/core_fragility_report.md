# Core Fragility - Fase 15b

## Method

`f_total` counts any law-signature change under one-bit flips.

`f_core` counts only changes to the laws that define the world's category or
regime. Noise and silence count as core changes because the defining regime is
lost.

Core-law convention:

- `frontera-rich-estable`: six-law frontier signature.
- `periodicidad-global`: `periodicidad`.
- `multiregimen-productivo`: the reference signature for that seed.
- `rule_90`: `temporal_scale_stability`.

## Core Fragility Table

| world | core_laws | f_total | f_core | f_secondary | f_noise |
| --- | --- | --- | --- | --- | --- |
| rule_208 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante | 0.000 | 0.000 | 0.000 | 0.000 |
| rule_209 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante | 0.000 | 0.000 | 0.000 | 0.000 |
| rule_51 | periodicidad | 0.193 | 0.000 | 0.193 | 0.000 |
| rule_90 | temporal_scale_stability | 0.172 | 0.000 | 0.172 | 0.000 |
| rule_46 | complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante | 0.031 | 0.031 | 0.000 | 0.000 |
| rule_124 | reference_signature_per_seed | 0.224 | 0.083 | 0.141 | 0.000 |
| rule_18 | reference_signature_per_seed | 0.349 | 0.135 | 0.214 | 0.000 |
| rule_110 | reference_signature_per_seed | 0.323 | 0.198 | 0.125 | 0.000 |
| rule_109 | reference_signature_per_seed | 0.250 | 0.250 | 0.000 | 0.000 |
| rule_137 | reference_signature_per_seed | 0.630 | 0.312 | 0.318 | 0.000 |
| rule_54 | reference_signature_per_seed | 0.714 | 0.677 | 0.036 | 0.375 |

## Interpretation

`rule_51` is the motivating case: `f_total = 0.193`,
but `f_core = 0.000`. Global periodicity survives
all measured one-bit flips; only secondary laws such as `densidad_estable`
change.

`rule_137` remains a true high-core-fragility world:
`f_core = 0.312`. Its defining productive regime
changes under most perturbations.
