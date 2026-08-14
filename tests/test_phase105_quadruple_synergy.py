from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase104_quadruple_synergy.py"
DECODER = ROOT / "outputs" / "periodic_backgrounds" / "decode_phase104_quadruple_synergy_ledger.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase105 = load_module("test_phase105_module", SCRIPT)
decoder = load_module("test_phase105_decoder", DECODER)


def adjacency(edges):
    nodes = {node for edge in edges for node in edge}
    graph = {node: set() for node in nodes}
    for left, right in edges:
        graph[left].add(right)
        graph[right].add(left)
    return graph


class Phase105QuadrupleSynergyTests(unittest.TestCase):
    def test_ledger_is_two_byte_little_endian(self):
        self.assertEqual(phase105.LEDGER_RECORD.size, 2)
        self.assertEqual(phase105.LEDGER_FORMAT, "<H")
        self.assertEqual(phase105.EXPECTED_QUARTET_COUNT * 2, 48_725_700)

    def test_flags_keep_scopes_and_routes_separate(self):
        mask = phase105.build_flags(
            {
                "kappa_scope": True,
                "lambda_scope": False,
                "kappa_route_a_rescue": True,
                "kappa_route_b_rescue": True,
            },
            4,
        )
        manifest = {
            "flag_bits": phase105.FLAG_BITS,
            "reserved_bits": list(phase105.RESERVED_BITS),
        }
        decoded = decoder.decode_flags(mask, manifest)
        self.assertEqual(decoded["internal_edge_count"], 4)
        self.assertTrue(decoded["kappa_scope"])
        self.assertFalse(decoded["lambda_scope"])
        self.assertTrue(decoded["kappa_route_a_rescue"])
        self.assertTrue(decoded["kappa_route_b_rescue"])
        self.assertFalse(decoded["reserved_bits_nonzero"])

    def test_q8_four_cycle_has_four_internal_edges(self):
        quartet = (0, 1, 2, 3)
        internal = sum(
            (left ^ right).bit_count() == 1
            for left, right in itertools.combinations(quartet, 2)
        )
        self.assertEqual(internal, 4)

    def test_four_nodes_can_be_minimal_rescue(self):
        full = adjacency(
            [
                (0, 1),
                (1, 2),
                (2, 3),
                (0, 4),
                (4, 5),
                (5, 6),
                (6, 7),
                (7, 3),
            ]
        )
        self.assertTrue(phase105.phase104.phase103.vertex_connectivity_two(full, {0}, {3}))
        self.assertTrue(phase105.phase104.phase103.edge_connectivity_two(full, {0}, {3}))
        for subset in itertools.chain.from_iterable(
            itertools.combinations((4, 5, 6, 7), size) for size in range(4)
        ):
            allowed = {0, 1, 2, 3, *subset}
            reduced = {
                node: {target for target in full[node] if target in allowed}
                for node in allowed
            }
            self.assertFalse(
                phase105.phase104.phase103.vertex_connectivity_two(reduced, {0}, {3})
            )
            self.assertFalse(
                phase105.phase104.phase103.edge_connectivity_two(reduced, {0}, {3})
            )

    def test_minimal_labels_are_metric_scoped(self):
        self.assertEqual(phase105.minimal_label(True, 1), "EXACTLY_4")
        self.assertEqual(phase105.minimal_label(True, 0), "AT_LEAST_5")
        self.assertEqual(
            phase105.minimal_label(False, 10),
            "NOT_APPLICABLE_NOT_AT_LEAST_FOUR",
        )

    def test_manifest_roundtrip_uses_ordered_words_and_hash(self):
        words = [1, 3, 7, 15, 31]
        records = list(itertools.combinations(words, 4))
        raw = b"".join(phase105.LEDGER_RECORD.pack(index) for index in range(len(records)))
        manifest = {
            "byte_order": "little-endian",
            "record_format": "<H",
            "record_size": 2,
            "record_count": len(records),
            "ledger_size": len(raw),
            "ledger_sha256": hashlib.sha256(raw).hexdigest(),
            "flag_bits": phase105.FLAG_BITS,
            "reserved_bits": list(phase105.RESERVED_BITS),
            "segments": [
                {
                    "stratum_index": 0,
                    "record_offset": 0,
                    "record_count": len(records),
                    "ordered_words": words,
                    "ordered_words_sha256": decoder.canonical_words_sha256(words),
                }
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            ledger = Path(directory) / "ledger.bin"
            ledger.write_bytes(raw)
            decoded = list(decoder.decode_rows(ledger, manifest))
        self.assertEqual([tuple(row["quartet"]) for row in decoded], records)

    def test_manifest_rejects_silent_word_reordering(self):
        words = [1, 3, 7, 15]
        manifest = {
            "record_count": 1,
            "segments": [
                {
                    "stratum_index": 0,
                    "record_offset": 0,
                    "record_count": 1,
                    "ordered_words": list(reversed(words)),
                    "ordered_words_sha256": decoder.canonical_words_sha256(words),
                }
            ],
        }
        with self.assertRaisesRegex(ValueError, "sorted unique"):
            decoder.validate_segments(manifest)

    def test_actual_phase95_historical_words_match_manifest_policy(self):
        phase95 = json.loads(phase105.PHASE95_PATH.read_text(encoding="utf-8"))
        phase104_results = json.loads(
            phase105.PHASE104_RESULTS_PATH.read_text(encoding="utf-8")
        )
        source = next(
            row
            for row in phase104_results["strata"]
            if row["kappa_minimal_cardinality"] == phase105.AT_LEAST_FOUR
            or row["lambda_minimal_cardinality"] == phase105.AT_LEAST_FOUR
        )
        cube = next(
            row for row in phase95["cube_nodes"] if row["cube_key"] == source["cube_key"]
        )
        words = phase105.historical_words_for(cube, int(source["period"]))
        independent = tuple(
            index
            for index, node in enumerate(cube["nodes"])
            if node["category"] == phase105.HISTORICAL_CATEGORY
            and node.get("ledger") is not None
            and int(node["ledger"]["source_period"]) == int(source["period"])
        )
        self.assertEqual(words, independent)
        self.assertEqual(len(words), int(source["node_count"]))
        self.assertEqual(
            phase105.ordered_words_sha256(words),
            decoder.canonical_words_sha256(list(independent)),
        )

    def test_corrupt_ledger_is_rejected(self):
        raw = struct.pack("<H", 0)
        manifest = {
            "record_size": 2,
            "record_count": 1,
            "ledger_size": 2,
            "ledger_sha256": "0" * 64,
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.bin"
            path.write_bytes(raw)
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                decoder.validate_ledger(path, manifest)

    def test_full_authorization_rejects_wrong_phrase(self):
        benchmark = {
            "status": "PASS",
            "workers": 5,
            "runner_sha256": phase105.normalized_source_sha256(
                phase105.Path(phase105.__file__)
            ),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            benchmark_path = root / "benchmark.json"
            benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")
            authorization_path = root / "authorization.json"
            authorization_path.write_text(
                json.dumps(
                    {
                        "authorization": "NO AUTORIZADO",
                        "benchmark_report_sha256": phase105.raw_sha256(benchmark_path),
                        "workers": 5,
                        "expected_record_count": phase105.EXPECTED_QUARTET_COUNT,
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(RuntimeError, "text mismatch"):
                phase105.validate_full_authorization(
                    authorization_path, benchmark_path, 5
                )
            self.assertTrue(authorization_path.exists())

    def test_normalized_runner_hash_ignores_line_endings(self):
        with tempfile.TemporaryDirectory() as directory:
            left = Path(directory) / "left.py"
            right = Path(directory) / "right.py"
            left.write_bytes(b"print('x')\nprint('y')\n")
            right.write_bytes(b"print('x')\r\nprint('y')\r\n")
            self.assertEqual(
                phase105.normalized_source_sha256(left),
                phase105.normalized_source_sha256(right),
            )

    def test_checkpoint_roundtrip_is_tied_to_words_and_runner(self):
        task = {
            "stratum_index": 0,
            "phase104_stratum_index": 0,
            "cube_key": "synthetic",
            "pair_index": 1,
            "period": 3,
            "historical_words": (1, 2, 3, 4),
            "ordered_words_sha256": phase105.ordered_words_sha256((1, 2, 3, 4)),
            "kappa_scope": True,
            "lambda_scope": True,
        }
        row = {
            "stratum_index": 0,
            "processed": 1,
            "ledger": phase105.LEDGER_RECORD.pack(0),
            "distribution": {0: 1},
            "kappa_rescues": {},
            "lambda_rescues": {},
            "required_kappa": 0,
            "required_lambda": 0,
            "kappa_examples": [],
            "lambda_examples": [],
        }
        original = phase105.FULL_CHECKPOINT_DIR
        with tempfile.TemporaryDirectory() as directory:
            phase105.FULL_CHECKPOINT_DIR = Path(directory)
            try:
                phase105.save_checkpoint(task, row)
                loaded = phase105.load_checkpoint(task)
            finally:
                phase105.FULL_CHECKPOINT_DIR = original
        self.assertEqual(loaded["ledger"], row["ledger"])
        self.assertEqual(loaded["processed"], 1)


if __name__ == "__main__":
    unittest.main()
