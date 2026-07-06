# ZUSE v1.19 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.19 without improvising claims.

Canonical links:

- Preprint v1.19: https://doi.org/10.5281/zenodo.21220980
- GitHub Release v1.19: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.19
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: the v1.19 concept DOI was not visible in the publication text
provided during release closure. Do not publish a v1.19 series DOI until it has
been explicitly verified.

## Show HN Draft

Title:

```text
Show HN: ZUSE - ANF gradient generalizes to external period-15 CA backgrounds
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

Fases 44-45 established an ANF degree-gradient law on the original length-8
T=15 periodic-background representatives:

degree = 24 - d + epsilon, with epsilon in {0,1}

and

log10(monomials) ~= 7.241925 - 0.307283 * d

v1.19 tests whether this law is specific to the original length-8 set.

Fase 49 runs the same exact bit-sliced Mobius ANF analysis on the 8 external
T=15 backgrounds discovered in Fase 34:

- 1 length-9 background under rule_73
- 5 length-10 backgrounds under rule_73
- 2 length-10 backgrounds under rule_109

Results:

- 8/8 external backgrounds replay-verified at T=15
- 63 active outputs analyzed
- 0/63 exceptions to degree = 24 - d + epsilon, epsilon in {0,1}
- external fit: log10(monomials) ~= 7.224069 - 0.302890 * d
- external R^2: 0.998263
- vs length-8 constants: intercept 0.25%, slope magnitude 1.43%

Verdict: ANF_GRADIENT_GENERALIZES.

The ANF gradient law is not specific to period-8 backgrounds. It appears to be
a property of the T=15 mechanism when the background preserves T_bg=3, at least
across the tested length-8 and length-9/10 witnesses.

Preprint v1.19:
https://doi.org/10.5281/zenodo.21220980

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.19 update:

The new version integrates Fase 49, external generalization of the ANF gradient
law for the T=15 causal cone.

The original law from Fases 44-45 was measured on length-8 periodic
backgrounds:

degree = 24 - d + epsilon, epsilon in {0,1}

Fase 49 tests the same ANF analysis on 8 external T=15 backgrounds from Fase 34
(length 9/10, rules 73 and 109).

Results:

- 8/8 external backgrounds replay-verified at T=15
- 63 active outputs
- 0/63 epsilon-band exceptions
- log10(monomials) ~= 7.224069 - 0.302890*d
- R^2 = 0.998263
- slope differs from the length-8 reference by 1.43%

Verdict: ANF_GRADIENT_GENERALIZES.

This shows that the ANF gradient is not a length-8 artifact.

Preprint v1.19:
https://doi.org/10.5281/zenodo.21220980

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.19 is out.

Fase 49 tests the ANF gradient law on 8 external T=15 backgrounds (len-9/10).

Result:
0/63 epsilon exceptions
R^2 = 0.998263
slope delta vs len-8 = 1.43%

Verdict: ANF_GRADIENT_GENERALIZES.

https://doi.org/10.5281/zenodo.21220980
```

## FAQ

### Does v1.19 replace v1.18?

No. v1.18 closed the horizon question for epsilon. v1.19 tests whether the ANF
gradient law generalizes outside the original length-8 background set.

### Is this a proof for all background lengths?

No. It is a controlled external validation on the 8 length-9/10 `T=15`
backgrounds discovered in Fase 34. It shows that the law is not specific to the
original length-8 representatives.

### What is the main result?

The ANF gradient generalizes cleanly to external length-9/10 `T=15`
backgrounds: 0/63 epsilon-band exceptions and a log-monomial slope within 1.43%
of the length-8 reference.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.

