import unittest

from zaa.collisions import detect_collision_candidates_rule110, run_collision_detection_rule110
from zaa.fixtures import load_fixture
from zaa.rule110_fixtures import (
    TWO_GLIDER_SPECS,
    build_two_glider_initial_condition,
    generate_all_two_glider_candidates,
)


class Rule110CollisionTests(unittest.TestCase):
    def test_single_glider_fixture_has_no_collision_candidates(self):
        fixture = load_fixture("fixtures/validated/FIX-A.npz")
        candidates = detect_collision_candidates_rule110(fixture["frames_esperados"])
        self.assertEqual(candidates, [])

    def test_two_glider_initial_condition_shape(self):
        spec = TWO_GLIDER_SPECS[0]
        ci = build_two_glider_initial_condition(spec.spec_a, spec.spec_b, spec.separation)
        self.assertEqual(ci.shape, (256,))
        self.assertGreater(int(ci.sum()), 0)

    def test_generate_all_two_glider_candidates(self):
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            generated = generate_all_two_glider_candidates(output_dir=tmp)
            names = sorted(item["npz"].name for item in generated)
            self.assertEqual(names, ["FIX-D.npz", "FIX-E.npz"])
            for item in generated:
                self.assertTrue(item["npz"].exists())
                self.assertTrue(item["png"].exists())
                self.assertTrue(item["summary"].exists())

    def test_collision_detection_reports_gap_for_single_glider_fixtures(self):
        report = run_collision_detection_rule110("fixtures/validated")
        self.assertEqual(report["total"], 0)
        self.assertEqual(report["gap"], "sin_colisiones_en_fixtures_actuales")


if __name__ == "__main__":
    unittest.main()
