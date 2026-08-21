# Fase 111 — Predeclaración aprobada

## Estado y gobernanza

- Estado: aprobada metodológicamente tras auditoría independiente de Claude Code y ajuste final de Codex.
- Fecha de cierre metodológico: 2026-08-21.
- Base: Fase 110 cerrada y publicada en `efc9aa4`.
- La versión publicada v1.37 permanece inmutable en `cdfcb13`.
- Los artefactos usarán el prefijo histórico `phase110_*`, pero declararán `phase: 111`.
- Solo se permiten pruebas dirigidas al cambio actual. La suite global queda prohibida salvo autorización explícita de Miguel.
- No se ejecutarán barridos, simulaciones, QUBO, solvers ni hardware cuántico.
- No se afirma validación externa o prospectiva ni sustitución del auditor exacto.

## Título

Potencial clasificatorio interno de `A_G` para el mecanismo de rescate `K2`, evaluado mediante validación agrupada leave-one-instance-out.

## Pregunta científica

¿Puede `A_G`, calculada geométricamente antes de cualquier análisis de mecanismo, actuar como clasificador de umbral único reproducible de `EXTERNAL_ATTACHMENT_RESCUE` frente a `INTERNAL_EDGE_DEPENDENT_RESCUE`, evaluado en instancias no usadas para ajustar ese umbral?

## Límite metodológico esencial

`A_G`, su dirección y parte de su separación por clase ya se observaron durante el diseño de Fase 110 y la auditoría previa. La validación leave-one-instance-out (`LOIO`) no constituye una validación predictiva independiente: el umbral se reajusta sin la instancia de prueba en cada fold, pero la elección de `A_G` como característica se hizo viendo el mismo censo que ahora se evalúa.

El resultado permitido es una caracterización interna, agrupada y reproducible del potencial clasificatorio de `A_G`. Nunca será una estimación no sesgada del rendimiento futuro ni autorizará sustituir las auditorías exactas de corte de Fases 96–107.

La salida fijará explícitamente:

- `outcome_data_seen_during_feature_design: true`;
- `feature_selection_nested_within_loio: false`;
- `external_validation: false`;
- `prospective_validation: false`;
- `causal_claim: false`;
- `population_generalization: false`.

## Fuentes cerradas

1. `phase105_minimal_rescue_motif_results.json`
   - raw: `9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24`
   - canonical: `982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353`
   - Fuente de identidad y `mechanism_label` en `mechanism_audits`, solo para `K2`.
2. `phase109_fixed_budget_hamming_partition_results.json`
   - raw: `ba5cf94330ce5c27c6b7c4420f910c637debac1273b9b25d3ad4fd787c141d04`
   - canonical: `dcf3d5847af14b3128e88dac765e491900340ddf4587b50281f42ac8ade147b1`
   - Fuente certificada de las 223 filas de `supplementary_full_census_pairs` y de `A_G`.

`A_G` se leerá directamente de Fase 110 y no se recalculará. No se leerán directamente Fases 94, 95, 96, 102 ni 108: `G_min` y `V_i` ya fueron consumidos y certificados por Fase 110.

## Claves de unión

- Identidad del rescate: `instance_key + words`, con palabras canónicas ascendentes.
- Identidad de instancia para `LOIO`: `instance_key` completo (`cube_key + pair_index + period + metric`).

Toda unión debe ser única y completa. Una ausencia o duplicidad abortará la ejecución.

## Universo

- 223 rescates `K2`, agrupados en 101 instancias.
- 6 instancias solo externas, 71 solo internas y 24 mixtas.
- Se usa el censo completo. La partición de 14 incidencias y la disyunción `V_i ∩ G_min = ∅` fueron verificadas sin fallos en las 101 instancias durante la auditoría previa.

## Predictora y respuesta

- Predictora única: `A_G(H)`, leída sin transformación ni normalización de la segunda fuente.
- Respuesta: `mechanism_label`, leída de la primera fuente y comprobada contra la segunda para cada rescate.

## Validación leave-one-instance-out

Se ejecutarán 101 folds. Cada fold excluye una instancia completa, aprende el umbral exclusivamente con las otras 100 y conserva todas las predicciones de la instancia excluida.

### Peso de entrenamiento

En un fold con `N=100` instancias de entrenamiento, cada rescate `j` de la instancia `i`, que contiene `n_i` rescates, recibe el peso exacto:

```text
w_ij = 1 / (N * n_i)
```

