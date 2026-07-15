# Fase 66: rule_109 Residual Persistence Audit

## Question

Is `rule_109/bg=1100/T=8/word=00000110` a genuine persistent oscillator,
or a transient that only passed the `HORIZON_ACCEPTABLE` threshold in the
finite Fase 55 window?

## Setup

- Rule: `109`
- Background: `1100`
- IC word: `00000110`
- Catalog T_local: `8`
- Width: `256`
- Horizon: `t=0..500`
- Defect: `state_with_IC(t) XOR background_only(t)`.

## Defect Size Trace

- Sampled every 10 steps.
- Sparkline: `.==#===#===#===#===#===#===#===#===#===#===#===#===`

| t | defect_size | defect_span | defect_center_rel |
| ---: | ---: | ---: | ---: |
| 0 | 4 | 7 | 2.750 |
| 10 | 6 | 12 | 1.333 |
| 20 | 6 | 11 | 2.333 |
| 30 | 8 | 12 | 2.750 |
| 40 | 6 | 12 | 2.333 |
| 50 | 6 | 12 | 1.333 |
| 60 | 6 | 11 | 2.333 |
| 70 | 8 | 12 | 2.750 |
| 80 | 6 | 12 | 2.333 |
| 90 | 6 | 12 | 1.333 |
| 100 | 6 | 11 | 2.333 |
| 110 | 8 | 12 | 2.750 |
| 120 | 6 | 12 | 2.333 |
| 130 | 6 | 12 | 1.333 |
| 140 | 6 | 11 | 2.333 |
| 150 | 8 | 12 | 2.750 |
| 160 | 6 | 12 | 2.333 |
| 170 | 6 | 12 | 1.333 |
| 180 | 6 | 11 | 2.333 |
| 190 | 8 | 12 | 2.750 |
| 200 | 6 | 12 | 2.333 |
| 210 | 6 | 12 | 1.333 |
| 220 | 6 | 11 | 2.333 |
| 230 | 8 | 12 | 2.750 |
| 240 | 6 | 12 | 2.333 |
| 250 | 6 | 12 | 1.333 |
| 260 | 6 | 11 | 2.333 |
| 270 | 8 | 12 | 2.750 |
| 280 | 6 | 12 | 2.333 |
| 290 | 6 | 12 | 1.333 |
| 300 | 6 | 11 | 2.333 |
| 310 | 8 | 12 | 2.750 |
| 320 | 6 | 12 | 2.333 |
| 330 | 6 | 12 | 1.333 |
| 340 | 6 | 11 | 2.333 |
| 350 | 8 | 12 | 2.750 |
| 360 | 6 | 12 | 2.333 |
| 370 | 6 | 12 | 1.333 |
| 380 | 6 | 11 | 2.333 |
| 390 | 8 | 12 | 2.750 |
| 400 | 6 | 12 | 2.333 |
| 410 | 6 | 12 | 1.333 |
| 420 | 6 | 11 | 2.333 |
| 430 | 8 | 12 | 2.750 |
| 440 | 6 | 12 | 2.333 |
| 450 | 6 | 12 | 1.333 |
| 460 | 6 | 11 | 2.333 |
| 470 | 8 | 12 | 2.750 |
| 480 | 6 | 12 | 2.333 |
| 490 | 6 | 12 | 1.333 |
| 500 | 6 | 11 | 2.333 |

## Classification

- Classification: `PERSISTENT_OSCILLATOR`
- Verdict: `RESIDUAL_CONFIRMED_PERSISTENT`
- Collapse step: `None`
- Observed exact period in last 100 steps: `8`
- Center slope in last 100 steps: `5.591147350029335e-05`
- Final defect size: `6`
- Tail size range: `5..8`

The defect persists through t=500 and repeats exactly with period 8 over the last 100 steps.

## Methodological Limit

- This phase tests persistence of one residual case only.
- Exact recurrence is measured on the background-subtracted defect frame, not on a canonicalized translated pattern.
- The classification is a preflight for causal interpretation; it does not measure a new ANF gradient.
