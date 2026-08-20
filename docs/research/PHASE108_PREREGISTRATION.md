# Fase 108 — Predeclaración aprobada

## Estado y gobernanza

- Estado: aprobada metodológicamente tras revisión independiente de Claude Code.
- Fecha de cierre metodológico: 2026-08-20.
- Base inmutable: ZUSE Automat Agent v1.37 (`cdfcb13`).
- Esta fase es investigación posterior y no modifica retroactivamente v1.37.
- Los artefactos usarán el prefijo histórico `phase107_*`, pero declararán `phase: 108`.
- No se ejecutarán solvers, annealing ni hardware cuántico y no se formularán afirmaciones de ventaja cuántica.

## Título

Dependencia de aristas internas en los rescates mínimos: caracterización estructural y análisis condicionado.

## Pregunta principal

Entre los rescates pertenecientes a clases donde se observan ambos resultados, ¿qué propiedades verificadas distinguen un `EXTERNAL_ATTACHMENT_RESCUE` de un `INTERNAL_EDGE_DEPENDENT_RESCUE`?

La topología del motivo se trata como estructura condicionante. No se presupone que sea una variable predictiva libre.

## Fuentes cerradas

1. `outputs/periodic_backgrounds/phase105_minimal_rescue_motif_results.json`.
2. `outputs/periodic_backgrounds/phase105_minimal_rescue_motif_manifest.json`.
3. Resultados de las fases 102–104 únicamente para recuperar `node_count` mediante `stratum_index`, cardinalidad y claves de instancia.

El analizador verificará los hashes crudos y canónicos ya certificados antes de leer los registros. Los modelos QUBO no son una fuente analítica de esta fase.

## Unidad principal y respuesta

La unidad principal es cada uno de los 1.476 rescates mínimos certificados, agrupado dentro de una de las 265 instancias.

La respuesta primaria es `mechanism_label`, con exactamente un valor por rescate:

- `EXTERNAL_ATTACHMENT_RESCUE`;
- `INTERNAL_EDGE_DEPENDENT_RESCUE`.

Se verificará como invariante que `mechanism_label` es una codificación exacta de `internal_edge_required`, sin discrepancias.

`cut_mechanisms` no forma parte del análisis principal.

## Estratificación estructural obligatoria

Antes de calcular asociaciones, los rescates se separarán según si el motivo contiene aristas internas.

- En motivos sin aristas, `INTERNAL_EDGE_DEPENDENT_RESCUE` es imposible por definición. Esta celda se reportará como restricción lógica, no como resultado empírico.
- En motivos con aristas, las celdas constantes se reportarán como separación completa observada.
- Solo las clases que contienen ambos valores de `mechanism_label` forman el dominio con variación empírica.

No se calculará un efecto global que mezcle restricciones lógicas, separación completa y variación empírica.

## Catálogo de motivos

Las 12 clases exactas permanecerán en todas las tablas de catálogo, incluso con cero rescates observados:

- cardinalidad 2: `2I`, `K2`;
- cardinalidad 3: `3I`, `K2+I`, `P3`;
- cardinalidad 4: `4I`, `K2+2I`, `2K2`, `P3+I`, `P4`, `K1_3`, `C4`.

Las clases ausentes entre los rescates mínimos son `4I`, `K1_3` y `C4`. Se reportarán con cero explícito.

## Dominio con variación observada

La auditoría independiente previa identificó variación genuina únicamente en `K2` y `K2+I`. Se analizarán como estratos separados:

- `K2` tiene cardinalidad 2 fija;
- `K2+I` tiene cardinalidad 3 fija.

La cardinalidad se incluirá en las tablas descriptivas globales, pero no será covariable en los ajustes internos de `K2` o `K2+I`, donde su varianza es cero.

No se realizará una comparación inferencial conjunta entre las 12 clases.

## Variables permitidas

### Principales

- `motif` como estrato estructural;
- `metric` (`kappa` o `lambda`), que varía dentro de `K2` y `K2+I`;
- `node_count`, recuperado de la fuente certificada correspondiente;
- identificador de instancia, usado únicamente para preservar el agrupamiento.

### Descriptivas

- cardinalidad;
- número de aristas internas;
- número de rescates por instancia;
- distribución por motivo y métrica.

No se incorporará ninguna variable cuya definición utilice `mechanism_label` o `internal_edge_required` como predictor del propio resultado.

## Análisis principal predeclarado

El conjunto certificado es un censo finito, no una muestra aleatoria. Por ello, el resultado primario será una caracterización exacta y reproducible, no una declaración de significación poblacional.

1. Construir la tabla exacta `motivo × métrica × mechanism_label` y sus proporciones.
2. Clasificar cada celda como:
   - `LOGICALLY_FORCED`;
   - `OBSERVED_COMPLETE_SEPARATION`;
   - `EMPIRICALLY_VARIABLE`;
   - `ZERO_OBSERVED`.
3. Para `K2` y `K2+I` por separado, informar:
   - recuentos y proporción interna por métrica;
   - diferencia de proporciones `lambda - kappa`;
   - odds ratio con corrección de Haldane–Anscombe solo si existe alguna celda cero;
   - distribución de `node_count` por resultado: número de registros, mínimo, mediana, máximo y media.
4. Informar el número de instancias distintas que sostienen cada estimación y la multiplicidad de rescates por instancia.
5. No interpretar diferencias descriptivas como efectos causales ni como evidencia fuera del conjunto certificado.

No se seleccionarán umbrales de `node_count`, agrupaciones de motivos ni covariables adicionales después de observar los resultados.

## Análisis secundario de cortes

`cut_mechanisms` se analizará separadamente:

- unidad: rescate × corte crítico;
- anidamiento: corte dentro de rescate, dentro de instancia;
- categorías: `INDIVIDUAL`, `DISTRIBUTED_EXTERNAL`, `INTERNAL_EDGE_ENABLED`;
- salida: recuentos exactos por motivo, métrica y `mechanism_label`, número de rescates con una o varias categorías y distribución de cortes por rescate.

No se mezclarán las unidades rescate y rescate × corte en una misma estimación.

## Invariantes y criterios de fallo

La ejecución abortará si falla cualquiera de estas condiciones:

1. Las fuentes no coinciden con sus hashes certificados.
2. El número de rescates no es 1.476 o el número de instancias no es 265.
3. Existe alguna discrepancia entre `mechanism_label` e `internal_edge_required`.
4. Un motivo se asocia con una cardinalidad distinta de su catálogo.
5. Falta la correspondencia inequívoca entre un rescate y su `node_count` de origen.
6. Aparece una categoría de mecanismo no predeclarada.
7. Las tablas no reconcilian exactamente con los totales de entrada.

## Interpretación permitida

La fase distinguirá explícitamente:

- relaciones necesarias por definición;
- regularidades constantes en los datos certificados;
- variación empírica real dentro de `K2` y `K2+I`.

Tanto la presencia como la ausencia de diferencias descriptivas son resultados válidos. No se afirmará causalidad, universalidad, aceleración ni ventaja cuántica.

## Veredicto de cierre esperado

Si todos los invariantes y reconciliaciones pasan, el veredicto será:

`CONDITIONED_MINIMAL_RESCUE_MECHANISM_ATLAS_VERIFIED`

