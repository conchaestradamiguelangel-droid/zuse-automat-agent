# Fase 75 - ANF Centrality: Epistemic Closure

## Purpose

Close the ANF-centrality-as-discriminator line of inquiry (Fases 71-74)
before opening a new question. No new simulations run in this phase; this
is a synthesis of Fases 71-74 results, written to prevent re-chasing the
same lead in a future phase.

## What Was Tested

`max_active_monomial_dist == 0` (exact ANF centrality of the maximum
active-monomial support) as a classifier for `positive` vs `non-positive`
periodic-background cases, across four phases:

| Phase | Scope | Result |
|---|---|---|
| 71 | 17 rule_109 cases | `dist=0` separates 5 positives from 12 non-positives perfectly (TP=5, FP=0). |
| 72 | Full Fase 55 census, 66 cases, 6 rules | Does not generalize: TP=5, FP=8, TN=53, FN=0 (precision=0.385). |
| 73 (original) | Same census + `T_local>=8` | Appeared to separate perfectly (TP=5, FP=0). Later found circular: `T_local>=8` is the same condition already used inside `classify_case()` to split `HORIZON_ACCEPTABLE` from `HORIZON_ARTIFACT`, so the label being predicted was partly built from the predictor. Verdict corrected to `CENTRALITY_HORIZON_FILTER_RECAPITULATES_LABEL` (commit `9d5767f`). |
| 74 | Same 13 centrality candidates, horizons 8/12/16/20, label-independent | Signal (`central_t15_like`) appears only at `T_WINDOW=12`, for both the 5 positives and the 8 artefacts. Verdict `CENTRALITY_HORIZON_DEPENDENT` (commit `d78dd17`). |

## What Is Established (safe to reuse)

1. **Local validity inside rule_109**: within the 17-case rule_109
   subcatalogue, `dist=0` is a perfect discriminator. This finding stands
   and is not contradicted by anything in Fases 72-74. It should be cited
   as rule_109-local, never as general.
2. **No global discriminative power**: across the 6-rule, 66-case census,
   `dist=0` alone has precision=0.385. It is not usable as a standalone
   classifier outside rule_109.
3. **The apparent horizon fix does not survive independent testing**: adding
   `T_local>=8` looked like a fix, but it only reproduces a boundary that
   was already inside the label definition. When re-tested at horizons
   that do not reuse that boundary (8, 16, 20), the signal disappears for
   every case, positive or artefact. There is no evidence that centrality
   plus horizon is a real, horizon-independent physical filter.
4. **`T_WINDOW=12` is a protocol artefact, not a validated constant**: the
   signal's exclusive appearance at horizon 12 means 12 was doing work in
   the original census construction (likely tied to how `T_local` values
   8/10/12 relate to a 12-step common window), not evidence of a physical
   period-12 discriminant.

## What Must Not Be Claimed Going Forward

- "ANF centrality discriminates positives from non-positives" — false
  outside rule_109.
- "Centrality + horizon sufficiency is a validated second filter" —
  false; this was the corrected claim from Fase 73/74.
- Any claim using `T_WINDOW=12` as a physically meaningful constant without
  first explaining why 12 specifically produces the effect (this is now
  the open question, see Fase 76).

## Recommendation

Do not reopen ANF centrality as a discriminator lead unless a genuinely
new external positive case (non-rule_109) becomes available in the
census — at that point the rule_109-local finding could be retested with
real recall data, which does not currently exist.

The productive follow-up is not "does centrality work" but "why does the
common horizon 12 make the signal appear for both positives and
artefacts" — opened as Fase 76.

## Provenance

- Artifacts referenced: `outputs/periodic_backgrounds/rule109_static_anf_geometry_*`
  (Fase 71), `anf_centrality_global_*` (Fase 72),
  `anf_centrality_horizon_filter_*` (Fase 73, corrected in `9d5767f`),
  `anf_centrality_independent_horizon_*` (Fase 74).
- No paper, DOI, tag, or release state touched by this phase.
- No new simulation or script executed; this is a documentation-only phase.
