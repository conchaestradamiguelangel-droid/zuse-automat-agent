# Rule 73/109 triple historical synergy atlas - Fase 104

## Gates and scope

- Fase-103 strata/pairs replayed: `142` / `404054`
- Triple strata: `73`
- Kappa strata/trials: `57` / `2745416`
- Lambda strata/trials: `71` / `3031106`
- Unique unordered triple interventions: `3061466`
- Route disagreements: `0`
- Monotonicity failures: `0`
- Fase-103 out-of-scope bits: `0`

## Minimum observed cardinality

| Metric | Exactly 3 strata | At least 4 strata | Rescuing triple trials |
|---|---:|---:|---:|
| kappa_v | 41 | 16 | 180 |
| lambda_e | 40 | 31 | 192 |

## Triple interaction

- Internal-edge distribution: `{0: 2693722, 1: 353303, 2: 14441, 3: 0}`
- Kappa rescues requiring an internal Hamming-1 edge: `98`
- Lambda rescues requiring an internal Hamming-1 edge: `98`
- Genuine three-node original vertex-cut coverage: `180`
- Genuine three-node original edge-cut coverage: `192`
- Kappa rescues by internal-edge count: `{0: 72, 1: 44, 2: 64}`
- Lambda rescues by internal-edge count: `{0: 82, 1: 52, 2: 58}`
- Kappa rescues by period/rule: `{2: 36, 3: 76, 6: 40, 12: 28}` / `{73: 82, 109: 98}`
- Lambda rescues by period/rule: `{2: 36, 3: 69, 6: 55, 12: 32}` / `{73: 91, 109: 101}`

## Binary ledger

- Records: `3061466`
- Record size: `10` bytes
- Ledger size: `30614660` bytes
- SHA-256: `b342a58d20aa7ecdc2a2a5ea45037a64739134151db41b562464163b7e93578f`
- The manifest specifies every field, bit and packed subfield; the decoder uses only the Python standard library.

## Verdict

`TRIPLE_SYNERGY_ATLAS_BUILT`

## Methodological limits

- EXACTLY_3 is proven only where every singleton and pair fails and at least one triple rescues.
- AT_LEAST_4 is a lower bound; quadruples and larger subsets are not enumerated here.
- Period labels index frozen historical-node families and are not treated as temporal causes.
- The atlas is restricted to 73 unresolved target-period strata in 48 frozen Q8 cubes.
