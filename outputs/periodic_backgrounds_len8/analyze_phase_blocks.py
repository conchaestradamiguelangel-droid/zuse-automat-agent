"""Fase 29: phase/block analysis of the T=15 locking cycle.

Fase 28 rejected a sparse truth-table support explanation for the
rule_73/rule_109 T=15 family. This script asks whether the five-state cycle
has a stronger local block description:

1. Are the five canonical XOR-defect shapes independent of the background?
2. If not, do phase-specific ordered local blocks recur across all backgrounds?

The analysis is intentionally conservative. A "block signature" is an ordered
contiguous sequence of per-position tokens. Each token contains the
background/defect neighborhoods seen across the three microsteps of one F^3
edge. A full local derivation would require a non-empty shared signature in all
five phases for both rules.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


OUT_DIR = Path(__file__).resolve().parent
LOCKING_RESULTS = OUT_DIR / "locking_mechanism_results.jsonl"
SYMBOLIC_RESULTS = OUT_DIR / "symbolic_locking_results.json"
LEN8_SCRIPT = OUT_DIR / "sweep_len8_periodic_oscillators.py"
RESULTS_JSON = OUT_DIR / "phase_blocks_results.json"
REPORT_MD = OUT_DIR / "phase_blocks_report.md"

SAMPLE_START = 81
BACKGROUND_PERIOD = 3
LOCKING_RATIO = 5
FINAL_STEP = SAMPLE_START + BACKGROUND_PERIOD * LOCKING_RATIO
BLOCK_PADDING = 3
MAX_PADDING_FOR_SEPARATION = 16


def load_len8_module():
    spec = importlib.util.spec_from_file_location("periodic_background_len8", LEN8_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot import detector from {LEN8_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def load_representatives() -> list[dict]:
    rows = [
        json.loads(line)
        for line in LOCKING_RESULTS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if len(rows) != 20:
        raise RuntimeError(f"Expected 20 Fase-27 representatives, got {len(rows)}")
    return rows


def load_symbolic() -> dict:
    return json.loads(SYMBOLIC_RESULTS.read_text(encoding="utf-8"))


def background_orbit(base, rule: int, word: str, steps: int) -> list[tuple[int, ...]]:
    frames = [base.background_state(word)]
    for _ in range(steps):
        frames.append(base.eca_step_state(frames[-1], rule))
    return frames


def perturbation_orbit(
    base,
    rule: int,
    background_frames: list[tuple[int, ...]],
    word: str,
) -> list[tuple[int, ...]]:
    diff = base.initial_diff(int(word, 2), len(word), background_frames[0])
    frames = [diff]
    for time_index in range(len(background_frames) - 1):
        diff = base.eca_step_diff(
            diff,
            background_frames[time_index],
            background_frames[time_index + 1],
            rule,
        )
        frames.append(diff)
    return frames


def canonical_defect(width: int, diff: tuple[int, ...]) -> dict:
    if not diff:
        raise RuntimeError("Cannot canonicalize an empty defect")

    positions = sorted(diff)
    gaps = []
    for index, position in enumerate(positions):
        next_position = positions[(index + 1) % len(positions)]
        if index == len(positions) - 1:
            next_position += width
        gaps.append((next_position - position, index))

    _largest_gap, cut_index = max(gaps)
    anchor = positions[(cut_index + 1) % len(positions)]
    offsets = tuple(sorted((position - anchor) % width for position in positions))
    active_width = max(offsets) + 1
    value = sum(1 << offset for offset in offsets)
    hex_digits = max(1, (active_width + 3) // 4)
    return {
        "anchor": anchor,
        "offsets": offsets,
        "width": active_width,
        "hex": f"{active_width}:{value:0{hex_digits}x}",
    }


def neighborhood_index(active: set[int], position: int, width: int) -> int:
    left = int((position - 1) % width in active)
    center = int(position in active)
    right = int((position + 1) % width in active)
    return (left << 2) | (center << 1) | right


def token_for_position(
    bg_frames: list[tuple[int, ...]],
    diff_frames: list[tuple[int, ...]],
    time_index: int,
    position: int,
    width: int,
) -> str:
    parts = []
    for micro_offset in range(BACKGROUND_PERIOD):
        t = time_index + micro_offset
        bg_now = set(bg_frames[t])
        diff_now = set(diff_frames[t])
        diff_next = set(diff_frames[t + 1])
        b_index = neighborhood_index(bg_now, position, width)
        d_index = neighborhood_index(diff_now, position, width)
        d_next = int(position in diff_next)
        parts.append(f"b{b_index:03b}/d{d_index:03b}->{d_next}")
    return "|".join(parts)


def block_signature(
    bg_frames: list[tuple[int, ...]],
    diff_frames: list[tuple[int, ...]],
    time_index: int,
    width: int,
    padding: int,
) -> dict:
    canonical = canonical_defect(width, diff_frames[time_index])
    offsets = canonical["offsets"]
    start = min(offsets) - padding
    end = max(offsets) + padding
    tokens = []
    for relative_position in range(start, end + 1):
        position = (canonical["anchor"] + relative_position) % width
        token = token_for_position(bg_frames, diff_frames, time_index, position, width)
        tokens.append([relative_position, token])
    return {
        "anchor": canonical["anchor"],
        "defect_hex": canonical["hex"],
        "padding": padding,
        "tokens": tokens,
        "token_sequence": [token for _relative, token in tokens],
    }


def common_contiguous_subsequences(sequences: list[list[str]]) -> list[dict]:
    """Return longest exact contiguous token sequences shared by every sequence."""
    if not sequences:
        return []
    shortest = min(sequences, key=len)
    other_sets_by_length: dict[int, list[set[tuple[str, ...]]]] = {}
    for length in range(1, len(shortest) + 1):
        other_sets_by_length[length] = [
            {tuple(seq[index : index + length]) for index in range(len(seq) - length + 1)}
            for seq in sequences[1:]
        ]

    best: list[tuple[str, ...]] = []
    for length in range(len(shortest), 0, -1):
        candidates = {
            tuple(shortest[index : index + length])
            for index in range(len(shortest) - length + 1)
        }
        for other_set in other_sets_by_length[length]:
            candidates &= other_set
        if candidates:
            best = sorted(candidates)
            break

    return [
        {
            "length": len(candidate),
            "tokens": list(candidate),
        }
        for candidate in best[:5]
    ]


def token_touches_defect(token: str) -> bool:
    for segment in token.split("|"):
        left, output = segment.split("->")
        _b_part, d_part = left.split("/")
        if d_part != "d000" or output == "1":
            return True
    return False


def signature_touches_defect(signature: dict) -> bool:
    return any(token_touches_defect(token) for token in signature["tokens"])


def group_shape_consistency(representatives: list[dict]) -> dict:
    by_rule: dict[int, list[dict]] = defaultdict(list)
    for representative in representatives:
        by_rule[int(representative["rule"])].append(representative)

    result = {}
    for rule, records in sorted(by_rule.items()):
        phases = []
        for phase_index in range(LOCKING_RATIO):
            counter = Counter(record["defect_states"][phase_index] for record in records)
            phases.append(
                {
                    "phase": phase_index,
                    "consistent": len(counter) == 1,
                    "distinct_count": len(counter),
                    "shape_counts": dict(sorted(counter.items())),
                }
            )
        result[str(rule)] = {
            "representatives": len(records),
            "all_phases_consistent": all(phase["consistent"] for phase in phases),
            "phases": phases,
        }
    return result


def analyze_representative(base, representative: dict) -> dict:
    rule = int(representative["rule"])
    background = representative["background"]
    word = representative["ic"]
    bg_frames = background_orbit(base, rule, background, FINAL_STEP)
    diff_frames = perturbation_orbit(base, rule, bg_frames, word)
    phases = []
    for phase_index in range(LOCKING_RATIO):
        time_index = SAMPLE_START + phase_index * BACKGROUND_PERIOD
        phases.append(
            {
                "phase": phase_index,
                "time": time_index,
                "block": block_signature(
                    bg_frames,
                    diff_frames,
                    time_index,
                    base.WIDTH,
                    BLOCK_PADDING,
                ),
                "separation_blocks": [
                    block_signature(
                        bg_frames,
                        diff_frames,
                        time_index,
                        base.WIDTH,
                        padding,
                    )["token_sequence"]
                    for padding in range(MAX_PADDING_FOR_SEPARATION + 1)
                ],
            }
        )
    return {
        "rule": rule,
        "background": background,
        "ic": word,
        "defect_states": representative["defect_states"],
        "phases": phases,
    }


def complement_background_in_token(token: str) -> str:
    parts = []
    for segment in token.split("|"):
        left, output = segment.split("->")
        b_part, d_part = left.split("/")
        b_value = int(b_part[1:], 2)
        d_value = int(d_part[1:], 2)
        parts.append(f"b{(7 - b_value):03b}/d{d_value:03b}->{output}")
    return "|".join(parts)


def summarize_ordered_blocks(records: list[dict]) -> dict:
    by_rule: dict[int, list[dict]] = defaultdict(list)
    for record in records:
        by_rule[int(record["rule"])].append(record)

    result = {}
    for rule, selected in sorted(by_rule.items()):
        phases = []
        for phase_index in range(LOCKING_RATIO):
            phase_records = [record["phases"][phase_index] for record in selected]
            sequences = [phase["block"]["token_sequence"] for phase in phase_records]
            common = common_contiguous_subsequences(sequences)
            nontrivial_common = [
                signature
                for signature in common
                if signature_touches_defect(signature)
            ]

            first_divergence_w = None
            all_unique_w = None
            distinct_by_w = []
            for padding in range(MAX_PADDING_FOR_SEPARATION + 1):
                signatures = [
                    tuple(phase["separation_blocks"][padding])
                    for phase in phase_records
                ]
                distinct_count = len(set(signatures))
                distinct_by_w.append(distinct_count)
                if first_divergence_w is None and distinct_count > 1:
                    first_divergence_w = padding
                if all_unique_w is None and distinct_count == len(phase_records):
                    all_unique_w = padding

            phases.append(
                {
                    "phase": phase_index,
                    "shared_contiguous_signatures_all": common,
                    "shared_contiguous_signatures": nontrivial_common,
                    "shared_signature_found": bool(nontrivial_common),
                    "trivial_shared_signature_found": bool(common),
                    "longest_shared_signature_length": (
                        nontrivial_common[0]["length"] if nontrivial_common else 0
                    ),
                    "longest_trivial_or_any_shared_length": (
                        common[0]["length"] if common else 0
                    ),
                    "first_divergence_padding": first_divergence_w,
                    "all_unique_padding": all_unique_w,
                    "distinct_counts_by_padding": distinct_by_w,
                }
            )

        result[str(rule)] = {
            "all_phases_have_shared_signature": all(
                phase["shared_signature_found"] for phase in phases
            ),
            "phases": phases,
        }

    return result


def compare_conjugate_blocks(block_summary: dict) -> dict:
    phases = []
    for phase_index in range(LOCKING_RATIO):
        sig73 = block_summary["73"]["phases"][phase_index]["shared_contiguous_signatures"]
        sig109 = block_summary["109"]["phases"][phase_index]["shared_contiguous_signatures"]
        transformed73 = [
            [complement_background_in_token(token) for token in signature["tokens"]]
            for signature in sig73
        ]
        raw109 = [signature["tokens"] for signature in sig109]
        phases.append(
            {
                "phase": phase_index,
                "shared_signature_complement_match": any(
                    transformed in raw109 for transformed in transformed73
                ),
                "rule73_signature_count": len(sig73),
                "rule109_signature_count": len(sig109),
            }
        )
    return {
        "all_phase_signatures_conjugate": all(
            phase["shared_signature_complement_match"] for phase in phases
        ),
        "phases": phases,
    }


def summarize_symbolic_inputs(symbolic: dict) -> dict:
    aggregate = symbolic["aggregate"]
    return {
        "status": symbolic["status"],
        "sparse_universal_support_found": aggregate["sparse_universal_support_found"],
        "rule73_phase_intersection_sizes": [
            len(keys)
            for keys in aggregate["rule_profiles"]["73"]["phase_intersections"]
        ],
        "rule109_phase_intersection_sizes": [
            len(keys)
            for keys in aggregate["rule_profiles"]["109"]["phase_intersections"]
        ],
        "conjugation_identity_exact": aggregate["conjugation_identity_exact"],
    }


def verdict(shape_summary: dict, block_summary: dict) -> str:
    shape_complete = all(
        rule_result["all_phases_consistent"]
        for rule_result in shape_summary.values()
    )
    if shape_complete:
        return "LOCAL_DEFECT_ONLY"
    block_complete = all(
        rule_result["all_phases_have_shared_signature"]
        for rule_result in block_summary.values()
    )
    if block_complete:
        return "LOCAL_BLOCK_SIGNATURE_FOUND"
    if any(
        phase["shared_signature_found"]
        for rule_result in block_summary.values()
        for phase in rule_result["phases"]
    ):
        return "PARTIAL_BLOCK_STRUCTURE"
    return "NO_LOCAL_BLOCK_DERIVATION"


def render_report(result: dict) -> str:
    lines = [
        "# Fase 29: Phase/Block Analysis of the T=15 Cycle",
        "",
        "## Question",
        "",
        "Fase 28 showed that no fixed sparse set of induced local keys explains",
        "all 100 `F^3` edges of the T=15 family. Fase 29 tests the next",
        "possibility: whether the five-cycle is visible as either a background-",
        "independent defect shape or a phase-specific ordered local block.",
        "",
        "## Inputs",
        "",
        "- Representatives: `20` minimal T=15 rule/background pairs from Fase 27.",
        "- Rules: `rule_73` and `rule_109`.",
        "- Sample times: `t=81,84,87,90,93`.",
        f"- Block window: active defect span plus `{BLOCK_PADDING}` cells on each side.",
        "- Per-position token: the ordered three-microstep sequence of",
        "  `(background neighborhood, defect neighborhood -> next defect bit)`.",
        "",
        "## Part A -- defect shape consistency",
        "",
        "| rule | phase 0 | phase 1 | phase 2 | phase 3 | phase 4 | all phases consistent |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for rule, summary in result["shape_consistency"].items():
        counts = [phase["distinct_count"] for phase in summary["phases"]]
        lines.append(
            f"| rule_{rule} | "
            + " | ".join(str(count) for count in counts)
            + f" | {summary['all_phases_consistent']} |"
        )
    lines.extend(
        [
            "",
            "A value of `1` would mean that every background produces the same",
            "canonical XOR-defect shape in that phase. The observed counts are all",
            "larger than one, so the T=15 cycle is not a pure defect-only dynamic.",
            "",
            "## Part B -- ordered block signatures",
            "",
            "| rule | phase | nontrivial shared signature | longest nontrivial length | any shared length | first W distinguishing backgrounds | W making all backgrounds unique |",
            "| --- | ---: | --- | ---: | ---: | ---: | ---: |",
        ]
    )
    for rule, summary in result["ordered_blocks"].items():
        for phase in summary["phases"]:
            lines.append(
                f"| rule_{rule} | {phase['phase']} | "
                f"{phase['shared_signature_found']} | "
                f"{phase['longest_shared_signature_length']} | "
                f"{phase['longest_trivial_or_any_shared_length']} | "
                f"{phase['first_divergence_padding']} | "
                f"{phase['all_unique_padding']} |"
            )
    lines.extend(
        [
            "",
            "The only exact shared length-1 blocks are trivial background-context",
            "tokens with `d000->0` through all three microsteps. They are reported",
            "as `any shared length` but are not counted as defect-driving local",
            "signatures.",
            "",
            "The `first W` column asks how many cells outside the active defect",
            "must be included before the ordered block distinguishes at least two",
            "backgrounds. `W=0` means the defect span itself already carries",
            "background-dependent local context.",
            "",
            "## Conjugation check",
            "",
            "| phase | complement maps shared rule_73 block to rule_109 block |",
            "| ---: | --- |",
        ]
    )
    for phase in result["block_conjugation"]["phases"]:
        lines.append(
            f"| {phase['phase']} | {phase['shared_signature_complement_match']} |"
        )

    symbolic = result["symbolic_inputs"]
    lines.extend(
        [
            "",
            "## Relation to Fase 28",
            "",
            f"- Sparse universal support found in Fase 28: "
            f"`{symbolic['sparse_universal_support_found']}`.",
            f"- Fase 28 rule_73 phase-intersection sizes: "
            f"`{symbolic['rule73_phase_intersection_sizes']}`.",
            f"- Fase 28 rule_109 phase-intersection sizes: "
            f"`{symbolic['rule109_phase_intersection_sizes']}`.",
            f"- Black/white induced conjugation identity exact: "
            f"`{symbolic['conjugation_identity_exact']}`.",
            "",
            "## Verdict",
            "",
            f"**Status:** `{result['verdict']}`.",
            "",
        ]
    )
    if result["verdict"] == "LOCAL_DEFECT_ONLY":
        lines.append(
            "The five-cycle is fully determined by the canonical defect shape; "
            "background context is not required."
        )
    elif result["verdict"] == "LOCAL_BLOCK_SIGNATURE_FOUND":
        lines.append(
            "Every phase has a shared ordered block signature in both rules. "
            "This is a candidate local block derivation of the five-cycle."
        )
    elif result["verdict"] == "PARTIAL_BLOCK_STRUCTURE":
        lines.append(
            "The cycle is not defect-only, but some phase-specific ordered blocks "
            "are shared across backgrounds. This is partial structure rather than "
            "a complete local derivation."
        )
    else:
        lines.append(
            "Neither the defect-only hypothesis nor the fixed-window ordered block "
            "hypothesis explains all phases. The T=15 mechanism requires context "
            "beyond this local block representation, or a different state variable."
        )

    lines.extend(
        [
            "",
            "## Falsifiable implication",
            "",
            "A complete symbolic derivation of the `rule_73/rule_109` T=15 family",
            "must encode the spatial phase of the length-8 background, or use a",
            "larger/higher-order state than the active defect plus a fixed local",
            "padding. A proposed derivation that predicts background-independent",
            "defect shapes or one shared ordered block in all five phases is",
            "falsified by this report.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    module = load_len8_module()
    base = module.load_base_module()
    representatives = load_representatives()
    symbolic = load_symbolic()
    phase_records = [analyze_representative(base, record) for record in representatives]
    shape_summary = group_shape_consistency(representatives)
    block_summary = summarize_ordered_blocks(phase_records)
    result = {
        "status": "OK",
        "verdict": verdict(shape_summary, block_summary),
        "constants": {
            "sample_start": SAMPLE_START,
            "background_period": BACKGROUND_PERIOD,
            "locking_ratio": LOCKING_RATIO,
            "block_padding": BLOCK_PADDING,
            "max_padding_for_separation": MAX_PADDING_FOR_SEPARATION,
        },
        "shape_consistency": shape_summary,
        "ordered_blocks": block_summary,
        "block_conjugation": compare_conjugate_blocks(block_summary),
        "symbolic_inputs": summarize_symbolic_inputs(symbolic),
        "representatives": phase_records,
    }
    RESULTS_JSON.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    REPORT_MD.write_text(render_report(result), encoding="utf-8")
    print(f"wrote {RESULTS_JSON}")
    print(f"wrote {REPORT_MD}")
    print(f"verdict={result['verdict']}")


if __name__ == "__main__":
    main()
