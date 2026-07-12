# Fase 59: rule_109/T=8 Background-IC Alignment Audit

## Question

What alignment descriptor separates `rule_109/bg=0011/T=8` (`NEGATIVE`)
from `rule_109/bg=0110/T=8` and `rule_109/bg=1100/T=8`
(`HORIZON_ACCEPTABLE`)?

This phase uses existing Fase 55 census cases only. It runs no new ECA
or ANF simulation.

## Target Cases

| background | category | IC word | bg phase | IC active | bg@IC | xor defect | defect support | defect offsets mod 4 |
| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |
| `0011` | `NEGATIVE` | `1000010` | 0 | `[0, 5]` | `00` | `1011011` | 5 | `[0, 1, 2, 3]` |
| `0110` | `HORIZON_ACCEPTABLE` | `0000011` | 1 | `[5, 6]` | `11` | `0110000` | 2 | `[1, 2]` |
| `1100` | `HORIZON_ACCEPTABLE` | `00000110` | 2 | `[5, 6]` | `10` | `11001010` | 4 | `[0, 1, 2]` |

## Descriptor Scan

- `bg_phase_in_0011_orbit` -> PARTIAL: 0011:0, 0110:1, 1100:2
- `ic_length`: 0011:7, 0110:7, 1100:8
- `ic_active_bits` -> DISCRIMINANT: 0011:(0, 5), 0110:(5, 6), 1100:(5, 6)
- `ic_active_offsets_mod4` -> DISCRIMINANT: 0011:(0, 1), 0110:(1, 2), 1100:(1, 2)
- `ic_support_size`: 0011:2, 0110:2, 1100:2
- `ic_span` -> DISCRIMINANT: 0011:6, 0110:2, 1100:2
- `background_window` -> PARTIAL: 0011:0011001, 0110:0110011, 1100:11001100
- `bg_at_ic` -> PARTIAL: 0011:00, 0110:11, 1100:10
- `bg_at_ic_ones` -> PARTIAL: 0011:0, 0110:2, 1100:1
- `xor_defect` -> PARTIAL: 0011:1011011, 0110:0110000, 1100:11001010
- `defect_active_bits` -> PARTIAL: 0011:(0, 2, 3, 5, 6), 0110:(1, 2), 1100:(0, 1, 4, 6)
- `defect_phase_offset` -> PARTIAL: 0011:(0, 1, 2, 3), 0110:(1, 2), 1100:(0, 1, 2)
- `defect_support_size` -> PARTIAL: 0011:5, 0110:2, 1100:4
- `defect_span`: 0011:7, 0110:2, 1100:7
- `defect_weight_by_mod4` -> PARTIAL: 0011:((0, 1), (1, 1), (2, 2), (3, 1)), 0110:((1, 1), (2, 1)), 1100:((0, 2), (1, 1), (2, 1))

## Verdict

`ALIGNMENT_DISCRIMINANT_FOUND`.

The following descriptors separate the negative case from both positives:
- `ic_active_bits`
- `ic_active_offsets_mod4`
- `ic_span`

The exact shared discriminator in this three-case audit is IC placement: both positive cases use adjacent active IC bits at offsets `(1, 2)` with span 2, while the negative case uses separated bits at offsets `(0, 1)` with span 6.

Background-subtracted descriptors (`xor_defect`, `defect_phase_offset`, and defect weights) also separate the negative case from the positives, but the two positives do not share one identical defect value. They therefore remain partial alignment evidence rather than the exact rule at this stage.

## Methodological Limit

- The verdict is based on three T=8 cases only. Any discriminator is a hypothesis that must be validated on broader rule_109 cases before being promoted to a causal law.
