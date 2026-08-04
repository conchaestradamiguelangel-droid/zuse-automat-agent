# Fase 90 Protocol: Global Period-Cap Re-sweep

Status: `DESIGN_ONLY_NOT_EXECUTED`.

No simulation, benchmark, checkpoint database, or result shard has been
created by this design phase. Execution requires a separate explicit approval.

## Scientific Question

How many persistent periodic-background oscillators were omitted globally
because the historical detector searched only periods `T=2..16`?

Fase 89 proved the defect locally: 363 of 2,008 rule_73 runs were strict
period-cap false negatives. It did not estimate the global rate because the
historical JSONL catalogs store positive hits only.

## Frozen Population

The re-sweep must reproduce the exact generators and ordering of the two
historical cohorts.

| cohort | rules | backgrounds | ICs/background | runs | work units |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline periods 1/2/4 | 256 | 15 | 502 | 1,927,680 | 256 |
| primitive len8 necklaces | 256 | 30 | 502 | 3,855,360 | 256 |
| **total** | | | | **5,783,040** | **512** |

Each work unit is exactly one `(cohort, rule)` pair. IC ordering remains the
historical order: lengths 1..8, then integer value 1..`2^length-1`.

## Two-Stage Detector

### Stage A: exhaustive source-window replay

Every one of the 5,783,040 runs is simulated with the historical physical
protocol:

- width 256;
- burn-in 80;
- end time 300;
- maximum localized difference span 32;
- actual state measured as XOR defect against the independently evolved
  periodic background.

The same shape sequence is classified twice:

1. **Historical replay:** stationary/moving periods `2..16`, preserving the
   old constant-shape and period-1-alias semantics exactly.
2. **Counterfactual detector:** strict all-pairs recurrence over the same
   `t=80..300` frames, periods `1..120`.

A Stage-A period-cap candidate must be bounded and unclassified by the
historical replay, but stationary or moving at `T>16` under the counterfactual
detector. `T=1`, late stabilization, extinction, span escape, and moving aliases
are separate classes, never folded into the period-cap count.

### Stage B: long confirmation only for candidates

Only Stage-A period-cap candidates are re-simulated to `t=1000`.
The tail `t=500..1000` is tested for exact stationary or constant-drift moving
recurrence at periods `1..120`.

A **global confirmed false negative** requires the same kind, minimal period,
and drift in Stage A and Stage B. A candidate that is no longer bounded periodic
is labeled `CANDIDATE_NOT_PERSISTENT`; one that remains periodic but changes
kind, minimal period, or drift is `CANDIDATE_LONG_CLASS_MISMATCH`. Neither is
silently counted as a confirmed cap false negative.

Stage B is a gate, not an optional spot check.

Fase 90 does not test late stabilization among every Stage-A noncandidate and
does not long-replay every historical positive. Those are different questions
and would require separately predeclared cohorts.

## Historical Replay Gate

Before interpreting any new candidate, Stage A must reproduce both old
positive catalogs under their original detector:

- baseline archived positive rows: 122,253;
- primitive-len8 archived positive rows: 323,872.

The comparison is by deterministic physical key and classification, not only
by aggregate count. Any mismatch stops Fase 90 with
`HISTORICAL_REPLAY_MISMATCH`; no global correction is reported until resolved.

## Complete Classification Ledger

Fase 90 must not repeat the positive-only archive design. Every attempted run
gets one fixed-width record in deterministic implicit order:

`cohort, rule, background_index, ic_index`.

The record schema is `<BBBBhhB>` (9 bytes): source kind, counterfactual kind,
source period, counterfactual period, source drift, counterfactual drift, and
flags. At 5,783,040 runs the raw ledger is 52,047,360 bytes (49.64 MiB), before
small manifests and candidate files. A decoder and schema version are required.

Each per-rule shard has a manifest with record count, byte size, configuration
digest, and content digest. SHA-256 is named explicitly rather than treated as
an eternal default; manifests are algorithm-agile so a later SHA3 or other
post-quantum migration does not change the scientific record layout. No claim
of quantum security is made.

## Parallelization

Current machine observed during design:

- Intel i5-12400;
- 6 physical / 12 logical processors;
- 15.77 GiB RAM.

