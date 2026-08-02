# Fase 86: Physical Realizability of the h=11 Input Selectors

## Question

Do the controlled symbolic input selectors isolated in Fase 85 occur
as persistent physical stationary oscillators under the original
periodic-background sweep protocol?

## Predeclared Protocol

- Rule: `73`.
- Physical backgrounds: `['00110111', '00111011', '00111101', '01101111']`.
- ICs: all 502 non-zero centered binary words of length 1..8 per background.
- Total physical runs: `2008`.
- Original detector: width 256, 300 steps, burn-in 80, stationary period 12.
- Local audit: sample t=80, h=11, 25 cells.
- Exact operator gate: reference boundary trace and local final-background
  vector must both match Fases 83-85.
  For a deterministic radius-1 rule, the same local rule and boundary
  trace induce the same actual-state map; the same final-background
  vector then induces the same background-subtracted defect map.
- No comparability threshold is changed or fitted.

A symbolic assignment counts as physically realized only when a source-protocol
IC produces a persistent T=12 stationary oscillator, the exact reference defect
operator is preserved, the t=80 assignment lies in the eight-bit Fase 85
subcube, and the physical h=11 final defect equals the symbolic prediction.

## Result

Status: `PHYSICAL_NONENDPOINT_SUBCUBE_REALIZED`.

Persistent physical oscillators reach non-endpoint assignments in the Fase 85 subcube, but none is a predeclared minimal selector.

- Runs processed: `2008`
- Stationary oscillators of any period: `1516`
- Stationary T=12 runs: `165`
- T=12 runs with the exact reference defect operator: `145`
- Raw physical hits in the Fase 85 subcube: `100`
- Unique physically reached subcube assignments: `6`
- Unique non-endpoint assignments reached: `4`
- Minimal A-side atomic breaks reached: `0`
- Minimal B-side rescues reached: `0`
- Physical/symbolic final-pattern mismatches: `0`
- Four known endpoint cases confirmed: `true`

## Physically Reached Fase 85 Assignments

| assignment | changes from A | reversions from B | role | comparable | physical ICs |
| --- | --- | --- | --- | --- | ---: |
| `0x0310630` | `[]` | `[7, 9, 10, 11, 12, 13, 15, 18]` | `ENDPOINT` | true | 19 |
| `0x0318230` | `[10, 15]` | `[7, 9, 11, 12, 13, 18]` | `NONENDPOINT_SUBCUBE` | false | 24 |
| `0x031aa30` | `[10, 11, 13, 15]` | `[7, 9, 12, 18]` | `NONENDPOINT_SUBCUBE` | false | 3 |
| `0x031be30` | `[11, 12, 13, 15]` | `[7, 9, 10, 18]` | `NONENDPOINT_SUBCUBE` | false | 6 |
| `0x03580b0` | `[7, 9, 10, 15, 18]` | `[11, 12, 13]` | `NONENDPOINT_SUBCUBE` | false | 17 |
| `0x035b8b0` | `[7, 9, 10, 11, 12, 13, 15, 18]` | `[]` | `ENDPOINT` | false | 31 |

## Physical IC Evidence

The complete alias list is stored in the JSON results. This compact
table gives one deterministic representative per reached assignment.

| assignment | representative background/IC | aliases | backgrounds |
| --- | --- | ---: | --- |
| `0x0310630` | `00111011/011` (len 3) | 19 | `['00111011', '00111101', '01101111']` |
| `0x0318230` | `00110111/11110` (len 5) | 24 | `['00110111', '00111101', '01101111']` |
| `0x031aa30` | `01101111/0000011` (len 7) | 3 | `['01101111']` |
| `0x031be30` | `01101111/0010011` (len 7) | 6 | `['01101111']` |
| `0x03580b0` | `00110111/0111` (len 4) | 17 | `['00110111', '00111011', '01101111']` |
| `0x035b8b0` | `00110111/111` (len 3) | 31 | `['00110111', '00111101', '01101111']` |

## Interpretation

The physical dynamics enters the symbolic subcube beyond its two
endpoints, but it does not realize either predeclared minimal selector.
Reachability is therefore broader than the observed endpoint pair but
does not yet validate the atomic selector claim physically.

## Methodological Limits

- The physical census is exhaustive only for four backgrounds and the
  original centered non-zero IC words of length 1..8.
- Failure to reach a selector does not prove that no longer, shifted, or
  multi-site physical perturbation can realize it.
- Success establishes reachability for rule_73/T12/h11/window25, not a
  universal selector law for cellular automata.
- Physical aliases are reported separately from unique t=80 assignments.
- No paper, DOI, tag, release, or classification threshold changed.
