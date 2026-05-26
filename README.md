# must_footprint_v0

Preliminary package for designing the MUST survey footprint and focal-plane tiling strategy.

## Demo

Run the first reference-boundary tiling demo with:

```bash
uv run must-footprint-demo
```

This reads `reference/desi1b-20240520-boundaries.ecsv`, generates three observing passes by default, and writes:

- `outputs/reference_tiling.png`
- `outputs/reference_tiles.csv`
- `outputs/reference_multipass_coverage.png`

Use `--passes 1` to reproduce a single-pass tiling table and figure.

For a funding-review style walkthrough with detailed terminal explanation, run:

```bash
uv run python scripts/run_review_demo.py
```

Build the review PDF with:

```bash
uv run python scripts/build_review_pdf.py
```

The source document is `docs/review.md`, and the generated PDF is `docs/review.pdf`.

## Optional Dependencies

The default install is intentionally small and supports the current demo.

Use these extras when a feature needs them:

```bash
uv sync --extra astro
uv sync --extra background-map
uv sync --extra fits-density
uv sync --extra skygrid
```

- `astro`: `astropy` and `shapely` for coordinate transforms, ECSV I/O, and real polygon operations.
- `background-map`: `reproject` and `scipy` for the optional Gaia Milky Way stellar-density image.
- `fits-density`: `fitsio` and `healpy` for the older commented FITS stellar-density path.
- `skygrid`: `m4opt` for geodesic sky-grid tiling. This works, but it is much heavier than the other extras.
