"""Plotting helpers for the MUST footprint demo."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from must_footprint.boundary import BoundaryTable
from must_footprint.tiling import TileTable


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

    selected = boundary_table.select(program)

    fig, ax = plt.subplots(figsize=(12, 6), constrained_layout=True)
    cap_colors = {"NGC": "#3b82f6", "SGC": "#f97316"}

    for cap in selected.caps():
        cap_boundary = selected.select(program, cap)
        color = cap_colors.get(cap, "#64748b")
        ax.fill(
            cap_boundary.ra,
            cap_boundary.dec,
            color=color,
            alpha=0.12,
            linewidth=0,
            label=f"{program.upper()} {cap} boundary",
        )
        ax.plot(cap_boundary.ra, cap_boundary.dec, color=color, linewidth=1.2)

    ax.scatter(
        tile_table.ra,
        tile_table.dec,
        s=8,
        c="#111827",
        alpha=0.72,
        linewidths=0,
        label=f"{len(tile_table):,} tile centers",
    )
    ax.axhline(min_dec_deg, color="#6b7280", linewidth=1.0, linestyle="--", label="Dec limit")

    ax.set_title("MUST demo tiling over the DESI bright-source boundary")
    ax.set_xlabel("Right ascension [deg]")
    ax.set_ylabel("Declination [deg]")
    ax.set_xlim(float(np.min(selected.ra)) - 5, float(np.max(selected.ra)) + 5)
    ax.set_ylim(min_dec_deg - 5, float(np.max(selected.dec)) + 5)
    ax.grid(True, color="#e5e7eb", linewidth=0.8)
    ax.legend(loc="lower left", fontsize=9, frameon=True)
    ax.invert_xaxis()

    fig.savefig(output_path, dpi=180)
    plt.close(fig)
    return output_path
