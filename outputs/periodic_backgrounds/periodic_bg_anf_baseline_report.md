# Fase 52: Periodic-Background ANF Baseline

## Question

Does the `T=15` ANF gradient appear in wide stationary local oscillators
over nontrivial periodic backgrounds with `T_local != 15`?

The primary verdict uses the common comparison horizon `T_WINDOW=12`,
`WINDOW_CELLS=25`. Each case is also evaluated at its own `T_local` when
`T_local != 12`. The ANF output is the localized XOR defect relative to the
periodic background orbit, matching the `T=15` convention.

## Summary

Status: `ANF_GRADIENT_MECHANISM_DEPENDENT`.

Periodic-background cases show mixed or insufficient active-output gradient evidence.

## Case table

| label | role | rule | background | IC | T_local | T_WINDOW | span | active | active dist count | active degree | active monomials | active log fit | nonconstant | nonconstant log fit |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- | ---: | --- |
| main_rule73_T10 | main | 73 | `0010` | `1110111` | 10 | 10 | 13 | 7 | 4 | [17, 21] | [137850, 1043090] | slope=-0.203651, intercept=6.232691, R^2=0.880488, reliable=yes | 25 | slope=-0.284093, intercept=6.459348, R^2=0.983864, reliable=yes |
| main_rule73_T10 | main | 73 | `0010` | `1110111` | 10 | 12 | 13 | 4 | 2 | [20, 23] | [482356, 4474733] | slope=-0.322466, intercept=7.295700, R^2=1.000000, reliable=no | 25 | slope=-0.310917, intercept=7.246698, R^2=0.997313, reliable=yes |
| secondary_rule109_T10 | secondary | 109 | `1011` | `00000001` | 10 | 10 | 13 | 7 | 4 | [17, 21] | [138594, 1113670] | slope=-0.196127, intercept=6.207426, R^2=0.922575, reliable=yes | 25 | slope=-0.302719, intercept=6.541847, R^2=0.977563, reliable=yes |
| secondary_rule109_T10 | secondary | 109 | `1011` | `00000001` | 10 | 12 | 13 | 7 | 4 | [20, 24] | [529108, 17758052] | slope=-0.307674, intercept=7.258688, R^2=0.999349, reliable=yes | 25 | slope=-0.323747, intercept=7.316418, R^2=0.990738, reliable=yes |
| period_control_rule73_T12 | period_control | 73 | `0011` | `10001010` | 12 | 12 | 12 | 7 | 5 | [18, 23] | [237918, 4474734] | slope=-0.296180, intercept=7.169455, R^2=0.877281, reliable=yes | 25 | slope=-0.355999, intercept=7.415210, R^2=0.807957, reliable=yes |
| low_period_control_rule94_T3 | low_period_control | 94 | `0010` | `1000101` | 3 | 3 | 13 | 8 | 6 | [6, 6] | [54, 55] | slope=0.000523, intercept=1.734615, R^2=0.049180, reliable=yes | 25 | slope=-0.051884, intercept=1.928403, R^2=0.494257, reliable=yes |
| low_period_control_rule94_T3 | low_period_control | 94 | `0010` | `1000101` | 3 | 12 | 13 | 8 | 6 | [18, 24] | [255578, 15830594] | slope=-0.341994, intercept=7.391120, R^2=0.955626, reliable=yes | 25 | slope=-0.375990, intercept=7.480598, R^2=0.944952, reliable=yes |

## Common-horizon reading

At `T_WINDOW=12`, all four cases have multiple active distance classes,
so unlike Fases 50--51 the gradient test is not blocked by compact active
support. The result therefore probes mechanism specificity rather than
only support width.

## Motifs

### main_rule73_T10

```text
####.###.####
#..#...#..#
######.######
#.##...##.#
###..#.#..###
#.###.###.#
###...#...###
#.#.###.#.#
####..#..####
#..#####..#
```

Packed/concrete consistency: `True`.

### secondary_rule109_T10

```text
####..#..####
#..#####..#
####.###.####
#..#...#..#
######.######
#.##...##.#
###..#.#..###
#.###.###.#
###...#...###
#.#.###.#.#
```

Packed/concrete consistency: `True`.

### period_control_rule73_T12

```text
#.#.###.##
##.#..#....#
#.#.###..##
##.#..#..##
#.#.####..#
##.#..##.###
#.#.##...#
##.#...#.###
#.#..##..#
##.#.##..###
#.#...##.#
##.#..#...##
```

Packed/concrete consistency: `True`.

### low_period_control_rule94_T3

```text
#.#.###...###
#.####...###
##..###...###
```

Packed/concrete consistency: `True`.
