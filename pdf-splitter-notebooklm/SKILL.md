---
name: pdf-splitter-notebooklm
description: >-
  Splits large PDF documents, textbooks, and clinical manuals into NotebookLM-compatible parts (under 500 pages and 200MB per file). Supports auto-detecting logical sections/chapters, splitting into equal multi-part volumes, or fixed page chunks.
---

# PDF Splitter for NotebookLM (`pdf-splitter-notebooklm`)

## Overview

Google NotebookLM enforces hard limits on source uploads:
- **Maximum 500 pages per PDF document**
- **Maximum 200 MB per file**
- **Maximum 500,000 words per source**
- **Up to 50 sources per notebook**

When a user requests to split a PDF, medical textbook, research monograph, or manual for NotebookLM, this skill splits the document into properly indexed, searchable PDF parts while preserving high-resolution images, bookmarks (table of contents), vector graphics, and OCR text.

---

## Quick Start

### 1. Split into 2 Balanced Volumes (Quickest)
```bash
python3 ~/.gemini/config/skills/pdf-splitter-notebooklm/scripts/split_pdf_notebooklm.py \
  --input "/path/to/document.pdf" \
  --mode volumes \
  --num-volumes 2
```

### 2. Split Automatically by Chapters / Sections
```bash
python3 ~/.gemini/config/skills/pdf-splitter-notebooklm/scripts/split_pdf_notebooklm.py \
  --input "/path/to/document.pdf" \
  --mode sections
```

### 3. Split by Fixed Page Chunks (e.g. 200 pages each)
```bash
python3 ~/.gemini/config/skills/pdf-splitter-notebooklm/scripts/split_pdf_notebooklm.py \
  --input "/path/to/document.pdf" \
  --mode chunks \
  --chunk-size 200
```

---

## Splitting Strategies

| Mode | Flag | Description | Best Used When |
| :--- | :--- | :--- | :--- |
| **Volumes** (Default) | `--mode volumes` | Splits document into balanced parts (e.g. 2 or 3 parts), ensuring each part is under `--max-pages` (default: 450 pages). | User wants minimal files to upload (e.g. 2-volume or 3-volume set). |
| **Sections** | `--mode sections` | Reads PDF bookmarks (TOC) or detects major anatomical/thematic sections. | User wants modular files by clinical topic for precise NotebookLM citations. |
| **Chunks** | `--mode chunks` | Slices document into exact page batches (e.g. 200 or 250 pages). | Document has no logical section headers and a fixed size is desired. |

---

## Command Options

- `--input`, `-i`: (Required) Absolute path to the source PDF.
- `--output-dir`, `-o`: (Optional) Custom output directory. Default is `<source_dir>/<file_stem>_notebooklm/`.
- `--mode`, `-m`: (Optional) `volumes` (default), `sections`, or `chunks`.
- `--num-volumes`, `-n`: (Optional) Specific number of parts (e.g. `2`).
- `--max-pages`: (Optional) Page threshold per output file (default: `450`, well below NotebookLM's 500-page limit).
- `--chunk-size`: (Optional) Pages per file when using `--mode chunks` (default: `200`).

---

## Key Benefits
- **Zero Quality Loss**: Uses direct PDF stream slicing (`PyMuPDF`) without recompressing or blurring raster images.
- **Full Text Searchability**: Retains original OCR text layers and typography.
- **Section Bookmarks**: Preserves or automatically generates document outline metadata for navigation.
