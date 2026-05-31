# ZUSE Automat Agent: Empirical Law Discovery in Elementary Cellular Automata

## Abstract (Provisional)

We present ZUSE Automat Agent, a deterministic discovery loop for elementary
cellular automata (ECA) that builds an empirical atlas of laws, world families,
and basin fragility without an LLM in the discovery loop. Across 20 worlds, 7
cycle laws, and controlled perturbation experiments, the system distinguishes
cycle-level laws from world-level regimes and from observer-induced artifacts.
Key findings include a unique local period-2 ECA oscillator in `rule_108`,
stable high-richness frontier worlds (`rule_46`, `rule_208`, `rule_209`), three
mechanisms of fragility, and a measured non-equivariance of the observer/dedup
pipeline despite translation-invariant ECA dynamics.

## 1. Contributions

We make the following contributions:

1. **ZUSE Automat Agent** — A deterministic, policy-driven discovery loop for
   ECA that accumulates multi-seed law evidence across worlds without symbolic
   regression or LLM guidance in the loop. The agent combines persistent
   world-record history, a dedup-gated observer stack, and a seven-law evaluator
   into a single reproducible pipeline.

2. **A five-category empirical atlas of 20 ECA worlds** — We classify 20 worlds
   into five dynamic families (*frontera-rich-estable*, *periodicidad-global*,
   *oscilador-local*, *multiregimen-productivo*,
   *multiregimen-escala-dependiente*) using law coverage, signature diversity,
   and fragility. The atlas extends Wolfram's four-class taxonomy by capturing
   intra-class structure and multi-scale silencing.

3. **A two-dimensional fragility framework** — We measure `f_total` and
   `f_core` separately, defining `f_gap = f_total - f_core` as a quantitative
   measure of secondary-law churn. Four distinct mechanisms are identified:
   stable basin (`rule_208/209`, `f_total = 0.000`), productive basin switching
   (`rule_137`, `f_gap = 0.318`), noise-boundary fragility (`rule_54`,
   `f_core = 0.677`), and quiescent-background activation (`rule_108`,
   `f_gap = 0.945`).

4. **`rule_108` as the unique stationary local-period-2 ECA oscillator** —
   Under an exhaustive protocol (128 quiescent ECA rules, 510 IC words per
   rule, span <= 32, period <= 16), `rule_108` is the only ECA rule that
   produces stationary local period-2 oscillators. The motif `#.# <-> ###`
   follows algebraically from `f(0,1,0) = f(1,0,1) = 1` and
   `f(1,1,1) = 0`, and the rule's left-right symmetry
   (`f(l,c,r) = f(r,c,l)`) explains why the oscillator does not drift.

5. **A measured separation between ECA dynamics and observer artifacts** —
   `rule_54` single-bit-IC frames are provably translation-invariant
   (confirmed by frame identity after shift normalization), while observer
   dedup counts range from 15 to 24 across IC positions. This non-equivariance
   is characterized as a pipeline property: absolute structure counts depend
   on IC context, but law signatures remain stable.

## 2. Related Work

Position the work against:

- Wolfram's ECA classes and the broader empirical program in *A New Kind of
  Science*.
- Cook's proof of universal computation in Rule 110.
- Automated scientific discovery systems such as AI Feynman, emphasizing the
  contrast between symbolic-regression discovery and ZUSE's deterministic
  observer/law/policy loop.

This section should clarify that ZUSE is not an LLM scientist; it is a
transparent experiment engine that accumulates evidence about cellular
automaton worlds.

## 3. System: ZUSE Automat Agent

ZUSE Automat Agent is a deterministic discovery loop over cellular automaton
worlds. A world is a simulator plus an initial-condition protocol and a time
window. For ECA worlds, the simulator is the standard binary radius-1 update
rule with periodic boundary conditions. The agent runs a world, computes frame
metrics, extracts candidate structures, evaluates a fixed set of laws, updates
world-level history, and chooses the next action through a transparent policy.

The loop has five layers:

1. **Simulation.** ECA frames are generated from explicit initial conditions
   with fixed `width`, `steps`, and `seed` or with designed ICs for controlled
   experiments. The simulator itself is not learned.

2. **Frame metrics.** Each run is summarized by density, entropy, temporal
   transition rate, gzip compressibility, and temporal mutual information.
   These features support both individual laws (`complejidad_alta`,
   `frontera_temporal`, `temporal_scale_stability`) and later meta-analysis.

3. **Observers and deduplication.** A stack of heuristic observers converts
   frame histories into `Estructura` records with type labels such as `glider`,
   `bloque`, and `oscilador`. The raw observer outputs are intentionally kept
   for audit, while `deduplicate_structures` estimates the number of physical
   structures. The production noise gate uses `dedup_structure_count > 40`.

4. **Cycle-law evaluation.** Seven laws are evaluated on each analyzable run.
   The result is a law signature: the set of accepted laws for that cycle.
   Noise-gated runs skip law evaluation rather than forcing a low-confidence
   signature.

