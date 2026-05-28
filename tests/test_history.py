import json
from pathlib import Path
import tempfile
import unittest

from zaa.history import WorldRecord, load_agent_state, save_agent_state, update_history


class WorldHistoryTests(unittest.TestCase):
    def test_update_accumulates_visits(self):
        history = {}
        update_history(history, "synthetic_glider", 3.0, "ok")
        update_history(history, "synthetic_glider", 1.0, "ok")
        record = history["synthetic_glider"]
        self.assertEqual(record.visit_count, 2)
        self.assertAlmostEqual(record.avg_score, 2.0)

    def test_noise_fraction_counts_correctly(self):
        history = {}
        update_history(history, "rule_30", -1.0, "ruido_no_analizable")
        update_history(history, "rule_30", -1.0, "ruido_no_analizable")
        update_history(history, "rule_30", 1.0, "ok")
        self.assertAlmostEqual(history["rule_30"].noise_fraction, 2 / 3)

    def test_avg_score_empty_record(self):
        self.assertEqual(WorldRecord().avg_score, 0.0)

    def test_noise_fraction_empty_record(self):
        self.assertEqual(WorldRecord().noise_fraction, 0.0)

    def test_law_signatures_recorded(self):
        history = {}
        sig = ("densidad_estable", "velocidad_constante")
        update_history(history, "synthetic_glider", 3.0, "ok", sig)
        update_history(history, "synthetic_glider", 3.0, "ok", sig)
        self.assertEqual(len(history["synthetic_glider"].law_signatures), 2)
        self.assertEqual(history["synthetic_glider"].law_signatures[0], frozenset(sig))

    def test_save_load_roundtrip(self):
        history = {}
        sig = ("densidad_estable", "velocidad_constante")
        update_history(history, "synthetic_glider", 3.0, "ok", sig)
        seen = {sig, ("periodicidad",)}
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
        try:
            save_agent_state(history, seen, path)
            loaded_history, loaded_seen = load_agent_state(path)
            self.assertEqual(loaded_history["synthetic_glider"].visit_count, 1)
            self.assertAlmostEqual(loaded_history["synthetic_glider"].avg_score, 3.0)
            self.assertIn(sig, loaded_seen)
            self.assertIn(("periodicidad",), loaded_seen)
        finally:
            path.unlink(missing_ok=True)

    def test_load_empty_state(self):
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        ) as f:
            json.dump({"schema_version": 1, "seen_law_signatures": [], "world_history": {}}, f)
            path = Path(f.name)
        try:
            history, seen = load_agent_state(path)
            self.assertEqual(history, {})
            self.assertEqual(seen, set())
        finally:
            path.unlink(missing_ok=True)

    def test_discovery_preloaded_state_skips_known_signatures(self):
        from zaa.discovery import DiscoveryConfig, run_discovery_loop

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)
        try:
            run_discovery_loop(DiscoveryConfig("synthetic_glider", cycles=3, state_file=str(path)))
            results2 = run_discovery_loop(DiscoveryConfig("synthetic_glider", cycles=1, state_file=str(path)))
            for r in results2:
                if r["analysis_status"] == "ok":
                    self.assertFalse(r["is_new_law_signature"])
        finally:
            path.unlink(missing_ok=True)

    def test_params_tried_recorded(self):
        history = {}
        sig = ("densidad_estable",)
        update_history(history, "rule_30", 2.0, "ok", sig, steps=48, width=64)
        record = history["rule_30"]
        self.assertEqual(len(record.params_tried), 1)
        self.assertEqual(record.params_tried[0], (48, 64, sig))

    def test_update_history_tracks_max_ok_steps(self):
        history = {}
        update_history(history, "rule_110", 2.0, "ok", steps=24, width=64)
        update_history(history, "rule_110", 1.0, "ok", steps=48, width=64)
        self.assertEqual(history["rule_110"].max_ok_steps, 48)

    def test_update_history_tracks_first_noise_steps(self):
        history = {}
        update_history(history, "rule_110", 0.0, "ruido_no_analizable", steps=48)
        update_history(history, "rule_110", 0.0, "ruido_no_analizable", steps=96)
        self.assertEqual(history["rule_110"].first_noise_steps, 48)

    def test_first_noise_steps_not_overwritten_by_larger(self):
        history = {}
        update_history(history, "rule_110", 0.0, "ruido_no_analizable", steps=96)
        update_history(history, "rule_110", 0.0, "ruido_no_analizable", steps=48)
        self.assertEqual(history["rule_110"].first_noise_steps, 48)

    def test_world_record_serializes_noise_boundary_fields(self):
        record = WorldRecord(max_ok_steps=24, first_noise_steps=48)
        data = record.to_dict()
        self.assertEqual(data["max_ok_steps"], 24)
        self.assertEqual(data["first_noise_steps"], 48)

    def test_load_agent_state_backward_compat_missing_fields(self):
        state = {
            "schema_version": 1,
            "seen_law_signatures": [],
            "world_history": {
                "rule_110": {
                    "visit_count": 1,
                    "scores": [2.0],
                    "noise_count": 0,
                    "law_signatures": [["densidad_estable"]],
                    "params_tried": [[24, 64, ["densidad_estable"]]],
                }
            },
        }
        with tempfile.NamedTemporaryFile(
            suffix=".json", delete=False, mode="w", encoding="utf-8"
        ) as handle:
            json.dump(state, handle)
            path = Path(handle.name)
        try:
            history, _ = load_agent_state(path)
            self.assertEqual(history["rule_110"].max_ok_steps, 0)
            self.assertEqual(history["rule_110"].first_noise_steps, 0)
        finally:
            path.unlink(missing_ok=True)

    def test_law_signature_diversity_requires_minimum_visits(self):
        record = WorldRecord(
            visit_count=4,
            law_signatures=[
                frozenset({"a"}),
                frozenset({"b"}),
                frozenset({"c"}),
                frozenset({"d"}),
            ],
        )
        self.assertIsNone(record.law_signature_diversity)
        self.assertFalse(record.is_multiregime_candidate)

    def test_law_signature_diversity_requires_minimum_non_empty_visits(self):
        record = WorldRecord(
            visit_count=8,
            law_signatures=[
                frozenset(),
                frozenset(),
                frozenset(),
                frozenset({"a"}),
                frozenset({"b"}),
                frozenset({"c"}),
                frozenset({"d"}),
                frozenset(),
            ],
        )
        self.assertEqual(record.non_empty_signature_visit_count, 4)
        self.assertEqual(record.unique_law_signature_count, 4)
        self.assertIsNone(record.law_signature_diversity)
        self.assertFalse(record.is_multiregime_candidate)

    def test_law_signature_diversity_counts_unique_signatures(self):
        record = WorldRecord(
            visit_count=5,
            law_signatures=[
                frozenset({"a"}),
                frozenset({"a"}),
                frozenset({"b"}),
                frozenset({"c"}),
                frozenset({"c"}),
            ],
        )
        self.assertEqual(record.unique_law_signature_count, 3)
        self.assertAlmostEqual(record.law_signature_diversity, 3 / 5)

    def test_law_signature_diversity_ignores_empty_signatures(self):
        record = WorldRecord(
            visit_count=8,
            law_signatures=[
                frozenset(),
                frozenset({"a"}),
                frozenset({"a"}),
                frozenset({"b"}),
                frozenset({"c"}),
                frozenset({"c"}),
                frozenset(),
                frozenset({"d"}),
            ],
        )
        self.assertEqual(record.non_empty_signature_visit_count, 6)
        self.assertEqual(record.unique_law_signature_count, 4)
        self.assertAlmostEqual(record.law_signature_diversity, 4 / 6)

    def test_empty_signatures_do_not_trigger_multiregime_evidence(self):
        history = {}
        for _ in range(8):
            update_history(history, "rule_90", 0.0, "ok", ())
        record = history["rule_90"]
        self.assertEqual(record.non_empty_signature_visit_count, 0)
        self.assertEqual(record.unique_law_signature_count, 0)
        self.assertIsNone(record.law_signature_diversity)
        self.assertFalse(record.is_multiregime_candidate)
        self.assertFalse(record.has_multiregime_evidence)
        self.assertEqual(record.peak_signature_diversity, 0.0)

    def test_repeated_single_non_empty_signature_is_not_multiregime(self):
        history = {}
        for _ in range(5):
            update_history(history, "rule_90", 1.0, "ok", ("velocidad_constante",))
        for _ in range(3):
            update_history(history, "rule_90", 0.0, "ok", ())
        record = history["rule_90"]
        self.assertEqual(record.non_empty_signature_visit_count, 5)
        self.assertEqual(record.unique_law_signature_count, 1)
        self.assertAlmostEqual(record.law_signature_diversity, 1 / 5)
        self.assertFalse(record.is_multiregime_candidate)
        self.assertFalse(record.has_multiregime_evidence)

    def test_multiregime_candidate_requires_diversity_noise_and_visits(self):
        record = WorldRecord(
            visit_count=5,
            scores=[1.0, 2.0, 3.0, 4.0, 5.0],
            noise_count=0,
            law_signatures=[
                frozenset({"a"}),
                frozenset({"b"}),
                frozenset({"c"}),
                frozenset({"d"}),
                frozenset({"d"}),
            ],
        )
        self.assertTrue(record.is_multiregime_candidate)

        noisy = WorldRecord(
            visit_count=5,
            noise_count=1,
            law_signatures=record.law_signatures,
        )
        self.assertFalse(noisy.is_multiregime_candidate)

    def test_score_variance_requires_at_least_two_scores(self):
        self.assertIsNone(WorldRecord(scores=[1.0]).score_variance)
        record = WorldRecord(scores=[1.0, 3.0])
        self.assertAlmostEqual(record.score_variance, 1.0)

    def test_multiregime_evidence_locks_once_detected(self):
        history = {}
        signatures = [
            ("a",),
            ("b",),
            ("c",),
            ("d",),
            ("d",),
        ]
        for sig in signatures:
            update_history(history, "rule_137", 3.0, "ok", sig)

        record = history["rule_137"]
        self.assertTrue(record.has_multiregime_evidence)
        self.assertAlmostEqual(record.peak_signature_diversity, 4 / 5)

        for _ in range(5):
            update_history(history, "rule_137", 3.0, "ok", ("d",))

        self.assertTrue(record.has_multiregime_evidence)
        self.assertAlmostEqual(record.peak_signature_diversity, 4 / 5)
        self.assertLess(record.law_signature_diversity, 0.5)

    def test_multiregime_evidence_requires_low_noise(self):
        history = {}
        updates = [
            ("ok", ("a",)),
            ("ruido_no_analizable", ()),
            ("ok", ("b",)),
            ("ok", ("c",)),
            ("ok", ("d",)),
        ]
        for status, sig in updates:
            update_history(history, "rule_54", 1.0, status, sig)

        record = history["rule_54"]
        self.assertFalse(record.has_multiregime_evidence)
        self.assertEqual(record.peak_signature_diversity, 0.0)

    def test_save_load_roundtrip_multiregime_evidence(self):
        history = {
            "rule_137": WorldRecord(
                visit_count=5,
                scores=[1.0, 2.0, 3.0, 4.0, 5.0],
                law_signatures=[
                    frozenset({"a"}),
                    frozenset({"b"}),
                    frozenset({"c"}),
                    frozenset({"d"}),
                    frozenset({"d"}),
                ],
                peak_signature_diversity=0.8,
                has_multiregime_evidence=True,
            )
        }
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as handle:
            path = Path(handle.name)
        try:
            save_agent_state(history, set(), path)
            loaded, _ = load_agent_state(path)
            self.assertTrue(loaded["rule_137"].has_multiregime_evidence)
            self.assertAlmostEqual(loaded["rule_137"].peak_signature_diversity, 0.8)
        finally:
            path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
