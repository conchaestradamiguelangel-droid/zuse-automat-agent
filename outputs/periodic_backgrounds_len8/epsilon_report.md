# Fase 46: Epsilon Residual Characterization

## Question

Fase 45 established `degree = 24 - abs(rel_pos) + epsilon`,
with `epsilon in {0,1}` and zero exceptions over 174 active outputs.
Fase 46 asks whether the residual epsilon has a compact predictor.

Rows with `dist=0` and `dist=1` are excluded because `epsilon=0` there
in all known cases; keeping them would inflate accuracy without explaining
the residual.

## Summary

Status: `EPSILON_REMAINS_RESIDUAL`.

- Source: `C:\Users\PC\Documents\Codex\2026-05-22\te-voy-a-dar-un-peque\outputs\periodic_backgrounds_len8\anf_stratification_results.json`
- Filter: `dist >= 2`
- Records analyzed: 141
- Representatives: 20
- Epsilon counts: {0: 83, 1: 58}
- Majority baseline: 58.87%

## Simple single-feature predictors

| feature | train acc | leave-one-rep-out mean | std | mapping |
| --- | ---: | ---: | ---: | --- |
| dist | 66.67% | 64.89% | 21.22% | `{'7': 0, '2': 0, '3': 0, '6': 1, '5': 1, '4': 0, '10': 0, '8': 0, '9': 1}` |
| defect_phase | 63.83% | 64.53% | 24.13% | `{'0': 0, '4': 0, '1': 1, '2': 1, '3': 0}` |
| local_bg_3mer | 66.67% | 64.18% | 14.04% | `{'011': 0, '000': 0, '110': 0, '100': 1, '010': 1, '001': 0, '111': 0, '101': 0}` |
| background_bit | 58.87% | 57.77% | 12.25% | `{'1': 0, '0': 0}` |
| rule | 58.87% | 57.77% | 12.25% | `{'73': 0, '109': 0}` |
| sign | 58.87% | 57.77% | 12.25% | `{'L': 0, 'R': 0}` |
| family_id | 60.99% | 56.77% | 12.83% | `{'F09': 0, 'F10': 0, 'F02': 0, 'F06': 0, 'F04': 0, 'F03': 1, 'F01': 0, 'F12': 0, 'F00': 0, 'F05': 0, 'F08': 0, 'F07': 0, 'F11': 0}` |
| local_bg_2mer | 60.28% | 56.40% | 20.88% | `{'11': 0, '00': 0, '10': 1, '01': 0}` |
| bg_transition | 59.57% | 50.43% | 14.60% | `{'1': 1, '0': 0}` |

## Decision tree, max_depth=3

- Train accuracy: 73.05%
- Leave-one-rep-out mean accuracy: 55.65%
- Leave-one-rep-out std: 20.67%

### Feature importances

| feature | importance |
| --- | ---: |
| `cat:family_id=F03` | 0.243831 |
| `num:dist` | 0.220389 |
| `cat:local_bg_3mer=001` | 0.164386 |
| `num:local_bg_2mer_int` | 0.148556 |
| `cat:family_id=F10` | 0.107281 |
| `cat:family_id=F07` | 0.074688 |
| `cat:local_bg_3mer=110` | 0.040869 |

### Tree

```text
|--- num:dist <= 4.50
|   |--- cat:family_id=F03 <= 0.50
|   |   |--- cat:family_id=F07 <= 0.50
|   |   |   |--- class: 0
|   |   |--- cat:family_id=F07 >  0.50
|   |   |   |--- class: 1
|   |--- cat:family_id=F03 >  0.50
|   |   |--- cat:local_bg_3mer=110 <= 0.50
|   |   |   |--- class: 1
|   |   |--- cat:local_bg_3mer=110 >  0.50
|   |   |   |--- class: 0
|--- num:dist >  4.50
|   |--- cat:local_bg_3mer=001 <= 0.50
|   |   |--- num:local_bg_2mer_int <= 2.50
|   |   |   |--- class: 1
|   |   |--- num:local_bg_2mer_int >  2.50
|   |   |   |--- class: 0
|   |--- cat:local_bg_3mer=001 >  0.50
|   |   |--- cat:family_id=F10 <= 0.50
|   |   |   |--- class: 0
|   |   |--- cat:family_id=F10 >  0.50
|   |   |   |--- class: 1
```

### Leave-one-rep-out folds

| rep | n | accuracy | actual eps=1 | predicted eps=1 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 4 | 50.00% | 2 | 0 |
| 1 | 6 | 50.00% | 3 | 2 |
| 2 | 8 | 87.50% | 2 | 1 |
| 3 | 5 | 40.00% | 2 | 1 |
| 4 | 6 | 50.00% | 2 | 1 |
| 5 | 5 | 40.00% | 2 | 3 |
| 6 | 7 | 28.57% | 3 | 2 |
| 7 | 3 | 100.00% | 1 | 1 |
| 8 | 13 | 61.54% | 3 | 8 |
| 9 | 7 | 57.14% | 3 | 0 |
| 10 | 10 | 40.00% | 3 | 3 |
| 11 | 7 | 100.00% | 3 | 3 |
| 12 | 9 | 66.67% | 4 | 3 |
| 13 | 12 | 50.00% | 6 | 4 |
| 14 | 9 | 66.67% | 4 | 3 |
| 15 | 7 | 57.14% | 3 | 2 |
| 16 | 6 | 66.67% | 2 | 2 |
| 17 | 6 | 33.33% | 5 | 1 |
| 18 | 4 | 25.00% | 2 | 1 |
| 19 | 7 | 42.86% | 3 | 7 |

## Interpretation

No tested feature set reaches 70% leave-one-rep-out accuracy. The epsilon bit remains a residual under the current local/background/family features.
This result does not refute the ANF gradient law; it separates the strong `24 - dist` backbone from the still-unexplained one-bit residual.
