# Fase 90 Runner Guide

Status: `BUILT_NOT_AUTHORIZED_NOT_EXECUTED`.

The protocol remains `DESIGN_ONLY_NOT_EXECUTED`. This guide documents the
implementation added after independent review; it is not an execution record.

## Components

- `phase90_resweep_core.py`: fixed-width ledger, artifact hashing, dynamic disk
  gate, authorization validation, and SQLite checkpoint state machine.
- `run_phase90_global_period_resweep.py`: generator preflight, authorized
  benchmark, Stage A, historical replay gate, Stage-B plan, authorized Stage B,
  verification, recovery, and final aggregation.
- `decode_phase90_ledger.py`: read-only decoder for the 9-byte ledger records.
- `tests/test_phase90_resweep.py`: unit tests that use temporary directories and
  do not run the global simulator.

No authorization JSON is committed. No benchmark, Stage A, or Stage B command
can run without a separate expiring authorization bound to the protocol digest.

## Safe Commands

These commands do not simulate cellular automata:

```powershell
python outputs/periodic_backgrounds/run_phase90_global_period_resweep.py preflight
python outputs/periodic_backgrounds/run_phase90_global_period_resweep.py status
python outputs/periodic_backgrounds/run_phase90_global_period_resweep.py verify
```

`status` and `verify` fail if the checkpoint has never been initialized; they do
not create an empty database and report a false success.

The preflight prints the immutable `protocol_sha256`, generator counts, work-unit
count, and `simulation_executed=false`.

## Authorization Model

Authorization files are external runtime inputs, not repository artifacts.
Every file requires:

```json
{
  "phase": 90,
  "approved": true,
  "protocol_sha256": "<preflight digest>",
  "stage": "<INIT|BENCHMARK|STAGE_A|STAGE_B>",
  "authorized_by": "Miguel Angel Concha Estrada",
  "max_workers": 1,
  "expires_at_epoch": 0
}
```

An expired file, wrong stage, wrong protocol hash, missing author, or excess
worker count fails closed.

## Benchmark Gate

The benchmark itself is a simulation and requires `stage=BENCHMARK`. Its
authorization must also list exact units and a maximum count:

```json
{
  "allowed_units": ["baseline_period_1_2_4:73", "primitive_len8:73"],
  "max_units": 2
}
```

Example shape of the command, not an instruction to run it now:

```powershell
python outputs/periodic_backgrounds/run_phase90_global_period_resweep.py benchmark `
  --authorization-file <benchmark-auth.json> `
  --unit baseline_period_1_2_4:73 `
  --unit primitive_len8:73 `
  --workers 2 `
  --report <benchmark-report.json>
```

Temporary benchmark shards are removed after the report is written. The report
records measured throughput, candidate density/bytes, projected Stage-A time,
and a dynamic disk requirement.

## Stage-A Gate

Stage A requires a new `stage=STAGE_A` authorization. It must include
`benchmark_report_sha256`; the requested worker count must equal the worker
count actually benchmarked. The runner also checks free disk immediately before
execution.

```powershell
python outputs/periodic_backgrounds/run_phase90_global_period_resweep.py stage-a `
  --authorization-file <stage-a-auth.json> `
  --benchmark-report <benchmark-report.json> `
  --workers <benchmarked-workers>
```

Stage A writes one ledger, candidate shard, replay shard, and manifest per
`(cohort, rule)`. Workers only write temporary files. The coordinator validates
and publishes each artifact, publishes the manifest last, and only then marks
the unit `COMPLETE` in SQLite.

After all 512 units complete:

```powershell
python outputs/periodic_backgrounds/run_phase90_global_period_resweep.py replay-gate
python outputs/periodic_backgrounds/run_phase90_global_period_resweep.py stage-b-plan
```

The replay gate compares canonical row digests and counts for every rule against
the two historical catalogs. Stage-B planning uses measured candidate count and
bytes, not the 5-GiB floor alone.

## Stage-B Gate

Stage B requires another external authorization with `stage=STAGE_B` and an
`expected_candidate_count` exactly matching `stage-b-plan`. It cannot start
unless historical replay status is `PASS` and the dynamic disk gate passes.

After all Stage-B units complete, `finalize` verifies every registered artifact,
checks that Stage-B rows equal Stage-A candidate count, and writes the final JSON
and Markdown report. It does not change the paper or release.

## Windows Recovery Tests

The test suite verifies actual replacement of an existing file on Windows and
three fail-closed cases:

- a locked/denied `os.replace` preserves the previous final artifact and leaves
  the temporary file available for diagnosis;
- a wrong temporary digest never reaches `os.replace`;
- corruption after checkpoint completion is detected by `verify`.

SQLite connections are explicitly closed. Python's connection context manager
commits or rolls back but does not close the Windows file handle.

Stale `RUNNING` units are not requeued automatically while another process might
still be alive. Recovery is explicit through `recover-stale` with a caller-chosen
epoch, then the authorized stage command may retry the unit. Retries publish
deterministic per-unit files and cannot duplicate merged candidates.
