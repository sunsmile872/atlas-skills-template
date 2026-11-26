---
name: pmr-slide-creator
description: Creates PM&R board-level presentations (.pptx) and 1:1 synced speaker notes (PPTX Notes + PRESENTER_NOTES_MASTER.md; optional --docx on explicit request) in two modes: (1) Topic/Board Lecture Mode (--engine bento, PptxGenJS 16:9 Bento/KPI/Chart/Continuum + 5-Layer Claim-ID + Google Slides Chart Normalizer) from ./textbook reference/ PDFs, and (2) Journal Club Mode (--mode jc) with authentic 4x paper table/figure crops + Red/Teal highlight boxes, Left-Accent/Hero KPI cards, 1-section-per-slide official CASP UK (11 checklists) or NIH NHLBI appraisal forms, conditional Safety & Dropout + Outcome Scale Primer slides, and 100% spoken English presenter notes. Executes via decoupled 4-Agent Pipeline (Agent 02 -> Human Checkpoint 1 -> Agent 03 [PDF-Firewalled] -> audit-deck -> Independent Agent 11 [Pro] + Agent 12 [Inherit] -> Human Checkpoint 2).
---

# PM&R Slide Creator (`pmr-slide-creator`)

Use this skill whenever creating a **PM&R presentation deck + 1:1 spoken presenter notes** in either of two modes:
- **Mode 1: Topic / Board Lecture Mode (Default `--mode topic --engine bento`)** — uses `./textbook reference/*.pdf` + Bento/Visual-First PptxGenJS engine (`14.0 pt` / `13.0–13.5 pt` Arial) + Thai spoken scripts (`--lang th`).
- **Mode 2: Journal Club Mode (`--mode jc --lang en --engine python`)** — uses a primary journal article PDF in `./source/` (or uploaded PDF) + optional `@karpathy-paper-lab` brief / thesis `SOT.md`, outputting **26–32 glanceable slides** + **English Speaker Notes**.

For interactive slide-by-slide refinement or post-delivery fixes, invoke **`pmr-slide-auditor`**.

---

## Core Philosophy & 5-Layer Error-Proof Architecture

1. **Decoupled 4-Role Pipeline (Zero Self-Grading, Zero PDF Hallucination)**:
   - **Role 1 — Evidence & Script Lead (`Agent 02`, `Pro`)**: Reads primary PDFs exclusively (**never** call `read_file` directly on large multi-hundred-page `.pdf` files — always extract targeted pages via `slide_auditor_cli.py search-textbooks` or PyMuPDF `fitz` to prevent `>1M tokens` crashes); locks 100% verbatim atomic claims (including verbatim `quote` text & exact page spans `pp. X–Y` — zero synthesized paraphrases in `claim_registry`) into `evidence_bundle_raw.json`, runs `claim_schema_compiler.py` (`-> evidence_bundle.json`), assigns `Planned Archetype` per slide (`Visual-First` + `Anti-Monotony`), and authors `notes_data_modules/mod*.py` (**Lean Slide, Rich Script**: deep clinical rationales, mechanisms, Q&A Traps, and exact card-type color wording such as `"การ์ดแถบสี..."` for white-bg left-accent cards vs. `"การ์ดสี..."` for full-tinted cards).
   - **Role 2 — PDF-Firewalled Visual Builder (`Agent 03`, `Inherit`)**: **Never reads textbook PDFs.** Compiles `.pptx` strictly from locked `evidence_bundle.json` + approved figures (`extracted_assets/`), normalizes Google Slides charts (`fix_pptx_charts_gslides.py --pptx <deck.pptx> --evidence evidence_bundle.json` so `bar_colors` auto-map without brittle `chartN.xml` guessing), injects notes into `.pptx` + `PRESENTER_NOTES_MASTER.md`, renders PNGs + Contact Sheet via LibreOffice (`visual_qa_renderer.py`), and verifies layout spacing before review. For horizontal clustered comparison charts (`1st` vs `2nd`), verify visually that `1st` sits chronologically ABOVE `2nd` matching the legend left-to-right, and lock aligned `plotArea` coordinates when stacking charts vertically.
   - **Roles 3 & 4 — Parallel Independent QA Gates (`Agent 11 [Pro]` + `Agent 12 [Inherit]`)**: After automated `slide_auditor_cli.py audit-deck` passes (`0` errors), `Agent 11` extracts targeted textbook pages via PyMuPDF `fitz` (never raw `read_file` on large PDFs) to verify `.pptx` + spoken notes + subtitle superscripts 1:1 against primary PDFs + `USER_INSTRUCTIONS_MASTER.md` (`35+35+30 = 100`), while `Agent 12` audits the rendered PNG Contact Sheet via `PPTEval` (`35+35+30 = 100`). Zero self-grading; any post-audit edit loops back cleanly through `Agent 02 -> Agent 03 -> audit-deck -> Agent 11 + Agent 12`.

