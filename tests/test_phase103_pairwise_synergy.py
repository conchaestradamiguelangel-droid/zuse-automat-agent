from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "outputs"
    / "periodic_backgrounds"
    / "analyze_phase102_pairwise_synergy.py"
)
DECODER = (
    ROOT
    / "outputs"
    / "periodic_backgrounds"
    / "decode_phase102_pairwise_synergy_ledger.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase103 = load_module("test_phase103_module", SCRIPT)
decoder = load_module("test_phase103_decoder", DECODER)


def adjacency(edges):
    nodes = {node for edge in edges for node in edge}
    graph = {node: set() for node in nodes}
    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
    return graph


class Phase103PairwiseSynergyTests(unittest.TestCase):
    def test_ledger_layout_is_ten_byte_little_endian(self):
        self.assertEqual(phase103.LEDGER_RECORD.size, 10)
        self.assertTrue(phase103.LEDGER_FORMAT.startswith("<"))
        self.assertEqual(
            [(field["offset"], field["width"]) for field in phase103.LEDGER_FIELDS],
            [(0, 2), (2, 1), (3, 1), (4, 2), (6, 1), (7, 1), (8, 1), (9, 1)],
        )

    def test_flag_mask_round_trip(self):
        values = {
            "adjacent_pair": True,
            "kappa_collective_scope": True,
            "lambda_route_b_rescue": True,
            "distributed_edge_coverage": True,
        }
        mask = phase103.flag_mask(values)
        decoded = decoder.decode_flags(mask, phase103.FLAG_BITS)
        for name in phase103.FLAG_BITS:
            self.assertEqual(decoded[name], values.get(name, False))

    def test_decoder_round_trip_uses_manifest_schema(self):
        flags = phase103.flag_mask(
            {"adjacent_pair": True, "kappa_route_b_rescue": True}
        )
        raw = phase103.LEDGER_RECORD.pack(7, 13, 29, flags, 2, 3, 1, 4)
        manifest = {
            "byte_order": "little-endian",
            "record_format": phase103.LEDGER_FORMAT,
            "record_size": phase103.LEDGER_RECORD.size,
            "record_count": 1,
            "ledger_size": len(raw),
            "ledger_sha256": hashlib.sha256(raw).hexdigest(),
            "fields": phase103.LEDGER_FIELDS,
            "flag_bits": phase103.FLAG_BITS,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.bin"
            path.write_bytes(raw)
            row = next(decoder.decode_rows(path, manifest))
        self.assertEqual(row["stratum_index"], 7)
        self.assertEqual((row["left_word"], row["right_word"]), (13, 29))
        self.assertEqual(row["uncovered_original_vertices"], 2)
        self.assertTrue(row["decoded_flags"]["adjacent_pair"])
        self.assertTrue(row["decoded_flags"]["kappa_route_b_rescue"])

    def test_decoder_rejects_corrupt_ledger(self):
        raw = phase103.LEDGER_RECORD.pack(0, 1, 2, 0, 0, 0, 0, 0)
        manifest = {
            "byte_order": "little-endian",
            "record_format": phase103.LEDGER_FORMAT,
            "record_size": phase103.LEDGER_RECORD.size,
            "record_count": 1,
            "ledger_size": len(raw),
            "ledger_sha256": "0" * 64,
            "fields": phase103.LEDGER_FIELDS,
            "flag_bits": phase103.FLAG_BITS,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.bin"
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                list(decoder.decode_rows(path, manifest))

    def test_two_nodes_can_collectively_rescue_both_metrics(self):
        base = adjacency([(0, 1), (1, 2), (2, 3)])
        vertices, edges = phase103.enumerate_terminal_cuts(base, {0}, {3})
        augmented = adjacency(
            [
                (0, 1),
                (1, 2),
                (2, 3),
                (0, 4),
                (4, 2),
                (1, 5),
                (5, 3),
            ]
        )
        new_edges = ((0, 4), (2, 4), (1, 5), (3, 5))
        route_a = phase103.route_a_audit(
            augmented, {0}, {3}, vertices, edges, 4, 5, new_edges
        )
        self.assertTrue(route_a["kappa_rescue"])
        self.assertTrue(route_a["lambda_rescue"])
        self.assertTrue(phase103.vertex_connectivity_two(augmented, {0}, {3}))
        self.assertTrue(phase103.edge_connectivity_two(augmented, {0}, {3}))

    def test_mutual_edge_can_be_required_for_pair_rescue(self):
        base = adjacency([(0, 1), (1, 2), (2, 3)])
        augmented = adjacency(
            [
                (0, 1),
                (1, 2),
                (2, 3),
                (0, 4),
                (1, 4),
                (4, 5),
                (2, 5),
                (3, 5),
            ]
        )
        self.assertTrue(phase103.vertex_connectivity_two(augmented, {0}, {3}))
        self.assertTrue(phase103.edge_connectivity_two(augmented, {0}, {3}))
        without_mutual = phase103.remove_edge_copy(augmented, (4, 5))
        self.assertFalse(phase103.vertex_connectivity_two(without_mutual, {0}, {3}))
        self.assertFalse(phase103.edge_connectivity_two(without_mutual, {0}, {3}))

    def test_route_a_and_route_b_agree_when_pair_does_not_rescue(self):
        base = adjacency([(0, 1), (1, 2), (2, 3)])
        vertices, edges = phase103.enumerate_terminal_cuts(base, {0}, {3})
        augmented = adjacency([(0, 1), (1, 2), (2, 3), (0, 4), (1, 4), (2, 5), (3, 5)])
        route_a = phase103.route_a_audit(
            augmented,
            {0},
            {3},
            vertices,
            edges,
            4,
            5,
            ((0, 4), (1, 4), (2, 5), (3, 5)),
        )
        self.assertFalse(route_a["kappa_rescue"])
        self.assertFalse(route_a["lambda_rescue"])
        self.assertFalse(phase103.vertex_connectivity_two(augmented, {0}, {3}))
        self.assertFalse(phase103.edge_connectivity_two(augmented, {0}, {3}))

    def test_minimal_cardinality_labels_do_not_mix_scope(self):
        self.assertEqual(phase103.minimal_label(True, 3), "EXACTLY_2")
        self.assertEqual(phase103.minimal_label(True, 0), "AT_LEAST_3")
        self.assertEqual(
            phase103.minimal_label(False, 5), "NOT_APPLICABLE_NOT_COLLECTIVE"
        )

    def test_manifest_loader_rejects_non_little_endian_format(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(
                json.dumps(
                    {
                        "byte_order": "little-endian",
                        "record_format": ">HBBHBBBB",
                        "record_size": 10,
                        "record_count": 0,
                        "ledger_size": 0,
                        "ledger_sha256": hashlib.sha256(b"").hexdigest(),
                        "fields": phase103.LEDGER_FIELDS,
                        "flag_bits": phase103.FLAG_BITS,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "does not declare little-endian"):
                decoder.load_manifest(path)


if __name__ == "__main__":
    unittest.main()
