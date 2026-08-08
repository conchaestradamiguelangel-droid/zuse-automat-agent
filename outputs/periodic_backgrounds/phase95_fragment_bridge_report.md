# Fase 96 - Intracube fragment bridge filtration

## Question

Which Q8 state families connect the disconnected components of one physical long-period class inside the same frozen background/rule cube?

## Frozen source and gates

- Source raw SHA-256: `1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3`
- Source canonical JSON SHA-256: `57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429`
- Fragmented class/cube intersections: 272
- Unordered component pairs: 979
- Reconciliation failures: 0
- Input is only the committed Fase-95 JSON; no Stage-A ledger and no ECA simulation is used.

## Filtration

- F1: all long-period classes.
- F2: F1 plus historical short-period positives and static-T1 states.
- F3: every ledger-backed non-zero state.
- F4: full Q8 including the unsimulated zero word, diagnostic only.

## Pairwise closure by any Q8 path

`{"F1_ALL_LONG_PERIOD": 627, "F2_ALL_CONFIRMED_PERSISTENT": 350, "F3_ALL_LEDGER_BACKED_NONZERO": 2}`

- Pairs unbridged without zero word: 0
- Intersection closure levels: `{"F1_ALL_LONG_PERIOD": 192, "F2_ALL_CONFIRMED_PERSISTENT": 78, "F3_ALL_LEDGER_BACKED_NONZERO": 2}`

## Exhaustive shortest-path anatomy

- Minimum pairwise Hamming distribution: `{"2": 417, "3": 244, "4": 189, "5": 96, "6": 31, "7": 2}`
- Best shortest-path levels: `{"F1_ALL_LONG_PERIOD": 424, "F2_ALL_CONFIRMED_PERSISTENT": 553, "F3_ALL_LEDGER_BACKED_NONZERO": 2}`
- Worst shortest-path levels: `{"F1_ALL_LONG_PERIOD": 126, "F2_ALL_CONFIRMED_PERSISTENT": 743, "F3_ALL_LEDGER_BACKED_NONZERO": 59, "F4_FULL_Q8_DIAGNOSTIC": 51}`
- Total shortest paths counted: 51778
- Shortest paths using zero word: 1683
- Pairs with at least one zero-word shortest path: 51
- Pairs whose every shortest path requires zero: 0

## F3 category ablation

- Pairs first closing at F3: 2
- Necessary-category counts: `{"SPAN_ESCAPE": 2}`
- Sufficient-over-F2 counts: `{"SPAN_ESCAPE": 2}`

## Example component pairs

| closure | d | shortest paths | best | worst | zero paths | class | cube |
|---|---:|---:|---|---|---:|---|---|
| F3_ALL_LEDGER_BACKED_NONZERO | 4 | 24 | F3_ALL_LEDGER_BACKED_NONZERO | F3_ALL_LEDGER_BACKED_NONZERO | 0 | 5e7461cb7292 | primitive_len8|rule_073|bg_029 |
| F3_ALL_LEDGER_BACKED_NONZERO | 4 | 24 | F3_ALL_LEDGER_BACKED_NONZERO | F3_ALL_LEDGER_BACKED_NONZERO | 0 | 82c2ce34723e | primitive_len8|rule_109|bg_000 |
| F2_ALL_CONFIRMED_PERSISTENT | 7 | 5040 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 144 | 180bf1a61de4 | primitive_len8|rule_109|bg_022 |
| F2_ALL_CONFIRMED_PERSISTENT | 6 | 720 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 48 | 0c86a2769da4 | primitive_len8|rule_073|bg_018 |
| F2_ALL_CONFIRMED_PERSISTENT | 6 | 720 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 48 | 5e42eb39ab94 | primitive_len8|rule_073|bg_020 |
| F2_ALL_CONFIRMED_PERSISTENT | 6 | 720 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 48 | 6a5a2781f889 | primitive_len8|rule_109|bg_022 |
| F2_ALL_CONFIRMED_PERSISTENT | 6 | 720 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 48 | a3799bccfe37 | primitive_len8|rule_073|bg_017 |
| F2_ALL_CONFIRMED_PERSISTENT | 6 | 720 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 36 | 3a3c199b612f | primitive_len8|rule_073|bg_011 |
| F2_ALL_CONFIRMED_PERSISTENT | 5 | 240 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 12 | 022a65471ba2 | primitive_len8|rule_073|bg_011 |
| F2_ALL_CONFIRMED_PERSISTENT | 5 | 120 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 12 | 09626463fed3 | primitive_len8|rule_073|bg_011 |
| F2_ALL_CONFIRMED_PERSISTENT | 5 | 120 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 12 | 3a3c199b612f | primitive_len8|rule_073|bg_011 |
| F2_ALL_CONFIRMED_PERSISTENT | 5 | 120 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 12 | 3a3c199b612f | primitive_len8|rule_073|bg_011 |
| F2_ALL_CONFIRMED_PERSISTENT | 5 | 120 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 12 | ed4d2f753f8c | primitive_len8|rule_109|bg_005 |
| F2_ALL_CONFIRMED_PERSISTENT | 5 | 240 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 12 | faf2b2de6911 | primitive_len8|rule_109|bg_022 |
| F2_ALL_CONFIRMED_PERSISTENT | 4 | 24 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 4 | 2ff0747616a6 | primitive_len8|rule_109|bg_007 |
| F2_ALL_CONFIRMED_PERSISTENT | 3 | 12 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 2 | 3016299516c1 | primitive_len8|rule_073|bg_008 |
| F2_ALL_CONFIRMED_PERSISTENT | 3 | 6 | F2_ALL_CONFIRMED_PERSISTENT | F4_FULL_Q8_DIAGNOSTIC | 2 | 3016299516c1 | primitive_len8|rule_073|bg_008 |
| F2_ALL_CONFIRMED_PERSISTENT | 6 | 720 | F2_ALL_CONFIRMED_PERSISTENT | F3_ALL_LEDGER_BACKED_NONZERO | 0 | 022a65471ba2 | primitive_len8|rule_073|bg_011 |
| F2_ALL_CONFIRMED_PERSISTENT | 6 | 720 | F2_ALL_CONFIRMED_PERSISTENT | F2_ALL_CONFIRMED_PERSISTENT | 0 | 0c86a2769da4 | primitive_len8|rule_073|bg_017 |
| F2_ALL_CONFIRMED_PERSISTENT | 6 | 720 | F2_ALL_CONFIRMED_PERSISTENT | F3_ALL_LEDGER_BACKED_NONZERO | 0 | 180bf1a61de4 | primitive_len8|rule_109|bg_022 |

## Verdict

`FRAGMENT_BRIDGE_FILTRATION_MAPPED`

The filtration maps local Q8 corridors between observed long-period fragments. It does not measure dynamical transitions or universal basin connectivity.

## Methodological limits

- The 979 pairs belong only to the 48 frozen Fase-95 Q8 cubes.
- Filtration levels classify initial states from prior detector outputs; they are not transition probabilities.
- The zero word was never simulated and is used only to count optional diagnostic shortest paths.
- No Stage-A ledger, ECA simulation, paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.
