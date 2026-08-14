# Zenodo v1.35 Record

Published and verified against the Zenodo API on 2026-08-14.

## Basic metadata

- **Resource type:** Preprint
- **Title:** ZUSE Automat Agent: Empirical Law Discovery in Elementary Cellular Automata
- **Publication date:** `2026-08-14`
- **Creator:** Miguel Angel Concha Estrada
- **Affiliation:** Independent researcher
- **Version:** v1.35
- **Publisher:** Zenodo
- **Language:** English
- **License:** Creative Commons Attribution 4.0 International
- **Copyright:** Copyright (C) 2026 The author.

## Description

La version v1.35 amplia el preprint de ZUSE con las Fases 91--103, una auditoria
verificada de la poblacion de osciladores de periodo largo recuperada en v1.34.
Esta version no repite ni modifica el censo de 5.783.040 configuraciones.

Resultados principales:

- Los 3.296 descriptores confirmados se reducen a 192 clases fisicas estrictas
  de atractor y 123 clases de morfologia del defecto.
- La deduplicacion deja 1.829 estados fisicos iniciales y elimina 1.467 alias de
  codificacion, sin conflictos deterministas.
- La conjugacion blanco/negro entre rule_73 y rule_109 se verifica exactamente
  para las 3.296 trayectorias y cierra las 123 clases bajo el cociente de
  conjugacion.
- Se construyen 48 hipercubos Q8 completos de intervenciones sobre palabras
  iniciales de ocho bits.
- Sobre 219 objetivos fragiles, 43.425 intervenciones unitarias obedecen una ley
  exacta de cobertura de cortes: la redundancia de vertices o aristas se
  recupera si y solo si el estado anadido evita todos los cortes criticos.
- La retirada directa de cortes, un calculo independiente de flujo maximo y el
  predicado geometrico coinciden sin excepciones.
- Una auditoria completa de 404.054 parejas demuestra cardinalidad minima de
  rescate exactamente dos en 69/126 estratos de conectividad de vertices y
  68/139 estratos de conectividad de aristas. Los minimos restantes solo quedan
  acotados como mayores o iguales que tres; las ternas de Fase 104 no se han
  ejecutado y no aportan resultados a esta version.

Las afirmaciones estan limitadas deliberadamente. Las aristas Q8 representan
intervenciones Hamming-1 sobre la palabra inicial central de ocho bits, no
transiciones temporales del automata celular. La ley exacta cubre 219 objetivos
dentro de 48 hipercubos congelados y no constituye un teorema universal.

Todos los resultados son deterministas y reproducibles mediante scripts,
manifiestos, ledgers compactos, informes y pruebas comprometidos en el
repositorio.

Repositorio:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Keywords

- elementary cellular automata
- empirical law discovery
- complex systems
- periodic backgrounds
- basin topology
- graph connectivity
- causal audit
- reproducible computational science

## Related work

- **Is supplement to / Software:** https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- **Repository URL:** https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- **Programming language:** Python
- **Development status:** Active

## File gate

- **Upload filename:** `zuse_preprint.pdf`
- **Expected local source:** `paper/zuse_preprint.pdf`
- **File size:** `1,025,045 bytes`
- **Pages:** `59`
- **MD5:** `2516656a558e1fc0c7690d51abef2656`
- **SHA-256:** `22644346bc11807661d0e7c23e8e2f068bb100d2ab77d5a8589c19314a3e9747`
- **Version DOI:** `10.5281/zenodo.21935967`
- **Series DOI:** `10.5281/zenodo.21935966`
