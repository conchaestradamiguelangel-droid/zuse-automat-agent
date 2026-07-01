# Fase 44: ANF Degree Audit of the T=15 Cone

## Question

Fases 41-43 ruled out sparse local tables, input elimination, and simple
ROBDD variable-order compression. Fase 44 asks whether the same 25-input,
12-step cone is compact as an algebraic normal form (ANF) polynomial over
GF(2).

Truth tables are simulated exactly in bit-packed form. Each active output
is then unpacked and transformed with the Mobius transform to obtain ANF
coefficients.

## Summary

Status: `LOW_OUTPUT_ANF_DEGREE_FOUND`.

- Representatives: 20
- Active outputs analyzed: 174
- Active-output degree range: 14..24
- Active-output monomial range: 9376..17758052
- Full-degree representatives (degree 25): 0/20
- Low-degree outputs (<20): 67/174
- Representatives with at least one low-degree output: 20/20

## Representative table

| family | rule | background | active outputs | active degree | active monomials |
| --- | ---: | --- | ---: | --- | --- |
| `F09` | 73 | `00000011` | 6 | 17..24 | 120454..15954881 |
| `F10` | 73 | `00001001` | 7 | 18..23 | 118490..8239890 |
| `F02` | 73 | `00001111` | 10 | 14..24 | 11823..15954882 |
| `F06` | 73 | `00101101` | 8 | 18..24 | 118490..15954882 |
| `F04` | 73 | `00101111` | 7 | 18..23 | 119459..8444922 |
| `F03` | 73 | `00110101` | 8 | 16..24 | 62011..15954881 |
| `F01` | 73 | `00110111` | 8 | 16..23 | 39665..8239891 |
| `F01` | 73 | `00111011` | 4 | 19..23 | 232373..8444923 |
| `F02` | 73 | `00111111` | 14 | 14..23 | 9376..8444922 |
| `F01` | 73 | `01101111` | 8 | 17..24 | 53313..15954882 |
| `F12` | 109 | `00000011` | 12 | 14..24 | 12062..17758051 |
| `F00` | 109 | `00001001` | 8 | 17..24 | 63271..17758051 |
| `F05` | 109 | `00001011` | 10 | 17..24 | 63271..17758051 |
| `F02` | 109 | `00001101` | 14 | 15..24 | 15200..17758051 |
| `F08` | 109 | `00001111` | 10 | 17..24 | 63271..17758051 |
| `F00` | 109 | `00010011` | 8 | 16..23 | 23615..9332331 |
| `F00` | 109 | `00011001` | 8 | 17..23 | 126339..9332331 |
| `F03` | 109 | `00110101` | 8 | 19..24 | 271368..17758052 |
| `F07` | 109 | `00111111` | 6 | 17..24 | 115500..17758052 |
| `F11` | 109 | `01101111` | 10 | 18..24 | 140320..17758051 |

## Family summary

| family | reps | active degree | active monomials |
| --- | ---: | --- | --- |
| `F00` | 3 | 16..24 | 23615..17758051 |
| `F01` | 3 | 16..24 | 39665..15954882 |
| `F02` | 3 | 14..24 | 9376..17758051 |
| `F03` | 2 | 16..24 | 62011..17758052 |
| `F04` | 1 | 18..23 | 119459..8444922 |
| `F05` | 1 | 17..24 | 63271..17758051 |
| `F06` | 1 | 18..24 | 118490..15954882 |
| `F07` | 1 | 17..24 | 115500..17758052 |
| `F08` | 1 | 17..24 | 63271..17758051 |
| `F09` | 1 | 17..24 | 120454..15954881 |
| `F10` | 1 | 18..23 | 118490..8239890 |
| `F11` | 1 | 18..24 | 140320..17758051 |
| `F12` | 1 | 14..24 | 12062..17758051 |

## Interpretation

ANF probes a different representation class from ROBDDs. The result is
mixed rather than a simple full-degree closure: no active output reaches
degree 25, and some active outputs have degree below 20. At the same time,
the representation is often very large, with monomial counts reaching
17,758,052. This exposes algebraic stratification inside the dense cone
rather than a universal compact polynomial shortcut.
