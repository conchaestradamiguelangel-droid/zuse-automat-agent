import unittest

from zaa.history import WorldRecord, update_history


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


if __name__ == "__main__":
    unittest.main()
