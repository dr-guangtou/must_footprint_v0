#!/usr/bin/env python3
"""Compatibility wrapper for the first reference-boundary tiling demo."""

# ruff: noqa: E402

import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root / "src"))

from must_footprint.demo import main  # noqa: E402

if __name__ == "__main__":
    main()
