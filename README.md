# ZUSE AUTOMAT AGENT

Estado: Fase B completada. 130 tests OK. FIX-D/E validados.

Premisas rectoras:

1. VELOCIDAD
2. ESCALABILIDAD
3. CUANTICA

## Fase 0a

Objetivo: laboratorio reproducible minimo para automatas celulares elementales
(ECA): 2 estados, radio 1, 256 reglas.

Incluye:

- Motor ECA 1D con Numpy.
- Motor generico 1D para `k` estados y radio `r` mediante tabla local o
  callable, sin exploracion exhaustiva del espacio de reglas.
- Metricas base: entropia, compresibilidad gzip, informacion mutua temporal,
  densidad y transiciones activas.
- Almacenamiento SQLite.
- Visualizador PNG con Pillow.
- Reportes Markdown por regla.
- CLI minima para simular reglas y generar dataset.
- Observadores 1D iniciales sobre datos sinteticos: correlacion, patches
  ligeros y diferencia de frames.

## Uso rapido

```powershell
python -m zaa simulate --rule 110 --steps 200 --width 256 --out outputs\rule110
python -m zaa dataset --steps 1000 --width 256 --cis 10 --db data\zaa.sqlite
python -m zaa benchmark --rule 110 --steps 1000000 --width 256
python -m zaa observe-synthetic --kind glider
python -m zaa generate-rule110-fixtures --out fixtures\pending
python -m zaa validate-rule110-fixtures --pending fixtures\pending --validated fixtures\validated
python -m zaa observe-life --kind glider
python -m zaa gate-g1a1 --fixtures fixtures\validated
python -m zaa laws-2a --fixtures fixtures\validated --out reports\fase2a
python -m zaa discover --world synthetic_glider --cycles 5
python -m zaa discover --world life_glider --cycles 3 --journal journal.jsonl
python -m zaa discover --world rule_30 --cycles 5 --steps 200 --width 256
python -m unittest discover -s tests
```

## Estado de fases

- Fase 0a: congelada en git.
- Fase 0b: congelada en git.
- Fase 1a: iniciado el pipeline de observadores 1D con datos sinteticos.
  La validacion real contra Rule 110 queda pendiente de fixtures congelados.
- Fase 1b: motor Game of Life y observadores 2D iniciales.
- Fase 2b: pipeline mecanico inicial de colisiones sinteticas. No conectado
  todavia a Rule 110 real.
- Fase 2b-real / Fase B: fixtures Rule 110 activos. `FIX-A`, `FIX-B` y
  `FIX-C1` validan gliders simples. `FIX-D` y `FIX-E` estan ya en
  `fixtures/validated/` como colisiones validadas computacionalmente mediante
  `dual_reference_diff`, con outcomes y evidencia visual en metadata/PNGs.
- Fase 3a/3b: discovery loop mecanico activo. Mundos: sinteticos 1D, Game of
  Life, ECA arbitrario. Sin LLM. Sin Rule 110 real (tracker bloqueado).
  Fase 3b anade exploracion por ciclo (seed variante), metricas correctas para
  GoL 3D y filtro de ruido (`structure_count > 100` ->
  `ruido_no_analizable`). Comando:
  `python -m zaa discover --world synthetic_glider --cycles 5`.
- Fase 3c: evaluacion de leyes por ciclo. Para mundos `ok`: velocidad
  constante, periodicidad, densidad estable y tipo unico. Para ruido:
  `laws_status=skipped_noise`. El resultado queda en el journal por ciclo.
- Fase 3d: politica heuristica v0. El agente decide cada ciclo:
  `repeat_vary_seed`, `increase_steps`, `change_world` o
  `skip_rule110_real`. Sin ML. Sin LLM. Sin Rule 110 real. Politica
  transparente if/else. Registra `action_taken`, `action_reason` y `score` en
  journal.
- Fase 3d-v1 / 3a-fix: politica mas agresiva con `MAX_REPEATS_DEFAULT=1`
  y `repeat_vary_seed` condicionado a mejora de score. La ley
  `velocidad_constante` pasa de "mejor caso" a fraccion de estructuras:
  acepta solo si `passing_fraction >= 0.5` entre estructuras en movimiento.
- Fase 3e: historial por mundo dentro del run. `WorldRecord` acumula
  `visit_count`, `scores` y `noise_count`. La politica evita mundos
  consistentemente ruidosos (`noise_fraction >= 0.75`, `visit_count >= 2`).
- Fase 3f: firma de leyes como novedad exploratoria. El agente registra
  `law_signature` e `is_new_law_signature`; una firma nueva dispara
  `firma_leyes_nueva_explorar_mas`.
- Fase 3g: persistencia entre runs con `--state-file`. Se guardan/cargan
  `world_history` y firmas conocidas en JSON (`schema_version=1`).
- Quinta ley: `complejidad_alta`, basada en entropia media y tasa de
  transicion (`entropy_mean > 0.8` y `transition_rate > 0.25`). Separa caos
  estable de orden simple; `rule_30` obtiene firma
  `(complejidad_alta, densidad_estable)`.
