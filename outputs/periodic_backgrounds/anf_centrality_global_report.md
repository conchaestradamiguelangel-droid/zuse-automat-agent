# Fase 72: ANF Centrality Discriminator Global Check

## Question

Does the Fase 71 centrality discriminator
`max_active_monomial_dist <= 0.0` remain valid outside the 17-case
`rule_109` subcatalogue?

This phase uses the full Fase 55 census at the common horizon
`T_WINDOW=12`. It does not touch the paper, DOI metadata, tags, or
release state.

## Critical Data Limitation

All five positive cases in the Fase 55 census are `rule_109` cases.
The other rules contain no `NATURAL_PERIOD_STRONG` or
`HORIZON_ACCEPTABLE` cases. Therefore this phase can test whether the
centrality rule creates false positives outside `rule_109`, but it
cannot test recall on non-`rule_109` positives.

## Census Coverage

- Cases: `66`
- Rules: `[54, 73, 94, 109, 133, 147]`
- Positives: `5`
- Non-positives: `61`
- External non-rule_109 cases: `49`
- External positives: `0`

Category counts by rule:

| rule | NATURAL_PERIOD_STRONG | HORIZON_ACCEPTABLE | HORIZON_ARTIFACT | NEGATIVE | INSUFFICIENT_SUPPORT |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 54 | 0 | 0 | 2 | 1 | 1 |
| 73 | 0 | 0 | 7 | 9 | 1 |
| 94 | 0 | 0 | 5 | 7 | 0 |
| 109 | 2 | 3 | 2 | 10 | 0 |
| 133 | 0 | 0 | 2 | 10 | 0 |
| 147 | 0 | 0 | 2 | 1 | 1 |

## Centrality Rule

- Full census: `TP=5, FP=8, TN=53, FN=0, accuracy=0.879, precision=0.385, recall=1.000`
- rule_109 only: `TP=5, FP=0, TN=12, FN=0, accuracy=1.000, precision=1.000, recall=1.000`
- non-rule_109 only: `TP=0, FP=8, TN=41, FN=0, accuracy=0.837, precision=0.000, recall=0.000`

## Case Table

