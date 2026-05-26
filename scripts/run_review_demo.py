#!/usr/bin/env python3
"""Run the funding-review multi-pass footprint demo in one terminal command."""

from __future__ import annotations

import argparse
from argparse import Namespace
from pathlib import Path

from must_footprint.demo import run_demo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the verbose multi-pass MUST footprint review demo."
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs/review_demo"),
        help="Directory for review-demo QA figures and tile table.",
    )
    parser.add_argument("--passes", type=int, default=3)
    parser.add_argument("--coverage-resolution", type=float, default=1.0)
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Disable detailed step-by-step explanation.",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    demo_args = Namespace(
        boundary=Path("reference/desi1b-20240520-boundaries.ecsv"),
        program="BRIGHT",
        min_dec=-10.0,
        tile_diameter=2.56,
        passes=args.passes,
        coverage_resolution=args.coverage_resolution,
        output_figure=output_dir / "review_demo_pass_overlay.png",
        output_coverage_figure=output_dir / "review_demo_coverage.png",
        output_tiles=output_dir / "review_demo_tiles.csv",
        verbose=not args.quiet,
    )

    if demo_args.verbose:
        print("Review demo output directory:", output_dir)
        print("This script runs the complete current workflow and writes QA figures.")

    figure_path, coverage_figure_path, tile_path, tile_count = run_demo(demo_args)

    print("Review demo complete.")
    print(f"Generated {tile_count:,} tile centers.")
    print(f"Pass-overlay QA figure: {figure_path}")
    print(f"Coverage QA figure: {coverage_figure_path}")
    print(f"Tile table: {tile_path}")


if __name__ == "__main__":
    main()
