from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase103_triple_synergy.py"
DECODER = ROOT / "outputs" / "periodic_backgrounds" / "decode_phase103_triple_synergy_ledger.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase104 = load_module("test_phase104_module", SCRIPT)
decoder = load_module("test_phase104_decoder", DECODER)


def adjacency(edges):
    nodes = {node for edge in edges for node in edge}
    graph = {node: set() for node in nodes}
    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
    return graph


class Phase104TripleSynergyTests(unittest.TestCase):
    def test_ledger_layout_is_ten_byte_little_endian(self):
        self.assertEqual(phase104.LEDGER_RECORD.size, 10)
        self.assertTrue(phase104.LEDGER_FORMAT.startswith("<"))
        self.assertEqual(
            [(field["offset"], field["width"]) for field in phase104.LEDGER_FIELDS],
            [(0, 2), (2, 1), (3, 1), (4, 1), (5, 2), (7, 1), (8, 1), (9, 1)],
        )

    def test_flags_and_packed_separators_round_trip(self):
        flags = phase104.build_flags(
            {"kappa_scope": True, "kappa_route_b_rescue": True}, 2
        )
        packed = phase104.pack_separators(0b101, 17)
        raw = phase104.LEDGER_RECORD.pack(7, 11, 13, 29, flags, 2, 3, packed)
        manifest = {
            "byte_order": "little-endian",
            "record_format": phase104.LEDGER_FORMAT,
            "record_size": phase104.LEDGER_RECORD.size,
            "record_count": 1,
            "ledger_size": len(raw),
            "ledger_sha256": hashlib.sha256(raw).hexdigest(),
            "fields": phase104.LEDGER_FIELDS,
            "flag_bits": phase104.FLAG_BITS,
            "packed_new_separators": {},
            "internal_edge_count_bits": "flags bits 0..1",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.bin"
            path.write_bytes(raw)
            row = next(decoder.decode_rows(path, manifest))
        self.assertEqual(row["internal_edge_count"], 2)
        self.assertEqual(row["new_vertex_separator_mask"], 0b101)
        self.assertEqual(row["new_edge_separator_count"], 17)
        self.assertTrue(row["decoded_flags"]["kappa_scope"])
        self.assertTrue(row["decoded_flags"]["kappa_route_b_rescue"])

    def test_decoder_rejects_corrupt_ledger(self):
        raw = phase104.LEDGER_RECORD.pack(0, 1, 2, 3, 0, 0, 0, 0)
        manifest = {
            "byte_order": "little-endian",
            "record_format": phase104.LEDGER_FORMAT,
            "record_size": 10,
            "record_count": 1,
            "ledger_size": 10,
            "ledger_sha256": "0" * 64,
            "fields": phase104.LEDGER_FIELDS,
            "flag_bits": phase104.FLAG_BITS,
            "packed_new_separators": {},
            "internal_edge_count_bits": "flags bits 0..1",
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.bin"
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                list(decoder.decode_rows(path, manifest))

    def test_three_nodes_can_rescue_when_all_pairs_fail(self):
        base = adjacency([(0, 1), (1, 2), (2, 3)])
        full = adjacency(
            [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6), (6, 3)]
        )
        self.assertTrue(phase104.phase103.vertex_connectivity_two(full, {0}, {3}))
        self.assertTrue(phase104.phase103.edge_connectivity_two(full, {0}, {3}))
        for subset in ((4,), (5,), (6,), (4, 5), (4, 6), (5, 6)):
            allowed = set(base) | set(subset)
            reduced = {
                node: {target for target in full[node] if target in allowed}
                for node in allowed
            }
            self.assertFalse(
                phase104.phase103.vertex_connectivity_two(reduced, {0}, {3})
            )
            self.assertFalse(
                phase104.phase103.edge_connectivity_two(reduced, {0}, {3})
            )

    def test_internal_edge_can_be_required(self):
        graph = adjacency(
            [(0, 1), (1, 2), (2, 3), (0, 4), (4, 5), (5, 6), (6, 3)]
        )
        self.assertTrue(
            phase104.internal_edge_required(
                graph, {0}, {3}, ((4, 5), (5, 6)), metric=phase104.KAPPA, rescue=True
            )
        )
        self.assertTrue(
            phase104.internal_edge_required(
                graph, {0}, {3}, ((4, 5), (5, 6)), metric=phase104.LAMBDA, rescue=True
            )
        )

    def test_q8_contains_no_three_mutual_edges(self):
        for triple in itertools.combinations(range(16), 3):
            internal = sum((left ^ right).bit_count() == 1 for left, right in itertools.combinations(triple, 2))
            self.assertLess(internal, 3)

    def test_minimal_labels_keep_metric_scope_separate(self):
        self.assertEqual(phase104.triple_minimal_label(True, 1), "EXACTLY_3")
        self.assertEqual(phase104.triple_minimal_label(True, 0), "AT_LEAST_4")
        self.assertEqual(
            phase104.triple_minimal_label(False, 4),
            "NOT_APPLICABLE_NOT_AT_LEAST_THREE",
        )

    def test_out_of_scope_metric_bits_default_false(self):
        flags = phase104.build_flags({"kappa_scope": False, "lambda_scope": True}, 0)
        decoded = decoder.decode_flags(flags, phase104.FLAG_BITS)
        for name in (
            "kappa_route_a_rescue",
            "kappa_route_b_rescue",
            "distributed_vertex_coverage",
            "internal_edge_required_kappa",
            "three_node_vertex_coverage",
        ):
            self.assertFalse(decoded[name])

    def test_committed_aggregate_dimensions_reconcile(self):
        results_path = (
            ROOT
            / "outputs"
            / "periodic_backgrounds"
            / "phase103_triple_synergy_results.json"
        )
        if not results_path.exists():
            self.skipTest("Fase-104 results are not materialized")
        results = json.loads(results_path.read_text(encoding="utf-8"))
        summary = results["summary"]
        self.assertEqual(sum(summary["kappa_rescues_by_period"].values()), 180)
        self.assertEqual(sum(summary["lambda_rescues_by_period"].values()), 192)
        self.assertEqual(sum(summary["kappa_rescues_by_rule"].values()), 180)
        self.assertEqual(sum(summary["lambda_rescues_by_rule"].values()), 192)
        self.assertEqual(
            sum(summary["kappa_rescues_by_internal_edge_count"].values()), 180
        )
        self.assertEqual(
            sum(summary["lambda_rescues_by_internal_edge_count"].values()), 192
        )


if __name__ == "__main__":
    unittest.main()
