# ZUSE v1.27 Outreach Pack

## Short Post

ZUSE v1.27 is out.

Fases 61-62 test dynamic alignment inside the `rule_109` ANF-gradient audit.

Result: `DYNAMIC_UNION_PARTIAL`.

- 17 `rule_109` cases analyzed.
- 5 positive ANF-gradient witnesses.
- 12 non-positive cases.
- No single dynamic descriptor separates all positives.
- A minimal predeclared union captures 4/5 positives with zero false positives:
  `size_growth_total <= -3 OR center_drift_abs <= 0.0`.
- Metrics: TP=4, FP=0, TN=12, FN=1.
- Precision=1.000, recall=0.800.
- Remaining residual: `bg=1100/T=8/word=00000110`.

The dynamic signal is real and high-precision, but not complete. The residual
now becomes the cleanest target for a future algebraic intervention.

Preprint: https://doi.org/10.5281/zenodo.21328117
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.27
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fases 61-62: DYNAMIC_UNION_PARTIAL.

v1.27 moves beyond static catalog descriptors and audits whether the remaining
`rule_109` ANF-gradient residual is explained by dynamic defect evolution.

Fase 61 evolves each IC-over-background state alongside the pure periodic
background under `rule_109` and measures:

`defect(t) = state_with_IC(t) XOR background_only(t)`

over `t=1..12`.

No single dynamic descriptor separates all five positive witnesses from the
twelve non-positive cases. However, three descriptor thresholds produce no
false positives:

- `max_defect_size >= 12`: TP=1, FP=0.
- `center_drift_abs <= 0.0`: TP=2, FP=0.
- `size_growth_total <= -3`: TP=2, FP=0.

Fase 62 validates one predeclared minimal union:

`size_growth_total <= -3 OR center_drift_abs <= 0.0`

Results:

- TP=4
- FP=0
- TN=12
- FN=1
- accuracy=0.941
- precision=1.000
- recall=0.800

Captured positives:

- `bg=0011/T=12/word=10010100`
- `bg=0110/T=8/word=0000011`
- `bg=1011/T=10/word=00000001`
- `bg=1100/T=12/word=00101001`

Remaining residual:

- `bg=1100/T=8/word=00000110`

The dynamic signal is real and high-precision, but it does not close the causal
explanation. The remaining residual survives static descriptors and the
minimal dynamic union, making it the best target for a future algebraic
intervention experiment.

Preprint: https://doi.org/10.5281/zenodo.21328117
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.27 - dynamic alignment in elementary cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.27 tests dynamic alignment in a `rule_109` ANF-gradient audit.

Previous phases showed that static descriptors reached a boundary:

- center-mediated local ANF is necessary, but not sufficient;
- period/horizon is informative, but incomplete;
- IC alignment is local, not a compact global rule.

This release evolves each IC-over-background state alongside the pure periodic
background and measures the XOR defect over `t=1..12`.

Result:

- No single dynamic descriptor separates all positives.
- A minimal predeclared union captures 4/5 positives with zero false positives.
- Precision=1.000, recall=0.800.
- The remaining residual is `bg=1100/T=8/word=00000110`.

So the dynamic signal is real, but still not a complete causal explanation.
The next step is algebraic intervention on the residual case.

Preprint: https://doi.org/10.5281/zenodo.21328117
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: HN account karma was 2 last time checked. Do not post Show HN until the
account has enough karma to avoid auto-removal.
