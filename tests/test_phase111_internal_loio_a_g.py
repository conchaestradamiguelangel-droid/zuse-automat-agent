from __future__ import annotations

import importlib.util
import sys
import unittest
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "outputs"
    / "periodic_backgrounds"
    / "analyze_phase110_internal_loio_a_g.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase111 = load_module("test_phase111_module", SCRIPT)


class Phase111InternalLoioAGTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results, cls.sources = phase111.analyze()

    def test_sources_join_exactly_and_census_is_fixed(self):
        audit = self.results["source_audit"]
        self.assertEqual(audit["join"]["identity_count"], 223)
        self.assertEqual(audit["join"]["mechanism_mismatches"], 0)
        self.assertEqual(audit["rescue_count"], 223)
        self.assertEqual(audit["instance_count"], 101)
        self.assertEqual(
            audit["instance_composition"],
            {"only_external": 6, "only_internal": 71, "mixed": 24},
        )

    def test_all_folds_retain_classes_and_baseline_is_internal(self):
        self.assertEqual(len(self.results["folds"]), 101)
        self.assertEqual(self.results["source_audit"]["training_class_loss_folds"], 0)
        self.assertEqual(self.results["source_audit"]["non_internal_baseline_folds"], 0)
        self.assertTrue(
            all(fold["baseline_class"] == phase111.INTERNAL for fold in self.results["folds"])
        )

    def test_threshold_set_and_tie_break_are_deterministic(self):
        self.assertEqual(self.results["design"]["thresholds"], list(range(3, 10)))
        tied = [
            {
                "threshold": threshold,
                "balanced_accuracy": Fraction(3, 4),
                "minimum_sensitivity": Fraction(2, 3),
                "sensitivity_gap": Fraction(1, 6),
            }
            for threshold in (6, 4, 5)
        ]
        self.assertEqual(phase111.choose_threshold(tied)["threshold"], 4)
        self.assertEqual(sum(self.results["threshold_distribution"].values()), 101)

    def test_exact_equal_instance_weights_are_declared_and_reconcile(self):
        self.assertEqual(self.results["design"]["arithmetic"], "exact_fractions")
        self.assertEqual(self.results["design"]["training_weight_rule"], "1/(100*n_i)")
        aggregate = self.results["aggregate"]["classifier_weighted"]
        self.assertEqual(aggregate["weight_rule"], "1/(101*n_i)")
        for metric in ("sensitivity_external", "sensitivity_internal", "balanced_accuracy"):
            value = aggregate[metric]
            self.assertAlmostEqual(value["decimal"], value["numerator"] / value["denominator"])

    def test_missing_held_out_class_is_na_not_zero(self):
        pure = [
            fold
            for fold in self.results["folds"]
            if 0 in fold["held_out_composition"].values()
        ]
        self.assertEqual(len(pure), 77)
        for fold in pure:
            if fold["held_out_composition"][phase111.EXTERNAL] == 0:
                self.assertIsNone(fold["held_out_sensitivity_external"])
            if fold["held_out_composition"][phase111.INTERNAL] == 0:
                self.assertIsNone(fold["held_out_sensitivity_internal"])

    def test_predictions_and_raw_confusion_reconcile(self):
        predictions = self.results["out_of_fold_predictions"]
        self.assertEqual(len(predictions), 223)
        matrix = self.results["aggregate"]["classifier_unweighted"][
            "matrix_actual_by_predicted"
        ]
        self.assertEqual(sum(sum(row.values()) for row in matrix.values()), 223)
        self.assertEqual(
            self.results["aggregate"]["baseline_weighted"]["balanced_accuracy"][
                "decimal"
            ],
            0.5,
        )

    def test_subgroups_use_their_own_equal_instance_weights(self):
        mixed = self.results["subgroups"]["mixed_24_instances"]["weighted"]
        mono = self.results["subgroups"]["monolabel_77_instances"]["weighted"]
        self.assertEqual((mixed["instance_count"], mixed["rescue_count"]), (24, 122))
        self.assertEqual((mono["instance_count"], mono["rescue_count"]), (77, 101))
        self.assertEqual(mixed["weight_rule"], "1/(24*n_i)")
        self.assertEqual(mono["weight_rule"], "1/(77*n_i)")

    def test_limits_and_single_predictor_are_explicit(self):
        scope = self.results["scope"]
        self.assertTrue(scope["outcome_data_seen_during_feature_design"])
        for field in (
            "feature_selection_nested_within_loio",
            "external_validation",
            "prospective_validation",
            "causal_claim",
            "population_generalization",
            "auditor_replacement_authorized",
        ):
            self.assertFalse(scope[field])
        self.assertEqual(self.results["source_audit"]["predictors_used"], ["A_G"])


if __name__ == "__main__":
    unittest.main()
