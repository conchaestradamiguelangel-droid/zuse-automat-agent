# Fase 71: rule_109 Static Positive ANF-Geometry Audit

## Question

Why is `bg=0110/T=8/word=0000011` a positive ANF-gradient witness
if its aligned snapshot transition is static and also appears in a negative case?

This phase reuses the Fase 55 ANF census and the Fase 70 subtype labels.
No paper, DOI metadata, tag, or release is modified.

## Method

- Rule: `109`
- Common horizon: `T_WINDOW=12`
- Inputs: `anf_gradient_census_results.json`,
  `rule109_period_horizon_results.json`, and
  `rule109_positive_subtype_results.json`.
- Geometry source: active output rows with `dist`, `monomial_count`,
  `log10_monomials`, plus `active_summary.log_monomial_fit`.

## Static Pair

| case | category | subtype | active | dist classes | slope | R2 | delta T15 % | max monomial dist | RMSE | central share | near-center share | mirror active mismatches |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `HORIZON_ACCEPTABLE` | `STATIC_POSITIVE` | 6 | 5 | -0.298928 | 0.998276 | 2.72 | 0.0 | 0.024 | 0.599 | 0.854 | 3 |
| `bg=0011/T=6/word=1100100/NEGATIVE` | `NEGATIVE` | `NON_POSITIVE` | 7 | 5 | -0.292946 | 0.930073 | 4.67 | 1.5 | 0.153 | 0.323 | 0.899 | 3 |

Active profiles for the static pair:

- Static positive distances: `[0.0, 1.0, 3.0, 4.0, 5.0, 5.0]`
- Static positive monomial counts: `[529108, 2222747, 17758051, 7563262, 1032721, 542069]`
- Static negative distances: `[0.5, 1.5, 1.5, 3.5, 4.5, 5.5, 5.5]`
- Static negative monomial counts: `[529108, 9332330, 7563262, 4165778, 1032721, 542069, 251774]`

## 17-Case Common-Horizon Table

