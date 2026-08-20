from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "outputs"
    / "periodic_backgrounds"
    / "analyze_phase107_conditioned_rescue_mechanisms.py"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


phase108 = load_module("test_phase108_module", SCRIPT)


class Phase108ConditionedRescueMechanismTests(unittest.TestCase):
    def test_catalog_has_all_twelve_exact_motifs(self):
        self.assertEqual(len(phase108.MOTIF_CATALOG), 12)
        self.assertEqual(
            [
                motif
                for motif, row in phase108.MOTIF_CATALOG.items()
                if row["cardinality"] == 4 and row["internal_edge_count"] in (0, 4)
            ],
            ["4I", "C4"],
        )

    def test_cell_classification_separates_logic_from_observation(self):
        self.assertEqual(
            phase108.cell_classification("2I", 10, 0), "LOGICALLY_FORCED"
        )
        self.assertEqual(
            phase108.cell_classification("P3", 0, 10),
            "OBSERVED_COMPLETE_SEPARATION",
        )
        self.assertEqual(
            phase108.cell_classification("K2", 3, 7), "EMPIRICALLY_VARIABLE"
        )
        self.assertEqual(
            phase108.cell_classification("C4", 0, 0), "ZERO_OBSERVED"
        )

    def test_edgeless_internal_dependency_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "Edgeless"):
            phase108.cell_classification("3I", 0, 1)

    def test_mechanism_label_mismatch_is_rejected(self):
        row = {
            "motif": "K2",
            "cardinality": 2,
            "mechanism_label": phase108.EXTERNAL,
            "internal_edge_required": True,
            "cut_mechanisms": ["INDIVIDUAL"],
            "stratum_index": 0,
        }
        with self.assertRaisesRegex(RuntimeError, "mechanism_label"):
            phase108.enrich_audits([row], {2: {}})

    def test_actual_census_reconciles_and_matches_reviewed_counts(self):
        results, _sources = phase108.analyze()
        primary = results["primary"]
        self.assertEqual(primary["rescue_count"], 1_476)
        self.assertEqual(primary["instance_count"], 265)
        self.assertEqual(primary["mechanism_counts"][phase108.EXTERNAL], 931)
        self.assertEqual(primary["mechanism_counts"][phase108.INTERNAL], 545)
        self.assertEqual(primary["zero_observed_motifs"], ["4I", "K1_3", "C4"])
        self.assertEqual(primary["empirically_variable_motifs"], ["K2", "K2+I"])

    def test_actual_variable_strata_are_exact(self):
        results, _sources = phase108.analyze()
        strata = results["primary"]["variable_strata"]
        self.assertEqual(strata["K2"]["total"], 223)
        self.assertEqual(strata["K2+I"]["total"], 96)
        self.assertEqual(
            strata["K2"]["by_metric"]["kappa"]["mechanism_counts"],
            {phase108.EXTERNAL: 24, phase108.INTERNAL: 83},
        )
        self.assertEqual(
            strata["K2+I"]["by_metric"]["lambda"]["mechanism_counts"],
            {phase108.EXTERNAL: 12, phase108.INTERNAL: 40},
        )

    def test_secondary_cut_unit_reconciles(self):
        results, _sources = phase108.analyze()
        secondary = results["secondary_cut_analysis"]
        self.assertEqual(secondary["cut_count"], 3_784)
        self.assertEqual(secondary["cut_counts"]["INDIVIDUAL"], 2_365)
        self.assertEqual(secondary["cut_counts"]["DISTRIBUTED_EXTERNAL"], 498)
        self.assertEqual(secondary["cut_counts"]["INTERNAL_EDGE_ENABLED"], 921)
        self.assertEqual(secondary["rescues_with_multiple_cut_categories"], 223)


if __name__ == "__main__":
    unittest.main()
