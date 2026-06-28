# Fase 35: Explicit Transition Tables for the T=15 Five-Cycle

## Question

For each of the 20 minimal T=15 representatives, build the explicit
local transition-table signature used by the three-step macro-map F^3,
then test whether those signatures coincide with the 13 Fase-30 shape
families.

## Representative signatures

| rule | background | family | signature | phase-canonical signature |
| ---: | --- | --- | --- | --- |
| 109 | `00001001` | `F00` | `5d998c548b2ade56` | `b8ae000d074b6b57` |
| 109 | `00010011` | `F00` | `5d998c548b2ade56` | `b8ae000d074b6b57` |
| 109 | `00011001` | `F00` | `5d998c548b2ade56` | `b8ae000d074b6b57` |
| 73 | `00110111` | `F01` | `53100f5e831d1ff6` | `88942ac61dbab7e6` |
| 73 | `00111011` | `F01` | `88942ac61dbab7e6` | `88942ac61dbab7e6` |
| 73 | `01101111` | `F01` | `53100f5e831d1ff6` | `88942ac61dbab7e6` |
| 73 | `00001111` | `F02` | `8ee1eb1169e22cf1` | `b9b429cd2c90b036` |
| 73 | `00111111` | `F02` | `83ac2e2fcf292439` | `b9b429cd2c90b036` |
| 109 | `00001101` | `F02` | `6159ba02bdcf0ef5` | `6159ba02bdcf0ef5` |
| 73 | `00110101` | `F03` | `c92537cea90fa1c3` | `236a124d13d1c701` |
| 109 | `00110101` | `F03` | `7e541566dfe931d6` | `15bab5eb54ad91bb` |
| 73 | `00101111` | `F04` | `48559cfa7f567775` | `2a78870f9626666b` |
| 109 | `00001011` | `F05` | `3c2492ae68ec8436` | `3c2492ae68ec8436` |
| 73 | `00101101` | `F06` | `32bcbf08f25b9af0` | `91b7171b2c93ee2a` |
| 109 | `00111111` | `F07` | `78e6c748ec71dbf9` | `4a0faa9f432369e5` |
| 109 | `00001111` | `F08` | `7c71bd590d4dd03e` | `dd11a56663197f98` |
| 73 | `00000011` | `F09` | `28d0b0b08d1e2e15` | `59072aabbcdddffa` |
| 73 | `00001001` | `F10` | `ad570c46783eef30` | `a4c0adc7ca1744c2` |
| 109 | `01101111` | `F11` | `ac5799d35773d20a` | `ac5799d35773d20a` |
| 109 | `00000011` | `F12` | `2d62c6c4eeef922a` | `6d7a1c0a8ae99be3` |

## Within-family comparison

| family | members | exact sequences | phase-canonical sequences | same up to phase rotation |
| --- | ---: | ---: | ---: | --- |
| `F00` | 3 | 1 | 1 | `True` |
| `F01` | 3 | 2 | 1 | `True` |
| `F02` | 3 | 3 | 2 | `False` |
| `F03` | 2 | 2 | 2 | `False` |
| `F04` | 1 | 1 | 1 | `True` |
| `F05` | 1 | 1 | 1 | `True` |
| `F06` | 1 | 1 | 1 | `True` |
| `F07` | 1 | 1 | 1 | `True` |
| `F08` | 1 | 1 | 1 | `True` |
| `F09` | 1 | 1 | 1 | `True` |
| `F10` | 1 | 1 | 1 | `True` |
| `F11` | 1 | 1 | 1 | `True` |
| `F12` | 1 | 1 | 1 | `True` |

## Descriptor-bucket comparison

| rule/subpatterns_len4 bucket members | families | same up to phase rotation | backgrounds |
| ---: | --- | --- | --- |
| 2 | `F01` | `True` | `00110111`, `00111011` |
| 2 | `F00` | `True` | `00010011`, `00011001` |

## Cross-family comparison

No phase-canonical transition-table signature is shared across different families.

## Verdict

**Status:** `TABLE_REFINES_FAMILY`.

No transition-table signature is shared across families, but at least one family splits into multiple table signatures. The table refines the Fase-30 shape-family partition.
