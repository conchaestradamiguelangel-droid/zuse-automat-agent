# ZUSE v1.37 Reproducibility Addendum

This addendum maps the published v1.37 claims to committed scripts and result
artifacts. It supplements the published v1.36 addendum and does not rerun any
cellular-automaton simulation.

## R13 - Exact minimal-rescue motif atlas

- **Claim:** all 27,828,370 pair, triple, and quadruple candidates are assigned
  to one of 12 exact unlabeled induced Hamming-1 motifs before outcomes are
  joined; 1,476 metric-specific minimal rescues are then audited for cut
  coverage and internal-edge dependence.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase105_minimal_rescue_motifs.py`
- **Result:**
  `outputs/periodic_backgrounds/phase105_minimal_rescue_motif_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase105_minimal_rescue_motif_report.md`
- **Raw ledger:**
  `outputs/periodic_backgrounds/phase105_minimal_rescue_motif_ledger.bin`
- **Manifest:**
  `outputs/periodic_backgrounds/phase105_minimal_rescue_motif_manifest.json`
- **Pure-Python decoder:**
  `outputs/periodic_backgrounds/decode_phase105_minimal_rescue_motif_ledger.py`
- **Expected signature:** 404,054 pairs, 3,061,466 triples, and 24,362,850
  quadruples; 2/3/7 motif classes by cardinality; 1,476 metric-specific
  minimal rescues; zero classifier or mechanism reconciliation failures.
- **Ledger SHA-256:**
  `987d8b54447bdd3919fdc5d41b7b36246bee534ed5c2a5462b6dbbfd61b16588`.
- **Result raw/canonical SHA-256:**
  `9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24` /
  `982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353`.

## R14 - Exact unit-cost QUBO compilation

- **Claim:** the 1,476 verified minimal rescues compile into 265 independent
  sparse unit-cost QUBOs with exactly 1,476 certified ground states and no
  missing or spurious solution.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase106_minimal_rescue_qubo.py`
- **Result:**
  `outputs/periodic_backgrounds/phase106_minimal_rescue_qubo_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase106_minimal_rescue_qubo_report.md`
- **Models:**
  `outputs/periodic_backgrounds/phase106_minimal_rescue_qubo_models.jsonl`
- **Manifest:**
  `outputs/periodic_backgrounds/phase106_minimal_rescue_qubo_manifest.json`
- **Pure-Python decoder:**
  `outputs/periodic_backgrounds/decode_phase106_minimal_rescue_qubo.py`
- **Expected signature:** 265 models; 17,624 accumulated `x` variables; 1,476
  accumulated `z` variables; 19,100 variables total; 9--172 variables per
  model; 32,861 nonzero sparse terms; 1,476 certified ground states; zero
  coefficient, energy, or reconciliation failures.
- **Models JSONL SHA-256:**
  `d6c813602e914b8863d248d47d7cecfcd498172ba2c3831441b750d5203c82ab`.
- **Manifest raw/canonical SHA-256:**
  `673a58bdd19efe946a52c748f398dc5e3168afcef38b2a0bf61dd2c369ca9063` /
  `c9f5e263c73ff73c6f6ce9ba49babecbd16f28c0c15840abcdca46f8399a5e74`.
- **Result raw/canonical SHA-256:**
  `64aac782da78ad9fdd17fe4f5db05bd86a81a871a0aa3b7436b2b0a145a0b95a` /
  `ed258326d547625e8263bb72f1fb3697e32574662dd4253d96414c536e741e17`.

## QUBO scope

- The QUBOs compile already verified rescues; they do not discover new ones.
- The objective uses unit node costs and exact integer coefficients.
- No quantum hardware, annealing device, heuristic solver, or new CA simulation
  is used.
- QUBO compatibility is a reusable representation, not evidence of quantum
  speedup or practical advantage.
