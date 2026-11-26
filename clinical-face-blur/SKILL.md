---
name: clinical-face-blur
description: >-
  Automatically blurs and de-identifies patient and attending staff faces in clinical videos and patient photographs. Supports Google Drive links (via local DriveFS SQLite resolution) and local filesystem paths. Employs YOLOv8-pose anatomical facial keypoint tracking with temporal trajectory smoothing, soft-edge feathered elliptical Gaussian blurring, audio preservation, and automatic temporary file cleanup.
---

# Clinical Face Blur & Patient De-Identification

## Overview
This skill automates medical-grade patient de-identification and face anonymization for clinical videos and patient examination photographs in compliance with healthcare privacy guidelines (HIPAA / PDPA).

### Key Features:
- **Anatomical Keypoint Tracking (YOLOv8-pose)**: Accurately locates facial boundaries (eyes, nose, ears, chin, and hairline) even in challenging pediatric or neurological examinations (patients tilted, crying, neck extension, or heads partially cropped at frame edges).
- **Feathered Elliptical Gaussian Blur**: Replaces harsh pixelated or square censor boxes with a soft-edge, broadcast/medical-grade elliptical vignette blur that preserves surrounding anatomical context (clothing, posture, and examination technique).
- **Smooth 2-Pass Video Stabilization**: Scans the entire video, detects head positions, and applies temporal moving-average trajectory smoothing to eliminate jitter or flickering between frames. Original synchronized AAC audio is preserved.
- **High-Resolution Apple HEIC & JPEG Support**: Handles 48 MP / 12 MP iPhone HEIC and JPEG photos with automated EXIF orientation correction.
- **Direct Google Drive Integration**: Automatically resolves Google Drive file and folder links (`https://drive.google.com/...`) via the local Google Drive for Mac SQLite metadata database, saving processed files directly to the user's synced Drive folder.
- **Clean Workspace**: Automatically purges intermediate scratch files upon task completion.

---

## Dependencies
All scripts should be executed using `~/.local/bin/uv run`:
- `ultralytics` (YOLOv8-pose model for anatomical face/shoulder tracking)
- `opencv-python==4.10.0.84` (Image processing, filtering, and video capture)
- `pillow` (EXIF orientation normalization and image handling)
- `imageio-ffmpeg` (Bundled Apple Silicon FFmpeg binary for video muxing)
- System `sips` (macOS native hardware HEIC/JPEG conversion)

---

## Quick Start

### 1. Process from Google Drive Link (Automatic Detection)
To blur any video or folder of photos directly from a Google Drive URL:
```bash
~/.local/bin/uv run \
  --with ultralytics \
  --with "opencv-python==4.10.0.84" \
  --with pillow \
  --with imageio-ffmpeg \
  python3 ~/.gemini/config/skills/clinical-face-blur/scripts/blur_media.py auto \
  --input "https://drive.google.com/drive/folders/1TQNBgDh1GuRHzk3riTtklx4X7--jX4Nz"
```

### 2. Process a Local Clinical Video
```bash
~/.local/bin/uv run \
  --with ultralytics \
  --with "opencv-python==4.10.0.84" \
  --with pillow \
  --with imageio-ffmpeg \
  python3 ~/.gemini/config/skills/clinical-face-blur/scripts/blur_media.py video \
  --input "/path/to/patient_video.mp4" \
  --output "/path/to/patient_video_blurred.mp4"
```

### 3. Process a Folder of Clinical Photos
```bash
~/.local/bin/uv run \
  --with ultralytics \
  --with "opencv-python==4.10.0.84" \
  --with pillow \
  --with imageio-ffmpeg \
  python3 ~/.gemini/config/skills/clinical-face-blur/scripts/blur_media.py photo \
  --input "/path/to/patient_photos" \
  --output-dir "/path/to/patient_photos/Blurred" \
  --format jpg
```

---

## CLI Options

| Command | Option | Description | Default |
| :--- | :--- | :--- | :--- |
| `auto` | `--input` | Local path or Google Drive file/folder URL | *Required* |
| `auto` | `--output-dir` | Target output directory | Same as source |
| `auto` | `--format` | Output photo format (`jpg`, `heic`, or `both`) | `jpg` |
| `video` | `--input` | Path to video file | *Required* |
| `video` | `--output` | Destination path for blurred MP4 | `{name}_blurred.mp4` |
| `video` | `--blur-strength`| Gaussian blur kernel size | `75` |
| `photo` | `--input` | Path to photo file or folder | *Required* |
| `photo` | `--output-dir` | Directory for blurred outputs | `{folder}/Blurred` |
| `photo` | `--format` | Output format (`jpg`, `heic`, or `both`) | `jpg` |

---

## Workflow Guidelines

1. **Locating Google Drive Media**:
   - When given a Google Drive link, extract the file/folder ID and query `metadata_sqlite_db` at `~/Library/Application Support/Google/DriveFS/<account_id>/` to find the local path in `~/Library/CloudStorage/GoogleDrive-*/`.
   - Run processing directly against the local mirror. Google Drive for Mac will automatically synchronize the blurred files back to the cloud.
2. **Clinical Privacy Standards**:
   - Always verify whether background healthcare staff or nurse faces and ID badges are visible; ensure all individuals are anonymized.
   - For photos without visible faces (e.g. focused limb exams or prone position), preserve the images intact without false-positive blurring of limbs or torso.
3. **Workspace Cleanliness**:
   - Keep the user's workspace tidy: delete intermediate frame extractions, debug images, or preview files once processing is complete.

---

## Common Pitfalls & Solutions

- **EXIF Orientation on iOS Photos**: Apple iPhone photos (HEIC/JPEG) contain EXIF orientation tags. Always use `ImageOps.exif_transpose` before running detection to avoid coordinates being rotated 90°.
- **Video Audio Loss with OpenCV**: OpenCV's `VideoWriter` strips audio. Always stream raw video frames through FFmpeg or use `-c:a copy` to remux the original audio track into the blurred video.
- **Head Partial Cropping**: In pediatric bed examinations, the head may be partially cropped by the top frame border. Use shoulder keypoints (`left_shoulder`, `right_shoulder`) to extrapolate head position and maintain continuous coverage up to `y = 0`.
