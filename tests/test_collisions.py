import unittest
from collections import Counter

from zaa.collisions import (
    Collision,
    collision_table,
    consistency_table,
    dominant_results,
    synthetic_collisions,
    validate_consistency,
)


class CollisionTests(unittest.TestCase):
    def test_collision_dataclass(self):
        event = Collision("glider", "bloque", "glider", t=12, x=33)
        self.assertEqual(event.tipo_a, "glider")
        self.assertEqual(event.tipo_b, "bloque")
        self.assertEqual(event.resultado, "glider")
        self.assertEqual(event.t, 12)
        self.assertEqual(event.x, 33)
        self.assertEqual(event.key, ("bloque", "glider"))

    def test_collision_table_groups_order_independently(self):
        events = [
            Collision("glider", "bloque", "glider", 1, 10),
            Collision("bloque", "glider", "glider", 2, 12),
            Collision("glider", "glider", "oscilador", 3, 14),
        ]
        table = collision_table(events)
        self.assertEqual(table[("bloque", "glider")], Counter({"glider": 2}))
        self.assertEqual(table[("glider", "glider")], Counter({"oscilador": 1}))

    def test_consistency_on_controlled_synthetic_data_exceeds_threshold(self):
        table = collision_table(synthetic_collisions(repetitions=25))
        consistency = consistency_table(table)
        self.assertTrue(consistency)
        for value in consistency.values():
            self.assertGreaterEqual(value, 0.95)
        validation = validate_consistency(table, threshold=0.95)
        self.assertTrue(all(validation.values()))

    def test_dominant_results(self):
        table = collision_table(synthetic_collisions(repetitions=3))
        dominant = dominant_results(table)
        self.assertEqual(dominant[("glider", "glider")][0], "oscilador")
        self.assertEqual(dominant[("bloque", "glider")][0], "glider")

    def test_inconsistent_table_fails_threshold(self):
        table = {
            ("glider", "glider"): Counter({"bloque": 9, "oscilador": 1}),
        }
        self.assertEqual(consistency_table(table)[("glider", "glider")], 0.9)
        self.assertFalse(validate_consistency(table, threshold=0.95)[("glider", "glider")])


if __name__ == "__main__":
    unittest.main()
