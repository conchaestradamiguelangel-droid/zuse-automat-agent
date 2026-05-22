"""Command line interface for ZUSE AUTOMAT AGENT Fase 0a."""

from __future__ import annotations

import argparse
from pathlib import Path

from .eca import random_initial_state, simulate, single_seed_initial_state
from .gates import evaluate_g1a1
from .metrics import summarize_frames
from .consensus import consensus_by_type, dominant_type
from .observers import run_observers
from .observers2d import run_observers_2d
from .packed_eca import array_to_int, run_packed
from .report import render_rule_report, save_report
from .rule110_fixtures import generate_all_candidates, normalize_all_validated_fixture_taxonomy, promote_all_candidates
from .storage import connect, count_universes, insert_universe
from .synthetic import moving_point, oscillator, static_block
from .visualize import save_frames_png
from .life2d import life_fixture, simulate_life
from .invariants import evaluate_all_fixture_laws, save_law_report


def cmd_simulate(args: argparse.Namespace) -> None:
    out_dir = Path(args.out)
    if args.single_seed:
        initial = single_seed_initial_state(args.width)
    else:
        initial = random_initial_state(args.width, seed=args.seed, density=args.density)

    frames = simulate(initial, args.rule, args.steps)
    metrics = summarize_frames(frames)
    image_path = save_frames_png(frames, out_dir / f"rule_{args.rule}.png", scale=args.scale)
    report = render_rule_report(
        rule=args.rule,
        width=args.width,
        steps=args.steps,
        seed=args.seed,
        metrics=metrics,
        image_path=str(image_path),
    )
    report_path = save_report(report, out_dir / f"rule_{args.rule}.md")
    print(f"image={image_path}")
    print(f"report={report_path}")


def cmd_dataset(args: argparse.Namespace) -> None:
    conn = connect(args.db)
    for rule in range(256):
        for ci_index in range(args.cis):
            seed = args.seed + rule * 10_000 + ci_index
            initial = random_initial_state(args.width, seed=seed, density=args.density)
            frames = simulate(initial, rule, args.steps)
            metrics = summarize_frames(frames)
            insert_universe(
                conn,
                rule=rule,
                ci_index=ci_index,
                seed=seed,
                width=args.width,
                steps=args.steps,
                metrics=metrics,
            )
    print(f"db={args.db}")
    print(f"universes={count_universes(conn)}")


def cmd_benchmark(args: argparse.Namespace) -> None:
    import time

    initial = single_seed_initial_state(args.width)
    packed = array_to_int(initial)
    start = time.perf_counter()
    final_state = run_packed(packed, args.rule, args.width, args.steps)
    elapsed = time.perf_counter() - start
    print(f"rule={args.rule}")
    print(f"width={args.width}")
    print(f"steps={args.steps}")
    print(f"elapsed_seconds={elapsed:.6f}")
    print(f"steps_per_second={args.steps / elapsed:.2f}")
    print(f"final_state_low64={final_state & ((1 << 64) - 1)}")


def cmd_observe_synthetic(args: argparse.Namespace) -> None:
    if args.kind == "glider":
        frames = moving_point(steps=args.steps, width=args.width)
    elif args.kind == "oscilador":
        frames = oscillator(steps=args.steps, width=args.width)
    else:
        frames = static_block(steps=args.steps, width=args.width)

    structures = run_observers(frames)
    consensus = consensus_by_type(structures)
    print(f"kind={args.kind}")
    print(f"structures={len(structures)}")
    print(f"dominant_type={dominant_type(structures)}")
    print(f"consensus={consensus}")
    for structure in structures:
        print(
            "structure="
            f"{structure.observador}:{structure.tipo}:"
            f"{structure.tipo_asignado_por}:conf={structure.confianza:.2f}"
        )


def cmd_generate_rule110_fixtures(args: argparse.Namespace) -> None:
    generated = generate_all_candidates(output_dir=args.out)
    for item in generated:
        print(f"npz={item['npz']}")
        print(f"png={item['png']}")
        print(f"summary={item['summary']}")


def cmd_validate_rule110_fixtures(args: argparse.Namespace) -> None:
    promoted = promote_all_candidates(pending_dir=args.pending, validated_dir=args.validated)
    for path in promoted:
        print(f"validated={path}")


def cmd_normalize_rule110_taxonomy(args: argparse.Namespace) -> None:
    normalized = normalize_all_validated_fixture_taxonomy(args.validated)
    for path in normalized:
        print(f"normalized={path}")


def cmd_observe_life(args: argparse.Namespace) -> None:
    frames = simulate_life(life_fixture(args.kind, height=args.height, width=args.width), args.steps)
    structures = run_observers_2d(frames)
    consensus = consensus_by_type(structures)
    print(f"kind={args.kind}")
    print(f"structures={len(structures)}")
    print(f"dominant_type={dominant_type(structures)}")
    print(f"consensus={consensus}")
    for structure in structures:
        print(
            "structure="
            f"{structure.observador}:{structure.tipo}:"
            f"{structure.tipo_asignado_por}:conf={structure.confianza:.2f}"
        )


