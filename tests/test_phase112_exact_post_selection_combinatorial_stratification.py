from __future__ import annotations

import importlib.util
import math
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "outputs"
    / "periodic_backgrounds"
    / "analyze_phase111_exact_post_selection_combinatorial_stratification.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase112 = load_module("test_phase112_module", SCRIPT)


def multiply_polynomials(left: list[int], right: list[int], maximum: int) -> list[int]:
    output = [0] * min(len(left) + len(right) - 1, maximum + 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            if i + j <= maximum:
                output[i + j] += a * b
    return output


def extreme_event_count_independent() -> int:
    polynomial = [1]
    factors = []
    factors.extend([[1, 1]] * 56)
    factors.extend([[1, 0, 1]] * 18)
    factors.extend([[1, 0, 0, 1]] * 3)
    for n_i, count in ((4, 14), (6, 4), (7, 6)):
        mixed_factor = [math.comb(n_i, k) if 0 < k < n_i else 0 for k in range(n_i + 1)]
        factors.extend([mixed_factor] * count)
    for factor in factors:
        polynomial = multiply_polynomials(polynomial, factor, phase112.EXPECTED_EXTERNAL)
    return polynomial[phase112.EXPECTED_EXTERNAL]


class Phase112ExactPostSelectionCalibrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results, cls.sources = phase112.analyze()

    def test_sources_reconcile_exactly(self):
        audit = self.results["source_audit"]
        self.assertEqual(audit["rescue_count"], 223)
        self.assertEqual(audit["instance_count"], 101)
        self.assertEqual(audit["external_count"], 54)
        self.assertEqual(audit["internal_count"], 169)
        self.assertEqual(audit["reconciliation"]["identity_count"], 223)
        for field, value in audit["reconciliation"].items():
            if field != "identity_count":
                self.assertEqual(value, 0)

    def test_multiplicity_distribution_and_structural_exclusion(self):
        self.assertEqual(
            self.results["source_audit"]["n_i_distribution"],
            {"1": 56, "2": 18, "3": 3, "4": 14, "6": 4, "7": 6},
        )
        self.assertEqual(self.results["source_audit"]["n_i_5_support"], 0)
        self.assertTrue(self.results["strata"]["X"]["included_in_DP"])
        self.assertFalse(self.results["strata"]["X"]["contributes_to_D"])

    def test_observed_vector_and_D_are_computed_from_census(self):
        observed = self.results["observed_statistic"]
        self.assertEqual((observed["mixed_Y"], observed["mixed_Z"]), (0, 24))
        self.assertEqual(
            Fraction(observed["D_obs"]["numerator"], observed["D_obs"]["denominator"]),
            Fraction(1),
        )
        table = {row["n_i"]: row for row in self.results["marginal_strata"]}
        self.assertEqual([table[n]["observed_mixed"] for n in (2, 3, 4, 6, 7)], [0, 0, 14, 4, 6])

    def test_DP_mass_and_full_map_are_exact(self):
        null = self.results["exact_joint_null"]
        expected = math.comb(223, 54)
        self.assertEqual(null["total_assignment_count"], expected)
        self.assertEqual(null["summed_dp_count"], expected)
        self.assertEqual(null["order_invariance_failures"], 0)
        self.assertEqual(null["state_map_cell_count"], 550)
        self.assertEqual(len(null["full_joint_distribution"]), 550)

    def test_tail_event_matches_independent_polynomial_calculation(self):
        null = self.results["exact_joint_null"]
        independent_count = extreme_event_count_independent()
        self.assertEqual(null["tail_count"], independent_count)
        self.assertEqual([(row["y"], row["z"]) for row in null["qualifying_pairs"]], [(0, 24)])
        expected_mass = Fraction(independent_count, math.comb(223, 54))
        self.assertEqual(
            Fraction(null["tail_mass"]["numerator"], null["tail_mass"]["denominator"]),
            expected_mass,
        )

    def test_secondary_results_only_reuse_certified_predictions(self):
        rows = {row["n_i"]: row for row in self.results["secondary_phase111_errors_by_n_i"]}
        self.assertEqual(
            [(n, rows[n]["rescue_count"], rows[n]["external_count"], rows[n]["internal_count"]) for n in (4, 6, 7)],
            [(4, 56, 28, 28), (6, 24, 6, 18), (7, 42, 12, 30)],
        )
        self.assertEqual([rows[n]["A_G_4_or_5_count"] for n in (4, 6, 7)], [44, 14, 18])
        self.assertEqual([rows[n]["phase111_error_count"] for n in (4, 6, 7)], [22, 12, 18])

    def test_scope_is_explicitly_post_selection_and_nonconfirmatory(self):
        scope = self.results["scope"]
        self.assertTrue(scope["outcome_data_seen_during_feature_design"])
        self.assertTrue(scope["threshold_selected_after_outcome_inspection"])
        self.assertTrue(scope["exact_null_model_is_descriptive_post_selection"])
        self.assertTrue(scope["tail_direction_selected_after_outcome_inspection"])
        for field in (
            "directional_hypothesis",
            "external_validation",
            "prospective_validation",
            "causal_claim",
            "population_generalization",
            "formal_null_hypothesis_test",
            "tail_probability_is_confirmatory_p_value",
            "multiple_selection_adjustment",
        ):
            self.assertFalse(scope[field])


if __name__ == "__main__":
    unittest.main()
