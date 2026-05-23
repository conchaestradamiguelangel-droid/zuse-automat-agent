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
            "dominant_type",
            "consensus",
            "metrics",
            "timestamp",
        ]:
            self.assertIn(key, result)

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


if __name__ == "__main__":
    unittest.main()
