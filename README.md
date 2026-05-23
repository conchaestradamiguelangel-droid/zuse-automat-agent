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

## Alertas metodologicas vivas

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
