#!/usr/bin/env python3
"""
Automated Textbook Cover & Figure Extractor (Phase 3 Prototype)
1. extract-covers: Extracts graphic front covers from PDFs (page 1 when embedded cover image exists; skips text-only PDFs cleanly).
2. find-figures: Scans PDFs for figure/table captions matching query keywords, clusters nearby images/drawings to auto-compute tight bboxes, and exports a labeled candidate Contact Sheet PNG + JSON.
3. extract-id: Extracts a selected candidate ID from figure_candidates.json at 4x (~300 DPI) zoom.
"""

from __future__ import annotations
import argparse
import glob
import json
import math
import os
import re
import sys
import fitz
from PIL import Image, ImageDraw, ImageFont


def slugify(text: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").lower()
    return s[:48] or "book"


def list_primary_pdfs(ref_dir: str, exclude_regex: str | None = None) -> list[str]:
    pdfs = sorted(glob.glob(os.path.join(ref_dir, "*.pdf")) + glob.glob(os.path.join(ref_dir, "*.PDF")))
    seen = set()
    out = []
    ex_pat = re.compile(exclude_regex, re.IGNORECASE) if exclude_regex else None
    for p in pdfs:
        if p in seen:
            continue
        seen.add(p)
        if ex_pat and ex_pat.search(os.path.basename(p)):
            continue
        out.append(p)
    return out


def cmd_extract_covers(args):
    pdfs = list_primary_pdfs(os.path.abspath(args.ref_dir), args.exclude)
    os.makedirs(args.out_dir, exist_ok=True)
    manifest = []

    for pdf_path in pdfs:
        bname = os.path.basename(pdf_path)
        doc = fitz.open(pdf_path)
        p0 = doc[0]
        imgs = p0.get_images(full=True)
        txt_len = len(p0.get_text("text").strip())

        if len(imgs) >= 1 and txt_len < 40:
            out_name = f"cover_{slugify(os.path.splitext(bname)[0])}.png"
            out_path = os.path.join(args.out_dir, out_name)
            pix = p0.get_pixmap(matrix=fitz.Matrix(args.zoom, args.zoom), alpha=False)
            pix.save(out_path)
            manifest.append({
                "pdf": bname,
                "has_graphic_cover": True,
                "cover_file": out_name,
                "width": pix.width,
                "height": pix.height,
            })
            print(f"EXTRACTED COVER: {bname} -> {out_name} ({pix.width}x{pix.height})")
        else:
            manifest.append({
                "pdf": bname,
                "has_graphic_cover": False,
                "cover_file": None,
                "reason": f"PDF page 1 is text-only (imgs={len(imgs)}, text_len={txt_len})",
            })
            print(f"SKIPPED (no graphic cover on p.1): {bname}")
        doc.close()

    man_path = os.path.join(args.out_dir, "covers_manifest.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print(f"SUCCESS: Saved cover manifest -> {man_path}")


def compute_candidate_bbox(page: fitz.Page, caption_rects: list[fitz.Rect]) -> fitz.Rect:
    """Cluster embedded image bboxes + vector drawing rects near/above the caption."""
    pw, ph = page.rect.width, page.rect.height
    margin = 14.0
    graphic_rects: list[fitz.Rect] = []

    for info in page.get_image_info(xrefs=False):
        r = fitz.Rect(info["bbox"])
        if r.width > 24 and r.height > 24 and r.width < pw * 0.98 and r.height < ph * 0.96:
            graphic_rects.append(r)

    # Include meaningful vector drawing bounding boxes if few raster images exist
    if len(graphic_rects) == 0:
        for d in page.get_drawings():
            r = d.get("rect")
            if r and r.width > 12 and r.height > 12 and r.width < pw * 0.92 and r.height < ph * 0.85:
                graphic_rects.append(fitz.Rect(r))

    if caption_rects:
        cap = caption_rects[0]
        # Prefer graphics above or overlapping vertically within 340 pt of the caption
        near = [
            r for r in graphic_rects
            if (r.y1 <= cap.y1 + 40 and r.y0 >= max(0, cap.y0 - 440))
            or (r.y0 >= cap.y0 - 20 and r.y1 <= min(ph, cap.y1 + 360))
        ]
        if near:
            union = fitz.Rect(near[0])
            for r in near[1:]:
                union.include_rect(r)
            # Optionally expand slightly to avoid clipping labels around edges
            return fitz.Rect(
                max(0, union.x0 - margin),
                max(0, union.y0 - margin),
                min(pw, union.x1 + margin),
                min(ph, union.y1 + margin),
            )

    if graphic_rects:
        union = fitz.Rect(graphic_rects[0])
        for r in graphic_rects[1:]:
            union.include_rect(r)
        return fitz.Rect(
            max(0, union.x0 - margin),
            max(0, union.y0 - margin),
            min(pw, union.x1 + margin),
            min(ph, union.y1 + margin),
        )

    # Fallback: cropped page body excluding header/footer bands
    return fitz.Rect(28, 48, pw - 28, ph - 48)


def cmd_find_figures(args):
    pdfs = list_primary_pdfs(os.path.abspath(args.ref_dir), args.exclude)
    keywords = [k.strip().lower() for k in re.split(r"[,;]+|\s+", args.query) if len(k.strip()) >= 2]
    fig_re = re.compile(r"(fig(?:ure|\.)\s*\d+[-.\d]*|table\s*\d+[-.\d]*)", re.IGNORECASE)

    os.makedirs(args.out_dir, exist_ok=True)
    candidates = []
    thumbs = []

    for pdf_path in pdfs:
        bname = os.path.basename(pdf_path)
        doc = fitz.open(pdf_path)
        per_book = 0
        for pno in range(len(doc)):
            page = doc[pno]
            txt = page.get_text("text")
            t_low = txt.lower()
            if not all(k in t_low for k in keywords):
                continue
            m = fig_re.search(txt)
            if not m:
                continue
            imgs = page.get_images(full=True)
            drawings = page.get_drawings()
            if len(imgs) == 0 and len(drawings) < 20 and "table" not in m.group(1).lower():
                continue

            cap_rects = page.search_for(m.group(1))
            bbox = compute_candidate_bbox(page, cap_rects)
            cid = f"C{len(candidates) + 1}"
            caption_lines = [ln.strip() for ln in txt.splitlines() if fig_re.search(ln)]
            caption_preview = caption_lines[0][:90] if caption_lines else m.group(1)

            pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), clip=bbox, alpha=False)
            prev_name = f"{cid}_{slugify(bname)[:16]}_p{pno+1}.png"
            prev_path = os.path.join(args.out_dir, prev_name)
            pix.save(prev_path)

            cand = {
                "id": cid,
                "pdf": bname,
                "pdf_path": pdf_path,
                "pdf_page": pno + 1,
                "caption_match": caption_preview,
                "bbox": [round(bbox.x0, 1), round(bbox.y0, 1), round(bbox.x1, 1), round(bbox.y1, 1)],
                "preview_png": prev_name,
                "preview_px": f"{pix.width}x{pix.height}",
            }
            candidates.append(cand)
            thumbs.append((cand, prev_path))
            per_book += 1
            if per_book >= args.limit_per_book or len(candidates) >= args.max_total:
                break
        doc.close()
        if len(candidates) >= args.max_total:
            break

    cand_json = os.path.join(args.out_dir, "figure_candidates.json")
    with open(cand_json, "w", encoding="utf-8") as f:
        json.dump(candidates, f, ensure_ascii=False, indent=2)

    if thumbs:
        cols = 3
        thumb_w, thumb_h_box = 480, 360
        pad, hdr_h = 20, 56
        rows = math.ceil(len(thumbs) / cols)
        canvas = Image.new("RGB", (cols * thumb_w + (cols + 1) * pad, rows * (thumb_h_box + hdr_h) + (rows + 1) * pad), (241, 245, 249))
        draw = ImageDraw.Draw(canvas)
        try:
            font_b = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 18)
            font_r = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
        except Exception:
            font_b = font_r = ImageFont.load_default()

        for idx, (cand, p_path) in enumerate(thumbs):
            r = idx // cols
            c = idx % cols
            x = pad + c * (thumb_w + pad)
            y = pad + r * (thumb_h_box + hdr_h + pad)
            draw.rectangle([x, y, x + thumb_w, y + thumb_h_box + hdr_h], fill=(255, 255, 255), outline=(203, 213, 225))
            draw.text((x + 10, y + 6), f"[{cand['id']}] {cand['pdf'][:26]} (PDF p.{cand['pdf_page']})", fill=(15, 23, 42), font=font_b)
            draw.text((x + 10, y + 30), cand["caption_match"][:56], fill=(13, 148, 136), font=font_r)

            im = Image.open(p_path).convert("RGB")
            sc = min((thumb_w - 20) / im.width, (thumb_h_box - 16) / im.height)
            im_r = im.resize((int(im.width * sc), int(im.height * sc)), Image.Resampling.LANCZOS)
            px = x + (thumb_w - im_r.width) // 2
            py = y + hdr_h + (thumb_h_box - im_r.height) // 2
            canvas.paste(im_r, (px, py))

        sheet_path = os.path.join(args.out_dir, "figure_candidates.png")
        canvas.save(sheet_path)
        print(f"SUCCESS: Found {len(candidates)} candidates -> {sheet_path} & {cand_json}")
    else:
        print(f"NO CANDIDATES FOUND for query '{args.query}'")


