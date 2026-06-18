# Primitive Period-8 Background Oscillator Sweep

## Protocol

- Rules: all 256 ECA rules.
- Backgrounds: all `30` primitive binary necklaces of length 8, represented by their lexicographically minimal rotation.
- ICs: `502` non-zero binary words of length 1..8.
- Width: `256`.
- Steps: `300`.
- Burn-in: `80`.
- Period search: `2..16`.
- Maximum localized difference span: `32`.
- Detector: exact recurrence of the localized difference between a perturbed run and the unperturbed background orbit.
- Expected runs: `3855360`.
- Processed runs: `3855360`.
- Elapsed seconds: `1343.787`.
- Candidate detections: `323872`.
- Filtered period-1 moving aliases: `95121`.

## Background Validation

The generator produced exactly 30 primitive length-8 necklaces. Every word has
minimal period 8 and is the lexicographically smallest member of its rotation
class.

## Results

- Stationary rules: `rule_1`, `rule_5`, `rule_28`, `rule_29`, `rule_33`, `rule_37`, `rule_54`, `rule_62`, `rule_70`, `rule_71`, `rule_73`, `rule_91`, `rule_94`, `rule_95`, `rule_108`, `rule_109`, `rule_118`, `rule_123`, `rule_127`, `rule_131`, `rule_133`, `rule_145`, `rule_147`, `rule_156`, `rule_157`, `rule_198`, `rule_199`, `rule_201`.
- Moving rules: `rule_3`, `rule_6`, `rule_7`, `rule_9`, `rule_17`, `rule_20`, `rule_21`, `rule_25`, `rule_27`, `rule_31`, `rule_35`, `rule_38`, `rule_39`, `rule_45`, `rule_49`, `rule_52`, `rule_53`, `rule_58`, `rule_59`, `rule_61`, `rule_62`, `rule_63`, `rule_65`, `rule_67`, `rule_75`, `rule_83`, `rule_87`, `rule_88`, `rule_89`, `rule_101`, `rule_103`, `rule_111`, `rule_114`, `rule_115`, `rule_118`, `rule_119`, `rule_125`, `rule_131`, `rule_134`, `rule_145`, `rule_148`, `rule_154`, `rule_155`, `rule_158`, `rule_159`, `rule_163`, `rule_166`, `rule_173`, `rule_177`, `rule_180`, `rule_210`, `rule_211`, `rule_214`, `rule_215`, `rule_229`.
- New stationary rules relative to backgrounds 1/2/4: `rule_62`, `rule_118`, `rule_131`, `rule_145`.
- New moving rules relative to backgrounds 1/2/4: `rule_7`, `rule_9`, `rule_21`, `rule_25`, `rule_31`, `rule_45`, `rule_61`, `rule_65`, `rule_67`, `rule_75`, `rule_87`, `rule_88`, `rule_89`, `rule_101`, `rule_103`, `rule_111`, `rule_125`, `rule_173`, `rule_229`.
- Periods above 4: 6, 8, 10, 12, 15.
- All observed periods: 2, 3, 4, 6, 8, 10, 12, 15.
- Speeds outside {0, 0.5, 1.0}: 0.666667.

### Candidate Table

