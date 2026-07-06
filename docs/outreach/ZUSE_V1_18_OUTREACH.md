# ZUSE v1.18 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.18 without improvising claims.

Canonical links:

- Preprint v1.18: https://doi.org/10.5281/zenodo.21215386
- GitHub Release v1.18: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.18
- v1.18 series: https://doi.org/10.5281/zenodo.21215385
- v1.17 series: https://doi.org/10.5281/zenodo.21205500
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.18 to concept DOI `21215385`, independently
from the v1.17 concept DOI `21205500`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - epsilon needs the full 12-step ANF cone horizon
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

v1.17 showed that the epsilon bit in the ANF degree law is dynamically
predictable from the full temporal degree-growth profile of a 25-cell,
12-step causal cone:

- degree_growth_slope over t=1..12
- leave-one-representative-out accuracy: 94.90%
- 0 mismatches against the final ANF audit

v1.18 asks whether this dynamic signal appears earlier.

Using the stored ANF histories from v1.17, the audit recomputes the
future-blind feature degree_growth_slope_K for partial horizons:

- K=6: 61.74% LORO accuracy
- K=8: 76.56%
- K=9: 75.27%
- K=10: 76.09%
- K=11: 79.47%
- K=12: 94.90%

Verdict: FULL_PROFILE_REQUIRED.

The jump from K=11 to K=12 shows that the epsilon residual is decided at the
full causal horizon. The v1.17 predictor is therefore not an early dynamic
shortcut; it is a full-horizon ANF growth-profile law.

Preprint v1.18:
https://doi.org/10.5281/zenodo.21215386

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.18 update:

The new version integrates Fase 48, an early dynamic ANF horizon audit for the
epsilon residual of the dense T=15 causal cone.

Fase 47 showed that degree_growth_slope over the full t=1..12 cone predicts
epsilon with 94.90% leave-one-representative-out accuracy.

Fase 48 tests whether this signal appears before the final cone layer:

- K=6: 61.74%
- K=8: 76.56%
- K=9: 75.27%
- K=10: 76.09%
- K=11: 79.47%
- K=12: 94.90%

The result is FULL_PROFILE_REQUIRED.

The epsilon bit is dynamically visible, but only at the full 12-step horizon.
This keeps the v1.17 interpretation honest: it is a full-profile law, not an
early shortcut.

Preprint v1.18:
https://doi.org/10.5281/zenodo.21215386

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.18 is out.

Fase 48 tests whether the ANF epsilon predictor appears early.

It does not:
K=11 gives 79.47% LORO accuracy, while K=12 jumps to 94.90%.

Verdict: FULL_PROFILE_REQUIRED.

https://doi.org/10.5281/zenodo.21215386
```

## FAQ

### Does v1.18 replace v1.17?

No. v1.17 found the dynamic full-profile predictor. v1.18 tests whether that
predictor can be truncated before the final cone layer. It cannot under the
tested protocol.

### Is this a closed-form symbolic formula?

No. This is a horizon audit over dynamic ANF degree profiles. It shows that the
predictive signal requires the full 12-step cone profile.

### What is the main result?

The epsilon bit is dynamically predictable, but not early:
`degree_growth_slope_K` reaches 79.47% LORO at K=11 and 94.90% at K=12.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.

