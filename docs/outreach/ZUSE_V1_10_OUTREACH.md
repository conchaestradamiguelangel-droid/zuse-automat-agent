# ZUSE v1.10 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.10 without improvising claims.

Canonical links:

- Preprint v1.10: https://doi.org/10.5281/zenodo.21009303
- GitHub Release v1.10: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.10
- v1.10 series: https://doi.org/10.5281/zenodo.21009302
- v1.9 series: https://doi.org/10.5281/zenodo.21001632
- v1.8 series: https://doi.org/10.5281/zenodo.21000645
- v1.7 series: https://doi.org/10.5281/zenodo.20971737
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.10 to concept DOI `21009302`, independently
from the v1.9 concept DOI `21001632`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - transition-table analysis of a period-15 CA oscillator
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.10 update closes the current post-burn-in analysis of the T=15
oscillator mechanism found in ECA rules 73 and 109.

Earlier versions discovered the T=15 family, showed that it is a five-state
localized XOR-defect cycle under F^3, proved exact black/white conjugation,
reduced the variation to 13 finite shape families, and validated a compact
length-8 descriptor:

(rule, subpatterns_len4, IC/background alignment)

v1.10 adds Fases 35-39:

- Fases 35-38 replace visual shape families with explicit macro-transition
  tables and effective orbit embeddings.
- The induced F^3 transition table is a sufficient discriminator and refines
  the 13 visual families.
- Family F00 is explained by convergence to a shared effective period-3
  background orbit.
- The first sufficient post-burn-in descriptor is:

  (rule, sample_orbit_step, sample_rotation_offset, defect_state0)

- Fase 39 tests whether defect_state0 can be predicted compactly before
  burn-in. Under the tested descriptors, the result is negative: all 20
  representatives enter the stable five-cycle by t=12, and 15/20 enter at
  t=3, but exact pre-burn-in predictors mostly collapse to singleton case
  identifiers or post-hoc measurements.

So the post-burn-in mechanism is now descriptively closed, while the remaining
symbolic problem is sharply delimited: predict defect_state0 from the raw
background/IC pair without effectively replaying the early transient.

Preprint v1.10:
https://doi.org/10.5281/zenodo.21009303

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.10 update:

The new version integrates Fases 35-39 of the T=15 oscillator mechanism.

Fases 35-38 replace visual shape families with explicit transition tables of
the localized XOR defect under the macro-operator F^3. The transition table is
a sufficient discriminator and refines the 13 visual families. One table
identity, family F00 under rule_109, is explained by convergence to a shared
effective period-3 background orbit.

The first sufficient post-burn-in descriptor is:

(rule, sample_orbit_step, sample_rotation_offset, defect_state0)

Fase 39 then asks whether defect_state0 can be predicted compactly before the
81-step burn-in. The result is negative for the tested descriptors. The entry
is fast: all 20 representatives enter the stable five-cycle by t=12, and 15/20
enter at t=3. But exact pre-burn-in predictors mostly become singleton case
identifiers or post-hoc measurements.

This closes the post-burn-in description of the T=15 family and leaves a
precise symbolic problem: predicting defect_state0 from the raw background/IC
pair without replaying the early transient.

Preprint v1.10:
https://doi.org/10.5281/zenodo.21009303

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.10 is out.

It adds transition-table and pre-burn-in analysis for the T=15 oscillator in
ECA rules 73/109. The post-burn-in mechanism is now descriptively closed by
(rule, sample_orbit_step, sample_rotation_offset, defect_state0), while compact
pre-burn-in prediction remains negative under the tested descriptors.

https://doi.org/10.5281/zenodo.21009303
```

## FAQ

### Does v1.10 replace the v1.9 external validation?

No. v1.9 showed that the T=15 mechanism is not confined to primitive length-8
backgrounds. v1.10 analyzes the mechanism more deeply in the confirmed minimal
representative set.

### What is new scientifically?

The visual families are no longer the deepest object. The explicit induced
transition table under F^3 refines them. The first sufficient post-burn-in
state variable is `(rule, sample_orbit_step, sample_rotation_offset,
defect_state0)`.

### What remains open?

Predicting `defect_state0` directly from the raw background/IC pair without
effectively running the early transient.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.
