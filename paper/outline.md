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

`rule_54` is the clearest example of noise-boundary fragility: perturbations do
not merely move the run to another productive signature, but can push the
observer output across the deduplicated structure gate. The production gate is:

```text
dedup_structure_count > 40 -> ruido_no_analizable
```

#### Fase 13: anatomy of the gate

Fase 13 measured three productive `rule_54` ICs at `steps = 96` and perturbed
each by all 64 one-bit flips. The reference deduplicated counts were close to
the gate:

| seed | reference dedup | noisy flips / 64 |
| --- | --- | --- |
| `20260638` | `32` | `14` |
| `20260640` | `33` | `18` |
| `20260642` | `39` | `40` |

Across the three seeds, `72/192` flips crossed into `ruido_no_analizable`
(`f_noise = 0.375`). Every noisy flip crossed for the same reason:
`dedup_structure_count > 40`. No alternative noise mechanism was observed.

The sensitive positions formed a clustered, multi-hot pattern rather than a
single contiguous block. Bins near the periodic boundary (`0..7` and `56..63`)
were repeatedly implicated, and bit 5 was the only bit whose flip crossed the
gate in all three measured seeds.

#### Fase 19: controlled single-bit negative case

Fase 19 tested whether bit 5 was a special absolute coordinate of `rule_54`.
It replaced the complex ICs with controlled single-bit ICs: for each
`k = 0..63`, the initial state contained only one active bit at position `k`.

The result separates CA physics from the observer pipeline:

- The ECA frames are translation-invariant after shift normalization.
- The observer/dedup counts are not translation-equivariant for this
  wide-spreading pattern: `dedup_structure_count` ranges from `15` to `24`
  across positions.
- The law signature is identical for all 64 positions:
  `temporal_scale_stability`.
- Every single-bit IC remains far below the gate (`dedup <= 24 < 40`).

Therefore, bit 5 is not a privileged coordinate of `rule_54`. The Fase 13
signal arises from the interaction between complex IC geometry and the
observer/gate pipeline. Complex ICs close to the threshold can be pushed across
it by local flips; a single active cell cannot.

#### Mechanism

`rule_54` has high total and core fragility (`f_total = 0.714`,
`f_core = 0.677`), but its mechanism differs from `rule_137`. In `rule_137`,
perturbations tend to move between productive regimes. In `rule_54`, a large
fraction of perturbations cross an analysis boundary: the run becomes too
fragmented for the current observer/dedup gate.

This makes `rule_54` a methodological case study as much as a dynamical one.
It shows that the atlas can identify worlds whose measured fragility is
dominated by proximity to an observer threshold. It also motivates the caveat that
absolute structure counts should not be treated as symmetry-invariant physical
observables without equivariance checks.

### 7.3 `rule_137` — Productive Basin Switching

`rule_137` is the primary example of productive basin switching: one-bit IC
perturbations change the law signature without ever crossing the noise gate or
reaching silence. All fragility is productive (`f_noise = 0.000`,
`f_silence = 0.000`), making it the cleanest case in the atlas for
inter-basin transitions.

#### Fragility profile

Three canonical seeds at `steps = 48`, `width = 64`:

| seed | reference signature | f_total |
| --- | --- | --- |
| `20260633` | `complejidad_alta + frontera_temporal` | `0.812` |
| `20260635` | `complejidad_alta + densidad_estable + frontera_temporal` | `0.219` |
| `20260673` | `complejidad_alta + densidad_estable + frontera_temporal + temporal_scale_stability + tipo_unico + velocidad_constante` | `0.859` |

Aggregate: `f_total = 0.630`, `f_core = 0.312`, `f_gap = 0.318`.

The per-seed range (`0.219..0.859`) is the widest in the atlas. Even the least
fragile measured seed has `f_total > 0.2`. The most fragile seeds (20260633 and
20260673) flip on more than 80% of one-bit perturbations.

#### Mechanism

