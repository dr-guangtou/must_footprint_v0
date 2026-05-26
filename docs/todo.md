# TODO

## Current Task: Make the Reference Boundary Tiling Demo Work

- [x] Check repository state and move work off `main`.
- [x] Review the reference script and ECSV file.
- [x] Add a small package structure for reusable demo code.
- [x] Keep `reference/preprocess_tiles.py` runnable as a wrapper.
- [x] Install dependencies with `uv`.
- [x] Run tests.
- [x] Run the demo and confirm it writes a figure and tile table.

## Review

- The original reference script could not run from this checkout because it expected external files under `../data/raw/tiles/` and imported astronomy packages not declared by the repo.
- The first working demo now reads the included ECSV boundary directly, generates simple tile centers, and writes `outputs/reference_tiling.png` plus `outputs/reference_tiles.csv`.
- The compatibility command `uv run python reference/preprocess_tiles.py` also works.
- Optional dependencies are split by feature: `astro`, `background-map`, `fits-density`, and `skygrid`.
- `m4opt` installed successfully, but it pulled in a broad dependency stack, so it is separated into the `skygrid` extra.
