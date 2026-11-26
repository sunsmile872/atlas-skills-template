#!/usr/bin/env python3
"""
CLI Helper for pmr-slide-creator skill:
1. check-ready: Inspects ./textbook reference/ folder and prints onboarding readiness status.
2. scan-refs: Scans PDFs in ./textbook reference/ for TOC/headings/keywords to build the Step 1 Slide Outline.
3. init-project: Initializes make_presentation.py, generate_presenter_notes.py, sync_to_drive.py, and USER_INSTRUCTIONS_MASTER.md.
"""

import argparse
import glob
import json
import os
import re
import shutil
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(SKILL_DIR, "templates")
CHECKLIST_ROOT = os.path.expanduser("~/.gemini/config/skills/karpathy-paper-lab/assets/checklists")


def find_ref_dir(project_dir, mode="topic"):
    if mode == "jc":
        for name in ("source", "textbook reference", "Textbook Reference"):
            p = os.path.join(project_dir, name)
            if os.path.isdir(p):
                return p
        default_dir = os.path.join(project_dir, "source")
        os.makedirs(default_dir, exist_ok=True)
        return default_dir
    candidates = [
        os.path.join(project_dir, "textbook reference"),
        os.path.join(project_dir, "Textbook Reference"),
        os.path.join(project_dir, "textbook_reference"),
    ]
    for c in candidates:
        if os.path.isdir(c):
            return c
    default_dir = os.path.join(project_dir, "textbook reference")
    os.makedirs(default_dir, exist_ok=True)
    return default_dir


def resolve_checklist_pdf(study_type):
    manifest_path = os.path.join(CHECKLIST_ROOT, "manifest.json")
    if not study_type or not os.path.exists(manifest_path):
        return None
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    st = study_type.lower().strip()
    alias = {
        "rct": ("casp_uk", "randomised-controlled-trial-rct-checklist"),
        "sr_ma_rct": ("casp_uk", "systematic-reviews-meta-analysis-rcts"),
        "sr_ma_obs": ("casp_uk", "systematic-reviews-meta-analysis-observational-studies"),
        "sr": ("casp_uk", "systematic-review-checklist"),
        "cohort": ("casp_uk", "cohort-study-checklist"),
        "case_control": ("casp_uk", "case-control-study-checklist"),
        "cross_sectional": ("casp_uk", "cross-sectional-studies-checklist"),
        "diagnostic": ("casp_uk", "diagnostic-study-checklist"),
        "qualitative": ("casp_uk", "qualitative-studies-checklist"),
        "economic": ("casp_uk", "economic-evaluation-checklist"),
        "cpr": ("casp_uk", "clinical-prediction-rule-checklist"),
        "before_after": ("nih_nhlbi", "nih-before-after-pre-post"),
        "case_series": ("nih_nhlbi", "nih-case-series"),
    }
    if st in alias:
        grp, slug = alias[st]
        entry = manifest.get(grp, {}).get(slug)
        if entry:
            cand = os.path.join(CHECKLIST_ROOT, grp, entry["file"])
            if os.path.exists(cand):
                return cand
    return None


def list_pdfs(ref_dir):
    pdfs = sorted(glob.glob(os.path.join(ref_dir, "*.pdf")) + glob.glob(os.path.join(ref_dir, "*.PDF")))
    seen = set()
    unique = []
    for p in pdfs:
        if p not in seen:
            seen.add(p)
            unique.append(p)
    return unique


def cmd_check_ready(args):
    project_dir = os.path.abspath(args.project_dir)
    mode = getattr(args, "mode", "topic")
    ref_dir = find_ref_dir(project_dir, mode=mode)
    pdfs = list_pdfs(ref_dir)

    print("=" * 72)
    print(f"PM&R SLIDE CREATOR — STEP 0 READINESS CHECK (MODE: {mode.upper()})")
    print("=" * 72)
    print(f"Project Directory : {project_dir}")
    print(f"Reference Folder  : {ref_dir}")
    print(f"PDFs Found        : {len(pdfs)}")
    if pdfs:
        for i, p in enumerate(pdfs, 1):
            size_mb = os.path.getsize(p) / (1024 * 1024)
            print(f"  [{i}] {os.path.basename(p)} ({size_mb:.1f} MB)")
        print("\nSTATUS: READY FOR STEP 1 (OUTLINE GENERATION)")
    else:
        print("\nSTATUS: WAITING FOR REFERENCE PDFs")
        lbl = "article PDF" if mode == "jc" else "textbook/guideline PDFs"
        print(f"Please place your {lbl} inside:\n  {ref_dir}")
    print("=" * 72)


