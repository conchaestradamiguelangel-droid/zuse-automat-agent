# Fase 110 — Predeclaración aprobada

## Estado y gobernanza

- Estado: aprobada metodológicamente tras auditoría independiente de Claude Code.
- Fecha de cierre metodológico: 2026-08-21.
- Base: Fase 109 cerrada y publicada en `06bdfaf`.
- La versión publicada v1.37 permanece inmutable en `cdfcb13`.
- Los artefactos usarán el prefijo histórico `phase109_*`, pero declararán `phase: 110`.
- Solo se permiten pruebas dirigidas al cambio actual. La suite global queda prohibida salvo autorización explícita de Miguel.
- No se ejecutarán barridos, simulaciones, QUBO, solvers ni hardware cuántico.

## Título

Partición del presupuesto fijo de conectividad Hamming-1 en rescates `K2`.

## Pregunta científica

¿Cómo difiere entre mecanismos la asignación del presupuesto fijo de 14 incidencias Hamming-1 externas del par hacia el universo candidato periodo-específico `V_i`, el grafo-puente físico `G_min` y la región residual?

No existe hipótesis direccional predeclarada.

## Fuentes cerradas

1. `phase94_hypercube_completion_results.json`
   - raw: `1429ac8edc3d5fd4ee8823e2b8437666cae8bdd129f2a4a47e4505bba9aa83a3`
   - canonical: `57c8988db22d659860b8c94accfa8be54ec5891a7ca036e7d0ea2150e3c3f429`
2. `phase95_fragment_bridge_results.json`
   - raw: `cbd414180e89658b3e20c73559dbcb490b2bca845a1165f3f6a8e36f25c2e823`
   - canonical: `5c43278492fa09f9367fa971e06d0a7b3e2b99e295a63279721bc78a4946f825`
3. `phase96_bridge_robustness_results.json`
   - raw: `3096af928d5eff638d9ad63b6503eb85ecbd66956f35c5df94674e07d72e5858`
   - canonical: `85deb69d8dbb650c6423fcfd229e258118596ca3418d2e6556819a9ad23a2c5b`
4. `phase102_pairwise_synergy_ledger.bin`
   - SHA-256: `24de12594fe8b95f6e70be4278b2dfadb7f29f181aef3d7aeea41f9fbe58de52`
5. `phase102_pairwise_synergy_manifest.json`
   - raw: `d434a20dd0c66350fadceac6ea4f6e3d73bd9769e51195083efc628ed8170057`
   - canonical: `580635c42efc2bb042e539f0a1f61d6ae15693d38d77a3333041757be9257ea5`
6. `phase102_pairwise_synergy_results.json`
   - raw: `9a5c70318085c8d6d1a7ad82a59fb631abda524926288c46cb0da30a7cd47268`
   - canonical: `152003197716bff38e552b3b51754df6dbfe4c6dc9f93326c3a55de594e5a6c3`
7. `phase105_minimal_rescue_motif_results.json`
   - raw: `9c56da0916c7a7125c3581f30d685038b4fa42b9c27ae6d1b35448cbbfb59b24`
   - canonical: `982eef2e0341d5630c170d14893e6839b6681162dc68cd16db9c20d45d976353`
8. `phase108_ambient_rescue_geometry_results.json`
   - raw: `02c858e4b8a801e39bec9512a54e317f0dfdd8c43cbe02ee5342c09442cfdae9`
   - canonical: `b479df629574d25d0655b3524962846de410b5382cb1b9c26b400117ac2ca1c0`
9. `analyze_phase96_bridge_robustness.py`
   - raw: `b282191a91b4f25dc5f3406d4ba30adb58465d2913c64446a6bca5dddd8e47f0`

`G_min` se reconstruirá replicando literalmente `node_levels()` y `allowed_words()` del script certificado, sin usar información de cortes, robustez o caminos.

## Claves de unión

- `G_min`: `cube_key + pair_index`.
- `V_i` y rescate: `cube_key + pair_index + period + metric`.
- Identidad del rescate: `instance_key + words`, con palabras canónicas ascendentes.

Toda unión debe ser única. Una ausencia o duplicidad abortará la ejecución.

## Universo principal

- 122 rescates `K2`.
- 24 instancias que contienen al menos un rescate externo y uno dependiente de arista interna.
- Cada instancia recibe el mismo peso, independientemente de su número de rescates.

El censo completo de 223 rescates `K2` se utilizará únicamente para la distribución descriptiva de `A_G` y para una tabla suplementaria cruda `(A_V,A_G)` no particional.

