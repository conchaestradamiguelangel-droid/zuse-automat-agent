# Fase 77: External Natural-Period ANF Census on Primitive Period-8 Backgrounds

## Question

Does the unchanged Fase 55 `comparable_to_t15()` predicate identify a
genuine natural-period ANF-gradient witness in stationary oscillators from
rules absent from the original six-rule census?

This phase creates an external holdout from the already completed
3,855,360-run primitive period-8 background sweep. Candidate selection was
fixed before ANF measurement. Only the natural oscillator period is measured;
`T_WINDOW=12` is deliberately excluded after Fases 74-76 established its
protocol resonance.

## Preflight

- Source rows: `323872`
- Stationary rows: `302032`
- Eligible raw detections: `24946`
- Candidate groups: `76`
- New rules: `[62, 118, 131, 145]`
- Rule distribution: `{62: 19, 118: 19, 131: 19, 145: 19}`
- Period distribution: `{3: 76}`
- Minimum span: `11`
- Representative per `(rule, background, T_local)`: maximum span, then
  shortest IC word, then lexical word.
- Measurement horizon: natural period only.

## Result

Status: `EXTERNAL_NATURAL_PERIOD_WITNESS_NOT_FOUND`.

No stationary oscillator from the four new period-8-background rules reproduces the predeclared T15-like ANF gradient at its own natural period.

- Cases measured: `76`
- Reliable fits: `76`
- Comparable natural-period witnesses: `0`
- Witness rules: `[]`
- Packed/concrete discrepancies: `0`
- Highest observed R^2: `0.619571` (`rule118_bg00001111_T3`; required `>=0.95`)
- Closest observed slope: `-0.099273` (`rule62_bg01101111_T3`; delta `67.69%`, required `<=10%`)

## Case Table

