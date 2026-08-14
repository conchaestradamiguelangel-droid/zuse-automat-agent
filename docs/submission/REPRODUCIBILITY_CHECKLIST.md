# ZUSE v1.36 Reproducibility Checklist

Audience: reviewers and editors. This is a claim-to-artifact map, not a developer manual.

All claims below are reproducible from deterministic scripts in the repository. Some full sweeps are computationally expensive; tracked reports and summary files are included so reviewers can verify the numerical signatures without rerunning every raw search.

## Quick Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m unittest discover -s tests
```

## R1 - 20-World Atlas and Seven-Law Coverage

Paper claim: ZUSE builds a 20-world atlas and reports seven operational cycle-law categories.

Regeneration script:

```powershell
python outputs\world_taxonomy\generate_law_map.py
```

Primary output:

- `outputs/world_taxonomy/law_map.md`

Expected signature:

- Main taxonomy table begins at `| world | eca_class | category | ... |`.
- It lists 20 worlds, including ECA rules, synthetic controls, and Life fixtures.
- The law coverage table has seven columns: `vel`, `per`, `den`, `tipo`, `compl`, `front`, `tss`.

Reviewer shortcut:

```powershell
Select-String outputs\world_taxonomy\law_map.md -Pattern "^\\| .* \\|"
```

## R2 - rule_108 Stationary Local Oscillator on Quiescent Background

Paper claim: the quiescent-background local oscillator search isolates `rule_108` as the rule with production periodicity hits in the phase-16 sweep.

Regeneration script:

```powershell
python outputs\local_oscillators_fase16\run_local_oscillator_search.py
```

Primary output:

- `outputs/local_oscillators_fase16/local_oscillator_report.md`

Expected signature:

- Width: `128`.
- Raw periodic hits: `2`.
- Production periodic hits: `2`.
- The "Rules With Periodicity Hits" table contains `rule_108`.
- The two production hits are `pair_gap1` and `triple`, both converging to a stationary period-2 motif of span 3.

Reviewer shortcut:

```powershell
Select-String outputs\local_oscillators_fase16\local_oscillator_report.md -Pattern "rule_108|Production periodic hits|stationary period-2"
```

## R3 - Fragility Spectrum

Paper claim: ZUSE separates fragility regimes, including high total fragility with different core/noise decompositions.

Regeneration scripts:

```powershell
python outputs\fragility_fase10\run_fragility.py
python outputs\fragility_fase10\compute_core_fragility.py
python outputs\fragility_fase10\complete_physical_fragility_fase22.py
```

Primary outputs:

- `outputs/fragility_fase10/fragility_report.md`
- `outputs/fragility_fase10/core_fragility_report.md`
- `outputs/fragility_fase10/fragility_position_map.md`
- `outputs/world_taxonomy/law_map.md`

Expected signatures:

- `outputs/world_taxonomy/law_map.md` reports `rule_108` with `fragility_total = 0.992` and `core_fragility = 0.047`.
- `outputs/fragility_fase10/core_fragility_report.md` reports `rule_54` with `f_total = 0.714` and `f_core = 0.677`.
- `outputs/fragility_fase10/fragility_report.md` identifies `rule_54` as a noise-boundary fragility exception with `f_noise = 0.375`.

Reviewer shortcut:

```powershell
Select-String outputs\world_taxonomy\law_map.md,outputs\fragility_fase10\core_fragility_report.md,outputs\fragility_fase10\fragility_report.md -Pattern "rule_108|rule_54|0.992|0.047|0.714|0.677|0.375"
```

## R4 - Periodic-Background Oscillator Sweep and T=15 Mechanism

Paper claim: periodic-background sweeps expose oscillator families invisible in the quiescent regime, including the `rule_73/rule_109` mechanism that later drives the T=15 and ANF-gradient audits.

Regeneration script:

```powershell
python outputs\periodic_backgrounds\sweep_periodic_background_oscillators.py
```

Primary outputs:

- `outputs/periodic_backgrounds/periodic_background_oscillator_results.jsonl`
- `outputs/periodic_backgrounds/periodic_background_oscillator_report.md`

Expected signatures:

- The report includes stationary cases for `rule_73` and `rule_109`.
- The tracked JSONL contains the periodic-background oscillator catalogue used by the T=15 and later ANF audits.
- Long replay and anatomy checks are reported in the paper and companion periodic-background outputs; reviewers can inspect the committed reports without regenerating every raw sweep.

Reviewer shortcut:

```powershell
Select-String outputs\periodic_backgrounds\periodic_background_oscillator_report.md -Pattern "rule_73|rule_109|stationary|T=15"
```

## R5 - ANF Gradient Law in the T=15 Causal Cone

Paper claim: a 25-cell, 12-step causal cone reveals an ANF gradient in which active-output monomial counts decay with distance from the defect center.

Regeneration script:

```powershell
python outputs\periodic_backgrounds\analyze_periodic_bg_anf_baseline.py
```

Primary output:

- `outputs/periodic_backgrounds/periodic_bg_anf_baseline_report.md`

Expected signature:

- Reference gradient appears in the periodic-background ANF reports and downstream census reports as:
  - slope `-0.307283`;
  - `R^2 = 0.998197`.
- The paper reports the degree-band law and the `R^2 = 0.998197` monomial gradient in Section 7.25 and summary Section 10.2.

Reviewer shortcut:

```powershell
Select-String paper\draft.md,outputs\periodic_backgrounds\*.md -Pattern "-0.307283|0.998197|degree"
```

## R6 - Global Audit of the Historical Period Cap

Paper claim: replaying both historical periodic-background populations recovers
and independently confirms 3,296 stationary oscillators omitted by the source
detector's `T<=16` limit.

Primary scripts:

```powershell
python outputs\periodic_backgrounds\audit_period_detector_limit.py
python outputs\periodic_backgrounds\run_phase90_global_period_resweep.py preflight
```

Primary outputs:

- `outputs/periodic_backgrounds/phase90_global_period_cap_resweep_results.json`
- `outputs/periodic_backgrounds/phase90_global_period_cap_resweep_report.md`
- `outputs/periodic_backgrounds/phase90_execution_audit.md`

Expected signature:

- Processed configurations: `5,783,040`.
- Historical unique positives replayed: `445,897`.
- Stage-A candidates and Stage-B confirmations: `3,296 / 3,296`.
- Missing, extra, duplicate, kind, period, and drift mismatches: all zero.
- Confirmed rules: `rule_73 = 1,623`, `rule_109 = 1,673`.
- Status: `GLOBAL_PERIOD_CAP_FALSE_NEGATIVES_CONFIRMED`.

The full replay is authorization-gated and checkpointed. Reviewers can inspect
the committed result and execution audit without rerunning the 5.78 million
configurations.

## Runtime Notes

- Unit tests and report inspection are quick.
- Regenerating local summaries is usually minutes-scale.
- Full oscillator sweeps and ANF analyses can be hours-scale on a laptop, especially broad periodic-background and period-8 searches.
- The repository therefore commits deterministic scripts plus summary reports. Large raw JSONL files are omitted only when they exceed practical git size; companion reports and summaries remain tracked.

## Versioned Artifacts

- Zenodo v1.36 DOI: https://doi.org/10.5281/zenodo.21939732
- GitHub release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.36
- PDF: `paper/zuse_preprint.pdf`
- Source: `paper/draft.md`
