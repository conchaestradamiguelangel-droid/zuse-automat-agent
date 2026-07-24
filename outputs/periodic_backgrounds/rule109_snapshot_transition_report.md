# Fase 69: rule_109 Aligned Snapshot-Transition Audit

## Question

Do richer spatial or spatiotemporal representations of the defect separate
the five positive `rule_109` ANF-gradient witnesses from the twelve
non-positive `rule_109` cases, especially the residual
`bg=1100/T=8/word=00000110`?

This phase does not touch the paper. It tests the next research direction
after v1.32: keeping the spatial defect shape instead of compressing each
frame to scalar temporal summaries.

## Alignment Protocol

Distances between snapshots are only meaningful after alignment. This
report therefore uses two explicit shape representations:

- `center_aligned`: doubled coordinates relative to the defect bounding-box
  center, `rel2 = 2*x - (left + right)`.
- `left_aligned`: coordinates relative to the leftmost active defect cell.

The center alignment is the primary shape comparison. The left alignment is
a control to catch cases where edge anchoring matters.

## Method

- Rule: `109`
- Width: `256`
- Horizon: `t=0..100`
- Burn-in for transition sets: `t >= 20`
- Defect: `state_with_IC(t) XOR background_only(t)`.
- Transition token: `(aligned_shape(t), aligned_shape(t+1))`.

## Case Metrics

| case | positive | period abs | period center | center shapes | center trans | pos-only center trans | mean center diff |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `bg=0011/T=3/word=0001100/NEGATIVE` | `False` | 2 | 2 | 2 | 2 | 0 | 9.000 |
| `bg=0011/T=6/word=1100100/NEGATIVE` | `False` | 1 | 1 | 1 | 1 | 0 | 0.000 |
| `bg=0011/T=8/word=1000010/NEGATIVE` | `False` | 6 | 6 | 6 | 6 | 0 | 5.025 |
| `bg=0011/T=10/word=10000010/NEGATIVE` | `False` | 10 | 10 | 10 | 10 | 0 | 6.800 |
| `bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG` | `True` | 12 | 12 | 12 | 12 | 12 | 7.550 |
| `bg=0110/T=3/word=001100/NEGATIVE` | `False` | 2 | 2 | 2 | 2 | 0 | 9.000 |
| `bg=0110/T=6/word=0010011/NEGATIVE` | `False` | 3 | 3 | 3 | 3 | 0 | 2.675 |
| `bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `True` | 1 | 1 | 1 | 1 | 0 | 0.000 |
| `bg=1011/T=6/word=00001001/HORIZON_ARTIFACT` | `False` | 6 | 6 | 6 | 6 | 0 | 7.000 |
| `bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE` | `True` | 10 | 10 | 10 | 10 | 10 | 8.600 |
| `bg=1100/T=3/word=00001110/NEGATIVE` | `False` | 3 | 3 | 3 | 3 | 0 | 2.000 |
| `bg=1100/T=6/word=00100110/NEGATIVE` | `False` | 6 | 6 | 6 | 6 | 0 | 7.688 |
| `bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE` | `True` | 8 | 8 | 8 | 8 | 8 | 10.750 |
| `bg=1100/T=10/word=00111001/NEGATIVE` | `False` | 10 | 10 | 10 | 10 | 0 | 6.800 |
| `bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG` | `True` | 12 | 12 | 12 | 12 | 12 | 7.550 |
| `bg=1101/T=6/word=0000100/HORIZON_ARTIFACT` | `False` | None | None | 81 | 80 | 0 | 20.938 |
| `bg=1101/T=10/word=0001000/NEGATIVE` | `False` | None | None | 81 | 80 | 0 | 25.450 |

## Exact Transition Set Tests

- Center-aligned transitions shared by all positives: `0`.
- Center-aligned transitions shared by all positives and no negatives: `0`.
- Left-aligned transitions shared by all positives: `0`.
- Left-aligned transitions shared by all positives and no negatives: `0`.
- Residual center-aligned transitions absent from every other case: `8`.
- Residual left-aligned transitions absent from every other case: `8`.

First residual-unique center transitions:

- `-10,-6,0,2,4,8,10->-11,-7,-5,-3,1,11`
- `-10,-6,0,2,8,10->-11,-7,-5,-3,3,5,11`
- `-10,-6,4,6,10->-11,-7,-5,1,9,11`
- `-11,-7,-5,-1,1,7,9,11->-10,-6,4,6,10`
- `-11,-7,-5,-3,1,11->-11,-7,-5,1,3,9,11`

## Numeric Threshold Scan

- Perfect rules: `0`.
- Best no-false-positive rule: `positive_only_center_transition_count >= 8` (TP=4, FP=0, TN=12, FN=1, precision=1.000, recall=0.800).
- Best accuracy rule: `positive_only_center_transition_count >= 8` (TP=4, FP=0, TN=12, FN=1, accuracy=0.941).

Top scanned rules:

- `positive_only_center_transition_count >= 8`: TP=4, FP=0, TN=12, FN=1, acc=0.941, precision=1.000, recall=0.800
- `positive_only_left_transition_count >= 8`: TP=4, FP=0, TN=12, FN=1, acc=0.941, precision=1.000, recall=0.800
- `positive_only_center_transition_count >= 10`: TP=3, FP=0, TN=12, FN=2, acc=0.882, precision=1.000, recall=0.600
- `positive_only_left_transition_count >= 10`: TP=3, FP=0, TN=12, FN=2, acc=0.882, precision=1.000, recall=0.600
- `period_abs >= 12`: TP=2, FP=0, TN=12, FN=3, acc=0.824, precision=1.000, recall=0.400
- `period_center_shape >= 12`: TP=2, FP=0, TN=12, FN=3, acc=0.824, precision=1.000, recall=0.400
- `period_left_shape >= 12`: TP=2, FP=0, TN=12, FN=3, acc=0.824, precision=1.000, recall=0.400
- `positive_only_center_transition_count >= 12`: TP=2, FP=0, TN=12, FN=3, acc=0.824, precision=1.000, recall=0.400
- `positive_only_left_transition_count >= 12`: TP=2, FP=0, TN=12, FN=3, acc=0.824, precision=1.000, recall=0.400
- `max_center_step_diff <= 0`: TP=1, FP=1, TN=11, FN=4, acc=0.706, precision=0.500, recall=0.200

## Verdict

`SNAPSHOT_TRANSITION_RESIDUAL_SPECIFIC`.

No global separator was found, but the residual contains aligned transitions absent from all non-positive cases.

## Methodological Limit

- This phase compares aligned defect snapshots, not full causal cones.
- Exact transition equality is strict; near-matches may require edit-distance graph methods in a later phase.
- Center alignment removes translation but may also erase drift information; left alignment is included as a control.
- No paper or DOI metadata is changed by this phase.
