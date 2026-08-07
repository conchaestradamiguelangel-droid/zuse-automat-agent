from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "outputs" / "periodic_backgrounds" / "analyze_phase90_long_period_attractors.py"


def load_module():
    spec = importlib.util.spec_from_file_location("test_phase91_module", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase91 = load_module()


class Phase91SignatureTests(unittest.TestCase):
    def test_input_aliases_can_collapse_to_one_physical_attractor(self):
        frames = [("0" * 64, (0, 2)), ("f" * 64, (0, 1, 2))]
        left_input = {"background_index": 1, "ic_index": 3, "word": "101"}
        right_input = {"background_index": 8, "ic_index": 99, "word": "111000"}
        left = phase91.joint_cycle_payload(
            rule=73,
            kind="STATIONARY",
            drift=0,
            defect_period=2,
            background_period=2,
            joint_frames=frames,
        )
        right = phase91.joint_cycle_payload(
            rule=73,
            kind="STATIONARY",
            drift=0,
            defect_period=2,
            background_period=2,
            joint_frames=frames[1:] + frames[:1],
        )
        self.assertNotEqual(left_input, right_input)
        self.assertEqual(phase91.sha256_json(left), phase91.sha256_json(right))

    def test_joint_signature_uses_lcm_and_shared_rotation(self):
        background = ("0" * 64, "1" * 64)
        defect = ((0,), (0, 1), (0, 2), (0, 1, 2))
        joint = [
            (background[index % 2], defect[index % 4])
            for index in range(4)
        ]
        rotated = joint[3:] + joint[:3]
        payload = phase91.joint_cycle_payload(
            rule=73,
            kind="STATIONARY",
            drift=0,
            defect_period=4,
            background_period=2,
            joint_frames=joint,
        )
        same = phase91.joint_cycle_payload(
            rule=73,
            kind="STATIONARY",
            drift=0,
            defect_period=4,
            background_period=2,
            joint_frames=rotated,
        )
        misaligned = phase91.joint_cycle_payload(
            rule=73,
            kind="STATIONARY",
            drift=0,
            defect_period=4,
            background_period=2,
            joint_frames=[
                (background[(index + 1) % 2], defect[index % 4])
                for index in range(4)
            ],
        )
        self.assertEqual(payload["joint_period"], 4)
        self.assertEqual(phase91.sha256_json(payload), phase91.sha256_json(same))
        self.assertNotEqual(
            phase91.sha256_json(payload), phase91.sha256_json(misaligned)
        )

    def test_different_locking_ratios_never_share_morphology_class(self):
        defect_cycle = [(0, 1), (0, 2)]
        ratio_one = phase91.morphology_payload(
            kind="STATIONARY",
            drift=0,
            defect_period=2,
            background_period=2,
            defect_cycle=defect_cycle,
        )
        ratio_two = phase91.morphology_payload(
            kind="STATIONARY",
            drift=0,
            defect_period=2,
            background_period=1,
            defect_cycle=defect_cycle,
        )
        self.assertEqual(ratio_one["locking_ratio"], [1, 1])
        self.assertEqual(ratio_two["locking_ratio"], [2, 1])
        self.assertNotEqual(
            phase91.sha256_json(ratio_one), phase91.sha256_json(ratio_two)
        )

    def test_reflection_is_a_separate_quotient(self):
        cycle = [(0, 1, 4), (0, 2, 4), (0, 1, 2, 4)]
        reflected = [(0, 3, 4), (0, 2, 4), (0, 2, 3, 4)]
        left = phase91.morphology_payload(
            kind="STATIONARY",
            drift=0,
            defect_period=3,
            background_period=1,
            defect_cycle=cycle,
        )
        right = phase91.morphology_payload(
            kind="STATIONARY",
            drift=0,
            defect_period=3,
            background_period=1,
            defect_cycle=reflected,
        )
        left_q = phase91.morphology_payload(
            kind="STATIONARY",
            drift=0,
            defect_period=3,
            background_period=1,
            defect_cycle=cycle,
            reflection_quotient=True,
        )
        right_q = phase91.morphology_payload(
            kind="STATIONARY",
            drift=0,
            defect_period=3,
            background_period=1,
            defect_cycle=reflected,
            reflection_quotient=True,
        )
        self.assertNotEqual(phase91.sha256_json(left), phase91.sha256_json(right))
        self.assertEqual(phase91.sha256_json(left_q), phase91.sha256_json(right_q))

    def test_rule73_rule109_conjugacy_is_not_strict_identity(self):
        defect = (0, 2, 3)
        rule73_strict = phase91.joint_cycle_payload(
            rule=73,
            kind="STATIONARY",
            drift=0,
            defect_period=1,
            background_period=1,
            joint_frames=[("0" * 64, defect)],
        )
        rule109_strict = phase91.joint_cycle_payload(
            rule=109,
            kind="STATIONARY",
            drift=0,
            defect_period=1,
            background_period=1,
            joint_frames=[("f" * 64, defect)],
        )
        rule73_quotient = phase91.joint_cycle_payload(
            rule=73,
            kind="STATIONARY",
            drift=0,
            defect_period=1,
            background_period=1,
            joint_frames=[("0" * 64, defect)],
            conjugacy_quotient=True,
        )
        rule109_quotient = phase91.joint_cycle_payload(
            rule=109,
            kind="STATIONARY",
            drift=0,
            defect_period=1,
            background_period=1,
            joint_frames=[("f" * 64, defect)],
            conjugacy_quotient=True,
        )
        self.assertNotEqual(
            phase91.sha256_json(rule73_strict),
            phase91.sha256_json(rule109_strict),
        )
        self.assertEqual(
            phase91.sha256_json(rule73_quotient),
            phase91.sha256_json(rule109_quotient),
        )


if __name__ == "__main__":
    unittest.main()
