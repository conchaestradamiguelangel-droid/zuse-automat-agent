# Fase 27: Five-State Locking Mechanism under F^3

## Hypothesis

Fase 26 found `T_local=15` over backgrounds with temporal period
`T_bg=3`. Fase 27 tests whether sampling the localized XOR defect once
per background period induces a minimal five-state cycle under the
three-step evolution operator `F^3`.

Sampling begins at `t=81`, after the established burn-in, rather than at
`t=0` where IC nucleation transients could obscure the asymptotic cycle.
Each representative is sampled through `t=141`, covering
`4` complete five-state cycles.

## Summary

- Representatives: `20`.
- Background phase exact under every `F^3` sample: `20/20`.
- Five first-cycle states distinct: `20/20`.
- Minimal cycle length under `F^3` equals 5: `20/20`.
- Four canonical cycles repeat exactly: `20/20`.
- Four raw-position cycles repeat exactly: `20/20`.
- Deterministic state transitions consistent: `20/20`.
- Stationary over every local period: `20/20`.

**Verdict:** `5-cycle under F^3 confirmed universally`.

## Per Representative

| rule | background | IC | distinct | minimal | 4 cycles | raw repeat | drift | confirmed |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| rule_73 | `00000011` | `0000011` | True | True | True | True | 0 | True |
| rule_73 | `00001001` | `00110010` | True | True | True | True | 0 | True |
| rule_73 | `00001111` | `00100000` | True | True | True | True | 0 | True |
| rule_73 | `00101101` | `010110` | True | True | True | True | 0 | True |
| rule_73 | `00101111` | `0000111` | True | True | True | True | 0 | True |
| rule_73 | `00110101` | `011010` | True | True | True | True | 0 | True |
| rule_73 | `00110111` | `011011` | True | True | True | True | 0 | True |
| rule_73 | `00111011` | `00100100` | True | True | True | True | 0 | True |
| rule_73 | `00111111` | `0001100` | True | True | True | True | 0 | True |
| rule_73 | `01101111` | `01101110` | True | True | True | True | 0 | True |
| rule_109 | `00000011` | `1110101` | True | True | True | True | 0 | True |
| rule_109 | `00001001` | `0001001` | True | True | True | True | 0 | True |
| rule_109 | `00001011` | `0001001` | True | True | True | True | 0 | True |
| rule_109 | `00001101` | `0100001` | True | True | True | True | 0 | True |
| rule_109 | `00001111` | `0001001` | True | True | True | True | 0 | True |
| rule_109 | `00010011` | `01001` | True | True | True | True | 0 | True |
| rule_109 | `00011001` | `01` | True | True | True | True | 0 | True |
| rule_109 | `00110101` | `010101` | True | True | True | True | 0 | True |
| rule_109 | `00111111` | `00111111` | True | True | True | True | 0 | True |
| rule_109 | `01101111` | `0101001` | True | True | True | True | 0 | True |

## Interpretation

A confirmed result establishes the finite-state mechanism of the measured
locking ratio: after the background returns to the same temporal phase
every three ECA steps, the localized defect advances by one node in a
minimal five-state cycle. Five applications of `F^3` are therefore
required to return the complete background-plus-defect state, yielding
`T_local = 5 * T_bg = 15`.

This is a computational state-cycle derivation. It does not yet reduce
the five nodes to a closed-form symbolic identity over the rule table.
