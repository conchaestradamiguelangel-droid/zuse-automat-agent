# Fase 98 - F1 bottleneck rescue filtration

## Question

Which F2/F3 state families remove the 219 unit bottlenecks observed among the 627 first-closing F1 component pairs?

## Frozen inputs and gates

- Fase-95 raw/canonical: `1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3` / `57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429`
- Fase-97 raw/canonical: `3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858` / `85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b`
- Fase-98 result raw/canonical: `0e0037a8cfef81e0f190275636977189d1d4d46db009a909cbc017e0a7693297` / `42eeed0fe5f8d4f75013bfd9d29466a7fc6600bf4bce1b1b82ae30707d3cb387`
- Replay: `EXACT_F1_AND_F3_FIELD_REPLAY`
- Monotonicity/reconciliation failures: 0/0

## Denominators

- Eligible first-closing F1 pairs: 627
- Unit-bottleneck targets: 219
- Already-redundant controls: 408
- Excluded pairs born at F2/F3: 350/2

Targets and controls are never mixed into one rescue percentage.

## F2 rescue over 219 targets

- Vertex labels: `{"RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY": 219}`
- Edge labels: `{"RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY": 219}`
- Joint status: `{"BOTH_RESCUED": 219}`
- Singleton rescue counts: `{"kappa_v": {"HISTORICAL_SOURCE_POSITIVE": 219, "STATIC_T1": 0}, "lambda_e": {"HISTORICAL_SOURCE_POSITIVE": 219, "STATIC_T1": 0}}`
- Historical singleton exactly matches full F2: `{"kappa_v": 219, "lambda_e": 219}`

## Connectivity evolution

- Target kappa_v F1/F2/F3: `{"f1": {"1": 219}, "f2": {"13": 8, "14": 3, "19": 4, "7": 27, "8": 177}, "f3": {"13": 2, "14": 9, "19": 4, "7": 17, "8": 187}}`
- Target lambda_e F1/F2/F3: `{"f1": {"1": 219}, "f2": {"13": 8, "14": 3, "20": 4, "7": 27, "8": 177}, "f3": {"13": 2, "14": 9, "20": 4, "7": 17, "8": 187}}`
- Control kappa_v F1/F2/F3: `{"f1": {"10": 2, "2": 201, "3": 91, "4": 74, "5": 30, "6": 10}, "f2": {"13": 2, "14": 36, "18": 5, "19": 4, "23": 2, "24": 3, "7": 55, "8": 301}, "f3": {"13": 2, "14": 36, "18": 1, "19": 8, "23": 2, "24": 3, "7": 43, "8": 313}}`
- Control lambda_e F1/F2/F3: `{"f1": {"10": 2, "2": 178, "3": 110, "4": 73, "5": 31, "6": 11, "7": 3}, "f2": {"13": 2, "14": 36, "18": 1, "19": 4, "20": 4, "23": 2, "24": 1, "26": 2, "7": 55, "8": 301}, "f3": {"13": 2, "14": 36, "18": 1, "20": 8, "23": 2, "24": 1, "26": 2, "7": 43, "8": 313}}`

## F3 category roles over targets not rescued in F2

- Evaluated targets by metric: `{"kappa_v": 0, "lambda_e": 0}`
- A zero here means NOT_APPLICABLE because F2 already rescued the metric; it is not a tested F3 failure.

- kappa_v: `{"EXTINCT": {"individually_sufficient": 0, "interaction_only": 0, "necessary_for_rescue": 0}, "SPAN_ESCAPE": {"individually_sufficient": 0, "interaction_only": 0, "necessary_for_rescue": 0}, "ZERO_INITIAL_DEFECT": {"individually_sufficient": 0, "interaction_only": 0, "necessary_for_rescue": 0}}`
- lambda_e: `{"EXTINCT": {"individually_sufficient": 0, "interaction_only": 0, "necessary_for_rescue": 0}, "SPAN_ESCAPE": {"individually_sufficient": 0, "interaction_only": 0, "necessary_for_rescue": 0}, "ZERO_INITIAL_DEFECT": {"individually_sufficient": 0, "interaction_only": 0, "necessary_for_rescue": 0}}`

## By rule

| rule | targets | controls | vertex F2 labels | edge F2 labels |
|---:|---:|---:|---|---|
| 73 | 103 | 202 | {"RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY": 103} | {"RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY": 103} |
| 109 | 116 | 206 | {"RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY": 116} | {"RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY": 116} |

## Verdict

`BOTTLENECK_RESCUE_FILTRATION_MAPPED`

## Methodological limits

- Only the 627 first-closing F1 pairs in the 48 frozen Q8 cubes are eligible.
- Rescue counts use 219 targets; 408 controls are never mixed into that denominator.
- Category subsets identify topological sufficiency/necessity, not temporal causality.
- The zero word and all F4 claims remain excluded.
- No claim is made about universal WIDTH=256 basin connectivity.
