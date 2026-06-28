# ZUSE v1.8 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.8 without improvising claims.

Canonical links:

- Preprint v1.8: https://doi.org/10.5281/zenodo.21000646
- GitHub Release v1.8: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.8
- v1.8 series: https://doi.org/10.5281/zenodo.21000645
- v1.7 series: https://doi.org/10.5281/zenodo.20971737
- v1.6 series: https://doi.org/10.5281/zenodo.20792050
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.8 to concept DOI `21000645`, independently
from the v1.7 concept DOI `20971737`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - compact state variable for a period-15 cellular automaton oscillator
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.8 update identifies a compact state variable for the T=15
oscillator family in ECA rules 73 and 109.

Earlier phases established the mechanism as a five-state localized XOR-defect
cycle under F^3, proved exact black/white conjugation, rejected sparse
truth-table support, rejected fixed local block derivations, and reduced the
variation to 13 finite shape families.

v1.8 asks what compact information controls those families.

Result:

- No compact background-only descriptor predicts all 13 families globally.
- Conditioned on the ECA rule, the circular multiset of length-4 background
  subwords (`subpatterns_len4`) separates the families.
- Rotation validation: fixed IC placement almost completely fails (3/140 T=15
  detections, 1/140 family match), while co-translating IC with the background
  gives 140/140 T=15 detections and 140/140 family matches.

The compact state variable for the confirmed representative set is:

(rule, subpatterns_len4, IC/background alignment)

Preprint v1.8:
https://doi.org/10.5281/zenodo.21000646

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.8 update:

The new version adds Fase 31-32, which isolate a compact state variable for the
T=15 oscillator family in ECA rule_73/rule_109.

Fase 31 searches for descriptors shorter than the full temporal background
orbit. No compact background-only descriptor among length-2..4 circular
subpattern counts, parity, run lengths, first-one position, or short orbit
prefixes predicts all 13 global shape families. But conditioned on the ECA
rule, the circular multiset of length-4 background subwords
(`subpatterns_len4`) separates all backgrounds per rule into unambiguous
shape-family buckets.

Fase 32 tests the rotation prediction. Fixed IC placement fails almost
completely: only 3/140 rotations produce T=15 and only 1/140 matches the
predicted family. With co-translated IC/background alignment, all 140/140
rotations produce T=15 and all 140/140 match the predicted family.

The compact state variable for the confirmed representative set is:

(rule, subpatterns_len4, IC/background alignment)

Preprint v1.8:
https://doi.org/10.5281/zenodo.21000646

GitHub Release v1.8:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.8
```

## Short FAQ

### What changed in v1.8?

v1.8 adds Fase 31 and Fase 32. These phases identify and validate a compact
state variable for the known T=15 shape-family representatives.

### What is the compact state variable?

```text
(rule, subpatterns_len4, IC/background alignment)
```

The rule selects the conjugate rule family, `subpatterns_len4` captures the
circular multiset of length-4 background subwords, and IC/background alignment
selects the correct phase.

### Does this predict unseen backgrounds?

Not yet. Fase 32 validates rotation-equivariance on the known 20 representative
backgrounds and their rotations. It is a structural validation, not an unseen
background benchmark.

### Why does fixed IC placement fail?

Because alignment is physical. Rotating the background while leaving the IC
fixed changes the local IC/background relation, and T=15 almost always
disappears.

### Does this solve the full symbolic derivation?

It gives the compact state variable for the confirmed representative set. A
future derivation still needs to map that triple explicitly to the five-state
defect cycle and phase offset.

### Is the discovery loop deterministic?

Yes. All empirical results come from deterministic scripts. Language-model
assistance was used only after execution for interpretation and documentation.
