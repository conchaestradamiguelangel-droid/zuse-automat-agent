# Fase 43: ROBDD Order-Sensitivity Preflight

## Question

Fase 42 established that all 25 causal-cone inputs are semantically
necessary. Fase 43 does not reopen that question. It asks whether the
ROBDD representation is sensitive to variable order, using the three
orders already materialized in Fase 42: `natural`, `reverse`, and
`center_out`.

This is a pre-SIFT audit. It is not a full dynamic-reordering run and
does not certify global BDD optimality over all 25! variable orders.

## Summary

Status: `ORDER_SENSITIVITY_FOUND`.

- Orders analyzed: `center_out`, `natural`, `reverse`
- Best global order: `reverse`
- Natural total active nodes: 552476
- Best global total active nodes: 549713
- Active-node reduction vs natural: 0.5%
- Natural total vector nodes: 1048969
- Best global total vector nodes: 1049085
- Vector-node reduction vs natural: -0.011%
- Representatives where best order is not natural: 14/20
- Representatives where `center_out` is worst: 20/20
- Maximum order-sensitivity ratio: 3.119x
- 25/25 input support preserved under all analyzed orders: `True`

## Order table

| order | total active | total vector | active range | vector range | support |
| --- | ---: | ---: | ---: | ---: | --- |
| `reverse` | 549713 | 1049085 | 16061..36907 | 51539..53481 | 25..25 / 25..25 |
| `natural` | 552476 | 1048969 | 17141..36966 | 51539..53901 | 25..25 / 25..25 |
| `center_out` | 1409201 | 2549988 | 43382..91935 | 126559..128513 | 25..25 / 25..25 |

## Per-representative best order

| family | rule | background | best order | natural active | best active | reduction | worst order | sensitivity |
| --- | ---: | --- | --- | ---: | ---: | ---: | --- | ---: |
| `F09` | 73 | `00000011` | `natural` | 25464 | 25464 | 0.0% | `center_out` | 3.036x |
| `F10` | 73 | `00001001` | `reverse` | 20501 | 19662 | 4.092% | `center_out` | 2.206x |
| `F02` | 73 | `00001111` | `reverse` | 29856 | 29567 | 0.968% | `center_out` | 2.579x |
| `F06` | 73 | `00101101` | `reverse` | 30464 | 30307 | 0.515% | `center_out` | 2.9x |
| `F04` | 73 | `00101111` | `natural` | 23868 | 23868 | 0.0% | `center_out` | 2.312x |
| `F03` | 73 | `00110101` | `natural` | 28916 | 28916 | 0.0% | `center_out` | 3.119x |
| `F01` | 73 | `00110111` | `natural` | 21557 | 21557 | 0.0% | `center_out` | 2.416x |
| `F01` | 73 | `00111011` | `reverse` | 17141 | 16061 | 6.301% | `center_out` | 2.915x |
| `F02` | 73 | `00111111` | `reverse` | 31203 | 30542 | 2.118% | `center_out` | 2.12x |
| `F01` | 73 | `01101111` | `natural` | 24405 | 24405 | 0.0% | `center_out` | 2.452x |
| `F12` | 109 | `00000011` | `reverse` | 36078 | 35749 | 0.912% | `center_out` | 2.509x |
| `F00` | 109 | `00001001` | `reverse` | 25363 | 24405 | 3.777% | `center_out` | 2.556x |
| `F05` | 109 | `00001011` | `reverse` | 30283 | 29972 | 1.027% | `center_out` | 2.324x |
| `F02` | 109 | `00001101` | `reverse` | 36966 | 36907 | 0.16% | `center_out` | 2.433x |
| `F08` | 109 | `00001111` | `reverse` | 28864 | 28755 | 0.378% | `center_out` | 2.322x |
| `F00` | 109 | `00010011` | `reverse` | 23258 | 21557 | 7.314% | `center_out` | 2.498x |
| `F00` | 109 | `00011001` | `reverse` | 27639 | 27158 | 1.74% | `center_out` | 2.594x |
| `F03` | 109 | `00110101` | `reverse` | 31225 | 30615 | 1.954% | `center_out` | 2.711x |
| `F07` | 109 | `00111111` | `reverse` | 25666 | 25464 | 0.787% | `center_out` | 3.063x |
| `F11` | 109 | `01101111` | `natural` | 33759 | 33759 | 0.0% | `center_out` | 2.723x |

## Interpretation

The ROBDD size is order-sensitive, but the tested improvement is small
globally and does not alter the Fase 42 support result: every analyzed
order still keeps 25/25 inputs in the active-output and full-vector
supports. The `center_out` order is consistently poor, which is useful
negative guidance for future dynamic reordering.

The next rigorous step, if pursued, is a real dynamic-reordering pass
(SIFT or adjacent-swap search with checkpointing) optimized for BDD
size only. Fase 43 shows that this is a representation-compactness
problem, not an input-elimination problem.
