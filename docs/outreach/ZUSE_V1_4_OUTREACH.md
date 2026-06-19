# ZUSE v1.4 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.4 without improvising claims.

Canonical links:

- Preprint v1.4: https://doi.org/10.5281/zenodo.20767477
- GitHub Release v1.4: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.4
- v1.4 series: https://doi.org/10.5281/zenodo.20767476
- v1.3 series: https://doi.org/10.5281/zenodo.20753498
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN Draft

Title:

```text
Show HN: ZUSE - deterministic oscillator discovery in cellular automata
```

Body:

```text
I built ZUSE Automat Agent, a deterministic discovery pipeline for elementary
cellular automata. It applies fixed observers and seven empirical cycle laws,
without an LLM in the discovery loop.

The v1.4 update closes two methodological questions raised by the period-8
background sweep.

First, a strict co-translation test shifts both the periodic background and
the initial condition together. The physical background and perturbation
orbits are exact translations in 80/80 runs. A linear shape representation
missed 22 boundary-crossing particles; circular canonicalization recovers
80/80 signatures.

Second, all 221 period-15 detections form a narrow family:

- only rule_73 and rule_109 participate
- the rules are left-right symmetric and exact black/white conjugates
- 20 rule/background representatives all have background temporal period 3
- the local oscillator locks at T=15, a reproducible 5:1 ratio
- exact recurrence persists through step 900 in 20/20 representatives
- only 23/160 background phases and 4/134 one-bit IC mutations retain T=15

The oscillator is therefore persistent in time but narrow in basin.

Preprint v1.4:
https://doi.org/10.5281/zenodo.20767477

Code and data:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.4 update:

Fase 25 tests strict co-translation equivariance for 10 period-8-background
oscillator cases. Both the background and IC are translated through k=0..7.
The physical orbits match exactly in 80/80 runs. Circular shape
canonicalization also recovers 80/80 oscillator signatures; the previous
linear representation lost 22 moving runs at the cyclic boundary.

Fase 26 analyzes all 221 T=15 detections from the period-8 sweep. They occur
only in rule_73 and rule_109, which are left-right symmetric and exact
black/white conjugates. All 20 minimal rule/background representatives have
background temporal period 3 and retain exact local period 15 through step
900, giving a consistent 5:1 locking ratio. The basin is narrow: 23/160
background phases and 4/134 one-bit IC mutations preserve T=15.

Preprint v1.4:
https://doi.org/10.5281/zenodo.20767477

GitHub Release v1.4:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.4
```

## Reddit Draft

Title:

```text
ZUSE v1.4: the ECA T=15 oscillator is a persistent 5:1 background-locked family
```

Body:

```text
I followed up the ZUSE period-8 background sweep with two controlled tests.

The first co-translates both the periodic background and initial condition.
The ECA and perturbation orbits are exact translations in 80/80 runs. A
linear detector had missed 22 moving cases at the 255/0 boundary; circular
canonicalization restores all 80 signatures.

The second analyzes every T=15 detection:

- 221 detections
- only rule_73 and rule_109
- 14 primitive length-8 backgrounds
- 20 rule/background pairs
- all backgrounds have temporal period 3
- exact local T=15 persists through step 900 in 20/20 representatives

This gives a consistent T_local/T_background = 15/3 = 5 locking ratio.
The family is persistent but initialization-sensitive: 23/160 background
phases and 4/134 one-bit IC mutations retain T=15.

Preprint:
https://doi.org/10.5281/zenodo.20767477

Code and full reports:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short FAQ

### What changed in v1.4?

v1.4 adds:

- strict co-translation validation: 80/80 physically equivalent runs;
- circular correction of 22 cyclic-boundary detector misses;
- complete anatomy of all 221 T=15 detections;
- long-horizon validation to step 900;
- phase and one-bit IC basin measurements;
- algebraic verification of the speed-2/3 mirror pairs.

### Is T=15 a numerical accident?

The evidence argues against that interpretation. It appears in 221 detections,
20 rule/background pairs, and 25 temporal motifs. All 20 minimal
representatives persist exactly through step 900.

### Why is the ratio 5:1?

Every participating unperturbed background has temporal period 3, while the
localized oscillator has fundamental period 15. The measured ratio is
therefore 15/3 = 5. A derivation from the rule tables remains open.

### Which rules produce T=15?

Only `rule_73` and `rule_109` in the tested protocol. Each is left-right
symmetric, and black/white conjugation maps one exactly to the other.

### Is the T=15 family robust?

It is robust in time but narrow in basin. Exact recurrence persists to step
900 in 20/20 minimal representatives, while only 23/160 tested background
phases and 4/134 one-bit IC mutations retain T=15.

### Did Fase 25 find an observer artifact?

Yes, and isolate it precisely. The physical orbits are equivariant in 80/80
runs. The old linear shape representation rejected 22 moving particles that
crossed the cyclic boundary. Circular canonicalization restores all 80
signatures.

### Are the speed-2/3 rules mirror pairs?

Yes. Direct rule-table reflection confirms `rule_9 <-> rule_65` and
`rule_111 <-> rule_125`, with opposite drift signs and equal speed magnitude.

### Does v1.4 invalidate the rule_108 uniqueness result?

No. `rule_108` remains the unique stationary oscillator found under the stated
quiescent-zero protocol. The later phases study periodic-background regimes.

### Is this a mathematical theorem?

No. It is an exhaustive computational result under stated finite width, step,
period, span, IC, and background bounds.

### What does "no LLM in the discovery loop" mean?

World execution, law evaluation, scoring, journaling, and result acceptance
are deterministic. LLM assistance is restricted to post-run interpretation
and documentation.