| kind | rule | background_canonical | candidates | min_len | min_word | T | drift | speed | motif | new_rule | new_T | new_speed |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| moving | rule_3 | 00000001 | 13 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00000011 | 31 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00000101 | 29 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00000111 | 31 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00001001 | 10 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00001011 | 40 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00001101 | 40 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00001111 | 42 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00010011 | 29 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00010101 | 41 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00010111 | 43 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00011001 | 17 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00011011 | 64 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00011101 | 65 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00011111 | 67 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00100101 | 8 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00100111 | 8 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00101011 | 18 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00101101 | 18 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00101111 | 18 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00110101 | 18 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00110111 | 18 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00111011 | 26 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00111101 | 27 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_3 | 00111111 | 27 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_6 | 00000001 | 10 | 3 | `101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00000011 | 8 | 3 | `101` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00000101 | 50 | 1 | `1` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00000111 | 6 | 3 | `001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00001001 | 6 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00001011 | 5 | 4 | `0011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00001101 | 63 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00001111 | 48 | 4 | `0011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00010011 | 19 | 4 | `1000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00010111 | 70 | 4 | `0110` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00011001 | 27 | 4 | `1100` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00011011 | 5 | 4 | `0100` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00011101 | 108 | 3 | `101` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00011111 | 3 | 6 | `001000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00100101 | 29 | 3 | `011` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00100111 | 6 | 6 | `010101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00101011 | 18 | 3 | `001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_6 | 00101101 | 57 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00101111 | 1 | 8 | `00110010` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00110111 | 70 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00111011 | 71 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00111101 | 112 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 00111111 | 97 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 01010111 | 88 | 4 | `0010` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 01011011 | 90 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 01011111 | 109 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 01101111 | 85 | 4 | `0011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_6 | 01111111 | 131 | 3 | `100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_7 | 00000011 | 31 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00000111 | 43 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00001011 | 33 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00001101 | 38 | 2 | `01` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00001111 | 34 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00010011 | 21 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00010111 | 29 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00011001 | 25 | 2 | `01` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00011011 | 11 | 6 | `101000` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00011101 | 44 | 4 | `1001` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00011111 | 24 | 4 | `0100` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00100111 | 22 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00101011 | 13 | 5 | `11000` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00101101 | 32 | 4 | `1100` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_7 | 00101111 | 33 | 4 | `0100` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_9 | 00001001 | 14 | 4 | `1000` | 3 | -2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_9 | 00101011 | 11 | 6 | `101100` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_9 | 00101101 | 13 | 5 | `00100` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_9 | 00101111 | 13 | 5 | `00100` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_9 | 00110101 | 5 | 6 | `010001` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_9 | 00110111 | 2 | 7 | `1100000` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_9 | 00111101 | 9 | 4 | `1000` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_9 | 00111111 | 9 | 4 | `1000` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_17 | 00000001 | 13 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00000011 | 31 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00000101 | 29 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00000111 | 31 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00001001 | 10 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00001011 | 40 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00001101 | 40 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00001111 | 42 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00010011 | 29 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00010101 | 41 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00010111 | 43 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00011001 | 17 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00011011 | 64 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00011101 | 65 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00011111 | 67 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00100101 | 8 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00100111 | 8 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00101011 | 18 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00101101 | 18 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00101111 | 18 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00110101 | 18 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00110111 | 18 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00111011 | 26 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00111101 | 27 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_17 | 00111111 | 27 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_20 | 00000001 | 4 | 7 | `0010011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00000011 | 13 | 7 | `0001011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00000101 | 13 | 7 | `0010101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_20 | 00000111 | 36 | 7 | `0000011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00001011 | 82 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00001111 | 72 | 5 | `01111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00010011 | 23 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00010101 | 32 | 3 | `101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_20 | 00011001 | 2 | 8 | `01010001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_20 | 00011011 | 87 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00011111 | 73 | 3 | `011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00100111 | 32 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_20 | 00101101 | 63 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00101111 | 61 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00110101 | 24 | 5 | `00010` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_20 | 00110111 | 45 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00111011 | 115 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00111101 | 3 | 8 | `00010000` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 00111111 | 93 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 01010111 | 12 | 3 | `001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 01101111 | 118 | 3 | `110` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_20 | 01111111 | 131 | 3 | `010` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_21 | 00000011 | 36 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00000111 | 47 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00001011 | 30 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00001101 | 45 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00001111 | 44 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00010011 | 6 | 7 | `0110010` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00010111 | 14 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00011001 | 42 | 2 | `01` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00011011 | 18 | 2 | `01` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00011101 | 48 | 4 | `1010` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00011111 | 34 | 4 | `0010` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00100111 | 41 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00101101 | 26 | 5 | `00001` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00110101 | 17 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_21 | 00111101 | 39 | 5 | `00001` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_25 | 00001001 | 2 | 7 | `0010011` | 3 | -3 | 1 | [[0], [0, 1], [0]] | True | False | False |
| moving | rule_25 | 00100101 | 17 | 4 | `1011` | 3 | -3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_25 | 00100111 | 9 | 4 | `0100` | 3 | -3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_25 | 00110111 | 25 | 1 | `1` | 3 | -3 | 1 | [[0, 1], [0, 1, 2], [0]] | True | False | False |
| moving | rule_25 | 01011011 | 3 | 6 | `100110` | 3 | -3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_27 | 00000001 | 26 | 5 | `01001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00000011 | 26 | 5 | `01001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00000101 | 8 | 4 | `1100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00000111 | 33 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00001001 | 7 | 7 | `0000001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00001011 | 7 | 7 | `0000001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00001101 | 21 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00001111 | 26 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00010011 | 10 | 5 | `00001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00010101 | 13 | 4 | `1100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00010111 | 9 | 4 | `0100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00011001 | 3 | 7 | `0000001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00011011 | 3 | 7 | `0000001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00011101 | 34 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00011111 | 39 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00100101 | 7 | 7 | `1010111` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00100111 | 4 | 5 | `11000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00101011 | 16 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00101101 | 20 | 4 | `1010` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00101111 | 26 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00110101 | 13 | 4 | `1100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00110111 | 13 | 4 | `0100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00111011 | 4 | 5 | `00001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00111101 | 18 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 00111111 | 18 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 01010111 | 61 | 2 | `01` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 01011011 | 23 | 5 | `11111` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 01011111 | 38 | 2 | `01` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 01101111 | 25 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_27 | 01111111 | 25 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_31 | 00000111 | 35 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00001101 | 36 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00001111 | 48 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00010111 | 17 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00011011 | 33 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00011101 | 63 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00011111 | 50 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00100111 | 23 | 2 | `01` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00101101 | 29 | 4 | `1100` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00101111 | 34 | 4 | `0100` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00110101 | 17 | 4 | `1001` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00110111 | 3 | 8 | `10110011` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00111011 | 40 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00111101 | 53 | 4 | `1001` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_31 | 00111111 | 34 | 4 | `0100` | 2 | 1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_35 | 00000001 | 13 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00000011 | 21 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00000101 | 10 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00000111 | 17 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00001001 | 17 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00001011 | 33 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00001101 | 17 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00001111 | 16 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00010011 | 37 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00010111 | 11 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00011001 | 49 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00011011 | 46 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00011101 | 50 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00011111 | 29 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00100111 | 25 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00101111 | 13 | 4 | `0001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00110111 | 11 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00111011 | 17 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00111101 | 10 | 5 | `01000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 00111111 | 9 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 01011111 | 13 | 6 | `000010` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 01101111 | 13 | 4 | `0001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_35 | 01111111 | 10 | 4 | `0001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_38 | 00000001 | 9 | 7 | `0010001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00000011 | 18 | 3 | `101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00000101 | 26 | 3 | `001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00000111 | 30 | 3 | `001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00001001 | 39 | 4 | `1000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00001011 | 40 | 3 | `001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00001101 | 34 | 4 | `1000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00001111 | 52 | 3 | `001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00010011 | 38 | 5 | `11111` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00010101 | 32 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 00010111 | 31 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 00011001 | 17 | 6 | `100000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00011011 | 17 | 6 | `100000` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 00011101 | 25 | 4 | `1000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00011111 | 31 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 00100101 | 11 | 6 | `000001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00101011 | 14 | 4 | `0100` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00101101 | 32 | 4 | `1000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00101111 | 14 | 4 | `0100` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 00110101 | 34 | 3 | `101` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 00110111 | 16 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 00111011 | 24 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 00111101 | 41 | 3 | `101` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 00111111 | 26 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 01010111 | 9 | 4 | `0101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 01011011 | 23 | 4 | `0001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 01011111 | 24 | 5 | `11111` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_38 | 01101111 | 7 | 7 | `1000111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_38 | 01111111 | 14 | 6 | `011011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_39 | 00000001 | 20 | 5 | `01001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00000011 | 22 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00000101 | 34 | 5 | `01001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00000111 | 32 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00001001 | 15 | 5 | `00001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00001011 | 12 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00001101 | 13 | 6 | `000001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00001111 | 22 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00010011 | 1 | 8 | `11110001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00010101 | 23 | 3 | `101` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00010111 | 35 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00011001 | 17 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00011011 | 3 | 6 | `111000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00011101 | 14 | 3 | `101` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00011111 | 27 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00100101 | 26 | 5 | `01000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00100111 | 8 | 3 | `111` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00101011 | 7 | 5 | `11100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00101101 | 7 | 6 | `000001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00101111 | 15 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00110101 | 6 | 5 | `01000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00110111 | 12 | 3 | `111` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00111011 | 13 | 3 | `111` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00111101 | 19 | 3 | `111` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 00111111 | 32 | 3 | `111` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 01010111 | 12 | 3 | `100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 01011011 | 9 | 7 | `0100000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 01011111 | 22 | 3 | `100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 01101111 | 16 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_39 | 01111111 | 26 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_45 | 00010011 | 12 | 3 | `001` | 6 | 6 | 1 | [[0, 1], [0, 1], [0, 2, 3], [0, 1, 2, 4], [0, 2], [0]] | True | True | False |
| moving | rule_49 | 00000001 | 13 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00000011 | 21 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00000101 | 15 | 3 | `011` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00000111 | 17 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00001001 | 19 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00001011 | 19 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00001101 | 36 | 3 | `011` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00001111 | 16 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00010011 | 52 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00010111 | 50 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00011001 | 56 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00011011 | 56 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00011101 | 12 | 6 | `000100` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00011111 | 27 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00100111 | 15 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00101111 | 10 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00110111 | 25 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00111011 | 14 | 5 | `01000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00111101 | 12 | 6 | `000100` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 00111111 | 9 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 01011111 | 2 | 7 | `1100010` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 01101111 | 10 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_49 | 01111111 | 9 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_52 | 00000001 | 19 | 5 | `01001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00000011 | 19 | 5 | `11001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00000101 | 12 | 5 | `01001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00000111 | 19 | 5 | `11001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00001001 | 15 | 6 | `101000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00001011 | 48 | 5 | `00001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00001101 | 15 | 5 | `01001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00001111 | 24 | 5 | `11001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00010011 | 40 | 3 | `101` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00010101 | 3 | 7 | `1010010` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00010111 | 32 | 3 | `101` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00011011 | 22 | 5 | `00001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00011101 | 3 | 7 | `1010010` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00011111 | 6 | 5 | `11111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00100101 | 23 | 5 | `01000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00100111 | 40 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00101011 | 44 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00101101 | 18 | 5 | `01000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00101111 | 40 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00110101 | 14 | 6 | `001000` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00110111 | 27 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00111011 | 27 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 00111101 | 7 | 7 | `1010010` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 00111111 | 16 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 01010111 | 30 | 3 | `010` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_52 | 01011111 | 12 | 4 | `0001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 01101111 | 13 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_52 | 01111111 | 18 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_53 | 00000001 | 16 | 5 | `01001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00000011 | 22 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00000101 | 43 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00000111 | 38 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00001001 | 14 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00001011 | 16 | 2 | `01` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00001101 | 22 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00001111 | 25 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00010011 | 17 | 3 | `101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00010101 | 61 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00010111 | 9 | 3 | `101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00011001 | 3 | 6 | `111000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00011011 | 3 | 6 | `111000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00011101 | 49 | 3 | `101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00011111 | 32 | 2 | `01` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00100101 | 19 | 5 | `01000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00100111 | 7 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00101011 | 10 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00101101 | 7 | 6 | `000001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00101111 | 13 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00110101 | 17 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00110111 | 11 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00111011 | 17 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00111101 | 24 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 00111111 | 26 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 01010111 | 17 | 3 | `100` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 01011011 | 8 | 7 | `0100000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 01011111 | 12 | 3 | `100` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 01101111 | 15 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_53 | 01111111 | 28 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_58 | 00100111 | 8 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_58 | 00110111 | 10 | 3 | `101` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_58 | 00111011 | 9 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00000001 | 8 | 4 | `1110` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00000011 | 11 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00000101 | 1 | 8 | `10111000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00000111 | 23 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00001001 | 14 | 4 | `1110` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00001011 | 17 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00001101 | 12 | 6 | `011100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00001111 | 16 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00010011 | 32 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00010111 | 51 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00011001 | 18 | 4 | `1110` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00011011 | 21 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00011101 | 15 | 5 | `01001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00011111 | 19 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00100111 | 43 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00101111 | 14 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00110111 | 51 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00111011 | 41 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00111101 | 33 | 3 | `101` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 00111111 | 23 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 01011111 | 16 | 4 | `0001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 01101111 | 14 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_59 | 01111111 | 12 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_61 | 00010011 | 20 | 2 | `01` | 3 | 3 | 1 | [[0, 1], [0, 1, 2], [0]] | True | False | False |
| moving | rule_61 | 00011011 | 8 | 3 | `101` | 3 | 3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_61 | 00100101 | 4 | 5 | `00110` | 3 | 3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_61 | 01011011 | 23 | 1 | `1` | 3 | 3 | 1 | [[0], [0], [0, 1]] | True | False | False |
| moving | rule_61 | 01101111 | 1 | 8 | `00110110` | 3 | 3 | 1 | [[0], [0, 1], [0]] | True | False | False |
| moving | rule_62 | 00000011 | 4 | 5 | `10001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_62 | 00001101 | 10 | 3 | `011` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_62 | 00011101 | 9 | 3 | `111` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_62 | 00101011 | 3 | 7 | `0111011` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_62 | 00101101 | 5 | 4 | `1011` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_62 | 00110101 | 2 | 8 | `10110000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_62 | 00110111 | 13 | 3 | `101` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_62 | 00111011 | 9 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00000011 | 30 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00000111 | 69 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00001011 | 17 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00001101 | 33 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00001111 | 45 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00010011 | 24 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00010111 | 52 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00011001 | 35 | 5 | `00001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00011011 | 12 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00011101 | 66 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00011111 | 36 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00100111 | 67 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00101011 | 17 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00101101 | 32 | 4 | `1000` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00101111 | 43 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00110101 | 26 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00110111 | 29 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00111011 | 23 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00111101 | 56 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 00111111 | 34 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 01010111 | 49 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 01011011 | 10 | 3 | `110` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 01011111 | 33 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 01101111 | 7 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_63 | 01111111 | 12 | 3 | `001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_65 | 00000001 | 17 | 1 | `1` | 3 | 2 | 0.666667 | [[0], [0], [0, 1]] | True | False | True |
| moving | rule_65 | 00000101 | 50 | 3 | `011` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00000111 | 12 | 4 | `0100` | 3 | 2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_65 | 00001001 | 23 | 3 | `111` | 3 | 2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_65 | 00010011 | 20 | 3 | `101` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00010101 | 15 | 6 | `001101` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00010111 | 41 | 3 | `011` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00011111 | 42 | 3 | `011` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00100111 | 8 | 5 | `00001` | 3 | 2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_65 | 00101011 | 1 | 8 | `01000010` | 3 | 2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_65 | 00101101 | 8 | 5 | `00010` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00101111 | 7 | 7 | `0110001` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00110101 | 11 | 6 | `001001` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00111011 | 17 | 6 | `100010` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00111101 | 12 | 3 | `001` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 00111111 | 6 | 5 | `11000` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 01010111 | 12 | 3 | `100` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 01011011 | 19 | 6 | `100010` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 01011111 | 10 | 3 | `100` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_65 | 01111111 | 6 | 5 | `11000` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_67 | 00001001 | 19 | 3 | `111` | 3 | 3 | 1 | [[0], [0, 1], [0]] | True | False | False |
| moving | rule_67 | 00100101 | 12 | 4 | `1100` | 3 | 3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_67 | 00100111 | 5 | 4 | `0100` | 3 | 3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_67 | 00111011 | 8 | 5 | `10110` | 3 | 3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_67 | 01101111 | 10 | 4 | `0011` | 3 | 3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_75 | 00101101 | 8 | 1 | `1` | 3 | 3 | 1 | [[0], [0], [0, 1, 2]] | True | False | False |
| moving | rule_75 | 01101111 | 5 | 6 | `001011` | 6 | 6 | 1 | [[0, 1, 2, 4], [0, 2], [0], [0, 1], [0, 1], [0, 2, 3]] | True | True | False |
| moving | rule_83 | 00000001 | 20 | 5 | `01001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00000011 | 36 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00000101 | 21 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00000111 | 27 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00001001 | 6 | 6 | `100000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00001011 | 15 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00001101 | 6 | 6 | `100000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00001111 | 23 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00010011 | 9 | 7 | `0000001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00010101 | 8 | 4 | `1100` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00010111 | 28 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00011001 | 3 | 7 | `0000001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00011011 | 3 | 7 | `0000001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00011101 | 8 | 4 | `1110` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00011111 | 29 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00100101 | 10 | 7 | `1010111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00100111 | 4 | 5 | `11000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00101011 | 9 | 6 | `110001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00101101 | 24 | 4 | `1110` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00101111 | 13 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00110101 | 19 | 3 | `101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00110111 | 2 | 7 | `1110000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00111011 | 7 | 6 | `111001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00111101 | 23 | 3 | `101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 00111111 | 21 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 01010111 | 18 | 4 | `0101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 01011011 | 23 | 5 | `10101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 01011111 | 30 | 5 | `11111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 01101111 | 26 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_83 | 01111111 | 26 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_87 | 00000111 | 23 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00001011 | 33 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00001111 | 37 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00010111 | 29 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00011011 | 23 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00011101 | 41 | 2 | `01` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00011111 | 45 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00100111 | 12 | 5 | `11010` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00101011 | 15 | 5 | `11000` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00101101 | 28 | 4 | `1001` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00101111 | 37 | 4 | `0100` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00110111 | 19 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00111011 | 10 | 6 | `101001` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00111101 | 51 | 4 | `1001` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_87 | 00111111 | 32 | 4 | `0100` | 2 | -1 | 0.5 | [[0], [0]] | True | False | False |
| moving | rule_88 | 00110111 | 10 | 4 | `0110` | 3 | -3 | 1 | [[0], [0, 2], [0]] | True | False | False |
| moving | rule_89 | 00110111 | 15 | 1 | `1` | 3 | -3 | 1 | [[0, 1, 2], [0], [0]] | True | True | False |
| moving | rule_101 | 00001001 | 8 | 5 | `01011` | 6 | -6 | 1 | [[0, 2, 3, 4], [0, 2], [0], [0, 1], [0, 1], [0, 1, 3]] | True | True | False |
| moving | rule_101 | 00011001 | 2 | 7 | `0010000` | 3 | -3 | 1 | [[0, 1, 2], [0], [0]] | True | False | False |
| moving | rule_103 | 00001001 | 12 | 3 | `011` | 3 | -3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_103 | 00011001 | 9 | 4 | `1011` | 3 | -3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_103 | 00011011 | 6 | 3 | `101` | 3 | -3 | 1 | [[0, 1], [0], [0]] | True | False | False |
| moving | rule_103 | 01011011 | 18 | 1 | `1` | 3 | -3 | 1 | [[0, 1, 2], [0], [0, 1]] | True | False | False |
| moving | rule_103 | 01101111 | 15 | 4 | `0001` | 3 | -3 | 1 | [[0], [0, 1], [0]] | True | False | False |
| moving | rule_111 | 00000001 | 6 | 6 | `111000` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00000011 | 6 | 6 | `111000` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00000101 | 12 | 4 | `1100` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00000111 | 45 | 4 | `0010` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00001011 | 6 | 7 | `0111101` | 3 | -2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_111 | 00001101 | 5 | 7 | `1001001` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00010101 | 12 | 4 | `1100` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00010111 | 40 | 3 | `111` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00011011 | 9 | 3 | `111` | 3 | -2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_111 | 00011111 | 15 | 1 | `1` | 3 | -2 | 0.666667 | [[0], [0], [0, 1]] | True | False | True |
| moving | rule_111 | 00100101 | 28 | 4 | `1111` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00101011 | 2 | 7 | `0111101` | 3 | -2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_111 | 00101101 | 2 | 7 | `1001001` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00110101 | 11 | 4 | `1100` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 00110111 | 25 | 4 | `0100` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 01010111 | 11 | 6 | `010011` | 3 | -2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_111 | 01011111 | 47 | 1 | `1` | 3 | -2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_111 | 01101111 | 25 | 4 | `0001` | 3 | -2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_111 | 01111111 | 15 | 3 | `001` | 3 | -2 | 0.666667 | [[0], [0], [0, 1]] | True | False | True |
| moving | rule_114 | 00100111 | 2 | 7 | `1110111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_114 | 00110111 | 13 | 3 | `101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_114 | 00111011 | 9 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00000001 | 11 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00000011 | 11 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00000101 | 14 | 5 | `00111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00000111 | 23 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00001001 | 14 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00001011 | 14 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00001101 | 26 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00001111 | 16 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00010011 | 12 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00010111 | 12 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00011001 | 35 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00011011 | 23 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00011101 | 30 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00011111 | 19 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00100111 | 44 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00101111 | 25 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00110111 | 39 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00111011 | 36 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00111101 | 17 | 5 | `01000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 00111111 | 23 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 01011111 | 10 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 01101111 | 15 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_115 | 01111111 | 12 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_118 | 00001011 | 5 | 4 | `0010` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_118 | 00010111 | 11 | 5 | `11011` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_118 | 00101101 | 3 | 7 | `1011101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_118 | 00110101 | 5 | 4 | `1101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_118 | 00110111 | 9 | 3 | `101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_118 | 00111011 | 11 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00000011 | 30 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00000111 | 69 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00001011 | 17 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00001101 | 33 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00001111 | 45 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00010011 | 24 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00010111 | 52 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00011001 | 35 | 5 | `00001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00011011 | 12 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00011101 | 66 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00011111 | 36 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00100111 | 67 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00101011 | 17 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00101101 | 32 | 4 | `1000` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00101111 | 43 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00110101 | 26 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00110111 | 29 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00111011 | 23 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00111101 | 56 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 00111111 | 34 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 01010111 | 49 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 01011011 | 10 | 3 | `110` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 01011111 | 33 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 01101111 | 7 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_119 | 01111111 | 12 | 3 | `001` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_125 | 00000011 | 14 | 1 | `1` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_125 | 00001011 | 11 | 6 | `110000` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_125 | 00001101 | 19 | 4 | `1000` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_125 | 00010011 | 1 | 8 | `11111001` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_125 | 00101011 | 15 | 6 | `110010` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_125 | 00101101 | 5 | 5 | `10010` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_125 | 00110101 | 8 | 4 | `1011` | 3 | 2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_125 | 00111011 | 26 | 3 | `011` | 3 | 2 | 0.666667 | [[0], [0, 1], [0]] | True | False | True |
| moving | rule_125 | 01101111 | 14 | 3 | `010` | 3 | 2 | 0.666667 | [[0, 1], [0], [0]] | True | False | True |
| moving | rule_131 | 00010011 | 9 | 4 | `0100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_131 | 00010111 | 9 | 5 | `11011` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_131 | 00011001 | 9 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_131 | 00101111 | 6 | 3 | `011` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_134 | 00000001 | 10 | 3 | `101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00000011 | 20 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00000101 | 34 | 1 | `1` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00000111 | 4 | 5 | `10101` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00001001 | 13 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00001011 | 15 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00001101 | 46 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00001111 | 45 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00010011 | 18 | 4 | `1000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00010111 | 7 | 5 | `11001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00011001 | 10 | 4 | `1100` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00011011 | 8 | 4 | `0100` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00011111 | 10 | 4 | `1000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00100101 | 29 | 3 | `101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00100111 | 12 | 4 | `1000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00101011 | 31 | 3 | `001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00101101 | 21 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00101111 | 17 | 6 | `010001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00110111 | 10 | 5 | `11000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_134 | 00111011 | 71 | 4 | `0011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00111101 | 98 | 5 | `01010` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 00111111 | 25 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 01010111 | 85 | 3 | `001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 01011011 | 66 | 5 | `00001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_134 | 01101111 | 9 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_145 | 00010011 | 11 | 4 | `0100` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_145 | 00011001 | 10 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_145 | 00011101 | 7 | 3 | `111` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_145 | 00101011 | 2 | 8 | `00100010` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_145 | 00101101 | 1 | 8 | `00100010` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_145 | 00111101 | 5 | 5 | `01110` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_145 | 00111111 | 3 | 6 | `011101` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_148 | 00000001 | 8 | 7 | `0010011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00000011 | 30 | 6 | `111000` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00000101 | 26 | 5 | `00111` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_148 | 00000111 | 102 | 2 | `01` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00001011 | 63 | 3 | `101` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00001101 | 8 | 7 | `0010001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00001111 | 28 | 6 | `011000` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00010011 | 12 | 4 | `0010` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00010101 | 42 | 3 | `101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_148 | 00010111 | 22 | 5 | `11001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00011001 | 7 | 5 | `01001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_148 | 00011011 | 21 | 6 | `101110` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00011101 | 5 | 6 | `011110` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00011111 | 3 | 8 | `00000001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00101101 | 28 | 4 | `1100` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00101111 | 41 | 2 | `01` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00110101 | 41 | 3 | `111` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_148 | 00110111 | 97 | 2 | `01` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 00111011 | 8 | 4 | `1000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_148 | 00111101 | 3 | 6 | `001001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_148 | 00111111 | 24 | 3 | `101` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 01011111 | 29 | 3 | `001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 01101111 | 2 | 7 | `1110111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_148 | 01111111 | 5 | 7 | `1110110` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_154 | 00000111 | 1 | 8 | `11110000` | 2 | -2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_154 | 00001001 | 2 | 7 | `0010011` | 4 | -4 | 1 | [[0, 1], [0, 1], [0], [0]] | False | False | False |
| moving | rule_154 | 00001011 | 5 | 6 | `111000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_154 | 00001101 | 2 | 7 | `1011101` | 4 | -4 | 1 | [[0, 1, 3], [0], [0], [0, 1]] | False | False | False |
| moving | rule_154 | 00001111 | 6 | 6 | `011000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_154 | 00010011 | 1 | 8 | `11110001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_154 | 00011011 | 3 | 6 | `111000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_154 | 00011101 | 6 | 5 | `01001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_154 | 00011111 | 4 | 6 | `011000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_154 | 00100101 | 6 | 3 | `111` | 4 | -4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_154 | 00100111 | 9 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_154 | 00101011 | 6 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_154 | 00101101 | 8 | 3 | `111` | 4 | -4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_154 | 00101111 | 11 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_154 | 00110101 | 11 | 3 | `111` | 2 | -2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_154 | 00110111 | 11 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_154 | 00111011 | 11 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_154 | 00111101 | 12 | 3 | `111` | 4 | -4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_154 | 00111111 | 14 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_154 | 01010111 | 4 | 5 | `11011` | 4 | -4 | 1 | [[0], [0, 1], [0, 1, 3], [0]] | False | False | False |
| moving | rule_154 | 01011011 | 7 | 5 | `11011` | 4 | -4 | 1 | [[0], [0, 1], [0, 1], [0]] | False | False | False |
| moving | rule_154 | 01011111 | 8 | 5 | `11011` | 4 | -4 | 1 | [[0], [0, 1], [0, 1], [0]] | False | False | False |
| moving | rule_154 | 01101111 | 5 | 6 | `001011` | 4 | -4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_154 | 01111111 | 10 | 5 | `11010` | 4 | -4 | 1 | [[0], [0, 1], [0, 1], [0]] | False | False | False |
| moving | rule_155 | 00000001 | 15 | 7 | `0010001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00000011 | 15 | 7 | `0010001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00000101 | 12 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00000111 | 1 | 8 | `10110000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 00001001 | 11 | 7 | `0000001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00001011 | 42 | 2 | `01` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00001101 | 30 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00001111 | 23 | 5 | `11001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 00010011 | 28 | 5 | `00001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00010101 | 34 | 4 | `1010` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 00010111 | 36 | 4 | `0100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00011001 | 19 | 5 | `00001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00011011 | 44 | 2 | `01` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00011101 | 14 | 5 | `01101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 00011111 | 20 | 5 | `11111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00100111 | 21 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00101011 | 45 | 3 | `001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00101101 | 18 | 5 | `01000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 00101111 | 52 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00110101 | 43 | 1 | `1` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 00110111 | 42 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00111011 | 50 | 2 | `01` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 00111101 | 18 | 1 | `1` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 00111111 | 22 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_155 | 01010111 | 2 | 8 | `10110100` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 01011011 | 17 | 6 | `111010` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 01011111 | 13 | 6 | `011010` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 01101111 | 22 | 5 | `11010` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_155 | 01111111 | 16 | 6 | `011010` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_158 | 00000001 | 5 | 7 | `0111101` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00000011 | 32 | 4 | `0100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00000101 | 30 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00000111 | 6 | 7 | `1001111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00001001 | 1 | 8 | `00010000` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00001011 | 37 | 2 | `01` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00001101 | 10 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_158 | 00001111 | 27 | 5 | `11001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00010011 | 92 | 2 | `01` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00010111 | 17 | 6 | `001000` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00011001 | 49 | 4 | `1000` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00011101 | 15 | 5 | `01001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00011111 | 99 | 2 | `01` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00100111 | 13 | 5 | `00010` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00101101 | 77 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00101111 | 77 | 4 | `0100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00110101 | 19 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_158 | 00110111 | 17 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00111011 | 34 | 3 | `001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_158 | 00111101 | 6 | 5 | `01000` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 00111111 | 27 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_158 | 01010111 | 50 | 4 | `0101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_158 | 01011111 | 18 | 6 | `000110` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_158 | 01111111 | 6 | 8 | `00000100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00000001 | 135 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00000011 | 88 | 3 | `001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00000111 | 55 | 4 | `0001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00001001 | 102 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00001011 | 56 | 1 | `1` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00001101 | 6 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00001111 | 63 | 5 | `11001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00010011 | 46 | 4 | `0010` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00010101 | 15 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00011001 | 5 | 5 | `01101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_159 | 00011011 | 32 | 3 | `011` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_159 | 00011101 | 2 | 7 | `1011100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00011111 | 27 | 5 | `11111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00100111 | 64 | 5 | `00001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00101101 | 72 | 3 | `001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00101111 | 95 | 4 | `0100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00110101 | 12 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_159 | 00110111 | 26 | 3 | `011` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00111011 | 49 | 3 | `001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_159 | 00111101 | 2 | 7 | `1011100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 00111111 | 15 | 3 | `111` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_159 | 01010111 | 39 | 4 | `0101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_159 | 01011111 | 8 | 8 | `01010100` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_159 | 01111111 | 3 | 8 | `00110100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_163 | 00010011 | 11 | 4 | `0100` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_163 | 00011001 | 9 | 1 | `1` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_163 | 00011011 | 1 | 8 | `00010001` | 2 | 1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_166 | 00000001 | 9 | 5 | `01011` | 4 | -4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_166 | 00000011 | 18 | 1 | `1` | 4 | -4 | 1 | [[0], [0], [0, 1], [0, 1]] | False | False | False |
| moving | rule_166 | 00000101 | 9 | 5 | `01011` | 2 | -2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_166 | 00000111 | 13 | 3 | `101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_166 | 00001001 | 5 | 5 | `01011` | 4 | -4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_166 | 00001011 | 14 | 1 | `1` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_166 | 00001101 | 8 | 5 | `01011` | 4 | -4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_166 | 00001111 | 17 | 1 | `1` | 2 | -2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_166 | 00010011 | 12 | 1 | `1` | 4 | -4 | 1 | [[0], [0], [0, 1], [0, 1]] | False | False | False |
| moving | rule_166 | 00010101 | 3 | 6 | `100000` | 2 | -2 | 1 | [[0, 1], [0, 1]] | False | False | False |
| moving | rule_166 | 00010111 | 5 | 4 | `1000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_166 | 00011001 | 5 | 6 | `111000` | 4 | -4 | 1 | [[0, 1], [0, 1, 3], [0], [0]] | False | False | False |
| moving | rule_166 | 00011011 | 10 | 1 | `1` | 4 | -4 | 1 | [[0], [0], [0, 1], [0, 1]] | False | False | False |
| moving | rule_166 | 00011101 | 3 | 6 | `100000` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_166 | 00011111 | 8 | 4 | `1000` | 2 | -2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_166 | 00100101 | 4 | 5 | `00001` | 4 | -4 | 1 | [[0], [0, 1], [0, 1], [0]] | False | False | False |
| moving | rule_166 | 00100111 | 5 | 4 | `1000` | 4 | -4 | 1 | [[0], [0], [0, 1], [0, 1]] | False | False | False |
| moving | rule_166 | 00101011 | 4 | 5 | `00001` | 2 | -2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_166 | 00101101 | 5 | 5 | `00001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_166 | 00101111 | 1 | 8 | `00100010` | 4 | -4 | 1 | [[0, 1, 3], [0], [0], [0, 1]] | False | False | False |
| moving | rule_166 | 00110101 | 6 | 5 | `00001` | 4 | -4 | 1 | [[0], [0, 1], [0, 1], [0]] | False | False | False |
| moving | rule_166 | 00110111 | 7 | 4 | `1000` | 4 | -4 | 1 | [[0], [0], [0, 1], [0, 1]] | False | False | False |
| moving | rule_166 | 00111101 | 4 | 5 | `00001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_166 | 00111111 | 4 | 5 | `00001` | 2 | -2 | 1 | [[0, 1], [0, 1]] | False | False | False |
| moving | rule_166 | 01011011 | 5 | 4 | `0001` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_166 | 01101111 | 5 | 4 | `0001` | 4 | -4 | 1 | [[0, 1], [0, 1], [0], [0]] | False | False | False |
| moving | rule_173 | 00010011 | 14 | 1 | `1` | 3 | 3 | 1 | [[0], [0], [0, 2]] | True | False | False |
| moving | rule_177 | 00010011 | 11 | 4 | `0100` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_177 | 00011001 | 9 | 1 | `1` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_177 | 00011011 | 6 | 4 | `0110` | 2 | -1 | 0.5 | [[0], [0]] | False | False | False |
| moving | rule_180 | 00000001 | 10 | 5 | `01001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00000011 | 8 | 5 | `11001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00000101 | 9 | 5 | `01001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00000111 | 6 | 5 | `11001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00001001 | 5 | 5 | `01011` | 4 | 4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_180 | 00001011 | 6 | 5 | `11011` | 4 | 4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_180 | 00001101 | 6 | 5 | `01001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00001111 | 7 | 5 | `11001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00010011 | 8 | 3 | `101` | 4 | 4 | 1 | [[0], [0, 1], [0, 2, 3], [0]] | False | False | False |
| moving | rule_180 | 00010101 | 3 | 6 | `001000` | 4 | 4 | 1 | [[0], [0, 1], [0, 2, 3], [0]] | False | False | False |
| moving | rule_180 | 00011001 | 4 | 5 | `01011` | 4 | 4 | 1 | [[0, 1], [0, 1], [0], [0]] | False | False | False |
| moving | rule_180 | 00011011 | 6 | 5 | `11011` | 4 | 4 | 1 | [[0, 1], [0, 1], [0], [0]] | False | False | False |
| moving | rule_180 | 00011101 | 2 | 7 | `1010000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00011111 | 2 | 7 | `1110000` | 2 | 2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_180 | 00100101 | 7 | 5 | `01000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00100111 | 4 | 5 | `11000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00101011 | 4 | 5 | `00001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_180 | 00101101 | 4 | 5 | `01000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00101111 | 5 | 5 | `11000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_180 | 00110101 | 5 | 6 | `001001` | 4 | 4 | 1 | [[0], [0, 1], [0, 2, 3], [0]] | False | False | False |
| moving | rule_180 | 00110111 | 2 | 7 | `1110000` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_180 | 00111011 | 4 | 5 | `00001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_180 | 01011011 | 5 | 4 | `0001` | 4 | 4 | 1 | [[0, 1], [0], [0], [0, 1]] | False | False | False |
| moving | rule_180 | 01101111 | 1 | 8 | `00110110` | 4 | 4 | 1 | [[0, 1], [0, 1], [0], [0]] | False | False | False |
| moving | rule_210 | 00000011 | 6 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0, 1]] | False | False | False |
| moving | rule_210 | 00000111 | 12 | 1 | `1` | 2 | 2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_210 | 00001001 | 6 | 3 | `111` | 4 | 4 | 1 | [[0, 1], [0, 1], [0], [0]] | False | False | False |
| moving | rule_210 | 00001011 | 2 | 7 | `0111011` | 4 | 4 | 1 | [[0, 2, 3], [0], [0], [0, 1]] | False | False | False |
| moving | rule_210 | 00001101 | 11 | 3 | `111` | 4 | 4 | 1 | [[0, 1], [0, 1], [0], [0]] | False | False | False |
| moving | rule_210 | 00001111 | 16 | 3 | `111` | 4 | 4 | 1 | [[0, 1], [0, 1], [0], [0]] | False | False | False |
| moving | rule_210 | 00010011 | 9 | 1 | `1` | 4 | 4 | 1 | [[0], [0], [0, 1], [0, 1]] | False | False | False |
| moving | rule_210 | 00010111 | 8 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_210 | 00011001 | 8 | 1 | `1` | 4 | 4 | 1 | [[0], [0], [0, 1], [0, 2, 3]] | False | False | False |
| moving | rule_210 | 00011011 | 8 | 1 | `1` | 4 | 4 | 1 | [[0], [0], [0, 1], [0, 1]] | False | False | False |
| moving | rule_210 | 00011101 | 13 | 1 | `1` | 4 | 4 | 1 | [[0], [0], [0, 1], [0, 2, 3]] | False | False | False |
| moving | rule_210 | 00011111 | 14 | 1 | `1` | 4 | 4 | 1 | [[0], [0], [0, 1], [0, 1]] | False | False | False |
| moving | rule_210 | 00100101 | 6 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_210 | 00100111 | 11 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_210 | 00101011 | 6 | 3 | `111` | 2 | 2 | 1 | [[0], [0]] | False | False | False |
| moving | rule_210 | 00101101 | 5 | 4 | `1100` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_210 | 00101111 | 10 | 4 | `0100` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_210 | 00110101 | 7 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_210 | 00110111 | 12 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_210 | 00111011 | 8 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_210 | 00111101 | 12 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_210 | 00111111 | 18 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_210 | 01010111 | 8 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0, 1]] | False | False | False |
| moving | rule_210 | 01011011 | 8 | 1 | `1` | 4 | 4 | 1 | [[0], [0, 1], [0, 1], [0]] | False | False | False |
| moving | rule_210 | 01011111 | 12 | 1 | `1` | 4 | 4 | 1 | [[0], [0, 1], [0, 1], [0]] | False | False | False |
| moving | rule_210 | 01101111 | 11 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_210 | 01111111 | 15 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00000001 | 13 | 5 | `01001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00000011 | 30 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00000101 | 22 | 5 | `01001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00000111 | 36 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00001001 | 5 | 7 | `0011111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00001011 | 22 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00001101 | 29 | 4 | `1000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00001111 | 47 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00010011 | 7 | 7 | `0000001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00010101 | 12 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00010111 | 35 | 4 | `0010` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00011101 | 21 | 4 | `1000` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00011111 | 22 | 4 | `0010` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00100101 | 31 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00100111 | 25 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00101011 | 22 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00101101 | 42 | 2 | `01` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00101111 | 37 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 00110101 | 47 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00110111 | 44 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00111011 | 22 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00111101 | 25 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 00111111 | 17 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 01010111 | 35 | 4 | `0010` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 01011011 | 20 | 5 | `11111` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 01011111 | 22 | 4 | `0011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_211 | 01101111 | 46 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_211 | 01111111 | 18 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00000011 | 31 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00000111 | 16 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00001001 | 3 | 7 | `0001011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00001011 | 20 | 5 | `00001` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00001101 | 17 | 4 | `1010` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00001111 | 38 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00010011 | 10 | 5 | `00011` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00010101 | 83 | 1 | `1` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00010111 | 6 | 6 | `010011` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00011001 | 14 | 4 | `1010` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00011011 | 20 | 1 | `1` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00011111 | 3 | 6 | `010100` | 2 | -2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00100101 | 73 | 5 | `00110` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00100111 | 10 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00101011 | 29 | 1 | `1` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00101101 | 78 | 5 | `00100` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00101111 | 11 | 4 | `0011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00110111 | 26 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 00111011 | 12 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00111101 | 69 | 4 | `1100` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 00111111 | 19 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 01011011 | 26 | 4 | `0001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 01011111 | 46 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_214 | 01101111 | 11 | 4 | `0011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_214 | 01111111 | 15 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00000001 | 134 | 3 | `011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00000011 | 93 | 3 | `001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00000101 | 114 | 2 | `01` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00000111 | 4 | 5 | `11011` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00001001 | 78 | 3 | `011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00001011 | 2 | 7 | `0110011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00001101 | 39 | 5 | `01001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00001111 | 33 | 3 | `101` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00010011 | 66 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00010101 | 66 | 4 | `1011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00010111 | 61 | 3 | `001` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00011001 | 5 | 6 | `101100` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00011011 | 10 | 5 | `10101` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00011101 | 60 | 3 | `011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00011111 | 5 | 4 | `0110` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00100101 | 107 | 5 | `00001` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00100111 | 6 | 3 | `101` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00101011 | 19 | 1 | `1` | 2 | -2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00101101 | 67 | 5 | `00110` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00101111 | 5 | 4 | `0011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00110111 | 30 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 00111011 | 16 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00111101 | 100 | 4 | `1000` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 00111111 | 12 | 3 | `111` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 01011011 | 26 | 4 | `0011` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 01011111 | 65 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_215 | 01101111 | 5 | 4 | `0011` | 2 | 2 | 1 | [[0, 1], [0]] | False | False | False |
| moving | rule_215 | 01111111 | 15 | 1 | `1` | 2 | 2 | 1 | [[0], [0, 1]] | False | False | False |
| moving | rule_229 | 00011001 | 6 | 5 | `01001` | 3 | -3 | 1 | [[0], [0], [0, 2]] | True | False | False |
| stationary | rule_1 | 00000001 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_1 | 00000011 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_1 | 00000101 | 490 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_1 | 00000111 | 490 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_1 | 00001001 | 484 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_1 | 00001011 | 484 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_1 | 00001101 | 484 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_1 | 00001111 | 484 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_1 | 00010011 | 485 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00010101 | 483 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00010111 | 483 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00011001 | 481 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00011011 | 481 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00011101 | 481 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00011111 | 481 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00100101 | 311 | 3 | `001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00100111 | 310 | 4 | `0001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00101011 | 220 | 4 | `0001` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_1 | 00101101 | 216 | 3 | `001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00101111 | 215 | 4 | `0001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00110101 | 236 | 3 | `001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00110111 | 235 | 4 | `0001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00111011 | 186 | 4 | `0001` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_1 | 00111101 | 181 | 3 | `001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 00111111 | 180 | 4 | `0001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 01010111 | 238 | 3 | `100` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 01011011 | 189 | 3 | `100` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 01011111 | 183 | 3 | `100` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 01101111 | 215 | 4 | `0001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_1 | 01111111 | 180 | 4 | `0001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_5 | 00000001 | 495 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_5 | 00000011 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 00000101 | 481 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_5 | 00000111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 00001001 | 491 | 1 | `1` | 2 | 0 | 0 | #.# / #.#.# | False | False | False |
| stationary | rule_5 | 00001011 | 491 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 00001101 | 495 | 1 | `1` | 2 | 0 | 0 | #.# / #.#.# | False | False | False |
| stationary | rule_5 | 00001111 | 495 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 00010011 | 475 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 00010101 | 446 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_5 | 00010111 | 466 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 00011001 | 480 | 1 | `1` | 2 | 0 | 0 | #.# / #.#.# | False | False | False |
| stationary | rule_5 | 00011011 | 480 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 00011101 | 471 | 1 | `1` | 2 | 0 | 0 | #.# / #.#.# | False | False | False |
| stationary | rule_5 | 00011111 | 471 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 00100101 | 448 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 00100111 | 481 | 2 | `01` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 00101011 | 467 | 2 | `01` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_5 | 00101101 | 494 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 00101111 | 470 | 2 | `01` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 00110101 | 467 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 00110111 | 415 | 2 | `01` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 00111011 | 389 | 2 | `01` | 2 | 0 | 0 | #.# / #.#.# | False | False | False |
| stationary | rule_5 | 00111101 | 471 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 00111111 | 340 | 2 | `01` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 01010111 | 466 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_5 | 01011011 | 480 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 01011111 | 471 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_5 | 01101111 | 403 | 3 | `010` | 2 | 0 | 0 | #.# / #.#.# | False | False | False |
| stationary | rule_5 | 01111111 | 339 | 3 | `010` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_28 | 00000001 | 384 | 2 | `01` | 2 | 0 | 0 | ####### / ####### | False | False | False |
| stationary | rule_28 | 00000011 | 376 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_28 | 00000101 | 355 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_28 | 00000111 | 450 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_28 | 00001001 | 449 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_28 | 00001011 | 320 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_28 | 00001101 | 444 | 2 | `01` | 2 | 0 | 0 | #### / ###### | False | False | False |
| stationary | rule_28 | 00001111 | 323 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_28 | 00010011 | 456 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_28 | 00010101 | 304 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_28 | 00010111 | 453 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_28 | 00011001 | 387 | 2 | `01` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_28 | 00011011 | 457 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_28 | 00011101 | 378 | 2 | `01` | 2 | 0 | 0 | #### / ###### | False | False | False |
| stationary | rule_28 | 00011111 | 469 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_28 | 00100101 | 455 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_28 | 00100111 | 453 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_28 | 00101011 | 316 | 3 | `001` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_28 | 00101101 | 454 | 2 | `01` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_28 | 00101111 | 319 | 3 | `001` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_28 | 00110101 | 452 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_28 | 00110111 | 451 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_28 | 00111011 | 362 | 3 | `001` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_28 | 00111101 | 469 | 2 | `01` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_28 | 00111111 | 359 | 3 | `001` | 2 | 0 | 0 | ######### / ######### | False | False | False |
| stationary | rule_28 | 01010111 | 305 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_28 | 01011011 | 464 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_28 | 01011111 | 378 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_28 | 01101111 | 457 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_28 | 01111111 | 392 | 2 | `01` | 2 | 0 | 0 | ######### / ######### | False | False | False |
| stationary | rule_29 | 00000001 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00000011 | 488 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_29 | 00000101 | 488 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00000111 | 479 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_29 | 00001001 | 482 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00001011 | 478 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_29 | 00001101 | 480 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00001111 | 478 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_29 | 00010011 | 473 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_29 | 00010101 | 479 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00010111 | 465 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_29 | 00011001 | 486 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00011011 | 473 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_29 | 00011101 | 482 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00011111 | 480 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_29 | 00100101 | 472 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_29 | 00100111 | 469 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00101011 | 478 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00101101 | 469 | 2 | `01` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_29 | 00101111 | 478 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00110101 | 469 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_29 | 00110111 | 470 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00111011 | 485 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 00111101 | 482 | 2 | `01` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_29 | 00111111 | 488 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 01010111 | 478 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 01011011 | 477 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 01011111 | 488 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 01101111 | 481 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_29 | 01111111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_33 | 00000001 | 486 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_33 | 00000011 | 491 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_33 | 00000101 | 481 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_33 | 00000111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_33 | 00001001 | 492 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_33 | 00001011 | 494 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_33 | 00001101 | 492 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_33 | 00001111 | 492 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_33 | 00010011 | 486 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 00010101 | 491 | 1 | `1` | 2 | 0 | 0 | ##### / ####### | False | False | False |
| stationary | rule_33 | 00010111 | 487 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_33 | 00011001 | 477 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 00011011 | 489 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 00011101 | 486 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_33 | 00011111 | 476 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 00100101 | 489 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_33 | 00100111 | 452 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 00101011 | 471 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 00101101 | 486 | 1 | `1` | 2 | 0 | 0 | ##..# / ### | False | False | False |
| stationary | rule_33 | 00101111 | 472 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 00110101 | 452 | 1 | `1` | 2 | 0 | 0 | ##### / ####### | False | False | False |
| stationary | rule_33 | 00110111 | 470 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_33 | 00111011 | 471 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 00111101 | 473 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_33 | 00111111 | 402 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 01010111 | 495 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 01011011 | 494 | 1 | `1` | 2 | 0 | 0 | ##..# / ### | False | False | False |
| stationary | rule_33 | 01011111 | 418 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_33 | 01101111 | 487 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_33 | 01111111 | 476 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_37 | 00000001 | 490 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00000011 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00000101 | 476 | 2 | `01` | 2 | 0 | 0 | ###.....### / #####...##### | False | False | False |
| stationary | rule_37 | 00000111 | 488 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00001001 | 488 | 1 | `1` | 2 | 0 | 0 | ####### / ######### | False | False | False |
| stationary | rule_37 | 00001011 | 486 | 1 | `1` | 2 | 0 | 0 | ####### / ######### | False | False | False |
| stationary | rule_37 | 00001101 | 485 | 1 | `1` | 2 | 0 | 0 | ####### / ######### | False | False | False |
| stationary | rule_37 | 00001111 | 493 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00010011 | 482 | 1 | `1` | 2 | 0 | 0 | #####..#### / ###....## | False | False | False |
| stationary | rule_37 | 00010101 | 487 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00010111 | 488 | 1 | `1` | 2 | 0 | 0 | #####..#### / ###....## | False | False | False |
| stationary | rule_37 | 00011001 | 478 | 1 | `1` | 2 | 0 | 0 | ######### / ####### | False | False | False |
| stationary | rule_37 | 00011011 | 470 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_37 | 00011101 | 482 | 1 | `1` | 2 | 0 | 0 | #####..##### / ###....### | False | False | False |
| stationary | rule_37 | 00011111 | 478 | 1 | `1` | 2 | 0 | 0 | ### / ##### | False | False | False |
| stationary | rule_37 | 00100101 | 493 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_37 | 00100111 | 491 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00101011 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00101101 | 492 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_37 | 00101111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00110101 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_37 | 00110111 | 478 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_37 | 00111011 | 477 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_37 | 00111101 | 490 | 1 | `1` | 2 | 0 | 0 | #..##......# / #....##......# | False | False | False |
| stationary | rule_37 | 00111111 | 458 | 1 | `1` | 2 | 0 | 0 | ### / ##### | False | False | False |
| stationary | rule_37 | 01010111 | 490 | 1 | `1` | 2 | 0 | 0 | #....# / #..# | False | False | False |
| stationary | rule_37 | 01011011 | 491 | 1 | `1` | 2 | 0 | 0 | #....#...# / #..#.....# | False | False | False |
| stationary | rule_37 | 01011111 | 474 | 1 | `1` | 2 | 0 | 0 | #..# / #....# | False | False | False |
| stationary | rule_37 | 01101111 | 482 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_37 | 01111111 | 474 | 1 | `1` | 2 | 0 | 0 | ### / ##### | False | False | False |
| stationary | rule_54 | 00000001 | 59 | 3 | `001` | 4 | 0 | 0 | #.#.#.## / #.#.#.# / ##.#.#.# / #.#.#.# | False | False | False |
| stationary | rule_54 | 00000101 | 360 | 1 | `1` | 4 | 0 | 0 | ##.#....##.#...## / #.#.....#.#...# / #.##....#.##.## / #.#.....#.#...# | False | False | False |
| stationary | rule_54 | 00000111 | 23 | 3 | `111` | 4 | 0 | 0 | #.# / ##.# / #.# / #.## | False | False | False |
| stationary | rule_54 | 00001011 | 358 | 1 | `1` | 4 | 0 | 0 | #.#...# / ##.#...## / #.#...# / #.##.## | False | False | False |
| stationary | rule_54 | 00001101 | 316 | 1 | `1` | 4 | 0 | 0 | #.#.#.# / #.###.# / #.#.#.# / ##.###.## | False | False | False |
| stationary | rule_54 | 00010101 | 91 | 3 | `001` | 4 | 0 | 0 | #.#.#.## / #.#.#.# / ##.#.#.# / #.#.#.# | False | False | False |
| stationary | rule_54 | 00011111 | 359 | 1 | `1` | 4 | 0 | 0 | #.#.....#...#.# / #.##....##.##.# / #.#.....#...#.# / ##.#....##...#.## | False | False | False |
| stationary | rule_54 | 00100111 | 353 | 1 | `1` | 4 | 0 | 0 | #.##....##.##.# / #.#.....#...#.# / ##.#....##...#.## / #.#.....#...#.# | False | False | False |
| stationary | rule_54 | 01010111 | 401 | 1 | `1` | 4 | 0 | 0 | ##.# / #.# / #.## / #.# | False | False | False |
| stationary | rule_54 | 01011011 | 309 | 1 | `1` | 4 | 0 | 0 | #.#.....#...#.# / ##.#....##...#.## / #.#.....#...#.# / #.##....##.##.# | False | False | False |
| stationary | rule_54 | 01011111 | 49 | 4 | `0010` | 4 | 0 | 0 | ##.# / #.# / #.## / #.# | False | False | False |
| stationary | rule_54 | 01111111 | 64 | 4 | `0001` | 4 | 0 | 0 | #.# / ##.# / #.# / #.## | False | False | False |
| stationary | rule_62 | 00000001 | 491 | 1 | `1` | 3 | 0 | 0 | ###.##.#.#.##.# / ##.##.###.##.### / #.##.##..##.## | True | False | False |
| stationary | rule_62 | 00000101 | 493 | 1 | `1` | 3 | 0 | 0 | ## / #.# / #.### | True | False | False |
| stationary | rule_62 | 00000111 | 489 | 1 | `1` | 3 | 0 | 0 | #..# / #..# / ##.## | True | False | False |
| stationary | rule_62 | 00001001 | 488 | 1 | `1` | 3 | 0 | 0 | #.##..#..##.## / ###.#..#.#.##.# / ##.###.##.##.### | True | False | False |
| stationary | rule_62 | 00001011 | 487 | 2 | `01` | 3 | 0 | 0 | #.#####..##..# / ###..#.#.#.#..# / ##.#.####.###.## | True | False | False |
| stationary | rule_62 | 00001111 | 495 | 1 | `1` | 3 | 0 | 0 | ## / # / # | True | False | False |
| stationary | rule_62 | 00010011 | 495 | 1 | `1` | 3 | 0 | 0 | #..# / ##.## / #..# | True | False | False |
| stationary | rule_62 | 00010111 | 490 | 1 | `1` | 3 | 0 | 0 | #.# / #..# / ##.## | True | False | False |
| stationary | rule_62 | 00011001 | 483 | 1 | `1` | 3 | 0 | 0 | #.##.##..##.## / ###.##.#.#.##.# / ##.##.###.##.### | True | False | False |
| stationary | rule_62 | 00011011 | 495 | 1 | `1` | 3 | 0 | 0 | ##.##.###.##.### / #.##.##..##.## / ###.##.#.#.##.# | True | False | False |
| stationary | rule_62 | 00011111 | 495 | 1 | `1` | 3 | 0 | 0 | ##..##.#.####.###.## / #...#.#####..##..# / #...###..#.#.#.#..# | True | False | False |
| stationary | rule_62 | 00100111 | 484 | 1 | `1` | 3 | 0 | 0 | ##..# / ###.## / #...# | True | False | False |
| stationary | rule_62 | 00101111 | 491 | 1 | `1` | 3 | 0 | 0 | # / #.# / ### | True | False | False |
| stationary | rule_62 | 00111101 | 488 | 1 | `1` | 3 | 0 | 0 | # / ## / # | True | False | False |
| stationary | rule_62 | 00111111 | 493 | 1 | `1` | 3 | 0 | 0 | ###.##.#.#.##.# / ##.##.###.##.### / #.##.##..##.## | True | False | False |
| stationary | rule_62 | 01010111 | 485 | 1 | `1` | 3 | 0 | 0 | ###.# / #.#### / #.## | True | False | False |
| stationary | rule_62 | 01011011 | 483 | 1 | `1` | 3 | 0 | 0 | ## / ### / # | True | False | False |
| stationary | rule_62 | 01011111 | 495 | 1 | `1` | 3 | 0 | 0 | ##...##.## / #....#..# / #....#..# | True | False | False |
| stationary | rule_62 | 01101111 | 478 | 1 | `1` | 3 | 0 | 0 | ###.##.#.#.##.# / ##.##.###.##.### / #.##.##..##.## | True | False | False |
| stationary | rule_70 | 00000001 | 366 | 1 | `1` | 2 | 0 | 0 | ########## / ######## | False | False | False |
| stationary | rule_70 | 00000011 | 367 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_70 | 00000101 | 369 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_70 | 00000111 | 480 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_70 | 00001001 | 455 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_70 | 00001011 | 455 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_70 | 00001101 | 391 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_70 | 00001111 | 393 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_70 | 00010011 | 350 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_70 | 00010101 | 345 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_70 | 00010111 | 379 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_70 | 00011001 | 464 | 1 | `1` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_70 | 00011011 | 464 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_70 | 00011101 | 480 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_70 | 00011111 | 480 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_70 | 00100101 | 463 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_70 | 00100111 | 478 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_70 | 00101011 | 451 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_70 | 00101101 | 458 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_70 | 00101111 | 459 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_70 | 00110101 | 321 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_70 | 00110111 | 363 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_70 | 00111011 | 456 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_70 | 00111101 | 374 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_70 | 00111111 | 375 | 1 | `1` | 2 | 0 | 0 | ####### / ####### | False | False | False |
| stationary | rule_70 | 01010111 | 360 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_70 | 01011011 | 450 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_70 | 01011111 | 375 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_70 | 01101111 | 459 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_70 | 01111111 | 373 | 2 | `01` | 2 | 0 | 0 | ####### / ####### | False | False | False |
| stationary | rule_71 | 00000001 | 495 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_71 | 00000011 | 492 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00000101 | 492 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00000111 | 493 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00001001 | 482 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_71 | 00001011 | 482 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00001101 | 495 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00001111 | 495 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00010011 | 482 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00010101 | 481 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00010111 | 482 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00011001 | 480 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_71 | 00011011 | 480 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00011101 | 489 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00011111 | 491 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00100101 | 474 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00100111 | 484 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00101011 | 467 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00101101 | 474 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00101111 | 483 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_71 | 00110101 | 481 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_71 | 00110111 | 482 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_71 | 00111011 | 472 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_71 | 00111101 | 487 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_71 | 00111111 | 491 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_71 | 01010111 | 482 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_71 | 01011011 | 471 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_71 | 01011111 | 491 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_71 | 01101111 | 483 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_71 | 01111111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_73 | 00000011 | 399 | 1 | `1` | 3 | 0 | 0 | ### / ##.## / # | False | True | False |
| stationary | rule_73 | 00000101 | 167 | 2 | `01` | 3 | 0 | 0 | # / ### / ##.## | False | True | False |
| stationary | rule_73 | 00000111 | 197 | 1 | `1` | 3 | 0 | 0 | ### / ## / #.## | False | True | False |
| stationary | rule_73 | 00001001 | 389 | 1 | `1` | 6 | 0 | 0 | ##.####.## / #.##....# / #..###..#.# / ##.###..##.# / #.###...## / #..##...# | False | True | False |
| stationary | rule_73 | 00001011 | 394 | 1 | `1` | 8 | 0 | 0 | ##### / #.#.#.# / #..###..# / #.##.##.# / ##..#..## / ##.## / # / #.# | False | True | False |
| stationary | rule_73 | 00001101 | 426 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | True | False |
| stationary | rule_73 | 00001111 | 400 | 1 | `1` | 6 | 0 | 0 | #.##.#...# / #...###.## / ##.#.#....# / ####..#.# / #..#..##.# / ######...## | False | True | False |
| stationary | rule_73 | 00010011 | 437 | 1 | `1` | 6 | 0 | 0 | ###.## / ##..# / #### / ##..## / ##.## / #.## | False | True | False |
| stationary | rule_73 | 00011001 | 402 | 1 | `1` | 2 | 0 | 0 | #.## / #.# | False | True | False |
| stationary | rule_73 | 00011011 | 438 | 1 | `1` | 6 | 0 | 0 | # / ## / # / #.# / ##.# / ## | False | True | False |
| stationary | rule_73 | 00100111 | 230 | 1 | `1` | 3 | 0 | 0 | ##.## / # / ### | False | True | False |
| stationary | rule_73 | 00101011 | 376 | 1 | `1` | 3 | 0 | 0 | ## / ##.# / ### | False | True | False |
| stationary | rule_73 | 00101101 | 433 | 1 | `1` | 6 | 0 | 0 | ## / # / #.# / ##.# / ## / # | False | True | False |
| stationary | rule_73 | 00101111 | 380 | 1 | `1` | 12 | 0 | 0 | ##.#...# / ###.## / #.#....# / #####..#.# / #..##.# / ###...## / ###...# / #..##.## / ####.....# / #.####...#.# / #....##.##.# / ##..#.....## | False | True | False |
| stationary | rule_73 | 00110101 | 422 | 1 | `1` | 6 | 0 | 0 | ## / # / #.# / #.## / ## / # | False | True | False |
| stationary | rule_73 | 00110111 | 384 | 2 | `01` | 6 | 0 | 0 | #.# / ##.# / ## / # / ## / # | False | True | False |
| stationary | rule_73 | 00111011 | 388 | 1 | `1` | 3 | 0 | 0 | #..##..##..# / ###.####.### / #.#.##.#.# | False | True | False |
| stationary | rule_73 | 00111101 | 352 | 3 | `001` | 6 | 0 | 0 | #...#.##.# / ##.###...# / #....#.#.## / #.#..#### / #.##..#..# / ##...###### | False | True | False |
| stationary | rule_73 | 00111111 | 270 | 1 | `1` | 3 | 0 | 0 | ##.## / # / ### | False | True | False |
| stationary | rule_73 | 01010111 | 139 | 3 | `001` | 3 | 0 | 0 | ## / ##.# / ### | False | True | False |
| stationary | rule_73 | 01011011 | 439 | 1 | `1` | 6 | 0 | 0 | #.# / ##.# / ## / # / ## / # | False | True | False |
| stationary | rule_73 | 01011111 | 49 | 5 | `11101` | 6 | 0 | 0 | ####.#### / #..#..# / ######### / #.###.# / ###...### / #.#.#.# | False | True | False |
| stationary | rule_73 | 01101111 | 392 | 1 | `1` | 12 | 0 | 0 | #..####..#.# / ###..#..##.# / #.####...## / #..#.#...# / #######.## / #####....# / #.##.##..#.# / #...#...##.# / ##.###....## / #.##..# / ###...## / #.#.#....# | False | True | False |
| stationary | rule_73 | 01111111 | 61 | 1 | `1` | 3 | 0 | 0 | ###.....### / #.......# / #.#.....#.# | False | True | False |
| stationary | rule_91 | 00000001 | 476 | 1 | `1` | 2 | 0 | 0 | ### / ##### | False | False | False |
| stationary | rule_91 | 00000011 | 465 | 1 | `1` | 2 | 0 | 0 | ### / ##### | False | False | False |
| stationary | rule_91 | 00000101 | 476 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 00000111 | 482 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 00001001 | 480 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_91 | 00001011 | 495 | 1 | `1` | 2 | 0 | 0 | #..###...#.## / #....###.#...## | False | False | False |
| stationary | rule_91 | 00001101 | 493 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 00001111 | 494 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 00010011 | 484 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_91 | 00010101 | 490 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 00010111 | 489 | 1 | `1` | 2 | 0 | 0 | ######### / ####### | False | False | False |
| stationary | rule_91 | 00011001 | 495 | 1 | `1` | 2 | 0 | 0 | ### / ##### | False | False | False |
| stationary | rule_91 | 00011011 | 492 | 1 | `1` | 2 | 0 | 0 | #...##...#..# / #.....##.#....# | False | False | False |
| stationary | rule_91 | 00011101 | 484 | 2 | `01` | 2 | 0 | 0 | #####.....##### / ###.......### | False | False | False |
| stationary | rule_91 | 00011111 | 488 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 00100101 | 489 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_91 | 00100111 | 473 | 1 | `1` | 2 | 0 | 0 | ######### / ####### | False | False | False |
| stationary | rule_91 | 00101011 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 00101101 | 492 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_91 | 00101111 | 481 | 2 | `01` | 2 | 0 | 0 | ##....### / ####..##### | False | False | False |
| stationary | rule_91 | 00110101 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 00110111 | 486 | 1 | `1` | 2 | 0 | 0 | ######### / ####### | False | False | False |
| stationary | rule_91 | 00111011 | 489 | 1 | `1` | 2 | 0 | 0 | ######### / ####### | False | False | False |
| stationary | rule_91 | 00111101 | 477 | 1 | `1` | 2 | 0 | 0 | ###.....### / #####...##### | False | False | False |
| stationary | rule_91 | 00111111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_91 | 01010111 | 489 | 1 | `1` | 2 | 0 | 0 | #.....##.#....# / #...##...#..# | False | False | False |
| stationary | rule_91 | 01011011 | 494 | 1 | `1` | 2 | 0 | 0 | #....#####...#..# / #..###..##.#....# | False | False | False |
| stationary | rule_91 | 01011111 | 473 | 1 | `1` | 2 | 0 | 0 | ###....## / #####..#### | False | False | False |
| stationary | rule_91 | 01101111 | 488 | 1 | `1` | 2 | 0 | 0 | ### / ##### | False | False | False |
| stationary | rule_91 | 01111111 | 490 | 1 | `1` | 2 | 0 | 0 | ##### / ### | False | False | False |
| stationary | rule_94 | 00000001 | 195 | 2 | `01` | 6 | 0 | 0 | #######.# / #.#####..## / ######.#.# / #.######.# / ######..## / #.#####.#.# | False | True | False |
| stationary | rule_94 | 00000101 | 194 | 2 | `01` | 3 | 0 | 0 | #.#.### / #.#### / ##..### | False | True | False |
| stationary | rule_94 | 00000111 | 195 | 2 | `01` | 3 | 0 | 0 | #####..## / #####.#.# / ######.# | False | True | False |
| stationary | rule_94 | 00001011 | 220 | 3 | `101` | 2 | 0 | 0 | ##.# / ##..# | False | True | False |
| stationary | rule_94 | 00001101 | 252 | 2 | `01` | 2 | 0 | 0 | #....### / #...### | False | True | False |
| stationary | rule_94 | 00010011 | 308 | 3 | `001` | 6 | 0 | 0 | #.#####.#.# / #######.# / #.#####..## / ######.#.# / #.######.# / ######..## | False | True | False |
| stationary | rule_94 | 00010101 | 182 | 4 | `1010` | 2 | 0 | 0 | ##.# / ##..# | False | False | False |
| stationary | rule_94 | 00010111 | 187 | 1 | `1` | 2 | 0 | 0 | #.# / #...# | False | False | False |
| stationary | rule_94 | 00011001 | 247 | 2 | `01` | 6 | 0 | 0 | #.######.# / ######..## / #.#####.#.# / #######.# / #.#####..## / ######.#.# | False | True | False |
| stationary | rule_94 | 00011011 | 187 | 3 | `001` | 2 | 0 | 0 | #.### / #### | False | True | False |
| stationary | rule_94 | 00011101 | 199 | 4 | `1000` | 3 | 0 | 0 | ##.#..## / ###.#### / ##..#.## | False | False | False |
| stationary | rule_94 | 00011111 | 163 | 5 | `00001` | 3 | 0 | 0 | #######..## / #######.#.# / ########.# | False | True | False |
| stationary | rule_94 | 00100101 | 288 | 1 | `1` | 2 | 0 | 0 | ###.# / #### | False | True | False |
| stationary | rule_94 | 00100111 | 286 | 1 | `1` | 6 | 0 | 0 | #.#.###.# / #.##### / ##..###.# / #.#.#### / #.####.# / ##..#### | False | True | False |
| stationary | rule_94 | 00101011 | 173 | 4 | `0101` | 2 | 0 | 0 | # / # | False | True | False |
| stationary | rule_94 | 00101101 | 489 | 1 | `1` | 2 | 0 | 0 | # / # | False | True | False |
| stationary | rule_94 | 00101111 | 492 | 1 | `1` | 2 | 0 | 0 | #...# / #.# | False | True | False |
| stationary | rule_94 | 00110101 | 241 | 2 | `01` | 2 | 0 | 0 | # / # | False | True | False |
| stationary | rule_94 | 00110111 | 242 | 1 | `1` | 2 | 0 | 0 | # / # | False | True | False |
| stationary | rule_94 | 00111011 | 210 | 3 | `001` | 2 | 0 | 0 | #.# / #...# | False | True | False |
| stationary | rule_94 | 00111101 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | True | False |
| stationary | rule_94 | 01010111 | 156 | 3 | `010` | 2 | 0 | 0 | ###.# / #### | False | True | False |
| stationary | rule_94 | 01011011 | 224 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_94 | 01011111 | 253 | 2 | `01` | 2 | 0 | 0 | #..## / #.## | False | True | False |
| stationary | rule_94 | 01101111 | 492 | 1 | `1` | 2 | 0 | 0 | #### / #.### | False | True | False |
| stationary | rule_94 | 01111111 | 297 | 2 | `01` | 6 | 0 | 0 | #.####### / ##..#####.# / #.#.###### / #.######.# / ##..###### / #.#.#####.# | False | True | False |
| stationary | rule_95 | 00000001 | 345 | 3 | `101` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00000011 | 351 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00000101 | 471 | 2 | `01` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00000111 | 474 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00001001 | 420 | 3 | `101` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00001011 | 470 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 00001101 | 481 | 2 | `01` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00001111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 00010011 | 414 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00010101 | 466 | 2 | `01` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 00010111 | 469 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00011001 | 453 | 3 | `001` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00011011 | 480 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 00011101 | 484 | 2 | `01` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 00011111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 00100101 | 478 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00100111 | 478 | 1 | `1` | 2 | 0 | 0 | #.# / #.#.# | False | False | False |
| stationary | rule_95 | 00101011 | 466 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_95 | 00101101 | 489 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 00101111 | 492 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_95 | 00110101 | 472 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 00110111 | 473 | 1 | `1` | 2 | 0 | 0 | #.# / #.#.# | False | False | False |
| stationary | rule_95 | 00111011 | 482 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_95 | 00111101 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 00111111 | 495 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_95 | 01010111 | 453 | 1 | `1` | 2 | 0 | 0 | # / #.# | False | False | False |
| stationary | rule_95 | 01011011 | 448 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 01011111 | 486 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_95 | 01101111 | 492 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_95 | 01111111 | 495 | 1 | `1` | 2 | 0 | 0 | #.# / # | False | False | False |
| stationary | rule_108 | 00000001 | 179 | 3 | `101` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_108 | 00000011 | 182 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_108 | 00000101 | 474 | 1 | `1` | 2 | 0 | 0 | ### / ## | False | False | False |
| stationary | rule_108 | 00000111 | 468 | 1 | `1` | 2 | 0 | 0 | ## / ### | False | False | False |
| stationary | rule_108 | 00001001 | 237 | 3 | `101` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_108 | 00001011 | 200 | 1 | `1` | 2 | 0 | 0 | #### / #.# | False | False | False |
| stationary | rule_108 | 00001101 | 296 | 3 | `111` | 2 | 0 | 0 | # / ## | False | False | False |
| stationary | rule_108 | 00001111 | 224 | 2 | `01` | 2 | 0 | 0 | #.# / #### | False | False | False |
| stationary | rule_108 | 00010011 | 232 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_108 | 00010101 | 332 | 2 | `01` | 2 | 0 | 0 | ##.## / #.## | False | False | False |
| stationary | rule_108 | 00010111 | 493 | 1 | `1` | 2 | 0 | 0 | ## / ### | False | False | False |
| stationary | rule_108 | 00011001 | 252 | 3 | `111` | 2 | 0 | 0 | #.# / ##.# | False | False | False |
| stationary | rule_108 | 00011011 | 227 | 1 | `1` | 2 | 0 | 0 | ### / #.# | False | False | False |
| stationary | rule_108 | 00011101 | 493 | 1 | `1` | 2 | 0 | 0 | ### / ## | False | False | False |
| stationary | rule_108 | 00011111 | 255 | 2 | `01` | 2 | 0 | 0 | #.# / ### | False | False | False |
| stationary | rule_108 | 00100101 | 471 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_108 | 00100111 | 465 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_108 | 00101011 | 268 | 1 | `1` | 2 | 0 | 0 | ###.# / #.#.# | False | False | False |
| stationary | rule_108 | 00101101 | 346 | 3 | `011` | 2 | 0 | 0 | #.## / #.### | False | False | False |
| stationary | rule_108 | 00101111 | 480 | 1 | `1` | 2 | 0 | 0 | ##.## / ##.# | False | False | False |
| stationary | rule_108 | 00110101 | 298 | 3 | `001` | 2 | 0 | 0 | #.#.### / #.#.#.# | False | False | False |
| stationary | rule_108 | 00110111 | 481 | 1 | `1` | 2 | 0 | 0 | ##.# / ###.# | False | False | False |
| stationary | rule_108 | 00111011 | 474 | 1 | `1` | 2 | 0 | 0 | ##### / #.# | False | False | False |
| stationary | rule_108 | 00111101 | 488 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_108 | 00111111 | 286 | 1 | `1` | 2 | 0 | 0 | ### / ## | False | False | False |
| stationary | rule_108 | 01010111 | 485 | 1 | `1` | 2 | 0 | 0 | #.# / ##.# | False | False | False |
| stationary | rule_108 | 01011011 | 205 | 3 | `110` | 2 | 0 | 0 | #.#..# / ###..# | False | False | False |
| stationary | rule_108 | 01011111 | 239 | 1 | `1` | 2 | 0 | 0 | #.## / #.# | False | False | False |
| stationary | rule_108 | 01101111 | 210 | 1 | `1` | 2 | 0 | 0 | #..## / #..# | False | False | False |
| stationary | rule_108 | 01111111 | 486 | 1 | `1` | 2 | 0 | 0 | ### / #.# | False | False | False |
| stationary | rule_109 | 00000001 | 51 | 1 | `1` | 3 | 0 | 0 | ##.## / # / ### | False | True | False |
| stationary | rule_109 | 00000011 | 294 | 1 | `1` | 6 | 0 | 0 | ####..#.# / #..#..##.# / ######...## / #.##.#...# / #...###.## / ##.#.#....# | False | True | False |
| stationary | rule_109 | 00000101 | 55 | 5 | `00101` | 2 | 0 | 0 | ###..# / #.#### | False | True | False |
| stationary | rule_109 | 00001001 | 397 | 2 | `01` | 3 | 0 | 0 | #..##..##..# / ###.####.### / #.#.##.#.# | False | True | False |
| stationary | rule_109 | 00001011 | 399 | 1 | `1` | 6 | 0 | 0 | #.#..#### / #.##..#..# / ##...###### / #...#.##.# / ##.###...# / #....#.#.## | False | True | False |
| stationary | rule_109 | 00001101 | 394 | 1 | `1` | 3 | 0 | 0 | ##.## / # / ### | False | True | False |
| stationary | rule_109 | 00001111 | 419 | 1 | `1` | 3 | 0 | 0 | ### / ## / ##.# | False | True | False |
| stationary | rule_109 | 00010011 | 376 | 1 | `1` | 6 | 0 | 0 | # / ## / # / #.# / #.## / ## | False | True | False |
| stationary | rule_109 | 00010101 | 118 | 1 | `1` | 3 | 0 | 0 | ## / #.## / ### | False | True | False |
| stationary | rule_109 | 00011001 | 397 | 1 | `1` | 3 | 0 | 0 | #### / ## / #..# | False | True | False |
| stationary | rule_109 | 00011011 | 233 | 1 | `1` | 6 | 0 | 0 | ##.### / #..## / #### / ##..## / ##.## / ##.# | False | True | False |
| stationary | rule_109 | 00011111 | 214 | 1 | `1` | 3 | 0 | 0 | ### / ##.## / # | False | True | False |
| stationary | rule_109 | 00100101 | 423 | 1 | `1` | 6 | 0 | 0 | ## / # / #.# / #.## / ## / # | False | True | False |
| stationary | rule_109 | 00100111 | 417 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | True | False |
| stationary | rule_109 | 00101011 | 371 | 2 | `01` | 3 | 0 | 0 | ###.####.### / #.#.##.#.# / #..##..##..# | False | True | False |
| stationary | rule_109 | 00101101 | 391 | 1 | `1` | 3 | 0 | 0 | ###.####.### / #.#.##.#.# / #..##..##..# | False | True | False |
| stationary | rule_109 | 00101111 | 403 | 3 | `001` | 2 | 0 | 0 | ##.### / ###.## | False | True | False |
| stationary | rule_109 | 00110101 | 405 | 1 | `1` | 3 | 0 | 0 | ###.####.### / #.#.##.#.# / #..##..##..# | False | True | False |
| stationary | rule_109 | 00110111 | 435 | 1 | `1` | 2 | 0 | 0 | ###....# / ###.....# | False | True | False |
| stationary | rule_109 | 00111011 | 406 | 1 | `1` | 2 | 0 | 0 | ##### / #.# | False | True | False |
| stationary | rule_109 | 00111101 | 442 | 1 | `1` | 6 | 0 | 0 | ## / # / #.# / #.## / ## / # | False | True | False |
| stationary | rule_109 | 00111111 | 384 | 1 | `1` | 6 | 0 | 0 | ######...## / #.##.#...# / #...###.## / ##.#.#....# / ####..#.# / #..#..##.# | False | True | False |
| stationary | rule_109 | 01011111 | 184 | 2 | `01` | 3 | 0 | 0 | # / ### / ##.## | False | True | False |
| stationary | rule_109 | 01101111 | 403 | 1 | `1` | 6 | 0 | 0 | #.##..#..# / ##...###### / #...#.##.# / ##.###...# / #....#.#.## / #.#..#### | False | True | False |
| stationary | rule_118 | 00000001 | 481 | 1 | `1` | 3 | 0 | 0 | #.##.#.#.##.### / ###.##.###.##.## / ##.##..##.##.# | True | False | False |
| stationary | rule_118 | 00000101 | 495 | 1 | `1` | 3 | 0 | 0 | #..#.#.#.#..### / ##.###.####.#.## / #..##..#####.# | True | False | False |
| stationary | rule_118 | 00000111 | 488 | 1 | `1` | 3 | 0 | 0 | ###.##.##.###.## / ##.##..#..##.# / #.##.#.#..#.### | True | False | False |
| stationary | rule_118 | 00001001 | 401 | 1 | `1` | 3 | 0 | 0 | #.# / #### / ## | True | False | False |
| stationary | rule_118 | 00001101 | 493 | 1 | `1` | 3 | 0 | 0 | #.# / ### / # | True | False | False |
| stationary | rule_118 | 00001111 | 493 | 1 | `1` | 3 | 0 | 0 | #.# / ### / # | True | False | False |
| stationary | rule_118 | 00010011 | 495 | 1 | `1` | 3 | 0 | 0 | ##.##..##.##.# / #.##.#.#.##.### / ###.##.###.##.## | True | False | False |
| stationary | rule_118 | 00011001 | 495 | 1 | `1` | 3 | 0 | 0 | ###..#.###.#..## / #.###..###.#.# / #.#..#.#.###### | True | False | False |
| stationary | rule_118 | 00011011 | 488 | 1 | `1` | 3 | 0 | 0 | ###.##.###.##.## / ##.##..##.##.# / #.##.#.#.##.### | True | False | False |
| stationary | rule_118 | 00011101 | 493 | 1 | `1` | 3 | 0 | 0 | #...#...# / #..##...# / ##.###..## | True | False | False |
| stationary | rule_118 | 00011111 | 495 | 1 | `1` | 3 | 0 | 0 | ##.### / #...# / #..## | True | False | False |
| stationary | rule_118 | 00100111 | 491 | 1 | `1` | 3 | 0 | 0 | ##.##..#.###.# / #.##.#.#.#..### / ###.##.###..#.## | True | False | False |
| stationary | rule_118 | 00101111 | 490 | 1 | `1` | 3 | 0 | 0 | # / ## / # | True | False | False |
| stationary | rule_118 | 00111101 | 488 | 1 | `1` | 3 | 0 | 0 | # / ## / # | True | False | False |
| stationary | rule_118 | 00111111 | 491 | 1 | `1` | 3 | 0 | 0 | #.##.#.#.##.### / ###.##.###.##.## / ##.##..##.##.# | True | False | False |
| stationary | rule_118 | 01010111 | 485 | 1 | `1` | 3 | 0 | 0 | ##.##..#.### / #.##.#.#.#..# / ###.##.###..#.# | True | False | False |
| stationary | rule_118 | 01011011 | 480 | 1 | `1` | 3 | 0 | 0 | ## / # / # | True | False | False |
| stationary | rule_118 | 01011111 | 495 | 1 | `1` | 3 | 0 | 0 | #.###..###.#.# / #.#..#.#.###### / ###..#.###.#..## | True | False | False |
| stationary | rule_118 | 01101111 | 495 | 1 | `1` | 3 | 0 | 0 | #.##.#.#.##.### / ###.##.###.##.## / ##.##..##.##.# | True | False | False |
| stationary | rule_123 | 00000001 | 476 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00000011 | 409 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00000101 | 424 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00000111 | 476 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_123 | 00001001 | 486 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_123 | 00001011 | 476 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_123 | 00001101 | 487 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00001111 | 491 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_123 | 00010011 | 477 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00010101 | 495 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00010111 | 489 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_123 | 00011001 | 490 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00011011 | 457 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00011101 | 490 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_123 | 00011111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_123 | 00100101 | 493 | 1 | `1` | 2 | 0 | 0 | #..## / ### | False | False | False |
| stationary | rule_123 | 00100111 | 488 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_123 | 00101011 | 469 | 1 | `1` | 2 | 0 | 0 | ##### / ####### | False | False | False |
| stationary | rule_123 | 00101101 | 493 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_123 | 00101111 | 493 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_123 | 00110101 | 440 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00110111 | 482 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_123 | 00111011 | 486 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_123 | 00111101 | 490 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_123 | 00111111 | 492 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_123 | 01010111 | 492 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_123 | 01011011 | 490 | 1 | `1` | 2 | 0 | 0 | ### / ##..# | False | False | False |
| stationary | rule_123 | 01011111 | 476 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_123 | 01101111 | 491 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_123 | 01111111 | 484 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_127 | 00000001 | 186 | 3 | `111` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00000011 | 189 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00000101 | 192 | 3 | `111` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00000111 | 475 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 00001001 | 241 | 3 | `111` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00001011 | 244 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00001101 | 322 | 3 | `111` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00001111 | 481 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 00010011 | 224 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00010101 | 226 | 3 | `111` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00010111 | 477 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 00011001 | 316 | 3 | `111` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00011011 | 319 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00011101 | 459 | 3 | `111` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00011111 | 489 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 00100101 | 195 | 3 | `011` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00100111 | 475 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 00101011 | 247 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00101101 | 324 | 3 | `011` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00101111 | 481 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 00110101 | 278 | 3 | `001` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00110111 | 479 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 00111011 | 464 | 1 | `1` | 2 | 0 | 0 | # / ### | False | False | False |
| stationary | rule_127 | 00111101 | 476 | 3 | `001` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 00111111 | 495 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_127 | 01010111 | 477 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_127 | 01011011 | 319 | 1 | `1` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_127 | 01011111 | 489 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_127 | 01101111 | 481 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_127 | 01111111 | 495 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_131 | 00000011 | 490 | 1 | `1` | 3 | 0 | 0 | ###.## / #...# / ##..# | True | False | False |
| stationary | rule_131 | 00000101 | 495 | 1 | `1` | 3 | 0 | 0 | # / ## / # | True | False | False |
| stationary | rule_131 | 00000111 | 495 | 1 | `1` | 3 | 0 | 0 | #.# / ### / # | True | False | False |
| stationary | rule_131 | 00001001 | 495 | 1 | `1` | 3 | 0 | 0 | ###.##.#.#.##.# / ##.##.###.##.### / #.##.##..##.## | True | False | False |
| stationary | rule_131 | 00001011 | 490 | 1 | `1` | 3 | 0 | 0 | #...###..#.#.#.#..# / ##..##.#.####.###.## / #...#.#####..##..# | True | False | False |
| stationary | rule_131 | 00001101 | 492 | 1 | `1` | 3 | 0 | 0 | #...###..#.#.#.#..# / ##..##.#.####.###.## / #...#.#####..##..# | True | False | False |
| stationary | rule_131 | 00001111 | 494 | 1 | `1` | 3 | 0 | 0 | #....######.#.#..#.# / #....##..#.###.#..### / ##...#.#.###..###.# | True | False | False |
| stationary | rule_131 | 00010101 | 486 | 1 | `1` | 3 | 0 | 0 | #.##.##..##.## / ###.##.#.#.##.# / ##.##.###.##.### | True | False | False |
| stationary | rule_131 | 00011011 | 492 | 1 | `1` | 3 | 0 | 0 | ##.##..##.## / #.##.#.#.##.# / #.##.###.##.### | True | False | False |
| stationary | rule_131 | 00011101 | 491 | 1 | `1` | 3 | 0 | 0 | ### / # / #.# | True | False | False |
| stationary | rule_131 | 00011111 | 488 | 1 | `1` | 3 | 0 | 0 | ##.##.###.##.### / #.##.##..##.## / ###.##.#.#.##.# | True | False | False |
| stationary | rule_131 | 00100101 | 483 | 1 | `1` | 3 | 0 | 0 | #.##.##..##.## / ###.##.#.#.##.# / ##.##.###.##.### | True | False | False |
| stationary | rule_131 | 00100111 | 492 | 1 | `1` | 3 | 0 | 0 | #.# / ### / # | True | False | False |
| stationary | rule_131 | 00110111 | 495 | 1 | `1` | 3 | 0 | 0 | #.# / #### / ## | True | False | False |
| stationary | rule_131 | 00111011 | 495 | 1 | `1` | 3 | 0 | 0 | #....##..#.###.#..### / ##...#.#.###..###.# / #....######.#.#..#.# | True | False | False |
| stationary | rule_131 | 00111101 | 491 | 1 | `1` | 3 | 0 | 0 | #.#####..##..# / ###..#.#.#.#..# / ##.#.####.###.## | True | False | False |
| stationary | rule_131 | 01011111 | 495 | 1 | `1` | 3 | 0 | 0 | ###..#.#.#.#..# / ##.#.####.###.## / #.#####..##..# | True | False | False |
| stationary | rule_131 | 01101111 | 426 | 1 | `1` | 3 | 0 | 0 | #.##.##..##.## / ###.##.#.#.##.# / ##.##.###.##.### | True | False | False |
| stationary | rule_131 | 01111111 | 483 | 1 | `1` | 3 | 0 | 0 | #.### / ### / ##.# | True | False | False |
| stationary | rule_133 | 00000001 | 278 | 2 | `01` | 6 | 0 | 0 | #######.# / #.#####..## / ######.#.# / #.######.# / ######..## / #.#####.#.# | False | True | False |
| stationary | rule_133 | 00000101 | 225 | 1 | `1` | 2 | 0 | 0 | #...# / #.# | False | True | False |
| stationary | rule_133 | 00000111 | 160 | 3 | `111` | 2 | 0 | 0 | ######## / #.####### | False | True | False |
| stationary | rule_133 | 00001001 | 491 | 1 | `1` | 2 | 0 | 0 | # / # | False | True | False |
| stationary | rule_133 | 00001011 | 491 | 1 | `1` | 2 | 0 | 0 | #.# / #...# | False | True | False |
| stationary | rule_133 | 00001101 | 495 | 1 | `1` | 6 | 0 | 0 | ##...#### / ###.####.# / #.#..#### / #####.# / ##.#### / #######.# | False | True | False |
| stationary | rule_133 | 00010011 | 262 | 3 | `011` | 2 | 0 | 0 | # / # | False | True | False |
| stationary | rule_133 | 00010101 | 152 | 4 | `1000` | 2 | 0 | 0 | #.## / ##.# | False | True | False |
| stationary | rule_133 | 00010111 | 185 | 2 | `01` | 2 | 0 | 0 | #.## / #..## | False | False | False |
| stationary | rule_133 | 00011001 | 229 | 2 | `01` | 6 | 0 | 0 | #.####..# / #..######.# / #.####.# / #..####..# / #.######.# / #..####.# | False | True | False |
| stationary | rule_133 | 00011011 | 334 | 2 | `01` | 2 | 0 | 0 | #.#######.# / ######### | False | True | False |
| stationary | rule_133 | 00011101 | 219 | 4 | `1000` | 3 | 0 | 0 | ##..#.## / ####.### / ##.#..## | False | True | False |
| stationary | rule_133 | 00011111 | 215 | 2 | `01` | 3 | 0 | 0 | ##..##### / #.#.##### / #.###### | False | True | False |
| stationary | rule_133 | 00100101 | 223 | 1 | `1` | 2 | 0 | 0 | # / # | False | False | False |
| stationary | rule_133 | 00100111 | 176 | 3 | `011` | 6 | 0 | 0 | #.#.###.# / #.##### / ##..###.# / #.#.#### / #.####.# / ##..#### | False | True | False |
| stationary | rule_133 | 00101011 | 187 | 4 | `0001` | 2 | 0 | 0 | #...# / #.# | False | True | False |
| stationary | rule_133 | 00101101 | 494 | 1 | `1` | 2 | 0 | 0 | #.### / #### | False | True | False |
| stationary | rule_133 | 00101111 | 220 | 3 | `001` | 3 | 0 | 0 | ####..# / ######.# / ####.# | False | True | False |
| stationary | rule_133 | 00110101 | 182 | 2 | `01` | 2 | 0 | 0 | ##.# / ##..# | False | True | False |
| stationary | rule_133 | 00110111 | 301 | 3 | `011` | 2 | 0 | 0 | #.### / #### | False | True | False |
| stationary | rule_133 | 00111011 | 293 | 3 | `001` | 3 | 0 | 0 | #####.#.# / ######.# / #####..## | False | True | False |
| stationary | rule_133 | 00111101 | 249 | 1 | `1` | 3 | 0 | 0 | ####.### / ##.#..## / ##..#.## | False | True | False |
| stationary | rule_133 | 01010111 | 184 | 3 | `010` | 2 | 0 | 0 | #.## / #..## | False | False | False |
| stationary | rule_133 | 01011011 | 336 | 1 | `1` | 3 | 0 | 0 | #######.#.# / ########.# / #######..## | False | True | False |
| stationary | rule_133 | 01011111 | 215 | 2 | `01` | 3 | 0 | 0 | ###.#.# / ####.# / ###..## | False | True | False |
| stationary | rule_133 | 01111111 | 208 | 2 | `01` | 6 | 0 | 0 | #.####### / ##..#####.# / #.#.###### / #.######.# / ##..###### / #.#.#####.# | False | True | False |
| stationary | rule_145 | 00000011 | 491 | 1 | `1` | 3 | 0 | 0 | #.##.#.#.#..### / ###.##.###..#.## / ##.##..#.###.# | True | False | False |
| stationary | rule_145 | 00000101 | 495 | 1 | `1` | 3 | 0 | 0 | # / #.# / ### | True | False | False |
| stationary | rule_145 | 00000111 | 495 | 1 | `1` | 3 | 0 | 0 | ## / # / # | True | False | False |
| stationary | rule_145 | 00001001 | 470 | 1 | `1` | 3 | 0 | 0 | #.##.#.#.##.### / ###.##.###.##.## / ##.##..##.##.# | True | False | False |
| stationary | rule_145 | 00001011 | 492 | 1 | `1` | 3 | 0 | 0 | #.# / #..# / ##.## | True | False | False |
| stationary | rule_145 | 00001101 | 492 | 1 | `1` | 3 | 0 | 0 | #..## / ##.### / #...# | True | False | False |
| stationary | rule_145 | 00001111 | 495 | 1 | `1` | 3 | 0 | 0 | #..# / #..# / ##.## | True | False | False |
| stationary | rule_145 | 00010101 | 489 | 1 | `1` | 3 | 0 | 0 | ##.##..##.##.# / #.##.#.#.##.### / ###.##.###.##.## | True | False | False |
| stationary | rule_145 | 00010111 | 487 | 2 | `01` | 3 | 0 | 0 | #...#...# / #..##...# / ##.###..## | True | False | False |
| stationary | rule_145 | 00011011 | 486 | 1 | `1` | 3 | 0 | 0 | #..# / ##.## / #..# | True | False | False |
| stationary | rule_145 | 00011111 | 486 | 1 | `1` | 3 | 0 | 0 | ###.##.###.##.## / ##.##..##.##.# / #.##.#.#.##.### | True | False | False |
| stationary | rule_145 | 00100101 | 489 | 1 | `1` | 3 | 0 | 0 | ##.##..##.##.# / #.##.#.#.##.### / ###.##.###.##.## | True | False | False |
| stationary | rule_145 | 00100111 | 495 | 1 | `1` | 3 | 0 | 0 | ###.##.###.##.## / ##.##..##.##.# / #.##.#.#.##.### | True | False | False |
| stationary | rule_145 | 00101111 | 490 | 1 | `1` | 3 | 0 | 0 | ## / #.# / ###.# | True | False | False |
| stationary | rule_145 | 00110111 | 495 | 1 | `1` | 3 | 0 | 0 | ###..#.###.#..##....# / #.###..###.#.#...## / #.#..#.#.######....# | True | False | False |
| stationary | rule_145 | 00111011 | 489 | 1 | `1` | 3 | 0 | 0 | ##.##..##.##.# / #.##.#.#.##.### / ###.##.###.##.## | True | False | False |
| stationary | rule_145 | 01011111 | 494 | 1 | `1` | 3 | 0 | 0 | ##### / #.# / #.## | True | False | False |
| stationary | rule_145 | 01101111 | 488 | 1 | `1` | 3 | 0 | 0 | ##.##..##.#.## / #.##.#.#.##.#.# / ###.##.###.##..# | True | False | False |
| stationary | rule_145 | 01111111 | 492 | 1 | `1` | 3 | 0 | 0 | ###.# / ### / #.## | True | False | False |
| stationary | rule_147 | 00000001 | 69 | 3 | `001` | 4 | 0 | 0 | #.#.#.# / #.#.#.## / #.#.#.# / ##.#.#.# | False | False | False |
| stationary | rule_147 | 00000101 | 51 | 3 | `101` | 4 | 0 | 0 | #.## / #.# / ##.# / #.# | False | False | False |
| stationary | rule_147 | 00000111 | 370 | 1 | `1` | 4 | 0 | 0 | #.#.....#...#.# / ##.#....##...#.## / #.#.....#...#.# / #.##....##.##.# | False | False | False |
| stationary | rule_147 | 00010101 | 407 | 1 | `1` | 4 | 0 | 0 | ##.#....##...#.## / #.#.....#...#.# / #.##....##.##.# / #.#.....#...#.# | False | False | False |
| stationary | rule_147 | 00011011 | 339 | 1 | `1` | 4 | 0 | 0 | ##...#.###.# / #...#.#.#.# / ##.##.###.## / #...#.#.#.# | False | False | False |
| stationary | rule_147 | 00011111 | 25 | 5 | `00011` | 4 | 0 | 0 | #.#.#.# / #.#.#.## / #.#.#.# / ##.#.#.# | False | False | False |
| stationary | rule_147 | 00100101 | 324 | 1 | `1` | 4 | 0 | 0 | #.#.#.#..##.#...#.# / ##.###.###..###.##.# / #.#.#.#.#..#....#.# / #.###.#######...#.## | False | False | False |
| stationary | rule_147 | 00101111 | 336 | 1 | `1` | 4 | 0 | 0 | #.#...#.....#.# / #.##.##....##.# / #.#...#.....#.# / ##.#...##....#.## | False | False | False |
| stationary | rule_147 | 00111101 | 283 | 1 | `1` | 4 | 0 | 0 | #.#.#.#..##.#...#.# / ##.###.###..###.##.# / #.#.#.#.#..#....#.# / #.###.#######...#.## | False | False | False |
| stationary | rule_147 | 01010111 | 73 | 1 | `1` | 4 | 0 | 0 | ##.# / #.# / #.## / #.# | False | False | False |
| stationary | rule_147 | 01011111 | 348 | 1 | `1` | 4 | 0 | 0 | ##.# / #.# / #.## / #.# | False | False | False |
| stationary | rule_147 | 01111111 | 57 | 3 | `010` | 4 | 0 | 0 | ####...#### / ##...## / #..#.#..# / #..###..# | False | False | False |
| stationary | rule_156 | 00000001 | 384 | 2 | `01` | 2 | 0 | 0 | ####### / ####### | False | False | False |
| stationary | rule_156 | 00000011 | 376 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_156 | 00000101 | 355 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_156 | 00000111 | 442 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_156 | 00001001 | 447 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_156 | 00001011 | 320 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_156 | 00001101 | 437 | 2 | `01` | 2 | 0 | 0 | #### / ###### | False | False | False |
| stationary | rule_156 | 00001111 | 323 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_156 | 00010011 | 462 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_156 | 00010101 | 304 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_156 | 00010111 | 445 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_156 | 00011001 | 387 | 2 | `01` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_156 | 00011011 | 455 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_156 | 00011101 | 378 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_156 | 00011111 | 453 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_156 | 00100101 | 466 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_156 | 00100111 | 443 | 3 | `001` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_156 | 00101011 | 316 | 3 | `001` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_156 | 00101101 | 456 | 2 | `01` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_156 | 00101111 | 319 | 3 | `001` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_156 | 00110101 | 454 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_156 | 00110111 | 451 | 3 | `001` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_156 | 00111011 | 362 | 3 | `001` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_156 | 00111101 | 469 | 2 | `01` | 2 | 0 | 0 | #### / ###### | False | False | False |
| stationary | rule_156 | 00111111 | 359 | 3 | `001` | 2 | 0 | 0 | ####### / ####### | False | False | False |
| stationary | rule_156 | 01010111 | 305 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_156 | 01011011 | 468 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_156 | 01011111 | 378 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_156 | 01101111 | 444 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_156 | 01111111 | 392 | 2 | `01` | 2 | 0 | 0 | ####### / ####### | False | False | False |
| stationary | rule_157 | 00000001 | 384 | 2 | `01` | 2 | 0 | 0 | ######### / ######### | False | False | False |
| stationary | rule_157 | 00000011 | 376 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_157 | 00000101 | 355 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_157 | 00000111 | 461 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_157 | 00001001 | 456 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_157 | 00001011 | 320 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_157 | 00001101 | 453 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_157 | 00001111 | 323 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_157 | 00010011 | 457 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_157 | 00010101 | 304 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_157 | 00010111 | 449 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_157 | 00011001 | 387 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_157 | 00011011 | 462 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_157 | 00011101 | 378 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_157 | 00011111 | 458 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_157 | 00100101 | 459 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_157 | 00100111 | 449 | 3 | `001` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_157 | 00101011 | 316 | 3 | `001` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_157 | 00101101 | 449 | 2 | `01` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_157 | 00101111 | 319 | 3 | `001` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_157 | 00110101 | 462 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_157 | 00110111 | 450 | 3 | `001` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_157 | 00111011 | 362 | 3 | `001` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_157 | 00111101 | 473 | 2 | `01` | 2 | 0 | 0 | #### / ###### | False | False | False |
| stationary | rule_157 | 00111111 | 359 | 3 | `001` | 2 | 0 | 0 | ####### / ####### | False | False | False |
| stationary | rule_157 | 01010111 | 305 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_157 | 01011011 | 459 | 2 | `01` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_157 | 01011111 | 378 | 2 | `01` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_157 | 01101111 | 449 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_157 | 01111111 | 392 | 2 | `01` | 2 | 0 | 0 | ####### / ####### | False | False | False |
| stationary | rule_198 | 00000001 | 366 | 1 | `1` | 2 | 0 | 0 | ########## / ######## | False | False | False |
| stationary | rule_198 | 00000011 | 367 | 1 | `1` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_198 | 00000101 | 369 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_198 | 00000111 | 480 | 1 | `1` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_198 | 00001001 | 462 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 00001011 | 462 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_198 | 00001101 | 391 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 00001111 | 393 | 1 | `1` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_198 | 00010011 | 350 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 00010101 | 345 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_198 | 00010111 | 379 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_198 | 00011001 | 467 | 1 | `1` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_198 | 00011011 | 467 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 00011101 | 487 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_198 | 00011111 | 475 | 1 | `1` | 2 | 0 | 0 | ## / #### | False | False | False |
| stationary | rule_198 | 00100101 | 455 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_198 | 00100111 | 475 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 00101011 | 447 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_198 | 00101101 | 462 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_198 | 00101111 | 465 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_198 | 00110101 | 321 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 00110111 | 363 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 00111011 | 446 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_198 | 00111101 | 374 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_198 | 00111111 | 375 | 1 | `1` | 2 | 0 | 0 | ###### / ######## | False | False | False |
| stationary | rule_198 | 01010111 | 360 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 01011011 | 448 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_198 | 01011111 | 375 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 01101111 | 465 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_198 | 01111111 | 373 | 2 | `01` | 2 | 0 | 0 | ######### / ######### | False | False | False |
| stationary | rule_199 | 00000001 | 366 | 1 | `1` | 2 | 0 | 0 | ######### / ######### | False | False | False |
| stationary | rule_199 | 00000011 | 367 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_199 | 00000101 | 369 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_199 | 00000111 | 484 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_199 | 00001001 | 452 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_199 | 00001011 | 453 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_199 | 00001101 | 391 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_199 | 00001111 | 393 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 00010011 | 350 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 00010101 | 345 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_199 | 00010111 | 379 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_199 | 00011001 | 473 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 00011011 | 473 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_199 | 00011101 | 482 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_199 | 00011111 | 475 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 00100101 | 459 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_199 | 00100111 | 473 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 00101011 | 455 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_199 | 00101101 | 458 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_199 | 00101111 | 461 | 1 | `1` | 2 | 0 | 0 | #### / ## | False | False | False |
| stationary | rule_199 | 00110101 | 321 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 00110111 | 363 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 00111011 | 452 | 1 | `1` | 2 | 0 | 0 | ###### / #### | False | False | False |
| stationary | rule_199 | 00111101 | 374 | 1 | `1` | 2 | 0 | 0 | ##### / ##### | False | False | False |
| stationary | rule_199 | 00111111 | 375 | 1 | `1` | 2 | 0 | 0 | ###### / ######## | False | False | False |
| stationary | rule_199 | 01010111 | 360 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 01011011 | 455 | 1 | `1` | 2 | 0 | 0 | ## / ## | False | False | False |
| stationary | rule_199 | 01011111 | 375 | 2 | `01` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 01101111 | 461 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_199 | 01111111 | 373 | 2 | `01` | 2 | 0 | 0 | ######### / ######### | False | False | False |
| stationary | rule_201 | 00000001 | 488 | 1 | `1` | 2 | 0 | 0 | ### / ## | False | False | False |
| stationary | rule_201 | 00000011 | 271 | 3 | `011` | 2 | 0 | 0 | ###.# / ##.# | False | False | False |
| stationary | rule_201 | 00000101 | 221 | 1 | `1` | 2 | 0 | 0 | ##.## / #.## | False | False | False |
| stationary | rule_201 | 00000111 | 245 | 2 | `01` | 2 | 0 | 0 | #.# / ### | False | False | False |
| stationary | rule_201 | 00001001 | 213 | 1 | `1` | 2 | 0 | 0 | #.## / #.### | False | False | False |
| stationary | rule_201 | 00001011 | 482 | 1 | `1` | 2 | 0 | 0 | ## / ### | False | False | False |
| stationary | rule_201 | 00001101 | 474 | 1 | `1` | 2 | 0 | 0 | ### / ### | False | False | False |
| stationary | rule_201 | 00001111 | 218 | 1 | `1` | 2 | 0 | 0 | ## / ### | False | False | False |
| stationary | rule_201 | 00010011 | 484 | 1 | `1` | 2 | 0 | 0 | ### / #.# | False | False | False |
| stationary | rule_201 | 00010101 | 489 | 1 | `1` | 2 | 0 | 0 | #.### / #.#.# | False | False | False |
| stationary | rule_201 | 00010111 | 491 | 1 | `1` | 2 | 0 | 0 | #### / #.# | False | False | False |
| stationary | rule_201 | 00011001 | 470 | 1 | `1` | 2 | 0 | 0 | #.## / #.# | False | False | False |
| stationary | rule_201 | 00011011 | 470 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_201 | 00011101 | 488 | 1 | `1` | 2 | 0 | 0 | ### / # | False | False | False |
| stationary | rule_201 | 00011111 | 474 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_201 | 00100101 | 205 | 3 | `001` | 2 | 0 | 0 | #.#..# / ###..# | False | False | False |
| stationary | rule_201 | 00100111 | 233 | 4 | `0001` | 2 | 0 | 0 | #.#....# / #.##...# | False | False | False |
| stationary | rule_201 | 00101011 | 243 | 3 | `001` | 2 | 0 | 0 | #.....## / #.....# | False | False | False |
| stationary | rule_201 | 00101101 | 184 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_201 | 00101111 | 182 | 1 | `1` | 2 | 0 | 0 | ### / ## | False | False | False |
| stationary | rule_201 | 00110101 | 198 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_201 | 00110111 | 234 | 2 | `01` | 2 | 0 | 0 | # / ## | False | False | False |
| stationary | rule_201 | 00111011 | 219 | 3 | `011` | 2 | 0 | 0 | #### / ### | False | False | False |
| stationary | rule_201 | 00111101 | 179 | 3 | `001` | 2 | 0 | 0 | ## / ### | False | False | False |
| stationary | rule_201 | 00111111 | 179 | 2 | `01` | 2 | 0 | 0 | # / ## | False | False | False |
| stationary | rule_201 | 01010111 | 290 | 1 | `1` | 2 | 0 | 0 | #.## / #.# | False | False | False |
| stationary | rule_201 | 01011011 | 473 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_201 | 01011111 | 477 | 1 | `1` | 2 | 0 | 0 | ## / # | False | False | False |
| stationary | rule_201 | 01101111 | 223 | 3 | `110` | 2 | 0 | 0 | ### / ## | False | False | False |
| stationary | rule_201 | 01111111 | 178 | 3 | `010` | 2 | 0 | 0 | #.# / ### | False | False | False |

