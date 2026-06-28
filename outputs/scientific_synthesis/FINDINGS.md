# ZAA Scientific Synthesis — Fases 11-21a

Date: 2026-05-31

This document consolidates the current scientific map of ZAA after the ECA
sweep, world taxonomy, basin-fragility diagnostics, `rule_54` gate anatomy,
`rule_51` periodicity validation, `core_fragility`, the Fase 16 local
oscillator search, the Fase 17 formal `rule_108` atlas profile, and the
Fase 18 local oscillator family sweep, the Fase 19 controlled `rule_54`
single-bit experiment, the Fase 20a profile of the remaining
`frontera_temporal` sweep candidates, and the Fase 20b long-journal check
of the top four new candidates, and the Fase 21a designed periodic-IC sweep.

Primary artifacts:

- `outputs/world_taxonomy/law_map.md`
- `outputs/pysr_fase7/FINDINGS.md`
- `outputs/fragility_fase10/fragility_report.md`
- `outputs/fragility_fase10/core_fragility_report.md`
- `outputs/rule54_gate_fase13/rule54_gate_report.md`
- `outputs/rule54_controlled_ic_fase19/rule54_single_bit_report.md`
- `outputs/periodicity_fase14/periodicity_sweep_report.md`
- `outputs/local_oscillators_fase16/local_oscillator_report.md`
- `outputs/profile_fase17/rule108_seed_profile.json`
- `outputs/profile_fase17/rule108_fragility.json`
- `outputs/local_oscillator_family_fase18/local_oscillator_family_report.md`
- `outputs/frontera_sweep/remaining_candidate_profiles.md`
- `outputs/frontera_sweep/top4_long_journal_fase20b/top4_long_report.md`
- `outputs/periodicity_fase21/periodic_ic_sweep_report.md`

## 1. Current Atlas

The atlas now covers 20 worlds and 7 cycle laws:

- `velocidad_constante`
- `periodicidad`
- `densidad_estable`
- `tipo_unico`
- `complejidad_alta`
- `frontera_temporal`
- `temporal_scale_stability`

The world taxonomy currently distinguishes:

| category | examples | defining behavior |
| --- | --- | --- |
| `frontera-rich-estable` | `rule_46`, `rule_208`, `rule_209` | stable high law richness, low diversity |
| `periodicidad-global` | `rule_51` | global period-2 frame complementation |
| `oscilador-local` | `rule_108` | local period-2 particle on quiescent background |
| `multiregimen-productivo` | `rule_137`, `rule_54`, `rule_110`, `rule_124`, `rule_109`, `rule_18` | productive signature diversity |
| `multiregimen-escala-dependiente` | `rule_90` | non-empty signatures at some scales, high-scale silence |
| `noise-bounded` | `rule_30`, `rule_150` | crosses the dedup noise gate |
| `sin-evidencia-multiregimen` | synthetic/Life controls | no multi-regime evidence in current journal |

## 2. frontera_temporal Is Undersampled, Not Rare

Early atlas runs made `frontera_temporal` look rare. The full ECA sweep changed
that interpretation.

Fase 11 sweep:

- Rules tested: all ECA `0..255`
- Seeds: `20260523..20260525`
- Steps: `24`
- Width: `64`

Result:

- 38 ECA rules activate `frontera_temporal` in at least `2/3` seeds.
- 17 ECA rules activate it in `3/3` seeds.
- `rule_46`, `rule_208`, and `rule_209` are the strongest stable-rich cases.

Formal profiles:

| world | category | mean_laws | peak_diversity | core |
| --- | --- | --- | --- | --- |
| `rule_46` | `frontera-rich-estable` | 5.833 | 0.333 | six-law frontier signature |
| `rule_208` | `frontera-rich-estable` | 6.000 | 0.167 | six-law frontier signature |
| `rule_209` | `frontera-rich-estable` | 6.000 | 0.167 | six-law frontier signature |

Fase 20a then profiled the 35 remaining sweep candidates under the same formal
six-seed protocol (`steps=24`, `width=64`, seeds `20260523..20260528`).
These candidate-protocol labels do not automatically overwrite the long-journal
atlas categories, but they answer whether the top-three rules were isolated
outliers.

Result:

| candidate-protocol category | count |
| --- | --- |
| `frontera-rich-estable` | 24 |
| `multiregimen-productivo` | 8 |
| `sin-evidencia-multiregimen` | 3 |

Highest-richness additional candidates:

| world | category | mean_laws | peak_diversity |
| --- | --- | --- | --- |
| `rule_84` | `frontera-rich-estable` | 5.833 | 0.333 |
| `rule_138` | `frontera-rich-estable` | 5.833 | 0.333 |
| `rule_212` | `frontera-rich-estable` | 5.833 | 0.333 |
| `rule_213` | `frontera-rich-estable` | 5.833 | 0.333 |
| `rule_174` | `frontera-rich-estable` | 5.667 | 0.333 |
| `rule_116` | `frontera-rich-estable` | 5.667 | 0.500 |
| `rule_244` | `frontera-rich-estable` | 5.667 | 0.500 |

