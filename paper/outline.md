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

Each law is evaluated per run (one world, one seed, one step count) after the
observer and dedup stages succeed (`analysis_status == ok`). The output is
binary: accepted or rejected. Law signatures are frozensets of accepted law
names.

### Formal Criteria

| # | Law | Inputs | Criterion | Constants |
| --- | --- | --- | --- | --- |
| 1 | `velocidad_constante` | Position tracks of moving structures | At least 50% of moving tracks (`velocity > 0.05` cells/step) have linear `x(t)` with normalized residual `< 0.15` | - |
| 2 | `periodicidad` | Structure type list | At least one structure classified as `oscilador` | - |
| 3 | `densidad_estable` | Frame density time series | Coefficient of variation `CV = sigma(rho) / mu(rho) < 0.15` | - |
| 4 | `tipo_unico` | Structure type set | Exactly one structure type present | - |
| 5 | `complejidad_alta` | Frame metrics | `entropy_mean > 0.80` and `transition_rate > 0.25` | - |
| 6 | `frontera_temporal` | Frame metrics | `entropy_mean > 0.80` and `0.28 < transition_rate < 0.4352` | upper threshold calibrated 2026-05-24 |
| 7 | `temporal_scale_stability` | Frame metrics + steps | `temporal_load = steps * gzip_ratio / transition_rate < 19.03` | threshold calibrated 2026-05-24 |

`temporal_scale_stability` rejects any run with `transition_rate = 0`
(quiescent or static configurations), since temporal load is undefined
(`infinity`).

### Calibrated Constants

The `frontera_temporal` upper threshold `0.4352` is the midpoint between the
maximum `transition_rate` observed for `rule_110` (`0.4147`) and the minimum
for `rule_30` (`0.4557`) across six canonical seeds at `steps = 24`,
`width = 64`.

The `temporal_scale_stability` threshold `19.03` was fit on
`datasets/fase2c_v3.csv` (120 ECA scale samples). A decision tree at
`max_depth = 4` achieved accuracy `0.908`, precision `0.886`, and recall
`0.954` on the `analysis_ok` label.

Both constants are valid for the atlas protocol (`width = 64`, `steps` roughly
`24..200`) and should be recalibrated if width or step range changes
substantially.

### Caveats

`tipo_unico` is an observer-dependent exploratory signal, not a mirror-invariant
physical property. Fase 6b showed that `rule_110` and `rule_124` are left-right
mirrors of each other with identical dynamics, yet `tipo_unico` can fire
asymmetrically depending on orientation. `tipo_unico` is retained in the atlas
for its exploratory value but should not be used as evidence of physical
asymmetry.

`frontera_temporal` and `temporal_scale_stability` both depend on
`transition_rate`. Fase 4a and later tree analyses identify transition rate as
the main discriminator separating organized frontier dynamics from pure chaos
or static order. Other metrics (`density_mean`, `gzip_ratio`,
`mutual_info_mean`) are useful context features but should not be treated as
independent causal evidence without ablation.

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

#### Discovery and formal profile

`rule_108` was identified during a targeted local-oscillator search (Fase 16)
using minimal ICs on a quiescent background (`f(0,0,0) = 0`). The canonical IC
is a pair of active cells separated by one gap (`#.#`, word `101` in binary).
Under `rule_108`, this IC produces an exact period-2 local oscillator:

```text
Step t:     . . . # . # . . .
Step t+1:   . . . # # # . . .
Step t+2:   . . . # . # . . .
```

The oscillator is stationary (center of mass fixed), bounded (`span <= 3`),
and stable over 200 steps with zero drift on a uniform-zero background.

Formal profile (6 canonical seed labels, `width = 128`, `steps = 200`,
IC = `pair_gap1`): `periodicidad` and `tipo_unico` are accepted in `6/6`
runs. Mean `dedup_structure_count = 1.000`. The oscillator is deterministic
given the canonical IC; the seed labels are retained only to keep the profile
format consistent with other atlas worlds.

#### Algebraic derivation

The oscillator follows from three entries in the `rule_108` table:

| Neighborhood | Output | Role |
| --- | --- | --- |
| `010` | `1` | isolated active center stays active |
| `101` | `1` | gap fills in: `#.# -> ###` |
| `111` | `0` | center empties: `### -> #.#` |

`rule_108` is left-right symmetric (`f(l,c,r) = f(r,c,l)`), which explains why
the oscillator does not drift: the two flanking cells exert equal influence on
the center.

#### Fragility: quiescent-background activation

`rule_108` has the largest fragility gap in the atlas:

| Metric | Value |
| --- | --- |
| `f_total` | `0.992` |
| `f_core` | `0.047` |
| `f_gap` | `0.945` |
| Core positions | `61, 62, 63, 65, 66, 67` |
| Pattern | `clustered` |

The mechanism is geometric. The canonical IC (`pair_gap1`, 2 active bits in
`width = 128`) leaves more than 120 cells at zero. A one-bit perturbation at
any of those background positions activates the quiescent background: because
`f(0,1,0) = 1`, an isolated `1` on a zero background immediately grows,
producing new detectable structures. This changes secondary laws while leaving
`periodicidad` and `tipo_unico` intact as long as the oscillator core is
undisturbed. A perturbation within the core neighborhood (positions `61..63`,
`65..67`) displaces or destroys the oscillator, accounting for
`f_core = 0.047`.

This constitutes a third fragility mechanism, distinct from productive basin
switching (`rule_137`, Section 7.3) and noise-boundary fragility (`rule_54`,
Section 7.2): quiescent-background activation. The core behavior is robust,
but the minimal IC makes secondary laws highly sensitive to background
activation.

#### Uniqueness

Fase 18 ran an exhaustive search over all 128 ECA rules with quiescent
backgrounds (`f(0,0,0) = 0`), testing 510 IC words per rule (all non-empty
binary words of length 1..8), with `width = 128`, `steps = 200`, and burn-in
of 80 steps. Only `rule_108` produced local period-2 oscillators. No other
rule produced any local oscillator under this protocol for periods `2..16` and
span `<= 32`.

The family is internal to `rule_108`: 132 out of 179 candidate IC words are
accepted by the production observer as `periodicidad`, with oscillator spans
3, 5, 6, 7, and 8. All confirmed oscillators have period exactly 2; no longer
period was found.

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
