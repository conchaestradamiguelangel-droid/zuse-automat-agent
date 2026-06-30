#!/usr/bin/env python3
"""Fase 43: pre-SIFT ROBDD order-sensitivity audit.

Fase 42 already materialized three ROBDD variable orders for the dense T=15
cone: natural, reverse, and center_out. A broader structural-order search can
make intermediate ROBDDs explode, so this phase first extracts the order signal
from the reproducible Fase 42 data before committing to full dynamic reordering.

This script does not rebuild BDDs. It analyzes the existing tracked
cone_bdd_results.json and asks:

- Is any tested order globally smaller than natural?
- Which representatives are order-sensitive?
- Does order sensitivity change the Fase 42 support result? (It should not.)

The result is a bounded preflight for SIFT, not a full SIFT run and not a global
optimality certificate over all 25! variable orders.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
SOURCE_JSON = OUT_DIR / "cone_bdd_results.json"
RESULTS_JSON = OUT_DIR / "bdd_sift_order_results.json"
REPORT_MD = OUT_DIR / "bdd_sift_order_report.md"
WINDOW_CELLS = 25


def percent_reduction(new: int, old: int) -> float:
    return round(100.0 * (old - new) / old, 3)


def load_source() -> dict:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    rows = data.get("rows", [])
    orders = sorted({row["order"] for row in rows})
    if not {"natural", "reverse", "center_out"}.issubset(set(orders)):
        raise RuntimeError(
            "Fase 43 requires Fase 42 results with natural, reverse, and center_out orders. "
            f"Found orders: {orders}"
        )
    return data


def summarize_order(order: str, rows: list[dict]) -> dict:
    subset = [row for row in rows if row["order"] == order]
    active = [row["active_reachable_nodes"] for row in subset]
    vector = [row["vector_reachable_nodes"] for row in subset]
    return {
        "order": order,
        "total_active_nodes": sum(active),
        "total_vector_nodes": sum(vector),
        "active_nodes_min": min(active),
        "active_nodes_max": max(active),
        "vector_nodes_min": min(vector),
        "vector_nodes_max": max(vector),
        "active_support_min": min(row["active_support_size"] for row in subset),
        "active_support_max": max(row["active_support_size"] for row in subset),
        "vector_support_min": min(row["vector_support_size"] for row in subset),
        "vector_support_max": max(row["vector_support_size"] for row in subset),
    }


def analyze() -> dict:
    source = load_source()
    rows = source["rows"]
    orders = sorted({row["order"] for row in rows})
    summaries = [summarize_order(order, rows) for order in orders]
    summaries_sorted = sorted(summaries, key=lambda item: (item["total_active_nodes"], item["total_vector_nodes"]))
    natural = next(item for item in summaries if item["order"] == "natural")
    best = summaries_sorted[0]

    grouped: dict[tuple[int, str], list[dict]] = defaultdict(list)
    for row in rows:
        grouped[(int(row["rule"]), row["background"])].append(row)

    per_rep = []
    for key, items in sorted(grouped.items()):
        natural_row = next(row for row in items if row["order"] == "natural")
        best_row = min(items, key=lambda row: (row["active_reachable_nodes"], row["vector_reachable_nodes"]))
        worst_row = max(items, key=lambda row: row["active_reachable_nodes"])
        per_rep.append(
            {
                "rule": key[0],
                "background": key[1],
                "family_id": natural_row["family_id"],
                "natural_active_nodes": natural_row["active_reachable_nodes"],
                "best_order": best_row["order"],
                "best_active_nodes": best_row["active_reachable_nodes"],
                "active_reduction_percent": percent_reduction(
                    best_row["active_reachable_nodes"], natural_row["active_reachable_nodes"]
                ),
                "worst_order": worst_row["order"],
                "worst_active_nodes": worst_row["active_reachable_nodes"],
                "order_sensitivity_ratio": round(
                    worst_row["active_reachable_nodes"] / best_row["active_reachable_nodes"], 3
                ),
            }
        )

    best_not_natural = sum(1 for row in per_rep if row["best_order"] != "natural")
    center_out_worst = sum(1 for row in per_rep if row["worst_order"] == "center_out")
    max_sensitivity = max(row["order_sensitivity_ratio"] for row in per_rep)
    all_support_25 = all(
        row["active_support_size"] == WINDOW_CELLS and row["vector_support_size"] == WINDOW_CELLS
        for row in rows
    )

    status = "ORDER_SENSITIVITY_FOUND"
    if best["order"] == "natural":
        status = "NO_GLOBAL_ORDER_IMPROVEMENT_FOUND"

    return {
        "status": status,
        "source": str(SOURCE_JSON),
        "record_count": len(grouped),
        "orders": orders,
        "search_scope": "pre_sift_existing_fase42_orders",
        "natural_total_active_nodes": natural["total_active_nodes"],
        "natural_total_vector_nodes": natural["total_vector_nodes"],
        "best_global_order": best["order"],
        "best_global_total_active_nodes": best["total_active_nodes"],
        "best_global_total_vector_nodes": best["total_vector_nodes"],
        "best_global_active_reduction_percent": percent_reduction(
            best["total_active_nodes"], natural["total_active_nodes"]
        ),
        "best_global_vector_reduction_percent": percent_reduction(
            best["total_vector_nodes"], natural["total_vector_nodes"]
        ),
        "representatives_where_best_not_natural": best_not_natural,
        "representatives_where_center_out_worst": center_out_worst,
        "max_order_sensitivity_ratio": max_sensitivity,
        "all_orders_keep_25_input_support": all_support_25,
        "summary_by_order": summaries_sorted,
        "per_representative": per_rep,
    }


def write_report(data: dict) -> None:
    lines = [
        "# Fase 43: ROBDD Order-Sensitivity Preflight",
        "",
        "## Question",
        "",
        "Fase 42 established that all 25 causal-cone inputs are semantically",
        "necessary. Fase 43 does not reopen that question. It asks whether the",
        "ROBDD representation is sensitive to variable order, using the three",
        "orders already materialized in Fase 42: `natural`, `reverse`, and",
        "`center_out`.",
        "",
        "This is a pre-SIFT audit. It is not a full dynamic-reordering run and",
        "does not certify global BDD optimality over all 25! variable orders.",
        "",
        "## Summary",
        "",
        f"Status: `{data['status']}`.",
        "",
        f"- Orders analyzed: {', '.join(f'`{order}`' for order in data['orders'])}",
        f"- Best global order: `{data['best_global_order']}`",
        f"- Natural total active nodes: {data['natural_total_active_nodes']}",
        f"- Best global total active nodes: {data['best_global_total_active_nodes']}",
        f"- Active-node reduction vs natural: {data['best_global_active_reduction_percent']}%",
        f"- Natural total vector nodes: {data['natural_total_vector_nodes']}",
        f"- Best global total vector nodes: {data['best_global_total_vector_nodes']}",
        f"- Vector-node reduction vs natural: {data['best_global_vector_reduction_percent']}%",
        f"- Representatives where best order is not natural: {data['representatives_where_best_not_natural']}/20",
        f"- Representatives where `center_out` is worst: {data['representatives_where_center_out_worst']}/20",
        f"- Maximum order-sensitivity ratio: {data['max_order_sensitivity_ratio']}x",
        f"- 25/25 input support preserved under all analyzed orders: `{data['all_orders_keep_25_input_support']}`",
        "",
        "## Order table",
        "",
        "| order | total active | total vector | active range | vector range | support |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in data["summary_by_order"]:
        lines.append(
            f"| `{row['order']}` | {row['total_active_nodes']} | {row['total_vector_nodes']} | "
            f"{row['active_nodes_min']}..{row['active_nodes_max']} | "
            f"{row['vector_nodes_min']}..{row['vector_nodes_max']} | "
            f"{row['active_support_min']}..{row['active_support_max']} / "
            f"{row['vector_support_min']}..{row['vector_support_max']} |"
        )

    lines.extend(
        [
            "",
            "## Per-representative best order",
            "",
            "| family | rule | background | best order | natural active | best active | reduction | worst order | sensitivity |",
            "| --- | ---: | --- | --- | ---: | ---: | ---: | --- | ---: |",
        ]
    )
    for row in data["per_representative"]:
        lines.append(
            f"| `{row['family_id']}` | {row['rule']} | `{row['background']}` | "
            f"`{row['best_order']}` | {row['natural_active_nodes']} | "
            f"{row['best_active_nodes']} | {row['active_reduction_percent']}% | "
            f"`{row['worst_order']}` | {row['order_sensitivity_ratio']}x |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "The ROBDD size is order-sensitive, but the tested improvement is small",
            "globally and does not alter the Fase 42 support result: every analyzed",
            "order still keeps 25/25 inputs in the active-output and full-vector",
            "supports. The `center_out` order is consistently poor, which is useful",
            "negative guidance for future dynamic reordering.",
            "",
            "The next rigorous step, if pursued, is a real dynamic-reordering pass",
            "(SIFT or adjacent-swap search with checkpointing) optimized for BDD",
            "size only. Fase 43 shows that this is a representation-compactness",
            "problem, not an input-elimination problem.",
            "",
        ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_report(analyze())


if __name__ == "__main__":
    main()
