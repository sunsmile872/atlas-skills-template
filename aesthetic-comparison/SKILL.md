---
name: aesthetic-comparison
description: >-
  Compiles patient before/after treatment photographs into a professional medical-grade poster infographic with optional clinical treatment protocols and customizable light/dark themes.
---

# Aesthetic Comparison

## Overview
This skill provides a programmatic workflow for medical aesthetic clinics to generate high-quality, standardized "Before & After" comparison images and publication-ready clinical evaluation posters. It transposes EXIF orientation automatically, performs **automatic anatomical face detection, scale compensation, and vertical height calibration** to ensure head size, eye level, nasal base, and chin line match at an exact 1:1 ratio across Before and After panels, crops photos to a consistent 3:4 aspect ratio, and formats clinical treatment protocols into a vertical A4 poster template.

### Critical Rule: No Critiques / Commentary
- **ห้ามใส่คำวิจารณ์โดยเด็ดขาด**: Never add subjective critiques, anatomical assessment text, clinical opinions, or evaluation commentary bullets on posters or comparison views.
- Keep all graphics, posters, and comparisons strictly clean and objective: only show factual treatment protocols/dosages, patient/clinic metadata, anatomical plane alignment guides, and calibrated imagery.

## Dependencies
- **Pillow** (PIL) - Used for image rotations, scaling, canvas drawings, and typography.
- **OpenCV** (`opencv-python`) - Used for automated facial feature detection, scale normalization, and height alignment.

## Quick Start
Run the comparison compiler using the following CLI pattern:
```bash
python3 ~/.gemini/config/skills/aesthetic-comparison/scripts/generate_comparison.py \
  --patient-dir "~/Gemini Antigravity/Playground/patient_folder" \
  --patient-name "Khem Jirat" \
  --theme "dark" \
  --output-dir "~/Gemini Antigravity/Playground/patient_folder"
```

## Utility Scripts
The generator script `~/.gemini/config/skills/aesthetic-comparison/scripts/generate_comparison.py` supports these arguments:
- `--patient-dir`: Absolute path to a folder containing `before` and `after` directories.
- `--patient-name`: Name of the patient (defaults to `"Unknown Patient"`), printed in the footer.
- `--theme`: Color scheme of the output image (`dark` or `light`).
- `--swap`: If set, reverses the mapping (maps the `after/` folder to the BEFORE column, and the `before/` folder to the AFTER column).
- `--views-only`: If set, only generates the individual side-by-side comparison images and skips building the full clinical poster.
- `--protocol-json`: Optional JSON string containing the treatment protocol fields:
  - `date`: Injection date string
  - `total_volume`: Combined volume injected (e.g., `"6.0 cc"`)
  - `neuramis_deep`: Volume of Neuramis Deep used (e.g., `"4.0 cc"`)
  - `restylane_vl`: Volume of Restylane Vital Light used (e.g., `"2.0 cc"`)
  - `temp_product`: Product name for Temporal region
  - `temp_dose`: Dosage for Temporal region (e.g., `"1.0 cc per side"`)
  - `mid_dose_n`: Neuramis dosage for Midface (e.g., `"1.0 cc per side"`)
  - `mid_dose_r`: Restylane dosage for Midface (e.g., `"1.0 cc per side"`)
- `--output-dir`: Folder path where the side-by-side files and final poster will be written.

### Example JSON for `--protocol-json`:
```json
{
  "date": "04/07/2026",
  "total_volume": "6.0 cc",
  "neuramis_deep": "4.0 cc",
  "restylane_vl": "2.0 cc",
  "temp_product": "Neuramis Deep (Sharp)",
  "temp_dose": "1.0 cc per side",
  "mid_dose_n": "1.0 cc per side",
  "mid_dose_r": "1.0 cc per side"
}
```

## Common Mistakes
1. **Invalid Folder Structure**: Ensure the patient directory has exactly two subfolders named exactly `before` and `after`.
2. **Missing Pillow Dependency**: If running in a new environment, make sure to execute using `uv run` to ensure dependencies like Pillow are resolved correctly.
3. **Mismatched Image Count**: Ensure the number of photos in the `before` folder matches the number of photos in the `after` folder. If they differ, the script exits with code 1 and outputs a list of files to help you resolve the pairs.
