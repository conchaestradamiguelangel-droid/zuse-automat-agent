# Fase 90 Execution Audit

## Authorization Boundary

Miguel Angel Concha Estrada explicitly authorized Stage B with five workers for
exactly the 3,296 Stage-A candidates. The authorization was protocol-bound,
candidate-count-bound, expiring, external to the repository, and removed after
Stage B completed. No Stage-B authorization remains active.

## Interrupted First Attempt

The first Stage-B invocation was terminated by the command wrapper after its
five-second timeout. The checkpoint then contained 22 COMPLETE units, one
FAILED unit, and 489 orphaned RUNNING units. The failed empty unit was
`baseline_period_1_2_4/rule_22` with `OSError(22, 'Invalid argument')` during
the interrupted publication sequence.

No second instance was started while the original process tree was alive. Once
termination was confirmed, the 489 stale RUNNING units were explicitly
requeued through `recover-stale`. The FAILED unit was eligible for retry under
the existing state machine. Stage B was relaunched with the same authorization
and five workers using external stdout/stderr logs.

Final attempt distribution: 22 units completed in one attempt and 490 units in
two attempts. All 512 units ended COMPLETE with no verification errors.

## Candidate Reconciliation

The Stage-A and Stage-B physical keys were compared independently using
`(cohort, rule, background_index, ic_index, word_len, word)`:

- Stage-A rows and unique keys: `3,296` / `3,296`.
- Stage-B rows and unique keys: `3,296` / `3,296`.
- Missing from Stage B: `0`.
- Extra in Stage B: `0`.
- Duplicate excess in either stage: `0`.
- Kind mismatches: `0`.
- Period mismatches: `0`.
- Drift mismatches: `0`.

All 3,296 rows have status `CONFIRMED_PERIOD_CAP_FALSE_NEGATIVE`.

## Cleanup And Integrity

The interrupted attempt left 978 PID-scoped temporary files totaling 1,324,643
bytes. They were removed only after final artifact verification, using resolved
paths restricted to the Stage-B runtime directory. Zero temporary files remain.
The external stdout log was retained and stderr was empty.

- Final results SHA-256: `cc850203d9d62234f551e8b4318c76fe1af45de3392d537dec3912151377d64a`.
- Final report SHA-256: `bf3e1469ceb150ed8b0f6c9c71101477777821fbff861dcec822fc648f4167dc`.
- Historical replay gate SHA-256: `36c5a17be9243c4c55b62e59478d85130970e03f82f4e6abede3ce875a8bbc5a`.

The paper, DOI, tags, releases, and v1.33 were not modified.
