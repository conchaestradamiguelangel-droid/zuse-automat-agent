# Fase 83: rule_73 h=11 Exact Causal Equivalence

## Question

Do the two h=11 controls from Fases 81-82 share the same exact
ANF polynomials after their 25-cell input windows are aligned by
translation, or only the same output-level degree/count geometry?

## Predeclared Correspondence

Variables are named by their local input coordinate `-12..12`.
No variable permutation is fitted. The right-hand case must be an
exact physical translation of the left-hand 25-cell window. The
four active outputs are then compared at the same local indices.

For each corresponding active output, the full 2^25-entry defect
truth table is transformed by Mobius inversion. Equality means zero
coefficient differences across all 2^25 possible monomials. SHA-256
is used only as a reproducible content identifier.

## Result

Status: `EXACT_CAUSAL_MAP_TRANSLATION_EQUIVALENCE`.

After a one-cell translation, both controls have identical boundary forcing, all 25 causal truth tables, and exact active-output ANF supports.

- Physical translation: `1` cell
- Positions translate exactly: `True`
- Sample defects translate exactly: `True`
- Final defects translate exactly: `True`
- Boundary forcing traces identical: `True`
- Actual causal truth tables identical: `25/25`
- Defect causal truth tables identical: `25/25`
- Exact active-output ANF matches: `4/4`
- Total differing active ANF coefficients: `0`
- Fase 82 geometry hash reproduced: `True`

## Reference Pair

| side | background | IC | global input window | active local outputs |
| --- | --- | --- | --- | --- |
| left | `00111011` | `011` | `114..138` | `[9, 13, 14, 15]` |
| right | `00111101` | `101` | `115..139` | `[9, 13, 14, 15]` |

## Exact Active-Output ANF Audit

| x2 | output | degree | monomials | exact | coefficient differences | SHA-256 |
| ---: | ---: | ---: | ---: | --- | ---: | --- |
| -6 | 9 | 21 | 1067658 | true | 0 | `5986979ecc5282706cea356fc6aa61b4f8ea23776b734a9f12058f3a38925c62` |
| 2 | 13 | 23 | 4431863 | true | 0 | `ac89a4d4d871642acb1e9b2830c4ddb65754e30ae1d1d811075ef3788721afee` |
| 4 | 14 | 22 | 1904465 | true | 0 | `b125c481ed07da9f6c819328501172b31022b833f5ff5eccc1715b088026d116` |
| 6 | 15 | 21 | 1067657 | true | 0 | `93276ac24bbde6fa183509352bb775ec9d609bb94553a61e9b5c4e62f1c66416` |

## Boundary Forcing

The packed causal calculation starts from the same 25 symbolic
variables in both cases. Its only case-specific inputs are the
left and right boundary bits injected at each step. Their traces
are listed below.

| step | left boundary | right boundary |
| ---: | ---: | ---: |
| 0 | 0 | 0 |
| 1 | 1 | 1 |
| 2 | 1 | 0 |
| 3 | 0 | 0 |
| 4 | 1 | 1 |
| 5 | 1 | 0 |
| 6 | 0 | 0 |
| 7 | 1 | 1 |
| 8 | 1 | 0 |
| 9 | 0 | 0 |
| 10 | 1 | 1 |

## Local-State Diagnostics

- Symbolic-window concrete samples equal: `True`
- Background samples equal: `True`
- Final actual windows equal: `True`
- Final background windows equal: `True`
- Final defect windows equal: `True`

These concrete-state equalities are diagnostics only. Exact causal
map equality is decided by the complete symbolic truth tables and
ANF coefficient supports, not by one realized trajectory.

## Interpretation

The Fase 82 geometry match is not merely a collision of counts
and degree histograms. Once translated by one cell, the two
controls implement the same finite-horizon causal operator.
Identical boundary forcing explains why the same rule acting on
the same symbolic variables produces identical truth tables and
therefore identical ANF polynomials.

## Methodological Limits

- This is an exact audit of one pair, one rule, one local period,
  one input-window width, and horizon h=11.
- Translation equivalence at finite horizon does not imply that the
  two infinite periodic backgrounds are globally symmetry-related.
- The result explains the Fase 81-82 pair but does not estimate how
  frequently such local causal equivalences occur outside this pair.
- SHA-256 is a content checksum; equality was also checked directly
  by zero coefficient-wise symmetric difference.
- No classification threshold was fitted and no paper or release
  metadata was changed.
