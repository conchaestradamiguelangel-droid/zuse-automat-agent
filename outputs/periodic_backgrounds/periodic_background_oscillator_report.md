# Periodic-Background Oscillator Sweep

## Protocol

- Rules: all 256 ECA rules.
- Backgrounds: unique non-zero tiled backgrounds with template length 1, 2, or 4 (`15` backgrounds).
- ICs: `502` non-zero binary words of length 1..8, replacing the centered background window.
- Width: `256`.
- Steps: `300`.
- Burn-in: `80`.
- Period search: `2..16`.
- Max perturbation span: `32`.
- Detector: exact recurrence of the localized difference between perturbed run and unperturbed background orbit.

## Result

- Processed runs: `1927680`
- Elapsed seconds: approximately `3595` total (`1957` interrupted first segment + `1638` resumed segment)
- Candidate detections: `122253`
- Stationary rules: `rule_1`, `rule_5`, `rule_18`, `rule_28`, `rule_29`, `rule_33`, `rule_37`, `rule_54`, `rule_70`, `rule_71`, `rule_73`, `rule_91`, `rule_94`, `rule_95`, `rule_108`, `rule_109`, `rule_122`, `rule_123`, `rule_126`, `rule_127`, `rule_129`, `rule_133`, `rule_147`, `rule_156`, `rule_157`, `rule_161`, `rule_183`, `rule_198`, `rule_199`, `rule_201`
- Moving rules: `rule_3`, `rule_6`, `rule_17`, `rule_20`, `rule_27`, `rule_35`, `rule_38`, `rule_39`, `rule_49`, `rule_52`, `rule_53`, `rule_58`, `rule_59`, `rule_62`, `rule_63`, `rule_83`, `rule_114`, `rule_115`, `rule_118`, `rule_119`, `rule_131`, `rule_134`, `rule_145`, `rule_148`, `rule_154`, `rule_155`, `rule_158`, `rule_159`, `rule_163`, `rule_166`, `rule_177`, `rule_180`, `rule_210`, `rule_211`, `rule_214`, `rule_215`
- New stationary rules beyond zero-background baseline: `rule_1`, `rule_5`, `rule_18`, `rule_28`, `rule_29`, `rule_33`, `rule_37`, `rule_54`, `rule_70`, `rule_71`, `rule_73`, `rule_91`, `rule_94`, `rule_95`, `rule_109`, `rule_122`, `rule_123`, `rule_126`, `rule_127`, `rule_129`, `rule_133`, `rule_147`, `rule_156`, `rule_157`, `rule_161`, `rule_183`, `rule_198`, `rule_199`, `rule_201`
- New moving rules beyond zero-background baseline: `rule_3`, `rule_17`, `rule_27`, `rule_35`, `rule_39`, `rule_49`, `rule_53`, `rule_58`, `rule_59`, `rule_62`, `rule_63`, `rule_83`, `rule_114`, `rule_115`, `rule_118`, `rule_119`, `rule_131`, `rule_145`, `rule_154`, `rule_155`, `rule_158`, `rule_159`, `rule_163`, `rule_177`, `rule_210`, `rule_211`, `rule_214`, `rule_215`
- Alias handling: Period-1 moving-particle aliases were filtered during detection; alias counts are not central to this periodic-background report.

## Candidate Rules

