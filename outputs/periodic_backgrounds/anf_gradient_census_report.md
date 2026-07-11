# Fase 55: Non-T15 ANF Gradient Census

## Question

Across the periodic-background oscillator catalog, how many non-T15 cases
with wide support reproduce the T15-like ANF gradient at their natural
period, and how many only do so at the common 12-step horizon?

The census excludes `T_local=2` compact baselines and `T_local=15` cases,
keeps groups with `span >= 11`, and evaluates one IC per
`(rule, background, T_local)` group. Already-tested groups use their exact
previous ICs as consistency baselines; new groups use max span, then
shortest word as the tie-breaker.

Reference: T15 Fase 45 slope `-0.307283`, R^2 `0.998197`.

## Preflight

- Candidate groups: 66
- Already-tested groups: 7
- Period distribution: `{3: 18, 4: 8, 6: 22, 8: 6, 10: 8, 12: 4}`
- Rule distribution: `{54: 4, 73: 17, 94: 12, 109: 17, 133: 12, 147: 4}`

## Summary

Status: `NEW_NATURAL_PERIOD_WITNESS_FOUND`.

At least one previously untested non-T15 oscillator reproduces a T15-like gradient at its natural period.

All categories: `{'HORIZON_ACCEPTABLE': 3, 'HORIZON_ARTIFACT': 20, 'INSUFFICIENT_SUPPORT': 3, 'NATURAL_PERIOD_STRONG': 2, 'NEGATIVE': 38}`

Previously untested categories: `{'HORIZON_ACCEPTABLE': 2, 'HORIZON_ARTIFACT': 18, 'INSUFFICIENT_SUPPORT': 3, 'NATURAL_PERIOD_STRONG': 2, 'NEGATIVE': 34}`

## Case Table

