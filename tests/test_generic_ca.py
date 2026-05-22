import unittest

import numpy as np

from zaa.eca import simulate
from zaa.generic_ca import eca_rule_table, simulate_callable, simulate_table, table_size


class GenericCaTests(unittest.TestCase):
    def test_table_size(self):
        self.assertEqual(table_size(2, 1), 8)
        self.assertEqual(table_size(3, 1), 27)
        self.assertEqual(table_size(2, 2), 32)

    def test_generic_table_matches_eca_for_all_rules(self):
        rng = np.random.default_rng(20260523)
        for rule in range(256):
            initial = rng.integers(0, 2, size=48, dtype=np.uint8)
            expected = simulate(initial, rule, 12)
            actual = simulate_table(initial, eca_rule_table(rule), states=2, radius=1, steps=12)
            np.testing.assert_array_equal(actual, expected, err_msg=f"rule={rule}")

    def test_callable_rule(self):
        initial = np.array([0, 1, 2, 1, 0], dtype=np.uint8)

        def max_neighbor(neighborhood):
            return int(np.max(neighborhood))

        frames = simulate_callable(initial, max_neighbor, states=3, radius=1, steps=2)
        expected = np.array(
            [
                [0, 1, 2, 1, 0],
                [1, 2, 2, 2, 1],
                [2, 2, 2, 2, 2],
            ],
            dtype=np.uint8,
        )
        np.testing.assert_array_equal(frames, expected)


if __name__ == "__main__":
    unittest.main()
