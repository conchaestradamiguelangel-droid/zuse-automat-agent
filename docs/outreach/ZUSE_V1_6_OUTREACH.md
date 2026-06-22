# ZUSE v1.6 Outreach Pack

Prepared text for sharing ZUSE Automat Agent v1.6 without improvising claims.

Canonical links:

- Preprint v1.6: https://doi.org/10.5281/zenodo.20792051
- GitHub Release v1.6: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.6
- v1.6 series: https://doi.org/10.5281/zenodo.20792050
- v1.5 series: https://doi.org/10.5281/zenodo.20768584
- v1.4 series: https://doi.org/10.5281/zenodo.20767476
- GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Series note: Zenodo assigned v1.6 to concept DOI `20792050`, independently
from the v1.5 concept DOI `20768584`. All concept series are retained
explicitly in the project metadata.

## Show HN Draft

Title:

```text
Show HN: ZUSE - induced algebra of a period-15 cellular automaton oscillator
```

Body:

```text
ZUSE Automat Agent is a deterministic discovery pipeline for elementary
cellular automata, with no LLM in the discovery loop.

v1.5 established that the period-15 oscillator in rules 73 and 109 is a
minimal five-state defect cycle under F^3. v1.6 studies its local algebra.

For background neighborhood b and XOR-defect neighborhood d, the exact induced
defect rule is:

delta_f(b,d) = f(b XOR d) XOR f(b).

Because rule_109 is the black/white conjugate of rule_73, simultaneous
complementation of full state and background leaves the XOR defect unchanged.
This gives the analytical identity:

delta_109(complement(b),d) = delta_73(b,d).

The implementation checks all 64 local cases and 10/10 complemented orbit
pairs.

The negative result is also useful: every one of the 100 F^3 edges uses all
eight ordinary truth-table entries, and no induced (b,d) key appears in every
edge. A sparse fixed subset of local entries cannot explain the cycle. A
closed-form derivation must encode spatial phase or a higher-order block state.

Preprint v1.6:
https://doi.org/10.5281/zenodo.20792051

Code and results:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent
```

## Wolfram Community Follow-Up

```text
ZUSE Automat Agent v1.6 update:

Fase 28 derives the exact induced local rule of the period-15 XOR defect:

delta_f(b,d) = f(b XOR d) XOR f(b).

Black/white conjugation between rule_73 and rule_109 then gives an analytical
identity for their defect dynamics:

delta_109(complement(b),d) = delta_73(b,d).

Equivalently, complementing both the full state and background preserves the
XOR defect orbit. Exhaustive local checks (64/64) and complemented orbit checks
(10/10) validate the implementation.

The analysis also rejects a tempting sparse explanation: all eight ordinary
truth-table entries occur in every F^3 edge, and no induced transition key is
universal across the 100 edges. The remaining symbolic problem requires
spatial phase or higher-order block states.

Preprint v1.6:
https://doi.org/10.5281/zenodo.20792051

GitHub Release v1.6:
https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.6
```

## Short FAQ

### What changed in v1.6?

v1.6 adds the exact induced defect rule, an analytical conjugation proposition,
implementation checks over 64 local cases and 10 orbit pairs, and a negative
result excluding one fixed sparse truth-table support.

### What is the induced defect rule?

For background neighborhood `b` and XOR-defect neighborhood `d`:

```text
delta_f(b,d) = f(b XOR d) XOR f(b)
```

It describes the next defect bit relative to the evolving background.

### What is proved analytically?

Since `rule_109` is the black/white conjugate of `rule_73`:

```text
delta_109(complement(b),d) = delta_73(b,d)
```

Thus complemented full-state/background pairs have identical XOR-defect
orbits.

### What was rejected?

No fixed sparse subset of ordinary or induced local transitions appears in all
five-cycle edges. The symbolic derivation must include phase or block-state
information.

### Does v1.6 change the five-state mechanism?

No. It refines it. The five-state cycle under `F^3` remains established in
20/20 representatives.

### Is this a complete closed-form proof of the five-cycle?

No. The conjugation relation is proved. The emergence of the five-cycle itself
still lacks a compact symbolic derivation.