Fase 20b tested selective atlas integration by running an independent
160-cycle policy journal over the four strongest new candidates
(`rule_84`, `rule_138`, `rule_212`, `rule_213`) without modifying production
`WORLD_SEQUENCE`.

Long-journal result:

| world | long-journal category | visits | mean_laws | peak_diversity | noise_ratio |
| --- | --- | --- | --- | --- | --- |
| `rule_84` | `sin-evidencia-multiregimen` | 40 | 3.125 | 0.143 | 0.300 |
| `rule_138` | `noise-bounded` | 41 | 2.561 | 0.167 | 0.561 |
| `rule_212` | `sin-evidencia-multiregimen` | 40 | 3.300 | 0.143 | 0.300 |
| `rule_213` | `sin-evidencia-multiregimen` | 39 | 3.000 | 0.148 | 0.308 |

Interpretation: the `steps=24` candidate profile is a useful frontera filter,
but not atlas-grade stability evidence. The top four are rich at the short
formal scale, then lose `frontera_temporal` frequency or approach the noise
gate under policy scaling. They should not be promoted to the canonical atlas
without a scale-aware category or additional controlled protocol.

This defines a candidate tier, **frontera-short-scale**: rules that are
frontier-rich under the fixed sweep protocol but fail atlas-grade long-journal
validation. This is a filter result, not a canonical world category.

Conclusion: `frontera_temporal` is demanding but not intrinsically rare. It is
the marker of a broad stable high-richness boundary band that the original
atlas under-sampled, not a three-rule anomaly. However, only long-journal
validation distinguishes stable atlas worlds from short-scale frontera
candidates.

## 3. periodicidad Exists in ECA in Global and Local Forms

Fase 14 tested periodicity across atlas ECA worlds and known periodic
candidates.

Result:

- Atlas ECA worlds: `0/50` periodicity hits each.
- `rule_51`: `50/50` periodicity hits, all production-valid.
- `rule_15` and `rule_57`: `0/50`.

Fase 21a then replaced random ICs with explicit spatially periodic ICs:
32 designed 8-bit words repeated into `width=64`, tested across all ECA
rules `0..255` at `steps=96`.

Result:

- Total runs: `8192`.
- Frame-periodic cases: `2128/8192`.
- Production `periodicidad` hits: `2086/8192`.
- ECA rules with at least one production hit: `207/256`.

Strongest rules:

| world | hits/32 | mechanism |
| --- | --- | --- |
| `rule_51` | 32/32 | global period-2 complementation |
| `rule_15` | 30/32 | periodic background induced by designed IC |
| `rule_85` | 30/32 | periodic background induced by designed IC |
| `rule_105` | 30/32 | periodic background induced by designed IC |
| `rule_170` | 30/32 | periodic background induced by designed IC |
| `rule_240` | 30/32 | periodic background induced by designed IC |
| `rule_150` | 28/32 | additive periodic background |

`rule_51` implements `f(a,b,c) = NOT b`, so every cell complements itself each
step independently of neighbors. This produces deterministic period-2 global
frame dynamics.

Formal `rule_51` profile:

| metric | value |
| --- | --- |
| category | `periodicidad-global` |
| ok | 6/6 |
| mean_laws | 4.500 |
| peak_diversity | 0.333 |
| core laws | `periodicidad` |
| core_fragility | 0.000 |

Fase 16 then searched for the stricter case: a local oscillator on a stable
zero background. The rule filter required `f(0,0,0)=0`, and the ICs were
minimal localized seeds (`point`, `pair_gap1`, `triple`) at width 128 and
steps 200.

Result:

- Candidate rules: 116 after excluding atlas and trivial zero-convergers.
- Rows evaluated: 348.
- Local oscillator candidates: 2.
- Positive rule: `rule_108`.

`rule_108` from `pair_gap1` or `triple` converges immediately to the stationary
period-2 motif:

```text
#.# <-> ###
```

The active region stays localized with span <= 3 for 200 steps, the background
remains quiescent, and the production pipeline accepts `periodicidad`.

Interpretation: `periodicidad` is now validated on real ECA dynamics in three
forms. Random ICs rarely produce observer-level periodicity. Designed periodic
ICs make it widespread (`207/256` rules), mostly as periodic backgrounds or
spatially repeated temporal cycles. `rule_51` is the clean global case, and
`rule_108` is the stricter local period-2 particle oscillator.

Fase 17 integrates `rule_108` formally into the atlas. The canonical IC is
`pair_gap1` on a quiescent zero background; the point IC is a negative control
that remains stable but does not activate `periodicidad`.

Formal `rule_108` profile:

| metric | value |
| --- | --- |
| category | `oscilador-local` |
| canonical IC | `pair_gap1` |
| ok | 6/6 |
| dominant signature | `periodicidad + tipo_unico` |
| mean_laws | 2.000 |
| mean_dedup_structure_count | 1.000 |
| motif | `#.# <-> ###` |
| f_total | 0.992 |
| core_fragility | 0.047 |
| core fragile positions | `61..63`, `65..67` |

Interpretation: almost any extra bit changes secondary laws (`f_total=0.992`),
but the oscillator core is highly robust (`core_fragility=0.047`) and its
fragility is localized around the motif.

