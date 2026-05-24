import unittest

from zaa.cycle_laws import (
    _FRONTERA_THRESHOLD_MAX,
    evaluate_complexity_law,
    evaluate_density_law,
    evaluate_frontera_temporal,
    evaluate_periodicity_law,
    evaluate_structure_count_law,
    evaluate_temporal_scale_stability,
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

    def test_velocity_law_rejects_chaotic_rule30(self):
        from zaa.eca import random_initial_state, simulate

        frames = simulate(random_initial_state(64, seed=20260523), 30, 24)
        structures = run_observers(frames)
        result = evaluate_velocity_law(structures)
        self.assertFalse(result.accepted)

    def test_velocity_law_evidence_has_fraction(self):
        structures = run_observers(moving_point(steps=24, width=64))
        result = evaluate_velocity_law(structures)
        self.assertIn("passing_fraction", result.evidence)
        self.assertIn("passing_count", result.evidence)
        self.assertIn("n_structures_tested", result.evidence)

    def test_complexity_law_accepts_rule30(self):
        from zaa.eca import random_initial_state, simulate

        frames = simulate(random_initial_state(64, seed=20260523), 30, 24)
        result = evaluate_complexity_law(frames)
        self.assertTrue(result.accepted)
        self.assertIn("entropy_mean", result.evidence)
        self.assertIn("transition_rate", result.evidence)

    def test_complexity_law_rejects_static_block(self):
        frames = static_block(steps=24, width=64)
        result = evaluate_complexity_law(frames)
        self.assertFalse(result.accepted)

    def test_complexity_law_rejects_moving_point(self):
        frames = moving_point(steps=24, width=64)
        result = evaluate_complexity_law(frames)
        self.assertFalse(result.accepted)

    def test_frontera_temporal_accepts_rule110_short(self):
        from zaa.eca import random_initial_state, simulate

        frames = simulate(random_initial_state(64, seed=20260523), 110, 24)
        result = evaluate_frontera_temporal(frames, threshold_max=_FRONTERA_THRESHOLD_MAX)
        self.assertTrue(result.accepted)
        self.assertEqual(result.reason, "caos_organizado")

    def test_frontera_temporal_rejects_rule30_short(self):
        from zaa.eca import random_initial_state, simulate

        frames = simulate(random_initial_state(64, seed=20260523), 30, 24)
        result = evaluate_frontera_temporal(frames, threshold_max=_FRONTERA_THRESHOLD_MAX)
        self.assertFalse(result.accepted)

    def test_frontera_temporal_rejects_static_block(self):
        frames = static_block(steps=24, width=64)
        result = evaluate_frontera_temporal(frames, threshold_max=_FRONTERA_THRESHOLD_MAX)
        self.assertFalse(result.accepted)

    def test_frontera_temporal_evidence_keys(self):
        from zaa.eca import random_initial_state, simulate

        frames = simulate(random_initial_state(64, seed=20260523), 110, 24)
        result = evaluate_frontera_temporal(frames, threshold_max=_FRONTERA_THRESHOLD_MAX)
        for key in ("transition_rate", "entropy_mean", "threshold_max"):
            self.assertIn(key, result.evidence)

    def test_temporal_scale_stability_accepts_low_steps_chaotic_frames(self):
        from zaa.eca import random_initial_state, simulate

        frames = simulate(random_initial_state(64, seed=20260523), 110, 24)
        result = evaluate_temporal_scale_stability(frames, steps=24)
        self.assertTrue(result.accepted)
        self.assertEqual(result.name, "temporal_scale_stability")

    def test_temporal_scale_stability_rejects_high_steps_chaotic_frames(self):
        from zaa.eca import random_initial_state, simulate

        frames = simulate(random_initial_state(64, seed=20260523), 110, 192)
        result = evaluate_temporal_scale_stability(frames, steps=192)
        self.assertFalse(result.accepted)

    def test_temporal_scale_stability_rejects_zero_transition_rate(self):
        frames = static_block(steps=24, width=64)
        result = evaluate_temporal_scale_stability(frames, steps=24)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "sin_transiciones_temporales")
        self.assertEqual(result.evidence["transition_rate"], 0.0)


if __name__ == "__main__":
    unittest.main()
