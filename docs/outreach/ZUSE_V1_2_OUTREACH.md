# ZUSE v1.2 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.2 without improvising claims.

Canonical links:

- Preprint v1.2: https://doi.org/10.5281/zenodo.20738025
- GitHub Release v1.2: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.2
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

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
- A periodic-background sweep (15 non-zero backgrounds, 256 rules, 1.9M runs)
  found 30 stationary and 36 moving oscillator rules, including period-4
  oscillators and speed-0.5 gliders absent under quiescent zero background.
  rule_108 persists under all-one background with the same motif.
- One-bit initial-condition fragility spans from f_total = 0.000 to 1.000, with
  rule_108 as the ECA outlier at f_total = 0.992.
- The project separates physical CA dynamics from observer artifacts; for
  example, ECA frames can be translation-invariant while the observer/dedup
  pipeline is not.

Preprint v1.2:
https://doi.org/10.5281/zenodo.20738025

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

I would be interested in critiques, related ECA oscillator classifications, or
counterexamples under broader protocols.
```

## Wolfram Community Follow-Up

```text
v1.2 update to the ZUSE Automat Agent preprint:

The v1.2 sweep extends the oscillator search to non-zero periodic backgrounds.
Testing all 256 ECA rules against 15 unique non-zero periodic backgrounds
(template lengths 1, 2, and 4) with 502 IC words (1,927,680 runs) finds:

- 30 stationary oscillator rules (29 new beyond the quiescent-zero baseline)
- 36 moving oscillator rules (28 new)
- Period-4 stationary oscillators: rule_54 and rule_147 under 0001 background
- Period-4 moving oscillator: rule_180 with drift +4 under 0001 background
- Speed-0.5 gliders (drift +/-1, T=2): multiple rules under non-zero backgrounds
- rule_108 persists under all-one background with the same motif ### / #.#

The quiescent-zero uniqueness claims from v1.1 remain valid and unchanged.
rule_108 is still the only stationary oscillator under quiescent zero background.
The periodic-background sweep defines a distinct, richer regime.

Updated preprint v1.2:
https://doi.org/10.5281/zenodo.20738025

GitHub Release v1.2:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.2
```

## Reddit Repost Draft

Title:

```text
ZUSE v1.2: periodic-background sweep - 30 stationary, 36 moving oscillator rules, T=4 and speed-0.5 gliders
```

Body:

```text
v1.2 update to ZUSE Automat Agent, the deterministic ECA discovery pipeline.

The v1.1 sweeps established:
- rule_108 as the unique stationary local period-2 oscillator under quiescent
  zero background
- 8 quiescent rules producing minimal period-2 speed-1 gliders (four mirror pairs)

The v1.2 sweep replaces the zero background with 15 non-zero periodic
backgrounds (template lengths 1, 2, and 4). Detector: exact recurrence of the
localized difference between perturbed run and unperturbed background orbit,
so global background periodicity does not count as a local oscillator.
Total: 1,927,680 runs.

Results:

- 30 stationary oscillator rules (29 new beyond the quiescent-zero baseline)
- 36 moving oscillator rules (28 new)

New phenomena not present under quiescent zero background:

- Period-4 stationary oscillators: rule_54 and rule_147 under 0001 background
- Period-4 moving oscillator: rule_180 with drift +4 under 0001 background
- Speed-0.5 gliders (drift +/-1, T=2): multiple rules under non-zero backgrounds
- rule_108 persists under all-one background with the same motif #.# <-> ###

The quiescent-zero uniqueness results from v1.1 are not contradicted.
The two regimes are distinct.

Preprint v1.2:
https://doi.org/10.5281/zenodo.20738025

Code:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Interested in related ECA oscillator results on non-zero backgrounds, or
counterexamples where quiescent uniqueness breaks down.
```

## Short FAQ

### What changed in v1.2 compared with v1.1?

v1.2 adds two extensions:

IC word extension to length 9..12: 982,528 additional runs per sweep.
No new stationary or moving oscillator rules appear beyond the length-1..8
baseline. The quiescent uniqueness claims from v1.1 hold to IC length 12.

Periodic-background oscillator sweep: 15 non-zero periodic backgrounds,
all 256 ECA rules, 502 IC words, 1,927,680 runs. Finds 30 stationary and
36 moving oscillator rules, including period-4 oscillators and speed-0.5
gliders not present under quiescent zero background. rule_108 persists under
all-one background with the same motif.

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

### Does the periodic-background sweep contradict the quiescent uniqueness claims?

No. The quiescent-zero uniqueness claims (`rule_108` stationary, 8-rule moving
family) hold under zero background. The periodic-background sweep defines a
separate background-conditioned regime. The two regimes should not be merged:
under zero background the oscillator space is sparse; under non-zero periodic
backgrounds it is substantially richer.

### Is this a mathematical theorem?

No. It is an exhaustive computational result under a stated protocol. The
claims depend on:

- quiescent zero background (or the specific non-zero background for v1.2 results),
- non-zero IC words of length 1..8 (extended to 1..12 for the IC sweep),
- finite width and step bounds,
- period and span detection limits.

IC words longer than 12 and longer periods remain possible extensions.

### What does "no LLM in the discovery loop" mean?

It means the empirical evidence is produced by deterministic scripts: running
worlds, evaluating laws, scoring, journaling, and generating atlas artifacts.
LLM assistance was used after the fact for interpretation and writing, not for
accepting or rejecting discoveries.
