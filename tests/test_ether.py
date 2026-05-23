import unittest

import numpy as np

from zaa.eca import simulate
from zaa.ether import defect_activity_ratio, diff_from_pure_ether, pure_ether_frames
from zaa.rule110_fixtures import ether_state


class EtherTests(unittest.TestCase):
    def test_pure_ether_diff_is_zero(self):
        frames = pure_ether_frames(64, 16)
        diff = diff_from_pure_ether(frames)
        self.assertEqual(int(diff.sum()), 0)
        self.assertEqual(defect_activity_ratio(frames), 0.0)

    def test_defect_diff_is_nonzero(self):
        ci = ether_state(64)
        ci[20] = 1 - ci[20]
        frames = simulate(ci, 110, 16)
        diff = diff_from_pure_ether(frames)
        self.assertGreater(int(diff.sum()), 0)
        self.assertTrue(set(np.unique(diff).tolist()).issubset({0, 1}))


if __name__ == "__main__":
    unittest.main()