Fase 18 asks whether `rule_108` is isolated or part of a broader ECA rule
family. It exhaustively tests all ECA rules with quiescent zero background
(`f(0,0,0)=0`) against all non-zero binary IC words of length `1..8`, centered
on a zero background.

Result:

- Rules tested: 128.
- IC words per rule: 510.
- Physical local-oscillator candidates: 179.
- Rules with candidates: 1.
- Unique rule: `rule_108`.
- Periods found: only `T=2`.
- Production-valid candidates: 132.

Interpretation: under the current stationary local-periodicity protocol,
`rule_108` is unique as an ECA rule. The family structure is not across rules;
it is internal to `rule_108`, where many short IC words converge to exact
local period-2 motifs. No period greater than 2 appears for words of length
<= 8.

## 4. Fragility Has Two Axes

Fase 15b separates:

- `f_total`: any law-signature change under one-bit IC flips.
- `f_core`: change in the laws that define the world's category/regime.

This distinction matters because some worlds keep their defining behavior while
secondary laws change.

| world | category | f_total | f_core | interpretation |
| --- | --- | --- | --- | --- |
| `rule_208` | `frontera-rich-estable` | 0.000 | 0.000 | perfectly stable |
| `rule_209` | `frontera-rich-estable` | 0.000 | 0.000 | perfectly stable |
| `rule_46` | `frontera-rich-estable` | 0.031 | 0.031 | almost perfectly stable |
| `rule_90` | `multiregimen-escala-dependiente` | 0.172 | 0.000 | secondary-law churn only |
| `rule_51` | `periodicidad-global` | 0.193 | 0.000 | periodicity survives, density churns |
| `rule_124` | `multiregimen-productivo` | 0.224 | 0.083 | mostly secondary churn |
| `rule_109` | `multiregimen-productivo` | 0.307 | 0.307 | core changes match total changes |
| `rule_110` | `multiregimen-productivo` | 0.323 | 0.198 | mixed core/secondary changes |
| `rule_18` | `multiregimen-productivo` | 0.349 | 0.135 | mixed, mostly secondary |
| `rule_137` | `multiregimen-productivo` | 0.630 | 0.312 | high productive-regime fragility |
| `rule_54` | `multiregimen-productivo` | 0.714 | 0.677 | high core fragility, noise-boundary |
| `rule_108` | `oscilador-local` | 0.992 | 0.047 | local oscillator survives almost all perturbations |

Key result: `rule_51` falsified the naive prediction that global periodicity
would imply `f_total = 0`. It does imply `f_core = 0`: the periodic behavior is
invariant, but secondary laws such as `densidad_estable` can change.
`rule_108` is the sharper version of the same lesson: `f_total` is almost
maximal, but core fragility remains low because the local oscillator survives
all but six central perturbations.

## 5. Three High-Fragility Mechanisms

The atlas now separates three high-fragility mechanisms. The third one only
became visible after `rule_108`: a near-empty quiescent background can be very
sensitive in full signature while its local core remains stable.

### Fase 13a — Fase 12 Fragility Arc Consolidated

Fase 12 closes the first complete fragility arc: the measured spectrum covers
10 worlds before adding the later `rule_51` and `rule_108` special cases. The
core result is not just the ranking by `f_total`, but the split between two
mechanisms that can both produce high fragility.

#### Spectrum Ordered by `f_total`

| world | category | f_total | f_noise | pattern |
| --- | --- | ---: | ---: | --- |
| `rule_208` | `frontera-rich-estable` | 0.000 | 0.000 | - |
| `rule_209` | `frontera-rich-estable` | 0.000 | 0.000 | - |
| `rule_46` | `frontera-rich-estable` | 0.031 | 0.000 | - |
| `rule_90` | `multiregimen-escala-dependiente` | 0.172 | 0.000 | clustered |
| `rule_124` | `multiregimen-productivo` | 0.224 | 0.000 | dispersed |
| `rule_109` | `multiregimen-productivo` | 0.307 | 0.000 | clustered |
| `rule_110` | `multiregimen-productivo` | 0.323 | 0.000 | clustered |
| `rule_18` | `multiregimen-productivo` | 0.349 | 0.000 | clustered |
| `rule_137` | `multiregimen-productivo` | 0.630 | 0.000 | dispersed |
| `rule_54` | `multiregimen-productivo` | 0.714 | 0.375 | clustered |

#### Mechanism Split

`rule_137` and `rule_54` are both high-fragility worlds, but their mechanisms
are different.

- **Productive basin switching**: `rule_137` has `f_total = 0.630` and
  `f_noise = 0.000`. One-bit perturbations move the IC between productive law
  signatures without collapsing the run into noise.
- **Noise-boundary fragility**: `rule_54` has `f_total = 0.714` and
  `f_noise = 0.375`. A large fraction of perturbations cross the deduplicated
  structure gate rather than merely switching productive signatures.

Thus high `f_total` is not a single phenomenon. It can mean a dense landscape
of productive basins (`rule_137`) or proximity to the observer noise boundary
(`rule_54`).

#### The `f_noise = 0` Rule and Its Exception

