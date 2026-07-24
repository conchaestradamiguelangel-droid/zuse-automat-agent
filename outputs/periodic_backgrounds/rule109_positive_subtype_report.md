# Fase 70: rule_109 Positive Dynamic-Subtype Audit

## Question

Are the five positive `rule_109` ANF-gradient witnesses dynamically
homogeneous, or did Fase 69 expose two different positive subtypes?

This phase reuses the Fase 69 aligned snapshot-transition data. It does
not touch the paper, DOI metadata, tags, or release state.

## Subtype Rule

- `DYNAMIC_POSITIVE`: positive case with
  `positive_only_center_transition_count >= 8`.
- `STATIC_POSITIVE`: positive case with `period_center_shape=1`,
  `unique_center_transitions=1`, and `mean_center_step_diff=0.0`.
- `UNCLASSIFIED_POSITIVE`: positive case not captured by either rule.

## Positive Cases

| case | subtype | period center | unique center transitions | pos-only center transitions | mean center diff | tail sizes | tail spans |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG` | `DYNAMIC_POSITIVE` | 12 | 12 | 12 | 7.550 | `[4, 5, 6, 7, 8]` | `[10, 11, 12]` |
| `bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `STATIC_POSITIVE` | 1 | 1 | 0 | 0.000 | `[6]` | `[8]` |
| `bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE` | `DYNAMIC_POSITIVE` | 10 | 10 | 10 | 8.600 | `[4, 6, 7, 8, 9, 11, 12]` | `[11, 13]` |
| `bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE` | `DYNAMIC_POSITIVE` | 8 | 8 | 8 | 10.750 | `[5, 6, 7, 8]` | `[11, 12]` |
| `bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG` | `DYNAMIC_POSITIVE` | 12 | 12 | 12 | 7.550 | `[4, 5, 6, 7, 8]` | `[10, 11, 12]` |

## Subtype Counts

- `DYNAMIC_POSITIVE`: `4`
- `NON_POSITIVE`: `12`
- `STATIC_POSITIVE`: `1`

## Static Signature Control

The static-positive signature is not by itself a global positive
classifier. It appears in one positive and one non-positive case:

| case | positive | subtype | period center | mean center diff |
| --- | --- | --- | ---: | ---: |
| `bg=0011/T=6/word=1100100/NEGATIVE` | `False` | `NON_POSITIVE` | 1 | 0.000 |
| `bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `True` | `STATIC_POSITIVE` | 1 | 0.000 |

Static-positive transition overlap:

- `bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` overlaps with:
  - `bg=0011/T=6/word=1100100/NEGATIVE` via `-7,-3,-1,1,3,7->-7,-3,-1,1,3,7`

## Dynamic Rule Check

The Phase 69 high-precision dynamic rule (`positive_only_center_transition_count >= 8`)
captures the transition-rich subtype only:

| case | positive | subtype | pos-only center transitions |
| --- | --- | --- | ---: |
| `bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG` | `True` | `DYNAMIC_POSITIVE` | 12 |
| `bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE` | `True` | `DYNAMIC_POSITIVE` | 10 |
| `bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE` | `True` | `DYNAMIC_POSITIVE` | 8 |
| `bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG` | `True` | `DYNAMIC_POSITIVE` | 12 |

## Verdict

`POSITIVE_DYNAMIC_SUBTYPES_CONFIRMED`.

The five positive rule_109 witnesses are not dynamically homogeneous: four are transition-rich positives and one is a static/degenerate positive.

The missed positive from Fase 69 is not a failure of alignment. It is a
static/degenerate positive whose exact transition token is also present
in a negative case. The dynamic positives and the static positive should
therefore be treated as separate mechanistic subfamilies in later work.

## Methodological Limit

- This is a subtype audit over the same 17-case rule_109 catalogue.
- It reuses exact aligned transitions from Fase 69; near-match graph
  structure is still untested.
- The static subtype is not claimed as a causal law. It is a warning that
  `positive` is not dynamically homogeneous.
- No paper or DOI metadata is changed by this phase.
