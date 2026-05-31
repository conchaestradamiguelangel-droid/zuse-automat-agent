# Local Oscillator Family Sweep - Fase 18

## Setup

- Rules: all ECA with quiescent zero background (`f(0,0,0)=0`), `128` rules.
- ICs: all non-zero binary words of length `1..8` centered on a zero background.
- Width: `128`.
- Steps: `200`.
- Burn-in: `80`.
- Periods tested: `2..16`.
- Locality filter: post-burn-in active span `<= 32`.
- Production validation: current ZAA observers + dedup noise gate (`dedup_structure_count <= 40`).

## Result

`rule_108` is the only ECA rule found with a local oscillator under this protocol.

- Physical candidates: `179`
- Rules with candidates: `1`
- `rule_108` production-valid candidates: `132`
- Periods found: `T=2`

## Candidate Rules

| world | candidates | periods | spans | production_hits | best_len | best_word | best_period | best_span | best_laws | best_motif |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rule_108 | 179 | T2:179 | 3:42, 5:20, 6:48, 7:42, 8:27 | 132 | 3 | 101 | 2 | 3 | periodicidad, tipo_unico | ### / #.# |

## Interpretation

This sweep upgrades Fase 16 from a hand-sized search (`point`, `pair_gap1`,
`triple`) to an exhaustive local-word search through length 8. It answers
whether the `rule_108` oscillator is isolated or part of a larger ECA family
under the current observer contract.

The search is still intentionally conservative: it detects exact stationary
periodicity after burn-in on a quiescent zero background. Moving periodic
particles, oscillators requiring wider ICs, or oscillators on non-zero/ether
backgrounds are outside this protocol.

Scientific reading: `rule_108` is not one member of a broader rule family under
this protocol. It is the unique quiescent ECA rule found. The family structure
is internal to `rule_108`: 179 short IC words converge to exact local period-2
behavior, and 132 of those are accepted by the production observer as
`periodicidad`.

No period greater than 2 appears for IC words of length <= 8. The span
distribution (`3, 5, 6, 7, 8`) shows that wider local motifs exist, but the
minimal canonical witness remains `101 -> ### / #.#` with span 3.