| case | positive | subtype | slope | R2 | active | dist | max monomial dist | RMSE | central share | near-center share | mirror mismatches |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `bg=0011/T=3/word=0001100/NEGATIVE` | `False` | `NON_POSITIVE` | -0.302580 | 0.933294 | 6 | 3 | 0.5 | 0.175 | 0.639 | 0.980 | 3 |
| `bg=0011/T=6/word=1100100/NEGATIVE` | `False` | `NON_POSITIVE` | -0.292946 | 0.930073 | 7 | 5 | 1.5 | 0.153 | 0.323 | 0.899 | 3 |
| `bg=0011/T=8/word=1000010/NEGATIVE` | `False` | `NON_POSITIVE` | -0.310312 | 0.924473 | 8 | 5 | 0.5 | 0.164 | 0.742 | 0.742 | 5 |
| `bg=0011/T=10/word=10000010/NEGATIVE` | `False` | `NON_POSITIVE` | -0.276202 | 0.899808 | 7 | 5 | 0.5 | 0.154 | 0.497 | 0.497 | 3 |
| `bg=0011/T=12/word=10010100/NATURAL_PERIOD_STRONG` | `True` | `DYNAMIC_POSITIVE` | -0.298274 | 0.998341 | 7 | 5 | 0.0 | 0.022 | 0.558 | 0.795 | 2 |
| `bg=0110/T=3/word=001100/NEGATIVE` | `False` | `NON_POSITIVE` | -0.302580 | 0.933294 | 6 | 3 | 0.5 | 0.175 | 0.639 | 0.980 | 3 |
| `bg=0110/T=6/word=0010011/NEGATIVE` | `False` | `NON_POSITIVE` | -0.313891 | 0.941622 | 7 | 5 | 0.5 | 0.149 | 0.503 | 0.885 | 6 |
| `bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `True` | `STATIC_POSITIVE` | -0.298928 | 0.998276 | 6 | 5 | 0.0 | 0.024 | 0.599 | 0.854 | 3 |
| `bg=1011/T=6/word=00001001/HORIZON_ARTIFACT` | `False` | `NON_POSITIVE` | -0.303174 | 0.999487 | 4 | 3 | 2.0 | 0.009 | 0.000 | 0.000 | 2 |
| `bg=1011/T=10/word=00000001/HORIZON_ACCEPTABLE` | `True` | `DYNAMIC_POSITIVE` | -0.307674 | 0.999349 | 7 | 4 | 0.0 | 0.014 | 0.387 | 0.793 | 0 |
| `bg=1100/T=3/word=00001110/NEGATIVE` | `False` | `NON_POSITIVE` | -0.311934 | 0.924475 | 8 | 5 | 0.5 | 0.166 | 0.590 | 0.808 | 5 |
| `bg=1100/T=6/word=00100110/NEGATIVE` | `False` | `NON_POSITIVE` | -0.313891 | 0.941622 | 7 | 5 | 0.5 | 0.149 | 0.503 | 0.885 | 6 |
| `bg=1100/T=8/word=00000110/HORIZON_ACCEPTABLE` | `True` | `DYNAMIC_POSITIVE` | -0.298928 | 0.998276 | 6 | 5 | 0.0 | 0.024 | 0.599 | 0.854 | 3 |
| `bg=1100/T=10/word=00111001/NEGATIVE` | `False` | `NON_POSITIVE` | -0.285905 | 0.896516 | 6 | 4 | 0.5 | 0.163 | 0.809 | 0.809 | 3 |
| `bg=1100/T=12/word=00101001/NATURAL_PERIOD_STRONG` | `True` | `DYNAMIC_POSITIVE` | -0.298274 | 0.998341 | 7 | 5 | 0.0 | 0.022 | 0.558 | 0.795 | 2 |
| `bg=1101/T=6/word=0000100/HORIZON_ARTIFACT` | `False` | `NON_POSITIVE` | -0.303174 | 0.999487 | 4 | 3 | 2.0 | 0.009 | 0.000 | 0.000 | 2 |
| `bg=1101/T=10/word=0001000/NEGATIVE` | `False` | `NON_POSITIVE` | -0.300746 | 1.000000 | 4 | 2 | 2.0 | 0.000 | 0.000 | 0.000 | 0 |

## Static Signature Rows

The static dynamic signature remains non-specific. The ANF geometry is
therefore the relevant difference, not the static transition itself.

| case | positive | category | slope | R2 | delta T15 % |
| --- | --- | --- | ---: | ---: | ---: |
| `bg=0011/T=6/word=1100100/NEGATIVE` | `False` | `NEGATIVE` | -0.292946 | 0.930073 | 4.67 |
| `bg=0110/T=8/word=0000011/HORIZON_ACCEPTABLE` | `True` | `HORIZON_ACCEPTABLE` | -0.298928 | 0.998276 | 2.72 |

## Threshold Scan

- Perfect scalar rules: `1`.
- Best no-false-positive rule: `max_active_monomial_dist <= 0.0` (TP=5, FP=0, TN=12, FN=0, precision=1.000, recall=1.000).
- Best accuracy rule: `max_active_monomial_dist <= 0.0` (TP=5, FP=0, TN=12, FN=0, accuracy=1.000).

Top scanned rules:

- `max_active_monomial_dist <= 0.0`: TP=5, FP=0, TN=12, FN=0, acc=1.000, precision=1.000, recall=1.000
- `delta_vs_t15_percent <= 0.12735766901969464`: TP=1, FP=0, TN=12, FN=4, acc=0.765, precision=1.000, recall=0.200
- `max_active_monomial_count >= 17758052`: TP=1, FP=0, TN=12, FN=4, acc=0.765, precision=1.000, recall=0.200
- `monomial_sum_active >= 45930072`: TP=1, FP=0, TN=12, FN=4, acc=0.765, precision=1.000, recall=0.200
- `delta_vs_t15_percent <= 0.985836736600605`: TP=1, FP=1, TN=11, FN=4, acc=0.706, precision=0.500, recall=0.200
- `mirror_active_mismatches <= 0`: TP=1, FP=1, TN=11, FN=4, acc=0.706, precision=0.500, recall=0.200
- `monomial_sum_active >= 42914564`: TP=1, FP=1, TN=11, FN=4, acc=0.706, precision=0.500, recall=0.200
- `active_distance_gap_count <= 0`: TP=0, FP=1, TN=11, FN=5, acc=0.647, precision=0.000, recall=0.000
- `central_monomial_share >= 0.8089066417439225`: TP=0, FP=1, TN=11, FN=5, acc=0.647, precision=0.000, recall=0.000
- `delta_vs_t15_percent >= 10.114829151290106`: TP=0, FP=1, TN=11, FN=5, acc=0.647, precision=0.000, recall=0.000

## Verdict

`STATIC_ANF_GEOMETRY_DISCRIMINANT_FOUND`.

At least one ANF-geometry scalar separates all positive rule_109 cases from non-positives at T_WINDOW=12: the maximum active monomial count is located at the exact cone center for every positive and for no non-positive.

The static positive is not explained by its temporal transition, which is
shared with a negative. It is distinguished by common-horizon ANF
geometry: the strongest active monomial support is centered at
`dist=0`, matching all other positives and no non-positive case. The
static pair also differs in fit quality: the positive has a T15-like
slope with near-perfect log-linear fit, while the static negative has a
similar slope but much weaker fit quality.

## Methodological Limit

- This phase uses existing common-horizon ANF measurements at `T_WINDOW=12`.
- The static pair is still only one positive and one negative; the 17-case
  table and threshold scan are included to avoid overfitting the pair.
- Scalar ANF-geometry summaries do not replace full causal-cone comparison.
- No paper or DOI metadata is changed by this phase.