| case | positive | max active monomial dist | R2 | slope | active | dist classes |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `rule=54/bg=0010/T=4/word=1000001/INSUFFICIENT_SUPPORT` | `False` | 2.0 | 1.000000 | -0.314622 | 4 | 2 |
| `rule=54/bg=0100/T=4/word=10000001/NEGATIVE` | `False` | 2.5 | 0.669022 | -0.257629 | 4 | 3 |
| `rule=54/bg=1011/T=4/word=00000001/HORIZON_ARTIFACT` | `False` | 2.0 | 0.999935 | -0.310719 | 8 | 4 |
| `rule=54/bg=1101/T=4/word=0001000/HORIZON_ARTIFACT` | `False` | 2.0 | 0.999935 | -0.310719 | 8 | 4 |
| `rule=73/bg=0010/T=6/word=1100111/HORIZON_ARTIFACT` | `False` | 2.0 | 0.999687 | -0.320463 | 4 | 3 |
| `rule=73/bg=0010/T=10/word=1110111/NEGATIVE` | `False` | 2.0 | 1.000000 | -0.322466 | 4 | 2 |
| `rule=73/bg=0011/T=3/word=10000000/HORIZON_ARTIFACT` | `False` | 0.5 | 0.952909 | -0.307493 | 6 | 3 |
| `rule=73/bg=0011/T=6/word=10000100/HORIZON_ARTIFACT` | `False` | 2.0 | 0.998642 | -0.315036 | 5 | 4 |
| `rule=73/bg=0011/T=8/word=10011100/NEGATIVE` | `False` | 0.5 | 0.929362 | -0.294933 | 8 | 5 |
| `rule=73/bg=0011/T=10/word=10111110/NEGATIVE` | `False` | 0.5 | 0.910209 | -0.293199 | 7 | 5 |
| `rule=73/bg=0011/T=12/word=10001010/NEGATIVE` | `False` | 2.5 | 0.877281 | -0.296180 | 7 | 5 |
| `rule=73/bg=0100/T=6/word=11001110/HORIZON_ARTIFACT` | `False` | 2.0 | 0.999687 | -0.320463 | 4 | 3 |
| `rule=73/bg=0100/T=10/word=11101110/NEGATIVE` | `False` | 2.0 | 1.000000 | -0.322466 | 4 | 2 |
| `rule=73/bg=1001/T=3/word=100001/INSUFFICIENT_SUPPORT` | `False` | 3.5 | 0.498975 | -0.297793 | 4 | 2 |
| `rule=73/bg=1001/T=6/word=1001000/HORIZON_ARTIFACT` | `False` | 3.0 | 0.998101 | -0.305386 | 4 | 3 |
| `rule=73/bg=1001/T=8/word=1001110/NEGATIVE` | `False` | 0.5 | 0.929362 | -0.294933 | 8 | 5 |
| `rule=73/bg=1100/T=3/word=0000001/HORIZON_ARTIFACT` | `False` | 0.0 | 0.998717 | -0.303913 | 6 | 5 |
| `rule=73/bg=1100/T=6/word=0001001/HORIZON_ARTIFACT` | `False` | 3.0 | 0.998101 | -0.305386 | 4 | 3 |
| `rule=73/bg=1100/T=8/word=0011111/NEGATIVE` | `False` | 1.0 | 0.760150 | -0.278180 | 6 | 5 |
| `rule=73/bg=1100/T=10/word=01100011/NEGATIVE` | `False` | 0.5 | 0.921729 | -0.311475 | 6 | 4 |
| `rule=73/bg=1100/T=12/word=00000011/NEGATIVE` | `False` | 0.5 | 0.938004 | -0.312019 | 8 | 5 |
| `rule=94/bg=0001/T=3/word=0110100/NEGATIVE` | `False` | 0.5 | 0.900856 | -0.304510 | 9 | 5 |
| `rule=94/bg=0001/T=6/word=0100010/NEGATIVE` | `False` | 0.5 | 0.897666 | -0.295750 | 8 | 4 |
| `rule=94/bg=0010/T=3/word=1000101/NEGATIVE` | `False` | 0.5 | 0.955626 | -0.341994 | 8 | 6 |
| `rule=94/bg=0010/T=6/word=100010/NEGATIVE` | `False` | 0.5 | 0.897666 | -0.295750 | 8 | 4 |
| `rule=94/bg=0100/T=3/word=10001001/NEGATIVE` | `False` | 0.5 | 0.955626 | -0.341994 | 8 | 6 |
| `rule=94/bg=0100/T=6/word=010001/NEGATIVE` | `False` | 0.5 | 0.896744 | -0.295663 | 8 | 4 |
| `rule=94/bg=0111/T=3/word=10000010/HORIZON_ARTIFACT` | `False` | 0.0 | 0.999961 | -0.295851 | 9 | 6 |
| `rule=94/bg=0111/T=6/word=10101000/HORIZON_ARTIFACT` | `False` | 0.0 | 0.999958 | -0.295845 | 8 | 5 |
| `rule=94/bg=1000/T=3/word=00011010/HORIZON_ARTIFACT` | `False` | 0.0 | 0.999967 | -0.295877 | 9 | 6 |
| `rule=94/bg=1000/T=6/word=00010001/NEGATIVE` | `False` | 0.5 | 0.903308 | -0.285650 | 8 | 5 |
| `rule=94/bg=1110/T=3/word=00010111/HORIZON_ARTIFACT` | `False` | 0.0 | 0.999989 | -0.295697 | 7 | 5 |
| `rule=94/bg=1110/T=6/word=00010101/HORIZON_ARTIFACT` | `False` | 0.0 | 0.999958 | -0.295845 | 8 | 5 |
| `rule=109/bg=0011/T=3/word=0001100/NEGATIVE` | `False` | 0.5 | 0.933294 | -0.302580 | 6 | 3 |
| `rule=109/bg=0011/T=6/word=1100100/NEGATIVE` | `False` | 1.5 | 0.930073 | -0.292946 | 7 | 5 |
| `rule=109/bg=0011/T=8/word=1000010/NEGATIVE` | `False` | 0.5 | 0.924473 | -0.310312 | 8 | 5 |
| `rule=109/bg=0011/T=10/word=10000010/NEGATIVE` | `False` | 0.5 | 0.899808 | -0.276202 | 7 | 5 |
| `rule=109/bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG` | `True` | 0.0 | 0.998341 | -0.298274 | 7 | 5 |
| `rule=109/bg=0110/T=3/word=001100/NEGATIVE` | `False` | 0.5 | 0.933294 | -0.302580 | 6 | 3 |
| `rule=109/bg=0110/T=6/word=0010011/NEGATIVE` | `False` | 0.5 | 0.941622 | -0.313891 | 7 | 5 |
| `rule=109/bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `True` | 0.0 | 0.998276 | -0.298928 | 6 | 5 |
| `rule=109/bg=1011/T=6/word=00001001/HORIZON_ARTIFACT` | `False` | 2.0 | 0.999487 | -0.303174 | 4 | 3 |
| `rule=109/bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE` | `True` | 0.0 | 0.999349 | -0.307674 | 7 | 4 |
| `rule=109/bg=1100/T=3/word=00001110/NEGATIVE` | `False` | 0.5 | 0.924475 | -0.311934 | 8 | 5 |
| `rule=109/bg=1100/T=6/word=00100110/NEGATIVE` | `False` | 0.5 | 0.941622 | -0.313891 | 7 | 5 |
| `rule=109/bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE` | `True` | 0.0 | 0.998276 | -0.298928 | 6 | 5 |
| `rule=109/bg=1100/T=10/word=00111001/NEGATIVE` | `False` | 0.5 | 0.896516 | -0.285905 | 6 | 4 |
| `rule=109/bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG` | `True` | 0.0 | 0.998341 | -0.298274 | 7 | 5 |
| `rule=109/bg=1101/T=6/word=0000100/HORIZON_ARTIFACT` | `False` | 2.0 | 0.999487 | -0.303174 | 4 | 3 |
| `rule=109/bg=1101/T=10/word=0001000/NEGATIVE` | `False` | 2.0 | 1.000000 | -0.300746 | 4 | 2 |
| `rule=133/bg=0001/T=3/word=10011100/NEGATIVE` | `False` | 0.5 | 0.902744 | -0.297780 | 9 | 5 |
| `rule=133/bg=0001/T=6/word=10001000/NEGATIVE` | `False` | 0.5 | 0.911641 | -0.297342 | 8 | 5 |
| `rule=133/bg=0111/T=3/word=10000011/HORIZON_ARTIFACT` | `False` | 0.0 | 0.999224 | -0.289461 | 9 | 6 |
| `rule=133/bg=0111/T=6/word=10010011/NEGATIVE` | `False` | 0.5 | 0.895001 | -0.281419 | 8 | 4 |
| `rule=133/bg=1000/T=3/word=00010011/HORIZON_ARTIFACT` | `False` | 0.0 | 0.999305 | -0.289489 | 9 | 6 |
| `rule=133/bg=1000/T=6/word=00010001/NEGATIVE` | `False` | 0.5 | 0.901177 | -0.272430 | 8 | 5 |
| `rule=133/bg=1011/T=3/word=00001001/NEGATIVE` | `False` | 0.5 | 0.914123 | -0.256035 | 8 | 6 |
| `rule=133/bg=1011/T=6/word=100100/NEGATIVE` | `False` | 0.5 | 0.895001 | -0.281419 | 8 | 4 |
| `rule=133/bg=1101/T=3/word=0000100/NEGATIVE` | `False` | 0.5 | 0.914123 | -0.256035 | 8 | 6 |
| `rule=133/bg=1101/T=6/word=001001/NEGATIVE` | `False` | 0.5 | 0.899975 | -0.289114 | 8 | 4 |
| `rule=133/bg=1110/T=3/word=0011001/NEGATIVE` | `False` | 0.5 | 0.884352 | -0.272166 | 9 | 5 |
| `rule=133/bg=1110/T=6/word=1001001/NEGATIVE` | `False` | 0.5 | 0.899975 | -0.289114 | 8 | 4 |
| `rule=147/bg=0010/T=4/word=1000001/HORIZON_ARTIFACT` | `False` | 2.0 | 0.999969 | -0.296740 | 8 | 4 |
| `rule=147/bg=0100/T=4/word=10000010/HORIZON_ARTIFACT` | `False` | 2.0 | 0.999969 | -0.296740 | 8 | 4 |
| `rule=147/bg=1011/T=4/word=01000010/NEGATIVE` | `False` | 2.5 | 0.652251 | -0.245129 | 4 | 3 |
| `rule=147/bg=1101/T=4/word=0100010/INSUFFICIENT_SUPPORT` | `False` | 2.0 | 1.000000 | -0.289124 | 4 | 2 |

## Threshold Scan

- Perfect scalar rules over all 66 cases: `0`.
- Best accuracy rule: `max_active_monomial_count >= 17758052` (TP=1, FP=0, TN=61, FN=4, accuracy=0.939, precision=1.000, recall=0.200).

Top scanned rules:

- `max_active_monomial_count >= 17758052`: TP=1, FP=0, TN=61, FN=4, accuracy=0.939, precision=1.000, recall=0.200
- `monomial_sum_active >= 45930072`: TP=1, FP=0, TN=61, FN=4, accuracy=0.939, precision=1.000, recall=0.200
- `monomial_sum_active >= 44761619`: TP=1, FP=1, TN=60, FN=4, accuracy=0.924, precision=0.500, recall=0.200
- `central_monomial_share >= 0.8089066417439225`: TP=0, FP=1, TN=60, FN=5, accuracy=0.909, precision=0.000, recall=0.000
- `max_active_monomial_dist >= 3.5`: TP=0, FP=1, TN=60, FN=5, accuracy=0.909, precision=0.000, recall=0.000
- `r2 <= 0.4989754913156895`: TP=0, FP=1, TN=60, FN=5, accuracy=0.909, precision=0.000, recall=0.000
- `slope >= -0.24512890188685513`: TP=0, FP=1, TN=60, FN=5, accuracy=0.909, precision=0.000, recall=0.000
- `monomial_sum_active <= 4045278`: TP=0, FP=2, TN=59, FN=5, accuracy=0.894, precision=0.000, recall=0.000
- `r2 <= 0.652251378139527`: TP=0, FP=2, TN=59, FN=5, accuracy=0.894, precision=0.000, recall=0.000
- `slope <= -0.341994175822892`: TP=0, FP=2, TN=59, FN=5, accuracy=0.894, precision=0.000, recall=0.000

## Verdict

`CENTRALITY_RULE109_CONFIRMED` + `CENTRALITY_EXTERNAL_FALSE_POSITIVES` + `CENTRALITY_GLOBAL_NOT_TESTABLE` + `CENTRALITY_PARTIAL`

The centrality rule remains perfect inside the 17-case `rule_109`
subcatalogue: every `rule_109` positive has its maximum active monomial
support at the exact cone center, and no `rule_109` non-positive case
does. It does not generalize as a full-census precision rule: eight
non-`rule_109` non-positive cases also have `max_active_monomial_dist=0`.
Because the census contains no positives outside `rule_109`, external
recall is still untestable. The correct claim is therefore local:
confirmed for `rule_109`, contradicted as a global precision rule, and
externally recall-untestable with the current catalogue.

## Methodological Limit

- The validation is global over the Fase 55 census, not over all ECA rules.
- Since all positives are `rule_109`, non-rule_109 recall cannot be estimated.
- The rule is evaluated at common horizon `T_WINDOW=12`; natural-period
  validation would be a separate question.
- No paper or DOI metadata is changed by this phase.
