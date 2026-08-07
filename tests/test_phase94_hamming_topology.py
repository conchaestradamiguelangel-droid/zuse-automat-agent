from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
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


phase94 = load("test_phase94_module", OUT / "analyze_phase93_hamming_topology.py")
core = load("test_phase94_core", OUT / "phase90_resweep_core.py")


class Phase94TopologyTests(unittest.TestCase):
    def test_window_and_flip_are_exact_hamming_one(self):
        phase94.validate_window()
        source = (125, 128, 131)
        targets = {phase94.flip_diff(source, position) for position in phase94.WINDOW_POSITIONS}
        self.assertEqual(len(targets), 8)
        for target in targets:
            self.assertEqual(len(set(source).symmetric_difference(target)), 1)

    def test_ledger_address_reads_exact_record(self):
        records = [
            core.LedgerRecord(source_kind=index, expanded_kind=index)
            for index in range(1, 5)
        ]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.bin"
            path.write_bytes(b"".join(record.encode() for record in records))
            observed = phase94.ledger_record_at(
                core=core,
                ledger_path=path,
                background_index=0,
                ic_index=3,
            )
        self.assertEqual(observed, records[3])

    def test_outside_category_requires_positive_ledger_evidence(self):
        source_positive = core.LedgerRecord(
            source_kind=int(core.Kind.STATIONARY),
            expanded_kind=int(core.Kind.STATIONARY),
            source_period=12,
            expanded_period=12,
            flags=core.FLAG_BOUNDED_SOURCE | core.FLAG_SOURCE_POSITIVE,
        )
        self.assertEqual(
            phase94.outside_category(core, source_positive),
            "HISTORICAL_SOURCE_POSITIVE",
        )
        cap_candidate = core.LedgerRecord(
            source_kind=int(core.Kind.BOUNDED_UNCLASSIFIED),
            expanded_kind=int(core.Kind.STATIONARY),
            expanded_period=18,
            flags=core.FLAG_BOUNDED_SOURCE | core.FLAG_CAP_CANDIDATE,
        )
        with self.assertRaises(RuntimeError):
            phase94.outside_category(core, cap_candidate)

    def test_reciprocity_gate_rejects_missing_reverse_edge(self):
        edges = [
            {
                "source_initial_state_sha256": "left",
                "target_initial_state_sha256": "right",
                "flip_position": 127,
            }
        ]
        with self.assertRaisesRegex(RuntimeError, "Missing reciprocal edge"):
            phase94.verify_reciprocity(edges)
        edges.append(
            {
                "source_initial_state_sha256": "right",
                "target_initial_state_sha256": "left",
                "flip_position": 127,
            }
        )
        phase94.verify_reciprocity(edges)

    def test_reciprocity_gate_checks_the_physical_round_trip(self):
        edges = [
            {
                "source_initial_state_sha256": "left",
                "target_initial_state_sha256": "right",
                "flip_position": 127,
            },
            {
                "source_initial_state_sha256": "right",
                "target_initial_state_sha256": "left",
                "flip_position": 127,
            },
        ]
        states = {
            "left": {
                "rule": 73,
                "background_t0_absolute": "aa",
                "initial_diff_absolute": [125],
            },
            "right": {
                "rule": 73,
                "background_t0_absolute": "aa",
                "initial_diff_absolute": [125, 127],
            },
        }
        phase94.verify_reciprocity(edges, states)
        states["right"]["initial_diff_absolute"] = [125, 128]
        with self.assertRaisesRegex(RuntimeError, "Reverse flip"):
            phase94.verify_reciprocity(edges, states)

    def test_manifest_validation_checks_digest_and_size(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = root / "rule_073.ledger.bin"
            manifest = root / "rule_073.manifest.json"
            record = core.LedgerRecord(
                source_kind=int(core.Kind.EXTINCT),
                expanded_kind=int(core.Kind.EXTINCT),
            )
            ledger.write_bytes(record.encode())
            digest = core.sha256_file(ledger)
            manifest.write_text(
                json.dumps(
                    {
                        "phase": 90,
                        "stage": "A",
                        "cohort": "test",
                        "rule": 73,
                        "processed_runs": 1,
                        "artifacts": {
                            "ledger": {
                                "size": core.LEDGER_SCHEMA.size,
                                "sha256": digest,
                            }
                        },
                    }
                ),
                encoding="utf-8",
            )
            observed = phase94.validate_ledger_artifact(
                core=core, ledger_path=ledger, manifest_path=manifest
            )
            self.assertEqual(observed["processed_runs"], 1)
            ledger.write_bytes(record.encode() + b"x")
            with self.assertRaises(ValueError):
                phase94.validate_ledger_artifact(
                    core=core, ledger_path=ledger, manifest_path=manifest
                )


if __name__ == "__main__":
    unittest.main()
