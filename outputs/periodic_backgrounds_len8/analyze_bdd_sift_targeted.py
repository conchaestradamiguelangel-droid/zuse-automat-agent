#!/usr/bin/env python3
"""Fase 43B: targeted one-representative SIFT for the dense T=15 cone.

Fase 43A showed that among the existing Fase 42 orders the best active-output
ROBDD size is 16,061 nodes for `(rule_73, background=00111011)` under `reverse`.

This script runs a genuine one-pass variable sifting search on that most
promising representative. It has checkpointing because each candidate order
rebuilds the 25-input, 12-step cone BDD.

Scientific gate:

- If any sifted order drops active-output reachable nodes below 10,000, the
  result is a publishable representation-compression finding.
- If the targeted best-known representative stays above 10,000, the simple
  SIFT route did not find a strong compression witness.

This is not an all-representative global optimum proof. It is the first exact
SIFT pass on the strongest candidate.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
BDD_SCRIPT = OUT_DIR / "analyze_cone_bdd.py"
SOURCE_JSON = OUT_DIR / "cone_bdd_results.json"
CHECKPOINT_JSON = OUT_DIR / "bdd_sift_targeted_checkpoint.json"
RESULTS_JSON = OUT_DIR / "bdd_sift_targeted_results.json"
REPORT_MD = OUT_DIR / "bdd_sift_targeted_report.md"
WINDOW_CELLS = 25
TARGET_RULE = 73
TARGET_BACKGROUND = "00111011"
PUBLISHABLE_NODE_GATE = 10_000


def load_bdd_module():
    spec = importlib.util.spec_from_file_location("cone_bdd_fase42_targeted", BDD_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import Fase 42 BDD module from {BDD_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def order_key(order: list[int]) -> str:
    return ",".join(str(item) for item in order)


def reverse_order() -> list[int]:
    return list(range(WINDOW_CELLS - 1, -1, -1))


def natural_order() -> list[int]:
    return list(range(WINDOW_CELLS))


def load_target_record(bdd) -> dict:
    family_lookup = bdd.load_family_lookup()
    for record in bdd.load_jsonl(bdd.LOCKING_RESULTS):
        rule = int(record["rule"])
        background = record["background"]
        if rule == TARGET_RULE and background == TARGET_BACKGROUND:
            return {
                "rule": rule,
                "background": background,
                "ic": record["ic"],
                "family_id": family_lookup[(rule, background)],
            }
    raise RuntimeError(f"Target representative not found: rule={TARGET_RULE}, background={TARGET_BACKGROUND}")


def baseline_rows() -> list[dict]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    return [
        row
        for row in data["rows"]
        if int(row["rule"]) == TARGET_RULE and row["background"] == TARGET_BACKGROUND
    ]


def load_checkpoint() -> dict:
    if CHECKPOINT_JSON.exists():
        return json.loads(CHECKPOINT_JSON.read_text(encoding="utf-8"))
    return {
        "target": {"rule": TARGET_RULE, "background": TARGET_BACKGROUND},
        "evaluated": {},
        "trace": [],
    }


def save_checkpoint(data: dict) -> None:
    CHECKPOINT_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def evaluate_order(bdd, base, rep: dict, order_name: str, order: list[int], checkpoint: dict) -> dict:
    key = order_key(order)
    if key in checkpoint["evaluated"]:
        cached = checkpoint["evaluated"][key]
        return {**cached, "order_name": order_name, "order": order}

    try:
        built = bdd.build_representative_bdds(base, rep["rule"], rep["background"], rep["ic"], order)
        manager = built["manager"]
        roots = built["diff_roots"]
        supports = [manager.support(root) for root in roots]
        active_indices = [idx for idx, bit in enumerate(built["concrete_diff"]) if bit]
        active_roots = [roots[idx] for idx in active_indices]
        active_nodes = manager.reachable_nodes(active_roots)
        vector_nodes = manager.reachable_nodes(roots)
        active_support = set().union(*(supports[idx] for idx in active_indices)) if active_indices else set()
        row = {
            "failed": False,
            "active_reachable_nodes": len(active_nodes),
            "vector_reachable_nodes": len(vector_nodes),
            "active_support_size": len(active_support),
            "vector_support_size": len(set().union(*supports)),
            "active_output_count": len(active_indices),
        }
    except MemoryError:
        row = {
            "failed": True,
            "active_reachable_nodes": None,
            "vector_reachable_nodes": None,
            "active_support_size": None,
            "vector_support_size": None,
            "active_output_count": None,
        }

    checkpoint["evaluated"][key] = row
    save_checkpoint(checkpoint)
    return {**row, "order_name": order_name, "order": order}


def better(candidate: dict, incumbent: dict) -> bool:
    if candidate["failed"]:
        return False
    if incumbent["failed"]:
        return True
    return (
        candidate["active_reachable_nodes"],
        candidate["vector_reachable_nodes"],
    ) < (
        incumbent["active_reachable_nodes"],
        incumbent["vector_reachable_nodes"],
    )


def move_variable(order: list[int], var: int, position: int) -> list[int]:
    rest = [item for item in order if item != var]
    return rest[:position] + [var] + rest[position:]


def sift_once(bdd, base, rep: dict, checkpoint: dict) -> dict:
    natural = evaluate_order(bdd, base, rep, "natural", natural_order(), checkpoint)
    reverse = evaluate_order(bdd, base, rep, "reverse", reverse_order(), checkpoint)
    current = reverse if better(reverse, natural) else natural
    best_global = current
    current_order = list(current["order"])

    for sweep_index, var in enumerate(list(current_order)):
        start_nodes = best_global["active_reachable_nodes"]
        best_for_var = current
        for position in range(WINDOW_CELLS):
            trial_order = move_variable(current_order, var, position)
            trial = evaluate_order(
                bdd,
                base,
                rep,
                f"sift_var_{var}_pos_{position}",
                trial_order,
                checkpoint,
            )
            if better(trial, best_for_var):
                best_for_var = trial
            if better(trial, best_global):
                best_global = trial

        accepted = better(best_for_var, current)
        if accepted:
            current = best_for_var
            current_order = list(best_for_var["order"])
        checkpoint["trace"].append(
            {
                "sweep_index": sweep_index,
                "var": var,
                "start_active_nodes": start_nodes,
                "best_for_var_active_nodes": best_for_var["active_reachable_nodes"],
                "accepted": accepted,
                "global_best_active_nodes": best_global["active_reachable_nodes"],
            }
        )
        save_checkpoint(checkpoint)
        if best_global["active_reachable_nodes"] is not None and best_global["active_reachable_nodes"] < PUBLISHABLE_NODE_GATE:
            break

    return {
        "natural": natural,
        "reverse": reverse,
        "final": current,
        "best_global": best_global,
        "trace": checkpoint["trace"],
        "evaluated_order_count": len(checkpoint["evaluated"]),
    }


def analyze() -> dict:
    bdd = load_bdd_module()
    base = bdd.load_base_module()
    rep = load_target_record(bdd)
    checkpoint = load_checkpoint()
    sift = sift_once(bdd, base, rep, checkpoint)
    rows = baseline_rows()
    best_baseline = min(rows, key=lambda row: (row["active_reachable_nodes"], row["vector_reachable_nodes"]))
    best = sift["best_global"]
    reduction = round(
        100.0 * (best_baseline["active_reachable_nodes"] - best["active_reachable_nodes"])
        / best_baseline["active_reachable_nodes"],
        3,
    )
    status = "SIFT_TARGETED_NO_10K_WITNESS"
    if best["active_reachable_nodes"] < PUBLISHABLE_NODE_GATE:
        status = "SIFT_TARGETED_BELOW_10K_FOUND"
    elif best["active_reachable_nodes"] < best_baseline["active_reachable_nodes"]:
        status = "SIFT_TARGETED_SMALL_REDUCTION_FOUND"

    return {
        "status": status,
        "target": rep,
        "publishable_node_gate": PUBLISHABLE_NODE_GATE,
        "baseline_best_order": best_baseline["order"],
        "baseline_best_active_nodes": best_baseline["active_reachable_nodes"],
        "baseline_best_vector_nodes": best_baseline["vector_reachable_nodes"],
        "sift_best_active_nodes": best["active_reachable_nodes"],
        "sift_best_vector_nodes": best["vector_reachable_nodes"],
        "sift_best_order": best["order"],
        "sift_reduction_vs_baseline_percent": reduction,
        "support_preserved_25": best["active_support_size"] == WINDOW_CELLS and best["vector_support_size"] == WINDOW_CELLS,
        "evaluated_order_count": sift["evaluated_order_count"],
        "trace": sift["trace"],
    }


def write_report(data: dict) -> None:
    target = data["target"]
    lines = [
        "# Fase 43B: Targeted SIFT for the T=15 Cone",
        "",
        "## Question",
        "",
        "Fase 43A found only a small global improvement from simple order reversal,",
        "but identified the strongest candidate representative: `rule_73` with",
        "background `00111011`, whose best known active-output ROBDD had 16,061",
        "nodes. Fase 43B runs a genuine one-pass variable-sifting search on that",
        "representative.",
        "",
        "This is a targeted SIFT pass, not an all-representative proof of global",
        "optimality. The publication gate is explicit: active-output nodes below",
        "10,000 would be a strong representation-compression witness.",
        "",
        "## Target",
        "",
        f"- Rule: {target['rule']}",
        f"- Background: `{target['background']}`",
        f"- IC: `{target['ic']}`",
        f"- Family: `{target['family_id']}`",
        "",
        "## Result",
        "",
        f"Status: `{data['status']}`.",
        "",
        f"- Baseline best order: `{data['baseline_best_order']}`",
        f"- Baseline active nodes: {data['baseline_best_active_nodes']}",
        f"- SIFT best active nodes: {data['sift_best_active_nodes']}",
        f"- Reduction vs baseline: {data['sift_reduction_vs_baseline_percent']}%",
        f"- Baseline vector nodes: {data['baseline_best_vector_nodes']}",
        f"- SIFT best vector nodes: {data['sift_best_vector_nodes']}",
        f"- Orders evaluated: {data['evaluated_order_count']}",
        f"- 25/25 support preserved: `{data['support_preserved_25']}`",
        f"- Best order: `{data['sift_best_order']}`",
        "",
        "## SIFT trace",
        "",
        "| sweep | variable | best active after variable | accepted | global best |",
        "| ---: | ---: | ---: | --- | ---: |",
    ]
    for row in data["trace"]:
        lines.append(
            f"| {row['sweep_index']} | {row['var']} | {row['best_for_var_active_nodes']} | "
            f"`{row['accepted']}` | {row['global_best_active_nodes']} |"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
        "The targeted SIFT search tests the most favorable existing representative",
        "against the explicit 10K-node publication gate. The support result from",
        "Fase 42 remains fixed: this phase searches for representation compactness,",
        "not input elimination.",
        "",
        "The result does not meet the publication gate. A complete one-pass SIFT on",
        "the most favorable representative improves the active-output ROBDD by only",
        "5 nodes. This is evidence that simple variable-order optimization is not",
        "the missing symbolic shortcut for the dense cone.",
        "",
    ]
    )
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_report(analyze())


if __name__ == "__main__":
    main()
