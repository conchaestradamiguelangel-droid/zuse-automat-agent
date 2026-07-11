# Fase 54: rule_73/rule_109 Family ANF Robustness

## Question

Does the ANF gradient documented for the T15 mechanism and the non-T15
`rule_109/T=10` witness extend to additional `rule_73/rule_109`
periodic-background witnesses at their own natural periods?

This test reuses the exact 25-input bit-sliced Mobius ANF engine from
Fases 52--53. The primary criterion is the natural-period horizon
`T_WINDOW=T_local`; the common 12-step horizon is reported as a secondary
comparison.

Reference: T15 Fase 45 slope `-0.307283`, R^2 `0.998197`.

## Summary

Status: `ANF_GRADIENT_ISOLATED_WITNESS`.

The selected rule_73/rule_109 witnesses have enough active support, but none reproduces the T15-like gradient at its natural period.

## Case Table

| label | role | rule | background | IC | T_local | T_WINDOW | span | active | dist | degree | monomials | active log fit |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| rule109_bg1011_T6 | same_rule_bg_period_variant | 109 | `1011` | `00001001` | 6 | 6 | 13 | 4 | 3 | [12, 12] | [4261, 4262] | slope=0.000026, R^2=0.604938, delta_vs_T15=99.99%, reliable=yes, comparable=no |
| rule109_bg1011_T6 | same_rule_bg_period_variant | 109 | `1011` | `00001001` | 6 | 12 | 13 | 4 | 3 | [20, 23] | [529108, 4224572] | slope=-0.303174, R^2=0.999487, delta_vs_T15=1.34%, reliable=yes, comparable=yes |
| rule109_bg1101_T10 | same_rule_new_bg | 109 | `1101` | `0001000` | 10 | 10 | 13 | 7 | 4 | [17, 21] | [138594, 1113670] | slope=-0.209698, R^2=0.880488, delta_vs_T15=31.76%, reliable=yes, comparable=no |
| rule109_bg1101_T10 | same_rule_new_bg | 109 | `1101` | `0001000` | 10 | 12 | 13 | 4 | 2 | [20, 23] | [529108, 4224572] | slope=-0.300746, R^2=1.000000, delta_vs_T15=2.13%, reliable=no, comparable=no |
| rule73_bg0010_T6 | rule73_period_variant | 73 | `0010` | `1100111` | 6 | 6 | 13 | 4 | 3 | [12, 12] | [4097, 4098] | slope=-0.000027, R^2=0.604938, delta_vs_T15=99.99%, reliable=yes, comparable=no |
| rule73_bg0010_T6 | rule73_period_variant | 73 | `0010` | `1100111` | 6 | 12 | 13 | 4 | 3 | [20, 23] | [482356, 4474733] | slope=-0.320463, R^2=0.999687, delta_vs_T15=4.29%, reliable=yes, comparable=yes |

## Natural-Period Reading

- `rule109_bg1011_T6`: slope=0.000026, R^2=0.604938, delta_vs_T15=99.99%, reliable=yes, comparable=no.
- `rule109_bg1101_T10`: slope=-0.209698, R^2=0.880488, delta_vs_T15=31.76%, reliable=yes, comparable=no.
- `rule73_bg0010_T6`: slope=-0.000027, R^2=0.604938, delta_vs_T15=99.99%, reliable=yes, comparable=no.

## Interpretation

The robustness claim is evaluated at each oscillator's own period. A
T15-like slope that appears only at the common 12-step horizon is treated
as secondary evidence, not as proof that the natural-period mechanism
itself obeys the same law.
