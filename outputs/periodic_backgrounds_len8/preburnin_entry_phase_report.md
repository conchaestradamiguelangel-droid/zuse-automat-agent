# Fase 39: Pre-burn-in Entry Phase Predictors

## Question

Fase 38 showed that `defect_state0` after burn-in determines the T=15
family together with rule and sampled background embedding. Fase 39 asks
whether the stable-cycle entry phase can be predicted from the initial
local background/IC configuration before running the 81-step burn-in.

- Entry times observed: `[0, 3, 6, 9, 12]`.
- Entry time counts: `{'0': 2, '3': 15, '6': 1, '9': 1, '12': 1}`.

## Descriptor tests

| target | descriptor | buckets | singleton buckets | ambiguous buckets | determines target | posthoc | compact enough |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| `entry_phase` | `rule_ic` | 18 | 17 | 0 | `True` | `False` | `False` |
| `entry_phase` | `rule_ic_len` | 8 | 4 | 3 | `False` | `False` | `False` |
| `entry_phase` | `rule_entry_time` | 7 | 5 | 0 | `True` | `True` | `False` |
| `entry_phase` | `rule_entry_time_phase` | 7 | 5 | 0 | `True` | `True` | `False` |
| `entry_phase` | `local_r1` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r2` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r3` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r4` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r5` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r_with_ic1` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r_with_ic2` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r_with_ic3` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r_with_ic4` | 20 | 20 | 0 | `True` | `False` | `False` |
| `entry_phase` | `local_r_with_ic5` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `rule_ic` | 18 | 17 | 1 | `False` | `False` | `False` |
| `family_id` | `rule_ic_len` | 8 | 4 | 4 | `False` | `False` | `False` |
| `family_id` | `rule_entry_time` | 7 | 5 | 2 | `False` | `True` | `False` |
| `family_id` | `rule_entry_time_phase` | 7 | 5 | 2 | `False` | `True` | `False` |
| `family_id` | `local_r1` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r2` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r3` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r4` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r5` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r_with_ic1` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r_with_ic2` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r_with_ic3` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r_with_ic4` | 20 | 20 | 0 | `True` | `False` | `False` |
| `family_id` | `local_r_with_ic5` | 20 | 20 | 0 | `True` | `False` | `False` |

## Entry summary

| family | rule | background | IC | entry time | entry phase | sample phase |
| --- | ---: | --- | --- | ---: | ---: | ---: |
| `F00` | 109 | `00001001` | `0001001` | 3 | 4 | 0 |
| `F00` | 109 | `00010011` | `01001` | 3 | 4 | 0 |
| `F00` | 109 | `00011001` | `01` | 3 | 4 | 0 |
| `F01` | 73 | `00110111` | `011011` | 3 | 4 | 0 |
| `F01` | 73 | `00111011` | `00100100` | 3 | 4 | 0 |
| `F01` | 73 | `01101111` | `01101110` | 3 | 4 | 0 |
| `F02` | 73 | `00001111` | `00100000` | 9 | 1 | 0 |
| `F02` | 73 | `00111111` | `0001100` | 3 | 4 | 0 |
| `F02` | 109 | `00001101` | `0100001` | 6 | 0 | 0 |
| `F03` | 73 | `00110101` | `011010` | 3 | 4 | 0 |
| `F03` | 109 | `00110101` | `010101` | 3 | 4 | 0 |
| `F04` | 73 | `00101111` | `0000111` | 3 | 4 | 0 |
| `F05` | 109 | `00001011` | `0001001` | 3 | 4 | 0 |
| `F06` | 73 | `00101101` | `010110` | 3 | 4 | 0 |
| `F07` | 109 | `00111111` | `00111111` | 0 | 3 | 0 |
| `F08` | 109 | `00001111` | `0001001` | 3 | 4 | 0 |
| `F09` | 73 | `00000011` | `0000011` | 0 | 3 | 0 |
| `F10` | 73 | `00001001` | `00110010` | 3 | 4 | 0 |
| `F11` | 109 | `01101111` | `0101001` | 3 | 4 | 0 |
| `F12` | 109 | `00000011` | `1110101` | 12 | 2 | 0 |

## Verdict

**Status:** `NONCOMPACT_PREBURNIN_DESCRIPTOR_FOUND`.

The first exact tested descriptor is `rule_ic`, but the successful local descriptors mostly create singleton buckets. This is a sample-level identifier, not yet a compact symbolic law. The useful structural result is temporal: all 20 representatives enter the stable five-cycle by t=12, and 15/20 enter at t=3.
