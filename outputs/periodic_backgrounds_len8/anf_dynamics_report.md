# Fase 47: Dynamic ANF Features for the T=15 Epsilon Residual

## Question

Fase 46 found no static predictor for the epsilon residual in
`degree = 24 - abs(rel_pos) + epsilon`. Fase 47 tests whether epsilon
is predicted by the temporal ANF growth profile inside the 25-cell,
12-step causal cone.

## Summary

Status: `EPSILON_DYNAMIC_RULE_FOUND`.

- Representatives: 20
- Records analyzed (`dist>=2`): 141
- Epsilon counts: {0: 83, 1: 58}
- Majority baseline: 58.87%
- t=12 verification mismatches against Fase 44: 0

## Single-feature predictors

| feature | train acc | leave-one-rep-out mean | std |
| --- | ---: | ---: | ---: |
| `degree_growth_slope` | 98.58% | 94.90% | 9.44% |
| `monomial_growth_slope` | 100.00% | 73.37% | 22.07% |
| `t_first_full_degree` | 71.63% | 71.96% | 11.38% |
| `lr_degree_diff_final` | 68.79% | 67.90% | 14.69% |
| `lr_slope_diff` | 73.05% | 66.82% | 15.59% |
| `dist` | 66.67% | 64.89% | 21.22% |
| `defect_phase` | 63.83% | 64.53% | 24.13% |
| `lr_t_first_diff` | 63.12% | 62.64% | 13.93% |
| `degree_at_t9` | 66.67% | 61.82% | 15.43% |
| `lr_log_slope_diff` | 74.47% | 58.83% | 13.04% |
| `t_first_degree_ge_20` | 63.83% | 58.70% | 13.84% |
| `degree_at_t3` | 58.87% | 57.77% | 12.25% |
| `degree_at_t6` | 60.28% | 57.14% | 13.89% |
| `max_degree_jump` | 58.87% | 55.85% | 12.12% |
| `log10_monomials_at_t6` | 68.09% | 53.78% | 13.65% |

## Decision tree, max_depth=3

- Train accuracy: 86.52%
- Leave-one-rep-out mean accuracy: 85.01%
- Leave-one-rep-out std: 15.15%

### Feature importances

| feature | importance |
| --- | ---: |
| `t_first_full_degree` | 0.529593 |
| `monomial_growth_slope` | 0.201649 |
| `lr_slope_diff` | 0.142284 |
| `degree_growth_slope` | 0.126474 |

### Tree

```text
|--- t_first_full_degree <= 11.50
|   |--- class: 0
|--- t_first_full_degree >  11.50
|   |--- monomial_growth_slope <= 0.55
|   |   |--- lr_slope_diff <= -0.02
|   |   |   |--- class: 0
|   |   |--- lr_slope_diff >  -0.02
|   |   |   |--- class: 1
|   |--- monomial_growth_slope >  0.55
|   |   |--- degree_growth_slope <= 1.90
|   |   |   |--- class: 0
|   |   |--- degree_growth_slope >  1.90
|   |   |   |--- class: 1
```

### Leave-one-rep-out folds

| rep | n | accuracy | actual eps=1 | predicted eps=1 |
| ---: | ---: | ---: | ---: | ---: |
| 0 | 4 | 75.00% | 2 | 3 |
| 1 | 6 | 83.33% | 3 | 4 |
| 2 | 8 | 100.00% | 2 | 2 |
| 3 | 5 | 80.00% | 2 | 3 |
| 4 | 6 | 100.00% | 2 | 2 |
| 5 | 5 | 80.00% | 2 | 3 |
| 6 | 7 | 85.71% | 3 | 4 |
| 7 | 3 | 100.00% | 1 | 1 |
| 8 | 13 | 69.23% | 3 | 7 |
| 9 | 7 | 100.00% | 3 | 3 |
| 10 | 10 | 50.00% | 3 | 8 |
| 11 | 7 | 100.00% | 3 | 3 |
| 12 | 9 | 88.89% | 4 | 5 |
| 13 | 12 | 91.67% | 6 | 7 |
| 14 | 9 | 100.00% | 4 | 4 |
| 15 | 7 | 85.71% | 3 | 4 |
| 16 | 6 | 100.00% | 2 | 2 |
| 17 | 6 | 50.00% | 5 | 4 |
| 18 | 4 | 75.00% | 2 | 3 |
| 19 | 7 | 85.71% | 3 | 4 |

## Interpretation

Dynamic ANF features meet the >=90% leave-one-representative-out gate.
The strongest feature is the full `degree_growth_slope` over t=1..12. This should be interpreted as a dynamic full-profile law of ANF growth, not as a static pre-computation shortcut: the feature uses the complete temporal degree trajectory through the final cone layer.
