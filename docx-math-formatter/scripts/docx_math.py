#!/usr/bin/env python3
"""
Convert LaTeX math equations in DOCX documents into native Microsoft Word Equations (OMML).
Supports SharePoint / Word Online compatible inline equations and standalone equation blocks.
"""

import sys
import os
import argparse
import re
from pathlib import Path
import docx
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import latex2mathml.converter
from lxml import etree

SKILL_DIR = Path(__file__).resolve().parent.parent
XSLT_PATH = SKILL_DIR / "assets" / "MML2OMML.XSL"

if not XSLT_PATH.exists():
    raise FileNotFoundError(f"Stylesheet not found at {XSLT_PATH}")

xslt_doc = etree.parse(str(XSLT_PATH))
transform = etree.XSLT(xslt_doc)

def latex_to_omml(latex_code: str):
    """Convert LaTeX string to Word OMML XML element."""
    mml = latex2mathml.converter.convert(latex_code)
    mml_doc = etree.fromstring(mml)
    omml_doc = transform(mml_doc)
    xml_str = etree.tostring(omml_doc).decode('utf-8')
    return parse_xml(xml_str)

def add_omml_run(paragraph, latex_code: str):
    """Append native OMML equation to a paragraph."""
    elem = latex_to_omml(latex_code)
    paragraph._p.append(elem)

def add_thai_run(paragraph, text: str, bold=False, italic=False, font_name="TH Sarabun New", font_size=16):
    """Add a text run with proper Thai font tags."""
    r = paragraph.add_run(text)
    r.bold = bold
    r.italic = italic
    r.font.name = font_name
    r.font.size = Pt(font_size)
    rPr = r._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)
    return r

def main():
    parser = argparse.ArgumentParser(description="Convert LaTeX equations in Word documents to native Word Equation (OMML)")
    parser.add_argument("--test", action="store_true", help="Run self-test conversion")
    args = parser.parse_args()

    if args.test:
        test_latex = r"n = \frac{(Z_{\alpha} + Z_{\beta})^2}{(p_1 - p_2)^2}"
        omml = latex_to_omml(test_latex)
        print("Test conversion successful! Root tag:", omml.tag)

if __name__ == "__main__":
    main()
