# Periodicity Sweep - Fase 14

## Setup

- Atlas rules: `rule_18, rule_46, rule_54, rule_90, rule_109, rule_110, rule_124, rule_137, rule_208, rule_209`
- Known periodic candidates: `rule_51, rule_15, rule_57`
- Seeds per rule: `50`
- Seed range: `20260523..20260572`
- Steps: `96`
- Width: `64`
- Production noise gate: `dedup_structure_count > 40`

`periodicity_raw` means at least one observer emitted `tipo=oscilador`.
`periodicity_production` means the cycle was not noise-gated and
`periodicidad` appeared in `laws_accepted`.

## Rule Summary

| world | group | periodicity_raw/50 | periodicity_production/50 | ok/50 | noise/50 | oscillator_count_mean | laws_frequency |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule_15 | known_periodic | 0 | 0 | 20 | 30 | 0.000 | complejidad_alta:20, densidad_estable:12, frontera_temporal:1, temporal_scale_stability:20, tipo_unico:17, velocidad_constante:20 |
| rule_18 | atlas | 0 | 0 | 42 | 8 | 0.000 | complejidad_alta:29, densidad_estable:4, temporal_scale_stability:1, tipo_unico:27, velocidad_constante:42 |
| rule_46 | atlas | 0 | 0 | 50 | 0 | 0.000 | complejidad_alta:49, densidad_estable:48, frontera_temporal:41, temporal_scale_stability:50, tipo_unico:47, velocidad_constante:50 |
| rule_51 | known_periodic | 50 | 50 | 50 | 0 | 42.920 | complejidad_alta:50, densidad_estable:31, periodicidad:50, temporal_scale_stability:50, tipo_unico:50 |
| rule_54 | atlas | 0 | 0 | 40 | 10 | 0.000 | complejidad_alta:40, densidad_estable:2, temporal_scale_stability:36, velocidad_constante:22 |
| rule_57 | known_periodic | 0 | 0 | 50 | 0 | 0.000 | complejidad_alta:50, densidad_estable:50, temporal_scale_stability:50, velocidad_constante:13 |
| rule_90 | atlas | 0 | 0 | 50 | 0 | 0.000 | velocidad_constante:7 |
| rule_109 | atlas | 0 | 0 | 50 | 0 | 0.000 | complejidad_alta:45, densidad_estable:48, frontera_temporal:38, temporal_scale_stability:26, tipo_unico:6, velocidad_constante:4 |
| rule_110 | atlas | 0 | 0 | 2 | 48 | 0.000 | complejidad_alta:2, densidad_estable:2, frontera_temporal:2, velocidad_constante:2 |
| rule_124 | atlas | 0 | 0 | 16 | 34 | 0.000 | complejidad_alta:16, densidad_estable:16, frontera_temporal:16, velocidad_constante:3 |
| rule_137 | atlas | 0 | 0 | 2 | 48 | 0.000 | complejidad_alta:2, densidad_estable:2, frontera_temporal:2 |
| rule_208 | atlas | 0 | 0 | 50 | 0 | 0.000 | complejidad_alta:49, densidad_estable:50, frontera_temporal:41, temporal_scale_stability:50, tipo_unico:50, velocidad_constante:50 |
| rule_209 | atlas | 0 | 0 | 48 | 2 | 0.000 | complejidad_alta:47, densidad_estable:48, frontera_temporal:41, temporal_scale_stability:48, tipo_unico:47, velocidad_constante:48 |

## First Periodicity Hits

| world | seed | oscillator_count_raw | analysis_status | periodicity_raw | periodicity_production | laws_accepted |
| --- | --- | --- | --- | --- | --- | --- |
| rule_51 | 20260523 | 43 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260524 | 51 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260525 | 43 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260526 | 43 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260527 | 41 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260528 | 39 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260529 | 47 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260530 | 47 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260531 | 47 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260532 | 53 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260533 | 41 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260534 | 37 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260535 | 43 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260536 | 49 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260537 | 45 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260538 | 39 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260539 | 43 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260540 | 51 | ok | yes | yes | periodicidad, densidad_estable, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260541 | 43 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |
| rule_51 | 20260542 | 35 | ok | yes | yes | periodicidad, tipo_unico, complejidad_alta, temporal_scale_stability |

## Answer

Atlas ECA worlds still do not activate `periodicidad`, but known periodic ECA rules do. This validates the law on real ECA dynamics rather than only synthetic frames.

## Interpretation

`rule_51` is the decisive positive control: it activates `periodicidad` in
`50/50` random ICs with `analysis_status=ok`. This is real ECA dynamics, not a
synthetic frame fixture. The mechanism is global period-2 complementation, so
the observer emits many `oscilador` structures at once.

The atlas result remains negative: none of the 10 measured atlas ECA rules
activate `periodicidad` under this random-IC protocol. Therefore the law is not
dead, but it belongs to a different ECA family than the current atlas worlds.

`rule_15` and `rule_57` do not activate `periodicidad` here, despite being
periodic-looking candidates. Under the current observer contract, exact
frame-level periodicity is what matters.