Nine of the ten Fase 12 worlds have `f_noise = 0.000`. This makes productive
fragility the default mechanism in the measured spectrum: perturbations
usually change signatures without making the run unanalyzable.

`rule_54` is the documented exception. Its `f_noise = 0.375` identifies a
separate mechanism: fragility caused by the run sitting close to the
`dedup_structure_count > 40` threshold.

#### Spatial Pattern: `rule_124` as Second Dispersed World

`rule_137` is not the only world with spatially dispersed fragility.
`rule_124` is the second dispersed case in the measured Fase 12 set:

- `rule_137`: `f_total = 0.630`, dispersed, high-intensity productive switching.
- `rule_124`: `f_total = 0.224`, dispersed, lower-intensity productive switching.

This distinction matters: **dispersed** describes the spatial geometry of
sensitivity, not its magnitude. `rule_124` shows that global sensitivity can
exist even when the total fragility is moderate.

### Productive Basin Switching

Example: `rule_137`

- `f_total = 0.630`
- `f_core = 0.312`
- `f_noise = 0.000`
- pattern: `dispersed`

Perturbations move the IC among productive law-signature regions. The world
does not fall into silence or noise; it changes productive regime.

### Noise-Boundary Fragility

Example: `rule_54`

- `f_total = 0.714`
- `f_core = 0.677`
- `f_noise = 0.375`
- pattern: `clustered`

Fase 13 showed that every noisy `rule_54` flip crosses the same gate:

```text
dedup_structure_count > 40
```

The most sensitive seed, `20260642`, starts at `reference_dedup_structure_count
= 39`, only one structure below the threshold. This explains why many local
perturbations push it into `ruido_no_analizable`.

Fase 19 adds the controlled negative case: single-bit ICs for every position
`k=0..63`, with `width=64` and `steps=96`.

Result:

- The ECA frames themselves are translation-invariant.
- The observer/dedup pipeline is not translation-equivariant for this
  wide-spreading pattern: `dedup_structure_count` ranges from `15` to `24`
  depending on position.
- The law signature is stable for all 64 positions:
  `temporal_scale_stability`.
- Every single-bit IC remains far below the noise gate (`>40`).

Interpretation: the Fase 13 bit-5 signal is not a special absolute coordinate
of the CA rule. It is an interaction between complex IC geometry and the
observer/gate pipeline. The noise-boundary mechanism requires rich ICs near
the dedup threshold; a single active cell cannot trigger it.

### Quiescent-Background Activation

Example: `rule_108`

- `f_total = 0.992`
- `f_core = 0.047`
- `f_gap = 0.945`
- pattern: `clustered` for the oscillator core

The canonical IC has only two active bits on a zero background. A one-bit
perturbation almost anywhere in the background can ignite additional dynamics
and change secondary laws. The local oscillator itself survives unless the
perturbation lands near the motif (`61..63`, `65..67`).

This is distinct from both `rule_137` and `rule_54`: the system is not moving
between dense productive basins, and it is not primarily crossing the noise
gate. It is exposing the difference between background sensitivity and core
behavioral robustness.

## 6. Robust Families

The `frontera-rich-estable` family is the robust end of the atlas:

| world | f_total | f_core |
| --- | --- | --- |
| `rule_208` | 0.000 | 0.000 |
| `rule_209` | 0.000 | 0.000 |
| `rule_46` | 0.031 | 0.031 |

`rule_46` and `rule_209` are complement-related (`255 - 209 = 46`), while
`rule_208` is independent of that pair. The zero-fragility result for
`rule_208/209` suggests very wide basins for stable high-richness dynamics.

## 7. Physical Fragility Atlas Completion

Fase 22 completes fragility for every non-synthetic atlas world. The remaining
physical worlds were `rule_30`, `rule_150`, and the three Life fixtures:

| world | category | protocol | f_total | f_core | f_noise |
| --- | --- | --- | ---: | ---: | ---: |
| `rule_30` | noise-bounded | productive ECA pockets | 0.021 | 0.021 | 0.000 |
| `rule_150` | noise-bounded | productive ECA pockets | 0.023 | 0.023 | 0.000 |
| `life_block` | sin-evidencia-multiregimen | 2D one-cell flips | 0.016 | 0.016 | 0.000 |
| `life_glider` | sin-evidencia-multiregimen | 2D one-cell flips | 0.032 | 0.032 | 0.000 |
| `life_blinker` | sin-evidencia-multiregimen | 2D one-cell flips | 1.000 | 1.000 | 0.000 |

The synthetic controls remain `n/a`: they are frame generators rather than
dynamical systems evolved from a perturbable IC. This is a methodological
boundary, not missing data.

Two conclusions follow:

- The `noise-bounded` category is not intrinsically fragile inside its
  productive pockets. `rule_30` and `rule_150` have low conditional fragility;
  their category is defined by frequent pre-law noise at scale, not by
  instability of the non-empty signatures that survive the gate.
- `life_blinker` is the most signature-fragile control (`f_total = 1.000`):
  any one-cell perturbation breaks the exact period-2 fixture signature. This
  is fixture disruption, not basin switching or noise-boundary fragility.

## 8. Open Questions

