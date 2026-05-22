import unittest

import numpy as np

from zaa.consensus import consensus_by_type, dominant_type
from zaa.life2d import life_fixture, simulate_life
from zaa.observers2d import run_observers_2d


class Life2DTests(unittest.TestCase):
    def test_block_is_stable(self):
        initial = life_fixture("block")
        frames = simulate_life(initial, 4)
        for frame in frames:
            np.testing.assert_array_equal(frame, initial)

    def test_blinker_has_period_2(self):
        initial = life_fixture("blinker")
        frames = simulate_life(initial, 2)
        self.assertFalse(np.array_equal(frames[0], frames[1]))
        np.testing.assert_array_equal(frames[0], frames[2])

    def test_glider_moves_after_four_steps(self):
        initial = life_fixture("glider")
        frames = simulate_life(initial, 4)
        expected = np.roll(np.roll(initial, 1, axis=0), 1, axis=1)
        np.testing.assert_array_equal(frames[4], expected)

    def test_observers_detect_block(self):
        frames = simulate_life(life_fixture("block"), 4)
        structures = run_observers_2d(frames)
        self.assertTrue(consensus_by_type(structures).get("bloque", False))
        self.assertEqual(dominant_type(structures), "bloque")

    def test_observers_detect_blinker(self):
        frames = simulate_life(life_fixture("blinker"), 6)
        structures = run_observers_2d(frames)
        self.assertTrue(consensus_by_type(structures).get("oscilador", False))
        self.assertEqual(dominant_type(structures), "oscilador")

    def test_observers_detect_glider(self):
        frames = simulate_life(life_fixture("glider"), 8)
        structures = run_observers_2d(frames)
        self.assertTrue(consensus_by_type(structures).get("glider", False))
        self.assertEqual(dominant_type(structures), "glider")
        for structure in structures:
            self.assertEqual(len(structure.posiciones[0]), 3)


if __name__ == "__main__":
    unittest.main()
