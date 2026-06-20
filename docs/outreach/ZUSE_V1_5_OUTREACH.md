# ZUSE v1.5 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.5 without improvising claims.

Canonical links:

- Preprint v1.5: https://doi.org/10.5281/zenodo.20768585
- GitHub Release v1.5: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.5
- v1.5 series: https://doi.org/10.5281/zenodo.20768584
- v1.4 series: https://doi.org/10.5281/zenodo.20767476
- v1.3 series: https://doi.org/10.5281/zenodo.20753498
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.5 to concept DOI `20768584`, independently
from the v1.4 concept DOI `20767476`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE derives a five-state mechanism for a period-15 ECA oscillator
```

Body:

```text
I built ZUSE Automat Agent, a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

Earlier sweeps found a stationary period-15 oscillator family restricted to
rule_73 and rule_109 over periodic backgrounds whose temporal period is 3.
The observed ratio was T_local/T_background = 15/3 = 5.

v1.5 tests the mechanism directly. After burn-in, the localized XOR defect is
sampled once per background period. Across all 20 minimal rule/background
representatives:

- the background returns to the exact same phase every 3 steps
- the defect visits five mutually distinct states under F^3
- no shorter cycle explains the sequence
- four consecutive cycles repeat in canonical and absolute-position encodings
- deterministic transitions are consistent
- all oscillators have zero drift

The result is 20/20: the measured 5:1 locking ratio is the cycle length of the
defect under the three-step operator F^3.

Preprint v1.5:
https://doi.org/10.5281/zenodo.20768585

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.5 update:

Fase 27 establishes the computational mechanism behind the period-15
oscillator family found in rule_73 and rule_109.

For each of the 20 minimal representatives, the localized XOR defect is sampled
once every background period after burn-in. The background has temporal period
3, while the defect follows a minimal five-state cycle under F^3. All checks
pass in 20/20 representatives, including four repeated cycles in canonical and
raw-position encodings and zero drift.

Therefore:

T_local = 5 * T_background = 5 * 3 = 15.

The finite-state mechanism is established computationally. A closed-form
symbolic derivation from the rule tables remains open.

Preprint v1.5:
https://doi.org/10.5281/zenodo.20768585

GitHub Release v1.5:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.5
```

## Reddit Draft

Title:

```text
The period-15 oscillator in ECA rules 73/109 is a five-state cycle under F^3
```

Body:

```text
I followed up the ZUSE period-15 oscillator result with a direct mechanism
test.

The unperturbed periodic backgrounds have temporal period 3. After burn-in, I
sampled the localized XOR defect once every three ECA steps for all 20 minimal
rule/background witnesses.

In every case:

- the background returns to the same phase
- the defect cycles through five distinct states
- the cycle has no shorter subperiod
- four complete cycles repeat exactly
- the raw absolute-position state repeats, not only the normalized shape
- drift over the local period is zero

So the period is explained computationally:

T_local = 5 applications of F^3 = 15 ECA steps.

Preprint:
https://doi.org/10.5281/zenodo.20768585

Code and JSONL:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Short FAQ

### What changed in v1.5?

v1.5 adds Fase 27, which establishes the finite-state mechanism of the
period-15 locking ratio across all 20 minimal representatives.

### What is F^3?

`F` is one ECA evolution step. `F^3` is the three-step operator. Because the
background returns to the same temporal phase every three steps, `F^3` exposes
the defect's internal dynamics without changing the background phase.

### Why is the oscillator period 15?

The defect has a minimal cycle of five states under `F^3`. Returning to the
initial defect state therefore takes five background periods:

```text
T_local = 5 * 3 = 15
```

### How strong is the validation?

All eight acceptance checks pass in 20/20 representatives. Four consecutive
cycles repeat in both normalized and absolute-position encodings.

### Is the mechanism now proved algebraically?

No. The computational state-cycle mechanism is established. A closed-form
symbolic derivation from the `rule_73/rule_109` truth tables remains open.

### Does v1.5 change the rule_108 result?

No. `rule_108` remains the unique stationary oscillator found under the stated
quiescent-zero protocol. Fase 27 concerns periodic-background oscillators.

### Is this a mathematical theorem?

No. It is a reproducible computational result under the stated finite
protocol.

### What does "no LLM in the discovery loop" mean?

Execution, law evaluation, scoring, journaling, and result acceptance are
deterministic. LLM assistance is restricted to post-run interpretation and
documentation.
