# Fase 26: Anatomy of the T=15 Stationary Oscillator Family

## Scope

This analysis filters every `T=15` detection from the Fase-24 primitive
length-8 background sweep. It inventories the family, verifies rule
symmetries, measures each unperturbed background's temporal orbit, and
reruns one minimal witness per rule/background pair through long-horizon,
background-phase, and one-bit IC tests.

## Inventory

- Fase-24 `T=15` detections: `221`.
- Rules: `rule_73, rule_109`.
- Primitive length-8 backgrounds: `14`.
- Rule/background pairs: `20`.
- Distinct temporal motifs up to cycle phase: `25`.
- Minimum witness: `rule_109`, background `00011001`, IC `01` (length 2).

The two rules are each left-right symmetric and are exact black/white
conjugates of one another:

| rule | reflection | black/white conjugate |
| --- | --- | --- |
| rule_73 | rule_73 | rule_109 |
| rule_109 | rule_109 | rule_73 |

## Background coupling and persistence

All participating backgrounds have temporal period `3` under their unperturbed ECA orbit. Thus the observed local period
`T=15` is five times the background temporal period `T_bg=3`, rather
than a direct copy of the spatial template length 8.

Long-horizon reruns preserve exact `T=15` recurrence through step 900 in `20/20` minimal representatives.
Because period detection scans upward from 1, these runs also exclude
all smaller candidate periods in the tested range.

## Robustness summary

- Fixed-IC background phase test: `23/160` runs retain `T=15`.
- One-bit mutations of the minimal witnesses: `4/134` retain `T=15`.
- Phase-test period outcomes: `{'12': 2, '15': 23, '3': 22, '6': 69, 'none': 44}`.
- Mutation-test period outcomes: `{'12': 2, '15': 4, '3': 49, '6': 65, 'none': 14}`.

The phase test changes the relative IC/background alignment and therefore
measures a physical basin property. Co-translation equivariance of the
underlying detector was already established in Fase 25.

## Per rule/background representative

| rule | background | hits | min IC | T_bg | T=15 at 900 | phase | one-bit mutations |
| --- | --- | ---: | --- | ---: | --- | ---: | ---: |
| rule_73 | `00000011` | 2 | `0000011` | 3 | yes | 1/8 | 0/7 |
| rule_73 | `00001001` | 4 | `00110010` | 3 | yes | 2/8 | 0/8 |
| rule_73 | `00001111` | 8 | `00100000` | 3 | yes | 2/8 | 1/8 |
| rule_73 | `00101101` | 31 | `010110` | 3 | yes | 1/8 | 0/6 |
| rule_73 | `00101111` | 6 | `0000111` | 3 | yes | 1/8 | 0/7 |
| rule_73 | `00110101` | 22 | `011010` | 3 | yes | 1/8 | 0/6 |
| rule_73 | `00110111` | 13 | `011011` | 3 | yes | 1/8 | 0/6 |
| rule_73 | `00111011` | 12 | `00100100` | 3 | yes | 1/8 | 0/8 |
| rule_73 | `00111111` | 23 | `0001100` | 3 | yes | 1/8 | 1/7 |
| rule_73 | `01101111` | 2 | `01101110` | 3 | yes | 1/8 | 1/8 |
| rule_109 | `00000011` | 22 | `1110101` | 3 | yes | 1/8 | 0/7 |
| rule_109 | `00001001` | 3 | `0001001` | 3 | yes | 1/8 | 0/7 |
| rule_109 | `00001011` | 5 | `0001001` | 3 | yes | 2/8 | 0/7 |
| rule_109 | `00001101` | 4 | `0100001` | 3 | yes | 1/8 | 0/7 |
| rule_109 | `00001111` | 14 | `0001001` | 3 | yes | 1/8 | 1/7 |
| rule_109 | `00010011` | 21 | `01001` | 3 | yes | 1/8 | 0/5 |
| rule_109 | `00011001` | 9 | `01` | 3 | yes | 1/8 | 0/2 |
| rule_109 | `00110101` | 11 | `010101` | 3 | yes | 1/8 | 0/6 |
| rule_109 | `00111111` | 1 | `00111111` | 3 | yes | 1/8 | 0/8 |
| rule_109 | `01101111` | 8 | `0101001` | 3 | yes | 1/8 | 0/7 |

## Interpretation

`T=15` is not a single accidental witness. It is a stationary family
restricted to the conjugate, reflection-symmetric pair `rule_73/rule_109`,
with multiple backgrounds, multiple IC basins, and exact persistence over
the longer horizon. The shared `T_bg=3` establishes a reproducible
five-to-one temporal locking ratio. This analysis does not yet derive the
15-cycle from the two rule tables; the algebraic mechanism of that locking
remains open.
