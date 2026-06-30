# ZUSE v1.14 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.14 without improvising claims.

Canonical links:

- Preprint v1.14: https://doi.org/10.5281/zenodo.21084311
- GitHub Release v1.14: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.14
- v1.14 series: https://doi.org/10.5281/zenodo.21084310
- v1.13 series: https://doi.org/10.5281/zenodo.21045808
- v1.12 series: https://doi.org/10.5281/zenodo.21044801
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.14 to concept DOI `21084310`, independently
from the v1.13 concept DOI `21045808`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - targeted SIFT audit of a dense period-15 CA cone
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

The latest v1.14 update asks whether the dense 25-input causal cone behind a
period-15 oscillator can be compacted by ROBDD variable ordering.

Context:

- Fase 40 found a 25-cell, 12-step causal cone that recovers defect_state0 in
  20/20 representatives, a 69.1x reduction versus the full 256-by-81 simulation.
- Fase 41 showed that this cone has no sparse local-table shortcut.
- Fase 42 showed that ROBDD reduction keeps all 25 inputs semantically
  necessary.

v1.14 adds Fase 43:

- Fase 43A compares natural, reverse, and center_out ROBDD orders.
- Reverse is best globally, but improves active-output nodes by only 0.5%.
- Center_out is worst in 20/20 representatives.
- Fase 43B runs a checkpointed one-pass SIFT search on the most favorable
  representative.
- Across 580 evaluated orders, active-output ROBDD size improves only from
  16,061 to 16,056 nodes: 5 nodes, or 0.031%.
- The explicit 10,000-node compression gate is not reached.
- Support remains 25/25.

This does not prove global BDD-size optimality over all possible variable
orders. It does rule out simple variable reordering, including targeted SIFT on
the best known candidate, as the missing symbolic shortcut for the dense cone.

Preprint v1.14:
https://doi.org/10.5281/zenodo.21084311

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.14 update:

The new version integrates Fase 43, a ROBDD order-sensitivity and targeted SIFT
audit of the dense T=15 causal-cone mechanism.

Fase 42 showed that all 25 causal-cone inputs remain semantically necessary
under ROBDD reduction. Fase 43 tests the next direct escape route: whether
variable ordering makes the dense Boolean representation compact.

Fase 43A compares the ROBDD orders already materialized in Fase 42: natural,
reverse, and center_out. Reverse is best globally, but improves total
active-output nodes by only 0.5%. Center_out is worst in 20/20 representatives.

Fase 43B runs a checkpointed one-pass SIFT search on the most favorable
representative: rule_73, background 00111011, family F01. Across 580 evaluated
orders, active-output ROBDD size improves only from 16,061 to 16,056 nodes, a
5-node reduction (0.031%), far above the explicit 10,000-node compression gate.
Support remains 25/25.

Verdict: simple variable reordering is not the missing symbolic shortcut for
the dense cone.

Preprint v1.14:
https://doi.org/10.5281/zenodo.21084311

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short Social Post

```text
ZUSE Automat Agent v1.14 is out.

Fase 43 tests whether ROBDD variable ordering compacts the dense T=15 causal
cone. Reverse improves active nodes by only 0.5%; targeted SIFT over 580 orders
improves the best candidate from 16,061 to 16,056 nodes (0.031%).

https://doi.org/10.5281/zenodo.21084311
```

## FAQ

### Does v1.14 replace v1.13?

No. v1.13 ruled out Boolean input elimination. v1.14 tests the next direct
question: whether changing ROBDD variable order makes the dense function
compact.

### What is the main result?

Simple variable ordering does not provide a useful compression. Reverse order
only improves active-output nodes by 0.5% globally, and targeted SIFT on the
best known representative improves by only 5 nodes.

### Does this prove global BDD optimality?

No. It does not prove the minimum BDD over all possible variable orders. It
rules out the practical next step tested here: simple reordering and targeted
one-pass SIFT on the most favorable candidate.

### Was an LLM used in the discovery loop?

No. The discovery loop is deterministic. Language-model assistance was used
after execution for interpretation, writing, and planning, not for world
selection, law evaluation, scoring, or empirical acceptance.