2. **100% Dynamic Primary Reference — Strict Zero External Info, Verbatim Numbers & Chart Hygiene**:
   - Every fact, number, classification, diagnostic criterion, drug dose, and figure (across Slides, Tables, Charts, Spoken Scripts, and Staff Q&A Traps) must come **exclusively** from the project's `./textbook reference/` (or `./source/` for JC) with **100% Verbatim Numerical Fidelity** (no rounding, no altered ranges, no external/weight assumptions).
   - **Chart Data Hygiene (One Denominator / One Study Design per Axis)**: Never mix incompatible denominators (e.g., anatomic digit shares vs. comorbidity multi-digit rates vs. population prevalence) or heterogeneous study designs/endpoints on a single chart axis. Split incompatible series into separate cards or stacked single-purpose charts, and enforce unambiguous axis labels (e.g., `"Trigger Finger in DM"`, not `"Diabetes Prevalence"`).
   - **Claim-ID & Native Superscripts (`¹ ² ³ ⁴`)**: Strip repeated inline textbook names from body cards. Attach native superscripts onto **words** (never digits like `A1²`) across **both body cards and quantitative claims in slide subtitles**, sync compact `Ref: [1] pp. ...` bottom-left + `01 / N` bottom-right on every slide, and conclude with a **Primary Textbook References** slide (`extract-covers` thumbnails or neutral book icon).
   - **Strict Ban on Ambiguous Shorthand**: Never emit `NS` (*clashes with Normal Saline* -> write `not significant` / `(not sig.)`), `lit` (`range`/`published cohorts`), `SQ` (`Subcutaneous`/`Subcut.`), `meta` standalone (`meta-analysis`), `q2h` (`every 2 h` / `every 2 hours`), or unexpanded `CTR` on early slides before defining `carpal tunnel release`. Prefer `Ultrasound`, `27-gauge, 5/8-inch`, `average`/`weeks`, `first-morning`.

3. **Visual-First, Anti-Monotony & Smart Visual Decision Rule**:
   - Prefer KPI Hero + Charts, 2×2 Matrices, Bento Grids, Process Continuums, and Alternating Split Figures (`>= 50%` visual/chart/figure/diagram slides). **Never repeat the same `archetype` 3 slides in a row** and alternate `figure_side` (`left`/`right`/`top`).
   - **Smart 3-Way Rule**: (Case 1) Multi-book synthesis -> Native Table/Cards; (Case 2) Canonical textbook figure/table -> `4x` crop via `auto-find-figures` (`#FFFFFF` borderless); (Case 3) No authentic textbook visual -> present **3-Way Comparison** (2D Flat Medical Vector on `#FFFFFF` with `Standard 25` zero embedded banners, Native Table, or Full-Width Content Card).

4. **Lean Slide, Rich Script & No Default `.docx`**:
   - Default output is **`.pptx` (embedded Speaker Notes on `1..N` slides) + `PRESENTER_NOTES_MASTER.md`**. Do **not** generate standalone `.docx` files unless the user explicitly passes `--docx`.
   - Enforce **Script Cleanliness**: `0` `"เสมอ"`, `0` `Step 1..4` mechanical recitals, `0` parentheses `(...)` or `(p. X)` page citations in `script`, exact **Chart Color ↔ Script Sync**, realistic cumulative timestamps (`[MM:SS - MM:SS]` aligned with Slide 01 intro), and **No Double Thank-You** across the last two slides.

---

## Step-by-Step Workflow (Steps 0 to 4)

### Step 0: Interactive Onboarding, Readiness Check & Style Selection

Immediately when invoked on a new project, run the readiness check and present the **Quick-Start Onboarding Guide** to the user:

