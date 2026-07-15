# ZUSE v1.29 Outreach Pack

## Short Post

ZUSE v1.29 is out.

Fase 64 audits the Hamming-1 neighbourhood of `rule_109` on the residual
background `bg=1100`.

Result: `HAMMING1_WITNESSES_FOUND_NOT_COMPARABLE`.

- Correct Hamming-1 neighbours: 108, 111, 105, 101, 125, 77, 45, 237.
- Correction: bit 4 is rule 125, not rule 93 (`109 XOR 16 = 125`).
- 7/8 neighbours have 0 stationary and 0 moving oscillators on `bg=1100`.
- The only survivor is rule 108, from bit flip 0.
- rule_108 produces compact T=2 witnesses, max_span=9.
- ANF slope: -0.017102, R²=0.264706, comparable=false.

So Hamming-1 perturbation does not produce a comparable modified
`rule_109/bg=1100/T=8` ANF-gradient mechanism.

Preprint: https://doi.org/10.5281/zenodo.21385274
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.29
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fase 64: HAMMING1_WITNESSES_FOUND_NOT_COMPARABLE.

v1.29 audits the Hamming-1 truth-table neighbourhood of `rule_109` on the
residual background:

`bg=1100`

The eight one-bit neighbours are:

- bit 0 -> rule 108
- bit 1 -> rule 111
- bit 2 -> rule 105
- bit 3 -> rule 101
- bit 4 -> rule 125
- bit 5 -> rule 77
- bit 6 -> rule 45
- bit 7 -> rule 237

Correction: the bit-4 neighbour is rule 125, not rule 93, because
`109 XOR 16 = 125`.

Preflight on `bg=1100`, IC length 1..8:

- Seven neighbours have 0 stationary and 0 moving oscillators.
- The only survivor is rule 108, produced by flipping bit 0.
- rule_108 yields 237 stationary witnesses, but they are compact T=2
  oscillators with max_span=9.

ANF measurement for the strongest witness:

`rule_108/bg=1100/T=2/word=00000001`

- T_WINDOW=2: active=5, distance classes=4, slope=-0.017102, R²=0.264706,
  comparable=false.
- T_WINDOW=12: same values, comparable=false.

Conclusion: Hamming-1 perturbation does not yield a comparable modified
`rule_109/bg=1100/T=8` mechanism. It either destroys oscillator support
entirely, or collapses to the compact `rule_108/T=2` attractor.

Preprint: https://doi.org/10.5281/zenodo.21385274
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.29 - Hamming-1 intervention audit in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.29 audits one-bit truth-table perturbations around a `rule_109` ANF-gradient
residual.

Target: `bg=1100`.

Result:

- 8 Hamming-1 neighbours tested.
- 7/8 have no oscillator support on `bg=1100`.
- The only survivor is rule 108, from bit flip 0.
- It collapses to compact T=2 oscillators, not the wide rule_109/T=8 mechanism.
- ANF slope=-0.017102, R²=0.264706, comparable=false.

So even atomic truth-table perturbations do not yield a comparable modified
ANF-gradient mechanism.

Preprint: https://doi.org/10.5281/zenodo.21385274
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: HN account karma was 2 last time checked. Do not post Show HN until the
account has enough karma to avoid auto-removal.
