# Fase 36: F00 Exact Transition-Table Identity

## Question

Fase 35 found that family F00 is exceptional: three distinct rule_109
backgrounds share the same exact five-phase transition-table signature.
Fase 36 isolates that identity and asks whether it is a real local
algebraic identity rather than a restatement of equal background orbits
or equal length-4 subpattern descriptors.

## Members

| background | IC | subpatterns_len4 hash | temporal orbit period | transition signature |
| --- | --- | --- | ---: | --- |
| `00001001` | `0001001` | `96c325847fe25551` | 3 | `5d998c548b2ade56` |
| `00010011` | `01001` | `0ca7f003f6de142e` | 3 | `5d998c548b2ade56` |
| `00011001` | `01` | `0ca7f003f6de142e` | 3 | `5d998c548b2ade56` |

## Identity checks

- Exact five-phase transition-table sequence identical: `True`.
- Phase-canonical transition-table sequence identical: `True`.
- Full compact local induced tables identical: `True`.
- Identical microtables: `15/15`.
- Distinct `subpatterns_len4` buckets among F00 members: `2`.
- Distinct raw background temporal cycles among F00 members: `3`.
- Distinct spatially canonical background cycle sets: `1`.

The three representatives therefore do not share the same length-4
subpattern descriptor, and their raw temporal cycles are shifted by
different preperiods/phases. However, after spatial canonicalization they
share the same period-3 background cycle set. The identical local
transition table is therefore explained by convergence to the same
effective background orbit before the defect is sampled.

## Background temporal orbits

### `00001001`

- preperiod: `0`
- period: `3`
- cycle: `00001001`, `01101001`, `11111001`
- canonical cycle rotations: `00001001`, `00101101`, `00111111`
- canonical cycle set: `00001001`, `00101101`, `00111111`

### `00010011`

- preperiod: `2`
- period: `3`
- cycle: `11110011`, `00010010`, `11010010`
- canonical cycle rotations: `00111111`, `00001001`, `00101101`
- canonical cycle set: `00001001`, `00101101`, `00111111`

### `00011001`

- preperiod: `2`
- period: `3`
- cycle: `11111001`, `00001001`, `01101001`
- canonical cycle rotations: `00111111`, `00001001`, `00101101`
- canonical cycle set: `00001001`, `00101101`, `00111111`

## Verdict

**Status:** `F00_EXACT_TABLE_IDENTITY`.

The F00 identity is stronger than a shape-family coincidence, but it is
not mysterious: the three initial backgrounds enter the same spatially
canonical period-3 background cycle before the sampled T=15 defect orbit.
They then induce the exact same sequence of 15 local microtables over the
five `F^3` transitions. This also shows that the v1.8 length-4 descriptor
was sufficient but not minimal for F00: two different `subpatterns_len4`
buckets collapse to the same effective background cycle and table.
