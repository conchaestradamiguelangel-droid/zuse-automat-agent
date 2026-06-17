# Extended Moving Oscillator Sweep - IC Words 9..12

## Protocol

- Rules: `128` quiescent ECA rules (`f(0,0,0)=0`)
- ICs: `7676` non-zero binary words of length `9..12`
- Width: `256`
- Steps: `300`
- Burn-in: `80`
- Period search: `2..16`
- Max active span: `32`
- Detector: exact normalized active-shape recurrence across three consecutive periods, with constant non-zero drift
- Period-1 moving particles are filtered before strict detection

## Result

- Processed runs: `982528`
- Elapsed seconds: `775.778`
- Candidate detections: `2059`
- Rules with candidates: `rule_6`, `rule_20`, `rule_38`, `rule_52`, `rule_134`, `rule_148`, `rule_166`, `rule_180`
- New rules beyond length 1..8 baseline: none
- Period-1 moving-particle aliases filtered: `9822`
- Rules with period-1 aliases: `rule_2`, `rule_10`, `rule_16`, `rule_24`, `rule_34`, `rule_42`, `rule_48`, `rule_56`, `rule_66`, `rule_74`, `rule_80`, `rule_88`, `rule_98`, `rule_106`, `rule_112`, `rule_120`, `rule_130`, `rule_138`, `rule_144`, `rule_152`, `rule_162`, `rule_170`, `rule_176`, `rule_184`, `rule_194`, `rule_202`, `rule_208`, `rule_216`, `rule_226`, `rule_234`, `rule_240`, `rule_248`

## Candidate Rules

| world | candidates | new_rule | min_len | min_word | T | drift | direction | orbit_span_mean | period_shapes | edge_touch |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rule_6 | 539 | no | 9 | `000000010` | 2 | -2 | left | 0.50 | `[[0], [0, 1]]` | False |
| rule_20 | 545 | no | 9 | `000000001` | 2 | 2 | right | 0.50 | `[[0], [0, 1]]` | False |
| rule_38 | 292 | no | 9 | `000000010` | 2 | -2 | left | 0.50 | `[[0], [0, 1]]` | False |
| rule_52 | 288 | no | 9 | `000000001` | 2 | 2 | right | 0.50 | `[[0], [0, 1]]` | False |
| rule_134 | 157 | no | 9 | `000000010` | 2 | -2 | left | 0.50 | `[[0], [0, 1]]` | False |
| rule_148 | 158 | no | 9 | `000000001` | 2 | 2 | right | 0.50 | `[[0], [0, 1]]` | False |
| rule_166 | 40 | no | 9 | `000000010` | 2 | -2 | left | 0.50 | `[[0], [0, 1]]` | False |
| rule_180 | 40 | no | 9 | `000000001` | 2 | 2 | right | 0.50 | `[[0], [0, 1]]` | False |

## Interpretation

This extends the moving-oscillator sweep from IC lengths `1..8` to `9..12`
without changing the quiescent background or detector. The key question is
whether longer local seeds introduce any moving oscillator rule not already seen
in the length-`1..8` sweep.

Exact-length words may contain leading or trailing zero padding. Therefore a
length-`9..12` witness can be an older shorter glider seed embedded inside a
longer word. The primary scientific signal is whether any new rule appears;
none does.
