# Fase 76 - Horizon-Period Resonance Audit

## Question

Why does `T_WINDOW=12` produce the `central_t15_like` signal for both
true positives and Fase 72 centrality artefacts, while horizons `8`,
`16`, and `20` do not?

This phase runs no new simulations. It derives horizon/period features
from Fase 74's four-horizon ANF measurements.

## Horizon Signal Counts

| horizon | signal | no_signal |
|---:|---:|---:|
| 12 | 13 | 0 |
| 16 | 0 | 13 |
| 20 | 0 | 13 |
| 8 | 0 | 13 |

## Ratio Buckets

| ratio bucket | signal | no_signal |
|---|---:|---:|
| (1,1.5] | 3 | 4 |
| (1.5,2] | 2 | 6 |
| 1 | 2 | 2 |
| <1 | 0 | 3 |
| >2 | 6 | 24 |

## Signal Rows

| case | horizon | T_local | 12/T or H/T | exact_multiple | positive | slope | R^2 | dist |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rule=109/bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG | 12 | 12 | 1.000 | True | True | -0.298274 | 0.998341 | 0.000 |
| rule=109/bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE | 12 | 8 | 1.500 | False | True | -0.298928 | 0.998276 | 0.000 |
| rule=109/bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE | 12 | 10 | 1.200 | False | True | -0.307674 | 0.999349 | 0.000 |
| rule=109/bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE | 12 | 8 | 1.500 | False | True | -0.298928 | 0.998276 | 0.000 |
| rule=109/bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG | 12 | 12 | 1.000 | True | True | -0.298274 | 0.998341 | 0.000 |
| rule=73/bg=1100/T=3/word=0000001/HORIZON_ARTIFACT | 12 | 3 | 4.000 | True | False | -0.303913 | 0.998717 | 0.000 |
| rule=94/bg=0111/T=3/word=10000010/HORIZON_ARTIFACT | 12 | 3 | 4.000 | True | False | -0.295851 | 0.999961 | 0.000 |
| rule=94/bg=0111/T=6/word=10101000/HORIZON_ARTIFACT | 12 | 6 | 2.000 | True | False | -0.295845 | 0.999958 | 0.000 |
| rule=94/bg=1000/T=3/word=00011010/HORIZON_ARTIFACT | 12 | 3 | 4.000 | True | False | -0.295877 | 0.999967 | 0.000 |
| rule=94/bg=1110/T=3/word=00010111/HORIZON_ARTIFACT | 12 | 3 | 4.000 | True | False | -0.295697 | 0.999989 | 0.000 |
| rule=94/bg=1110/T=6/word=00010101/HORIZON_ARTIFACT | 12 | 6 | 2.000 | True | False | -0.295845 | 0.999958 | 0.000 |
| rule=133/bg=0111/T=3/word=10000011/HORIZON_ARTIFACT | 12 | 3 | 4.000 | True | False | -0.289461 | 0.999224 | 0.000 |
| rule=133/bg=1000/T=3/word=00010011/HORIZON_ARTIFACT | 12 | 3 | 4.000 | True | False | -0.289489 | 0.999305 | 0.000 |

## Interpretation

Verdict: `COMMON_HORIZON_12_PROTOCOL_RESONANCE`.

The central T15-like signature appears exclusively at the original common horizon 12. Within that horizon, positives occupy the low-oversampling band 12/T_local<=1.5, while artefacts occupy short-period exact multiples 12/T_local in {2,4}. The result explains Fase 73 as a protocol resonance, not as a horizon-independent law.

At `T_WINDOW=12`, the same central T15-like signature appears in all 13
centrality candidates. It is therefore not a positive/negative
separator. The split inside horizon 12 is instead:

- positives: ratio range [1.0, 1.5] (`12/T_local <= 1.5`)
- artefacts: ratio range [2.0, 4.0] (`12/T_local >= 2`)

That second bullet is exactly why short-period cases looked like
centrality false positives: `T=3` and `T=6` are exact divisors of the
12-step common window. But exact divisibility is not sufficient either,
because true positives include non-multiple ratios such as `12/8=1.5`
and `12/10=1.2`.

## Methodological Limit

- This audit explains the Fase 72-74 centrality candidates only; it does
  not claim a universal property of all ECA horizons.
- The result identifies a protocol-level resonance at the original common
  horizon 12, not a new physical period-12 law.
- Future work should not use `T_WINDOW=12` as a free discriminator unless
  the horizon is justified independently of the Fase 55 label rule.
