# Fase 61: rule_109 Dynamic Alignment Audit

## Question

Do positive and non-positive `rule_109` catalog cases differ in how the
background-subtracted defect evolves over the common horizon `t=1..12`?

Unlike Fases 59-60, this phase runs new ECA simulations. For each case it
evolves both the IC-over-background state and the pure periodic background
under rule_109, then measures their XOR defect.

## Dataset

- Cases: 17
- Positives: 5
- Non-positives: 12
- Width: 256
- Horizon: 12

| bg | T | category | word | size@1 | size@12 | span@6 | compact@6 | growth_early | monotone |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `0011` | 3 | `NEGATIVE` | `0001100` | 4 | 6 | 8 | 0.750 | 1.250 | false |
| `0011` | 6 | `NEGATIVE` | `1100100` | 6 | 6 | 8 | 0.750 | 1.000 | true |
| `0011` | 8 | `NEGATIVE` | `1000010` | 3 | 4 | 8 | 0.500 | 1.333 | false |
| `0011` | 10 | `NEGATIVE` | `10000010` | 5 | 7 | 12 | 0.500 | 1.000 | false |
| `0011` | 12 | `NATURAL_PERIOD_STRONG` | `10010100` | 7 | 4 | 11 | 0.545 | 1.143 | false |
| `0110` | 3 | `NEGATIVE` | `001100` | 4 | 6 | 8 | 0.750 | 1.250 | false |
| `0110` | 6 | `NEGATIVE` | `0010011` | 2 | 2 | 4 | 0.500 | 1.000 | false |
| `0110` | 8 | `HORIZON_ACCEPTABLE` | `0000011` | 2 | 6 | 8 | 0.750 | 3.000 | true |
| `1011` | 6 | `HORIZON_ARTIFACT` | `00001001` | 5 | 6 | 11 | 0.545 | 2.200 | false |
| `1011` | 10 | `HORIZON_ACCEPTABLE` | `00000001` | 5 | 7 | 11 | 0.545 | 2.200 | false |
| `1100` | 3 | `NEGATIVE` | `00001110` | 5 | 9 | 12 | 0.750 | 1.800 | false |
| `1100` | 6 | `NEGATIVE` | `00100110` | 6 | 8 | 12 | 0.667 | 1.167 | false |
| `1100` | 8 | `HORIZON_ACCEPTABLE` | `00000110` | 6 | 6 | 12 | 0.667 | 1.167 | false |
| `1100` | 10 | `NEGATIVE` | `00111001` | 6 | 6 | 11 | 0.545 | 1.000 | false |
| `1100` | 12 | `NATURAL_PERIOD_STRONG` | `00101001` | 7 | 4 | 11 | 0.545 | 1.143 | false |
| `1101` | 6 | `HORIZON_ARTIFACT` | `0000100` | 4 | 7 | 7 | 0.714 | 1.500 | false |
| `1101` | 10 | `NEGATIVE` | `0001000` | 2 | 10 | 11 | 0.364 | 3.000 | false |

## Descriptor Separation

### `growth_rate_early`

- Perfect separating rule(s): none
- No-false-positive rule(s): none
- Best rule: `growth_rate_early >= 2.2` -> TP=2, FP=2, TN=10, FN=3, accuracy=0.706

### `compactness_mean`

- Perfect separating rule(s): none
- No-false-positive rule(s): none
- Best rule: `compactness_mean <= 0.5722222222222222` -> TP=3, FP=3, TN=9, FN=2, accuracy=0.706

### `span_at_t6`

- Perfect separating rule(s): none
- No-false-positive rule(s): none
- Best rule: `span_at_t6 <= 4` -> TP=0, FP=1, TN=11, FN=5, accuracy=0.647

### `defect_size_final`

- Perfect separating rule(s): none
- No-false-positive rule(s): none
- Best rule: `defect_size_final <= 4` -> TP=2, FP=2, TN=10, FN=3, accuracy=0.706

### `compactness_at_t6`

- Perfect separating rule(s): none
- No-false-positive rule(s): none
- Best rule: `compactness_at_t6 <= 0.36363636363636365` -> TP=0, FP=1, TN=11, FN=5, accuracy=0.647

### `defect_monotone`

- Perfect separating rule(s): none
- No-false-positive rule(s): none
- Best rule: `defect_monotone == True` -> TP=1, FP=1, TN=11, FN=4, accuracy=0.706

### `max_defect_size`

- Perfect separating rule(s): none
- No-false-positive rule(s):
  - `max_defect_size >= 12` -> TP=1, FP=0, TN=12, FN=4, accuracy=0.765
    - Captures: `bg=1011/T=10/word=00000001`
- Best rule: `max_defect_size >= 12` -> TP=1, FP=0, TN=12, FN=4, accuracy=0.765

### `max_defect_span`

- Perfect separating rule(s): none
- No-false-positive rule(s): none
- Best rule: `max_defect_span >= 13` -> TP=1, FP=2, TN=10, FN=4, accuracy=0.647

### `center_drift_abs`

- Perfect separating rule(s): none
- No-false-positive rule(s):
  - `center_drift_abs <= 0.0` -> TP=2, FP=0, TN=12, FN=3, accuracy=0.824
    - Captures: `bg=0110/T=8/word=0000011`, `bg=1011/T=10/word=00000001`
- Best rule: `center_drift_abs <= 0.0` -> TP=2, FP=0, TN=12, FN=3, accuracy=0.824

### `size_growth_total`

- Perfect separating rule(s): none
- No-false-positive rule(s):
  - `size_growth_total <= -3` -> TP=2, FP=0, TN=12, FN=3, accuracy=0.824
    - Captures: `bg=0011/T=12/word=10010100`, `bg=1100/T=12/word=00101001`
- Best rule: `size_growth_total <= -3` -> TP=2, FP=0, TN=12, FN=3, accuracy=0.824

### `span_growth_total`

- Perfect separating rule(s): none
- No-false-positive rule(s): none
- Best rule: `span_growth_total <= 1` -> TP=2, FP=3, TN=9, FN=3, accuracy=0.647

## Verdict

`DYNAMIC_PARTIAL`.

Dynamic descriptors provide partial high-precision signal: at least one threshold has no false positives, but no tested descriptor separates all positives from all non-positives.

## Methodological Limit

- The audit is restricted to the 17 `rule_109` cases in the existing Fase 55 catalog.
- It does not establish a universal law over all rule_109 backgrounds or all ECA rules.
- The pure background is evolved under rule_109 in parallel with the IC state; the defect is measured as `state(t) XOR background(t)`.
