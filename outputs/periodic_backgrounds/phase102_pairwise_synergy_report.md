# Rule 73/109 pairwise historical synergy atlas - Fase 103

## Gates and scope

- Collective strata: `142`
- Kappa strata/trials: `126` / `384354`
- Lambda strata/trials: `139` / `372299`
- Unique unordered pair interventions: `404054`
- Adjacent/nonadjacent pairs: `16307` / `387747`
- Route disagreements: `0`
- Monotonicity failures: `0`

## Minimum observed cardinality

| Metric | Exactly 2 strata | At least 3 strata | Rescuing pair trials |
|---|---:|---:|---:|
| kappa_v | 69 | 57 | 454 |
| lambda_e | 68 | 71 | 470 |

## Pair interaction

- Kappa rescues requiring the mutual Hamming-1 edge: `83`
- Lambda rescues requiring the mutual Hamming-1 edge: `86`

## Binary ledger

- Records: `404054`
- Record size: `10` bytes
- Ledger size: `4040540` bytes
- SHA-256: `43d029c26f83027d2804f54a8222a0bfc361b9c9c12280b890d0dc5f8082a344`
- Format and bit meanings are fully specified in the JSON manifest; the decoder uses only the Python standard library.

## Verdict

`PAIRWISE_SYNERGY_ATLAS_BUILT`

## Methodological limits

- EXACTLY_2 is proven only where no singleton rescues and at least one pair does.
- AT_LEAST_3 is a lower bound; triples and higher subsets are not enumerated here.
- Period labels index available historical-node families and are not treated as temporal causes.
- The atlas is restricted to 142 frozen target-period strata in 48 Q8 cubes.
