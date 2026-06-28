# Fase 32: Rotation Generalization Test for `rule + subpatterns_len4`

## Question

Fase 31 found that `rule + subpatterns_len4` separates the 13 observed
T=15 shape families. Because the length-4 circular subpattern multiset
is invariant under rotation of the length-8 background, Fase 32 tests
whether the predicted family is preserved across all seven non-trivial
background rotations.

Two modes are tested:

- `fixed_ic`: rotate the background but leave the IC centered.
- `cotranslated_ic`: rotate the background and shift IC placement by
  `-rotation`, preserving local IC/background alignment.

## Summary

| mode | runs | T=15 detections | family matches |
| --- | ---: | ---: | ---: |
| `fixed_ic` | 140 | 3 | 1 |
| `cotranslated_ic` | 140 | 140 | 140 |

## By rule

| mode | rule | runs | T=15 detections | family matches |
| --- | ---: | ---: | ---: | ---: |
| `fixed_ic` | 73 | 70 | 2 | 1 |
| `fixed_ic` | 109 | 70 | 1 | 0 |
| `cotranslated_ic` | 73 | 70 | 70 | 70 |
| `cotranslated_ic` | 109 | 70 | 70 | 70 |

## Verdict

**Status:** `ALIGNMENT_CONDITIONED_DESCRIPTOR_CONFIRMED`.

The descriptor survives exactly when IC/background alignment is preserved. The compact state variable is therefore not background alone but `(rule, subpatterns_len4, IC-background alignment)`.

## Falsifiable implication

If `rule + subpatterns_len4` is a genuine compact descriptor, every
rotation of a background with preserved IC/background alignment must
produce the same phase-rotated defect-cycle family. Any failed
co-translated match falsifies the descriptor as stated.
