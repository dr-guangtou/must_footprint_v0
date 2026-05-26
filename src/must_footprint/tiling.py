"""Simple tile-center generation for the demo footprint."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from matplotlib.path import Path

from must_footprint.boundary import BoundaryTable


@dataclass(frozen=True)
class TileTable:
    """Tile centers generated inside a survey boundary."""

    ra: np.ndarray
    dec: np.ndarray
    cap: np.ndarray
    diameter_deg: float

    def as_array(self) -> np.ndarray:
        """Return tile rows as ``RA, DEC`` numeric columns."""
        return np.column_stack([self.ra, self.dec])

    def __len__(self) -> int:
        return len(self.ra)


@dataclass(frozen=True)
class MultiPassTileTable:
    """Tile centers generated for one or more observing passes."""

    ra: np.ndarray
    dec: np.ndarray
    cap: np.ndarray
    pass_index: np.ndarray
    diameter_deg: float

    def as_array(self) -> np.ndarray:
        """Return tile rows as ``PASS, RA, DEC`` numeric columns."""
        return np.column_stack([self.pass_index, self.ra, self.dec])

    def select_pass(self, pass_index: int) -> TileTable:
        """Return one observing pass as a single-pass tile table."""
        mask = self.pass_index == pass_index
        return TileTable(
            ra=self.ra[mask],
            dec=self.dec[mask],
            cap=self.cap[mask],
            diameter_deg=self.diameter_deg,
        )

    def __len__(self) -> int:
        return len(self.ra)


def make_boundary_path(boundary: BoundaryTable) -> Path:
    """Create a closed matplotlib path from a cap boundary."""
    points = boundary.as_points()
    if len(points) < 3:
        raise ValueError("A footprint cap needs at least three boundary points")

    if not np.allclose(points[0], points[-1]):
        points = np.vstack([points, points[0]])

    return Path(points, closed=True)


def _generate_cap_tile_centers(
    cap_boundary: BoundaryTable,
    *,
    min_dec_deg: float,
    tile_diameter_deg: float,
    ra_offset_fraction: float,
    dec_offset_fraction: float,
) -> tuple[np.ndarray, np.ndarray]:
    path = make_boundary_path(cap_boundary)

    min_ra = float(np.min(cap_boundary.ra))
    max_ra = float(np.max(cap_boundary.ra))
    min_dec = max(float(np.min(cap_boundary.dec)), min_dec_deg)
    max_dec = float(np.max(cap_boundary.dec))
    dec_spacing = tile_diameter_deg * np.sqrt(3.0) / 2.0

    dec_start = min_dec + dec_offset_fraction * dec_spacing
    dec_rows = np.arange(dec_start, max_dec + dec_spacing, dec_spacing)
    cap_ra_values: list[np.ndarray] = []
    cap_dec_values: list[np.ndarray] = []

    for row_index, dec_value in enumerate(dec_rows):
        cos_dec = max(float(np.cos(np.deg2rad(dec_value))), 0.05)
        ra_spacing = tile_diameter_deg / cos_dec
        parity_offset = 0.5 * ra_spacing if row_index % 2 else 0.0
        row_start = min_ra + parity_offset + ra_offset_fraction * ra_spacing
        ra_values = np.arange(row_start, max_ra + ra_spacing, ra_spacing)
        dec_values = np.full_like(ra_values, dec_value, dtype=float)
        points = np.column_stack([ra_values, dec_values])
        inside = path.contains_points(points)

        if np.any(inside):
            cap_ra_values.append(ra_values[inside])
            cap_dec_values.append(dec_values[inside])

    if not cap_ra_values:
        return np.asarray([], dtype=float), np.asarray([], dtype=float)

    return np.concatenate(cap_ra_values), np.concatenate(cap_dec_values)


def generate_tile_centers(
    boundary_table: BoundaryTable,
    *,
    program: str = "BRIGHT",
    min_dec_deg: float = -10.0,
    tile_diameter_deg: float = 2.56,
) -> TileTable:
    """Generate simple hex-spaced tile centers inside each cap.

    This is intentionally a first working approximation. It places tile centers
    on rows separated by the flat-sky hex-grid spacing, adjusts the RA spacing
    by ``cos(dec)``, and keeps centers that fall inside the reference boundary.
    """
    selected = boundary_table.select(program)
    if len(selected) == 0:
        raise ValueError(f"No rows found for program {program!r}")

    all_ra: list[np.ndarray] = []
    all_dec: list[np.ndarray] = []
    all_caps: list[np.ndarray] = []

    for cap in selected.caps():
        cap_boundary = selected.select(program, cap)
        cap_ra, cap_dec = _generate_cap_tile_centers(
            cap_boundary,
            min_dec_deg=min_dec_deg,
            tile_diameter_deg=tile_diameter_deg,
            ra_offset_fraction=0.0,
            dec_offset_fraction=0.0,
        )
        if len(cap_ra):
            all_ra.append(cap_ra)
            all_dec.append(cap_dec)
            all_caps.append(np.full(cap_ra.shape, cap))

    if not all_ra:
        raise ValueError("No tile centers were generated inside the selected footprint")

    ra = np.concatenate(all_ra)
    dec = np.concatenate(all_dec)
    cap = np.concatenate(all_caps)
    order = np.lexsort((ra, dec, cap))

    return TileTable(
        ra=ra[order],
        dec=dec[order],
        cap=cap[order],
        diameter_deg=tile_diameter_deg,
    )


def pass_offset_fractions(pass_index: int, pass_count: int) -> tuple[float, float]:
    """Return deterministic offset fractions for one 1-based observing pass."""
    if pass_count < 1:
        raise ValueError("pass_count must be at least 1")

    zero_based_index = pass_index - 1
    if zero_based_index < 0 or zero_based_index >= pass_count:
        raise ValueError("pass_index must be between 1 and pass_count")

    if pass_count == 1:
        return 0.0, 0.0

    dec_step_multiplier = 2 if pass_count % 2 else pass_count - 1
    return (zero_based_index % pass_count) / pass_count, (
        (zero_based_index * dec_step_multiplier) % pass_count
    ) / pass_count


def generate_multi_pass_tile_centers(
    boundary_table: BoundaryTable,
    *,
    program: str = "BRIGHT",
    min_dec_deg: float = -10.0,
    tile_diameter_deg: float = 2.56,
    pass_count: int = 3,
) -> MultiPassTileTable:
    """Generate deterministic offset tiling patterns for multiple passes."""
    selected = boundary_table.select(program)
    if len(selected) == 0:
        raise ValueError(f"No rows found for program {program!r}")
    if pass_count < 1:
        raise ValueError("pass_count must be at least 1")

    all_ra: list[np.ndarray] = []
    all_dec: list[np.ndarray] = []
    all_caps: list[np.ndarray] = []
    all_passes: list[np.ndarray] = []

    for pass_index in range(1, pass_count + 1):
        ra_offset_fraction, dec_offset_fraction = pass_offset_fractions(pass_index, pass_count)

        for cap in selected.caps():
            cap_boundary = selected.select(program, cap)
            cap_ra, cap_dec = _generate_cap_tile_centers(
                cap_boundary,
                min_dec_deg=min_dec_deg,
                tile_diameter_deg=tile_diameter_deg,
                ra_offset_fraction=ra_offset_fraction,
                dec_offset_fraction=dec_offset_fraction,
            )
            if len(cap_ra):
                all_ra.append(cap_ra)
                all_dec.append(cap_dec)
                all_caps.append(np.full(cap_ra.shape, cap))
                all_passes.append(np.full(cap_ra.shape, pass_index, dtype=int))

    if not all_ra:
        raise ValueError("No tile centers were generated inside the selected footprint")

    ra = np.concatenate(all_ra)
    dec = np.concatenate(all_dec)
    cap = np.concatenate(all_caps)
    pass_index = np.concatenate(all_passes)
    order = np.lexsort((ra, dec, cap, pass_index))

    return MultiPassTileTable(
        ra=ra[order],
        dec=dec[order],
        cap=cap[order],
        pass_index=pass_index[order],
        diameter_deg=tile_diameter_deg,
    )
