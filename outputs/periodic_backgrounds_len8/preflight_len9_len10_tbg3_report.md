# Fase 34 Preflight: T_bg=3 Availability in Length-9/10 Backgrounds

## Question

Before launching a length-9/10 T=15 validation, check whether primitive
backgrounds of those lengths can still have temporal background period
`T_bg=3` under `rule_73` and `rule_109`. If no such backgrounds exist,
the 5:1 locking mechanism cannot be tested in the same form.

## Period census

| length | rule | primitive necklaces | period counts | T_bg=3 |
| ---: | ---: | ---: | --- | ---: |
| 8 | 73 | 30 | `{'2': 8, '3': 17, '6': 5}` | 17 |
| 8 | 109 | 30 | `{'2': 8, '3': 17, '6': 5}` | 17 |
| 9 | 73 | 56 | `{'1': 5, '2': 40, '3': 11}` | 11 |
| 9 | 109 | 56 | `{'1': 5, '2': 40, '3': 11}` | 11 |
| 10 | 73 | 99 | `{'1': 4, '2': 45, '3': 22, '8': 28}` | 22 |
| 10 | 109 | 99 | `{'1': 4, '2': 45, '3': 22, '8': 28}` | 22 |

## T_bg=3 examples

- len `9`, rule `73`: `000000101`, `000000111`, `000001001`, `000001111`, `001001111`, `001010111`, `001011101`, `001110101`, `001111111`, `010101111`
- len `9`, rule `109`: `000000001`, `000000011`, `000010101`, `000011011`, `000011111`, `000101011`, `000101101`, `000110101`, `000111111`, `010111111`
- len `10`, rule `73`: `0000001001`, `0000001111`, `0000010011`, `0000011001`, `0000011011`, `0000100111`, `0000101011`, `0000110101`, `0000110111`, `0000111001`
- len `10`, rule `109`: `0000000011`, `0000101011`, `0000101101`, `0000110101`, `0000111111`, `0001001001`, `0001001011`, `0001001101`, `0001001111`, `0001011001`

## Verdict

**Status:** `T_BG_3_AVAILABLE_LEN9_LEN10`.

Length-9 and length-10 primitive backgrounds do contain `T_bg=3` cases
under both `rule_73` and `rule_109`: 11 per rule at length 9 and 22 per
rule at length 10. Therefore a targeted Fase 34 validation is meaningful.

The correct next experiment is not a blind all-rule sweep. It should target
`rule_73/rule_109`, primitive len-9/10 backgrounds with `T_bg=3`, and the
same IC family/protocol used for the T=15 mechanism.
