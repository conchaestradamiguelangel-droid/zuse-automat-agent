# Rule 73/109 exact cut-coverage rescue law - Fase 102

## Scope and gates

- Targets: `219`
- Exposures: `43425`
- Re-enumerated critical vertices: `411`
- Re-enumerated critical edges: `394`
- Input/replay/cut reconciliation failures: `0`
- Scientific counterexamples: `0`

## Exact law

- Vertex rescue iff every individually critical F1 vertex is bypassed.
- Edge rescue iff every individually critical F1 edge is bypassed.
- Both predicates use equality with the total cut count; no threshold was scanned.

| Metric | TP | FP | TN | FN |
|---|---:|---:|---:|---:|
| kappa_v | 1505 | 0 | 41920 | 0 |
| lambda_e | 1566 | 0 | 41859 | 0 |
| both | 1505 | 0 | 41920 | 0 |

## Complete coverage

| Fase-101 geometry status | Exposures | Neither | Edge only | Vertex only | Both | Law mismatches |
|---|---:|---:|---:|---:|---:|---:|
| MATCHED_GEOMETRY | 31682 | 31493 | 0 | 0 | 189 | 0 |
| UNMATCHED_GEOMETRY | 11743 | 10366 | 61 | 0 | 1316 | 0 |

## Interpretation

Fase 101 showed that period-associated differences disappear within geometry-matched strata. Fase 102 closes the unmatched remainder for unit interventions: the complete cut-coverage predicate reproduces every directly re-enumerated rescue outcome across all 43,425 exposures.

The result is mechanistic rather than correlational within this frozen graph family. It does not imply that source period causes rescue; period only changes which nodes and geometries are available.

## Epistemic disclosure

The exact correspondence was visible in an exploratory preflight after Fases 100-101. This phase independently re-enumerates cuts and unit outcomes to audit that correspondence; it is not presented as a blind prospective discovery.

## Verdict

`EXACT_CUT_COVERAGE_RESCUE_LAW_VERIFIED`

## Methodological limits

- The preflight was exploratory after Fases 100-101; Fase 102 is a formal audit, not a blind discovery claim.
- The law covers unit interventions in 219 frozen F1 targets across 48 Q8 cubes.
- The phase does not test interactions among two or more added historical nodes.
- No temporal-period causality, universal basin, other WIDTH, or quantum-computing claim is made.
