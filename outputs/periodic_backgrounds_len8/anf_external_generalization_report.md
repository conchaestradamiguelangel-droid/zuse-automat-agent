# Fase 49: External ANF Gradient Generalization

## Question

Fases 44-45 established the ANF degree gradient on the original length-8
`T=15` representatives. Fase 49 tests whether the same structure appears
on the external length-9/10 `T=15` backgrounds found in Fase 34.

The analysis reuses the exact 25-input, 12-step bit-packed cone and Mobius
ANF transform from Fase 44. The external backgrounds are not rotations of
the original length-8 set.

## Summary

Status: `ANF_GRADIENT_GENERALIZES`.

- Target external backgrounds: 8
- Replay-verified T=15 backgrounds: 8
- Failed replay backgrounds: 0
- Active outputs analyzed: 63
- Active degree range: 16..24
- Active monomial range: 39665..17758051
- Epsilon counts: `{'0': 39, '1': 24}`
- Epsilon-band exceptions: 0 (0.00%)

## Log-monomial fit

`log10(monomials) = a + slope * dist`

- External intercept `a`: 7.224069
- External slope: -0.302890
- External slope magnitude: 0.302890
- External R^2: 0.998263
- Length-8 reference intercept: 7.241925
- Length-8 reference slope magnitude: 0.307283
- Intercept delta vs length-8: 0.25%
- Slope delta vs length-8: 1.43%

## Representative table

| length | rule | background | IC | detections | replay | active outputs | degree | epsilon | monomials |
| ---: | ---: | --- | --- | ---: | --- | ---: | --- | --- | --- |
| 9 | 73 | `001110101` | `0111011` | 6 | `True` | 7 | 19..24 | 0..1 | 240508..15954882 |
| 10 | 73 | `0000001001` | `10000001` | 9 | `True` | 6 | 17..21 | 0..1 | 107103..2028466 |
| 10 | 73 | `0000111001` | `00000011` | 3 | `True` | 8 | 18..23 | 0..1 | 255533..8444922 |
| 10 | 73 | `0000111011` | `00000011` | 3 | `True` | 8 | 18..23 | 0..1 | 255533..8444922 |
| 10 | 73 | `0010111011` | `0000111` | 27 | `True` | 10 | 17..24 | 0..1 | 57252..15954882 |
| 10 | 73 | `0011011101` | `0001001` | 25 | `True` | 8 | 16..24 | 0..1 | 39665..15954881 |
| 10 | 109 | `0000000011` | `0100001` | 14 | `True` | 8 | 19..24 | 0..1 | 276546..17758051 |
| 10 | 109 | `0011111011` | `1001111` | 3 | `True` | 8 | 17..24 | 0..1 | 141326..17758051 |

## Interpretation

The ANF gradient generalizes to the external length-9/10 `T=15`
backgrounds under the tested criteria. The epsilon band remains exact
and the log-monomial slope stays within the predefined tolerance of the
length-8 reference.

Note: the Fase 34 external witnesses have varying active defect widths,
so Fase 49 does not assume a constant visual defect width. The 25-cell
cone is fixed by the radius-1, 12-step causal horizon.
