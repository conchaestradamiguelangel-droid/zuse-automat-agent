# Fase 92 - Exact rule_73/rule_109 conjugacy closure

## Question

Are the rule-specific classes in the Fase-91 atlas genuine dynamical asymmetries, or occupancy gaps caused by canonical background-phase sampling and exclusion of the zero IC?

## Predeclared protocol

- Input: exactly the 3,296 versioned Fase-91 cases.
- Transform: rule_73 <-> rule_109, bitwise-complemented background with the exact original phase, and bitwise-complemented IC with the same length.
- Zero IC is allowed only in the diagnostic constructed stratum.
- Coverage metadata never controls simulation or the abort gate.
- Physical gate: background complementarity and defect equality at every t=0..1000, equal kind/period/drift, and equal conjugacy-class hash.
- A single physical mismatch aborts before results are published.

## Physical closure

- Source cases: 3296
- Exact trajectory matches: 3296
- Physical mismatches: 0
- Fase-91 conjugacy classes: 123
- Classes spanning both rules after constructed closure: 123
- Classes still rule-specific after closure: 0

## Evidence strata

| stratum | input rows | role |
|---|---:|---|
| OBSERVED_CATALOG_PAIR | 160 | Direct counterpart already present in the frozen catalog |
| CONSTRUCTED_PHASE_COMPLEMENT | 3096 | Exact deterministic complement absent only because one canonical background phase was sampled |
| CONSTRUCTED_PHASE_PLUS_ZERO_IC | 40 | Diagnostic exact complement absent by both phase sampling and zero-IC exclusion |
| CONSTRUCTED_ZERO_IC | 0 | Diagnostic zero-IC complement with represented background phase |

- Distinct observed catalog pair orbits: 80
- Rows excluded from real catalog-coverage claims because the conjugate IC is zero: 40

## Coverage status

`{"BACKGROUND_PHASE_AND_ZERO_IC_OMITTED": 40, "BACKGROUND_PHASE_OMITTED": 3096, "PARTNER_PRESENT": 160}`

## Verdict

`CONJUGACY_CLOSURE_CONFIRMED_SAMPLING_ASYMMETRY`

All constructed comparisons are deterministic symmetry validations. Only the observed catalog-pair stratum measures direct frozen-catalog coverage; constructed rows are not independent statistical observations.

## Methodological limits

- Only 160/3,296 input rows have their exact conjugate already present in the frozen catalog; these form 80 bidirectional pair orbits.
- The remaining comparisons complete a known exact ECA symmetry and quantify sampling occupancy. They do not add independent statistical power or establish behavior outside the two frozen cohorts.
- The 40 zero-IC complements are reported separately and excluded from direct catalog-coverage claims.
- No ANF-gradient measurement is performed.
- No paper, DOI, tag, release, v1.34, or v1.35 artifact is modified.