```bash
python3 ~/.gemini/config/skills/pmr-slide-creator/scripts/slide_creator_cli.py check-ready --project-dir .
```

Present the following structured onboarding message in Thai:

1. **ภาพรวมขั้นตอนการทำงาน (2-Stage Workflow Overview)**:
   - **ระยะที่ 1 (`pmr-slide-creator`)**: เตรียมไฟล์ PDF ใน `./textbook reference/` $\rightarrow$ เลือกโทนสีสไลด์ (Theme Preset) $\rightarrow$ สแกนสารบัญเพื่อเสนอ **เฉพาะตาราง Outline หัวข้อสไลด์** ให้ตรวจก่อน $\rightarrow$ ดึงความจำ `USER_INSTRUCTIONS_MASTER.md` ล่าสุด + สกัดรูปจริงจากตำราสร้างไฟล์ `.pptx` และ `.docx` ฉบับแรก
   - **ระยะที่ 2 (`pmr-slide-auditor`)**: เมื่อสร้างสไลด์ชุดแรกเสร็จแล้ว ส่งไม้ต่อไปยังสกิล **`pmr-slide-auditor`** เพื่อตรวจละเอียดทีละสไลด์ (Single-Slide Deep Audit) หรือเป็นชุด (Batch Audit) พร้อมซิงก์กฎใหม่สะสมเข้าความจำหลักตลอดเวลา
2. **สถานะโฟลเดอร์ `./textbook reference/`**:
   - **หากยังไม่มีไฟล์ PDF ใน `./textbook reference/`**: ระบบได้สร้างโฟลเดอร์ `./textbook reference/` รอไว้ให้แล้ว แจ้งให้ผู้ใช้นำไฟล์ PDF ตำราหลัก (เช่น *Braddom*, *Cuccurullo*, *DeLisa*, *Preston & Shapiro*, CPG) มาวางใน `./textbook reference/` ก่อน แล้วแจ้ง **1) หัวข้อเรื่อง (Topic)** และ **2) ระยะเวลานำเสนอ / จำนวนสไลด์เป้าหมาย**
   - **หากพบไฟล์ PDF ใน `./textbook reference/` แล้ว**: แสดงรายชื่อไฟล์ PDF ที่ตรวจพบทั้งหมดทันที
3. **เลือกโทนสีและสไตล์สไลด์ (Built-in Slide Style Presets)**:
   - แจ้งว่าหากไม่ระบุ ระบบจะใช้ **Preset A (`navy_teal` — Default มาตรฐานสอบบอร์ด)** ทันที หรือเลือกสลับได้ 4 โทน:
     - **Preset A (`navy_teal` — Default)**: Clinical Navy (`#0F172A`) & Teal (`#0D9488`) บนพื้นขาวอมฟ้า (`#F8FAFC`)
     - **Preset B (`academic_brick` — {{INSTITUTION}} / {{INSTITUTION}} Tone)**: Brick Terracotta (`#A73B24`) & Dark Slate (`#1E293B`) บนพื้นขาวอุ่น (`#FAF8F6`)
     - **Preset C (`emerald_charcoal` — Rehab / MSK Tone)**: Deep Emerald (`#065F46`) & Warm Amber (`#D97706`) บนพื้นขาวอมเขียวอ่อน (`#F3F8F6`)
     - **Preset D (`custom`)**: กำหนดโค้ดสีเอง หรือแนบรูปสไลด์ตัวอย่างเพื่อให้ระบบตั้งค่าสีตามต้องการ

---

### Step 1: Scan Textbooks & Checkpoint 1 — Propose Outline + `figure_candidates.png` (Do Not Build Slides Yet)

Once PDFs are in `./textbook reference/` and the user confirms the topic and duration/slide count:

1. Dispatch `Agent 02` (`Pro`) to run `scan-refs` + `slide_auditor_cli.py auto-find-figures` (`extract-covers` + `find-figures` -> `figure_candidates.png`) across `./textbook reference/*.pdf`:
   ```bash
   python3 ~/.gemini/config/skills/pmr-slide-creator/scripts/slide_creator_cli.py scan-refs \
     --project-dir . --query "<topic keywords>" --output reference_outline.json
   python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py auto-find-figures \
     find-figures --project-dir . --query "<topic keywords>" --out-sheet figure_candidates.png
   ```
