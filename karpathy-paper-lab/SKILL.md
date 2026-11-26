---
name: karpathy-paper-lab
description: Distills clinical, PM&R, or AI/biomedical papers for Journal Club and 10-minute resident talks into a Core Mental Model, Mermaid Evidence Map, Mechanistic Walkthrough, Bounded Analogy, Follow-by-Hand Toy Calculation, Statistical & Arithmetic Reality Check (EPV >= 10, Table 1/CONSORT math, timepoint separation, blinding nuance), official CASP UK (11 checklists) or NIH NHLBI verbatim appraisal, and a 5-question Active Recall Staff Defense Quiz.
---

# Karpathy Paper Lab (Journal Club & Resident Defense)

Use this blueprint whenever analyzing a paper (PDF, DOI, PMID, or abstract) for **Journal Club**, **10-minute resident talks**, or **board/staff defense**.

## Grounding & Verification Rules
- **Verbatim Numbers Only**: Only state numbers ($N$, $n$, $p$-values, $OR$, $HR$, CI, ARR, NNT, medians/IQR) directly observed in the paper. If full text is unavailable and only the abstract was read, declare `<limits>Abstract-only</limits>` explicitly.
- **Arithmetic & Integrity Audit (Zero Self-Blinding)**:
  - Sum every CONSORT/flowchart branch and compare itemized exclusion sums against the exclusion header count.
  - Sum every Table 1 categorical breakdown per arm against the arm $n$; flag any published arithmetic typos and percentage mismatches.
  - Audit baseline imbalances (`p < 0.05`) and note exact rank order across arms.
- **Timepoint & Outcome Separation**: Separate immediate post-treatment (`T1-T2`) vs. follow-up (`T1-T3`), active-vs-active comparisons vs. sham/control-only gains, and primary vs. secondary outcomes without blurring timepoints.
- **Blinding & Design Reality**: Distinguish clinical outcome-assessor blinding from intervention-operator, device/imaging assessor, and statistical-analyst blinding, plus Peduzzi $\text{EPV} \ge 10$, ITT vs. Per-Protocol attrition, and repeated-measure correlation (`GEE`/`LMM` vs. unadjusted univariate tests).

---

## Official Checklist Routing (`assets/checklists/` — Never Self-Generate)

Select the **single best-fit official checklist** from `~/.gemini/config/skills/karpathy-paper-lab/assets/checklists/manifest.json` based on study design and quote **verbatim question numbers, exact wording, and `CONSIDER` prompts** (`Yes` / `No` / `Can't Tell` for CASP; `Yes` / `No` / `CD / NR / NA` for NIH):

| Study Design | Official Checklist File (`assets/checklists/...`) |
| :--- | :--- |
| Randomised Controlled Trial (RCT) | `casp_uk/randomised-controlled-trial-rct-checklist.pdf` |
| Systematic Review + Meta-Analysis of RCTs | `casp_uk/systematic-reviews-meta-analysis-rcts.pdf` |
| Systematic Review + Meta-Analysis of Observational Studies | `casp_uk/systematic-reviews-meta-analysis-observational-studies.pdf` |
| Systematic Review (Narrative / Scoping / Umbrella) | `casp_uk/systematic-review-checklist.pdf` |
| Cohort Study | `casp_uk/cohort-study-checklist.pdf` |
| Case-Control Study | `casp_uk/case-control-study-checklist.pdf` |
| Cross-Sectional Study | `casp_uk/cross-sectional-studies-checklist.pdf` |
| Diagnostic Test Accuracy Study | `casp_uk/diagnostic-study-checklist.pdf` |
| Qualitative Study | `casp_uk/qualitative-studies-checklist.pdf` |
| Economic Evaluation | `casp_uk/economic-evaluation-checklist.pdf` |
| Clinical Prediction Rule | `casp_uk/clinical-prediction-rule-checklist.pdf` |
| Before-After (Pre-Post) Study With No Control Group | `nih_nhlbi/nih-before-after-pre-post.pdf` |
| Case Series Study | `nih_nhlbi/nih-case-series.pdf` |

---

## Output Modes

### Mode A: Standard 7-Part Quick Brief (10-Min Talk / Quick Study)
1. **Core Mental Model (1 Paragraph)**: Central clinical/physiological insight in crisp prose (keep primary vs. sham/active timepoints exact).
2. **Navigable Evidence Map (Mermaid)**: `flowchart LR` showing Population $\rightarrow$ Intervention $\rightarrow$ Comparator $\rightarrow$ Primary Outcome & Main Mechanism.
3. **Input-to-Output Mechanism Walkthrough**: Step-by-step protocol, timing, dosing/intensity, and outcome battery (only state measurement order if explicitly reported in Methods).
4. **Bounded Analogy (And Where It Breaks)**: One clinical/physiological intuition analogy + exact failure boundary.
5. **Follow-by-Hand Toy Calculation**: Concrete calculation from paper numbers ($\text{ARR}$, $\text{NNT}$, $\text{EPV}$, MCID gap, or Table 1/attrition arithmetic check).
6. **Methodological & Statistical Reality Check (`<limits>`)**: Audit 3–5 concrete flaws ($\text{EPV} \ge 10$, confounders, blinding, attrition, statistical model, external validity for Thai PM&R).
7. **Active Recall Staff Defense Quiz (5 Questions)**: Rapid-fire attending questions + concise Answer Keys.

### Mode B: Full {{INSTITUTION}} PM&R Journal Club Appraisal Brief (`--journal-club`)
Include all **7 Karpathy parts** above **plus**:
- **6-Section Journal Club Pre-Digest** mapped 1:1 for `pmr-slide-creator --mode jc`:
  - `01 Introduction`: Clinical burden, mechanism comparison, Research Gap & Verbatim Objective, plus **Outcome Scale / MCID Primer** (if a key clinical score like FAC, NDI, FIM, or SWE is central).
  - `02 Methods`: Design, IRB/Ethics No., Reporting Guideline (`CONSORT`/`STROBE`/`PRISMA`), Inclusion/Exclusion keywords, Intervention protocols, Outcomes, Sample size & Statistics.
  - `03 Results`: CONSORT/Flow accounting, Table 1–N high-yield takeaways & exact highlighted cells (`p`-values / arithmetic audit / baseline imbalances).
  - `04 Discussion`: **Study Strengths** (balanced clinical value), Literature Comparison, **Safety & Dropout Analysis** (flag whenever AEs > 0% or dropout > 5–10% / differential attrition), **Study Limitations**.
  - `05 Conclusion`: Tight 1-line clinical conclusion points grounded strictly in observed significant differences.
  - `06 Critical Appraisal & Local Bridge`: Complete **Verbatim Checklist Table** from `assets/checklists/` (every item + `CONSIDER` note + verdict + evidence rationale) + **{{INSTITUTION}} / {{INSTITUTION}} PM&R Clinical & Thesis Bridge** (explicitly tagging any external thesis comparison such as `SOT.md`).