| kind | world | candidates | background | min_len | min_word | T | drift | motif_or_shapes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| moving | rule_3 | 138 | 0001 | 1 | `1` | 2 | 1 | [[0], [0]] |
| moving | rule_6 | 862 | 1 | 3 | `100` | 2 | -2 | [[0, 1], [0]] |
| moving | rule_17 | 138 | 0001 | 1 | `1` | 2 | -1 | [[0], [0]] |
| moving | rule_20 | 871 | 1 | 3 | `010` | 2 | 2 | [[0, 1], [0]] |
| moving | rule_27 | 306 | 1 | 2 | `01` | 2 | 1 | [[0], [0]] |
| moving | rule_35 | 369 | 0001 | 1 | `1` | 2 | 1 | [[0], [0]] |
| moving | rule_38 | 422 | 1 | 2 | `01` | 2 | -2 | [[0, 1], [0]] |
| moving | rule_39 | 297 | 1 | 2 | `01` | 2 | 1 | [[0], [0]] |
| moving | rule_49 | 369 | 0001 | 1 | `1` | 2 | -1 | [[0], [0]] |
| moving | rule_52 | 423 | 1 | 2 | `10` | 2 | 2 | [[0, 1], [0]] |
| moving | rule_53 | 297 | 1 | 2 | `01` | 2 | -1 | [[0], [0]] |
| moving | rule_58 | 191 | 0011 | 1 | `1` | 2 | 1 | [[0], [0]] |
| moving | rule_59 | 373 | 0001 | 4 | `1110` | 2 | 1 | [[0], [0]] |
| moving | rule_62 | 349 | 0001 | 3 | `011` | 2 | 1 | [[0], [0]] |
| moving | rule_63 | 140 | 0011 | 1 | `1` | 2 | 1 | [[0], [0]] |
| moving | rule_83 | 306 | 1 | 2 | `01` | 2 | -1 | [[0], [0]] |
| moving | rule_114 | 191 | 0011 | 1 | `1` | 2 | -1 | [[0], [0]] |
| moving | rule_115 | 373 | 0001 | 3 | `111` | 2 | -1 | [[0], [0]] |
| moving | rule_118 | 349 | 0001 | 5 | `00001` | 2 | -1 | [[0], [0]] |
| moving | rule_119 | 140 | 0011 | 1 | `1` | 2 | -1 | [[0], [0]] |
| moving | rule_131 | 572 | 0001 | 1 | `1` | 2 | 1 | [[0], [0]] |
| moving | rule_134 | 335 | 10 | 3 | `001` | 2 | 2 | [[0, 1], [0]] |
| moving | rule_145 | 344 | 0001 | 1 | `1` | 2 | -1 | [[0], [0]] |
| moving | rule_148 | 323 | 01 | 3 | `001` | 2 | -2 | [[0], [0, 1]] |
| moving | rule_154 | 92 | 1 | 2 | `01` | 2 | -2 | [[0], [0, 1]] |
| moving | rule_155 | 422 | 1 | 2 | `01` | 2 | -2 | [[0], [0, 1]] |
| moving | rule_158 | 412 | 1 | 2 | `01` | 2 | -2 | [[0], [0, 1]] |
| moving | rule_159 | 848 | 1 | 2 | `01` | 2 | -2 | [[0], [0, 1]] |
| moving | rule_163 | 189 | 0001 | 1 | `1` | 2 | 1 | [[0], [0]] |
| moving | rule_166 | 48 | 0001 | 7 | `0000001` | 2 | -2 | [[0], [0, 1]] |
| moving | rule_177 | 189 | 0001 | 1 | `1` | 2 | -1 | [[0], [0]] |
| moving | rule_180 | 48 | 0001 | 3 | `101` | 4 | 4 | [[0], [0, 1], [0, 2, 3], [0]] |
| moving | rule_210 | 90 | 1 | 2 | `10` | 2 | 2 | [[0], [0, 1]] |
| moving | rule_211 | 419 | 1 | 2 | `10` | 2 | 2 | [[0], [0, 1]] |
| moving | rule_214 | 399 | 1 | 2 | `10` | 2 | 2 | [[0], [0, 1]] |
| moving | rule_215 | 860 | 1 | 2 | `10` | 2 | 2 | [[0], [0, 1]] |
| stationary | rule_1 | 4530 | 1 | 4 | `0001` | 2 | 0 | # / ### |
| stationary | rule_5 | 6390 | 1 | 3 | `010` | 2 | 0 | # / #.# |
| stationary | rule_18 | 4 | 0011 | 8 | `10001010` | 2 | 0 | #..###.## / ##.###..# |
| stationary | rule_28 | 4968 | 01 | 2 | `01` | 2 | 0 | #### / ## |
| stationary | rule_29 | 7248 | 1 | 2 | `01` | 2 | 0 | # / # |
| stationary | rule_33 | 6045 | 1 | 2 | `01` | 2 | 0 | # / ### |
| stationary | rule_37 | 7080 | 1 | 2 | `01` | 2 | 0 | ### / ##### |
| stationary | rule_54 | 229 | 0001 | 3 | `001` | 4 | 0 | ##.# / #.# / #.## / #.# |
| stationary | rule_70 | 4968 | 01 | 3 | `010` | 2 | 0 | ### / ### |
| stationary | rule_71 | 7248 | 1 | 2 | `01` | 2 | 0 | # / # |
| stationary | rule_73 | 2210 | 0001 | 1 | `1` | 2 | 0 | ##### / #.# |
| stationary | rule_91 | 7131 | 1 | 2 | `01` | 2 | 0 | ##### / ### |
| stationary | rule_94 | 1629 | 01 | 4 | `1010` | 2 | 0 | ###.# / #### |
| stationary | rule_95 | 6593 | 1 | 2 | `01` | 2 | 0 | #.# / # |
| stationary | rule_108 | 4267 | 1 | 2 | `01` | 2 | 0 | ### / #.# |
| stationary | rule_109 | 2212 | 0011 | 1 | `1` | 2 | 0 | ##.# / #.# |
| stationary | rule_122 | 2 | 0111 | 8 | `10011110` | 2 | 0 | #..#.### / ###.#..# |
| stationary | rule_123 | 6121 | 1 | 2 | `01` | 2 | 0 | ### / # |
| stationary | rule_126 | 16 | 0001 | 7 | `1111010` | 2 | 0 | ###.#..# / #..#.### |
| stationary | rule_127 | 4909 | 1 | 2 | `01` | 2 | 0 | ### / # |
| stationary | rule_129 | 16 | 0001 | 7 | `1111010` | 2 | 0 | ###.#..# / #..#.### |
| stationary | rule_133 | 1622 | 01 | 4 | `1000` | 2 | 0 | #.## / ##.# |
| stationary | rule_147 | 230 | 0001 | 5 | `00011` | 4 | 0 | #.# / ##.# / #.# / #.## |
| stationary | rule_156 | 4968 | 01 | 2 | `01` | 2 | 0 | #### / ## |
| stationary | rule_157 | 4968 | 01 | 2 | `01` | 2 | 0 | #### / ## |
| stationary | rule_161 | 2 | 0001 | 8 | `10000110` | 2 | 0 | ###.#..# / #..#.### |
| stationary | rule_183 | 4 | 0011 | 8 | `10001110` | 2 | 0 | ##.###..# / #..###.## |
| stationary | rule_198 | 4968 | 01 | 3 | `010` | 2 | 0 | ### / ### |
| stationary | rule_199 | 4968 | 01 | 3 | `010` | 2 | 0 | ### / ### |
| stationary | rule_201 | 4213 | 1 | 3 | `010` | 2 | 0 | ### / #.# |

## Interpretation

This opens a different protocol from the quiescent-zero sweeps. The tested
background set includes all-one plus non-zero period-2 and period-4 tiled
backgrounds. Hits are local perturbations measured relative to a periodic
background orbit, so global background periodicity alone does not count as a
local oscillator.

Scientific reading: non-zero periodic backgrounds greatly enlarge the local
oscillator landscape. Under this protocol, many rules that were silent on a
zero background support stationary or moving localized difference patterns.
These results should not be merged into the zero-background uniqueness claims;
they define a new background-conditioned regime.