### Resolved: Moving Local Oscillators

Fase moving oscillators (2026-06-11) tested the next protocol proposed after
the `rule_108` stationary-oscillator result.

Protocol:

- Rules: all `128` quiescent ECA rules (`f(0,0,0)=0`)
- ICs: `502` non-zero binary words of exact length `1..8`
- Width: `256`
- Steps: `300`
- Burn-in: `80`
- Detector: direct physical recurrence, not the ZAA observer/dedup/law pipeline

Result:

- `8` rules produce moving local oscillators:
  `rule_6`, `rule_20`, `rule_38`, `rule_52`, `rule_134`, `rule_148`,
  `rule_166`, `rule_180`.
- All witnesses have period `T=2`.
- All move with drift `|dx|=2` per period, i.e. velocity `1` cell/step, the
  maximum possible speed for radius-1 ECA.
- The minimal phase pattern is:

```text
[0] <-> [0, 1]
```

The rules form four mirror pairs:

| left-moving | right-moving |
| --- | --- |
| `rule_6` | `rule_20` |
| `rule_38` | `rule_52` |
| `rule_134` | `rule_148` |
| `rule_166` | `rule_180` |

The family is algebraically simple. The bits controlling neighborhoods `101`
and `111` (`b5` and `b7`) do not participate in the minimal traveling cycle,
so they parameterize variants of the same physical mechanism rather than eight
independent discoveries.

Comparison with Fase 18:

- Stationary local oscillator: unique rule, `rule_108`, with motif
  `#.# <-> ###`.
- Moving local oscillator: one minimal glider family across eight rules, with
  motif `[0] <-> [0,1]`.

Interpretation: moving local oscillators do exist in quiescent ECA under this
protocol, but only as a very small maximum-speed family. These rules are not
promoted into the canonical atlas because they have not passed the long-journal
ZAA protocol; they are documented as a direct physical sweep result.

### Extended IC sweep: length 9..12

A follow-up sweep extended both the stationary and moving oscillator searches
to IC words of length 9..12 (7,676 non-zero words per sweep), covering 982,528
rule/IC runs each.

Stationary: 3,802 detections, all in rule_108. No new stationary oscillator
rule beyond the length-1..8 baseline. Minimum witness is the embedded `101`
motif (`000000101` at length 9).

Moving: 2,059 detections, all in the same eight-rule family
(rule_6/20/38/52/134/148/166/180). No new moving oscillator rule. The sweep
also filtered 9,822 period-1 moving particle aliases across 32 rules.

Conclusion: IC words of length 1..8 are sufficient to discover the complete
zero-background oscillator landscape under this protocol up to seed length 12.
Extensions to IC length >12 remain open; the non-zero background extension is
reported below as a separate regime.

### Periodic-background oscillator sweep

A separate sweep replaced the quiescent zero background with 15 unique
non-zero periodic backgrounds (template lengths 1, 2, and 4) and tested all
256 ECA rules against 502 non-zero IC words (1,927,680 runs total). The
detector identifies local perturbations relative to the unperturbed background
orbit; global background periodicity alone does not count as a local
oscillator.

Stationary oscillators: 30 rules, of which 29 are new relative to the
zero-background baseline. Moving oscillators: 36 rules, of which 28 are new.

Key phenomena not present under zero background:

- Period-4 stationary oscillators: rule_54 and rule_147 under `0001`
  background.
- Period-4 moving oscillator: rule_180 with drift +4 under `0001` background
  (shapes `[0] -> [0,1] -> [0,2,3] -> [0]`), distinct from its T=2
  speed-1 glider under quiescent background.
- Speed-0.5 gliders: multiple rules (rule_3, rule_17, rule_27, rule_35,
  rule_39 and others) produce T=2 gliders with drift +/-1 under non-zero
  backgrounds. Under quiescent zero background the only observed speed was
  1 cell/step.
- rule_108 reappears under all-one background with the same motif ### / #.#,
  confirming the oscillator is intrinsic to the rule table, not a product of
  the zero-background condition.

Scientific reading: the zero-background and periodic-background regimes are
distinct. The zero-background uniqueness claims (rule_108 stationary, 8-rule
moving family) remain valid and are not contradicted. The periodic-background
sweep defines a separate background-conditioned oscillator landscape that is
substantially richer and includes period and speed classes absent from the
quiescent regime.

### Period-8 background oscillator sweep (Fase 24)

A further sweep extended the periodic-background protocol to length-8 primitive
binary backgrounds, testing whether longer background periods produce new
oscillator rules, longer periods T, or glider speeds outside the set observed
under backgrounds of length 1, 2, and 4.

Protocol:

- All 256 ECA rules.
- 30 primitive binary necklaces of length 8 (lexicographically minimal
  rotation, minimal period exactly 8). The count follows from Mobius inversion:
  `(1/8) * (2^8 - 2^4) = 30`.
- 502 non-zero IC words of length 1..8 per rule/background pair.
- Width 256, steps 300, burn-in 80. Period search 2..16, max span 32.
- Same differential detector as Fase 23: exact recurrence of localized
  difference from the unperturbed background orbit.
- Total: 3,855,360 runs. Elapsed: 1,343.8 s.

