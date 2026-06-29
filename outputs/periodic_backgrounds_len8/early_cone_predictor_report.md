# Fase 40: Early Causal-Cone Predictor

## Question

Fase 39 found no compact algebraic pre-burn-in predictor of the
`T=15` entry phase. Fase 40 tests a weaker but constructive hypothesis:
can the post-burn-in stable-cycle state be recovered by simulating only
the local causal cone of the initial IC for `t = 3, 6, 9, 12`, rather
than the full 256-cell system through the 81-step burn-in?

Two local windows are tested:

- `span`: the full IC span plus a causal margin of `t` cells on each side;
- `center`: the strict `2t+1` window around the IC center.

When a cone state lands on one of the five stable-cycle states, its phase
is projected forward to `t=81` before comparison with `defect_state0`.

## Summary

| mode | t_window | stable hits | full-t matches | entry matches | projected sample matches | direct sample matches | compression range | success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| span | 3 | 17/20 | 20/20 | 15/20 | 17/20 | 0/20 | 493.7x..864.0x | `False` |
| span | 6 | 18/20 | 20/20 | 1/20 | 18/20 | 18/20 | 172.8x..246.9x | `False` |
| span | 9 | 19/20 | 20/20 | 1/20 | 19/20 | 0/20 | 88.6x..115.2x | `False` |
| span | 12 | 20/20 | 20/20 | 1/20 | 20/20 | 0/20 | 54.0x..66.5x | `True` |
| center | 3 | 0/20 | 0/20 | 0/20 | 0/20 | 0/20 | 987.4x..987.4x | `False` |
| center | 6 | 2/20 | 3/20 | 0/20 | 2/20 | 2/20 | 265.8x..265.8x | `False` |
| center | 9 | 17/20 | 17/20 | 1/20 | 17/20 | 0/20 | 121.3x..121.3x | `False` |
| center | 12 | 20/20 | 20/20 | 1/20 | 20/20 | 0/20 | 69.1x..69.1x | `True` |

## Family fallback

| mode | t_window | descriptor | buckets | ambiguous buckets | determines family |
| --- | ---: | --- | ---: | ---: | --- |
| span | 3 | `(rule, cone_state)` | 17 | 0 | `True` |
| span | 6 | `(rule, cone_state)` | 16 | 1 | `False` |
| span | 9 | `(rule, cone_state)` | 17 | 0 | `True` |
| span | 12 | `(rule, cone_state)` | 17 | 0 | `True` |
| center | 3 | `(rule, cone_state)` | 17 | 2 | `False` |
| center | 6 | `(rule, cone_state)` | 20 | 0 | `True` |
| center | 9 | `(rule, cone_state)` | 17 | 0 | `True` |
| center | 12 | `(rule, cone_state)` | 17 | 0 | `True` |

## Representative table

| family | rule | background | IC | entry t | entry phase | span t=3 | span t=6 | span t=9 | span t=12 |
| --- | ---: | --- | --- | ---: | ---: | --- | --- | --- | --- |
| `F00` | 109 | `00001001` | `0001001` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F00` | 109 | `00010011` | `01001` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F00` | 109 | `00011001` | `01` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F01` | 73 | `00110111` | `011011` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F01` | 73 | `00111011` | `00100100` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F01` | 73 | `01101111` | `01101110` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F02` | 73 | `00001111` | `00100000` | 9 | 1 | not stable | not stable | phase 1 -> ok | phase 2 -> ok |
| `F02` | 73 | `00111111` | `0001100` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F02` | 109 | `00001101` | `0100001` | 6 | 0 | not stable | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F03` | 73 | `00110101` | `011010` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F03` | 109 | `00110101` | `010101` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F04` | 73 | `00101111` | `0000111` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F05` | 109 | `00001011` | `0001001` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F06` | 73 | `00101101` | `010110` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F07` | 109 | `00111111` | `00111111` | 0 | 3 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F08` | 109 | `00001111` | `0001001` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F09` | 73 | `00000011` | `0000011` | 0 | 3 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F10` | 73 | `00001001` | `00110010` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F11` | 109 | `01101111` | `0101001` | 3 | 4 | phase 4 -> ok | phase 0 -> ok | phase 1 -> ok | phase 2 -> ok |
| `F12` | 109 | `00000011` | `1110101` | 12 | 2 | not stable | not stable | not stable | phase 2 -> ok |

## Verdict

**Status:** `EARLY_CONE_PREDICTOR_FOUND`.

The early causal-cone predictor succeeds. The smallest successful
configuration is `center` at `t=12`, with a
compression range of 69.1x..69.1x relative to the full
256 x 81 simulation. This converts the negative Fase 39 result
into a constructive causal compression: no compact closed-form
descriptor was found, but the relevant state can be recovered by
a short local simulation.
