# Moving Oscillator Sweep

Direct physical search for local oscillators that repeat after a period
while translating by a fixed non-zero displacement.

## Protocol

- Rules: 128 quiescent ECA rules (`f(0,0,0)=0`)
- ICs: 502 non-zero binary words of length 1..8
  (502 exact-length non-zero words; 510 is the inclusive count before
  excluding the all-zero word at each length.)
- Width: 256
- Steps: 300
- Burn-in: 80
- Period search: 2..16
- Max active span: 32
- Detector: exact normalized active shape recurrence across three
  consecutive periods, with constant non-zero drift.
- Period-1 moving particles are filtered before the T=2..16 search,
  because otherwise they alias as trivial moving oscillators at every
  multiple period.

## Results

- Total expected runs: 64256
- Processed runs: 64256
- Elapsed seconds: 312.602
- Candidate detections: 613
- Rules with candidates: [6, 20, 38, 52, 134, 148, 166, 180]
- Period-1 moving-particle aliases filtered: 0
- Rules with period-1 aliases: []

| rule | candidates | minimal IC | T | drift | direction | orbit_span_mean | period_shapes | edge_touch |
| --- | ---: | --- | ---: | ---: | --- | ---: | --- | --- |
| 6 | 109 | `10` | 2 | -2 | left | 0.50 | `[[0], [0, 1]]` | False |
| 20 | 110 | `1` | 2 | 2 | right | 0.50 | `[[0], [0, 1]]` | False |
| 38 | 100 | `10` | 2 | -2 | left | 0.50 | `[[0], [0, 1]]` | False |
| 52 | 98 | `1` | 2 | 2 | right | 0.50 | `[[0], [0, 1]]` | False |
| 134 | 67 | `10` | 2 | -2 | left | 0.50 | `[[0], [0, 1]]` | False |
| 148 | 65 | `1` | 2 | 2 | right | 0.50 | `[[0], [0, 1]]` | False |
| 166 | 32 | `10` | 2 | -2 | left | 0.50 | `[[0], [0, 1]]` | False |
| 180 | 32 | `1` | 2 | 2 | right | 0.50 | `[[0], [0, 1]]` | False |

## Comparison With Fase 18

- Fase 18 (stationary local oscillator): only `rule_108` produced
  stationary local period-2 oscillators under the quiescent protocol.
- Fase moving: `rule_6`, `rule_20`, `rule_38`, `rule_52`, `rule_134`, `rule_148`, `rule_166`, `rule_180`.
- Period-1 moving particles/gliders filtered before strict detection: none.
- Conclusion: moving oscillators exist in ECA under this protocol.
