# ZUSE v1.25 Outreach Pack

## Short Post

ZUSE v1.25 is out.

Fase 58 tests whether period/horizon is the missing second condition after
center-mediated ANF in `rule_109`.

Result: `PERIOD_HORIZON_PARTIAL_DISCRIMINANT`.

- 17 `rule_109` catalog cases.
- 5 positive ANF-gradient witnesses.
- 12 non-positive cases.
- `T_local == 12` has no false positives but captures only 2/5 positives.
- `T_local >= 8` captures 5/5 positives but adds 4 false positives.
- `bg=0011/T=8` is negative while `bg=0110/T=8` and `bg=1100/T=8` are positive.

Period/horizon is informative, but incomplete. The next causal layer is likely
background phase, IC placement, or alignment.

Preprint: https://doi.org/10.5281/zenodo.21327600
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.25
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fase 58: PERIOD_HORIZON_PARTIAL_DISCRIMINANT.

v1.25 tests whether period/horizon is the missing second condition after the
Fase 57 result that center-mediated ANF is necessary but not sufficient.

The phase uses only the existing Fase 55 census and restricts analysis to the
17 `rule_109` catalog cases.

Results:

- `rule_109` cases: 17
- Positive witnesses: 5
- Non-positive cases: 12
- Common horizon: `T_WINDOW=12`
- `T_local == 12`: TP=2, FP=0, TN=12, FN=3
- `T_local >= 8`: TP=5, FP=4, TN=8, FN=0
- No period/horizon-only rule separates the 17 cases perfectly.

Key residual:

- `rule_109/bg=0011/T=8` is `NEGATIVE`
- `rule_109/bg=0110/T=8` and `rule_109/bg=1100/T=8` are `HORIZON_ACCEPTABLE`

Those backgrounds are in the same cyclic rotation orbit, so the residual is
not explained by coarse background orbit class. The next discriminant points
to background phase, IC placement, or alignment inside the oscillator
mechanism.

Preprint: https://doi.org/10.5281/zenodo.21327600
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.25 - empirical law discovery in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.25 continues the causal audit of a rule_109 ANF-gradient pattern.

The previous release showed center-mediated ANF is necessary but not
sufficient. This release tests whether period/horizon is the missing second
condition.

Result:

- `T_local == 12` has no false positives but catches only 2/5 positives.
- `T_local >= 8` catches 5/5 positives but adds 4 false positives.
- `bg=0011/T=8` is negative while two same-period, same-orbit backgrounds are positive.

So period/horizon is informative, but incomplete. The next layer is likely
background phase, IC placement, or alignment.

Preprint: https://doi.org/10.5281/zenodo.21327600
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: previous Show HN attempts were at low account karma. Check HN account
karma before posting.