Result:

- Candidate detections: 323,872.
- Filtered period-1 aliases: 95,121.
- New stationary rules beyond the length-1/2/4 baseline: rule_62, rule_118,
  rule_131, rule_145 - 4 rules, all T=3.
- New moving rules: rule_7, rule_9, rule_21, rule_25, rule_31, rule_45, rule_61,
  rule_65, rule_67, rule_75, rule_87, rule_88, rule_89, rule_101, rule_103,
  rule_111, rule_125, rule_173, rule_229 - 19 rules.

New period classes not observed under shorter backgrounds:

- T=6, T=8, T=10, T=12, T=15. Under lengths 1/2/4 the maximum observed period
  was T=4.
- T=15 is a non-trivial period not divisible by the background length (8). No
  mechanism is inferred from the current data; it requires further
  investigation.

New glider speed:

- Speed 2/3 cell/step (drift +/-2, T=3). The observed speed set prior to this
  sweep was {0, 0.5, 1.0}; 2/3 is a new rational class with denominator 3.
- Observed in: rule_9 (drift -2, T=3, background `00001001`), rule_65
  (drift +2, T=3, background `00000001`), rule_111 (drift -2, T=3), and
  rule_125 (drift +2, T=3).
- Direct rule-table reflection, `g(l,c,r) = f(r,c,l)`, confirms two exact
  mirror pairs: rule_9 <-> rule_65 and rule_111 <-> rule_125. Each pair
  carries opposite drift signs with the same T=3 speed magnitude. The
  speed-2/3 family therefore has the same left/right mirror structure as the
  speed-1 family.

Background phase dependence:

A rotation sub-test sampled 10 rules and applied all 8 rotations of their
canonical background with the IC fixed. Results: 0/10 rotationally robust,
10/10 phase-dependent after circular-geometry correction. Representative
sensitivity levels:

- Near-robust (7/8 rotations active): rule_62 and rule_118
  (background `00000001`, T=3).
- Moving cases: rule_9 and rule_65 activate in 6/8 phases, rule_125 in 5/8,
  and rule_111 and rule_45 in 2/8.

This test varies background phase with the IC fixed. It measures alignment
sensitivity rather than pure translation. The original linear-shape observer
underestimated several moving-rule counts because cyclic boundary crossings
were rejected.

### Strict co-translation test (Fase 25)

Fase 25 co-translated both the periodic background and IC through `k=0..7` for
the same 10 cases (80 runs), preserving their relative alignment exactly.

Results:

- Background initial states: 80/80 exact translations.
- Full 301-frame background orbits: 80/80 exact translations.
- Initial XOR perturbations: 80/80 exact translations.
- Full 301-frame XOR perturbation orbits: 80/80 exact translations.
- Original `linear_shape` signature recovery: 58/80 runs, 5/10 cases.
- Failure mechanism: 22/22 misses are `cyclic_wrap_linearization`; localized
  moving differences straddle positions 255 and 0, producing a false linear
  span near 255.
- Circular shape canonicalization (cut at the largest empty arc and unwrap
  position continuously): 80/80 signatures, 10/10 cases.

Conclusion: the ECA physics and differential recurrence detector are
co-translation equivariant when cyclic geometry is represented correctly. The
observed failures are a boundary artifact of `linear_shape`, not a failure of
the simulator or physical phase relation. Reanalysis with circular geometry
confirms that background-phase dependence remains real, while its severity for
moving rules was overstated by the linear observer.

### T=15 anatomy (Fase 26)

Fase 26 filters all 221 `T=15` detections from the primitive length-8 sweep and
reruns one minimal witness for each of the 20 rule/background pairs.

The family is algebraically narrow:

- Only `rule_73` (123 detections) and `rule_109` (98 detections) participate.
- Both rules are left-right symmetric.
- They are exact black/white conjugates of one another.
- The 221 detections span 14 primitive backgrounds and 25 temporal motifs up
  to cycle phase.
- The minimum witness is `rule_109`, background `00011001`, IC `01`.

Every participating unperturbed background has temporal period `T_bg=3`.
The local oscillator therefore has a reproducible locking ratio
`T_local/T_bg = 15/3 = 5`; it is not a direct copy of the spatial template
length 8. Exact `T=15` recurrence persists through step 900 in all 20/20
minimal representatives, with period detection scanning upward from `T=1`.

The basin is narrow despite that temporal persistence:

- Fixed-IC background rotations preserve `T=15` in 23/160 runs.
- One-bit mutations of the minimal witnesses preserve `T=15` in 4/134 runs.
- Most alternatives fall into shorter periods `T=3` or `T=6`; a small number
  produce `T=12` or no localized period in the search window.

This establishes `T=15` as a persistent, background-locked oscillator family,
not a one-run accident. The rule-table derivation of the five-to-one locking
mechanism remains open.

### Five-state locking mechanism (Fase 27)

