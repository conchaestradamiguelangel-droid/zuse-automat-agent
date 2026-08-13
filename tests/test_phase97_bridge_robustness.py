from __future__ import annotations

import importlib.util
import itertools
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "outputs"
    / "periodic_backgrounds"
    / "analyze_phase96_bridge_robustness.py"
)
spec = importlib.util.spec_from_file_location("test_phase97_module", SCRIPT)
phase97 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = phase97
spec.loader.exec_module(phase97)


def exhaustive_vertex_cut(allowed, component_a, component_b):
    interior = sorted(set(allowed) - set(component_a) - set(component_b))
    for size in range(len(interior) + 1):
        for removed in itertools.combinations(interior, size):
            if not phase97.connected_between(
                set(allowed), component_a, component_b, removed_vertices=removed
            ):
                return size
    raise AssertionError("No vertex cut found")


def exhaustive_edge_cut(allowed, component_a, component_b):
    edges = phase97.q8_edges(set(allowed))
    for size in range(len(edges) + 1):
        for removed in itertools.combinations(edges, size):
            if not phase97.connected_between(
                set(allowed), component_a, component_b, removed_edges=removed
            ):
                return size
    raise AssertionError("No edge cut found")


class Phase97BridgeRobustnessTests(unittest.TestCase):
    def test_q3_connectivity_matches_exhaustive_cuts(self):
        allowed = set(range(8))
        component_a, component_b = [0], [7]
        vertex = phase97.vertex_connectivity_profile(
            allowed, component_a, component_b
        )
        edge = phase97.edge_connectivity_profile(allowed, component_a, component_b)
        self.assertEqual(vertex["kappa_v"], 3)
        self.assertEqual(edge["lambda_e"], 3)
        self.assertEqual(vertex["kappa_v"], exhaustive_vertex_cut(allowed, component_a, component_b))
        self.assertEqual(edge["lambda_e"], exhaustive_edge_cut(allowed, component_a, component_b))

    def test_chain_reports_pair_specific_critical_vertex_and_edges(self):
        allowed = {0, 1, 3}
        critical_v, critical_e = phase97.individually_critical(allowed, [0], [3])
        self.assertEqual(critical_v, [1])
        self.assertEqual(critical_e, [[0, 1], [1, 3]])
        self.assertEqual(
            phase97.vertex_connectivity_profile(allowed, [0], [3])["kappa_v"],
            1,
        )
        self.assertEqual(
            phase97.edge_connectivity_profile(allowed, [0], [3])["lambda_e"],
            1,
        )

    def test_reported_q3_minimum_cuts_disconnect_terminals(self):
        allowed = set(range(8))
        vertex = phase97.vertex_connectivity_profile(allowed, [0], [7])
        edge = phase97.edge_connectivity_profile(allowed, [0], [7])
        self.assertFalse(
            phase97.connected_between(
                allowed, [0], [7], removed_vertices=vertex["minimum_vertex_cut"]
            )
        )
        self.assertFalse(
            phase97.connected_between(
                allowed,
                [0],
                [7],
                removed_edges={tuple(row) for row in edge["minimum_edge_cut"]},
            )
        )

    def test_shortest_path_common_vertex_is_counted_exactly(self):
        profile = phase97.shortest_path_profile({0, 1, 3}, [0], [3])
        self.assertEqual(profile["distance"], 2)
        self.assertEqual(profile["count"], 1)
        self.assertEqual(profile["common_interior_vertices"], [1])

    def test_span_tests_keep_four_claims_separate(self):
        nodes = [
            {
                "category": "EXTINCT",
                "physical_class_sha256": None,
                "strict_initial_state_sha256": str(word),
            }
            for word in range(256)
        ]
        nodes[1]["category"] = phase97.SPAN_CATEGORY
        shortest = phase97.shortest_path_profile({0, 1, 3}, [0], [3])
        tests = phase97.span_escape_tests(
            {0, 1, 3}, [0], [3], nodes, shortest, 1, [1]
        )
        self.assertTrue(tests["category_essential"])
        self.assertTrue(tests["shortest_path_category_mandatory"])
        self.assertTrue(tests["common_span_state_on_all_shortest_paths"])
        self.assertTrue(tests["unique_span_vertex_bottleneck"])

    def test_canonical_hash_is_layout_independent(self):
        self.assertEqual(
            phase97.canonical_sha256({"z": [2, 1], "a": False}),
            phase97.canonical_sha256({"a": False, "z": [2, 1]}),
        )


if __name__ == "__main__":
    unittest.main()
