# MUST Footprint Demo Specification

This repository is a first formal demo for designing the MUST survey footprint and focal-plane tiling on the sky.

## Current Scope

- Read the reference DESI boundary ECSV file in `reference/desi1b-20240520-boundaries.ecsv`.
- Select one observing program, currently `BRIGHT` by default.
- Treat the `NGC` and `SGC` boundary point sequences as two sky polygons in right ascension and declination.
- Generate one or more simple hex-spaced passes of tile centers inside those polygons.
- Apply a minimum declination limit of `Dec >= -10 deg` by default.
- Save QA figures and a CSV table of tile centers.

## Current Non-Goals

- This demo does not optimize survey strategy.
- Multi-pass mode uses deterministic offsets rather than a true optimized survey strategy.
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

## Multi-Pass Mode

- `--passes` controls the number of observing passes and defaults to `3`.
- Pass 1 uses the current reference tiling.
- Later passes use deterministic fractional RA/Dec offsets derived from the tile spacing.
- Shifted tile centers are clipped back to the same footprint and minimum declination.
- The tile CSV uses `PASS,RA,DEC,CAP`, with 1-based pass IDs.
- The pass overlay QA figure shows all pass centers over the footprint.
- The coverage QA figure samples the footprint on a regular RA/Dec grid and counts how many tile disks cover each sample point.
- The coverage grid is a diagnostic only; it is not an area-exact spherical coverage calculation.

## Expected Demo Command

```bash
uv run must-footprint-demo
```

Expected outputs:

- `outputs/reference_tiling.png`
- `outputs/reference_tiles.csv`
- `outputs/reference_multipass_coverage.png`
