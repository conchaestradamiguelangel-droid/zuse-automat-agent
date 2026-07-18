# ZUSE External Landscape Audit

Date: 2026-07-18

Purpose: turn the external audit into engineering decisions for ZUSE. This is
not a literature review for the paper yet. It is a filter: what improves the
scientific core, what is only framing, and what should be rejected.

## Current ZUSE Position

ZUSE is a deterministic empirical-law discovery pipeline for elementary
cellular automata. Its current strong point is not just finding patterns, but
documenting a falsification chain:

- detect a law;
- test static explanations;
- test dynamic explanations;
- test external backgrounds;
- test perturbations;
- publish each stable claim with code, outputs, commits, and Zenodo versions.

The current v1.30 claim is:

- `CONTEXT_UNDISCRIMINATED`;
- `RESIDUAL_CONFIRMED_PERSISTENT`;
- the residual `rule_109/bg=1100/T=8/word=00000110` is a genuine period-8
  oscillator through `t=500`;
- aggregate context frequencies do not explain it.

The next scientific question is therefore phase/order/trajectory, not another
uniform rule perturbation.

## External Work: Decision Table

| Area | Reference | What It Does | Useful for ZUSE | Decision |
| --- | --- | --- | --- | --- |
| Symbolic regression | PySR / SymbolicRegression.jl | Open-source practical symbolic regression for interpretable scientific models. | Reopen only after ZUSE has a larger dataset; current 17/66 case datasets are too small. | Later |
| Physics-inspired SR | AI Feynman | Uses neural fitting plus physics-inspired decompositions such as symmetry/separability before symbolic regression. | The useful idea is not the tool itself, but the workflow: test separability before fitting. | Study selectively |
| Program search | FunSearch | LLM-generated programs plus systematic evaluator / evolutionary search. | Possible future IC/background search, but only when ANF-gradient scoring is cheap enough or cached. | Later |
| Automated science agents | The AI Scientist | End-to-end idea generation, experiments, paper writing, and review in ML domains. | Useful only as contrast. ZUSE should keep human verification and deterministic evaluators. | Do not adopt |
| Computational mechanics | CSSR / epsilon-machines | Infers predictive causal states from discrete time series. | Best immediate candidate: test statistical complexity / causal-state structure on 17 `rule_109` cases. | Incorporate next |
| Mechanistic interpretability | Circuits / ablation language | Explains model behavior through circuits and ablations. | Useful vocabulary for Fases 63-66: ablation, local circuit, faithful mechanism. | Incorporate as framing |
| CA simulator validation | Golly | Open-source CA simulator with HashLife and Wolfram 1D rule support. | Use as optional visual sanity check, not as core pipeline dependency. | Optional |
| Interactive scientific communication | Distill-style articles | Explorable explanations and interactive figures. | Useful for outreach later: residual phase animation, ANF gradient plots. | Later |
| Continuous CA / artificial life | Lenia | Continuous CA with rich autonomous patterns. | Good contrast only; methods do not transfer to binary 1D ECA. | Do not adopt technically |
| Generic ABM / SciML frameworks | NetLogo, Mesa, SciML/UDE | Agent-based or continuous differential-equation tooling. | Adds abstraction overhead and does not fit binary radius-1 ECA. | Reject |

## Verified Source Notes

The following sources were checked against primary or near-primary references
before turning the audit into decisions:

- PySR paper: https://arxiv.org/abs/2305.01582
- AI Feynman paper: https://www.science.org/doi/10.1126/sciadv.aay2631
- FunSearch paper: https://www.nature.com/articles/s41586-023-06924-6
- CSSR homepage: https://bactra.org/CSSR/
- Computational mechanics overview: https://arxiv.org/abs/cond-mat/9907176
- The AI Scientist paper: https://arxiv.org/abs/2408.06292
- Golly official page: https://golly.sourceforge.io/
- Lenia page: https://chakazul.github.io/lenia.html
- Distill hiatus / journal status: https://distill.pub/2021/distill-hiatus

## What We Should Incorporate Now

### 1. Fase 67 remains valid

Do not replace Fase 67. The external audit reinforces it.

Reason: CSSR/computational mechanics and mechanistic interpretability both say
the next useful object is a time-resolved state/trajectory, not an aggregate
count. That matches the current ZUSE residual.

Immediate Fase 67 question:

> Which phase of the period-8 residual trajectory separates
> `bg=1100/T=8/word=00000110` from the nearest negative
> `bg=1100/T=10/word=00111001`?

### 2. Add a compact "mechanism audit" vocabulary

Use these words in future reports and possibly the paper:

- `ablation`: for Fases 63-64 interventions;
- `local circuit`: for the center-mediated `rule_109` ANF structure;
- `faithful mechanism`: for a perturbation that preserves oscillatory support;
- `unfaithful ablation`: for a perturbation that destroys the mechanism before
  the ANF gradient can be measured.

This improves clarity without changing science.

### 3. Plan a CSSR / causal-state test after Fase 67

The best new method candidate is not PySR yet. It is a discrete-state
trajectory model:

- input: defect snapshots or phase-coded defect traces;
- target: the 17 `rule_109` cases;
- question: do positives and negatives differ in inferred causal-state
  structure or statistical complexity?

Keep this small. Do not attempt a universal CSSR library integration before a
minimal pilot.

Recommended future phase:

`Fase 68: causal-state / phase-symbol audit for rule_109`

### 4. Delay PySR until the dataset grows

PySR is real and relevant, but ZUSE currently has too few independent gradient
cases for robust symbolic regression. Reopen when one of these is true:

- at least 150-200 comparable gradient measurements;
- multiple rule families beyond `rule_109`;
- a clear target variable beyond binary category labels.

### 5. Use Golly only as a visual sanity check

Golly can help visually verify a few oscillators, but it should not become a
dependency of the ZUSE scientific pipeline. The core must remain scriptable,
deterministic, and repo-native.

## What We Should Not Incorporate

- Do not adopt The AI Scientist style autonomy. ZUSE's advantage is human
  verification plus deterministic evaluators, not fully automated paper
  generation.
- Do not cite Wolfram Physics Project as technical support unless a specific,
  directly relevant claim is verified and needed. It is too broad and
  reputationally risky for this paper.
- Do not migrate ECA simulation to NetLogo, Mesa, or SciML. These frameworks
  reduce speed and add abstraction without helping the current questions.
- Do not build interactive Distill-style output now. Useful later for outreach,
  not for the active causal chain.

## Roadmap Impact

Recommended sequence:

1. `Fase 67`: phase/trajectory comparison of residual vs nearest negative.
2. `Fase 68`: minimal causal-state / phase-symbol audit if Fase 67 still leaves
   ambiguity.
3. Optional visual sanity check in Golly for the residual and nearest negative.
4. Larger-catalog expansion before any serious PySR revival.

## Bottom Line

The audit does not suggest changing direction. It sharpens the path:

- ZUSE is already strong on reproducibility and negative-result discipline.
- The immediate weakness is not tooling; it is catalog breadth and
  time-resolved mechanism explanation.
- The next level is phase/trajectory analysis, followed by a small
  computational-mechanics-style test.

