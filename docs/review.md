# MUST Footprint Design Demo Review

## Purpose

This document introduces the current development demo for the MUST survey footprint design package. It is written for a funding review audience that may not already know the survey strategy context or the software structure.

The current repository is still a preliminary demo. Its purpose is to show that we have a formal and testable foundation for turning a survey boundary on the sky into a repeatable set of telescope pointings, then evaluating the result with clear QA figures.

## Survey Footprint Design Procedure

A spectroscopic survey needs to decide where the telescope should point on the sky. Each pointing covers a limited field of view. A footprint design tool starts from a survey boundary and turns it into a list of tile centers. Each tile center is one planned telescope pointing.

The basic procedure in this demo is:

1. Read a reference sky boundary from an ECSV file.
2. Select one survey program. The default is the `BRIGHT` program.
3. Treat the two boundary caps, `NGC` and `SGC`, as sky regions that should be tiled.
4. Generate tile centers on a simple hex-like pattern.
5. Remove tile centers outside the selected footprint or below the minimum declination limit.
6. Repeat the pattern with deterministic offsets to represent multiple observing passes.
7. Create QA figures so the design can be visually checked.

This is not yet an optimized survey strategy engine. The current multi-pass pattern is intentionally simple. It creates the software structure and visual diagnostics needed before adding more sophisticated optimization.

## Why Multi-Pass Mode Matters

Real spectroscopic surveys usually observe a region more than once. Multiple passes help improve completeness, allow repeated observations, and reduce gaps caused by field geometry or operational constraints.

For a practical survey design, two goals matter:

- Efficiency: use as few tiles as possible for one pass while still covering the footprint.
- Uniformity: after `N` passes, most of the footprint should be covered close to `N` times, with less area under-covered or over-covered.

The current demo does not solve the full optimization problem. Instead, it provides a first multi-pass mode that can be inspected visually and tested automatically.

## Current Demo Workflow

The one-command review demo is:

```bash
uv run python scripts/run_review_demo.py
```

By default, the script runs in verbose mode. It explains each step in the terminal:

- Which boundary file is being read.
- Which program and sky caps are selected.
- How many observing passes are being generated.
- How the current offset-pass strategy works.
- How the coverage QA map is calculated.
- Where the resulting files are written.

The default demo creates three observing passes. Pass 1 uses the base tiling. Later passes are shifted by deterministic fractional offsets and clipped back to the same sky footprint. This keeps the result reproducible and easy to compare across code changes.

## Demo Outputs

The review demo writes its outputs under `outputs/review_demo/`:

- `review_demo_pass_overlay.png`: a QA map showing the footprint boundary and tile centers for each pass in different colors.
- `review_demo_coverage.png`: a QA map showing how many tile disks cover each sampled point in the footprint.
- `review_demo_tiles.csv`: the tile table with columns `PASS,RA,DEC,CAP`.

The coverage map is a diagnostic grid. It is useful for seeing broad under-covered or over-covered regions, but it is not yet an area-exact spherical survey metric.

![Pass-overlay QA figure](../outputs/review_demo/review_demo_pass_overlay.png)

![Coverage-count QA figure](../outputs/review_demo/review_demo_coverage.png)

## Current Interpretation

The current default demo generates three passes. The expected result is a dense overlay of three offset tile patterns across both the NGC and SGC regions. The coverage QA figure should show that most of the footprint is close to the target three-pass coverage, while some edge regions and overlap regions can have lower or higher counts.

This behavior is acceptable for the current development stage. The important result is that the package can now represent multiple observing passes, write a pass-aware tile table, and produce QA figures that make the design understandable to non-specialists.

## Next Development Steps

The next technical improvements should build on this structure:

- Replace the simple offset rule with an optimization method for tile placement.
- Add area-aware coverage metrics on the sphere.
- Add support for observing constraints such as airmass, moon avoidance, and survey scheduling.
- Add focal-plane tilt and instrument-specific geometry when the relevant design assumptions are ready.
- Keep producing review-friendly QA figures for every major design mode.
