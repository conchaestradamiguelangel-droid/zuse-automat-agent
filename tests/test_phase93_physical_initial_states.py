from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase91_physical_initial_states.py"
BASE_SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "sweep_periodic_background_oscillators.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase93 = load("test_phase93_module", SCRIPT)
base = load("test_phase93_base", BASE_SCRIPT)


class Phase93InitialStateTests(unittest.TestCase):
    def test_manual_placement_matches_historical_initial_diff(self):
        background = base.background_state("0011")
        expected = base.initial_diff(int("00101", 2), 5, background)
        observed = phase93.manual_initial_diff(
            word="00101", word_len=5, background_state=background
        )
        self.assertEqual(observed, expected)

    def test_strict_identity_preserves_absolute_position(self):
        background = base.background_state("0011")
        left = phase93.strict_initial_payload(
            rule=73, background_state=background, initial_diff=(126, 128)
        )
        right = phase93.strict_initial_payload(
            rule=73, background_state=background, initial_diff=(127, 129)
        )
        self.assertNotEqual(phase93.sha256_json(left), phase93.sha256_json(right))
        self.assertEqual(
            left["position_policy"], "ABSOLUTE_FIXED_GRID_NO_CANONICALIZATION"
        )

    def test_encoding_descriptors_do_not_enter_strict_identity(self):
        first_encoding = {
            "rule": 109,
            "background": "0011",
            "word": "1",
            "word_len": 1,
        }
        second_encoding = {
            "rule": 109,
            "background": "0011",
            "word": "1110",
            "word_len": 4,
        }
        first = phase93.derive_initial_state(first_encoding, base)
        second = phase93.derive_initial_state(second_encoding, base)
        self.assertNotEqual(first_encoding, second_encoding)
        self.assertEqual(first["initial_diff_absolute"], [128])
        self.assertEqual(first["strict_sha256"], second["strict_sha256"])

    def test_gate_reads_existing_physical_class_and_rejects_conflict(self):
        groups = {
            "initial": [
                {"physical_class_sha256": "class-a"},
                {"physical_class_sha256": "class-b"},
            ]
        }
        with self.assertRaisesRegex(
            RuntimeError, "INITIAL_STATE_DETERMINISM_VIOLATION"
        ):
            phase93.validate_determinism(groups)

    def test_conjugacy_is_separate_from_strict_identity(self):
        background73 = base.background_state("0011")
        background109 = tuple(
            position for position in range(phase93.WIDTH) if position not in set(background73)
        )
        strict73 = phase93.strict_initial_payload(
            rule=73, background_state=background73, initial_diff=(127, 128)
        )
        strict109 = phase93.strict_initial_payload(
            rule=109, background_state=background109, initial_diff=(127, 128)
        )
        quotient73 = phase93.conjugacy_initial_payload(
            rule=73, background_state=background73, initial_diff=(127, 128)
        )
        quotient109 = phase93.conjugacy_initial_payload(
            rule=109, background_state=background109, initial_diff=(127, 128)
        )
        self.assertNotEqual(
            phase93.sha256_json(strict73), phase93.sha256_json(strict109)
        )
        self.assertEqual(
            phase93.sha256_json(quotient73), phase93.sha256_json(quotient109)
        )


if __name__ == "__main__":
    unittest.main()
