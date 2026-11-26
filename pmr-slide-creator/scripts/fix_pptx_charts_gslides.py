#!/usr/bin/env python3
"""
Google Slides & Cross-Viewer Chart XML Normalizer for PptxGenJS Decks.
Fixes PptxGenJS 4.x chart incompatibilities in Google Slides:
  1. Converts <c:cat><c:multiLvlStrRef> -> standard <c:cat><c:strRef> + <c:strCache>
     and sets <c:noMultiLvlLbl val="0"/> on <c:catAx> so Google Slides renders actual
     Y-axis category labels instead of falling back to 1, 2, 3...
  2. Converts integer 0..100 percentages with custom 0"%" format into standard decimal
     values (0.00..1.00) with formatCode="0%" across chart XML + embedded xlsx so '%'
     renders cleanly in Google Slides, PowerPoint, Keynote, and LibreOffice.
  3. Supports optional per-bar custom <c:dPt> colors on target chart indices.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

NS_C = "http://schemas.openxmlformats.org/drawingml/2006/chart"
NS_A = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS_R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_X = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"

ET.register_namespace("c", NS_C)
ET.register_namespace("a", NS_A)
ET.register_namespace("r", NS_R)


def _c(tag: str) -> str:
    return f"{{{NS_C}}}{tag}"


def _a(tag: str) -> str:
    return f"{{{NS_A}}}{tag}"


def _convert_multilvl_to_strref(chart_root: ET.Element) -> bool:
    changed = False
    for cat in chart_root.findall(f".//{_c('cat')}"):
        ml = cat.find(_c("multiLvlStrRef"))
        if ml is None:
            continue
        f_el = ml.find(_c("f"))
        ml_cache = ml.find(_c("multiLvlStrCache"))
        str_ref = ET.Element(_c("strRef"))
        if f_el is not None:
            new_f = ET.SubElement(str_ref, _c("f"))
            new_f.text = f_el.text
        str_cache = ET.SubElement(str_ref, _c("strCache"))
        pts: list[tuple[str, str]] = []
        if ml_cache is not None:
            lvl = ml_cache.find(_c("lvl"))
            pt_parent = lvl if lvl is not None else ml_cache
            for pt in pt_parent.findall(_c("pt")):
                v_el = pt.find(_c("v"))
                pts.append((pt.get("idx", str(len(pts))), v_el.text if v_el is not None else ""))
        pt_cnt = ET.SubElement(str_cache, _c("ptCount"))
        pt_cnt.set("val", str(len(pts)))
        for idx_str, val in pts:
            pt_el = ET.SubElement(str_cache, _c("pt"))
            pt_el.set("idx", idx_str)
            v_el = ET.SubElement(pt_el, _c("v"))
            v_el.text = val
        cat.remove(ml)
        cat.append(str_ref)
        changed = True

    for nm in chart_root.findall(f".//{_c('catAx')}/{_c('noMultiLvlLbl')}"):
        if nm.get("val") != "0":
            nm.set("val", "0")
            changed = True
    return changed


def _convert_pct_decimals(chart_root: ET.Element, xlsx_bytes: bytes | None) -> tuple[bool, bytes | None]:
    """Converts integer percent series (e.g. 97 with 0"%") into 0.97 + 0%."""
    has_pct_dlbl = False
    for nf in chart_root.findall(f".//{_c('dLbls')}/{_c('numFmt')}"):
        fc = nf.get("formatCode", "")
        if "%" in fc:
            has_pct_dlbl = True
            if fc != "0%":
                nf.set("formatCode", "0%")
            nf.set("sourceLinked", "0")

    if not has_pct_dlbl:
        return False, xlsx_bytes

    for val_ax in chart_root.findall(f".//{_c('valAx')}"):
        sc = val_ax.find(_c("scaling"))
        if sc is not None:
            mx = sc.find(_c("max"))
            if mx is not None:
                try:
                    mv = float(mx.get("val", "0"))
                    if mv > 2.0:
                        mx.set("val", f"{mv / 100.0:.2f}")
                except ValueError:
                    pass
        nf = val_ax.find(_c("numFmt"))
        if nf is not None:
            nf.set("formatCode", "0%")
            nf.set("sourceLinked", "0")

    for num_cache in chart_root.findall(f".//{_c('val')}/{_c('numRef')}/{_c('numCache')}"):
        fc_el = num_cache.find(_c("formatCode"))
        if fc_el is not None:
            fc_el.text = "0%"
        for pt in num_cache.findall(_c("pt")):
            v_el = pt.find(_c("v"))
            if v_el is not None and v_el.text:
                try:
                    fv = float(v_el.text)
                    if fv > 1.5:
                        v_el.text = f"{fv / 100.0:.4g}"
                except ValueError:
                    pass

    if xlsx_bytes:
        out_buf = io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(xlsx_bytes), "r") as xin, zipfile.ZipFile(
            out_buf, "w", zipfile.ZIP_DEFLATED
        ) as xout:
            for item in xin.infolist():
                data = xin.read(item.filename)
                if item.filename == "xl/worksheets/sheet1.xml":
                    ET.register_namespace("", NS_X)
                    xroot = ET.fromstring(data)
                    for cell in xroot.findall(f".//{{{NS_X}}}c"):
                        if cell.get("t") == "s":
                            continue
                        v_el = cell.find(f"{{{NS_X}}}v")
                        if v_el is not None and v_el.text:
                            try:
                                fv = float(v_el.text)
                                if fv > 1.5:
                                    v_el.text = f"{fv / 100.0:.4g}"
                            except ValueError:
                                pass
                    data = ET.tostring(xroot, encoding="utf-8", xml_declaration=True)
                xout.writestr(item, data)
        xlsx_bytes = out_buf.getvalue()
    return True, xlsx_bytes


def _apply_bar_colors(chart_root: ET.Element, hex_colors: list[str]) -> None:
    ser = chart_root.find(f".//{_c('barChart')}/{_c('ser')}")
    if ser is None or not hex_colors:
        return
    # Remove any old dPt
    for old in list(ser.findall(_c("dPt"))):
        ser.remove(old)
    # Insert dPt before c:cat
    cat_el = ser.find(_c("cat"))
    insert_idx = list(ser).index(cat_el) if cat_el is not None else len(ser)
    for idx_b, hx in enumerate(hex_colors):
        dpt = ET.Element(_c("dPt"))
        ix = ET.SubElement(dpt, _c("idx"))
        ix.set("val", str(idx_b))
        inv = ET.SubElement(dpt, _c("invertIfNegative"))
        inv.set("val", "0")
        sp = ET.SubElement(dpt, _c("spPr"))
        sf = ET.SubElement(sp, _a("solidFill"))
        clr = ET.SubElement(sf, _a("srgbClr"))
        clr.set("val", hx.lstrip("#").upper())
        ET.SubElement(sp, _a("effectLst"))
        ser.insert(insert_idx + idx_b, dpt)


def _extract_chart_title_and_cats(chart_root: ET.Element) -> tuple[str, list[str]]:
    title_parts = [t.text or "" for t in chart_root.findall(f".//{_c('title')}//{_a('t')}")]
    title = "".join(title_parts).strip()
    cats: list[str] = []
    for pt in chart_root.findall(f".//{_c('cat')}//{_c('pt')}"):
        v_el = pt.find(_c("v"))
        if v_el is not None and v_el.text:
            cats.append(v_el.text.strip())
    return title, cats


def _resolve_bar_colors_from_evidence(chart_root: ET.Element, evidence_data: dict | None) -> list[str]:
    if not evidence_data:
        return []
    c_title, c_cats = _extract_chart_title_and_cats(chart_root)
    for sl in evidence_data.get("slides", []):
        candidates = []
        if isinstance(sl.get("chart"), dict):
            candidates.append(sl["chart"])
        if isinstance(sl.get("charts"), list):
            candidates.extend([c for c in sl["charts"] if isinstance(c, dict)])
        for ch in candidates:
            bcols = ch.get("bar_colors")
            if not isinstance(bcols, list) or not bcols:
                continue
            spec_cats = [str(x).strip() for x in ch.get("categories", [])]
            spec_title = str(ch.get("title", "")).strip()
            if (spec_title and spec_title == c_title) or (spec_cats and spec_cats == c_cats):
                return [str(x) for x in bcols]
    return []


def normalize_pptx_charts(
    pptx_path: Path,
    bar_color_map: dict[str, list[str]] | None = None,
    evidence_data: dict | None = None,
) -> int:
    bar_color_map = bar_color_map or {}
    fixed_count = 0
    tmp_out = pptx_path.with_suffix(".tmp.pptx")
    with zipfile.ZipFile(pptx_path, "r") as zin:
        contents = {name: zin.read(name) for name in zin.namelist()}

    for name in sorted(list(contents.keys())):
        if not (name.startswith("ppt/charts/chart") and name.endswith(".xml")):
            continue
        chart_root = ET.fromstring(contents[name])
        c1 = _convert_multilvl_to_strref(chart_root)
        # Find linked xlsx via rels
        rels_name = f"ppt/charts/_rels/{Path(name).name}.rels"
        xlsx_name = None
        if rels_name in contents:
            rroot = ET.fromstring(contents[rels_name])
            for rel in rroot:
                tgt = rel.get("Target", "")
                if tgt.endswith(".xlsx"):
                    xlsx_name = "ppt/embeddings/" + Path(tgt).name
                    break
        xlsx_data = contents.get(xlsx_name) if xlsx_name else None
        c2, new_xlsx = _convert_pct_decimals(chart_root, xlsx_data)
        if c2 and xlsx_name and new_xlsx is not None:
            contents[xlsx_name] = new_xlsx

        chart_basename = Path(name).name
        target_colors = bar_color_map.get(chart_basename) or _resolve_bar_colors_from_evidence(chart_root, evidence_data)
        if target_colors:
            _apply_bar_colors(chart_root, target_colors)
            c1 = True

        if c1 or c2:
            contents[name] = ET.tostring(chart_root, encoding="utf-8", xml_declaration=True)
            fixed_count += 1

    with zipfile.ZipFile(tmp_out, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in contents.items():
            zout.writestr(name, data)
    shutil.move(str(tmp_out), str(pptx_path))
    return fixed_count


def check_pptx_charts(pptx_path: Path) -> list[str]:
    """Return list of Google-Slides chart compatibility issues found in ppt/charts/chart*.xml."""
    issues: list[str] = []
    with zipfile.ZipFile(pptx_path, "r") as zin:
        for name in sorted(zin.namelist()):
            if not (name.startswith("ppt/charts/chart") and name.endswith(".xml")):
                continue
            raw = zin.read(name).decode("utf-8", errors="ignore")
            if "multiLvlStrRef" in raw:
                issues.append(f"{name}: contains <c:multiLvlStrRef> (breaks Google Slides Y-axis labels)")
            if 'formatCode="0&quot;%&quot;"' in raw or 'formatCode=\'0"%"\'' in raw:
                issues.append(f"{name}: contains integer 0\"%\" formatCode (drops % on Google Slides)")
    return issues


def main():
    parser = argparse.ArgumentParser(description="Fix or verify PptxGenJS chart XML for Google Slides compatibility")
    parser.add_argument("--pptx", required=True)
    parser.add_argument("--out", default="", help="Optional output PPTX path (defaults to in-place update)")
    parser.add_argument("--evidence", default="", help="Optional evidence_bundle.json to auto-resolve chart bar_colors")
    parser.add_argument("--bar-colors-json", default="", help="Optional JSON mapping chart1.xml/chart2.xml -> [hex...]")
    parser.add_argument("--check", action="store_true", help="Verify chart XML without modifying file (exit 1 on issues)")
    args = parser.parse_args()

    in_path = Path(args.pptx)
    if args.check:
        issues = check_pptx_charts(in_path)
        if issues:
            print(f"FAILED: {len(issues)} Google Slides chart compatibility issue(s):")
            for iss in issues:
                print(f"  - {iss}")
            sys.exit(1)
        print(f"PASS 100%: All chart XMLs in {in_path.name} are Google-Slides compatible (<c:strRef> + 0%).")
        return

    out_path = Path(args.out) if args.out else in_path
    if out_path != in_path:
        shutil.copy2(str(in_path), str(out_path))
    cmap = json.loads(args.bar_colors_json) if args.bar_colors_json else {}
    ev_data = json.loads(Path(args.evidence).read_text(encoding="utf-8")) if args.evidence and Path(args.evidence).exists() else None
    n = normalize_pptx_charts(out_path, bar_color_map=cmap, evidence_data=ev_data)
    print(f"SUCCESS: Normalized {n} chart(s) to standard <c:strRef> + 0% format -> {out_path}")


if __name__ == "__main__":
    main()
