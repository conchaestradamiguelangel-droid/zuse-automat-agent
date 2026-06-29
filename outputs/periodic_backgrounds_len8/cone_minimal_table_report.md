# Fase 41: Minimal Table/Circuit Audit for the T=15 Cone

## Question

Fase 40 showed that a strict 25-cell cone simulated for 12 steps
recovers `defect_state0` in 20/20 minimal T=15 representatives. Fase 41
asks whether that cone has a smaller formal representation: fewer induced
local table entries, fewer ordinary ECA rule entries, or a pruned causal
dependency graph for the final localized defect.

## Global summary

- Representatives: 20.
- Cone size: 25 cells x 12 steps.
- Cone space-time nodes including t=0: 325.
- Full simulation baseline: 20736 cell-steps.
- Induced key count range: 49..62 of 64 possible `(b,d)->d_next` keys.
- Active-output initial variable range: 25..25 of 25 cone inputs.
- Active-output internal node range: 234..310 of 325 cone nodes.
- All ordinary ECA rule entries used in every representative: `True`.
- Active outputs need all 25 initial cone inputs: `True`.
- Induced tables are dense (minimum 49/64 keys): `True`.

The full 25-bit final vector has no causal pruning under this model: it
requires the full 25-cell-by-13-layer cone. The reductions below refer to
the active localized defect support, not to proving that every final zero
bit is zero.

## Representative table

| family | rule | background | IC | induced keys | ordinary entries | active final bits | active input vars | active nodes | compression vs full |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `F00` | 109 | `00001001` | `0001001` | 52 | 8 | 8 | 25 | 266 | 78.0x |
| `F00` | 109 | `00010011` | `01001` | 54 | 8 | 8 | 25 | 260 | 79.8x |
| `F00` | 109 | `00011001` | `01` | 54 | 8 | 8 | 25 | 270 | 76.8x |
| `F01` | 73 | `00110111` | `011011` | 54 | 8 | 8 | 25 | 260 | 79.8x |
| `F01` | 73 | `00111011` | `00100100` | 59 | 8 | 4 | 25 | 234 | 88.6x |
| `F01` | 73 | `01101111` | `01101110` | 52 | 8 | 8 | 25 | 266 | 78.0x |
| `F02` | 73 | `00001111` | `00100000` | 55 | 8 | 10 | 25 | 299 | 69.4x |
| `F02` | 73 | `00111111` | `0001100` | 62 | 8 | 14 | 25 | 310 | 66.9x |
| `F02` | 109 | `00001101` | `0100001` | 56 | 8 | 14 | 25 | 303 | 68.4x |
| `F03` | 73 | `00110101` | `011010` | 55 | 8 | 8 | 25 | 257 | 80.7x |
| `F03` | 109 | `00110101` | `010101` | 55 | 8 | 8 | 25 | 265 | 78.2x |
| `F04` | 73 | `00101111` | `0000111` | 52 | 8 | 7 | 25 | 281 | 73.8x |
| `F05` | 109 | `00001011` | `0001001` | 56 | 8 | 10 | 25 | 283 | 73.3x |
| `F06` | 73 | `00101101` | `010110` | 53 | 8 | 8 | 25 | 262 | 79.1x |
| `F07` | 109 | `00111111` | `00111111` | 55 | 8 | 6 | 25 | 258 | 80.4x |
| `F08` | 109 | `00001111` | `0001001` | 54 | 8 | 10 | 25 | 289 | 71.8x |
| `F09` | 73 | `00000011` | `0000011` | 55 | 8 | 6 | 25 | 258 | 80.4x |
| `F10` | 73 | `00001001` | `00110010` | 49 | 8 | 7 | 25 | 280 | 74.1x |
| `F11` | 109 | `01101111` | `0101001` | 55 | 8 | 10 | 25 | 285 | 72.8x |
| `F12` | 109 | `00000011` | `1110101` | 49 | 8 | 12 | 25 | 296 | 70.1x |

## Family table signatures

| family | members | induced table signatures | ordinary signatures |
| --- | ---: | ---: | ---: |
| `F00` | 3 | 3 | 1 |
| `F01` | 3 | 3 | 1 |
| `F02` | 3 | 3 | 1 |
| `F03` | 2 | 2 | 1 |
| `F04` | 1 | 1 | 1 |
| `F05` | 1 | 1 | 1 |
| `F06` | 1 | 1 | 1 |
| `F07` | 1 | 1 | 1 |
| `F08` | 1 | 1 | 1 |
| `F09` | 1 | 1 | 1 |
| `F10` | 1 | 1 | 1 |
| `F11` | 1 | 1 | 1 |
| `F12` | 1 | 1 | 1 |

## Verdict

**Status:** `STRUCTURAL_CONE_REDUCTION_ONLY`.

Fase 41 finds a structural circuit reduction, but not a sparse
truth-table or input-variable reduction. All eight ordinary ECA
rule entries are used in every representative, the induced
`(b,d)->d_next` tables are dense (49..62 of 64 keys), and the
active localized output still depends on all 25 initial cone
inputs. The only reduction is internal: computing the active final
defect support uses 234..310 internal cone nodes instead of all
325 nodes. Thus Fase 40's 25-cell cone is close to minimal at the
input level; the next symbolic target is not a smaller support, but
a Boolean simplification of the dense 25-input, 12-step circuit.
