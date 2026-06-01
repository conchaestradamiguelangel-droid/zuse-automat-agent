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
| `rule_109` | `multiregimen-productivo` | 0.250 | 0.250 | core changes match total changes |
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
| `rule_109` | `multiregimen-productivo` | 0.250 | 0.000 | clustered |
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

## 7. Open Questions

1. **Symbolic formulas**  
   The physical tree has strong empirical signal, but PySR/Julia remains a
   technical blocker. The current robust conclusion is a family map, not one
   universal equation.

2. **Observer translation equivariance**  
   Fase 19 shows that ECA dynamics remain translation-invariant while the
   current observer/dedup counts do not for wide-spreading `rule_54` patterns.
   This does not affect the law signature in the controlled case, but it is a
   known limitation if future work uses absolute counts as physical evidence.

## 8. Bottom Line

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