**Protocol.** Each of the 20 minimal `T=15` representatives from Fase 26 is
simulated at width 256. After burn-in, the localized XOR defect
`D(t) = X(t) XOR B(t)` is sampled at `t = 81 + 3k` for `k=0..20`, covering
four complete candidate five-cycles. Acceptance requires all eight checks:
the background returns to the exact same phase at every sample; the first five
defect states are mutually distinct; the fifth transition closes the cycle;
the minimal cycle under `F^3` has length five; four consecutive cycles repeat
in both canonical and raw-position encodings; transitions are deterministic
across cycles; and the oscillator is stationary over each local period.

**Results - 20/20 representatives (gate: positive).**

- Background returns to exact phase every 3 steps: 20/20.
- Five sampled defect states `S0..S4` are mutually distinct: 20/20.
- Minimal cycle under `F^3` has length five: 20/20.
- Four consecutive cycles are identical in canonical and raw encodings: 20/20.
- Deterministic transitions are consistent across cycles: 20/20.
- All 20 oscillators are stationary (`drift=0`).

**Established mechanism.** Each background period (`T_bg=3` steps) advances
the defect by exactly one node in a five-cycle under `F^3`. Five background
periods are necessary and sufficient to complete the defect cycle, yielding
`T_local = 5 * T_bg = 15`. The 5:1 ratio is therefore the cycle length of the
defect under `F^3`, not a coincidence of spatial parameters.

**Open.** The five defect states have not been reduced to a closed-form
symbolic identity from the rule-table algebra of `rule_73/rule_109`. The
finite-state mechanism is established computationally; its symbolic
derivation remains open.

**Script.** `outputs/periodic_backgrounds_len8/analyze_locking_mechanism.py`

**Outputs.** `locking_mechanism_results.jsonl`,
`locking_mechanism_report.md`.

### Induced defect rule and exact conjugation (Fase 28)

Fase 28 analyzes all 300 microsteps inside the 100 `F^3` edges from Fase 27.
The relevant local law is not the original ECA rule alone. For background
neighborhood `b` and XOR-defect neighborhood `d`, the defect obeys:

`delta_f(b,d) = f(b XOR d) XOR f(b)`.

**Analytical result.** Let `C` denote bitwise complementation. Since
`rule_109` is the black/white conjugate of `rule_73`,
`F_109(C(X)) = C(F_73(X))`. Simultaneously complementing the full state and
background therefore gives, by induction,
`X_109(t)=C(X_73(t))` and `B_109(t)=C(B_73(t))`. Hence:

`D_109(t) = C(X_73(t)) XOR C(B_73(t)) = D_73(t)`.

Equivalently,
`delta_109(C(b),d) = delta_73(b,d)`. This is an analytical identity, not an
empirical generalization. The script confirms all 64 local `(b,d)` cases and
10/10 complemented orbit pairs as implementation sanity checks.

**Rejected sparse-support hypothesis.** Every one of the 100 `F^3` edges uses
all eight ordinary rule entries in its causal defect cone. No single induced
`(b,d)` key appears in all 100 edges. Therefore, the five-cycle is not driven
by one fixed sparse subset of truth-table entries.

Non-trivial phase-specific intersections remain within each rule:

- `rule_73`: intersection sizes `[9, 6, 7, 5, 4]` for `S0->S1` through
  `S4->S0`.
- `rule_109`: intersection sizes `[11, 11, 10, 9, 8]`.

These signatures are rule-specific rather than universal. A future symbolic
derivation must encode spatial phase or a higher-order block state; entry
presence alone is insufficient.

**Script.** `outputs/periodic_backgrounds_len8/analyze_symbolic_locking.py`

**Outputs.** `symbolic_locking_results.json`,
`symbolic_locking_report.md`.

### Block-locality limits (Fase 29)

Fase 29 tests whether the T=15 five-state cycle can be described as either a
pure defect-only dynamic or a fixed ordered local block. The input is the same
20 minimal `rule_73/rule_109` representatives from Fase 27.

For each representative, the canonical XOR-defect shape is sampled at
`t = 81, 84, 87, 90, 93`. If the mechanism were background-independent, each
phase would have one shared shape per rule. Instead:

- `rule_73`: 8, 9, 9, 9, 9 distinct shapes across the five phases.
- `rule_109`: 8, 8, 8, 8, 8 distinct shapes across the five phases.

The ordered block scan uses the active defect span plus up to three padding
cells on each side. No nontrivial shared block signature exists in any phase
for either rule. The only exact shared length-1 tokens are trivial
background-context tokens of the form `d000->0` across all three microsteps.
The first divergence appears already at `W=0`, meaning the active defect span
itself carries background-specific context before any exterior padding is
added.

**Verdict.** `NO_LOCAL_BLOCK_DERIVATION`. The T=15 mechanism is not reducible
to one universal defect shape or one fixed local block signature. A derivation
must encode background spatial phase, a larger state variable, or both.

**Script.** `outputs/periodic_backgrounds_len8/analyze_phase_blocks.py`

**Outputs.** `phase_blocks_results.json`, `phase_blocks_report.md`.

### Background-indexed shape families (Fase 30)

Fase 30 asks whether the background dependence found in Fase 29 is arbitrary
or structured. Two five-state defect cycles are treated as equivalent if one
is a cyclic phase rotation of the other.

The 20 representatives collapse into a finite family map:

