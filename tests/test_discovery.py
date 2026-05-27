import json
import tempfile
import unittest

from zaa.discovery import DiscoveryConfig, build_world, run_cycle, run_discovery_loop, save_journal


class DiscoveryTests(unittest.TestCase):
    def test_build_world_synthetic_glider_shape(self):
        config = DiscoveryConfig("synthetic_glider", steps=10, width=32)
        frames = build_world(config)
        self.assertEqual(frames.shape, (11, 32))

    def test_build_world_life_glider_shape(self):
        config = DiscoveryConfig("life_glider", steps=10, width=32, height=24)
        frames = build_world(config)
        self.assertEqual(frames.shape, (11, 24, 32))

    def test_build_world_rule_110_shape(self):
        config = DiscoveryConfig("rule_110", steps=10, width=32)
        frames = build_world(config)
        self.assertEqual(frames.shape, (11, 32))

    def test_build_world_invalid_raises(self):
        with self.assertRaises(ValueError):
            build_world(DiscoveryConfig("invalido"))

    def test_run_cycle_keys(self):
        result = run_cycle(DiscoveryConfig("synthetic_glider", steps=10, width=32), 0)
        for key in [
            "cycle_id",
            "world_type",
            "steps",
            "width",
            "structure_count",
            "dedup_structure_count",
            "inflation_ratio",
            "dominant_type",
            "analysis_status",
            "consensus",
            "metrics",
            "timestamp",
        ]:
            self.assertIn(key, result)

    def test_run_discovery_loop_emits_world_meta_prev_fields(self):
        result = run_discovery_loop(DiscoveryConfig("synthetic_glider", cycles=1))[0]
        for key in [
            "world_signature_diversity_prev",
            "world_score_variance_prev",
            "world_is_multiregime_candidate_prev",
            "world_unique_signatures_prev",
            "world_has_multiregime_evidence_prev",
            "world_peak_diversity_prev",
        ]:
            self.assertIn(key, result)
        self.assertIsNone(result["world_signature_diversity_prev"])
        self.assertIsNone(result["world_score_variance_prev"])
        self.assertFalse(result["world_is_multiregime_candidate_prev"])
        self.assertEqual(result["world_unique_signatures_prev"], 0)
        self.assertFalse(result["world_has_multiregime_evidence_prev"])
        self.assertEqual(result["world_peak_diversity_prev"], 0.0)

    def test_life_glider_metrics_are_nonzero(self):
        result = run_cycle(DiscoveryConfig("life_glider", steps=20, width=32, height=32), 0)
        self.assertGreater(result["metrics"]["density_mean"], 0.0)

    def test_synthetic_glider_cycles_explore_positions(self):
        config = DiscoveryConfig("synthetic_glider", cycles=3, width=64)
        results = [run_cycle(config, cycle_id) for cycle_id in range(3)]
        self.assertTrue(all(item["structure_count"] > 0 for item in results))
        densities = {item["metrics"]["density_mean"] for item in results}
        self.assertGreaterEqual(len(densities), 2)

    def test_rule_30_is_marked_as_noise(self):
        result = run_cycle(DiscoveryConfig("rule_30", steps=200, width=256), 0)
        self.assertEqual(result["analysis_status"], "ruido_no_analizable")

    def test_rule_109_high_steps_is_ok_under_dedup_gate(self):
        result = run_cycle(DiscoveryConfig("rule_109", steps=192, width=64, seed=20260523), 0)
        self.assertEqual(result["analysis_status"], "ok")
        self.assertLessEqual(result["dedup_structure_count"], 40)
        self.assertGreater(result["structure_count"], 40)

    def test_rule_30_high_steps_remains_noise_under_dedup_gate(self):
        result = run_cycle(DiscoveryConfig("rule_30", steps=96, width=64, seed=20260523), 0)
        self.assertEqual(result["analysis_status"], "ruido_no_analizable")
        self.assertGreater(result["dedup_structure_count"], 40)

    def test_rule_137_high_steps_remains_noise_under_dedup_gate(self):
        result = run_cycle(DiscoveryConfig("rule_137", steps=96, width=64, seed=20260523), 0)
        self.assertEqual(result["analysis_status"], "ruido_no_analizable")
        self.assertGreater(result["dedup_structure_count"], 40)

    def test_synthetic_glider_status_ok(self):
        result = run_cycle(DiscoveryConfig("synthetic_glider"), 0)
        self.assertEqual(result["analysis_status"], "ok")

    def test_run_discovery_loop_cycles(self):
        results = run_discovery_loop(DiscoveryConfig("synthetic_bloque", cycles=3))
        self.assertEqual(len(results), 3)
        self.assertEqual([item["cycle_id"] for item in results], [0, 1, 2])

    def test_save_journal_writes_jsonl(self):
        results = run_discovery_loop(DiscoveryConfig("synthetic_oscilador", cycles=2))
        with tempfile.TemporaryDirectory() as tmp:
            path = save_journal(results, f"{tmp}/journal.jsonl")
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        for line in lines:
            self.assertIn("world_type", json.loads(line))

    def test_world_steps_do_not_carry_over(self):
        config = DiscoveryConfig("synthetic_glider", cycles=20, steps=24)
        results = run_discovery_loop(config)
        for r in results:
            if r["world_type"] == "rule_30":
                self.assertLessEqual(r["steps"], 48)
                return

    def test_rule110_noise_boundary_prevents_repeated_large_scales(self):
        state = {
            "schema_version": 1,
            "seen_law_signatures": [
                [
                    "complejidad_alta",
                    "densidad_estable",
                    "frontera_temporal",
                    "temporal_scale_stability",
                ]
            ],
            "world_history": {
                "rule_110": {
                    "visit_count": 2,
                    "scores": [3.0, -1.0],
                    "noise_count": 1,
                    "law_signatures": [
                        [
                            "complejidad_alta",
                            "densidad_estable",
                            "frontera_temporal",
                            "temporal_scale_stability",
                        ],
                        [],
                    ],
                    "params_tried": [
                        [
                            24,
                            64,
                            [
                                "complejidad_alta",
                                "densidad_estable",
                                "frontera_temporal",
                                "temporal_scale_stability",
                            ],
                        ],
                        [48, 64, []],
                    ],
                    "max_ok_steps": 24,
                    "first_noise_steps": 48,
                }
            },
        }
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        ) as handle:
            json.dump(state, handle)
            path = handle.name
        try:
            results = run_discovery_loop(DiscoveryConfig("rule_110", cycles=1, steps=24, state_file=path))
            self.assertEqual(results[0]["steps"], 24)
            self.assertEqual(results[0]["action_reason"], "noise_boundary_alcanzado")
        finally:
            from pathlib import Path

            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
