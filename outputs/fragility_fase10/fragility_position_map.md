# Fragility Position Map - Fase 10b/12a/12c/13b/15a

## Method

Data source: `outputs/fragility_fase10/fragility_results.jsonl`.

For each `(world, seed)`, `fragility_vec[i] = 1` when flipping bit `i` changes the law signature, reaches silence, or reaches noise; otherwise `0`.

Cluster threshold: `bin_range > 0.30` -> clustered, else dispersed.

## Per-World Analysis

### rule_109 (3 seeds) - Fase 13b multi-seed confirmation

Bin fragility (8 bins x 8 positions, mean across 3 seeds):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.167 |
| 1 | 8-15 | 0.292 |
| 2 | 16-23 | 0.417 |
| 3 | 24-31 | 0.667 |
| 4 | 32-39 | 0.208 |
| 5 | 40-47 | 0.292 |
| 6 | 48-55 | 0.208 |
| 7 | 56-63 | 0.208 |

Per-seed comparison:

| seed | f_total | f_other_sig | f_silence | f_noise | bin_range | peak_bin | peak_center | central_peak |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20260554 | 0.250 | 0.250 | 0.000 | 0.000 | 0.875 | 1 | 11.500 | no |
| 20260601 | 0.469 | 0.469 | 0.000 | 0.000 | 0.750 | 3 | 27.500 | yes |
| 20260602 | 0.203 | 0.203 | 0.000 | 0.000 | 0.625 | 3 | 27.500 | yes |

Top 10 fragile positions: [25, 26, 27, 16, 17, 18, 23, 24, 28, 44]

Left half (0-31) mean: 0.385 | Right half (32-63) mean: 0.229

Pattern: clustered (bin_range = 0.500)

Fase 13b verdict: **cluster_confirmado**. Cluster confirmado como propiedad robusta de `rule_109`: al menos 2/3 seeds tienen `bin_range > 0.5` y pico central.

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

### rule_51 (3 seeds)

Bin fragility (8 bins x 8 positions):

| Bin | Positions | Mean fragility |
| --- | --- | --- |
| 0 | 0-7 | 0.250 |
| 1 | 8-15 | 0.208 |
| 2 | 16-23 | 0.083 |
| 3 | 24-31 | 0.208 |
| 4 | 32-39 | 0.208 |
| 5 | 40-47 | 0.167 |
| 6 | 48-55 | 0.292 |
| 7 | 56-63 | 0.125 |

Top 10 fragile positions: [1, 2, 3, 4, 5, 7, 8, 10, 13, 14]

Left half (0-31) mean: 0.188 | Right half (32-63) mean: 0.198

Pattern: dispersed (bin_range = 0.208)

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
| rule_109 | 0.385 | 0.229 | 0.500 | clustered |
| rule_110 | 0.281 | 0.365 | 0.417 | clustered |
| rule_124 | 0.167 | 0.281 | 0.292 | dispersed |
| rule_137 | 0.583 | 0.677 | 0.250 | dispersed |
| rule_18 | 0.385 | 0.312 | 0.417 | clustered |
| rule_208 | 0.000 | 0.000 | 0.000 | dispersed |
| rule_209 | 0.000 | 0.000 | 0.000 | dispersed |
| rule_46 | 0.031 | 0.031 | 0.083 | dispersed |
| rule_51 | 0.188 | 0.198 | 0.208 | dispersed |
| rule_54 | 0.656 | 0.771 | 0.458 | clustered |
| rule_90 | 0.177 | 0.167 | 0.333 | clustered |

## Conclusion

`rule_51` adds a global-periodic world with moderate signature fragility: periodicity survives, but density-related signature components can change under one-bit flips.

`rule_137` remains the clearest dispersed high-fragility productive basin. `rule_54` remains the clearest noise-boundary fragility case.
