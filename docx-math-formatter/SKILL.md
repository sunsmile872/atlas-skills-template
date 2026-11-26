---
name: docx-math-formatter
description: >-
  Converts LaTeX formulas, raw equation text, and statistical sample-size calculations into native Microsoft Word Equations (OMML) within .docx files. Ensures full compatibility with desktop Word and Word on SharePoint/Web, preventing broken plain-text equations.
---

# Word Math Formatter (`docx-math-formatter`)

## Overview

When clinical research papers, thesis drafts, or statistical sample-size formulas are written in raw LaTeX or plain text, Microsoft Word (especially Word on SharePoint / Word Online) displays them as broken plain text without proper fractions, radicals, or subscripts.

This skill automates the parsing and conversion of LaTeX math into **Native Word Equation format (OMML - Office Math Markup Language)** in `.docx` documents, ensuring equations render properly across both Desktop Word and Web/SharePoint.

---

## Technical Pipeline

1. **LaTeX to MathML**: Converts LaTeX string to MathML XML using `latex2mathml`.
2. **MathML to OMML**: Transforms MathML to Microsoft Office Math Markup Language using `MML2OMML.XSL`.
3. **Word Document Injection**: Attaches native `<m:oMath>` elements into Word paragraphs via `python-docx` and `parse_xml`.
4. **Desktop App Sync**: Closes stale document caches in Microsoft Word via AppleScript to ensure immediate visual updates.

---

## When to Use

Activate this skill when:
- The user has equations, formulas, or statistical calculations written in plain text or LaTeX in a `.docx` file and wants them formatted as professional Word equations.
- Equations copied or viewed in **Word SharePoint / Word Online** appear broken, flattened, or plain-text.
- Medical sample size calculations ($Z_\alpha, Z_\beta, \mu, p_1, q_1$) need structured step-by-step mathematical representation.

---

## Usage Guide

### 1. Running Automated Script
Execute using `uv` with necessary XML/docx dependencies:

```bash
~/.local/bin/uv run --with python-docx --with latex2mathml --with lxml python3 \
  ~/.gemini/config/skills/docx-math-formatter/scripts/docx_math.py
```

### 2. Copy-Paste Workflow for Word SharePoint / Web
Word on the Web (SharePoint) does not support direct raw LaTeX pasting into normal text blocks. Advise the user with one of two workflows:

1. **Desktop App (Recommended)**:
   - Click **Editing** $\rightarrow$ **Open in Desktop App**.
   - Copy the equation from the locally formatted `.docx` and paste directly. Native OMML syncs cleanly back to SharePoint.
2. **Equation Box Insert (Web Shortcut)**:
   - In Word Online, go to **Insert** $\rightarrow$ **Equation**.
   - Paste the linear equation syntax (e.g., `q_1 = 21/166 = 0.13`) and press **Spacebar**. Word Online converts it to formal math instantly.

---

## Assets & Dependencies
- Stylesheet: `assets/MML2OMML.XSL` (Standard Microsoft MathML to OMML XSLT)
- Libraries: `python-docx`, `latex2mathml`, `lxml`
