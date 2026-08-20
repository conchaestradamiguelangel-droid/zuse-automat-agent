# Fase 109 — Geometría ambiental de rescates

**Veredicto:** `AMBIENT_GEOMETRY_CONDITIONED_RESCUE_ANALYSIS_VERIFIED`

## Auditoría de fuentes

- Pares del ledger: 404.054
- Strata reconstruidos: 142
- Rescates K2/K2+I: 319
- Discrepancias `V_i` frente a `node_count`: 0
- Discrepancias `V_i` frente a `x_words`: 0
- Fallos de invariancia al orden: 0

## Resultado principal K2

- Instancias mixtas: 24
- Variable principal: `S_ext`.
- Media de Delta_i: -1.220833
- Mediana de Delta_i: -0.500000
- Rango de Delta_i: [-3.500000, 0.500000]
- Signos de Delta_i: 2 positivos, 0 nulos, 22 negativos.
- Estabilidad leave-one-instance-out de la media: [-1.295652, -1.121739]

### Distribución completa de S_ext en K2

- EXTERNAL_ATTACHMENT_RESCUE: n=54, media=5.370370, mediana=5.000000, rango=[3, 8].
- INTERNAL_EDGE_DEPENDENT_RESCUE: n=169, media=5.810651, mediana=6.000000, rango=[1, 10].

### Variables secundarias K2

- `M_ext`: media Delta_i=-0.487500, mediana=-0.500000; 2 positivos, 4 nulos, 18 negativos.
- `B_ext`: media Delta_i=-0.245833, mediana=-0.450000; 10 positivos, 0 nulos, 14 negativos.

## K2+I descriptivo

- Instancias mixtas: 4
- Rescates en esas instancias: 28
- Se reportan por separado `S_ext_all`, `S_ext_edge` y `d_ext_isolated`; no sostienen inferencia propia.

| Variable | Mecanismo | n | Media | Mediana | Rango |
|---|---|---:|---:|---:|---|
| S_ext_all | EXTERNAL_ATTACHMENT_RESCUE | 6 | 9.333333 | 9.000000 | [9, 10] |
| S_ext_all | INTERNAL_EDGE_DEPENDENT_RESCUE | 22 | 7.909091 | 9.000000 | [5, 10] |
| S_ext_edge | EXTERNAL_ATTACHMENT_RESCUE | 6 | 7.333333 | 7.000000 | [7, 8] |
| S_ext_edge | INTERNAL_EDGE_DEPENDENT_RESCUE | 22 | 5.909091 | 7.000000 | [3, 8] |
| d_ext_isolated | EXTERNAL_ATTACHMENT_RESCUE | 6 | 2.000000 | 2.000000 | [2, 2] |
| d_ext_isolated | INTERNAL_EDGE_DEPENDENT_RESCUE | 22 | 2.000000 | 2.000000 | [2, 2] |

## Descripción entre instancias

`period` se conserva únicamente como procedencia y no se usa como covariable.

| Motivo | Regla | Métrica | Instancias | node_count medio | Proporción interna media por instancia | Externos | Internos |
|---|---:|---|---:|---:|---:|---:|---:|
| K2 | 73 | kappa | 16 | 71.750000 | 0.888393 | 8 | 27 |
| K2 | 73 | lambda | 21 | 79.761905 | 0.716553 | 13 | 32 |
| K2 | 109 | kappa | 32 | 83.437500 | 0.877976 | 16 | 56 |
| K2 | 109 | lambda | 32 | 76.593750 | 0.872768 | 17 | 54 |
| K2+I | 73 | kappa | 10 | 58.000000 | 0.783333 | 5 | 15 |
| K2+I | 73 | lambda | 12 | 53.666667 | 0.812500 | 6 | 18 |
| K2+I | 109 | kappa | 12 | 56.083333 | 0.819444 | 5 | 19 |
| K2+I | 109 | lambda | 16 | 53.687500 | 0.859375 | 6 | 22 |

## Límites

El análisis caracteriza el censo certificado. No separa un efecto de periodo frente a `node_count`, no formula causalidad y no generaliza fuera de los datos. Los modelos QUBO se usaron únicamente para comprobar `x_words`; no se analizaron sus coeficientes.
