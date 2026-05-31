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

- A reproducible, non-generative discovery agent for ECA law exploration.
- A 20-world atlas organized into dynamic categories and 7 cycle laws.
- A fragility framework separating `f_total`, `f_core`, and `f_gap`.
- Case studies showing unique local oscillation, noise-gate fragility,
  productive basin switching, and stable-rich frontier dynamics.
- A methodological result: observer/dedup counts can break translation
  equivariance even when underlying ECA dynamics preserve it.

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

Describe the architecture:

- ECA simulation engine.
- Frame metrics: entropy, gzip ratio, transition rate, mutual information,
  density.
- Observer stack and deduplication.
- Seven cycle-law evaluators.
- Discovery policy and persistent `WorldRecord` history.

Emphasize that the LLM is used only outside the loop for interpretation and
documentation, not to select or evaluate laws during agent runs.

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
