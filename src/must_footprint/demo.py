"""Command-line demo for reference-boundary tiling."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from must_footprint.boundary import read_boundary_ecsv
from must_footprint.plotting import plot_reference_tiling
from must_footprint.tiling import generate_tile_centers


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
        "--output-figure",
        type=Path,
        default=Path("outputs/reference_tiling.png"),
        help="Output path for the generated figure.",
    )
    parser.add_argument(
        "--output-tiles",
        type=Path,
        default=Path("outputs/reference_tiles.csv"),
        help="Output path for the generated tile-center table.",
    )
    return parser


def write_tile_table(
    path: Path,
    tile_ra: np.ndarray,
    tile_dec: np.ndarray,
    tile_cap: np.ndarray,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        file.write("RA,DEC,CAP\n")
        for ra_value, dec_value, cap_value in zip(tile_ra, tile_dec, tile_cap, strict=True):
            file.write(f"{ra_value:.8f},{dec_value:.8f},{cap_value}\n")
    return path


def run_demo(args: argparse.Namespace) -> tuple[Path, Path, int]:
    boundaries = read_boundary_ecsv(args.boundary)
    tiles = generate_tile_centers(
        boundaries,
        program=args.program,
        min_dec_deg=args.min_dec,
        tile_diameter_deg=args.tile_diameter,
    )
    figure_path = plot_reference_tiling(
        boundaries,
        tiles,
        program=args.program,
        min_dec_deg=args.min_dec,
        output_path=args.output_figure,
    )
    tile_path = write_tile_table(args.output_tiles, tiles.ra, tiles.dec, tiles.cap)
    return figure_path, tile_path, len(tiles)


def main() -> None:
    args = build_parser().parse_args()
    figure_path, tile_path, tile_count = run_demo(args)
    print(f"Generated {tile_count:,} tile centers")
    print(f"Figure: {figure_path}")
    print(f"Tiles: {tile_path}")


if __name__ == "__main__":
    main()
