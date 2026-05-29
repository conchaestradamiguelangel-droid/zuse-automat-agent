# Fragility Position Map - Fase 10b/12a

## Method

Data source: `outputs/fragility_fase10/fragility_results.jsonl`.

For each `(world, seed)`, `fragility_vec[i] = 1` when flipping bit `i` changes the law signature, reaches silence, or reaches noise; otherwise `0`.

Cluster threshold: `bin_range > 0.30` -> clustered, else dispersed.

## Per-World Analysis

### rule_109 (1 seed) - single IC, no cross-seed average

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.000 |
| 1 | 8-15 | 0.875 |
| 2 | 16-23 | 0.500 |
| 3 | 24-31 | 0.625 |
| 4 | 32-39 | 0.000 |
| 5 | 40-47 | 0.000 |
| 6 | 48-55 | 0.000 |
| 7 | 56-63 | 0.000 |

Top 10 fragile positions: [8, 9, 10, 11, 12, 13, 15, 16, 17, 22]

Left half (0-31) mean: 0.500 | Right half (32-63) mean: 0.000

Pattern: clustered (bin_range = 0.875)

### rule_137 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.625 |
| 1 | 8-15 | 0.583 |
| 2 | 16-23 | 0.542 |
| 3 | 24-31 | 0.583 |
| 4 | 32-39 | 0.625 |
| 5 | 40-47 | 0.667 |
| 6 | 48-55 | 0.625 |
| 7 | 56-63 | 0.792 |

Top 10 fragile positions: [2, 3, 5, 17, 38, 40, 47, 48, 56, 59]

Left half (0-31) mean: 0.583 | Right half (32-63) mean: 0.677

Pattern: dispersed (bin_range = 0.250)

### rule_18 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.375 |
| 1 | 8-15 | 0.625 |
| 2 | 16-23 | 0.333 |
| 3 | 24-31 | 0.208 |
| 4 | 32-39 | 0.208 |
| 5 | 40-47 | 0.292 |
| 6 | 48-55 | 0.375 |
| 7 | 56-63 | 0.375 |

Top 10 fragile positions: [0, 9, 11, 2, 8, 10, 14, 19, 23, 32]

Left half (0-31) mean: 0.385 | Right half (32-63) mean: 0.312

Pattern: clustered (bin_range = 0.417)

### rule_208 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.000 |
| 1 | 8-15 | 0.000 |
| 2 | 16-23 | 0.000 |
| 3 | 24-31 | 0.000 |
| 4 | 32-39 | 0.000 |
| 5 | 40-47 | 0.000 |
| 6 | 48-55 | 0.000 |
| 7 | 56-63 | 0.000 |

Top 10 fragile positions: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Left half (0-31) mean: 0.000 | Right half (32-63) mean: 0.000

Pattern: dispersed (bin_range = 0.000)

### rule_209 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.000 |
| 1 | 8-15 | 0.000 |
| 2 | 16-23 | 0.000 |
| 3 | 24-31 | 0.000 |
| 4 | 32-39 | 0.000 |
| 5 | 40-47 | 0.000 |
| 6 | 48-55 | 0.000 |
| 7 | 56-63 | 0.000 |

Top 10 fragile positions: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

Left half (0-31) mean: 0.000 | Right half (32-63) mean: 0.000

Pattern: dispersed (bin_range = 0.000)

### rule_46 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.083 |
| 1 | 8-15 | 0.000 |
| 2 | 16-23 | 0.000 |
| 3 | 24-31 | 0.042 |
| 4 | 32-39 | 0.000 |
| 5 | 40-47 | 0.042 |
| 6 | 48-55 | 0.083 |
| 7 | 56-63 | 0.000 |

Top 10 fragile positions: [3, 7, 28, 44, 48, 55, 0, 1, 2, 4]

Left half (0-31) mean: 0.031 | Right half (32-63) mean: 0.031

Pattern: dispersed (bin_range = 0.083)

### rule_90 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.375 |
| 1 | 8-15 | 0.208 |
| 2 | 16-23 | 0.083 |
| 3 | 24-31 | 0.042 |
| 4 | 32-39 | 0.208 |
| 5 | 40-47 | 0.083 |
| 6 | 48-55 | 0.083 |
| 7 | 56-63 | 0.292 |

Top 10 fragile positions: [2, 6, 10, 33, 60, 62, 0, 1, 3, 4]

Left half (0-31) mean: 0.177 | Right half (32-63) mean: 0.167

Pattern: clustered (bin_range = 0.333)

## Cross-World Summary

| world | left_mean | right_mean | bin_range | pattern |
| --- | --- | --- | --- | --- |
| rule_109 | 0.500 | 0.000 | 0.875 | clustered |
| rule_137 | 0.583 | 0.677 | 0.250 | dispersed |
| rule_18 | 0.385 | 0.312 | 0.417 | clustered |
| rule_208 | 0.000 | 0.000 | 0.000 | dispersed |
| rule_209 | 0.000 | 0.000 | 0.000 | dispersed |
| rule_46 | 0.031 | 0.031 | 0.083 | dispersed |
| rule_90 | 0.177 | 0.167 | 0.333 | clustered |

## Conclusion

`rule_137` remains the clearest dispersed high-fragility basin: its fragility is spread across the IC rather than concentrated in one local region.

`rule_46`, `rule_208`, and `rule_209` are stable frontier-rich worlds. `rule_208` and `rule_209` have zero positional fragility in this sample; `rule_46` has only sparse low-level fragility. Their broad basins contrast sharply with `rule_137`.
