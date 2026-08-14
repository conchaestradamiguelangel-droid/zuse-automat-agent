# ZUSE v1.35 Reproducibility Addendum

This addendum maps the new claims in the v1.35 candidate to their committed
scripts and result artifacts. It supplements, rather than replaces,
`docs/submission/REPRODUCIBILITY_CHECKLIST.md`.

## R6 - Long-period attractor quotient

- **Claim:** 3,296 confirmed descriptors collapse into 192 strict physical
  attractor classes and 123 defect-morphology classes.
- **Script:** `outputs/periodic_backgrounds/analyze_phase90_long_period_attractors.py`
- **Result:** `outputs/periodic_backgrounds/phase90_long_period_attractor_results.json`
- **Report:** `outputs/periodic_backgrounds/phase90_long_period_attractor_report.md`
- **Expected signature:** 3,296 inputs; 192 strict classes; 123 morphology
  classes; 65 reflection classes; 3,104 strict-identity aliases.

## R7 - Conjugacy closure and physical-state deduplication

- **Claims:** all 3,296 conjugate trajectories match exactly; all 123 quotient
  classes close across the two rules; 1,829 strict physical initial states
  remain after removing 1,467 encoding aliases, with zero deterministic
  conflicts.
- **Scripts:**
  `analyze_phase91_conjugacy_closure.py` and
  `analyze_phase91_physical_initial_states.py` in
  `outputs/periodic_backgrounds/`.
- **Results:**
  `phase91_conjugacy_closure_results.json` and
  `phase91_physical_initial_state_results.json` in the same directory.
- **Expected signature:** 3,296/3,296 exact conjugacies; 123/123 closed
  quotient classes; 1,829 unique initial states; 1,467 aliases; 0 conflicts.

## R8 - Q8 intervention topology

- **Claim:** 1,829 observed states induce 14,632 Hamming-1 interventions; the
  complete 48-cube atlas partitions 192 classes into 51 connected-single-cube,
  21 cross-cube-only, 41 within-cube-fragmented, and 79 mixed classes.
- **Scripts:** `analyze_phase93_hamming_topology.py` and
  `analyze_phase94_hypercube_completion.py`.
- **Results:** `phase93_hamming_topology_results.json` and
  `phase94_hypercube_completion_results.json`.
- **Expected signature:** intervention outcomes 1,818 same class, 3,484 other
  long class, 9,249 represented outside the long set, 81 zero-word boundary;
  48 cubes and 192 classes with the 51/21/41/79 partition.

## R9 - Exact unit cut-coverage law

- **Claim:** on 43,425 unit interventions, complete coverage of all
  pair-specific critical cuts is equivalent to restored vertex/edge
  redundancy.
- **Script:** `outputs/periodic_backgrounds/analyze_phase101_cut_coverage_law.py`
- **Result:** `outputs/periodic_backgrounds/phase101_cut_coverage_law_results.json`
- **Report:** `outputs/periodic_backgrounds/phase101_cut_coverage_law_report.md`
- **Expected signature:** vertex `TP=1505, TN=41920, FP=0, FN=0`; edge
  `TP=1566, TN=41859, FP=0, FN=0`; 411 re-enumerated critical vertices, 394
  critical edges, and zero reconciliation failures.

## R10 - Pairwise minimum-cardinality atlas

- **Claim:** among collective-only strata, the minimum is exactly two in
  69/126 vertex and 68/139 edge strata; remaining minima are only bounded
  below by three.
- **Script:** `outputs/periodic_backgrounds/analyze_phase102_pairwise_synergy.py`
- **Result:** `outputs/periodic_backgrounds/phase102_pairwise_synergy_results.json`
- **Report:** `outputs/periodic_backgrounds/phase102_pairwise_synergy_report.md`
- **Raw ledger:** `outputs/periodic_backgrounds/phase102_pairwise_synergy_ledger.bin`
- **Manifest:** `outputs/periodic_backgrounds/phase102_pairwise_synergy_manifest.json`
- **Pure-Python decoder:**
  `outputs/periodic_backgrounds/decode_phase102_pairwise_synergy_ledger.py`
- **Expected signature:** 404,054 unordered pairs; 384,354 vertex and 372,299
  edge trials; 454/470 rescuing pairs; 83/86 rescues requiring the mutual
  Hamming-1 edge; zero Route-A/Route-B disagreements.
- **Ledger SHA-256:**
  `24de12594fe8b95f6e70be4278b2dfadb7f29f181aef3d7aeea41f9fbe58de52`.

## Runtime and scope

- Fases 91--103 reuse committed Fase-90 outputs and deterministic graph
  analyses; they do not rerun the 5,783,040-configuration CA census.
- The complete Fase-103 pair audit takes approximately five minutes on the
  reference Windows workstation and writes a 4,040,540-byte ledger.
- Fase 104 is predeclared but not executed and contributes no result to v1.35.
- The repository suite for the candidate is expected to collect 297 tests:
  291 pass and 6 are skipped in the current Windows environment.
