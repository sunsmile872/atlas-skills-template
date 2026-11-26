#!/usr/bin/env python3
"""
Visual QA Renderer (Prototype)
Converts .pptx -> .pdf (via LibreOffice if installed, or Microsoft PowerPoint AppleScript on macOS)
and renders high-res PNG images + contact sheets for Visual QA inspection.
"""

import argparse
import math
import os
import shutil
import subprocess
import sys
import fitz
from PIL import Image, ImageDraw, ImageFont


def export_pdf_libreoffice(pptx_path: str, pdf_path: str) -> bool:
    soffice = (
        shutil.which("soffice")
        or shutil.which("libreoffice")
        or ("/Applications/LibreOffice.app/Contents/MacOS/soffice" if os.path.exists("/Applications/LibreOffice.app/Contents/MacOS/soffice") else None)
    )
    if not soffice:
        return False
    out_dir = os.path.dirname(os.path.abspath(pdf_path))
    os.makedirs(out_dir, exist_ok=True)
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", out_dir, pptx_path],
        check=True,
    )
    gen_pdf = os.path.join(out_dir, os.path.splitext(os.path.basename(pptx_path))[0] + ".pdf")
    if os.path.abspath(gen_pdf) != os.path.abspath(pdf_path) and os.path.exists(gen_pdf):
        shutil.move(gen_pdf, pdf_path)
    return os.path.exists(pdf_path)


def export_pdf_powerpoint_mac(pptx_path: str, pdf_path: str) -> bool:
    os.makedirs(os.path.dirname(os.path.abspath(pdf_path)), exist_ok=True)
    script = f'''
set inPath to POSIX file "{os.path.abspath(pptx_path)}"
set outPath to POSIX file "{os.path.abspath(pdf_path)}"
tell application "Microsoft PowerPoint"
    open inPath
    delay 1.5
    save active presentation in outPath as save as PDF
    close active presentation saving no
end tell
'''
    subprocess.run(["osascript", "-e", script], check=True)
    return os.path.exists(pdf_path)


def render_pdf_to_pngs(pdf_path: str, out_dir: str, zoom: float = 2.0) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    paths = []
    mat = fitz.Matrix(zoom, zoom)
    for idx in range(len(doc)):
        pix = doc[idx].get_pixmap(matrix=mat, alpha=False)
        out_png = os.path.join(out_dir, f"slide_{idx + 1:02d}.png")
        pix.save(out_png)
        paths.append(out_png)
    doc.close()
    return paths


def make_contact_sheet(png_paths: list[str], out_path: str, cols: int = 4, thumb_w: int = 640) -> None:
    if not png_paths:
        return
    pad = 24
    hdr_h = 34
    thumbs = []
    for i, p in enumerate(png_paths, 1):
        im = Image.open(p).convert("RGB")
        r = thumb_w / im.width
        im = im.resize((thumb_w, int(im.height * r)), Image.Resampling.LANCZOS)
        thumbs.append((i, im))

    thumb_h = max(im.height for _, im in thumbs)
    rows = math.ceil(len(thumbs) / cols)
    canvas_w = cols * thumb_w + (cols + 1) * pad
    canvas_h = rows * (thumb_h + hdr_h) + (rows + 1) * pad
    canvas = Image.new("RGB", (canvas_w, canvas_h), (241, 245, 249))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 20)
    except Exception:
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20, index=1)
        except Exception:
            font = ImageFont.load_default()

    for idx, (s_num, im) in enumerate(thumbs):
        r = idx // cols
        c = idx % cols
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + hdr_h + pad)
        draw.text((x, y + 4), f"Slide {s_num:02d}", fill=(15, 23, 42), font=font)
        canvas.paste(im, (x, y + hdr_h))

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    canvas.save(out_path)
    print(f"SUCCESS: Saved {len(thumbs)}-slide contact sheet -> {out_path}")


def make_side_by_side_sheet(pairs: list[tuple[str, str, str]], out_path: str) -> None:
    rows = []
    target_w = 960
    pad = 24
    hdr_h = 44

    for label, p1, p2 in pairs:
        im1 = Image.open(p1).convert("RGB")
        im2 = Image.open(p2).convert("RGB")
        r1 = target_w / im1.width
        r2 = target_w / im2.width
        im1 = im1.resize((target_w, int(im1.height * r1)), Image.Resampling.LANCZOS)
        im2 = im2.resize((target_w, int(im2.height * r2)), Image.Resampling.LANCZOS)
        row_h = max(im1.height, im2.height) + hdr_h + pad
        rows.append((label, im1, im2, row_h))

    canvas_w = target_w * 2 + pad * 3
    canvas_h = sum(r[3] for r in rows) + pad
    canvas = Image.new("RGB", (canvas_w, canvas_h), (241, 245, 249))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22, index=1)
    except Exception:
        font = ImageFont.load_default()

    y = pad
    for label, im1, im2, row_h in rows:
        draw.text((pad, y + 8), f"{label} — BEFORE (v1 python-pptx)", fill=(100, 116, 139), font=font)
        draw.text((pad * 2 + target_w, y + 8), f"{label} — AFTER (v2 PptxGenJS Visual-Learner)", fill=(13, 148, 136), font=font)
        canvas.paste(im1, (pad, y + hdr_h))
        canvas.paste(im2, (pad * 2 + target_w, y + hdr_h))
        y += row_h

    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    canvas.save(out_path)
    print(f"SUCCESS: Saved comparison sheet -> {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Render PPTX slides to PNG for Visual QA")
    parser.add_argument("--pptx", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--zoom", type=float, default=2.0)
    parser.add_argument("--contact-sheet", help="Optional path to save multi-slide contact sheet PNG")
    parser.add_argument("--cols", type=int, default=4)
    args = parser.parse_args()

    pdf_path = os.path.join(args.out_dir, "deck_render.pdf")
    ok = export_pdf_libreoffice(args.pptx, pdf_path)
    if not ok:
        ok = export_pdf_powerpoint_mac(args.pptx, pdf_path)
    if not ok:
        print("ERROR: Failed to export PPTX to PDF.", file=sys.stderr)
        sys.exit(1)

    pngs = render_pdf_to_pngs(pdf_path, args.out_dir, zoom=args.zoom)
    print(f"SUCCESS: Rendered {len(pngs)} slide PNGs in {args.out_dir}")
    if args.contact_sheet:
        make_contact_sheet(pngs, args.contact_sheet, cols=args.cols)


if __name__ == "__main__":
    main()