`f_noise = 0.000`: no perturbed IC crosses the deduplicated structure gate. The
world remains analyzable throughout. The fragility is a property of productive
basin geography, not proximity to an observer threshold.

The pattern is `dispersed`: sensitive positions are distributed across the IC
width rather than concentrated near a motif. This is consistent with a world
that has many narrow productive basins whose boundaries intersect throughout
the IC space.

`peak_diversity = 0.833` — the highest in the atlas. The canonical seeds
themselves already visit multiple distinct productive regimes. The fragility
measurement extends this: not just that the world can reach different signatures
under different seeds, but that a single-bit perturbation to any one canonical
IC is enough to move between regimes.

#### f_core and f_gap interpretation

`f_core = 0.312` reflects genuine regime switching: flips that remove or
change laws defining the canonical signature. `f_gap = 0.318` reflects
secondary-law churn: the core productive signature survives, but laws on the
signature boundary (such as `densidad_estable` or `tipo_unico`) toggle.

The two components are roughly equal (0.312 vs 0.318), meaning `rule_137` sits
in a region where both core-regime transitions and secondary-law transitions are
common. This is structurally different from `rule_108` (`f_gap = 0.945`, where
the core oscillator is robust and secondary laws dominate) and from `rule_54`
(`f_gap = 0.037`, where the core productive signature changes but almost no
fragility is secondary).

#### Contrast with `rule_54` and `rule_108`

`rule_54` and `rule_137` both have high `f_total` (0.714 vs 0.630), but the
mechanisms are opposite: `rule_54` fragility is dominated by noise-gate
crossings (`f_noise = 0.375`), while `rule_137` fragility is entirely
productive. A perturbed `rule_137` IC stays analyzable and law-rich; it is
simply in a different productive regime.

`rule_108` contrasts from the opposite direction: its `f_core = 0.047` shows
that the defining behavior (the local oscillator) is nearly indestructible,
while `rule_137`'s `f_core = 0.312` shows that its defining signatures change
under nearly a third of all one-bit flips.

### 7.4 `rule_46`, `rule_208`, `rule_209` — Stable-Rich Frontier

These three worlds define the `frontera-rich-estable` category: low signature
diversity, near-maximal law richness, and very low fragility. They are the
counterexample that revised the early atlas interpretation of
`frontera_temporal`.

The first 15-world atlas made `frontera_temporal` look rare: it appeared only
as a minority law in class-4 multi-regime worlds such as `rule_137`,
`rule_110`, and `rule_54`. Fase 11 showed that this was a sampling artifact.
A sweep over all 256 ECA rules (`seeds = 20260523..20260525`, `W = 64`,
`T = 24`) found 38 rules where `frontera_temporal` activates in at least two
of three seeds, and 17 rules where it activates in all three.

The top rules by law richness were `rule_46`, `rule_208`, and `rule_209`.
Formal six-seed profiles (`20260523..20260528`, `W = 64`, `T = 24`) placed all
three in a new category:

| world | mean laws | peak diversity | category |
| --- | ---: | ---: | --- |
| `rule_46` | `5.833` | `0.333` | `frontera-rich-estable` |
| `rule_208` | `6.000` | `0.167` | `frontera-rich-estable` |
| `rule_209` | `6.000` | `0.167` | `frontera-rich-estable` |

The dominant signature is the same six-law set:

```text
velocidad_constante
densidad_estable
tipo_unico
complejidad_alta
frontera_temporal
temporal_scale_stability
```

Only `periodicidad` is absent. This makes the family nearly maximal under the
current seven-law system without relying on multi-regime exploration.

#### Stable richness rather than multi-regime diversity

The category is defined by the conjunction of high richness and low diversity.
`rule_137` is rich because it moves among several productive law signatures.
The frontier-rich worlds are rich because the same high-law signature appears
reliably across seeds.

This distinction matters operationally. A policy that only looks for signature
diversity would miss these worlds, even though they produce more accepted laws
per visit than any multi-regime world in the atlas. The Fase 11 taxonomy update
therefore adds:

```text
frontera-rich-estable := mean_laws >= 4.0 and peak_diversity <= 0.5
```

evaluated after noise-bounded and multi-regime cases.

#### Complement symmetry and independent convergence

`rule_46` and `rule_209` are a complement pair (`46 = 255 - 209`): exchanging
zeros and ones maps one into the other. Their shared profile is therefore one
physical phenomenon seen through global bit inversion.

`rule_208` is more surprising. Its complement is `rule_47`, not `rule_46` or
`rule_209`, yet it reaches the same maximum-richness profile. This suggests
that the `frontera-rich-estable` regime is not a single isolated symmetry
orbit; at least two distinct ECA regions converge to the same six-law
frontier.

#### Fragility

Fase 12 measured one-bit fragility for the three worlds using the same protocol
as `rule_137` and `rule_54`:

| world | f_total | f_core | f_noise |
| --- | ---: | ---: | ---: |
| `rule_46` | `0.031` | `0.031` | `0.000` |
| `rule_208` | `0.000` | `0.000` | `0.000` |
| `rule_209` | `0.000` | `0.000` | `0.000` |

The result is the opposite end of the fragility spectrum from `rule_137`.
Where `rule_137` has many narrow productive basins (`f_total = 0.630`),
`rule_208` and `rule_209` have measured basins so wide that no single-bit flip
changes the law signature. `rule_46` is only slightly fragile: two of 192
single-bit perturbations change signature across the three measured seeds.

This confirms that high law richness does not imply high fragility. Richness
can arise either from many neighboring productive regimes (`rule_137`) or from
a single broad, stable regime (`rule_46/208/209`).

#### Scientific revision

The correct conclusion is not that `frontera_temporal` is intrinsically rare.
It is rare in the original discovery atlas because the original world sequence
under-sampled stable high-richness boundary worlds. In the full ECA sweep,
`frontera_temporal` is a robust marker of the `frontera-rich-estable` family.

## 8. Observer Artifacts and Pipeline Equivariance

The ZUSE pipeline contains two classes of observer artifact that the atlas
identifies and characterizes. Framing these artifacts as results — not just
implementation limitations — is important: they define the boundary between
what the system measures reliably and what it does not.

### 8.1 Mirror asymmetry in `tipo_unico` (Fase 6b)

`rule_110` and `rule_124` are left-right mirrors of each other: the rule table
for `rule_124` is obtained by reflecting every neighborhood
`f(l,c,r) -> f(r,c,l)` in the `rule_110` table. Under periodic boundary
conditions, the two rules produce physically equivalent dynamics up to spatial
reflection.

Despite this equivalence, `tipo_unico` can fire asymmetrically: it may be
accepted for one orientation and rejected for the other, depending on which
structure types the heuristic observers label from the specific frame sequence.
Since `tipo_unico` counts whether exactly one structure type appears, its value
depends on the labeling convention of the observers, not only on the CA
dynamics.

`tipo_unico` is retained in the atlas for its exploratory value: it reliably
distinguishes runs with homogeneous structure populations from runs with mixed
populations. It should not be used as evidence of physical left-right
asymmetry.

### 8.2 Translation non-equivariance of the dedup pipeline (Fase 19)

ECA with periodic boundary conditions is translation-invariant: shifting the
initial condition by any number of cells produces the same dynamics up to a
spatial shift. A pipeline that correctly identifies physical structures should
therefore return the same structure count for all translations of the same IC.

Fase 19 tested this directly: 64 single-bit ICs for `rule_54`, one active bit
at each position `k = 0..63`, with `width = 64` and `steps = 96`. The ECA
frames were confirmed translation-invariant (frame identity after shift
normalization: `True`). The observer/dedup pipeline was not:

| metric | range across 64 positions |
| --- | --- |
| `dedup_structure_count` | `15..24` (29 distinct result classes) |
| `raw_structure_count` | `45..72` |
| law signature | `temporal_scale_stability` (all 64 identical) |
| `analysis_status` | `ok` (all 64) |

