# ZUSE v1.1 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.1 without improvising claims.

Canonical links:

- Preprint v1.1: https://doi.org/10.5281/zenodo.20687470
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
- Repository README: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN Draft

Title:

```text
Show HN: ZUSE - deterministic discovery of empirical laws in cellular automata
```

Body:

```text
I built ZUSE Automat Agent, a deterministic discovery pipeline for elementary
cellular automata. It runs cellular-automata worlds, applies fixed observers,
evaluates seven empirical cycle laws, and builds a reproducible atlas of world
behavior.

The discovery loop does not use an LLM: world execution, law evaluation,
scoring, journaling, and atlas generation are deterministic. I used LLM
assistance only afterward for interpretation and documentation.

Some results:

- A 20-world empirical atlas with seven operational categories.
- frontera_temporal activates in 38/256 ECA rules under at least two of three seeds.
- rule_108 is the only quiescent ECA rule found to produce stationary local
  period-2 oscillators under the tested protocol: 101 <-> 111 (#.# <-> ###).
- A companion sweep found a moving oscillator family: 8 quiescent rules produce
  minimal period-2 speed-1 gliders, arranged as four mirror pairs.
- One-bit initial-condition fragility spans from f_total = 0.000 to 1.000, with
  rule_108 as the ECA outlier at f_total = 0.992.
- The project separates physical CA dynamics from observer artifacts; for
  example, ECA frames can be translation-invariant while the observer/dedup
  pipeline is not.

Preprint v1.1:
https://doi.org/10.5281/zenodo.20687470

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

I would be interested in critiques, related ECA oscillator classifications, or
counterexamples under broader protocols.
```

## Wolfram Community Follow-Up

```text
Small update to the ZUSE Automat Agent preprint:

I added a v1.1 result extending the rule_108 stationary oscillator search.
When the stationarity requirement is relaxed, a companion sweep over all 128
quiescent ECA rules finds a minimal moving oscillator family:

- rules: 6, 20, 38, 52, 134, 148, 166, 180
- period: T = 2
- drift: +/-2 per period
- speed: 1 cell/step, the maximum speed for radius-1 ECA
- shape cycle: [0] <-> [0,1]

These eight rules form four mirror pairs. They are distinct from rule_108:
rule_108 is the unique stationary local period-2 oscillator under the tested
protocol, while the eight-rule family is the unique moving period-2 speed-1
glider family found under the companion protocol.

Updated preprint v1.1:
https://doi.org/10.5281/zenodo.20687470

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Reddit Repost Draft

Title:

```text
ZUSE v1.1: rule_108 stationary oscillator plus an 8-rule moving glider family
```

Body:

```text
I posted earlier about ZUSE Automat Agent, a deterministic discovery pipeline
for elementary cellular automata. I have now updated the preprint to v1.1 with
a companion result.

The original local-oscillator sweep found rule_108 as the only quiescent ECA
rule producing stationary local period-2 oscillators under the tested protocol:

101 <-> 111

or, using #/. notation:

#.# <-> ###

The v1.1 companion sweep relaxes the zero-drift requirement and searches for
moving local oscillators. It finds 8 quiescent ECA rules:

rule_6, rule_20, rule_38, rule_52, rule_134, rule_148, rule_166, rule_180

All share the same minimal moving glider:

[0] <-> [0,1]

with period T=2, drift +/-2 per period, and speed 1 cell/step.

Preprint v1.1:
https://doi.org/10.5281/zenodo.20687470

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

I am especially interested in related classifications of elementary-CA local
oscillators or counterexamples under longer IC words, non-zero backgrounds, or
longer periods.
```

## Short FAQ

### What changed in v1.1 compared with v1.0?

v1.1 adds the moving-oscillator sweep, integrates it into `paper/draft.md`,
adds Figure 6, regenerates the PDF, and updates citation metadata to the v1.1
Zenodo DOI.

### Why 502 IC words and not 510?

The inclusive count of binary words of length 1..8 is:

```text
2^1 + 2^2 + ... + 2^8 = 510
```

The sweep excludes the all-zero word at each length because it is the quiescent
background itself and cannot seed a local oscillator. There are 8 such all-zero
words, one per length. Therefore:

```text
510 - 8 = 502
```

### What is the rule_108 result?

Under the stationary protocol, `rule_108` is the only quiescent ECA rule found
to produce stationary local period-2 oscillators. Its minimal motif is:

```text
101 <-> 111
```

or:

```text
#.# <-> ###
```

The motif has period 2 and zero drift.

### What is the moving oscillator result?

When the zero-drift requirement is relaxed, eight quiescent ECA rules produce
minimal moving period-2 gliders:

```text
rule_6, rule_20, rule_38, rule_52, rule_134, rule_148, rule_166, rule_180
```

They form four mirror pairs and share the same shape cycle:

```text
[0] <-> [0,1]
```

The drift is `+/-2` per period, so the speed is 1 cell per step.

### Does the moving-glider family contradict the rule_108 uniqueness claim?

No. The rule_108 claim is explicitly about stationary local oscillators under
the tested protocol. The eight-rule family appears only after relaxing the
stationarity requirement. The two results partition the tested quiescent local
oscillator landscape into:

- one stationary oscillator rule: `rule_108`
- one moving glider family: 8 rules, four mirror pairs

### Is this a mathematical theorem?

No. It is an exhaustive computational result under a stated protocol. The
claims depend on:

- quiescent zero background,
- ECA rules with `f(0,0,0)=0`,
- non-zero IC words of length 1..8,
- finite width and step bounds,
- period and span detection limits.

Longer IC words, non-zero backgrounds, longer periods, and broader detector
definitions remain possible extensions.

### What does "no LLM in the discovery loop" mean?

It means the empirical evidence is produced by deterministic scripts: running
worlds, evaluating laws, scoring, journaling, and generating atlas artifacts.
LLM assistance was used after the fact for interpretation and writing, not for
accepting or rejecting discoveries.
