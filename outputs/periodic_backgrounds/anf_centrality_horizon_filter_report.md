# Fase 73: ANF Centrality Horizon Filter

## Question

Can the eight external false positives from Fase 72 be explained as
short-period / oversampled-horizon artefacts?

This phase tests the cheap second filter first: combine ANF centrality
(`max_active_monomial_dist=0`) with a sufficient local period under the
common horizon `T_WINDOW=12`.

## Centrality Candidates

These are all cases with `max_active_monomial_dist=0` in the full Fase 55
census.

| case | positive | T | ratio | category | R2 | slope | dist classes | max dist |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| `rule=73/bg=1100/T=3/word=0000001/HORIZON_ARTIFACT` | `False` | 3 | 4.000 | `HORIZON_ARTIFACT` | 0.998717 | -0.303913 | 5 | 0.0 |
| `rule=94/bg=0111/T=3/word=10000010/HORIZON_ARTIFACT` | `False` | 3 | 4.000 | `HORIZON_ARTIFACT` | 0.999961 | -0.295851 | 6 | 0.0 |
| `rule=94/bg=0111/T=6/word=10101000/HORIZON_ARTIFACT` | `False` | 6 | 2.000 | `HORIZON_ARTIFACT` | 0.999958 | -0.295845 | 5 | 0.0 |
| `rule=94/bg=1000/T=3/word=00011010/HORIZON_ARTIFACT` | `False` | 3 | 4.000 | `HORIZON_ARTIFACT` | 0.999967 | -0.295877 | 6 | 0.0 |
| `rule=94/bg=1110/T=3/word=00010111/HORIZON_ARTIFACT` | `False` | 3 | 4.000 | `HORIZON_ARTIFACT` | 0.999989 | -0.295697 | 5 | 0.0 |
| `rule=94/bg=1110/T=6/word=00010101/HORIZON_ARTIFACT` | `False` | 6 | 2.000 | `HORIZON_ARTIFACT` | 0.999958 | -0.295845 | 5 | 0.0 |
| `rule=109/bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG` | `True` | 12 | 1.000 | `NATURAL_PERIOD_STRONG` | 0.998341 | -0.298274 | 5 | 0.0 |
| `rule=109/bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `True` | 8 | 1.500 | `HORIZON_ACCEPTABLE` | 0.998276 | -0.298928 | 5 | 0.0 |
| `rule=109/bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE` | `True` | 10 | 1.200 | `HORIZON_ACCEPTABLE` | 0.999349 | -0.307674 | 4 | 0.0 |
| `rule=109/bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE` | `True` | 8 | 1.500 | `HORIZON_ACCEPTABLE` | 0.998276 | -0.298928 | 5 | 0.0 |
| `rule=109/bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG` | `True` | 12 | 1.000 | `NATURAL_PERIOD_STRONG` | 0.998341 | -0.298274 | 5 | 0.0 |
| `rule=133/bg=0111/T=3/word=10000011/HORIZON_ARTIFACT` | `False` | 3 | 4.000 | `HORIZON_ARTIFACT` | 0.999224 | -0.289461 | 6 | 0.0 |
| `rule=133/bg=1000/T=3/word=00010011/HORIZON_ARTIFACT` | `False` | 3 | 4.000 | `HORIZON_ARTIFACT` | 0.999305 | -0.289489 | 6 | 0.0 |

## Period/Horizon Split

- Centrality only: `TP=5, FP=8, TN=53, FN=0, accuracy=0.879, precision=0.385, recall=1.000`
- Centrality + `T_local >= 8`: `TP=5, FP=0, TN=61, FN=0, accuracy=1.000, precision=1.000, recall=1.000`
- Centrality + `12/T_local <= 1.5`: `TP=5, FP=0, TN=61, FN=0, accuracy=1.000, precision=1.000, recall=1.000`

The centrality false positives are all short-period cases:

- `T_local=3`: `6` false positives
- `T_local=6`: `2` false positives

The true positives are all sufficient-horizon cases:

- `T_local=8`: `2` true positives
- `T_local=10`: `1` true positives
- `T_local=12`: `2` true positives

## Threshold Scan

- Perfect rules: `2`.
- Best accuracy rule: `centrality AND T_local >= 8` (TP=5, FP=0, TN=61, FN=0, accuracy=1.000, precision=1.000, recall=1.000).

Top scanned rules:

- `centrality AND T_local >= 8`: TP=5, FP=0, TN=61, FN=0, accuracy=1.000, precision=1.000, recall=1.000
- `centrality AND oversampling_ratio <= 1.5`: TP=5, FP=0, TN=61, FN=0, accuracy=1.000, precision=1.000, recall=1.000
- `centrality AND T_local >= 10`: TP=3, FP=0, TN=61, FN=2, accuracy=0.970, precision=1.000, recall=0.600
- `centrality AND oversampling_ratio <= 1.2`: TP=3, FP=0, TN=61, FN=2, accuracy=0.970, precision=1.000, recall=0.600
- `centrality AND T_local >= 12`: TP=2, FP=0, TN=61, FN=3, accuracy=0.955, precision=1.000, recall=0.400
- `centrality AND oversampling_ratio <= 1.0`: TP=2, FP=0, TN=61, FN=3, accuracy=0.955, precision=1.000, recall=0.400
- `centrality AND R2 >= 1.0`: TP=0, FP=0, TN=61, FN=5, accuracy=0.924, precision=0.000, recall=0.000
- `centrality AND R2 >= 0.9999690787708423`: TP=0, FP=1, TN=60, FN=5, accuracy=0.909, precision=0.000, recall=0.000
- `centrality AND R2 >= 0.9999889688516735`: TP=0, FP=1, TN=60, FN=5, accuracy=0.909, precision=0.000, recall=0.000
- `centrality AND T_local >= 4`: TP=5, FP=2, TN=59, FN=0, accuracy=0.970, precision=0.714, recall=1.000

## Verdict

`CENTRALITY_HORIZON_FILTER_SEPARATES`.

The second filter is horizon sufficiency: centrality plus T_local>=8 (equivalently 12/T_local<=1.5 in this census) separates all positives from all non-positives.

The Fase 72 centrality false positives are not random failures of the
centrality metric. They are short-period centrality artefacts: six have
`T_local=3` and two have `T_local=6`. Adding the horizon sufficiency
condition `T_local>=8` removes all eight false positives while preserving
all five observed positives.

## Methodological Limit

- This is still a validation over the Fase 55 census, not all ECA rules.
- All observed positives remain rule_109 cases, so external recall is not
  tested.
- The filter is evaluated at common horizon `T_WINDOW=12`; natural-period
  centrality would be a separate audit.
- No paper or DOI metadata is changed by this phase.
