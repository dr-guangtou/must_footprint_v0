from pathlib import Path

import numpy as np

from must_footprint.boundary import read_boundary_ecsv
from must_footprint.coverage import build_coverage_grid, summarize_coverage
from must_footprint.tiling import (
    generate_multi_pass_tile_centers,
    generate_tile_centers,
    make_boundary_path,
    pass_offset_fractions,
)

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


def test_generate_multi_pass_tile_centers_is_deterministic_and_clipped() -> None:
    boundaries = read_boundary_ecsv(REFERENCE_BOUNDARY)
    first_tiles = generate_multi_pass_tile_centers(
        boundaries,
        tile_diameter_deg=12.0,
        min_dec_deg=-10.0,
        pass_count=3,
    )
    second_tiles = generate_multi_pass_tile_centers(
        boundaries,
        tile_diameter_deg=12.0,
        min_dec_deg=-10.0,
        pass_count=3,
    )

    assert np.array_equal(first_tiles.pass_index, second_tiles.pass_index)
    assert np.allclose(first_tiles.ra, second_tiles.ra)
    assert np.allclose(first_tiles.dec, second_tiles.dec)
    assert set(np.unique(first_tiles.pass_index)) == {1, 2, 3}
    assert np.all(first_tiles.dec >= -10.0)

    for cap in np.unique(first_tiles.cap):
        path = make_boundary_path(boundaries.select("BRIGHT", str(cap)))
        cap_mask = first_tiles.cap == cap
        cap_points = np.column_stack([first_tiles.ra[cap_mask], first_tiles.dec[cap_mask]])
        assert np.all(path.contains_points(cap_points))


def test_coverage_grid_counts_are_valid_inside_footprint() -> None:
    boundaries = read_boundary_ecsv(REFERENCE_BOUNDARY)
    tiles = generate_multi_pass_tile_centers(
        boundaries,
        tile_diameter_deg=12.0,
        min_dec_deg=-10.0,
        pass_count=3,
    )
    coverage_grid = build_coverage_grid(
        boundaries,
        tiles,
        min_dec_deg=-10.0,
        resolution_deg=5.0,
    )
    stats = summarize_coverage(tiles, coverage_grid)

    assert np.any(coverage_grid.footprint_mask)
    assert np.all(coverage_grid.valid_coverage >= 0)
    assert stats.total_tiles == len(tiles)
    assert set(stats.tile_counts_by_pass) == {1, 2, 3}
    assert stats.max_coverage >= 1


def test_pass_offset_fractions_vary_for_even_pass_count() -> None:
    offsets = [pass_offset_fractions(pass_index, 2) for pass_index in [1, 2]]

    assert offsets == [(0.0, 0.0), (0.5, 0.5)]
