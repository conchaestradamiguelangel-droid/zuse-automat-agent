# Rule 73/109 unit-cardinality historical-period potency - Fase 100

## Protocol

Each historical node is added alone to the pair-specific F1 graph. The analysis uses exact Q8 max-flow connectivity and performs no CA simulation.

## Gates

- Frozen cubes: `48`
- Physical historical nodes: `9096`
- Unit target-node exposures: `43425`
- Target-period strata: `919`
- Within-target period comparisons per metric: `1584`
- Reconciliation failures: `0`
- Monotonicity failures: `0`
- Fase-99 replay: `EXACT_TARGET_STRATUM_AND_GROUP_REPLAY`

## Global partition

- Unit connectivity `(kappa_v,lambda_e)`: `{"1,1": 41859, "1,2": 61, "2,2": 1499, "2,3": 6}`
- Same-node rescue of both metrics: `1505`
- Edge-only rescues: `61`
- Vertex-only rescues: `0`
- kappa group relations: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 126, "NONRESCUING_PERIOD_CONTROL": 381, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 412}`
- lambda group relations: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 139, "NONRESCUING_PERIOD_CONTROL": 365, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 415}`

## Period potency

| Period | Exposures | Strata | kappa rescues | kappa micro | kappa strata hit | lambda rescues | lambda micro | lambda strata hit |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 4071 | 41 | 86 | 0.021125 | 26 | 86 | 0.021125 | 26 |
| 3 | 11656 | 206 | 419 | 0.035947 | 105 | 419 | 0.035947 | 105 |
| 5 | 250 | 28 | 0 | 0.000000 | 0 | 0 | 0.000000 | 0 |
| 6 | 22644 | 219 | 792 | 0.034976 | 159 | 853 | 0.037670 | 162 |
| 8 | 263 | 41 | 26 | 0.098859 | 17 | 26 | 0.098859 | 17 |
| 10 | 273 | 33 | 2 | 0.007326 | 2 | 2 | 0.007326 | 2 |
| 12 | 3362 | 211 | 154 | 0.045806 | 82 | 154 | 0.045806 | 82 |
| 15 | 906 | 140 | 26 | 0.028698 | 21 | 26 | 0.028698 | 21 |

## Relation to full-period groups

### T=2

- `kappa_v`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 15, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 26}`
- `lambda_e`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 15, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 26}`

### T=3

- `kappa_v`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 49, "NONRESCUING_PERIOD_CONTROL": 52, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 105}`
- `lambda_e`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 65, "NONRESCUING_PERIOD_CONTROL": 36, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 105}`

### T=5

- `kappa_v`: `{"NONRESCUING_PERIOD_CONTROL": 28}`
- `lambda_e`: `{"NONRESCUING_PERIOD_CONTROL": 28}`

### T=6

- `kappa_v`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 32, "NONRESCUING_PERIOD_CONTROL": 28, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 159}`
- `lambda_e`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 29, "NONRESCUING_PERIOD_CONTROL": 28, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 162}`

### T=8

- `kappa_v`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 1, "NONRESCUING_PERIOD_CONTROL": 23, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 17}`
- `lambda_e`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 1, "NONRESCUING_PERIOD_CONTROL": 23, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 17}`

### T=10

- `kappa_v`: `{"NONRESCUING_PERIOD_CONTROL": 31, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 2}`
- `lambda_e`: `{"NONRESCUING_PERIOD_CONTROL": 31, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 2}`

### T=12

- `kappa_v`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 29, "NONRESCUING_PERIOD_CONTROL": 100, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 82}`
- `lambda_e`: `{"COLLECTIVE_ONLY_PERIOD_RESCUE": 29, "NONRESCUING_PERIOD_CONTROL": 100, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 82}`

### T=15

- `kappa_v`: `{"NONRESCUING_PERIOD_CONTROL": 119, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 21}`
- `lambda_e`: `{"NONRESCUING_PERIOD_CONTROL": 119, "SINGLE_NODE_EXPLAINS_GROUP_RESCUE": 21}`

## Interpretation

The micro and macro rates quantify one-node topological potency associated with each period. They do not establish period causality. Collective-only strata identify full-period rescue that cannot be attributed to any one node in isolation.

## Verdict

`UNIT_CARDINALITY_PERIOD_POTENCY_MAPPED`

## Methodological limits

- Unit cardinality removes the immediate advantage of adding more nodes, but not geometric placement.
- Collective rescue by two or more nodes is not decomposed in this phase.
- Period labels are associated metadata, not demonstrated temporal causes.
- The atlas is limited to 219 bottlenecks in 48 frozen Q8 cubes.
- No WIDTH=256 basin probability or temporal transition probability is estimated.
