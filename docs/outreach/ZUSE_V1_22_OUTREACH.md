# ZUSE v1.22 Outreach Pack

## Short Post

ZUSE v1.22 is out.

Fase 55 runs a catalog census for non-T15 ANF-gradient witnesses.

Result: `NEW_NATURAL_PERIOD_WITNESS_FOUND`.

- 66 non-T15 periodic-background groups with span >= 11.
- 128 ANF measurements, 0 packed/concrete mismatches.
- 2 new natural-period witnesses, both in `rule_109/T=12`.
- 2 new acceptable-horizon witnesses, both in `rule_109/T=8`.
- No `rule_73` or external-family case becomes a strong/acceptable witness.

The non-T15 evidence is not isolated, but it is concentrated in `rule_109`
within the censused catalog.

Preprint: https://doi.org/10.5281/zenodo.21306875
Release: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent/releases/tag/v1.22
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## GitHub Release Body

## What's new

Fase 55: NEW_NATURAL_PERIOD_WITNESS_FOUND.

v1.22 adds a catalog-level census for non-T15 ANF-gradient witnesses in
stationary periodic-background oscillators.

Scope:

- `T_local != 2` and `T_local != 15`
- `span >= 11`
- 66 candidate groups across rules 54, 73, 94, 109, 133, and 147
- 128 ANF measurements
- 0 packed/concrete mismatches

Category counts:

- `NATURAL_PERIOD_STRONG`: 2
- `HORIZON_ACCEPTABLE`: 3
- `HORIZON_ARTIFACT`: 20
- `INSUFFICIENT_SUPPORT`: 3
- `NEGATIVE`: 38

New natural-period witnesses:

- `rule_109/bg=0011/T=12/IC=10010100`: slope `-0.298274`, R^2 `0.998341`, delta `2.93%`
- `rule_109/bg=1100/T=12/IC=00101001`: slope `-0.298274`, R^2 `0.998341`, delta `2.93%`

Because these have `T_local=12`, the natural-period and common-horizon
measurements are the same run. They are valid natural-period witnesses, but not
two independent confirmations across different horizons.

New acceptable-horizon witnesses:

- `rule_109/bg=0110/T=8/IC=0000011`: at `T_WINDOW=12`, slope `-0.298928`, R^2 `0.998276`, delta `2.72%`
- `rule_109/bg=1100/T=8/IC=00000110`: at `T_WINDOW=12`, slope `-0.298928`, R^2 `0.998276`, delta `2.72%`

Baseline recovered:

- `rule_109/bg=1011/T=10/IC=00000001`: at `T_WINDOW=12`, slope `-0.307674`, R^2 `0.999349`, delta `0.13%`

No `rule_73` or external-family case (`rule_54`, `rule_94`, `rule_133`,
`rule_147`) becomes a natural-period or acceptable-horizon witness.

The updated interpretation: the ANF gradient is not merely an isolated non-T15
witness, but neither is it symmetric across the full `rule_73/rule_109` family.
Within the censused catalog, robust non-T15 evidence is concentrated in
`rule_109`.

Preprint: https://doi.org/10.5281/zenodo.21306875
Code: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

## Show HN

Title:

Show HN: ZUSE v1.22 - empirical law discovery in cellular automata

Body:

I built ZUSE, a deterministic discovery loop for elementary cellular automata.
It runs fixed evaluators over CA worlds and accumulates reproducible evidence
for empirical laws, oscillator mechanisms, and observer artifacts.

v1.22 adds a catalog census for a spatial ANF-gradient law discovered in a
T=15 oscillator and later tested outside T=15.

Key result:

- 66 non-T15 periodic-background groups censused.
- 2 new natural-period witnesses and 2 new acceptable-horizon witnesses.
- All strong/acceptable non-T15 evidence is concentrated in `rule_109`.
- No `rule_73` or external-family case becomes a strong/acceptable witness.

Preprint: https://doi.org/10.5281/zenodo.21306875
GitHub: https://github.com/conchaestradamiguelangel-droid/zuse-automat-agent

Note: previous Show HN attempts were at low account karma. Check HN account
karma before posting.
