from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "periodic_backgrounds"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase96 = load("test_phase96_module", OUT / "analyze_phase95_fragment_bridges.py")


class Phase96FragmentBridgeTests(unittest.TestCase):
    def test_q8_without_zero_is_connected(self):
        phase96.validate_nonzero_q8_connectivity()

    def test_component_pair_denominator_is_979(self):
        distribution = phase96.EXPECTED_INTERSECTION_COMPONENT_DISTRIBUTION
        observed = sum(count * (size * (size - 1) // 2) for size, count in distribution.items())
        self.assertEqual(observed, 979)

    def test_shortest_path_dp_counts_every_permutation(self):
        levels = [3] * 256
        levels[0] = 0
        levels[255] = 0
        counts = phase96.shortest_path_level_counts(0, 255, levels)
        self.assertEqual(sum(counts.values()), 40320)

    def test_shortest_paths_report_best_and_worst_zero_routes(self):
        levels = [3] * 256
        levels[1] = 0
        levels[2] = 0
        levels[3] = 1
        levels[0] = 4
        profile = phase96.shortest_component_pair_profile([1], [2], levels)
        self.assertEqual(profile["minimum_hamming_distance"], 2)
        self.assertEqual(profile["shortest_path_count"], 2)
        self.assertEqual(profile["shortest_path_count_by_required_level"], {
            "F1_ALL_LONG_PERIOD": 1,
            "F4_FULL_Q8_DIAGNOSTIC": 1,
        })
        self.assertEqual(profile["best_shortest_path_level"], "F1_ALL_LONG_PERIOD")
        self.assertEqual(profile["worst_shortest_path_level"], "F4_FULL_Q8_DIAGNOSTIC")
        self.assertFalse(profile["all_shortest_paths_require_zero_word"])

    def test_earliest_connection_uses_any_path_not_only_shortest(self):
        levels = [3] * 256
        levels[1] = 0
        levels[2] = 0
        levels[3] = 2
        levels[0] = 4
        self.assertEqual(phase96.earliest_connection_level([1], [2], levels), 2)

    def test_f3_ablation_reports_necessary_and_sufficient_category(self):
        nodes = [
            {"category": "SPAN_ESCAPE", "physical_class_sha256": None}
            for _ in range(256)
        ]
        nodes[1] = {"category": phase96.LONG_CATEGORY, "physical_class_sha256": "x"}
        nodes[2] = {"category": phase96.LONG_CATEGORY, "physical_class_sha256": "x"}
        nodes[3] = {"category": "EXTINCT", "physical_class_sha256": None}
        levels = phase96.node_levels(nodes, "x")
        result = phase96.f3_ablation([1], [2], nodes, levels)
        self.assertIn("EXTINCT", result["sufficient_categories"])

    def test_canonical_hash_is_layout_independent(self):
        value = {"z": [2, 1], "a": False}
        self.assertEqual(
            phase96.canonical_sha256(value),
            phase96.canonical_sha256({"a": False, "z": [2, 1]}),
        )


if __name__ == "__main__":
    unittest.main()
