from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import run_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic CLI companion demo for Narrative Coupling."
    )
    parser.add_argument(
        "--stream",
        choices=("neutral", "break", "all"),
        default="neutral",
        help="Which event stream to replay.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        help="Optional path for structured JSON trace output.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output when --json-out is used.",
    )
    return parser


def format_totals(totals: dict[str, float]) -> str:
    return ", ".join(f"{theme}={value:.3f}" for theme, value in totals.items())


def print_summary(results: dict[str, list]) -> None:
    for stream_name, runs in results.items():
        print(f"=== stream: {stream_name} ===")
        for run in runs:
            progression = " -> ".join(step.dominant_theme for step in run.steps)
            print(f"profile: {run.profile_name}")
            print(f"progression: {progression}")
            print(f"final totals: {format_totals(run.final_theme_totals)}")
            print(f"final dominant: {run.final_dominant_theme}")
            print(f"summary: {run.interpretation_summary}")
            print()


def write_json(results: dict[str, list], output_path: Path, pretty: bool) -> None:
    payload = {
        stream_name: [run.to_dict() for run in runs]
        for stream_name, runs in results.items()
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2 if pretty else None, sort_keys=pretty)
        handle.write("\n")


def main() -> None:
    args = build_parser().parse_args()
    results = run_demo(args.stream)
    print_summary(results)
    if args.json_out:
        write_json(results, args.json_out, args.pretty)
        print(f"json trace written to: {args.json_out}")


if __name__ == "__main__":
    main()
