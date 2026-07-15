# Fase 64: rule_109 Hamming-1 Neighborhood on bg=1100

## Question

Do any one-bit truth-table perturbations of `rule_109` preserve
stationary oscillator support on the residual background `bg=1100`?

Fase 63 tested whole-monomial ANF edits. Those edits are algebraically
natural but flip multiple truth-table bits at once. Fase 64 instead uses
the atomic ECA intervention: `rule_i = 109 XOR (1 << i)` for `i=0..7`.

## Status

`HAMMING1_WITNESSES_FOUND`

At least one Hamming-1 neighbor has a bg=1100 stationary oscillator and was measured by the ANF-gradient protocol.

## Hamming-1 table

| bit flipped | rule | binary | ANF monomials | center mediated | raw catalog | Fase 55 census | stationary hits | moving hits | aliases | max span | periods | measured |
| ---: | ---: | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| 0 | 108 | `01101100` | `C XOR LR` | false | true | false | 237 | 0 | 0 | 9 | [2] | 1 |
| 1 | 111 | `01101111` | `1 XOR L XOR LR XOR LC` | false | false | false | 0 | 0 | 0 | 0 | [] | 0 |
| 2 | 105 | `01101001` | `1 XOR R XOR C XOR L` | false | false | false | 0 | 0 | 0 | 0 | [] | 0 |
| 3 | 101 | `01100101` | `1 XOR R XOR L XOR LC` | true | false | false | 0 | 0 | 0 | 0 | [] | 0 |
| 4 | 125 | `01111101` | `1 XOR R XOR CR XOR LR` | false | false | false | 0 | 0 | 0 | 0 | [] | 0 |
| 5 | 77 | `01001101` | `1 XOR R XOR CR XOR L XOR LR XOR LC` | false | false | false | 0 | 0 | 0 | 0 | [] | 0 |
| 6 | 45 | `00101101` | `1 XOR R XOR CR XOR L` | true | false | false | 0 | 0 | 0 | 0 | [] | 0 |
| 7 | 237 | `11101101` | `1 XOR R XOR CR XOR L XOR LC` | true | false | false | 0 | 0 | 0 | 0 | [] | 0 |

## ANF measurements

### bit 0 / rule_108 / `00000001`

| T_WINDOW | active | dist classes | slope | R^2 | delta vs T15 | comparable |
| ---: | ---: | ---: | ---: | ---: | ---: | --- |
| 2 | 5 | 4 | -0.017102 | 0.264706 | 94.43% | false |
| 12 | 5 | 4 | -0.017102 | 0.264706 | 94.43% | false |

## Interpretation

This phase tests whether the Fase 63 block was caused by intervention
granularity. If even Hamming-1 neighbors lack stationary support, the
`rule_109/bg=1100` oscillator is locally isolated in truth-table space
under the current periodic-background detector. If a neighbor survives
only as a compact low-period oscillator, it is support-preserving in a
weak sense but not a comparable replacement for the wide residual
mechanism.
