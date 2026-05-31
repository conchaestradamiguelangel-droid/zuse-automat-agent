# Rule 54 Controlled Single-Bit IC - Fase 19

## Setup

- Rule: `rule_54`
- Width: `64`
- Steps: `96`
- ICs: one active bit at each position `k=0..63`
- Boundary conditions: periodic, inherited from `zaa.eca.simulate`
- Noise gate: `dedup_structure_count > 40`

With strict periodic boundary conditions, all 64 ICs are translations of each
other. Therefore all comparable pipeline outputs should be identical.

## Translation-Invariance Check

ECA frame dynamics translation-invariant: `True`.

The 64 positions split into 29 result classes. Because the ECA frame dynamics are translation-invariant, this is an observer/dedup pipeline artifact rather than a CA boundary-condition issue.

- Unique result classes: `29`
- Dedup counts observed: `[15, 16, 17, 18, 19, 20, 21, 22, 24]`
- Raw counts observed: `[45, 48, 51, 54, 57, 60, 63, 66, 72]`
- Law signatures observed: `['temporal_scale_stability']`

Baseline result:

- `analysis_status`: `ok`
- `dedup_structure_count`: `20`
- `raw_structure_count`: `60`
- `laws_accepted`: `temporal_scale_stability`
- `dominant_type`: `glider`
- `max_cyclic_active_span`: `63`
- `final_cyclic_active_span`: `61`
- `max_active_count`: `48`
- `final_active_count`: `16`

## Per-Position Table

| k | dedup | raw | status | laws | max_cyclic_span | final_cyclic_span | max_active_count | final_active_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 20 | 60 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 1 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 2 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 3 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 4 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 5 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 6 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 7 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 8 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 9 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 10 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 11 | 16 | 48 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 12 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 13 | 16 | 48 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 14 | 18 | 54 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 15 | 19 | 57 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 16 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 17 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 18 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 19 | 16 | 48 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 20 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 21 | 16 | 48 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 22 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 23 | 18 | 54 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 24 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 25 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 26 | 16 | 48 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 27 | 16 | 48 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 28 | 16 | 48 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 29 | 16 | 48 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 30 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 31 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 32 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 33 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 34 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 35 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 36 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 37 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 38 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 39 | 18 | 54 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 40 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 41 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 42 | 18 | 54 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 43 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 44 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 45 | 17 | 51 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 46 | 20 | 60 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 47 | 22 | 66 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 48 | 20 | 60 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 49 | 20 | 60 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 50 | 20 | 60 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 51 | 19 | 57 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 52 | 19 | 57 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 53 | 19 | 57 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 54 | 22 | 66 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 55 | 24 | 72 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 56 | 22 | 66 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 57 | 22 | 66 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 58 | 21 | 63 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 59 | 22 | 66 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 60 | 20 | 60 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 61 | 20 | 60 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 62 | 15 | 45 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |
| 63 | 20 | 60 | ok | temporal_scale_stability | 63 | 61 | 48 | 16 |

## Comparison With Fase 13

Fase 13 complex-IC reference dedup counts: `{'20260638@96': 32, '20260640@96': 33, '20260642@96': 39}`. Noise flips by seed: `{20260638: 14, 20260640: 18, 20260642: 40}`.

The controlled single-bit IC produces `dedup_structure_count =
20`, far below the noise threshold of
`40`. Therefore the Fase 13 noise-gate crossing
requires complex random IC geometry; a single active cell is not enough to
approach the gate.

## Interpretation

The bit-5 universality observed in Fase 13 is not an intrinsic absolute
coordinate of `rule_54`: the ECA frames themselves are translation-invariant
under the single-bit protocol. However, the current observer/dedup pipeline is
not translation-equivariant for this wide-spreading pattern: it returns
deduplicated counts from `15` to `24` depending on where the same translated
pattern crosses the linear frame boundary.

This means Fase 13's bit-5 result should be interpreted as interaction between
the complex IC geometry and the observer/gate pipeline, not as a special cell
coordinate in the CA rule. The law signature is stable (`temporal_scale_stability`
for all 64 positions), and every single-bit IC stays far below the noise gate.
