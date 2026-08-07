# Fase 94 - Catalog-induced Hamming-1 topology

## Question

Within the frozen observed long-period occupancy, does a one-cell intervention remain in the same attractor, move to another long-period class, or leave the recovered long-period set?

## Frozen protocol and positive evidence

- Nodes: exactly the 1,829 strict physical initial states from Fase 93.
- Interventions: one flip at each absolute position 124..131; exactly eight directed flips per node.
- Every non-zero target is addressed in the complete Fase-90 Stage-A binary ledger by cohort, rule, background index, and length-8 IC index.
- Ledger size and SHA-256 are validated against each Stage-A manifest before graph construction.
- Absence is never interpreted as a negative. A represented target outside the long-period set must have an explicit non-candidate LedgerRecord.
- In-set edges require reciprocal cap-candidate evidence and a real reverse edge at the same flipped cell.
- No simulation is executed.

## Reconciliation

- Nodes: 1829
- Directed interventions: 14632
- Ledger-backed non-zero interventions: 14551
- Zero-IC unsampled interventions: 81
- Reconciliation failures: 0
- Internal reciprocal edge failures: 0

## Directed outcomes

- Same physical class: 1818
- Different long-period class: 3484
- Represented outside long-period set: 9249
- Zero IC unsampled: 81
- Retained anywhere in long-period set: 0.362356
- Retained in the same class: 0.124248

## Explicit ledger outcomes outside the long-period set

`{"EXTINCT": 39, "HISTORICAL_SOURCE_POSITIVE": 9037, "SPAN_ESCAPE": 104, "STATIC_T1": 49, "ZERO_INITIAL_DEFECT": 20}`

## Graph structure

- Undirected in-set edges: 2651
- Undirected same-class edges: 909
- Undirected cross-class edges: 1742
- Weighted class-to-class links: 551
- Internally connected physical classes: 51
- Internally fragmented physical classes: 141
- Maximum internal component count: 32
- Nodes with all eight flips in the same class: 0
- Internal component-count distribution: `{"1": 51, "10": 9, "11": 1, "12": 4, "13": 1, "14": 1, "15": 2, "16": 1, "17": 2, "18": 6, "19": 1, "2": 38, "20": 3, "21": 1, "22": 1, "24": 1, "28": 1, "3": 23, "30": 1, "32": 1, "4": 12, "5": 10, "6": 7, "7": 7, "8": 5, "9": 2}`

## Largest class occupancies and internal topology

| nodes | components | same exits | cross exits | ledger exits | zero exits | rules | T |
|---:|---:|---:|---:|---:|---:|---|---|
| 77 | 17 | 174 | 103 | 331 | 8 | [109] | [24] |
| 70 | 22 | 134 | 99 | 327 | 0 | [73] | [24] |
| 48 | 15 | 88 | 60 | 235 | 1 | [73] | [24] |
| 48 | 32 | 34 | 50 | 300 | 0 | [109] | [30] |
| 48 | 20 | 60 | 73 | 249 | 2 | [73] | [18] |
| 46 | 20 | 56 | 84 | 228 | 0 | [73] | [18] |
| 46 | 30 | 34 | 36 | 298 | 0 | [109] | [30] |
| 45 | 21 | 64 | 90 | 203 | 3 | [109] | [18] |
| 45 | 20 | 54 | 59 | 242 | 5 | [109] | [18] |
| 44 | 28 | 34 | 33 | 284 | 1 | [73] | [30] |
| 38 | 18 | 42 | 48 | 212 | 2 | [109] | [18] |
| 36 | 18 | 50 | 55 | 180 | 3 | [109] | [24] |
| 36 | 16 | 42 | 58 | 184 | 4 | [109] | [18] |
| 34 | 17 | 34 | 57 | 178 | 3 | [73] | [18] |
| 34 | 12 | 48 | 49 | 172 | 3 | [109] | [18] |

## Verdict

`LONG_PERIOD_BASIN_TOPOLOGY_MAPPED`

This is the catalog-induced Hamming-1 topology of observed long-period occupancy. It is not the complete basin topology of the ECA configuration space.

## Methodological limits

- Nodes are restricted to the 1,829 deduplicated long-period states from the two frozen Fase-90 cohorts.
- The intervention window is the fixed central length-8 IC support; flips elsewhere in WIDTH=256 are not tested.
- REPRESENTED_OUTSIDE_LONG_PERIOD_SET is backed by an explicit Stage-A ledger record but is not called negative: it includes short-period positives and other detector outcomes.
- Zero IC was excluded by the historical generator and remains an unsimulated, separately counted boundary.
- No paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.
