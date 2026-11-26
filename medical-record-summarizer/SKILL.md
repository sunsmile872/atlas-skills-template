---
name: medical-record-summarizer
description: "Summarizes raw OPD/IPD medical records (digital/scanned PDFs, iPhone .HEIC chart photos) into fact-first chronological timelines, onset-ordered problem lists, medication/exam trajectories, and chart contradiction audits, with optional Word (.docx) export and chronological PDF merge. Use when reading patient chart folders, summarizing admission/OPD history, auditing discrepancies in medical records, or answering factual chart Q&A."
---

# Medical Record Summarizer (`medical-record-summarizer`)

Synthesizes raw hospital charts (OPD/IPD folders, scanned/digital PDFs, and `.HEIC` chart photos) into **fact-first** clinical summaries with strict **source provenance** and **chart audit** verification.

---

## Core Guardrails

1. **Fact-First, Zero Extrapolation:** Report only facts documented in the chart. Attribute clinical reasoning to the recording physician/team; mark absent records explicitly as `ไม่พบข้อมูลในเวชระเบียน`. Keep the summary free of unsolicited treatment advice.
2. **Mandatory Source Provenance:** Tag every clinical claim, lab, medication, and exam finding with `[File/Page | Date]` (e.g. `[IMG_2982]` or `[OPD_p14 | 28/05/69]`).
3. **Signal-over-Noise:** Exclude billing receipts and administrative forms unless clinically relevant to continuity of care.
4. **PDPA Mode:** Default to **Full Chart Mode** for private clinical continuity; switch to **De-identified Mode** (strip name, CID, phone, address) whenever intended for teaching or presentations.

---

## 4-Stage Execution Pipeline

### Stage 1: Ingest & Prepare Inputs
1. Inspect the target path (`OPD/`, `IPD/`, or mixed photo folder):
   - **`.HEIC` / photo folder:** Run `python3 ~/.gemini/config/skills/medical-record-summarizer/scripts/prepare_chart_inputs.py prepare-photos "<src_dir>" "<scratch_jpg_dir>"` to convert `.HEIC` → `.jpg` via `sips` and flag exact SHA-256 duplicates.
   - **Multi-PDF folder (when merge is requested):** Run `python3 ~/.gemini/config/skills/medical-record-summarizer/scripts/prepare_chart_inputs.py merge-pdfs "<src_dir>" "<output_merged.pdf>"` to sort chronologically and generate bookmarks (enforcing `/Filter /DCTDecode` and `compress=False` on any embedded JPEG streams).
2. Read every converted `.jpg` (via `read_file` in parallel batches) or every PDF page (text extraction plus visual read for scans/handwriting).
3. *Completion criterion:* Every file/page in scope is accounted for in the chronological index; duplicate captures are noted.

### Stage 2: Fact-First Extraction & Chart Audit
1. Extract into structured clinical domains with `[File/Page]` provenance:
   - **Patient Profile & Pre-morbid Baseline** (demographics, underlying diseases, functional status).
   - **One-Liner Clinical Summary**.
   - **Problem List ordered by Onset** (onset/timeline, clinical status, source tags).
   - **Chronological Timeline** (PTA → referring hospital → admission → OR/POD → latest).
   - **Domain Trajectories** (serial neuro/motor exam, labs/weight trends, antibiotic & medication reconciliation).
2. **Chart Audit (Contradictions & Gaps):**
   - Cross-check bedside/copy-forward notes against primary diagnostic reports (imaging, pathology, microbiology) and medication orders; surface every discrepancy explicitly.
   - List all referenced reports or pending results absent from the folder (e.g., pending cultures, referenced MRI/consult replies).
3. *Completion criterion:* Zero ungrounded claims; every contradiction and missing referenced document surfaced.

### Stage 3: Draft Report (`Markdown-First`)
Read [`references/output_templates.md`](references/output_templates.md) and apply the matching mode:
- **Mode 1 — Clinical Summary & Chart Audit** *(default for chart folders)*
- **Mode 2 — IPD Discharge Summary & Problem Grouping**
- **Mode 3 — In-Depth Chart Review**
- **Mode 4 — Interactive Chart Q&A** *(direct evidence quote + provenance + contradiction check)*

Save the draft `.md` to `<workspace>/outputs/` (if gitignored) or conversation scratch.

### Stage 4: Export, QA & Handoff Gate
1. **Word Export (when requested):** Run:
   ```bash
   python3 ~/.gemini/config/skills/medical-record-summarizer/scripts/build_chart_docx.py "<input.md>" "<output.docx>" --title "<Title>" --subtitle "<Subtitle>" --preview-dir "<scratch_dir>"
   ```
   Confirm zero stray markdown tokens (`**`, `` ` ``) and visually inspect the rendered `qlmanage` preview PNG via `read_file`.
2. **Google Drive Sync (only when requested):** Upload outputs via `gdrive`.
3. **Mandatory Handoff Gate:** Deliver clickable `file://` link(s) with a concise summary, then ask the user **1 short question**:
   > *"ต้องการส่งต่อข้อมูลเคสนี้ให้ `vault-consult` เพื่อวิเคราะห์และวางแผน PM&R Consult ต่อไหมครับ?"*
   Invoke `vault-consult` only after explicit user confirmation.
