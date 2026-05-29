# World Taxonomy and Law Map

Source journal: `outputs/experiments_2026-05-27/journal_8c_long.jsonl`

Additional formal profiles: `outputs/frontera_sweep/top_rules_profile.json`
when present.

Schema check: world field detected as `world_type`. First-row keys include:
`action_reason, action_taken, analysis_status, consensus, cycle_id, dedup_structure_count, details, dominant_type, inflation_ratio, is_new_law_signature, law_signature, laws_accepted, laws_evaluated, laws_rejected, laws_status, metrics, scale_attempt_count, score, steps, structure_count, timestamp, width, world_avg_score_prev, world_has_multiregime_evidence_prev, world_is_multiregime_candidate_prev, world_peak_diversity_prev, world_score_variance_prev, world_signature_diversity_prev, world_type, world_unique_signatures_prev, world_visit_count`.

## Taxonomy

This taxonomy separates four mechanisms that looked similar before Fase 8:

- **multi-regimen-productivo**: the world has real law-signature diversity and
  most visits produce at least one accepted law.
- **multi-regimen-escala-dependiente**: the world has real non-empty signature
  diversity, but most visits are silent at the explored scale.
- **frontera-rich-estable**: the world has low signature diversity but high
  stable law richness (`mean_laws >= 4.0`).
- **noise-bounded**: the world fails before law evaluation at high scale because
  `analysis_status == "ruido_no_analizable"`.
- **sin-evidencia-multiregimen**: no sufficient evidence of multi-regime behavior
  in this journal.

Mechanical distinction:

- `rule_90` style silence is post-analysis: `analysis_ok=True`, structures exist,
  but `laws_accepted=[]`.
- `rule_150` style failure is pre-analysis: the deduplicated structure gate marks
  the cycle as `ruido_no_analizable`, so laws are not evaluated.

Thresholds used:

- `DIVERSITY_THRESHOLD = 0.5`
- `NON_EMPTY_RATIO_THRESHOLD = 0.5`
- `NOISE_RATIO_THRESHOLD = 0.5`
- `RICH_LAWS_THRESHOLD = 4.0`

Classification function:

```python
def classify_world(stats):
    if stats['total_visits'] == 0:
        return "sin-datos"
    noise_ratio = stats['noise_visits'] / stats['total_visits']
    if noise_ratio > NOISE_RATIO_THRESHOLD:
        return "noise-bounded"
    if stats['peak_diversity'] is not None and stats['peak_diversity'] > DIVERSITY_THRESHOLD:
        if stats['non_empty_ratio'] < NON_EMPTY_RATIO_THRESHOLD:
            return "multiregimen-escala-dependiente"
        else:
            return "multiregimen-productivo"
    if stats['mean_laws'] >= RICH_LAWS_THRESHOLD:
        return "frontera-rich-estable"
    return "sin-evidencia-multiregimen"
```

## World Classification Table

| world | eca_class | category | total_visits | non_empty_ratio | noise_ratio | peak_diversity | mean_laws | dominant_signature | fragility_total | fragility_pattern |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| life_blinker | unknown | sin-evidencia-multiregimen | 18 | 1.000 | 0.000 | 0.200 | 3.000 | periodicidad + densidad_estable + tipo_unico | ? | ? |
| life_block | unknown | sin-evidencia-multiregimen | 12 | 1.000 | 0.000 | 0.200 | 2.000 | densidad_estable + tipo_unico | ? | ? |
| life_glider | unknown | sin-evidencia-multiregimen | 14 | 1.000 | 0.000 | 0.333 | 2.357 | densidad_estable + tipo_unico | ? | ? |
| rule_109 | class-4 | multiregimen-productivo | 15 | 0.667 | 0.333 | 0.667 | 2.000 | densidad_estable + complejidad_alta + frontera_temporal | 0.250 | clustered |
| rule_110 | class-4 | multiregimen-productivo | 11 | 0.636 | 0.364 | 0.600 | 2.727 | velocidad_constante + densidad_estable + complejidad_alta + frontera_temporal | ? | ? |
| rule_124 | unknown | multiregimen-productivo | 12 | 0.583 | 0.417 | 0.600 | 2.167 | densidad_estable + complejidad_alta + frontera_temporal + temporal_scale_stability | ? | ? |
| rule_137 | class-4 | multiregimen-productivo | 15 | 0.800 | 0.200 | 0.833 | 2.867 | densidad_estable + complejidad_alta + frontera_temporal | 0.630 | dispersed |
| rule_150 | class-3 (additive) | noise-bounded | 8 | 0.250 | 0.750 | 0.000 | 0.750 | densidad_estable + complejidad_alta + temporal_scale_stability | ? | ? |
| rule_18 | class-3 (moving wave fronts) | multiregimen-productivo | 13 | 0.769 | 0.231 | 0.800 | 2.308 | velocidad_constante + tipo_unico + temporal_scale_stability | 0.349 | clustered |
| rule_208 | unknown | frontera-rich-estable | 6 | 1.000 | 0.000 | 0.167 | 6.000 | velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability | 0.000 | dispersed |
| rule_209 | unknown | frontera-rich-estable | 6 | 1.000 | 0.000 | 0.167 | 6.000 | velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability | 0.000 | dispersed |
| rule_30 | class-3 (chaotic) | noise-bounded | 10 | 0.400 | 0.600 | 0.000 | 1.100 | densidad_estable + complejidad_alta + temporal_scale_stability | ? | ? |
| rule_46 | unknown | frontera-rich-estable | 6 | 1.000 | 0.000 | 0.333 | 5.833 | velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability | 0.031 | dispersed |
| rule_54 | class-4 | multiregimen-productivo | 12 | 0.667 | 0.333 | 0.800 | 1.917 | complejidad_alta + temporal_scale_stability | ? | ? |
| rule_90 | class-3 (additive/XOR) | multiregimen-escala-dependiente | 14 | 0.357 | 0.000 | 0.600 | 0.500 | temporal_scale_stability | 0.172 | clustered |
| synthetic_bloque | unknown | sin-evidencia-multiregimen | 14 | 1.000 | 0.000 | 0.200 | 2.000 | densidad_estable + tipo_unico | ? | ? |
| synthetic_glider | unknown | sin-evidencia-multiregimen | 18 | 1.000 | 0.000 | 0.400 | 3.167 | velocidad_constante + densidad_estable + tipo_unico | ? | ? |
| synthetic_oscilador | unknown | sin-evidencia-multiregimen | 14 | 1.000 | 0.000 | 0.400 | 2.286 | periodicidad + tipo_unico | ? | ? |

