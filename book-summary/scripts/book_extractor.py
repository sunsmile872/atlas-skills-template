#!/usr/bin/env python3
"""
Book Extractor for book-summary skill.
Extracts Table of Contents, chapters, text, and metadata from PDF, EPUB, AZW3, and MOBI books.
"""

import sys
import os
import json
import re
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

def clean_html(html_text: str) -> str:
    """Removes HTML tags and normalizes whitespace."""
    # Replace common block elements with newlines
    text = re.sub(r'<(?:p|div|h[1-6]|li|tr|br)[^>]*>', '\n', html_text, flags=re.IGNORECASE)
    # Strip all remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    # Unescape HTML entities
    import html
    text = html.unescape(text)
    # Normalize multiple newlines
    lines = [line.strip() for line in text.splitlines()]
    clean_lines = []
    prev_blank = False
    for line in lines:
        if line:
            clean_lines.append(line)
            prev_blank = False
        elif not prev_blank:
            clean_lines.append('')
            prev_blank = True
    return '\n'.join(clean_lines).strip()

class BookExtractor:
    def __init__(self, file_path: str):
        self.path = Path(file_path).resolve()
        if not self.path.exists():
            raise FileNotFoundError(f"File not found: {self.path}")
        self.suffix = self.path.suffix.lower()

    def get_info(self) -> dict:
        if self.suffix == '.pdf':
            return self._info_pdf()
        elif self.suffix == '.epub':
            return self._info_epub()
        elif self.suffix in ['.azw3', '.mobi']:
            return self._info_kindle()
        else:
            raise ValueError(f"Unsupported format: {self.suffix}")

    def _info_pdf(self) -> dict:
        if not fitz:
            raise RuntimeError("PyMuPDF (fitz) is not installed.")
        doc = fitz.open(self.path)
        meta = doc.metadata or {}
        raw_toc = doc.get_toc() # [[lvl, title, page], ...]
        toc = []
        if raw_toc:
            for idx, item in enumerate(raw_toc):
                lvl, title, page = item[0], item[1].strip(), item[2]
                toc.append({
                    "index": idx + 1,
                    "level": lvl,
                    "title": title,
                    "start_page": page
                })
        else:
            # Fallback: estimate chapters if no TOC
            toc.append({"index": 1, "level": 1, "title": "Full Document", "start_page": 1})

        total_pages = doc.page_count
        # Estimate word count by sampling
        sample_pages = min(10, total_pages)
        sample_words = sum(len(doc[p].get_text().split()) for p in range(sample_pages))
        avg_words_per_page = sample_words / sample_pages if sample_pages > 0 else 250
        est_words = int(avg_words_per_page * total_pages)

        return {
            "title": meta.get("title") or self.path.stem,
            "author": meta.get("author") or "Unknown",
            "format": "PDF",
            "total_pages": total_pages,
            "estimated_words": est_words,
            "toc": toc
        }

    def _info_epub(self) -> dict:
        with zipfile.ZipFile(self.path, 'r') as z:
            # Find container.xml
            try:
                container = z.read('META-INF/container.xml')
                root = ET.fromstring(container)
                opf_path = root.find('.//{*}rootfile').attrib['full-path']
            except Exception:
                opf_path = [n for n in z.namelist() if n.endswith('.opf')][0]

            opf_dir = str(Path(opf_path).parent)
            if opf_dir == '.':
                opf_dir = ''
            opf_content = z.read(opf_path)
            opf_root = ET.fromstring(opf_content)

            # Metadata
            ns = {'dc': 'http://purl.org/dc/elements/1.1/', 'opf': 'http://www.idpf.org/2007/opf'}
            title_el = opf_root.find('.//dc:title', ns)
            author_el = opf_root.find('.//dc:creator', ns)
            title = title_el.text if title_el is not None and title_el.text else self.path.stem
            author = author_el.text if author_el is not None and author_el.text else "Unknown"

            # Spine
            manifest = {}
            for item in opf_root.findall('.//{*}manifest/{*}item'):
                manifest[item.attrib.get('id')] = item.attrib.get('href')

            spine_ids = [item.attrib.get('idref') for item in opf_root.findall('.//{*}spine/{*}itemref')]
            
            chapters = []
            total_words = 0
            for idx, sid in enumerate(spine_ids):
                href = manifest.get(sid)
                if not href:
                    continue
                file_rel = f"{opf_dir}/{href}".lstrip('/') if opf_dir else href
                try:
                    raw_content = z.read(file_rel).decode('utf-8', errors='ignore')
                    clean_text = clean_html(raw_content)
                    words = len(clean_text.split())
                    if words < 30:
                        continue  # Skip empty or cover pages
                    total_words += words
                    
                    # Extract heading or fallback
                    first_lines = [l for l in clean_text.splitlines() if l][:3]
                    ch_title = first_lines[0] if first_lines else f"Section {idx+1}"
                    if len(ch_title) > 60:
                        ch_title = ch_title[:57] + "..."
                        
                    chapters.append({
                        "index": len(chapters) + 1,
                        "spine_index": idx,
                        "file": file_rel,
                        "title": ch_title,
                        "word_count": words
                    })
                except Exception:
                    continue

        return {
            "title": title,
            "author": author,
            "format": "EPUB",
            "total_chapters": len(chapters),
            "estimated_words": total_words,
            "toc": chapters
        }

    def _info_kindle(self) -> dict:
        # Check novel-translator-th kindleunpack
        ku_path = Path("~/.gemini/config/skills/novel-translator-th/scripts")
        if ku_path.exists() and (ku_path / "translator.py").exists():
            return {
                "title": self.path.stem,
                "author": "Unknown",
                "format": self.suffix.upper().lstrip('.'),
                "message": "Use kindleunpack via translator.py to unpack mobi8/epub structure",
                "toc": []
            }
        return {
            "title": self.path.stem,
            "author": "Unknown",
            "format": self.suffix.upper().lstrip('.'),
            "toc": []
        }

    def extract_chapter(self, target_idx: int) -> str:
        """Extracts text of a given chapter or page range."""
        info = self.get_info()
        if self.suffix == '.pdf':
            doc = fitz.open(self.path)
            toc = info.get("toc", [])
            if not toc:
                return "\n".join([page.get_text() for page in doc])
            
            # Find item
            item = next((t for t in toc if t["index"] == target_idx), None)
            if not item:
                raise ValueError(f"Chapter index {target_idx} not found in TOC.")
            start_p = item["start_page"] - 1 # 0-based
            # Next chapter page
            next_items = [t for t in toc if t["index"] == target_idx + 1]
            end_p = next_items[0]["start_page"] - 2 if next_items else doc.page_count - 1
            if end_p < start_p:
                end_p = start_p
            
            text_blocks = []
            for p in range(start_p, min(end_p + 1, doc.page_count)):
                text_blocks.append(f"--- [Page {p+1}] ---\n" + doc[p].get_text())
            return "\n\n".join(text_blocks)

        elif self.suffix == '.epub':
            with zipfile.ZipFile(self.path, 'r') as z:
                toc = info.get("toc", [])
                item = next((t for t in toc if t["index"] == target_idx), None)
                if not item:
                    raise ValueError(f"Chapter index {target_idx} not found in TOC.")
                raw = z.read(item["file"]).decode('utf-8', errors='ignore')
                return f"# {item['title']}\n\n" + clean_html(raw)
        else:
            raise NotImplementedError("Use unpack mode for Kindle AZW3/MOBI books first.")

