# Fase 42: ROBDD Audit of the T=15 Cone Circuit

## Question

Fase 41 found no sparse table or input-support shortcut inside the
25-cell, 12-step cone. Fase 42 constructs reduced ordered binary decision
diagrams (ROBDDs) for the same cone circuit and tests whether canonical
Boolean reduction finds hidden simplification.

Variable order tested: `natural` (left-to-right cone order). BDD size
is order-dependent, but input support is a semantic property: if a
reduced BDD contains all 25 variables, no input variable is irrelevant
for that represented Boolean function.

## Summary by variable order

| order | active nodes | vector nodes | active support | vector support |
| --- | ---: | ---: | ---: | ---: |
| `natural` | 17141..36966 | 51539..53901 | 25..25 | 25..25 |

## Representative table

| family | rule | background | order | active nodes | vector nodes | active support | vector support | nonconstant outputs |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `F09` | 73 | `00000011` | `natural` | 25464 | 52846 | 25 | 25 | 25 |
| `F10` | 73 | `00001001` | `natural` | 20501 | 51804 | 25 | 25 | 25 |
| `F02` | 73 | `00001111` | `natural` | 29856 | 52048 | 25 | 25 | 25 |
| `F06` | 73 | `00101101` | `natural` | 30464 | 52031 | 25 | 25 | 25 |
| `F04` | 73 | `00101111` | `natural` | 23868 | 53901 | 25 | 25 | 25 |
| `F03` | 73 | `00110101` | `natural` | 28916 | 52187 | 25 | 25 | 25 |
| `F01` | 73 | `00110111` | `natural` | 21557 | 52185 | 25 | 25 | 25 |
| `F01` | 73 | `00111011` | `natural` | 17141 | 52626 | 25 | 25 | 25 |
| `F02` | 73 | `00111111` | `natural` | 31203 | 53121 | 25 | 25 | 25 |
| `F01` | 73 | `01101111` | `natural` | 24405 | 52257 | 25 | 25 | 25 |
| `F12` | 109 | `00000011` | `natural` | 36078 | 52022 | 25 | 25 | 25 |
| `F00` | 109 | `00001001` | `natural` | 25363 | 52401 | 25 | 25 | 25 |
| `F05` | 109 | `00001011` | `natural` | 30283 | 52231 | 25 | 25 | 25 |
| `F02` | 109 | `00001101` | `natural` | 36966 | 51688 | 25 | 25 | 25 |
| `F08` | 109 | `00001111` | `natural` | 28864 | 51909 | 25 | 25 | 25 |
| `F00` | 109 | `00010011` | `natural` | 23258 | 53131 | 25 | 25 | 25 |
| `F00` | 109 | `00011001` | `natural` | 27639 | 52555 | 25 | 25 | 25 |
| `F03` | 109 | `00110101` | `natural` | 31225 | 53309 | 25 | 25 | 25 |
| `F07` | 109 | `00111111` | `natural` | 25666 | 53178 | 25 | 25 | 25 |
| `F11` | 109 | `01101111` | `natural` | 33759 | 51539 | 25 | 25 | 25 |

## Verdict

**Status:** `BDD_NO_INPUT_REDUCTION`.

ROBDD reduction confirms the Fase 41 input-support result: the
active localized outputs still depend on all 25 cone inputs.
The natural-order ROBDDs contain all 25 support variables for
every representative, certifying that no input variable is
irrelevant to the represented active-output functions. This does
not prove global minimum BDD size over all 25! orders, but it
does rule out Boolean input elimination.
