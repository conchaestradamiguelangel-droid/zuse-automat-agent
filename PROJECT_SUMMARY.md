# ZUSE Automat Agent - What We Found

ZUSE Automat Agent is a deterministic system that explores very simple digital
worlds and records which kinds of behavior appear. Each world is made of cells
that switch on and off according to fixed rules. ZUSE runs those worlds many
times, measures patterns such as stability, repetition, complexity, and
fragility, and builds a reproducible map of what it finds.

## Key Results

- `frontera_temporal` is common, not rare: it activates in `38/256`
  elementary cellular automaton rules under at least two of three seeds, and in
  `17/256` rules under all three.
- `rule_108` is the only ECA rule found to produce a stationary local period-2
  oscillator under the quiescent-background protocol. Its core motif is
  `#.# <-> ###`.
- One-bit initial-condition fragility spans almost the full range: from
  `f_total = 0.000` in `rule_208` and `rule_209` to `f_total = 0.992` in
  `rule_108`.
- Four fragility mechanisms are distinguished: stable basins, productive basin
  switching, noise-boundary crossing, and quiescent-background activation.
- The underlying ECA dynamics can be translation-invariant while the measurement
  pipeline is not. ZUSE measures and documents this observer artifact instead
  of hiding it.

## Why It Matters

ZUSE is a small reproducible example of automated scientific discovery: it shows
how a deterministic system can explore complex behavior, separate real dynamics
from measurement artifacts, and produce a citable empirical atlas without a
language model inside the discovery loop.

## Read More

- Preprint: https://doi.org/10.5281/zenodo.20516375
- Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- Full atlas: [outputs/world_taxonomy/law_map.md](outputs/world_taxonomy/law_map.md)
- Reproducibility guide: [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
