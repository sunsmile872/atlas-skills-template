#!/usr/bin/env python3
"""
Convert Markdown book summaries with Mermaid diagrams and tables
into clean Microsoft Word (.docx) files ready for Google Docs and iPad.
Automatically syncs to Google Drive if available.
"""

import sys
import os
import re
import shutil
import tempfile
import subprocess
from pathlib import Path

import markdown
from htmldocx import HtmlToDocx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
GDRIVE_BASE_DIR = Path.home() / "Library/CloudStorage/GoogleDrive-{{USER_EMAIL}}/My Drive/Gemini/Book summary"
GDRIVE_FALLBACK_DIR = Path.home() / "Library/CloudStorage/GoogleDrive-{{USER_EMAIL}}/My Drive/Gemini/Docs from gemini"

def render_mermaid_to_png(mermaid_code: str, output_png: Path) -> bool:
    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<script type="module">
  import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
  mermaid.initialize({{
    startOnLoad: true,
    theme: 'neutral',
    themeVariables: {{
      fontFamily: 'Sarabun, sans-serif',
      fontSize: '15px',
      primaryColor: '#e0f2fe',
      primaryTextColor: '#0f172a',
      primaryBorderColor: '#0284c7',
      lineColor: '#475569',
      secondaryColor: '#f0fdf4',
      tertiaryColor: '#fef3c7'
    }}
  }});
</script>
<style>
  body {{
    background: #ffffff;
    margin: 0;
    padding: 24px;
    display: inline-block;
  }}
  .mermaid {{
    background: #ffffff;
  }}
