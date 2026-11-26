# PPTEval & Evidence Verification Scoring Rubric (`100` Points)

Independent Tier 3 Quality Gates (`Agent 11` & `Agent 12`) MUST score every delivered deck against these two `35 + 35 + 30 = 100` rubrics. Never self-grade; score from fresh context using actual compiled `.pptx`, rendered PNGs, and primary PDFs.

---

## Gate A: `Agent 11` (`Pro`) — Citation, Evidence & Instruction Rubric (`100` pts)

### 1. Verbatim & Numeric Accuracy (`35` pts)
- Every number, percentage, range, decimal, dose, needle size, duration, angle, and outcome rate matches primary PDFs **100% verbatim** (slides + charts + spoken scripts + Q&A traps).
- Deduct `-0.5` to `-2.0` per unverified number, rounding slip, synthesized causal claim without direct textbook support, or missing caveat.

### 2. Citation Precision & Zero-Mixing (`35` pts)
- **Zero-Mixing:** Claims attributed to the exact source book & printed page (`1:1` PDF-to-`.pptx` audit).
- **Structural Parity (`verify_verbatim.py`):** `0` phantom footers, `0` orphaned superscripts, `0` digit-adjacent superscripts (`A1²`), `0` unexpanded `[[k]]` tokens, exact Deck ↔ References Slide parity.
- **Subtitle Quantitative Tagging:** Quantitative takeaways in subtitles carry matching superscripts where clinically ambiguous (`-0.5` if omitted).
- **Google Slides Chart Compatibility:** `<c:strRef>`, `<c:noMultiLvlLbl val="0"/>`, and decimal `0%` across XML + `.xlsx` (`-2.0` if broken).

### 3. Clinical Pedagogical Depth & Anti-Slop (`30` pts)
- **Lean Slide, Rich Script:** Concise `8–12` word cards; deep mechanisms, contraindications, and Staff Q&A Traps live in Speaker Notes.
- **Script Cleanliness (`17/17` / `N/N` parity):** `0` `"เสมอ"`, `0` `Step 1..4` mechanical recitals, `0` parentheses/page refs `(p. X)` in `script`, `0` wrong color/percent references (`Slide ↔ Script Sync`), realistic cumulative timestamps matching Slide 01 intro, no double thank-you across final two slides.
- **Ambiguous Shorthand Ban:** `0` `NS` (*Normal Saline* clash), `lit`, `SQ`, standalone `meta`, `q2h`, or unexpanded early `CTR` (Topic or JC); `0` English AI Slop (`crucial`, `paramount`, `delve`, `landscape`, `notably`, `"In conclusion"`, `—`) in JC.

---

## Gate B: `Agent 12` (`Inherit`) — Visual & Design `PPTEval` Rubric (`100` pts)

Evaluated directly on rendered LibreOffice PNGs & Contact Sheet (`visual_qa_renderer.py`):

### 1. Content — Readability, Conciseness & Citation Clarity (`35` pts)
- Auditorium-ready typography (`14.0 pt` primary / `13.0–13.5 pt` dense grids; `Arial` with zero serif/glyph fallback), crisp line wrapping, legible `Ref:` footer & bottom-right `01 / N` pagination, clear superscript hierarchy.

### 2. Design — Layout Variety, Spacing & Visual Rhythm (`35` pts)
- **Visual-First & Anti-Monotony:** `>= 50%` visual/chart/figure/diagram slides, `0` consecutive 3-slide identical archetypes, alternating `figure_side` (`left`/`right`/`top`).
- **Zero Collisions or Overflows:** `0` clipped text, `0` card/divider overflows, `0` title-vs-badge collisions (`callout_badge`), `0` truncated chart Y-axis labels, `0` misaligned table highlight boxes (`--mode jc`).

### 3. Coherence — Figures, Palette & Reference Symmetry (`30` pts)
- Pure `#FFFFFF` borderless textbook/vector plates (`Standard 25`, zero double/triple card frames), consistent Navy/Teal/Mint or chosen theme preset, semantic chart colors matching callouts, real textbook covers (`extract-covers`) + neutral fallback slot on References slide.

---

## Release Gate Threshold
- Minimum passing score per gate: **`>= 90 / 100`** with **`0` critical errors** from `slide_auditor_cli.py audit-deck` (or `verify-jc-deck --lang en`). Any post-audit edit invalidates prior passes until re-audited.