- `rule_73`: 7 phase-rotated shape families, largest family size 3.
- `rule_109`: 8 phase-rotated shape families, largest family size 3.
- Global after merging exact phase-rotated cycles across both rules:
  13 families.

Two families are shared across the conjugate rules. One has size 3
(two `rule_73` backgrounds and one `rule_109` background). A second has size 2:
background `00110101` produces phase-rotationally equivalent defect cycles
under both `rule_73` and `rule_109`. This is not a direct consequence of the
black/white conjugation identity from Fase 28, because the bitwise complement
of `00110101` is `11001010`, a distinct word.

Simple background descriptors do not determine the shape family:
`active_count`, `transition_count`, and `active_transition_pair` all leave
ambiguous buckets. The canonical temporal orbit of the background under the
same rule is exact in the representative set, but this mostly restates the
full background orbit rather than giving a compact symbolic law.

**Verdict.** `PARTIAL_POSITIVE`. The T=15 cycle is not one universal defect
cycle, but neither is it arbitrary. The correct symbolic target is now sharper:
map the temporal background orbit and IC alignment to one of 13 finite
defect-cycle families plus a phase offset.

**Script.** `outputs/periodic_backgrounds_len8/analyze_shape_families.py`

**Outputs.** `shape_families_results.json`, `shape_families_report.md`.

### Compact descriptor search (Fase 31)

Fase 31 searches for a shorter descriptor of the T=15 shape family than the
full temporal background orbit. The test uses the 20 representatives and 13
shape families from Fase 30.

Background-only descriptors tested:

- circular subpattern multisets of length 2, 3, and 4;
- parity;
- circular run lengths;
- run count;
- first-one position;
- temporal orbit prefixes of length 8, 16, and 24.

No compact background-only descriptor determines the 13 global families.
`orbit_prefix_24` does determine the family, but it is effectively the full
background orbit rather than a compact law. A global decision tree over all
numeric features achieves only 0.700 training accuracy at depth 4.

Conditioned on the ECA rule, however, several descriptors separate the
families. The shortest non-orbit candidate is:

`rule + subpatterns_len4`.

That descriptor means: rule identity plus the circular multiset of length-4
background subwords. It separates all 10 backgrounds per rule into unambiguous
shape-family buckets in the confirmed representative set.

**Verdict.** `COMPACT_DESCRIPTOR_FOUND`, but only as a rule-conditioned
candidate. It is not a global background-only law.

**Script.** `outputs/periodic_backgrounds_len8/analyze_compact_descriptor.py`

**Outputs.** `compact_descriptor_results.json`,
`compact_descriptor_report.md`.

### Rotation generalization of compact descriptor (Fase 32)

Fase 32 tests the key falsifiable prediction of `rule + subpatterns_len4`.
Because the length-4 circular subpattern multiset is invariant under rotation
of the background word, every non-trivial background rotation should preserve
the predicted shape family if the local IC/background alignment is also
preserved.

For each of the 20 minimal representatives, all seven non-trivial background
rotations are tested in two modes:

- `fixed_ic`: background rotated, IC position fixed;
- `cotranslated_ic`: background rotated and IC placement shifted by the same
  amount, preserving local alignment.

Results:

- `fixed_ic`: 3/140 rotations produce T=15; 1/140 matches the predicted family.
- `cotranslated_ic`: 140/140 rotations produce T=15; 140/140 match the
  predicted family.

**Verdict.** `ALIGNMENT_CONDITIONED_DESCRIPTOR_CONFIRMED`. The compact state
variable is not background alone. It is the triple:

`(rule, subpatterns_len4, IC/background alignment)`.

The result is a rotation-equivariance validation on known representatives and
their rotations, not a prediction over new backgrounds. It establishes that
IC/background alignment is a physical state variable: without it, the descriptor
fails almost completely.

**Script.** `outputs/periodic_backgrounds_len8/test_rotation_generalization.py`

**Outputs.** `rotation_generalization_results.jsonl`,
`rotation_generalization_report.md`.

Scientific reading: period-8 primitive backgrounds enlarge the oscillator
landscape relative to shorter backgrounds. The three Fase-24 questions are
answered affirmatively: new rules appear, new periods T>4 include T=15, and a
new glider speed class (2/3 cell/step) appears. The zero-background uniqueness
claims (rule_108 stationary, 8-rule moving family) are unaffected.

1. **Symbolic formulas**  
   The physical tree has strong empirical signal, but PySR/Julia remains a
   technical blocker. The current robust conclusion is a family map, not one
   universal equation.

2. **Observer translation equivariance**  
   Fase 19 shows that ECA dynamics remain translation-invariant while the
   current observer/dedup counts do not for wide-spreading `rule_54` patterns.
   This does not affect the law signature in the controlled case, but it is a
   known limitation if future work uses absolute counts as physical evidence.

## 9. Bottom Line

The current atlas is no longer just a list of laws by world. It is a structured
map with:

- world families,
- law coverage,
- basin fragility,
- core fragility,
- and distinct mechanisms of high fragility.

The most important conceptual update is that law signatures are not all equal:
some laws define a regime, while others are secondary descriptors. `f_core`
captures that difference.
