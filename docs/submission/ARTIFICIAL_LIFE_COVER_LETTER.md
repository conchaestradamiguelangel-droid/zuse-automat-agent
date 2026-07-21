# Cover Letter Draft - Artificial Life

Dear Editors,

I am pleased to submit the manuscript **"ZUSE Automat Agent: Empirical Law Discovery in Elementary Cellular Automata"** for consideration in *Artificial Life*. The paper presents ZUSE, a deterministic discovery pipeline for elementary cellular automata (ECA). ZUSE runs fixed simulation protocols, evaluates seven operational cycle laws, stores multi-seed WorldRecords, and measures basin fragility without using a language model inside the empirical discovery loop. Across a 20-world atlas, the system separates law coverage, observer artifacts, and fragility regimes that are collapsed by coarse visual taxonomy.

The main scientific case study concerns a periodic-background oscillator family in `rule_73/rule_109`. A length-8 background sweep identifies a `T=15` five-state locking mechanism, and a 25-cell, 12-step causal cone reveals an algebraic normal form (ANF) gradient: active-output monomial counts decay with distance from the defect center with `R^2 = 0.998197`, while active-output degree follows a spatial band law. The paper then audits the mechanism through a sequence of falsification tests, including non-T15 witnesses, compact T=2 controls, rule-family censuses, center-mediation analysis, perturbation audits, phase organization, and compressed causal-complexity proxies. The resulting claims remain empirical and protocol-bounded: ZUSE is presented as a reproducible evidence engine for CA law discovery, not as a universal autonomous scientist.

The manuscript fits *Artificial Life* because it sits at the intersection of emergent computation, cellular automata, computational mechanics, automated scientific discovery, and mechanistic analysis of artificial dynamical systems. The contribution is not merely an application of machine learning to CA; it is a fully reproducible audit trail showing how candidate laws, mechanism-specific gradients, and negative results can be discovered, challenged, and refined in a deterministic artificial-life substrate.

All code, data, scripts, reports, figures, PDFs, and versioned releases are public. The current citable preprint is available on Zenodo:

https://doi.org/10.5281/zenodo.21435062

The repository and reproducibility artifacts are available at:

https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

This manuscript is not under consideration elsewhere. I have no conflicts of interest to declare.

Sincerely,

Miguel Angel Concha Estrada  
Independent researcher  
conchaestradamiguelangel@gmail.com
