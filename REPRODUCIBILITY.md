# Reproducibility

This repository contains the deterministic code and summary artifacts used for
the ZUSE Automat Agent v1.0 preprint.

## Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The core runtime uses Python, NumPy, and Pillow. Some historical exploratory
scripts mention PySR or scikit-learn; those are not required to run the core
agent, regenerate the atlas tables, or run the main diagnostics documented here.

## Smoke Tests

```powershell
python -m unittest discover -s tests
```

If `pytest` is installed locally, the historical verification command was:

```powershell
python -X utf8 -m pytest --tb=short -q
```

## Core Agent

Run one ECA simulation:

```powershell
python -m zaa simulate --rule 110 --steps 200 --width 256 --out outputs\rule110
```

Run a short discovery loop:

```powershell
python -m zaa discover --world rule_110 --cycles 5 --journal journal.jsonl
```

## Regenerate Main Artifacts

World taxonomy and law map:

```powershell
python outputs\world_taxonomy\generate_law_map.py
```

Frontera-temporal sweep:

```powershell
python outputs\frontera_sweep\run_frontera_sweep.py
python outputs\frontera_sweep\profile_top_rules.py
python outputs\frontera_sweep\profile_remaining_candidates.py
```

Fragility diagnostics:

```powershell
python outputs\fragility_fase10\run_fragility.py
python outputs\fragility_fase10\compute_core_fragility.py
python outputs\fragility_fase10\complete_physical_fragility_fase22.py
```

Rule 54 gate and controlled-IC diagnostics:

```powershell
python outputs\rule54_gate_fase13\analyze_rule54_gate.py
python outputs\rule54_controlled_ic_fase19\analyze_rule54_single_bit.py
```

Local oscillator search:

```powershell
python outputs\local_oscillators_fase16\run_local_oscillator_search.py
python outputs\local_oscillator_family_fase18\sweep_local_oscillator_family.py
```

Periodicity sweeps:

```powershell
python outputs\periodicity_fase14\run_periodicity_sweep.py
python outputs\periodicity_fase21\run_periodic_ic_sweep.py
```

## Large Raw JSONL Files

The repository tracks scripts and summary reports, but raw JSONL outputs larger
than 1 MB are omitted from git to keep the public release compact. Regenerate
them with the scripts above when exact raw rows are needed.

Omitted raw files in v1.0:

- `outputs/periodicity_fase21/periodic_ic_sweep_results.jsonl`
- `outputs/fragility_fase10/fragility_completion_fase22_results.jsonl`

Tracked companion summaries:

- `outputs/periodicity_fase21/periodic_ic_sweep_report.md`
- `outputs/periodicity_fase21/periodic_ic_sweep_summary.json`
- `outputs/fragility_fase10/fragility_completion_fase22_report.md`
- `outputs/fragility_fase10/fragility_completion_fase22_summary.json`

## Preprint

The paper source is [paper/draft.md](paper/draft.md). The v1.0 PDF is committed
as [paper/zuse_preprint.pdf](paper/zuse_preprint.pdf) and archived on Zenodo:

```text
https://doi.org/10.5281/zenodo.20516375
```
