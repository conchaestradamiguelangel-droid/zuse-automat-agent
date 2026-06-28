# ZUSE v1.9 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.9 without improvising claims.

Canonical links:

- Preprint v1.9: https://doi.org/10.5281/zenodo.21001633
- GitHub Release v1.9: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.9
- v1.9 series: https://doi.org/10.5281/zenodo.21001632
- v1.8 series: https://doi.org/10.5281/zenodo.21000645
- v1.7 series: https://doi.org/10.5281/zenodo.20971737
- v1.6 series: https://doi.org/10.5281/zenodo.20792050
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.9 to concept DOI `21001632`, independently
from the v1.8 concept DOI `21000645`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - external validation of a period-15 cellular automaton oscillator
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.9 update tests whether the T=15 oscillator mechanism found in
ECA rules 73 and 109 is confined to primitive length-8 backgrounds.

Earlier phases established the mechanism as a five-state localized XOR-defect
cycle under F^3, proved exact black/white conjugation, reduced the variation
to 13 finite shape families, and identified a compact length-8 state variable:

(rule, subpatterns_len4, IC/background alignment)

v1.9 adds two checks:

- Fase 33 audits the full binary circular length-8 universe. There are only
  two subpatterns_len4 descriptor collisions, and both are already inside the
  confirmed T=15 set and preserve the same defect-cycle family.
- Fase 34 leaves length 8. A targeted test over primitive length-9/10
  backgrounds with T_bg=3 performs 33,132 runs and finds 90 T=15 detections
  across 8 external backgrounds.

So the compact descriptor remains a length-8 family identifier, but the T=15
mechanism itself is not a length-8 artifact: it generalizes when T_bg=3 is
preserved.

Preprint v1.9:
https://doi.org/10.5281/zenodo.21001633

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.9 update:

The new version adds Fase 33-34, extending the T=15 oscillator analysis beyond
the primitive length-8 background universe.

Fase 33 audits the descriptor used in v1.8. Across all binary circular
length-8 backgrounds, only two subpatterns_len4 collisions exist:
00110111/00111011 and 00010011/00011001. Both are already in the confirmed
T=15 set, and both preserve the same defect-cycle family. There is no unseen
length-8 background, outside rotations of the known representatives, that
shares a T=15 subpatterns_len4 descriptor under the same rule.

Fase 34 then tests external backgrounds. A preflight finds primitive
length-9 and length-10 backgrounds with temporal background period T_bg=3
under rule_73 and rule_109. A targeted validation over 66 such backgrounds,
two rules, and 502 IC words performs 33,132 runs.

Result: 90 T=15 detections across 8 external backgrounds:

- 1 length-9 background under rule_73
- 5 length-10 backgrounds under rule_73
- 2 length-10 backgrounds under rule_109

This shows that the T=15 mechanism is not confined to primitive length-8
backgrounds. It generalizes when T_bg=3 is preserved. The compact descriptor
from v1.8 remains length-8 specific; extending it to variable background
length remains a separate symbolic problem.

Preprint v1.9:
https://doi.org/10.5281/zenodo.21001633

GitHub Release v1.9:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.9
```

## Short FAQ

### What changed in v1.9?

v1.9 adds Fase 33 and Fase 34. Fase 33 closes the length-8 descriptor universe;
Fase 34 shows that the T=15 mechanism generalizes to external primitive
length-9/10 backgrounds when `T_bg=3` is preserved.

### Does this replace the v1.8 descriptor?

No. The v1.8 descriptor remains a length-8 family identifier:

```text
(rule, subpatterns_len4, IC/background alignment)
```

v1.9 shows that the underlying T=15 mechanism is broader than length 8, while
the variable-length descriptor remains open.

### Is this an unseen-background validation?

Yes for the mechanism, not for the exact v1.8 descriptor. The 8 positive
backgrounds in Fase 34 are primitive length-9/10 backgrounds, not rotations of
the length-8 representatives.

### What is the strongest result?

The null hypothesis "T=15 is a primitive length-8 artifact" is falsified. A
targeted external test finds 90 T=15 detections across 8 new backgrounds.

### Is an LLM in the discovery loop?

No. The sweeps, detectors, and acceptance tests are deterministic scripts.
Language-model assistance is used only after execution for interpretation,
writing, and documentation.
