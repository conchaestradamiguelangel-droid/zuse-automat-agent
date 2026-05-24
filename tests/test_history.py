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
        self.assertEqual(history["synthetic_glider"].law_signatures[0], sig)

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
            results2 = run_discovery_loop(DiscoveryConfig("synthetic_glider", cycles=3, state_file=str(path)))
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


if __name__ == "__main__":
    unittest.main()
