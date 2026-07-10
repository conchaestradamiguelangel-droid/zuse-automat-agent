# Fase 50: rule_108 T=2 ANF Baseline

## Question

Does the ANF gradient observed for the `T=15` mechanism also appear in
the cleanest known stationary local oscillator: `rule_108` on a quiescent
zero background with IC `101` and local period `T=2`?

The primary horizon is `T_WINDOW=12`, `WINDOW_CELLS=25`: this is a common
comparison horizon against the `T=15` cone, not the minimal T=2 cone.
The secondary control is the minimal `T_WINDOW=2`, `WINDOW_CELLS=5` cone.

## Summary

Status: `ANF_GRADIENT_T15_SPECIFIC`.

The concrete active T=2 oscillator support spans too few distances for a T=15-like active-output gradient.

## Horizon table

| T_WINDOW | window cells | final active | active dist count | active degree | active monomials | active log fit | nonconstant count | nonconstant log fit |
| ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- |
| 12 | 25 | 2 | 1 | [3, 3] | [4, 4] | not enough support | 25 | slope=-0.030015, intercept=0.717103, R^2=0.379256, reliable=yes |
| 2 | 5 | 2 | 1 | [3, 3] | [2, 2] | not enough support | 5 | slope=-0.301030, intercept=0.602060, R^2=1.000000, reliable=yes |

## Concrete orbit

### T_WINDOW=12

```text
...........#.#...........
...........###...........
...........#.#...........
...........###...........
...........#.#...........
...........###...........
...........#.#...........
...........###...........
...........#.#...........
...........###...........
...........#.#...........
...........###...........
...........#.#...........
```

Packed/concrete consistency: `True`.

### T_WINDOW=2

```text
.#.#.
.###.
.#.#.
```

Packed/concrete consistency: `True`.

## Interpretation

The `rule_108` oscillator is a genuine stationary local period-2 witness,
but its concrete active support is extremely small: the final even phase
has two active cells (`#.#`) and the odd phase has three (`###`). Under
the primary 25-cell, 12-step comparison cone, the concrete active outputs
occupy only one distance class from the center. This is not enough support
for a spatial active-output gradient comparable to the `T=15` ANF law.

The script also reports all nonconstant cone outputs as a diagnostic, but
the scientific verdict is based on the concrete active oscillator support,
matching the active-output convention used in the `T=15` ANF audits.
