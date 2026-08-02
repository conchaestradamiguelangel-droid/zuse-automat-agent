# Fase 84: rule_73 h=11 Exact Causal-Equivalence Census

## Question

Does the exact finite-horizon causal equivalence established for
the two Fase 83 controls recur anywhere else in the complete
rule_73/T=12 length-8 cohort at h=11?

Fase 82 audited only 25 comparable events, including eight h=11
cases. Fase 84 audits all 18 physical cases at h=11, including the
ten cases that did not cross the T15-comparability threshold.

## Predeclared Exact Test

Each case is aligned by translation of its 25 local variables.
For every output, the complete packed actual-state truth table and
the background-subtracted defect truth table are compared directly
against the left Fase 83 reference. No distance or threshold is fitted.

An exact operator match requires all 25 actual tables and all 25 defect
tables to be identical. A full Fase 83 recurrence additionally requires
the translated sample/final defects and the 11-step boundary trace to
match. Since Mobius inversion is bijective, identical defect truth
tables imply identical ANF polynomials without recomputing coefficients.

Hashes index candidate classes, but every repeated class is re-simulated
and checked by direct array equality.

## Result

Status: `REFERENCE_OPERATOR_SPLITS_TRANSLATION_EQUIVALENCE_SUBTYPES`.

The four-case reference operator class splits into two exact translated-trajectory subtypes: the original comparable pair and an external non-comparable pair.

- Physical h=11 cases: `18`
- Comparable cases: `8`
- Non-comparable cases: `10`
- Exact causal-map matches including references: `4`
- Matches to original full subtype including references: `2`
- Matches to original full subtype outside reference pair: `0`
- Exact operator matches outside reference pair: `2`
- Actual-only matches outside reference pair: `0`
- Duplicate exact causal classes in full cohort: `4`
- Duplicate full translation-equivalence classes: `2`
- Members of duplicate full-equivalence classes: `4`
- Size of reference causal-operator class: `4`
- Full trajectory subtypes inside reference operator class: `2`
- Concrete mismatches: `0`
- Fase 83 reference hashes reproduced: `True`

## Complete h=11 Cohort

| case | cohort | comparable | input | active outputs | actual rows | defect rows | causal match | boundary | full match |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | --- | --- |
| bg00000011 | baseline_control | false | `0x0b476b4` | 7 | 4/25 | 4/25 | false | false | false |
| bg00001001 | baseline_witness | false | `0x0c620c6` | 9 | 3/25 | 1/25 | false | false | false |
| bg00001011 | baseline_control | false | `0x16a2d6b` | 5 | 4/25 | 2/25 | false | false | false |
| bg00001101 | baseline_witness | false | `0x1631a8b` | 9 | 4/25 | 2/25 | false | false | false |
| bg00001111 | baseline_witness | true | `0x1407c6b` | 10 | 4/25 | 0/25 | false | false | false |
| bg00010011 | baseline_control | false | `0x18c6f8d` | 6 | 4/25 | 2/25 | false | false | false |
| bg00011001 | baseline_witness | true | `0x0df1ad6` | 8 | 3/25 | 2/25 | false | false | false |
| bg00011011 | baseline_witness | false | `0x03580b6` | 7 | 5/25 | 4/25 | false | false | false |
| bg00101011 | baseline_control | false | `0x1b10637` | 6 | 3/25 | 3/25 | false | false | false |
| bg00101101 | baseline_witness | true | `0x158ab8b` | 9 | 4/25 | 1/25 | false | false | false |
| bg00101111 | baseline_witness | true | `0x17c516b` | 8 | 4/25 | 0/25 | false | false | false |
| bg00110101 | baseline_witness | true | `0x147546b` | 9 | 4/25 | 1/25 | false | false | false |
| bg00110111 | baseline_control | false | `0x035b8b0` | 7 | 25/25 | 25/25 | true | true | false |
| bg00111011 | baseline_control | true | `0x0310630` | 4 | 25/25 | 25/25 | true | true | true |
| bg00111101 | baseline_control | true | `0x0310630` | 4 | 25/25 | 25/25 | true | true | true |
| bg00111111 | baseline_witness | true | `0x156e2db` | 10 | 4/25 | 0/25 | false | false | false |
| bg01011011 | baseline_control | false | `0x0b1a036` | 8 | 3/25 | 3/25 | false | false | false |
| bg01101111 | baseline_control | false | `0x035b8b0` | 7 | 25/25 | 25/25 | true | true | false |

## Exact Duplicate Classes

- Class 1: `bg00001011`, `bg00001101`; direct verification = `True`
- Class 2: `bg00001111`, `bg00101111`, `bg00111111`; direct verification = `True`
- Class 3: `bg00101101`, `bg00110101`; direct verification = `True`
- Class 4: `bg00110111`, `bg00111011`, `bg00111101`, `bg01101111`; direct verification = `True`

## Exact Translation-Equivalence Classes

- Subtype 1: `bg00110111`, `bg01101111`; direct verification = `True`
- Subtype 2: `bg00111011`, `bg00111101`; direct verification = `True`

## Interpretation

The Fase 83 operator is not unique to the original pair. It is
shared by four controls, but their realized defect trajectories
split into two exact translation-equivalence subtypes. The
original pair has four active outputs and crosses the scalar
threshold; the external pair has seven active outputs and does
not. Operator identity is therefore not sufficient for the
h=11 crossing: the concrete 25-bit symbolic assignment selects the
trajectory subtype.

## Methodological Limits

- The census is complete only for the 18 rule_73/T=12 primitive
  length-8 cases already fixed by Fases 78-80 at h=11.
- It does not test other rules, local periods, background lengths,
  window widths, or horizons.
- Repeated causal operators are exact finite-horizon equivalences;
  they do not imply global equivalence of infinite backgrounds.
- A unique high-dimensional operator in n=18 does not estimate
  out-of-sample prevalence or predictive accuracy.
- No paper, DOI, tag, release, or classification threshold changed.
