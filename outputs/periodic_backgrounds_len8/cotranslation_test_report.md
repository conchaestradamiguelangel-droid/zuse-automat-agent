# Fase 25: Strict Co-Translation Equivariance Test

## Method

The 10 cases used in the Fase-24 rotation sub-test are rerun at translations
`k=0..7`. For a physical translation `+k`, the length-8 background word is
rotated **right** by `k` and the IC insertion center is moved to `center+k`.
This preserves the relative IC/background alignment. A left rotation combined
with `center+k` would move the two objects in opposite directions and would not
be a co-translation.

For every run, the test verifies:

1. the shifted background initial state equals the translated base background;
2. the full 301-frame background orbit equals the translated base orbit;
3. the initial perturbation difference equals the translated base difference;
4. the full 301-frame perturbation orbit equals the translated base orbit;
5. the detected signature `(kind, T, drift)` matches the Fase-24 signature.

Protocol parameters are unchanged: width 256, steps 300, burn-in 80, period
search 2..16, maximum active span 32.

## Summary

- Cases: `10`.
- Translations per case: `8`.
- Total runs: `80`.
- Physics-equivalent runs: `80/80`.
- Original linear-shape signature matches: `58/80`.
- Original linear-shape equivariant cases: `5/10`.
- Original failure reasons: `{"cyclic_wrap_linearization": 22}`.
- Circular-shape signature matches: `80/80`.
- Circular-shape equivariant cases: `10/10`.

| kind | rule | background | IC | T | drift | linear_match | circular_match | physics_ok | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| stationary | rule_62 | 00000001 | `1` | 3 | 0 | 8/8 | 8/8 | True | equivariant_after_circular_fix |
| stationary | rule_118 | 00000001 | `1` | 3 | 0 | 8/8 | 8/8 | True | equivariant_after_circular_fix |
| stationary | rule_131 | 00000011 | `1` | 3 | 0 | 8/8 | 8/8 | True | equivariant_after_circular_fix |
| stationary | rule_145 | 00000011 | `1` | 3 | 0 | 8/8 | 8/8 | True | equivariant_after_circular_fix |
| moving | rule_9 | 00001001 | `1000` | 3 | -2 | 4/8 | 8/8 | True | equivariant_after_circular_fix |
| moving | rule_65 | 00000001 | `1` | 3 | 2 | 4/8 | 8/8 | True | equivariant_after_circular_fix |
| moving | rule_111 | 00011111 | `1` | 3 | -2 | 4/8 | 8/8 | True | equivariant_after_circular_fix |
| moving | rule_125 | 00000011 | `1` | 3 | 2 | 4/8 | 8/8 | True | equivariant_after_circular_fix |
| moving | rule_45 | 00010011 | `001` | 6 | 6 | 2/8 | 8/8 | True | equivariant_after_circular_fix |
| stationary | rule_73 | 00001001 | `1` | 6 | 0 | 8/8 | 8/8 | True | equivariant_after_circular_fix |

## Per-Translation Results