def cmd_gate_g1a1(args: argparse.Namespace) -> None:
    report = evaluate_g1a1(args.fixtures)
    print(f"gate={report['gate']}")
    print(f"passed={report['passed']}")
    print(f"required={report['required']}")
    print(f"passed_required={report['passed_required']}")
    for result in report["results"]:
        print(
            "fixture="
            f"{result['fixture_id']}:expected={result['expected_type']}:"
            f"dominant={result['dominant_type']}:passed={result['passed']}:"
            f"consensus={result['consensus']}"
        )


def cmd_laws_2a(args: argparse.Namespace) -> None:
    report = evaluate_all_fixture_laws(args.fixtures)
    saved = save_law_report(report, args.out) if args.out else None
    print(f"fixtures={args.fixtures}")
    print(f"accepted={report['accepted']}")
    print(f"rejected={report['rejected']}")
    for fixture_report in report["reports"]:
        print(f"fixture={fixture_report['fixture_id']}")
        for result in fixture_report["results"]:
            print(
                "law="
                f"{result['name']}:accepted={result['accepted']}:"
                f"consistency={result['consistency']:.3f}:"
                f"mdl={result['mdl_candidate']}<null={result['mdl_null']}"
            )
    if saved:
        print(f"json={saved['json']}")
        print(f"markdown={saved['markdown']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="zaa", description="ZUSE AUTOMAT AGENT Fase 0a")
    sub = parser.add_subparsers(dest="command", required=True)

    sim = sub.add_parser("simulate", help="simulate one ECA rule")
    sim.add_argument("--rule", type=int, required=True)
    sim.add_argument("--steps", type=int, default=200)
    sim.add_argument("--width", type=int, default=256)
    sim.add_argument("--seed", type=int, default=110)
    sim.add_argument("--density", type=float, default=0.5)
    sim.add_argument("--scale", type=int, default=2)
    sim.add_argument("--single-seed", action="store_true")
    sim.add_argument("--out", default="outputs")
    sim.set_defaults(func=cmd_simulate)

    dataset = sub.add_parser("dataset", help="generate the Fase 0a SQLite dataset")
    dataset.add_argument("--steps", type=int, default=1000)
    dataset.add_argument("--width", type=int, default=256)
    dataset.add_argument("--cis", type=int, default=10)
    dataset.add_argument("--seed", type=int, default=20260523)
    dataset.add_argument("--density", type=float, default=0.5)
    dataset.add_argument("--db", default="data/zaa.sqlite")
    dataset.set_defaults(func=cmd_dataset)

    bench = sub.add_parser("benchmark", help="benchmark the bit-packed ECA engine")
    bench.add_argument("--rule", type=int, default=110)
    bench.add_argument("--steps", type=int, default=1_000_000)
    bench.add_argument("--width", type=int, default=256)
    bench.set_defaults(func=cmd_benchmark)

    obs = sub.add_parser("observe-synthetic", help="run Fase 1a observers on synthetic frames")
    obs.add_argument("--kind", choices=["glider", "oscilador", "bloque"], required=True)
    obs.add_argument("--steps", type=int, default=24)
    obs.add_argument("--width", type=int, default=64)
    obs.set_defaults(func=cmd_observe_synthetic)

    fix = sub.add_parser("generate-rule110-fixtures", help="generate pending Rule 110 fixture candidates")
    fix.add_argument("--out", default="fixtures/pending")
    fix.set_defaults(func=cmd_generate_rule110_fixtures)

    validate = sub.add_parser("validate-rule110-fixtures", help="promote pending Rule 110 fixtures to validated")
    validate.add_argument("--pending", default="fixtures/pending")
    validate.add_argument("--validated", default="fixtures/validated")
    validate.set_defaults(func=cmd_validate_rule110_fixtures)

    normalize = sub.add_parser("normalize-rule110-taxonomy", help="normalize validated Rule 110 fixture taxonomy")
    normalize.add_argument("--validated", default="fixtures/validated")
    normalize.set_defaults(func=cmd_normalize_rule110_taxonomy)

    life = sub.add_parser("observe-life", help="run Fase 1b observers on known Game of Life fixtures")
    life.add_argument("--kind", choices=["block", "blinker", "glider"], required=True)
    life.add_argument("--steps", type=int, default=8)
    life.add_argument("--height", type=int, default=32)
    life.add_argument("--width", type=int, default=32)
    life.set_defaults(func=cmd_observe_life)

    gate = sub.add_parser("gate-g1a1", help="evaluate Gate G1a.1 on validated Rule 110 fixtures")
    gate.add_argument("--fixtures", default="fixtures/validated")
    gate.set_defaults(func=cmd_gate_g1a1)

    laws = sub.add_parser("laws-2a", help="evaluate Fase 2a discrete law candidates")
    laws.add_argument("--fixtures", default="fixtures/validated")
    laws.add_argument("--out", default="")
    laws.set_defaults(func=cmd_laws_2a)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
