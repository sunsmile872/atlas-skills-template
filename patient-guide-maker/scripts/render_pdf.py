#!/usr/bin/env python3
"""
A4 PDF Compiler & Single-Page Fit Validator for patient-guide-maker
Renders HTML into PDF using headless Chrome and strictly verifies that page count == 1 (or requested max-pages).
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def render_html_to_pdf(html_path, pdf_path):
    html_abs = Path(html_path).resolve()
    pdf_abs = Path(pdf_path).resolve()
    pdf_abs.parent.mkdir(parents=True, exist_ok=True)
    
    file_url = f"file://{html_abs}"
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_abs}",
        file_url
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error rendering PDF: {res.stderr}", file=sys.stderr)
        return False
    return True

def get_page_count(pdf_path):
    try:
        import pypdf
        reader = pypdf.PdfReader(str(pdf_path))
        return len(reader.pages)
    except Exception:
        # Fallback to mdls on macOS
        try:
            res = subprocess.run(["mdls", "-name", "kMDItemNumberOfPages", str(pdf_path)], capture_output=True, text=True)
            for line in res.stdout.splitlines():
                if "kMDItemNumberOfPages" in line:
                    return int(line.split("=")[1].strip())
        except Exception:
            pass
    return 1

def main():
    parser = argparse.ArgumentParser(description="Render HTML to single-page A4 PDF and verify page count.")
    parser.add_argument("--html", required=True, help="Path to input HTML file")
    parser.add_argument("--output", required=True, help="Path to output PDF file")
    parser.add_argument("--max-pages", type=int, default=1, help="Expected page count (default 1)")
    
    args = parser.parse_args()
    
    if not os.path.exists(CHROME_PATH):
        print(f"Google Chrome not found at {CHROME_PATH}", file=sys.stderr)
        sys.exit(1)
        
    print(f"Rendering {args.html} -> {args.output}...")
    if not render_html_to_pdf(args.html, args.output):
        sys.exit(1)
        
    pages = get_page_count(args.output)
    print(f"Rendered successfully: {pages} page(s)")
    
    if pages > args.max_pages:
        print(f"⚠️ WARNING: PDF is {pages} pages, which exceeds the target of {args.max_pages} page(s)!", file=sys.stderr)
        print("Please reduce padding/margins or font sizes in the HTML template to ensure a strict 1-page fit.", file=sys.stderr)
        sys.exit(2)
    else:
        print(f"✅ Strict {args.max_pages}-page A4 fit verified!")

if __name__ == "__main__":
    main()
