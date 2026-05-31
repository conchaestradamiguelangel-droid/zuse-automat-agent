# Rule 51 Global Periodicity Profile - Fase 15a

Protocol: `steps=96`, `width=64`, seeds `20260523..20260528`.

`rule_51` is `f(a,b,c) = NOT b`: every cell complements itself each step,
independent of neighbors. The resulting period-2 behavior is global and
deterministic for every IC.

## Overview

- Classification: `periodicidad-global`
- ok: `6/6`
- mean_n_laws: `4.500`
- peak_diversity: `0.333`
- mean_dedup_structure_count: `14.000`
- mean_transition_rate: `1.000`
- mean_entropy: `0.986`

## Law Frequencies

| law | count | class |
| --- | --- | --- |
| velocidad_constante | 0/6 | absent |
| periodicidad | 6/6 | core |
| densidad_estable | 3/6 | present |
| tipo_unico | 6/6 | core |
| complejidad_alta | 6/6 | core |
| frontera_temporal | 0/6 | absent |
| temporal_scale_stability | 6/6 | core |

## Signatures

{
  "periodicidad + tipo_unico + complejidad_alta + temporal_scale_stability": 3,
  "periodicidad + densidad_estable + tipo_unico + complejidad_alta + temporal_scale_stability": 3
}

## Interpretation

This validates `periodicidad` on real ECA dynamics, but not as a local particle
oscillator. It is global frame-level period-2 complementation. The current
observer correctly detects periodicity, but the physical mechanism is distinct
from `synthetic_oscilador` or `life_blinker`.
