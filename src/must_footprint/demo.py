"""Command-line demo for reference-boundary tiling."""

from __future__ import annotations

import argparse
from pathlib import Path

from must_footprint.boundary import read_boundary_ecsv
from must_footprint.coverage import build_coverage_grid, summarize_coverage
from must_footprint.plotting import plot_coverage_grid, plot_multi_pass_tiling
from must_footprint.tiling import MultiPassTileTable, generate_multi_pass_tile_centers


def log_verbose(verbose: bool, message: str) -> None:
    """Print a detailed demo message when verbose mode is enabled."""
    if verbose:
        print(message)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a simple MUST demo tiling from the reference DESI boundary ECSV."
    )
    parser.add_argument(
        "--boundary",
        type=Path,
        default=Path("reference/desi1b-20240520-boundaries.ecsv"),
        help="Path to the boundary ECSV file.",
    )
    parser.add_argument("--program", default="BRIGHT", choices=["BRIGHT", "DARK"])
    parser.add_argument("--min-dec", type=float, default=-10.0, help="Minimum tile declination.")
    parser.add_argument(
        "--tile-diameter",
        type=float,
        default=2.56,
        help="Approximate tile diameter in degrees.",
    )
    parser.add_argument(
        "--passes",
        type=int,
        default=3,
        help="Number of deterministic offset observing passes.",
    )
    parser.add_argument(
        "--coverage-resolution",
        type=float,
        default=1.0,
        help="RA/Dec grid resolution in degrees for the coverage QA figure.",
    )
    parser.add_argument(
        "--output-figure",
        type=Path,
        default=Path("outputs/reference_tiling.png"),
        help="Output path for the generated pass-overlay figure.",
    )
    parser.add_argument(
        "--output-coverage-figure",
        type=Path,
        default=Path("outputs/reference_multipass_coverage.png"),
        help="Output path for the generated coverage QA figure.",
    )
    parser.add_argument(
        "--output-tiles",
        type=Path,
        default=Path("outputs/reference_tiles.csv"),
        help="Output path for the generated tile-center table.",
    )
    verbosity = parser.add_mutually_exclusive_group()
    verbosity.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        default=True,
        help="Explain each step of the demo. This is the default.",
    )
    verbosity.add_argument(
        "--quiet",
        dest="verbose",
        action="store_false",
        help="Print only the final result summary.",
    )
    return parser


def write_tile_table(
    path: Path,
    tile_table: MultiPassTileTable,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write("PASS,RA,DEC,CAP\n")
        for pass_index, ra_value, dec_value, cap_value in zip(
            tile_table.pass_index,
            tile_table.ra,
            tile_table.dec,
            tile_table.cap,
            strict=True,
        ):
            file.write(f"{pass_index},{ra_value:.8f},{dec_value:.8f},{cap_value}\n")
    return path


def run_demo(args: argparse.Namespace) -> tuple[Path, Path, Path, int]:
    log_verbose(
        args.verbose,
        "MUST footprint demo: start from a reference sky boundary and build a "
        "preliminary multi-pass tiling pattern.",
    )
    log_verbose(args.verbose, f"Reading boundary points from {args.boundary}.")
    boundaries = read_boundary_ecsv(args.boundary)
    selected = boundaries.select(args.program)
    log_verbose(
        args.verbose,
        f"Selected the {args.program} program with {len(selected):,} boundary points "
        f"across caps: {', '.join(selected.caps())}.",
    )
    log_verbose(
        args.verbose,
        f"Generating {args.passes} observing pass(es) with tile diameter "
        f"{args.tile_diameter:.2f} deg and minimum declination {args.min_dec:.1f} deg.",
    )
    tiles = generate_multi_pass_tile_centers(
        boundaries,
        program=args.program,
        min_dec_deg=args.min_dec,
        tile_diameter_deg=args.tile_diameter,
        pass_count=args.passes,
    )
    pass_counts = {
        pass_index: int((tiles.pass_index == pass_index).sum())
        for pass_index in range(1, args.passes + 1)
    }
    log_verbose(
        args.verbose,
        "The current preliminary strategy keeps pass 1 fixed and creates later "
        "passes by deterministic fractional offsets. Every shifted pass is clipped "
        "back to the same footprint.",
    )
    log_verbose(
        args.verbose,
        "Tile counts by pass: "
        + ", ".join(f"pass {pass_index}: {count:,}" for pass_index, count in pass_counts.items()),
    )
    log_verbose(
        args.verbose,
        f"Building a diagnostic coverage grid with {args.coverage_resolution:.2f} deg sampling.",
    )
    coverage_grid = build_coverage_grid(
        boundaries,
        tiles,
        program=args.program,
        min_dec_deg=args.min_dec,
        resolution_deg=args.coverage_resolution,
    )
    coverage_stats = summarize_coverage(tiles, coverage_grid)
    log_verbose(
        args.verbose,
        "The coverage map counts how many tile disks cover each sampled point. "
        "It is a visual QA diagnostic, not an area-exact spherical survey metric.",
    )
    log_verbose(args.verbose, f"Writing pass-overlay QA figure to {args.output_figure}.")
    figure_path = plot_multi_pass_tiling(
        boundaries,
        tiles,
        program=args.program,
        min_dec_deg=args.min_dec,
        output_path=args.output_figure,
    )
    log_verbose(
        args.verbose,
        f"Writing coverage-count QA figure to {args.output_coverage_figure}.",
    )
    coverage_figure_path = plot_coverage_grid(
        boundaries,
        coverage_grid,
        program=args.program,
        min_dec_deg=args.min_dec,
        output_path=args.output_coverage_figure,
    )
    log_verbose(args.verbose, f"Writing tile table to {args.output_tiles}.")
    tile_path = write_tile_table(args.output_tiles, tiles)
    print(f"Coverage mean: {coverage_stats.mean_coverage:.2f}")
    print(f"Coverage min/max: {coverage_stats.min_coverage}/{coverage_stats.max_coverage}")
    print(f"Target coverage fraction: {coverage_stats.target_coverage_fraction:.3f}")
    return figure_path, coverage_figure_path, tile_path, len(tiles)


def main() -> None:
    args = build_parser().parse_args()
    figure_path, coverage_figure_path, tile_path, tile_count = run_demo(args)
    print(f"Generated {tile_count:,} tile centers")
    print(f"Figure: {figure_path}")
    print(f"Coverage figure: {coverage_figure_path}")
    print(f"Tiles: {tile_path}")


if __name__ == "__main__":
    main()