## Rotation Validation

Up to ten distinct positive rules were retested across all eight rotations of
their representative background, prioritizing new rules and new period/speed
classes.

| kind | rule | canonical_background | witness | T | drift | matching_rotations | matching_phases | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stationary | rule_62 | 00000001 | `1` | 3 | 0 | 7/8 | 0, 1, 2, 3, 4, 5, 6 | phase-dependent |
| stationary | rule_118 | 00000001 | `1` | 3 | 0 | 7/8 | 0, 1, 2, 3, 4, 5, 6 | phase-dependent |
| stationary | rule_131 | 00000011 | `1` | 3 | 0 | 6/8 | 0, 1, 2, 3, 4, 5 | phase-dependent |
| stationary | rule_145 | 00000011 | `1` | 3 | 0 | 6/8 | 0, 1, 2, 3, 4, 5 | phase-dependent |
| moving | rule_9 | 00001001 | `1000` | 3 | -2 | 1/8 | 0 | phase-dependent |
| moving | rule_65 | 00000001 | `1` | 3 | 2 | 1/8 | 0 | phase-dependent |
| moving | rule_111 | 00011111 | `1` | 3 | -2 | 1/8 | 0 | phase-dependent |
| moving | rule_125 | 00000011 | `1` | 3 | 2 | 1/8 | 0 | phase-dependent |
| moving | rule_45 | 00010011 | `001` | 6 | 6 | 1/8 | 0 | phase-dependent |
| stationary | rule_73 | 00001001 | `1` | 6 | 0 | 4/8 | 0, 3, 5, 6 | phase-dependent |

