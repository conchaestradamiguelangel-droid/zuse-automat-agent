from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase105_minimal_rescue_motifs.py"
DECODER = ROOT / "outputs" / "periodic_backgrounds" / "decode_phase105_minimal_rescue_motif_ledger.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase106 = load_module("test_phase106_module", SCRIPT)
decoder = load_module("test_phase106_decoder", DECODER)


class Phase106MinimalRescueMotifTests(unittest.TestCase):
    def assert_motif(self, words, expected):
        self.assertEqual(phase106.classify_motif(words)["motif"], expected)

    def test_exact_motif_catalog(self):
        self.assert_motif((0, 3), "2I")
        self.assert_motif((0, 1), "K2")
        self.assert_motif((0, 3, 12), "3I")
        self.assert_motif((0, 1, 12), "K2+I")
        self.assert_motif((0, 1, 3), "P3")
        self.assert_motif((0, 3, 12, 48), "4I")
        self.assert_motif((0, 1, 12, 48), "K2+2I")
        self.assert_motif((0, 1, 12, 13), "2K2")
        self.assert_motif((0, 1, 3, 48), "P3+I")
        self.assert_motif((0, 1, 3, 7), "P4")
        self.assert_motif((0, 1, 2, 4), "K1_3")
        self.assert_motif((0, 1, 2, 3), "C4")

    def test_isomorphism_is_permutation_invariant(self):
        words = (0, 1, 3, 7)
        signatures = {
            phase106.classify_motif(permutation)["canonical_adjacency_mask"]
            for permutation in __import__("itertools").permutations(words)
        }
        self.assertEqual(len(signatures), 1)

    def test_edge_count_does_not_merge_nonisomorphic_motifs(self):
        self.assertEqual(phase106.classify_motif((0, 1, 12, 13))["edge_count"], 2)
        self.assertEqual(phase106.classify_motif((0, 1, 3, 48))["edge_count"], 2)
        self.assertNotEqual(
            phase106.classify_motif((0, 1, 12, 13))["motif"],
            phase106.classify_motif((0, 1, 3, 48))["motif"],
        )
        self.assertEqual(phase106.classify_motif((0, 1, 3, 7))["edge_count"], 3)
        self.assertEqual(phase106.classify_motif((0, 1, 2, 4))["edge_count"], 3)
        self.assertNotEqual(
            phase106.classify_motif((0, 1, 3, 7))["motif"],
            phase106.classify_motif((0, 1, 2, 4))["motif"],
        )

    def test_non_q8_triangle_is_rejected(self):
        triangle_mask = 0b111
        with self.assertRaisesRegex(RuntimeError, "Unclassified"):
            key = (3, *phase106.graph_invariants(triangle_mask, 3))
            motif = phase106.INVARIANT_TO_MOTIF.get(key)
            if motif is None:
                raise RuntimeError("Unclassified or non-Q8 motif")

    def test_geometry_record_roundtrip_and_reserved_bit(self):
        value = phase106.pack_geometry(phase106.MOTIF_IDS["C4"], 4)
        self.assertEqual(phase106.unpack_geometry(value)["motif"], "C4")
        manifest = {"motif_ids": phase106.MOTIF_IDS}
        self.assertEqual(decoder.decode_byte(value, manifest)["internal_edge_count"], 4)
        with self.assertRaisesRegex(ValueError, "Reserved"):
            decoder.decode_byte(value | 0x80, manifest)

    def test_cut_mechanisms_are_mutually_exclusive(self):
        individual = [[True, False, False, False], [False, False, False, False]]
        external = [True, True, False, False]
        full = [True, True, True, False]
        self.assertEqual(
            phase106.classify_cut_mechanisms(individual, external, full),
            ["INDIVIDUAL", "DISTRIBUTED_EXTERNAL", "INTERNAL_EDGE_ENABLED", "UNCOVERED"],
        )

    def test_add_words_can_remove_only_internal_edges(self):
        base = {0: {1}, 1: {0}}
        full, _new_full, internal = phase106.add_words(base, (2, 3), internal_edges=True)
        external, _new_external, _ = phase106.add_words(base, (2, 3), internal_edges=False)
        self.assertIn((2, 3), internal)
        self.assertIn(3, full[2])
        self.assertNotIn(3, external[2])
        self.assertEqual(full[2] - {3}, external[2])

    def test_internal_edge_audit_reports_each_removal_explicitly(self):
        phase102 = phase106.load_phase102_module()
        context = {
            "adjacency": {0: {1}, 1: {0, 3}, 3: {1, 7}, 7: {3}},
            "component_a": {0},
            "component_b": {7},
            "critical_vertices": (1, 3),
            "critical_edges": ((0, 1), (1, 3), (3, 7)),
        }
        for metric in ("kappa", "lambda"):
            audit = phase106.audit_rescue_set(phase102, context, (2, 6), metric)
            self.assertTrue(audit["full_rescue"])
            self.assertFalse(audit["external_rescue"])
            self.assertEqual(audit["mechanism_label"], "INTERNAL_EDGE_DEPENDENT_RESCUE")
            self.assertTrue(audit["internal_edge_required"])
            self.assertEqual(len(audit["per_internal_edge_removal"]), 1)
            edge = audit["per_internal_edge_removal"][0]
            self.assertEqual(edge["edge"], [2, 6])
            self.assertEqual(edge["rescue"], edge["max_flow_rescue"])
            self.assertFalse(edge["rescue"])
            self.assertGreater(edge["uncovered_original_cut_count"], 0)

    def test_geometry_manifest_roundtrip(self):
        records = bytes(
            [
                phase106.pack_geometry(phase106.MOTIF_IDS["K2"], 1),
                phase106.pack_geometry(phase106.MOTIF_IDS["P3"], 2),
            ]
        )
        manifest = {
            "record_size": 1,
            "record_count": 2,
            "ledger_size": 2,
            "ledger_sha256": hashlib.sha256(records).hexdigest(),
            "motif_ids": phase106.MOTIF_IDS,
            "encoding": {},
            "segments": [
                {"cardinality": 2, "source_name": "PAIR", "stratum_index": 0, "geometry_record_offset": 0, "record_count": 1},
                {"cardinality": 3, "source_name": "TRIPLE", "stratum_index": 0, "geometry_record_offset": 1, "record_count": 1},
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ledger_path = root / "ledger.bin"
            manifest_path = root / "manifest.json"
            ledger_path.write_bytes(records)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            loaded = decoder.load_manifest(manifest_path)
            rows = list(decoder.decode_rows(ledger_path, loaded))
        self.assertEqual([row["motif"] for row in rows], ["K2", "P3"])

    def test_corrupt_geometry_ledger_is_rejected(self):
        manifest = {"ledger_size": 1, "ledger_sha256": "0" * 64}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.bin"
            path.write_bytes(b"\0")
            with self.assertRaisesRegex(ValueError, "SHA-256"):
                decoder.validate_ledger(path, manifest)

    def test_full_authorization_is_bound_to_benchmark(self):
        benchmark = {
            "status": "PASS",
            "workers": 5,
            "runner_sha256": phase106.normalized_source_sha256(SCRIPT),
            "full_record_count": phase106.EXPECTED_RECORD_COUNT,
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            benchmark_path = root / "benchmark.json"
            benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")
            digest = phase106.raw_sha256(benchmark_path)
            authorization_path = root / "authorization.json"
            authorization_path.write_text(
                json.dumps(
                    {
                        "authorization": f"Autorizo el barrido completo de Fase 106 con 5 workers, ligado al benchmark SHA-256 {digest}.",
                        "benchmark_report_sha256": digest,
                        "workers": 5,
                        "expected_record_count": phase106.EXPECTED_RECORD_COUNT,
                    }
                ),
                encoding="utf-8",
            )
            phase106.validate_full_authorization(authorization_path, benchmark_path, 5)

    def test_actual_preflight_reconciles_all_source_records(self):
        values = phase106.gate_inputs()
        tasks = phase106.build_tasks(values)
        self.assertEqual(sum(task["record_count"] for task in tasks), phase106.EXPECTED_RECORD_COUNT)
        self.assertEqual(
            {n: sum(task["record_count"] for task in tasks if task["cardinality"] == n) for n in (2, 3, 4)},
            {2: 404_054, 3: 3_061_466, 4: 24_362_850},
        )

    def test_out_of_scope_route_is_diagnostic_not_minimal_rescue(self):
        self.assertEqual(
            phase106.reconcile_metric_flags(
                scope=False, route_a=True, route_b=True, required=False
            ),
            "OUT_OF_SCOPE_DIAGNOSTIC",
        )
        with self.assertRaisesRegex(RuntimeError, "scope/route/requirement"):
            phase106.reconcile_metric_flags(
                scope=False, route_a=True, route_b=True, required=True
            )


if __name__ == "__main__":
    unittest.main()
