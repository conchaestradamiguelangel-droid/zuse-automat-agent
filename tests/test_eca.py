import unittest

import numpy as np

from zaa.eca import rule_bits, simulate, single_seed_initial_state, step
from zaa.fixtures import load_fixture, save_fixture
from zaa.metrics import summarize_frames
from zaa.packed_eca import array_to_int, int_to_array, packed_step, packed_step_rule110


class EcaTests(unittest.TestCase):
    def test_rule_bits(self):
        self.assertEqual(rule_bits(0).tolist(), [0, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(rule_bits(255).tolist(), [1, 1, 1, 1, 1, 1, 1, 1])

    def test_rule_0_goes_blank(self):
        state = np.ones(16, dtype=np.uint8)
        next_state = step(state, 0)
        self.assertEqual(int(next_state.sum()), 0)

    def test_rule_255_goes_full(self):
        state = np.zeros(16, dtype=np.uint8)
        next_state = step(state, 255)
        self.assertEqual(int(next_state.sum()), 16)

    def test_simulate_shape(self):
        initial = single_seed_initial_state(32)
        frames = simulate(initial, 110, 10)
        self.assertEqual(frames.shape, (11, 32))
        self.assertEqual(frames.dtype, np.uint8)

    def test_metrics_are_present(self):
        initial = single_seed_initial_state(32)
        frames = simulate(initial, 30, 10)
        metrics = summarize_frames(frames)
        self.assertIn("entropy_mean", metrics)
        self.assertIn("gzip_ratio", metrics)
        self.assertIn("mutual_info_mean", metrics)
        self.assertIn("density_mean", metrics)
        self.assertIn("transition_rate", metrics)

    def test_packed_step_matches_numpy_step(self):
        rng = np.random.default_rng(123)
        for rule in [0, 18, 30, 54, 90, 110, 184, 255]:
            state = rng.integers(0, 2, size=64, dtype=np.uint8)
            packed = array_to_int(state)
            expected = step(state, rule)
            actual = int_to_array(packed_step(packed, rule, 64), 64)
            np.testing.assert_array_equal(actual, expected)

    def test_specialized_rule110_matches_numpy_step(self):
        rng = np.random.default_rng(456)
        state = rng.integers(0, 2, size=128, dtype=np.uint8)
        packed = array_to_int(state)
        expected = step(state, 110)
        actual = int_to_array(packed_step_rule110(packed, 128), 128)
        np.testing.assert_array_equal(actual, expected)

    def test_rule110_truth_table_ground_truth(self):
        # Manually derived from Rule 110 truth table:
        # 111->0, 110->1, 101->1, 100->0, 011->1, 010->1, 001->1, 000->0.
        initial = np.array([0, 0, 0, 0, 1, 0, 0, 0, 0], dtype=np.uint8)
        expected = np.array(
            [
                [0, 0, 0, 0, 1, 0, 0, 0, 0],
                [0, 0, 0, 1, 1, 0, 0, 0, 0],
                [0, 0, 1, 1, 1, 0, 0, 0, 0],
                [0, 1, 1, 0, 1, 0, 0, 0, 0],
                [1, 1, 1, 1, 1, 0, 0, 0, 0],
                [1, 0, 0, 0, 1, 0, 0, 0, 1],
            ],
            dtype=np.uint8,
        )
        np.testing.assert_array_equal(simulate(initial, 110, 5), expected)

    def test_npz_fixture_round_trip(self):
        import tempfile

        initial = single_seed_initial_state(16)
        frames = simulate(initial, 110, 3)
        with tempfile.TemporaryDirectory() as tmp:
            path = save_fixture(
                f"{tmp}/fixture.npz",
                nombre="smoke",
                fuente="test",
                seed=1,
                ci=initial,
                frames_esperados=frames,
                gliders_esperados=[{"tipo": "glider", "t_inicio": 0, "t_fin": 3}],
            )
            loaded = load_fixture(path)
        np.testing.assert_array_equal(loaded["ci"], initial)
        np.testing.assert_array_equal(loaded["frames_esperados"], frames)
        self.assertEqual(loaded["metadata"]["nombre"], "smoke")


if __name__ == "__main__":
    unittest.main()
