import unittest

from zaa.consensus import consensus_by_type, dominant_type
from zaa.observers import filter_structures_by_start_frame, run_observers
from zaa.structures import Estructura
from zaa.synthetic import moving_point, oscillator, static_block


class ObserverTests(unittest.TestCase):
    def test_moving_point_has_glider_consensus(self):
        structures = run_observers(moving_point())
        consensus = consensus_by_type(structures)
        self.assertTrue(consensus.get("glider", False))
        self.assertEqual(dominant_type(structures), "glider")

    def test_static_block_has_block_consensus(self):
        structures = run_observers(static_block())
        consensus = consensus_by_type(structures)
        self.assertTrue(consensus.get("bloque", False))
        self.assertEqual(dominant_type(structures), "bloque")

    def test_oscillator_has_oscillator_consensus(self):
        structures = run_observers(oscillator())
        consensus = consensus_by_type(structures)
        self.assertTrue(consensus.get("oscilador", False))
        self.assertEqual(dominant_type(structures), "oscilador")

    def test_period3_oscillator_has_oscillator_consensus(self):
        import numpy as np

        frames = np.zeros((18, 32), dtype=np.uint8)
        for t in range(frames.shape[0]):
            frames[t, 14 + (t % 3)] = 1
        structures = run_observers(frames)
        consensus = consensus_by_type(structures)
        self.assertTrue(consensus.get("oscilador", False))

    def test_structure_contract_fields(self):
        structures = run_observers(moving_point())
        structure = structures[0]
        data = structure.to_dict()
        self.assertIn("tipo", data)
        self.assertIn("tipo_asignado_por", data)
        self.assertIn("posiciones", data)
        self.assertIn("confianza", data)
        self.assertIn("observador", data)
        self.assertEqual(len(structure.posiciones[0]), 3)

    def test_filter_structures_by_start_frame_filters_late_births(self):
        early = Estructura(0, "glider", "test", ((2, 3, 0),), 1, 1.0, "test")
        late = Estructura(1, "glider", "test", ((8, 3, 0),), 1, 1.0, "test")
        filtered = filter_structures_by_start_frame([early, late], 5)
        self.assertEqual(filtered, [early])

    def test_filter_structures_by_start_frame_preserves_original_objects(self):
        structures = [
            Estructura(0, "glider", "test", ((1, 3, 0),), 1, 1.0, "test"),
            Estructura(1, "bloque", "test", ((6, 3, 0),), 1, 1.0, "test"),
        ]
        filtered = filter_structures_by_start_frame(structures, 5)
        self.assertIs(filtered[0], structures[0])
        self.assertEqual(len(structures), 2)

    def test_filter_structures_by_start_frame_zero_returns_empty(self):
        structures = [Estructura(0, "glider", "test", ((0, 3, 0),), 1, 1.0, "test")]
        self.assertEqual(filter_structures_by_start_frame(structures, 0), [])


if __name__ == "__main__":
    unittest.main()
