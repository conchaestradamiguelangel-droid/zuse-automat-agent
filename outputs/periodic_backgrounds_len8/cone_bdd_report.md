# Fase 42: ROBDD Audit of the T=15 Cone Circuit

## Question

Fase 41 found no sparse table or input-support shortcut inside the
25-cell, 12-step cone. Fase 42 constructs reduced ordered binary decision
diagrams (ROBDDs) for the same cone circuit and tests whether canonical
Boolean reduction finds hidden simplification.

Variable orders tested: `natural`, `reverse`, and `center_out`.

## Summary by variable order

| order | active nodes | vector nodes | active support | vector support |
| --- | ---: | ---: | ---: | ---: |
| `natural` | 17141..36966 | 51539..53901 | 25..25 | 25..25 |
| `reverse` | 16061..36907 | 51539..53481 | 25..25 | 25..25 |
| `center_out` | 43382..91935 | 126559..128513 | 25..25 | 25..25 |

## Representative table

| family | rule | background | order | active nodes | vector nodes | active support | vector support | nonconstant outputs |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `F09` | 73 | `00000011` | `center_out` | 77302 | 127064 | 25 | 25 | 25 |
| `F10` | 73 | `00001001` | `center_out` | 43382 | 126978 | 25 | 25 | 25 |
| `F02` | 73 | `00001111` | `center_out` | 76258 | 126559 | 25 | 25 | 25 |
| `F06` | 73 | `00101101` | `center_out` | 87889 | 127916 | 25 | 25 | 25 |
| `F04` | 73 | `00101111` | `center_out` | 55180 | 128513 | 25 | 25 | 25 |
| `F03` | 73 | `00110101` | `center_out` | 90176 | 127838 | 25 | 25 | 25 |
| `F01` | 73 | `00110111` | `center_out` | 52075 | 127008 | 25 | 25 | 25 |
| `F01` | 73 | `00111011` | `center_out` | 46811 | 128319 | 25 | 25 | 25 |
| `F02` | 73 | `00111111` | `center_out` | 64741 | 128010 | 25 | 25 | 25 |
| `F01` | 73 | `01101111` | `center_out` | 59839 | 127513 | 25 | 25 | 25 |
| `F12` | 109 | `00000011` | `center_out` | 89703 | 127452 | 25 | 25 | 25 |
| `F00` | 109 | `00001001` | `center_out` | 62385 | 127731 | 25 | 25 | 25 |
| `F05` | 109 | `00001011` | `center_out` | 69665 | 127672 | 25 | 25 | 25 |
| `F02` | 109 | `00001101` | `center_out` | 89802 | 126849 | 25 | 25 | 25 |
| `F08` | 109 | `00001111` | `center_out` | 66759 | 126995 | 25 | 25 | 25 |
| `F00` | 109 | `00010011` | `center_out` | 53860 | 127021 | 25 | 25 | 25 |
| `F00` | 109 | `00011001` | `center_out` | 70455 | 128240 | 25 | 25 | 25 |
| `F03` | 109 | `00110101` | `center_out` | 82985 | 128129 | 25 | 25 | 25 |
| `F07` | 109 | `00111111` | `center_out` | 77999 | 126957 | 25 | 25 | 25 |
| `F11` | 109 | `01101111` | `center_out` | 91935 | 127224 | 25 | 25 | 25 |

## Verdict

**Status:** `BDD_NO_INPUT_REDUCTION`.

ROBDD reduction confirms the Fase 41 input-support result: the
active localized outputs still depend on all 25 cone inputs under
all tested variable orders. BDD node counts vary with ordering, but
no order exposes an irrelevant input variable. This does not prove
global minimum BDD size over all 25! orders, but it rules out the
most useful simple Boolean reduction: input elimination.