def cmd_scan_refs(args):
    if fitz is None:
        print("ERROR: PyMuPDF (fitz) is required for scan-refs.", file=sys.stderr)
        sys.exit(1)

    project_dir = os.path.abspath(args.project_dir)
    mode = getattr(args, "mode", "topic")
    ref_dir = find_ref_dir(project_dir, mode=mode)
    pdfs = list_pdfs(ref_dir)
    keywords = [k.strip().lower() for k in re.split(r"[,;]+|\s+", args.query) if len(k.strip()) >= 3]

    report = {"project_dir": project_dir, "mode": mode, "query": args.query, "books": []}

    for pdf_path in pdfs:
        bname = os.path.basename(pdf_path)
        doc = fitz.open(pdf_path)
        toc = doc.get_toc()
        matched_toc = []
        for level, title, page in toc:
            t_low = title.lower()
            if not keywords or any(k in t_low for k in keywords):
                matched_toc.append({"level": level, "title": title, "pdf_page": page})

        matched_pages = []
        if not matched_toc and keywords:
            for pno in range(len(doc)):
                txt = doc[pno].get_text("text")
                t_low = txt.lower()
                hits = [k for k in keywords if k in t_low]
                if len(hits) >= max(1, min(2, len(keywords))):
                    first_lines = [ln.strip() for ln in txt.splitlines() if ln.strip()][:4]
                    matched_pages.append({
                        "pdf_page": pno + 1,
                        "matched_keywords": hits,
                        "header_preview": " | ".join(first_lines)[:160],
                    })
                    if len(matched_pages) >= 40:
                        break

        report["books"].append({
            "filename": bname,
            "total_pages": len(doc),
            "toc_matches": matched_toc[:60],
            "page_matches": matched_pages,
        })
        doc.close()

    out_path = os.path.join(project_dir, args.output)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"SUCCESS: Scanned {len(pdfs)} PDFs ({mode}) -> saved outline data to {out_path}")


def slugify(text):
    s = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")
    return s or "PMR_Presentation"


def cmd_init_project(args):
    project_dir = os.path.abspath(args.project_dir)
    mode = getattr(args, "mode", "topic")
    engine = getattr(args, "engine", "auto")
    if engine == "auto":
        engine = "python" if mode == "jc" else "bento"
    lang = getattr(args, "lang", None) or ("en" if mode == "jc" else "th")
    ref_dir = find_ref_dir(project_dir, mode=mode)
    pdfs = list_pdfs(ref_dir)

    os.makedirs(os.path.join(project_dir, "extracted_assets"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "notes_data_modules"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "audit_buffer"), exist_ok=True)

    # Copy matching official CASP/NIH checklist PDF into ./source/ in jc mode
    checklist_src = resolve_checklist_pdf(getattr(args, "study_type", None))
    if mode == "jc" and checklist_src:
        dst_chk = os.path.join(ref_dir, os.path.basename(checklist_src))
        if not os.path.exists(dst_chk) or args.overwrite:
            shutil.copy2(checklist_src, dst_chk)
            print(f"COPIED OFFICIAL CHECKLIST: {dst_chk}")
        pdfs = list_pdfs(ref_dir)

    slug = slugify(args.topic)
    if mode == "jc":
        pptx_name = f"{slug}_Journal_Club_{{INSTITUTION}}_PMR.pptx"
        tag = "English" if lang == "en" else "Thai"
        docx_name = f"{slug}_Presenter_Notes_{tag}_{args.slides}Slides.docx"
    else:
        pptx_name = f"{slug}_Presenter.pptx"
        docx_name = f"{slug}_Presenter_Notes_{args.slides}Slides.docx"

    tb_lines = []
    if pdfs:
        for p in pdfs:
            tb_lines.append(f"   - `{os.path.basename(p)}`")
    else:
        folder_lbl = "./source/" if mode == "jc" else "./textbook reference/"
        tb_lines.append(f"   - *(Place primary PDFs inside `{folder_lbl}`)*")

    replacements = {
        "{{THEME_NAME}}": args.theme,
        "{{PPTX_FILENAME}}": pptx_name,
        "{{DOCX_FILENAME}}": docx_name,
        "{{TOPIC_TITLE}}": args.topic,
        "{{TOPIC_SUBTITLE}}": args.subtitle,
        "{{SLIDE_COUNT}}": str(args.slides),
        "{{NOTES_LANG}}": lang,
        "{{TEXTBOOK_LIST}}": "\n".join(tb_lines),
    }

    template_map = [
        ("generate_notes_template.py", "generate_presenter_notes.py"),
        ("sync_to_drive_template.py", "sync_to_drive.py"),
        ("USER_INSTRUCTIONS_TEMPLATE.md", "USER_INSTRUCTIONS_MASTER.md"),
    ]
    if engine == "bento":
        template_map.insert(0, (os.path.join("bento_engine", "build_bento_deck_template.js"), "build_slides.js"))
        template_map.append((os.path.join("bento_engine", "package.json"), "package.json"))
        icons_src = os.path.join(TEMPLATES_DIR, "bento_engine", "icons")
        icons_dst = os.path.join(project_dir, "icons")
        if os.path.isdir(icons_src):
            os.makedirs(icons_dst, exist_ok=True)
            for fn in os.listdir(icons_src):
                if fn.endswith(".png"):
                    dst_f = os.path.join(icons_dst, fn)
                    if not os.path.exists(dst_f) or args.overwrite:
                        shutil.copy2(os.path.join(icons_src, fn), dst_f)
        raw_skeleton = os.path.join(project_dir, "evidence_bundle_raw.json")
        if not os.path.exists(raw_skeleton) or args.overwrite:
            skeleton = {
                "meta": {"topic": args.topic, "subtitle": args.subtitle, "theme": args.theme, "lang": lang},
                "references": [],
                "claim_registry": {},
                "slides": [],
            }
            with open(raw_skeleton, "w", encoding="utf-8") as f:
                json.dump(skeleton, f, ensure_ascii=False, indent=2)
            print(f"CREATED: {raw_skeleton}")
    else:
        template_map.insert(0, ("make_presentation_template.py", "make_presentation.py"))

    for src_name, dst_name in template_map:
        src_path = os.path.join(TEMPLATES_DIR, src_name)
        dst_path = os.path.join(project_dir, dst_name)
        if os.path.exists(dst_path) and not args.overwrite:
            print(f"SKIPPED (already exists): {dst_path}")
            continue
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
        for k, v in replacements.items():
            content = content.replace(k, v)
        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"CREATED: {dst_path}")


