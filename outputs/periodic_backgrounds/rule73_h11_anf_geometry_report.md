# Fase 81: rule_73 h=11 Output-Resolved ANF Geometry

## Question

Are the two Fase 80 controls that cross the T15-comparability threshold
at `h=11` geometrically distinct from the six baseline witnesses that are
also comparable at `h=11`?

This phase reuses the committed Fase 80 cohort and its deterministic h=11
measurements. No threshold is fitted. Each active output is aligned to the
center of the final defect and represented by normalized monomial mass,
normalized degree mass, and active support.

The separation test was fixed before inspecting pairwise distances. The
two controls count as a geometric subtype only if they are a strictly
separated mutual pair under both signed and radial monomial total-variation
distance. Degree and support distances are diagnostics, not rescue criteria.

The analyzer stores output-wise degree and monomial counts, not individual
ANF coefficient identities. The claim is therefore about output-resolved
ANF geometry, not polynomial identity.

## Result

Status: `H11_CONTROL_GEOMETRY_CLUSTER_FOUND`.

The two h=11 controls form a strictly separated mutual pair under both predeclared monomial-geometry distances.

- h=11 comparable cases: `8`
- Baseline witnesses: `6`
- Baseline controls: `2`
- Separation metrics passed: `['signed_monomial_tv', 'radial_monomial_tv']`
- Control-pair distances: `{'signed_monomial_tv': 0.0, 'radial_monomial_tv': 0.0, 'signed_degree_tv': 0.0, 'support_jaccard': 0.0}`
- Control raw measurements have distinct hashes: `True`
- Measurement source: `deterministic h=11 remeasurement`
- Concrete mismatches: `0`

## Case Geometry

| cohort | background | active outputs | span | center mass | weighted radius | symmetry error | max-mass x2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| baseline_witness | `00001111` | 10 | 20 | 0.000000 | 2.032547 | 0.442257 | [-3] |
| baseline_witness | `00011001` | 8 | 17 | 0.000000 | 1.932228 | 0.764734 | [-2] |
| baseline_witness | `00101101` | 9 | 16 | 0.000000 | 1.288905 | 0.357895 | [-3, -1, 1] |
| baseline_witness | `00101111` | 8 | 20 | 0.000000 | 1.406477 | 0.998460 | [-1] |
| baseline_witness | `00110101` | 9 | 16 | 0.000000 | 1.218793 | 0.244376 | [-1, 1] |
| baseline_control | `00111011` | 4 | 7 | 0.000000 | 1.728914 | 0.747946 | [2] |
| baseline_control | `00111101` | 4 | 7 | 0.000000 | 1.728914 | 0.747946 | [2] |
| baseline_witness | `00111111` | 10 | 18 | 0.000000 | 2.948544 | 0.723232 | [3] |

## Predeclared Separation Tests

| metric | control-control | nearest witness from control 1 | nearest witness from control 2 | separated |
| --- | ---: | --- | --- | --- |
| signed_monomial_tv | 0.000000 | bg00011001 (0.770631) | bg00011001 (0.770631) | true |
| radial_monomial_tv | 0.000000 | bg00011001 (0.069823) | bg00011001 (0.069823) | true |

## Coarse Symmetry Audit

- Background orbit relations: `[]`
- IC orbit relations: `[{'transform': 'rotation', 'shift': 2}, {'transform': 'reflection_rotation', 'shift': 1}]`

The control ICs are cyclic variants, but their length-8 backgrounds
are not related by rotation, reflection, complement, or reflected
complement. Their identical output-resolved profiles are therefore
not explained by the coarse background orbit.

## Nearest Neighbors

| metric | case | cohort | nearest | nearest cohort | distance |
| --- | --- | --- | --- | --- | ---: |
| signed_monomial_tv | bg00001111 | baseline_witness | bg00111111 | baseline_witness | 0.574304 |
| signed_monomial_tv | bg00011001 | baseline_witness | bg00111011 | baseline_control | 0.770631 |
| signed_monomial_tv | bg00101101 | baseline_witness | bg00110101 | baseline_witness | 0.323500 |
| signed_monomial_tv | bg00101111 | baseline_witness | bg00110101 | baseline_witness | 0.465976 |
| signed_monomial_tv | bg00110101 | baseline_witness | bg00101101 | baseline_witness | 0.323500 |
| signed_monomial_tv | bg00111011 | baseline_control | bg00111101 | baseline_control | 0.000000 |
| signed_monomial_tv | bg00111101 | baseline_control | bg00111011 | baseline_control | 0.000000 |
| signed_monomial_tv | bg00111111 | baseline_witness | bg00001111 | baseline_witness | 0.574304 |
| radial_monomial_tv | bg00001111 | baseline_witness | bg00111111 | baseline_witness | 0.348211 |
| radial_monomial_tv | bg00011001 | baseline_witness | bg00111011 | baseline_control | 0.069823 |
| radial_monomial_tv | bg00101101 | baseline_witness | bg00110101 | baseline_witness | 0.125560 |
| radial_monomial_tv | bg00101111 | baseline_witness | bg00101101 | baseline_witness | 0.217055 |
| radial_monomial_tv | bg00110101 | baseline_witness | bg00101101 | baseline_witness | 0.125560 |
| radial_monomial_tv | bg00111011 | baseline_control | bg00111101 | baseline_control | 0.000000 |
| radial_monomial_tv | bg00111101 | baseline_control | bg00111011 | baseline_control | 0.000000 |
| radial_monomial_tv | bg00111111 | baseline_witness | bg00001111 | baseline_witness | 0.348211 |
| signed_degree_tv | bg00001111 | baseline_witness | bg00101111 | baseline_witness | 0.428571 |
| signed_degree_tv | bg00011001 | baseline_witness | bg00111011 | baseline_control | 0.723684 |
| signed_degree_tv | bg00101101 | baseline_witness | bg00110101 | baseline_witness | 0.331429 |
| signed_degree_tv | bg00101111 | baseline_witness | bg00001111 | baseline_witness | 0.428571 |
| signed_degree_tv | bg00110101 | baseline_witness | bg00101101 | baseline_witness | 0.331429 |
| signed_degree_tv | bg00111011 | baseline_control | bg00111101 | baseline_control | 0.000000 |
| signed_degree_tv | bg00111101 | baseline_control | bg00111011 | baseline_control | 0.000000 |
| signed_degree_tv | bg00111111 | baseline_witness | bg00101101 | baseline_witness | 0.491525 |
| support_jaccard | bg00001111 | baseline_witness | bg00101111 | baseline_witness | 0.500000 |
| support_jaccard | bg00011001 | baseline_witness | bg00111011 | baseline_control | 0.800000 |
| support_jaccard | bg00101101 | baseline_witness | bg00110101 | baseline_witness | 0.500000 |
| support_jaccard | bg00101111 | baseline_witness | bg00001111 | baseline_witness | 0.500000 |
| support_jaccard | bg00110101 | baseline_witness | bg00101101 | baseline_witness | 0.500000 |
| support_jaccard | bg00111011 | baseline_control | bg00111101 | baseline_control | 0.000000 |
| support_jaccard | bg00111101 | baseline_control | bg00111011 | baseline_control | 0.000000 |
| support_jaccard | bg00111111 | baseline_witness | bg00101101 | baseline_witness | 0.642857 |

