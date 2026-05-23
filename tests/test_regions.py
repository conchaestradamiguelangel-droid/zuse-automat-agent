import unittest

from zaa.ether import diff_from_pure_ether
from zaa.fixtures import load_fixture
from zaa.gates import evaluate_g1a1
from zaa.observers import find_connected_regions_1d, observar_regiones_rule110, track_regions_1d


class RegionTrackerTests(unittest.TestCase):
    def test_find_connected_regions_1d(self):
        regions = find_connected_regions_1d([0, 1, 1, 0, 1, 0])
        self.assertEqual(len(regions), 2)
        self.assertEqual(regions[0]["center_x"], 2)
        self.assertEqual(regions[0]["width"], 2)
        self.assertEqual(regions[0]["cells"], [1, 2])
        self.assertEqual(regions[1]["center_x"], 4)
        self.assertEqual(regions[1]["width"], 1)
        self.assertEqual(regions[1]["cells"], [4])

    def test_track_regions_on_fix_a_is_compact(self):
        fixture = load_fixture("fixtures/validated/FIX-A.npz")
        tracks = track_regions_1d(diff_from_pure_ether(fixture["frames_esperados"]))
        self.assertLessEqual(len(tracks), 5)

    def test_observar_regiones_rule110_emits_structures(self):
        fixture = load_fixture("fixtures/validated/FIX-A.npz")
        structures = observar_regiones_rule110(fixture["frames_esperados"])
        self.assertTrue(structures)
        self.assertLessEqual(len(structures), 5)
        self.assertTrue(all(structure.observador == "regiones_rule110" for structure in structures))

    def test_g1a1_coherent_for_required_fixtures(self):
        report = evaluate_g1a1("fixtures/validated")
        by_id = {item["fixture_id"]: item for item in report["results"]}
        self.assertTrue(by_id["FIX-A"]["coherent_detection"])
        self.assertTrue(by_id["FIX-C1"]["coherent_detection"])


if __name__ == "__main__":
    unittest.main()
