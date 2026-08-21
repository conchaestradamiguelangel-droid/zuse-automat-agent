# Fase 112 — Predeclaración aprobada

## Estado y gobernanza

- Estado: aprobada metodológicamente por Codex tras auditoría de viabilidad de Claude Code, revisión directa de las tres fuentes cerradas y cierre de todas las decisiones antes del código. Pendiente de construcción por Codex y de verificación independiente posterior — mismo patrón que Fases 108-111.
- Base: Fase 111 cerrada y publicada en `5f79d52`. v1.37 permanece inmutable en `cdfcb13`.
- `phase: 112`. Los artefactos usarán el prefijo histórico `phase111_*`, pero declararán `phase: 112` (mismo patrón de desacoplo prefijo/número usado en Fases 108-111). Solo pruebas dirigidas; suite global prohibida salvo autorización de Miguel.
- No se ejecutarán barridos, simulaciones, QUBO, solvers ni hardware cuántico.
- No se afirma validación externa, prospectiva, causalidad, generalización poblacional ni capacidad predictiva futura. Este análisis es descriptivo y post-selección: el umbral y el contraste se definieron después de observar las etiquetas.

## Título

Multiplicidad de rescates y segregación de mecanismos condicionada por oportunidad combinatoria.

## Pregunta científica

¿La multiplicidad de rescates mínimos por instancia (`n_i`) se asocia con la heterogeneidad de `mechanism_label` dentro de la instancia más allá de lo esperable únicamente por la oportunidad combinatoria creada por disponer de más rescates?

## Límite metodológico fijado antes de la ejecución de producción

El patrón central de esta fase —instancias con `n_i∈{2,3}` con exceso de homogeneidad de etiquetas dentro de la instancia, e instancias con `n_i∈{4,6,7}` con exceso de mezcla de etiquetas dentro de la instancia— ya se observó explorando el censo completo antes de escribir esta predeclaración. El umbral que separa ambos estratos (`n_i=4`), el estadístico `D` y la dirección de cola `D≥D_obs` se eligieron después de observar los resultados. **Por esta razón, la masa de cola calculada por la programación dinámica no es un p-valor confirmatorio con control de error: es una calibración descriptiva posselección.** No se afirma "modelo nulo rechazado" en ningún sentido formal — se afirma que el patrón observado ocupa una región extremadamente rara bajo el modelo intercambiable especificado, como calibración descriptiva posselección. El modelo nulo combinatorio exacto definido abajo evalúa la compatibilidad del patrón observado con una asignación intercambiable de etiquetas entre los huecos, condicionada solo a los tamaños de instancia y al total fijo de etiquetas externas/internas — **no demuestra ni descarta un mecanismo causal**, y no autoriza ninguna afirmación de capacidad predictiva, validación externa o generalización poblacional.

La salida fijará explícitamente:

outcome_data_seen_during_feature_design: true
threshold_selected_after_outcome_inspection: true
exact_null_model_is_descriptive_post_selection: true
directional_hypothesis: false
external_validation: false
prospective_validation: false
causal_claim: false
population_generalization: false
formal_null_hypothesis_test: false
tail_probability_is_confirmatory_p_value: false
tail_direction_selected_after_outcome_inspection: true
multiple_selection_adjustment: false

## Fuentes cerradas

1. `phase105_minimal_rescue_motif_results.json`
   - raw: `9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24`
   - canonical: `982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353`
   - Fuente de identidad de rescate y `mechanism_label`, solo `K2` (`mechanism_audits`).
2. `phase109_fixed_budget_hamming_partition_results.json` (salida certificada de Fase 110)
   - raw: `ba5cf94330ce5c27c6b7c4420f910c637debac1273b9b25d3ad4fd787c141d04`
   - canonical: `dcf3d5847af14b3128e88dac765e491900340ddf4587b50281f42ac8ade147b1`
   - Campo `supplementary_full_census_pairs` (223 filas): `instance_key`, `words`, `A_G`, `mechanism_label` — fuente de `n_i` (agrupando por `instance_key`) y de `A_G` para el análisis secundario.
3. `phase110_internal_loio_a_g_results.json` (salida certificada de Fase 111)
   - raw: `c135f9d0c63b0baa5ffd0a8c9d4c16a9f258482fbe1ac560a3eff076feb76c0d`
   - canonical: `6a8223b20905eafb92cb6fa5727574587d4f4e2313a414e274500d789fd75d80`
   - Campo `out_of_fold_predictions` (223 filas): `instance_key`, `words`, `A_G`, `actual`, `predicted` — fuente exclusiva del análisis secundario de errores de Fase 111. **No se reajusta ni se reentrena ningún clasificador**: los valores de `predicted` se leen tal cual, sin recomputar folds ni umbrales.

