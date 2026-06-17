# Extended Stationary Oscillator Sweep - IC Words 9..12

## Protocol

- Rules: `128` quiescent ECA rules (`f(0,0,0)=0`)
- ICs: `7676` non-zero binary words of length `9..12`
- Width: `128`
- Steps: `200`
- Burn-in: `80`
- Periods tested: `2..16`
- Locality filter: post-burn-in active span `<= 32`
- Detector: exact stationary recurrence, zero drift

## Result

- Processed runs: `982528`
- Elapsed seconds: `708.666`
- Candidate detections: `3802`
- Rules with candidates: `rule_108`
- New rules beyond length 1..8 baseline: none

## Candidate Rules

| world | candidates | new_rule | min_len | min_word | T | span | motif |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule_108 | 3802 | no | 9 | `000000101` | 2 | 3 | ### / #.# |

## Interpretation

This extends the Fase 18 stationary search from IC lengths `1..8` to `9..12`
without changing the quiescent background, width, step count, period window, or
locality filter. The key question is whether longer local seeds introduce any
stationary oscillator rule not already seen in the length-`1..8` sweep.

Exact-length words may contain leading or trailing zero padding. Therefore a
length-`9..12` witness can be an older shorter motif embedded inside a longer
word. The primary scientific signal is whether any new rule appears; none does.
