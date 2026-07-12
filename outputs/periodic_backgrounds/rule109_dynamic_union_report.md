# Fase 62: rule_109 Dynamic Union Test

## Question

Does the minimal union of the two strongest no-false-positive dynamic
descriptors from Fase 61 separate all positive `rule_109` cases?

This phase does not run new simulations. It reuses the Fase 61 dynamic
alignment output and tests one predeclared union only:

`size_growth_total <= -3 OR center_drift_abs <= 0.0`

## Results

### `minimal_union`

- Rule: `size_growth_total <= -3 OR center_drift_abs <= 0.0`
- TP=4, FP=0, TN=12, FN=1
- Accuracy=0.941, precision=1.000, recall=0.800
- True positives: `bg=0011/T=12/word=10010100`, `bg=0110/T=8/word=0000011`, `bg=1011/T=10/word=00000001`, `bg=1100/T=12/word=00101001`
- False positives: `none`
- False negatives: `bg=1100/T=8/word=00000110`

### `union_plus_max_defect_size`

- Rule: `size_growth_total <= -3 OR center_drift_abs <= 0.0 OR max_defect_size >= 12`
- TP=4, FP=0, TN=12, FN=1
- Accuracy=0.941, precision=1.000, recall=0.800
- True positives: `bg=0011/T=12/word=10010100`, `bg=0110/T=8/word=0000011`, `bg=1011/T=10/word=00000001`, `bg=1100/T=12/word=00101001`
- False positives: `none`
- False negatives: `bg=1100/T=8/word=00000110`

## Case Table

| bg | T | category | positive | size_growth_total | center_drift_abs | max_defect_size | minimal_union |
| --- | ---: | --- | --- | ---: | ---: | ---: | --- |
| `0011` | 3 | `NEGATIVE` | false | 2 | 1.833 | 6 | false |
| `0011` | 6 | `NEGATIVE` | false | 0 | 0.167 | 6 | false |
| `0011` | 8 | `NEGATIVE` | false | 1 | 1.450 | 5 | false |
| `0011` | 10 | `NEGATIVE` | false | 2 | 1.286 | 8 | false |
| `0011` | 12 | `NATURAL_PERIOD_STRONG` | true | -3 | 0.250 | 8 | true |
| `0110` | 3 | `NEGATIVE` | false | 2 | 1.833 | 6 | false |
| `0110` | 6 | `NEGATIVE` | false | 0 | 1.500 | 4 | false |
| `0110` | 8 | `HORIZON_ACCEPTABLE` | true | 4 | 0.000 | 6 | true |
| `1011` | 6 | `HORIZON_ARTIFACT` | false | 1 | 0.083 | 11 | false |
| `1011` | 10 | `HORIZON_ACCEPTABLE` | true | 2 | 0.000 | 12 | true |
| `1100` | 3 | `NEGATIVE` | false | 4 | 0.111 | 9 | false |
| `1100` | 6 | `NEGATIVE` | false | 2 | 0.600 | 8 | false |
| `1100` | 8 | `HORIZON_ACCEPTABLE` | true | 0 | 0.417 | 8 | false |
| `1100` | 10 | `NEGATIVE` | false | 0 | 0.667 | 8 | false |
| `1100` | 12 | `NATURAL_PERIOD_STRONG` | true | -3 | 0.250 | 8 | true |
| `1101` | 6 | `HORIZON_ARTIFACT` | false | 3 | 2.821 | 7 | false |
| `1101` | 10 | `NEGATIVE` | false | 8 | 1.500 | 10 | false |

## Verdict

`DYNAMIC_UNION_PARTIAL`.

The minimal dynamic union captures 4/5 positive cases with zero false
positives. The single remaining positive residual is
`bg=1100/T=8/word=00000110`.

Adding `max_defect_size >= 12` does not improve recall, because it captures
a positive case already captured by `center_drift_abs <= 0.0`.

Thus the Fase 61 dynamic signal is real but remains subfamily-specific. It
does not close the causal explanation with a compact dynamic descriptor.

## Methodological Limit

- This phase only tests the minimal union suggested by Fase 61. It is not a search over arbitrary dynamic combinations.
