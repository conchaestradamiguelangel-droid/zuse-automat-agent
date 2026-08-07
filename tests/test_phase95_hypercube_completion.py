from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "periodic_backgrounds"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase95 = load(
    "test_phase95_module", OUT / "analyze_phase94_hypercube_completion.py"
)


class Phase95HypercubeTests(unittest.TestCase):
    def test_q8_has_exact_degree_and_edge_counts(self):
        edges = phase95.q8_edges()
        self.assertEqual(len(edges), 2048)
        degrees = {value: 0 for value in range(256)}
        undirected = set()
        for source, target, position in edges:
            degrees[source] += 1
            self.assertEqual((source ^ target).bit_count(), 1)
            self.assertIn(position, range(124, 132))
            undirected.add((min(source, target), max(source, target), position))
        self.assertEqual(set(degrees.values()), {8})
        self.assertEqual(len(undirected), 1024)

    def test_frozen_descriptor_denominators_are_explicit(self):
        self.assertEqual(phase95.EXPECTED_BASELINE_DESCRIPTOR_COUNT, 160)
        self.assertEqual(phase95.EXPECTED_PRIMITIVE_DESCRIPTOR_COUNT, 3136)
        self.assertEqual(
            phase95.EXPECTED_BASELINE_DESCRIPTOR_COUNT
            + phase95.EXPECTED_PRIMITIVE_DESCRIPTOR_COUNT,
            3296,
        )

    def test_q8_bit_order_matches_absolute_word_positions(self):
        self.assertEqual(phase95.q8_target(0, 124), 128)
        self.assertEqual(phase95.q8_target(0, 131), 1)
        self.assertEqual(phase95.q8_target(128, 124), 0)

    def test_fragmentation_labels_are_exclusive(self):
        self.assertEqual(
            phase95.fragmentation_label([1]), "CONNECTED_SINGLE_CUBE"
        )
        self.assertEqual(phase95.fragmentation_label([1, 1]), "CROSS_CUBE_ONLY")
        self.assertEqual(
            phase95.fragmentation_label([2]), "WITHIN_CUBE_FRAGMENTED"
        )
        self.assertEqual(phase95.fragmentation_label([1, 2]), "MIXED")

    def test_components_and_minimum_hamming(self):
        components = phase95.component_words({0, 1, 6, 7})
        self.assertEqual(components, [[0, 1], [6, 7]])
        self.assertEqual(phase95.minimum_component_hamming(components), 2)
        self.assertIsNone(phase95.minimum_component_hamming([[0, 1]]))

    def test_canonical_hash_ignores_json_layout(self):
        value = {"b": [2, 1], "a": True}
        pretty = json.loads(json.dumps(value, indent=2))
        compact = json.loads(json.dumps(value, separators=(",", ":")))
        self.assertEqual(
            phase95.canonical_sha256(pretty), phase95.canonical_sha256(compact)
        )

    def test_phase94_replay_gate_rejects_edge_mismatch(self):
        fake = {
            "edges": [{"outcome": "expected"}],
            "summary": {},
            "physical_classes": [],
            "class_graph": [],
        }
        with self.assertRaisesRegex(RuntimeError, "wrong replay edge count"):
            phase95.validate_phase94_replay(None, fake, {}, [])

    def test_exact_gate_rejects_one_field_difference(self):
        expected = [{"outcome": "SAME", "flip_position": 124}]
        observed = [{"outcome": "DIFFERENT", "flip_position": 124}]
        with self.assertRaisesRegex(RuntimeError, "edge row 0 differs"):
            phase95.require_exact("edge", observed, expected)


if __name__ == "__main__":
    unittest.main()