2. Build an adaptive module outline with **`Planned Archetype`** per slide (`kpi_hero_plus_chart`, `split_figure_card`, `top_figure_plus_strip`, `quadrant_2x2_*`, `bento_2col_care`, `process_continuum_4step`, `references_slide`), respecting `Anti-Monotony` (never 3 consecutive identical archetypes).
3. **Human Checkpoint 1 (Mandatory Stop)**: Present **Slide Outline Table + matched figure candidates (`figure_candidates.png` + book/page IDs + 3-Way options where no textbook visual exists)** for explicit user approval before cropping final `4x` assets or compiling slides.

---

### Step 2: Initialize Engine & Sync `USER_INSTRUCTIONS_MASTER.md`

After the user approves Checkpoint 1:

```bash
python3 ~/.gemini/config/skills/pmr-slide-creator/scripts/slide_creator_cli.py init-project \
  --project-dir . --mode topic --engine bento --theme "<navy_teal|academic_brick|emerald_charcoal>" \
  --topic "<Presentation Title>" --slides <N>
```

This creates:
- `build_slides.js` + `package.json` + `icons/` (Bento/Visual-First 16:9 PptxGenJS engine; or `make_presentation.py` when `--engine python` / `--mode jc`)
- `evidence_bundle_raw.json` (Stage 1 Claim-ID skeleton for `Agent 02`)
- `generate_presenter_notes.py` + `sync_to_drive.py` + `USER_INSTRUCTIONS_MASTER.md` (with `.pptx` Notes + `PRESENTER_NOTES_MASTER.md` default)
- `extracted_assets/`, `notes_data_modules/`, and `audit_buffer/` directories

---

### Step 3: Execute Stage 1 (`Agent 02`) -> Stage 2 (`Agent 03`) -> Stage 3 (`audit-deck` + `Agent 11` & `Agent 12`)

1. **Stage 1 (`Agent 02`, `Pro`)**:
   - Extract approved figures at `4x` zoom (`auto-find-figures extract-id` / `extract-covers`), inspect every PNG via `read_file`, author atomic `claim_registry` + slides in `evidence_bundle_raw.json`, compile via `claim_schema_compiler.py` (`-> evidence_bundle.json`), and write 1:1 spoken scripts/Q&A/transitions in `notes_data_modules/mod*.py`.
2. **Stage 2 (`Agent 03`, `Inherit`, PDF-Firewalled)**:
   - Compile `.pptx` from locked `evidence_bundle.json` (`node build_slides.js`), run `fix_pptx_charts_gslides.py --pptx <deck.pptx>`, inject presenter notes (`inject_notes_v2.py` -> `.pptx` + `PRESENTER_NOTES_MASTER.md`), and render LibreOffice PNGs + Contact Sheet (`visual_qa_renderer.py`) to inspect every modified slide visually.
3. **Stage 3 (`audit-deck` + Parallel Independent `Agent 11 [Pro]` & `Agent 12 [Inherit]`)**:
   ```bash
   python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py audit-deck \
     --project-dir . --pptx <deck.pptx> --evidence evidence_bundle.json --md PRESENTER_NOTES_MASTER.md --profile pmr_board
   ```
   - Dispatch `Agent 11` (`Pro`) for 1:1 PDF + `USER_INSTRUCTIONS_MASTER.md` verification and `Agent 12` (`Inherit`) for Contact Sheet `PPTEval` verification (`references/pp_eval_rubric.md`). Zero self-grading; any post-audit edit loops back cleanly through `Agent 02 -> Agent 03 -> Agent 11 + 12`.

---

### Step 4: Human Checkpoint 2 — Deliver Drive Link, Contact Sheet & Handoff to `pmr-slide-auditor`

1. Report exact `.pptx` path, `PRESENTER_NOTES_MASTER.md`, Google Drive link (`sync_to_drive.py` / `gdrive mutate upload`), Contact Sheet PNG, and independent `Agent 11` + `Agent 12` scores.
2. Provide ready-to-copy commands if the user wants targeted slide-by-slide edits via **`pmr-slide-auditor`**:
   - **ตรวจละเอียดรายหน้า (Interactive Deep Audit)**: พิมพ์ **`audit สไลด์ X ด้วย pmr-slide-auditor`**

---

## Journal Club Mode (`--mode jc --lang en --engine python`)

