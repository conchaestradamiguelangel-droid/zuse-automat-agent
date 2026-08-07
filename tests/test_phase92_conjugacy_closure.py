from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase91_conjugacy_closure.py"
BASE_SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "sweep_periodic_background_oscillators.py"
RUNNER_SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "run_phase90_global_period_resweep.py"


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


phase92 = load("test_phase92_module", SCRIPT)
base = load("test_phase92_base", BASE_SCRIPT)
runner = load("test_phase92_runner", RUNNER_SCRIPT)


class Phase92ConjugacyTests(unittest.TestCase):
    def test_rule_and_words_are_exact_involutions(self):
        self.assertEqual(phase92.conjugate_rule(73), 109)
        self.assertEqual(phase92.conjugate_rule(109), 73)
        self.assertEqual(phase92.conjugate_rule(phase92.conjugate_rule(73)), 73)
        self.assertEqual(phase92.complement_word("001101"), "110010")
        self.assertEqual(
            phase92.complement_word(phase92.complement_word("001101")),
            "001101",
        )

    def test_catalog_absence_is_metadata_not_an_abort(self):
        status, stratum = phase92.coverage_status(
            background_present=False,
            ic_present=True,
            partner_present=False,
        )
        self.assertEqual(status, "BACKGROUND_PHASE_OMITTED")
        self.assertEqual(stratum, "CONSTRUCTED_PHASE_COMPLEMENT")

    def test_zero_ic_has_a_separate_diagnostic_stratum(self):
        status, stratum = phase92.coverage_status(
            background_present=False,
            ic_present=False,
            partner_present=False,
        )
        self.assertEqual(status, "BACKGROUND_PHASE_AND_ZERO_IC_OMITTED")
        self.assertEqual(stratum, "CONSTRUCTED_PHASE_PLUS_ZERO_IC")

    def test_represented_but_missing_partner_is_an_error(self):
        with self.assertRaises(RuntimeError):
            phase92.coverage_status(
                background_present=True,
                ic_present=True,
                partner_present=False,
            )

    def test_zero_ic_complement_preserves_exact_defect(self):
        original_rule = 73
        transformed_rule = 109
        original_background = "0011"
        transformed_background = phase92.complement_word(original_background)
        original_frames = [base.background_state(original_background)]
        transformed_frames = [base.background_state(transformed_background)]
        for _ in range(12):
            original_frames.append(base.eca_step_state(original_frames[-1], original_rule))
            transformed_frames.append(
                base.eca_step_state(transformed_frames[-1], transformed_rule)
            )
        original_word = "1111"
        transformed_word = "0000"
        left = base.initial_diff(int(original_word, 2), 4, original_frames[0])
        right = base.initial_diff(int(transformed_word, 2), 4, transformed_frames[0])
        self.assertEqual(left, right)
        for timestamp in range(12):
            self.assertEqual(
                phase92.complement_state(original_frames[timestamp]),
                transformed_frames[timestamp],
            )
            self.assertEqual(left, right)
            left = base.eca_step_diff(
                left,
                original_frames[timestamp],
                original_frames[timestamp + 1],
                original_rule,
            )
            right = base.eca_step_diff(
                right,
                transformed_frames[timestamp],
                transformed_frames[timestamp + 1],
                transformed_rule,
            )


if __name__ == "__main__":
    unittest.main()
