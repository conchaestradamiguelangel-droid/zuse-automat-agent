# Fase 85: rule_73 h=11 Input-Selector Intervention

## Question

Which minimal changes between the two 25-bit inputs identified in
Fase 84 select the comparable four-output trajectory or the
non-comparable seven-output trajectory while the exact causal
operator and boundary forcing remain fixed?

## Predeclared Intervention

Endpoint A is `0x0310630` and endpoint B is
`0x035b8b0`. They differ at eight variable
indices `[7, 9, 10, 11, 12, 13, 15, 18]`. Fase 85 exhaustively evaluates
all 2^8 = 256 assignments in the connecting subcube. A subset bit
equal to 1 selects the B allele at that variable; 0 retains A.

Every assignment is evolved for 11 steps under the same rule_73
boundary trace. The final state is independently read from the complete
packed causal truth tables. T15 comparability reuses the unchanged
Fase 55 `comparable_to_t15()` predicate on the active-output ANF fit.

Intermediate assignments are controlled symbolic interventions. They
are not claimed to be stationary oscillators already present in the
physical background catalogue.

## Result

Status: `SINGLE_BIT_ANF_INPUT_SELECTOR_FOUND`.

At least one single-bit intervention changes T15 comparability while the causal operator and boundary forcing remain fixed.

- Assignments evaluated: `256`
- Packed/local mismatches: `0`
- Comparable assignments: `15`
- Non-comparable assignments: `241`
- Exact A final patterns: `1`
- Exact B final patterns: `3`
- Other final patterns: `252`
- Exact A trajectories: `1`
- Exact B trajectories: `1`
- Other trajectories: `254`

## Minimal Interventions

- A -> exact B final pattern: distance 4: changed bits=[7, 11, 15, 18] (`0x0358eb0`)
- B -> exact A final pattern: distance 8: reverted bits=[7, 9, 10, 11, 12, 13, 15, 18] (`0x0310630`)
- A -> non-comparable: distance 1: changed bits=[7] (`0x03106b0`), changed bits=[10] (`0x0310230`), changed bits=[11] (`0x0310e30`), changed bits=[12] (`0x0311630`), changed bits=[13] (`0x0312630`), changed bits=[15] (`0x0318630`), changed bits=[18] (`0x0350630`)
- B -> comparable: distance 2: reverted bits=[11, 15] (`0x03530b0`), reverted bits=[9, 12] (`0x035aab0`)

## Single-Bit Audit

| bit | local x | A->B allele | active | comparable | B->A allele | active | comparable |
| ---: | ---: | --- | ---: | --- | --- | ---: | --- |
| 7 | -5 | OTHER_PATTERN | 5 | false | OTHER_PATTERN | 6 | false |
| 9 | -3 | OTHER_PATTERN | 5 | true | OTHER_PATTERN | 7 | false |
| 10 | -2 | OTHER_PATTERN | 6 | false | OTHER_PATTERN | 6 | false |
| 11 | -1 | OTHER_PATTERN | 6 | false | OTHER_PATTERN | 4 | false |
| 12 | 0 | OTHER_PATTERN | 5 | false | OTHER_PATTERN | 7 | false |
| 13 | 1 | OTHER_PATTERN | 3 | false | OTHER_PATTERN | 7 | false |
| 15 | 3 | OTHER_PATTERN | 2 | false | OTHER_PATTERN | 5 | false |
| 18 | 6 | OTHER_PATTERN | 6 | false | OTHER_PATTERN | 6 | false |

## Inclusion-Minimal Selector Sets

These sets are exact within the eight-bit subcube; no statistical
fit or feature selection is used.

### From A: inclusion-minimal changes producing non-comparability

| changed bits | local coordinates |
| --- | --- |
| `[7]` | `[-5]` |
| `[10]` | `[-2]` |
| `[11]` | `[-1]` |
| `[12]` | `[0]` |
| `[13]` | `[1]` |
| `[15]` | `[3]` |
| `[18]` | `[6]` |

### From B: inclusion-minimal reversions restoring comparability

| reverted bits | local coordinates |
| --- | --- |
| `[9, 12]` | `[-3, 0]` |
| `[11, 15]` | `[-1, 3]` |
| `[10, 11, 12]` | `[-2, -1, 0]` |
| `[9, 11, 13]` | `[-3, -1, 1]` |
| `[10, 11, 13]` | `[-2, -1, 1]` |
| `[9, 13, 18]` | `[-3, 1, 6]` |
| `[7, 13, 15, 18]` | `[-5, 1, 3, 6]` |
| `[7, 11, 12, 13, 18]` | `[-5, -1, 0, 1, 6]` |

## Endpoint Verification

| endpoint | input | final class | active outputs | comparable | slope | R2 |
| --- | --- | --- | ---: | --- | ---: | ---: |
| A | `0x0310630` | A_COMPARABLE_PATTERN | 4 | true | -0.303828 | 0.990540 |
| B | `0x035b8b0` | B_NONCOMPARABLE_PATTERN | 7 | false | -0.276100 | 0.943352 |

## Interpretation

The h=11 ANF crossing is sensitive to at least one atomic input
edit even though rule, horizon, causal operator, final background,
and boundary forcing are unchanged. This isolates the selection
mechanism at input-assignment level rather than rule or operator
level. Exact endpoint trajectories may still require more than
one bit; comparability and endpoint identity are reported
separately. In particular, three assignments reach the exact B
final pattern, but only endpoint B reproduces the exact B
trajectory. Final-state convergence therefore does not imply
full trajectory identity.

## Methodological Limits

- The 256 assignments exhaust only the eight-bit subcube connecting
  two observed inputs; the remaining 17 variables are held fixed.
- Controlled intermediate inputs are valid symbolic interventions
  but are not necessarily stationary oscillators in the source sweep.
- Comparability is the unchanged empirical Fase 55 predicate, not a
  universal physical phase label.
- The result is local to rule_73, T=12, h=11, window 25, and this
  boundary-forcing class.
- No paper, DOI, tag, release, or threshold changed.
