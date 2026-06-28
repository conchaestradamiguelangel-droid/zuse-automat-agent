# Fase 37: Canonical Background Orbit vs T=15 Families

## Question

Fase 36 explained the F00 table identity by convergence to the same
spatially canonical period-3 background orbit. Fase 37 tests whether this
generalizes to all 20 minimal T=15 representatives.

Candidate background invariant:

```text
(rule, canonical_period3_orbit)
```

## Family -> rule/orbit mapping

| family | members | rules | rule/orbit keys | one rule/orbit | backgrounds |
| --- | ---: | --- | ---: | --- | --- |
| `F00` | 3 | `109` | 1 | `True` | `00001001`, `00010011`, `00011001` |
| `F01` | 3 | `73` | 1 | `True` | `00110111`, `00111011`, `01101111` |
| `F02` | 3 | `73, 109` | 2 | `False` | `00001111`, `00111111`, `00001101` |
| `F03` | 2 | `73, 109` | 2 | `False` | `00110101`, `00110101` |
| `F04` | 1 | `73` | 1 | `True` | `00101111` |
| `F05` | 1 | `109` | 1 | `True` | `00001011` |
| `F06` | 1 | `73` | 1 | `True` | `00101101` |
| `F07` | 1 | `109` | 1 | `True` | `00111111` |
| `F08` | 1 | `109` | 1 | `True` | `00001111` |
| `F09` | 1 | `73` | 1 | `True` | `00000011` |
| `F10` | 1 | `73` | 1 | `True` | `00001001` |
| `F11` | 1 | `109` | 1 | `True` | `01101111` |
| `F12` | 1 | `109` | 1 | `True` | `00000011` |

## Rule/orbit -> family mapping

| rule/orbit key | members | families | one family | backgrounds |
| --- | ---: | --- | --- | --- |
| `109:b2f2515010581b5b` | 10 | `F00, F02, F03, F05, F07, F08, F11, F12` | `False` | `00001001`, `00010011`, `00011001`, `00001101`, `00110101`, `00001011`, `00111111`, `00001111`, `01101111`, `00000011` |
| `73:7fa678d693b74ab5` | 10 | `F01, F02, F03, F04, F06, F09, F10` | `False` | `00110111`, `00111011`, `01101111`, `00001111`, `00111111`, `00110101`, `00101111`, `00101101`, `00000011`, `00001001` |

## Summary

- Records: `20`.
- Shape families: `13`.
- Rule-conditioned canonical orbit keys: `2`.
- Canonical orbit sets ignoring rule: `2`.
- Families with more than one rule/orbit key: `2`.
- Rule/orbit keys mapping to more than one family: `2`.

## Verdict

**Status:** `CANONICAL_ORBIT_NOT_ENOUGH`.

The rule-conditioned canonical background orbit is not sufficient by itself. It collapses the 20 representatives to two keys, one for `rule_73` and one for `rule_109`, while those keys map to many shape families. Therefore the missing information is not the asymptotic background orbit but the IC/background alignment and local embedding of the defect inside that orbit.

Families split by rule/orbit key:
- `F02` -> 109:b2f2515010581b5b, 73:7fa678d693b74ab5
- `F03` -> 109:b2f2515010581b5b, 73:7fa678d693b74ab5

Ambiguous rule/orbit keys:
- `109:b2f2515010581b5b` -> F00, F02, F03, F05, F07, F08, F11, F12
- `73:7fa678d693b74ab5` -> F01, F02, F03, F04, F06, F09, F10
