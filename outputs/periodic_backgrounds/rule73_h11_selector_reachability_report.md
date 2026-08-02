# Fase 87: Preimage and Basin Restrictions of the h=11 Selectors

## Question

Why do the nine minimal symbolic selectors of Fase 85 fail to appear
in the physical T=12 census of Fase 86?

## Predeclared Protocol

The same 2,008 source-protocol runs are recomputed: rule_73, the four
reference backgrounds, all 502 centered non-zero IC words of length
1..8, width 256, 300 steps, and burn-in 80. Every bounded state from
t=80 through t=289 is aligned on its defect and tested against the nine
minimal selector assignments. The upper limit leaves eleven future
steps available for the exact h=11 operator test.

The gates are evaluated without threshold fitting:

1. exact selector appears in any bounded post-burn state;
2. exact selector appears at the original sample phase t=80;
3. exact selector preserves the reference boundary trace and final
   local background, hence the exact defect operator;
4. the source run is a stationary period-12 oscillator.

Affine GF(2) invariants are computed exactly from reached subcube masks
as a descriptive reachability audit, not fitted as a classifier.

## Result

Status: `MINIMAL_SELECTORS_EXCLUDED_FROM_T12_BASIN`.

Minimal selectors have bounded physical preimages under the exact operator but none belongs to the persistent T=12 basin.

- Runs processed: `2008`
- Bounded source trajectories: `1879`
- Post-burn states scanned: `394590`
- Reference-operator subcube occurrences: `6930`
- Unique all-phase reference-operator subcube masks: `17`
- Minimal selectors with any bounded post-burn preimage: `2/9`
- Minimal selectors reached at t=80: `1/9`
- Minimal selectors reached with reference operator: `2/9`
- Minimal selectors in stationary T=12 reference basin: `0/9`

## Selector Gate Audit

| selector | role | changed/reverted bits | post-burn ICs | t=80 ICs | operator ICs | operator IC periods | T12 basin ICs | fixed-phase invariant violations | all-phase invariant violations |
| --- | --- | --- | ---: | ---: | ---: | --- | ---: | --- | --- |
| `0x0310230` | `A_ATOMIC_BREAK` | `[10]` | 0 | 0 | 0 | `{}` | 0 | `[]` | `[]` |
| `0x03106b0` | `A_ATOMIC_BREAK` | `[7]` | 0 | 0 | 0 | `{}` | 0 | `[0, 2]` | `[0]` |
| `0x0310e30` | `A_ATOMIC_BREAK` | `[11]` | 0 | 0 | 0 | `{}` | 0 | `[1]` | `[]` |
| `0x0311630` | `A_ATOMIC_BREAK` | `[12]` | 1 | 1 | 1 | `{'6': 1}` | 0 | `[]` | `[]` |
| `0x0312630` | `A_ATOMIC_BREAK` | `[13]` | 0 | 0 | 0 | `{}` | 0 | `[1]` | `[]` |
| `0x0318630` | `A_ATOMIC_BREAK` | `[15]` | 0 | 0 | 0 | `{}` | 0 | `[]` | `[]` |
| `0x0350630` | `A_ATOMIC_BREAK` | `[18]` | 0 | 0 | 0 | `{}` | 0 | `[2]` | `[0]` |
| `0x03530b0` | `B_MINIMAL_RESCUE` | `[11, 15]` | 0 | 0 | 0 | `{}` | 0 | `[1]` | `[]` |
| `0x035aab0` | `B_MINIMAL_RESCUE` | `[9, 12]` | 40 | 0 | 40 | `{'NONSTATIONARY': 40}` | 0 | `[0]` | `[]` |

## Exact Affine Reachability Invariants

### Fixed sample phase t=80, stationary T=12 reference basin

| id | subcube indices | global input bits | parity |
| ---: | --- | --- | ---: |
| 0 | `[0, 1]` | `[7, 9]` | 0 |
| 1 | `[3, 5]` | `[11, 13]` | 0 |
| 2 | `[0, 7]` | `[7, 18]` | 0 |

### All scanned phases with the reference operator

| id | subcube indices | global input bits | parity |
| ---: | --- | --- | ---: |
| 0 | `[0, 7]` | `[7, 18]` | 0 |

Each row means that the XOR of the listed subcube bits has the
reported parity for every reached mask in that cohort.

## Interpretation

The exact operator admits physical selector preimages, but those
preimages do not settle into the stationary T=12 basin. The
restriction is dynamical-basin selection rather than local
operator reachability.

## Methodological Limits

- Exhaustive only for four backgrounds, centered non-zero ICs len1..8,
  and bounded trajectories accepted by the original sweep protocol.
- Runs rejected for extinction or span greater than 32 are outside the
  bounded source cohort and are not assigned post-burn preimages.
- Affine invariants summarize observed reachability exactly but do not
  prove a universal conservation law of rule_73.
- Absence here does not exclude longer, shifted, or multi-site ICs.
- No paper, DOI, tag, release, or threshold changed.
