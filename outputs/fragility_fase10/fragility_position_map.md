# Fragility Position Map - Fase 10b/12a/12c

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

### rule_110 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.375 |
| 1 | 8-15 | 0.250 |
| 2 | 16-23 | 0.125 |
| 3 | 24-31 | 0.375 |
| 4 | 32-39 | 0.542 |
| 5 | 40-47 | 0.250 |
| 6 | 48-55 | 0.125 |
| 7 | 56-63 | 0.542 |

Top 10 fragile positions: [38, 56, 61, 63, 0, 1, 4, 6, 25, 29]

Left half (0-31) mean: 0.281 | Right half (32-63) mean: 0.365

Pattern: clustered (bin_range = 0.417)

### rule_124 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.125 |
| 1 | 8-15 | 0.083 |
| 2 | 16-23 | 0.208 |
| 3 | 24-31 | 0.250 |
| 4 | 32-39 | 0.250 |
| 5 | 40-47 | 0.375 |
| 6 | 48-55 | 0.292 |
| 7 | 56-63 | 0.208 |

Top 10 fragile positions: [0, 29, 31, 32, 40, 41, 44, 45, 51, 52]

Left half (0-31) mean: 0.167 | Right half (32-63) mean: 0.281

Pattern: dispersed (bin_range = 0.292)

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

### rule_54 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.750 |
| 1 | 8-15 | 0.458 |
| 2 | 16-23 | 0.583 |
| 3 | 24-31 | 0.833 |
| 4 | 32-39 | 0.792 |
| 5 | 40-47 | 0.583 |
| 6 | 48-55 | 0.917 |
| 7 | 56-63 | 0.792 |

Top 10 fragile positions: [0, 5, 6, 7, 14, 25, 27, 28, 29, 30]

Left half (0-31) mean: 0.656 | Right half (32-63) mean: 0.771

Pattern: clustered (bin_range = 0.458)

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
| rule_110 | 0.281 | 0.365 | 0.417 | clustered |
| rule_124 | 0.167 | 0.281 | 0.292 | dispersed |
| rule_137 | 0.583 | 0.677 | 0.250 | dispersed |
| rule_18 | 0.385 | 0.312 | 0.417 | clustered |
| rule_208 | 0.000 | 0.000 | 0.000 | dispersed |
| rule_209 | 0.000 | 0.000 | 0.000 | dispersed |
| rule_46 | 0.031 | 0.031 | 0.083 | dispersed |
| rule_54 | 0.656 | 0.771 | 0.458 | clustered |
| rule_90 | 0.177 | 0.167 | 0.333 | clustered |

## Conclusion

`rule_137` remains a dispersed high-fragility productive basin. `rule_54` is even more fragile in total, but for a different reason: many perturbations cross the noise gate rather than merely shifting to another productive signature.

`rule_46`, `rule_208`, and `rule_209` remain stable frontier-rich worlds. `rule_208` and `rule_209` have zero positional fragility in this sample; `rule_46` has only sparse low-level fragility.
