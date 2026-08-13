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
    / "analyze_phase98_historical_period_rescue.py"
)
spec = importlib.util.spec_from_file_location("test_phase99_module", SCRIPT)
phase99 = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = phase99
spec.loader.exec_module(phase99)


def profiles(periods, rescued):
    rows = []
    for subset in phase99.powerset(tuple(periods)):
        rows.append(
            {
                "periods": list(subset),
                "kappa_v": 2 if frozenset(subset) in rescued else 1,
                "lambda_e": 2 if frozenset(subset) in rescued else 1,
            }
        )
    return rows


class Phase99HistoricalPeriodRescueTests(unittest.TestCase):
    def test_unique_singleton_rescue(self):
        rows = profiles((2, 3), {frozenset({2}), frozenset({2, 3})})
        minimal = phase99.minimal_rescuing_period_sets(rows, "kappa_v")
        self.assertEqual(minimal, [[2]])
        self.assertEqual(phase99.classify_minimal_period_sets(minimal), "UNIQUE_SINGLETON_RESCUE")

    def test_multiple_singleton_alternatives(self):
        rows = profiles(
            (2, 3),
            {frozenset({2}), frozenset({3}), frozenset({2, 3})},
        )
        minimal = phase99.minimal_rescuing_period_sets(rows, "kappa_v")
        self.assertEqual(minimal, [[2], [3]])
        self.assertEqual(
            phase99.classify_minimal_period_sets(minimal),
            "MULTIPLE_SINGLETON_ALTERNATIVES",
        )

    def test_interaction_required(self):
        rows = profiles((2, 3), {frozenset({2, 3})})
        minimal = phase99.minimal_rescuing_period_sets(rows, "kappa_v")
        self.assertEqual(minimal, [[2, 3]])
        self.assertEqual(phase99.classify_minimal_period_sets(minimal), "INTERACTION_REQUIRED")

    def test_mixed_singleton_and_interaction_minima(self):
        rescued = {
            frozenset({2}),
            frozenset({3, 5}),
            frozenset({2, 3}),
            frozenset({2, 5}),
            frozenset({2, 3, 5}),
        }
        rows = profiles((2, 3, 5), rescued)
        minimal = phase99.minimal_rescuing_period_sets(rows, "kappa_v")
        self.assertEqual(minimal, [[2], [3, 5]])
        self.assertEqual(
            phase99.classify_minimal_period_sets(minimal),
            "MIXED_SINGLETON_AND_INTERACTION_MINIMA",
        )

    def test_absent_period_is_not_given_a_role(self):
        roles = phase99.period_roles((2, 3), [[2]])
        self.assertEqual(set(roles), {"2", "3"})
        self.assertTrue(roles["3"]["unused_in_minimal_rescue"])

    def test_cover_monotonicity_counts_every_relation(self):
        rows = profiles(
            (2, 3, 5),
            {
                frozenset({2}),
                frozenset({2, 3}),
                frozenset({2, 5}),
                frozenset({2, 3, 5}),
            },
        )
        count, failures = phase99.validate_cover_monotonicity(rows, (2, 3, 5))
        self.assertEqual(count, 12)
        self.assertEqual(failures, 0)

    def test_cover_monotonicity_detects_failure(self):
        rows = profiles((2,), {frozenset()})
        count, failures = phase99.validate_cover_monotonicity(rows, (2,))
        self.assertEqual(count, 1)
        self.assertEqual(failures, 2)


if __name__ == "__main__":
    unittest.main()
