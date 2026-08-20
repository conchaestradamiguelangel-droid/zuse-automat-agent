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
    / "analyze_phase108_ambient_rescue_geometry.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase109 = load_module("test_phase109_module", SCRIPT)


class Phase109AmbientRescueGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results, cls.sources = phase109.analyze()

    def test_k2_geometry_is_order_invariant_and_excludes_internal_edge(self):
        universe = (0, 1, 2, 4, 8)
        forward = phase109.k2_geometry((0, 1), universe)
        reverse = phase109.k2_geometry((1, 0), universe)
        self.assertEqual(forward, reverse)
        self.assertEqual(forward["endpoint_external_degrees"], [3, 0])
        self.assertEqual(forward["S_ext"], 3)
        self.assertEqual(forward["M_ext"], 0)
        self.assertEqual(forward["B_ext"], 3)

    def test_k2i_roles_are_unique_and_order_invariant(self):
        universe = (0, 1, 2, 4, 8, 12)
        forward = phase109.k2i_geometry((0, 1, 12), universe)
        reverse = phase109.k2i_geometry((12, 1, 0), universe)
        self.assertEqual(forward, reverse)
        self.assertEqual(forward["edge_endpoints"], [0, 1])
        self.assertEqual(forward["isolated_word"], 12)
        self.assertEqual(
            forward["S_ext_all"],
            forward["S_ext_edge"] + forward["d_ext_isolated"],
        )

    def test_certified_universe_reconstruction_is_exact(self):
        audit = self.results["source_audit"]["universe_reconstruction"]
        self.assertEqual(audit["record_count"], 404_054)
        self.assertEqual(audit["stratum_count"], 142)
        self.assertEqual(audit["node_count_mismatches"], 0)
        self.assertEqual(audit["combination_count_mismatches"], 0)

    def test_all_relevant_qubo_universes_cross_check(self):
        audit = self.results["source_audit"]["rescues"]
        self.assertEqual(audit["rescue_count"], 319)
        self.assertEqual(audit["universe_mismatches"], 0)
        self.assertEqual(audit["order_invariance_failures"], 0)
        self.assertEqual(audit["qubo_universe_cross_checked_instance_count"], 151)

    def test_mixed_instance_counts_are_predeclared(self):
        geometry = self.results["rescue_geometry"]
        self.assertEqual(sum(row["motif"] == "K2" for row in geometry), 223)
        self.assertEqual(sum(row["motif"] == "K2+I" for row in geometry), 96)
        self.assertEqual(
            self.results["primary_k2_within_instance"]["mixed_instance_count"], 24
        )
        self.assertEqual(self.results["descriptive_k2i"]["mixed_instance_count"], 4)

    def test_primary_feature_and_equal_instance_weighting_are_fixed(self):
        primary = self.results["primary_k2_within_instance"]
        self.assertEqual(primary["features"]["S_ext"]["role"], "primary")
        self.assertTrue(primary["features"]["S_ext"]["instance_balanced"])
        self.assertEqual(len(primary["per_instance"]), 24)
        self.assertTrue(
            all(row["external_count"] >= 1 and row["internal_count"] >= 1 for row in primary["per_instance"])
        )

    def test_period_is_provenance_only(self):
        secondary = self.results["secondary_between_instance"]
        for motif in ("K2", "K2+I"):
            self.assertEqual(
                secondary[motif]["period_role"], "provenance_only_not_a_covariate"
            )
            for row in secondary[motif]["instances"]:
                self.assertIn("period_provenance_only", row)

    def test_forbidden_explanatory_fields_are_declared(self):
        forbidden = set(
            self.results["source_audit"]["forbidden_explanatory_fields"]
        )
        self.assertEqual(forbidden, phase109.FORBIDDEN_EXPLANATORY_FIELDS)


if __name__ == "__main__":
    unittest.main()
