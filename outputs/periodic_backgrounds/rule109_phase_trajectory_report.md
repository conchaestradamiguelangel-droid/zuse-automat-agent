# Fase 67: rule_109 Phase-Trajectory Audit

## Question

At which internal phase, if any, does the persistent residual
`rule_109/bg=1100/T=8/word=00000110` differ qualitatively from the nearest
negative case `rule_109/bg=1100/T=10/word=00111001`?

## Setup

- Rule: `109`
- Background: `1100`
- Width: `256`
- Defect: `state_with_IC(t) XOR background_only(t)`.

## Part A: Residual Period-8 Snapshots

- Residual evolved to `t=80`.
- Period check: `defect(t) == defect(t+8)` for `t >= 16`.
- Checked pairs: `57`.
- Mismatches: `0`.

| phase | t | size | span | center_rel | active positions | dominant contexts |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 16 | 6 | 12 | 2.333 | `[-3, -1, 0, 3, 7, 8]` | `[011, 111]` |
| 1 | 17 | 7 | 11 | 2.571 | `[-3, -1, 2, 3, 4, 6, 7]` | `[010, 101]` |
| 2 | 18 | 6 | 12 | 1.333 | `[-3, -1, 0, 1, 3, 8]` | `[111]` |
| 3 | 19 | 7 | 12 | 2.571 | `[-3, -1, 0, 3, 4, 7, 8]` | `[100]` |
| 4 | 20 | 6 | 11 | 2.333 | `[-3, -1, 2, 3, 6, 7]` | `[010]` |
| 5 | 21 | 7 | 12 | 2.000 | `[-3, -1, 0, 1, 4, 5, 8]` | `[111]` |
| 6 | 22 | 8 | 12 | 2.750 | `[-3, -1, 0, 2, 3, 6, 7, 8]` | `[000]` |
| 7 | 23 | 5 | 11 | 2.400 | `[-3, -1, 4, 5, 7]` | `[111]` |

## Part B: Negative T=10 Defect Trace

- Negative evolved to `t=100`.
- Exact period detected after t=20: `10`.

| t | defect_size | defect_span | center_rel |
| ---: | ---: | ---: | ---: |
| 0 | 6 | 8 | 3.000 |
| 5 | 8 | 11 | 3.000 |
| 10 | 7 | 10 | 2.286 |
| 15 | 8 | 11 | 3.000 |
| 20 | 7 | 10 | 2.286 |
| 25 | 8 | 11 | 3.000 |
| 30 | 7 | 10 | 2.286 |
| 35 | 8 | 11 | 3.000 |
| 40 | 7 | 10 | 2.286 |
| 45 | 8 | 11 | 3.000 |
| 50 | 7 | 10 | 2.286 |
| 55 | 8 | 11 | 3.000 |
| 60 | 7 | 10 | 2.286 |
| 65 | 8 | 11 | 3.000 |
| 70 | 7 | 10 | 2.286 |
| 75 | 8 | 11 | 3.000 |
| 80 | 7 | 10 | 2.286 |
| 85 | 8 | 11 | 3.000 |
| 90 | 7 | 10 | 2.286 |
| 95 | 8 | 11 | 3.000 |
| 100 | 7 | 10 | 2.286 |

### Negative Period Snapshots

| phase | t | size | span | center_rel | active positions | dominant contexts |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 0 | 91 | 7 | 12 | 2.571 | `[-3, -2, 1, 2, 5, 7, 8]` | `[111, 011]` |
| 1 | 92 | 6 | 10 | 2.333 | `[-2, -1, 2, 3, 5, 7]` | `[010]` |
| 2 | 93 | 6 | 12 | 3.000 | `[-3, 0, 1, 5, 7, 8]` | `[111]` |
| 3 | 94 | 6 | 11 | 1.333 | `[-3, -2, -1, 2, 5, 7]` | `[000]` |
| 4 | 95 | 8 | 11 | 3.000 | `[-2, 0, 1, 2, 3, 5, 7, 8]` | `[111]` |
| 5 | 96 | 6 | 11 | 1.667 | `[-3, -2, 1, 2, 5, 7]` | `[111, 110, 001, 011, 100, 010]` |
| 6 | 97 | 7 | 11 | 3.143 | `[-2, -1, 2, 3, 5, 7, 8]` | `[010, 101]` |
| 7 | 98 | 5 | 11 | 2.000 | `[-3, 0, 1, 5, 7]` | `[111]` |
| 8 | 99 | 7 | 12 | 2.286 | `[-3, -2, -1, 2, 5, 7, 8]` | `[000]` |
| 9 | 100 | 7 | 10 | 2.286 | `[-2, 0, 1, 2, 3, 5, 7]` | `[111]` |

## Part C: Residual Context Frequencies by Phase

| phase | 000 | 001 | 010 | 011 | 100 | 101 | 110 | 111 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.167 | 0.000 | 0.000 | 0.333 | 0.167 | 0.000 | 0.000 | 0.333 |
| 1 | 0.000 | 0.000 | 0.286 | 0.143 | 0.143 | 0.286 | 0.000 | 0.143 |
| 2 | 0.000 | 0.000 | 0.000 | 0.167 | 0.167 | 0.000 | 0.167 | 0.500 |
| 3 | 0.143 | 0.143 | 0.143 | 0.143 | 0.286 | 0.000 | 0.000 | 0.143 |
| 4 | 0.000 | 0.000 | 0.500 | 0.000 | 0.167 | 0.333 | 0.000 | 0.000 |
| 5 | 0.000 | 0.000 | 0.000 | 0.143 | 0.143 | 0.000 | 0.000 | 0.714 |
| 6 | 0.500 | 0.125 | 0.125 | 0.000 | 0.250 | 0.000 | 0.000 | 0.000 |
| 7 | 0.000 | 0.000 | 0.200 | 0.000 | 0.200 | 0.000 | 0.200 | 0.400 |

## Part D: Periodic Phase Comparison

| residual phase | nearest negative phase | context L1 | active Jaccard | size delta | span delta |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 0 | 0 | 0.571 | 0.300 | -1 | 0 |
| 1 | 6 | 0.000 | 0.400 | 0 | 0 |
| 2 | 2 | 0.333 | 0.500 | 0 | 0 |
| 3 | 5 | 0.524 | 0.182 | 1 | 1 |
| 4 | 1 | 0.000 | 0.500 | 0 | 1 |
| 5 | 2 | 0.095 | 0.625 | 1 | 0 |
| 6 | 3 | 0.250 | 0.400 | 2 | 1 |
| 7 | 7 | 0.400 | 0.429 | 0 | 0 |

- Mean best phase L1: `0.272`
- Max best phase L1: `0.571`
- Mean best active Jaccard: `0.417`
- Min best active Jaccard: `0.182`

## Verdict

`PHASE_DISCRIMINANT_FOUND`.

Both traces are periodic, but at least one residual phase has no close context-profile match among negative phases.

## Methodological Limit

- This phase compares one positive residual with one nearest negative control.
- Context profiles by phase are still aggregate profiles inside each frame; they do not yet model causal-state transitions.
- If the result is `T10_APERIODIC`, the next audit should compare periodic residual structure against phase-symbol traces across all 17 rule_109 cases.