## Law Coverage Matrix

Law columns:

- `vel` = `velocidad_constante`
- `per` = `periodicidad`
- `den` = `densidad_estable`
- `tipo` = `tipo_unico`
- `compl` = `complejidad_alta`
- `front` = `frontera_temporal`
- `tss` = `temporal_scale_stability`

Cell states:

- `✓`: law appears in the dominant signature or in at least 50% of non-empty visits.
- `·`: law appears in at least one non-empty visit but in less than 50%.
- `-`: non-empty visits exist and the law never appears.
- `?`: no non-empty visits.

| world | vel | per | den | tipo | compl | front | tss |
| --- | --- | --- | --- | --- | --- | --- | --- |
| life_blinker | - | ✓ | ✓ | ✓ | - | - | - |
| life_block | - | - | ✓ | ✓ | - | - | - |
| life_glider | · | - | ✓ | ✓ | - | - | - |
| rule_109 | - | - | ✓ | · | ✓ | ✓ | ✓ |
| rule_110 | ✓ | - | ✓ | - | ✓ | ✓ | · |
| rule_124 | · | - | ✓ | - | ✓ | ✓ | ✓ |
| rule_137 | · | - | ✓ | · | ✓ | ✓ | ✓ |
| rule_150 | - | - | ✓ | - | ✓ | - | ✓ |
| rule_18 | ✓ | - | - | ✓ | ✓ | - | ✓ |
| rule_208 | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| rule_209 | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| rule_30 | - | - | ✓ | - | ✓ | - | ✓ |
| rule_46 | ✓ | - | ✓ | ✓ | ✓ | ✓ | ✓ |
| rule_54 | ✓ | - | · | · | ✓ | - | ✓ |
| rule_90 | · | - | · | - | · | - | ✓ |
| synthetic_bloque | - | - | ✓ | ✓ | - | - | - |
| synthetic_glider | ✓ | - | ✓ | ✓ | - | - | · |
| synthetic_oscilador | - | ✓ | - | ✓ | - | - | · |

## Notable World Profiles

### rule_18 — multi-régimen productivo (class-3 moving structures)

Formal map protocol: `steps=24`, `width=64`, seeds `20260523..20260528`.
Result: `6/6 ok`, deduplicated structures `8..13`, temporal load about
`7.2..7.55`, and high transition rate about `0.52..0.57`.

Core laws:

- `complejidad_alta`: `6/6`
- `temporal_scale_stability`: `6/6`
- `velocidad_constante`: `5/6`
- `tipo_unico`: `4/6`

Dominant formal signature:
`velocidad_constante + tipo_unico + complejidad_alta + temporal_scale_stability`
in `4/6` seeds.

Interpretation: rule_18 is an alternate route to law richness, not the same
class-4 route as rule_110/rule_137. It combines stable temporal scale with
moving, relatively homogeneous wave-front structures.

### rule_90 — multi-régimen escala-dependiente (XOR/additive)

In the 200-cycle post-8c journal, rule_90 has `analysis_status == ok` in all
visits and reaches `steps=400`, but high-scale visits are mostly silent:
structures exist, the analysis runs, and `laws_accepted=[]`.

This is post-analysis silence, not noise. The agent should not spend
multi-regime repeats on silent cycles, and Fase 8c enforces that.

Interpretation: rule_90 has real early non-empty signatures, but the additive
XOR dynamics become too regular or too algebraic for the current seven laws at
high scale.

### rule_150 — noise-bounded (additive)

rule_150 produces a stable non-empty signature at low scale:
`densidad_estable + complejidad_alta + temporal_scale_stability`.

At higher scale it crosses the deduplicated structure gate and becomes
`ruido_no_analizable`. This is pre-analysis failure, unlike rule_90. The agent
handles it by changing world once the noise boundary is observed.
