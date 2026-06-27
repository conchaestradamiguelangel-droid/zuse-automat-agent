# Fase 30: Background-Indexed Shape Families for the T=15 Cycle

## Question

Fase 29 showed that the T=15 cycle is not described by a single
background-independent defect shape or by one fixed local block
signature. Fase 30 asks whether the background-dependent defect cycles
nevertheless collapse into a small number of phase-rotated shape
families.

Two five-state cycles are considered equivalent when one is a cyclic
phase rotation of the other.

## Summary

- Representatives: `20`.
- Global shape families: `13`.
- Largest global family size: `3`.
- rule_109: `8` families; largest family size `3`.
- rule_73: `7` families; largest family size `3`.

## Shape families by rule

| rule | family | size | backgrounds (phase shift) |
| --- | ---: | ---: | --- |
| rule_109 | 1 | 3 | `00001001` (s=0), `00010011` (s=0), `00011001` (s=0) |
| rule_109 | 2 | 1 | `00110101` (s=3) |
| rule_109 | 3 | 1 | `00001011` (s=4) |
| rule_109 | 4 | 1 | `00111111` (s=2) |
| rule_109 | 5 | 1 | `00001111` (s=4) |
| rule_109 | 6 | 1 | `00001101` (s=0) |
| rule_109 | 7 | 1 | `01101111` (s=4) |
| rule_109 | 8 | 1 | `00000011` (s=1) |
| rule_73 | 1 | 3 | `00110111` (s=0), `00111011` (s=3), `01101111` (s=0) |
| rule_73 | 2 | 2 | `00001111` (s=1), `00111111` (s=4) |
| rule_73 | 3 | 1 | `00101111` (s=3) |
| rule_73 | 4 | 1 | `00110101` (s=3) |
| rule_73 | 5 | 1 | `00101101` (s=3) |
| rule_73 | 6 | 1 | `00000011` (s=0) |
| rule_73 | 7 | 1 | `00001001` (s=4) |

## Shared families across conjugate rules

| family | size | rules | members |
| ---: | ---: | --- | --- |
| 1 | 3 | rule_73, rule_109 | `rule_73/00001111`, `rule_73/00111111`, `rule_109/00001101` |
| 2 | 2 | rule_73, rule_109 | `rule_73/00110101`, `rule_109/00110101` |

## Descriptor tests

| descriptor | buckets | pure buckets | ambiguous buckets | determines family |
| --- | ---: | ---: | ---: | --- |
| `active_count` | 5 | 0 | 5 | False |
| `transition_count` | 3 | 0 | 3 | False |
| `active_transition_pair` | 8 | 0 | 8 | False |
| `temporal_orbit_canonical` | 20 | 20 | 0 | True |

Simple scalar background descriptors do not determine the shape family.
The strongest tested descriptor is the canonical temporal orbit of the
background under the same rule; it is exact in this representative set,
but this is mostly a restatement of the full background orbit rather
than a compact symbolic law.

## Verdict

**Status:** `PARTIAL_POSITIVE`.

The T=15 family is not one universal defect cycle. It decomposes into
a finite set of background-indexed five-state shape families: seven
families for `rule_73`, eight for `rule_109`, and thirteen globally
after merging exact phase-rotated cycles shared across the conjugate
rules. This is stronger than the Fase 29 negative result because it
shows where the background dependence lives: in discrete phase-rotated
shape families, not in unstructured variation.

## Falsifiable implication

A future symbolic derivation should map the temporal background orbit
and local IC alignment to one of these finite shape families and a
phase offset. Any derivation predicting a single universal five-state
defect cycle is falsified; any derivation predicting arbitrary
unclustered shape variation is also too weak.
