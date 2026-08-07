# Fase 91 - Long-period attractor atlas

## Question

Do the 3,296 period-cap misses confirmed by Fase 90 represent distinct physical attractors, or input-condition aliases feeding a smaller set of recurrent cycles?

## Frozen protocol

- Input: exactly the 3,296 Stage-B rows confirmed by Fase 90.
- Replay: WIDTH=256, burn-in=80, t=0..1000, exact tail t=500..1000, maximum period 120.
- Abort gate: any kind/period/drift mismatch against Stage B aborts the analysis.
- Strict physical identity is computed from the resulting attractor, never from the input key.
- Joint background/defect cycles are canonicalized over lcm(T_defect,T_background), with one shared temporal rotation.
- Morphology retains the reduced locking ratio; different locking ratios cannot collapse into one morphology class.
- Reflection and rule_73/rule_109 black-white conjugacy are separate quotients, not strict identity.

## Reconciliation

- Source rows: 3296
- Unique physical input keys: 3296
- Stage-B mismatches: 0
- Maximum joint period: 120

## Atlas

- Strict physical attractor classes: 192
- Input aliases collapsed by strict physical identity: 3104
- Defect morphology classes: 123
- Reflection-quotient morphology classes: 65
- rule_73/rule_109 conjugacy classes: 123
- Strict classes with more than one input alias: 169
- Largest strict physical basin in this IC census: 175
- Morphology classes spanning both rules: 69
- Conjugacy classes spanning both rules: 69

## Period structure

- Defect periods: `{"120": 27, "18": 1703, "24": 750, "26": 5, "30": 545, "40": 53, "42": 18, "48": 44, "60": 105, "66": 31, "90": 15}`
- Background periods: `{"1": 160, "2": 735, "3": 2401}`
- Reduced locking ratios: `{"10:1": 545, "13:1": 5, "14:1": 18, "16:1": 44, "18:1": 160, "20:1": 158, "22:1": 31, "30:1": 15, "40:1": 27, "6:1": 866, "8:1": 750, "9:1": 677}`

## Largest strict physical classes

| aliases | rules | T defect | T background | ratio | examples |
|---:|---|---|---|---|---|
| 175 | [109] | [24] | [3] | [(8, 1)] | r109/00001001/001; r109/00001001/011; r109/00001001/0001 |
| 161 | [73] | [24] | [3] | [(8, 1)] | r73/00000011/10010101; r73/00000011/10100101; r73/00000011/10101001 |
| 125 | [73] | [30] | [3] | [(10, 1)] | r73/00000011/00011; r73/00000011/000011; r73/00000011/100000 |
| 125 | [109] | [30] | [3] | [(10, 1)] | r109/00000011/001; r109/00000011/011; r109/00000011/101 |
| 100 | [73] | [30] | [3] | [(10, 1)] | r73/00000011/0010; r73/00000011/00100; r73/00000011/000100 |
| 96 | [109] | [18] | [2] | [(9, 1)] | r109/00100101/00010; r109/00100101/100000; r109/00100101/100010 |
| 93 | [109] | [30] | [3] | [(10, 1)] | r109/00000011/11101; r109/00000011/011101; r109/00000011/0111010 |
| 92 | [73] | [18] | [2] | [(9, 1)] | r73/00001011/00001; r73/00001011/11101; r73/00001011/000001 |
| 90 | [73] | [18] | [2] | [(9, 1)] | r73/00001011/1000; r73/00001011/10000; r73/00001011/10111 |
| 89 | [73] | [24] | [3] | [(8, 1)] | r73/00000011/0000001; r73/00000011/1000001; r73/00000011/00000001 |
| 89 | [109] | [18] | [2] | [(9, 1)] | r109/00100101/11000; r109/00100101/11010; r109/00100101/111000 |
| 88 | [109] | [18] | [2] | [(9, 1)] | r109/00100101/01010; r109/00100101/10110; r109/00100101/11110 |
| 78 | [109] | [18] | [3] | [(6, 1)] | r109/00001001/01000001; r109/00001001/01110100; r109/00001001/01110111 |
| 69 | [109] | [18] | [3] | [(6, 1)] | r109/00101011/1000001; r109/00101011/01000001; r109/00101011/01010001 |
| 65 | [109] | [18] | [3] | [(6, 1)] | r109/00001001/01111100; r109/00001001/01111101; r109/00001011/01111100 |

## Verdict

`LONG_PERIOD_ATTRACTOR_ATLAS_BUILT`

The verdict is descriptive. Collapse counts quantify exact equivalence under the predeclared signatures; they do not by themselves establish a universal law outside the two frozen Fase-90 cohorts.

## Methodological limits

- The atlas covers only the 3,296 confirmed period-cap misses from the frozen baseline and primitive-length-8 cohorts.
- Strict identity is translation-invariant but preserves the complete background state relative to the defect and their joint temporal phase.
- Morphology identity is weaker than physical identity and must not be interpreted as proof of the same basin or background-conditioned mechanism.
- No ANF-gradient measurement is performed in this phase.
- No paper, DOI, tag, release, or v1.34 artifact is modified.
