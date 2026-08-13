# Fase 97 - Intracube bridge robustness atlas

## Question

Are the 979 Fase-96 component bridges supported by redundant intervention paths, or do they depend on pair-specific vertex/edge bottlenecks?

## Frozen sources and reconciliation

- Fase-95 raw SHA-256: `1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3`
- Fase-95 canonical SHA-256: `57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429`
- Fase-96 raw SHA-256: `cbd414180e89658b3e20c73559dbcb490b2bca845a1165f3f6a8e36f25c2e823`
- Fase-96 canonical SHA-256: `5c43278492fa09f9367fa971e06d0a7b3e2b99e295a63279721bc78a4946f825`
- Fase-97 result raw SHA-256: `3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858`
- Fase-97 result canonical SHA-256: `85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b`
- Cubes/intersections/pairs: 48/272/979
- Fase-96 replay: `EXACT_PAIRWISE_RECONCILIATION`
- Reconciliation failures: 0

## Graph semantics

The graph is the undirected Q8 Hamming-1 intervention graph. It is not a directed CA-time graph. Vertex and edge connectivity are measured separately between complete F0 terminal components.

## Robustness by predeclared closure stratum

| stratum | pairs | G_min kappa_v | G_min lambda_e | G_F3 kappa_v | G_F3 lambda_e |
|---|---:|---|---|---|---|
| F1_ALL_LONG_PERIOD | 627 | {"1": 219, "10": 2, "2": 201, "3": 91, "4": 74, "5": 30, "6": 10} | {"1": 219, "10": 2, "2": 178, "3": 110, "4": 73, "5": 31, "6": 11, "7": 3} | {"13": 4, "14": 45, "18": 1, "19": 12, "23": 2, "24": 3, "7": 60, "8": 500} | {"13": 4, "14": 45, "18": 1, "20": 12, "23": 2, "24": 1, "26": 2, "7": 60, "8": 500} |
| F2_ALL_CONFIRMED_PERSISTENT | 350 | {"13": 9, "14": 16, "19": 1, "2": 2, "7": 22, "8": 300} | {"13": 9, "14": 16, "2": 2, "20": 1, "7": 22, "8": 300} | {"13": 6, "14": 19, "19": 1, "7": 5, "8": 319} | {"13": 6, "14": 19, "20": 1, "7": 5, "8": 319} |
| F3_ALL_LEDGER_BACKED_NONZERO | 2 | {"8": 2} | {"8": 2} | {"8": 2} | {"8": 2} |

No aggregate robustness percentage mixes F1, F2, and F3 denominators.

## Pair-specific bottlenecks

- F1_ALL_LONG_PERIOD: G_min single-vertex bottlenecks 219/627; G_F3 0/627.
- F2_ALL_CONFIRMED_PERSISTENT: G_min single-vertex bottlenecks 0/350; G_F3 0/350.
- F3_ALL_LEDGER_BACKED_NONZERO: G_min single-vertex bottlenecks 0/2; G_F3 0/2.

## SPAN_ESCAPE tests

- G_F3 true counts over 979 pairs: `{"category_essential": 2, "common_span_state_on_all_shortest_paths": 0, "shortest_path_category_mandatory": 2, "unique_span_vertex_bottleneck": 0}`
- G_min is NOT_APPLICABLE for the 977 F1/F2 pairs.
- The two first-closing F3 pairs must have identical G_min and G_F3 test results.

| pair | cube | category essential | shortest mandatory | common state | unique vertex bottleneck |
|---:|---|---|---|---|---|
| 367 | primitive_len8\|rule_073\|bg_029 | True | True | False | False |
| 475 | primitive_len8\|rule_109\|bg_000 | True | True | False | False |

## Intersection weakest links

- G_min weakest kappa_v: `{"1": 104, "14": 2, "2": 74, "3": 31, "4": 20, "5": 8, "7": 3, "8": 30}`
- G_min weakest lambda_e: `{"1": 104, "14": 2, "2": 69, "3": 36, "4": 18, "5": 10, "7": 3, "8": 30}`
- G_F3 weakest kappa_v: `{"14": 3, "19": 4, "24": 1, "7": 27, "8": 237}`
- G_F3 weakest lambda_e: `{"14": 3, "20": 4, "24": 1, "7": 27, "8": 237}`

## Verdict

`BRIDGE_ROBUSTNESS_ATLAS_BUILT`

## Methodological limits

- Only the 48 frozen Fase-95 length-8 Q8 cubes are analyzed.
- Q8 edges are reversible bit-flip interventions, not directed CA-time transitions.
- Connectivity is topological and is not a transition probability.
- The unsimulated zero word is excluded from every primary robustness metric.
- No claim is made about universal WIDTH=256 basin connectivity.