- Rotationally robust samples: `0/10`.
- Phase-dependent samples: `10/10`.

This validation changes the phase of the periodic background relative to a
fixed centered IC. Phase dependence therefore demonstrates physical coupling
to background phase; it does not by itself prove an observer artifact. A
strict observer-equivariance test would co-translate both background and IC.

## Explicit Answers

1. **Do new rules appear beyond the period-1/2/4 sweep?** Yes. New stationary rules: rule_62, rule_118, rule_131, rule_145; new moving rules: rule_7, rule_9, rule_21, rule_25, rule_31, rule_45, rule_61, rule_65, rule_67, rule_75, rule_87, rule_88, rule_89, rule_101, rule_103, rule_111, rule_125, rule_173, rule_229.
2. **Do oscillators with T > 4 appear?** Yes. New observed periods: 6, 8, 10, 12, 15.
3. **Do speeds outside 0, 0.5, and 1 cell/step appear?** Yes. New observed absolute speeds: 0.666667 cells/step.

## Interpretation

This experiment changes only the primitive background period. Results remain
background-conditioned local perturbations, not global periodicity of the
background orbit. Primitive period-8 backgrounds add both rule coverage and
new dynamical classes: fundamental periods up to 15 and speed 2/3. The sampled
novelties are phase-sensitive rather than invariant across all eight background
phases, so each claim must retain its background-phase condition.