Cada instancia de entrenamiento aporta peso total `1/N`. Los pesos, sensibilidades, balanced accuracy y desempates se calcularán con aritmética racional exacta (`fractions.Fraction`); los decimales serán únicamente representaciones de salida.

### Umbrales y selección

Los candidatos son `t ∈ {3,4,5,6,7,8,9}`. Se predice `EXTERNAL` si `A_G >= t` e `INTERNAL` en caso contrario.

Para cada candidato se calcularán en entrenamiento:

```text
Sens_EXT,w(t) = aciertos EXTERNAL ponderados / EXTERNAL ponderados
Sens_INT,w(t) = aciertos INTERNAL ponderados / INTERNAL ponderados
BA_w(t) = (Sens_EXT,w(t) + Sens_INT,w(t)) / 2
```

Se maximiza `BA_w`. Los empates se resuelven, en este orden exacto:

1. maximizar `min(Sens_EXT,w, Sens_INT,w)`;
2. minimizar `|Sens_EXT,w - Sens_INT,w|`;
3. elegir el menor umbral numérico.

No habrá ajustes posteriores al umbral elegido.

## Baseline obligatorio

En cada fold, el baseline predice la clase mayoritaria de las 100 instancias de entrenamiento bajo los mismos pesos igual-por-instancia. Un empate se resuelve como `INTERNAL`.

Con estas fuentes cerradas, que el baseline resulte `INTERNAL` en los 101 folds es un invariante duro: cualquier excepción abortará. La comparación principal será `BA_w` del clasificador menos `BA_w` del baseline. La exactitud simple será secundaria y nunca se presentará sola.

## Evaluación fuera de fold

Al agregar las 101 instancias excluidas, cada rescate `j` de la instancia `i` recibe:

```text
q_ij = 1 / (101 * n_i)
```

Así cada instancia aporta exactamente `1/101`. Las sensibilidades agregadas y la `BA_w` principal se calcularán con estos pesos racionales exactos.

La balanced accuracy sin ponderar será secundaria y se calculará a partir de las sensibilidades por clase derivadas de la matriz de confusión cruda de los 223 rescates.

## Informe por fold

Para cada fold se conservarán:

- `instance_key` excluido y umbral elegido;
- composición real de etiquetas;
- predicción de cada rescate;
- sensibilidad externa si existe al menos un rescate externo, o `NA` si no existe;
- sensibilidad interna si existe al menos un rescate interno, o `NA` si no existe.

Una clase ausente en prueba nunca recibirá sensibilidad cero. Una instancia monoclase solo contribuye a la sensibilidad de la clase presente.

## Resultados agregados

- distribución de los 101 umbrales elegidos;
- sensibilidades externa e interna ponderadas y `BA_w` agregada;
- balanced accuracy sin ponderar secundaria;
- matriz de confusión cruda de los 223 rescates;
- comparación explícita con el baseline;
- resultados descriptivos separados para las 24 instancias mixtas y las 77 monoclase.

En cada subgrupo de `N_group` instancias, cada rescate tendrá peso `1/(N_group*n_i)`. Para cada subgrupo se informarán sensibilidades ponderadas, `BA_w` y matriz de confusión cruda. Los dos subgrupos no se fusionarán en una cifra que oculte su composición.

## Variables y conceptos prohibidos

No se utilizarán como predictores ni para construir `A_G`:

- `minimum_vertex_cut`, `minimum_edge_cut`;
- `individually_critical_vertices`, `individually_critical_edges`;
- `kappa_v`, `lambda_e`, `robustness_label`;
- `edge_disjoint_path_count`, `internally_vertex_disjoint_path_count`;
- `cut_mechanisms`, `cut_mechanism_counts`;
- `external_rescue`, `per_internal_edge_removal`;
- `source_internal_edge_required`, `full_rescue`;
- `covers_all_original_cuts`, `new_separator_count`;
- `A_V`, `A_R`;
- `mechanism_label` e `internal_edge_required`, salvo como respuesta o verificación.

## Criterios de aborto

La ejecución abortará si:

1. cambia cualquier hash certificado;
2. una unión no es única o completa;
3. `mechanism_label` difiere entre fuentes;
4. no aparecen exactamente 223 rescates, 101 instancias y la composición 6+71+24;
5. algún fold pierde una clase completa en entrenamiento;
6. el baseline no resulta `INTERNAL` en los 101 folds;
7. el umbral o las sensibilidades dependen del orden de evaluación de los folds;
8. una variable prohibida entra como predictor.

## Veredicto esperado

`INTERNAL_LOIO_CLASSIFICATION_POTENTIAL_A_G_VERIFIED`
