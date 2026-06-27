# ZUSE v1.7 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.7 without improvising claims.

Canonical links:

- Preprint v1.7: https://doi.org/10.5281/zenodo.20971738
- GitHub Release v1.7: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.7
- v1.7 series: https://doi.org/10.5281/zenodo.20971737
- v1.6 series: https://doi.org/10.5281/zenodo.20792050
- v1.5 series: https://doi.org/10.5281/zenodo.20768584
- v1.4 series: https://doi.org/10.5281/zenodo.20767476
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.7 to concept DOI `20971737`, independently
from the v1.6 concept DOI `20792050`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - symbolic boundary of a period-15 cellular automaton oscillator
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.7 update closes the current symbolic-boundary analysis of a
period-15 oscillator family in ECA rules 73 and 109.

Earlier phases established that the T=15 oscillator is a five-state localized
XOR-defect cycle under F^3, and that rules 73 and 109 are related by exact
black/white conjugation at the induced defect level.

v1.7 asks whether the mechanism can be reduced further.

Result:

- No pure defect-only dynamic: canonical defect shapes are background-specific
  already at W=0.
- No fixed local block signature: no nontrivial ordered block is shared across
  all backgrounds in any phase.
- But the variation is structured: the 20 minimal representatives collapse into
  13 phase-rotated defect-cycle shape families.

So the remaining symbolic problem is now sharper: map the temporal background
orbit and IC alignment to one of a finite set of defect-cycle families and a
phase offset.

Preprint v1.7:
https://doi.org/10.5281/zenodo.20971738

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.7 update:

The new version adds the Fase 29-30 symbolic-boundary analysis of the T=15
oscillator family in ECA rule_73/rule_109.

Fase 29 tests whether the five-state XOR-defect cycle can be explained as a
pure defect-only dynamic or by a fixed local block signature. It cannot:
canonical defect shapes are background-specific already at W=0, and no
nontrivial shared local block signature exists across all backgrounds.

Fase 30 shows that the variation is nevertheless finite and structured. The 20
minimal T=15 representatives collapse into 13 phase-rotated defect-cycle shape
families: 7 for rule_73 and 8 for rule_109, with two families shared across the
conjugate rules.

This completes the current symbolic-delimitation arc: the five-state mechanism
is established computationally, exact conjugation is proved analytically, sparse
truth-table support is rejected, fixed local block derivation is rejected, and
the remaining problem is reduced to mapping temporal background orbit plus IC
alignment to a finite shape family and phase offset.

Preprint v1.7:
https://doi.org/10.5281/zenodo.20971738

GitHub Release v1.7:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.7
```

## Short FAQ

### What changed in v1.7?

v1.7 adds Fase 29 and Fase 30. These phases test whether the T=15 mechanism can
be reduced to defect-only dynamics or fixed local block signatures, then cluster
the remaining background-dependent variation into finite shape families.

### What is the main result?

The T=15 oscillator is not explained by one universal local defect cycle or one
fixed local block signature. However, its variation is not arbitrary: 20 minimal
representatives collapse into 13 phase-rotated defect-cycle families.

### What does W=0 mean?

It means that the active defect span itself already contains
background-dependent context. No extra padding outside the defect is needed
before different backgrounds become distinguishable.

### Does this solve the symbolic mechanism?

Not fully. It narrows the target. A future derivation must map the temporal
background orbit and IC alignment to a finite shape family and phase offset.

### Does v1.7 change the v1.6 conjugation result?

No. v1.7 builds on it. The exact induced conjugation relation between rule_73
and rule_109 remains valid.

### Is the discovery loop deterministic?

Yes. All empirical results come from deterministic scripts. Language-model
assistance was used only after execution for interpretation and documentation.
