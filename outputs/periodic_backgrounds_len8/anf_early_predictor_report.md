# Fase 48: Early Dynamic ANF Predictor

## Question

Fase 47 found that the complete `degree_growth_slope` over `t=1..12`
predicts epsilon with 94.90% leave-one-representative-out accuracy.
Fase 48 asks how much of that trajectory is necessary.

## Summary

Status: `FULL_PROFILE_REQUIRED`.

- Source: `C:\Users\PC\Documents\Codex\2026-05-22\te-voy-a-dar-un-peque\outputs\periodic_backgrounds_len8\anf_dynamics_results.json`
- Horizons tested: [6, 8, 9, 10, 11, 12]
- K=12 reproduces Fase 47 within 2 percentage points: `True`
- K=12 delta from Fase 47 reference: 0.00%

Important note: `degree_growth_slope_K` is future-blind and uses only
`t=1..K`. `t_first_full_degree_K` uses the final expected degree from Fase
44 and is therefore not fully future-blind.

## Horizon table

| K | degree_growth_slope_K LORO | degree train | monomial slope LORO | t_first_full LORO | tree LORO | tree train |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 6 | 61.74% | 64.54% | 64.60% | 57.77% | 54.36% | 70.21% |
| 8 | 76.56% | 80.85% | 71.28% | 57.77% | 63.59% | 73.05% |
| 9 | 75.27% | 81.56% | 72.00% | 57.77% | 55.40% | 71.63% |
| 10 | 76.09% | 84.40% | 69.50% | 57.77% | 71.39% | 73.05% |
| 11 | 79.47% | 89.36% | 72.66% | 71.96% | 83.19% | 82.27% |
| 12 | 94.90% | 98.58% | 73.37% | 71.96% | 83.19% | 82.27% |

## Per-horizon tree summaries

### K=6

- Train accuracy: 70.21%
- LORO mean accuracy: 54.36%
- Feature importances:
  - `monomial_growth_slope_6`: 0.712564
  - `dist`: 0.287436

### K=8

- Train accuracy: 73.05%
- LORO mean accuracy: 63.59%
- Feature importances:
  - `monomial_growth_slope_8`: 0.514566
  - `degree_growth_slope_8`: 0.485434

### K=9

- Train accuracy: 71.63%
- LORO mean accuracy: 55.40%
- Feature importances:
  - `degree_growth_slope_9`: 0.519810
  - `monomial_growth_slope_9`: 0.480190

### K=10

- Train accuracy: 73.05%
- LORO mean accuracy: 71.39%
- Feature importances:
  - `degree_growth_slope_10`: 0.567466
  - `monomial_growth_slope_10`: 0.432534

### K=11

- Train accuracy: 82.27%
- LORO mean accuracy: 83.19%
- Feature importances:
  - `t_first_full_degree_11`: 0.571012
  - `monomial_growth_slope_11`: 0.292622
  - `degree_growth_slope_11`: 0.136366

### K=12

- Train accuracy: 82.27%
- LORO mean accuracy: 83.19%
- Feature importances:
  - `t_first_full_degree_12`: 0.558098
  - `degree_growth_slope_12`: 0.229399
  - `monomial_growth_slope_12`: 0.212503

## Interpretation

The >=90% gate is reached only at K=12. The v1.17 result is therefore a full-profile law, not an early predictor.
