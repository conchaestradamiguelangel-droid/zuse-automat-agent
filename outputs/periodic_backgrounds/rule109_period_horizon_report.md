# Fase 58: rule_109 Period/Horizon Discriminator

## Question

Given the Fase 57 result that center-mediated local ANF is necessary but
not sufficient, can period/horizon features separate the 5 positive
`rule_109` ANF-gradient witnesses from the 12 non-positive center-mediated
cases?

This phase uses only the Fase 55 census. It runs no new ECA or ANF
simulation.

## Dataset

- `rule_109` catalog cases: 17
- Positive cases (`NATURAL_PERIOD_STRONG` or `HORIZON_ACCEPTABLE`): 5
- Non-positive cases: 12
- Common horizon: `T_WINDOW=12`

## Case Table

| background | T_local | ratio 12/T | category | positive | word |
| --- | ---: | ---: | --- | --- | --- |
| `0011` | 3 | 4.000 | `NEGATIVE` | `False` | `0001100` |
| `0011` | 6 | 2.000 | `NEGATIVE` | `False` | `1100100` |
| `0011` | 8 | 1.500 | `NEGATIVE` | `False` | `1000010` |
| `0011` | 10 | 1.200 | `NEGATIVE` | `False` | `10000010` |
| `0011` | 12 | 1.000 | `NATURAL_PERIOD_STRONG` | `True` | `10010100` |
| `0110` | 3 | 4.000 | `NEGATIVE` | `False` | `001100` |
| `0110` | 6 | 2.000 | `NEGATIVE` | `False` | `0010011` |
| `0110` | 8 | 1.500 | `HORIZON_ACCEPTABLE` | `True` | `0000011` |
| `1011` | 6 | 2.000 | `HORIZON_ARTIFACT` | `False` | `00001001` |
| `1011` | 10 | 1.200 | `HORIZON_ACCEPTABLE` | `True` | `00000001` |
| `1100` | 3 | 4.000 | `NEGATIVE` | `False` | `00001110` |
| `1100` | 6 | 2.000 | `NEGATIVE` | `False` | `00100110` |
| `1100` | 8 | 1.500 | `HORIZON_ACCEPTABLE` | `True` | `00000110` |
| `1100` | 10 | 1.200 | `NEGATIVE` | `False` | `00111001` |
| `1100` | 12 | 1.000 | `NATURAL_PERIOD_STRONG` | `True` | `00101001` |
| `1101` | 6 | 2.000 | `HORIZON_ARTIFACT` | `False` | `0000100` |
| `1101` | 10 | 1.200 | `NEGATIVE` | `False` | `0001000` |

## Period and Horizon Stratification

By `T_local`:

- `T=3`: `{'NEGATIVE': 3}`
- `T=6`: `{'NEGATIVE': 3, 'HORIZON_ARTIFACT': 2}`
- `T=8`: `{'NEGATIVE': 1, 'HORIZON_ACCEPTABLE': 2}`
- `T=10`: `{'NEGATIVE': 3, 'HORIZON_ACCEPTABLE': 1}`
- `T=12`: `{'NATURAL_PERIOD_STRONG': 2}`

By oversampling ratio `12/T_local`:

- `1.000`: `{'NATURAL_PERIOD_STRONG': 2}`
- `1.200`: `{'NEGATIVE': 3, 'HORIZON_ACCEPTABLE': 1}`
- `1.500`: `{'NEGATIVE': 1, 'HORIZON_ACCEPTABLE': 2}`
- `2.000`: `{'NEGATIVE': 3, 'HORIZON_ARTIFACT': 2}`
- `4.000`: `{'NEGATIVE': 3}`

## Rule Search

Best period/horizon-only rules:

- `T_local == 12`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `T_local >= 12`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `oversampling_ratio <= 1.000`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `oversampling_ratio == 1.000`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `T_local == 8`: acc=0.765, TP=2, FP=1, TN=11, FN=3
- `T_local >= 8`: acc=0.765, TP=5, FP=4, TN=8, FN=0
- `oversampling_ratio <= 1.500`: acc=0.765, TP=5, FP=4, TN=8, FN=0
- `oversampling_ratio == 1.500`: acc=0.765, TP=2, FP=1, TN=11, FN=3

No period/horizon-only rule separates positives from non-positives perfectly.

Best overall small rules:

- `T_local == 12`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `T_local >= 12`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `T_local >= 12 AND background != 0110`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `T_local >= 12 AND background != 1011`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `T_local >= 12 AND background != 1101`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `T_local >= 12 AND canonical_background == 0011`: acc=0.824, TP=2, FP=0, TN=12, FN=3
- `T_local >= 8 AND background != 0011`: acc=0.824, TP=4, FP=2, TN=10, FN=1
- `T_local >= 8 AND background != 1101`: acc=0.824, TP=5, FP=3, TN=9, FN=0

## Verdict

`PERIOD_HORIZON_PARTIAL_DISCRIMINANT`.

Period/horizon is informative but incomplete. The remaining residual likely depends on background, IC, or alignment features.

The key residual is whether `T_local >= 8` or `12/T_local <= 1.5` is
enough. It is not: `rule_109/bg=0011/T=8` is non-positive despite
meeting that horizon threshold, while `bg=0110/T=8` and `bg=1100/T=8`
are positive. Thus the second condition is not period/horizon alone.
