# Zenodo v1.37 Record

Published and verified against the Zenodo API on 2026-08-16.

## Informacion basica

- **Tipo de recurso:** Preprint
- **Titulo:** ZUSE Automat Agent: Empirical Law Discovery in Elementary Cellular Automata
- **Fecha de publicacion:** `2026-08-16`
- **Creador:** Miguel Angel Concha Estrada
- **Afiliacion:** Independent researcher
- **Version:** v1.37
- **Editor:** Zenodo
- **Idioma:** English
- **Licencia:** Creative Commons Attribution 4.0 International
- **Copyright:** Copyright (C) 2026 The author.

## Descripcion

La version v1.37 incorpora las Fases 106--107 y extiende la auditoria de
cardinalidad minima publicada en v1.36 con dos artefactos reutilizables: un
atlas exacto de motivos de rescate y una compilacion QUBO certificada.

Esta version no repite simulaciones del automata celular ni modifica los
censos anteriores. Reutiliza los ledgers verificados de parejas, ternas y
cuartetos dentro de los 48 hipercubos Q8 congelados.

Resultados principales:

- La Fase 106 clasifica exhaustivamente 27.828.370 conjuntos candidatos de
  cardinalidad 2--4 mediante 12 motivos no etiquetados de adyacencia Hamming-1.
- Dos clasificadores de isomorfismo independientes coinciden en todos los
  registros, sin discrepancias de reconciliacion.
- Se auditan 1.476 rescates minimos especificos por metrica, conservando por
  separado cobertura de cortes, rescate completo y dependencia de aristas
  internas.
- La Fase 107 compila esos rescates en 265 modelos QUBO dispersos de coste
  unitario.
- Los modelos acumulan 19.100 variables y 32.861 terminos no nulos, con un
  rango de 9 a 172 variables por modelo.
- La evaluacion entera independiente certifica exactamente 1.476 estados
  fundamentales, sin soluciones espurias ni rescates ausentes.

El alcance esta limitado deliberadamente. Los motivos describen grafos
inducidos por intervenciones Hamming-1 sobre palabras centrales de ocho bits;
no son transiciones temporales del automata celular. Los QUBO codifican
rescates ya enumerados y verificados: no descubren rescates nuevos, no usan
hardware cuantico ni annealing, y no demuestran aceleracion o ventaja
cuantica. Su valor es proporcionar una representacion de optimizacion exacta,
auditable y preparada para evaluacion futura en solvers clasicos o cuanticos.

Todos los resultados son deterministas y reproducibles mediante scripts,
manifiestos, ledgers compactos, modelos JSONL, informes y pruebas comprometidos
en el repositorio.

Repositorio:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Palabras clave

- elementary cellular automata
- empirical law discovery
- complex systems
- basin topology
- graph motifs
- minimum cardinality
- QUBO
- quantum-ready optimization
- reproducible computational science

## Trabajos relacionados

- **Es suplemento de / Software:** https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- **URL del repositorio:** https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- **Lenguaje de programacion:** Python
- **Estado de desarrollo:** Active

## Control del archivo

- **Nombre para subir:** `zuse_preprint.pdf`
- **Origen local esperado:** `paper/zuse_preprint.pdf`
- **Tamano:** `1,043,688 bytes`
- **Paginas:** `61`
- **MD5:** `4cffbfd41886c44d5d25ef0557e088d4`
- **SHA-256:** `b595d553b652bf31382fcc55a13770d80fcdb791d16a5d2bcf53d3b4804b62c1`
- **DOI de version:** `10.5281/zenodo.21965090`
- **DOI de serie:** `10.5281/zenodo.21965089`
