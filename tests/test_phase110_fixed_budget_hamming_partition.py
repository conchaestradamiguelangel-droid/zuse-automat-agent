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
    / "analyze_phase109_fixed_budget_hamming_partition.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase110 = load_module("test_phase110_module", SCRIPT)


class Phase110FixedBudgetHammingPartitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results, cls.sources = phase110.analyze()

    def test_node_level_rule_matches_frozen_phase96_logic(self):
        nodes = [
            {"word8": f"{word:08b}", "physical_class_sha256": None, "category": phase110.ZERO_CATEGORY}
            for word in range(256)
        ]
        nodes[0]["physical_class_sha256"] = "physical"
        nodes[1]["category"] = phase110.LONG_CATEGORY
        nodes[2]["category"] = "STATIC_T1"
        nodes[3]["category"] = "SPAN_ESCAPE"
        levels = phase110.node_levels(nodes, "physical")
        self.assertEqual(levels[:5], [0, 1, 2, 3, 4])
        self.assertEqual(phase110.allowed_words(levels, 2), {0, 1, 2})

    def test_bridge_incidence_is_order_invariant(self):
        gmin = {2, 4, 8, 16}
        self.assertEqual(
            phase110.bridge_incidence((0, 1), gmin),
            phase110.bridge_incidence((1, 0), gmin),
        )
        self.assertEqual(phase110.bridge_incidence((0, 1), gmin), 4)

    def test_all_certified_sources_and_reconstructions_pass(self):
        audit = self.results["source_audit"]
        self.assertEqual(audit["gmin"]["pair_count"], 979)
        self.assertEqual(audit["gmin"]["allowed_node_count_mismatches"], 0)
        self.assertEqual(audit["universes"]["record_count"], 404_054)
        self.assertEqual(audit["universes"]["stratum_count"], 142)
        self.assertEqual(audit["universes"]["reconstruction_mismatches"], 0)
        self.assertEqual(audit["motif_reconciliation"]["identity_count"], 223)
        self.assertEqual(
            audit["motif_reconciliation"]["identity_or_mechanism_mismatches"], 0
        )

    def test_primary_scope_is_exact_and_partition_reconciles(self):
        audit = self.results["source_audit"]["partition"]
        self.assertEqual(audit["total_k2"], 223)
        self.assertEqual(audit["primary_instances"], 24)
        self.assertEqual(audit["primary_rescues"], 122)
        self.assertEqual(audit["subset_failures"], 0)
        self.assertEqual(audit["disjointness_failures"], 0)
        self.assertEqual(audit["partition_failures"], 0)
        for row in self.results["primary_partition_rows"]:
            self.assertEqual(row["A_V"] + row["A_G"] + row["A_R"], 14)
            self.assertGreaterEqual(row["A_R"], 0)

    def test_primary_and_secondary_roles_are_fixed(self):
        self.assertEqual(self.results["primary_A_G"]["role"], "primary")
        self.assertEqual(self.results["secondary_A_R"]["role"], "secondary")
        self.assertEqual(len(self.results["primary_A_G"]["per_instance"]), 24)
        self.assertEqual(len(self.results["secondary_A_R"]["per_instance"]), 24)

    def test_centered_relation_has_equal_instance_weight(self):
        relation = self.results["centered_A_V_A_G_relation"]
        weights: dict[str, float] = {}
        for row in relation["residual_rows"]:
            weights[row["instance_key"]] = weights.get(row["instance_key"], 0.0) + row["weight"]
        self.assertEqual(len(weights), 24)
        for value in weights.values():
            self.assertAlmostEqual(value, 1 / 24)
        self.assertTrue(relation["correlation_defined"])
        self.assertGreater(relation["variance_A_V"], 0)
        self.assertGreater(relation["variance_A_G"], 0)

    def test_full_census_is_not_claimed_as_partition(self):
        self.assertEqual(len(self.results["supplementary_full_census_pairs"]), 223)
        self.assertFalse(self.results["scope"]["full_census_partition_claim"])
        self.assertTrue(
            all("A_R" not in row for row in self.results["supplementary_full_census_pairs"])
        )

    def test_interpretive_limits_are_explicit(self):
        scope = self.results["scope"]
        self.assertFalse(scope["causal_claim"])
        self.assertFalse(scope["population_generalization"])
        self.assertFalse(scope["directional_hypothesis"])
        self.assertFalse(scope["statistical_independence_claimed"])


if __name__ == "__main__":
    unittest.main()
