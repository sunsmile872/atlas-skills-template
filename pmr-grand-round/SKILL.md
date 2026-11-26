---
name: pmr-grand-round
description: "Prepares PM&R and EMG Conference Grand Round playbooks and A4 PDF study guides from short prompts or real patient cases. Triggers on: grand round, emg conference, neurology/rehab case prep, Stroke, SCI, TBI, ALS/MND, CIDP, GBS, MG, plexopathy, radiculopathy, myopathy."
---

# PM&R & EMG Grand Round (`pmr-grand-round`)

Generates structured, clinical-reasoning Grand Round playbooks (and printable A4 iPad PDFs) grounded in the resident's Medical & PM&R Knowledge Vault (`vault-consult`) and current guidelines.

## Core Tone & Design Standards
- **Pure Clinical Reasoning:** Frame every history cluster, exam maneuver, and test choice around anatomical localization, syndrome differentiation, and functional/therapeutic decisions. Keep language strictly clinical and physician-natural (Thai explanations with exact English medical terminology).
- **Define on First Mention & Explain "Why":** Whenever introducing composite diagnostic terms (e.g., *Chronic + Active*, *Complete vs. Incomplete*) or regional/nerve count rules, define their exact criteria immediately on first appearance and explain the anatomical/clinical rationale behind the rule.
- **Consistency Gate:** Keep qualifying conditions identical across callout boxes and comparison tables (never omit required qualifiers such as *"paired with chronic neurogenic MUAPs"* inside summary table cells).
- **Dual-System Physical Exam:** Present bedside examination in **Neurological System Sequence** (*General/Mental/Speech → Cranial Nerves → Upper Limb → Thoracic/Resp → Lower Limb → Sensory & Cerebellar → Spine & Bedside Mimic Screens → Gait & Functional Baseline*), stating **Why** for every item and **How-to** specifically for high-trap maneuvers (`Key-Traps`). Follow immediately with a **Summary Map** translating system findings into diagnostic/anatomical regions or levels.
- **Visual Format:** Vertical A4 HTML-to-PDF in Dark Navy (`#0F172A`), Teal (`#0D9488`), and Mint (`#CCFBF1`) with flexbox bottom footers (`margin-top: auto`) so pages never collide. Let sections expand across as many clean A4 pages as needed without cramping to an arbitrary page count.

---

## Step 1: Select Execution Mode
Classify the request into one of three branches and read **only** the matching reference blueprint:
1. **EDX / Neuromuscular Mode** *(ALS/MND, CIDP, GBS, MG, Plexopathy, Radiculopathy, Mononeuropathy, Myopathy)* → read [`references/edx_mode.md`](references/edx_mode.md).
2. **Neurorehab / PM&R Mode** *(Stroke, SCI, TBI, Spasticity, Amputee, Dysphagia/Bladder rehab)* → read [`references/neurorehab_mode.md`](references/neurorehab_mode.md).
3. **Hybrid Mode** *(e.g., Post-stroke shoulder drop/plexopathy, SCI conus vs. cauda equina)* → read both references and merge Rehab Problem List with targeted EDX Planning.

If the prompt includes real patient data (clinical vignette, MMT, NCS table, or Needle EMG findings), activate **Case-Adaptive Output**: embed a dedicated **Case Localization, Data Interpretation & Discussion Script** into the guide (and for formal EDX reports, follow the {{INSTITUTION}} format: `NCS shows:`, `EMG shows:`, `Conclusion: Abnormal study. According to electrodiagnostic study is compatible with [diagnosis].`).

---

## Step 2: Knowledge Grounding & Currency Check
1. **Query the Vault (`vault-consult`):** Run `python3 ~/.gemini/config/skills/vault-consult/scripts/query_vault.py <keywords>` and read relevant textbook sections (*Preston & Shapiro*, *Easy EMG*, *McLean*, *Frontera*, *Braddom*, *DeLisa*, *Campbell-Walsh*) and resident notes (`vault/rehab/`).
2. **Verify Current Standards:** Check web/literature for latest diagnostic criteria or FDA/clinical guideline updates (e.g., *Gold Coast 2020*, *EAN/PNS 2021*, *ISNCSCI 2019*, recent DMT approvals/withdrawals).
3. **Completion Criterion:** All numeric thresholds, ratios, drug statuses, and diagnostic criteria in the draft come directly from verified vault/search output.

---

## Step 3: Draft & Compile the A4 PDF
1. Copy/adapt [`templates/grand_round_a4.html`](templates/grand_round_a4.html) using the modular section sequence in the selected mode reference (`edx_mode.md` or `neurorehab_mode.md`), writing the working HTML to the conversation scratch folder and targeting the output PDF at `<workspace>/outputs/<Topic>_Grand_Round_Guide.pdf`.
2. Compile and verify the PDF using [`scripts/build_and_verify_pdf.py`](scripts/build_and_verify_pdf.py):
   ```bash
   python3 ~/.gemini/config/skills/pmr-grand-round/scripts/build_and_verify_pdf.py <input.html> <output.pdf> --png-dir <scratch_dir>
   ```
3. **Visual QA Gate (Mandatory):** Open **every** generated verification PNG with `read_file` to confirm:
   - Balanced page breaks with zero 3–5 line spillover pages.
   - Zero footer/card overlap and crisp Thai diacritics/tone marks.
   - All tables legible and consistent with callout boxes (no omitted qualifiers).

---

## Step 4: Final Delivery
Deliver the clickable `file://` link to the verified PDF along with a concise high-yield map of the pages. If real patient numbers were provided, include the verbal conference discussion summary directly in the reply.
