# Zenodo v1.35 Draft

This is a paste-ready draft for the manual Zenodo publication. Do not fill in
the DOI, publication date, checksum, or file size until the final candidate has
passed independent review.

## Basic metadata

- **Resource type:** Preprint
- **Title:** ZUSE Automat Agent: Empirical Law Discovery in Elementary Cellular Automata
- **Publication date:** `YYYY-MM-DD`
- **Creator:** Miguel Angel Concha Estrada
- **Affiliation:** Independent researcher
- **Version:** v1.35
- **Publisher:** Zenodo
- **Language:** English
- **License:** Creative Commons Attribution 4.0 International
- **Copyright:** Copyright (C) 2026 The author.

## Description

Version v1.35 extends the ZUSE preprint with Fases 91--103, a verified analysis
of the long-period oscillator population recovered in v1.34. The update does
not rerun or alter the 5,783,040-configuration census. It quotients the 3,296
confirmed long-period cases into physical attractors, constructs local
Hamming-1 intervention graphs, and derives an exact topological law for basin
robustness within the frozen protocol.

Main results:

- The 3,296 confirmed descriptors collapse into 192 strict physical attractor
  classes and 123 defect-morphology classes.
- Deduplication leaves 1,829 strict physical initial states and removes 1,467
  encoding aliases, with zero deterministic conflicts.
- Black/white conjugacy between rule_73 and rule_109 is verified exactly for
  all 3,296 trajectories and closes all 123 conjugacy-quotient classes.
- Forty-eight complete length-8 Q8 intervention cubes separate fragmentation
  within a fixed rule/background cube from fragmentation across cubes.
- On 219 fragile targets, 43,425 unit interventions obey an exact cut-coverage
  law: vertex or edge redundancy is restored if and only if the added state
  bypasses every corresponding critical cut. Direct cut removal, an independent
  max-flow calculation, and the geometric predicate agree with zero exceptions.
- A complete audit of 404,054 unordered pairs proves minimum rescue
  cardinality two in 69/126 vertex-connectivity strata and 68/139
  edge-connectivity strata. The remaining minima are bounded below by three;
  triples have not yet been executed.

The claims are deliberately bounded. Q8 edges are Hamming-1 interventions on
the central eight-bit initial word, not temporal transitions of the cellular
automaton. The exact law covers 219 targets in 48 frozen intervention cubes and
does not establish a theorem for arbitrary ECA basins, initial-condition widths,
or intervention families.

All results are deterministic and reproducible from committed scripts,
manifests, compact ledgers, reports, and tests.

Repository:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Keywords

- elementary cellular automata
- empirical law discovery
- complex systems
- periodic backgrounds
- basin topology
- graph connectivity
- causal audit
- reproducible computational science

## Related work

- **Is supplement to / Software:** https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- **Repository URL:** https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- **Programming language:** Python
- **Development status:** Active

## File gate

- **Upload filename:** `zuse_preprint.pdf`
- **Expected local source:** `paper/zuse_preprint.pdf`
- **File size:** `1,025,045 bytes`
- **Pages:** `59`
- **MD5:** `2516656a558e1fc0c7690d51abef2656`
- **SHA-256:** `22644346bc11807661d0e7c23e8e2f068bb100d2ab77d5a8589c19314a3e9747`
- **Version DOI:** `TBD after Zenodo publication`
- **Series DOI:** `TBD after Zenodo publication`
