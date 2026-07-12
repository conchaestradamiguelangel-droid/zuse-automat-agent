# ZUSE v1.24 Outreach Pack

## Short Post

ZUSE v1.24 is out.

Fase 57 tests whether the `rule_109` center-mediated ANF structure is causal
for the ANF-gradient witnesses found in the catalog census.

Result: `CAUSAL_CANDIDATE_NECESSARY_NOT_SUFFICIENT`.

- 256 ECA rules classified by local ANF.
- `center_mediated=True`: 64 rules.
- `strict_center_mediated=True`: 56 rules.
- In the Fase 55 catalog, only `rule_109` is center-mediated.
- Positive ANF-gradient witnesses: 5.
- Positives with `center_mediated=False`: 0/5.
- Non-positive cases with `center_mediated=True`: 12.

Interpretation: center mediation is necessary inside the catalog, but not
sufficient. The next discriminant is period/horizon.

Preprint: https://doi.org/10.5281/zenodo.21327353
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.24
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fase 57: CAUSAL_CANDIDATE_NECESSARY_NOT_SUFFICIENT.

v1.24 adds a catalog-level causality audit for the `rule_109` center-mediated
ANF candidate identified in v1.23.

The phase runs no new ECA or cone simulations. It computes the local
3-variable ANF of all 256 ECA rules and joins that rule-level classification
to the existing Fase 55 ANF-gradient census.

Definitions:

- `C_alone`: isolated `C` monomial appears.
- `LR_no_center`: `LR` monomial appears without the center.
- `center_mediated`: `C_alone=False` and `LR_no_center=False`.
- `strict_center_mediated`: `center_mediated=True` plus at least one center
  interaction monomial.

Results:

- 256 ECA rules analyzed.
- `center_mediated=True`: 64 rules.
- `strict_center_mediated=True`: 56 rules.
- Catalog rules: 54, 73, 94, 109, 133, 147.
- Only `rule_109` is center-mediated inside the catalog.
- Positive ANF-gradient witnesses: 5.
- Positive witnesses with `center_mediated=False`: 0/5.
- Non-positive cases with `center_mediated=True`: 12.

The candidate survives as a necessary structural condition inside the Fase 55
catalog, but not as a complete causal explanation. The next causal layer is
period/horizon structure.

Preprint: https://doi.org/10.5281/zenodo.21327353
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.24 - empirical law discovery in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.24 tests a causal candidate for an ANF-gradient law. The previous phase
identified a center-mediated local ANF structure in `rule_109`; this release
checks whether that structure is necessary or sufficient in the catalog.

Result:

- 256 ECA rules classified by local ANF.
- 5/5 positive ANF-gradient witnesses are center-mediated.
- 0/5 positives have `center_mediated=False`.
- But 12 center-mediated catalog cases are not positive.

So the candidate is necessary in the catalog, but not sufficient. The next
discriminant is period/horizon.

Preprint: https://doi.org/10.5281/zenodo.21327353
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: previous Show HN attempts were at low account karma. Check HN account
karma before posting.
