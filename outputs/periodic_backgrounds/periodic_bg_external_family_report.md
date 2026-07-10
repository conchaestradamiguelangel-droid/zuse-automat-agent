# Fase 53: External-Family Periodic Background ANF Test

## Question

Does the T15-like ANF gradient appear in periodic-background oscillators
outside the `rule_73/rule_109` family, and does it appear at the natural
period rather than only after oversampling to `T_WINDOW=12`?

All cases use the same 25-input bit-sliced Mobius ANF engine as Fase 52.
The selected ICs are the shortest catalog witnesses at the maximum wide
support (`span=11`) for each `(rule, background, T_local)` group.

Reference: T15 Fase 45 slope `-0.307283`, R^2 `0.998197`.

## Summary

Status: `ANF_GRADIENT_FAMILY_73_109`.

None of the external non-73/109 candidates reproduces the T15-like ANF gradient at its own period or at the common horizon.

## Case Table

| label | rule | background | IC | T_local | T_WINDOW | active | dist | degree | monomials | active log fit |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| external_rule54_T4 | 54 | `0010` | `1000001` | 4 | 4 | 4 | 2 | [7, 7] | [184, 185] | slope=-0.002354, R^2=1.000000, delta_vs_T15=99.23%, reliable=no, comparable=no |
| external_rule54_T4 | 54 | `0010` | `1000001` | 4 | 12 | 4 | 2 | [21, 21] | [1589144, 3279330] | slope=-0.314622, R^2=1.000000, delta_vs_T15=2.39%, reliable=no, comparable=no |
| external_rule94_T6 | 94 | `0001` | `0100010` | 6 | 6 | 8 | 4 | [12, 12] | [3794, 3795] | slope=0.000000, R^2=0.000000, delta_vs_T15=100.00%, reliable=yes, comparable=no |
| external_rule94_T6 | 94 | `0001` | `0100010` | 6 | 12 | 8 | 4 | [20, 24] | [524352, 15830595] | slope=-0.295750, R^2=0.897666, delta_vs_T15=3.75%, reliable=yes, comparable=no |
| external_rule133_T6 | 133 | `1011` | `100100` | 6 | 6 | 8 | 4 | [12, 12] | [3234, 3235] | slope=0.000000, R^2=0.000000, delta_vs_T15=100.00%, reliable=yes, comparable=no |
| external_rule133_T6 | 133 | `1011` | `100100` | 6 | 12 | 8 | 4 | [19, 24] | [523418, 13958114] | slope=-0.281419, R^2=0.895001, delta_vs_T15=8.42%, reliable=yes, comparable=no |

## Interpretation

The distinction between natural-period and common-horizon measurements is
central. A gradient that appears only at `T_WINDOW=12` is treated as a
horizon effect, not as direct evidence that the oscillator's own period
has the same algebraic law as the T15 mechanism.
