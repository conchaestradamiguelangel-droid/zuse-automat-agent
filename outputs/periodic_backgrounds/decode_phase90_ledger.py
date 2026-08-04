#!/usr/bin/env python3
"""Decode a compact Fase 90 per-rule ledger without running simulations."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Iterator


OUT_DIR = Path(__file__).resolve().parent
ROOT = OUT_DIR.parent.parent
CORE_PATH = OUT_DIR / "phase90_resweep_core.py"
BASE_SCRIPT = OUT_DIR / "sweep_periodic_background_oscillators.py"
LEN8_SCRIPT = ROOT / "outputs" / "periodic_backgrounds_len8" / "sweep_len8_periodic_oscillators.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


core = load_module("phase90_decoder_core", CORE_PATH)


def decode_rows(
    ledger_path: Path,
    *,
    cohort: str,
    rule: int,
) -> Iterator[dict[str, Any]]:
    base = load_module("phase90_decoder_base", BASE_SCRIPT)
    len8 = load_module("phase90_decoder_len8", LEN8_SCRIPT)
    if cohort == "baseline_period_1_2_4":
        backgrounds = list(base.background_words())
    elif cohort == "primitive_len8":
        backgrounds = list(len8.primitive_len8_backgrounds())
    else:
        raise ValueError(f"Unknown cohort {cohort}")
    words = list(base.ic_words())
    expected = len(backgrounds) * len(words)
    observed = ledger_path.stat().st_size // core.LEDGER_SCHEMA.size
    if observed != expected:
        raise ValueError(f"Ledger has {observed} records, expected {expected}")
    kind_names = {int(kind): kind.name for kind in core.Kind}
    for flat_index, record in enumerate(core.iter_ledger(ledger_path)):
        background_index, ic_index = divmod(flat_index, len(words))
        word_len, _value, word = words[ic_index]
        yield {
            "cohort": cohort,
            "rule": rule,
            "background_index": background_index,
            "background": backgrounds[background_index],
            "ic_index": ic_index,
            "word_len": int(word_len),
            "word": word,
            "source_kind": kind_names[record.source_kind],
            "source_period": record.source_period,
            "source_drift": record.source_drift,
            "expanded_kind": kind_names[record.expanded_kind],
            "expanded_period": record.expanded_period,
            "expanded_drift": record.expanded_drift,
            "bounded_source": bool(record.flags & core.FLAG_BOUNDED_SOURCE),
            "source_positive": bool(record.flags & core.FLAG_SOURCE_POSITIVE),
            "period_cap_candidate": bool(record.flags & core.FLAG_CAP_CANDIDATE),
            "static_t1": bool(record.flags & core.FLAG_STATIC_T1),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    parser.add_argument(
        "--cohort",
        required=True,
        choices=["baseline_period_1_2_4", "primitive_len8"],
    )
    parser.add_argument("--rule", type=int, required=True, choices=range(256))
    parser.add_argument("--only-cap-candidates", action="store_true")
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    emitted = 0
    for row in decode_rows(args.ledger, cohort=args.cohort, rule=args.rule):
        if args.only_cap_candidates and not row["period_cap_candidate"]:
            continue
        print(json.dumps(row, sort_keys=True))
        emitted += 1
        if args.limit is not None and emitted >= args.limit:
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
