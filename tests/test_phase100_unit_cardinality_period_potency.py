from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "outputs"
    / "periodic_backgrounds"
    / "analyze_phase99_unit_cardinality_period_potency.py"
)
spec = importlib.util.spec_from_file_location("test_phase100_module", SCRIPT)
phase100 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = phase100
spec.loader.exec_module(phase100)


class Phase100UnitCardinalityPeriodPotencyTests(unittest.TestCase):
    def test_single_node_explains_group_rescue(self):
        self.assertEqual(
            phase100.classify_group_relation(2, 1),
            "SINGLE_NODE_EXPLAINS_GROUP_RESCUE",
        )

    def test_collective_only_group_rescue(self):
        self.assertEqual(
            phase100.classify_group_relation(2, 0),
            "COLLECTIVE_ONLY_PERIOD_RESCUE",
        )

    def test_nonrescuing_period_control(self):
        self.assertEqual(
            phase100.classify_group_relation(1, 0),
            "NONRESCUING_PERIOD_CONTROL",
        )

    def test_monotonicity_contradiction_is_explicit(self):
        self.assertEqual(
            phase100.classify_group_relation(1, 1),
            "MONOTONICITY_CONTRADICTION",
        )

    def test_fraction_comparison_uses_exact_cross_products(self):
        self.assertEqual(phase100.compare_fractions(1, 3, 2, 6), "TIE")
        self.assertEqual(phase100.compare_fractions(2, 5, 1, 3), "LEFT_HIGHER")
        self.assertEqual(phase100.compare_fractions(1, 4, 1, 3), "RIGHT_HIGHER")

    def test_macro_mean_does_not_micro_weight_large_strata(self):
        result = phase100.mean_fraction_payload([(1, 1), (0, 100)])
        self.assertEqual(result["numerator"], 1)
        self.assertEqual(result["denominator"], 2)
        self.assertEqual(result["stratum_count"], 2)

    def test_vertex_and_edge_relations_can_differ(self):
        vertex = phase100.classify_group_relation(2, 1)
        edge = phase100.classify_group_relation(2, 0)
        self.assertNotEqual(vertex, edge)

    def test_absent_period_has_no_synthetic_fraction(self):
        with self.assertRaises(ValueError):
            phase100.mean_fraction_payload([])


if __name__ == "__main__":
    unittest.main()
