# Fragility Position Map - Fase 10b

## Method

Input: `outputs/fragility_fase10/fragility_results.jsonl`. For each `(world, seed)`, a 64-position fragility vector is computed with `1` when `outcome != "same_sig"` and `0` otherwise. Vectors are averaged across seeds per world.

Cluster threshold: `bin_range > 0.30` - `clustered`, else `dispersed`. Bins are 8 contiguous spatial bins of 8 positions each.

## Per-World Analysis

### rule_109 (1 seed - single IC, no cross-seed average)

Bin fragility (8 bins - 8 positions):

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

Top 10 fragile positions: `[8, 9, 10, 11, 12, 13, 15, 16, 17, 22]`

Left half (0-31) mean: `0.500` | Right half (32-63) mean: `0.000`

Pattern: `clustered` (bin_range = `0.875`)

### rule_137 (3 seeds)

Bin fragility (8 bins - 8 positions):

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

Top 10 fragile positions: `[2, 3, 5, 17, 38, 40, 47, 48, 56, 59]`

Left half (0-31) mean: `0.583` | Right half (32-63) mean: `0.677`

Pattern: `dispersed` (bin_range = `0.250`)

### rule_18 (3 seeds)

Bin fragility (8 bins - 8 positions):

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

Top 10 fragile positions: `[0, 9, 11, 2, 8, 10, 14, 19, 23, 32]`

Left half (0-31) mean: `0.385` | Right half (32-63) mean: `0.312`

Pattern: `clustered` (bin_range = `0.417`)

### rule_90 (3 seeds)

Bin fragility (8 bins - 8 positions):

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

Top 10 fragile positions: `[2, 6, 10, 33, 60, 62, 0, 1, 3, 4]`

Left half (0-31) mean: `0.177` | Right half (32-63) mean: `0.167`

Pattern: `clustered` (bin_range = `0.333`)

## Cross-World Summary

| world | left_mean | right_mean | bin_range | pattern |
| --- | --- | --- | --- | --- |
| rule_109 | 0.500 | 0.000 | 0.875 | clustered |
| rule_137 | 0.583 | 0.677 | 0.250 | dispersed |
| rule_18 | 0.385 | 0.312 | 0.417 | clustered |
| rule_90 | 0.177 | 0.167 | 0.333 | clustered |

## Conclusion

`rule_137` is `dispersed` by the bin-range criterion (`0.250`). Its fragility is high in magnitude, but its sensitive positions are not concentrated into one dominant spatial cluster under the 8-bin test.

Worlds classified as clustered: `rule_109`, `rule_18`, `rule_90`.

This supports the high-dimensional basin-boundary interpretation: for `rule_137`, sensitivity is a global property of the IC neighborhood rather than a localized fragile segment. Compared with `rule_18`, `rule_109`, and `rule_90`, `rule_137` differs mainly in total fragility, not in spatial concentration.
