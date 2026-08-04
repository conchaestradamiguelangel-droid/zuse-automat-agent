# Fase 88: Long-Horizon Branches of the Reachable h=11 Selectors

## Question

What dynamical attractors receive the two minimal selectors that Fase 87
found physically reachable but absent from the stationary T=12 basin?

## Predeclared Protocol

- Source cohort: the same 2,008 rule_73 runs from Fases 86-87.
- Long horizon: 1,000 steps; burn-in 80; bounded span <=32.
- Tail recurrence: exact equality over t=500..1000, periods 1..120.
- Stationary recurrence requires equal offsets and absolute position.
- Moving recurrence requires equal offsets and constant non-zero drift.
- The original detector searched only periods 2..16; longer exact periods
  are reported as new diagnostics, not silently relabeled source hits.
- No threshold, paper, DOI, tag, or release is changed.

## Result

Status: `REACHABLE_SELECTORS_ROUTE_TO_T6_AND_T30_ATTRACTORS`.

The bit-12 selector belongs to a persistent T=6 attractor, while every physical [9,12] rescue preimage belongs to a persistent T=30 attractor outside the original period-search range.

## Branch A: bit-12 selector

- Selector: `0x0311630`.
- Reference IC: `01101111/00110101`.
- Long-tail class: `STATIONARY`.
- Exact tail period: `6`.
- Target occurrences through t=989: `152`.
- Source ICs in the same translation-normalized T=6 shape attractor: `1`.
- Backgrounds represented in that basin: `['01101111']`.

### Six-phase cycle at t=80..85

| phase | assignment | in subcube | reference operator | bit12 selector | Fase85 comparable | defect size | span |
| ---: | --- | --- | --- | --- | --- | ---: | ---: |
| 0 | `0x0311630` | true | true | true | false | 4 | 8 |
| 1 | `0x1b446b7` | false | false | false | n/a | 7 | 10 |
| 2 | `0x0b11634` | false | false | false | n/a | 6 | 12 |
| 3 | `0x03446b0` | false | true | false | n/a | 7 | 12 |
| 4 | `0x1b11637` | false | false | false | n/a | 6 | 12 |
| 5 | `0x0b446b4` | false | false | false | n/a | 5 | 7 |

## Branch B: [9,12] rescue

- Selector: `0x035aab0`.
- Physical ICs audited: `40`.
- Long-horizon persistent bounded ICs: `40`.
- Tail classes: `{'STATIONARY_T30': 40}`.
- Unique translation-normalized cycle hashes: `1`.
- Total exact selector occurrences through t=989: `1203`.

| background | IC | tail class | period | drift | max span | selector occurrences | first occurrence |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `00110111` | `001111` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `00110111` | `0011111` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `00110111` | `1110100` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `00110111` | `00011111` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `00110111` | `01110100` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `00111011` | `0111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111011` | `01111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111011` | `001111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111011` | `101111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111011` | `0011111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111011` | `1000110` | STATIONARY | 30 | 0 | 12 | 31 | 86 |
| `00111011` | `1011111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111011` | `10011111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111011` | `11000110` | STATIONARY | 30 | 0 | 12 | 31 | 86 |
| `00111011` | `11011111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `0011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `00111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `000111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `010001` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `00111101` | `100111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `0001111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `0100011` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `00111101` | `1001111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `10001111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `00111101` | `10100011` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `00111101` | `11001111` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `01101111` | `10100` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `01101111` | `110100` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `01101111` | `1100011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `01101111` | `1101000` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `01101111` | `1110011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `01101111` | `00101011` | STATIONARY | 30 | 0 | 12 | 31 | 83 |
| `01101111` | `00111011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `01101111` | `00111110` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `01101111` | `01110011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `01101111` | `01111011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `01101111` | `11100011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |
| `01101111` | `11101000` | STATIONARY | 30 | 0 | 12 | 30 | 104 |
| `01101111` | `11110011` | STATIONARY | 30 | 0 | 12 | 30 | 101 |

## Interpretation

The two reachable selectors do not fail to settle. They select
different persistent attractors: T=6 for the bit-12 branch and
T=30 for the [9,12] rescue branch. The earlier NONSTATIONARY label
for the rescue was relative to the source detector's period cap
of 16, not evidence of genuine aperiodicity.

## Methodological Limits

- The T=6 basin count uses translation-normalized defect-shape cycles;
  it does not assert equality of complete infinite backgrounds.
- Long recurrence is verified to t=1000 and period 120, not proved for
  arbitrary time or periods above 120.
- Rescue ICs are the exact 40 preimages found under the four-background,
  centered len1..8 source protocol.
- The result is local to rule_73 and does not establish a universal
  bifurcation law for cellular automata.
- No paper, DOI, tag, release, or threshold changed.
