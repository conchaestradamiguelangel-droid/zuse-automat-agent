# ZUSE v1.15 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.15 without improvising claims.

Canonical links:

- Preprint v1.15: https://doi.org/10.5281/zenodo.21117311
- GitHub Release v1.15: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.15
- v1.15 series: https://doi.org/10.5281/zenodo.21117310
- v1.14 series: https://doi.org/10.5281/zenodo.21084310
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.15 to concept DOI `21117310`, independently
from the v1.14 concept DOI `21084310`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - ANF gradient laws in a period-15 cellular automaton cone
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.15 update switches representation class for the dense period-15
causal cone: after ROBDD audits found no useful input-support or variable-order
shortcut, ZUSE analyzes the same 25-input, 12-step cone using algebraic normal
form (ANF) over GF(2).

Fase 44:

- Builds exact bit-packed truth tables for the 25-input cone.
- Applies a Mobius transform to obtain ANF coefficients per active output.
- Analyzes 174 active outputs across the 20 minimal T=15 representatives.
- Active-output ANF degree ranges from 14 to 24.
- No output reaches the formal degree-25 ceiling.
- Monomial counts range from 9,376 to 17,758,052.

Fase 45 finds two spatial laws:

- degree = 24 - abs(rel_pos) + epsilon, with epsilon in {0,1}
- zero exceptions over 174 active outputs
- log10(monomials) ~= 7.241925 - 0.307283 * abs(rel_pos)
- R^2 = 0.998197

The slope is close to -log10(2), so monomial count decays almost by a factor of
two per cell away from the defect center.

This is the first positive algebraic structure after the ROBDD negative results:
the T=15 cone is still dense and input-complete, but ANF exposes a spatial
complexity gradient centered on the active defect.

Preprint v1.15:
https://doi.org/10.5281/zenodo.21117311

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.15 update:

The new version integrates Fase 44 and Fase 45, an algebraic normal form (ANF)
audit of the dense T=15 causal-cone mechanism.

Earlier ROBDD phases showed that the 25-cell, 12-step cone has no useful
input-support shortcut and is not compacted by simple variable ordering or
targeted SIFT. v1.15 asks whether the same cone has structure in ANF over GF(2).

Fase 44 computes exact bit-packed truth tables and applies Mobius transforms to
174 active outputs across the 20 minimal T=15 representatives. Active-output
degree ranges from 14 to 24; no output reaches degree 25. Monomial counts range
from 9,376 to 17,758,052.

Fase 45 shows that this variation is not arbitrary:

degree = 24 - abs(rel_pos) + epsilon, epsilon in {0,1}

with zero exceptions over 174 active outputs, and:

log10(monomials) ~= 7.241925 - 0.307283 * abs(rel_pos)

with R^2 = 0.998197. The slope is close to -log10(2), meaning monomial count
decays almost by a factor of two per cell away from the defect center.

Verdict: the cone remains dense, but ANF exposes a spatial algebraic-complexity
gradient invisible to the ROBDD audits.

Preprint v1.15:
https://doi.org/10.5281/zenodo.21117311

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.15 is out.

After ROBDD audits found no shortcut for the dense T=15 causal cone, ANF reveals
a clean spatial law: degree = 24 - abs(rel_pos) + epsilon, epsilon in {0,1},
with zero exceptions over 174 active outputs. Monomial counts decay almost as
2^-d from the defect center (R^2=0.998197).

https://doi.org/10.5281/zenodo.21117311
```

## FAQ

### Does v1.15 replace the ROBDD results?

No. It complements them. v1.13-v1.14 show that ROBDD input elimination and
variable ordering do not provide the missing shortcut. v1.15 changes
representation class and finds structure in ANF.

### What is the main result?

The dense T=15 cone is not algebraically uniform. ANF degree and monomial count
form a spatial complexity gradient centered on the active defect.

### Is this a closed symbolic formula for the oscillator?

No. It is a positive structural law for the cone outputs. The residual epsilon
and the algebraic left/right asymmetry remain open.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.
