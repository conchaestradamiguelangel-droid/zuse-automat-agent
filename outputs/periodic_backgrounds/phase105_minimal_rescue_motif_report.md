# Fase 106 - Minimal rescue motif atlas

**Verdict:** `MINIMAL_RESCUE_MOTIF_ATLAS_BUILT`

No cellular-automaton simulations were executed. Geometry was frozen before outcomes were joined.

## Frozen denominators

| Cardinality | Metric | Trials | Minimal rescues |
|---:|---|---:|---:|
| 2 | kappa | 384354 | 454 |
| 2 | lambda | 372299 | 470 |
| 3 | kappa | 2745416 | 180 |
| 3 | lambda | 3031106 | 192 |
| 4 | kappa | 20638850 | 77 |
| 4 | lambda | 19941575 | 103 |

## Methodological limits

- Motif classes are exact unlabeled induced Hamming-1 graphs; edge count alone is never used as the class.
- Motif/outcome heterogeneity is retained and never repaired by post-hoc class merging.
- Cut coverage, full rescue, and internal-edge dependence are separate reported quantities.
- Every internal edge has an explicit removal audit: coverage, rescue, uncovered cuts, and new separators.
- Results remain limited to the frozen 48 Q8 cubes and cardinalities 2-4.
- The sparse motif/cut representation is QUBO-compatible data, not a quantum algorithm or advantage claim.
