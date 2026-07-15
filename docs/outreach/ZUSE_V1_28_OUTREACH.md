# ZUSE v1.28 Outreach Pack

## Short Post

ZUSE v1.28 is out.

Fase 63 tests algebraic interventions around the `rule_109` ANF-gradient
residual.

Result: `ALGEBRAIC_INTERVENTION_PREFLIGHT_BLOCKED`.

- Target residual: `bg=1100/T=8/word=00000110`.
- Four minimal ANF edits tested:
  - remove `LC` -> rule 173
  - remove `CR` -> rule 229
  - add isolated `C` -> rule 161
  - add `LR` without center -> rule 205
- All four edits are algebraically verified.
- On `bg=1100`, IC length 1..8:
  - 0 stationary oscillators for all four synthetic rules.
  - 0 moving oscillators for all four synthetic rules.

So the direct intervention is blocked before cone-ANF measurement: the
monomial-level edits destroy comparable oscillator support.

Preprint: https://doi.org/10.5281/zenodo.21385190
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.28
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fase 63: ALGEBRAIC_INTERVENTION_PREFLIGHT_BLOCKED.

v1.28 integrates the algebraic intervention preflight around the surviving
`rule_109` ANF-gradient residual:

`bg=1100/T=8/word=00000110`

The local ANF of `rule_109` is:

`1 XOR L XOR LC XOR R XOR CR XOR LCR`

Four minimal monomial-level interventions were tested:

- remove `LC` -> synthetic rule 173
- remove `CR` -> synthetic rule 229
- add isolated `C` -> synthetic rule 161
- add `LR` without center -> synthetic rule 205

All four edits are algebraically verified. A preflight oscillator sweep on
`bg=1100`, using IC words of length 1..8, finds:

- rule 173: 502 ICs, 0 stationary, 0 moving, 12 period-1 aliases
- rule 229: 502 ICs, 0 stationary, 0 moving, 8 period-1 aliases
- rule 161: 502 ICs, 0 stationary, 0 moving, 0 aliases
- rule 205: 502 ICs, 0 stationary, 0 moving, 0 aliases

No cone-ANF gradient measurement is run for these synthetic rules because none
preserves a comparable stationary oscillator on `bg=1100`.

Interpretation: the result is an informative block, not a failed measurement.
At monomial-edit resolution, the `rule_109` mechanism is not separable into
independently removable local ANF terms while preserving oscillator support.
The next causal intervention must be finer or more conditioned, such as a
Hamming-1 truth-table neighborhood test.

Preprint: https://doi.org/10.5281/zenodo.21385190
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.28 - algebraic intervention preflight in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.28 tests whether a surviving `rule_109` ANF-gradient residual can be probed
by minimal algebraic intervention.

Target residual:

`bg=1100/T=8/word=00000110`

Four local ANF edits are tested:

- remove `LC`
- remove `CR`
- add isolated `C`
- add `LR` without center

These produce synthetic ECA rules 173, 229, 161, and 205. All edits are
verified algebraically.

Result:

- 502 ICs tested on `bg=1100` for each synthetic rule.
- 0 stationary oscillators for all four rules.
- 0 moving oscillators for all four rules.

So the direct intervention is blocked before ANF-gradient measurement: the
minimal monomial-level edits destroy the comparable oscillator support.

Preprint: https://doi.org/10.5281/zenodo.21385190
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: HN account karma was 2 last time checked. Do not post Show HN until the
account has enough karma to avoid auto-removal.
