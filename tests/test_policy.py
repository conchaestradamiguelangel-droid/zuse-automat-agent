import unittest

from zaa.history import WorldRecord
from zaa.policy import MAX_REPEATS_DEFAULT, PolicyState, _next_world, compute_score, decide


def state(**overrides):
    data = {
        "world_type": "synthetic_glider",
        "analysis_status": "ok",
        "structure_count": 1,
        "laws_accepted": [],
        "dominant_type": "glider",
        "steps": 24,
        "seed": 10,
        "repeats_in_current_world": 0,
    }
    data.update(overrides)
    return PolicyState(**data)


class PolicyTests(unittest.TestCase):
    def test_noise_changes_world(self):
        decision = decide(state(analysis_status="ruido_no_analizable"))
        self.assertEqual(decision.action, "change_world")
        self.assertEqual(decision.reason, "ruido_no_analizable")

    def test_no_structures_increases_steps(self):
        decision = decide(state(structure_count=0, steps=24), max_steps=400)
        self.assertEqual(decision.action, "increase_steps")
        self.assertEqual(decision.next_steps, 48)

    def test_no_structures_at_max_changes_world(self):
        decision = decide(state(structure_count=0, steps=400), max_steps=400)
        self.assertEqual(decision.action, "change_world")

    def test_many_laws_repeats_with_new_seed(self):
        decision = decide(state(laws_accepted=["a", "b"], repeats_in_current_world=0, is_new_law_signature=True))
        self.assertEqual(decision.action, "repeat_vary_seed")
        self.assertEqual(decision.next_seed, 11)

    def test_many_laws_without_score_improvement_changes_world(self):
        decision = decide(
            state(laws_accepted=["a", "b"], repeats_in_current_world=0, score=2.0, steps=400),
            prev_score=3.0,
            max_steps=400,
        )
        self.assertEqual(decision.action, "change_world")

    def test_many_laws_with_score_improvement_repeats(self):
        decision = decide(
            state(laws_accepted=["a", "b"], repeats_in_current_world=0, score=3.0, steps=400),
            prev_score=2.0,
            max_steps=400,
        )
        self.assertEqual(decision.action, "repeat_vary_seed")

    def test_many_laws_at_max_repeats_changes_world(self):
        decision = decide(state(laws_accepted=["a", "b"], repeats_in_current_world=3), max_repeats=3)
        self.assertEqual(decision.action, "change_world")

    def test_few_laws_increases_steps(self):
        decision = decide(state(laws_accepted=["a"], steps=24))
        self.assertEqual(decision.action, "increase_steps")

    def test_score_counts_laws(self):
        self.assertEqual(compute_score(state(laws_accepted=["a", "b"]), None), 2.0)

    def test_score_penalizes_noise(self):
        self.assertEqual(compute_score(state(analysis_status="ruido_no_analizable"), None), -1.0)

    def test_score_rewards_new_dominant(self):
        self.assertEqual(compute_score(state(dominant_type="glider"), "bloque"), 0.5)

    def test_next_world_wraps(self):
        self.assertEqual(_next_world("rule_110"), "synthetic_glider")

    def test_next_world_advances(self):
        self.assertEqual(_next_world("synthetic_glider"), "synthetic_oscilador")

    def test_blocked_world_is_skipped(self):
        decision = decide(state(world_type="rule110_real"))
        self.assertEqual(decision.action, "skip_rule110_real")

    def test_max_repeats_default_is_one(self):
        self.assertEqual(MAX_REPEATS_DEFAULT, 1)

    def test_history_consistently_noisy_changes_world(self):
        record = WorldRecord(visit_count=4, scores=[-1.0, -1.0, -1.0, 1.0], noise_count=3)
        decision = decide(state(), world_record=record)
        self.assertEqual(decision.action, "change_world")
        self.assertEqual(decision.reason, "mundo_consistentemente_ruidoso")

    def test_new_law_signature_triggers_repeat(self):
        decision = decide(state(is_new_law_signature=True, structure_count=3))
        self.assertEqual(decision.action, "repeat_vary_seed")
        self.assertEqual(decision.reason, "firma_leyes_nueva_explorar_mas")

    def test_scale_search_on_known_signature(self):
        decision = decide(state(laws_accepted=["a", "b"], repeats_in_current_world=0))
        self.assertEqual(decision.action, "increase_steps")
        self.assertEqual(decision.reason, "firma_conocida_buscar_escala")
        self.assertEqual(decision.next_steps, 48)

    def test_scale_search_does_not_fire_after_repeat(self):
        decision = decide(state(laws_accepted=["a", "b"], repeats_in_current_world=1))
        self.assertNotEqual(decision.reason, "firma_conocida_buscar_escala")

    def test_scale_search_does_not_fire_at_max_steps(self):
        decision = decide(state(laws_accepted=["a", "b"], repeats_in_current_world=0, steps=400), max_steps=400)
        self.assertNotEqual(decision.reason, "firma_conocida_buscar_escala")


if __name__ == "__main__":
    unittest.main()
