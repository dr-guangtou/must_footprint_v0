# MUST Footprint Demo Specification

This repository is a first formal demo for designing the MUST survey footprint and focal-plane tiling on the sky.

## Current Scope

- Read the reference DESI boundary ECSV file in `reference/desi1b-20240520-boundaries.ecsv`.
- Select one observing program, currently `BRIGHT` by default.
- Treat the `NGC` and `SGC` boundary point sequences as two sky polygons in right ascension and declination.
- Generate a simple hex-spaced set of tile centers inside those polygons.
- Apply a minimum declination limit of `Dec >= -10 deg` by default.
- Save a figure and a CSV table of tile centers.

## Current Non-Goals

- This demo does not optimize survey strategy.
- This demo does not model fiber assignment, target priority, weather, airmass, moon avoidance, cadence, or focal-plane tilt.
- This demo does not use the richer stellar-density background processing in the original reference script.

## Dependency Policy

- Default dependencies stay small: `numpy` and `matplotlib`.
- The `astro` extra is for near-term astronomy geometry work: `astropy` and `shapely`.
- The `background-map` extra is for optional Gaia stellar-density image reprojection.
- The `fits-density` extra is for the older commented FITS stellar-density path.
- The `skygrid` extra is for `m4opt`. It installed successfully in this environment, but it pulls in a much larger scientific stack, so it should stay optional until the package needs geodesic sky-grid tiling.

## Architecture

- `src/must_footprint/boundary.py` reads and filters boundary data.
- `src/must_footprint/tiling.py` generates tile centers.
- `src/must_footprint/plotting.py` creates the demo figure.
- `src/must_footprint/demo.py` provides the command-line workflow.
- `reference/preprocess_tiles.py` is kept as a compatibility wrapper so the original reference command remains runnable.

## Expected Demo Command

```bash
uv run must-footprint-demo
```

Expected outputs:

- `outputs/reference_tiling.png`
- `outputs/reference_tiles.csv`
