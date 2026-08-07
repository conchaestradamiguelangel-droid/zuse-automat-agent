# Fase 95 - Frozen length-8 hypercube completion

## Question

Are the fragmented physical classes from Fase 94 disconnected inside individual background/rule Q8 cubes, or only split across different cubes that cannot share Hamming edges?

## Frozen protocol

- Universe: only background/rule cubes that contain at least one of the 1,829 Fase-93 long-period states.
- Each cube is the standard Q8: 256 absolute length-8 words, degree 8, 2,048 directed and 1,024 undirected Hamming-1 edges.
- Both Fase-90 cohorts use the same 502-word generator. Shorter baseline encodings are required to reproduce an exact length-8 alias before inclusion.
- Every non-zero node is classified by an explicit Stage-A LedgerRecord. Word 00000000 remains an unsimulated boundary.
- No edges are created between different cohorts, rules, or background indices.
- No simulation is executed.

## Source and replay gates

- Long nodes reconciled through exact length-8 aliases: 1829
- Baseline descriptors -> unique long nodes: 160 -> 120
- Primitive-length-8 descriptors -> unique long nodes: 3136 -> 1709
- Fase-94 directed edges replayed field by field: 14632
- Fase-94 replay mismatches: 0
- Ledger/candidate reconciliation failures: 0

## Complete local Q8 atlas

- Cubes reconstructed: 48
- Cubes by cohort: `{"baseline_period_1_2_4": 6, "primitive_len8": 42}`
- Cubes by rule: `{"109": 24, "73": 24}`
- Nodes: 12288
- Directed edges: 98304
- Undirected edges: 49152
- Long-period occupied nodes: 1829
- Long-period occupancy fraction: 0.148844
- Node-category distribution: `{"EXTINCT": 103, "HISTORICAL_SOURCE_POSITIVE": 9096, "LONG_PERIOD_CAP_CANDIDATE": 1829, "SPAN_ESCAPE": 1058, "STATIC_T1": 106, "ZERO_IC_BOUNDARY_UNSAMPLED": 48, "ZERO_INITIAL_DEFECT": 48}`

## Fragmentation decomposition

- CONNECTED_SINGLE_CUBE: 51
- CROSS_CUBE_ONLY: 21
- WITHIN_CUBE_FRAGMENTED: 41
- MIXED: 79
- Classes with any within-cube fragmentation: 120
- Classes fragmented only by cube separation: 21
- Minimum inter-component Hamming distribution: `{"2": 206, "3": 47, "4": 10, "5": 9}`

## Largest class occupancies

| nodes | cubes | components | label | fragmented cubes | min Hamming | rules | T |
|---:|---:|---:|---|---:|---:|---|---|
| 77 | 10 | 17 | MIXED | 4 | 2 | [109] | [24] |
| 70 | 10 | 22 | MIXED | 6 | 2 | [73] | [24] |
| 48 | 7 | 15 | MIXED | 2 | 2 | [73] | [24] |
| 48 | 12 | 32 | MIXED | 9 | 2 | [109] | [30] |
| 48 | 6 | 20 | MIXED | 6 | 2 | [73] | [18] |
| 46 | 6 | 20 | MIXED | 6 | 2 | [73] | [18] |
| 46 | 12 | 30 | MIXED | 9 | 2 | [109] | [30] |
| 45 | 8 | 21 | MIXED | 6 | 2 | [109] | [18] |
| 45 | 6 | 20 | MIXED | 6 | 2 | [109] | [18] |
| 44 | 12 | 28 | MIXED | 9 | 2 | [73] | [30] |
| 38 | 6 | 18 | MIXED | 5 | 2 | [109] | [18] |
| 36 | 6 | 18 | MIXED | 3 | 2 | [109] | [24] |
| 36 | 6 | 16 | MIXED | 6 | 2 | [109] | [18] |
| 34 | 6 | 17 | MIXED | 4 | 2 | [73] | [18] |
| 34 | 5 | 12 | MIXED | 4 | 2 | [109] | [18] |
| 34 | 12 | 24 | MIXED | 8 | 2 | [73] | [30] |
| 33 | 6 | 11 | MIXED | 4 | 2 | [73] | [18] |
| 33 | 8 | 18 | MIXED | 5 | 2 | [73] | [18] |
| 33 | 7 | 19 | MIXED | 7 | 2 | [73] | [18] |
| 32 | 7 | 18 | MIXED | 7 | 2 | [109] | [18] |

## Verdict

`MIXED_FRAGMENTATION_STRUCTURE`

This result distinguishes fragmentation inside one frozen local Q8 cube from separation across different background/rule cubes. It is not a universal ECA basin topology.

## Methodological limits

- The atlas is complete only for length-8 IC words on positions 124..131 and only for frozen backgrounds that contain observed long-period states.
- Word 00000000 was excluded by the historical generator and is retained as an unsimulated boundary node.
- Short-period and external states carry explicit ledger categories but no long-period physical-class identity.
- No inference is made about WIDTH=256 states outside the central eight-bit subspace.
- No paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.
