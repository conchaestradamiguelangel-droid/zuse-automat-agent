# ZUSE v1.17 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.17 without improvising claims.

Canonical links:

- Preprint v1.17: https://doi.org/10.5281/zenodo.21205501
- GitHub Release v1.17: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.17
- v1.17 series: https://doi.org/10.5281/zenodo.21205500
- v1.16 series: https://doi.org/10.5281/zenodo.21144177
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.17 to concept DOI `21205500`, independently
from the v1.16 concept DOI `21144177`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - dynamic ANF growth law in a period-15 CA cone
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

v1.16 showed that the epsilon bit in the ANF degree law is not predicted by
static descriptors such as rule, signed position, local background, family, or
cycle phase.

v1.17 changes the feature class from static descriptors to dynamic ANF
growth profiles. The analysis recomputes ANF degree and monomial count at every
cone layer t=1..12 for the same 20 minimal T=15 representatives and the same
141 nontrivial residual rows with dist >= 2.

Internal verification:

- representatives: 20
- records analyzed: 141
- t=12 mismatches against Fase 44: 0

Results:

- Status: EPSILON_DYNAMIC_RULE_FOUND
- best single feature: degree_growth_slope
- degree_growth_slope train accuracy: 98.58%
- degree_growth_slope leave-one-representative-out accuracy: 94.90%
- monomial_growth_slope LORO accuracy: 73.37%
- t_first_full_degree LORO accuracy: 71.96%
- depth-3 decision tree: 86.52% train, 85.01% LORO

Interpretation:

The epsilon bit is not visible in static output descriptors, but it is strongly
encoded in how ANF degree accumulates across the 12-step causal cone. Outputs
with epsilon=1 are associated with algebraic degree still growing near the
causal horizon.

This is not a static pre-computation shortcut. The strongest feature uses the
complete temporal degree trajectory through the final cone layer. The result is
a dynamic full-profile law of ANF growth.

Preprint v1.17:
https://doi.org/10.5281/zenodo.21205501

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.17 update:

The new version integrates Fase 47, dynamic ANF growth-profile features for the
epsilon residual of the dense T=15 causal cone.

Fase 46 showed that epsilon is not predicted by static descriptors. Fase 47
recomputes ANF degree and monomial count at each cone layer t=1..12.

The strongest single feature is degree_growth_slope:

- train accuracy: 98.58%
- leave-one-representative-out accuracy: 94.90%
- 0 mismatches against Fase 44 at t=12

The result is EPSILON_DYNAMIC_RULE_FOUND.

Important caution: this is not a static pre-computation shortcut. The feature
uses the complete temporal degree trajectory through the final cone layer. It is
best understood as a dynamic full-profile law of ANF growth.

Preprint v1.17:
https://doi.org/10.5281/zenodo.21205501

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.17 is out.

Fase 47 resolves the ANF epsilon residual dynamically: degree_growth_slope over
t=1..12 predicts epsilon with 94.90% leave-one-representative-out accuracy and
0 mismatches against the final ANF audit.

Not a static shortcut; a full-profile dynamic law.

https://doi.org/10.5281/zenodo.21205501
```

## FAQ

### Does v1.17 replace v1.16?

No. v1.16 showed that static descriptors do not predict epsilon. v1.17 changes
feature class and shows that epsilon is strongly encoded in the dynamic ANF
degree-growth trajectory.

### Is this a closed-form symbolic formula?

No. The strongest feature uses the complete temporal degree trajectory through
the final cone layer. It is a dynamic profile law, not a static pre-run formula.

### What is the main result?

The epsilon bit in the ANF degree law is dynamically predictable:
`degree_growth_slope` reaches 94.90% leave-one-representative-out accuracy.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.
