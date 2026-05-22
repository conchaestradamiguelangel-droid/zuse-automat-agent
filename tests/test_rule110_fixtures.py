import unittest

import numpy as np

from zaa.eca import simulate
from zaa.rule110_fixtures import (
    FIXTURE_SPECS,
    align_candidate,
    build_initial_condition,
    difference_from_ether,
    ether_state,
    generate_candidate,
)


class Rule110FixtureTests(unittest.TestCase):
    def test_ether_state_shape_and_values(self):
        state = ether_state(256)
        self.assertEqual(state.shape, (256,))
        self.assertEqual(state.dtype, np.uint8)
        self.assertTrue(set(state.tolist()).issubset({0, 1}))

    def test_specs_fit_in_width(self):
        for spec in FIXTURE_SPECS:
            ci = build_initial_condition(spec)
            self.assertEqual(ci.shape, (spec.width,))
            expected = [int(ch) for ch in spec.pattern]
            actual = ci[spec.insert_at : spec.insert_at + len(spec.pattern)].tolist()
            self.assertEqual(actual, expected)

    def test_generate_candidate_outputs_npz_and_png(self):
        import tempfile

        spec = FIXTURE_SPECS[0]
        with tempfile.TemporaryDirectory() as tmp:
            generated = generate_candidate(spec, output_dir=tmp)
            self.assertTrue(generated["npz"].exists())
            self.assertTrue(generated["png"].exists())
            self.assertTrue(generated["summary"].exists())

    def test_difference_from_pure_ether_is_zero_for_ether(self):
        frames = simulate(ether_state(64), 110, 12)
        self.assertEqual(difference_from_ether(frames), 0)

    def test_auto_alignment_makes_each_candidate_nontrivial(self):
        for spec in FIXTURE_SPECS:
            aligned = align_candidate(spec)
            frames = simulate(build_initial_condition(aligned), 110, aligned.steps)
            self.assertGreater(difference_from_ether(frames), 0, spec.fixture_id)


if __name__ == "__main__":
    unittest.main()
