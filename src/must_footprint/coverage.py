"""Coverage diagnostics for multi-pass tiling demos."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from must_footprint.boundary import BoundaryTable
from must_footprint.tiling import MultiPassTileTable, make_boundary_path


@dataclass(frozen=True)
class CoverageGrid:
    """Regular-grid diagnostic coverage counts over the selected footprint."""

    ra: np.ndarray
    dec: np.ndarray
    coverage: np.ndarray
    footprint_mask: np.ndarray
    target_pass_count: int

    @property
    def valid_coverage(self) -> np.ndarray:
        """Return coverage values inside the footprint."""
        return self.coverage[self.footprint_mask]


@dataclass(frozen=True)
class CoverageStats:
    """Summary numbers for a coverage QA grid."""

    total_tiles: int
    tile_counts_by_pass: dict[int, int]
    mean_coverage: float
    min_coverage: int
    max_coverage: int
    target_coverage_fraction: float


def build_coverage_grid(
    boundary_table: BoundaryTable,
    tile_table: MultiPassTileTable,
    *,
    program: str = "BRIGHT",
    min_dec_deg: float = -10.0,
    resolution_deg: float = 1.0,
    chunk_size: int = 128,
) -> CoverageGrid:
    """Count tile-disk coverage on a regular RA/Dec diagnostic grid."""
    if resolution_deg <= 0:
        raise ValueError("resolution_deg must be positive")
    if chunk_size < 1:
        raise ValueError("chunk_size must be at least 1")

    selected = boundary_table.select(program)
    if len(selected) == 0:
        raise ValueError(f"No rows found for program {program!r}")

    min_ra = float(np.min(selected.ra))
    max_ra = float(np.max(selected.ra))
    min_dec = max(float(np.min(selected.dec)), min_dec_deg)
    max_dec = float(np.max(selected.dec))

    ra_values = np.arange(min_ra, max_ra + 0.5 * resolution_deg, resolution_deg)
    dec_values = np.arange(min_dec, max_dec + 0.5 * resolution_deg, resolution_deg)
    ra_grid, dec_grid = np.meshgrid(ra_values, dec_values)
    points = np.column_stack([ra_grid.ravel(), dec_grid.ravel()])

    footprint_mask = np.zeros(points.shape[0], dtype=bool)
    for cap in selected.caps():
        path = make_boundary_path(selected.select(program, cap))
        footprint_mask |= path.contains_points(points)

    valid_ra = points[footprint_mask, 0]
    valid_dec = points[footprint_mask, 1]
    valid_counts = np.zeros(valid_ra.shape, dtype=int)
    cos_dec = np.cos(np.deg2rad(valid_dec))
    radius_deg = tile_table.diameter_deg / 2.0
    radius_squared = radius_deg * radius_deg

    for start in range(0, len(tile_table), chunk_size):
        end = start + chunk_size
        delta_ra = (valid_ra[:, np.newaxis] - tile_table.ra[start:end]) * cos_dec[:, np.newaxis]
        delta_dec = valid_dec[:, np.newaxis] - tile_table.dec[start:end]
        valid_counts += np.count_nonzero(
            delta_ra * delta_ra + delta_dec * delta_dec <= radius_squared,
            axis=1,
        )

    coverage = np.full(points.shape[0], -1, dtype=int)
    coverage[footprint_mask] = valid_counts

    return CoverageGrid(
        ra=ra_values,
        dec=dec_values,
        coverage=coverage.reshape(dec_grid.shape),
        footprint_mask=footprint_mask.reshape(dec_grid.shape),
        target_pass_count=int(np.max(tile_table.pass_index)),
    )


def summarize_coverage(
    tile_table: MultiPassTileTable,
    coverage_grid: CoverageGrid,
) -> CoverageStats:
    """Summarize tile counts and coverage uniformity for QA output."""
    valid_coverage = coverage_grid.valid_coverage
    if len(valid_coverage) == 0:
        raise ValueError("Coverage grid has no valid footprint samples")

    unique_passes, pass_counts = np.unique(tile_table.pass_index, return_counts=True)
    tile_counts_by_pass = {
        int(pass_index): int(pass_count)
        for pass_index, pass_count in zip(unique_passes, pass_counts, strict=True)
    }

    return CoverageStats(
        total_tiles=len(tile_table),
        tile_counts_by_pass=tile_counts_by_pass,
        mean_coverage=float(np.mean(valid_coverage)),
        min_coverage=int(np.min(valid_coverage)),
        max_coverage=int(np.max(valid_coverage)),
        target_coverage_fraction=float(
            np.mean(valid_coverage == coverage_grid.target_pass_count)
        ),
    )
