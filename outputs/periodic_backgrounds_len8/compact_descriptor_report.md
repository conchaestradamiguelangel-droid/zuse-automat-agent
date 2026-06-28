# Fase 31: Compact Descriptor Search for T=15 Shape Families

## Question

Fase 30 showed that the 20 minimal T=15 representatives collapse into
13 phase-rotated defect-cycle shape families. Fase 31 asks whether a
short descriptor of the circular length-8 background predicts that
family without using the full temporal orbit as identity.

## Descriptor separation

| scope | descriptor | buckets | ambiguous | determines family |
| --- | --- | ---: | ---: | --- |
| global | `subpatterns_len2` | 8 | 8 | False |
| global | `subpatterns_len3` | 10 | 7 | False |
| global | `subpatterns_len4` | 12 | 5 | False |
| global | `parity` | 2 | 2 | False |
| global | `run_lengths_circular` | 14 | 5 | False |
| global | `run_lengths_sorted` | 5 | 5 | False |
| global | `run_count` | 3 | 3 | False |
| global | `first_one_pos` | 5 | 4 | False |
| global | `orbit_prefix_8` | 14 | 5 | False |
| global | `orbit_prefix_16` | 17 | 3 | False |
| global | `orbit_prefix_24` | 20 | 0 | True |
| global | `orbit_canonical_prefix_8` | 8 | 5 | False |
| global | `orbit_canonical_prefix_16` | 13 | 6 | False |
| global | `orbit_canonical_prefix_24` | 19 | 1 | False |
| rule_conditioned | `subpatterns_len2` | 14 | 3 | False |
| rule_conditioned | `subpatterns_len3` | 16 | 2 | False |
| rule_conditioned | `subpatterns_len4` | 18 | 0 | True |
| rule_conditioned | `parity` | 4 | 4 | False |
| rule_conditioned | `run_lengths_circular` | 20 | 0 | True |
| rule_conditioned | `run_lengths_sorted` | 10 | 5 | False |
| rule_conditioned | `run_count` | 6 | 5 | False |
| rule_conditioned | `first_one_pos` | 9 | 4 | False |
| rule_conditioned | `orbit_prefix_8` | 20 | 0 | True |
| rule_conditioned | `orbit_prefix_16` | 20 | 0 | True |
| rule_conditioned | `orbit_prefix_24` | 20 | 0 | True |
| rule_conditioned | `orbit_canonical_prefix_8` | 10 | 6 | False |
| rule_conditioned | `orbit_canonical_prefix_16` | 14 | 6 | False |
| rule_conditioned | `orbit_canonical_prefix_24` | 19 | 1 | False |
| 73 | `subpatterns_len2` | 7 | 2 | False |
| 73 | `subpatterns_len3` | 8 | 1 | False |
| 73 | `subpatterns_len4` | 9 | 0 | True |
| 73 | `parity` | 2 | 2 | False |
| 73 | `run_lengths_circular` | 10 | 0 | True |
| 73 | `run_lengths_sorted` | 5 | 3 | False |
| 73 | `run_count` | 3 | 3 | False |
| 73 | `first_one_pos` | 4 | 2 | False |
| 73 | `orbit_prefix_8` | 10 | 0 | True |
| 73 | `orbit_prefix_16` | 10 | 0 | True |
| 73 | `orbit_prefix_24` | 10 | 0 | True |
| 73 | `orbit_canonical_prefix_8` | 6 | 4 | False |
| 73 | `orbit_canonical_prefix_16` | 6 | 4 | False |
| 73 | `orbit_canonical_prefix_24` | 9 | 1 | False |
| 109 | `subpatterns_len2` | 7 | 1 | False |
| 109 | `subpatterns_len3` | 8 | 1 | False |
| 109 | `subpatterns_len4` | 9 | 0 | True |
| 109 | `parity` | 2 | 2 | False |
| 109 | `run_lengths_circular` | 10 | 0 | True |
| 109 | `run_lengths_sorted` | 5 | 2 | False |
| 109 | `run_count` | 3 | 2 | False |
| 109 | `first_one_pos` | 5 | 2 | False |
| 109 | `orbit_prefix_8` | 10 | 0 | True |
| 109 | `orbit_prefix_16` | 10 | 0 | True |
| 109 | `orbit_prefix_24` | 10 | 0 | True |
| 109 | `orbit_canonical_prefix_8` | 4 | 2 | False |
| 109 | `orbit_canonical_prefix_16` | 8 | 2 | False |
| 109 | `orbit_canonical_prefix_24` | 10 | 0 | True |

## Decision tree

- Training accuracy on the 20 representatives: `0.700`.
- Effective depth: `4`.
- Node count: `13`.

Non-zero feature importances:

- `sub3_110`: `0.219`
- `sub3_100`: `0.211`
- `sub4_1010`: `0.178`
- `orbit24_bit_21`: `0.138`
- `rule`: `0.138`
- `orbit8_bit_5`: `0.116`

Tree:

```text
|--- sub3_110 <= 1.50
|   |--- sub3_100 <= 1.50
|   |   |--- sub4_1010 <= 1.50
|   |   |   |--- orbit8_bit_5 <= 0.50
|   |   |   |   |--- class: F06
|   |   |   |--- orbit8_bit_5 >  0.50
|   |   |   |   |--- class: F03
|   |   |--- sub4_1010 >  1.50
|   |   |   |--- class: F04
|   |--- sub3_100 >  1.50
|   |   |--- orbit24_bit_21 <= 0.50
|   |   |   |--- class: F01
|   |   |--- orbit24_bit_21 >  0.50
|   |   |   |--- class: F11
|--- sub3_110 >  1.50
|   |--- rule <= 91.00
|   |   |--- class: F02
|   |--- rule >  91.00
|   |   |--- class: F12
```

## Verdict

**Status:** `COMPACT_DESCRIPTOR_FOUND`.

The following background-only descriptors determine the global family: `orbit_prefix_24`.
Conditioned on the ECA rule, the following descriptors determine the global family: `rule + subpatterns_len4`, `rule + run_lengths_circular`, `rule + orbit_prefix_8`, `rule + orbit_prefix_16`, `rule + orbit_prefix_24`.
The shortest non-orbit candidate is therefore `rule + subpatterns_len4`: the circular multiset of length-4 background words, with the rule identity supplied.
A compact rule-conditioned descriptor candidate exists. It should be tested on a larger representative set before being treated as a symbolic law.

## Falsifiable implication

A global background-only derivation based only on length-2..4 circular
subpattern counts, parity, run lengths, or short orbit prefixes is
falsified if it predicts one family per descriptor bucket, because
the ambiguous global buckets listed in `compact_descriptor_results.json`
contain multiple shape families. A rule-conditioned derivation based
on the length-4 circular subpattern multiset remains viable and is
the next compact symbolic target to test.
