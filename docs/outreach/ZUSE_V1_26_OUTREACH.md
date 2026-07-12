# ZUSE v1.26 Outreach Pack

## Short Post

ZUSE v1.26 is out.

Fases 59-60 close the static-descriptor audit of the `rule_109` ANF-gradient
residual.

Result: `ALIGNMENT_LOOKUP_ONLY`.

- Fase 59: IC placement perfectly separates the three `rule_109/T=8` cases.
- Positive T=8 cases use adjacent IC active bits with `ic_span=2`.
- The negative T=8 case uses separated IC active bits with `ic_span=6`.
- Fase 60 validates this against all 17 `rule_109` cases.
- The T=8 rule captures only 2/5 positives globally.
- `ic_span` overlaps between positive and non-positive cases.
- The only perfect global separator is exact `ic_active_bits`, a lookup-like IC pattern.

So the static causal chain is now bounded: center mediation is necessary but
not sufficient; period/horizon is informative but incomplete; IC alignment is
local, not a compact global rule.

Preprint: https://doi.org/10.5281/zenodo.21327839
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.26
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fases 59-60: ALIGNMENT_LOOKUP_ONLY.

v1.26 audits the residual left by the period/horizon analysis inside
`rule_109`.

The key Fase 58 residual was:

- `rule_109/bg=0011/T=8`: `NEGATIVE`
- `rule_109/bg=0110/T=8`: `HORIZON_ACCEPTABLE`
- `rule_109/bg=1100/T=8`: `HORIZON_ACCEPTABLE`

All three share center mediation and the same period/horizon threshold, so
Fase 59 tests static IC/background alignment descriptors.

Local T=8 result:

- Negative: active IC bits `(0,5)`, offsets `(0,1)`, `ic_span=6`.
- Positives: active IC bits `(5,6)`, offsets `(1,2)`, `ic_span=2`.
- Status: `ALIGNMENT_DISCRIMINANT_FOUND`.

Validation on all 17 `rule_109` cases:

- The local rule is perfect on T=8: TP=2, FP=0, TN=1, FN=0.
- Across all `rule_109` cases, it captures only 2/5 positives.
- `ic_span` values overlap between positive and non-positive cases.
- Exact `ic_active_bits` separates the catalog, but only as a lookup-like IC pattern.
- Status: `ALIGNMENT_LOOKUP_ONLY`.

Conclusion: static descriptors have reached their current limit. The next
causal layer likely requires dynamic alignment features or an intervention
experiment, not more catalog-level static descriptors.

Preprint: https://doi.org/10.5281/zenodo.21327839
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.26 - empirical law discovery in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.26 closes a static causal audit around a `rule_109` ANF-gradient pattern.

Previous phases found:

- center-mediated local ANF is necessary, but not sufficient;
- period/horizon is informative, but incomplete;
- one T=8 residual remains.

This release tests IC/background alignment.

Result:

- IC placement perfectly separates the three T=8 cases.
- But the rule does not generalize to all 17 `rule_109` cases.
- The only perfect global separator is exact `ic_active_bits`, which is a lookup-like catalog descriptor, not a compact causal rule.

So the static-descriptor audit reaches a clean boundary. The next step would be
dynamic alignment or algebraic intervention.

Preprint: https://doi.org/10.5281/zenodo.21327839
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: HN account karma was 2 last time checked. Do not post Show HN until the
account has enough karma to avoid auto-removal.
