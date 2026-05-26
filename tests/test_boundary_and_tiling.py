from pathlib import Path

import numpy as np

from must_footprint.boundary import read_boundary_ecsv
from must_footprint.tiling import generate_tile_centers, make_boundary_path

REFERENCE_BOUNDARY = Path("reference/desi1b-20240520-boundaries.ecsv")


def test_read_boundary_ecsv_counts_reference_rows() -> None:
    boundaries = read_boundary_ecsv(REFERENCE_BOUNDARY)

    assert len(boundaries) == 5314
    assert len(boundaries.select("BRIGHT")) == 2656
    assert len(boundaries.select("DARK")) == 2658
    assert boundaries.select("BRIGHT").caps() == ("NGC", "SGC")


def test_generate_tile_centers_stays_inside_boundary_and_above_dec_limit() -> None:
    boundaries = read_boundary_ecsv(REFERENCE_BOUNDARY)
    tiles = generate_tile_centers(boundaries, tile_diameter_deg=12.0, min_dec_deg=-10.0)

    assert len(tiles) > 0
    assert np.all(tiles.dec >= -10.0)

    for cap in np.unique(tiles.cap):
        path = make_boundary_path(boundaries.select("BRIGHT", str(cap)))
        cap_mask = tiles.cap == cap
        cap_points = np.column_stack([tiles.ra[cap_mask], tiles.dec[cap_mask]])
        assert np.all(path.contains_points(cap_points))
