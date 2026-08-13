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
    / "analyze_phase97_bottleneck_rescue.py"
)
spec = importlib.util.spec_from_file_location("test_phase98_module", SCRIPT)
phase98 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = phase98
spec.loader.exec_module(phase98)


def evaluations(base, category_words, categories=("A", "B")):
    return phase98.evaluate_category_subsets(
        set(base), category_words, categories, [0], [3]
    )


class Phase98BottleneckRescueTests(unittest.TestCase):
    def test_one_category_alone_rescues(self):
        rows = evaluations({0, 1, 3}, {"A": {2}, "B": set()})
        self.assertEqual(phase98.minimal_rescuing_subsets(rows, "kappa_v"), [["A"]])

    def test_either_category_is_sufficient(self):
        rows = evaluations(
            {0, 1, 3},
            {"A": {2}, "B": {4, 5, 7}},
        )
        self.assertEqual(
            phase98.minimal_rescuing_subsets(rows, "kappa_v"), [["A"], ["B"]]
        )

    def test_both_categories_are_required(self):
        rows = evaluations(
            {0, 1, 3},
            {"A": {4}, "B": {5, 7}},
        )
        self.assertEqual(
            phase98.minimal_rescuing_subsets(rows, "kappa_v"), [["A", "B"]]
        )

    def test_f3_two_category_interaction_without_singleton(self):
        rows = evaluations(
            {0, 1, 3},
            {"A": {4}, "B": {5, 7}, "C": {8}},
            ("A", "B", "C"),
        )
        minimal = phase98.minimal_rescuing_subsets(rows, "kappa_v")
        self.assertIn(["A", "B"], minimal)
        roles = phase98.f3_category_roles(minimal, ("A", "B", "C"))
        self.assertTrue(roles["A"]["interaction_only"])
        self.assertFalse(roles["A"]["individually_sufficient"])

    def test_f2_labels_are_mechanical(self):
        self.assertEqual(
            phase98.classify_f2([["HISTORICAL_SOURCE_POSITIVE"]]),
            "RESCUED_BY_HISTORICAL_SOURCE_POSITIVE_ONLY",
        )
        self.assertEqual(
            phase98.classify_f2(
                [["HISTORICAL_SOURCE_POSITIVE"], ["STATIC_T1"]]
            ),
            "EITHER_F2_CATEGORY_SUFFICIENT",
        )

    def test_canonical_hash_is_layout_independent(self):
        self.assertEqual(
            phase98.canonical_sha256({"z": [2, 1], "a": False}),
            phase98.canonical_sha256({"a": False, "z": [2, 1]}),
        )


if __name__ == "__main__":
    unittest.main()
