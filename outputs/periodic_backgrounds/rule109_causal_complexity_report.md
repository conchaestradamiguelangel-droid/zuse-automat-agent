# Fase 68: rule_109 Causal-Complexity Proxy Audit

## Question

Do temporal transition-complexity descriptors of the defect separate the
five positive `rule_109` ANF-gradient witnesses from the twelve
non-positive `rule_109` cases?

This phase is a small, executable proxy for causal-state/CSSR analysis. It
does not reconstruct full causal states. Instead, it converts each time
step into a phase symbol and measures the complexity of the resulting
symbol-transition sequence.

## Method

- Rule: `109`
- Width: `256`
- Horizon: `t=0..100`
- Defect: `state_with_IC(t) XOR background_only(t)`.
- Step symbol: `(dominant_context(t), defect_size_bucket(t))`.
- Size buckets: `0`, `1-3`, `4-6`, `7-9`, `10+`.
- Metrics: `bigram_entropy`, `unique_transitions`, `lz_complexity`, `period_detected`, `unique_symbols`.

## Case Metrics

| case | positive | bigram entropy | unique transitions | LZ | symbolic period | unique symbols |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `bg=0011/T=3/word=0001100/NEGATIVE` | `False` | 1.352 | 7 | 23 | 2 | 6 |
| `bg=0011/T=6/word=1100100/NEGATIVE` | `False` | 0.081 | 2 | 15 | 1 | 2 |
| `bg=0011/T=8/word=1000010/NEGATIVE` | `False` | 2.858 | 11 | 33 | 6 | 8 |
| `bg=0011/T=10/word=10000010/NEGATIVE` | `False` | 3.510 | 14 | 39 | 10 | 10 |
| `bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG` | `True` | 3.673 | 14 | 42 | 12 | 11 |
| `bg=0110/T=3/word=001100/NEGATIVE` | `False` | 1.352 | 7 | 23 | 2 | 6 |
| `bg=0110/T=6/word=0010011/NEGATIVE` | `False` | 1.779 | 6 | 25 | 3 | 5 |
| `bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `True` | 0.322 | 5 | 18 | 1 | 5 |
| `bg=1011/T=6/word=00001001/HORIZON_ARTIFACT` | `False` | 2.749 | 9 | 33 | 6 | 7 |
| `bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE` | `True` | 3.416 | 12 | 39 | 10 | 8 |
| `bg=1100/T=3/word=00001110/NEGATIVE` | `False` | 1.844 | 7 | 26 | 3 | 5 |
| `bg=1100/T=6/word=00100110/NEGATIVE` | `False` | 2.858 | 11 | 33 | 6 | 7 |
| `bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE` | `True` | 3.202 | 12 | 36 | 8 | 8 |
| `bg=1100/T=10/word=00111001/NEGATIVE` | `False` | 3.416 | 12 | 39 | 10 | 9 |
| `bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG` | `True` | 3.673 | 14 | 42 | 12 | 10 |
| `bg=1101/T=6/word=0000100/HORIZON_ARTIFACT` | `False` | 4.040 | 28 | 44 | None | 12 |
| `bg=1101/T=10/word=0001000/NEGATIVE` | `False` | 3.448 | 23 | 40 | None | 13 |

## Threshold Scan

- Majority baseline accuracy: 0.706
- Perfect complexity rules: 0
- Perfect non-period complexity rules: 0

Best no-false-positive rule:

- `period_detected >= 12`: TP=2, FP=0, TN=12, FN=3, accuracy=0.824, precision=1.000, recall=0.400

Best accuracy rule:

- `period_detected >= 12`: TP=2, FP=0, TN=12, FN=3, accuracy=0.824, precision=1.000, recall=0.400

Best non-period complexity rule:

- `bigram_entropy >= 3.673269689515108`: TP=2, FP=1, TN=11, FN=3, accuracy=0.765, precision=0.667, recall=0.400

Top scanned rules:

- `period_detected >= 12`: TP=2, FP=0, TN=12, FN=3, acc=0.824, precision=1.000, recall=0.400
- `bigram_entropy >= 3.673269689515108`: TP=2, FP=1, TN=11, FN=3, acc=0.765, precision=0.667, recall=0.400
- `lz_complexity >= 42`: TP=2, FP=1, TN=11, FN=3, acc=0.765, precision=0.667, recall=0.400
- `bigram_entropy <= 0.3222921890824148`: TP=1, FP=1, TN=11, FN=4, acc=0.706, precision=0.500, recall=0.200
- `lz_complexity <= 18`: TP=1, FP=1, TN=11, FN=4, acc=0.706, precision=0.500, recall=0.200
- `period_detected <= 1`: TP=1, FP=1, TN=11, FN=4, acc=0.706, precision=0.500, recall=0.200
- `unique_transitions <= 5`: TP=1, FP=1, TN=11, FN=4, acc=0.706, precision=0.500, recall=0.200
- `bigram_entropy <= 0.08079313589591118`: TP=0, FP=1, TN=11, FN=5, acc=0.647, precision=0.000, recall=0.000
- `bigram_entropy >= 4.039611868972394`: TP=0, FP=1, TN=11, FN=5, acc=0.647, precision=0.000, recall=0.000
- `lz_complexity <= 15`: TP=0, FP=1, TN=11, FN=5, acc=0.647, precision=0.000, recall=0.000

## Metric Ranges

| metric | positive range | negative range |
| --- | --- | --- |
| `bigram_entropy` | 0.322..3.673 | 0.081..4.040 |
| `unique_transitions` | 5..14 | 2..28 |
| `lz_complexity` | 18..42 | 15..44 |
| `period_detected` | 1..12 | 1..10 |
| `unique_symbols` | 5..11 | 2..13 |

## Verdict

`COMPLEXITY_NEGATIVE`.

The selected transition-complexity metrics do not provide a new discriminator. The best no-false-positive rule is symbolic period >= 12, which recapitulates the earlier period/horizon result rather than adding a new causal-state signal.

## Methodological Limit

- This is a causal-state proxy, not a full CSSR reconstruction.
- The symbolization intentionally compresses each frame to dominant context plus size bucket.
- A positive separator here would be a guide for CSSR, not a universal proof.
- A negative or partial result means the discriminant may live in richer spatial patterns or longer histories than these symbols encode.
