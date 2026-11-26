---
name: video-to-pdf-slides
description: >-
  Extracts slide changes from a lecture/presentation video file and compiles them directly into a single PDF document.
---

# Video to PDF Slides (`video-to-pdf-slides`)

## Overview

The `video-to-pdf-slides` skill automates the extraction and compilation of lecture video files into clean, readable PDF documents. It detects visual slide transitions, extracts unique frames as JPEGs, and compiles them into a single multi-page PDF document.

## Dependencies

This skill is self-contained and does not depend on other agent skills. 

- **Python Dependencies** (loaded automatically via `uv run` inline script metadata):
  - `opencv-python` (slide change detection)
  - `pillow` (image processing and PDF compilation)
  - `static-ffmpeg` (provides static ffmpeg paths)

## Quick Start

You can run the entire pipeline in a single step using the `run` subcommand. Run this command from your terminal:

```bash
uv run ~/.gemini/config/skills/video-to-pdf-slides/scripts/video_to_pdf.py run \
  --video "/path/to/lecture.mp4" \
  --output-pdf "/path/to/presentation_slides.pdf"
```

This will automatically create a directory containing the slide images and a metadata JSON file inside the same folder as the output PDF, extract the slides, and compile them into the final PDF.

---

## Utility Scripts

The skill runs through a central command-line helper: `video_to_pdf.py`.

### Subcommand: `run` (Recommended)

Runs the entire extraction and compilation pipeline.

- **Arguments**:
  - `--video`: (Required) Path to the input video file.
  - `--output-pdf`: (Required) Path to the final compiled PDF document.
  - `--output-dir`: (Optional) Directory to save individual slide JPEGs (defaults to `<pdf_dir>/<pdf_name>_slides/`).
  - `--metadata`: (Optional) Path to save slide metadata JSON (defaults to `<pdf_dir>/<pdf_name>_metadata.json`).
  - `--threshold`: (Optional) Sensitivity threshold for change detection. Default is `6.0` (lower is more sensitive).
  - `--min-duration`: (Optional) Minimum visibility time in seconds for a slide. Default is `10.0` (shorter slides are merged backward).

### Subcommand: `extract-slides`

Detects changes in the video timeline and saves them as sequential JPEGs.

- **Arguments**:
  - `--video`: (Required) Path to input video file.
  - `--output-dir`: (Required) Directory to save slide images.
  - `--metadata`: (Required) Path to save the metadata JSON.
  - `--threshold`: (Optional) Default: `6.0`.
  - `--min-duration`: (Optional) Default: `10.0`.

### Subcommand: `compile-pdf`

Compiles a set of slide JPEGs (listed in a metadata file) into a PDF.

- **Arguments**:
  - `--metadata`: (Required) Path to the metadata JSON.
  - `--output-pdf`: (Required) Path to save the compiled PDF.

---

## Rate Limiting

Not applicable. All computations are performed locally.

---

## Common Mistakes

- **Incorrect Pathing**: Always verify that the video file path is correct. If the video file doesn't exist or is unreadable, the command will fail loudly.
- **Sensitivity issues**: If slides are missed or duplicate slides are kept, try adjusting `--threshold` (e.g. lowering to `4.0` for subtle changes, or raising to `8.0` if slide content has subtle animations that trigger duplicate slides).
