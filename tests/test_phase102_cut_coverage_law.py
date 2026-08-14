from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase101_cut_coverage_law.py"
spec = importlib.util.spec_from_file_location("test_phase102_module", SCRIPT)
phase102 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = phase102
spec.loader.exec_module(phase102)


def adjacency(edges):
    nodes = {node for edge in edges for node in edge}
    graph = {node: set() for node in nodes}
    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
    return graph


class Phase102CutCoverageLawTests(unittest.TestCase):
    def test_q8_neighbors_are_eight_hamming_one_words(self):
        neighbors = phase102.q8_neighbors(0b10101010)
        self.assertEqual(len(set(neighbors)), 8)
        self.assertTrue(all((0b10101010 ^ word).bit_count() == 1 for word in neighbors))

    def test_enumerates_multiple_vertex_and_edge_cuts(self):
        graph = adjacency([(0, 1), (1, 2), (2, 3)])
        vertices, edges = phase102.enumerate_terminal_cuts(graph, {0}, {3})
        self.assertEqual(vertices, (1, 2))
        self.assertEqual(edges, ((0, 1), (1, 2), (2, 3)))

    def test_removed_vertex_can_leave_more_than_two_components(self):
        graph = adjacency([(0, 1), (0, 2), (0, 4)])
        self.assertFalse(phase102.terminals_connected(graph, {1}, {2}, removed_vertex=0))
        left = phase102.reachable(graph, {1}, removed_vertex=0)
        right = phase102.reachable(graph, {2}, removed_vertex=0)
        orphan = phase102.reachable(graph, {4}, removed_vertex=0)
        self.assertEqual((left, right, orphan), ({1}, {2}, {4}))

    def test_complete_and_partial_cut_coverage(self):
        partitions = [({0, 1}, {2, 3}), ({0}, {1, 2, 3})]
        self.assertEqual(phase102.bypass_count({0, 2}, partitions), 2)
        self.assertEqual(phase102.bypass_count({1, 2}, partitions), 1)

    def test_edge_only_rescue_is_possible(self):
        # The only bridge is 0-1. Vertex 3 remains an articulation after the
        # new node bypasses that bridge, so lambda is rescued but kappa is not.
        base = adjacency(
            [(0, 1), (1, 2), (2, 3), (3, 1), (3, 5), (3, 6), (5, 6)]
        )
        vertices, edges = phase102.enumerate_terminal_cuts(base, {0}, {5, 6})
        self.assertIn(3, vertices)
        self.assertEqual(edges, ((0, 1),))
        augmented = {node: set(neighbors) for node, neighbors in base.items()}
        augmented[7] = {0, 2}
        augmented[0].add(7)
        augmented[2].add(7)
        vertex_rescue, edge_rescue, _, _ = phase102.direct_unit_rescue(
            augmented, {0}, {5, 6}
        )
        self.assertFalse(vertex_rescue)
        self.assertTrue(edge_rescue)

    def test_vertex_rescue_implies_edge_rescue_in_cycle(self):
        graph = adjacency([(0, 1), (1, 3), (3, 2), (2, 0)])
        vertex_rescue, edge_rescue, _, _ = phase102.direct_unit_rescue(graph, {0}, {3})
        self.assertTrue(vertex_rescue)
        self.assertTrue(edge_rescue)

    def test_missing_or_extra_cut_is_detectable(self):
        graph = adjacency([(0, 1), (1, 2)])
        vertices, edges = phase102.enumerate_terminal_cuts(graph, {0}, {2})
        self.assertNotEqual(vertices, ())
        self.assertNotEqual(edges, ((0, 1),))

    def test_removing_added_node_recovers_base(self):
        base = phase102.build_q8_adjacency({0, 1, 3})
        augmented, _ = phase102.add_unit_node(base, 2)
        recovered = {
            node: {target for target in targets if target != 2}
            for node, targets in augmented.items()
            if node != 2
        }
        self.assertEqual(recovered, base)

    def test_injected_counterexample_rejects_law(self):
        row = {
            "vertex_predicted": True,
            "vertex_direct": False,
            "edge_predicted": True,
            "edge_direct": True,
            "law_match": False,
        }
        self.assertEqual(
            phase102.law_verdict([row]), "CUT_COVERAGE_RESCUE_LAW_REJECTED"
        )

    def test_numeric_connectivity_flag_uses_boolean_threshold(self):
        self.assertTrue(phase102.connectivity_rescued(2))
        self.assertTrue(phase102.connectivity_rescued(3))
        self.assertFalse(phase102.connectivity_rescued(1))


if __name__ == "__main__":
    unittest.main()
