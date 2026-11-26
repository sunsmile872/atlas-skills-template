#!/usr/bin/env python3
"""
Presenter Notes Bridge for PptxGenJS v2 Decks (Phase 3 Prototype)
Injects 1:1 spoken scripts, Staff Q&A Defense Traps, and transitions from notes_data_modules/mod*.py
into any compiled .pptx (handling trailing References slide gracefully), and writes
PRESENTER_NOTES_MASTER.md (no .docx output unless --out-docx is explicitly requested).
"""

from __future__ import annotations
import argparse
import glob
import importlib.util
import os
import sys
from pptx import Presentation


def load_notes_modules(modules_dir: str) -> dict[int, dict]:
    notes_data: dict[int, dict] = {}
    if not os.path.isdir(modules_dir):
        return notes_data
    for py_file in sorted(glob.glob(os.path.join(modules_dir, "mod*.py"))):
        spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(py_file))[0], py_file)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "DATA"):
                notes_data.update(mod.DATA)
    return notes_data


def inject_pptx_notes(pptx_path: str, notes_data: dict[int, dict], lang: str = "th", out_pptx: str | None = None):
    prs = Presentation(pptx_path)
    is_en = lang.lower().startswith("en")
    injected = 0
    for idx, slide in enumerate(prs.slides, 1):
        info = notes_data.get(idx)
        if not info:
            # Handle trailing References slide cleanly
            if idx == len(prs.slides):
                slide.notes_slide.notes_text_frame.text = (
                    "[0:10] Primary Textbook References\n\n"
                    "Summary of primary textbooks and exact chapters/pages cited across the presentation."
                )
                injected += 1
            continue
        if is_en:
            notes_text = (
                f"[{info['time']}] {info['title']}\n\n"
                f"[Spoken Script]:\n{info['script']}\n\n"
                f"[Staff Q&A Defense]:\n{info['trap']}\n\n"
                f"[Transition]: {info['trans']}"
            )
        else:
            notes_text = (
                f"[{info['time']}] {info['title']}\n\n"
                f"【บทพูดบรรยาย】:\n{info['script']}\n\n"
                f"【Staff Q&A Trap】:\n{info['trap']}\n\n"
                f"【Transition】: {info['trans']}"
            )
        slide.notes_slide.notes_text_frame.text = notes_text
        injected += 1

    target = out_pptx or pptx_path
    prs.save(target)
    print(f"SUCCESS: Injected notes into {injected}/{len(prs.slides)} slides -> {target}")
    return len(prs.slides)


def generate_markdown(notes_data: dict[int, dict], topic: str, out_md: str, lang: str = "th", total_slides: int = 0):
    is_en = lang.lower().startswith("en")
    md_lines = [
        f"# Master Presenter Notes & Staff Q&A Defense Suite{' (English)' if is_en else ''}",
        f"## {topic}",
        "",
        "---",
        "",
    ]
    for idx in sorted(notes_data.keys()):
        info = notes_data[idx]
        if is_en:
            md_lines.append(f"### Slide {idx:02d} | {info['title']} ({info['time']})")
            md_lines.append(f"**Spoken Script**:\n> {info['script']}\n")
            md_lines.append(f"**Staff Q&A Defense**:\n```text\n{info['trap']}\n```\n")
        else:
            md_lines.append(f"### Slide {idx:02d}: {info['title']} ({info['time']})")
            md_lines.append(f"**บทพูดบรรยาย**:\n> {info['script']}\n")
            md_lines.append(f"**Staff Q&A Defense Trap**:\n```text\n{info['trap']}\n```\n")
        md_lines.append(f"*Transition*: `{info['trans']}`\n")
        md_lines.append("---\n")

    if total_slides > max(notes_data.keys()):
        ref_idx = total_slides
        md_lines.append(f"### Slide {ref_idx:02d}: Primary Textbook References (0:10)")
        md_lines.append(
            "**Spoken Guidepost**:\n> Summary of primary textbooks and exact chapters/pages cited across the presentation.\n"
            if is_en
            else "**บทพูดปิดท้าย**:\n> สรุปรายชื่อตำราหลัก พร้อมบทและเลขหน้าที่อ้างอิงตลอดการนำเสนอครับ\n"
        )
        md_lines.append("---\n")

    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"SUCCESS: Generated {out_md}")


def main():
    parser = argparse.ArgumentParser(description="Inject presenter notes into v2 PPTX decks and save Markdown master")
    parser.add_argument("--pptx", required=True)
    parser.add_argument("--modules-dir", required=True)
    parser.add_argument("--topic", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--lang", default="th", choices=["th", "en"])
    args = parser.parse_args()

    notes_data = load_notes_modules(args.modules_dir)
    if not notes_data:
        print(f"ERROR: No mod*.py notes modules found in {args.modules_dir}", file=sys.stderr)
        sys.exit(1)

    total_slides = inject_pptx_notes(args.pptx, notes_data, lang=args.lang)
    generate_markdown(notes_data, args.topic, args.out_md, lang=args.lang, total_slides=total_slides)


if __name__ == "__main__":
    main()
