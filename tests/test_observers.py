import unittest

from zaa.consensus import consensus_by_type, dominant_type
from zaa.observers import run_observers
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


if __name__ == "__main__":
    unittest.main()
