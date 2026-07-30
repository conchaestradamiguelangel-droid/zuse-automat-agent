# Fase 80: rule_73 len-8 Horizon-Response Topology

## Question

Do the Fase 78 `rule_73/T=12` witnesses occupy contiguous local
robustness bands around their natural-period horizon, or are the Fase 79
survivals isolated threshold crossings?

The horizon grid `8..16` was fixed before measurement. Existing Fase 79
measurements at horizons `10`, `12`, `14`, and `16` are reused exactly;
only horizons `8`, `9`, `11`, `13`, and `15` are newly measured. The
Fase 55 `comparable_to_t15()` predicate and all thresholds are unchanged.

A baseline band is a consecutive run of comparable horizons that contains
`h=12`. Comparable horizons outside that run are reported separately as
disconnected islands.

## Result

Status: `RULE73_HORIZON_BANDS_WITH_CONTROL_CROSSINGS`.

7/9 baseline witnesses form a contiguous band through h=12, but 2 controls also become comparable somewhere in h=8..16.

- Cases: `18`
- Baseline witnesses: `9`
- Baseline controls: `9`
- Witnesses with any off-baseline positive: `7`
- Witnesses with a contiguous band through h=12: `7`
- Witnesses surviving at an immediate neighbor h=11 or h=13: `7`
- Baseline-band width distribution: `{'rule73_bg00001001_T12': 1, 'rule73_bg00001101_T12': 2, 'rule73_bg00001111_T12': 3, 'rule73_bg00011001_T12': 2, 'rule73_bg00011011_T12': 1, 'rule73_bg00101101_T12': 4, 'rule73_bg00101111_T12': 3, 'rule73_bg00110101_T12': 4, 'rule73_bg00111111_T12': 2}`
- Controls becoming comparable anywhere in h=8..16: `2`
- Comparable counts by horizon (witness/control): `{'8': {'witness': 0, 'control': 0}, '9': {'witness': 0, 'control': 0}, '10': {'witness': 1, 'control': 0}, '11': {'witness': 6, 'control': 2}, '12': {'witness': 9, 'control': 0}, '13': {'witness': 5, 'control': 0}, '14': {'witness': 2, 'control': 0}, '15': {'witness': 0, 'control': 0}, '16': {'witness': 0, 'control': 0}}`
- Total comparable response ridge by horizon: `{'8': 0, '9': 0, '10': 1, '11': 8, '12': 9, '13': 5, '14': 2, '15': 0, '16': 0}`
- Packed/concrete discrepancies: `0`

## Response Matrix

`C` means comparable to the unchanged T15 reference; `-` means not comparable.

| cohort | background | IC | h8 | h9 | h10 | h11 | h12 | h13 | h14 | h15 | h16 | band through h12 | disconnected |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline_control | `00000011` | `00101` | - | - | - | - | - | - | - | - | - | [] | [] |
| baseline_witness | `00001001` | `00010111` | - | - | - | - | C | - | - | - | - | [12] | [] |
| baseline_control | `00001011` | `00001000` | - | - | - | - | - | - | - | - | - | [] | [] |
| baseline_witness | `00001101` | `00010011` | - | - | - | - | C | C | - | - | - | [12, 13] | [] |
| baseline_witness | `00001111` | `00000001` | - | - | - | C | C | C | - | - | - | [11, 12, 13] | [] |
| baseline_control | `00010011` | `0101` | - | - | - | - | - | - | - | - | - | [] | [] |
| baseline_witness | `00011001` | `1001100` | - | - | - | C | C | - | - | - | - | [11, 12] | [] |
| baseline_witness | `00011011` | `1010000` | - | - | - | - | C | - | - | - | - | [12] | [] |
| baseline_control | `00101011` | `011` | - | - | - | - | - | - | - | - | - | [] | [] |
| baseline_witness | `00101101` | `01110001` | - | - | - | C | C | C | C | - | - | [11, 12, 13, 14] | [] |
| baseline_witness | `00101111` | `01000101` | - | - | - | C | C | C | - | - | - | [11, 12, 13] | [] |
| baseline_witness | `00110101` | `10001110` | - | - | C | C | C | C | - | - | - | [10, 11, 12, 13] | [] |
| baseline_control | `00110111` | `111` | - | - | - | - | - | - | - | - | - | [] | [] |
| baseline_control | `00111011` | `011` | - | - | - | C | - | - | - | - | - | [] | [11] |
| baseline_control | `00111101` | `101` | - | - | - | C | - | - | - | - | - | [] | [11] |
| baseline_witness | `00111111` | `00011101` | - | - | - | C | C | - | C | - | - | [11, 12] | [14] |
| baseline_control | `01011011` | `101111` | - | - | - | - | - | - | - | - | - | [] | [] |
| baseline_control | `01101111` | `1` | - | - | - | - | - | - | - | - | - | [] | [] |

