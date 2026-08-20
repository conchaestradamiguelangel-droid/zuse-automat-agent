# Fase 108 — Atlas condicionado de mecanismos de rescate

**Veredicto:** `CONDITIONED_MINIMAL_RESCUE_MECHANISM_ATLAS_VERIFIED`

- Rescates certificados: 1.476
- Instancias: 265
- Mecanismo externo: 931
- Dependencia de arista interna: 545
- Discrepancias entre `mechanism_label` e `internal_edge_required`: 0

## Catálogo exacto

| Motivo | n | Aristas | Externo | Interno | Clasificación |
|---|---:|---:|---:|---:|---|
| 2I | 2 | 0 | 701 | 0 | LOGICALLY_FORCED |
| K2 | 2 | 1 | 54 | 169 | EMPIRICALLY_VARIABLE |
| 3I | 3 | 0 | 154 | 0 | LOGICALLY_FORCED |
| K2+I | 3 | 1 | 22 | 74 | EMPIRICALLY_VARIABLE |
| P3 | 3 | 2 | 0 | 122 | OBSERVED_COMPLETE_SEPARATION |
| 4I | 4 | 0 | 0 | 0 | ZERO_OBSERVED |
| K2+2I | 4 | 1 | 0 | 35 | OBSERVED_COMPLETE_SEPARATION |
| 2K2 | 4 | 2 | 0 | 48 | OBSERVED_COMPLETE_SEPARATION |
| P3+I | 4 | 2 | 0 | 67 | OBSERVED_COMPLETE_SEPARATION |
| P4 | 4 | 3 | 0 | 30 | OBSERVED_COMPLETE_SEPARATION |
| K1_3 | 4 | 3 | 0 | 0 | ZERO_OBSERVED |
| C4 | 4 | 4 | 0 | 0 | ZERO_OBSERVED |

## Estratos con variación empírica

### K2

- kappa: 83/107 internos (0.775701); 48 instancias.
- lambda: 86/116 internos (0.741379); 53 instancias.
- Diferencia de proporciones lambda−kappa: -0.034322.
- Odds ratio lambda/kappa: 0.828916.
- `node_count`, EXTERNAL_ATTACHMENT_RESCUE: n=54, mín=77, mediana=127.0, máx=149, media=120.185185.
- `node_count`, INTERNAL_EDGE_DEPENDENT_RESCUE: n=169, mín=26, mediana=109, máx=149, media=94.781065.

### K2+I

- kappa: 34/44 internos (0.772727); 22 instancias.
- lambda: 40/52 internos (0.769231); 28 instancias.
- Diferencia de proporciones lambda−kappa: -0.003497.
- Odds ratio lambda/kappa: 0.980392.
- `node_count`, EXTERNAL_ATTACHMENT_RESCUE: n=22, mín=95, mediana=95.0, máx=102, media=96.909091.
- `node_count`, INTERNAL_EDGE_DEPENDENT_RESCUE: n=74, mín=8, mediana=74.0, máx=103, media=61.054054.

## Análisis secundario de cortes

- Cortes críticos: 3.784
- `INDIVIDUAL`: 2.365
- `DISTRIBUTED_EXTERNAL`: 498
- `INTERNAL_EDGE_ENABLED`: 921
- Rescates con varias categorías de corte: 223

## Límite de interpretación

Los ceros estructurales no se interpretan como hallazgos estadísticos. Las diferencias son descriptivas del censo certificado y no implican causalidad ni generalización poblacional. No se usaron modelos QUBO, solvers ni hardware cuántico.