def main():
    parser = argparse.ArgumentParser(description="PM&R Slide Creator CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_check = sub.add_parser("check-ready", help="Check ./textbook reference/ or ./source/ readiness")
    p_check.add_argument("--project-dir", default=".")
    p_check.add_argument("--mode", default="topic", choices=["topic", "jc"])
    p_check.set_defaults(func=cmd_check_ready)

    p_scan = sub.add_parser("scan-refs", help="Scan PDFs for TOC and topic matches")
    p_scan.add_argument("--project-dir", default=".")
    p_scan.add_argument("--mode", default="topic", choices=["topic", "jc"])
    p_scan.add_argument("--query", required=True)
    p_scan.add_argument("--output", default="reference_outline.json")
    p_scan.set_defaults(func=cmd_scan_refs)

    p_init = sub.add_parser("init-project", help="Initialize presentation engine and USER_INSTRUCTIONS_MASTER.md")
    p_init.add_argument("--project-dir", default=".")
    p_init.add_argument("--mode", default="topic", choices=["topic", "jc"])
    p_init.add_argument("--engine", default="auto", choices=["auto", "bento", "python"], help="Deck builder engine (default: bento for topic, python for jc)")
    p_init.add_argument("--lang", default=None, choices=["en", "th"], help="Speaker notes language (default: en for jc, th for topic)")
    p_init.add_argument(
        "--study-type",
        default=None,
        choices=["rct", "sr_ma_rct", "sr_ma_obs", "sr", "cohort", "case_control", "cross_sectional", "diagnostic", "qualitative", "economic", "cpr", "before_after", "case_series"],
        help="Auto-copy official CASP UK or NIH NHLBI checklist PDF into ./source/ for --mode jc",
    )
    p_init.add_argument("--topic", required=True)
    p_init.add_argument("--subtitle", default="Evidence-Based PM&R Clinical Review & Rehabilitation Continuum")
    p_init.add_argument("--theme", default="navy_teal", choices=["navy_teal", "academic_brick", "emerald_charcoal", "custom"])
    p_init.add_argument("--slides", type=int, default=30)
    p_init.add_argument("--overwrite", action="store_true")
    p_init.set_defaults(func=cmd_init_project)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
