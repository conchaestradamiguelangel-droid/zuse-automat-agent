import unittest

from zaa.invariants import evaluate_all_fixture_laws, evaluate_fixture_laws, save_law_report


class InvariantTests(unittest.TestCase):
    def test_fixture_law_report_shape(self):
        report = evaluate_fixture_laws("fixtures/validated/FIX-A.npz")
        self.assertEqual(report["fixture_id"], "FIX-A")
        self.assertGreaterEqual(len(report["results"]), 4)

    def test_velocity_is_accepted_for_validated_fixtures(self):
        report = evaluate_all_fixture_laws("fixtures/validated")
        accepted = set(tuple(item) for item in report["accepted"])
        self.assertIn(("FIX-A", "velocidad_constante"), accepted)
        self.assertIn(("FIX-B", "velocidad_constante"), accepted)
        self.assertIn(("FIX-C1", "velocidad_constante"), accepted)

    def test_parity_is_not_forced(self):
        report = evaluate_all_fixture_laws("fixtures/validated")
        rejected = set(tuple(item) for item in report["rejected"])
        self.assertTrue(any(name == "paridad_total" for _, name in rejected))

    def test_save_law_report(self):
        import tempfile

        report = evaluate_all_fixture_laws("fixtures/validated")
        with tempfile.TemporaryDirectory() as tmp:
            saved = save_law_report(report, tmp)
            self.assertTrue(saved["json"].exists())
            self.assertTrue(saved["markdown"].exists())


if __name__ == "__main__":
    unittest.main()
