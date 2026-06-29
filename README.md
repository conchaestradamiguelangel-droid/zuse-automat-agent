# ZUSE Automat Agent

Deterministic empirical law discovery for elementary cellular automata (ECA).

ZUSE Automat Agent runs cellular-automata worlds, applies a fixed observer stack,
evaluates seven binary cycle laws, and stores multi-seed evidence in reproducible
journals. The discovery loop is policy-driven and deterministic: no language
model participates in world selection, law evaluation, scoring, or acceptance.

## Preprint

**Latest: v1.12** - Minimal cone-table audit: the T=15 causal cone is dense, uses 25/25 inputs and all 8 ECA entries; only structural internal pruning remains.

- v1.12 DOI: [10.5281/zenodo.21044802](https://doi.org/10.5281/zenodo.21044802)
- v1.11 DOI: [10.5281/zenodo.21034813](https://doi.org/10.5281/zenodo.21034813)
- v1.10 DOI: [10.5281/zenodo.21009303](https://doi.org/10.5281/zenodo.21009303)
- v1.9 DOI: [10.5281/zenodo.21001633](https://doi.org/10.5281/zenodo.21001633)
- v1.8 DOI: [10.5281/zenodo.21000646](https://doi.org/10.5281/zenodo.21000646)
- v1.7 DOI: [10.5281/zenodo.20971738](https://doi.org/10.5281/zenodo.20971738)
- v1.6 DOI: [10.5281/zenodo.20792051](https://doi.org/10.5281/zenodo.20792051)
- v1.5 DOI: [10.5281/zenodo.20768585](https://doi.org/10.5281/zenodo.20768585)
- v1.4 DOI: [10.5281/zenodo.20767477](https://doi.org/10.5281/zenodo.20767477)
- v1.3 DOI: [10.5281/zenodo.20753499](https://doi.org/10.5281/zenodo.20753499)
- v1.2 DOI: [10.5281/zenodo.20738025](https://doi.org/10.5281/zenodo.20738025)
- v1.1 DOI: [10.5281/zenodo.20687470](https://doi.org/10.5281/zenodo.20687470)
- v1.0 DOI: [10.5281/zenodo.20516375](https://doi.org/10.5281/zenodo.20516375)
- v1.12 series DOI: [10.5281/zenodo.21044801](https://doi.org/10.5281/zenodo.21044801)
- v1.11 series DOI: [10.5281/zenodo.21034812](https://doi.org/10.5281/zenodo.21034812)
- v1.10 series DOI: [10.5281/zenodo.21009302](https://doi.org/10.5281/zenodo.21009302)
- v1.9 series DOI: [10.5281/zenodo.21001632](https://doi.org/10.5281/zenodo.21001632)
- v1.8 series DOI: [10.5281/zenodo.21000645](https://doi.org/10.5281/zenodo.21000645)
- v1.7 series DOI: [10.5281/zenodo.20971737](https://doi.org/10.5281/zenodo.20971737)
- v1.6 series DOI: [10.5281/zenodo.20792050](https://doi.org/10.5281/zenodo.20792050)
- v1.5 series DOI: [10.5281/zenodo.20768584](https://doi.org/10.5281/zenodo.20768584)
- v1.4 series DOI: [10.5281/zenodo.20767476](https://doi.org/10.5281/zenodo.20767476)
- v1.3 series DOI: [10.5281/zenodo.20753498](https://doi.org/10.5281/zenodo.20753498)
- Previous-series DOI (v1.2 and earlier): [10.5281/zenodo.20738024](https://doi.org/10.5281/zenodo.20738024)
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
Elementary Cellular Automata (v1.12). Zenodo.
https://doi.org/10.5281/zenodo.21044802
```

## License

Code is released under the [MIT License](LICENSE). The preprint is distributed
under Creative Commons Attribution 4.0 International via Zenodo.


