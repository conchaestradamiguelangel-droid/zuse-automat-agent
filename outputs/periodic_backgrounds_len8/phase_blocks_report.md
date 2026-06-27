# Fase 29: Phase/Block Analysis of the T=15 Cycle

## Question

Fase 28 showed that no fixed sparse set of induced local keys explains
all 100 `F^3` edges of the T=15 family. Fase 29 tests the next
possibility: whether the five-cycle is visible as either a background-
independent defect shape or a phase-specific ordered local block.

## Inputs

- Representatives: `20` minimal T=15 rule/background pairs from Fase 27.
- Rules: `rule_73` and `rule_109`.
- Sample times: `t=81,84,87,90,93`.
- Block window: active defect span plus `3` cells on each side.
- Per-position token: the ordered three-microstep sequence of
  `(background neighborhood, defect neighborhood -> next defect bit)`.

## Part A -- defect shape consistency

| rule | phase 0 | phase 1 | phase 2 | phase 3 | phase 4 | all phases consistent |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| rule_73 | 8 | 9 | 9 | 9 | 9 | False |
| rule_109 | 8 | 8 | 8 | 8 | 8 | False |

A value of `1` would mean that every background produces the same
canonical XOR-defect shape in that phase. The observed counts are all
larger than one, so the T=15 cycle is not a pure defect-only dynamic.

## Part B -- ordered block signatures

| rule | phase | nontrivial shared signature | longest nontrivial length | any shared length | first W distinguishing backgrounds | W making all backgrounds unique |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| rule_73 | 0 | False | 0 | 1 | 0 | None |
| rule_73 | 1 | False | 0 | 0 | 0 | None |
| rule_73 | 2 | False | 0 | 1 | 0 | None |
| rule_73 | 3 | False | 0 | 0 | 0 | None |
| rule_73 | 4 | False | 0 | 0 | 0 | None |
| rule_109 | 0 | False | 0 | 0 | 0 | None |
| rule_109 | 1 | False | 0 | 1 | 0 | None |
| rule_109 | 2 | False | 0 | 1 | 0 | None |
| rule_109 | 3 | False | 0 | 0 | 0 | None |
| rule_109 | 4 | False | 0 | 0 | 0 | None |

The only exact shared length-1 blocks are trivial background-context
tokens with `d000->0` through all three microsteps. They are reported
as `any shared length` but are not counted as defect-driving local
signatures.

The `first W` column asks how many cells outside the active defect
must be included before the ordered block distinguishes at least two
backgrounds. `W=0` means the defect span itself already carries
background-dependent local context.

## Conjugation check

| phase | complement maps shared rule_73 block to rule_109 block |
| ---: | --- |
| 0 | False |
| 1 | False |
| 2 | False |
| 3 | False |
| 4 | False |

## Relation to Fase 28

- Sparse universal support found in Fase 28: `False`.
- Fase 28 rule_73 phase-intersection sizes: `[9, 6, 7, 5, 4]`.
- Fase 28 rule_109 phase-intersection sizes: `[11, 11, 10, 9, 8]`.
- Black/white induced conjugation identity exact: `True`.

## Verdict

**Status:** `NO_LOCAL_BLOCK_DERIVATION`.

Neither the defect-only hypothesis nor the fixed-window ordered block hypothesis explains all phases. The T=15 mechanism requires context beyond this local block representation, or a different state variable.

## Falsifiable implication

A complete symbolic derivation of the `rule_73/rule_109` T=15 family
must encode the spatial phase of the length-8 background, or use a
larger/higher-order state than the active defect plus a fixed local
padding. A proposed derivation that predicts background-independent
defect shapes or one shared ordered block in all five phases is
falsified by this report.
