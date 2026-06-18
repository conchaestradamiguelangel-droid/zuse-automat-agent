# ZUSE v1.3 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.3 without improvising claims.

Canonical links:

- Preprint v1.3: https://doi.org/10.5281/zenodo.20753499
- GitHub Release v1.3: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.3
- All versions: https://doi.org/10.5281/zenodo.20738024
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN Draft

Title:

```text
Show HN: ZUSE - deterministic oscillator discovery in cellular automata
```

Body:

```text
I built ZUSE Automat Agent, a deterministic discovery pipeline for elementary
cellular automata. It runs CA worlds, applies fixed observers, evaluates seven
empirical cycle laws, and builds a reproducible atlas without an LLM in the
discovery loop.

The latest experiment tests all 256 ECA rules against all 30 primitive binary
necklaces of length 8 and 502 non-zero initial-condition words: 3,855,360 runs.

Compared with the previous length-1/2/4 background sweep, it finds:

- 4 new stationary oscillator rules
- 19 new moving oscillator rules
- new periods T=6, 8, 10, 12, and 15
- a new glider speed: 2/3 cell per step (drift +/-2, T=3)

A rotation sub-test shows background-phase dependence in all 10 sampled cases:
some oscillators activate in 7/8 phases, while others require one specific
phase (1/8). This measures physical IC/background alignment sensitivity; a
strict observer-equivariance test would co-translate both IC and background.

Earlier results remain unchanged: under quiescent zero background, rule_108 is
the unique stationary local period-2 oscillator found under the tested
protocol, and eight rules form the minimal moving period-2 speed-1 family.

Preprint v1.3:
https://doi.org/10.5281/zenodo.20753499

Code and data:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

I would be interested in related classifications, explanations for the
emergent T=15 period, or counterexamples under broader background protocols.
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.3 update:

The new Fase-24 sweep extends the background-conditioned oscillator search to
all 30 primitive binary necklaces of length 8.

Protocol:
- all 256 ECA rules
- 30 primitive period-8 backgrounds
- 502 non-zero IC words
- 3,855,360 deterministic runs

Results beyond the previous length-1/2/4 background sweep:
- 4 new stationary oscillator rules
- 19 new moving oscillator rules
- new periods T=6, 8, 10, 12, and 15
- a new glider speed of 2/3 cell per step (drift +/-2, T=3)

The T=15 result is reported as a non-trivial emergent period; no mechanism is
claimed yet. A rotation test also finds strong background-phase dependence:
near-robust cases activate in 7/8 phases, while strongly phase-sensitive cases
activate in only 1/8.

The quiescent-zero uniqueness claims remain unchanged.

Preprint v1.3:
https://doi.org/10.5281/zenodo.20753499

GitHub Release v1.3:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.3
```

## Reddit Repost Draft

Title:

```text
ZUSE v1.3: period-8 backgrounds produce T=15 oscillators and speed-2/3 gliders in ECA
```

Body:

```text
I extended the ZUSE deterministic ECA oscillator search to primitive
period-8 backgrounds.

The sweep covers all 256 ECA rules, all 30 primitive binary necklaces of
length 8, and 502 non-zero IC words: 3,855,360 runs.

Relative to the previous periodic-background sweep, the new results are:

- 4 new stationary oscillator rules: 62, 118, 131, 145
- 19 new moving oscillator rules
- new observed periods: T=6, 8, 10, 12, 15
- new speed: 2/3 cell per step (drift +/-2, T=3)

Representative speed-2/3 rules include rule_9 and rule_111 moving left, and
rule_65 and rule_125 moving right. I have not yet verified algebraically
whether these form reflection-conjugate pairs.

T=15 is especially interesting because it is not divisible by the background
period 8. I am reporting it as an emergent period without proposing a mechanism.

All 10 sampled cases were background-phase dependent when the background was
rotated with the IC held fixed. This measures alignment sensitivity, not by
itself an observer artifact.

Preprint v1.3:
https://doi.org/10.5281/zenodo.20753499

Code, report, and raw results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short FAQ

### What changed in v1.3 compared with v1.2?

v1.3 adds the primitive period-8 background sweep:

- 256 rules x 30 backgrounds x 502 IC words = 3,855,360 runs.
- 4 new stationary rules and 19 new moving rules.
- New period classes: T=6, 8, 10, 12, and 15.
- New glider speed: 2/3 cell per step.
- Background-phase validation on 10 sampled results.

The abstract and Sections 7.7, 9.3, and 10.2 are updated.

### What does "primitive period-8 background" mean?

It is a binary word of length 8 whose minimal repeating period is exactly 8.
Backgrounds equivalent by cyclic rotation are represented by their
lexicographically smallest rotation. There are exactly 30 such binary
necklaces.

### Why is T=15 notable?

It is the longest period observed in the current searches and is not divisible
by the background period 8. The data establish the recurrence but do not yet
explain its mechanism.

### What is the new speed class?

The new gliders move two cells every three time steps:

```text
speed = |drift| / T = 2 / 3
```

Observed examples include `rule_9`, `rule_65`, `rule_111`, and `rule_125`.

### Are the speed-2/3 rules mirror pairs?

Possibly, but this has not been established from rule-table algebra. The current
result only records left- and right-moving variants with the same speed
signature.

### Does phase dependence mean the observer is wrong?

No. The rotation test holds the IC fixed while changing the background phase.
It therefore measures physical alignment sensitivity. Testing observer
translation equivariance requires co-translating both the IC and background.

### Does v1.3 invalidate the rule_108 uniqueness result?

No. `rule_108` remains the unique stationary oscillator found under the stated
quiescent-zero protocol. v1.3 studies a different, background-conditioned
regime.

### Is this a mathematical theorem?

No. It is an exhaustive computational result under finite width, step, period,
span, IC, and background bounds.

### What does "no LLM in the discovery loop" mean?

World execution, law evaluation, scoring, journaling, and acceptance are
deterministic. LLM assistance is restricted to post-run interpretation and
documentation.