No se leen `phase94`/`phase95`/`phase96`/`phase102`/`phase108` directamente: todo lo necesario ya está certificado en las salidas de Fase 109/110/111.

## Claves de unión

- Identidad del rescate: `instance_key + words` (canónicas, ascendentes).
- Identidad de instancia: `instance_key` completo.
- `n_i` de una instancia = número de filas con esa `instance_key` en la fuente 2. Debe coincidir exactamente con el número de filas con esa `instance_key` en la fuente 1 y en la fuente 3 (aborto si difieren).

### Reconciliación completa entre las tres fuentes (obligatoria, por cada identidad de rescate)

Para cada rescate (`instance_key+words`), además de la igualdad de `n_i` ya exigida arriba, se comprueba:

1. `actual` (fuente 3) == `mechanism_label` (fuente 1) == `mechanism_label` (fuente 2) — las tres deben coincidir exactamente.
2. `A_G` (fuente 3) == `A_G` (fuente 2) — coincidencia exacta.
3. `predicted` (fuente 3) pertenece exactamente al conjunto `{EXTERNAL_ATTACHMENT_RESCUE, INTERNAL_EDGE_DEPENDENT_RESCUE}` — ningún otro valor.
4. Cada identidad de rescate aparece exactamente una vez en `out_of_fold_predictions` (fuente 3) — ni duplicada ni ausente respecto a las 223 identidades certificadas por la fuente 1.

Cualquier discrepancia en 1-4 aborta la ejecución antes de calcular nada.

## Universo y estratos

- 223 rescates `K2`, agrupados en 101 instancias.
- Distribución de `n_i` certificada por auditoría previa: `{1:56, 2:18, 3:3, 4:14, 6:4, 7:6}`. **`n_i=5` no aparece en el censo: 0 instancias** — se declara como soporte ausente, no como frontera demostrada entre `n_i=4` y `n_i=6`.
- `K_ext=54` rescates `EXTERNAL_ATTACHMENT_RESCUE`, `K_int=169` rescates `INTERNAL_EDGE_DEPENDENT_RESCUE` sobre el total `N=223`. Ambos totales son fijos y certificados (fuente 1).

### Partición en tres conjuntos disjuntos (obligatoria, exhaustiva de las 101 instancias)

- **Conjunto excluido `X`** (`n_i=1`, 56 instancias): con un único rescate, la instancia es monoclase por definición, para cualquier reparto posible de etiquetas. `X` **no contribuye a `y`, `z` ni `D`**, pero sus 56 huecos sí forman parte del espacio combinatorio completo, de la programación dinámica y de la normalización `C(223,54)` — no se retiran del reparto de etiquetas, solo se excluyen del contraste.
- **Estrato bajo `Y`** (`n_i∈{2,3}`, 21 instancias: 18 con `n_i=2`, 3 con `n_i=3`; 45 rescates): estrato donde se observa **exceso de homogeneidad (agrupamiento de etiquetas dentro de la instancia)** frente al modelo nulo.
- **Estrato alto `Z`** (`n_i∈{4,6,7}`, 24 instancias: 14 con `n_i=4`, 4 con `n_i=6`, 6 con `n_i=7`; 122 rescates): estrato donde se observa **exceso de mezcla (heterogeneidad de etiquetas dentro de la instancia)** frente al modelo nulo.

Una instancia es **mixta** si contiene al menos un rescate `EXTERNAL_ATTACHMENT_RESCUE` y al menos uno `INTERNAL_EDGE_DEPENDENT_RESCUE`; **monoclase** en caso contrario.

## Estadístico principal

D = (instancias mixtas en Z / 24) − (instancias mixtas en Y / 21)

`D∈[-1,1]`. El valor observado `D_obs` se calcula directamente del censo, no se asume. El código debe calcular `D_obs` a partir de los datos reales antes de usarlo como umbral de cola en el modelo nulo — no se hardcodea.

## Modelo nulo combinatorio exacto (programación dinámica conjunta, sin Monte Carlo ni aproximación)

