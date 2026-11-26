# Navy / Teal / Mint Pitch Note & CRF Templates + Thai Instrument Guide

## 1. Visual Styling Tokens (A4 Chrome Print-to-PDF)
- **Page:** `@page { size: A4; margin: 11mm 12mm 11mm 12mm; }`
- **Fonts:** `"Sukhumvit Set", "Thonburi", -apple-system, BlinkMacSystemFont, sans-serif` (offline-safe on macOS, crisp Thai tonemarks).
- **Palette:**
  - Navy Header / Table Header: `#0F2744` -> `#163A5F` with `#0D9488` bottom accent
  - Teal Section Bar / Mint Callout: `#0D9488`, background `#F0FDFA`, border `#5EEAD4`
  - Slate Body Text: `#1E293B`, muted `#475569`, table border `#CBD5E1`

## 2. Standard 2-Page Pitch Note (or 3-Page Executive Visual Dossier)
- **HTML Readability & Rendering Rule:** Write crisp, scannable clinical prose using clean `<strong>`, `<em>`, `&rarr;`, `<sup>`, and `<sub>` tags—never leave raw Markdown backticks or LaTeX macros (`\xrightarrow`, `\text{}`) in HTML, and **never wrap normal terms, stats, or PMIDs in inline gray `<code>` pills** inside prose/tables (reserve subtle pill badges strictly for sparse status tags like `แนะนำ` or `เลือก 1 แบบ`). **Keep PRISMA hit counts, Boolean search strings, and screening ledgers (`S1/S2/Q3`, `CT-1..4`) out of the Pitch Note**—summarize database checks in 1 concise natural sentence (e.g., confirming zero competing trials on PubMed, ClinicalTrials.gov, and TCTR).
- **Mode A — Standard 2-Page Pitch Note (Quick Executive Brief):**
  - **Page 1:** Navy header banner -> Mint Working Title + 1-Sentence Core Story & Research Questions -> 2-Column Side-by-Side Comparison Cards (`1A` Advisor Anchor + `1B` Meta-Analysis/Benchmark; always include Author, Title, Journal/Year, PMID) -> PICO & Minimum Data Set Table.
  - **Page 2:** Sample Size Math & Justification -> OPD/Clinical Workflow -> 4 Clinical Translation Impacts (Mint box) -> Advisor Meeting Discussion Questions (+ `TCTR`/IRB notes if interventional).
- **Mode B — Strictly 3-Page Executive Visual Dossier (Readable Advisor Meeting Pack):**
  - **One-Study-Per-Row & Brevity Rule:** Never merge two distinct studies into one row—every cited paper gets its own row (Author/Journal/Year, PMID/PMCID, `N`, and **1–2 concise lines** of quantitative takeaways). Keep heavy regression proofs and exhaustive checklists inside `SOT.md` / `01_Protocol`.
  - **Page 1 (60-Second Plain-Thai Funnel + Hypotheses):** Navy Hero Banner -> Mint 1-Sentence Core Idea -> **60-Second Plain-Thai 3-Step Storytelling Funnel** (*Step 1: What prior studies/local team already proved [explicitly naming arms compared and outcomes measured] $\rightarrow$ Step 2: The 3–4 unanswered gaps [and why subjective/psychophysical outcomes alone are insufficient] $\rightarrow$ Step 3: Our solution*, keeping dense numbers/PMIDs out of Page 1 prose) -> **Structured Research Questions (`1 Primary + 2 Secondary`) & Explicit Two-Sided Statistical Hypotheses ($H_0: \mu_A = \mu_B$ vs. $H_1: \mu_A \neq \mu_B$, $\alpha = 0.05$)**.
  - **Page 2 (Methodological Flaw Fix Matrix + Advisor Lineage + Workflow):** **Prior-Study Flaw vs. Our Protocol Fix Matrix** & **Advisor/{{INSTITUTION}} Continuity Table** -> **Horizontal 4-Step Visual OPD Workflow** (with strict measurement order so physical compression/stretching never contaminates objective imaging) -> Concise Eligibility & Safety Box.
  - **Page 3 (Verified Evidence Table + Sample Size Comparison + 5 Decisions):** Clean 8–10 Study Quantitative Evidence Table (1 study per row with exact PMID/PMCID) -> Sample Size Comparison Table (e.g., **Design 1 Recommended: 2-Arm Parallel Baseline-Adjusted ANCOVA `Borm 1 - ρ²`** vs. **Design 2 Backup: Crossover `even N` / Williams design**, explicitly noting carryover trade-offs) -> **5-Point Advisor Decision Checklist** (including EC{{INSTITUTION}} V6.0 `SUB-10` device form if applicable).

## 3. Printable 2-Page OPD CRF Layout
- **Page 1:** Study ID/Date header, 2-column Inclusion/Exclusion checkboxes (`☐`), Demographics & Clinical Variables (`Must-Have` vs. `Optional`).
- **Page 2:** 2-column Functional/Clinical Scoring Rubrics (e.g., `FAC 0–5` & `mRS 0–6` so no separate cheat sheet is needed), Objective Test Box (e.g., `TUG` protocol + `white-space: nowrap` on trailing blanks), Questionnaire Summary Table, and Clinical Notes + Sign-off.

## 4. Common Thai Clinical Instruments & Licensing Notes
- **Free / Open-Access (Direct Download / CPG Excerpt):**
  - **Thai Short FES-I (7 items):** Official University of Manchester PDF (`sites.manchester.ac.uk/fes-i/`, translated by Sasiporn Ounjaichon; free for non-commercial use).
  - **Thai DMS Fall Prevention CPG (Sept 2019 / พ.ศ. 2562):** Extract only essential pages (Cover, FOF evidence, Short FES-I, `TUG` protocol, Imprint) rather than keeping the 16 MB full file.
  - **WHOQOL-BREF-Thai (26 items):** Thai Department of Mental Health open clinical scale.
- **Copyrighted / Registration Required (Never Bypass):**
  - **Thai `EQ-5D-5L + EQ-VAS`:** Register free non-commercial academic study at `https://registration.euroqol.org/` (include sample size `N`, institution, Thai language, paper/digital mode); score with Thai HITAP Value Set (Pattanaphesaj et al., 2018).
