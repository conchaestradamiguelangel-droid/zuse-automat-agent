# Fase 34: Targeted Length-9/10 T=15 Validation

## Protocol

- Rules: `rule_73`, `rule_109`.
- Backgrounds: primitive length-9/10 necklaces with `T_bg=3` under the same rule.
- ICs: 502 non-zero binary words of length 1..8.
- Width: inherited from the periodic-background detector (`256`).
- Sample gate: five distinct defect states under `F^3` after burn-in, repeated for four cycles.

## Summary

- Target backgrounds: `66`.
- Processed runs: `33132`.
- Positive T=15 detections: `90`.
- Positive backgrounds: `8`.
- Elapsed seconds: `287.05`.

| length/rule | target backgrounds | T=15 detections | positive backgrounds |
| --- | ---: | ---: | ---: |
| `len10_rule109` | 22 | 17 | 2 |
| `len10_rule73` | 22 | 67 | 5 |
| `len9_rule109` | 11 | 0 | 0 |
| `len9_rule73` | 11 | 6 | 1 |

## Minimal witnesses

| length | rule | background | detections | min IC | defect states |
| ---: | ---: | --- | ---: | --- | --- |
| 9 | 73 | `001110101` | 6 | `0111011` | `11:421`, `11:471`, `11:575`, `11:505`, `11:489` |
| 10 | 73 | `0000001001` | 9 | `10000001` | `14:30c3`, `14:36db`, `14:340b`, `14:352b`, `14:3123` |
| 10 | 73 | `0000111001` | 3 | `00000011` | `11:6d1`, `12:d8f`, `12:d9d`, `13:1bbb`, `13:1b87` |
| 10 | 73 | `0000111011` | 3 | `00000011` | `11:6d1`, `12:d8f`, `12:d9d`, `13:1bbb`, `13:1b87` |
| 10 | 73 | `0010111011` | 27 | `0000111` | `14:2469`, `14:3669`, `15:76e9`, `15:68e9`, `12:969` |
| 10 | 73 | `0011011101` | 25 | `0001001` | `10:23b`, `10:37b`, `11:76b`, `11:6ab`, `8:9b` |
| 10 | 109 | `0000000011` | 14 | `0100001` | `12:861`, `12:8f1`, `12:af5`, `12:a05`, `12:909` |
| 10 | 109 | `0011111011` | 3 | `1001111` | `13:1e6b`, `13:14eb`, `13:11eb`, `9:1ab`, `11:6ab` |

## Verdict

**Status:** `T15_EXTERNAL_LEN9_LEN10_FOUND`.

The T=15 mechanism does generalize outside primitive length-8 backgrounds when the prerequisite `T_bg=3` is preserved. These are genuine external backgrounds, not rotations of the original representative set.
