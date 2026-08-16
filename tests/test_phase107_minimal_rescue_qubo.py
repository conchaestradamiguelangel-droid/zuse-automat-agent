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
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase106_minimal_rescue_qubo.py"
DECODER = ROOT / "outputs" / "periodic_backgrounds" / "decode_phase106_minimal_rescue_qubo.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase107 = load_module("test_phase107_module", SCRIPT)
decoder = load_module("test_phase107_decoder", DECODER)


def synthetic_instance(words=(1, 2, 3), hyperedges=((1, 2), (2, 3))):
    return {
        "instance_key": "synthetic|0|2|kappa",
        "cube_key": "synthetic",
        "pair_index": 0,
        "period": 2,
        "metric": "kappa",
        "rule": 73,
        "background_index": 0,
        "source_stratum_index": 0,
        "cardinality": 2,
        "ordered_words": list(words),
        "hyperedges": [list(edge) for edge in hyperedges],
    }


class Phase107MinimalRescueQuboTests(unittest.TestCase):
    def test_hyperedge_identity_is_canonical(self):
        self.assertEqual(phase107.canonical_hyperedge((7, 1, 3), 3), (1, 3, 7))
        self.assertEqual(
            phase107.canonical_hyperedge((3, 7, 1), 3),
            phase107.canonical_hyperedge((7, 1, 3), 3),
        )
        with self.assertRaisesRegex(RuntimeError, "duplicate"):
            phase107.canonical_hyperedge((1, 1), 2)

    def test_exact_qubo_coefficients(self):
        model = phase107.build_qubo(synthetic_instance())
        coefficients = {(i, j): value for i, j, value in model["qubo_upper"]}
        self.assertEqual(model["constant"], 3)
        self.assertEqual([coefficients[(i, i)] for i in range(3)], [1, 1, 1])
        self.assertEqual(coefficients[(3, 3)], 3)
        self.assertEqual(coefficients[(4, 4)], 3)
        self.assertEqual(coefficients[(3, 4)], 6)
        self.assertEqual(coefficients[(0, 3)], -3)
        self.assertEqual(coefficients[(1, 3)], -3)
        self.assertNotIn((0, 1), coefficients)

    def test_factorized_and_expanded_match_exhaustively(self):
        model = phase107.build_qubo(synthetic_instance())
        ground = []
        for bits in itertools.product((0, 1), repeat=5):
            x = {index for index, value in enumerate(bits[:3]) if value}
            z = {index for index, value in enumerate(bits[3:]) if value}
            route_a = phase107.factorized_energy(model, x, z)
            route_b = phase107.expanded_energy(model, x, z)
            self.assertEqual(route_a, route_b)
            if route_a == model["ground_energy"]:
                ground.append(bits)
        self.assertEqual(len(ground), 2)
        self.assertEqual(sum(bits[3] for bits in ground), 1)
        self.assertEqual(sum(bits[4] for bits in ground), 1)

    def test_single_hyperedge_and_extra_candidate(self):
        model = phase107.build_qubo(synthetic_instance(words=(1, 2, 9), hyperedges=((1, 2),)))
        self.assertEqual(model["ground_state_degeneracy"], 1)
        self.assertEqual(phase107.factorized_energy(model, {0, 1}, {0}), 2)
        self.assertEqual(phase107.factorized_energy(model, {0, 1, 2}, {0}), 3)
        self.assertEqual(phase107.factorized_energy(model, set(), set()), 3)

    def test_overlapping_hyperedges_do_not_create_spurious_ground(self):
        model = phase107.build_qubo(synthetic_instance())
        self.assertGreater(phase107.factorized_energy(model, {0, 1, 2}, {0, 1}), 2)

    def test_decoder_roundtrip_and_hash_gate(self):
        model = phase107.build_qubo(synthetic_instance())
        payload = phase107.canonical_json_bytes(model) + b"\n"
        manifest = {
            "format": "canonical-jsonl-one-model-per-line",
            "integer_coefficients": True,
            "model_count": 1,
            "models_size": len(payload),
            "models_sha256": hashlib.sha256(payload).hexdigest(),
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            models_path = root / "models.jsonl"
            manifest_path = root / "manifest.json"
            models_path.write_bytes(payload)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            loaded = decoder.load_manifest(manifest_path)
            rows = list(decoder.iter_models(models_path, loaded))
            self.assertEqual(rows[0]["instance_key"], model["instance_key"])
            models_path.write_bytes(payload + b"x")
            with self.assertRaisesRegex(ValueError, "size"):
                list(decoder.iter_models(models_path, loaded))

    def test_authorization_is_bound_to_current_benchmark(self):
        benchmark = {
            "status": "PASS",
            "workers": 5,
            "runner_sha256": phase107.normalized_source_sha256(SCRIPT),
            "expected_instance_count": phase107.EXPECTED_INSTANCE_COUNT,
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            benchmark_path = root / "benchmark.json"
            benchmark_path.write_text(json.dumps(benchmark), encoding="utf-8")
            digest = phase107.raw_sha256(benchmark_path)
            authorization_path = root / "authorization.json"
            authorization_path.write_text(
                json.dumps(
                    {
                        "authorization": f"Autorizo la compilacion completa de Fase 107 con 5 workers, ligada al benchmark SHA-256 {digest}.",
                        "benchmark_report_sha256": digest,
                        "workers": 5,
                        "expected_instance_count": phase107.EXPECTED_INSTANCE_COUNT,
                    }
                ),
                encoding="utf-8",
            )
            phase107.validate_full_authorization(authorization_path, benchmark_path, 5)

    def test_actual_preflight_reconstructs_frozen_population(self):
        values = phase107.gate_inputs()
        instances = phase107.build_instances(values)
        self.assertEqual(len(instances), 265)
        self.assertEqual(sum(len(row["hyperedges"]) for row in instances), 1476)
        self.assertEqual(sum(len(row["ordered_words"]) for row in instances), 17624)
        self.assertEqual(
            (min(len(row["ordered_words"]) + len(row["hyperedges"]) for row in instances),
             max(len(row["ordered_words"]) + len(row["hyperedges"]) for row in instances)),
            (9, 172),
        )


if __name__ == "__main__":
    unittest.main()
