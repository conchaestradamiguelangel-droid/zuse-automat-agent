# Top Frontera Temporal Rule Profiles - Fase 11b

Protocol: `steps=24`, `width=64`, seeds `20260523..20260528`.

Frequency classes:

- `core`: `>=4/6`
- `present`: `2-3/6`
- `trace`: `1/6`
- `absent`: `0/6`

Symmetry note: `rule_46` and `rule_209` are complementary (`255 - n`).
`rule_208` is not part of that pair; its complement is `rule_47`.

## Overview

| world | classification | ok | mean_n_laws | peak_diversity | mean_tr | mean_entropy |
| --- | --- | --- | --- | --- | --- | --- |
| rule_46 | sin-evidencia-multiregimen | 6/6 | 5.833 | 0.333 | 0.361 | 0.935 |
| rule_208 | sin-evidencia-multiregimen | 6/6 | 6.000 | 0.167 | 0.350 | 0.945 |
| rule_209 | sin-evidencia-multiregimen | 6/6 | 6.000 | 0.167 | 0.361 | 0.935 |

## Law Frequency Matrix

| world | velocidad_constante | periodicidad | densidad_estable | tipo_unico | complejidad_alta | frontera_temporal | temporal_scale_stability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule_46 | 6/6 core | 0/6 absent | 5/6 core | 6/6 core | 6/6 core | 6/6 core | 6/6 core |
| rule_208 | 6/6 core | 0/6 absent | 6/6 core | 6/6 core | 6/6 core | 6/6 core | 6/6 core |
| rule_209 | 6/6 core | 0/6 absent | 6/6 core | 6/6 core | 6/6 core | 6/6 core | 6/6 core |

## rule_46

- Classification: `sin-evidencia-multiregimen`
- Mean accepted laws: `5.833`
- Mean transition rate: `0.361`
- Mean entropy: `0.935`
- Dominant signatures:

  - `velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability`: `5/6`
  - `velocidad_constante + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability`: `1/6`

## rule_208

- Classification: `sin-evidencia-multiregimen`
- Mean accepted laws: `6.000`
- Mean transition rate: `0.350`
- Mean entropy: `0.945`
- Dominant signatures:

  - `velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability`: `6/6`

## rule_209

- Classification: `sin-evidencia-multiregimen`
- Mean accepted laws: `6.000`
- Mean transition rate: `0.361`
- Mean entropy: `0.935`
- Dominant signatures:

  - `velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability`: `6/6`

## Interpretation

`rule_46` and `rule_209` form the expected complement pair. `rule_209`
reaches maximum observed richness (`mean_n_laws=6.000`), while `rule_46` is
nearly identical (`mean_n_laws=5.833`) with one seed missing `densidad_estable`.
Their signature profiles should be interpreted as one physical phenomenon under
bit complement symmetry.

`rule_208` also reaches `mean_n_laws=6.000`, but it is not the
complement of either rule_46 or rule_209. Its dominant signatures are
therefore evidence for a second route to maximum frontera-rich behavior,
unless later analysis shows another symmetry relation.

Signature comparison:

- `rule_46`: `{'velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability': 5, 'velocidad_constante + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability': 1}`
- `rule_209`: `{'velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability': 6}`
- `rule_208`: `{'velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability': 6}`
