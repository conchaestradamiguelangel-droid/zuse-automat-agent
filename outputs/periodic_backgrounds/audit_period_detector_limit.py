#!/usr/bin/env python3
"""Fase 89: audit false negatives caused by the source period cap."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parent.parent
SWEEP_SCRIPT = OUT_DIR / "sweep_periodic_background_oscillators.py"
FASE86_RESULTS = OUT_DIR / "rule73_h11_physical_selector_realizability_results.json"
FASE88_SCRIPT = OUT_DIR / "analyze_rule73_h11_selector_branches.py"
BASELINE_CATALOG = OUT_DIR / "periodic_background_oscillator_results.jsonl"
LEN8_CATALOG = ROOT / "outputs" / "periodic_backgrounds_len8" / "sweep_len8_results.jsonl"
RESULTS_JSON = OUT_DIR / "period_detector_limit_audit_results.json"
REPORT_MD = OUT_DIR / "period_detector_limit_audit_report.md"

RULE = 73
SOURCE_STEPS = 300
BURN_IN = 80
LONG_STEPS = 1000
TAIL_START = 500
SOURCE_PERIOD_MIN = 2
SOURCE_PERIOD_MAX = 16
DIAGNOSTIC_MAX_PERIOD = 120
MAX_SPAN = 32
EXPECTED_RUNS = 2008
BASELINE_TOTAL_RUNS = 256 * 15 * 502
LEN8_TOTAL_RUNS = 256 * 30 * 502


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def count_jsonl(path: Path) -> int:
    with path.open("rb") as handle:
        return sum(1 for line in handle if line.strip())


def sha256_json(value: Any) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def canonical_cycle(shapes: list[Any], period: int) -> tuple[tuple[int, ...], ...]:
    sequence = tuple(
        tuple(int(offset) for offset in shape.offsets)
        for shape in shapes[-period:]
    )
    return min(sequence[index:] + sequence[:index] for index in range(period))


def build_background_frames(base, background: str) -> list[tuple[int, ...]]:
    frames = [base.background_state(background)]
    for _ in range(LONG_STEPS):
        frames.append(base.eca_step_state(frames[-1], RULE))
    return frames


def simulate_shapes(
    base,
    bg_frames: list[tuple[int, ...]],
    word_value: int,
    word_len: int,
) -> dict[str, Any]:
    diff = base.initial_diff(word_value, word_len, bg_frames[0])
    if not diff:
        return {
            "shapes": [],
            "termination": "ZERO_INITIAL_DEFECT",
            "termination_time": 0,
        }
    shapes = []
    termination = None
    termination_time = None
    for time in range(LONG_STEPS + 1):
        if time >= BURN_IN:
            shape = base.linear_shape(diff)
            if shape is None:
                termination = "EXTINCT_OR_WRAPPED"
                termination_time = time
                break
            if int(shape.span) > MAX_SPAN:
                termination = "SPAN_ESCAPE"
                termination_time = time
                break
            shapes.append(shape)
        if time < LONG_STEPS:
            diff = base.eca_step_diff(
                diff,
                bg_frames[time],
                bg_frames[time + 1],
                RULE,
            )
            if not diff and time + 1 < BURN_IN:
                termination = "EXTINCT_PREBURN"
                termination_time = time + 1
                break
    persistent = (
        termination is None
        and len(shapes) == LONG_STEPS - BURN_IN + 1
    )
    return {
        "shapes": shapes,
        "termination": termination,
        "termination_time": termination_time,
        "persistent_bounded": persistent,
    }


def source_classification(base, shapes: list[Any]) -> dict[str, Any]:
    needed = SOURCE_STEPS - BURN_IN + 1
    if len(shapes) < needed:
        return {"kind": "SOURCE_UNBOUNDED_OR_EXTINCT", "period": None, "drift": None}
    source_shapes = shapes[:needed]
    stationary = base.detect_stationary(source_shapes)
    moving, alias = base.detect_moving(source_shapes)
    if stationary is not None:
        return {
            "kind": "STATIONARY",
            "period": int(stationary["period_T"]),
            "drift": 0,
        }
    if moving is not None:
        return {
            "kind": "MOVING",
            "period": int(moving["period_T"]),
            "drift": int(moving["drift_per_period"]),
        }
    if alias is not None:
        return {
            "kind": "PERIOD1_MOVING_ALIAS",
            "period": 1,
            "drift": int(alias["drift_per_period"]),
        }
    return {"kind": "UNCLASSIFIED_BOUNDED", "period": None, "drift": None}


def exact_dynamics(shapes: list[Any], max_period: int) -> dict[str, Any]:
    """Apply the source detector's strict all-pairs recurrence at a wider cap."""
    if not shapes:
        return {"kind": "NO_SHAPES", "period": None, "drift": None}
    for period in range(1, min(max_period, len(shapes) - 1) + 1):
        if all(
            shapes[index].offsets == shapes[index + period].offsets
            and int(shapes[index].min_pos) == int(shapes[index + period].min_pos)
            for index in range(len(shapes) - period)
        ):
            return {"kind": "STATIONARY", "period": period, "drift": 0}
    for period in range(1, min(max_period, len(shapes) - 1) + 1):
        drift = None
        valid = True
        for index in range(len(shapes) - period):
            left = shapes[index]
            right = shapes[index + period]
            if left.offsets != right.offsets:
                valid = False
                break
            observed = int(right.min_pos) - int(left.min_pos)
            if observed == 0:
                valid = False
                break
            if drift is None:
                drift = observed
            elif observed != drift:
                valid = False
                break
        if valid and drift is not None:
            return {"kind": "MOVING", "period": period, "drift": drift}
    return {"kind": "UNCLASSIFIED", "period": None, "drift": None}


