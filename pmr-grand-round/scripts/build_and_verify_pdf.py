#!/usr/bin/env python3
"""Compile an A4 Grand Round HTML file to PDF via Chrome Headless and verify visual rendering."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def main() -> int:
    parser = argparse.ArgumentParser(description="Compile HTML to A4 PDF and run visual verification.")
    parser.add_argument("html_path", help="Path to source HTML file")
    parser.add_argument("pdf_path", help="Destination PDF path")
    parser.add_argument("--png-dir", required=True, help="Directory to save rendered page PNGs for inspection")
    parser.add_argument("--dpi", type=int, default=150, help="DPI for verification PNGs (default: 150)")
    args = parser.parse_args()

    html_path = Path(args.html_path).resolve()
    pdf_path = Path(args.pdf_path).resolve()
    png_dir = Path(args.png_dir).resolve()
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    png_dir.mkdir(parents=True, exist_ok=True)

    if not html_path.exists():
        print(f"ERROR: HTML not found: {html_path}", file=sys.stderr)
        return 1

    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0 or not pdf_path.exists():
        print(f"ERROR: Chrome print-to-pdf failed (rc={res.returncode}):\n{res.stderr}", file=sys.stderr)
        return 1

    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("ERROR: PyMuPDF (fitz) is required for visual render verification.", file=sys.stderr)
        return 1

    doc = fitz.open(pdf_path)
    print(f"PDF compiled: {pdf_path} ({len(doc)} pages, {os.path.getsize(pdf_path)} bytes)")
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=args.dpi)
        out_png = png_dir / f"verify_page_{i + 1}.png"
        pix.save(str(out_png))
        samples = pix.samples
        mn, mx = min(samples), max(samples)
        text_len = len(page.get_text().strip())
        if mn == mx or text_len == 0:
            print(f"FAIL: Page {i + 1} appears blank (min={mn}, max={mx}, text_len={text_len})", file=sys.stderr)
            return 1
        print(f"  Page {i + 1}: {pix.width}x{pix.height} px, min={mn}, max={mx}, text_len={text_len} -> {out_png}")

    # Native macOS QuickLook check
    ql = subprocess.run(
        ["qlmanage", "-t", "-s", "1000", "-o", str(png_dir), str(pdf_path)],
        capture_output=True,
        text=True,
    )
    if ql.returncode != 0:
        print(f"WARNING: qlmanage returned {ql.returncode}: {ql.stderr}", file=sys.stderr)
    else:
        print("QuickLook check passed.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
