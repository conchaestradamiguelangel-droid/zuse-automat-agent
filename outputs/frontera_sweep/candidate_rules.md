# Frontera Temporal ECA Sweep - Fase 11a

## Setup

- Rules: `0..255`
- Seeds: `[20260523, 20260524, 20260525]`
- Steps: `24`
- Width: `64`
- Candidate threshold: `frontera_temporal` accepted in at least `2/3` seeds.
- Sort: `frontera_temporal_rate DESC`, then `mean_n_laws DESC`.

`frontera_temporal` is evaluated on the full `steps=24` frame stack. There is no
subcycle sampling.

## Candidate Rules

| rule_id | eca_class | frontera_temporal_rate | hits | mean_n_laws | rich_frontera_rate | ok_rate | mean_transition_rate | other_laws_freq |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 46 | unknown | 1.000 | 3/3 | 6.000 | 1.000 | 1.000 | 0.364 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 208 | unknown | 1.000 | 3/3 | 6.000 | 1.000 | 1.000 | 0.356 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 209 | unknown | 1.000 | 3/3 | 6.000 | 1.000 | 1.000 | 0.369 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 80 | unknown | 1.000 | 3/3 | 5.667 | 1.000 | 1.000 | 0.358 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 148 | unknown | 1.000 | 3/3 | 5.667 | 1.000 | 1.000 | 0.394 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 174 | unknown | 1.000 | 3/3 | 5.667 | 1.000 | 1.000 | 0.355 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 20 | unknown | 1.000 | 3/3 | 5.333 | 1.000 | 1.000 | 0.374 | complejidad_alta:1.00, densidad_estable:0.33, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 137 | class-4 | 1.000 | 3/3 | 5.333 | 1.000 | 1.000 | 0.407 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:0.67 |
| 158 | unknown | 1.000 | 3/3 | 5.333 | 1.000 | 1.000 | 0.410 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 175 | unknown | 1.000 | 3/3 | 5.333 | 1.000 | 1.000 | 0.362 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 159 | unknown | 1.000 | 3/3 | 5.000 | 1.000 | 1.000 | 0.357 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, velocidad_constante:1.00 |
| 124 | unknown | 1.000 | 3/3 | 4.333 | 1.000 | 1.000 | 0.404 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33 |
| 193 | unknown | 1.000 | 3/3 | 4.333 | 1.000 | 1.000 | 0.416 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33 |
| 214 | unknown | 1.000 | 3/3 | 4.333 | 1.000 | 1.000 | 0.419 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, velocidad_constante:0.33 |
| 73 | unknown | 1.000 | 3/3 | 4.000 | 1.000 | 1.000 | 0.299 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00 |
| 110 | class-4 | 1.000 | 3/3 | 4.000 | 1.000 | 1.000 | 0.403 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00 |
| 29 | unknown | 1.000 | 3/3 | 3.333 | 1.000 | 1.000 | 0.330 | complejidad_alta:1.00, densidad_estable:0.33, temporal_scale_stability:1.00 |
| 84 | unknown | 0.667 | 2/3 | 5.667 | 0.667 | 1.000 | 0.416 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 138 | unknown | 0.667 | 2/3 | 5.667 | 0.667 | 1.000 | 0.386 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 212 | unknown | 0.667 | 2/3 | 5.667 | 0.667 | 1.000 | 0.416 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 213 | unknown | 0.667 | 2/3 | 5.667 | 0.667 | 1.000 | 0.417 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 244 | unknown | 0.667 | 2/3 | 5.667 | 0.667 | 1.000 | 0.385 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 10 | unknown | 0.667 | 2/3 | 5.333 | 0.667 | 1.000 | 0.388 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 14 | unknown | 0.667 | 2/3 | 5.333 | 0.667 | 1.000 | 0.415 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 74 | unknown | 0.667 | 2/3 | 5.333 | 0.667 | 1.000 | 0.324 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 116 | unknown | 0.667 | 2/3 | 5.333 | 0.667 | 1.000 | 0.392 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 142 | unknown | 0.667 | 2/3 | 5.333 | 0.667 | 1.000 | 0.415 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 229 | unknown | 0.667 | 2/3 | 5.333 | 0.667 | 1.000 | 0.308 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 52 | unknown | 0.667 | 2/3 | 5.000 | 0.667 | 1.000 | 0.396 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 139 | unknown | 0.667 | 2/3 | 5.000 | 0.667 | 1.000 | 0.398 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 143 | unknown | 0.667 | 2/3 | 5.000 | 0.667 | 1.000 | 0.416 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 155 | unknown | 0.667 | 2/3 | 5.000 | 0.667 | 1.000 | 0.401 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 245 | unknown | 0.667 | 2/3 | 5.000 | 0.667 | 1.000 | 0.392 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:0.67 |
| 6 | unknown | 0.667 | 2/3 | 4.667 | 0.667 | 1.000 | 0.329 | complejidad_alta:0.67, densidad_estable:0.33, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 38 | unknown | 0.667 | 2/3 | 4.667 | 0.667 | 1.000 | 0.367 | complejidad_alta:0.67, densidad_estable:0.33, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 134 | unknown | 0.667 | 2/3 | 4.667 | 0.667 | 1.000 | 0.357 | complejidad_alta:0.67, densidad_estable:0.33, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 211 | unknown | 0.667 | 2/3 | 4.333 | 0.667 | 1.000 | 0.372 | complejidad_alta:0.67, densidad_estable:1.00, temporal_scale_stability:1.00, velocidad_constante:1.00 |
| 109 | class-4 | 0.667 | 2/3 | 3.333 | 0.667 | 1.000 | 0.327 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00 |

