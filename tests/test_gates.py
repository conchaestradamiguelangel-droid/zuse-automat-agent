import unittest

from zaa.gates import evaluate_g1a1


class GateTests(unittest.TestCase):
    def test_g1a1_report_shape(self):
        report = evaluate_g1a1("fixtures/validated")
        self.assertEqual(report["gate"], "G1a.1")
        self.assertIn("passed", report)
        self.assertIn("results", report)
        self.assertGreaterEqual(len(report["results"]), 3)


if __name__ == "__main__":
    unittest.main()
