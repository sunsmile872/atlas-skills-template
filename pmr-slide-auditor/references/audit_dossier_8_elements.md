# 8-Element Inline Audit Dossier Reference Template

Every slide audited by `pmr-slide-auditor` **MUST** be presented inline in chat with all 8 elements below in exact order:

---

### 1. Header & Metadata
- **Slide Number & Title**: `Slide XX: <Title> — <Subtitle>`
- **Category Badge**: `<CATEGORY>`
- **Slide Layout Function**: `add_split_content_slide` / `add_table_slide` / `add_content_slide`
- **Audit Status**: `PASS 100% (Verified against Primary Textbooks & USER_INSTRUCTIONS_MASTER.md)`

---

### 2. ASCII Wireframe Layout Box
Render a clear 16:9 ASCII box showing the left card width, right card width (or full-width card / native table), image dimensions, and caption placement:
```text
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│ [CATEGORY BADGE]                                                                         │
│ Slide Title (22pt Bold) — Subtitle (11.5pt Muted)                                        │
├───────────────────────────────────────────────┬──────────────────────────────────────────┤
│ Left Content Card (width = X.XX", h = 5.35")  │ Right White Card (width = Y.YY", h=5.35")│
│  • Bullet 1 Heading: Concise description...   │  ┌────────────────────────────────────┐  │
│  • Bullet 2 Heading: Concise description...   │  │     Authentic Textbook Figure      │  │
│  • Bullet 3 Heading: Concise description...   │  │      (Native W x H px, 4x HD)      │  │
│  • Bullet 4 Heading: Concise description...   │  └────────────────────────────────────┘  │
│  • Bullet 5 Heading: Concise description...   │  Figure Title (9.5pt Bold)               │
│                                               │  Source: Textbook, Ch. X, Fig. Y, p. Z   │
├───────────────────────────────────────────────┴──────────────────────────────────────────┤
│ Ref: Primary Textbook (Edition), Ch. X, pp. Y–Z [Book Page Only]                         │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### 3. Bullets on Slide (`build_slides.py`) — Dual-Density Choices (Option A vs Option B)
Present both text density options for the user to choose on a slide-by-slide basis:

#### Option A: Balanced Standard (12–16 words / bullet — rich clinical nuance)
1. **`<Heading 1>`**: `<Description 1>` *(XX words)*
2. **`<Heading 2>`**: `<Description 2>` *(XX words)*
3. **`<Heading 3>`**: `<Description 3>` *(XX words)*
4. **`<Heading 4>`**: `<Description 4>` *(XX words)*
5. **`<Heading 5>`**: `<Description 5>` *(XX words)*

#### Option B: Ultra-Lean Telegraphic (6–10 words / bullet — high-yield metrics & airy white space)
1. **`<Heading 1>`**: `<Lean Description 1>` *(XX words)*
2. **`<Heading 2>`**: `<Lean Description 2>` *(XX words)*
3. **`<Heading 3>`**: `<Lean Description 3>` *(XX words)*
4. **`<Heading 4>`**: `<Lean Description 4>` *(XX words)*
5. **`<Heading 5>`**: `<Lean Description 5>` *(XX words)*

- **Agent Recommendation (Text Density)**: Provide a 1-line clinical and visual rationale recommending Option A or Option B (e.g., *"แนะนำ Option B สำหรับสไลด์นี้เนื่องจากมีรูปภาพ/ตารางข้างเคียง เพื่อเปิด Breathing room สบายตา"* หรือ *"แนะนำ Option A เพื่อคงกลไกพยาธิสรีรวิทยาอย่างครบถ้วน"*).
- **Slide Footnote (`Ref:`)**: `<Book Page Only Citation>`

---

### 4. Visual Asset & Textbook Provenance (Smart Visual Decision Rule & Best-Figure Gate)
- **Smart Visual Decision**: Explain whether the slide uses (1) a Native Table, (2) an Authentic Textbook Figure / Cropped Canonical Table, or (3) When no textbook figure exists: Mandatory 3-Way Comparison offered to user (Option 1: AI-Generated Clean 2D Medical Vector Infographic, Option 2: Native Table, Option 3: Full-Width Content Card).
- **If using an image**:
  - **File**: `extracted_assets/<filename>.png`
  - **Native Resolution**: `W × H px` (extracted at 4x zoom from `<Textbook PDF>`, Book p. `X` / PDF p. `Y`)
  - **PPTX White Card Geometry**: Card `left=X.XXX"`, `width=Y.YYY"`, `bottom=6.900"` | Picture `W" × H"`, `top=1.660"`, `bottom=Z.ZZZ"` | Caption+Source `top=C.CCC"`, `bottom=D.DDD" <= 6.850"` (100% enclosed)
  - **Candidate Figure Comparison Table**:

| Candidate Option | Textbook Source (Book Page / PDF Page) | Native Resolution | Selection Verdict & Clinical Rationale |
| :--- | :--- | :--- | :--- |
| **Option 1 (Selected)** | ... | ... | **SELECTED**: ... |
| **Option 2** | ... | ... | Not selected: ... |

---

### 5. 1:1 Spoken Script (บทพูดภาษาไทยธรรมชาติ 28–30 วินาที)
Display the full spoken script (`~110–130 words`, zero bullet header recital) and show the explicit `[1]`–`[5]` mapping to the 5 slide bullets.

---

### 6. Clinical Transition Hook
> `*Transition*: "<Natural clinical bridge to Slide XX+1>"`

---

### 7. Staff Defense Trap (Spotlight Examination Trap — {{ADVISOR_NAME}} Style)
```text
Q: <In-depth biomechanical, pathophysiological, or board-level clinical question>?
A: <Evidence-based resident answer citing exact primary textbook mechanisms and numbers>.
```

---

### 8. Line-by-Line Textbook Citation Verification Table

| Bullet / Element | Primary Textbook & Chapter | Book Page | PDF Page | Verbatim Textbook Quote (100% Verified) | Status |
| :--- | :--- | :---: | :---: | :--- | :---: |
| **Bullet 1** | ... | p. XX | p. YY | *"..."* | **PASS 100%** |
| **Bullet 2** | ... | p. XX | p. YY | *"..."* | **PASS 100%** |
| **Bullet 3** | ... | p. XX | p. YY | *"..."* | **PASS 100%** |
| **Bullet 4** | ... | p. XX | p. YY | *"..."* | **PASS 100%** |
| **Bullet 5** | ... | p. XX | p. YY | *"..."* | **PASS 100%** |