Se define el modelo nulo de asignación intercambiable: los 223 rescates se reparten en los 101 huecos de instancia con tamaños `n_i` fijos (los mismos 101 tamaños observados), y se eligen uniformemente al azar, entre las `C(223,54)` formas posibles, cuáles 54 de los 223 huecos llevan la etiqueta `EXTERNAL_ATTACHMENT_RESCUE` (las restantes 169 llevan `INTERNAL_EDGE_DEPENDENT_RESCUE`). No se simula: se calcula la distribución exacta por programación dinámica.

### Especificación exacta de la programación dinámica

1. Cada una de las 101 instancias es un "hueco" de tamaño `n_i` con una etiqueta de grupo: `X` (`n_i=1`, no rastreado), `Y` (`n_i∈{2,3}`) o `Z` (`n_i∈{4,6,7}`).
2. El estado de la DP es una terna `(j, y, z)`: `j` = número de etiquetas `EXTERNAL` ya asignadas entre las instancias procesadas; `y` = número de instancias del estrato `Y` que resultaron mixtas hasta el momento; `z` = número de instancias del estrato `Z` que resultaron mixtas hasta el momento. Estado inicial `(0,0,0)` con conteo `1`.
3. Para cada instancia de tamaño `n` y grupo `g`, y para cada `k∈{0,...,n}` (número de `EXTERNAL` que caen en ese hueco), se transiciona multiplicando por el coeficiente binomial `C(n,k)` (número de formas de elegir qué posiciones concretas del hueco son `EXTERNAL`, aunque para esta fase la identidad interna no importa, solo el conteo): `j→j+k`; si `g=Y` y `0<k<n`, `y→y+1`; si `g=Z` y `0<k<n`, `z→z+1`; si `g=X`, `y`/`z` no cambian.
4. Las 101 instancias se procesan en cualquier orden — la convolución es conmutativa y el resultado no puede depender del orden. El código debe verificar esto explícitamente ejecutando la DP completa con **al menos dos órdenes deterministas distintos** de las 101 instancias (por ejemplo, orden de aparición en la fuente y orden inverso, o el orden natural y uno ordenado por `instance_key`) y comparando la **igualdad exacta del mapa completo `(y,z) → conteo entero`** entre ambas ejecuciones — no basta con comparar únicamente `P(D≥D_obs)` y la lista de pares cualificantes, porque dos distribuciones distintas podrían coincidir casualmente solo en esa cola. Aborto si el mapa completo difiere en cualquier celda entre los dos órdenes.
5. Al terminar, se restringe a los estados con `j=54` exactamente. La suma de los conteos en `j=54` debe ser exactamente `C(223,54)` — aborto si no coincide (garantiza que la DP cubrió todo el espacio sin pérdida ni duplicación).
6. Dividiendo cada conteo por `C(223,54)` se obtiene la distribución de probabilidad conjunta exacta (como `fractions.Fraction`) de `(y,z)` bajo el modelo nulo.
7. Para cada par `(y,z)` con masa positiva, se calcula `D(y,z) = z/24 − y/21`. La probabilidad nula del patrón observado es:

P(D >= D_obs) = suma de la masa de todos los pares (y,z) con D(y,z) >= D_obs

8. El código debe reportar explícitamente la lista completa de pares `(y,z)` que satisfacen `D(y,z) >= D_obs` (no solo la probabilidad agregada), para que quede auditable qué configuraciones cuentan como "igual o más extremas". Cada par cualificante debe reportarse con su **conteo entero** (numerador de la DP en `j=54`) y su **masa `Fraction` exacta** (conteo/`C(223,54)`), no únicamente sus coordenadas `(y,z)`.
9. Toda la aritmética (conteos, `C(n,k)`, `C(223,54)`, división final) se hace con enteros exactos de precisión arbitraria y `fractions.Fraction`; los decimales son solo representación de salida.

## Resultados descriptivos obligatorios

1. Vector completo `M_n` para `n∈{2,3,4,6,7}`: número de instancias con ese `n_i`, número observado de mixtas, número observado de monoclase.
2. Expectativa marginal hipergeométrica por estrato: `P(monoclase | n_i) = [C(54,n_i) + C(169,n_i)] / C(223,n_i)`, y el número esperado de mixtas/monoclase en cada estrato (`instancias_con_ese_n_i × (1 − P(monoclase))` y `× P(monoclase)`), como `Fraction` exacta.
3. Total agregado: número observado de instancias mixtas (excluyendo `X`) frente al total esperado bajo el modelo marginal (suma de los esperados por estrato), mostrando explícitamente que el agregado puede quedar numéricamente próximo a su expectativa marginal, aunque las desviaciones opuestas por estrato se cancelen.
4. `D_obs` calculado de los datos, y `P(D >= D_obs)` calculada por la programación dinámica conjunta del apartado anterior, junto con la lista completa de pares `(y,z)` que la componen.
5. `n_i=1` (conjunto `X`) reportado aparte, fuera del contraste. `n_i=5` reportado explícitamente como soporte ausente (0 instancias), no como frontera.

