#!/usr/bin/env python3
"""Fase 42: ROBDD audit of the dense T=15 causal cone.

Fase 41 showed that the 25-cell, 12-step cone has no sparse local-table or
input-support shortcut. Fase 42 constructs reduced ordered binary decision
diagrams (ROBDDs) for the cone's Boolean circuit and asks whether canonical
Boolean reduction finds hidden simplification.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from functools import lru_cache
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
BASE_SCRIPT = OUT_DIR.parent / "periodic_backgrounds" / "sweep_periodic_background_oscillators.py"
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
EMBEDDING_RESULTS = OUT_DIR / "defect_embedding_descriptor_results.json"
RESULTS_JSON = OUT_DIR / "cone_bdd_results.json"
REPORT_MD = OUT_DIR / "cone_bdd_report.md"

T_WINDOW = 12
WINDOW_CELLS = 25
SAMPLE_START = 81
BACKGROUND_PERIOD = 3
ORDERS = {
    "natural": list(range(WINDOW_CELLS)),
}


def load_base_module():
    spec = importlib.util.spec_from_file_location("periodic_background_base", BASE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import base detector from {BASE_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def bit_from_state(active: set[int], pos: int, width: int) -> int:
    return 1 if (pos % width) in active else 0


def ic_start(width: int, ic: str) -> int:
    return width // 2 - len(ic) // 2


def initial_actual_bit(base, bg_set: set[int], global_pos: int, ic: str) -> int:
    start = ic_start(base.WIDTH, ic)
    if start <= global_pos <= start + len(ic) - 1:
        idx = global_pos - start
        return int(ic[idx])
    return bit_from_state(bg_set, global_pos, base.WIDTH)


def rule_output(rule: int, left: int, center: int, right: int) -> int:
    idx = (left << 2) | (center << 1) | right
    return (rule >> idx) & 1


def canonical_defect(width: int, diff: tuple[int, ...]) -> dict | None:
    if not diff:
        return None
    positions = sorted(diff)
    gaps = []
    for index, position in enumerate(positions):
        next_position = positions[(index + 1) % len(positions)]
        if index == len(positions) - 1:
            next_position += width
        gaps.append((next_position - position, index))
    _largest_gap, cut_index = max(gaps)
    anchor = positions[(cut_index + 1) % len(positions)]
    offsets = tuple(sorted((position - anchor) % width for position in positions))
    active_width = max(offsets) + 1
    value = sum(1 << offset for offset in offsets)
    hex_digits = max(1, (active_width + 3) // 4)
    return {
        "anchor": anchor,
        "offsets": offsets,
        "width": active_width,
        "hex": f"{active_width}:{value:0{hex_digits}x}",
    }


def load_family_lookup() -> dict[tuple[int, str], str]:
    embedding = json.loads(EMBEDDING_RESULTS.read_text(encoding="utf-8"))
    return {
        (int(row["rule"]), row["background"]): row["family_id"]
        for row in embedding["rows"]
    }


class BDDManager:
    ZERO = 0
    ONE = 1

    def __init__(self, order: list[int]):
        self.order = order
        self.level = {var: idx for idx, var in enumerate(order)}
        self.nodes: list[tuple[int, int, int] | None] = [None, None]
        self.unique: dict[tuple[int, int, int], int] = {}
        self.var_nodes = {var: self.mk(var, self.ZERO, self.ONE) for var in order}

    def mk(self, var: int, low: int, high: int) -> int:
        if low == high:
            return low
        key = (var, low, high)
        found = self.unique.get(key)
        if found is not None:
            return found
        node_id = len(self.nodes)
        self.nodes.append(key)
        self.unique[key] = node_id
        return node_id

    def var(self, var: int) -> int:
        return self.var_nodes[var]

    def const(self, value: int) -> int:
        return self.ONE if value else self.ZERO

    def top_var(self, node: int) -> int | None:
        if node in (self.ZERO, self.ONE):
            return None
        return self.nodes[node][0]  # type: ignore[index]

    def cofactor(self, node: int, var: int) -> tuple[int, int]:
        if node in (self.ZERO, self.ONE):
            return node, node
        node_var, low, high = self.nodes[node]  # type: ignore[misc]
        if node_var == var:
            return low, high
        return node, node

    @lru_cache(maxsize=None)
    def bnot(self, node: int) -> int:
        if node == self.ZERO:
            return self.ONE
        if node == self.ONE:
            return self.ZERO
        var, low, high = self.nodes[node]  # type: ignore[misc]
        return self.mk(var, self.bnot(low), self.bnot(high))

    def band(self, left: int, right: int) -> int:
        return self.apply("and", left, right)

    def bor(self, left: int, right: int) -> int:
        return self.apply("or", left, right)

    def bxor(self, left: int, right: int) -> int:
        return self.apply("xor", left, right)

    @lru_cache(maxsize=None)
    def apply(self, op: str, left: int, right: int) -> int:
        if op == "and":
            if left == self.ZERO or right == self.ZERO:
                return self.ZERO
            if left == self.ONE:
                return right
            if right == self.ONE:
                return left
            if left == right:
                return left
        elif op == "or":
            if left == self.ONE or right == self.ONE:
                return self.ONE
            if left == self.ZERO:
                return right
            if right == self.ZERO:
                return left
            if left == right:
                return left
        elif op == "xor":
            if left == self.ZERO:
                return right
            if right == self.ZERO:
                return left
            if left == self.ONE:
                return self.bnot(right)
            if right == self.ONE:
                return self.bnot(left)
            if left == right:
                return self.ZERO
        else:
            raise ValueError(op)

        lvar = self.top_var(left)
        rvar = self.top_var(right)
        if lvar is None:
            top = rvar
        elif rvar is None:
            top = lvar
        else:
            top = lvar if self.level[lvar] <= self.level[rvar] else rvar
        assert top is not None
        l_low, l_high = self.cofactor(left, top)
        r_low, r_high = self.cofactor(right, top)
        return self.mk(top, self.apply(op, l_low, r_low), self.apply(op, l_high, r_high))

    def ite_var(self, var_node: int, high: int, low: int) -> int:
        return self.bor(self.band(var_node, high), self.band(self.bnot(var_node), low))

    def eca_output(self, rule: int, left: int, center: int, right: int) -> int:
        # Shannon expansion over the local neighborhood. This is much smaller
        # than materializing a DNF with up to eight minterms.
        def bit(idx: int) -> int:
            return self.const((rule >> idx) & 1)

        c0 = self.ite_var(right, bit(1), bit(0))
        c1 = self.ite_var(right, bit(3), bit(2))
        l0 = self.ite_var(center, c1, c0)

        c2 = self.ite_var(right, bit(5), bit(4))
        c3 = self.ite_var(right, bit(7), bit(6))
        l1 = self.ite_var(center, c3, c2)

        return self.ite_var(left, l1, l0)

    def reachable_nodes(self, roots: list[int]) -> set[int]:
        seen: set[int] = set()
        stack = list(roots)
        while stack:
            node = stack.pop()
            if node in (self.ZERO, self.ONE) or node in seen:
                continue
            seen.add(node)
            _var, low, high = self.nodes[node]  # type: ignore[misc]
            stack.append(low)
            stack.append(high)
        return seen

    def support(self, root: int) -> set[int]:
        return {self.nodes[node][0] for node in self.reachable_nodes([root])}  # type: ignore[index]

    def eval(self, root: int, assignment: dict[int, int]) -> int:
        node = root
        while node not in (self.ZERO, self.ONE):
            var, low, high = self.nodes[node]  # type: ignore[misc]
            node = high if assignment[var] else low
        return int(node == self.ONE)


def build_representative_bdds(base, rule: int, background: str, ic: str, order: list[int]) -> dict:
    manager = BDDManager(order)
    width = base.WIDTH
    bg_frames = background_orbit(base, rule, background, T_WINDOW)
    start = ic_start(width, ic)
    center = start + (len(ic) - 1) // 2
    left = center - T_WINDOW
    positions = list(range(left, left + WINDOW_CELLS))

    rows: list[list[int]] = [[manager.var(i) for i in range(WINDOW_CELLS)]]
    for t in range(T_WINDOW):
        bg_now = set(bg_frames[t])
        next_row = []
        for idx, global_pos in enumerate(positions):
            parents = []
            for delta in (-1, 0, 1):
                local = idx + delta
                if 0 <= local < WINDOW_CELLS:
                    parents.append(rows[-1][local])
                else:
                    parents.append(manager.const(bit_from_state(bg_now, global_pos + delta, width)))
            next_row.append(manager.eca_output(rule, parents[0], parents[1], parents[2]))
        rows.append(next_row)

    bg_final = set(bg_frames[T_WINDOW])
    diff_roots = [
        manager.bxor(node, manager.const(bit_from_state(bg_final, global_pos, width)))
        for node, global_pos in zip(rows[-1], positions)
    ]

    bg0 = set(bg_frames[0])
    concrete_assignment = {
        idx: initial_actual_bit(base, bg0, global_pos, ic)
        for idx, global_pos in enumerate(positions)
    }
    concrete_diff = [manager.eval(root, concrete_assignment) for root in diff_roots]
    concrete_positions = [
        global_pos % width
        for global_pos, bit in zip(positions, concrete_diff)
        if bit
    ]
    canonical = canonical_defect(width, tuple(sorted(concrete_positions)))
    return {
        "manager": manager,
        "diff_roots": diff_roots,
        "concrete_diff": concrete_diff,
        "canonical": canonical,
    }


def analyze() -> dict:
    base = load_base_module()
    family_lookup = load_family_lookup()
    rows = []
    for record in load_jsonl(LOCKING_RESULTS):
        rule = int(record["rule"])
        background = record["background"]
        ic = record["ic"]
        stable_states = list(record["defect_states"])
        for order_name, order in ORDERS.items():
            built = build_representative_bdds(base, rule, background, ic, order)
            manager: BDDManager = built["manager"]
            roots: list[int] = built["diff_roots"]
            vector_nodes = manager.reachable_nodes(roots)
            supports = [manager.support(root) for root in roots]
            active_indices = [idx for idx, bit in enumerate(built["concrete_diff"]) if bit]
            active_roots = [roots[idx] for idx in active_indices]
            active_nodes = manager.reachable_nodes(active_roots)
            active_support = set().union(*(supports[idx] for idx in active_indices)) if active_indices else set()
            row = {
                "rule": rule,
                "background": background,
                "family_id": family_lookup[(rule, background)],
                "ic": ic,
                "order": order_name,
                "canonical_t12": built["canonical"]["hex"] if built["canonical"] else None,
                "matches_stable_state": built["canonical"]["hex"] in stable_states if built["canonical"] else False,
                "total_bdd_nodes_allocated": len(manager.nodes) - 2,
                "vector_reachable_nodes": len(vector_nodes),
                "active_reachable_nodes": len(active_nodes),
                "vector_support_size": len(set().union(*supports)),
                "active_support_size": len(active_support),
                "per_output_node_count_min": min(len(manager.reachable_nodes([root])) for root in roots),
                "per_output_node_count_max": max(len(manager.reachable_nodes([root])) for root in roots),
                "per_output_support_min": min(len(support) for support in supports),
                "per_output_support_max": max(len(support) for support in supports),
                "nonconstant_outputs": sum(root not in (manager.ZERO, manager.ONE) for root in roots),
                "active_output_count": len(active_indices),
            }
            rows.append(row)

    grouped: dict[tuple[int, str], list[dict]] = {}
    for row in rows:
        if row["order"] == "natural":
            grouped[(row["rule"], row["background"])] = []
    for row in rows:
        grouped.setdefault((row["rule"], row["background"]), []).append(row)

    best_by_rep = []
    for items in grouped.values():
        best = min(items, key=lambda item: item["active_reachable_nodes"])
        best_by_rep.append(best)

    active_nodes = [row["active_reachable_nodes"] for row in rows]
    vector_nodes = [row["vector_reachable_nodes"] for row in rows]
    active_supports = [row["active_support_size"] for row in rows]
    vector_supports = [row["vector_support_size"] for row in rows]
    all_active_need_all_inputs = all(size == WINDOW_CELLS for size in active_supports)
    all_vector_need_all_inputs = all(size == WINDOW_CELLS for size in vector_supports)
    status = "BDD_NO_INPUT_REDUCTION"
    if not all_active_need_all_inputs:
        status = "BDD_INPUT_REDUCTION_FOUND"

    summary_by_order = []
    for order_name in ORDERS:
        subset = [row for row in rows if row["order"] == order_name]
        summary_by_order.append(
            {
                "order": order_name,
                "active_nodes_min": min(row["active_reachable_nodes"] for row in subset),
                "active_nodes_max": max(row["active_reachable_nodes"] for row in subset),
                "vector_nodes_min": min(row["vector_reachable_nodes"] for row in subset),
                "vector_nodes_max": max(row["vector_reachable_nodes"] for row in subset),
                "active_support_min": min(row["active_support_size"] for row in subset),
                "active_support_max": max(row["active_support_size"] for row in subset),
                "vector_support_min": min(row["vector_support_size"] for row in subset),
                "vector_support_max": max(row["vector_support_size"] for row in subset),
            }
        )

    return {
        "status": status,
        "record_count": 20,
        "orders": list(ORDERS),
        "all_active_outputs_need_all_25_inputs": all_active_need_all_inputs,
        "all_vector_outputs_need_all_25_inputs": all_vector_need_all_inputs,
        "active_reachable_node_range_all_orders": [min(active_nodes), max(active_nodes)],
        "vector_reachable_node_range_all_orders": [min(vector_nodes), max(vector_nodes)],
        "best_active_reachable_node_range_by_rep": [
            min(row["active_reachable_nodes"] for row in best_by_rep),
            max(row["active_reachable_nodes"] for row in best_by_rep),
        ],
        "summary_by_order": summary_by_order,
        "rows": rows,
    }


def write_report(data: dict) -> None:
    lines = [
        "# Fase 42: ROBDD Audit of the T=15 Cone Circuit",
        "",
        "## Question",
        "",
        "Fase 41 found no sparse table or input-support shortcut inside the",
        "25-cell, 12-step cone. Fase 42 constructs reduced ordered binary decision",
        "diagrams (ROBDDs) for the same cone circuit and tests whether canonical",
        "Boolean reduction finds hidden simplification.",
        "",
        "Variable order tested: `natural` (left-to-right cone order). BDD size",
        "is order-dependent, but input support is a semantic property: if a",
        "reduced BDD contains all 25 variables, no input variable is irrelevant",
        "for that represented Boolean function.",
        "",
        "## Summary by variable order",
        "",
        "| order | active nodes | vector nodes | active support | vector support |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for row in data["summary_by_order"]:
        lines.append(
            f"| `{row['order']}` | {row['active_nodes_min']}..{row['active_nodes_max']} | "
            f"{row['vector_nodes_min']}..{row['vector_nodes_max']} | "
            f"{row['active_support_min']}..{row['active_support_max']} | "
            f"{row['vector_support_min']}..{row['vector_support_max']} |"
        )

    lines.extend(
        [
            "",
            "## Representative table",
            "",
            "| family | rule | background | order | active nodes | vector nodes | active support | vector support | nonconstant outputs |",
            "| --- | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |",
        ]
    )
    for row in data["rows"]:
        if row["order"] != "natural":
            continue
        lines.append(
            f"| `{row['family_id']}` | {row['rule']} | `{row['background']}` | `{row['order']}` | "
            f"{row['active_reachable_nodes']} | {row['vector_reachable_nodes']} | "
            f"{row['active_support_size']} | {row['vector_support_size']} | {row['nonconstant_outputs']} |"
        )

    lines.extend(
        [
            "",
            "## Verdict",
            "",
            f"**Status:** `{data['status']}`.",
            "",
        ]
    )
    if data["status"] == "BDD_NO_INPUT_REDUCTION":
        lines.extend(
            [
                "ROBDD reduction confirms the Fase 41 input-support result: the",
                "active localized outputs still depend on all 25 cone inputs.",
                "The natural-order ROBDDs contain all 25 support variables for",
                "every representative, certifying that no input variable is",
                "irrelevant to the represented active-output functions. This does",
                "not prove global minimum BDD size over all 25! orders, but it",
                "does rule out Boolean input elimination.",
            ]
        )
    else:
        lines.extend(
            [
                "At least one tested ROBDD order exposes input reduction. This would",
                "identify a smaller symbolic target than the Fase 41 cone.",
            ]
        )
    lines.append("")
    RESULTS_JSON.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    write_report(analyze())


if __name__ == "__main__":
    main()
