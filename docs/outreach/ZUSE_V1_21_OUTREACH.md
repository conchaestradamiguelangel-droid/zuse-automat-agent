# ZUSE v1.21 Outreach Pack

## Short Post

ZUSE v1.21 is out.

Fase 54 tests whether the non-T15 ANF-gradient witness from v1.20 generalizes
inside the tested `rule_73`/`rule_109` family at natural periods.

Result: `ANF_GRADIENT_ISOLATED_WITNESS`.

- `rule_109/bg=1011/T6` is flat at its natural period.
- `rule_73/bg=0010/T6` is flat at its natural period.
- `rule_109/bg=1101/T10` has a partial slope, but not T15-quality.
- Two T=6 cases show T15-like slopes only at the oversampled 12-step horizon.

The strong non-T15 witness remains isolated: `rule_109/bg=1011/T10`.

Preprint: https://doi.org/10.5281/zenodo.21306102
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.21
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fase 54: ANF_GRADIENT_ISOLATED_WITNESS.

v1.21 adds a family robustness test for the ANF gradient inside the tested
`rule_73`/`rule_109` periodic-background family.

v1.20 identified a strong non-T15 witness: `rule_109` on background `1011`
with `T_local=10`, reproducing the T15 monomial-decay slope within 0.13%.

Fase 54 tests three additional family witnesses at their natural periods:

- `rule_109/bg=1011/T6`: slope `0.000026`, R^2 `0.604938`
- `rule_109/bg=1101/T10`: slope `-0.209698`, R^2 `0.880488`, 31.76% from the T15 slope
- `rule_73/bg=0010/T6`: slope `-0.000027`, R^2 `0.604938`

None reproduces the T15-quality gradient at its natural period.

At the common 12-step horizon, two T=6 cases do show T15-like slopes:

- `rule_109/bg=1011/T6`: slope `-0.303174`, R^2 `0.999487`
- `rule_73/bg=0010/T6`: slope `-0.320463`, R^2 `0.999687`

Because those gradients appear only after oversampling to 12 steps, they are
classified as horizon effects rather than natural-period witnesses.

The paper claim is now sharper: the ANF gradient is mechanism-dependent, but
it does not broadly generalize to every tested `rule_73`/`rule_109` family
member at natural period. The strong non-T15 natural-period witness remains
the isolated `rule_109/bg=1011/T10` case.

Preprint: https://doi.org/10.5281/zenodo.21306102
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.21 - empirical law discovery in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.21 adds a negative robustness test for an ANF gradient discovered in a
T=15 oscillator and one non-T15 witness.

The key result is an isolated witness:

- Additional `rule_73/rule_109` T=6 cases are flat at natural period.
- A second `rule_109/T10` case has only a partial slope.
- T15-like slopes reappear for T=6 only when oversampled to 12 steps.

Preprint: https://doi.org/10.5281/zenodo.21306102
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: previous Show HN attempts were at low account karma. Check HN account
karma before posting.