The mechanism is a boundary interaction: `rule_54` produces wide-spreading
patterns that cross the periodic frame boundary. The dedup algorithm's handling
of cyclic-span structures varies depending on the absolute IC position relative
to where structure boundaries fall on the lattice. The result is a
position-dependent count that is not a translation-equivariant physical
observable.

### 8.3 Implications for the atlas

Both artifacts are bounded in their effect:

- `tipo_unico` asymmetry is a labeling artifact, not a count artifact. It
  affects which laws are accepted, but only for runs where the structure
  population is near the one-type boundary. Runs with clearly homogeneous
  or clearly mixed populations are unaffected.

- Dedup non-equivariance affects absolute structure counts but not law
  signatures. In Fase 19, all 64 translated ICs produce identical law
  signatures despite varying dedup counts. The noise gate (`dedup > 40`) is
  never approached by single-bit ICs, and law evaluation depends on count
  magnitude only through the gate.

The atlas therefore relies on law signatures as the primary evidence unit.
Absolute dedup counts appear in world profiles as context and should be
interpreted with the translation-equivariance caveat. Future work on
symmetry-invariant observers would remove both artifacts.

## 9. Limitations

### 9.1 Fixed protocol parameters

The atlas is valid for the parameter regime used: `width = 64` (formal
profiles), `width = 128` (rule_108 oscillator), `steps` roughly `24..200`, and
the IC protocols defined per world. The two calibrated thresholds —
`frontera_temporal` upper bound `0.4352` and `temporal_scale_stability`
threshold `19.03` — were fit on data from this regime. Applying the atlas to
significantly different widths or step counts requires recalibration. This is
not a flaw in the methodology; it is the expected scope of an empirically
grounded atlas.

### 9.2 Heuristic observers

The observer stack uses geometric heuristics to label structures as `glider`,
`bloque`, or `oscilador`. These heuristics are not derived from first
principles and are not provably complete or sound for arbitrary ECA dynamics.
As shown in Section 8, they are not translation-equivariant for wide-spreading
patterns and are not mirror-invariant for `tipo_unico`. The atlas is built on
law signatures, which are more robust than absolute observer counts, but the
underlying observers remain heuristic. Replacing them with symmetry-invariant
observers would be a meaningful improvement.

### 9.3 Bounded local oscillator protocol

The uniqueness claim for `rule_108` holds under a specific protocol: quiescent
zero background, stationary exact periodicity (no drift), IC words of binary
length 1..8 (510 non-zero words per rule), and period detection window 2..16
with local span <= 32. Moving oscillators, longer IC words, non-zero
backgrounds, or longer detection periods are outside the current protocol. The
claim is therefore: no other quiescent ECA rule produces a stationary
local-period oscillator under this protocol. It is not a claim about ECA
oscillators in general.

### 9.4 Empirical atlas, not axiomatic classification

The world categories are induced from observed law signatures across a finite
number of seeds and step counts. A world classified as
`multiregimen-productivo` on 6..15 visits could exhibit different behavior at
larger scale, with different IC distributions, or under longer runs. The
categories are stable empirical summaries, not theorems. `rule_90` is a clear
example: it is classified as `multiregimen-escala-dependiente` because
high-scale visits become silent under the current protocol, but the underlying
XOR dynamics have algebraic structure that the current seven laws do not
capture.

### 9.5 PySR symbolic regression pending

The decision-tree analyses (Section 4, temporal calibration) provide strong
empirical signal but not closed-form symbolic expressions. PySR was planned as
a follow-up to produce interpretable formulas for the calibrated thresholds and
fragility spectra. The Julia dependency required by PySR remains unresolved.
Current conclusions rely on deterministic scripts and tree-based models. This
does not affect the validity of the atlas findings, but the symbolic
interpretation layer is incomplete.

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
