# ZUSE v1.30 Outreach Pack

## Short Post

ZUSE v1.30 is out.

Fases 65-66 audit the remaining `rule_109/bg=1100/T=8` ANF-gradient residual.

Result:

- Aggregate context frequencies do not discriminate the residual.
- All eight contexts `000..111` appear in the selected defects.
- The residual is closest by L1 context-frequency distance to a negative `bg=1100/T=10` control.
- Long-horizon persistence refutes the transient hypothesis.
- The residual persists to `t=500` with exact period 8 and negligible center drift.

So the causal discriminator is not the set or aggregate frequency of local
contexts. It must live in phase ordering, trajectory, or a finer dynamic
invariant.

Preprint: https://doi.org/10.5281/zenodo.21385475
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.30
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fases 65-66: CONTEXT_UNDISCRIMINATED + RESIDUAL_CONFIRMED_PERSISTENT.

v1.30 audits the remaining `rule_109` residual:

`bg=1100/T=8/word=00000110`

Fase 65 asks whether aggregate local context usage separates the residual from
other positive witnesses and nearby negative controls. It does not:

- Contexts in every positive and no negative control: none.
- Contexts used only by the residual: none.
- Contexts never used by any selected defect cell: none.
- All eight contexts `000..111` appear.

The residual is closest by L1 context-frequency distance to the negative
control:

`bg=1100/T=10/word=00111001`

with L1 distance `0.104`.

Fase 66 then tests whether the residual was merely a long transient. It is not.

Long-horizon persistence audit:

- Horizon: `t=0..500`
- Classification: `PERSISTENT_OSCILLATOR`
- Verdict: `RESIDUAL_CONFIRMED_PERSISTENT`
- Collapse step: none
- Exact period observed in the last 100 steps: `8`
- Center slope in the last 100 steps: `5.591147350029335e-05`
- Final defect size: `6`
- Tail defect-size range: `5..8`

Conclusion: the residual is a genuine period-8 oscillator, not a pre-collapse
artifact. The discriminator is not the set or aggregate frequency of local
contexts; it must lie in phase ordering, trajectory, or another time-resolved
invariant.

Preprint: https://doi.org/10.5281/zenodo.21385475
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.30 - context and persistence audit in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.30 audits the remaining `rule_109/bg=1100/T=8` ANF-gradient residual.

The result is a useful negative:

- Aggregate context frequencies do not discriminate the residual.
- All eight local contexts `000..111` appear.
- The residual is closest by L1 context-frequency distance to a negative
  `bg=1100/T=10` control.
- A long-horizon audit refutes the simple explanation that it is a transient.
- It persists to `t=500`, repeats with exact period 8 in the last 100 steps,
  and has negligible center drift.

So the residual is a genuine oscillator, but its discriminator is not in the
set or aggregate frequency of local contexts. It must be in phase ordering,
trajectory, or a finer time-resolved invariant.

Preprint: https://doi.org/10.5281/zenodo.21385475
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: HN account karma was 2 last time checked. Do not post Show HN until the
account has enough karma to avoid auto-removal.
