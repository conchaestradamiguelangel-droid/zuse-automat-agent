import csv
import json
from pathlib import Path
import tempfile
import unittest

from zaa.dataset import METRIC_KEYS, build_dataset, build_sample, save_csv, save_jsonl


class DatasetTests(unittest.TestCase):
    def test_build_sample_has_required_keys(self):
        sample = build_sample("rule_110", 24, 64, 20260523)
        for key in (
            "world_type",
            "steps",
            "width",
            "seed",
            "analysis_status",
            "structure_count",
        ) + tuple(METRIC_KEYS):
            self.assertIn(key, sample)

    def test_build_sample_rule110_law_frontera_temporal_accepted(self):
        sample = build_sample("rule_110", 24, 64, 20260523)
        self.assertEqual(sample["analysis_status"], "ok")
        self.assertEqual(sample["law_frontera_temporal"], 1)

    def test_build_sample_rule30_law_frontera_temporal_rejected(self):
        sample = build_sample("rule_30", 24, 64, 20260523)
        self.assertEqual(sample["analysis_status"], "ok")
        self.assertEqual(sample["law_frontera_temporal"], 0)

    def test_build_dataset_correct_count(self):
        specs = [("rule_30", 24, 64), ("rule_110", 24, 64)]
        samples = build_dataset(specs, n_seeds=3, base_seed=20260523)
        self.assertEqual(len(samples), 6)

    def test_save_csv_roundtrip(self):
        samples = build_dataset([("synthetic_glider", 24, 64)], n_seeds=2)
        with tempfile.TemporaryDirectory() as tmp:
            path = save_csv(samples, Path(tmp) / "ds.csv")
            with path.open(encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 2)
        self.assertIn("world_type", rows[0])
        self.assertIn("transition_rate", rows[0])

    def test_save_jsonl_roundtrip(self):
        samples = build_dataset([("synthetic_bloque", 24, 64)], n_seeds=2)
        with tempfile.TemporaryDirectory() as tmp:
            path = save_jsonl(samples, Path(tmp) / "ds.jsonl")
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        row = json.loads(lines[0])
        self.assertEqual(row["world_type"], "synthetic_bloque")


if __name__ == "__main__":
    unittest.main()