def cmd_extract_id(args):
    with open(args.candidates_json, "r", encoding="utf-8") as f:
        cands = json.load(f)
    match = next((c for c in cands if c["id"].upper() == args.id.upper()), None)
    if not match:
        print(f"ERROR: Candidate ID '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(match["pdf_path"])
    page = doc[match["pdf_page"] - 1]
    rect = fitz.Rect(*match["bbox"])
    pix = page.get_pixmap(matrix=fitz.Matrix(args.zoom, args.zoom), clip=rect, alpha=False)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    pix.save(args.out)
    doc.close()
    print(f"SUCCESS: Extracted [{match['id']}] {pix.width}x{pix.height} px -> {args.out}")


def main():
    parser = argparse.ArgumentParser(description="Automated Textbook Cover & Figure Extractor")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_cov = sub.add_parser("extract-covers", help="Extract textbook front covers from PDFs")
    p_cov.add_argument("--ref-dir", required=True)
    p_cov.add_argument("--out-dir", required=True)
    p_cov.add_argument("--zoom", type=float, default=2.0)
    p_cov.add_argument("--exclude", help="Optional regex to exclude PDF filenames")
    p_cov.set_defaults(func=cmd_extract_covers)

    p_find = sub.add_parser("find-figures", help="Auto-detect figure/table bboxes and render contact sheet")
    p_find.add_argument("--ref-dir", required=True)
    p_find.add_argument("--query", required=True)
    p_find.add_argument("--out-dir", required=True)
    p_find.add_argument("--limit-per-book", type=int, default=3)
    p_find.add_argument("--max-total", type=int, default=9)
    p_find.add_argument("--exclude", help="Optional regex to exclude PDF filenames")
    p_find.set_defaults(func=cmd_find_figures)

    p_ext = sub.add_parser("extract-id", help="Extract selected candidate ID at high-res 4x zoom")
    p_ext.add_argument("--candidates-json", required=True)
    p_ext.add_argument("--id", required=True)
    p_ext.add_argument("--zoom", type=float, default=4.0)
    p_ext.add_argument("--out", required=True)
    p_ext.set_defaults(func=cmd_extract_id)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
