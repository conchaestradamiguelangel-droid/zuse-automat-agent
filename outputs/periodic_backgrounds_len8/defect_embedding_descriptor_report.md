# Fase 38: Defect Embedding Descriptor for T=15 Families

## Question

Fase 37 showed that the canonical period-3 background orbit alone is too
coarse. Fase 38 adds embedding variables: temporal orbit step, spatial
rotation offset, IC start alignment, and defect anchor alignment.

## Descriptor tests

| descriptor | buckets | ambiguous buckets | determines family |
| --- | ---: | ---: | --- |
| `entry_embedding` | 13 | 5 | `False` |
| `sample_embedding` | 14 | 2 | `False` |
| `sample_embedding_ic_start` | 16 | 2 | `False` |
| `sample_embedding_ic_len_start` | 16 | 2 | `False` |
| `sample_embedding_defect_anchor` | 16 | 2 | `False` |
| `sample_embedding_defect_state` | 19 | 0 | `True` |
| `full_embedding_without_ic_word` | 17 | 2 | `False` |

## Representative embeddings

| family | rule | background | entry step/rot | sample step/rot | IC start sample | defect anchor sample |
| --- | ---: | --- | --- | --- | ---: | ---: |
| `F00` | 109 | `00001001` | 0/0 | 0/0 | 5 | 1 |
| `F00` | 109 | `00010011` | 2/4 | 0/7 | 5 | 7 |
| `F00` | 109 | `00011001` | 2/5 | 0/0 | 7 | 1 |
| `F01` | 73 | `00110111` | 0/4 | 1/1 | 6 | 6 |
| `F01` | 73 | `00111011` | 0/0 | 1/5 | 1 | 6 |
| `F01` | 73 | `01101111` | 1/0 | 1/0 | 4 | 4 |
| `F02` | 73 | `00001111` | 2/5 | 1/0 | 4 | 4 |
| `F02` | 73 | `00111111` | 0/6 | 1/3 | 0 | 3 |
| `F02` | 109 | `00001101` | 2/5 | 0/0 | 5 | 4 |
| `F03` | 73 | `00110101` | 0/4 | 2/6 | 3 | 3 |
| `F03` | 109 | `00110101` | 2/0 | 1/0 | 5 | 3 |
| `F04` | 73 | `00101111` | 0/3 | 1/0 | 5 | 2 |
| `F05` | 109 | `00001011` | 2/5 | 0/0 | 5 | 1 |
| `F06` | 73 | `00101101` | 2/0 | 2/0 | 5 | 7 |
| `F07` | 109 | `00111111` | 2/0 | 2/0 | 4 | 4 |
| `F08` | 109 | `00001111` | 1/5 | 0/0 | 5 | 1 |
| `F09` | 73 | `00000011` | 0/0 | 0/0 | 5 | 1 |
| `F10` | 73 | `00001001` | 0/3 | 2/5 | 1 | 6 |
| `F11` | 109 | `01101111` | 2/5 | 1/5 | 2 | 5 |
| `F12` | 109 | `00000011` | 2/2 | 0/5 | 2 | 3 |

## Ambiguity structure

The scalar embedding descriptors narrow the problem but do not close it.
`sample_embedding` leaves two ambiguous buckets: one under `rule_109`
mixing F00/F02/F05/F08, and one under `rule_73` mixing F01/F02/F04.
Adding IC start, IC length, or defect-anchor alignment does not remove
those ambiguities. The first successful descriptor includes the actual
canonical defect state at the sampled phase.

## Verdict

**Status:** `EMBEDDING_DESCRIPTOR_FOUND`.

The first descriptor that determines family is `sample_embedding_defect_state`. This identifies the missing state variable left open by Fase 37: not just the background orbit embedding, but the local defect shape after burn-in. The resulting sufficient state is `(rule, sample_orbit_step, sample_rotation_offset, defect_state0)`. This is a constructive descriptor, but it is not yet a closed-form prediction from the initial background and IC alone.
