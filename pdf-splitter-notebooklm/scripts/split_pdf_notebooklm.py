#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "pymupdf>=1.23.0",
# ]
# ///

"""
split_pdf_notebooklm.py
-----------------------
Splits large PDF documents into NotebookLM-compatible segments
(under 500 pages and 200MB per file).

Usage:
    uv run split_pdf_notebooklm.py --input "/path/to/book.pdf" --mode volumes
    uv run split_pdf_notebooklm.py --input "/path/to/book.pdf" --mode sections
    uv run split_pdf_notebooklm.py --input "/path/to/book.pdf" --mode chunks --chunk-size 250
"""

import argparse
import math
import os
import re
import sys
import fitz  # PyMuPDF


def sanitize_filename(name: str) -> str:
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name[:100]


def clean_stem_name(stem: str) -> str:
    # Unescape HTML entities like &_039_s or &#39;
    cleaned = re.sub(r'&_?0*39;?_?s?', "'s", stem)
    cleaned = re.sub(r'&amp;?_?', 'and ', cleaned)
    cleaned = re.sub(r'&#?\w+;', ' ', cleaned)
    # Remove metadata trailing brackets like {Authors}...(Year...)
    cleaned = re.sub(r'\{[^}]*\}.*$', '', cleaned)
    cleaned = re.sub(r'\([^\)]*\).*$', '', cleaned)
    cleaned = re.sub(r'\[[^\]]*\].*$', '', cleaned)
    cleaned = re.sub(r'[\'"_]', ' ', cleaned)
    cleaned = re.sub(r'\s+', '_', cleaned.strip(' _-'))
    return sanitize_filename(cleaned)


def normalize_sliced_toc(doc_toc, start_p: int, end_p: int):
    """
    Slices the TOC for pages [start_p, end_p] and ensures a valid hierarchy:
    - Root level is always 1.
    - No child level increases by more than 1 relative to parent.
    - Preserves all nested chapter/section titles.
    """
    raw_toc = []
    for item in doc_toc:
        level, title, page = item[0], item[1], item[2]
        if start_p <= page <= end_p:
            raw_toc.append([level, title, page - start_p + 1] + list(item[3:]))

    if not raw_toc:
        return []

    normalized = []
    prev_level = 0
    prev_orig_level = 0
    for item in raw_toc:
        orig_level = item[0]
        title = item[1]
        page = item[2]
        extra = item[3:]

        if not normalized:
            new_level = 1
        else:
            if orig_level > prev_orig_level:
                new_level = prev_level + 1
            elif orig_level == prev_orig_level:
                new_level = prev_level
            else:
                drop = prev_orig_level - orig_level
                new_level = max(1, prev_level - drop)

        normalized.append([new_level, title, page] + list(extra))
        prev_level = new_level
        prev_orig_level = orig_level

    return normalized


def find_optimal_volume_cuts(doc: fitz.Document, total_pages: int, num_volumes: int, max_pages: int):
    """
    Attempts to snap volume cuts to top-level Part or Chapter boundaries in TOC,
    ensuring each volume stays under max_pages.
    """
    toc = doc.get_toc()
    l1_starts = []
    l2_starts = []
    if toc:
        for level, title, page in toc:
            if 1 < page <= total_pages:
                if level == 1:
                    l1_starts.append(page)
                elif level == 2:
                    l2_starts.append(page)

    l1_starts = sorted(list(set(l1_starts)))
    l2_starts = sorted(list(set(l2_starts)))

    if num_volumes <= 1 or (not l1_starts and not l2_starts):
        # Default even page division
        pages_per_vol = math.ceil(total_pages / num_volumes)
        cuts = []
        for v in range(1, num_volumes):
            cuts.append(min(v * pages_per_vol, total_pages))
        return cuts

    # Greedily search for best cut points
    cuts = []
    curr_start = 1
    for v in range(1, num_volumes):
        remaining_vols = num_volumes - v
        ideal_cut = curr_start + (total_pages - curr_start + 1) / (remaining_vols + 1)

        # First priority: check Level 1 (Major Parts)
        valid_l1 = []
        for ch_start in l1_starts:
            cut_cand = ch_start - 1
            vol_len = cut_cand - curr_start + 1
            rem_len = total_pages - cut_cand
            if vol_len <= max_pages and (rem_len / remaining_vols) <= max_pages and cut_cand > curr_start:
                valid_l1.append(cut_cand)

        if valid_l1:
            best_cut = min(valid_l1, key=lambda c: abs(c - ideal_cut))
            cuts.append(best_cut)
            curr_start = best_cut + 1
            continue

        # Second priority: check Level 2 (Chapters)
        valid_l2 = []
        for ch_start in l2_starts:
            cut_cand = ch_start - 1
            vol_len = cut_cand - curr_start + 1
            rem_len = total_pages - cut_cand
            if vol_len <= max_pages and (rem_len / remaining_vols) <= max_pages and cut_cand > curr_start:
                valid_l2.append(cut_cand)

        if valid_l2:
            best_cut = min(valid_l2, key=lambda c: abs(c - ideal_cut))
            cuts.append(best_cut)
            curr_start = best_cut + 1
            continue

        # Fallback to even division
        fallback_cut = min(curr_start + math.ceil((total_pages - curr_start + 1) / (remaining_vols + 1)) - 1, total_pages)
        cuts.append(fallback_cut)
        curr_start = fallback_cut + 1

    return cuts


