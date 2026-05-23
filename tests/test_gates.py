import unittest

from zaa.gates import evaluate_g1a1


class GateTests(unittest.TestCase):
    def test_g1a1_report_shape(self):
        report = evaluate_g1a1("fixtures/validated")
        self.assertEqual(report["gate"], "G1a.1")
        self.assertIn("passed", report)
        self.assertIn("results", report)
        self.assertGreaterEqual(len(report["results"]), 3)

    def test_g1a1_uses_defect_representation(self):
        report = evaluate_g1a1("fixtures/validated")
        for result in report["results"]:
            self.assertIn("defect_activity_ratio", result)
            self.assertGreater(result["defect_activity_ratio"], 0.0)
            self.assertIn("structure_count", result)
            self.assertIn("coherent_detection", result)
            self.assertIn("emitted_types", result)


if __name__ == "__main__":
    unittest.main()