Recommended initial worker count: **5** using `ProcessPoolExecutor`. One physical
core remains for the coordinator, filesystem, and desktop. Workers receive one
rule unit at a time and never write the shared checkpoint database.

Workers produce temporary ledger and candidate shards. The coordinator checks
their size, record count, and digest, atomically renames them, then marks the
unit complete in SQLite. Final merges are ordered by cohort then rule, so worker
completion order cannot change the result.

Increasing beyond five workers requires a benchmark showing improved throughput
without memory pressure or disk contention. Logical processor count alone is
not sufficient justification.

## Checkpoints and Recovery

Checkpoint database:

`outputs/periodic_backgrounds/fase90/checkpoint.sqlite`

Required work-unit states: `PENDING`, `RUNNING`, `COMPLETE`, `FAILED`.
The database stores configuration digest, attempt count, timestamps, processed
count, aggregate counters, shard paths, and shard digests.

Commit sequence:

1. Worker writes `.tmp` ledger, candidate, and manifest files.
2. Coordinator validates schema, size, count, and hashes.
3. Coordinator uses `os.replace` to publish immutable final shard names.
4. One SQLite transaction records the artifacts and marks the unit `COMPLETE`.

On restart, a `COMPLETE` unit is skipped only if every artifact still validates.
A stale `RUNNING` unit is requeued. Temporary files never count as progress.
Candidate output is per-unit, so retry cannot duplicate global rows.

The old JSON checkpoint pattern is not sufficient here: it can record a rule as
complete without transactionally binding that state to exact result bytes.

## Cost Model

Historical measurements on this project:

| sweep | runs | historical wall time | observed wall rate |
| --- | ---: | ---: | ---: |
| baseline | 1,927,680 | 3,595 s | 536 runs/s |
| len8 (parallel) | 3,855,360 | 1,343.787 s | 2,869 runs/s |

These timings used different execution architectures and are not a benchmark
of the proposed detector. The period-120 comparison adds work, especially for
unclassified trajectories. The honest planning range for Stage A is **45-120
minutes** on the current machine. It must be replaced by a measured estimate
after a separately authorized pilot.

Stage B cost cannot be fixed before Stage A reveals the candidate count. Fase 89
observed roughly 91 long runs/s in one process. For planning only:

`wall_seconds ~= candidates / (91 * workers * efficiency)`

with five workers and conservative efficiency 0.75. Examples:

- 100,000 candidates: about 4.9 minutes;
- 500,000 candidates: about 24.4 minutes;
- 1.12 million candidates: about 54.6 minutes.

Those are extrapolations, not promises. Stage A must publish the actual candidate
count and a revised Stage-B estimate before long confirmation begins.

Reserve at least **5 GiB free disk** before execution. The compact ledger is only
about 50 MiB, but candidate JSONL, manifests, SQLite, temporary shards, logs,
and duplicate space during atomic replacement require headroom.

## Execution Gates

No sweep starts until all are true:

1. Protocol and machine-readable JSON are reviewed independently.
2. A runner and decoder exist with unit tests for detector equivalence, record
   encoding, atomic checkpoint recovery, deterministic merge, and corruption.
3. Generator-only preflight reproduces 15 baseline backgrounds, 30 primitive
   len8 necklaces, 502 ICs, 512 work units, and 5,783,040 total runs.
4. At least 5 GiB disk is free.
5. A small, separately approved benchmark determines worker count and updates
   the time estimate without changing scientific thresholds.
6. Miguel explicitly authorizes Stage A.

After Stage A, Stage B starts only after the replay gate passes and the actual
candidate count, projected runtime, and disk use are reported.

## Final Outputs When Executed

- immutable configuration and environment manifest;
- checkpoint SQLite database;
- 512 compact classification-ledger shards plus manifests;
- 512 deterministic candidate shards;
- historical replay comparison;
- Stage-B long-confirmation rows;
- summaries by cohort, rule, background, kind, period, drift, and normalized
  attractor hash;
- explicit counts for confirmed cap false negatives, nonpersistent candidates,
  long-class mismatches, aliases, extinction, and span escape;
- report with global verdict and methodological limits.

No paper, DOI, tag, release, or detector threshold changes merely because the
protocol exists or the sweep later completes.
