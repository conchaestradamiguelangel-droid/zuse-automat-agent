#!/usr/bin/env python3
"""Fase 76: horizon-period audit for the T_WINDOW=12 centrality signal.

This phase does not run new ANF simulations. It consumes Fase 74's
independent-horizon measurements and asks what is special about horizon 12:
is the signal explained by period ratios, exact multiples, or the fact that
12 was the protocol's common calibration horizon?
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


OUT_DIR = Path(__file__).resolve().parent
SOURCE_JSON = OUT_DIR / "anf_centrality_independent_horizon_results.json"
RESULTS_JSON = OUT_DIR / "horizon_period_resonance_results.json"
REPORT_MD = OUT_DIR / "horizon_period_resonance_report.md"


def load_source() -> dict[str, Any]:
    return json.loads(SOURCE_JSON.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ratio_bucket(ratio: float) -> str:
    if ratio < 1.0:
        return "<1"
    if abs(ratio - 1.0) < 1e-9:
        return "1"
    if ratio <= 1.5:
        return "(1,1.5]"
    if ratio <= 2.0:
        return "(1.5,2]"
    return ">2"


def flatten_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in source["rows"]:
        t_local = int(case["T_local"])
        for horizon in source["horizons"]:
            hrow = case["horizons"][str(horizon)]
            ratio = horizon / t_local
            rows.append(
                {
                    "case": case["label"],
                    "rule": int(case["rule"]),
                    "background": str(case["background"]),
                    "word": str(case["word"]),
                    "T_local": t_local,
                    "category": str(case["category"]),
                    "positive": bool(case["positive"]),
                    "horizon": int(horizon),
                    "ratio": ratio,
                    "ratio_bucket": ratio_bucket(ratio),
                    "exact_multiple": horizon % t_local == 0,
                    "horizon_mod_T": horizon % t_local,
                    "is_common_horizon_12": horizon == 12,
                    "central_t15_like": bool(hrow["central_t15_like"]),
                    "max_active_monomial_dist": hrow["max_active_monomial_dist"],
                    "slope": hrow["slope"],
                    "r2": hrow["r2"],
                    "reliable": hrow["reliable"],
                    "active_count": hrow["active_count"],
                    "distinct_dist_count": hrow["distinct_dist_count"],
                }
            )
    return rows


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, int]]:
    grouped: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        label = "signal" if row["central_t15_like"] else "no_signal"
        grouped[str(row[key])][label] += 1
    return {k: dict(v) for k, v in sorted(grouped.items())}


def signal_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row["central_t15_like"]]


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    signal = signal_rows(rows)
    signal_by_horizon = Counter(row["horizon"] for row in signal)
    signal_by_ratio_bucket = Counter(row["ratio_bucket"] for row in signal)
    positives_at_12 = [row for row in signal if row["horizon"] == 12 and row["positive"]]
    artefacts_at_12 = [row for row in signal if row["horizon"] == 12 and not row["positive"]]
    non12_signal = [row for row in signal if row["horizon"] != 12]

    ratios_pos = [row["ratio"] for row in positives_at_12]
    ratios_art = [row["ratio"] for row in artefacts_at_12]
    exact_multiple_signal = [row for row in signal if row["exact_multiple"]]
    nonmultiple_signal = [row for row in signal if not row["exact_multiple"]]

    if len(non12_signal) == 0 and len(signal) > 0:
        status = "COMMON_HORIZON_12_PROTOCOL_RESONANCE"
        interpretation = (
            "The central T15-like signature appears exclusively at the original common horizon 12. "
            "Within that horizon, positives occupy the low-oversampling band 12/T_local<=1.5, "
            "while artefacts occupy short-period exact multiples 12/T_local in {2,4}. "
            "The result explains Fase 73 as a protocol resonance, not as a horizon-independent law."
        )
    elif non12_signal:
        status = "HORIZON_SIGNAL_EXTENDS_BEYOND_12"
        interpretation = (
            "At least one non-12 horizon also produces central T15-like signal; the effect is not unique to "
            "the original common horizon."
        )
    else:
        status = "NO_HORIZON_SIGNAL"
        interpretation = "No central T15-like signal is present in the audited horizons."

    return {
        "status": status,
        "interpretation": interpretation,
        "case_count": len({row["case"] for row in rows}),
        "horizon_measurement_count": len(rows),
        "signal_count": len(signal),
        "signal_by_horizon": dict(sorted(signal_by_horizon.items())),
        "signal_by_ratio_bucket": dict(sorted(signal_by_ratio_bucket.items())),
        "signal_exact_multiple_count": len(exact_multiple_signal),
        "signal_nonmultiple_count": len(nonmultiple_signal),
        "non12_signal_count": len(non12_signal),
        "positive_signal_at_12_count": len(positives_at_12),
        "artifact_signal_at_12_count": len(artefacts_at_12),
        "positive_ratios_at_12": ratios_pos,
        "artifact_ratios_at_12": ratios_art,
        "positive_ratio_range_at_12": [min(ratios_pos), max(ratios_pos)] if ratios_pos else None,
        "artifact_ratio_range_at_12": [min(ratios_art), max(ratios_art)] if ratios_art else None,
        "signal_exact_multiple_labels": [row["case"] for row in exact_multiple_signal],
        "signal_nonmultiple_labels": [row["case"] for row in nonmultiple_signal],
    }


def build_results() -> dict[str, Any]:
    source = load_source()
    rows = flatten_rows(source)
    return {
        "phase": 76,
        "source": SOURCE_JSON.name,
        "rows": rows,
        "summary": summarize(rows),
        "counts": {
            "by_horizon": count_by(rows, "horizon"),
            "by_ratio_bucket": count_by(rows, "ratio_bucket"),
            "by_exact_multiple": count_by(rows, "exact_multiple"),
            "by_common_horizon_12": count_by(rows, "is_common_horizon_12"),
        },
    }


def fmt(value: Any, digits: int = 3) -> str:
    if value is None:
        return "None"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_report(data: dict[str, Any]) -> None:
    summary = data["summary"]
    rows = data["rows"]
    lines: list[str] = [
        "# Fase 76 - Horizon-Period Resonance Audit",
        "",
        "## Question",
        "",
        "Why does `T_WINDOW=12` produce the `central_t15_like` signal for both",
        "true positives and Fase 72 centrality artefacts, while horizons `8`,",
        "`16`, and `20` do not?",
        "",
        "This phase runs no new simulations. It derives horizon/period features",
        "from Fase 74's four-horizon ANF measurements.",
        "",
        "## Horizon Signal Counts",
        "",
        "| horizon | signal | no_signal |",
        "|---:|---:|---:|",
    ]
    for horizon, counts in data["counts"]["by_horizon"].items():
        lines.append(f"| {horizon} | {counts.get('signal', 0)} | {counts.get('no_signal', 0)} |")

    lines.extend([
        "",
        "## Ratio Buckets",
        "",
        "| ratio bucket | signal | no_signal |",
        "|---|---:|---:|",
    ])
    for bucket, counts in data["counts"]["by_ratio_bucket"].items():
        lines.append(f"| {bucket} | {counts.get('signal', 0)} | {counts.get('no_signal', 0)} |")

    lines.extend([
        "",
        "## Signal Rows",
        "",
        "| case | horizon | T_local | 12/T or H/T | exact_multiple | positive | slope | R^2 | dist |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for row in [row for row in rows if row["central_t15_like"]]:
        lines.append(
            f"| {row['case']} | {row['horizon']} | {row['T_local']} | {fmt(row['ratio'])} | "
            f"{row['exact_multiple']} | {row['positive']} | {fmt(row['slope'], 6)} | "
            f"{fmt(row['r2'], 6)} | {fmt(row['max_active_monomial_dist'])} |"
        )

    lines.extend([
        "",
        "## Interpretation",
        "",
        f"Verdict: `{summary['status']}`.",
        "",
        summary["interpretation"],
        "",
        "At `T_WINDOW=12`, the same central T15-like signature appears in all 13",
        "centrality candidates. It is therefore not a positive/negative",
        "separator. The split inside horizon 12 is instead:",
        "",
        f"- positives: ratio range {summary['positive_ratio_range_at_12']} (`12/T_local <= 1.5`)",
        f"- artefacts: ratio range {summary['artifact_ratio_range_at_12']} (`12/T_local >= 2`)",
        "",
        "That second bullet is exactly why short-period cases looked like",
        "centrality false positives: `T=3` and `T=6` are exact divisors of the",
        "12-step common window. But exact divisibility is not sufficient either,",
        "because true positives include non-multiple ratios such as `12/8=1.5`",
        "and `12/10=1.2`.",
        "",
        "## Methodological Limit",
        "",
        "- This audit explains the Fase 72-74 centrality candidates only; it does",
        "  not claim a universal property of all ECA horizons.",
        "- The result identifies a protocol-level resonance at the original common",
        "  horizon 12, not a new physical period-12 law.",
        "- Future work should not use `T_WINDOW=12` as a free discriminator unless",
        "  the horizon is justified independently of the Fase 55 label rule.",
        "",
    ])
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    data = build_results()
    save_json(RESULTS_JSON, data)
    write_report(data)
    print(f"Wrote {RESULTS_JSON}")
    print(f"Wrote {REPORT_MD}")
    print(f"Status: {data['summary']['status']}")


if __name__ == "__main__":
    main()
