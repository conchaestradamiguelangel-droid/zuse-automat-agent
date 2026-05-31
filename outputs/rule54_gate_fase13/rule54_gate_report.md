# Rule 54 Noise Gate Anatomy - Fase 13

## Setup

- World: `rule_54`
- Rule: `54`
- Seeds: `20260638, 20260640, 20260642`
- Steps: `96`
- Width: `64`
- Noise gate: `dedup_structure_count > 40`
- Cluster threshold: `bin_range > 0.30`

## Gate Summary

Noise flips: `72/192` = `0.375`.

| seed | noise_flips | noise_rate | raw_mean | dedup_mean | dedup_mean_when_noise | reference_raw | reference_dedup |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20260638 | 14 | 0.219 | 110.859 | 36.938 | 45.000 | 96 | 32 |
| 20260640 | 18 | 0.281 | 114.094 | 38.031 | 45.833 | 99 | 33 |
| 20260642 | 40 | 0.625 | 124.594 | 41.531 | 43.725 | 117 | 39 |

## Position Map

| bin | positions | noise_rate |
| --- | --- | --- |
| 0 | 0-7 | 0.500 |
| 1 | 8-15 | 0.167 |
| 2 | 16-23 | 0.375 |
| 3 | 24-31 | 0.333 |
| 4 | 32-39 | 0.250 |
| 5 | 40-47 | 0.333 |
| 6 | 48-55 | 0.542 |
| 7 | 56-63 | 0.500 |

Left half mean: `0.344`  
Right half mean: `0.406`  
Bin range: `0.375`  
Pattern: `clustered`

Top noisy positions:

| bit_position | noise_rate | noise_count |
| --- | --- | --- |
| 5 | 1.000 | 3 |
| 0 | 0.667 | 2 |
| 6 | 0.667 | 2 |
| 14 | 0.667 | 2 |
| 19 | 0.667 | 2 |
| 22 | 0.667 | 2 |
| 27 | 0.667 | 2 |
| 29 | 0.667 | 2 |
| 30 | 0.667 | 2 |
| 36 | 0.667 | 2 |

## Noise-Crossing Flips

| seed | bit_position | raw_count | dedup_count | cruza_gate | motivo |
| --- | --- | --- | --- | --- | --- |
| 20260638 | 5 | 126 | 42 | yes | dedup_structure_count>40 |
| 20260638 | 14 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260638 | 27 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260638 | 34 | 156 | 52 | yes | dedup_structure_count>40 |
| 20260638 | 41 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260638 | 49 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260638 | 50 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260638 | 51 | 156 | 52 | yes | dedup_structure_count>40 |
| 20260638 | 52 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260638 | 53 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260638 | 54 | 144 | 48 | yes | dedup_structure_count>40 |
| 20260638 | 55 | 126 | 42 | yes | dedup_structure_count>40 |
| 20260638 | 56 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260638 | 57 | 153 | 51 | yes | dedup_structure_count>40 |
| 20260640 | 0 | 138 | 46 | yes | dedup_structure_count>40 |
| 20260640 | 4 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260640 | 5 | 141 | 47 | yes | dedup_structure_count>40 |
| 20260640 | 6 | 150 | 50 | yes | dedup_structure_count>40 |
| 20260640 | 7 | 144 | 48 | yes | dedup_structure_count>40 |
| 20260640 | 17 | 150 | 50 | yes | dedup_structure_count>40 |
| 20260640 | 19 | 144 | 48 | yes | dedup_structure_count>40 |
| 20260640 | 22 | 144 | 48 | yes | dedup_structure_count>40 |
| 20260640 | 23 | 144 | 48 | yes | dedup_structure_count>40 |
| 20260640 | 27 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260640 | 29 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260640 | 30 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260640 | 32 | 126 | 42 | yes | dedup_structure_count>40 |
| 20260640 | 36 | 126 | 42 | yes | dedup_structure_count>40 |
| 20260640 | 39 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260640 | 59 | 144 | 48 | yes | dedup_structure_count>40 |
| 20260640 | 61 | 138 | 46 | yes | dedup_structure_count>40 |
| 20260640 | 62 | 153 | 51 | yes | dedup_structure_count>40 |
| 20260642 | 0 | 135 | 45 | yes | dedup_structure_count>40 |
| 20260642 | 1 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 2 | 138 | 46 | yes | dedup_structure_count>40 |
| 20260642 | 3 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260642 | 5 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260642 | 6 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 8 | 150 | 50 | yes | dedup_structure_count>40 |
| 20260642 | 9 | 135 | 45 | yes | dedup_structure_count>40 |
| 20260642 | 14 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 16 | 126 | 42 | yes | dedup_structure_count>40 |
| 20260642 | 19 | 135 | 45 | yes | dedup_structure_count>40 |
| 20260642 | 20 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 21 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260642 | 22 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260642 | 26 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 28 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 29 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260642 | 30 | 135 | 45 | yes | dedup_structure_count>40 |
| 20260642 | 36 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260642 | 38 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 40 | 138 | 46 | yes | dedup_structure_count>40 |
| 20260642 | 41 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 43 | 135 | 45 | yes | dedup_structure_count>40 |
| 20260642 | 44 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260642 | 45 | 162 | 54 | yes | dedup_structure_count>40 |
| 20260642 | 46 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 47 | 138 | 46 | yes | dedup_structure_count>40 |
| 20260642 | 48 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260642 | 49 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260642 | 52 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260642 | 53 | 129 | 43 | yes | dedup_structure_count>40 |
| 20260642 | 54 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260642 | 55 | 132 | 44 | yes | dedup_structure_count>40 |
| 20260642 | 56 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 58 | 135 | 45 | yes | dedup_structure_count>40 |
| 20260642 | 59 | 123 | 41 | yes | dedup_structure_count>40 |
| 20260642 | 60 | 135 | 45 | yes | dedup_structure_count>40 |
| 20260642 | 61 | 126 | 42 | yes | dedup_structure_count>40 |
| 20260642 | 62 | 153 | 51 | yes | dedup_structure_count>40 |
| 20260642 | 63 | 126 | 42 | yes | dedup_structure_count>40 |

## Interpretation

The rule_54 noise mechanism is exactly the deduplicated structure gate:
every noisy flip has `dedup_structure_count > 40`.

The noise positions are spatially clustered:
`bin_range = 0.375`. This tests the Fase 12 hypothesis that
rule_54's clustered fragility reflects a localized region of the IC pushing the
system over the dedup threshold.

The clustering is not a single contiguous block. It is a multi-hot spatial
pattern with strongest bins at the edges/right tail (`0-7`, `48-55`, `56-63`)
and weaker response in the middle. Bit `5` is the only position that crosses
the gate in all three measured seeds.

Seed sensitivity matters: seed `20260642` accounts for the largest
number of noise flips and starts at `reference_dedup_structure_count =
39`, only one structure below the threshold. That
explains why many one-bit perturbations push it over the gate.