| rule | background | T | IC | span | active | distances | natural-period fit |
| ---: | --- | ---: | --- | ---: | ---: | ---: | --- |
| 62 | `00000001` | 3 | `11000001` | 25 | 13 | 10 | slope=-0.066477, R^2=0.596666, reliable=true, comparable=false |
| 62 | `00000101` | 3 | `0001101` | 25 | 13 | 10 | slope=-0.056752, R^2=0.471633, reliable=true, comparable=false |
| 62 | `00000111` | 3 | `000100` | 21 | 11 | 7 | slope=0.000096, R^2=0.015406, reliable=true, comparable=false |
| 62 | `00001001` | 3 | `00101100` | 26 | 15 | 10 | slope=-0.076241, R^2=0.496054, reliable=true, comparable=false |
| 62 | `00001011` | 3 | `00111011` | 29 | 13 | 9 | slope=-0.068227, R^2=0.478303, reliable=true, comparable=false |
| 62 | `00001111` | 3 | `00000011` | 29 | 11 | 9 | slope=-0.080574, R^2=0.585545, reliable=true, comparable=false |
| 62 | `00010011` | 3 | `0001` | 21 | 10 | 8 | slope=-0.000130, R^2=0.031494, reliable=true, comparable=false |
| 62 | `00010111` | 3 | `11100110` | 24 | 10 | 8 | slope=-0.084585, R^2=0.575076, reliable=true, comparable=false |
| 62 | `00011001` | 3 | `00111100` | 27 | 12 | 8 | slope=-0.083342, R^2=0.535461, reliable=true, comparable=false |
| 62 | `00011011` | 3 | `00110010` | 21 | 11 | 7 | slope=0.000096, R^2=0.015406, reliable=true, comparable=false |
| 62 | `00011111` | 3 | `00110111` | 21 | 10 | 7 | slope=0.000076, R^2=0.009288, reliable=true, comparable=false |
| 62 | `00100111` | 3 | `000100` | 23 | 11 | 9 | slope=-0.034677, R^2=0.470907, reliable=true, comparable=false |
| 62 | `00101111` | 3 | `0010011` | 28 | 13 | 10 | slope=-0.067437, R^2=0.497679, reliable=true, comparable=false |
| 62 | `00111101` | 3 | `001010` | 24 | 17 | 11 | slope=-0.071202, R^2=0.456908, reliable=true, comparable=false |
| 62 | `00111111` | 3 | `011011` | 25 | 13 | 10 | slope=-0.066477, R^2=0.596666, reliable=true, comparable=false |
| 62 | `01010111` | 3 | `10001000` | 23 | 12 | 9 | slope=-0.030609, R^2=0.388889, reliable=true, comparable=false |
| 62 | `01011011` | 3 | `00110010` | 25 | 16 | 12 | slope=-0.090307, R^2=0.583602, reliable=true, comparable=false |
| 62 | `01011111` | 3 | `00110111` | 25 | 17 | 11 | slope=-0.092059, R^2=0.518600, reliable=true, comparable=false |
| 62 | `01101111` | 3 | `00010111` | 26 | 15 | 10 | slope=-0.099273, R^2=0.460266, reliable=true, comparable=false |
| 118 | `00000001` | 3 | `11011` | 25 | 13 | 10 | slope=-0.066477, R^2=0.596666, reliable=true, comparable=false |
| 118 | `00000101` | 3 | `10111` | 29 | 13 | 8 | slope=-0.071053, R^2=0.567581, reliable=true, comparable=false |
| 118 | `00000111` | 3 | `10011` | 25 | 12 | 9 | slope=-0.085221, R^2=0.449447, reliable=true, comparable=false |
| 118 | `00001001` | 3 | `100001` | 29 | 12 | 9 | slope=-0.071574, R^2=0.539240, reliable=true, comparable=false |
| 118 | `00001101` | 3 | `0000011` | 29 | 11 | 7 | slope=-0.068106, R^2=0.432644, reliable=true, comparable=false |
| 118 | `00001111` | 3 | `0110111` | 25 | 12 | 9 | slope=-0.074392, R^2=0.619571, reliable=true, comparable=false |
| 118 | `00010011` | 3 | `0010` | 25 | 16 | 12 | slope=-0.090307, R^2=0.583602, reliable=true, comparable=false |
| 118 | `00011001` | 3 | `00000110` | 30 | 13 | 9 | slope=-0.059800, R^2=0.330107, reliable=true, comparable=false |
| 118 | `00011011` | 3 | `00000110` | 26 | 11 | 8 | slope=-0.084900, R^2=0.551387, reliable=true, comparable=false |
| 118 | `00011101` | 3 | `00000111` | 21 | 10 | 7 | slope=-0.012481, R^2=0.220287, reliable=true, comparable=false |
| 118 | `00011111` | 3 | `00010111` | 29 | 12 | 10 | slope=-0.049629, R^2=0.450926, reliable=true, comparable=false |
| 118 | `00100111` | 3 | `001` | 25 | 16 | 12 | slope=-0.090307, R^2=0.583602, reliable=true, comparable=false |
| 118 | `00101111` | 3 | `0110111` | 25 | 13 | 10 | slope=-0.056752, R^2=0.471633, reliable=true, comparable=false |
| 118 | `00111101` | 3 | `001010` | 24 | 17 | 11 | slope=-0.084464, R^2=0.543344, reliable=true, comparable=false |
| 118 | `00111111` | 3 | `0000100` | 23 | 16 | 11 | slope=-0.057381, R^2=0.369491, reliable=true, comparable=false |
| 118 | `01010111` | 3 | `001000` | 25 | 16 | 12 | slope=-0.090307, R^2=0.583602, reliable=true, comparable=false |
| 118 | `01011011` | 3 | `00000110` | 27 | 13 | 10 | slope=-0.075026, R^2=0.602349, reliable=true, comparable=false |
| 118 | `01011111` | 3 | `01111111` | 29 | 13 | 10 | slope=-0.068027, R^2=0.515842, reliable=true, comparable=false |
| 118 | `01101111` | 3 | `0010111` | 25 | 13 | 10 | slope=-0.066477, R^2=0.596666, reliable=true, comparable=false |
| 131 | `00000011` | 3 | `10000110` | 23 | 15 | 11 | slope=-0.046429, R^2=0.294993, reliable=true, comparable=false |
| 131 | `00000101` | 3 | `0000001` | 29 | 14 | 11 | slope=-0.068269, R^2=0.458988, reliable=true, comparable=false |
| 131 | `00000111` | 3 | `0010111` | 29 | 12 | 10 | slope=-0.049766, R^2=0.266440, reliable=true, comparable=false |
| 131 | `00001001` | 3 | `00010001` | 25 | 13 | 10 | slope=-0.059892, R^2=0.461617, reliable=true, comparable=false |
| 131 | `00001011` | 3 | `00010010` | 25 | 13 | 10 | slope=-0.063122, R^2=0.513020, reliable=true, comparable=false |
| 131 | `00001101` | 3 | `00010010` | 25 | 13 | 10 | slope=-0.063122, R^2=0.513020, reliable=true, comparable=false |
| 131 | `00001111` | 3 | `00010010` | 25 | 12 | 9 | slope=-0.067046, R^2=0.475891, reliable=true, comparable=false |
| 131 | `00010101` | 3 | `11001` | 25 | 16 | 12 | slope=-0.076158, R^2=0.489308, reliable=true, comparable=false |
| 131 | `00011011` | 3 | `0110` | 25 | 16 | 12 | slope=-0.076158, R^2=0.489308, reliable=true, comparable=false |
| 131 | `00011101` | 3 | `0101000` | 28 | 12 | 10 | slope=-0.080245, R^2=0.303771, reliable=true, comparable=false |
| 131 | `00011111` | 3 | `001001` | 25 | 12 | 9 | slope=-0.056582, R^2=0.389949, reliable=true, comparable=false |
| 131 | `00100101` | 3 | `10000001` | 27 | 13 | 9 | slope=-0.080162, R^2=0.369152, reliable=true, comparable=false |
| 131 | `00100111` | 3 | `10000001` | 26 | 11 | 8 | slope=-0.060387, R^2=0.525197, reliable=true, comparable=false |
| 131 | `00110111` | 3 | `011` | 25 | 16 | 12 | slope=-0.076158, R^2=0.489308, reliable=true, comparable=false |
| 131 | `00111011` | 3 | `1110010` | 25 | 14 | 10 | slope=-0.053147, R^2=0.343446, reliable=true, comparable=false |
| 131 | `00111101` | 3 | `0101000` | 26 | 12 | 11 | slope=-0.080505, R^2=0.579501, reliable=true, comparable=false |
| 131 | `01011111` | 3 | `000100` | 29 | 13 | 8 | slope=-0.070900, R^2=0.521931, reliable=true, comparable=false |
| 131 | `01101111` | 3 | `00010` | 29 | 13 | 11 | slope=-0.076090, R^2=0.479841, reliable=true, comparable=false |
| 131 | `01111111` | 3 | `000100` | 25 | 13 | 10 | slope=-0.059892, R^2=0.461617, reliable=true, comparable=false |
| 145 | `00000011` | 3 | `01001` | 25 | 13 | 10 | slope=-0.059892, R^2=0.461617, reliable=true, comparable=false |
| 145 | `00000101` | 3 | `0010011` | 25 | 17 | 11 | slope=-0.077487, R^2=0.435148, reliable=true, comparable=false |
| 145 | `00000111` | 3 | `0010011` | 21 | 10 | 7 | slope=0.000133, R^2=0.009288, reliable=true, comparable=false |
| 145 | `00001001` | 3 | `00010011` | 26 | 12 | 8 | slope=-0.049129, R^2=0.271282, reliable=true, comparable=false |
| 145 | `00001011` | 3 | `00101010` | 28 | 14 | 10 | slope=-0.062148, R^2=0.418395, reliable=true, comparable=false |
| 145 | `00001101` | 3 | `00101010` | 28 | 14 | 10 | slope=-0.062148, R^2=0.418395, reliable=true, comparable=false |
| 145 | `00001111` | 3 | `00111111` | 29 | 11 | 9 | slope=-0.095283, R^2=0.569900, reliable=true, comparable=false |
| 145 | `00010101` | 3 | `0011000` | 23 | 11 | 9 | slope=-0.031675, R^2=0.239734, reliable=true, comparable=false |
| 145 | `00010111` | 3 | `10011000` | 24 | 10 | 8 | slope=-0.046975, R^2=0.587777, reliable=true, comparable=false |
| 145 | `00011011` | 3 | `00101` | 23 | 14 | 10 | slope=-0.025952, R^2=0.174416, reliable=true, comparable=false |
| 145 | `00011111` | 3 | `10111` | 21 | 11 | 7 | slope=0.000169, R^2=0.015406, reliable=true, comparable=false |
| 145 | `00100101` | 3 | `0000011` | 25 | 16 | 12 | slope=-0.076158, R^2=0.489308, reliable=true, comparable=false |
| 145 | `00100111` | 3 | `0000011` | 21 | 11 | 7 | slope=0.000169, R^2=0.015406, reliable=true, comparable=false |
| 145 | `00101111` | 3 | `00100011` | 29 | 13 | 9 | slope=-0.041898, R^2=0.355839, reliable=true, comparable=false |
| 145 | `00110111` | 3 | `1` | 21 | 11 | 9 | slope=-0.000281, R^2=0.051779, reliable=true, comparable=false |
| 145 | `00111011` | 3 | `11110` | 25 | 16 | 12 | slope=-0.076158, R^2=0.489308, reliable=true, comparable=false |
| 145 | `01011111` | 3 | `01000000` | 25 | 13 | 10 | slope=-0.063122, R^2=0.513020, reliable=true, comparable=false |
| 145 | `01101111` | 3 | `0000001` | 26 | 13 | 10 | slope=-0.081448, R^2=0.503017, reliable=true, comparable=false |
| 145 | `01111111` | 3 | `0001000` | 25 | 13 | 10 | slope=-0.059892, R^2=0.461617, reliable=true, comparable=false |

## Methodological Limits

- This is an external-background census over four newly observed rules,
  not an exhaustive new sweep of every possible background and IC length.
- All selected external candidates have natural period 3. The phase can
  detect a natural-period witness, but it does not add external positive
  coverage at periods 8, 10, or 12.
- The T15 comparison thresholds are inherited unchanged from Fase 55.
  No threshold is fitted to these results.
- A negative result supports rule_109 specificity within the two completed
  background catalogs; it is not a universal impossibility theorem.
