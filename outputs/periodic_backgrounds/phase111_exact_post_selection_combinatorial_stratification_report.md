# Fase 112 — Calibración combinatoria exacta posselección

**Veredicto:** `EXACT_POST_SELECTION_COMBINATORIAL_STRATIFICATION_CALIBRATED`

## Auditoría

- 223 rescates K2 en 101 instancias; 54 externos y 169 internos.
- Distribución n_i: 1→56, 2→18, 3→3, 4→14, 6→4, 7→6; n_i=5 ausente.
- Reconciliaciones de identidad, etiqueta y A_G entre tres fuentes: 0 discrepancias.
- Mapa conjunto exacto: 550 celdas; invariancia al orden confirmada.
- Masa DP: C(223,54), exacta y sin pérdida.

## Estratificación observada

- n_i=2: 0/18 mixtas; expectativa marginal nula=6.636287.
- n_i=3: 0/3 mixtas; expectativa marginal nula=1.659072.
- n_i=4: 14/14 mixtas; expectativa marginal nula=9.377853.
- n_i=6: 4/4 mixtas; expectativa marginal nula=3.257983.
- n_i=7: 6/6 mixtas; expectativa marginal nula=5.164463.

- Total observado fuera de X: 24 mixtas.
- Total esperado marginal fuera de X: 26.095657.
- D_obs: 1.000000.
- Masa de cola descriptiva posselección P(D≥D_obs): 38951964724584450553462327154355251113779200/2535528860474948942462906430600829326029052742647049 = 1.53624615881e-08.

## Errores certificados de Fase 111 por n_i

- n_i=4: EXT/INT=28/28; A_G∈{4,5}=44/56; errores=22/56.
- n_i=6: EXT/INT=6/18; A_G∈{4,5}=14/24; errores=12/24.
- n_i=7: EXT/INT=12/30; A_G∈{4,5}=18/42; errores=18/42.

## Límites

El estadístico, el umbral y la dirección de cola fueron seleccionados después de observar los resultados. La masa exacta es una calibración descriptiva posselección, no un p-valor confirmatorio ni un rechazo formal. No existe afirmación causal, predictiva, prospectiva o de generalización poblacional.
