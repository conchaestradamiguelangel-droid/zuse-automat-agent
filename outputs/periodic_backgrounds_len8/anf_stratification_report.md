# Fase 45: ANF Stratification Laws of the T=15 Cone

## Question

Fase 44 found mixed ANF complexity: active outputs have degrees 14..24
and monomial counts ranging from thousands to tens of millions. Fase 45
asks whether that variation is structured.

No new simulation is performed. This analysis loads
`anf_degree_results.json` and analyzes the 174 active outputs.

## Summary

Status: `ANF_GRADIENT_LAWS_CONFIRMED`.

### Law 1: ANF degree gradient

- Formula tested: `degree = 24 - abs(rel_pos) + epsilon, epsilon in {0,1}`
- Exceptions outside epsilon {0,1}: 0/174
- Epsilon counts: {0: 116, 1: 58}
- Pearson r(|rel_pos|, degree): -0.984525
- Linear fit degree ~= 24.093185 + -0.942523 * dist; R^2=0.969289
- Degree-24 cap holds: `True` (max degree 24)

### Law 2: monomial-count exponential decay

- Pearson r(|rel_pos|, log10(monomials)): -0.999098
- Linear fit log10(monomials) ~= 7.241925 + -0.307283 * dist; R^2=0.998197
- Difference from -log10(2): -0.006253

## Distance table

| dist | n | degree | epsilon 0/1 | mean log10(monomials) | log10 range |
| ---: | ---: | --- | --- | ---: | --- |
| 0 | 13 | 24..24 | 13/0 | 7.232 | 7.203..7.249 |
| 1 | 20 | 23..23 | 20/0 | 6.926 | 6.879..6.970 |
| 2 | 22 | 22..23 | 18/4 | 6.626 | 6.614..6.653 |
| 3 | 26 | 21..22 | 16/10 | 6.325 | 6.291..6.347 |
| 4 | 15 | 20..21 | 11/4 | 6.019 | 6.001..6.041 |
| 5 | 17 | 19..20 | 6/11 | 5.710 | 5.683..5.742 |
| 6 | 21 | 18..19 | 8/13 | 5.407 | 5.366..5.480 |
| 7 | 19 | 17..18 | 12/7 | 5.098 | 5.030..5.159 |
| 8 | 12 | 16..17 | 7/5 | 4.793 | 4.727..4.888 |
| 9 | 5 | 15..16 | 2/3 | 4.473 | 4.373..4.598 |
| 10 | 4 | 14..15 | 3/1 | 4.077 | 3.972..4.182 |

## Epsilon characterization

Epsilon is the residual in `degree = 24 - dist + epsilon`.

### By sign

| sign | total | epsilon=0 | epsilon=1 | epsilon=1 rate |
| --- | ---: | ---: | ---: | ---: |
| `C` | 13 | 13 | 0 | 0.000 |
| `L` | 87 | 55 | 32 | 0.368 |
| `R` | 74 | 48 | 26 | 0.351 |

### By rule

| rule | total | epsilon=0 | epsilon=1 | epsilon=1 rate |
| --- | ---: | ---: | ---: | ---: |
| `109` | 94 | 59 | 35 | 0.372 |
| `73` | 80 | 57 | 23 | 0.287 |

## Left/right symmetry

- Matched left/right pairs: 30
- Same degree: 16/30 (0.533)
- Same epsilon: 16/30 (0.533)

## Interpretation

The ANF variation from Fase 44 is highly structured. Degree is almost a
linear function of distance from the cone center, with zero violations
outside a one-bit epsilon band. Monomial counts decay almost exactly
exponentially with distance, with slope close to -log10(2). The cone is
therefore not algebraically uniform: it has a spatial complexity
gradient centered on the active defect.
