# Fase 60: rule_109 Alignment Discriminator Validation

## Question

Does the Fase 59 `rule_109/T=8` IC-placement discriminator generalize
to all 17 `rule_109` cases in the Fase 55 census?

This validation uses existing descriptor data only. It runs no new ECA
or ANF simulation.

## Dataset

- Rule_109 cases: 17
- Positive cases: 5
- Non-positive cases: 12

| bg | T | category | word | ic_span | ic_offsets_mod4 | positive |
| --- | ---: | --- | --- | ---: | --- | --- |
| `0011` | 3 | `NEGATIVE` | `0001100` | 2 | `(0, 3)` | false |
| `0011` | 6 | `NEGATIVE` | `1100100` | 5 | `(0, 1)` | false |
| `0011` | 8 | `NEGATIVE` | `1000010` | 6 | `(0, 1)` | false |
| `0011` | 10 | `NEGATIVE` | `10000010` | 7 | `(0, 2)` | false |
| `0011` | 12 | `NATURAL_PERIOD_STRONG` | `10010100` | 6 | `(0, 1, 3)` | true |
| `0110` | 3 | `NEGATIVE` | `001100` | 2 | `(2, 3)` | false |
| `0110` | 6 | `NEGATIVE` | `0010011` | 5 | `(1, 2)` | false |
| `0110` | 8 | `HORIZON_ACCEPTABLE` | `0000011` | 2 | `(1, 2)` | true |
| `1011` | 6 | `HORIZON_ARTIFACT` | `00001001` | 4 | `(0, 3)` | false |
| `1011` | 10 | `HORIZON_ACCEPTABLE` | `00000001` | 1 | `(3,)` | true |
| `1100` | 3 | `NEGATIVE` | `00001110` | 3 | `(0, 1, 2)` | false |
| `1100` | 6 | `NEGATIVE` | `00100110` | 5 | `(1, 2)` | false |
| `1100` | 8 | `HORIZON_ACCEPTABLE` | `00000110` | 2 | `(1, 2)` | true |
| `1100` | 10 | `NEGATIVE` | `00111001` | 6 | `(0, 2, 3)` | false |
| `1100` | 12 | `NATURAL_PERIOD_STRONG` | `00101001` | 6 | `(0, 2, 3)` | true |
| `1101` | 6 | `HORIZON_ARTIFACT` | `0000100` | 1 | `(0,)` | false |
| `1101` | 10 | `NEGATIVE` | `0001000` | 1 | `(3,)` | false |

## Fase 59 Rule Re-test

Fase 59 found the exact local rule for the three T=8 cases:

`ic_span == 2` and `ic_active_offsets_mod4 == (1, 2)`.

On T=8 only:
- TP=2, FP=0, TN=1, FN=0, accuracy=1.000

On all 17 rule_109 cases:
- TP=2, FP=0, TN=12, FN=3, accuracy=0.824

## Descriptor Validation

### `ic_span`

- Perfect set rule: `false`
- Positive values: `1`, `2`, `6`
- Overlap values: `1`, `2`, `6`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=6, TN=6, FN=0, accuracy=0.647
- Best threshold: `ic_span <= 2` -> TP=3, FP=4, TN=8, FN=2, accuracy=0.647

### `ic_active_bits`

- Perfect set rule: `true`
- Positive values: `(0, 3, 5)`, `(2, 4, 7)`, `(5, 6)`, `(7)`
- Overlap values: `none`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=0, TN=12, FN=0, accuracy=1.000

### `ic_active_offsets_mod4`

- Perfect set rule: `false`
- Positive values: `(0, 1, 3)`, `(0, 2, 3)`, `(1, 2)`, `(3)`
- Overlap values: `(0, 2, 3)`, `(1, 2)`, `(3)`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=4, TN=8, FN=0, accuracy=0.765

### `ic_support_size`

- Perfect set rule: `false`
- Positive values: `1`, `2`, `3`
- Overlap values: `1`, `2`, `3`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=11, TN=1, FN=0, accuracy=0.353
- Best threshold: `ic_support_size <= 1` -> TP=1, FP=2, TN=10, FN=4, accuracy=0.647

### `bg_phase_in_0011_orbit`

- Perfect set rule: `false`
- Positive values: `0`, `1`, `2`, `null`
- Overlap values: `0`, `1`, `2`, `null`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=12, TN=0, FN=0, accuracy=0.294
- Best threshold: `bg_phase_in_0011_orbit >= 2` -> TP=2, FP=3, TN=9, FN=3, accuracy=0.647

### `bg_at_ic_ones`

- Perfect set rule: `false`
- Positive values: `1`, `2`
- Overlap values: `1`, `2`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=9, TN=3, FN=0, accuracy=0.471
- Best threshold: `bg_at_ic_ones >= 3` -> TP=0, FP=1, TN=11, FN=5, accuracy=0.647

### `defect_support_size`

- Perfect set rule: `false`
- Positive values: `2`, `4`, `5`
- Overlap values: `4`, `5`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=6, TN=6, FN=0, accuracy=0.647
- Best threshold: `defect_support_size <= 2` -> TP=1, FP=1, TN=11, FN=4, accuracy=0.706

### `defect_phase_offset`

- Perfect set rule: `false`
- Positive values: `(0, 1, 2)`, `(0, 1, 2, 3)`, `(0, 2, 3)`, `(1, 2)`
- Overlap values: `(0, 1, 2)`, `(0, 1, 2, 3)`, `(0, 2, 3)`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=7, TN=5, FN=0, accuracy=0.588

### `defect_span`

- Perfect set rule: `false`
- Positive values: `2`, `7`, `8`
- Overlap values: `7`, `8`
- Predict-positive-if-value-seen-in-positive: TP=5, FP=7, TN=5, FN=0, accuracy=0.588
- Best threshold: `defect_span >= 8` -> TP=2, FP=2, TN=10, FN=3, accuracy=0.706

## Verdict

`ALIGNMENT_LOOKUP_ONLY`.

- Perfect descriptors: `ic_active_bits`
- Compact perfect descriptors: `none`

The exact IC-active-bit pattern separates the 17 cases, but this is a
lookup-like descriptor tied to the selected IC word for each catalog
group. It is useful as an audit result, but it is not yet a compact
causal rule.

The Fase 59 IC-placement discriminator is exact for the three T=8 cases,
but it does not generalize to all 17 `rule_109` cases. In particular,
positive and non-positive cases share `ic_span` values 1, 2, and 6.

Therefore coarse IC placement is a local T=8 discriminator, not a
standalone global causal condition for the rule_109 gradient.

## Methodological Limit

- The validation is restricted to the 17 rule_109 cases already present in the Fase 55 census. It does not establish a universal ECA law.
