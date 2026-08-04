import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "periodic_backgrounds"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_module("test_phase90_core", OUT / "phase90_resweep_core.py")
runner = load_module(
    "test_phase90_runner", OUT / "run_phase90_global_period_resweep.py"
)
decoder = load_module(
    "test_phase90_decoder", OUT / "decode_phase90_ledger.py"
)


class Phase90LedgerTests(unittest.TestCase):
    def test_record_roundtrip_and_fixed_size(self):
        record = core.LedgerRecord(
            source_kind=int(core.Kind.BOUNDED_UNCLASSIFIED),
            expanded_kind=int(core.Kind.STATIONARY),
            expanded_period=30,
            expanded_drift=-2,
            flags=core.FLAG_BOUNDED_SOURCE | core.FLAG_CAP_CANDIDATE,
        )
        payload = record.encode()
        self.assertEqual(len(payload), 9)
        self.assertEqual(core.LedgerRecord.decode(payload), record)

    def test_invalid_record_values_fail_closed(self):
        with self.assertRaises(ValueError):
            core.LedgerRecord(0, 1, expanded_period=256).encode()
        with self.assertRaises(ValueError):
            core.LedgerRecord(0, 1, expanded_drift=40000).encode()

    def test_iter_ledger_rejects_partial_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.bin"
            path.write_bytes(b"123456789x")
            with self.assertRaises(ValueError):
                list(core.iter_ledger(path))

    def test_decoder_maps_implicit_baseline_order(self):
        count = 15 * 502
        record = core.LedgerRecord(
            source_kind=int(core.Kind.BOUNDED_UNCLASSIFIED),
            expanded_kind=int(core.Kind.STATIONARY),
            expanded_period=24,
            flags=core.FLAG_BOUNDED_SOURCE | core.FLAG_CAP_CANDIDATE,
        ).encode()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rule.bin"
            path.write_bytes(record * count)
            rows = decoder.decode_rows(
                path, cohort="baseline_period_1_2_4", rule=73
            )
            first = next(rows)
            self.assertEqual(first["background"], "1")
            self.assertEqual(first["word"], "1")
            self.assertTrue(first["period_cap_candidate"])
            self.assertEqual(first["expanded_period"], 24)
            rows.close()