### stationary rule_62

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00000001 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 1 | 10000000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 2 | 01000000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 3 | 00100000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 4 | 00010000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 5 | 00001000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 6 | 00000100 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 7 | 00000010 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
### stationary rule_118

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00000001 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 1 | 10000000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 2 | 01000000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 3 | 00100000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 4 | 00010000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 5 | 00001000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 6 | 00000100 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 7 | 00000010 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
### stationary rule_131

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00000011 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 1 | 10000001 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 2 | 11000000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 3 | 01100000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 4 | 00110000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 5 | 00011000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 6 | 00001100 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 7 | 00000110 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
### stationary rule_145

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00000011 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 1 | 10000001 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 2 | 11000000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 3 | 01100000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 4 | 00110000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 5 | 00011000 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 6 | 00001100 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
| 7 | 00000110 | True | True | True | True | stationary, T=3, drift=0 | - | True | stationary, T=3, drift=0 | True |
### moving rule_9

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00001001 | True | True | True | True | moving, T=3, drift=-2 | - | True | moving, T=3, drift=-2 | True |
| 1 | 10000100 | True | True | True | True | - | cyclic_wrap_linearization@t=203 | False | moving, T=3, drift=-2 | True |
| 2 | 01000010 | True | True | True | True | moving, T=3, drift=-2 | - | True | moving, T=3, drift=-2 | True |
| 3 | 00100001 | True | True | True | True | - | cyclic_wrap_linearization@t=206 | False | moving, T=3, drift=-2 | True |
| 4 | 10010000 | True | True | True | True | moving, T=3, drift=-2 | - | True | moving, T=3, drift=-2 | True |
| 5 | 01001000 | True | True | True | True | - | cyclic_wrap_linearization@t=209 | False | moving, T=3, drift=-2 | True |
| 6 | 00100100 | True | True | True | True | moving, T=3, drift=-2 | - | True | moving, T=3, drift=-2 | True |
| 7 | 00010010 | True | True | True | True | - | cyclic_wrap_linearization@t=212 | False | moving, T=3, drift=-2 | True |
### moving rule_65

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00000001 | True | True | True | True | moving, T=3, drift=2 | - | True | moving, T=3, drift=2 | True |
| 1 | 10000000 | True | True | True | True | - | cyclic_wrap_linearization@t=196 | False | moving, T=3, drift=2 | True |
| 2 | 01000000 | True | True | True | True | moving, T=3, drift=2 | - | True | moving, T=3, drift=2 | True |
| 3 | 00100000 | True | True | True | True | - | cyclic_wrap_linearization@t=193 | False | moving, T=3, drift=2 | True |
| 4 | 00010000 | True | True | True | True | moving, T=3, drift=2 | - | True | moving, T=3, drift=2 | True |
| 5 | 00001000 | True | True | True | True | - | cyclic_wrap_linearization@t=190 | False | moving, T=3, drift=2 | True |
| 6 | 00000100 | True | True | True | True | moving, T=3, drift=2 | - | True | moving, T=3, drift=2 | True |
| 7 | 00000010 | True | True | True | True | - | cyclic_wrap_linearization@t=187 | False | moving, T=3, drift=2 | True |
### moving rule_111

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00011111 | True | True | True | True | moving, T=3, drift=-2 | - | True | moving, T=3, drift=-2 | True |
| 1 | 10001111 | True | True | True | True | - | cyclic_wrap_linearization@t=202 | False | moving, T=3, drift=-2 | True |
| 2 | 11000111 | True | True | True | True | moving, T=3, drift=-2 | - | True | moving, T=3, drift=-2 | True |
| 3 | 11100011 | True | True | True | True | - | cyclic_wrap_linearization@t=205 | False | moving, T=3, drift=-2 | True |
| 4 | 11110001 | True | True | True | True | moving, T=3, drift=-2 | - | True | moving, T=3, drift=-2 | True |
| 5 | 11111000 | True | True | True | True | - | cyclic_wrap_linearization@t=208 | False | moving, T=3, drift=-2 | True |
| 6 | 01111100 | True | True | True | True | moving, T=3, drift=-2 | - | True | moving, T=3, drift=-2 | True |
| 7 | 00111110 | True | True | True | True | - | cyclic_wrap_linearization@t=211 | False | moving, T=3, drift=-2 | True |
### moving rule_125

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00000011 | True | True | True | True | moving, T=3, drift=2 | - | True | moving, T=3, drift=2 | True |
| 1 | 10000001 | True | True | True | True | - | cyclic_wrap_linearization@t=195 | False | moving, T=3, drift=2 | True |
| 2 | 11000000 | True | True | True | True | moving, T=3, drift=2 | - | True | moving, T=3, drift=2 | True |
| 3 | 01100000 | True | True | True | True | - | cyclic_wrap_linearization@t=192 | False | moving, T=3, drift=2 | True |
| 4 | 00110000 | True | True | True | True | moving, T=3, drift=2 | - | True | moving, T=3, drift=2 | True |
| 5 | 00011000 | True | True | True | True | - | cyclic_wrap_linearization@t=189 | False | moving, T=3, drift=2 | True |
| 6 | 00001100 | True | True | True | True | moving, T=3, drift=2 | - | True | moving, T=3, drift=2 | True |
| 7 | 00000110 | True | True | True | True | - | cyclic_wrap_linearization@t=186 | False | moving, T=3, drift=2 | True |
### moving rule_45

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00010011 | True | True | True | True | moving, T=6, drift=6 | - | True | moving, T=6, drift=6 | True |
| 1 | 10001001 | True | True | True | True | - | cyclic_wrap_linearization@t=126 | False | moving, T=6, drift=6 | True |
| 2 | 11000100 | True | True | True | True | - | cyclic_wrap_linearization@t=125 | False | moving, T=6, drift=6 | True |
| 3 | 01100010 | True | True | True | True | - | cyclic_wrap_linearization@t=124 | False | moving, T=6, drift=6 | True |
| 4 | 00110001 | True | True | True | True | - | cyclic_wrap_linearization@t=123 | False | moving, T=6, drift=6 | True |
| 5 | 10011000 | True | True | True | True | - | cyclic_wrap_linearization@t=122 | False | moving, T=6, drift=6 | True |
| 6 | 01001100 | True | True | True | True | moving, T=6, drift=6 | - | True | moving, T=6, drift=6 | True |
| 7 | 00100110 | True | True | True | True | - | cyclic_wrap_linearization@t=120 | False | moving, T=6, drift=6 | True |
### stationary rule_73

