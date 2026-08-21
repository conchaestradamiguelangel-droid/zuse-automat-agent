# Fase 111 — Potencial clasificatorio interno LOIO de A_G

**Veredicto:** `INTERNAL_LOIO_CLASSIFICATION_POTENTIAL_A_G_VERIFIED`

## Auditoría

- Rescates K2: 223 en 101 instancias.
- Composición: 6 solo externas, 71 solo internas y 24 mixtas.
- Folds LOIO: 101; todos conservan ambas clases en entrenamiento.
- Baseline de entrenamiento: INTERNAL en 101/101 folds.
- Discrepancias de identidad, mecanismo u orden de folds: 0.

## Resultado agregado fuera de fold

- Sensibilidad externa ponderada: 1.000000.
- Sensibilidad interna ponderada: 0.870184.
- Balanced accuracy ponderada: 0.935092.
- Balanced accuracy cruda secundaria: 0.837278.
- Baseline balanced accuracy ponderada: 0.500000.
- Mejora sobre baseline: 0.435092.
- Matriz cruda (filas reales, columnas predichas): EXT=[54, 0], INT=[55, 114].

## Subgrupos descriptivos

- 24 instancias mixtas: sensibilidad externa ponderada 1.000000, sensibilidad interna 0.295000, BA_w 0.647500.
- 77 instancias monoclase: sensibilidad externa ponderada 1.000000, sensibilidad interna 0.985915, BA_w 0.992958.

## Umbrales elegidos

- t=3: 0 folds.
- t=4: 101 folds.
- t=5: 0 folds.
- t=6: 0 folds.
- t=7: 0 folds.
- t=8: 0 folds.
- t=9: 0 folds.

## Límites

Este es un análisis interno del mismo censo usado para elegir A_G. La selección de la característica no está anidada en LOIO. No constituye validación externa o prospectiva, no estima sin sesgo el rendimiento futuro y no autoriza sustituir las auditorías exactas. No se afirma causalidad ni generalización poblacional.
