#!/usr/bin/env python3
"""Convert a Markdown medical chart summary into a styled A4 Word (.docx) report with visual QA."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Cm, Pt, RGBColor

NAVY = RGBColor(0x0F, 0x17, 0x2A)
TEAL = RGBColor(0x0D, 0x94, 0x88)
SLATE = RGBColor(0x33, 0x41, 0x55)
MUTED = RGBColor(0x64, 0x74, 0x8B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
FONT_NAME = "TH Sarabun New"


def set_run_font(run, size_pt: float, bold: bool = False, italic: bool = False, color: RGBColor = SLATE) -> None:
    run.font.name = FONT_NAME
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.insert(0, rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), FONT_NAME)


def add_formatted_runs(
    p,
    text: str,
    base_size: float = 15.0,
    base_color: RGBColor = SLATE,
    base_bold: bool = False,
    base_italic: bool = False,
) -> None:
    """Parse **bold**, *italic*, and `code/provenance` spans cleanly (handles nested spans)."""
    pattern = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            r = p.add_run(text[pos:m.start()])
            set_run_font(r, base_size, bold=base_bold, italic=base_italic, color=base_color)
        token = m.group(0)
        if token.startswith("**") and token.endswith("**"):
            inner = token[2:-2]
            c = NAVY if base_color == SLATE else base_color
            if "`" in inner or "*" in inner:
                add_formatted_runs(p, inner, base_size=base_size, base_color=c, base_bold=True, base_italic=base_italic)
            else:
                r = p.add_run(inner)
                set_run_font(r, base_size, bold=True, italic=base_italic, color=c)
        elif token.startswith("*") and token.endswith("*"):
            inner = token[1:-1]
            if "`" in inner or "**" in inner:
                add_formatted_runs(p, inner, base_size=base_size, base_color=base_color, base_bold=base_bold, base_italic=True)
            else:
                r = p.add_run(inner)
                set_run_font(r, base_size, bold=base_bold, italic=True, color=base_color)
        elif token.startswith("`") and token.endswith("`"):
            inner = token[1:-1]
            r = p.add_run(inner)
            is_tag = inner.startswith("[") or "IMG_" in inner or "_p" in inner
            set_run_font(r, base_size - 0.8 if is_tag else base_size, bold=base_bold, italic=base_italic, color=TEAL if is_tag else NAVY)
        pos = m.end()
    if pos < len(text):
        r = p.add_run(text[pos:])
        set_run_font(r, base_size, bold=base_bold, italic=base_italic, color=base_color)


def set_cell_shading(cell, fill_hex: str) -> None:
    cell._tc.get_or_add_tcPr().append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>'))


def set_cell_margins(cell, top: int = 85, bottom: int = 85, left: int = 110, right: int = 110) -> None:
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tcMar.append(node)
    tcPr.append(tcMar)


def set_table_borders(table, border_color: str = "CBD5E1") -> None:
    table._tbl.tblPr.append(
        parse_xml(
            f'<w:tblBorders {nsdecls("w")}>'
            f'<w:top w:val="single" w:sz="6" w:space="0" w:color="{border_color}"/>'
            f'<w:bottom w:val="single" w:sz="8" w:space="0" w:color="0F172A"/>'
            f'<w:insideH w:val="single" w:sz="4" w:space="0" w:color="{border_color}"/>'
            f'<w:left w:val="none"/><w:right w:val="none"/><w:insideV w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            f"</w:tblBorders>"
        )
    )


def set_row_cant_split(row) -> None:
    row._tr.get_or_add_trPr().append(OxmlElement("w:cantSplit"))


def set_row_header(row) -> None:
    row._tr.get_or_add_trPr().append(OxmlElement("w:tblHeader"))


def add_callout_box(doc: Document, title: str, items: list[str], fill_hex: str, border_hex: str) -> None:
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    cell = tbl.cell(0, 0)
    cell.width = Cm(17.4)
    set_cell_shading(cell, fill_hex)
    set_cell_margins(cell, top=130, bottom=130, left=190, right=170)
    cell._tc.get_or_add_tcPr().append(
        parse_xml(
            f'<w:tcBorders {nsdecls("w")}>'
            f'<w:left w:val="single" w:sz="24" w:space="0" w:color="{border_hex}"/>'
            f'<w:top w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            f'<w:right w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            f'<w:bottom w:val="single" w:sz="4" w:space="0" w:color="E2E8F0"/>'
            f"</w:tcBorders>"
        )
    )
    set_row_cant_split(tbl.rows[0])

    p0 = cell.paragraphs[0]
    p0.paragraph_format.space_after = Pt(4)
    set_run_font(p0.add_run(title), 16.0, bold=True, color=NAVY)

    for idx, item in enumerate(items):
        p = cell.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(2.5 if idx < len(items) - 1 else 0)
        p.paragraph_format.line_spacing = 1.13
        add_formatted_runs(p, item, base_size=14.5, base_color=SLATE)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)


def add_section_heading(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(9)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p._p.get_or_add_pPr().append(
        parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom w:val="single" w:sz="10" w:space="3" w:color="0D9488"/></w:pBdr>')
    )
    set_run_font(p.add_run(text), 17.5, bold=True, color=NAVY)


def add_sub_heading(doc: Document, text: str) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    set_run_font(p.add_run(text), 15.5, bold=True, color=TEAL)


def add_styled_table(doc: Document, headers: list[str], rows: list[list[str]]) -> None:
    n_cols = len(headers)
    if n_cols == 5:
        widths = [0.8, 3.8, 2.4, 7.6, 2.8]
    elif n_cols == 8:
        widths = [2.4, 2.4, 1.8, 1.5, 1.5, 1.8, 3.8, 2.2]
    else:
        widths = [round(17.4 / n_cols, 2)] * n_cols

    tbl = doc.add_table(rows=len(rows) + 1, cols=n_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    set_table_borders(tbl)

    hdr_row = tbl.rows[0]
    set_row_header(hdr_row)
    set_row_cant_split(hdr_row)
    for j, h in enumerate(headers):
        cell = hdr_row.cells[j]
        cell.width = Cm(widths[j])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, "0F172A")
        set_cell_margins(cell, top=95, bottom=95, left=95, right=95)
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(0)
        set_run_font(p.add_run(h), 14.0, bold=True, color=WHITE)

    for i, row_data in enumerate(rows):
        row = tbl.rows[i + 1]
        set_row_cant_split(row)
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        for j, val in enumerate(row_data):
            cell = row.cells[j]
            cell.width = Cm(widths[j])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            set_cell_shading(cell, bg)
            set_cell_margins(cell, top=70, bottom=70, left=90, right=90)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            add_formatted_runs(p, val, base_size=13.5, base_color=SLATE)

    sp = doc.add_paragraph()
    sp.paragraph_format.space_after = Pt(4)


def add_page_number_footer(section, footer_label: str) -> None:
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    set_run_font(p.add_run(f"{footer_label}   |   หน้า "), 12.0, color=MUTED)
    for fld_name, sep in (("PAGE", " / "), ("NUMPAGES", "")):
        fld = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="{fld_name}"/>')
        r_tmp = OxmlElement("w:r")
        rPr = OxmlElement("w:rPr")
        rFonts = OxmlElement("w:rFonts")
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), FONT_NAME)
        sz = OxmlElement("w:sz")
        sz.set(qn("w:val"), "24")
        col = OxmlElement("w:color")
        col.set(qn("w:val"), "64748B")
        rPr.extend([rFonts, sz, col])
        t = OxmlElement("w:t")
        t.text = "1"
        r_tmp.extend([rPr, t])
        fld.append(r_tmp)
        p._p.append(fld)
        if sep:
            set_run_font(p.add_run(sep), 12.0, color=MUTED)


def parse_md_table(lines: list[str]) -> tuple[list[str], list[list[str]]]:
    clean = [ln.strip() for ln in lines if ln.strip().startswith("|")]
    headers = [c.strip() for c in clean[0].strip("|").split("|")]
    rows = []
    for ln in clean[2:]:
        cells = [c.strip() for c in ln.strip("|").split("|")]
        while len(cells) < len(headers):
            cells.append("")
        rows.append(cells[: len(headers)])
    return headers, rows


def build_docx(md_path: Path, out_path: Path, title: str, subtitle: str, footer_label: str) -> None:
    lines = md_path.read_text(encoding="utf-8").splitlines()
    doc = Document()
    section = doc.sections[0]
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)
    section.top_margin = Cm(1.5)
    section.bottom_margin = Cm(1.5)
    section.left_margin = Cm(1.8)
    section.right_margin = Cm(1.8)
    doc.styles["Normal"].font.name = FONT_NAME
    doc.styles["Normal"].font.size = Pt(15)
    add_page_number_footer(section, footer_label)

    # Banner
    banner = doc.add_table(rows=1, cols=1)
    banner.alignment = WD_TABLE_ALIGNMENT.CENTER
    banner.autofit = False
    bcell = banner.cell(0, 0)
    bcell.width = Cm(17.4)
    set_cell_shading(bcell, "0F172A")
    set_cell_margins(bcell, top=155, bottom=155, left=220, right=220)
    bp1 = bcell.paragraphs[0]
    bp1.paragraph_format.space_after = Pt(2)
    set_run_font(bp1.add_run(title), 20.5, bold=True, color=WHITE)
    bp2 = bcell.add_paragraph()
    bp2.paragraph_format.space_after = Pt(0)
    set_run_font(bp2.add_run(subtitle), 13.5, color=RGBColor(0x99, 0xF6, 0xE4))
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Skip top title/metadata block before first H2
    idx = 0
    while idx < len(lines) and not lines[idx].startswith("## "):
        idx += 1

    while idx < len(lines):
        ln = lines[idx]
        stripped = ln.strip()
        if not stripped or stripped == "---":
            idx += 1
            continue

        if stripped.startswith("## ") and ("One-Liner" in stripped or "ภาพรวม" in stripped):
            heading = stripped[3:]
            idx += 1
            body = []
            while idx < len(lines) and not lines[idx].startswith("## ") and lines[idx].strip() != "---":
                if lines[idx].strip():
                    body.append(lines[idx].strip())
                idx += 1
            add_callout_box(doc, heading, body, fill_hex="F0FDFA", border_hex="0D9488")
            continue

        if stripped.startswith("## ") and ("Chart Audit" in stripped or "ความสอดคล้อง" in stripped):
            heading = stripped[3:]
            idx += 1
            items = []
            while idx < len(lines) and not lines[idx].startswith("## "):
                s = lines[idx].strip()
                if s and s != "---":
                    items.append("    • " + s[2:] if s.startswith("- ") else s)
                idx += 1
            add_callout_box(doc, heading, items, fill_hex="FFFBEB", border_hex="D97706")
            continue

        if stripped.startswith("## "):
            add_section_heading(doc, stripped[3:])
            idx += 1
            continue

        if stripped.startswith("### "):
            add_sub_heading(doc, stripped[4:])
            idx += 1
            continue

        if stripped.startswith("|"):
            tbl_lines = []
            while idx < len(lines) and lines[idx].strip().startswith("|"):
                tbl_lines.append(lines[idx])
                idx += 1
            headers, rows = parse_md_table(tbl_lines)
            add_styled_table(doc, headers, rows)
            continue

        if stripped.startswith("- ") or stripped.startswith("  - "):
            indent_level = len(ln) - len(ln.lstrip(" "))
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5 if indent_level == 0 else 1.1)
            p.paragraph_format.first_line_indent = Cm(-0.35)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2.5)
            p.paragraph_format.line_spacing = 1.12
            set_run_font(p.add_run("•  " if indent_level == 0 else "◦  "), 15.0, bold=True, color=TEAL)
            add_formatted_runs(p, stripped[2:].strip(), base_size=15.0, base_color=SLATE)
            idx += 1
            continue

        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.12
        add_formatted_runs(p, stripped, base_size=15.0, base_color=SLATE)
        idx += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out_path))

    # Programmatic leak check
    chk = Document(str(out_path))
    texts = [p.text for p in chk.paragraphs] + [c.text for t in chk.tables for r in t.rows for c in r.cells]
    joined = "\n".join(texts)
    if "**" in joined or "`" in joined:
        raise RuntimeError("Found unparsed markdown tokens (** or `) in generated .docx!")
    print(f"Saved & verified clean .docx: {out_path} ({out_path.stat().st_size} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert Markdown chart summary to styled A4 .docx.")
    parser.add_argument("input_md", type=Path)
    parser.add_argument("output_docx", type=Path)
    parser.add_argument("--title", default="รายงานสรุปเวชระเบียนผู้ป่วย (Medical Record Summary & Chart Audit)")
    parser.add_argument("--subtitle", default="Fact-First Mode  |  Source Provenance Verified")
    parser.add_argument("--footer", default="Medical Record Summary")
    parser.add_argument("--preview-dir", type=Path, default=None, help="Optional dir for qlmanage PNG preview.")
    args = parser.parse_args()

    build_docx(args.input_md, args.output_docx, args.title, args.subtitle, args.footer)
    if args.preview_dir:
        args.preview_dir.mkdir(parents=True, exist_ok=True)
        subprocess.run(["qlmanage", "-t", "-s", "1600", "-o", str(args.preview_dir), str(args.output_docx)], check=True)


if __name__ == "__main__":
    main()