Use whenever building a **{{INSTITUTION}} PM&R Journal Club** deck (~26–32 slides) from a primary article PDF + `@karpathy-paper-lab` brief:

1. **Initialize Engine & Official Checklist**:
   ```bash
   python3 ~/.gemini/config/skills/pmr-slide-creator/scripts/slide_creator_cli.py init-project \
     --project-dir . --mode jc --lang en --study-type <rct|sr_ma_rct|before_after|...> \
     --topic "<Article Short Title>" --slides 30
   ```
   *(Copies the matching CASP UK 2024 or NIH NHLBI checklist PDF into `./source/` automatically; standardizes `Arial` font, symmetrical Eligibility cards, word-wrapped CASP cards with exact Amber verdict classification for `Cannot Tell`/`Not Reported`, badge-safe header width, and bottom-right `01 / N` numbering via `finalize_jc_slide_numbers(prs)`.)*
2. **Design & Layout Standard (Senior Glanceability, `4-6 sec scan`)**:
   - **Opener (`Slides 1-3`)**: Clean Cover (Title + Resident/Advisor) $\rightarrow$ `4x` Article Header Crop (`p. 1`) $\rightarrow$ 6-Section TOC.
   - **Chrome-Lite Body (`add_jc_slim_header`)**: Single-line `22 pt` title (`19.5 pt` wrapped if `callout_badge` present) + slim bottom `Ref:` + `01 / N` pagination.
   - **Visual Variety (`1 slide = 1-2 visual chunks`, keyword cues `<= 12 words`)**:
     - `01 Introduction`: Clinical burden, Modality compare (`add_jc_left_accent_cards_slide`), `Gap & Objective` 2-block card, plus **Outcome Scale / MCID Primer** when a clinical score is central.
     - `02 Methods`: `Study Design` 4 Hero KPI cards + **Ethics IRB & Reporting Guideline**, symmetric `Eligibility` (`add_jc_eligibility_slide`), `Protocols`, `Outcomes & Stats`.
     - `03 Results`: `4x` CONSORT/PRISMA crop + **`add_jc_cropped_table_slide`** (`h=6.08"`, pixel-mapped Coral Red `#DC2626` / Teal `#0D9488` highlight boxes verified via `visual_qa_renderer.py` Contact Sheet + `read_file`). Reserve native tables for Baseline Audit / synthesis not in the paper.
     - `04 Discussion`: **Study Strengths** (`2x2` left-accent cards), Literature Comparison, **Conditional `Safety & Dropout Analysis`** (whenever AEs `> 0%` or dropout `> 5-10%` / differential attrition occurs), **Study Limitations**.
     - `05 Conclusion`: Tight keyword takeaways strictly matching verified significant endpoints.
     - `06 Critical Appraisal & {{INSTITUTION}} Bridge`: **1 Checklist Section per Slide** via **`add_jc_checklist_slide`** (official `4x` CASP UK 2024 or NIH NHLBI PNG with centered `✓` on left, verdict badges + rationale on right) $\rightarrow$ **{{INSTITUTION}} Clinical / Thesis Bridge** $\rightarrow$ `Thank You & Q&A`.
3. **100% Spoken English Speaker Notes (`.pptx` Notes + `.md` Default; `--docx` Optional)**:
   - Run `python3 generate_presenter_notes.py` (writes `.pptx` Notes + `PRESENTER_NOTES_MASTER.md` with 1:1 parity; pass `--docx` only when printed Word handouts are explicitly requested). Keep `0` English AI Slop (`crucial`, `paramount`, `delve`, `landscape`, `notably`, `"In conclusion"`), `0` Thai chars, `0` em-dashes (`—`), and `0` ambiguous shorthand (`NS`, `lit`, `SQ`, `meta`).
4. **Verify via Automated + Independent Dual Gates**:
   - Run `fix_pptx_charts_gslides.py --pptx <deck.pptx>` (if charts exist), `visual_qa_renderer.py` Contact Sheet, `slide_auditor_cli.py verify-jc-deck --project-dir . --pptx <deck.pptx> --lang en`, and dispatch independent `Agent 11 [Pro]` (Paper PDF 1:1 truth/endpoints/CASP audit) + `Agent 12 [Inherit]` (PNG Contact Sheet & Table Highlight verification).
