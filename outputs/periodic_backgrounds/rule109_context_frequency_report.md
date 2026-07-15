# Fase 65: rule_109 Context-Frequency Audit

## Question

Which local contexts `(L,C,R)` are used by active defect cells in the
residual `rule_109/bg=1100/T=8/word=00000110`, compared with the other
positive rule_109 witnesses and the bg=1100 negative controls?

## Method

- Rule: `109`
- Width: `256`
- Horizon: `t=0..50`
- Defect: `state_with_IC(t) XOR background_only(t)`.
- Context index: `(L << 2) | (C << 1) | R`, so contexts are `000` through `111`.
- For active defect cells at `t>0`, contexts are read from `state_with_IC(t-1)`.
- For `t=0`, contexts are read from the pure background frame.

## Context Frequency Table

| case | group | category | total active cells | 000 | 001 | 010 | 011 | 100 | 101 | 110 | 111 |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bg=0011/T=12/word=10010100` | `positive` | `NATURAL_PERIOD_STRONG` | 321 | 0.065 | 0.196 | 0.131 | 0.081 | 0.019 | 0.118 | 0.162 | 0.227 |
| `bg=0110/T=8/word=0000011` | `positive` | `HORIZON_ACCEPTABLE` | 298 | 0.007 | 0.319 | 0.315 | 0.010 | 0.319 | 0.007 | 0.010 | 0.013 |
| `bg=1011/T=10/word=00000001` | `positive` | `HORIZON_ACCEPTABLE` | 396 | 0.051 | 0.232 | 0.109 | 0.058 | 0.232 | 0.000 | 0.058 | 0.260 |
| `bg=1100/T=8/word=00000110` | `positive` | `HORIZON_ACCEPTABLE` | 328 | 0.119 | 0.040 | 0.143 | 0.119 | 0.183 | 0.079 | 0.049 | 0.268 |
| `bg=1100/T=12/word=00101001` | `positive` | `NATURAL_PERIOD_STRONG` | 321 | 0.065 | 0.019 | 0.131 | 0.162 | 0.196 | 0.118 | 0.081 | 0.227 |
| `bg=1100/T=3/word=00001110` | `negative_control` | `NEGATIVE` | 416 | 0.005 | 0.269 | 0.267 | 0.046 | 0.231 | 0.046 | 0.048 | 0.089 |
| `bg=1100/T=6/word=00100110` | `negative_control` | `NEGATIVE` | 314 | 0.061 | 0.217 | 0.134 | 0.083 | 0.010 | 0.131 | 0.156 | 0.210 |
| `bg=1100/T=10/word=00111001` | `negative_control` | `NEGATIVE` | 330 | 0.094 | 0.036 | 0.133 | 0.142 | 0.185 | 0.091 | 0.064 | 0.255 |

## Separation Tests

- Contexts in every positive and no negative control: none
- Contexts used by the residual and by no other positive: none
- Contexts used by every other positive but absent from the residual: none
- Contexts never used by any selected defect cell: none

## Residual Frequency Neighbours

| rank | case | group | category | L1 distance from residual |
| ---: | --- | --- | --- | ---: |
| 1 | `bg=1100/T=10/word=00111001` | `negative_control` | `NEGATIVE` | 0.104 |
| 2 | `bg=1100/T=12/word=00101001` | `positive` | `NATURAL_PERIOD_STRONG` | 0.256 |
| 3 | `bg=1011/T=10/word=00000001` | `positive` | `HORIZON_ACCEPTABLE` | 0.503 |
| 4 | `bg=0011/T=12/word=10010100` | `positive` | `NATURAL_PERIOD_STRONG` | 0.618 |
| 5 | `bg=1100/T=6/word=00100110` | `negative_control` | `NEGATIVE` | 0.671 |
| 6 | `bg=1100/T=3/word=00001110` | `negative_control` | `NEGATIVE` | 0.802 |
| 7 | `bg=0110/T=8/word=0000011` | `positive` | `HORIZON_ACCEPTABLE` | 1.174 |

## Verdict

- Context status: `CONTEXT_UNDISCRIMINATED`
- Intervention status: `NO_UNUSED_CONTEXT_INTERVENTION_CANDIDATE`

The selected context-frequency descriptors do not expose a clear pattern.

## Methodological Limit

- The negative set is deliberately narrow: three bg=1100 negative controls.
- A context absent from these 8 cases is only a candidate for safe intervention, not a proof of global safety.
- This phase measures context usage, not ANF gradients for new rules.