def diagnostic_classification(fase88, shapes: list[Any], persistent: bool) -> dict[str, Any]:
    if not persistent:
        return {"kind": "NOT_PERSISTENT_BOUNDED", "period": None, "drift": None}
    return fase88.detect_tail_dynamics(shapes)


def class_label(row: dict[str, Any]) -> str:
    period = row.get("period")
    return f"{row['kind']}_T{period}" if period is not None else row["kind"]


def public_case(
    background: str,
    word_len: int,
    word: str,
    source: dict[str, Any],
    extended_source: dict[str, Any],
    diagnostic: dict[str, Any],
    simulation: dict[str, Any],
) -> dict[str, Any]:
    extended_period = extended_source.get("period")
    cap_miss = (
        source["kind"] == "UNCLASSIFIED_BOUNDED"
        and extended_source["kind"] in {"STATIONARY", "MOVING"}
        and extended_period is not None
        and int(extended_period) > SOURCE_PERIOD_MAX
    )
    long_confirms_cap_miss = (
        cap_miss
        and diagnostic["kind"] == extended_source["kind"]
        and diagnostic.get("period") == extended_period
        and diagnostic.get("drift") == extended_source.get("drift")
    )
    delayed_short = (
        source["kind"] == "UNCLASSIFIED_BOUNDED"
        and extended_source["kind"] == "UNCLASSIFIED"
        and diagnostic["kind"] in {"STATIONARY", "MOVING"}
        and diagnostic.get("period") is not None
        and 2 <= int(diagnostic["period"]) <= SOURCE_PERIOD_MAX
    )
    delayed_long = (
        source["kind"] == "UNCLASSIFIED_BOUNDED"
        and extended_source["kind"] == "UNCLASSIFIED"
        and diagnostic["kind"] in {"STATIONARY", "MOVING"}
        and diagnostic.get("period") is not None
        and int(diagnostic["period"]) > SOURCE_PERIOD_MAX
    )
    static_t1 = (
        source["kind"] == "UNCLASSIFIED_BOUNDED"
        and extended_source["kind"] == "STATIONARY"
        and extended_period == 1
    )
    cycle_hash = None
    if diagnostic["kind"] in {"STATIONARY", "MOVING"}:
        diagnostic_period = int(diagnostic["period"])
        cycle_hash = sha256_json(
            {
                "shape_cycle": canonical_cycle(simulation["shapes"], diagnostic_period),
                "kind": diagnostic["kind"],
                "drift": diagnostic.get("drift"),
            }
        )
    return {
        "background": background,
        "word_len": word_len,
        "word": word,
        "source_class": class_label(source),
        "source_kind": source["kind"],
        "source_period": source.get("period"),
        "source_drift": source.get("drift"),
        "extended_source_class": class_label(extended_source),
        "extended_source_kind": extended_source["kind"],
        "extended_source_period": extended_source.get("period"),
        "extended_source_drift": extended_source.get("drift"),
        "diagnostic_class": class_label(diagnostic),
        "diagnostic_kind": diagnostic["kind"],
        "diagnostic_period": diagnostic.get("period"),
        "diagnostic_drift": diagnostic.get("drift"),
        "persistent_bounded": bool(simulation.get("persistent_bounded")),
        "termination": simulation.get("termination"),
        "termination_time": simulation.get("termination_time"),
        "period_cap_false_negative": cap_miss,
        "long_confirms_period_cap_false_negative": long_confirms_cap_miss,
        "delayed_short_period": delayed_short,
        "delayed_long_period": delayed_long,
        "static_t1_excluded_by_design": static_t1,
        "cycle_sha256": cycle_hash,
    }


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    source_counts = Counter(row["source_class"] for row in rows)
    extended_source_counts = Counter(row["extended_source_class"] for row in rows)
    diagnostic_counts = Counter(row["diagnostic_class"] for row in rows)
    cap_misses = [row for row in rows if row["period_cap_false_negative"]]
    confirmed_cap_misses = [
        row for row in cap_misses if row["long_confirms_period_cap_false_negative"]
    ]
    delayed = [row for row in rows if row["delayed_short_period"]]
    delayed_long = [row for row in rows if row["delayed_long_period"]]
    static = [row for row in rows if row["static_t1_excluded_by_design"]]
    cap_periods = Counter(int(row["extended_source_period"]) for row in cap_misses)
    cap_backgrounds = Counter(row["background"] for row in cap_misses)
    cap_attractors = {
        row["cycle_sha256"] for row in cap_misses if row["cycle_sha256"] is not None
    }
    source_detected = sum(
        row["source_kind"] in {"STATIONARY", "MOVING"} for row in rows
    )
    source_detected_long_matches = sum(
        row["source_kind"] in {"STATIONARY", "MOVING"}
        and row["diagnostic_kind"] == row["source_kind"]
        and row["diagnostic_period"] == row["source_period"]
        and row["diagnostic_drift"] == row["source_drift"]
        for row in rows
    )
    long_periodic = sum(
        row["diagnostic_kind"] in {"STATIONARY", "MOVING"} for row in rows
    )
    return {
        "processed_runs": len(rows),
        "source_detected_oscillator_count": source_detected,
        "source_detected_long_match_count": source_detected_long_matches,
        "source_detected_long_mismatch_count": source_detected - source_detected_long_matches,
        "source_class_counts": dict(sorted(source_counts.items())),
        "extended_source_class_counts": dict(sorted(extended_source_counts.items())),
        "diagnostic_periodic_count": long_periodic,
        "diagnostic_class_counts": dict(sorted(diagnostic_counts.items())),
        "persistent_bounded_count": sum(row["persistent_bounded"] for row in rows),
        "period_cap_false_negative_count": len(cap_misses),
        "long_confirmed_period_cap_false_negative_count": len(confirmed_cap_misses),
        "period_cap_false_negative_periods": {
            str(period): count for period, count in sorted(cap_periods.items())
        },
        "period_cap_false_negative_backgrounds": dict(sorted(cap_backgrounds.items())),
        "period_cap_false_negative_unique_attractors": len(cap_attractors),
        "period_cap_missed_fraction_of_long_periodic": (
            len(cap_misses) / long_periodic if long_periodic else 0.0
        ),
        "period_cap_increase_over_source_detected": (
            len(cap_misses) / source_detected if source_detected else 0.0
        ),
        "delayed_short_period_count": len(delayed),
        "delayed_long_period_count": len(delayed_long),
        "static_t1_excluded_by_design_count": len(static),
        "cap_miss_rate_among_source_unclassified": (
            len(cap_misses)
            / sum(row["source_kind"] == "UNCLASSIFIED_BOUNDED" for row in rows)
            if any(row["source_kind"] == "UNCLASSIFIED_BOUNDED" for row in rows)
            else 0.0
        ),
    }