## Variables predeclaradas

Para `H={u,v}`:

```text
A_V(H) = S_ext certificado en Fase 109
A_G(H) = suma, sobre u y v, de vecinos Hamming-1 pertenecientes a G_min
A_R(H) = 14 - A_V(H) - A_G(H)
```

`A_V` se leerá directamente de `phase108_ambient_rescue_geometry_results.json`, indexado por `instance_key + words`. No se recalculará.

`A_G` es la variable principal nueva. `A_R` es secundaria y solo se calculará dentro del universo principal certificado.

La identidad de 14 procede de los siete vecinos externos de cada extremo de un par `K2` en `Q8`.

## Invariantes de la partición

En los 122 rescates principales deben cumplirse:

- `H` es subconjunto de `V_i`;
- `V_i` y `G_min` son disjuntos;
- `A_V + A_G + A_R == 14`;
- `A_R >= 0`;
- `A_V`, `A_G` y `A_R` no dependen del orden de `u,v`.

Aunque la disyunción fue verificada externamente para las 101 instancias `K2`, ampliar la partición fuera de las 24 instancias mixtas queda explícitamente fuera del alcance de esta fase.

## Contraste principal

Para cada instancia mixta `i`:

```text
Delta_i(A_G) = media(A_G | EXTERNAL)_i - media(A_G | INTERNAL)_i
```

Se informarán:

- los 24 valores `Delta_i(A_G)`;
- media y mediana;
- rango y signos positivo/nulo/negativo;
- intervalo de estabilidad determinista al excluir cada instancia una vez;
- distribución completa de `A_G` por mecanismo en los 223 rescates `K2`.

## Variable secundaria

`A_R` recibirá el mismo resumen equilibrado por instancia, pero no podrá sustituir a `A_G` como resultado principal.

## Relación descriptiva A_V–A_G

Se conservarán:

- los 122 pares crudos `(A_V,A_G)` del universo principal;
- los 223 pares crudos como suplemento no particional.

Para cada rescate `j` de la instancia principal `i`:

```text
x_ij = A_V_ij - media_i(A_V)
y_ij = A_G_ij - media_i(A_G)
w_ij = 1 / (24 * n_i)
```

Se calcularán exactamente:

```text
cov_w = sum(w_ij * x_ij * y_ij)
var_w(A_V) = sum(w_ij * x_ij^2)
var_w(A_G) = sum(w_ij * y_ij^2)
corr_w = cov_w / sqrt(var_w(A_V) * var_w(A_G))
```

Cada instancia aporta peso total `1/24`. Si alguna varianza ponderada es cero, `corr_w` se declarará indefinida y no se sustituirá por otro estadístico.

La relación se describirá como condicionada y mecánica. No demostrará independencia ni dependencia estadística formal.

## K2+I

`K2+I` queda fuera: la identidad de 14 incidencias de un par no se aplica a cardinalidad 3.

## Variables prohibidas

No se utilizarán como predictores ni para construir `A_V`, `A_G` o `A_R`:

- `minimum_vertex_cut`, `minimum_edge_cut`;
- `individually_critical_vertices`, `individually_critical_edges`;
- `kappa_v`, `lambda_e`, `robustness_label`;
- `edge_disjoint_path_count`, `internally_vertex_disjoint_path_count`;
- `cut_mechanisms`, `cut_mechanism_counts`;
- `external_rescue`, `per_internal_edge_removal`;
- `source_internal_edge_required`, `full_rescue`;
- `covers_all_original_cuts`, `new_separator_count`;
- `mechanism_label` o `internal_edge_required`, salvo como respuesta o verificación.

`G_min` se usa exclusivamente como conjunto de palabras.

## Criterios de aborto

La ejecución abortará si:

1. cambia cualquier hash certificado;
2. una unión no es única o completa;
3. `V_i ∩ G_min` no es vacío en alguna de las 24 instancias;
4. `H` no está contenido en `V_i`;
5. `A_V+A_G+A_R != 14` o `A_R < 0` en cualquier rescate principal;
6. no aparecen exactamente 24 instancias, 122 rescates principales y 223 `K2` totales;
7. alguna variable geométrica depende del orden de las palabras;
8. una variable prohibida entra como predictor.

## Límites interpretativos obligatorios

Los resultados fijarán:

- `causal_claim: false`;
- `population_generalization: false`;
- `directional_hypothesis: false`;
- `statistical_independence_claimed: false`.

## Veredicto esperado

`FIXED_BUDGET_HAMMING_PARTITION_K2_VERIFIED`
