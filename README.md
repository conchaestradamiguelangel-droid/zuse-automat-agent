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
- Metricas base: entropia, compresibilidad gzip, informacion mutua temporal,
  densidad y transiciones activas.
- Almacenamiento SQLite.
- Visualizador PNG con Pillow.
- Reportes Markdown por regla.
- CLI minima para simular reglas y generar dataset.

## Uso rapido

```powershell
python -m zaa simulate --rule 110 --steps 200 --width 256 --out outputs\rule110
python -m zaa dataset --steps 1000 --width 256 --cis 10 --db data\zaa.sqlite
python -m unittest discover -s tests
```

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