def get_volume_summary(doc: fitz.Document, start_p: int, end_p: int) -> str:
    toc = doc.get_toc()
    ch_titles = []
    if toc:
        # Check major part or chapter titles, ignoring small front-matter
        for level, title, page in toc:
            if level in (1, 2) and start_p <= page <= end_p:
                # Filter out pure front-matter if major sections exist
                cleaned = title.strip()
                if cleaned not in ('Front cover', 'Half title page', 'Evolve page', 'Copyright page'):
                    ch_titles.append(cleaned)
    if ch_titles:
        if len(ch_titles) <= 3:
            return ", ".join(ch_titles)
        return f"{ch_titles[0]} to {ch_titles[-1]} ({len(ch_titles)} sections)"
    return f"Pages {start_p}-{end_p}"


def split_by_volumes(doc: fitz.Document, input_stem: str, output_dir: str, num_volumes: int, total_pages: int, max_pages: int = 450):
    cuts = find_optimal_volume_cuts(doc, total_pages, num_volumes, max_pages)
    cut_bounds = [0] + cuts + [total_pages]
    results = []

    for v in range(len(cut_bounds) - 1):
        start_p = cut_bounds[v] + 1
        end_p = cut_bounds[v + 1]
        if start_p > total_pages:
            break

        summary_desc = get_volume_summary(doc, start_p, end_p)
        out_name = f"{input_stem}_Part{v+1:02d}_pp{start_p:04d}-{end_p:04d}.pdf"
        out_path = os.path.join(output_dir, out_name)

        dest_doc = fitz.open()
        dest_doc.insert_pdf(doc, from_page=start_p - 1, to_page=end_p - 1)

        # Slice relevant TOC entries and normalize root level to 1
        doc_toc = doc.get_toc()
        normalized_toc = normalize_sliced_toc(doc_toc, start_p, end_p)

        if normalized_toc:
            try:
                dest_doc.set_toc(normalized_toc)
            except Exception as e:
                print(f"Warning: Failed to set full TOC for Part {v+1} ({e}), setting simplified TOC.")
                dest_doc.set_toc([[1, f"Part {v+1} (Pages {start_p}-{end_p})", 1]])
        else:
            dest_doc.set_toc([[1, f"Part {v+1} (Pages {start_p}-{end_p})", 1]])

        dest_doc.save(out_path, garbage=3, deflate=True)
        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        count = len(dest_doc)
        dest_doc.close()
        results.append((out_path, count, size_mb, summary_desc))

    return results


def find_text_sections(doc: fitz.Document, total_pages: int):
    """Detects 'Section X' or 'Part X' from first lines of pages when TOC is empty."""
    found = []
    section_pattern = re.compile(r'^(?:(?:Section|Part)\s*(\d+|[IVXLCDM]+)|(\d+|[IVXLCDM]+)\s*(?:Section|Part))', re.I)

    for p in range(total_pages):
        text = doc[p].get_text() or ''
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        for idx, line in enumerate(lines[:6]):
            m = section_pattern.search(line)
            if m:
                title_cand = ""
                if idx + 1 < len(lines):
                    title_cand = lines[idx + 1]
                section_title = f"{line}: {title_cand}".strip(" :")
                found.append((p + 1, section_title))
                break

    deduped = []
    last_p = -100
    for p, title in found:
        if p - last_p >= 15:
            deduped.append((p, title))
            last_p = p

    return deduped


