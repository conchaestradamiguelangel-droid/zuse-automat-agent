# Fase 56: rule_109 Symmetry and Orbit Structure Audit

## Question

Why do the non-T15 ANF-gradient witnesses found in Fase 55 concentrate in
`rule_109` rather than spreading across the full `rule_73/rule_109` family
or the external rules in the catalog?

This audit performs no new ANF simulation. It uses the Fase 55 census JSON
and analyzes background rotations/complements, rule-level ANF, and direct
cross-rule comparisons.

## Status

- `orbit_symmetry_status`: `PARTIAL`
- `rule_anf_status`: `RULE109_CENTER_MEDIATED_CONFIRMED`
- `cross_rule_status`: `RULE109_SPECIFIC_ON_SHARED_BACKGROUNDS`
- `overall_status`: `RULE109_SYMMETRY_MECHANISM_CANDIDATE`

## Positive Cases from Fase 55

| case | category | canonical rotation | complement in census |
| --- | --- | --- | --- |
| `rule_109/bg=0011/T=12/word=10010100` | `NATURAL_PERIOD_STRONG` | `0011` | `1100` -> `NATURAL_PERIOD_STRONG` |
| `rule_109/bg=0110/T=8/word=0000011` | `HORIZON_ACCEPTABLE` | `0011` | `1001` -> absent |
| `rule_109/bg=1011/T=10/word=00000001` | `HORIZON_ACCEPTABLE` | `0111` | `0100` -> absent |
| `rule_109/bg=1100/T=8/word=00000110` | `HORIZON_ACCEPTABLE` | `0011` | `0011` -> `NEGATIVE` |
| `rule_109/bg=1100/T=12/word=00101001` | `NATURAL_PERIOD_STRONG` | `0011` | `0011` -> `NATURAL_PERIOD_STRONG` |

## Rotation Orbits

### `rule_109/bg=0011/T=12`
- `0011`: `NATURAL_PERIOD_STRONG` (word `10010100`)
- `0110`: absent from census
- `1100`: `NATURAL_PERIOD_STRONG` (word `00101001`)
- `1001`: absent from census

### `rule_109/bg=0110/T=8`
- `0110`: `HORIZON_ACCEPTABLE` (word `0000011`)
- `1100`: `HORIZON_ACCEPTABLE` (word `00000110`)
- `1001`: absent from census
- `0011`: `NEGATIVE` (word `1000010`)

### `rule_109/bg=1011/T=10`
- `1011`: `HORIZON_ACCEPTABLE` (word `00000001`)
- `0111`: absent from census
- `1110`: absent from census
- `1101`: `NEGATIVE` (word `0001000`)

### `rule_109/bg=1100/T=8`
- `1100`: `HORIZON_ACCEPTABLE` (word `00000110`)
- `1001`: absent from census
- `0011`: `NEGATIVE` (word `1000010`)
- `0110`: `HORIZON_ACCEPTABLE` (word `0000011`)

### `rule_109/bg=1100/T=12`
- `1100`: `NATURAL_PERIOD_STRONG` (word `00101001`)
- `1001`: absent from census
- `0011`: `NATURAL_PERIOD_STRONG` (word `10010100`)
- `0110`: absent from census

## Rule-Level ANF

| rule | ANF expression | center alone? | LR without center? | center monomials |
| ---: | --- | --- | --- | --- |
| 73 | `1 XOR L XOR C XOR R XOR LR XOR LCR` | `True` | `True` | `['C', 'LCR']` |
| 109 | `1 XOR L XOR LC XOR R XOR CR XOR LCR` | `False` | `False` | `['LC', 'CR', 'LCR']` |

`rule_109` has no isolated center monomial and no `LR` monomial without
the center. Its center dependence appears only through interactions
(`LC`, `CR`, `LCR`). By contrast, `rule_73` contains `C` alone and `LR`
without the center.

## Cross-Rule Comparisons

| rule_109 positive case | matching rule_73 case |
| --- | --- |
| `rule_109/bg=0011/T=12/word=10010100` -> `NATURAL_PERIOD_STRONG` | `rule_73/bg=0011/T=12/word=10001010` -> `NEGATIVE` |
| `rule_109/bg=0110/T=8/word=0000011` -> `HORIZON_ACCEPTABLE` | absent from census |
| `rule_109/bg=1011/T=10/word=00000001` -> `HORIZON_ACCEPTABLE` | absent from census |
| `rule_109/bg=1100/T=8/word=00000110` -> `HORIZON_ACCEPTABLE` | `rule_73/bg=1100/T=8/word=0011111` -> `NEGATIVE` |
| `rule_109/bg=1100/T=12/word=00101001` -> `NATURAL_PERIOD_STRONG` | `rule_73/bg=1100/T=12/word=00000011` -> `NEGATIVE` |

## Interpretation

The cyclic-orbit evidence is partial: several witnesses lie in the rotation
orbit of `0011`, but the `rule_109/bg=1011/T10` baseline belongs to a
different rotation orbit. The algebraic contrast is sharper: `rule_109`
mediates center dependence through neighbor interactions, whereas
`rule_73` has direct center and neighbor-only terms. The cross-rule table
shows that where matching `rule_73` cases exist on the same backgrounds
and periods, they do not become positive witnesses.

This supports a rule_109-specific mechanism candidate, but it is not a
closed proof: background orbit structure and rule-level ANF both appear
relevant.