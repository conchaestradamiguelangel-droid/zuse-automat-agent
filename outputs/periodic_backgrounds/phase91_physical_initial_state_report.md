# Fase 93 - Physical initial-state deduplication

## Question

How much of the apparent long-period basin occupancy in Fase 91 is due to distinct physical initial states, and how much is due to multiple word-length/padding encodings of the same state?

## Frozen identity

- Source: the versioned Fase-91 JSON with its exact predeclared SHA-256.
- Strict initial identity: rule, complete background state at t=0, and absolute initial defect positions on WIDTH=256.
- Placement: start = WIDTH//2 - word_len//2, checked independently against the historical initial_diff implementation.
- No translation, rotation, reflection, or temporal canonicalization is used.
- Final class is read directly from the verified Fase-91 physical_class_sha256 field; no dynamics or attractor hash is recomputed.
- Gate: one strict initial state mapping to multiple final physical classes aborts with INITIAL_STATE_DETERMINISM_VIOLATION.

## Reconciliation

- Raw Fase-91 input rows: 3296
- Strict physical initial states: 1829
- Encoding aliases removed: 1467
- Determinism conflicts: 0
- Final physical attractor classes retained: 192

## Observed long-period basin occupancy

- Largest raw descriptor occupancy: 175
- Largest deduplicated physical-state occupancy: 77
- Singleton physical classes after deduplication: 29
- Maximum encodings of one physical initial state: 8
- Encoding multiplicity distribution: `{"1": 1014, "2": 453, "3": 190, "4": 93, "5": 48, "6": 25, "7": 4, "8": 2}`
- Strict initial states under the separate rule_73/rule_109 conjugacy quotient: 1769

## Largest deduplicated occupancies

| unique states | raw inputs | encoding aliases | rules | T defect | examples |
|---:|---:|---:|---|---|---|
| 77 | 175 | 98 | [109] | [24] | r109/00001001/001; r109/00001001/011; r109/00001001/0001 |
| 70 | 161 | 91 | [73] | [24] | r73/00000011/10010101; r73/00000011/10100101; r73/00000011/10101001 |
| 48 | 89 | 41 | [73] | [24] | r73/00000011/0000001; r73/00000011/1000001; r73/00000011/00000001 |
| 48 | 93 | 45 | [109] | [30] | r109/00000011/11101; r109/00000011/011101; r109/00000011/0111010 |
| 48 | 90 | 42 | [73] | [18] | r73/00001011/1000; r73/00001011/10000; r73/00001011/10111 |
| 46 | 92 | 46 | [73] | [18] | r73/00001011/00001; r73/00001011/11101; r73/00001011/000001 |
| 46 | 125 | 79 | [109] | [30] | r109/00000011/001; r109/00000011/011; r109/00000011/101 |
| 45 | 78 | 33 | [109] | [18] | r109/00001001/01000001; r109/00001001/01110100; r109/00001001/01110111 |
| 45 | 96 | 51 | [109] | [18] | r109/00100101/00010; r109/00100101/100000; r109/00100101/100010 |
| 44 | 125 | 81 | [73] | [30] | r73/00000011/00011; r73/00000011/000011; r73/00000011/100000 |
| 38 | 89 | 51 | [109] | [18] | r109/00100101/11000; r109/00100101/11010; r109/00100101/111000 |
| 36 | 45 | 9 | [109] | [24] | r109/00010011/0100100; r109/00010011/0100110; r109/00010011/0101100 |
| 36 | 88 | 52 | [109] | [18] | r109/00100101/01010; r109/00100101/10110; r109/00100101/11110 |
| 34 | 63 | 29 | [73] | [18] | r73/00001011/00101; r73/00001011/000101; r73/00001011/110001 |
| 34 | 69 | 35 | [109] | [18] | r109/00101011/1000001; r109/00101011/01000001; r109/00101011/01010001 |

## Verdict

`PHYSICAL_INITIAL_STATE_BASINS_DEDUPLICATED`

Fase-91 raw alias counts are not basin volumes. The deduplicated counts quantify observed long-period basin occupancy only within the frozen protocol and candidate set.

## Methodological limits

- The 3,296 cases remain restricted to the two frozen Fase-90 cohorts: baseline_period_1_2_4 and primitive_len8.
- Only confirmed long-period detector misses are included; short-period positives, negatives, and zero ICs are outside this occupancy denominator.
- Deduplicated occupancy is not a universal basin volume in the complete ECA configuration space.
- The conjugacy quotient is reported separately and never replaces strict physical identity.
- No simulation, ANF measurement, paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.
