# Fase 7 - Journal Symbolic Analysis

Date: 2026-05-28

Dataset: `outputs/experiments_2026-05-27/journal_5b.jsonl`

Rows: 200 discovery cycles from the Fase 5b run.

## Questions

1. Is the journal internally consistent enough to recover `score`?
2. Can world-history features predict `is_new_law_signature`?
3. Can physical features alone predict `n_laws_accepted`?

## Result 1 - Score Is Exactly Recoverable

Using the minimal features:

- `n_laws_accepted`
- `analysis_noise`
- `dominant_changed`

Linear regression recovers:

```text
score = n_laws_accepted - analysis_noise + 0.5 * dominant_changed
R2 = 1.0
```

This validates that the journal records all inputs needed by `compute_score`.

## Result 2 - New Signatures Are Mostly History-Driven

Target: `is_new_law_signature` predicted from lag-1 features.

Balanced decision tree:

```text
positives: 20/199 = 10.0%
accuracy: 0.9045
balanced_accuracy: 0.9247
precision: 0.5135
recall: 0.95
confusion [[TN, FP], [FN, TP]]:
[[161, 18],
 [  1, 19]]
```

Dominant features are world-history fields:

- `world_visit_count`
- `world_score_variance_prev`
- `world_unique_signatures_prev`
- `world_signature_diversity_prev`

Interpretation: the model rediscovers policy/history structure more than new physics.

## Result 3 - Physical Features Predict Law Richness

Target: `n_laws_accepted`.

Features used:

- `dedup_structure_count`
- `inflation_ratio`
- `entropy_mean`
- `entropy_var`
- `gzip_ratio`
- `mutual_info_mean`
- `density_mean`
- `transition_rate`
- `analysis_ok`
- `steps`

Results:

```text
Linear regression:
R2 = 0.828
RMSE = 0.554

Decision tree max_depth=4:
R2 = 0.929
RMSE = 0.356
```

The strongest physical regime found by the tree is:

```text
analysis_ok = 1
entropy_mean > 0.97
gzip_ratio > 0.17
mutual_info_mean > 0.02
=> high law richness (~4.5 accepted laws)
```

Interpretation: law-rich worlds sit near the organized-chaos/class-4 region:
high entropy, nontrivial compressibility, and nonzero mutual information.

This is a meta-observation over worlds, not an 8th cycle law.

## PySR Status

PySR was not completed. Importing `pysr` repeatedly blocked inside `juliapkg`:

```text
[juliapkg] Waiting for lock on C:\Users\PC\.julia\environments\pyjuliapkg\lock.pid
```

No persistent lock file or live Julia/Python process remained after interruption.
Likely cause: first-run Julia package initialization on Windows. PySR can be retried
later by letting `import pysr` run uninterrupted for 20+ minutes, or by repairing the
Julia/PySR environment.

## Conclusion

Fase 7 is scientifically closed without PySR:

- The journal is internally consistent.
- The policy score is exactly recoverable.
- New-signature prediction is mostly historical.
- Law richness is strongly predicted by physical metrics alone.

Open validation step for the future: test whether the physical tree generalizes to
new ECA worlds not present in the 200-cycle journal.