## Análisis secundario: errores de Fase 111 por estrato de `n_i` dentro de `Z`

Usando exclusivamente `out_of_fold_predictions` de la fuente 3, sin recalcular ni reajustar ningún umbral ni clasificador:

Para cada `n_i∈{4,6,7}`, dentro de las instancias mixtas de `Z`:

- composición de rescates (`EXTERNAL`/`INTERNAL`);
- número y proporción de rescates con `A_G∈{4,5}` (zona ambigua identificada en Fase 111);
- número y proporción de rescates con `predicted != actual` (error de Fase 111, leído tal cual, no recomputado).

Este apartado es puramente descriptivo, estrato por estrato. **No se ajusta una tendencia, no se calcula una pendiente ni un coeficiente de correlación entre `n_i` y la tasa de error, y no se afirma que el error aumente o disminuya con `n_i`.** Los tres estratos se presentan como tres cifras independientes, no como una serie con dirección.

## Variables y conceptos prohibidos

- No se recalcula, reajusta ni reentrena ningún umbral o clasificador de Fase 111 (ni `A_G`, ni `A_V`, ni ninguna combinación).
- No se usa `A_V` ni `A_R` en esta fase (no forman parte de la pregunta de Fase 112).
- No se usa `LOIO` ni ningún esquema de validación cruzada — esta fase no predice, describe.
- No se ajusta ninguna regresión, pendiente o coeficiente de tendencia entre `n_i` y la tasa de error de Fase 111.
- No se sustituye la programación dinámica exacta por una simulación Monte Carlo ni por una aproximación normal/binomial.
- `minimum_vertex_cut`, `minimum_edge_cut`, `individually_critical_vertices/edges`, `kappa_v`, `lambda_e`, `robustness_label`, `cut_mechanisms`, `cut_mechanism_counts`, `external_rescue`, `per_internal_edge_removal`: prohibidos como en fases anteriores.

## Criterios de aborto

1. Cambia cualquier hash certificado de entrada.
2. Una unión (identidad de rescate o instancia) no es única o completa entre las tres fuentes.
3. `mechanism_label` difiere entre la fuente 1 y la fuente 2 para cualquier rescate.
4. `n_i` calculado desde la fuente 1 difiere del calculado desde la fuente 2 o la fuente 3 para cualquier instancia.
5. La distribución de `n_i` observada difiere de `{1:56, 2:18, 3:3, 4:14, 6:4, 7:6}`, o `n_i=5` aparece con soporte `>0`.
6. `K_ext != 54` o `K_int != 169` o `N != 223`.
7. La suma de la masa de la DP en `j=54` no es exactamente `C(223,54)`.
8. El mapa completo `(y,z) → conteo entero` difiere en cualquier celda entre los dos órdenes deterministas distintos de procesamiento de las 101 instancias en la DP (no solo `P(D >= D_obs)` o la lista de pares cualificantes).
9. El análisis secundario de Fase 111 recalcula, reajusta o reentrena cualquier umbral, o usa un campo distinto de `out_of_fold_predictions` ya certificado.
10. Una variable prohibida entra en cualquier cómputo.
11. Cualquier discrepancia en la reconciliación completa entre fuentes (sección "Reconciliación completa entre las tres fuentes"): `actual`/`mechanism_label` no coinciden entre las tres fuentes, `A_G` difiere entre fuente 2 y fuente 3, `predicted` fuera del conjunto de dos etiquetas permitidas, o identidad de rescate duplicada o ausente en `out_of_fold_predictions`.

## Veredicto esperado

`EXACT_POST_SELECTION_COMBINATORIAL_STRATIFICATION_CALIBRATED`

Se emitirá si las fuentes, reconciliaciones, masa combinatoria, distribución conjunta exacta e invariancia al orden superan todos los criterios de aborto. La masa de cola se reportará como `Fraction` exacta y decimal, sin convertirla en criterio confirmatorio ni en rechazo formal. El veredicto no depende de que `P(D >= D_obs)` cruce ningún umbral de magnitud — es incondicional a los criterios de aborto, no a la magnitud de la masa de cola.