| case | tested | category | natural-period fit | common-horizon fit |
| --- | --- | --- | --- | --- |
| `rule_54/bg=0010/T=4/word=1000001` | no | `INSUFFICIENT_SUPPORT` | slope=-0.002354, R^2=1.000000, delta=99.23%, reliable=no, comparable=no | slope=-0.314622, R^2=1.000000, delta=2.39%, reliable=no, comparable=no |
| `rule_54/bg=0100/T=4/word=10000001` | no | `NEGATIVE` | slope=-0.001284, R^2=0.818182, delta=99.58%, reliable=yes, comparable=no | slope=-0.257629, R^2=0.669022, delta=16.16%, reliable=yes, comparable=no |
| `rule_54/bg=1011/T=4/word=00000001` | no | `HORIZON_ARTIFACT` | slope=0.000706, R^2=0.600000, delta=99.77%, reliable=yes, comparable=no | slope=-0.310719, R^2=0.999935, delta=1.12%, reliable=yes, comparable=yes |
| `rule_54/bg=1101/T=4/word=0001000` | no | `HORIZON_ARTIFACT` | slope=0.000706, R^2=0.600000, delta=99.77%, reliable=yes, comparable=no | slope=-0.310719, R^2=0.999935, delta=1.12%, reliable=yes, comparable=yes |
| `rule_73/bg=0010/T=6/word=1100111` | yes | `HORIZON_ARTIFACT` | slope=-0.000027, R^2=0.604938, delta=99.99%, reliable=yes, comparable=no | slope=-0.320463, R^2=0.999687, delta=4.29%, reliable=yes, comparable=yes |
| `rule_73/bg=0010/T=10/word=1110111` | yes | `NEGATIVE` | slope=-0.203651, R^2=0.880488, delta=33.73%, reliable=yes, comparable=no | slope=-0.322466, R^2=1.000000, delta=4.94%, reliable=no, comparable=no |
| `rule_73/bg=0011/T=3/word=10000000` | no | `HORIZON_ARTIFACT` | slope=0.001009, R^2=0.428571, delta=99.67%, reliable=yes, comparable=no | slope=-0.307493, R^2=0.952909, delta=0.07%, reliable=yes, comparable=yes |
| `rule_73/bg=0011/T=6/word=10000100` | no | `HORIZON_ARTIFACT` | slope=0.000009, R^2=0.044118, delta=100.00%, reliable=yes, comparable=no | slope=-0.315036, R^2=0.998642, delta=2.52%, reliable=yes, comparable=yes |
| `rule_73/bg=0011/T=8/word=10011100` | no | `NEGATIVE` | slope=-0.093791, R^2=0.653974, delta=69.48%, reliable=yes, comparable=no | slope=-0.294933, R^2=0.929362, delta=4.02%, reliable=yes, comparable=no |
| `rule_73/bg=0011/T=10/word=10111110` | no | `NEGATIVE` | slope=-0.196632, R^2=0.911425, delta=36.01%, reliable=yes, comparable=no | slope=-0.293199, R^2=0.910209, delta=4.58%, reliable=yes, comparable=no |
| `rule_73/bg=0011/T=12/word=10001010` | yes | `NEGATIVE` | slope=-0.296180, R^2=0.877281, delta=3.61%, reliable=yes, comparable=no | slope=-0.296180, R^2=0.877281, delta=3.61%, reliable=yes, comparable=no |
| `rule_73/bg=0100/T=6/word=11001110` | no | `HORIZON_ARTIFACT` | slope=-0.000027, R^2=0.604938, delta=99.99%, reliable=yes, comparable=no | slope=-0.320463, R^2=0.999687, delta=4.29%, reliable=yes, comparable=yes |
| `rule_73/bg=0100/T=10/word=11101110` | no | `NEGATIVE` | slope=-0.203651, R^2=0.880488, delta=33.73%, reliable=yes, comparable=no | slope=-0.322466, R^2=1.000000, delta=4.94%, reliable=no, comparable=no |
| `rule_73/bg=1001/T=3/word=100001` | no | `INSUFFICIENT_SUPPORT` | slope=0.000000, R^2=1.000000, delta=100.00%, reliable=no, comparable=no | slope=-0.297793, R^2=0.498975, delta=3.09%, reliable=no, comparable=no |
| `rule_73/bg=1001/T=6/word=1001000` | no | `HORIZON_ARTIFACT` | slope=-0.000029, R^2=0.272727, delta=99.99%, reliable=yes, comparable=no | slope=-0.305386, R^2=0.998101, delta=0.62%, reliable=yes, comparable=yes |
| `rule_73/bg=1001/T=8/word=1001110` | no | `NEGATIVE` | slope=-0.093791, R^2=0.653974, delta=69.48%, reliable=yes, comparable=no | slope=-0.294933, R^2=0.929362, delta=4.02%, reliable=yes, comparable=no |
| `rule_73/bg=1100/T=3/word=0000001` | no | `HORIZON_ARTIFACT` | slope=0.000250, R^2=0.017699, delta=99.92%, reliable=yes, comparable=no | slope=-0.303913, R^2=0.998717, delta=1.10%, reliable=yes, comparable=yes |
| `rule_73/bg=1100/T=6/word=0001001` | no | `HORIZON_ARTIFACT` | slope=-0.000029, R^2=0.272727, delta=99.99%, reliable=yes, comparable=no | slope=-0.305386, R^2=0.998101, delta=0.62%, reliable=yes, comparable=yes |
| `rule_73/bg=1100/T=8/word=0011111` | no | `NEGATIVE` | slope=-0.083475, R^2=0.457321, delta=72.83%, reliable=yes, comparable=no | slope=-0.278180, R^2=0.760150, delta=9.47%, reliable=yes, comparable=no |
| `rule_73/bg=1100/T=10/word=01100011` | no | `NEGATIVE` | slope=-0.190548, R^2=0.789733, delta=37.99%, reliable=yes, comparable=no | slope=-0.311475, R^2=0.921729, delta=1.36%, reliable=yes, comparable=no |
| `rule_73/bg=1100/T=12/word=00000011` | no | `NEGATIVE` | slope=-0.312019, R^2=0.938004, delta=1.54%, reliable=yes, comparable=no | slope=-0.312019, R^2=0.938004, delta=1.54%, reliable=yes, comparable=no |
| `rule_94/bg=0001/T=3/word=0110100` | no | `NEGATIVE` | slope=0.000234, R^2=0.007353, delta=99.92%, reliable=yes, comparable=no | slope=-0.304510, R^2=0.900856, delta=0.90%, reliable=yes, comparable=no |
| `rule_94/bg=0001/T=6/word=0100010` | no | `NEGATIVE` | slope=0.000000, R^2=0.000000, delta=100.00%, reliable=yes, comparable=no | slope=-0.295750, R^2=0.897666, delta=3.75%, reliable=yes, comparable=no |
| `rule_94/bg=0010/T=3/word=1000101` | yes | `NEGATIVE` | slope=0.000523, R^2=0.049180, delta=99.83%, reliable=yes, comparable=no | slope=-0.341994, R^2=0.955626, delta=11.30%, reliable=yes, comparable=no |
| `rule_94/bg=0010/T=6/word=100010` | no | `NEGATIVE` | slope=0.000000, R^2=0.000000, delta=100.00%, reliable=yes, comparable=no | slope=-0.295750, R^2=0.897666, delta=3.75%, reliable=yes, comparable=no |
| `rule_94/bg=0100/T=3/word=10001001` | no | `NEGATIVE` | slope=0.000523, R^2=0.049180, delta=99.83%, reliable=yes, comparable=no | slope=-0.341994, R^2=0.955626, delta=11.30%, reliable=yes, comparable=no |
| `rule_94/bg=0100/T=6/word=010001` | no | `NEGATIVE` | slope=0.000000, R^2=0.000000, delta=100.00%, reliable=yes, comparable=no | slope=-0.295663, R^2=0.896744, delta=3.78%, reliable=yes, comparable=no |
| `rule_94/bg=0111/T=3/word=10000010` | no | `HORIZON_ARTIFACT` | slope=-0.000613, R^2=0.076923, delta=99.80%, reliable=yes, comparable=no | slope=-0.295851, R^2=0.999961, delta=3.72%, reliable=yes, comparable=yes |
| `rule_94/bg=0111/T=6/word=10101000` | no | `HORIZON_ARTIFACT` | slope=-0.000014, R^2=0.250000, delta=100.00%, reliable=yes, comparable=no | slope=-0.295845, R^2=0.999958, delta=3.72%, reliable=yes, comparable=yes |
| `rule_94/bg=1000/T=3/word=00011010` | no | `HORIZON_ARTIFACT` | slope=-0.000321, R^2=0.020161, delta=99.90%, reliable=yes, comparable=no | slope=-0.295877, R^2=0.999967, delta=3.71%, reliable=yes, comparable=yes |
| `rule_94/bg=1000/T=6/word=00010001` | no | `NEGATIVE` | slope=0.000003, R^2=0.006623, delta=100.00%, reliable=yes, comparable=no | slope=-0.285650, R^2=0.903308, delta=7.04%, reliable=yes, comparable=no |
| `rule_94/bg=1110/T=3/word=00010111` | no | `HORIZON_ARTIFACT` | slope=-0.000448, R^2=0.056180, delta=99.85%, reliable=yes, comparable=no | slope=-0.295697, R^2=0.999989, delta=3.77%, reliable=yes, comparable=yes |
| `rule_94/bg=1110/T=6/word=00010101` | no | `HORIZON_ARTIFACT` | slope=-0.000014, R^2=0.250000, delta=100.00%, reliable=yes, comparable=no | slope=-0.295845, R^2=0.999958, delta=3.72%, reliable=yes, comparable=yes |
| `rule_109/bg=0011/T=3/word=0001100` | no | `NEGATIVE` | slope=-0.000947, R^2=0.428571, delta=99.69%, reliable=yes, comparable=no | slope=-0.302580, R^2=0.933294, delta=1.53%, reliable=yes, comparable=no |
| `rule_109/bg=0011/T=6/word=1100100` | no | `NEGATIVE` | slope=0.000005, R^2=0.029963, delta=100.00%, reliable=yes, comparable=no | slope=-0.292946, R^2=0.930073, delta=4.67%, reliable=yes, comparable=no |
| `rule_109/bg=0011/T=8/word=1000010` | no | `NEGATIVE` | slope=-0.100601, R^2=0.633598, delta=67.26%, reliable=yes, comparable=no | slope=-0.310312, R^2=0.924473, delta=0.99%, reliable=yes, comparable=no |
| `rule_109/bg=0011/T=10/word=10000010` | no | `NEGATIVE` | slope=-0.203273, R^2=0.913158, delta=33.85%, reliable=yes, comparable=no | slope=-0.276202, R^2=0.899808, delta=10.11%, reliable=yes, comparable=no |
| `rule_109/bg=0011/T=12/word=10010100` | no | `NATURAL_PERIOD_STRONG` | slope=-0.298274, R^2=0.998341, delta=2.93%, reliable=yes, comparable=yes | slope=-0.298274, R^2=0.998341, delta=2.93%, reliable=yes, comparable=yes |
| `rule_109/bg=0110/T=3/word=001100` | no | `NEGATIVE` | slope=-0.000947, R^2=0.428571, delta=99.69%, reliable=yes, comparable=no | slope=-0.302580, R^2=0.933294, delta=1.53%, reliable=yes, comparable=no |
| `rule_109/bg=0110/T=6/word=0010011` | no | `NEGATIVE` | slope=0.000005, R^2=0.029963, delta=100.00%, reliable=yes, comparable=no | slope=-0.313891, R^2=0.941622, delta=2.15%, reliable=yes, comparable=no |
| `rule_109/bg=0110/T=8/word=0000011` | no | `HORIZON_ACCEPTABLE` | slope=-0.106802, R^2=0.617294, delta=65.24%, reliable=yes, comparable=no | slope=-0.298928, R^2=0.998276, delta=2.72%, reliable=yes, comparable=yes |
| `rule_109/bg=1011/T=6/word=00001001` | yes | `HORIZON_ARTIFACT` | slope=0.000026, R^2=0.604938, delta=99.99%, reliable=yes, comparable=no | slope=-0.303174, R^2=0.999487, delta=1.34%, reliable=yes, comparable=yes |
| `rule_109/bg=1011/T=10/word=00000001` | yes | `HORIZON_ACCEPTABLE` | slope=-0.196127, R^2=0.922575, delta=36.17%, reliable=yes, comparable=no | slope=-0.307674, R^2=0.999349, delta=0.13%, reliable=yes, comparable=yes |
| `rule_109/bg=1100/T=3/word=00001110` | no | `NEGATIVE` | slope=-0.000833, R^2=0.219731, delta=99.73%, reliable=yes, comparable=no | slope=-0.311934, R^2=0.924475, delta=1.51%, reliable=yes, comparable=no |
| `rule_109/bg=1100/T=6/word=00100110` | no | `NEGATIVE` | slope=0.000005, R^2=0.029963, delta=100.00%, reliable=yes, comparable=no | slope=-0.313891, R^2=0.941622, delta=2.15%, reliable=yes, comparable=no |
| `rule_109/bg=1100/T=8/word=00000110` | no | `HORIZON_ACCEPTABLE` | slope=-0.106802, R^2=0.617294, delta=65.24%, reliable=yes, comparable=no | slope=-0.298928, R^2=0.998276, delta=2.72%, reliable=yes, comparable=yes |
| `rule_109/bg=1100/T=10/word=00111001` | no | `NEGATIVE` | slope=-0.196256, R^2=0.786691, delta=36.13%, reliable=yes, comparable=no | slope=-0.285905, R^2=0.896516, delta=6.96%, reliable=yes, comparable=no |
| `rule_109/bg=1100/T=12/word=00101001` | no | `NATURAL_PERIOD_STRONG` | slope=-0.298274, R^2=0.998341, delta=2.93%, reliable=yes, comparable=yes | slope=-0.298274, R^2=0.998341, delta=2.93%, reliable=yes, comparable=yes |
| `rule_109/bg=1101/T=6/word=0000100` | no | `HORIZON_ARTIFACT` | slope=0.000026, R^2=0.604938, delta=99.99%, reliable=yes, comparable=no | slope=-0.303174, R^2=0.999487, delta=1.34%, reliable=yes, comparable=yes |
| `rule_109/bg=1101/T=10/word=0001000` | yes | `NEGATIVE` | slope=-0.209698, R^2=0.880488, delta=31.76%, reliable=yes, comparable=no | slope=-0.300746, R^2=1.000000, delta=2.13%, reliable=no, comparable=no |
| `rule_133/bg=0001/T=3/word=10011100` | no | `NEGATIVE` | slope=0.000211, R^2=0.007353, delta=99.93%, reliable=yes, comparable=no | slope=-0.297780, R^2=0.902744, delta=3.09%, reliable=yes, comparable=no |
| `rule_133/bg=0001/T=6/word=10001000` | no | `NEGATIVE` | slope=0.000004, R^2=0.006623, delta=100.00%, reliable=yes, comparable=no | slope=-0.297342, R^2=0.911641, delta=3.24%, reliable=yes, comparable=no |
| `rule_133/bg=0111/T=3/word=10000011` | no | `HORIZON_ARTIFACT` | slope=-0.000552, R^2=0.076923, delta=99.82%, reliable=yes, comparable=no | slope=-0.289461, R^2=0.999224, delta=5.80%, reliable=yes, comparable=yes |
| `rule_133/bg=0111/T=6/word=10010011` | no | `NEGATIVE` | slope=0.000000, R^2=0.000000, delta=100.00%, reliable=yes, comparable=no | slope=-0.281419, R^2=0.895001, delta=8.42%, reliable=yes, comparable=no |
| `rule_133/bg=1000/T=3/word=00010011` | no | `HORIZON_ARTIFACT` | slope=-0.000289, R^2=0.020161, delta=99.91%, reliable=yes, comparable=no | slope=-0.289489, R^2=0.999305, delta=5.79%, reliable=yes, comparable=yes |
| `rule_133/bg=1000/T=6/word=00010001` | no | `NEGATIVE` | slope=0.000004, R^2=0.006623, delta=100.00%, reliable=yes, comparable=no | slope=-0.272430, R^2=0.901177, delta=11.34%, reliable=yes, comparable=no |
| `rule_133/bg=1011/T=3/word=00001001` | no | `NEGATIVE` | slope=0.000471, R^2=0.049180, delta=99.85%, reliable=yes, comparable=no | slope=-0.256035, R^2=0.914123, delta=16.68%, reliable=yes, comparable=no |
| `rule_133/bg=1011/T=6/word=100100` | no | `NEGATIVE` | slope=0.000000, R^2=0.000000, delta=100.00%, reliable=yes, comparable=no | slope=-0.281419, R^2=0.895001, delta=8.42%, reliable=yes, comparable=no |
| `rule_133/bg=1101/T=3/word=0000100` | no | `NEGATIVE` | slope=0.000471, R^2=0.049180, delta=99.85%, reliable=yes, comparable=no | slope=-0.256035, R^2=0.914123, delta=16.68%, reliable=yes, comparable=no |
| `rule_133/bg=1101/T=6/word=001001` | no | `NEGATIVE` | slope=0.000000, R^2=0.000000, delta=100.00%, reliable=yes, comparable=no | slope=-0.289114, R^2=0.899975, delta=5.91%, reliable=yes, comparable=no |
| `rule_133/bg=1110/T=3/word=0011001` | no | `NEGATIVE` | slope=0.000211, R^2=0.007353, delta=99.93%, reliable=yes, comparable=no | slope=-0.272166, R^2=0.884352, delta=11.43%, reliable=yes, comparable=no |
| `rule_133/bg=1110/T=6/word=1001001` | no | `NEGATIVE` | slope=0.000000, R^2=0.000000, delta=100.00%, reliable=yes, comparable=no | slope=-0.289114, R^2=0.899975, delta=5.91%, reliable=yes, comparable=no |
| `rule_147/bg=0010/T=4/word=1000001` | no | `HORIZON_ARTIFACT` | slope=0.001350, R^2=0.600000, delta=99.56%, reliable=yes, comparable=no | slope=-0.296740, R^2=0.999969, delta=3.43%, reliable=yes, comparable=yes |
| `rule_147/bg=0100/T=4/word=10000010` | no | `HORIZON_ARTIFACT` | slope=0.001350, R^2=0.600000, delta=99.56%, reliable=yes, comparable=no | slope=-0.296740, R^2=0.999969, delta=3.43%, reliable=yes, comparable=yes |
| `rule_147/bg=1011/T=4/word=01000010` | no | `NEGATIVE` | slope=-0.002455, R^2=0.818182, delta=99.20%, reliable=yes, comparable=no | slope=-0.245129, R^2=0.652251, delta=20.23%, reliable=yes, comparable=no |
| `rule_147/bg=1101/T=4/word=0100010` | no | `INSUFFICIENT_SUPPORT` | slope=-0.004501, R^2=1.000000, delta=98.54%, reliable=no, comparable=no | slope=-0.289124, R^2=1.000000, delta=5.91%, reliable=no, comparable=no |

## Category Definitions

- `NATURAL_PERIOD_STRONG`: reliable and comparable at `T_WINDOW=T_local`.
- `HORIZON_ACCEPTABLE`: reliable and comparable at `T_WINDOW=12` with `T_local >= 8`.
- `HORIZON_ARTIFACT`: comparable at `T_WINDOW=12` with `T_local <= 6`.
- `INSUFFICIENT_SUPPORT`: natural-period fit is not reliable.
- `NEGATIVE`: reliable natural-period fit but not comparable at either threshold.
