# ZUSE v1.36 Reproducibility Addendum

This addendum maps the new candidate v1.36 claims to committed scripts and
result artifacts. It supplements the published v1.35 addendum and does not
rerun the 5,783,040-configuration cellular-automaton census.

## R11 - Triple minimum-cardinality audit

- **Claim:** among strata left unresolved by singleton and pair audits, the
  minimum rescue cardinality is exactly three in 41/57 vertex-connectivity
  strata and 40/71 edge-connectivity strata.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase103_triple_synergy.py`
- **Result:**
  `outputs/periodic_backgrounds/phase103_triple_synergy_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase103_triple_synergy_report.md`
- **Raw ledger:**
  `outputs/periodic_backgrounds/phase103_triple_synergy_ledger.bin`
- **Manifest:**
  `outputs/periodic_backgrounds/phase103_triple_synergy_manifest.json`
- **Expected signature:** 3,061,466 unordered triples; 2,745,416 vertex and
  3,031,106 edge trials; 41/57 and 40/71 `EXACTLY_3`; 16/57 and 31/71
  remaining `AT_LEAST_4`; 180/192 rescuing triples; 98/98 rescues requiring an
  internal Hamming-1 edge; zero Route-A/Route-B disagreements.
- **Ledger SHA-256:**
  `b342a58d20aa7ecdc2a2a5ea45037a64739134151db41b562464163b7e93578f`.

## R12 - Quadruple closure of the collective ladder

- **Claim:** every stratum left unresolved by triples has minimum rescue
  cardinality exactly four: 16/16 vertex-connectivity strata and 31/31
  edge-connectivity strata, with zero strata remaining `AT_LEAST_5`.
- **Script:**
  `outputs/periodic_backgrounds/analyze_phase104_quadruple_synergy.py`
- **Result:**
  `outputs/periodic_backgrounds/phase104_quadruple_synergy_results.json`
- **Report:**
  `outputs/periodic_backgrounds/phase104_quadruple_synergy_report.md`
- **Raw ledger:**
  `outputs/periodic_backgrounds/phase104_quadruple_synergy_ledger.bin`
- **Manifest:**
  `outputs/periodic_backgrounds/phase104_quadruple_synergy_manifest.json`
- **Pure-Python decoder:**
  `outputs/periodic_backgrounds/decode_phase104_quadruple_synergy_ledger.py`
- **Expected signature:** 24,362,850 unordered quadruples; 20,638,850 vertex
  and 19,941,575 edge trials; 77/103 rescuing quadruples; internal Hamming-1
  edge required in 77/77 and 103/103; zero route disagreements, reserved bits,
  or out-of-scope flags.
- **Ledger SHA-256:**
  `530d541e64d538c4e87dc416bda831e7caafa9b827b0068662b9117e8f70dc8a`.

## Combined cardinality signature

Across the collective-only strata frozen before pair enumeration, the exact
minimum partitions are:

| Metric | Exactly 2 | Exactly 3 | Exactly 4 | Unresolved >=5 |
| --- | ---: | ---: | ---: | ---: |
| Vertex connectivity | 69 | 41 | 16 | 0 |
| Edge connectivity | 68 | 40 | 31 | 0 |

These are exhaustive finite-protocol results, not universal bounds for other
rules, word lengths, target classes, or intervention families.

## Runtime and scope

- Fases 104--105 reuse the frozen Q8 graphs and do not run new CA simulations.
- The triple ledger contains 3,061,466 records and is 30,614,660 bytes.
- The quadruple ledger contains 24,362,850 two-byte records and is 48,725,700
  bytes.
- Independent verification decoded all quadruple records, checked all 32 word
  lists against Fase 95, and reproduced every aggregate without discrepancy.
- The repository suite for the candidate collects 318 tests: 312 pass and 6
  are skipped in the current Windows environment.
