# Fase 28: Symbolic Signature of the Five-State Locking Cycle

## Induced defect rule

The defect does not evolve under `f` alone. For a background neighborhood
`b` and XOR-defect neighborhood `d`, its exact local rule is:

`delta_f(b,d) = f(b XOR d) XOR f(b)`.

All three microsteps of each of the five `F^3` transitions are profiled
for all 20 minimal T=15 representatives.

**Status:** `MIXED` - black/white conjugation is proved analytically,
while the proposed sparse universal-entry explanation is rejected.

## Global support

- Ordinary rule entries present in every macro-transition: `['000', '001', '010', '011', '100', '101', '110', '111']`.
- Ordinary rule entries never used in the causal defect cone: `[]`.
- Induced `(background, defect)` keys present in every representative: `['b000_d010', 'b000_d100', 'b000_d101', 'b000_d111', 'b001_d001', 'b001_d010', 'b001_d110', 'b010_d010', 'b010_d101', 'b010_d111', 'b011_d011', 'b011_d100', 'b011_d110', 'b100_d010', 'b100_d011', 'b100_d100', 'b100_d110', 'b101_d010', 'b101_d101', 'b101_d111', 'b110_d001', 'b110_d010', 'b110_d110', 'b111_d001', 'b111_d010', 'b111_d011', 'b111_d100', 'b111_d101', 'b111_d110', 'b111_d111']`.
- Induced keys present in every one of the 100 F^3 transitions: `[]`.
- Induced keys never used: `[]`.
- Non-empty universal induced support found: `False`.

Every macro-transition uses all eight ordinary rule entries, while no
single induced `(b,d)` key appears in all 100 macro-transitions. The
original sparse-entry hypothesis is therefore rejected by the data.

## Black/white conjugation

**Proposition.** Let `C` denote bitwise complementation. Because
`rule_109` is the black/white conjugate of `rule_73`, their global
maps satisfy `F_109(C(X)) = C(F_73(X))`. Therefore, if both the full
state and background are complemented, induction gives
`X_109(t)=C(X_73(t))` and `B_109(t)=C(B_73(t))` for every `t`.
Consequently:

`D_109(t) = C(X_73(t)) XOR C(B_73(t)) = D_73(t)`.

Equivalently, the induced local rules obey the exact identity
`delta_109(C(b),d) = delta_73(b,d)`. This is an analytical result;
the exhaustive local and orbit checks below are implementation sanity
checks rather than the basis of the proof.

- Exact local identity `delta_109(complement(b),d) = delta_73(b,d)`: `64/64`.
- Exact orbit-level conjugation tests: `10/10`.
- Under simultaneous complementation of background and full IC, the XOR
  defect is invariant rather than complemented:
  `(~X) XOR (~B) = X XOR B`.

| background rule_73 | IC rule_73 | complemented background | complemented IC | exact |
| --- | --- | --- | --- | --- |
| `00000011` | `0000011` | `11111100` | `1111100` | True |
| `00001001` | `00110010` | `11110110` | `11001101` | True |
| `00001111` | `00100000` | `11110000` | `11011111` | True |
| `00101101` | `010110` | `11010010` | `101001` | True |
| `00101111` | `0000111` | `11010000` | `1111000` | True |
| `00110101` | `011010` | `11001010` | `100101` | True |
| `00110111` | `011011` | `11001000` | `100100` | True |
| `00111011` | `00100100` | `11000100` | `11011011` | True |
| `00111111` | `0001100` | `11000000` | `1110011` | True |
| `01101111` | `01101110` | `10010000` | `10010001` | True |

## Per-rule support

| rule | ordinary entries | induced union | induced intersection |
| --- | --- | ---: | ---: |
| rule_73 | `['000', '001', '010', '011', '100', '101', '110', '111']` | 56 | 37 |
| rule_109 | `['000', '001', '010', '011', '100', '101', '110', '111']` | 56 | 36 |

Phase-specific intersections exist within each rule but differ across
backgrounds and between the conjugate rules. Their sizes by phase are:

- rule_73: `[9, 6, 7, 5, 4]`.
- rule_109: `[11, 11, 10, 9, 8]`.

## Falsifiable hypothesis

No non-empty induced transition key is shared by all 100 F^3 edges. Therefore the five-cycle is not driven by a fixed sparse subset of local table entries; it depends on phase- and background-specific spatial organization of the full induced defect rule. Independently, the exact identity delta_109(complement(b),d)=delta_73(b,d) predicts that every rule_73 defect orbit has an identical rule_109 orbit under simultaneous black/white complementation of background and full IC. One counterexample to either the 64-row local identity or the orbit mapping would falsify the conjugation claim.

The positive result is the analytically proved conjugation law. The
negative result is
equally informative: neither ordinary table-entry reduction nor one fixed
induced-key support explains all five-cycle edges. A minimal Boolean
derivation of the five-cycle must therefore encode spatial phase or a
higher-order block state, rather than only entry presence.

## Scope

- Representatives: `20`.
- Macro-transitions: `100` (20 representatives x 5 edges).
- Microsteps profiled: `300`.
- Sample interval: `t=81..96`.
