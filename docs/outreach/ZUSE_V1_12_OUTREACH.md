# ZUSE v1.12 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.12 without improvising claims.

Canonical links:

- Preprint v1.12: https://doi.org/10.5281/zenodo.21044802
- GitHub Release v1.12: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.12
- v1.12 series: https://doi.org/10.5281/zenodo.21044801
- v1.11 series: https://doi.org/10.5281/zenodo.21034812
- v1.10 series: https://doi.org/10.5281/zenodo.21009302
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.12 to concept DOI `21044801`, independently
from the v1.11 concept DOI `21034812`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - minimal cone audit of a period-15 CA oscillator
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.12 update audits whether the 25-cell causal cone found in v1.11
contains a smaller hidden shortcut.

Context:

- Fase 39 found no compact closed-form pre-burn-in descriptor.
- Fase 40 found a constructive causal compression: a strict 25-cell cone over
  12 steps recovers defect_state0 in 20/20 representatives, a 69.1x reduction
  versus the full 256-by-81 simulation.

v1.12 adds Fase 41:

- The induced (b,d)->d_next tables are dense: 49..62 of 64 keys are used.
- All 8 ordinary ECA truth-table entries are used in every representative.
- The final active defect support still depends on all 25 initial cone inputs.
- The only reduction is structural: active-output computation uses 234..310
  internal cone nodes instead of all 325 nodes.

So the cone is close to minimal at the input-support level. The next symbolic
problem is not finding a smaller causal support, but simplifying a dense
25-input, 12-step Boolean circuit.

Preprint v1.12:
https://doi.org/10.5281/zenodo.21044802

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.12 update:

The new version integrates Fase 41, a minimal cone-table audit of the T=15
causal-cone mechanism.

Fase 40 showed that a strict 25-cell cone simulated for 12 steps recovers
defect_state0 in 20/20 minimal representatives, giving a 69.1x compression
relative to the full 256-by-81 simulation.

Fase 41 asks whether this cone hides a smaller object: a sparse induced truth
table, fewer required input bits, or a pruned causal dependency graph.

The answer is negative at the table/input level:

- induced (b,d)->d_next tables use 49..62 of 64 possible keys;
- all 8 ordinary ECA truth-table entries are used in every representative;
- the active localized output still depends on all 25 initial cone inputs.

The only reduction is structural: active-output dependency uses 234..310
internal nodes instead of all 325 cone nodes.

Verdict: STRUCTURAL_CONE_REDUCTION_ONLY.

Preprint v1.12:
https://doi.org/10.5281/zenodo.21044802

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.12 is out.

Fase 41 audits the 25-cell causal cone behind the T=15 oscillator. The cone is
dense: 49..62/64 induced keys, 8/8 ECA entries, 25/25 inputs. Only structural
internal pruning remains (234..310/325 nodes).

https://doi.org/10.5281/zenodo.21044802
```

## FAQ

### Does v1.12 replace v1.11?

No. v1.11 showed that a 25-cell, 12-step causal cone recovers the missing
state with 69.1x compression. v1.12 audits whether that cone can be reduced
further by sparse tables or input elimination.

### What is the main result?

The cone is close to minimal at the input-support level. All 25 initial inputs
and all 8 ordinary ECA entries remain active. The induced tables are dense.

### Is the symbolic mechanism solved?

Not yet. The next target is Boolean simplification of the dense 25-input,
12-step local circuit.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.