- Fase 3h: exploracion parametrica por firma conocida. Si una firma ya es
  conocida pero tiene al menos dos leyes aceptadas, el agente prueba mas
  escala (`firma_conocida_buscar_escala`) incrementando `steps`.
- Fase 3i: parametros por mundo. `steps` deja de heredarse globalmente entre
  mundos; cada mundo conserva su propia escala. Esto elimino la contaminacion
  por carry-over que hacia que `rule_30` y `rule_110` heredaran `steps=400`.
- Fase 4a (commit 2cd91c1): 7a ley `temporal_scale_stability`
  (`temporal_load = steps * gzip_ratio / transition_rate < 19.03`).
  Calibrada con PySR sobre dataset ECA caotico (90.8% accuracy).
  Cierra alerta rule_30/rule_110: `frontera_temporal`
  (`tr` en `(0.28, 0.44]`) los distingue desde Fase 3i.
  `rule_110` tr=0.402, `rule_30` tr=0.456.
- Fase 4b (commit 04948eb): filtro diagnostico anti-eter
  `filter_structures_by_start_frame(structures, T=18)` en
  `zaa/observers.py`. T=18 es constante empirica para width=64, no heuristica
  perezosa. El eter de Rule 110 madura en frame ~18; el filtro retiene solo
  estructuras nacidas antes de ese umbral.
- Fase B (commit 85c397b): `FIX-D` y `FIX-E` validados computacionalmente
  mediante `dual_reference_diff`. Metodo: comparar run contra referencias de
  un solo glider para aislar cada componente y la zona de colision.
  Outcomes:
  - `FIX-D` (`A+B`): `glider_B_consumed_ether_phase_transition`.
  - `FIX-E` (`A+C1`): `glider_C1_transformed_compound_output`.
  `diff_from_pure_ether` es valido solo para CI = `ether_state(width) +
  perturbacion`. Para discovery aleatorio, T=18 es la herramienta correcta.

## Estado de colisiones Rule 110 - Fase B

`diff_from_pure_ether` + `observar_regiones_rule110` son validos para runs
cuya CI es `ether_state(width) + perturbacion` (fixtures canonicos). En ese
caso el defecto de costura (`width mod 14 != 0`) cancela en el diff porque
ambas simulaciones parten del mismo IC.

Para discovery con IC aleatoria: el diff canonico produce ~50% de actividad
residual (el defecto de costura no cancela). En ese caso, `T=18` es la
herramienta correcta (`filter_structures_by_start_frame`).

`FIX-D` y `FIX-E` estan en `fixtures/validated/` con metadata enriquecida y
6 diff PNGs como evidencia visual.

## Alertas metodologicas vivas

### Rule 110 - alerta CERRADA

La firma `(complejidad_alta, densidad_estable)` era compartida por `rule_110`
y `rule_30` con 5 leyes. Cerrada en Fase 4a: `frontera_temporal`
(`tr` en `(0.28, 0.44]`) distingue los dos:

- `rule_110`: tr=0.402 -> `frontera_temporal=True`
- `rule_30`: tr=0.456 -> `frontera_temporal=False`

Para `steps > 24` en discovery, `temporal_scale_stability` actua como
limite de ventana: `temporal_load = steps * gzip_ratio / tr < 19.03`.

### Gate G1a.1

`gate-g1a1` pasa sobre los fixtures validados de Rule 110 usando
`diff(frames, ether_puro)` y un tracker de regiones conectadas 1D. El evaluador
informa `coherent_detection`, `structure_count` y `emitted_types` para separar
"pasa por tipo presente" de "detecta una particula compacta".

La deuda metodologica restante es mejorar la independencia real de observadores:
el tracker de regiones reduce la fragmentacion, pero O2 sigue siendo un
stand-in sin k-means genuino.

### Fase 2a

Las leyes `velocidad_constante`, `periodicidad` y `conteo_estructuras` se aceptan
en fixtures Rule 110 porque se evalua contra metadata computacionalmente
validada del fixture. Sirven como prueba mecanica del pipeline MDL, pero no son
observacion independiente. La evaluacion no circular actual es
`paridad_total`, que se calcula sobre frames reales y se rechaza correctamente.

## Fixtures Rule 110

`python -m zaa generate-rule110-fixtures` genera candidatos `.npz` y PNG en
`fixtures/pending/`. Los candidatos se mueven a `fixtures/validated/` mediante
validacion computacional (`dual_reference_diff`) o revision visual humana.

- `FIX-A`, `FIX-B`, `FIX-C1`: validados computacionalmente (gliders simples).
- `FIX-D`, `FIX-E`: validados computacionalmente (colisiones, outcomes
  documentados en metadata).

## Dependencias actuales

Requeridas:

- Python 3.11+
- numpy
- scipy
- pillow
- pysr  # instalado - calibracion Fase 4a

Opcionales en fases posteriores:

- numba
- scikit-learn
