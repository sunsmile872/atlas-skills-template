#!/usr/bin/env python3
"""Prepare raw chart folders (.HEIC photo conversion + duplicate detection, or chronological PDF merge)."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

import fitz

THAI_MONTHS = {
    "ม.ค.": 1, "มค": 1, "มกราคม": 1,
    "ก.พ.": 2, "กพ": 2, "กุมภาพันธ์": 2,
    "มี.ค.": 3, "มีค": 3, "มีนาคม": 3,
    "เม.ย.": 4, "เมย": 4, "เมษายน": 4,
    "พ.ค.": 5, "พค": 5, "พฤษภาคม": 5,
    "มิ.ย.": 6, "มิย": 6, "มิถุนายน": 6,
    "ก.ค.": 7, "กค": 7, "กรกฎาคม": 7,
    "ส.ค.": 8, "สค": 8, "สิงหาคม": 8,
    "ก.ย.": 9, "กย": 9, "กันยายน": 9,
    "ต.ค.": 10, "ตค": 10, "ตุลาคม": 10,
    "พ.ย.": 11, "พย": 11, "พฤศจิกายน": 11,
    "ธ.ค.": 12, "ธค": 12, "ธันวาคม": 12,
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def cmd_prepare_photos(src_dir: Path, dst_dir: Path) -> None:
    dst_dir.mkdir(parents=True, exist_ok=True)
    exts = {".heic", ".jpg", ".jpeg", ".png"}
    files = sorted(p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in exts)

    manifest = []
    seen_hashes: dict[str, str] = {}
    for src in files:
        out_name = f"{src.stem}.jpg" if src.suffix.lower() == ".heic" else src.name
        out_path = dst_dir / out_name
        if src.suffix.lower() == ".heic":
            subprocess.run(
                ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "85", str(src), "--out", str(out_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            out_path.write_bytes(src.read_bytes())

        digest = sha256_file(src)
        dup_of = seen_hashes.get(digest)
        if dup_of is None:
            seen_hashes[digest] = src.name
        manifest.append(
            {
                "source": src.name,
                "converted": str(out_path),
                "size_bytes": out_path.stat().st_size,
                "sha256_prefix": digest[:12],
                "exact_duplicate_of": dup_of,
            }
        )

    manifest_path = dst_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Prepared {len(manifest)} images in {dst_dir} (manifest: {manifest_path})")


def normalize_year(y: int) -> int:
    if y < 100:
        return (y + 2500 - 543) if y >= 40 else (2000 + y)
    return (y - 543) if y >= 2400 else y


def extract_first_date(text: str, fallback_mtime: float) -> datetime:
    # Match numeric dd/mm/yyyy or dd-mm-yy
    m = re.search(r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b", text)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), normalize_year(int(m.group(3)))
        try:
            return datetime(y, mo, d)
        except ValueError:
            pass
    # Match Thai month names
    m_th = re.search(r"\b(\d{1,2})\s+([^\s\d]{2,12})\s+(\d{2,4})\b", text)
    if m_th:
        d = int(m_th.group(1))
        mo = THAI_MONTHS.get(m_th.group(2))
        y = normalize_year(int(m_th.group(3)))
        if mo:
            try:
                return datetime(y, mo, d)
            except ValueError:
                pass
    return datetime.fromtimestamp(fallback_mtime)


def cmd_merge_pdfs(src_dir: Path, out_pdf: Path) -> None:
    pdfs = sorted(p for p in src_dir.rglob("*.pdf") if p.is_file())
    records = []
    for p in pdfs:
        with fitz.open(p) as doc:
            first_text = doc[0].get_text("text") if len(doc) else ""
            dt = extract_first_date(f"{p.name}\n{first_text}", p.stat().st_mtime)
            records.append((dt, p.name, p, len(doc)))

    records.sort(key=lambda r: (r[0], r[1]))
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    merged = fitz.open()
    toc = []
    cursor_page = 1

    for dt, name, path, n_pages in records:
        with fitz.open(path) as src_doc:
            merged.insert_pdf(src_doc)
        toc.append([1, f"{dt.strftime('%Y-%m-%d')} | {name}", cursor_page])
        cursor_page += n_pages

    if toc:
        merged.set_toc(toc)
    merged.save(str(out_pdf), deflate=True, garbage=3)
    merged.close()
    print(f"Merged {len(records)} PDFs ({cursor_page - 1} pages) -> {out_pdf}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare medical chart folders (.HEIC photos or multi-PDF merge).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_img = sub.add_parser("prepare-photos", help="Convert .HEIC/.jpg/.png folder to readable JPEGs + manifest.")
    p_img.add_argument("src_dir", type=Path)
    p_img.add_argument("dst_dir", type=Path)

    p_pdf = sub.add_parser("merge-pdfs", help="Sort and merge a folder of chart PDFs chronologically with bookmarks.")
    p_pdf.add_argument("src_dir", type=Path)
    p_pdf.add_argument("out_pdf", type=Path)

    args = parser.parse_args()
    if args.cmd == "prepare-photos":
        cmd_prepare_photos(args.src_dir, args.dst_dir)
    elif args.cmd == "merge-pdfs":
        cmd_merge_pdfs(args.src_dir, args.out_pdf)


if __name__ == "__main__":
    main()
