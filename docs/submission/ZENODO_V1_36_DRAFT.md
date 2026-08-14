# Zenodo v1.36 Draft

Texto preparado para la publicacion manual en Zenodo. No rellenar el DOI, el
tamano ni las sumas de verificacion hasta que el PDF candidato pase la revision
independiente final.

## Orden de carga

1. Crear un nuevo registro de Zenodo para la version v1.36.
2. Arrastrar unicamente `paper/zuse_preprint.pdf` y comprobar que Zenodo muestra
   `zuse_preprint.pdf` con `1,028,156 bytes` antes de continuar.
3. En "¿Ya tienes un DOI?", dejar el campo vacio: Zenodo debe reservar uno nuevo.
4. Seleccionar **Preprint** como tipo de recurso.
5. Completar titulo, fecha, creador, descripcion, licencia y campos recomendados
   exactamente como aparecen debajo.
6. En trabajos relacionados, anadir el repositorio con relacion
   **Is supplement to / Es suplemento de** y esquema URL.
7. Mantener visibilidad publica, sin embargo, y revisar que solo exista un PDF.
8. No pulsar **Publicar** hasta que la revision independiente confirme que el
   nombre, tamano, 59 paginas, MD5 y SHA-256 coinciden con el control final.
9. Despues de publicar, copiar el DOI de version y el DOI de serie. Esos dos
   valores se usaran para actualizar `CITATION.cff`, `README.md`, el tag v1.36
   y la GitHub Release en un commit posterior separado.

## Informacion basica

- **Tipo de recurso:** Preprint
- **Titulo:** ZUSE Automat Agent: Empirical Law Discovery in Elementary Cellular Automata
- **Fecha de publicacion:** `2026-08-14`
- **Creador:** Miguel Angel Concha Estrada
- **Afiliacion:** Independent researcher
- **Version:** v1.36
- **Editor:** Zenodo
- **Idioma:** English
- **Licencia:** Creative Commons Attribution 4.0 International
- **Copyright:** Copyright (C) 2026 The author.

## Descripcion

La version v1.36 completa la auditoria de cardinalidad minima iniciada en
v1.35. Esta version incorpora las Fases 104--105 y no repite ni modifica el
censo de 5.783.040 configuraciones. Reutiliza los 48 hipercubos Q8 congelados y
extiende la ley exacta de cobertura de cortes desde intervenciones unitarias y
parejas hasta ternas y cuartetos.

Resultados principales:

- La Fase 104 enumera exhaustivamente 3.061.466 ternas en los 73 estratos que
  seguian sin resolverse despues de la auditoria de parejas.
- La cardinalidad minima es exactamente tres en 41/57 estratos de conectividad
  de vertices y 40/71 estratos de conectividad de aristas, con 180 y 192 ternas
  rescatadoras respectivamente.
- La Fase 105 enumera exhaustivamente 24.362.850 cuartetos en los 32 estratos
  restantes, con 20.638.850 ensayos de vertices y 19.941.575 de aristas.
- Todos los estratos restantes quedan resueltos con cardinalidad minima
  exactamente cuatro: 16/16 para vertices y 31/31 para aristas. No queda ningun
  estrato acotado como mayor o igual que cinco.
- La particion final de minimos en los estratos colectivos es 69/41/16 para
  vertices y 68/40/31 para aristas en cardinalidades 2/3/4.
- Se encuentran 77 cuartetos rescatadores de conectividad de vertices y 103 de
  aristas. Todos requieren al menos una arista Hamming-1 interna entre los
  cuatro estados anadidos.
- La retirada exhaustiva de cortes y un calculo independiente de flujo maximo
  coinciden sin excepciones. La decodificacion independiente del ledger de
  24.362.850 registros reproduce todos los agregados y no detecta bits
  reservados, fuera de alcance ni discrepancias entre rutas.

Las afirmaciones estan limitadas deliberadamente. Las aristas Q8 representan
intervenciones Hamming-1 sobre la palabra inicial central de ocho bits, no
transiciones temporales del automata celular. El cierre de cardinalidad 2--4
se aplica unicamente a los estratos, objetivos y poblaciones congelados del
protocolo; no constituye un limite universal para otros automatas, longitudes
de palabra, cuencas o familias de intervencion.

Todos los resultados son deterministas y reproducibles mediante scripts,
manifiestos, ledgers compactos, informes y pruebas comprometidos en el
repositorio.

Repositorio:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Palabras clave

- elementary cellular automata
- empirical law discovery
- complex systems
- basin topology
- graph connectivity
- minimum cardinality
- Hamming intervention
- reproducible computational science

## Trabajos relacionados

- **Es suplemento de / Software:** https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- **URL del repositorio:** https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- **Lenguaje de programacion:** Python
- **Estado de desarrollo:** Active

## Control del archivo

- **Nombre para subir:** `zuse_preprint.pdf`
- **Origen local esperado:** `paper/zuse_preprint.pdf`
- **Tamano:** `1,028,156 bytes`
- **Paginas:** `59`
- **MD5:** `b4dd0183c0cacf42b1e28ab9903fece5`
- **SHA-256:** `082812f1055acabe492ab9e85f95e6520a573e07822479ac3c380ecb11a6182d`
- **DOI de version:** `TBD after Zenodo publication`
- **DOI de serie:** `TBD after Zenodo publication`