## Comparable Measurements

| cohort | background | horizon | slope | R2 | slope delta |
| --- | --- | ---: | ---: | ---: | ---: |
| baseline_witness | `00001001` | 12 | -0.311180 | 0.975890 | 1.27% |
| baseline_witness | `00001101` | 12 | -0.305307 | 0.998962 | 0.64% |
| baseline_witness | `00001101` | 13 | -0.287415 | 0.957675 | 6.47% |
| baseline_witness | `00001111` | 11 | -0.320032 | 0.977161 | 4.15% |
| baseline_witness | `00001111` | 12 | -0.300277 | 0.967589 | 2.28% |
| baseline_witness | `00001111` | 13 | -0.307092 | 0.978938 | 0.06% |
| baseline_witness | `00011001` | 11 | -0.315490 | 0.999361 | 2.67% |
| baseline_witness | `00011001` | 12 | -0.291364 | 0.999252 | 5.18% |
| baseline_witness | `00011011` | 12 | -0.299605 | 0.998701 | 2.50% |
| baseline_witness | `00101101` | 11 | -0.302499 | 0.964031 | 1.56% |
| baseline_witness | `00101101` | 12 | -0.292005 | 0.964906 | 4.97% |
| baseline_witness | `00101101` | 13 | -0.308117 | 0.960687 | 0.27% |
| baseline_witness | `00101101` | 14 | -0.286499 | 0.958552 | 6.76% |
| baseline_witness | `00101111` | 11 | -0.300526 | 0.985393 | 2.20% |
| baseline_witness | `00101111` | 12 | -0.307370 | 0.963517 | 0.03% |
| baseline_witness | `00101111` | 13 | -0.290298 | 0.991843 | 5.53% |
| baseline_witness | `00110101` | 10 | -0.278857 | 0.980284 | 9.25% |
| baseline_witness | `00110101` | 11 | -0.281605 | 0.967763 | 8.36% |
| baseline_witness | `00110101` | 12 | -0.322055 | 0.971373 | 4.81% |
| baseline_witness | `00110101` | 13 | -0.314610 | 0.966450 | 2.38% |
| baseline_control | `00111011` | 11 | -0.303828 | 0.990540 | 1.12% |
| baseline_control | `00111101` | 11 | -0.303828 | 0.990540 | 1.12% |
| baseline_witness | `00111111` | 11 | -0.306468 | 0.952197 | 0.27% |
| baseline_witness | `00111111` | 12 | -0.278618 | 0.965251 | 9.33% |
| baseline_witness | `00111111` | 14 | -0.297369 | 0.959874 | 3.23% |

## Independent Re-measurement

One band witness and one control crossing were recomputed without
reading their checkpoint entries.

| cohort | background | horizon | exact raw match | concrete match |
| --- | --- | ---: | --- | --- |
| baseline_witness | `00101101` | 11 | true | true |
| baseline_control | `00111011` | 11 | true | true |

## Interpretation

At least one natural-period witness remains comparable at an
immediately adjacent integer horizon, so the response is not only
a collection of isolated even-horizon crossings. The width and
background dependence of each band are reported without fitting a
new classifier.

At cohort level, the response is concentrated in a finite ridge around
`h=12`, but cohort membership is not invariant: two baseline controls
become comparable only at `h=11`. The result therefore supports local
horizon bands for most natural-period witnesses, not a fixed set of
backgrounds that remains positive throughout the neighborhood.

Control crossings prevent interpreting the response topology as a
clean witness-specific robustness property.

## Methodological Limits

- The grid is local (`h=8..16`) and does not establish behavior at
  arbitrarily short or long horizons.
- The analysis covers one ECA rule and primitive length-8 backgrounds.
- Band membership is defined by the inherited Fase 55 threshold; no
  new threshold is fitted.
- The same physical oscillator and IC are retained while only the
  measurement horizon changes.
