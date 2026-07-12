# ZUSE v1.23 Outreach Pack

## Short Post

ZUSE v1.23 is out.

Fase 56 audits why non-T15 ANF-gradient witnesses concentrate in `rule_109`.

Result: `RULE109_SYMMETRY_MECHANISM_CANDIDATE`.

- Orbit symmetry: `PARTIAL`.
- Rule-level ANF: `RULE109_CENTER_MEDIATED_CONFIRMED`.
- Cross-rule comparison: `RULE109_SPECIFIC_ON_SHARED_BACKGROUNDS`.
- `rule_73 = 1 XOR L XOR C XOR R XOR LR XOR LCR`.
- `rule_109 = 1 XOR L XOR LC XOR R XOR CR XOR LCR`.

The candidate mechanism is structural: in `rule_109`, the center cell appears
only mediated by neighbors (`LC`, `CR`, `LCR`), unlike `rule_73`.

Preprint: https://doi.org/10.5281/zenodo.21326792
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.23
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fase 56: RULE109_SYMMETRY_MECHANISM_CANDIDATE.

v1.23 adds a structural audit of why robust non-T15 ANF-gradient witnesses
from the catalog census concentrate in `rule_109`.

The audit uses existing Fase 55 data and local rule algebra only. It does not
run new ANF simulations.

Results:

- `orbit_symmetry_status`: `PARTIAL`
- `rule_anf_status`: `RULE109_CENTER_MEDIATED_CONFIRMED`
- `cross_rule_status`: `RULE109_SPECIFIC_ON_SHARED_BACKGROUNDS`
- `overall_status`: `RULE109_SYMMETRY_MECHANISM_CANDIDATE`

Exact local rule ANF:

```text
rule_73  = 1 XOR L XOR C XOR R XOR LR XOR LCR
rule_109 = 1 XOR L XOR LC XOR R XOR CR XOR LCR
```

The key structural difference is center mediation. In `rule_109`, the center
appears only through interactions with neighbors (`LC`, `CR`, `LCR`). There is
no isolated `C` term and no `LR` term without the center. In `rule_73`, the
center contributes directly and the neighbors can interact without it.

The orbit evidence is partial: several positive witnesses belong to the
cyclic orbit of `0011`, but the `rule_109/bg=1011/T=10` witness belongs to a
different orbit. Available cross-rule comparisons show that `rule_73` does not
reproduce the gradient on shared backgrounds and periods.

This is not a closed causal proof. It is a precise structural candidate for
why the ANF-gradient evidence concentrates in `rule_109`.

Preprint: https://doi.org/10.5281/zenodo.21326792
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.23 - empirical law discovery in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.23 adds a structural audit of a non-T15 ANF-gradient pattern discovered in
the catalog census. The robust witnesses concentrate in `rule_109`, and the
new audit identifies a candidate mechanism in the local rule algebra:

```text
rule_73  = 1 XOR L XOR C XOR R XOR LR XOR LCR
rule_109 = 1 XOR L XOR LC XOR R XOR CR XOR LCR
```

In `rule_109`, the center cell appears only mediated by neighbors (`LC`, `CR`,
`LCR`), while `rule_73` has an isolated center term and an `LR` term without
the center.

Preprint: https://doi.org/10.5281/zenodo.21326792
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: previous Show HN attempts were at low account karma. Check HN account
karma before posting.
