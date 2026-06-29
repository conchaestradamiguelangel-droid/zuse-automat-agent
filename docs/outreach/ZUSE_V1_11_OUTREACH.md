# ZUSE v1.11 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.11 without improvising claims.

Canonical links:

- Preprint v1.11: https://doi.org/10.5281/zenodo.21034813
- GitHub Release v1.11: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.11
- v1.11 series: https://doi.org/10.5281/zenodo.21034812
- v1.10 series: https://doi.org/10.5281/zenodo.21009302
- v1.9 series: https://doi.org/10.5281/zenodo.21001632
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.11 to concept DOI `21034812`, independently
from the v1.10 concept DOI `21009302`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - 69x causal compression of a period-15 CA oscillator
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.11 update studies the T=15 oscillator mechanism found in ECA
rules 73 and 109.

Earlier phases discovered the T=15 family, showed that it is a five-state
localized XOR-defect cycle under F^3, proved exact black/white conjugation,
reduced the variation to 13 finite shape families, validated a compact
length-8 descriptor, and showed that the post-burn-in state variable
`defect_state0` determines the family.

v1.11 adds Fase 40:

- Fase 39 found no compact closed-form pre-burn-in descriptor for predicting
  `defect_state0`.
- Fase 40 replaces the full 256-cell, 81-step simulation with a local causal
  cone.
- The strict center cone at t=12 has only 25 cells and 12 steps.
- It matches the full-system defect state at t=12 in 20/20 cases.
- After phase projection, it recovers post-burn-in `defect_state0` at t=81 in
  20/20 cases.
- This is a 69.1x compression relative to the full 256-by-81 simulation.

So the T=15 mechanism does not require global information. The remaining
symbolic problem is sharper: replace the 25-cell, 12-step causal-cone
computation with a compact rule.

Preprint v1.11:
https://doi.org/10.5281/zenodo.21034813

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.11 update:

The new version integrates Fase 40, an early causal-cone compression test for
the T=15 oscillator mechanism in ECA rules 73 and 109.

Fase 39 previously found no compact closed-form pre-burn-in descriptor for
predicting defect_state0. Fase 40 asks a weaker but constructive question:
can the relevant state be recovered by simulating only the local causal cone
of the initial perturbation?

The answer is yes. The strict center cone at t=12 contains 25 cells and is
simulated for 12 steps. It matches the full 256-cell system at t=12 in 20/20
minimal representatives, and after phase projection recovers the post-burn-in
defect_state0 at t=81 in 20/20 representatives.

This gives a 69.1x compression relative to the full 256-by-81 simulation.

The result completes the current mechanism chain: the T=15 oscillator does not
require global information. What remains open is symbolic: replacing that
25-cell, 12-step causal-cone computation with a compact rule.

Preprint v1.11:
https://doi.org/10.5281/zenodo.21034813

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.11 is out.

Fase 40 shows that the T=15 oscillator mechanism in ECA rules 73/109 does not
need global information: a strict 25-cell causal cone simulated for 12 steps
recovers the post-burn-in defect state in 20/20 cases, a 69.1x compression.

https://doi.org/10.5281/zenodo.21034813
```

## FAQ

### Does v1.11 replace v1.10?

No. v1.10 closed the post-burn-in mechanism description. v1.11 adds the next
step: a local causal-cone computation that recovers the missing pre-burn-in
state.

### What is the main result?

The T=15 mechanism is locally causal. A 25-cell, 12-step cone is enough to
recover `defect_state0` in 20/20 minimal representatives after phase projection.

### Is this a closed-form symbolic proof?

No. It is a constructive computational compression. The remaining symbolic
problem is to replace the 25-cell, 12-step cone computation with a compact rule.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.
