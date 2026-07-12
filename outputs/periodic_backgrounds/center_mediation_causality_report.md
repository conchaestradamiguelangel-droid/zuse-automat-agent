# Fase 57: Center-Mediated ANF Causality Audit

## Question

Is the center-mediated local ANF structure identified in Fase 56 necessary
and/or sufficient for the ANF-gradient witnesses found in the Fase 55
periodic-background catalog, or is it only correlated with them?

This phase runs no new ECA or cone simulations. It computes the 3-variable
ANF of all 256 ECA rules and joins that rule-level classification to the
existing Fase 55 census.

## Definition

- `C_alone`: the isolated `C` monomial appears.
- `LR_no_center`: the `LR` monomial appears without the center.
- `center_mediated`: `C_alone=False` and `LR_no_center=False`.
- `strict_center_mediated`: `center_mediated=True` and at least one center
  interaction monomial exists.

## 256-Rule Summary

- ECA rules analyzed: 256
- `center_mediated=True`: 64 rules
- `strict_center_mediated=True`: 56 rules

## Catalog Rule Table

| rule | expression | C_alone | LR_no_center | center_mediated | strict | cases | positives | categories |
| --- | --- | --- | --- | --- | --- | ---: | ---: | --- |
| `54` | `L XOR C XOR R XOR LR` | `True` | `True` | `False` | `False` | 4 | 0 | HORIZON_ARTIFACT:2, INSUFFICIENT_SUPPORT:1, NEGATIVE:1 |
| `73` | `1 XOR L XOR C XOR R XOR LR XOR LCR` | `True` | `True` | `False` | `False` | 17 | 0 | HORIZON_ARTIFACT:7, INSUFFICIENT_SUPPORT:1, NEGATIVE:9 |
| `94` | `L XOR C XOR LC XOR R XOR CR XOR LCR` | `True` | `False` | `False` | `False` | 12 | 0 | HORIZON_ARTIFACT:5, NEGATIVE:7 |
| `109` | `1 XOR L XOR LC XOR R XOR CR XOR LCR` | `False` | `False` | `True` | `True` | 17 | 5 | HORIZON_ACCEPTABLE:3, HORIZON_ARTIFACT:2, NATURAL_PERIOD_STRONG:2, NEGATIVE:10 |
| `133` | `1 XOR L XOR R XOR LR XOR LCR` | `False` | `True` | `False` | `False` | 12 | 0 | HORIZON_ARTIFACT:2, NEGATIVE:10 |
| `147` | `1 XOR C XOR LR` | `True` | `True` | `False` | `False` | 4 | 0 | HORIZON_ARTIFACT:2, INSUFFICIENT_SUPPORT:1, NEGATIVE:1 |

## Necessity Test

- Positive cases: 5
- Positive cases with `center_mediated=False`: 0
- Status: `CENTER_MEDIATION_NECESSARY_IN_CATALOG`

All positive witnesses in the catalog occur in rules classified as `center_mediated=True`.

## Sufficiency Test

- Non-positive cases: 61
- Non-positive cases with `center_mediated=True`: 12
- Non-positive cases with `strict_center_mediated=True`: 12
- Status: `CENTER_MEDIATION_NOT_SUFFICIENT_IN_CATALOG`

Representative non-positive center-mediated cases:

- `rule_109/bg=0011/T=3/word=0001100` -> `NEGATIVE`
- `rule_109/bg=0011/T=6/word=1100100` -> `NEGATIVE`
- `rule_109/bg=0011/T=8/word=1000010` -> `NEGATIVE`
- `rule_109/bg=0011/T=10/word=10000010` -> `NEGATIVE`
- `rule_109/bg=0110/T=3/word=001100` -> `NEGATIVE`
- `rule_109/bg=0110/T=6/word=0010011` -> `NEGATIVE`
- `rule_109/bg=1011/T=6/word=00001001` -> `HORIZON_ARTIFACT`
- `rule_109/bg=1100/T=3/word=00001110` -> `NEGATIVE`
- `rule_109/bg=1100/T=6/word=00100110` -> `NEGATIVE`
- `rule_109/bg=1100/T=10/word=00111001` -> `NEGATIVE`
- `rule_109/bg=1101/T=6/word=0000100` -> `HORIZON_ARTIFACT`
- `rule_109/bg=1101/T=10/word=0001000` -> `NEGATIVE`

## Overall Verdict

`CAUSAL_CANDIDATE_NECESSARY_NOT_SUFFICIENT`.

Interpretation: center mediation is necessary for the positive witnesses
inside the Fase 55 catalog, but it is not sufficient. Several
center-mediated rules or cases do not become ANF-gradient witnesses.
Therefore, the Fase 56 candidate survives as a necessary structural
condition in the catalog, but not as a complete causal explanation.

## Methodological Limits

- Necessity and sufficiency are evaluated only inside the Fase 55 catalog.
- Sufficiency is empirical over observed catalog cases, not universal over all ECA worlds.
- A closed causal proof would require intervention or synthetic-rule construction.
