# Fase 90 - Global period-cap resweep, Stage A

Status: `STAGE_A_COMPLETE_REPLAY_PASS_STAGE_B_NOT_AUTHORIZED`.

## Execution

- Protocol SHA-256: `344033959ec57a6614d78cac025185743bfbe552e354ee2239ed4fa237a4aea3`.
- Five-worker benchmark SHA-256: `9fbc905422bbe3fb16a4b86b9cb97febb53792270bf80e874107744916239c6d`.
- Work units completed: `512/512`.
- Runs processed: `5,783,040/5,783,040`.
- Wall span: `2,834.397 s` (approximately 47 min 14 s).
- Artifact verification errors: `0`.
- Scientific thresholds changed: `false`.

## Stage-A Candidates

The counterfactual T=1..120 detector selected `3,296` bounded cases that were
not classified by the historical T=2..16 detector. These are candidates for
long confirmation, not confirmed false negatives.

| Dimension | Count |
| --- | ---: |
| baseline_period_1_2_4 | 160 |
| primitive_len8 | 3,136 |
| rule_73 | 1,623 |
| rule_109 | 1,673 |
| stationary | 3,296 |
| moving | 0 |

Period distribution: T18=1703, T24=750, T26=5, T30=545, T40=53, T42=18,
T48=44, T60=105, T66=31, T90=15, and T120=27.

## Historical Replay Gate

The first raw-row gate failed with `445,897` replay rows versus `446,125`
historical rows. The failure had two independently inspectable causes:

1. The baseline source contains `228` exact duplicate rows for rule_131. Its
   `572` raw rows reduce to `344` unique physical identities, exactly the `344`
   reproduced by Stage A; neither side has a unique identity absent from the
   other.
2. Primitive-len8 counts match rule by rule, but the historical catalog adds
   `new_T`, `new_rule`, `new_speed`, and derived `speed` annotations that are
   not detector identity fields in the replay shards.

The gate implementation was corrected after observing this mismatch. It now
compares deduplicated physical detector identities while retaining raw counts
and duplicate counts in the report. Detector outputs and Stage-A shards were
not modified or recomputed. On that basis the gate passes with `445,897`
expected identities, `445,897` actual identities, and `0` mismatches across
all 512 `(cohort, rule)` comparisons.

The original mismatch report is preserved outside the repository with SHA-256
`ea70a59f6ea627a10ed6623114d6e0d21f1894361d57fbda1ded5549b2ea7349`.
The corrected replay report SHA-256 is
`36c5a17be9243c4c55b62e59478d85130970e03f82f4e6abede3ce875a8bbc5a`.

## Stage-B Gate

Stage B is not authorized and has not run. Its current plan contains `3,296`
candidates (`643,899` bytes), passes the 5-GiB disk floor, and gives a rough
non-benchmarked estimate of `9.659 s`. That estimate is planning information,
not a duration guarantee.

No candidate may be called a persistent period-cap false negative until Stage
B re-simulates it to t=1000 and reproduces kind, minimal period, and drift on
the independent t=500..1000 tail.
