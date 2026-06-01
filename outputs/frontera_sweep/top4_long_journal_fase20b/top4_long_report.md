# Top-4 Frontera Long Journal - Fase 20b

## Setup

- Worlds: `rule_84, rule_138, rule_212, rule_213`
- Cycles: `160`
- Initial steps: `24`
- Width: `64`
- Base seed: `20260610`
- Journal: `outputs/frontera_sweep/top4_long_journal_fase20b/journal_top4_long.jsonl`
- State: `outputs/frontera_sweep/top4_long_journal_fase20b/agent_state_top4_long.json`

The script runs the normal ZUSE discovery loop with a local four-world
`WORLD_SEQUENCE` override. No production code or atlas sequence is modified.

## Classification Summary

| classification | count |
| --- | --- |
| noise-bounded | 1 |
| sin-evidencia-multiregimen | 3 |

## World Summary

| world | classification | visits | non_empty_ratio | noise_ratio | peak_diversity | mean_laws | mean_steps | max_steps | dominant_signature |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rule_84 | sin-evidencia-multiregimen | 40 | 0.700 | 0.300 | 0.143 | 3.125 | 168.150 | 192 | velocidad_constante + densidad_estable + complejidad_alta + temporal_scale_stability |
| rule_138 | noise-bounded | 41 | 0.439 | 0.561 | 0.167 | 2.561 | 166.146 | 192 | velocidad_constante + densidad_estable + tipo_unico + complejidad_alta + frontera_temporal + temporal_scale_stability |
| rule_212 | sin-evidencia-multiregimen | 40 | 0.700 | 0.300 | 0.143 | 3.300 | 170.425 | 192 | velocidad_constante + densidad_estable + complejidad_alta + temporal_scale_stability |
| rule_213 | sin-evidencia-multiregimen | 39 | 0.692 | 0.308 | 0.148 | 3.000 | 176.615 | 192 | velocidad_constante + densidad_estable + complejidad_alta + temporal_scale_stability |

## Law Frequency Rates

Rates are computed over non-empty visits.

| world | velocidad_constante | periodicidad | densidad_estable | tipo_unico | complejidad_alta | frontera_temporal | temporal_scale_stability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule_84 | 1.000 | 0.000 | 1.000 | 0.214 | 1.000 | 0.250 | 1.000 |
| rule_138 | 1.000 | 0.000 | 1.000 | 0.944 | 0.944 | 0.944 | 1.000 |
| rule_212 | 1.000 | 0.000 | 1.000 | 0.250 | 1.000 | 0.464 | 1.000 |
| rule_213 | 1.000 | 0.000 | 1.000 | 0.111 | 1.000 | 0.222 | 1.000 |

## Interpretation

The top candidates do **not** remain `frontera-rich-estable` under the independent long-journal policy run.

This upgrades the Fase 20a result from a fixed six-seed profile to an
independent policy-run check for the four strongest additional candidates.
The fixed `steps=24` profile should be treated as a frontera filter, not as atlas-grade stability evidence. These four worlds should not be promoted to the canonical atlas without a scale-aware category or additional controlled protocol.
