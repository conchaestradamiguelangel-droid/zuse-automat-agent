# Fase 43B: Targeted SIFT for the T=15 Cone

## Question

Fase 43A found only a small global improvement from simple order reversal,
but identified the strongest candidate representative: `rule_73` with
background `00111011`, whose best known active-output ROBDD had 16,061
nodes. Fase 43B runs a genuine one-pass variable-sifting search on that
representative.

This is a targeted SIFT pass, not an all-representative proof of global
optimality. The publication gate is explicit: active-output nodes below
10,000 would be a strong representation-compression witness.

## Target

- Rule: 73
- Background: `00111011`
- IC: `00100100`
- Family: `F01`

## Result

Status: `SIFT_TARGETED_SMALL_REDUCTION_FOUND`.

- Baseline best order: `reverse`
- Baseline active nodes: 16061
- SIFT best active nodes: 16056
- Reduction vs baseline: 0.031%
- Baseline vector nodes: 52705
- SIFT best vector nodes: 52698
- Orders evaluated: 580
- 25/25 support preserved: `True`
- Best order: `[22, 21, 20, 19, 23, 24, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]`

## SIFT trace

| sweep | variable | best active after variable | accepted | global best |
| ---: | ---: | ---: | --- | ---: |
| 0 | 24 | 16057 | `True` | 16057 |
| 1 | 23 | 16056 | `True` | 16056 |
| 2 | 22 | 16056 | `False` | 16056 |
| 3 | 21 | 16056 | `False` | 16056 |
| 4 | 20 | 16056 | `False` | 16056 |
| 5 | 19 | 16056 | `False` | 16056 |
| 6 | 18 | 16056 | `False` | 16056 |
| 7 | 17 | 16056 | `False` | 16056 |
| 8 | 16 | 16056 | `False` | 16056 |
| 9 | 15 | 16056 | `False` | 16056 |
| 10 | 14 | 16056 | `False` | 16056 |
| 11 | 13 | 16056 | `False` | 16056 |
| 12 | 12 | 16056 | `False` | 16056 |
| 13 | 11 | 16056 | `False` | 16056 |
| 14 | 10 | 16056 | `False` | 16056 |
| 15 | 9 | 16056 | `False` | 16056 |
| 16 | 8 | 16056 | `False` | 16056 |
| 17 | 7 | 16056 | `False` | 16056 |
| 18 | 6 | 16056 | `False` | 16056 |
| 19 | 5 | 16056 | `False` | 16056 |
| 20 | 4 | 16056 | `False` | 16056 |
| 21 | 3 | 16056 | `False` | 16056 |
| 22 | 2 | 16056 | `False` | 16056 |
| 23 | 1 | 16056 | `False` | 16056 |
| 24 | 0 | 16056 | `False` | 16056 |
| 0 | 24 | 16057 | `True` | 16057 |
| 1 | 23 | 16056 | `True` | 16056 |
| 2 | 22 | 16056 | `False` | 16056 |
| 3 | 21 | 16056 | `False` | 16056 |
| 4 | 20 | 16056 | `False` | 16056 |
| 5 | 19 | 16056 | `False` | 16056 |
| 6 | 18 | 16056 | `False` | 16056 |
| 7 | 17 | 16056 | `False` | 16056 |
| 8 | 16 | 16056 | `False` | 16056 |
| 9 | 15 | 16056 | `False` | 16056 |
| 10 | 14 | 16056 | `False` | 16056 |
| 11 | 13 | 16056 | `False` | 16056 |
| 12 | 12 | 16056 | `False` | 16056 |
| 13 | 11 | 16056 | `False` | 16056 |
| 14 | 10 | 16056 | `False` | 16056 |
| 15 | 9 | 16056 | `False` | 16056 |
| 16 | 8 | 16056 | `False` | 16056 |
| 17 | 7 | 16056 | `False` | 16056 |
| 18 | 6 | 16056 | `False` | 16056 |
| 19 | 5 | 16056 | `False` | 16056 |
| 20 | 4 | 16056 | `False` | 16056 |
| 21 | 3 | 16056 | `False` | 16056 |
| 22 | 2 | 16056 | `False` | 16056 |
| 23 | 1 | 16056 | `False` | 16056 |
| 24 | 0 | 16056 | `False` | 16056 |

## Interpretation

The targeted SIFT search tests the most favorable existing representative
against the explicit 10K-node publication gate. The support result from
Fase 42 remains fixed: this phase searches for representation compactness,
not input elimination.

The result does not meet the publication gate. A complete one-pass SIFT on
the most favorable representative improves the active-output ROBDD by only
5 nodes. This is evidence that simple variable-order optimization is not
the missing symbolic shortcut for the dense cone.
