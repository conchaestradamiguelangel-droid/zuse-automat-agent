# ZUSE Automat Agent

Deterministic empirical law discovery for elementary cellular automata (ECA).

ZUSE Automat Agent runs cellular-automata worlds, applies a fixed observer stack,
evaluates seven binary cycle laws, and stores multi-seed evidence in reproducible
journals. The discovery loop is policy-driven and deterministic: no language
model participates in world selection, law evaluation, scoring, or acceptance.

## Preprint

- Version DOI: [10.5281/zenodo.20516375](https://doi.org/10.5281/zenodo.20516375)
- All-versions DOI: [10.5281/zenodo.20516374](https://doi.org/10.5281/zenodo.20516374)
- PDF: [paper/zuse_preprint.pdf](paper/zuse_preprint.pdf)

## Scientific Artifacts

- [World taxonomy and law coverage matrix](outputs/world_taxonomy/law_map.md):
  formal classification of 20 worlds, seven-law coverage, and measured
  fragility where available.
- [Scientific synthesis](outputs/scientific_synthesis/FINDINGS.md): consolidated
  findings across world families, law coverage, fragility mechanisms, and open
  questions.
- [Physical-tree findings](outputs/pysr_fase7/FINDINGS.md): meta-analysis of
  physical metrics that predict law richness.
- [Fragility report](outputs/fragility_fase10/fragility_report.md): basin
  fragility spectrum and observed mechanisms.
- [Rule 54 noise-gate anatomy](outputs/rule54_gate_fase13/rule54_gate_report.md):
  diagnosis of the dedup noise-boundary mechanism.
- [Local oscillator family sweep](outputs/local_oscillator_family_fase18/local_oscillator_family_report.md):
  exhaustive quiescent ECA sweep; `rule_108` is unique under the current local
  oscillator protocol.
- [Periodicity sweep](outputs/periodicity_fase21/periodic_ic_sweep_report.md):
  designed periodic ICs validate `periodicidad` across ECA.

## Install

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Quick Start

Run a simulation:

```powershell
python -m zaa simulate --rule 110 --steps 200 --width 256 --out outputs\rule110
```

Run a short deterministic discovery loop:

```powershell
python -m zaa discover --world rule_110 --cycles 5 --journal journal.jsonl
```

Run the test suite:

```powershell
python -m unittest discover -s tests
```

## Reproducibility

See [REPRODUCIBILITY.md](REPRODUCIBILITY.md) for the commands used to regenerate
the atlas, fragility reports, oscillator sweeps, and periodicity results.

Large raw JSONL outputs are not tracked in git when they exceed 1 MB. The
corresponding scripts and summary reports are tracked, and the raw files can be
regenerated from the commands in the reproducibility guide.

## Citation

```text
Concha Estrada, M. A. (2026). ZUSE Automat Agent: Empirical Law Discovery in
Elementary Cellular Automata (v1.0). Zenodo.
https://doi.org/10.5281/zenodo.20516375
```

## License

Code is released under the [MIT License](LICENSE). The preprint is distributed
under Creative Commons Attribution 4.0 International via Zenodo.
