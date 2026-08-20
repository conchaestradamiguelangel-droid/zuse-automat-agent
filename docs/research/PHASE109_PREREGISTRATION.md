# Fase 109 — Predeclaración aprobada

## Estado y gobernanza

- Estado: aprobada metodológicamente tras auditoría independiente de Claude Code.
- Fecha de cierre metodológico: 2026-08-20.
- Base: Fase 108 cerrada en `4972d5c`.
- La versión publicada v1.37 permanece inmutable en `cdfcb13`.
- Los artefactos usarán el prefijo histórico `phase108_*`, pero declararán `phase: 109`.
- Solo se permiten pruebas dirigidas al cambio actual. La suite global queda prohibida salvo autorización explícita de Miguel.
- No se ejecutarán nuevos barridos, simulaciones, QUBO, solvers ni hardware cuántico.

## Título

Geometría ambiental y dependencia de aristas internas en rescates `K2`.

## Objetivo

Explicar la variación observada entre mecanismos externos e internos sin reutilizar como predictores variables que codifican `internal_edge_required` directa o indirectamente.

El análisis es una caracterización exacta del censo certificado. No demostrará causalidad ni generalizará fuera de él.

## Fuentes cerradas

### Universo candidato principal

- Ledger: `outputs/periodic_backgrounds/phase102_pairwise_synergy_ledger.bin`.
- SHA-256 certificado: `24de12594fe8b95f6e70be4278b2dfadb7f29f181aef3d7aeea41f9fbe58de52`.
- Manifiesto: `outputs/periodic_backgrounds/phase102_pairwise_synergy_manifest.json`.
- Resultados de strata: `outputs/periodic_backgrounds/phase102_pairwise_synergy_results.json`.
- Formato del registro: `<HBBHBBBB`.

Para cada `stratum_index`, el universo candidato `V_i` será la unión de `left_word` y `right_word` de sus registros. Debe cumplirse que:

- existan exactamente 404.054 registros;
- existan exactamente 142 strata;
- `|V_i| == node_count` en cada stratum;
- el número de registros de cada stratum sea `C(node_count, 2)`.

### Mecanismos

- `outputs/periodic_backgrounds/phase105_minimal_rescue_motif_results.json`.
- Solo se analizarán sus 319 rescates `K2` y `K2+I` certificados.

### Verificación cruzada, no fuente analítica

- `outputs/periodic_backgrounds/phase106_minimal_rescue_qubo_models.jsonl`.
- SHA-256 certificado: `d6c813602e914b8863d248d47d7cecfcd498172ba2c3831441b750d5203c82ab`.

`variables.x_words` deberá coincidir exactamente con `V_i` para todas las instancias de los 319 rescates. Los coeficientes QUBO no se leerán ni analizarán. Cualquier discrepancia abortará la ejecución.

## Pregunta principal: nivel intra-instancia

Dentro de las 24 instancias `K2` que contienen ambos mecanismos, ¿la conectividad Hamming-1 externa del par distingue los rescates externos de los dependientes de su arista interna?

El diseño mantiene constantes dentro de cada instancia:

- objetivo y universo candidato;
- `node_count` y periodo;
- regla y métrica;
- cardinalidad y clase de motivo.

## Variables geométricas predeclaradas para K2

Sea `G_i=(V_i,E_i)`, con una arista si y solo si la distancia Hamming es uno. Para un rescate `K2`, `H={u,v}`:

```text
d_ext(u; H) = |{w en V_i \ H : Hamming(u,w)=1}|
S_ext(H) = d_ext(u;H) + d_ext(v;H)
M_ext(H) = min(d_ext(u;H), d_ext(v;H))
B_ext(H) = |d_ext(u;H) - d_ext(v;H)|
```

- `S_ext` es la variable principal.
- `M_ext` y `B_ext` son secundarias.
- La arista interna `(u,v)` se excluye explícitamente.
- Las tres variables deben ser invariantes al orden de las palabras.
- No se añadirán transformaciones geométricas después de observar los resultados.

## Contraste principal equilibrado por instancia

Para cada una de las 24 instancias mixtas `K2`:

```text
Delta_i = media(S_ext | EXTERNAL)_i - media(S_ext | INTERNAL)_i
```

Cada instancia tendrá el mismo peso, con independencia de su número de rescates.

Se informarán:

- los 24 valores `Delta_i`;
- media y mediana de `Delta_i`;
- número de valores positivos, nulos y negativos;
- intervalo de estabilidad determinista obtenido al excluir cada instancia una vez;
- distribuciones completas de `S_ext` por mecanismo.

No se interpretará el signo como efecto causal ni se usará una prueba poblacional de significación como resultado principal.

## Variables secundarias K2

Se repetirá el mismo resumen equilibrado para `M_ext` y `B_ext`. Se identificarán explícitamente como análisis secundarios y no podrán sustituir a `S_ext` como resultado principal.

## K2+I descriptivo

Las cuatro instancias mixtas `K2+I` no sostendrán inferencia propia.

Para `H={a,b,c}`, donde `(a,b)` es la única arista interna y `c` el nodo aislado, se calcularán:

- `S_ext_all`: suma del grado externo de los tres nodos, excluyendo todas las aristas internas de `H`;
- `S_ext_edge`: suma del grado externo de los dos extremos de la arista;
- `d_ext_isolated`: grado externo del nodo aislado.

Se reportarán por separado, sin fusionar roles estructurales ni combinarlos con `K2`.

## Pregunta secundaria entre instancias

¿`node_count` y `rule` describen diferencias en la proporción interna de las instancias, manteniendo `metric` como estrato?

- Unidad: instancia específica de métrica.
- Análisis separado para `K2` y `K2+I`.
- Por instancia: recuentos externo e interno, proporción interna, `node_count`, `rule` y `metric`.
- Resultado: tablas y tamaños descriptivos exactos; no se presentarán como efectos causales.

`period` se conservará solo como procedencia. No entrará como covariable ni se interpretará de manera independiente de `node_count`, debido a su colinealidad estructural observada.

## Variables prohibidas por circularidad o invariancia

No podrán utilizarse como predictores:

- `cut_mechanisms` o `cut_mechanism_counts`;
- `external_rescue`;
- `per_internal_edge_removal`;
- `source_internal_edge_required`;
- `full_rescue`;
- `covers_all_original_cuts`;
- `new_separator_count`;
- `mechanism_label`, salvo como respuesta;
- `internal_edge_required`, salvo para verificar la respuesta.

## Criterios de aborto

La ejecución abortará si:

1. cambia cualquier hash certificado de entrada;
2. no se reconstruyen exactamente 404.054 pares, 142 strata y sus identidades combinatorias;
3. no aparecen exactamente 319 rescates `K2`/`K2+I`;
4. no aparecen exactamente 24 instancias mixtas `K2` y 4 `K2+I`;
5. `V_i` y los `x_words` certificados discrepan en cualquier instancia analizada;
6. un rescate no pertenece inequívocamente a una instancia y un stratum;
7. las variables geométricas dependen del orden de las palabras;
8. una variable circular entra como explicación;
9. se intenta estimar un efecto independiente de `period`.

## Veredicto esperado

Si todos los invariantes y reconciliaciones pasan:

`AMBIENT_GEOMETRY_CONDITIONED_RESCUE_ANALYSIS_VERIFIED`