def split_by_sections(doc: fitz.Document, input_stem: str, output_dir: str, total_pages: int, max_pages: int):
    toc = doc.get_toc()
    section_markers = []

    if toc:
        top_items = [item for item in toc if item[0] == 1]
        if len(top_items) >= 2:
            section_markers = [(item[2], item[1]) for item in top_items]
        else:
            # Check level 2 if level 1 is just the single book title wrapper
            l2_items = [item for item in toc if item[0] == 2 and any(k in item[1].lower() for k in ('section', 'part', 'unit', 'volume'))]
            if len(l2_items) >= 2:
                section_markers = [(item[2], item[1]) for item in l2_items]

    if not section_markers:
        section_markers = find_text_sections(doc, total_pages)

    if not section_markers or len(section_markers) < 2:
        print("Notice: No clear section markers detected. Defaulting to balanced volumes split.")
        num_vols = math.ceil(total_pages / max_pages)
        return split_by_volumes(doc, input_stem, output_dir, num_vols, total_pages)

    if section_markers[0][0] > 1:
        section_markers.insert(0, (1, "Front Matter & Introduction"))

    ranges = []
    for i in range(len(section_markers)):
        start_p = section_markers[i][0]
        title = section_markers[i][1]
        end_p = (section_markers[i+1][0] - 1) if (i + 1 < len(section_markers)) else total_pages
        if end_p >= start_p:
            ranges.append((start_p, end_p, title))

    results = []
    for idx, (start_p, end_p, title) in enumerate(ranges):
        clean_title = sanitize_filename(title)
        out_name = f"{idx+1:02d}_{clean_title}_pp{start_p:03d}-{end_p:03d}.pdf"
        out_path = os.path.join(output_dir, out_name)

        dest_doc = fitz.open()
        dest_doc.insert_pdf(doc, from_page=start_p - 1, to_page=end_p - 1)
        
        doc_toc = doc.get_toc()
        sec_toc = normalize_sliced_toc(doc_toc, start_p, end_p)
        if sec_toc:
            try:
                dest_doc.set_toc(sec_toc)
            except Exception:
                dest_doc.set_toc([[1, title, 1]])
        else:
            dest_doc.set_toc([[1, title, 1]])
            
        dest_doc.save(out_path, garbage=3, deflate=True)
        size_mb = os.path.getsize(out_path) / (1024 * 1024)
        count = len(dest_doc)
        dest_doc.close()
        results.append((out_path, count, size_mb, title))

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Split large PDFs into NotebookLM-ready parts (under 500 pages and 200MB)"
    )
    parser.add_argument("--input", "-i", required=True, help="Path to input PDF file")
    parser.add_argument("--output-dir", "-o", default=None, help="Directory to save split files")
    parser.add_argument(
        "--mode", "-m",
        choices=["volumes", "sections", "chunks"],
        default="volumes",
        help="Split strategy: 'volumes' (balanced multi-part), 'sections' (by detected chapters/sections), or 'chunks' (fixed page count)"
    )
    parser.add_argument("--num-volumes", "-n", type=int, default=None, help="Specific number of volumes (e.g. 2)")
    parser.add_argument("--max-pages", type=int, default=450, help="Max pages per file (NotebookLM limit is 500, default 450)")
    parser.add_argument("--chunk-size", type=int, default=200, help="Pages per file for 'chunks' mode")

    args = parser.parse_args()

    input_path = os.path.abspath(args.input)
    if not os.path.exists(input_path):
        print(f"Error: Input file does not exist: {input_path}", file=sys.stderr)
        sys.exit(1)

    input_dir = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    stem, _ = os.path.splitext(base_name)
    clean_stem = clean_stem_name(stem)

    if args.output_dir:
        output_dir = os.path.abspath(args.output_dir)
    else:
        output_dir = os.path.join(input_dir, f"{clean_stem}_notebooklm")

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(input_path)
    total_pages = len(doc)
    size_mb = os.path.getsize(input_path) / (1024 * 1024)

    print("=" * 60)
    print(f"Input Document : {base_name}")
    print(f"Total Pages    : {total_pages}")
    print(f"File Size      : {size_mb:.2f} MB")
    print(f"Split Mode     : {args.mode}")
    print(f"Destination    : {output_dir}")
    print("=" * 60)

    if total_pages <= args.max_pages and size_mb < 180.0:
        print(f"Notice: This file ({total_pages} pages, {size_mb:.2f} MB) is ALREADY within NotebookLM limits (<500 pages, <200MB).")

    if args.mode == "volumes":
        num_vols = args.num_volumes or math.ceil(total_pages / args.max_pages)
        if num_vols < 2:
            num_vols = 2
        results = split_by_volumes(doc, clean_stem, output_dir, num_vols, total_pages, max_pages=args.max_pages)
    elif args.mode == "sections":
        results = split_by_sections(doc, clean_stem, output_dir, total_pages, args.max_pages)
    elif args.mode == "chunks":
        chunk = args.chunk_size
        num_chunks = math.ceil(total_pages / chunk)
        results = split_by_volumes(doc, clean_stem, output_dir, num_chunks, total_pages, max_pages=args.max_pages)

    doc.close()

    print("\nGenerated NotebookLM-Ready Files:")
    print("-" * 60)
    for path, pages, fsize, desc in results:
        fname = os.path.basename(path)
        print(f"  • {fname}")
        print(f"    Pages: {pages} | Size: {fsize:.2f} MB | {desc}")
    print("-" * 60)
    print(f"\nAll files saved to: {output_dir}")


if __name__ == "__main__":
    main()
