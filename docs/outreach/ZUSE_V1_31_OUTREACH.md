# ZUSE v1.31 Outreach Pack

## Short Post

ZUSE v1.31 is out.

Fases 67-68 close the scalar temporal audit of the persistent
`rule_109/bg=1100/T=8` ANF-gradient residual.

Result: `PHASE_PARTIAL_NOT_SEPARATING`.

- The residual and nearest negative control are both genuine periodic circuits.
- Residual phases 0, 3, and 7 have no close equivalent in the negative cycle.
- Phase context `100` replicates in 4/5 positives, but also appears in 2/3 negatives.
- A compressed causal-complexity proxy over all 17 `rule_109` cases finds no new separator.
- The only no-false-positive rule is `period_detected >= 12`, which recapitulates the older period/horizon result.

Conclusion: the residual is not explained by any tested scalar temporal
descriptor. The remaining information appears to live in richer spatial or
spatiotemporal cone structure.

Preprint: https://doi.org/10.5281/zenodo.21433927
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.31
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fases 67-68: PHASE_PARTIAL_NOT_SEPARATING.

v1.31 integrates the phase-organization and compressed causal-complexity audit
of the remaining `rule_109` residual:

`bg=1100/T=8/word=00000110`

Fase 67 compares the residual with its nearest negative control:

`bg=1100/T=10/word=00111001`

Both are genuine periodic circuits:

- residual period: `8`
- negative-control period: `10`

Phase-level result:

- residual phases 1 and 4 have context L1 distance `0.000` to their best negative matches;
- residual phase 0 has L1 `0.571`;
- residual phase 3 has L1 `0.524`, active Jaccard `0.182`, and uniquely dominant context `100`;
- residual phase 7 has L1 `0.400`.

Fase 67b cross-validates the phase-dominant contexts:

- `011`: dominant in 3/5 positives and 2/3 negatives.
- `100`: dominant in 4/5 positives and 2/3 negatives.
- `111`: dominant in 4/5 positives and 3/3 negatives.

So the signal is consistent but not separating.

Fase 68 tests a compressed causal-complexity proxy over all 17 `rule_109`
cases. Each step is symbolized as:

`(dominant_context(t), defect_size_bucket(t))`

Metrics:

- `bigram_entropy`
- `unique_transitions`
- `lz_complexity`
- `period_detected`
- `unique_symbols`

Result:

- perfect rules: `0`
- perfect non-period complexity rules: `0`
- best no-false-positive rule: `period_detected >= 12`
- best non-period rule: `bigram_entropy >= 3.673269689515108`, with TP=2, FP=1

Conclusion: compressed temporal summaries do not explain the residual. The
remaining signal appears to live in richer spatial or spatiotemporal cone
structure, not in scalar temporal descriptors of the defect.

Preprint: https://doi.org/10.5281/zenodo.21433927
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.31 - phase and causal-complexity audit in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.31 closes the scalar temporal audit of a persistent `rule_109` residual in
the ANF-gradient block.

The result is deliberately negative:

- phase organization gives a partial signal;
- context `100` appears in 4/5 positives, but also in 2/3 negatives;
- a compressed causal-complexity proxy over all 17 `rule_109` cases finds no clean separator;
- the best no-false-positive rule only repeats the earlier period/horizon result.

So the residual is real, but scalar temporal descriptors do not explain it.
The remaining information appears to require richer spatial or spatiotemporal
cone structure.

Preprint: https://doi.org/10.5281/zenodo.21433927
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: HN account karma was 2 last time checked. Do not post Show HN until the
account has enough karma to avoid auto-removal.