class Phase90AuthorizationTests(unittest.TestCase):
    def write_authorization(self, path, **changes):
        data = {
            "phase": 90,
            "approved": True,
            "protocol_sha256": "abc",
            "stage": "STAGE_A",
            "authorized_by": "Miguel",
            "max_workers": 5,
            "expires_at_epoch": 2000.0,
        }
        data.update(changes)
        path.write_text(json.dumps(data), encoding="utf-8")

    def test_valid_authorization(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "auth.json"
            self.write_authorization(path)
            result = core.validate_authorization(
                path,
                expected_protocol_digest="abc",
                expected_stage="STAGE_A",
                max_workers=5,
                now=1000.0,
            )
            self.assertEqual(result["authorized_by"], "Miguel")

    def test_wrong_stage_digest_expiry_and_worker_limit_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "auth.json"
            self.write_authorization(path)
            for kwargs in (
                {"expected_protocol_digest": "wrong", "expected_stage": "STAGE_A", "max_workers": 5},
                {"expected_protocol_digest": "abc", "expected_stage": "STAGE_B", "max_workers": 5},
                {"expected_protocol_digest": "abc", "expected_stage": "STAGE_A", "max_workers": 6},
            ):
                with self.assertRaises(PermissionError):
                    core.validate_authorization(path, now=1000.0, **kwargs)
            with self.assertRaises(PermissionError):
                core.validate_authorization(
                    path,
                    expected_protocol_digest="abc",
                    expected_stage="STAGE_A",
                    max_workers=5,
                    now=3000.0,
                )


class Phase90CheckpointTests(unittest.TestCase):
    def test_claim_is_exclusive_and_stale_running_requeues(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "checkpoint.sqlite"
            core.initialize_checkpoint(
                db, protocol_sha256="digest", units=[("cohort", 7, 2)]
            )
            with core.checkpoint_connection(db) as connection:
                self.assertTrue(
                    core.claim_unit(
                        connection, stage="A", cohort="cohort", rule=7, now=10.0
                    )
                )
                self.assertFalse(
                    core.claim_unit(
                        connection, stage="A", cohort="cohort", rule=7, now=11.0
                    )
                )
                self.assertEqual(
                    core.requeue_stale_units(connection, stale_before=20.0), 1
                )
                self.assertTrue(
                    core.claim_unit(
                        connection, stage="A", cohort="cohort", rule=7, now=21.0
                    )
                )

    def test_checkpoint_rejects_protocol_rebind(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "checkpoint.sqlite"
            core.initialize_checkpoint(
                db, protocol_sha256="one", units=[("cohort", 0, 1)]
            )
            with self.assertRaises(ValueError):
                core.initialize_checkpoint(
                    db, protocol_sha256="two", units=[("cohort", 0, 1)]
                )

    def test_completion_binds_validated_artifacts_and_detects_corruption(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db = root / "checkpoint.sqlite"
            core.initialize_checkpoint(
                db, protocol_sha256="digest", units=[("cohort", 0, 1)]
            )
            ledger = root / "ledger.bin"
            ledger.write_bytes(core.LedgerRecord(0, 0).encode())
            manifest = {
                "artifacts": {
                    "ledger": {
                        "path": str(ledger),
                        "size": ledger.stat().st_size,
                        "sha256": core.sha256_file(ledger),
                    }
                }
            }
            manifest_path = root / "manifest.json"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            manifest_info = core.artifact_info(manifest_path)
            with core.checkpoint_connection(db) as connection:
                self.assertTrue(
                    core.claim_unit(
                        connection, stage="A", cohort="cohort", rule=0
                    )
                )
                core.complete_unit(
                    connection,
                    stage="A",
                    cohort="cohort",
                    rule=0,
                    processed_runs=1,
                    source_positive_count=0,
                    candidate_count=0,
                    elapsed_seconds=0.1,
                    manifest=manifest,
                    manifest_info=manifest_info,
                )
                self.assertEqual(core.verify_complete_units(connection), [])
                ledger.write_bytes(b"corrupt!!")
                errors = core.verify_complete_units(connection)
                self.assertEqual(len(errors), 1)
                self.assertIn("cohort:0", errors[0])


class Phase90WindowsPublishTests(unittest.TestCase):
    def test_replace_overwrites_existing_file_and_verifies_digest(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            temp = root / "new.tmp"
            final = root / "final.bin"
            temp.write_bytes(b"new-content")
            final.write_bytes(b"old-content")
            expected = core.sha256_file(temp)
            info = core.publish_temp_file(temp, final, expected)
            self.assertFalse(temp.exists())
            self.assertEqual(final.read_bytes(), b"new-content")
            self.assertEqual(info["sha256"], expected)

    def test_replace_permission_failure_preserves_old_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            temp = root / "new.tmp"
            final = root / "final.bin"
            temp.write_bytes(b"new-content")
            final.write_bytes(b"old-content")
            expected = core.sha256_file(temp)
            with mock.patch.object(core.os, "replace", side_effect=PermissionError("locked")):
                with self.assertRaises(PermissionError):
                    core.publish_temp_file(temp, final, expected)
            self.assertEqual(final.read_bytes(), b"old-content")
            self.assertTrue(temp.exists())

    def test_temp_digest_failure_never_replaces_final(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            temp = root / "new.tmp"
            final = root / "final.bin"
            temp.write_bytes(b"new-content")
            final.write_bytes(b"old-content")
            with self.assertRaises(ValueError):
                core.publish_temp_file(temp, final, "0" * 64)
            self.assertEqual(final.read_bytes(), b"old-content")


class Phase90ProtocolTests(unittest.TestCase):
    def test_generator_preflight_is_exact_and_simulation_free(self):
        protocol = core.load_protocol(
            OUT / "phase90_global_period_cap_resweep_protocol.json"
        )
        result = runner.generator_preflight(protocol)
        self.assertTrue(result["matches_protocol"])
        self.assertFalse(result["simulation_executed"])
        self.assertEqual(result["global_runs"], 5_783_040)
        self.assertEqual(result["work_units"], 512)

    def test_dynamic_disk_gate_grows_with_measured_candidates(self):
        floor = 5 * 1024**3
        small = core.dynamic_disk_requirement(
            fixed_ledger_bytes=52_047_360,
            candidate_count=100,
            candidate_bytes=10_000,
        )
        large = core.dynamic_disk_requirement(
            fixed_ledger_bytes=52_047_360,
            candidate_count=10_000_000,
            candidate_bytes=2_000_000_000,
        )
        self.assertEqual(small, floor)
        self.assertGreater(large, floor)

    def test_protocol_remains_design_only(self):
        protocol = core.load_protocol(
            OUT / "phase90_global_period_cap_resweep_protocol.json"
        )
        self.assertFalse(protocol["execution"]["allowed"])
        self.assertEqual(protocol["status"], "DESIGN_ONLY_NOT_EXECUTED")

    def test_stage_a_benchmark_report_is_digest_and_worker_bound(self):
        report = {
            "phase": 90,
            "status": "PASS",
            "protocol_sha256": "protocol",
            "workers": 5,
            "simulation_executed": True,
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "benchmark.json"
            path.write_text(json.dumps(report), encoding="utf-8")
            digest = core.sha256_file(path)
            accepted = runner.validate_benchmark_report(
                path,
                protocol_sha256="protocol",
                workers=5,
                expected_digest=digest,
            )
            self.assertEqual(accepted["workers"], 5)
            with self.assertRaises(PermissionError):
                runner.validate_benchmark_report(
                    path,
                    protocol_sha256="protocol",
                    workers=4,
                    expected_digest=digest,
                )
            with self.assertRaises(PermissionError):
                runner.validate_benchmark_report(
                    path,
                    protocol_sha256="protocol",
                    workers=5,
                    expected_digest="0" * 64,
                )

    def test_final_summary_separates_confirmed_and_mismatched_candidates(self):
        rows = [
            {
                "confirmation_status": "CONFIRMED_PERIOD_CAP_FALSE_NEGATIVE",
                "stage_b_period": 30,
                "cohort": "primitive_len8",
                "rule": 73,
            },
            {
                "confirmation_status": "CANDIDATE_LONG_CLASS_MISMATCH",
                "stage_b_period": 24,
                "cohort": "primitive_len8",
                "rule": 73,
            },
            {
                "confirmation_status": "CANDIDATE_NOT_PERSISTENT",
                "stage_b_period": 0,
                "cohort": "baseline_period_1_2_4",
                "rule": 109,
            },
        ]
        summary = runner.summarize_long_results(rows)
        self.assertEqual(summary["candidate_count"], 3)
        self.assertEqual(summary["confirmed_count"], 1)
        self.assertEqual(summary["confirmed_period_distribution"], {"30": 1})
        self.assertEqual(summary["confirmed_rule_distribution"], {"73": 1})

    def test_status_requires_existing_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                runner.require_checkpoint(Path(tmp) / "missing.sqlite")


if __name__ == "__main__":
    unittest.main()