## Pairwise Distances

| left | right | cohorts | signed monomial TV | radial monomial TV | signed degree TV | support Jaccard |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| bg00001111 | bg00011001 | baseline_witness/baseline_witness | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00001111 | bg00101101 | baseline_witness/baseline_witness | 0.638326 | 0.572209 | 0.485714 | 0.642857 |
| bg00001111 | bg00101111 | baseline_witness/baseline_witness | 0.700687 | 0.700687 | 0.428571 | 0.500000 |
| bg00001111 | bg00110101 | baseline_witness/baseline_witness | 0.721821 | 0.673433 | 0.480000 | 0.642857 |
| bg00001111 | bg00111011 | baseline_witness/baseline_control | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00001111 | bg00111101 | baseline_witness/baseline_control | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00001111 | bg00111111 | baseline_witness/baseline_witness | 0.574304 | 0.348211 | 0.497175 | 0.666667 |
| bg00011001 | bg00101101 | baseline_witness/baseline_witness | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00011001 | bg00101111 | baseline_witness/baseline_witness | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00011001 | bg00110101 | baseline_witness/baseline_witness | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00011001 | bg00111011 | baseline_witness/baseline_control | 0.770631 | 0.069823 | 0.723684 | 0.800000 |
| bg00011001 | bg00111101 | baseline_witness/baseline_control | 0.770631 | 0.069823 | 0.723684 | 0.800000 |
| bg00011001 | bg00111111 | baseline_witness/baseline_witness | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101101 | bg00101111 | baseline_witness/baseline_witness | 0.706156 | 0.217055 | 0.685714 | 0.785714 |
| bg00101101 | bg00110101 | baseline_witness/baseline_witness | 0.323500 | 0.125560 | 0.331429 | 0.500000 |
| bg00101101 | bg00111011 | baseline_witness/baseline_control | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101101 | bg00111101 | baseline_witness/baseline_control | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101101 | bg00111111 | baseline_witness/baseline_witness | 0.859863 | 0.570793 | 0.491525 | 0.642857 |
| bg00101111 | bg00110101 | baseline_witness/baseline_witness | 0.465976 | 0.301815 | 0.548571 | 0.692308 |
| bg00101111 | bg00111011 | baseline_witness/baseline_control | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101111 | bg00111101 | baseline_witness/baseline_control | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00101111 | bg00111111 | baseline_witness/baseline_witness | 0.739378 | 0.704252 | 0.790960 | 0.875000 |
| bg00110101 | bg00111011 | baseline_witness/baseline_control | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00110101 | bg00111101 | baseline_witness/baseline_control | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00110101 | bg00111111 | baseline_witness/baseline_witness | 0.706857 | 0.672693 | 0.570621 | 0.733333 |
| bg00111011 | bg00111101 | baseline_control/baseline_control | 0.000000 | 0.000000 | 0.000000 | 0.000000 |
| bg00111011 | bg00111111 | baseline_control/baseline_witness | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| bg00111101 | bg00111111 | baseline_control/baseline_witness | 1.000000 | 1.000000 | 1.000000 | 1.000000 |

## Interpretation

The scalar fit equality at h=11 hides a distinct output-resolved
geometry: the controls form their own compact pair under both
signed and radial monomial mass.

## Methodological Limits

- The comparison contains six witnesses and two controls from one rule,
  one local period, and one horizon.
- The criterion tests a predeclared cluster relation; it does not fit a
  classifier or estimate out-of-sample accuracy.
- Profiles retain output-wise counts and degrees but not monomial
  coefficient identities.
- A positive cluster would be a hypothesis about the h=11 crossing, not
  a universal ECA mechanism.
