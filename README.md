# ZUSE AUTOMAT AGENT

Estado: Fase 0a iniciada.

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
- Fase 2b-real: pipeline de deteccion de eventos candidatos Rule 110 activo.
  Los fixtures validados actuales (`FIX-A`, `FIX-B`, `FIX-C1`) contienen un
  solo glider, asi que producen 0 colisiones. Se generan candidatos de dos
  gliders (`FIX-D`, `FIX-E`) en `fixtures/pending/`, pendientes de revision
  visual/computacional antes de moverlos a `fixtures/validated/`.
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

## Limite metodologico conocido - diff 2-gliders en W=256

El pipeline `detect_collision_candidates_rule110` no detecta eventos candidatos
en fixtures de 2 gliders con `W=256`.

Causa: `diff(frames, ether_puro)` produce alrededor de 3.300 celulas de
perturbacion por glider en un dominio de 256 celdas. Con dos gliders, los campos
de perturbacion se solapan aunque la separacion sea >=100 celdas.
`track_regions_1d` ve una sola region fusionada, no dos tracks separados.

Resultado experimental:

- `FIX-E` (`A + C1`, `separation=100`, `steps=180`): 1 track, 0 candidatos.
- El tracker sigue el baricentro fusionado, no cada glider individualmente.

Estado: Fase 2b-real bloqueada en Rule 110 hasta resolver una de estas:

- Dominio mas ancho (`W=512+`) para separar campos de perturbacion.
- Tracker basado en diff frame-a-frame en lugar de diff contra ether fijo.
- Template matching especifico por tipo de glider.

Fase 2b sintetica sigue siendo la base valida y no esta afectada.

Confirmado con `W=512`, `separation=200`, `steps=300`: mismo resultado. El
problema es estructural al enfoque `diff`.

## Alertas metodologicas vivas

### Rule 110 a escala corta

Tras Fase 3i, `rule_110` pudo evaluarse con `steps=24`, `width=64` y seed
fijo sin heredar escalas altas de otros mundos. Resultado:

- `steps=24`: `status=ok`, `structure_count` alrededor de 69-78 en 6 seeds.
- Firma robusta principal: `(complejidad_alta, densidad_estable)`.
- En 2 de 6 seeds tambien aparece `velocidad_constante`.
- `steps>=48`: pasa a `ruido_no_analizable` por superar el umbral de
  estructuras.

Interpretacion actual: `rule_110` tiene una ventana corta explorable antes de
que el ether/estructura densa dispare demasiadas regiones para los
observadores actuales. Con las 5 leyes actuales, `rule_110@steps=24` y
`rule_30` no quedan distinguidos de forma estable: ambos comparten la firma
`(complejidad_alta, densidad_estable)` en su regimen explorable.

Siguiente pregunta metodologica: distinguir caos tipo Rule 30 de transitorio
caotico Rule 110, posiblemente con una sexta ley de periodicidad/ether local,
autocorrelacion espacio-temporal o frontera `max_ok_steps`/`noise_boundary`.

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
`fixtures/pending/`. No son fixtures validados hasta que una persona revise las
previsualizaciones y los mueva explicitamente a `fixtures/validated/`.

## Dependencias actuales

Requeridas:

- Python 3.11+
- numpy
- scipy
- pillow

Opcionales en fases posteriores:

- numba
- scikit-learn
- pysr