| k | shifted_background | bg0_shift | bg_orbit_shift | IC_diff_shift | XOR_orbit_shift | linear_signature | failure | linear_match | circular_signature | circular_match |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | 00001001 | True | True | True | True | stationary, T=6, drift=0 | - | True | stationary, T=6, drift=0 | True |
| 1 | 10000100 | True | True | True | True | stationary, T=6, drift=0 | - | True | stationary, T=6, drift=0 | True |
| 2 | 01000010 | True | True | True | True | stationary, T=6, drift=0 | - | True | stationary, T=6, drift=0 | True |
| 3 | 00100001 | True | True | True | True | stationary, T=6, drift=0 | - | True | stationary, T=6, drift=0 | True |
| 4 | 10010000 | True | True | True | True | stationary, T=6, drift=0 | - | True | stationary, T=6, drift=0 | True |
| 5 | 01001000 | True | True | True | True | stationary, T=6, drift=0 | - | True | stationary, T=6, drift=0 | True |
| 6 | 00100100 | True | True | True | True | stationary, T=6, drift=0 | - | True | stationary, T=6, drift=0 | True |
| 7 | 00010010 | True | True | True | True | stationary, T=6, drift=0 | - | True | stationary, T=6, drift=0 | True |

## Reanalysis of Fase-24 Background-Phase Dependence

The original Fase-24 phase test rotated the background while keeping the IC
fixed. Re-evaluating those same 80 runs with circular shape canonicalization
changes several moving-rule counts but does not remove phase dependence:
`0/10` cases are active in all eight phases.

| kind | rule | original_linear_match | circular_match |
| --- | --- | --- | --- |
| stationary | rule_62 | 7/8 | 7/8 |
| stationary | rule_118 | 7/8 | 7/8 |
| stationary | rule_131 | 6/8 | 6/8 |
| stationary | rule_145 | 6/8 | 6/8 |
| moving | rule_9 | 1/8 | 6/8 |
| moving | rule_65 | 1/8 | 6/8 |
| moving | rule_111 | 1/8 | 2/8 |
| moving | rule_125 | 1/8 | 5/8 |
| moving | rule_45 | 1/8 | 2/8 |
| stationary | rule_73 | 4/8 | 4/8 |

The stationary counts are unchanged. Moving-rule sensitivity was overstated by
the linear boundary artifact: for example, `rule_9` and `rule_65` rise from
`1/8` to `6/8`. Because no case reaches `8/8`, the remaining phase dependence
is physical IC/background alignment sensitivity.

## Conclusion

The ECA background and perturbation orbits are exactly co-translated. The original linear-shape preprocessing recovers 58/80 signatures because 22 moving runs straddle positions 255 and 0, inflating their linear span and causing rejection. A circular shape canonicalization that cuts at the largest empty arc and unwraps position continuously recovers 80/80 signatures and 10/10 cases. The physical detector is therefore equivariant after cyclic geometry is represented correctly; the observed failure is a boundary artifact of linear_shape.
