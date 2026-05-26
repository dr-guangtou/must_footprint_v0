"""Plotting helpers for the MUST footprint demo."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from must_footprint.boundary import BoundaryTable
from must_footprint.coverage import CoverageGrid
from must_footprint.tiling import MultiPassTileTable, TileTable


def _plot_boundaries(
    ax: plt.Axes,
    boundary_table: BoundaryTable,
    *,
    program: str,
    min_dec_deg: float,
) -> None:
    selected = boundary_table.select(program)
    cap_colors = {"NGC": "#3b82f6", "SGC": "#f97316"}

    for cap in selected.caps():
        cap_boundary = selected.select(program, cap)
        color = cap_colors.get(cap, "#64748b")
        ax.fill(
            cap_boundary.ra,
            cap_boundary.dec,
            color=color,
            alpha=0.10,
            linewidth=0,
            label=f"{program.upper()} {cap} boundary",
        )
        ax.plot(cap_boundary.ra, cap_boundary.dec, color=color, linewidth=1.2)

    ax.axhline(min_dec_deg, color="#6b7280", linewidth=1.0, linestyle="--", label="Dec limit")
    ax.set_xlabel("Right ascension [deg]")
    ax.set_ylabel("Declination [deg]")
    ax.set_xlim(float(np.min(selected.ra)) - 5, float(np.max(selected.ra)) + 5)
    ax.set_ylim(min_dec_deg - 5, float(np.max(selected.dec)) + 5)
    ax.grid(True, color="#e5e7eb", linewidth=0.8)
    ax.invert_xaxis()


def plot_reference_tiling(
    boundary_table: BoundaryTable,
    tile_table: TileTable,
    *,
    program: str,
    min_dec_deg: float,
    output_path: str | Path,
) -> Path:
    """Save a simple figure showing the reference footprint and tile centers."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    _plot_boundaries(ax, boundary_table, program=program, min_dec_deg=min_dec_deg)

    ax.scatter(
        tile_table.ra,
        tile_table.dec,
        s=8,
        c="#111827",
        alpha=0.72,
        linewidths=0,
        label=f"{len(tile_table):,} tile centers",
    )

    ax.set_title("MUST demo tiling over the DESI bright-source boundary")
    ax.legend(loc="lower left", fontsize=9, frameon=True)

    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path


def plot_multi_pass_tiling(
    boundary_table: BoundaryTable,
    tile_table: MultiPassTileTable,
    *,
    program: str,
    min_dec_deg: float,
    output_path: str | Path,
) -> Path:
    """Save a pass-overlay QA figure for a multi-pass tiling demo."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    _plot_boundaries(ax, boundary_table, program=program, min_dec_deg=min_dec_deg)

    pass_values = np.unique(tile_table.pass_index)
    color_map = plt.get_cmap("tab10")
    for color_index, pass_index in enumerate(pass_values):
        mask = tile_table.pass_index == pass_index
        ax.scatter(
            tile_table.ra[mask],
            tile_table.dec[mask],
            s=8,
            color=color_map(color_index % 10),
            alpha=0.62,
            linewidths=0,
            label=f"Pass {pass_index}: {np.count_nonzero(mask):,} tiles",
        )

    ax.set_title(f"MUST demo multi-pass tiling ({len(pass_values)} passes)")
    ax.legend(loc="lower left", fontsize=8, frameon=True, ncol=2)

    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path


def plot_coverage_grid(
    boundary_table: BoundaryTable,
    coverage_grid: CoverageGrid,
    *,
    program: str,
    min_dec_deg: float,
    output_path: str | Path,
) -> Path:
    """Save a coverage-count QA figure for a multi-pass tiling demo."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    coverage = np.ma.masked_where(~coverage_grid.footprint_mask, coverage_grid.coverage)
    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    mesh = ax.pcolormesh(
        coverage_grid.ra,
        coverage_grid.dec,
        coverage,
        cmap="viridis",
        shading="nearest",
    )
    _plot_boundaries(ax, boundary_table, program=program, min_dec_deg=min_dec_deg)
    colorbar = fig.colorbar(mesh, ax=ax)
    colorbar.set_label("Tile-disk coverage count")
    ax.set_title("MUST demo multi-pass coverage QA")

    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path
