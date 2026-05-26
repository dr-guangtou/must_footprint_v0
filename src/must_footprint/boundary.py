"""Read and filter survey boundary files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class BoundaryTable:
    """Boundary points loaded from the DESI ECSV reference file."""

    program: np.ndarray
    cap: np.ndarray
    ra: np.ndarray
    dec: np.ndarray

    def select(self, program: str, cap: str | None = None) -> BoundaryTable:
        """Return rows matching one program and, optionally, one cap."""
        mask = self.program == program.upper()
        if cap is not None:
            mask &= self.cap == cap.upper()

        return BoundaryTable(
            program=self.program[mask],
            cap=self.cap[mask],
            ra=self.ra[mask],
            dec=self.dec[mask],
        )

    def caps(self) -> tuple[str, ...]:
        """Return cap names in first-seen order."""
        return tuple(dict.fromkeys(self.cap.tolist()))

    def as_points(self) -> np.ndarray:
        """Return boundary coordinates as an ``(N, 2)`` array."""
        return np.column_stack([self.ra, self.dec])

    def __len__(self) -> int:
        return len(self.ra)


def read_boundary_ecsv(path: str | Path) -> BoundaryTable:
    """Read the simple DESI boundary ECSV file used by the demo.

    The reference file is ECSV, but its data block has four plain columns:
    ``PROGRAM CAP RA DEC``. Reading that directly keeps this first demo free
    from a heavy astronomy I/O dependency while preserving the source format.
    """
    path = Path(path)
    programs: list[str] = []
    caps: list[str] = []
    ra_values: list[float] = []
    dec_values: list[float] = []
    data_started = False

    with path.open(encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            if not data_started:
                if stripped.split() == ["PROGRAM", "CAP", "RA", "DEC"]:
                    data_started = True
                continue

            fields = stripped.split()
            if len(fields) != 4:
                raise ValueError(f"Expected four columns at {path}:{line_number}, got {fields!r}")

            program, cap, ra_text, dec_text = fields
            programs.append(program.upper())
            caps.append(cap.upper())
            ra_values.append(float(ra_text))
            dec_values.append(float(dec_text))

    if not data_started:
        raise ValueError(f"No PROGRAM CAP RA DEC data header found in {path}")

    if not programs:
        raise ValueError(f"No boundary rows found in {path}")

    return BoundaryTable(
        program=np.asarray(programs),
        cap=np.asarray(caps),
        ra=np.asarray(ra_values, dtype=float),
        dec=np.asarray(dec_values, dtype=float),
    )