def main():
    parser = argparse.ArgumentParser(description="Book Extractor for book-summary skill")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Info
    p_info = subparsers.add_parser("info", help="Get metadata and TOC")
    p_info.add_argument("file", help="Path to book file")

    # Chapter
    p_chap = subparsers.add_parser("chapter", help="Extract specific chapter text")
    p_chap.add_argument("file", help="Path to book file")
    p_chap.add_argument("index", type=int, help="Chapter index from TOC (1-based)")

    # Dump
    p_dump = subparsers.add_parser("dump", help="Dump all chapters to output folder")
    p_dump.add_argument("file", help="Path to book file")
    p_dump.add_argument("-o", "--output", required=True, help="Output directory")

    args = parser.parse_args()
    extractor = BookExtractor(args.file)

    if args.command == "info":
        info = extractor.get_info()
        print(json.dumps(info, ensure_ascii=False, indent=2))

    elif args.command == "chapter":
        text = extractor.extract_chapter(args.index)
        print(text)

    elif args.command == "dump":
        info = extractor.get_info()
        out_dir = Path(args.output)
        out_dir.mkdir(parents=True, exist_ok=True)
        toc = info.get("toc", [])
        print(f"Dumping {len(toc)} sections to {out_dir}...")
        for item in toc:
            idx = item["index"]
            title_clean = re.sub(r'[\/\\:\*\?\"<>\|]', '_', item["title"])[:40].strip()
            fname = out_dir / f"{idx:02d}_{title_clean}.txt"
            try:
                ch_text = extractor.extract_chapter(idx)
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(ch_text)
                print(f"  [OK] Extracted: {fname.name} ({len(ch_text.split())} words)")
            except Exception as e:
                print(f"  [Error] Chapter {idx}: {e}")

if __name__ == "__main__":
    main()
