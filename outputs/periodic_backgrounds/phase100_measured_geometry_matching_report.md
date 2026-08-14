# Rule 73/109 measured-geometry matching audit - Fase 101

## Gates and coverage

- Exposures: `43425`
- Geometry strata: `13088`
- Matched strata: `4090`
- Matched exposures: `31682`
- Unmatched exposures: `11743`
- Comparisons per metric: `7281`
- Reconciliation failures: `0`

## Matched and unmatched outcomes

| Period | All | Matched | Unmatched | Coverage | Matched kappa rate | Unmatched kappa rate | Matched lambda rate | Unmatched lambda rate |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 4071 | 3464 | 607 | 0.850897 | 0.000000 | 0.141680 | 0.000000 | 0.141680 |
| 3 | 11656 | 9305 | 2351 | 0.798301 | 0.005588 | 0.156104 | 0.005588 | 0.156104 |
| 5 | 250 | 250 | 0 | 1.000000 | 0.000000 | N/A | 0.000000 | N/A |
| 6 | 22644 | 14810 | 7834 | 0.654036 | 0.004794 | 0.092035 | 0.004794 | 0.099821 |
| 8 | 263 | 201 | 62 | 0.764259 | 0.004975 | 0.403226 | 0.004975 | 0.403226 |
| 10 | 273 | 249 | 24 | 0.912088 | 0.008032 | 0.000000 | 0.008032 | 0.000000 |
| 12 | 3362 | 2770 | 592 | 0.823914 | 0.020217 | 0.165541 | 0.020217 | 0.165541 |
| 15 | 906 | 633 | 273 | 0.698675 | 0.011058 | 0.069597 | 0.011058 | 0.069597 |

## Geometry homogeneity

- All strata kappa: `{"GEOMETRY_HOMOGENEOUS_NONRESCUE": 11836, "GEOMETRY_HOMOGENEOUS_RESCUE": 1252}`
- All strata lambda: `{"GEOMETRY_HOMOGENEOUS_NONRESCUE": 11775, "GEOMETRY_HOMOGENEOUS_RESCUE": 1313}`
- Matched strata kappa: `{"GEOMETRY_HOMOGENEOUS_NONRESCUE": 4005, "GEOMETRY_HOMOGENEOUS_RESCUE": 85}`
- Matched strata lambda: `{"GEOMETRY_HOMOGENEOUS_NONRESCUE": 4005, "GEOMETRY_HOMOGENEOUS_RESCUE": 85}`

## Period comparisons after geometry matching

- Kappa directions: `{"TIE": 7281}`
- Lambda directions: `{"TIE": 7281}`
- Every matched stratum is outcome-homogeneous, and every period-pair comparison is an exact tie for both metrics.

## T5 coverage note

- `T5 occurs only in 40 measured-geometry strata, all also containing T2, T3, and T6; its 100% matched coverage is restricted support, not universal geometric coverage.`
- Counterpart geometry strata: `{"12": 20, "2": 40, "3": 40, "6": 40, "8": 36}`

## Interpretation

Within the 31,682 matched exposures, the period-associated differences from Fase 100 disappear after controlling target identity, unit cardinality, and the frozen measured signature. This is a coverage-conditioned result: 11,743 unmatched exposures remain outside the comparison, and no feature was added after observing outcomes.

## Verdict

`MEASURED_GEOMETRY_MATCHED_ATLAS_BUILT`

## Methodological limits

- Matched and unmatched exposure results are always reported side by side.
- The frozen 13-variable signature is measured local geometry, not exact colored-graph isomorphism.
- Residual period association may reflect geometry not represented in the signature.
- The phase does not decompose collective interactions of two or more historical nodes.
- No temporal causality, transition probability, or universal WIDTH=256 basin claim is made.