5. **Policy and memory.** The agent stores a persistent `WorldRecord` per
   world, including visit count, score history, noise fraction, law signatures,
   peak signature diversity, and multiregime evidence. The policy then chooses
   among actions such as varying the seed, increasing scale, repeating a
   multi-regime world once more, or changing world.

The agent is deliberately non-generative inside the loop. No LLM proposes laws,
selects worlds, or evaluates a cycle. Symbolic regression was used only outside
the loop for calibration and analysis; it is not part of the online discovery
policy. The LLM-assisted work reported here occurs after runs are complete: it
helps design follow-up experiments, interpret artifacts, and write
documentation. This separation is important because every accepted law
signature in the atlas can be reproduced from deterministic scripts.

## 4. Seven Cycle Laws

List and define the current law set:

1. `velocidad_constante`
2. `periodicidad`
3. `densidad_estable`
4. `tipo_unico`
5. `complejidad_alta`
6. `frontera_temporal`
7. `temporal_scale_stability`

For each law, include its operational criterion and the level at which it
applies. Note explicitly that `tipo_unico` is an observer-dependent exploratory
signal, not a mirror-invariant physical law.

## 5. World Atlas: 20 Worlds and Dynamic Categories

Use `outputs/world_taxonomy/law_map.md` as the source table.

Primary categories:

- `frontera-rich-estable`
- `periodicidad-global`
- `oscilador-local`
- `multiregimen-productivo`
- `multiregimen-escala-dependiente`
- `noise-bounded`

Control/no-evidence bucket:

- `sin-evidencia-multiregimen` for controls and worlds without sufficient
  multi-regime evidence

The text should explain that the atlas is not just a score table: it separates
families by law coverage, diversity, fragility, and mechanism.

## 6. Fragility: `f_total`, `f_core`, `f_gap`

Define the perturbation protocol and metrics:

- `f_total`: fraction of one-bit IC perturbations that change any law
  signature.
- `f_core`: fraction that changes the category-defining core laws.
- `f_gap = f_total - f_core`: secondary-law churn or background sensitivity.

Main interpretation:

- Low `f_total` and low `f_core`: broad stable basin.
- High `f_total` and high `f_core`: true regime fragility.
- High `f_total` and low `f_core`: robust behavior with secondary-law churn.

Use `rule_108` as the extreme gap case and `rule_54` as the high-core-fragility
case.

## 7. Case Studies

### 7.1 `rule_108` — Unique Local Oscillator

`rule_108` produces the local period-2 motif:

```text
#.# <-> ###
```

Fase 18 shows it is unique among 128 quiescent ECA rules under the local-word
protocol (`length <= 8`). The family is internal to `rule_108`: 179 short IC
words converge to exact period-2 local oscillators; 132 are accepted by the
production observer as `periodicidad`.

### 7.2 `rule_54` — Noise Gate Anatomy

`rule_54` demonstrates noise-boundary fragility. In random complex ICs, local
bit flips can push `dedup_structure_count` over the threshold 40. Fase 19 shows
that a single active cell never approaches the gate, so the mechanism requires
complex IC geometry.

### 7.3 `rule_137` — Productive Basin Switching

`rule_137` has high productive fragility: perturbations move the IC between
non-empty law-signature regimes rather than into silence or noise. It is a key
example of high-dimensional basin structure.

### 7.4 `rule_46`, `rule_208`, `rule_209` — Stable-Rich Frontier

These worlds show that `frontera_temporal` was undersampled, not intrinsically
rare. They have high law richness with low diversity and extremely low
fragility, including zero measured fragility for `rule_208` and `rule_209`.

## 8. Observer Artifacts and Pipeline Equivariance

Fase 19 separates ECA dynamics from observer behavior:

- The `rule_54` single-bit frames are translation-invariant after shift
  normalization.
- The observer/dedup pipeline returns different structure counts depending on
  absolute position (`dedup_structure_count` 15..24).
- The law signature remains stable, but absolute counts are not safe as
  translation-equivariant physical evidence.

This section should frame observer artifacts as part of the scientific result,
not just an implementation flaw.

## 9. Limitations

- Observers are heuristic and not fully symmetry-invariant.
- `tipo_unico` is useful for exploration but not a mirror-invariant property.
- The atlas is empirical and parameterized by width, steps, thresholds, and IC
  protocols.
- Local oscillator uniqueness is proven only under the current protocol:
  quiescent background, stationary exact periodicity, IC words of length <= 8.
- PySR symbolic formulas remain blocked by Julia infrastructure; current
  conclusions rely on deterministic scripts and tree-based analysis.

## 10. Next Work

- Convert the outline into a full preprint with figures and tables.
- Add figures:
  - world taxonomy table,
  - law coverage matrix,
  - `f_total`/`f_core` spectrum,
  - `rule_108` oscillator motif,
  - `rule_54` gate and observer non-equivariance.
- Optionally extend local-oscillator search to moving oscillators, wider IC
  words, or non-zero backgrounds.
- Revisit PySR once Julia setup is stable.
