# Fase 78: rule_73 Primitive-Length-8 Natural-Period Holdout

## Question

Does a genuine non-rule_109 witness appear when the ANF-gradient test is
applied to previously unmeasured primitive length-8 `rule_73` oscillators
in the same natural-period range as the known positives (`T=8,10,12`)?

The holdout is selected from the completed 3,855,360-run physical sweep.
Selection is fixed before ANF measurement. The unchanged Fase 55
`comparable_to_t15()` predicate is evaluated at each oscillator's natural
period only. No common `T_WINDOW=12` measurement is introduced for T=8/10.

## Preflight

- Source rows: `323872`
- Eligible raw detections: `729`
- Candidate groups: `25`
- Distinct primitive length-8 backgrounds: `18`
- Period distribution: `{8: 1, 10: 6, 12: 18}`
- Minimum span: `11`
- Representative per `(rule, background, T_local)`: maximum span, then
  shortest IC word, then lexical word.
- Measurement horizon: natural period only.

## Result

Status: `RULE73_LEN8_NATURAL_WITNESS_FOUND`.

At least one primitive length-8 rule_73 oscillator reproduces the predeclared T15-like ANF gradient at its natural period.

- Cases measured: `25`
- Reliable fits: `24`
- Comparable natural-period witnesses: `9`
- Witness period distribution: `{12: 9}`
- Witness backgrounds: `['00001001', '00001101', '00001111', '00011001', '00011011', '00101101', '00101111', '00110101', '00111111']`
- Packed/concrete discrepancies: `0`
- Highest observed R^2: `0.999252` (`rule73_bg00011001_T12`; required `>=0.95`)
- Closest observed slope: `-0.307370` (`rule73_bg00101111_T12`; delta `0.03%`, required `<=10%`)

## Case Table

| background | T | IC | span | active | distances | natural-period fit |
| --- | ---: | --- | ---: | ---: | ---: | --- |
| `00001011` | 8 | `00000001` | 12 | 8 | 6 | slope=-0.046504, R^2=0.444247, reliable=true, comparable=false |
| `00001011` | 10 | `00001110` | 12 | 7 | 6 | slope=-0.203172, R^2=0.891469, reliable=true, comparable=false |
| `00001101` | 10 | `00100001` | 17 | 10 | 7 | slope=-0.248562, R^2=0.938148, reliable=true, comparable=false |
| `00010011` | 10 | `10001` | 12 | 6 | 4 | slope=-0.248233, R^2=0.924703, reliable=true, comparable=false |
| `00011001` | 10 | `1000110` | 17 | 7 | 6 | slope=-0.221030, R^2=0.936838, reliable=true, comparable=false |
| `00011011` | 10 | `101111` | 12 | 7 | 4 | slope=-0.166118, R^2=0.627356, reliable=true, comparable=false |
| `01011011` | 10 | `1010000` | 12 | 7 | 6 | slope=-0.203172, R^2=0.891469, reliable=true, comparable=false |
| `00000011` | 12 | `00101` | 12 | 3 | 2 | slope=-0.309103, R^2=0.999107, reliable=false, comparable=false |
| `00001001` | 12 | `00010111` | 20 | 9 | 6 | slope=-0.311180, R^2=0.975890, reliable=true, comparable=true |
| `00001011` | 12 | `00001000` | 12 | 4 | 3 | slope=-0.253532, R^2=0.640376, reliable=true, comparable=false |
| `00001101` | 12 | `00010011` | 17 | 8 | 7 | slope=-0.305307, R^2=0.998962, reliable=true, comparable=true |
| `00001111` | 12 | `00000001` | 20 | 13 | 8 | slope=-0.300277, R^2=0.967589, reliable=true, comparable=true |
| `00010011` | 12 | `0101` | 12 | 5 | 4 | slope=-0.258267, R^2=0.903180, reliable=true, comparable=false |
| `00011001` | 12 | `1001100` | 17 | 9 | 7 | slope=-0.291364, R^2=0.999252, reliable=true, comparable=true |
| `00011011` | 12 | `1010000` | 12 | 8 | 6 | slope=-0.299605, R^2=0.998701, reliable=true, comparable=true |
| `00101011` | 12 | `011` | 12 | 7 | 4 | slope=-0.299233, R^2=0.944041, reliable=true, comparable=false |
| `00101101` | 12 | `01110001` | 20 | 10 | 9 | slope=-0.292005, R^2=0.964906, reliable=true, comparable=true |
| `00101111` | 12 | `01000101` | 20 | 13 | 9 | slope=-0.307370, R^2=0.963517, reliable=true, comparable=true |
| `00110101` | 12 | `10001110` | 20 | 10 | 9 | slope=-0.322055, R^2=0.971373, reliable=true, comparable=true |
| `00110111` | 12 | `111` | 12 | 5 | 4 | slope=-0.316229, R^2=0.928727, reliable=true, comparable=false |
| `00111011` | 12 | `011` | 12 | 5 | 3 | slope=-0.288555, R^2=0.883918, reliable=true, comparable=false |
| `00111101` | 12 | `101` | 12 | 5 | 3 | slope=-0.288555, R^2=0.883918, reliable=true, comparable=false |
| `00111111` | 12 | `00011101` | 20 | 12 | 10 | slope=-0.278618, R^2=0.965251, reliable=true, comparable=true |
| `01011011` | 12 | `101111` | 12 | 7 | 5 | slope=-0.346384, R^2=0.940009, reliable=true, comparable=false |
| `01101111` | 12 | `1` | 12 | 5 | 4 | slope=-0.316229, R^2=0.928727, reliable=true, comparable=false |

## Interpretation

The holdout contains nine natural-period witnesses, all at `T=12`,
across nine distinct primitive length-8 backgrounds. No witness appears
at `T=8` or `T=10`. The result therefore generalizes the observed ANF
gradient beyond `rule_109`, but only in a period-conditioned form.

`rule_73` is not center-mediated under the Fase 57 definition. These
external-background witnesses show that center mediation is not necessary
once the analysis is extended beyond the original Fase 55 catalog. This
does not contradict the earlier catalog-scoped verdict; it supplies the
external positive that verdict explicitly lacked.

## Methodological Limits

- This is an external-background holdout, not an external-rule holdout:
  `rule_73` was already present in Fase 55, but none of these primitive
  length-8 backgrounds was used there.
- The holdout covers the relevant T=8/10/12 range but only one non-rule_109
  rule. It cannot establish a universal ECA generalization result.
- All nine witnesses occur at `T_local=12`. Their natural period therefore
  coincides with the `T_WINDOW=12` protocol resonance identified in Fase 76.
  They satisfy the predeclared natural-period criterion, but robustness at
  neighboring horizons remains untested.
- The thresholds are inherited unchanged from Fase 55 and are not fitted
  to these cases.
- A positive case would be the first observed non-rule_109 natural-period
  witness. A negative result would strengthen, but not prove universally,
  the observed rule_109 specificity.
