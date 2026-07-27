# Fase 74 - Independent Horizon Audit for ANF Centrality

## Question

Does exact ANF centrality remain a discriminator when the horizon is varied,
without reusing `T_local>=8` as the classifier that originally split
`HORIZON_ACCEPTABLE` from `HORIZON_ARTIFACT`?

The audit remeasures the 13 Fase 72 centrality candidates at horizons
`8`, `12`, `16`, and `20`. A case is marked `central_t15_like` at a
horizon only when both conditions hold:

- `max_active_monomial_dist == 0`
- the active-output log-monomial fit is comparable to the T15 baseline
  under the same slope/R^2 rule used by Fase 55

## Candidate Table

| case | cat | pos | T | h8 | h12 | h16 | h20 | count |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rule=109/bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG | NATURAL_PERIOD_STRONG | True | 12 | no | yes | no | no | 1 |
| rule=109/bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE | HORIZON_ACCEPTABLE | True | 8 | no | yes | no | no | 1 |
| rule=109/bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE | HORIZON_ACCEPTABLE | True | 10 | no | yes | no | no | 1 |
| rule=109/bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE | HORIZON_ACCEPTABLE | True | 8 | no | yes | no | no | 1 |
| rule=109/bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG | NATURAL_PERIOD_STRONG | True | 12 | no | yes | no | no | 1 |
| rule=73/bg=1100/T=3/word=0000001/HORIZON_ARTIFACT | HORIZON_ARTIFACT | False | 3 | no | yes | no | no | 1 |
| rule=94/bg=0111/T=3/word=10000010/HORIZON_ARTIFACT | HORIZON_ARTIFACT | False | 3 | no | yes | no | no | 1 |
| rule=94/bg=0111/T=6/word=10101000/HORIZON_ARTIFACT | HORIZON_ARTIFACT | False | 6 | no | yes | no | no | 1 |
| rule=94/bg=1000/T=3/word=00011010/HORIZON_ARTIFACT | HORIZON_ARTIFACT | False | 3 | no | yes | no | no | 1 |
| rule=94/bg=1110/T=3/word=00010111/HORIZON_ARTIFACT | HORIZON_ARTIFACT | False | 3 | no | yes | no | no | 1 |
| rule=94/bg=1110/T=6/word=00010101/HORIZON_ARTIFACT | HORIZON_ARTIFACT | False | 6 | no | yes | no | no | 1 |
| rule=133/bg=0111/T=3/word=10000011/HORIZON_ARTIFACT | HORIZON_ARTIFACT | False | 3 | no | yes | no | no | 1 |
| rule=133/bg=1000/T=3/word=00010011/HORIZON_ARTIFACT | HORIZON_ARTIFACT | False | 3 | no | yes | no | no | 1 |

## Rule Tests

| rule | confusion |
|---|---:|
| horizon_8_central_t15_like | TP=0 FP=0 TN=8 FN=5 acc=0.615 prec=0.000 rec=0.000 |
| horizon_12_central_t15_like | TP=5 FP=8 TN=0 FN=0 acc=0.385 prec=0.385 rec=1.000 |
| horizon_16_central_t15_like | TP=0 FP=0 TN=8 FN=5 acc=0.615 prec=0.000 rec=0.000 |
| horizon_20_central_t15_like | TP=0 FP=0 TN=8 FN=5 acc=0.615 prec=0.000 rec=0.000 |
| all_horizons_central_t15_like | TP=0 FP=0 TN=8 FN=5 acc=0.615 prec=0.000 rec=0.000 |
| independent_horizons_8_16_20_central_t15_like | TP=0 FP=0 TN=8 FN=5 acc=0.615 prec=0.000 rec=0.000 |
| at_least_3_horizons_central_t15_like | TP=0 FP=0 TN=8 FN=5 acc=0.615 prec=0.000 rec=0.000 |

Horizon-wise central T15-like counts:

| horizon | positives | artefacts |
|---:|---:|---:|
| 8 | 0 | 0 |
| 12 | 5 | 8 |
| 16 | 0 | 0 |
| 20 | 0 | 0 |

## Persistence Counts

Positive candidates:

- rule=109/bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG: 1/4 horizons [12]
- rule=109/bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE: 1/4 horizons [12]
- rule=109/bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE: 1/4 horizons [12]
- rule=109/bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE: 1/4 horizons [12]
- rule=109/bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG: 1/4 horizons [12]

Centrality artefacts:

- rule=73/bg=1100/T=3/word=0000001/HORIZON_ARTIFACT: 1/4 horizons [12]
- rule=94/bg=0111/T=3/word=10000010/HORIZON_ARTIFACT: 1/4 horizons [12]
- rule=94/bg=0111/T=6/word=10101000/HORIZON_ARTIFACT: 1/4 horizons [12]
- rule=94/bg=1000/T=3/word=00011010/HORIZON_ARTIFACT: 1/4 horizons [12]
- rule=94/bg=1110/T=3/word=00010111/HORIZON_ARTIFACT: 1/4 horizons [12]
- rule=94/bg=1110/T=6/word=00010101/HORIZON_ARTIFACT: 1/4 horizons [12]
- rule=133/bg=0111/T=3/word=10000011/HORIZON_ARTIFACT: 1/4 horizons [12]
- rule=133/bg=1000/T=3/word=00010011/HORIZON_ARTIFACT: 1/4 horizons [12]

## Verdict

`CENTRALITY_HORIZON_DEPENDENT`.

The central T15-like signal appears only at the original common horizon 12 for both positives and centrality artefacts. It does not survive as an independent-horizon discriminator; Fase 73 remains a descriptive consistency check rather than a non-circular validation.

Best rule: `horizon_12_central_t15_like` -> TP=5 FP=8 TN=0 FN=0 acc=0.385 prec=0.385 rec=1.000.

## Methodological Limit

- This is still limited to the 13 exact-centrality candidates from Fase 72.
- Positives outside rule_109 remain untestable because the Fase 55 census contains none.
- The audit avoids using `T_local>=8` as a classifier, but still evaluates against
  the Fase 55 category labels for bookkeeping.
- Recomputing larger horizons is not a universal ECA proof; it is a non-circular
  stress test of the Fase 73 descriptive split.
