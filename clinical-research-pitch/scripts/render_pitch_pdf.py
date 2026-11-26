#!/usr/bin/env python3
"""Render HTML pitch note / CRF to A4 PDF via headless Chrome and verify every page visually."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile

import fitz

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def render_and_verify(html_path: str, pdf_path: str, png_dir: str | None = None) -> None:
    if not os.path.exists(CHROME):
        raise FileNotFoundError(f"Google Chrome not found at {CHROME}")

    os.makedirs(os.path.dirname(os.path.abspath(pdf_path)), exist_ok=True)
    subprocess.run(
        [
            CHROME,
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            os.path.abspath(html_path),
        ],
        check=True,
    )

    doc = fitz.open(pdf_path)
    out_dir = png_dir or tempfile.mkdtemp(prefix="pitch_verify_")
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    print(f"Rendered {pdf_path}: {len(doc)} pages, {os.path.getsize(pdf_path)/1024:.1f} KB")

    for idx in range(len(doc)):
        pix = doc[idx].get_pixmap(dpi=130)
        mn, mx = min(pix.samples), max(pix.samples)
        assert mn < 200 and mx > 200, f"Blank or uniform page {idx+1}: min={mn}, max={mx}"
        png_path = os.path.join(out_dir, f"{base}_p{idx+1}.png")
        pix.save(png_path)
        print(f"  Page {idx+1} verified -> {png_path} (extrema {mn}..{mx})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Render HTML to A4 PDF via Chrome and verify pages.")
    ap.add_argument("html", help="Input HTML file")
    ap.add_argument("pdf", help="Output PDF path")
    ap.add_argument("--png-dir", help="Optional directory to save rendered verification PNGs")
    args = ap.parse_args()
    render_and_verify(args.html, args.pdf, args.png_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
