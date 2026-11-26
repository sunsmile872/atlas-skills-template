---
name: video-compressor
description: >-
  Compresses large presentation and lecture videos using the highly efficient
  H.265 (HEVC) software encoder to achieve ~98% file size reduction with high visual quality.
---

# Video Compressor

## Overview
This skill provides a utility script to compress large lecture or presentation videos down to highly optimized, lightweight HEVC (H.265) files. It is specifically tailored for content with relatively static frames (like presentation slides), achieving size reductions of up to 98% while maintaining crisp readability.

## Dependencies
* **Python packages:** `static-ffmpeg`, `opencv-python`, `numpy` (installed automatically on first run of the script).

## Quick Start
You can execute the compression script directly from the terminal.

```bash
python3 ~/.gemini/config/plugins/custom/skills/video-compressor/scripts/compress.py compress --input "/path/to/original.mp4" --output "/path/to/compressed.mp4"
```

## Utility Scripts
The skill is backed by the CLI script [compress.py](file://~/.gemini/config/plugins/custom/skills/video-compressor/scripts/compress.py).

### Commands

#### 1. `compress`
Runs the video compression using the `libx265` software encoder.

```bash
python3 ~/.gemini/config/plugins/custom/skills/video-compressor/scripts/compress.py compress \
  --input "/path/to/original.mp4" \
  --output "/path/to/compressed.mp4" \
  --crf 26 \
  --preset ultrafast \
  --output-json "/path/to/result.json"
```

* **Arguments:**
  * `--input` (required): Absolute path to the source video file.
  * `--output` (required): Absolute path where the compressed video will be written.
  * `--crf` (optional, default: 26): Constant Rate Factor. Lower means higher quality. `26` is ideal for presentation slides.
  * `--preset` (optional, default: ultrafast): Encoding speed preset (e.g. `ultrafast`, `veryfast`, `fast`, `medium`). For H.265 slide compression, `ultrafast` is recommended as it runs at 5x real-time speed.
  * `--output-json` (optional): Path to write the conversion stats JSON file instead of printing to stdout.

#### 2. `validate`
Verifies visual quality difference by comparing a single frame between the original and compressed videos.

```bash
python3 ~/.gemini/config/plugins/custom/skills/video-compressor/scripts/compress.py validate \
  --original "/path/to/original.mp4" \
  --compressed "/path/to/compressed.mp4" \
  --frame 450 \
  --output-json "/path/to/validation.json"
```

* **Arguments:**
  * `--original` (required): Absolute path to the original source video.
  * `--compressed` (required): Absolute path to the compressed video.
  * `--frame` (optional, default: 450): The frame index to capture and compare (450 corresponds to 15 seconds at 30 fps).
  * `--output-json` (optional): Path to write the quality metrics JSON file instead of printing to stdout.

## Common Mistakes
1. **Running on high-motion movies:** Using `--crf 26` on a high-action scene or movie might result in visible pixelation. If compressing standard cinematic content, lower the CRF value (e.g. `--crf 20` or `--crf 22`).
2. **Missing path files:** Always pass absolute file paths to both `--input` and `--output` flags to avoid issues with working directories.
