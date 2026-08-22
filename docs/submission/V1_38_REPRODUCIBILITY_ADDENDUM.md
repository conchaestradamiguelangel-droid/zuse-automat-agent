# ZUSE v1.38 Reproducibility Addendum

This addendum maps the candidate v1.38 claims to committed scripts and result
artifacts. It supplements the published v1.37 addendum and does not rerun any
cellular-automaton simulation.

## R15 - Conditioned minimal-rescue mechanism atlas

- **Claim:** the 1,476 verified metric-specific minimal rescues are classified
  by frozen Hamming-1 motif and exact internal-edge dependence. Only `K2` and
  `K2+I` contain both mechanism labels in the frozen census.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase107_conditioned_rescue_mechanisms.py`
- **Result:**
  `outputs/periodic_backgrounds/phase107_conditioned_rescue_mechanism_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase107_conditioned_rescue_mechanism_report.md`
- **Manifest:**
  `outputs/periodic_backgrounds/phase107_conditioned_rescue_mechanism_manifest.json`
- **Expected signature:** 1,476 rescues in 265 instances; 931 external
  attachment and 545 internal-edge dependent; 12 motif rows; zero mechanism
  reconciliation failures.
- **Result raw/canonical SHA-256:**
  `cc7521f112a35c8cf2aa284c8fe700ef63dbbbd4699a6009b10b966f1eadfee4` /
  `288abe40606b2a5cff09e802eacf8eeea24d6ed0f3288d40681047e69b95ba09`.

## R16 - Ambient rescue geometry

- **Claim:** in 24 mixed `K2` instances, external-attachment rescues have lower
  mean connectivity toward the period-specific candidate universe than
  internal-edge-dependent rescues in 22/24 instances.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase108_ambient_rescue_geometry.py`
- **Result:**
  `outputs/periodic_backgrounds/phase108_ambient_rescue_geometry_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase108_ambient_rescue_geometry_report.md`
- **Manifest:**
  `outputs/periodic_backgrounds/phase108_ambient_rescue_geometry_manifest.json`
- **Expected signature:** 404,054 pair-ledger rows reconstruct 142 candidate
  universes; 319 `K2`/`K2+I` rescues; 24 mixed `K2` instances; mean
  `Delta_i(A_V)=-1.220833`; signs `2/0/22`; zero source or order failures.
- **Result raw/canonical SHA-256:**
  `02c858e4b8a801e39bec9512a54e317f0dfdd8c43cbe02ee5342c09442cfdae9` /
  `b479df629574d25d0655b3524962846de410b5382cb1b9c26b400117ac2ca1c0`.

## R17 - Fixed-budget Hamming partition

- **Claim:** for all 122 rescues in the 24 mixed `K2` instances,
  `A_V+A_G+A_R=14`. The bridge-graph difference has mean
  `Delta_i(A_G)=1.816667` and is positive in 24/24 instances.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase109_fixed_budget_hamming_partition.py`
- **Result:**
  `outputs/periodic_backgrounds/phase109_fixed_budget_hamming_partition_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase109_fixed_budget_hamming_partition_report.md`
- **Manifest:**
  `outputs/periodic_backgrounds/phase109_fixed_budget_hamming_partition_manifest.json`
- **Expected signature:** 223 `K2` rescues total; 122 in 24 mixed instances;
  zero containment, disjointness, partition, identity, or order failures;
  centered descriptive correlation `-0.824731`.
- **Result raw/canonical SHA-256:**
  `ba5cf94330ce5c27c6b7c4420f910c637debac1273b9b25d3ad4fd787c141d04` /
  `dcf3d5847af14b3128e88dac765e491900340ddf4587b50281f42ac8ade147b1`.

## R18 - Internal classification limitation

- **Claim:** `A_G` is not presented as an externally validated predictor. In
  the 24 mixed instances, its internal LOIO weighted balanced accuracy is
  `0.647500` and internal sensitivity is `0.295000`; the higher aggregate
  score is dominated by 77 monolabel instances.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase110_internal_loio_a_g.py`
- **Result:**
  `outputs/periodic_backgrounds/phase110_internal_loio_a_g_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase110_internal_loio_a_g_report.md`
- **Manifest:**
  `outputs/periodic_backgrounds/phase110_internal_loio_a_g_manifest.json`
- **Expected signature:** 223 rescues in 101 instances; composition `6/71/24`
  only-external/only-internal/mixed; 101 LOIO folds; threshold `t=4` in every
  fold; mixed-instance weighted balanced accuracy `259/400`.
- **Result raw/canonical SHA-256:**
  `c135f9d0c63b0baa5ffd0a8c9d4c16a9f258482fbe1ac560a3eff076feb76c0d` /
  `6a8223b20905eafb92cb6fa5727574587d4f4e2313a414e274500d789fd75d80`.

## R19 - Post-selection multiplicity calibration

- **Claim:** this artifact is exploratory and not a confirmatory paper result.
  It exactly calibrates the observed, outcome-selected multiplicity contrast
  under an exchangeable allocation with fixed instance sizes and class totals.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase111_exact_post_selection_combinatorial_stratification.py`
- **Result:**
  `outputs/periodic_backgrounds/phase111_exact_post_selection_combinatorial_stratification_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase111_exact_post_selection_combinatorial_stratification_report.md`
- **Manifest:**
  `outputs/periodic_backgrounds/phase111_exact_post_selection_combinatorial_stratification_manifest.json`
- **Expected signature:** 550 exact `(y,z)` cells; total DP mass
  `C(223,54)`; `D_obs=1`; one qualifying pair `(0,24)`; exact descriptive
  post-selection tail mass approximately `1.53624615881e-08`.
- **Result raw/canonical SHA-256:**
  `0a0024fa5ac2f3ef2c879ecd2e603b86a7a973a0fc0d2057264558415a196a6b` /
  `7513f3cb1b6ecd125c13ec61ab891059a8981547c65c119bb8cc522a4d8c56f5`.

## Interpretation boundary

- Fases 108--112 reuse the frozen population underlying Fases 106--107; they
  are not independent replications.
- The main candidate-v1.38 result is the conditioned geometry and exact
  fixed-budget partition in the 122 rescues from 24 mixed `K2` instances.
- No external or prospective validation, causal effect, population
  generalization, formal significance test, or statistical independence claim
  is made.
- Fases 111--112 are retained as internal limitation and post-selection audit,
  not promoted to independent headline discoveries.
