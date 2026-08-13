# Fase 99 - Historical rescue decomposition by source period

## Question

Which historical stationary source-period families are sufficient or jointly required to rescue the 219 F1 unit bottlenecks?

## Frozen inputs and gates

- Fase-95 raw/canonical: `1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3` / `57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429`
- Fase-98 raw/canonical: `0e0037a8cfef81e0f190275636977189d1d4d46db009a909cbc017e0a7693297` / `42eeed0fe5f8d4f75013bfd9d29466a7fc6600bf4bce1b1b82ae30707d3cb387`
- Fase-99 result raw/canonical: `df46d597fbb73a0cd5d048047c3c54a98ca479d9a0ff3a8d0bb6528392f46170` / `98b075368ed7129d229bfe8bbf8aeac19d8d7e2958b2df1f344672623e5efc62`
- Replay: `EXACT_TARGET_AND_EXTREME_REPLAY`
- Reconciliation/monotonicity failures: 0/0

## Denominators

- Historical nodes gated: 9096
- Targets: 219; excluded controls: 408
- Available-period counts: `{"3": 38, "4": 140, "5": 21, "7": 20}`
- Subset profiles / cover relations: 5776 / 15576

## Historical abundance

- Global nodes by period: `{"10": 167, "12": 713, "15": 163, "2": 1600, "3": 2054, "5": 54, "6": 4216, "8": 129}`
- Target-cube availability by period: `{"10": 33, "12": 211, "15": 140, "2": 41, "3": 206, "5": 28, "6": 219, "8": 41}`

These counts expose abundance as a confounder; they are not causal weights.

## Rescue signatures

### kappa_v

- Labels: `{"MIXED_SINGLETON_AND_INTERACTION_MINIMA": 26, "MULTIPLE_SINGLETON_ALTERNATIVES": 188, "UNIQUE_SINGLETON_RESCUE": 5}`
- Minimal cardinality: `{"1": 219}`
- Singleton sufficient: `{"10": 2, "12": 111, "15": 21, "2": 41, "3": 154, "5": 0, "6": 191, "8": 18}`
- Singleton sufficient / available: `{"10": {"available_target_count": 33, "singleton_sufficient_count": 2}, "12": {"available_target_count": 211, "singleton_sufficient_count": 111}, "15": {"available_target_count": 140, "singleton_sufficient_count": 21}, "2": {"available_target_count": 41, "singleton_sufficient_count": 41}, "3": {"available_target_count": 206, "singleton_sufficient_count": 154}, "5": {"available_target_count": 28, "singleton_sufficient_count": 0}, "6": {"available_target_count": 219, "singleton_sufficient_count": 191}, "8": {"available_target_count": 41, "singleton_sufficient_count": 18}}`
- Necessary: `{"10": 0, "12": 0, "15": 0, "2": 0, "3": 0, "5": 0, "6": 5, "8": 0}`
- Roles: `{"10": {"individually_sufficient": 2, "interaction_only": 0, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 31}, "12": {"individually_sufficient": 111, "interaction_only": 20, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 80}, "15": {"individually_sufficient": 21, "interaction_only": 12, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 107}, "2": {"individually_sufficient": 41, "interaction_only": 0, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 0}, "3": {"individually_sufficient": 154, "interaction_only": 14, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 38}, "5": {"individually_sufficient": 0, "interaction_only": 0, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 28}, "6": {"individually_sufficient": 191, "interaction_only": 12, "necessary_for_rescue": 5, "unused_in_minimal_rescue": 16}, "8": {"individually_sufficient": 18, "interaction_only": 0, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 23}}`

### lambda_e

- Labels: `{"MIXED_SINGLETON_AND_INTERACTION_MINIMA": 20, "MULTIPLE_SINGLETON_ALTERNATIVES": 194, "UNIQUE_SINGLETON_RESCUE": 5}`
- Minimal cardinality: `{"1": 219}`
- Singleton sufficient: `{"10": 2, "12": 111, "15": 21, "2": 41, "3": 170, "5": 0, "6": 191, "8": 18}`
- Singleton sufficient / available: `{"10": {"available_target_count": 33, "singleton_sufficient_count": 2}, "12": {"available_target_count": 211, "singleton_sufficient_count": 111}, "15": {"available_target_count": 140, "singleton_sufficient_count": 21}, "2": {"available_target_count": 41, "singleton_sufficient_count": 41}, "3": {"available_target_count": 206, "singleton_sufficient_count": 170}, "5": {"available_target_count": 28, "singleton_sufficient_count": 0}, "6": {"available_target_count": 219, "singleton_sufficient_count": 191}, "8": {"available_target_count": 41, "singleton_sufficient_count": 18}}`
- Necessary: `{"10": 0, "12": 0, "15": 0, "2": 0, "3": 0, "5": 0, "6": 5, "8": 0}`
- Roles: `{"10": {"individually_sufficient": 2, "interaction_only": 0, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 31}, "12": {"individually_sufficient": 111, "interaction_only": 18, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 82}, "15": {"individually_sufficient": 21, "interaction_only": 8, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 111}, "2": {"individually_sufficient": 41, "interaction_only": 0, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 0}, "3": {"individually_sufficient": 170, "interaction_only": 8, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 28}, "5": {"individually_sufficient": 0, "interaction_only": 0, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 28}, "6": {"individually_sufficient": 191, "interaction_only": 12, "necessary_for_rescue": 5, "unused_in_minimal_rescue": 16}, "8": {"individually_sufficient": 18, "interaction_only": 0, "necessary_for_rescue": 0, "unused_in_minimal_rescue": 23}}`

## By rule

| rule | targets | kappa labels | lambda labels |
|---:|---:|---|---|
| 73 | 103 | {"MIXED_SINGLETON_AND_INTERACTION_MINIMA": 12, "MULTIPLE_SINGLETON_ALTERNATIVES": 88, "UNIQUE_SINGLETON_RESCUE": 3} | {"MIXED_SINGLETON_AND_INTERACTION_MINIMA": 9, "MULTIPLE_SINGLETON_ALTERNATIVES": 91, "UNIQUE_SINGLETON_RESCUE": 3} |
| 109 | 116 | {"MIXED_SINGLETON_AND_INTERACTION_MINIMA": 14, "MULTIPLE_SINGLETON_ALTERNATIVES": 100, "UNIQUE_SINGLETON_RESCUE": 2} | {"MIXED_SINGLETON_AND_INTERACTION_MINIMA": 11, "MULTIPLE_SINGLETON_ALTERNATIVES": 103, "UNIQUE_SINGLETON_RESCUE": 2} |

## Verdict

`HISTORICAL_PERIOD_RESCUE_ATLAS_BUILT`

## Methodological limits

- Only 219 F1 unit-bottleneck targets in 48 frozen Q8 cubes are analyzed.
- Source period groups can differ greatly in node abundance; no matched-size control is performed.
- Period grouping does not separate distinct morphologies sharing one period.
- Topological sufficiency is not temporal traversal or period causality.
- No claim is made about universal WIDTH=256 basin connectivity.
