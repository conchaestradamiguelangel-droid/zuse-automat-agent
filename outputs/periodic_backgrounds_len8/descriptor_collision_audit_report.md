# Fase 33: Descriptor Collision Audit for T=15

## Question

Fase 32 validated `rule + subpatterns_len4 + IC/background alignment` on rotations of the 20 known T=15 representatives. Fase 33 asks whether there are unseen length-8 backgrounds with the same `subpatterns_len4` descriptor that could provide an external validation target.

## Collision summary

| universe | k | necklaces | buckets | ambiguous buckets | max collision |
| --- | ---: | ---: | ---: | ---: | ---: |
| all binary len-8 | 2 | 36 | 18 | 8 | 5 |
| all binary len-8 | 3 | 36 | 27 | 8 | 3 |
| all binary len-8 | 4 | 36 | 34 | 2 | 2 |
| primitive non-zero len-8 | 2 | 30 | 15 | 8 | 4 |
| primitive non-zero len-8 | 3 | 30 | 23 | 6 | 3 |
| primitive non-zero len-8 | 4 | 30 | 28 | 2 | 2 |

## Length-4 ambiguous necklaces

Across all binary length-8 necklaces, only two `subpatterns_len4` collisions exist:

- `00110111, 00111011`
- `00010011, 00011001`

The same two collisions also occur inside the primitive non-zero universe:

- `00110111, 00111011`
- `00010011, 00011001`

## Known T=15 descriptor buckets

| rule | descriptor buckets | external same-descriptor backgrounds |
| ---: | ---: | ---: |
| 73 | 9 | 0 |
| 109 | 9 | 0 |

The only T=15 descriptor collisions are family-preserving:

- rule `73`: `00110111`, `00111011`; family-preserving: `yes`
- rule `109`: `00010011`, `00011001`; family-preserving: `yes`

## Verdict

**Status:** `NO_UNSEEN_SAME_DESCRIPTOR_BACKGROUND`.

**Verdict:** `FAMILY_SAFE_COLLISIONS_ONLY`.

There is no unseen length-8 background, outside rotations of the known representatives, that shares the T=15 `subpatterns_len4` descriptor under the same rule. Therefore the natural external validation test proposed after Fase 32 is impossible inside the length-8 background universe.

The two length-4 descriptor collisions that do exist are already inside the confirmed T=15 set and preserve the defect-cycle family. This supports the descriptor as a family identifier, but it also means that further generalization requires a larger background universe, such as primitive length-9/10 backgrounds or a symbolic proof over circular words.

## Falsifiable implication

Any future length-8 counterexample must either break the collision audit above or use a descriptor different from `subpatterns_len4`. For external prediction, the next empirical test must leave the length-8 universe.