## Rich Frontera Candidates

Rules where `frontera_temporal` appears and co-appears with at least two other
laws in at least `2/3` seeds.

| rule_id | eca_class | frontera_temporal_rate | mean_n_laws | other_laws_freq |
| --- | --- | --- | --- | --- |
| 46 | unknown | 1.000 | 6.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 208 | unknown | 1.000 | 6.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 209 | unknown | 1.000 | 6.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 80 | unknown | 1.000 | 5.667 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 148 | unknown | 1.000 | 5.667 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 174 | unknown | 1.000 | 5.667 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 20 | unknown | 1.000 | 5.333 | complejidad_alta:1.00, densidad_estable:0.33, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 137 | class-4 | 1.000 | 5.333 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:0.67 |
| 158 | unknown | 1.000 | 5.333 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 175 | unknown | 1.000 | 5.333 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 159 | unknown | 1.000 | 5.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, velocidad_constante:1.00 |
| 124 | unknown | 1.000 | 4.333 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33 |
| 193 | unknown | 1.000 | 4.333 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33 |
| 214 | unknown | 1.000 | 4.333 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, velocidad_constante:0.33 |
| 73 | unknown | 1.000 | 4.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00 |
| 110 | class-4 | 1.000 | 4.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00 |
| 29 | unknown | 1.000 | 3.333 | complejidad_alta:1.00, densidad_estable:0.33, temporal_scale_stability:1.00 |
| 84 | unknown | 0.667 | 5.667 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 138 | unknown | 0.667 | 5.667 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 212 | unknown | 0.667 | 5.667 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 213 | unknown | 0.667 | 5.667 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 244 | unknown | 0.667 | 5.667 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 10 | unknown | 0.667 | 5.333 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 14 | unknown | 0.667 | 5.333 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 74 | unknown | 0.667 | 5.333 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 116 | unknown | 0.667 | 5.333 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 142 | unknown | 0.667 | 5.333 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 229 | unknown | 0.667 | 5.333 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 52 | unknown | 0.667 | 5.000 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:1.00 |
| 139 | unknown | 0.667 | 5.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 143 | unknown | 0.667 | 5.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 155 | unknown | 0.667 | 5.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.33, velocidad_constante:1.00 |
| 245 | unknown | 0.667 | 5.000 | complejidad_alta:1.00, densidad_estable:1.00, temporal_scale_stability:1.00, tipo_unico:0.67, velocidad_constante:0.67 |
| 6 | unknown | 0.667 | 4.667 | complejidad_alta:0.67, densidad_estable:0.33, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 38 | unknown | 0.667 | 4.667 | complejidad_alta:0.67, densidad_estable:0.33, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 134 | unknown | 0.667 | 4.667 | complejidad_alta:0.67, densidad_estable:0.33, temporal_scale_stability:1.00, tipo_unico:1.00, velocidad_constante:1.00 |
| 211 | unknown | 0.667 | 4.333 | complejidad_alta:0.67, densidad_estable:1.00, temporal_scale_stability:1.00, velocidad_constante:1.00 |
| 109 | class-4 | 0.667 | 3.333 | complejidad_alta:1.00, densidad_estable:0.67, temporal_scale_stability:1.00 |

## Interpretation

This sweep searches for worlds where `frontera_temporal` is not merely a rare
isolated trigger, but part of a productive law signature. Candidate rules should
be considered for deeper discovery only when the frontera signal co-occurs with
multiple other laws.
