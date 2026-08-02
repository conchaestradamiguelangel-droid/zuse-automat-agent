# Fase 82: rule_73 Control-Signature Recurrence Grid

## Question

Does the exact output-resolved ANF geometry shared by the two h=11
control crossings from Fase 81 recur among any of the 25 comparable
measurements in the complete Fase 80 horizon grid?

The Fase 80 grid covers horizons h=8..16. Comparable measurements occur
only at h=10..14, with counts 1, 8, 9, 5, and 2 respectively. Fase 82
therefore audits 25 comparable events, not every measured grid point.

## Signature Definition

Each active output is centered by translation and represented exactly as:

`(coordinate_x2, degree, monomial_count, complete degree_histogram)`

The oriented signature is the sorted tuple of these output records. The
reflection-canonical signature is the lexicographically smaller of the
oriented signature and its coordinate-reflected copy. SHA-256 hashes are
deterministic content identifiers only; no cryptographic or post-quantum
security claim is made.

These signatures do not establish exact ANF polynomial identity because
the analyzer does not retain individual monomial coefficient identities.

Approximate distances from Fase 81 are reported separately and never used
to rescue an exact non-match.

## Result

Status: `CONTROL_SIGNATURE_UNIQUE_TO_H11_PAIR`.

The exact h=11 control geometry occurs only in the two reference controls across all 25 comparable events.

- Comparable events: `25`
- Distinct physical cases: `11`
- Comparable horizon counts: `{'10': 1, '11': 8, '12': 9, '13': 5, '14': 2}`
- Measurement sources: `{'committed Fase 78 result': 9, 'deterministic remeasurement': 16}`
- Oriented exact matches: `2`
- Reflection-canonical exact matches: `2`
- Oriented matches outside reference pair: `0`
- Reflection matches outside reference pair: `0`
- Concrete mismatches: `0`

## Reference Signature

- Reference events: `['rule73_bg00111011_T12_h11', 'rule73_bg00111101_T12_h11']`
- Oriented SHA-256: `7f17ad40bb5ce02da8d4b718ef3385ec30c34cdb2ecc85d07b91c8f473e5f9a7`
- Reflection-canonical SHA-256: `504b516783b96aabc93aae26b51db3f2880bf31e4c4516189d9a511dcc5d132a`
- Reference raw measurements distinct: `True`

## Exact Oriented Matches

| event | cohort | horizon | background | IC |
| --- | --- | ---: | --- | --- |
| bg00111011_T12_h11 | baseline_control | 11 | `00111011` | `011` |
| bg00111101_T12_h11 | baseline_control | 11 | `00111101` | `101` |

## Exact Matches Under Reflection

| event | cohort | horizon | oriented match |
| --- | --- | ---: | --- |
| bg00111011_T12_h11 | baseline_control | 11 | true |
| bg00111101_T12_h11 | baseline_control | 11 | true |

## Approximate Neighbors

Exact reference members are excluded from these rankings.

### signed_monomial_tv

| rank | event | cohort | horizon | distance |
| ---: | --- | --- | ---: | ---: |
| 1 | bg00001101_T12_h12 | baseline_witness | 12 | 0.588135 |
| 2 | bg00101111_T12_h13 | baseline_witness | 13 | 0.607156 |
| 3 | bg00011011_T12_h12 | baseline_witness | 12 | 0.639114 |
| 4 | bg00110101_T12_h10 | baseline_witness | 10 | 0.649168 |
| 5 | bg00011001_T12_h11 | baseline_witness | 11 | 0.770631 |

### radial_monomial_tv

| rank | event | cohort | horizon | distance |
| ---: | --- | --- | ---: | ---: |
| 1 | bg00011001_T12_h11 | baseline_witness | 11 | 0.069823 |
| 2 | bg00101111_T12_h13 | baseline_witness | 13 | 0.276053 |
| 3 | bg00110101_T12_h10 | baseline_witness | 10 | 0.400077 |
| 4 | bg00011001_T12_h12 | baseline_witness | 12 | 0.485262 |
| 5 | bg00011011_T12_h12 | baseline_witness | 12 | 0.514995 |

### signed_degree_tv

| rank | event | cohort | horizon | distance |
| ---: | --- | --- | ---: | ---: |
| 1 | bg00011011_T12_h12 | baseline_witness | 12 | 0.619883 |
| 2 | bg00001101_T12_h12 | baseline_witness | 12 | 0.722222 |
| 3 | bg00011001_T12_h11 | baseline_witness | 11 | 0.723684 |
| 4 | bg00110101_T12_h10 | baseline_witness | 10 | 0.759036 |
| 5 | bg00101111_T12_h13 | baseline_witness | 13 | 0.762069 |

### support_jaccard

| rank | event | cohort | horizon | distance |
| ---: | --- | --- | ---: | ---: |
| 1 | bg00011011_T12_h12 | baseline_witness | 12 | 0.666667 |
| 2 | bg00001101_T12_h12 | baseline_witness | 12 | 0.800000 |
| 3 | bg00011001_T12_h11 | baseline_witness | 11 | 0.800000 |
| 4 | bg00101111_T12_h13 | baseline_witness | 13 | 0.800000 |
| 5 | bg00011001_T12_h12 | baseline_witness | 12 | 0.818182 |

## Complete Comparable Grid

| event | cohort | source | oriented | reflection | signed TV | radial TV | degree TV | support Jaccard |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| bg00110101_T12_h10 | baseline_witness | deterministic remeasurement | false | false | 0.649168 | 0.400077 | 0.759036 | 0.818182 |
| bg00001111_T12_h11 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00011001_T12_h11 | baseline_witness | deterministic remeasurement | false | false | 0.770631 | 0.069823 | 0.723684 | 0.800000 |
| bg00101101_T12_h11 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101111_T12_h11 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00110101_T12_h11 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00111011_T12_h11 | baseline_control | deterministic remeasurement | true | true | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| bg00111101_T12_h11 | baseline_control | deterministic remeasurement | true | true | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| bg00111111_T12_h11 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00001001_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00001101_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 0.588135 | 0.588135 | 0.722222 | 0.800000 |
| bg00001111_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00011001_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 0.830793 | 0.485262 | 0.763736 | 0.818182 |
| bg00011011_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 0.639114 | 0.514995 | 0.619883 | 0.666667 |
| bg00101101_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101111_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00110101_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00111111_T12_h12 | baseline_witness | committed Fase 78 result | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00001101_T12_h13 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00001111_T12_h13 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101101_T12_h13 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101111_T12_h13 | baseline_witness | deterministic remeasurement | false | false | 0.607156 | 0.276053 | 0.762069 | 0.800000 |
| bg00110101_T12_h13 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101101_T12_h14 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00111111_T12_h14 | baseline_witness | deterministic remeasurement | false | false | 1.000000 | 1.000000 | 1.000000 | 1.000000 |

## Interpretation

The two Fase 81 controls define a unique exact geometry within
the 25-event comparable grid. Neither translation-oriented nor
reflection-canonical matching finds the signature in a witness or
at another horizon.

## Methodological Limits

- The grid starts from 18 physical rule_73/T=12 cases. The 25 comparable
  events come from 11 of them; repeated horizons are not independent
  oscillators.
- Comparable support is limited to h=10..14 even though the measured
  grid spans h=8..16.
- Exact geometry retains per-output counts and degree histograms, not
  individual ANF monomial identities.
- Approximate rankings are descriptive and have no fitted cutoff.
- The exact signature is high-dimensional; uniqueness in 25 events
  does not estimate out-of-sample discrimination by itself.
- The result remains local to rule_73 and primitive length-8
  backgrounds.
