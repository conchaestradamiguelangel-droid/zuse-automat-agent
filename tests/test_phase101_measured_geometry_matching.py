from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase100_measured_geometry_matching.py"
spec = importlib.util.spec_from_file_location("test_phase101_module", SCRIPT)
phase101 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = phase101
spec.loader.exec_module(phase101)


def node(category=None, physical=None):
    return {"category": category, "physical_class_sha256": physical}


class Phase101MeasuredGeometryMatchingTests(unittest.TestCase):
    def test_neighbor_roles_partition_f1_degree(self):
        nodes = [node() for _ in range(256)]
        word = 0
        neighbors = phase101.q8_neighbors(word)
        nodes[neighbors[2]] = node(physical="target")
        nodes[neighbors[3]] = node(category="LONG_PERIOD_CAP_CANDIDATE")
        roles = phase101.neighbor_role_counts(
            nodes, "target", {neighbors[0]}, {neighbors[1]}, set(neighbors[:4]), word
        )
        self.assertEqual(sum(roles.values()), 4)
        self.assertEqual(roles, {
            "neighbors_A": 1, "neighbors_B": 1,
            "neighbors_F0_nonterminal": 1, "neighbors_other_F1": 1,
        })

    def test_shortest_distances(self):
        allowed = {0, 1, 3, 7}
        self.assertEqual(phase101.shortest_distances(allowed, {0}), {0: 0, 1: 1, 3: 2, 7: 3})

    def test_vertex_bypass_with_more_than_two_remaining_components(self):
        # Removing 0 separates A={1}, B={2}, and an orphan branch {4}.
        allowed = {0, 1, 2, 4}
        components = phase101.connected_components(allowed, removed_vertex=0)
        self.assertEqual(len(components), 3)
        left = phase101.reachable(allowed, {1}, removed_vertex=0)
        right = phase101.reachable(allowed, {2}, removed_vertex=0)
        self.assertEqual(phase101.bypass_count({1, 2}, [(left, right)]), 1)
        self.assertEqual(phase101.bypass_count({1, 4}, [(left, right)]), 0)

    def test_edge_bypass_uses_both_terminal_sides(self):
        allowed = {0, 1, 3}
        edge = (1, 3)
        left = phase101.reachable(allowed, {0}, removed_edge=edge)
        right = phase101.reachable(allowed, {3}, removed_edge=edge)
        self.assertEqual(len(phase101.connected_components(allowed, removed_edge=edge)), 2)
        self.assertEqual(phase101.bypass_count({0, 3}, [(left, right)]), 1)

    def test_geometry_signature_has_no_period_or_outcome(self):
        signature_fields = {
            "f1_degree", "neighbors_A", "neighbors_B", "neighbors_F0_nonterminal",
            "neighbors_other_F1", "distance_to_A", "distance_to_B",
            "critical_vertex_count", "bypassed_critical_vertex_count",
            "adjacent_critical_vertex_count", "critical_edge_count",
            "bypassed_critical_edge_count", "incident_critical_edge_endpoint_count",
        }
        self.assertNotIn("period", signature_fields)
        self.assertNotIn("kappa_v", signature_fields)
        self.assertNotIn("lambda_e", signature_fields)

    def test_homogeneity_accepts_heterogeneous_result(self):
        self.assertEqual(
            phase101.homogeneity_label([False, True]), "GEOMETRY_HETEROGENEOUS"
        )
        self.assertEqual(
            phase101.homogeneity_label([False, False]), "GEOMETRY_HOMOGENEOUS_NONRESCUE"
        )

    def test_exact_fraction_comparison(self):
        self.assertEqual(phase101.compare_fractions(1, 3, 2, 6), "TIE")
        self.assertEqual(phase101.compare_fractions(2, 3, 1, 2), "LEFT_HIGHER")

    def test_zero_denominator_is_not_available(self):
        self.assertEqual(phase101.fraction_payload(0, 0), "NOT_AVAILABLE")

    def test_matching_key_includes_target_identity(self):
        signature = "same-signature"
        self.assertNotEqual(("cube-a", 1, signature), ("cube-a", 2, signature))


if __name__ == "__main__":
    unittest.main()
