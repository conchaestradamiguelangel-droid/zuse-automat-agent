import unittest

from zaa.cycle_laws import (
    evaluate_density_law,
    evaluate_periodicity_law,
    evaluate_structure_count_law,
    evaluate_velocity_law,
)
from zaa.discovery import DiscoveryConfig, run_cycle
from zaa.observers import run_observers
from zaa.synthetic import moving_point, oscillator, static_block


class CycleLawTests(unittest.TestCase):
    def test_velocity_law_accepts_moving_point(self):
        structures = run_observers(moving_point(steps=24, width=64))
        result = evaluate_velocity_law(structures)
        self.assertTrue(result.accepted)

    def test_periodicity_law_accepts_oscillator(self):
        structures = run_observers(oscillator(steps=24, width=64))
        result = evaluate_periodicity_law(structures)
        self.assertTrue(result.accepted)

    def test_density_law_accepts_static_block(self):
        frames = static_block(steps=24, width=64)
        result = evaluate_density_law(frames)
        self.assertTrue(result.accepted)

    def test_structure_count_law_accepts_single_type(self):
        structures = run_observers(moving_point(steps=24, width=64))
        result = evaluate_structure_count_law(structures)
        self.assertTrue(result.accepted)

    def test_run_cycle_includes_law_fields(self):
        result = run_cycle(DiscoveryConfig("synthetic_glider"), 0)
        self.assertIn("laws_accepted", result)
        self.assertIn("laws_rejected", result)
        self.assertIn("laws_status", result)

    def test_noise_cycle_skips_laws(self):
        result = run_cycle(DiscoveryConfig("rule_30", steps=200, width=256), 0)
        self.assertEqual(result["laws_status"], "skipped_noise")
        self.assertEqual(result["laws_accepted"], [])


if __name__ == "__main__":
    unittest.main()
