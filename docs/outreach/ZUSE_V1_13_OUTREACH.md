# ZUSE v1.13 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.13 without improvising claims.

Canonical links:

- Preprint v1.13: https://doi.org/10.5281/zenodo.21045809
- GitHub Release v1.13: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.13
- v1.13 series: https://doi.org/10.5281/zenodo.21045808
- v1.12 series: https://doi.org/10.5281/zenodo.21044801
- v1.11 series: https://doi.org/10.5281/zenodo.21034812
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.13 to concept DOI `21045808`, independently
from the v1.12 concept DOI `21044801`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - ROBDD audit of a dense period-15 CA cone
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.13 update audits the 25-input, 12-step causal cone behind a
period-15 oscillator mechanism using reduced ordered binary decision diagrams
(ROBDDs).

Context:

- Fase 39 found no compact closed-form pre-burn-in descriptor.
- Fase 40 found a constructive causal compression: a strict 25-cell cone over
  12 steps recovers defect_state0 in 20/20 representatives, a 69.1x reduction
  versus the full 256-by-81 simulation.
- Fase 41 showed that this cone has no sparse local-table shortcut: induced
  tables are dense, all 8 ECA entries are used, and all 25 cone inputs remain
  in the structural support.

v1.13 adds Fase 42:

- Active-output ROBDD reachable nodes: 17,141..36,966.
- Full 25-bit vector ROBDD reachable nodes: 51,539..53,901.
- Active-output support: 25/25 inputs in every representative.
- Full-vector support: 25/25 inputs in every representative.
- Verdict: BDD_NO_INPUT_REDUCTION.

So Boolean input elimination is ruled out as a symbolic shortcut. This does not
claim globally minimal BDD size over all possible variable orders; the remaining
symbolic task is expression or BDD-size reduction of a dense function that
genuinely depends on all 25 inputs.

Preprint v1.13:
https://doi.org/10.5281/zenodo.21045809

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.13 update:

The new version integrates Fase 42, an ROBDD audit of the dense T=15 causal-cone
mechanism.

Fase 40 showed that a strict 25-cell cone simulated for 12 steps recovers
defect_state0 in 20/20 minimal representatives, giving a 69.1x compression
relative to the full 256-by-81 simulation. Fase 41 then showed that the cone has
no sparse local-table shortcut and still needs all 25 inputs at the structural
support level.

Fase 42 verifies the same boundary at the Boolean-function level with ROBDDs:

- active-output ROBDD reachable nodes: 17,141..36,966;
- full 25-bit vector ROBDD reachable nodes: 51,539..53,901;
- active-output support: 25/25 inputs in every representative;
- full-vector support: 25/25 inputs in every representative.

Verdict: BDD_NO_INPUT_REDUCTION.

This rules out Boolean input elimination as the next symbolic shortcut. It does
not claim globally minimal BDD size over every possible variable ordering; the
remaining task is reducing or expressing a dense function that really depends
on all 25 cone inputs.

Preprint v1.13:
https://doi.org/10.5281/zenodo.21045809

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.13 is out.

Fase 42 audits the dense 25-input T=15 causal cone with ROBDDs:
25/25 inputs remain necessary, active-output BDDs have 17K..37K nodes, and the
full 25-bit vector has 51K..54K nodes.

Verdict: BDD_NO_INPUT_REDUCTION.

https://doi.org/10.5281/zenodo.21045809
```

## FAQ

### Does v1.13 replace v1.12?

No. v1.12 audited sparse tables and structural input support. v1.13 verifies
the same boundary at the Boolean-function level using ROBDDs.

### What is the main result?

All 25 causal-cone inputs remain necessary for the localized active output and
for the full 25-bit output vector. Boolean input elimination is not available as
a symbolic shortcut.

### Does this prove the smallest possible BDD?

No. The audit uses the natural left-to-right cone variable order. Variable
support is semantic, but BDD size can depend on ordering. The result rules out
irrelevant input variables; it does not claim a globally minimal BDD size over
all 25! variable orders.

### Is the symbolic mechanism solved?

Not fully. The mechanism is descriptively closed to a dense 25-input causal
cone. The remaining symbolic target is expression or size reduction of that
dense Boolean function.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.
