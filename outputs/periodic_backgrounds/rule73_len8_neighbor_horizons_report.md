# Fase 79: rule_73 len-8 Neighboring-Horizon Robustness

## Question

Do the nine natural-period `rule_73/T=12` witnesses from Fase 78 retain
the unchanged T15-like ANF-gradient signature when measured away from the
exact `T_WINDOW=12` point?

All 18 `rule_73/T=12` holdout cases are evaluated. The nine Fase 78
witnesses form the primary cohort; the other nine cases are controls.
Horizons `10`, `14`, and `16` were fixed before measurement. Horizon `12`
is reused directly from Fase 78. The Fase 55 `comparable_to_t15()`
predicate is unchanged.

## Result

Status: `RULE73_LEN8_NEIGHBOR_HORIZON_PARTIAL`.

3 of the nine Fase 78 witnesses remain comparable at one or more predeclared neighboring horizons.

- T=12 cases: `18`
- Baseline Fase 78 witnesses: `9`
- Baseline witnesses surviving at any neighbor: `3`
- Baseline witnesses surviving by horizon: `{'10': 1, '14': 2, '16': 0}`
- Surviving witness labels: `[{'label': 'rule73_bg00101101_T12', 'horizons': [14]}, {'label': 'rule73_bg00110101_T12', 'horizons': [10]}, {'label': 'rule73_bg00111111_T12', 'horizons': [14]}]`
- Baseline-negative controls becoming comparable at neighbors: `0`
- Control positives by horizon: `{'10': 0, '14': 0, '16': 0}`
- Packed/concrete discrepancies: `0`

## Case Table

| cohort | background | IC | h10 slope/R2/cmp | h12 | h14 | h16 | neighbor survival |
| --- | --- | --- | --- | --- | --- | --- | --- |
| baseline_control | `00000011` | `00101` | -0.240709/0.853871/false | -0.309103/0.999107/false | -0.201357/0.913215/false | -0.113402/0.616054/false | [] |
| baseline_witness | `00001001` | `00010111` | -0.267433/0.877120/false | -0.311180/0.975890/true | -0.358049/0.623171/false | -0.194748/0.859535/false | [] |
| baseline_control | `00001011` | `00001000` | -0.153294/0.452130/false | -0.253532/0.640376/false | -0.164269/0.275653/false | -0.091700/0.205521/false | [] |
| baseline_witness | `00001101` | `00010011` | -0.291485/0.897442/false | -0.305307/0.998962/true | -0.244907/0.955242/false | -0.151481/0.815416/false | [] |
| baseline_witness | `00001111` | `00000001` | -0.286643/0.945876/false | -0.300277/0.967589/true | -0.276866/0.938084/false | -0.169267/0.866469/false | [] |
| baseline_control | `00010011` | `0101` | -0.228555/0.905219/false | -0.258267/0.903180/false | -0.220353/0.774489/false | -0.084900/0.264273/false | [] |
| baseline_witness | `00011001` | `1001100` | -0.251894/0.950522/false | -0.291364/0.999252/true | -0.228381/0.666641/false | -0.105207/0.344790/false | [] |
| baseline_witness | `00011011` | `1010000` | -0.244734/0.952794/false | -0.299605/0.998701/true | -0.202166/0.867990/false | -0.051921/0.353903/false | [] |
| baseline_control | `00101011` | `011` | -0.202919/0.891022/false | -0.299233/0.944041/false | -0.169718/0.578686/false | -0.148264/0.639791/false | [] |
| baseline_witness | `00101101` | `01110001` | -0.230684/0.818432/false | -0.292005/0.964906/true | -0.286499/0.958552/true | -0.165711/0.772137/false | [14] |
| baseline_witness | `00101111` | `01000101` | -0.260637/0.945971/false | -0.307370/0.963517/true | -0.294286/0.803801/false | -0.201609/0.866791/false | [] |
| baseline_witness | `00110101` | `10001110` | -0.278857/0.980284/true | -0.322055/0.971373/true | -0.276689/0.944300/false | -0.177964/0.792414/false | [10] |
| baseline_control | `00110111` | `111` | -0.198159/0.759016/false | -0.316229/0.928727/false | -0.112231/0.295342/false | -0.053374/0.311379/false | [] |
| baseline_control | `00111011` | `011` | -0.210396/0.179288/false | -0.288555/0.883918/false | -0.232211/0.878409/false | -0.113035/0.473420/false | [] |
| baseline_control | `00111101` | `101` | -0.210396/0.179288/false | -0.288555/0.883918/false | -0.232211/0.878409/false | -0.113035/0.473420/false | [] |
| baseline_witness | `00111111` | `00011101` | -0.266009/0.777992/false | -0.278618/0.965251/true | -0.297369/0.959874/true | -0.188153/0.667362/false | [14] |
| baseline_control | `01011011` | `101111` | -0.244232/0.609428/false | -0.346384/0.940009/false | -0.249571/0.301511/false | -0.166970/0.287715/false | [] |
| baseline_control | `01101111` | `1` | -0.198159/0.759016/false | -0.316229/0.928727/false | -0.112231/0.295342/false | -0.053374/0.311379/false | [] |

## Interpretation

Three of the nine Fase 78 witnesses survive outside the exact 12-step
evaluation point: one at horizon 10 and two at horizon 14. No control
case becomes comparable at any neighboring horizon. The Fase 78 result
is therefore not a pure point resonance at `T_WINDOW=12`.

The robustness is nevertheless partial and background-conditioned.
Six baseline witnesses do not survive, and no witness remains comparable
at horizon 16. This supports a finite neighboring-horizon band for a
subset of backgrounds, not horizon invariance or a universal law.

Control cases are included to detect a second failure mode: neighboring
horizons may create new comparable fits among cases that were negative at
their natural period. Such cases are reported separately rather than
counted as witness robustness.

## Methodological Limits

- The audit varies measurement horizon, not the physical oscillator or IC.
- It covers one rule and primitive length-8 backgrounds only.
- Survival at a neighboring horizon is evidence of protocol robustness,
  not a universal causal law.
- The thresholds are inherited unchanged from Fase 55.