</style>
</head>
<body>
<div class="mermaid">
{mermaid_code}
</div>
</body>
</html>"""
    
    temp_html = output_png.with_suffix(".html")
    temp_html.write_text(html_content, encoding="utf-8")
    
    cmd = [
        CHROME_PATH,
        "--headless",
        "--disable-gpu",
        f"--screenshot={output_png.resolve()}",
        "--window-size=1200,800",
        "--default-background-color=00000000",
        str(temp_html.resolve())
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=25)
        return output_png.exists() and output_png.stat().st_size > 0
    except Exception as e:
        print(f"[Warning] Failed to render Mermaid to PNG: {e}")
        return False
    finally:
        if temp_html.exists():
            temp_html.unlink()

def preprocess_markdown(md_text: str, temp_dir: Path) -> str:
    # 1. Process Mermaid blocks
    def replace_mermaid(match):
        code = match.group(1).strip()
        img_name = f"mermaid_{hash(code) & 0xffffffff:08x}.png"
        img_path = temp_dir / img_name
        success = render_mermaid_to_png(code, img_path)
        if success:
            return f"\n\n<p align=\"center\"><img src=\"{img_path.resolve()}\" alt=\"Diagram\" style=\"max-width: 100%;\" /></p>\n\n"
        return f"\n\n```\n{code}\n```\n\n"

    md_text = re.sub(r'```mermaid\s*\n(.*?)\n```', replace_mermaid, md_text, flags=re.DOTALL)

    # 2. Process GitHub-style Callouts (> [!NOTE], > [!TIP], etc.)
    def replace_callout(match):
        callout_type = match.group(1).upper()
        content = match.group(2).strip()
        icon_map = {
            "NOTE": "ℹ️ ข้อมูลเพิ่มเติม (Note)",
            "TIP": "💡 เคล็ดลับ / ข้อแนะนำ (Tip)",
            "IMPORTANT": "⚠️ ข้อควรระวัง / ประเด็นสำคัญ (Important)",
            "WARNING": "🚨 คำเตือน (Warning)",
            "CAUTION": "🛑 ข้อห้าม / ความเสี่ยงสูง (Caution)"
        }
        title = icon_map.get(callout_type, f"📌 {callout_type}")
        return f"\n\n> **{title}**<br>{content}\n\n"

    md_text = re.sub(r'>\s*\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]\s*\n((?:>.*\n?)*)', replace_callout, md_text)
    
    return md_text

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def style_document(doc: Document):
    # Set default margins (0.75 in)
    for section in doc.sections:
        section.top_margin = Inches(0.8)
        section.bottom_margin = Inches(0.8)
        section.left_margin = Inches(0.8)
        section.right_margin = Inches(0.8)
        
    # Set Normal Font
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Sarabun'
    font.size = Pt(11)
    font.color.rgb = RGBColor(15, 23, 42) # #0f172a slate-900

    # Format tables
    for table in doc.tables:
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Style header row
        if len(table.rows) > 0:
            header_row = table.rows[0]
            for cell in header_row.cells:
                # Shading light teal-navy
                shading = parse_xml(r'<w:shd {} w:fill="E0F2FE"/>'.format(nsdecls('w')))
                cell._tc.get_or_add_tcPr().append(shading)
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.bold = True
                        run.font.color.rgb = RGBColor(3, 105, 161) # #0369a1
                        run.font.size = Pt(10.5)

        # Style data cells
        for row in table.rows[1:]:
            for cell in row.cells:
                set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = Pt(10)

def convert_md_to_docx(md_path: Path, docx_path: Path) -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="md2docx_"))
    try:
        md_text = md_path.read_text(encoding="utf-8")
        processed_md = preprocess_markdown(md_text, temp_dir)

        # Markdown -> HTML
        html = markdown.markdown(
            processed_md,
            extensions=["tables", "fenced_code", "sane_lists", "nl2br"]
        )

        doc = Document()
        parser = HtmlToDocx()
        parser.add_html_to_document(html, doc)

        style_document(doc)

        docx_path.parent.mkdir(parents=True, exist_ok=True)
        doc.save(str(docx_path))
        print(f"[OK] DOCX generated: {docx_path.resolve()}")
        return docx_path
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    if len(sys.argv) < 2:
        print("Usage: md_to_docx.py <input.md> [-o output.docx]")
        sys.exit(1)

    input_md = Path(sys.argv[1]).resolve()
    if not input_md.exists():
        print(f"Error: {input_md} does not exist.")
        sys.exit(1)

    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        output_docx = Path(sys.argv[idx + 1]).resolve()
    else:
        output_docx = input_md.with_suffix(".docx")

    convert_md_to_docx(input_md, output_docx)

    # Sync to Google Drive (Strictly ONLY .docx and companion .pdf - NEVER .md or .html)
    book_folder_name = input_md.stem.replace('_Comprehensive_Summary', '').replace('_', ' ').strip().lower()
    if GDRIVE_BASE_DIR.exists():
        target_dir = GDRIVE_BASE_DIR / book_folder_name
        target_dir.mkdir(parents=True, exist_ok=True)
        gdrive_target = target_dir / output_docx.name
        shutil.copy2(output_docx, gdrive_target)
        print(f"[OK] Synced DOCX to Google Drive: {gdrive_target}")

        # Also sync companion PDF if present
        pdf_companion = input_md.parent / f"{input_md.stem.replace('_Comprehensive_Summary', '_Executive_Infographic')}.pdf"
        if not pdf_companion.exists():
            pdf_companion = input_md.parent / f"{input_md.stem.replace('_Comprehensive_Summary', '_Infographic')}.pdf"
        if pdf_companion.exists():
            shutil.copy2(pdf_companion, target_dir / pdf_companion.name)
            print(f"[OK] Synced Infographic PDF to Google Drive: {target_dir / pdf_companion.name}")
    elif GDRIVE_FALLBACK_DIR.exists():
        gdrive_target = GDRIVE_FALLBACK_DIR / output_docx.name
        shutil.copy2(output_docx, gdrive_target)
        print(f"[OK] Synced DOCX to Google Drive fallback: {gdrive_target}")
    else:
        print(f"[Notice] Google Drive folder not found, skipping cloud sync.")

if __name__ == "__main__":
    main()