def verdict(summary: dict[str, Any]) -> tuple[str, str]:
    if summary["period_cap_false_negative_count"]:
        return (
            "SOURCE_PERIOD_CAP_FALSE_NEGATIVES_FOUND_LOCAL_COHORT",
            "The original T<=16 detector omits persistent long-period oscillators in the directly audited 2,008-run cohort. The archived global catalogs remain unauditable without a full re-sweep because they store positives only.",
        )
    return (
        "NO_SOURCE_PERIOD_CAP_FALSE_NEGATIVES_IN_LOCAL_COHORT",
        "No persistent T>16 oscillator was omitted in the directly audited cohort. This does not establish completeness of the positive-only global catalogs.",
    )


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    lines = [
        "# Fase 89: Source Period-Cap Integrity Audit",
        "",
        "## Question",
        "",
        "Did the original oscillator detector's period cap T<=16 cause additional",
        "persistent oscillators to be omitted as unclassified/nonstationary cases?",
        "",
        "## Archive Preflight",
        "",
        "The two historical oscillator JSONL catalogs are positive-only archives:",
        "they contain detected hits, not one labeled row for every attempted run.",
        "Therefore global false negatives cannot be reconstructed from those files.",
        "",
        f"- Baseline periodic-background sweep: `{data['archive_preflight']['baseline_total_runs']}` attempted runs, `{data['archive_preflight']['baseline_archived_positive_rows']}` archived positive rows.",
        f"- Primitive len8 sweep: `{data['archive_preflight']['len8_total_runs']}` attempted runs, `{data['archive_preflight']['len8_archived_positive_rows']}` archived positive rows.",
        f"- Full historical re-sweep required for global count: `{data['archive_preflight']['global_resweep_required_runs']}` runs.",
        "",
        "Fase 89 consequently audits the complete source cohort directly implicated",
        "by Fases 86-88 rather than pretending the positive-only files contain negatives.",
        "",
        "## Predeclared Local Protocol",
        "",
        "- Rule: `73`; four h=11 causal-class backgrounds.",
        "- ICs: all 502 non-zero centered words of length 1..8 per background.",
        "- Cohort: 2,008 physical runs.",
        "- Source classification: burn-in 80, t<=300, stationary/moving T=2..16.",
        "- Independent diagnostic: t<=1000, exact tail recurrence on t=500..1000, T=1..120, span<=32.",
        "- Counterfactual source-window classification: same t=80..300 frames and",
        "  same strict all-pairs recurrence, but period cap extended to 120.",
        "- Period-cap false negative: source bounded but unclassified and that",
        "  counterfactual source-window detector finds stationary/moving T>16.",
        "- Long-tail classification independently checks the same kind/period on t=500..1000.",
        "- Static T=1 and delayed T<=16 cases are counted separately.",
        "- No source threshold, paper, DOI, tag, or release is changed.",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        data["verdict_reason"],
        "",
        f"- Runs processed: `{summary['processed_runs']}`",
        f"- Source-detected stationary/moving oscillators: `{summary['source_detected_oscillator_count']}`",
        f"- Source detections retaining the same long-tail class: `{summary['source_detected_long_match_count']}`",
        f"- Source detections changing class at long horizon: `{summary['source_detected_long_mismatch_count']}`",
        f"- Persistent bounded at t=1000: `{summary['persistent_bounded_count']}`",
        f"- Long-tail periodic cases: `{summary['diagnostic_periodic_count']}`",
        f"- False negatives attributable specifically to T<=16: `{summary['period_cap_false_negative_count']}`",
        f"- Same kind/period independently confirmed on t=500..1000: `{summary['long_confirmed_period_cap_false_negative_count']}`",
        f"- Unique long-period attractors among those false negatives: `{summary['period_cap_false_negative_unique_attractors']}`",
        f"- Missed share of long-periodic cohort: `{summary['period_cap_missed_fraction_of_long_periodic']:.6f}`",
        f"- Increase relative to source-detected count: `{summary['period_cap_increase_over_source_detected']:.6f}`",
        f"- Long-period distribution: `{summary['period_cap_false_negative_periods']}`",
        f"- Background distribution: `{summary['period_cap_false_negative_backgrounds']}`",
        f"- Delayed T<=16 cases (not period-cap misses): `{summary['delayed_short_period_count']}`",
        f"- Delayed T>16 cases (not period-cap-only misses): `{summary['delayed_long_period_count']}`",
        f"- Static T=1 cases excluded by source design: `{summary['static_t1_excluded_by_design_count']}`",
        "",
        "### Source classes",
        "",
    ]
    for key, count in summary["source_class_counts"].items():
        lines.append(f"- `{key}`: `{count}`")
    lines.extend(["", "### Counterfactual source-window classes with cap 120", ""])
    for key, count in summary["extended_source_class_counts"].items():
        lines.append(f"- `{key}`: `{count}`")
    lines.extend(["", "### Long-tail classes", ""])
    for key, count in summary["diagnostic_class_counts"].items():
        lines.append(f"- `{key}`: `{count}`")
    misses = [row for row in data["cases"] if row["period_cap_false_negative"]]
    lines.extend(
        [
            "",
            "## Period-Cap False Negatives",
            "",
            "| background | IC | source | source cap=120 | long-tail | drift | attractor hash |",
            "| --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in misses:
        lines.append(
            f"| `{row['background']}` | `{row['word']}` | `{row['source_class']}` | "
            f"`{row['extended_source_class']}` | `{row['diagnostic_class']}` | "
            f"{row['diagnostic_drift']} | `{row['cycle_sha256']}` |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "This phase distinguishes a demonstrated local detector defect from an",
            "unmeasured global one. Every listed T>16 row is a real false negative",
            "of the historical T<=16 detector inside the 2,008-run cohort. The phase",
            "does not assign a global correction count to the two positive-only",
            "archives; doing so requires re-running 5,783,040 source configurations.",
            "",
            "Earlier phase-local claims remain reproducible under their declared",
            "source protocol, but any wording implying that its 'any period' count",
            "was exhaustive beyond T=16 must be read as detector-bounded.",
            "",
            "## Impact on Earlier Phases",
            "",
            "- Fase 86's `stationary_any_period_count=1516` is exactly the source",
            "  detector count and must be interpreted as stationary T=2..16, not",
            "  literally all periods. The corrected local long-periodic count is 1879.",
            "- All 1516 source detections retain the same kind and period at long",
            "  horizon; no previously detected oscillator is invalidated.",
            "- The T=12 cohort used by Fases 81-87 remains 165 cases and is unchanged;",
            "  the newly recovered cases have periods 18..120.",
            "- Fase 87's 40 rescue trajectories are included among the recovered T=30",
            "  cases, agreeing with Fase 88. Reachability and exact-operator results",
            "  remain valid; only the historical NONSTATIONARY interpretation changes.",
            "- Completeness claims about the 1,927,680-run baseline and 3,855,360-run",
            "  len8 sweeps remain untested until those positive-only cohorts are re-run.",
            "",
            "## Methodological Limits",
            "",
            "- Exhaustive only for rule_73, the four Fase 84 backgrounds, and centered ICs length 1..8.",
            "- Tail recurrence is verified through t=1000 and periods<=120, not proved indefinitely.",
            "- The global baseline and len8 catalogs remain positive-only; no global false-negative rate is claimed.",
            "- The audit changes no historical rows or published version.",
            "",
        ]
    )
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def run(preflight_only: bool = False) -> dict[str, Any]:
    fase86 = load_json(FASE86_RESULTS)
    backgrounds = tuple(fase86["preflight"]["backgrounds"])
    archive_preflight = {
        "baseline_catalog": str(BASELINE_CATALOG.relative_to(ROOT)),
        "baseline_total_runs": BASELINE_TOTAL_RUNS,
        "baseline_archived_positive_rows": count_jsonl(BASELINE_CATALOG),
        "len8_catalog": str(LEN8_CATALOG.relative_to(ROOT)),
        "len8_total_runs": LEN8_TOTAL_RUNS,
        "len8_archived_positive_rows": count_jsonl(LEN8_CATALOG),
        "global_resweep_required_runs": BASELINE_TOTAL_RUNS + LEN8_TOTAL_RUNS,
        "negative_rows_archived": False,
    }
    preflight = {
        "rule": RULE,
        "backgrounds": list(backgrounds),
        "ic_count_per_background": 502,
        "source_run_count": len(backgrounds) * 502,
        "source_steps": SOURCE_STEPS,
        "source_period_range": [SOURCE_PERIOD_MIN, SOURCE_PERIOD_MAX],
        "long_steps": LONG_STEPS,
        "tail_start": TAIL_START,
        "diagnostic_period_range": [1, DIAGNOSTIC_MAX_PERIOD],
        "max_span": MAX_SPAN,
        "threshold_fitting": False,
    }
    if preflight_only:
        return {
            "phase": 89,
            "archive_preflight": archive_preflight,
            "preflight": preflight,
        }

    base = load_module("fase89_source_detector", SWEEP_SCRIPT)
    fase88 = load_module("fase89_long_detector", FASE88_SCRIPT)
    words = list(base.ic_words())
    rows = []
    for background in backgrounds:
        bg_frames = build_background_frames(base, background)
        for word_len, word_value, word in words:
            simulation = simulate_shapes(base, bg_frames, word_value, word_len)
            source = source_classification(base, simulation["shapes"])
            source_shape_count = SOURCE_STEPS - BURN_IN + 1
            extended_source = (
                exact_dynamics(
                    simulation["shapes"][:source_shape_count],
                    DIAGNOSTIC_MAX_PERIOD,
                )
                if len(simulation["shapes"]) >= source_shape_count
                else {"kind": "NOT_AVAILABLE", "period": None, "drift": None}
            )
            diagnostic = diagnostic_classification(
                fase88,
                simulation["shapes"],
                bool(simulation.get("persistent_bounded")),
            )
            rows.append(
                public_case(
                    background,
                    int(word_len),
                    word,
                    source,
                    extended_source,
                    diagnostic,
                    simulation,
                )
            )
    if len(rows) != EXPECTED_RUNS:
        raise RuntimeError(f"Processed {len(rows)} runs, expected {EXPECTED_RUNS}")
    rows.sort(key=lambda row: (row["background"], row["word_len"], row["word"]))
    summary = summarize(rows)
    status, reason = verdict(summary)
    data = {
        "phase": 89,
        "status": status,
        "verdict_reason": reason,
        "archive_preflight": archive_preflight,
        "preflight": preflight,
        "summary": summary,
        "cases": rows,
    }
    RESULTS_JSON.write_text(
        json.dumps(data, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_report(data)
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    data = run(preflight_only=args.preflight_only)
    if args.preflight_only:
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0
    print(f"status={data['status']}")
    print(json.dumps(data["summary"], indent=2, sort_keys=True))
    print(f"report={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
