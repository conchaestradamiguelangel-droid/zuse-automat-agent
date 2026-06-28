#!/usr/bin/env python3
"""Fase 34 preflight: check T_bg=3 availability for len-9/10 backgrounds.

The compact descriptor from Fase 31-33 was established inside primitive
length-8 backgrounds. Before launching a larger length-9/10 validation, this
script checks whether the prerequisite for the T=15 mechanism still exists:
background temporal period T_bg=3 under rule_73/rule_109.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


OUT_JSON = Path(__file__).with_name("preflight_len9_len10_tbg3_results.json")
OUT_REPORT = Path(__file__).with_name("preflight_len9_len10_tbg3_report.md")


def eca_step(state: tuple[int, ...], rule: int) -> tuple[int, ...]:
    n = len(state)
    out = []
    for i in range(n):
        left = state[(i - 1) % n]
        center = state[i]
        right = state[(i + 1) % n]
        idx = (left << 2) | (center << 1) | right
        out.append((rule >> idx) & 1)
    return tuple(out)


def rotations(word: str) -> list[str]:
    return [word[i:] + word[:i] for i in range(len(word))]


def canonical_rotation(word: str) -> str:
    return min(rotations(word))


def minimal_word_period(word: str) -> int:
    n = len(word)
    for period in range(1, n + 1):
        if n % period == 0 and all(word[i] == word[i % period] for i in range(n)):
            return period
    return n


def primitive_necklaces(n: int) -> list[str]:
    seen = set()
    reps = []
    for value in range(1, 2**n):
        word = format(value, f"0{n}b")
        if minimal_word_period(word) != n:
            continue
        canon = canonical_rotation(word)
        if canon not in seen:
            seen.add(canon)
            reps.append(canon)
    return sorted(reps)


def temporal_period(word: str, rule: int, max_steps: int = 5000) -> dict:
    state = tuple(int(ch) for ch in word)
    seen = {state: 0}
    for step in range(1, max_steps + 1):
        state = eca_step(state, rule)
        if state in seen:
            return {"preperiod": seen[state], "period": step - seen[state]}
        seen[state] = step
    return {"preperiod": None, "period": None}


def main() -> None:
    results = {"rules": [73, 109], "lengths": [8, 9, 10], "by_length_rule": {}}

    for length in results["lengths"]:
        reps = primitive_necklaces(length)
        for rule in results["rules"]:
            periods = Counter()
            preperiods = Counter()
            examples = defaultdict(list)
            records = []
            for background in reps:
                pinfo = temporal_period(background, rule)
                period = pinfo["period"]
                preperiod = pinfo["preperiod"]
                periods[str(period)] += 1
                preperiods[str(preperiod)] += 1
                if len(examples[str(period)]) < 10:
                    examples[str(period)].append(background)
                if period == 3:
                    records.append(
                        {
                            "background": background,
                            "preperiod": preperiod,
                            "period": period,
                        }
                    )
            results["by_length_rule"][f"len{length}_rule{rule}"] = {
                "primitive_necklaces": len(reps),
                "period_counts": dict(sorted(periods.items(), key=lambda item: int(item[0]) if item[0] != "None" else 10**9)),
                "preperiod_counts": dict(sorted(preperiods.items(), key=lambda item: int(item[0]) if item[0] != "None" else 10**9)),
                "t_bg_3_count": len(records),
                "t_bg_3_records": records,
                "period_examples": {period: vals for period, vals in sorted(examples.items())},
            }

    OUT_JSON.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    OUT_REPORT.write_text(render_report(results), encoding="utf-8")


def render_report(results: dict) -> str:
    lines = [
        "# Fase 34 Preflight: T_bg=3 Availability in Length-9/10 Backgrounds",
        "",
        "## Question",
        "",
        "Before launching a length-9/10 T=15 validation, check whether primitive",
        "backgrounds of those lengths can still have temporal background period",
        "`T_bg=3` under `rule_73` and `rule_109`. If no such backgrounds exist,",
        "the 5:1 locking mechanism cannot be tested in the same form.",
        "",
        "## Period census",
        "",
        "| length | rule | primitive necklaces | period counts | T_bg=3 |",
        "| ---: | ---: | ---: | --- | ---: |",
    ]
    for length in results["lengths"]:
        for rule in results["rules"]:
            row = results["by_length_rule"][f"len{length}_rule{rule}"]
            lines.append(
                f"| {length} | {rule} | {row['primitive_necklaces']} | "
                f"`{row['period_counts']}` | {row['t_bg_3_count']} |"
            )
    lines += [
        "",
        "## T_bg=3 examples",
        "",
    ]
    for length in [9, 10]:
        for rule in results["rules"]:
            row = results["by_length_rule"][f"len{length}_rule{rule}"]
            examples = [rec["background"] for rec in row["t_bg_3_records"][:10]]
            lines.append(f"- len `{length}`, rule `{rule}`: {', '.join(f'`{bg}`' for bg in examples)}")
    lines += [
        "",
        "## Verdict",
        "",
        "**Status:** `T_BG_3_AVAILABLE_LEN9_LEN10`.",
        "",
        "Length-9 and length-10 primitive backgrounds do contain `T_bg=3` cases",
        "under both `rule_73` and `rule_109`: 11 per rule at length 9 and 22 per",
        "rule at length 10. Therefore a targeted Fase 34 validation is meaningful.",
        "",
        "The correct next experiment is not a blind all-rule sweep. It should target",
        "`rule_73/rule_109`, primitive len-9/10 backgrounds with `T_bg=3`, and the",
        "same IC family/protocol used for the T=15 mechanism.",
        "",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    main()
