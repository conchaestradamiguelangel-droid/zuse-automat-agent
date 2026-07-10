# ZUSE v1.20 Outreach Pack

## Short Post

ZUSE v1.20 is out.

Fases 50-53 test whether the ANF gradient found in the T=15 oscillator is
period-specific, support-width-specific, or mechanism-dependent.

Result: mechanism-dependent.

- Compact T=2 baselines do not have enough active support.
- A non-T15 `rule_109/T=10` witness reproduces the T=15 slope within 0.13%.
- External `rule_54`, `rule_94`, and `rule_133` families are flat at their own periods.

Preprint: https://doi.org/10.5281/zenodo.21301212
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.20
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fases 50-53: ANF_GRADIENT_FAMILY_73_109.

v1.20 tests whether the ANF gradient discovered for the T=15 causal cone is a
generic consequence of period, cone size, or active-support width.

The answer is no: the gradient is mechanism-dependent in the tested cases.

Key results:

- Compact T=2 baselines (`rule_108` and four right-moving T=2 gliders) lack
  enough active-output support for a comparable spatial gradient.
- A wide non-T15 periodic-background witness, `rule_109` on background `1011`
  with `T_local=10`, reproduces the T=15 slope almost exactly at the common
  12-step horizon:
  - T=15 reference slope: `-0.307283`
  - `rule_109/T=10` slope: `-0.307674`
  - delta: `0.13%`
  - R^2: `0.999349`
- External wide candidates outside the `rule_73/rule_109` family
  (`rule_54`, `rule_94`, `rule_133`) are flat at their natural periods and do
  not reproduce the T15-quality gradient.

The paper now states the claim carefully: the ANF gradient appears robustly
within the tested `rule_73/rule_109` periodic-background family, including a
non-T15 `rule_109/T=10` witness, but no universality claim is made for untested
ECA families.

Preprint: https://doi.org/10.5281/zenodo.21301212
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.20 - empirical law discovery in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.20 tests whether an ANF gradient found in a T=15 oscillator is specific to
that period or reflects a broader mechanism.

The key result is mechanism-dependence:

- Compact T=2 oscillators do not have enough active support for the gradient.
- A non-T15 `rule_109/T=10` witness reproduces the T=15 slope within 0.13%.
- External `rule_54`, `rule_94`, and `rule_133` candidates are flat at their
  own periods.

Preprint: https://doi.org/10.5281/zenodo.21301212
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: previous Show HN attempts were at low account karma. Check HN account
karma before posting.
