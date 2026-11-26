---
name: lecture-notes
description: >-
  Compiles medical lecture slide PDFs (clean digital slides or lecture photos) and audio recordings (.m4a, .mp3, .wav, Google Drive) into high-resolution iPad study suites with Thai clinical pearls, audio timestamps, case deep dives, and diagnostic infographics.
---

# Medical Lecture Notes Compiler (`lecture-notes`)

## Overview

The `lecture-notes` skill transforms medical lecture presentation slides and companion audio recordings into a comprehensive, high-resolution study suite designed specifically for iPad reading and Apple Pencil note-taking (e.g. GoodNotes, Notability).

It automates:
1. **Slide Extraction & Enhancement**: Supports both clean digital PDF exports (instant 100% vector/high-dpi extraction) and lecture hall screen photos (adaptive CLAHE contrast enhancement on pure white iPad canvas with zero text clipping).
2. **Audio-to-Slide Time Alignment**: Transcribes spoken lecture audio, maps timestamps to corresponding slides, and extracts high-yield **Clinical Pearls** (diagnostic rules, red flags, verbal emphasis from the lecturer).
3. **iPad-Optimized Deliverables**: Renders pixel-perfect, vertical A4 pages on a pure white background (`#FFFFFF`) with clinical color coding (Navy Blue, Teal, Mint).

---

## When to Activate This Skill

Activate this skill whenever:
- The user mentions `lecture-notes` or says "ทำ lecture-notes ให้หน่อย"
- The user provides a lecture slide PDF along with an audio recording (`.m4a`, `.mp3`, `.wav`) or transcript
- The user asks to summarize a medical lecture, symposium, or conference presentation into iPad study notes

---

## Input Modes & Handling

### 1. Slide Deck (PDF)
- **Mode A: Clean Digital Export (Default for normal PDF slides)**
  - Vector or direct digital export from PowerPoint/Keynote.
  - Extracted directly at 2.5x Retina resolution onto a pure white canvas.
  - **No cropping or contrast alteration required**.
- **Mode B: Lecture Hall Photos / Screen Captures**
  - Slides photographed from a projection screen.
  - Mounted centered on a 4:3 iPad canvas with pure white background (`#FFFFFF`).
  - Adaptive contrast enhancement (CLAHE in Lab color space) to make faint text and blue/grey tables crisp and legible.
  - **Zero text clipping**: Guarantees all titles, footnotes, citations, and edges are 100% visible.

### 2. Audio Recording (Optional but Recommended)
- Formats: `.m4a` (Apple Voice Memos), `.mp3`, `.wav`, `.aac`, or Google Drive links.
- Uses speech-to-text (Whisper/local transcription) to align spoken content with slide numbers and generate timecodes (`[MM:SS - MM:SS]`).

---

## Standard Output Suite

All output files are saved directly to the user's working folder or iCloud Drive:

```
[Output Directory]/
├── [Topic]_Annotated_Lecture_Notes_White_iPad.pdf    <-- Primary study notes (Slide + Thai pearls + Time)
├── [Topic]_Cleaned_Slides_White_iPad.pdf             <-- Cleaned slides for rapid review
├── [Topic]_Case_Deep_Dive_Slides_White_iPad.pdf      <-- Clinical cases & electrodiagnosis (if applicable)
└── [Topic]_Master_Infographic_Vertical_A4.pdf        <-- Diagnostic algorithm flowchart (if applicable)
```

### Layout Specification (Approach B Annotated Notes)
- **Dimensions**: Vertical A4 (210mm × 297mm) / iPad 4:3 ratio.
- **Background**: Pure white (`#FFFFFF`) throughout.
- **Top Section**: High-resolution slide image centered in a clean frame.
- **Bottom Section**: Clinical Pearls card with green/teal accent border:
  - ⏱️ **Timestamp Badge**: Start and end time for quick audio review.
  - 💡 **Clinical Pearls**: Bullet points in Thai summarizing what the professor emphasized verbally, especially points absent from the slide text.
  - **Safe Bottom Margin**: Clean space reserved for handwritten notes using Apple Pencil.

---

## Quick Execution

### Using the Python Compiler Script

```bash
python3 ~/.gemini/config/skills/lecture-notes/scripts/compile_lecture_notes.py \
  --pdf "/path/to/lecture_slides.pdf" \
  --notes-json "/path/to/slide_notes.json" \
  --output-dir "/path/to/output_folder" \
  --title "Polyneuropathy Masterclass" \
  --mode auto
```

### JSON Format for `--notes-json`

```json
[
  {
    "slide": 1,
    "title": "Pattern of Polyneuropathy (Symmetric vs Asymmetric)",
    "timestamp": "00:00 - 02:40",
    "points": [
      "<strong>Symmetric vs Asymmetric:</strong> จุดเริ่มต้นของการ Approach คือดูว่ารอยโรคสมมาตรหรือไม่ ถ้าสมมาตรให้คิดถึง systemic, toxic, หรือ metabolic",
      "<strong>The 50% Rule:</strong> ในกลุ่ม Length-dependent อาการชาที่มือจะไม่เกิดจนกว่าขาจะชาถึงระดับเข่า",
      "<strong>DTRs:</strong> Reflex จะหายจากปลายเท้าก่อน (Ankle jerk หายก่อน Knee jerk)"
    ]
  }
]
```

---

## Agent Workflow Guidelines

1. **Inspect Inputs**:
   - Locate the PDF slides and identify total page count.
   - Detect if slides are clean digital vector exports or lecture screen photos.
   - Locate any companion audio files (`.m4a`, `.mp3`) or transcripts.

2. **Transcribe & Extract Clinical Pearls**:
   - Process audio segments mapped to each slide.
   - Extract clinical pearls, focusing on diagnostic rules, clinical reasoning, pitfalls, and red flags emphasized by the instructor.

3. **Build and Render Deliverables**:
   - Generate `slide_notes.json` or structured HTML data.
   - Run `compile_lecture_notes.py` using Google Chrome headless to guarantee zero layout shift, crisp vector text, and exact iPad pagination.

4. **Verify Quality**:
   - Verify that 100% of pages are generated without omissions.
   - Ensure pure white background (`#FFFFFF`) with zero text clipping.
   - Inform the user with direct links to the generated PDF files.
