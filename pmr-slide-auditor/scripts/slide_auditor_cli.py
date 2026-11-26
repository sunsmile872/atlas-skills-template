#!/usr/bin/env python3
"""
CLI Helper for pmr-slide-auditor skill (Phase 5):
1. check-banned: Profile-scoped banned phrases & ambiguous shorthand scanner.
2. search-textbooks / find-figures / extract-figure / auto-find-figures: PDF discovery & 4x crop tools.
3. verify-pptx-bounds: Single-slide or whole-deck bounds + wrapped text height estimator.
4. verify-jc-deck / audit-deck: Full automated gates + LibreOffice Contact Sheet renderer.
5. sync-rule: Two-way continuous rule sync to global USER_INSTRUCTIONS_TEMPLATE.md.
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

from pptx import Presentation

SCRIPTS_DIR = Path(__file__).resolve().parent
CREATOR_TEMPLATES_DIR = Path.home() / ".gemini/config/skills/pmr-slide-creator/templates"
CREATOR_SCRIPTS_DIR = Path.home() / ".gemini/config/skills/pmr-slide-creator/scripts"

UNIVERSAL_BANNED = [
    (r"\blandmark\b", "Banned word 'Landmark' (use neutral study citation)"),
    (r"\bworkhorse\b", "Banned slang 'Workhorse'"),
    (r"\baxiom\b", "Banned word 'Axiom'"),
    (r"\bcrucial\b|\bparamount\b|\bdelve\b|\btestament\b|\bgame[- ]changer\b", "Banned AI hype lexicon"),
    (r"\blandscape\b|\bnotably\b|\bin conclusion\b", "Banned AI boilerplate"),
    (r"—", "Banned em-dash (use colon, comma, parentheses, or hyphen)"),
    (r"ทั้ง\s*\d+\s*แขน|แขน\s*Sham|แขนทดลอง", "Banned Thai AI calque 'แขน' (use 'กลุ่ม')"),
    (r"เชิงวัตถุวิสัย|เชิงอัตวิสัย", "Banned Thai AI calque (use 'เชิงปริมาณ / objective' or 'subjective')"),
    (r"ผู้ประเมินปกปิด|ปกปิดสองทาง|ธรณีความเจ็บปวด", "Banned Thai AI calque (use 'blinded assessor / double-blind / PPT')"),
    (r"อนุรักษนิยม", "Banned Thai AI calque 'อนุรักษนิยม' (use 'conservative')"),
]

PMR_BANNED = [
    (r"กฎเหล็ก", "Banned dramatic phrase 'กฎเหล็ก'"),
    (r"ท่องให้ขึ้นใจ", "Banned condescending phrase 'ท่องให้ขึ้นใจ'"),
    (r"ระบาดวิทยา", "Banned Thai translation for Epidemiology (use 'Epidemiology')"),
    (r"สาเหตุการเกิดโรค", "Banned Thai translation for Etiology (use 'Etiology')"),
    (r"ความพิการ", "Banned term 'ความพิการ' for joint deformity (use 'Deformity' or 'ข้อผิดรูป')"),
    (r"ทแยงไขว้", "Banned translation for figure-of-eight (use 'figure of eight')"),
    (r"การลดบวมเชิงรุก", "Banned unnatural translation (use 'การลดบวมอย่าง aggressive')"),
    (r"จะสั่งจ่าย.*เสมอ", "Banned rigid/absolute phrasing (use flexible clinical phrasing)"),
    (r"หลักการชีวกลศาสตร์พื้นฐาน", "Banned phrase 'หลักการชีวกลศาสตร์พื้นฐาน'"),
    (r"ลูกสะบ้า", "Banned Thai anatomical term 'ลูกสะบ้า' (use 'Patella')"),
    (r"บนเสื่อกายภาพ", "Banned awkward phrase 'บนเสื่อกายภาพ' (use clean exercise names)"),
    (r"เพื่อรักษาแนวเชิงกราน", "Banned awkward phrase (use 'เพื่อเพิ่ม Pelvic stability และป้องกันไม่ให้เดินหลังแอ่นชดเชย')"),
    (r"ชีวกลศาสตร์", "Banned Thai translation (use 'Biomechanics')"),
    (r"คว่ำ-หงาย|คว่ำหงาย", "Banned Thai translation (use 'Pronation และ Supination')"),
    (r"คานงัด|ก้านคาน|แขนงคาน", "Banned translation (use 'Lever arm')"),
    (r"ข้อต่อชีวภาพ|ข้อเข่าชีวภาพ", "Banned phrase (use 'ข้อต่อ' or 'ข้อเข่า')"),
    (r"กระดูกหน้าแข้ง", "Banned Thai anatomical term (use 'Tibia')"),
    (r"กระดูกสะบัก", "Banned Thai anatomical term (use 'Scapula')"),
]

AMPUTATION_BANNED = [
    (r"สูญเสียรยางค์|การตัดรยางค์", "Banned Thai translation for Amputation (use 'Amputation')"),
    (r"ผู้พิการแขนขาขาด|คนไข้ตัดขา", "Banned phrase for Amputee (use 'Amputee')"),
    (r"ตอขา|\bstumps?\b", "Banned Thai/slang word for residual limb (use 'residual limb')"),
    (r"เบ้าเทียม", "Banned awkward term (use 'เบ้าขาเทียม' or 'Prosthetic socket')"),
    (r"ข้างที่ตัด", "Banned phrase (use 'ฝั่ง Prosthetic side')"),
    (r"\bPLP\b", "Banned abbreviation (use full 'Phantom Limb Pain')"),
    (r"\bRLP\b", "Banned abbreviation (use full 'Residual Limb Pain')"),
]

AMBIGUOUS_ABBREVS = [
    (r"\bNS\b", "Ambiguous abbreviation 'NS' (clashes with Normal Saline; use 'not significant' or '(not sig.)')"),
    (r"\blit\b", "Informal abbreviation 'lit' (use 'range' or 'published cohorts')"),
    (r"\bSQ\b", "Use 'Subcutaneous' / 'Subcut.' instead of 'SQ'"),
    (r"\bmeta\b(?!-analys|-analytic)", "Standalone 'meta' (use 'meta-analysis')"),
    (r"\bq\d+h\b", "Use 'every N h' / 'every N hours' instead of 'q2h'"),
]


def _get_banned_patterns(profile: str):
    pats = list(UNIVERSAL_BANNED)
    if profile in ("pmr_board", "amputation"):
        pats.extend(PMR_BANNED)
    if profile == "amputation":
        pats.extend(AMPUTATION_BANNED)
    return pats


def find_ref_dir(project_dir):
    for name in ("textbook reference", "Textbook Reference", "textbook_reference", "source"):
        p = os.path.join(project_dir, name)
        if os.path.isdir(p):
            return p
    return os.path.join(project_dir, "textbook reference")


def get_primary_pdfs(project_dir, exclude_regex=r"(senior|legacy)"):
    ref_dir = find_ref_dir(project_dir)
    pdfs = sorted(glob.glob(os.path.join(ref_dir, "*.pdf")) + glob.glob(os.path.join(ref_dir, "*.PDF")))
    seen = set()
    primary = []
    ex_re = re.compile(exclude_regex, flags=re.IGNORECASE) if exclude_regex else None
    for p in pdfs:
        if p in seen:
            continue
        seen.add(p)
        bname = os.path.basename(p)
        if ex_re and ex_re.search(bname):
            continue
        primary.append(p)
    return primary


def _iter_json_strings(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, list):
        for item in obj:
            yield from _iter_json_strings(item)
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _iter_json_strings(v)


def _clean_js_line_for_lint(line: str) -> str:
    # Strip JS // comments and JS identifier/property references (data.meta, const meta, meta.presenter, meta:)
    cleaned = re.sub(r'(?:^|\s)//.*$', '', line)
    cleaned = re.sub(r'\.[mM]eta\b|\b(?:const|let|var)\s+meta\b|\bmeta\s*[:.]', ' ', cleaned)
    return cleaned


def cmd_check_banned(args):
    project_dir = os.path.abspath(args.project_dir)
    profile = getattr(args, "profile", "pmr_board")
    patterns = _get_banned_patterns(profile) + AMBIGUOUS_ABBREVS
    abbrev_pats = {p[0] for p in AMBIGUOUS_ABBREVS}

    targets = sorted(
        glob.glob(os.path.join(project_dir, "build*.py"))
        + glob.glob(os.path.join(project_dir, "build*.js"))
        + glob.glob(os.path.join(project_dir, "notes_data_modules", "*.py"))
    )
    for md_name in ("PRESENTER_NOTES_MASTER.md",):
        pm_md = os.path.join(project_dir, md_name)
        if os.path.exists(pm_md):
            targets.append(pm_md)

    violations = []
    for fpath in targets:
        is_js = fpath.endswith(".js")
        in_block_comment = False
        with open(fpath, "r", encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                scan_line = line
                if is_js:
                    if in_block_comment:
                        if "*/" in scan_line:
                            scan_line = scan_line.split("*/", 1)[1]
                            in_block_comment = False
                        else:
                            continue
                    if "/*" in scan_line:
                        if "*/" in scan_line:
                            scan_line = re.sub(r"/\*.*?\*/", " ", scan_line)
                        else:
                            scan_line = scan_line.split("/*", 1)[0]
                            in_block_comment = True
                    scan_line = _clean_js_line_for_lint(scan_line)
                for pat, reason in patterns:
                    flags = 0 if pat in abbrev_pats else re.IGNORECASE
                    if re.search(pat, scan_line, flags=flags):
                        violations.append((os.path.basename(fpath), lineno, reason, line.strip()[:120]))

    ev_path = os.path.join(project_dir, "evidence_bundle.json")
    if os.path.exists(ev_path):
        import json as _json
        with open(ev_path, "r", encoding="utf-8") as ef:
            ev_data = _json.load(ef)
        for s_idx, slide_obj in enumerate(ev_data.get("slides", []), 1):
            s_num = slide_obj.get("slide_id", s_idx)
            for s_str in _iter_json_strings(slide_obj):
                for pat, reason in patterns:
                    flags = 0 if pat in abbrev_pats else re.IGNORECASE
                    if re.search(pat, s_str, flags=flags):
                        violations.append(("evidence_bundle.json", f"slide {s_num}", reason, s_str.strip()[:120]))

    total_checked = len(targets) + (1 if os.path.exists(ev_path) else 0)
    if not violations:
        print(f"PASS 100%: Zero banned terms or ambiguous abbreviations found across {total_checked} target files (profile={profile})!")
    else:
        print(f"WARNING: Found {len(violations)} potential banned-term/abbreviation occurrences (profile={profile}):")
        for fname, lineno, reason, snippet in violations:
            print(f"  - {fname}:{lineno} [{reason}] -> {snippet}")
        if getattr(args, "strict", False):
            sys.exit(1)


def _parse_page_range(spec: str) -> tuple[int, int] | None:
    if not spec:
        return None
    m = re.match(r"^\s*(\d+)(?:\s*-\s*(\d+))?\s*$", spec)
    if not m:
        raise ValueError(f"Invalid --pdf-pages range '{spec}' (expected e.g. '210-220' or '213')")
    lo = int(m.group(1))
    hi = int(m.group(2)) if m.group(2) else lo
    return (max(1, lo), max(lo, hi))


def cmd_search_textbooks(args):
    if fitz is None:
        print("ERROR: PyMuPDF (fitz) is required.", file=sys.stderr)
        sys.exit(1)

    pdfs = get_primary_pdfs(os.path.abspath(args.project_dir), exclude_regex=getattr(args, "exclude_regex", r"(senior|legacy)"))
    book_filter = getattr(args, "book_filter", "")
    if book_filter:
        bf_re = re.compile(book_filter, flags=re.IGNORECASE)
        pdfs = [p for p in pdfs if bf_re.search(os.path.basename(p))]
    page_range = _parse_page_range(getattr(args, "pdf_pages", ""))
    keywords = [k.strip().lower() for k in re.split(r"[,;]+|\s+", args.query) if len(k.strip()) >= 2]

    for pdf_path in pdfs:
        bname = os.path.basename(pdf_path)
        doc = fitz.open(pdf_path)
        hits_count = 0
        start_p = (page_range[0] - 1) if page_range else 0
        end_p = min(len(doc), page_range[1]) if page_range else len(doc)
        print(f"\n=== {bname} (Total PDF pages: {len(doc)}, scanning {start_p + 1}-{end_p}) ===", flush=True)
        for pno in range(start_p, end_p):
            txt = doc[pno].get_text("text")
            t_low = txt.lower()
            if all(k in t_low for k in keywords):
                hits_count += 1
                print(f"  [PDF p. {pno + 1}]", flush=True)
                for line in txt.splitlines():
                    if any(k in line.lower() for k in keywords):
                        print(f"    > {line.strip()[:140]}", flush=True)
                if hits_count >= args.limit:
                    break
        doc.close()


def cmd_find_figures(args):
    if fitz is None:
        print("ERROR: PyMuPDF (fitz) is required.", file=sys.stderr)
        sys.exit(1)

    pdfs = get_primary_pdfs(os.path.abspath(args.project_dir), exclude_regex=getattr(args, "exclude_regex", r"(senior|legacy)"))
    keywords = [k.strip().lower() for k in re.split(r"[,;]+|\s+", args.query) if len(k.strip()) >= 2]
    fig_re = re.compile(r"(fig(?:ure|\.)\s*\d+|table\s*\d+)", re.IGNORECASE)

    for pdf_path in pdfs:
        bname = os.path.basename(pdf_path)
        doc = fitz.open(pdf_path)
        print(f"\n=== Figure/Table Candidates in {bname} ===")
        found = 0
        for pno in range(len(doc)):
            page = doc[pno]
            txt = page.get_text("text")
            t_low = txt.lower()
            if any(k in t_low for k in keywords) and fig_re.search(txt):
                imgs = page.get_images(full=True)
                matched_lines = [ln.strip() for ln in txt.splitlines() if fig_re.search(ln) or any(k in ln.lower() for k in keywords)]
                print(f"  [PDF p. {pno + 1} | Embedded images: {len(imgs)}]")
                for ml in matched_lines[:6]:
                    print(f"    * {ml[:140]}")
                found += 1
                if found >= args.limit:
                    break
        doc.close()


def cmd_extract_figure(args):
    if fitz is None:
        print("ERROR: PyMuPDF (fitz) is required.", file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(args.pdf)
    page = doc[args.pdf_page - 1]
    mat = fitz.Matrix(args.zoom, args.zoom)
    if args.bbox:
        x0, y0, x1, y1 = [float(v) for v in args.bbox.split(",")]
        rect = fitz.Rect(x0, y0, x1, y1)
        pix = page.get_pixmap(matrix=mat, clip=rect, alpha=False)
    else:
        pix = page.get_pixmap(matrix=mat, alpha=False)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    pix.save(args.out)
    print(f"SUCCESS: Saved {pix.width}x{pix.height} px image to {args.out} (from PDF page {args.pdf_page})")
    doc.close()


def _estimate_wrapped_height_in(text: str, box_w_in: float, pt_size: float, line_mult: float = 1.22) -> float:
    """Conservatively estimate rendered height of wrapped text inside a PPTX textbox."""
    if not text or box_w_in <= 0.15:
        return 0.0
    avg_char_in = (pt_size / 72.0) * 0.50
    chars_per_line = max(8, int((box_w_in - 0.12) / avg_char_in))
    lines = 0
    for para in text.splitlines():
        p = para.strip()
        lines += max(1, (len(p) + chars_per_line - 1) // chars_per_line) if p else 1
    return lines * (pt_size / 72.0) * line_mult


def _check_pptx_bounds_internal(pptx_path: str, slide_num: int | None = None) -> tuple[list[str], list[str]]:
    prs = Presentation(pptx_path)
    indices = [slide_num] if slide_num else list(range(1, len(prs.slides) + 1))
    errors: list[str] = []
    warnings: list[str] = []
    for s_idx in indices:
        slide = prs.slides[s_idx - 1]
        for sh_idx, sh in enumerate(slide.shapes, 1):
            left = sh.left / 914400
            top = sh.top / 914400
            width = sh.width / 914400
            height = sh.height / 914400
            right = left + width
            bottom = top + height
            if left < -0.02 or top < -0.02 or right > 13.36 or bottom > 7.52:
                errors.append(
                    f"Slide {s_idx:02d} Shape {sh_idx:02d}: Out-of-bounds ({left:.2f},{top:.2f} -> {right:.2f},{bottom:.2f})"
                )
            if top < 6.98 and bottom > 6.965 and not (top <= 0.02 and height >= 7.45):
                warnings.append(
                    f"Slide {s_idx:02d} Shape {sh_idx:02d}: Card/text encroaches footer zone (bottom={bottom:.3f}\" > 6.965\")"
                )
            if sh.has_text_frame:
                txt = sh.text_frame.text.strip()
                if txt and height > 0.20:
                    p0 = sh.text_frame.paragraphs[0]
                    fs = (
                        p0.font.size.pt
                        if p0.font.size
                        else (p0.runs[0].font.size.pt if p0.runs and p0.runs[0].font.size else 13.5)
                    )
                    est_h = _estimate_wrapped_height_in(txt, width, fs)
                    if est_h > height + 0.25 and top >= 0.80:
                        warnings.append(
                            f"Slide {s_idx:02d} Shape {sh_idx:02d}: Estimated wrapped height {est_h:.2f}\" > box {height:.2f}\" ('{txt[:35]}...')"
                        )
    return errors, warnings


def cmd_verify_pptx_bounds(args):
    prs = Presentation(args.pptx)
    target_slide = None if args.all or not args.slide else args.slide
    if target_slide is not None:
        slide = prs.slides[target_slide - 1]
        print(f"=== PPTX Bounding Box Audit — Slide {target_slide} ===")
        for idx, sh in enumerate(slide.shapes, 1):
            left = sh.left / 914400
            top = sh.top / 914400
            width = sh.width / 914400
            height = sh.height / 914400
            right = left + width
            bottom = top + height
            txt_preview = sh.text_frame.text.replace("\n", " | ")[:70] if sh.has_text_frame else ""
            status = "OVERFLOW_WARNING (bottom > 6.90\")" if (top < 6.95 and bottom > 6.905) else "OK"
            print(
                f"  Shape {idx:02d} ({sh.shape_type}): "
                f"left={left:.3f}\", top={top:.3f}\", w={width:.3f}\", h={height:.3f}\", "
                f"right={right:.3f}\", bottom={bottom:.3f}\" [{status}] {txt_preview}"
            )
    errs, warns = _check_pptx_bounds_internal(args.pptx, target_slide)
    if target_slide is None:
        print(f"=== Whole-Deck PPTX Bounds & Wrap Audit ({len(prs.slides)} slides) ===")
        for w in warns:
            print(f"  ! {w}")
        if errs:
            for e in errs:
                print(f"  - {e}")
            sys.exit(1)
        print(f"PASS 100%: {len(prs.slides)}/{len(prs.slides)} slides within canvas bounds ({len(warns)} wrap notice(s)).")
    elif errs:
        for e in errs:
            print(f"ERROR: {e}")
        sys.exit(1)


def _check_single_image_compliance(
    source_label: str,
    slide_label: str,
    img_name: str,
    fig_source: str,
    asset_dir: str,
    Image,
    np,
    require_source: bool = True,
) -> list[tuple[str, str, str]]:
    violations = []
    img_path = os.path.join(asset_dir, img_name)
    if not os.path.exists(img_path):
        return [(source_label, slide_label, f"Missing asset file: {img_name}")]

    is_ai_generated = any(k in img_name.lower() for k in ["vector", "infographic", "ai_gen"]) or "ai-generated" in fig_source.lower()
    if is_ai_generated:
        if "AI-Generated" not in fig_source:
            violations.append((
                source_label,
                f"{slide_label} ({img_name})",
                f"AI image is missing transparent attribution in figure_source! Expected 'AI-Generated Clinical Infographic | Based on...', got: '{fig_source}'",
            ))
        try:
            im = Image.open(img_path).convert("RGB")
            arr = np.array(im)
            h, w, _ = arr.shape
            corners = [
                ("Top-Left", arr[2, 2]),
                ("Top-Right", arr[2, w - 3]),
                ("Bottom-Left", arr[h - 3, 2]),
                ("Bottom-Right", arr[h - 3, w - 3]),
            ]
            for cname, cval in corners:
                if int(cval[0]) < 220 or int(cval[1]) < 220 or int(cval[2]) < 220:
                    violations.append((
                        source_label,
                        f"{slide_label} ({img_name})",
                        f"Non-white background at {cname} corner: RGB{tuple(cval)}. AI vector images inside white card must have 100% pure white canvas (#FFFFFF)!",
                    ))
                    break
        except Exception as e:
            violations.append((source_label, slide_label, f"Failed to inspect image {img_name}: {e}"))
    elif require_source and not fig_source.strip():
        violations.append((source_label, f"{slide_label} ({img_name})", "Textbook image missing figure_source attribution!"))
    return violations


def cmd_check_visual_compliance(args):
    """
    Visual Governance Linter:
    Supports BOTH Phase 5 Bento (`evidence_bundle.json`) and Legacy Python (`build*.py`).
    Verifies image existence in extracted_assets/, Pure White Canvas corners for AI vector art,
    and textbook/AI attribution.
    """
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        print("ERROR: PIL and numpy are required for visual compliance check.", file=sys.stderr)
        sys.exit(1)

    project_dir = os.path.abspath(args.project_dir)
    ev_path = os.path.join(project_dir, "evidence_bundle.json")
    target_files = sorted(glob.glob(os.path.join(project_dir, "build*.py")))

    if not os.path.exists(ev_path) and not target_files:
        print(f"ERROR: No evidence_bundle.json or build*.py found in {project_dir}", file=sys.stderr)
        sys.exit(1)

    asset_dir = os.path.join(project_dir, "extracted_assets")
    violations = []
    checked_count = 0

    if os.path.exists(ev_path):
        import json as _json
        with open(ev_path, "r", encoding="utf-8") as ef:
            ev_data = _json.load(ef)
        for idx, sl in enumerate(ev_data.get("slides", []), 1):
            s_no = sl.get("slide_id", idx)
            fig = sl.get("figure") if isinstance(sl.get("figure"), dict) else None
            img_name = fig.get("image_file") if fig else sl.get("image_file")
            if not img_name:
                continue
            fig_source = str((fig.get("source") if fig else sl.get("figure_source")) or "")
            claim_id = str((fig.get("claim_id") if fig else "") or "")
            has_attr = bool(fig_source.strip() or claim_id.strip())
            checked_count += 1
            violations.extend(
                _check_single_image_compliance(
                    "evidence_bundle.json",
                    f"Slide {s_no}",
                    img_name,
                    fig_source if fig_source.strip() else claim_id,
                    asset_dir,
                    Image,
                    np,
                    require_source=not has_attr,
                )
            )
        for ref in ev_data.get("references", []):
            cov = ref.get("cover_image")
            if cov:
                checked_count += 1
                cov_path = os.path.join(asset_dir, cov)
                if not os.path.exists(cov_path):
                    violations.append(("evidence_bundle.json", f"Ref [{ref.get('id', '?')}]", f"Missing cover asset: {cov}"))

    for tf in target_files:
        bname = os.path.basename(tf)
        with open(tf, "r", encoding="utf-8") as f:
            content = f.read()

        slide_blocks = re.split(r'#\s*SLIDE\s+(\d+):?', content)
        for i in range(1, len(slide_blocks), 2):
            slide_no = slide_blocks[i]
            b_text = slide_blocks[i+1]

            img_m = re.search(r'image_file\s*=\s*["\']([^"\']+)["\']', b_text)
            src_m = re.search(r'figure_source\s*=\s*["\']([^"\']+)["\']', b_text)

            if not img_m:
                continue

            img_name = img_m.group(1)
            fig_source = src_m.group(1) if src_m else ""
            checked_count += 1
            violations.extend(
                _check_single_image_compliance(bname, f"Slide {slide_no}", img_name, fig_source, asset_dir, Image, np)
            )

    print(f"=== Visual Governance Compliance Audit ({checked_count} slide image references checked) ===")
    if not violations:
        print("PASS 100%: All presentation images strictly comply with Pure White Canvas (#FFFFFF) and Transparent AI Attribution rules!")
    else:
        print(f"FAILED: Found {len(violations)} visual governance violations:")
        for fname, s_info, msg in violations:
            print(f"  - [{fname}] {s_info}: {msg}")
        sys.exit(1)


def _estimate_text_width_in(text, pt_size, bold=False):
    """Estimate single-line width in inches using macOS Helvetica/Arial TTF via PIL when available."""
    try:
        from PIL import ImageFont
        for fp in (
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Bold.ttf" if bold else "/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        ):
            if os.path.exists(fp):
                idx = 1 if (bold and fp.endswith(".ttc")) else 0
                font = ImageFont.truetype(fp, int(round(pt_size * 1.3333)), index=idx) if fp.endswith(".ttc") else ImageFont.truetype(fp, int(round(pt_size * 1.3333)))
                bbox = font.getbbox(text)
                return (bbox[2] - bbox[0]) / 96.0
    except Exception:
        pass
    return len(text) * (pt_size / 72.0) * (0.56 if bold else 0.52)


def _load_mod(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if not spec or not spec.loader:
        raise ImportError(f"Cannot load module {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def cmd_verify_jc_deck(args):
    """Comprehensive Journal Club QA: bounds, header-badge overlap, Arial/01-N footer, 1:1 Notes parity, AI slop & chart checks."""
    project_dir = os.path.abspath(args.project_dir)
    prs = Presentation(args.pptx)
    slide_count = len(prs.slides)
    w_in = prs.slide_width / 914400
    h_in = prs.slide_height / 914400
    issues = []
    warnings = []

    if abs(w_in - 13.333) > 0.02 or abs(h_in - 7.500) > 0.02:
        issues.append(f"Slide dimensions {w_in:.3f}x{h_in:.3f} in != 13.333x7.500 in")

    vv_mod = _load_mod(SCRIPTS_DIR / "verify_verbatim.py", "verify_verbatim")
    fc_mod = _load_mod(CREATOR_SCRIPTS_DIR / "fix_pptx_charts_gslides.py", "fix_pptx_charts_gslides")

    helvetica_hits = 0
    for s_idx, slide in enumerate(prs.slides, 1):
        hdr_boxes = []
        footer_texts = []
        slide_text_blob = []
        for sh in slide.shapes:
            l = sh.left / 914400
            t = sh.top / 914400
            r = l + sh.width / 914400
            b = t + sh.height / 914400
            if l < -0.02 or t < -0.02 or r > 13.35 or b > 7.52:
                issues.append(f"Slide {s_idx}: Shape out-of-bounds ({l:.2f},{t:.2f} -> {r:.2f},{b:.2f})")
            if sh.has_text_frame:
                txt = sh.text_frame.text.strip()
                if txt:
                    slide_text_blob.append(txt)
                    if t >= 6.95:
                        footer_texts.append(txt)
                    elif t < 0.72 and b <= 0.80:
                        hdr_boxes.append((l, t, r, b, txt))
                    if (sh.height / 914400) <= 0.45 and "\n" not in txt and len(txt) > 8:
                        p0 = sh.text_frame.paragraphs[0]
                        fs = p0.font.size.pt if p0.font.size else (p0.runs[0].font.size.pt if p0.runs and p0.runs[0].font.size else 14.0)
                        bold = bool(p0.font.bold or (p0.runs and p0.runs[0].font.bold))
                        est_w = _estimate_text_width_in(txt, fs, bold=bold)
                        usable_w = (sh.width / 914400) - 0.10
                        if est_w > usable_w and fs >= 15.0:
                            issues.append(f"Slide {s_idx}: Single-line header wrap risk '{txt[:40]}' ({est_w:.2f}\" > {usable_w:.2f}\")")
                for para in sh.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.name and "helvetica" in run.font.name.lower():
                            helvetica_hits += 1

        # Header title vs callout_badge horizontal overlap check
        for i in range(len(hdr_boxes)):
            for j in range(i + 1, len(hdr_boxes)):
                l1, t1, r1, b1, tx1 = hdr_boxes[i]
                l2, t2, r2, b2, tx2 = hdr_boxes[j]
                if max(l1, l2) < min(r1, r2) and max(t1, t2) < min(b1, b2):
                    issues.append(f"Slide {s_idx}: Header/Badge horizontal overlap ('{tx1[:22]}' vs '{tx2[:22]}')")

        expected_pg = f"{s_idx:02d} / {slide_count:02d}"
        if not any(expected_pg in ft or f"{s_idx}/{slide_count}" in ft.replace(" ", "") for ft in footer_texts):
            warnings.append(f"Slide {s_idx}: Missing bottom-right pagination '{expected_pg}' (run finalize_jc_slide_numbers)")

        nt = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
        if not nt:
            issues.append(f"Slide {s_idx}: Missing speaker notes")
        elif args.lang == "en" and re.search(r"[\u0E00-\u0E7F]", nt):
            issues.append(f"Slide {s_idx}: Thai characters found in --lang en speaker notes")
        if "—" in nt:
            issues.append(f"Slide {s_idx}: Em-dash found in speaker notes")

        full_slide_and_notes = "\n".join(slide_text_blob) + "\n" + nt
        for pat, reason in UNIVERSAL_BANNED:
            if re.search(pat, full_slide_and_notes, flags=re.IGNORECASE):
                issues.append(f"Slide {s_idx}: Banned AI/Slop pattern [{reason}]")
        for pat, reason in AMBIGUOUS_ABBREVS:
            if re.search(pat, full_slide_and_notes):
                issues.append(f"Slide {s_idx}: {reason}")

    if helvetica_hits:
        warnings.append(f"Font notice: {helvetica_hits} run(s) still use 'Helvetica' instead of cross-platform 'Arial'")

    chart_issues = fc_mod.check_pptx_charts(Path(args.pptx))
    issues.extend(chart_issues)

    pm_md = args.md if getattr(args, "md", "") else os.path.join(project_dir, "PRESENTER_NOTES_MASTER.md")
    if os.path.exists(pm_md):
        with open(pm_md, "r", encoding="utf-8") as f:
            md_txt = f.read()
        md_map = vv_mod._parse_md_notes(pm_md)
        if len(md_map) != slide_count:
            issues.append(f"PRESENTER_NOTES_MASTER.md has {len(md_map)} slides vs PPTX {slide_count}")
        else:
            for s_idx, slide in enumerate(prs.slides, 1):
                nt = slide.notes_slide.notes_text_frame.text.strip() if slide.has_notes_slide else ""
                pn = vv_mod._parse_pptx_note(nt)
                mn = md_map.get(s_idx, {})
                for fld in ("script", "trap", "trans"):
                    if mn.get(fld) and pn.get(fld) != mn.get(fld):
                        issues.append(f"Slide {s_idx}: PPTX vs Markdown '{fld}' 1:1 parity mismatch")
        if args.lang == "en" and re.search(r"[\u0E00-\u0E7F]", md_txt):
            issues.append("PRESENTER_NOTES_MASTER.md contains Thai characters under --lang en")
        if "—" in md_txt:
            issues.append("PRESENTER_NOTES_MASTER.md contains em-dash")

    docx_files = sorted(glob.glob(os.path.join(project_dir, "*Presenter_Notes*.docx")))
    if docx_files:
        try:
            import docx
            d = docx.Document(docx_files[-1])
            xml_blob = "".join(t.text or "" for p in d.paragraphs for t in [p])
            hdrs = [p for p in d.paragraphs if p.text.startswith("Slide ")]
            if len(hdrs) != slide_count:
                issues.append(f"DOCX has {len(hdrs)} Slide headers vs PPTX {slide_count}")
            if any(not p.paragraph_format.keep_with_next for p in hdrs):
                issues.append("DOCX missing keep_with_next=True on one or more Slide headers")
            if args.lang == "en" and re.search(r"[\u0E00-\u0E7F]", xml_blob):
                issues.append("DOCX contains Thai characters under --lang en")
        except Exception as e:
            issues.append(f"DOCX read error: {e}")

    print(f"=== Journal Club Deck Audit ({slide_count} slides, lang={args.lang}) ===")
    for w in warnings:
        print(f"  ! {w}")
    if not issues:
        print(f"PASS 100%: {slide_count}/{slide_count} slides clean (0 OOB, 0 header wraps, {args.lang} parity verified)!")
    else:
        print(f"FAILED: Found {len(issues)} issue(s):")
        for iss in issues:
            print(f"  - {iss}")
        sys.exit(1)


def cmd_sync_rule(args):
    """Two-Way Rule Sync between project ./USER_INSTRUCTIONS_MASTER.md and global USER_INSTRUCTIONS_TEMPLATE.md."""
    project_dir = Path(args.project_dir).resolve()
    master_path = project_dir / "USER_INSTRUCTIONS_MASTER.md"
    tmpl_path = Path(args.template).resolve() if args.template else (CREATOR_TEMPLATES_DIR / "USER_INSTRUCTIONS_TEMPLATE.md")
    if not tmpl_path.exists():
        print(f"ERROR: Global template not found: {tmpl_path}", file=sys.stderr)
        sys.exit(1)

    section_hdr = "## หมวดที่ 9: กฎเพิ่มเติมล่าสุด (Two-Way Synced Rules)"
    new_rules: list[str] = []
    if args.rule:
        new_rules.append(args.rule.strip())
    elif master_path.exists():
        m_txt = master_path.read_text(encoding="utf-8")
        if section_hdr in m_txt:
            tail = m_txt.split(section_hdr, 1)[1]
            for line in tail.splitlines():
                s = line.strip()
                if s.startswith("- "):
                    new_rules.append(s[2:].strip())

    if not new_rules:
        print("INFO: No new rules provided (--rule '...' or Category 9 entries in USER_INSTRUCTIONS_MASTER.md). Nothing to sync.")
        return

    updated_files = []
    targets = [tmpl_path]
    if master_path.exists() and args.rule:
        targets.insert(0, master_path)

    for target in targets:
        content = target.read_text(encoding="utf-8")
        added = []
        if section_hdr not in content:
            content = content.rstrip() + f"\n\n---\n\n{section_hdr}\n"
        for rule in new_rules:
            if rule in content:
                continue
            content = content.rstrip() + f"\n- {rule}"
            added.append(rule)
        if added:
            target.write_text(content + "\n", encoding="utf-8")
            updated_files.append((str(target), len(added)))

    if updated_files:
        for path_str, cnt in updated_files:
            print(f"SUCCESS: Synced {cnt} rule(s) -> {path_str}")
    else:
        print("PASS: All specified rules already present in target files (no duplicate writes).")


def cmd_audit_deck(args):
    """Unified one-shot automated gate: verify_verbatim + Notes/Abbrev/Monotony + Google Slides chart check + bounds + optional Contact Sheet."""
    project_dir = Path(args.project_dir).resolve()
    pptx_path = Path(args.pptx).resolve()
    ev_path = Path(args.evidence).resolve()
    md_path = Path(args.md).resolve() if args.md else (project_dir / "PRESENTER_NOTES_MASTER.md")

    cmd_vv = [
        sys.executable,
        str(SCRIPTS_DIR / "verify_verbatim.py"),
        "--evidence",
        str(ev_path),
        "--pptx",
        str(pptx_path),
        "--profile",
        args.profile,
    ]
    if md_path.exists():
        cmd_vv.extend(["--md", str(md_path)])
    if args.notes_dir and Path(args.notes_dir).exists():
        cmd_vv.extend(["--notes-dir", str(Path(args.notes_dir).resolve())])
    if args.allow_legacy_shorthand:
        cmd_vv.append("--allow-legacy-shorthand")
    if getattr(args, "strict_warnings", False):
        cmd_vv.append("--strict-warnings")

    print("[1/4] Running Verbatim, Parity, Monotony, Notes & Abbreviation Gates...")
    r1 = subprocess.run(cmd_vv)
    if r1.returncode != 0:
        sys.exit(r1.returncode)

    print("[2/4] Running Google Slides Chart XML Gate...")
    r2 = subprocess.run([sys.executable, str(CREATOR_SCRIPTS_DIR / "fix_pptx_charts_gslides.py"), "--pptx", str(pptx_path), "--check"])
    if r2.returncode != 0:
        sys.exit(r2.returncode)

    print("[3/4] Running Whole-Deck Bounds & Wrap Gate...")
    errs, warns = _check_pptx_bounds_internal(str(pptx_path), slide_num=None)
    for w in warns:
        print(f"  ! {w}")
    if errs:
        for e in errs:
            print(f"  - {e}")
        sys.exit(1)
    print(f"PASS: Whole-deck bounds clean ({len(warns)} wrap notice(s)).")

    if args.render_dir:
        print("[4/4] Rendering PNG Slides & Contact Sheet via LibreOffice...")
        rdir = Path(args.render_dir).resolve()
        render_cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "visual_qa_renderer.py"),
            "--pptx",
            str(pptx_path),
            "--out-dir",
            str(rdir),
            "--contact-sheet",
            str(rdir / "contact_sheet.png"),
        ]
        r4 = subprocess.run(render_cmd)
        if r4.returncode != 0:
            sys.exit(r4.returncode)
    else:
        print("[4/4] Render skipped (pass --render-dir to generate PNG Contact Sheet).")


def _forward_script(script_name: str, extra_args: list[str]):
    res = subprocess.run([sys.executable, str(SCRIPTS_DIR / script_name)] + extra_args)
    sys.exit(res.returncode)


def main():
    parser = argparse.ArgumentParser(description="PM&R Slide Auditor CLI (Phase 5)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_vis = sub.add_parser("check-visual-compliance", help="Scan slides for image background and AI attribution compliance")
    p_vis.add_argument("--project-dir", default=".")
    p_vis.set_defaults(func=cmd_check_visual_compliance)

    p_ban = sub.add_parser("check-banned", help="Scan project for banned phrases and ambiguous abbreviations")
    p_ban.add_argument("--project-dir", default=".")
    p_ban.add_argument("--profile", default="pmr_board", choices=["universal", "pmr_board", "journal_club", "amputation"])
    p_ban.add_argument("--strict", action="store_true")
    p_ban.set_defaults(func=cmd_check_banned)

    p_jc = sub.add_parser("verify-jc-deck", help="Audit Journal Club PPTX bounds, wraps, notes parity, AI slop, and charts")
    p_jc.add_argument("--project-dir", default=".")
    p_jc.add_argument("--pptx", required=True)
    p_jc.add_argument("--md", default="")
    p_jc.add_argument("--lang", default="en", choices=["en", "th"])
    p_jc.set_defaults(func=cmd_verify_jc_deck)

    p_srch = sub.add_parser("search-textbooks", help="Search primary textbook PDFs")
    p_srch.add_argument("--project-dir", default=".")
    p_srch.add_argument("--query", required=True)
    p_srch.add_argument("--limit", type=int, default=15)
    p_srch.add_argument("--book-filter", default="", help="Optional regex filter for PDF filename (e.g. 'Frontera|Hand')")
    p_srch.add_argument("--pdf-pages", default="", help="Optional 1-based PDF page range (e.g. '210-220')")
    p_srch.add_argument("--exclude-regex", default=r"(senior|legacy)")
    p_srch.set_defaults(func=cmd_search_textbooks)

    p_fig = sub.add_parser("find-figures", help="Find figure/table candidates in primary textbooks")
    p_fig.add_argument("--project-dir", default=".")
    p_fig.add_argument("--query", required=True)
    p_fig.add_argument("--limit", type=int, default=15)
    p_fig.add_argument("--exclude-regex", default=r"(senior|legacy)")
    p_fig.set_defaults(func=cmd_find_figures)

    p_ext = sub.add_parser("extract-figure", help="Extract figure or cropped table at 4x resolution")
    p_ext.add_argument("--pdf", required=True)
    p_ext.add_argument("--pdf-page", type=int, required=True)
    p_ext.add_argument("--bbox", help="Optional x0,y0,x1,y1 in PDF points")
    p_ext.add_argument("--zoom", type=float, default=4.0)
    p_ext.add_argument("--out", required=True)
    p_ext.set_defaults(func=cmd_extract_figure)

    p_bnd = sub.add_parser("verify-pptx-bounds", help="Verify PPTX white card, bounds, and wrapped text height")
    p_bnd.add_argument("--pptx", required=True)
    p_bnd.add_argument("--slide", type=int, default=None)
    p_bnd.add_argument("--all", action="store_true", help="Audit every slide in PPTX (default when --slide omitted)")
    p_bnd.set_defaults(func=cmd_verify_pptx_bounds)

    p_sync = sub.add_parser("sync-rule", help="Two-Way Rule Sync to global USER_INSTRUCTIONS_TEMPLATE.md")
    p_sync.add_argument("--project-dir", default=".")
    p_sync.add_argument("--rule", default="", help="Rule text to append cleanly to project & global template")
    p_sync.add_argument("--template", default="", help="Optional override path to global template")
    p_sync.set_defaults(func=cmd_sync_rule)

    p_aud = sub.add_parser("audit-deck", help="Unified Phase 5 gate: verbatim + notes + abbrev + charts + bounds + render")
    p_aud.add_argument("--project-dir", default=".")
    p_aud.add_argument("--pptx", required=True)
    p_aud.add_argument("--evidence", required=True)
    p_aud.add_argument("--md", default="")
    p_aud.add_argument("--notes-dir", default="")
    p_aud.add_argument("--profile", default="pmr_board", choices=["universal", "pmr_board", "journal_club", "amputation"])
    p_aud.add_argument("--render-dir", default="")
    p_aud.add_argument("--allow-legacy-shorthand", action="store_true")
    p_aud.add_argument("--strict-warnings", action="store_true", help="Fail if hygiene warnings (e.g. Double thank-you) occur")
    p_aud.set_defaults(func=cmd_audit_deck)

    p_af = sub.add_parser("auto-find-figures", help="Forward to auto_find_figures.py (extract-covers / find-figures / extract-id)")
    p_af.set_defaults(func=None)

    p_rn = sub.add_parser("render-slides", help="Forward to visual_qa_renderer.py (LibreOffice PDF->PNG + contact sheet)")
    p_rn.set_defaults(func=None)

    args, rest = parser.parse_known_args()
    if args.cmd == "auto-find-figures":
        _forward_script("auto_find_figures.py", rest)
    elif args.cmd == "render-slides":
        _forward_script("visual_qa_renderer.py", rest)
    elif rest:
        parser.error(f"unrecognized arguments: {' '.join(rest)}")
    else:
        args.func(args)


if __name__ == "__main__":
    main()
