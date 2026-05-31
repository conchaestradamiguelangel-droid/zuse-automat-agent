# Local Oscillator Search - Fase 16

## Setup

- Candidate rules: ECA rules with `f(0,0,0)=0`.
- Exclusions: atlas rules `rule_18, rule_30, rule_46, rule_51, rule_54, rule_90, rule_109, rule_110, rule_124, rule_137, rule_150, rule_208, rule_209` and trivial rules `rule_0, rule_2, rule_4`.
- Candidate count: `116` rules.
- ICs: `point`, `pair_gap1`, `triple` on all-zero background.
- Width: `128`.
- Steps: `200`.
- Minimum survival: `50` steps.
- Production noise gate: `dedup_structure_count > 40`.

`periodicity_raw` means at least one observer emitted `tipo=oscilador`.
`periodicity_production` means the cycle was not noise-gated and
`periodicidad` appeared in `laws_accepted`.

A genuine local candidate requires:

- at least one oscillator structure,
- survival for at least `50` steps,
- bounded late growth (`span` and active-cell count stable within `4` cells),
- no reliance on a changing non-quiescent background.

## Result

Found 2 local-oscillator candidates under the minimal quiescent-background protocol.

Rows evaluated: `348`.
Raw periodic hits: `2`.
Production periodic hits: `2`.
Interesting local candidates: `2`.

## Rules With Periodicity Hits

| world | periodicity_raw/3 | periodicity_production/3 | interesting/3 | ok/3 | laws_frequency |
| --- | --- | --- | --- | --- | --- |
| rule_108 | 2 | 2 | 2 | 3 | densidad_estable:1, periodicidad:2, tipo_unico:3 |

## First Periodicity Hit Details

| world | ic_type | analysis_status | oscillator_count_raw | periodicity_production | survival_steps | final_span | bounded | interesting | laws_accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rule_108 | pair_gap1 | ok | 5 | yes | 200 | 3 | yes | yes | periodicidad, tipo_unico |
| rule_108 | triple | ok | 5 | yes | 200 | 3 | yes | yes | periodicidad, tipo_unico |

## Interpretation

This sweep isolates the hardest version of the periodicity question: a local
oscillator on a stable zero background, seeded by at most three active cells.
It deliberately excludes `rule_51`, because Fase 15 already showed that
`rule_51` is global period-2 complementation rather than a local particle.

The positive case is `rule_108`. From both `pair_gap1`
and `triple` ICs, it converges immediately to the stationary period-2 motif
`#.# <-> ###` on an all-zero background. The active region remains localized
with span <= 3 for 200 steps, and the production pipeline accepts
`periodicidad`.

This is qualitatively different from `rule_51`: `rule_51` is global
period-2 complementation, while `rule_108` contains a genuine local oscillator
particle on a quiescent background. Therefore `periodicidad` now has an ECA
local-particle witness, not only synthetic/Life witnesses and a global ECA
witness.
