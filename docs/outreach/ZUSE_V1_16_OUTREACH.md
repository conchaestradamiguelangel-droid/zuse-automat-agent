# ZUSE v1.16 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.16 without improvising claims.

Canonical links:

- Preprint v1.16: https://doi.org/10.5281/zenodo.21144178
- GitHub Release v1.16: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.16
- v1.16 series: https://doi.org/10.5281/zenodo.21144177
- v1.15 series: https://doi.org/10.5281/zenodo.21117310
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.16 to concept DOI `21144177`, independently
from the v1.15 concept DOI `21117310`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - residual audit of ANF gradient in a period-15 CA cone
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

v1.15 found a positive algebraic structure in the dense period-15 causal cone:
ANF degree follows

degree = 24 - abs(rel_pos) + epsilon, epsilon in {0,1}

with zero exceptions over 174 active outputs, while monomial counts decay almost
by a factor of two per cell away from the defect center.

v1.16 audits the remaining one-bit residual epsilon.

The test excludes dist=0 and dist=1, where epsilon=0 in all known cases, leaving
141 active outputs across the 20 minimal T=15 representatives.

Results:

- epsilon counts: {0: 83, 1: 58}
- majority baseline: 58.87%
- best single-feature predictor: dist, 64.89% leave-one-representative-out accuracy
- defect_phase: 64.53%
- local_bg_3mer: 64.18%
- background_bit, rule identity, and left/right sign collapse to the majority baseline
- depth-3 decision tree: 73.05% train accuracy, but only 55.65% leave-one-representative-out

Verdict: EPSILON_REMAINS_RESIDUAL.

This does not weaken the ANF gradient law. It separates the strong spatial
backbone from a one-bit residual that is not captured by static rule, position,
local-background, family, or cycle-phase descriptors.

Preprint v1.16:
https://doi.org/10.5281/zenodo.21144178

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.16 update:

The new version integrates Fase 46, an epsilon-residual audit for the ANF degree
gradient of the dense T=15 causal cone.

Fases 44-45 established the law:

degree = 24 - abs(rel_pos) + epsilon, epsilon in {0,1}

with zero exceptions over 174 active outputs. Fase 46 asks whether the remaining
epsilon bit has a compact predictor.

After excluding dist=0 and dist=1, where epsilon=0 in all known cases, the audit
uses 141 active outputs across the 20 minimal T=15 representatives.

Best results:

- dist: 64.89% leave-one-representative-out accuracy
- defect_phase: 64.53%
- local_bg_3mer: 64.18%
- background_bit, rule identity, and left/right sign collapse to baseline
- depth-3 decision tree: 73.05% training accuracy, 55.65% leave-one-representative-out

Verdict: EPSILON_REMAINS_RESIDUAL. The ANF gradient backbone is strong, but the
one-bit residual is not explained by the static features tested here.

Preprint v1.16:
https://doi.org/10.5281/zenodo.21144178

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.16 is out.

Fase 46 audits the one-bit residual in the ANF gradient law for the T=15 causal
cone. Best single-feature LORO accuracy is 64.89%; a depth-3 tree trains at
73.05% but drops to 55.65% LORO.

Verdict: EPSILON_REMAINS_RESIDUAL.

https://doi.org/10.5281/zenodo.21144178
```

## FAQ

### Does v1.16 weaken the v1.15 ANF gradient?

No. The gradient law remains intact. v1.16 tests the residual epsilon bit after
the main `24 - abs(rel_pos)` backbone is accounted for.

### What is the main result?

The epsilon residual is not predicted by the static feature class tested here:
rule, position, local background, family, or cycle phase.

### Is this a final impossibility proof?

No. It is a bounded negative result for the current static features and
leave-one-representative-out validation. A future explanation may require
dynamic ANF-computation features.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.
