# Fase 67b: rule_109 Phase Cross-Validation

## Question

Do the dominant contexts from the residual's discriminant phases generalize
across the five positive `rule_109` witnesses?

The primary target context is `100`, because Fase 67 found it as the unique
dominant context in residual phase 3, which had the strongest spatial
separation from the nearest negative phase (`active Jaccard = 0.182`).
The report also checks `011` and `111`, the dominant contexts from residual
phases 0 and 7.

## Dataset

- Positives: 5
- Negative controls: 3
- Horizon: `t=0..80`
- Defect: `state_with_IC(t) XOR background_only(t)`.

## Case Summary

| group | case | period | target dominant phases | target unique phases |
| --- | --- | ---: | --- | --- |
| `positive` | `bg=0011/T=12/word=10010100` | 12 | none | none |
| `positive` | `bg=0110/T=8/word=0000011` | 1 | `0` | none |
| `positive` | `bg=1011/T=10/word=00000001` | 10 | `0`, `2`, `5`, `6`, `7` | none |
| `positive` | `bg=1100/T=8/word=00000110` | 8 | `2` | `2` |
| `positive` | `bg=1100/T=12/word=00101001` | 12 | `1`, `3`, `4`, `7`, `10` | none |
| `negative_control` | `bg=1100/T=3/word=00001110` | 3 | `0` | none |
| `negative_control` | `bg=1100/T=6/word=00100110` | 6 | none | none |
| `negative_control` | `bg=1100/T=10/word=00111001` | 10 | `5` | none |

## Verdict

`PHASE_CROSSVAL_CONSISTENT`.

- Positive cases with `100` dominant: 4/5
- Positive cases with `100` uniquely dominant: 1/5
- Negative controls with `100` dominant: 2/3
- Negative controls with `100` uniquely dominant: 0/3

## Target Context Summary

| context | positives dominant | positives unique | negatives dominant | negatives unique |
| --- | ---: | ---: | ---: | ---: |
| `011` | 3/5 | 1/5 | 2/3 | 0/3 |
| `100` | 4/5 | 1/5 | 2/3 | 0/3 |
| `111` | 4/5 | 4/5 | 3/3 | 2/3 |

Context 100 is dominant in 4/5 positives. It also appears as dominant in at least one negative control, so it is not a clean positive-only discriminator.

## Methodological Limit

- This is a cross-check of one phase-level context, not a full causal-state model.
- Dominance is computed within each phase frame, not across phase transitions.
- A partial or negative result here motivates Fase 68: phase-symbol / causal-state analysis over all 17 rule_109 cases.
