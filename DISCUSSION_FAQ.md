# Discussion FAQ

Short answers for comments about ZUSE Automat Agent v1.0.

## Is this a formal proof that only rule 108 has local oscillators?

No. The result is exhaustive under a specific protocol: quiescent zero
background, all 128 ECA rules with `f(0,0,0) = 0`, all non-empty binary IC words
of length 1 to 8, width 128, 200 steps, stationary local oscillators, period 2
to 16, and local span up to 32.

Under that protocol, only `rule_108` produced stationary local period-2
oscillators. Moving oscillators, longer IC words, non-zero backgrounds, or longer
periods are outside the claim.

## What does `101 <-> 111` mean?

It is the local period-2 motif found in `rule_108`. A small local pattern
alternates between:

```text
101
111
101
111
...
```

Using `#` for active cells and `.` for inactive cells, this is the same as:

```text
#.# <-> ###
```

The motif stays stationary on a zero background under the tested protocol.

## Why is rule 108 special?

`rule_108` has the local transitions needed for this motif:

- `010 -> 1`: an isolated active center persists.
- `101 -> 1`: the gap in `101` fills.
- `111 -> 0`: the dense triplet empties at the center.

The rule is also left-right symmetric, which helps explain why the oscillator
does not drift.

## What does "no LLM in the discovery loop" mean?

It means the empirical results are produced by deterministic scripts. The system
chooses worlds, runs simulations, applies observers, evaluates laws, scores
results, and writes journals without a language model deciding what counts as
evidence.

A language model was used afterward for interpretation, documentation, and
writing assistance, not for accepting or rejecting discoveries.

## How can I reproduce the result?

Start with the reproducibility guide:

https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/blob/master/REPRODUCIBILITY.md

The local oscillator search scripts are:

```text
outputs/local_oscillators_fase16/run_local_oscillator_search.py
outputs/local_oscillator_family_fase18/sweep_local_oscillator_family.py
```

The preprint is archived here:

https://doi.org/10.5281/zenodo.20516375

## What is the broader project doing?

ZUSE builds an empirical atlas of cellular-automata worlds. It evaluates seven
cycle laws, groups worlds into dynamic categories, and measures one-bit
initial-condition fragility.

The goal is not only to find interesting rules, but to separate three things:

- physical CA behavior,
- observer/pipeline artifacts,
- and reproducible empirical law signatures.

## What would count as a useful counterexample?

A useful counterexample would be another ECA rule, under the same protocol, that
produces a stationary local oscillator with period 2 to 16 and span up to 32.

Broader-protocol examples are also interesting, but they should be labeled as
extensions rather than direct contradictions. Examples:

- moving local oscillators,
- IC words longer than 8,
- non-zero or periodic backgrounds,
- periods longer than 16,
- wider local spans.

## What are the next experiments?

The natural v1.1 directions are:

- search for moving local oscillators,
- extend IC word length from 8 to 12 or 16,
- test non-zero and periodic backgrounds,
- build symmetry-invariant observers to reduce mirror and translation artifacts.
