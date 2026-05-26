# TODO

## Current Task: Make the Reference Boundary Tiling Demo Work

- [x] Check repository state and move work off `main`.
- [x] Review the reference script and ECSV file.
- [x] Add a small package structure for reusable demo code.
- [x] Keep `reference/preprocess_tiles.py` runnable as a wrapper.
- [x] Install dependencies with `uv`.
- [x] Run tests.
- [x] Run the demo and confirm it writes a figure and tile table.

## Current Task: Add Preliminary Multi-Pass Mode

- [x] Define preliminary multi-pass behavior in the spec.
- [x] Add deterministic multi-pass tiling structures and generation.
- [x] Add coverage QA calculation and figures.
- [x] Extend the command-line demo and CSV output.
- [x] Add tests for multi-pass generation and coverage QA.
- [x] Run linting, tests, and the multi-pass demo command.

## Review

- Multi-pass mode now defaults to three deterministic offset passes.
- The demo writes a pass-overlay figure, a coverage-count QA figure, and one CSV with `PASS,RA,DEC,CAP`.
- The coverage map is a regular-grid diagnostic, not an area-exact spherical coverage metric.

## Current Task: Add Funding Review Demo and Documentation

- [x] Add verbose mode to the demo workflow, enabled by default.
- [x] Add a one-command review demo script.
- [x] Add `docs/review.md` for a non-specialist funding review audience.
- [x] Generate `docs/review.pdf`.
- [x] Run linting, tests, the review demo, and the PDF build.

## Review

- The review demo can be run with `uv run python scripts/run_review_demo.py`.
- The default review demo is verbose and writes pass-overlay and coverage QA figures under `outputs/review_demo/`.
- The review document source is `docs/review.md`; the generated PDF is `docs/review.pdf`.

## Review

- The original reference script could not run from this checkout because it expected external files under `../data/raw/tiles/` and imported astronomy packages not declared by the repo.
- The first working demo now reads the included ECSV boundary directly, generates simple tile centers, and writes `outputs/reference_tiling.png` plus `outputs/reference_tiles.csv`.
- The compatibility command `uv run python reference/preprocess_tiles.py` also works.
- Optional dependencies are split by feature: `astro`, `background-map`, `fits-density`, and `skygrid`.
- `m4opt` installed successfully, but it pulled in a broad dependency stack, so it is separated into the `skygrid` extra.
