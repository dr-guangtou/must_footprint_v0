#!/usr/bin/env python3
"""Convert docs/review.md into a simple PDF with embedded QA figures."""

from __future__ import annotations

import argparse
import re
import textwrap
from pathlib import Path

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

IMAGE_PATTERN = re.compile(r"!\[(?P<caption>[^\]]*)\]\((?P<path>[^)]+)\)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the review PDF from Markdown.")
    parser.add_argument("--input", type=Path, default=Path("docs/review.md"))
    parser.add_argument("--output", type=Path, default=Path("docs/review.pdf"))
    return parser


def flush_text_page(pdf: PdfPages, lines: list[str], page_title: str) -> None:
    if not lines:
        return

    fig, ax = plt.subplots(figsize=(8.5, 11))
    ax.axis("off")
    y = 0.96

    for raw_line in lines:
        line = raw_line.rstrip()
        if not line:
            y -= 0.025
            continue

        if line.startswith("# "):
            ax.text(0.06, y, line[2:], fontsize=18, fontweight="bold", va="top")
            y -= 0.055
        elif line.startswith("## "):
            ax.text(0.06, y, line[3:], fontsize=13, fontweight="bold", va="top")
            y -= 0.040
        elif line.startswith("- "):
            for wrapped_line in textwrap.wrap(line[2:], width=88):
                ax.text(0.085, y, f"- {wrapped_line}", fontsize=9.5, va="top")
                y -= 0.022
        elif re.match(r"^\d+\. ", line):
            for wrapped_line in textwrap.wrap(line, width=90):
                ax.text(0.075, y, wrapped_line, fontsize=9.5, va="top")
                y -= 0.022
        elif line.startswith("```"):
            continue
        else:
            for wrapped_line in textwrap.wrap(line, width=95):
                ax.text(0.06, y, wrapped_line, fontsize=9.5, va="top")
                y -= 0.022

        if y < 0.07:
            ax.text(0.50, 0.025, page_title, fontsize=8, ha="center", color="#666666")
            pdf.savefig(fig)
            plt.close(fig)
            fig, ax = plt.subplots(figsize=(8.5, 11))
            ax.axis("off")
            y = 0.96

    ax.text(0.50, 0.025, page_title, fontsize=8, ha="center", color="#666666")
    pdf.savefig(fig)
    plt.close(fig)
    lines.clear()


def add_image_page(pdf: PdfPages, markdown_path: Path, caption: str, image_path_text: str) -> None:
    image_path = (markdown_path.parent / image_path_text).resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Markdown image path does not exist: {image_path}")

    image = mpimg.imread(image_path)
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.imshow(image)
    ax.axis("off")
    fig.suptitle(caption, fontsize=13, fontweight="bold")
    pdf.savefig(fig)
    plt.close(fig)


def build_review_pdf(markdown_path: Path, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    page_title = "MUST Footprint Design Demo Review"

    with PdfPages(output_path) as pdf:
        for line in markdown_path.read_text(encoding="utf-8").splitlines():
            image_match = IMAGE_PATTERN.fullmatch(line.strip())
            if image_match:
                flush_text_page(pdf, lines, page_title)
                add_image_page(
                    pdf,
                    markdown_path,
                    image_match.group("caption"),
                    image_match.group("path"),
                )
            else:
                lines.append(line)

        flush_text_page(pdf, lines, page_title)

    return output_path


def main() -> None:
    args = build_parser().parse_args()
    output_path = build_review_pdf(args.input, args.output)
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
