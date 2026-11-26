---
name: clinical-academic-editor
description: Drafts, edits, and audits clinical/PM&R manuscripts, protocols, and discussions in Markdown-First format (3-paragraph funnel Introduction, Pure Objective Results, 6-step mechanistic Discussion, AMA/Vancouver style). Includes deterministic Python tools (`citation_engine.py` for 2-pass PubMed/CrossRef 1:1 citation checks and resequencing; `deliverable_auditor.py` for 4-pillar statistical, LaTeX/SI, and anti-slop audits).
---

# Clinical Academic Editor

## Core Rules
1. **Markdown-First**: Draft, revise, and audit all proposals, results, and manuscripts in `.md` before any `.docx` export. Never export `.docx` unprompted; when explicitly requested, convert equations to native OMML via `docx-math-formatter`.
2. **Zero-Fabrication**: Never invent PMIDs, DOIs, author names, $N$, $p$-values, $OR$, $HR$, or CIs. Missing data -> STOP and ask.
3. **Pure Results Separation**: Keep Results strictly descriptive (Tables 1–3, effect sizes, CIs, $p$-values). Zero mechanistic speculation or literature commentary in Results.

## Structural Blueprints
- **Introduction (3-Paragraph Funnel)**:
  1. Clinical Burden & Functional Impact
  2. Current Standard of Care & Specific Knowledge Gap
  3. Study Objective, Specific Aims & Hypothesis
- **Discussion (6-Step Mechanistic Architecture)**:
  1. Principal Finding (concise synthesis, do not echo raw Results tables)
  2. Biological / Neurophysiological / Biomechanical Mechanism
  3. Literature Dialogue (corroboration + contradictions + novel contribution)
  4. Clinical & Rehabilitation Practice Implications
  5. Broader Health Systems Significance
  6. Limitations (methodological/confounding) & Future Directions

## Automated Verification Tools

### 1. Citation Engine (`citation_engine.py`)
```bash
# 2-pass live PubMed + CrossRef audit + optional local PDF grounding
python3 ~/.gemini/config/skills/clinical-academic-editor/scripts/citation_engine.py audit-2pass path/to/draft.md --library path/to/Literature_Library

# Dry-run or in-place reference resequencing by appearance order
python3 ~/.gemini/config/skills/clinical-academic-editor/scripts/citation_engine.py resequence path/to/draft.md
python3 ~/.gemini/config/skills/clinical-academic-editor/scripts/citation_engine.py resequence path/to/draft.md -i
```

### 2. 4-Pillar Deliverable Auditor (`deliverable_auditor.py`)
Audits read-only with SHA-256 byte-level invariance proof across:
- **Pillar 1**: Forward/reverse citation completeness & live API verification
- **Pillar 2**: Statistical consistency ($0 \le p \le 1$, reject $p = 0.000$, subgroup sums $n_A + n_B = N$, percentage accuracy, Peduzzi $\text{EPV} \ge 10$, `SOT.md` cross-check)
- **Pillar 3**: Balanced LaTeX math delimiters (`$...$`, `$$...$$`) & SI unit spacing (`15 mm Hg`, not `15mmHg`)
- **Pillar 4**: Banned AI lexicon & long clause-stacked sentences ($> 45$ words)

```bash
python3 ~/.gemini/config/skills/clinical-academic-editor/scripts/deliverable_auditor.py path/to/draft.md --sot path/to/SOT.md
```

Walk through the generated `citation_audit_report.md` and `deliverable_audit_report.md` with the investigator before applying manual edits.
