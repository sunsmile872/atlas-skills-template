---
name: pmr-slide-auditor
description: Audits and refines PM&R presentation slides (build_slides.js/.py / .pptx), spoken notes (notes_data_modules/ / PRESENTER_NOTES_MASTER.md), and Google Slides charts against ./textbook reference/*.pdf (or ./source/) and ./USER_INSTRUCTIONS_MASTER.md. Harmonized with Atlas 3-Tier Mesh: runs automated audit-deck gates + independent Agent 11 (Pro PDF 1:1) & Agent 12 (Inherit PNG Contact Sheet) using references/pp_eval_rubric.md for full decks, and supports Interactive Slide-by-Slide Deep Audit with the 8-Element Inline Audit Dossier, Human Choice Gate, and Two-Way Rule Sync (sync-rule).
---

# PM&R Board-Level Slide Auditor (`pmr-slide-auditor`)

Use this skill whenever **auditing, verifying, refining, or fixing slides and spoken presenter scripts** in an existing presentation project.

---

## Execution Modes (Atlas 3-Tier Mesh & Interactive Deep Audit)

1. **Mode 1: Full-Deck Automated + Parallel Independent Gate (Default for Complete Builds)**:
   - Run the single-command automated audit first:
     ```bash
     python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py audit-deck \
       --project-dir . --pptx <deck.pptx> --evidence evidence_bundle.json \
       --md PRESENTER_NOTES_MASTER.md --profile pmr_board --render-dir renders/
     ```
     *(For Journal Club `--mode jc`, run `verify-jc-deck --project-dir . --pptx <deck.pptx> --lang en` + `render-slides`.)*
   - Dispatch **Parallel Independent Review** in fresh contexts (zero self-grading, scoring per `~/.gemini/config/skills/pmr-slide-auditor/references/pp_eval_rubric.md`):
     - **`Agent 11` (`Pro`)**: **NEVER call `read_file` directly on huge multi-hundred-page textbook PDFs** (`>1M tokens` crash risk); always extract targeted pages via `slide_auditor_cli.py search-textbooks` or PyMuPDF (`fitz`). Performs 1:1 PDF-to-`.pptx` verbatim, `claim_registry` quote verbatim (zero paraphrases), subtitle superscripts, chart XML, and `USER_INSTRUCTIONS_MASTER.md` script audit (`35 + 35 + 30 = 100`), flagging `Double thank-you` or missing subtitle superscripts explicitly (use `verify_verbatim.py --strict-warnings` for release sign-off).
     - **`Agent 12` (`Inherit`)**: Visual `PPTEval` audit across rendered LibreOffice PNGs & Contact Sheet (`35 + 35 + 30 = 100`), checking denominator clarity, chronological clustered bar order (`1st` above `2nd`), aligned `plotArea` spines, and exact card-type color sync.
   - **Re-Audit Lock & Zero Inline Bypass**: Any edit to slide copy, data, or scripts invalidates prior Gate passes and must route strictly through **`Agent 02` (`[Sub·Pro]`: PDFs via `fitz`, `evidence_bundle_raw.json` $\rightarrow$ `evidence_bundle.json`, `notes_data_modules/`) $\rightarrow$ `Agent 03` (`[Sub·Inherit]`, PDF-Firewalled: `build_slides.js`/`.py`, `.pptx`, `fix_pptx_charts_gslides.py --evidence evidence_bundle.json`, `inject_notes_v2.py`, PNG renders) $\rightarrow$ `audit-deck` $\rightarrow$ `Agent 11 [Sub·Pro]` + `Agent 12 [Sub·Inherit]`**.

2. **Mode 2: Interactive Single-Slide or Batch Deep Audit (User-Requested Targeted Edits)**:
   - Even when the user asks to refine 1–2 specific slides (e.g., *"audit สไลด์ 11 ด้วย pmr-slide-auditor"* or *"ปรับหน้า 2 กับหน้า 12"*), **the Coordinator (`01`) MUST NOT read `./textbook reference/*.pdf` or propose content/visual options `[Inline]`**.
   - **Step A (Discovery & Human Choice Gate)**: Always dispatch **`Agent 02` (`[Sub·Pro]`)** to read `USER_INSTRUCTIONS_MASTER.md`, inspect `./textbook reference/*.pdf` via PyMuPDF `fitz` (never `read_file` on whole large PDFs) + `evidence_bundle_raw.json` + `notes_data_modules/`, run Gates 1–4, and return the **8-Element Inline Audit Dossier** (`references/audit_dossier_8_elements.md`) or concrete options (enforcing One Denominator / One Study Design per Chart) for the **Human Choice Gate** before modifying any file.
   - **Step B (Isolated Preview Sandbox for Structural / Chart Redesigns)**: When refining layouts or charts on an existing delivered deck, build an isolated preview first inside `audit_buffer/preview_<tag>/` (`Agent 02 -> Agent 03 -> audit-deck -> Agent 11 [Sub·Pro] + Agent 12 [Sub·Inherit]`) and present a **Before vs. After visual comparison** (rendered PNGs/carousel) for user sign-off **before** modifying canonical production files.
   - **Step C (Production Execution after User Choice)**: Route approved edits through **`Agent 02 [Sub·Pro]` $\rightarrow$ `Agent 03 [Sub·Inherit]` (PDF-Firewalled) $\rightarrow$ `audit-deck` $\rightarrow$ `Agent 11 [Sub·Pro]` + `Agent 12 [Sub·Inherit]`**.

---

## The 5 Mandatory Quality Gates (Run Before Presenting Every Slide)

### Gate 1: Pre-Flight Master Memory & Banned Terms Check
1. **Mandatory Pre-Flight Memory Lock (ZERO EXCEPTIONS)**:
   - **Always call `read_file` on `./USER_INSTRUCTIONS_MASTER.md`** before auditing, proposing, or modifying ANY slide, and **MANDATORILY whenever a conversation has been truncated/summarized (`<CONTEXT_SUMMARY>`)**.
   - Never rely on internal weights, probabilistic memory, or summary snippets. The exact text of `./USER_INSTRUCTIONS_MASTER.md` (especially หมวดที่ 7: กฎเรื่องรูปภาพและข้อห้าม 3D/AI) must be physically read into active context before proposing any layout or visual option.
2. Run the banned-terms & ambiguous-abbreviation scanner (profile-scoped: `universal`, `pmr_board`, `journal_club`, `amputation`):
   ```bash
   python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py check-banned \
     --project-dir . --profile pmr_board --strict
   ```
   Ensure zero occurrences of banned phrases, Thai AI calques, and ambiguous shorthand (`NS` vs. Normal Saline, `lit`, `SQ`, standalone `meta`, `q2h`, or unexpanded early `CTR`).

---

### Gate 2: Textbook Verbatim Verification & Dual-Density Bullet Selection (Option A vs Option B)
1. Search `./textbook reference/*.pdf` for the slide's clinical concepts:
   ```bash
   python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py search-textbooks \
     --project-dir . \
     --query "<keywords>"
   ```
2. **Formulate Dual-Density Bullet Choices in Element 3**:
   - **Option B (Ultra-Lean Telegraphic: `6–10 words` per bullet) — (Primary Default Recommendation - Rule 24)**: Crisp keywords, high-yield numbers, and airy white space / minimalist aesthetic. Default for all Tier 1 & Tier 2 general slides.
   - **Option A (Balanced Standard: `12–16 words` per bullet)**: Rich clinical nuance, full pathophysiology, and balanced readability. Reserved primarily for Tier 3 deep biomechanical formulas, drug titration doses, or complex multi-step diagnostics.
   - **No Regressive Lengthening (Quality Guard Role)**: If the slide's active bullets are already crisp Ultra-Lean, 100% textbook verified, and zero banned words, **preserve the approved phrasing 100%**. Never arbitrarily expand concise text back into dense paragraphs. Only propose modifications when fixing textbook factual discrepancies or removing banned terms.
   - **Agent Recommendation**: Recommend Option B by default (or Option A for Tier 3 heavyweights) with a 1-line clinical rationale.
   - **Uniform Auditorium Pro Typography Standard (Level 3 Baseline)**: Font sizing across the master deck is calibrated to **Heading 16.0 pt Bold** (`Helvetica Neue`), **Body 14.0 pt Regular** (`Arial`, +36.1% glyph/ink surface area), **Slide Title 24.0 pt Bold**, and **Subtitle 13.5 pt Regular**. Option B achieves its ultra-clean look through generous white space while maintaining this prominent, auditorium-ready font size.
3. **4-Point Quality Rubric (Applies to both Option A & B)**:
   - **100% Textbook Verifiable, Zero External Information & Exact Verbatim Numbers**: Every fact, number, percentage, range, decimal, angle, drug dose, or pressure/time threshold (on slides, tables, spoken scripts, and Q&A defense traps) must come **exclusively** from the PDF files inside `./textbook reference/` and be reproduced **100% verbatim without any modification** (strictly no rounding, no range alteration, no approximation, and no importing facts from external sources or AI internal training weights).
   - **High PM&R Clinical Actionability**: Emphasizes physiatric assessment, biomechanics, rehabilitation prescription, or complication prevention.
   - **Clean 2–4 Word Bold English Heading**: No long parenthetical sub-clauses inside the bold heading.
   - **Zero Banned Words**: No `landmark`, `workhorse`, `axiom`, `stump`, `PLP`, `RLP`, etc.
4. **Book Page Only in Slide Footnote**:
   - The slide's `footnote=` parameter must display **only the printed Book Page** (e.g., `Atlas of Amputations 4th ed., Ch. 51, pp. 600–601`). Put the PDF page number only in Element 8 of the Audit Dossier.

---

### Gate 3: Smart Visual Decision Rule & 3-Way Comparison, Visual `read_file`, & Dynamic White Card Framing
1. **Apply the Smart Visual Decision Rule (Never Force Unrelated Images)**:
   - **Zero Unilateral Visual Decisions with Proactive Recommendations Allowed (Human Choice Gate)**:
     The agent is **STRICTLY PROHIBITED** from unilaterally deciding on a visual choice or filtering out textbook candidates on its own. Element 4 of every slide audit MUST display the **Best-Figure Selection Table** listing all extracted textbook candidate figures (with book page, chapter, figure number, and native pixel resolution) alongside 2D flat vector, native table, and single card options. The agent is encouraged to provide a polite, clinically reasoned recommendation (*"Agent Recommendation"*) under the table, but **MUST STOP immediately** and wait for the user's explicit command before modifying `build_slides.py` or committing changes.
   - **Zero 3D AI & Zero AI Humans**: Never propose, generate, or accept 3D glossy plastic renders or photorealistic AI human figures. Slide visuals must ONLY use authentic textbook figures, 2D Flat Medical Vector (Navy/Teal/Mint theme), or native tables.
   - **Case 1 (Multi-Book Synthesis or Multi-Modality Comparison)** $\rightarrow$ Use a **Native PowerPoint Comparison Table (`add_table_slide`)**.
   - **Case 2 (Authentic Clinical Photo, Anatomical Diagram, or Canonical Cropped Textbook Table/Box)** $\rightarrow$ Use **`add_split_content_slide`** with a high-res (`4x zoom`) crop from `./textbook reference/*.pdf`. *(If both a native table and a cropped textbook table/box are good candidates, offer both options for the user to choose).*
   - **Case 3 (No Authentic Matching Figure or Table in Primary Textbooks)** $\rightarrow$ **Mandatory 3-Way Comparison**: Render all 3 options and display side-by-side previews for the user to choose:
     - **Option 1: AI-Generated Clean 2D Medical Vector Infographic** (`add_split_content_slide` with right-card 4-quadrant/multi-panel vector art in Navy/Teal/Mint theme, strictly 2D flat line-art, zero photorealistic people/3D plastic, 100% legible English text, transparent `figure_source="AI-Generated Clinical Infographic | Based on <Ref>"`).
     - **Option 2: Native Comparison Table** (`add_table_slide`).
     - **Option 3: Full-Width Content Card** (`add_content_slide` or `add_split_content_slide(..., image_file=None)`).
   - **Case 4 (Clinical Algorithms, Pathways & Progressive Continuum - 3 to 5 Stages)** $\rightarrow$ Use **`add_algorithm_slide`**:
     - Triggered for slides covering sequential clinical decision pathways, triage, or progressive rehabilitation continuum.
     - Displays 3 to 5 horizontal stage cards ($11.733" \times 5.350"$) with connecting chevrons (`➔`).
     - Header color progression: Navy Dark (`#0A192F`) $\rightarrow$ Navy Mid (`#1E3A8A`) $\rightarrow$ Deep Teal (`#0F766E`) $\rightarrow$ Teal Green (`#0D9488`).
     - 2 to 3 Action Items per card (`Label: Description`, $\le 10-12$ words each) to preserve ample breathing room ($\ge 0.20"$ above bottom container $6.90"$).
     - Spoken script strictly 1:1 ($N$ stages = $N$ sentences, 40–50s duration, zero robotic stage header recital).
     - In Element 4, always present the 4 standard choices with Native Flowchart Algorithm highlighted as **(Recommended)**, and stop for user choice.
2. **Mandatory Visual Inspection (`read_file`) & Multi-Level Parity**:
   - Whenever a slide uses an image, **always call `read_file` on the PNG file** in `extracted_assets/` to verify with your own eyes that:
     - It came from the true **Book Page** (never confuse Book Page with PDF Page!).
     - It matches every anatomical level discussed on the slide (e.g., if the slide covers both **Transtibial** and **Transfemoral** contractures, build a high-res composite showing both Transtibial and Transfemoral figures).
3. **Balanced White Card Framing & Dynamic Expansion**:
   - Adjust `add_split_content_slide` card parameters to match the image aspect ratio and detail density:
     - **Portrait / Vertical Figure**: `left_width=Inches(6.65)` to `Inches(7.00)`, `right_left=Inches(7.683)` to `Inches(8.033)`, `right_width=Inches(4.50)` to `Inches(4.85)`, `pic_max_height=Inches(4.48)`, `cap_top_pos=Inches(6.24)`.
     - **Standard Figure (Level 3 Default)**: `left_width=Inches(6.00)`, `right_left=Inches(7.033)`, `right_width=Inches(5.50)`.
     - **Wide / Multi-Panel / High-Detail Figure or Cropped Textbook Table**: Expand the white card to `left_width=Inches(5.10)` to `Inches(5.40)`, `right_left=Inches(6.133)` to `Inches(6.433)`, `right_width=Inches(6.10)` to `Inches(6.40)`, `pic_max_height=Inches(4.30)` to `Inches(4.50)`, `cap_top_pos=Inches(6.24)`.
4. **Verify Whole-Deck Bounds, Rendered PNGs & Google Slides Charts**:
   - Use `auto-find-figures find-figures` / `extract-id` / `extract-covers` to replace manual `--bbox` trial-and-error, and inspect every PNG with `read_file`.
   - Run whole-deck bounds + wrapped-text check (`--all`) and render a LibreOffice PNG Contact Sheet:
     ```bash
     python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py verify-pptx-bounds --pptx <deck.pptx> --all
     python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py render-slides --pptx <deck.pptx> --out-dir renders/ --contact-sheet renders/contact_sheet.png
     ```
5. **Zero Artificial Card-Inside-Card Framing & Clean Borderless Standard (Redundant Border Elimination)**:
   - The PowerPoint layout (`add_split_content_slide`) already renders a white card container (`img_card`) with a subtle Slate 200 border.
   - **Strictly Prohibited**: Never wrap clinical photos, X-rays, or diagrams inside an artificial Dark Navy (`#0A192F`) or colored container canvas with internal sub-card borders. This creates an unsightly "box inside a box inside a card" (Double/Triple Border Phenomenon).
   - **Pure White Composite Rule**: Multi-panel composites and AI vector infographics MUST use a pure white background (`RGB(255, 255, 255)`), minimal typography, and zero outlines/borders around sub-panels so the image blends seamlessly into the slide card.
   - **Tight Cropping**: Always crop textbook figures tightly to their true bounding boxes, eliminating any extraneous PDF page margins or stray lines.
6. **Standard 25 (Zero Embedded Header Rule) & Pure White Canvas Verification Gate**:
   - **Zero Embedded Header**: AI-generated infographics and diagrams embedded on slides must NEVER contain a canvas-level top title/banner. The slide native title, tracker, and figure title already label the content; embedded headers waste 20–30% of card space and duplicate headers.
   - **Pure White Canvas (`#FFFFFF`, Corner RGB >= 220)**: All AI vector infographics must be borderless on pure white `#FFFFFF`. Automated linter checks corner pixels.
   - **Mandatory Academic Transparency Attribution**: Whenever an AI image is used, `figure_source` must explicitly declare `AI-Generated Clinical Infographic | Based on <Textbook Reference>`.
   - **Automated Visual Compliance Pre-flight**: Run `python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py check-visual-compliance --project-dir .` to ensure 100% compliance across all slide image references.

---

### Gate 4: Flowing Clinical Paragraphs & Transition Hook
1. **Flowing Clinical Paragraphs (Rich Clinical Storytelling for Grand Rounds 75–90 Min)**:
   - Presenter notes are formatted as natural, articulate clinical paragraphs averaging **~45–50 seconds per slide** (~90–120 words), resulting in ~72–75 minutes for ~88 slides, leaving 15 minutes for Q&A with faculty.
   - **Zero Numbered Lists**: NEVER insert numbered bullets (1., 2., 3., 4., 5.) in spoken scripts.
   - **Figure-Guided Narrative**: Guide the audience organically through on-screen diagrams, figures, and comparison panels (e.g., *"ภาพด้านบน...", "กราฟทางขวา..."*).
2. **Standard 21 (Zero Robotic Header Recital)**:
   - **Never** read the English bullet heading aloud at the start of a sentence. Weave the concept naturally into physician-to-physician spoken Thai.
3. **Mechanism-to-Action & Pathophysiological Depth**:
   - Always explain the pathophysiological mechanism behind clinical observations and prohibitions, followed by corrective physiatric management.
4. **Clean Transition Hook**:
   - End with a natural clinical bridge (`DATA[slide_num]['trans']`) to Slide $N+1$ without appending redundant English category labels at the end.

---

### Gate 5: Two-Way Continuous Learning (`update-rule`)
Whenever the user gives feedback, adds a new style preference, bans a phrase, or refines layout standards during an audit:
1. Immediately update `./USER_INSTRUCTIONS_MASTER.md` in the current project.
2. Sync universal rules directly into `~/.gemini/config/skills/pmr-slide-creator/templates/USER_INSTRUCTIONS_TEMPLATE.md` via:
   ```bash
   python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py sync-rule \
     --project-dir . --rule "<universal rule text>"
   ```
   so every future project automatically inherits the newly learned rule!

3. Run `python3 ~/.gemini/config/skills/pmr-slide-auditor/scripts/slide_auditor_cli.py verify-jc-deck --project-dir . --pptx <deck.pptx> --lang en` + `render-slides` when auditing a **Journal Club** deck (verifies bounds, badge overlaps, Arial typography, `01 / N` pagination, 1:1 English notes parity, zero AI slop / ambiguous shorthand, and Google Slides chart XML). Default outputs remain `.pptx` Speaker Notes + `PRESENTER_NOTES_MASTER.md` (`--docx` only when requested).

---

## Mandatory Output Format: 8-Element Inline Audit Dossier

Read `~/.gemini/config/skills/pmr-slide-auditor/references/audit_dossier_8_elements.md` and output **all 8 elements inline in the chat response** for every audited slide (never collapse into a short summary or link out to `audit_buffer/`).
