#!/usr/bin/env python3
"""
Medical Lecture Notes Compiler (Skill: lecture-notes)
Compiles slide PDFs (digital or lecture photos) + audio transcripts into
polished, high-resolution iPad study materials (Approach B & C) on pure white backgrounds.
"""

import os
import sys
import argparse
import base64
import subprocess
import json
import pypdfium2 as pdfium
import cv2
import numpy as np
from pathlib import Path

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def is_photo_slide(img):
    """Detects whether an image is a photo of a lecture screen or a clean digital slide."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Check edges and dark borders around the canvas
    h, w = gray.shape
    top_bar = np.mean(gray[:int(h * 0.05), :])
    bottom_bar = np.mean(gray[int(h * 0.95):, :])
    left_bar = np.mean(gray[:, :int(w * 0.05)])
    right_bar = np.mean(gray[:, int(w * 0.95):])
    
    # In lecture photos, surrounding walls or casings are dark or textured
    if left_bar < 60 and right_bar < 60 and (top_bar < 80 or bottom_bar < 80):
        return True
    return False

def render_slide_images(pdf_path, temp_dir, mode="auto"):
    """
    Renders all pages of a PDF to high-resolution JPEG images.
    - If digital: direct 2.5x high-DPI rendering on pure white canvas.
    - If photo: applies adaptive contrast enhancement (CLAHE) on pure white iPad canvas.
    """
    pdf = pdfium.PdfDocument(str(pdf_path))
    total_pages = len(pdf)
    print(f"[*] Rendering {total_pages} slides from: {pdf_path}")
    
    slide_paths = []
    
    for i in range(total_pages):
        page = pdf[i]
        # Render high-resolution
        pil_img = page.render(scale=2.5).to_pil()
        cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        h, w = cv_img.shape[:2]
        
        slide_is_photo = (mode == "photo") or (mode == "auto" and is_photo_slide(cv_img))
        
        if slide_is_photo:
            # Mount onto clean iPad canvas with CLAHE enhancement
            # iPad 4:3 canvas (2048 x 1536) pure white
            canvas = np.ones((1536, 2048, 3), dtype=np.uint8) * 255
            scale = min(1920 / w, 1380 / h)
            new_w, new_h = int(w * scale), int(h * scale)
            resized = cv2.resize(cv_img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
            
            # CLAHE contrast enhancement
            lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=1.6, tileGridSize=(8, 8))
            cl = clahe.apply(l)
            enhanced = cv2.cvtColor(cv2.merge((cl, a, b)), cv2.COLOR_LAB2BGR)
            
            ox = (2048 - new_w) // 2
            oy = (1536 - new_h) // 2
            canvas[oy:oy+new_h, ox:ox+new_w] = enhanced
            out_img = canvas
        else:
            # Digital slide: mount centered on crisp white canvas
            out_img = cv_img
            
        out_path = Path(temp_dir) / f"slide_{i+1:03d}.jpg"
        cv2.imwrite(str(out_path), out_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
        slide_paths.append(str(out_path))
        
    return slide_paths

def generate_annotated_html(slide_paths, slides_data, lecture_title="Lecture Notes"):
    """
    Builds the complete HTML document for Approach B Annotated Notes (iPad Vertical A4, pure white theme).
    """
    pages_html = []
    
    for i, slide_path in enumerate(slide_paths):
        slide_num = i + 1
        with open(slide_path, "rb") as f:
            b64_img = base64.b64encode(f.read()).decode("utf-8")
        data_uri = f"data:image/jpeg;base64,{b64_img}"
        
        # Metadata & clinical notes
        info = slides_data.get(slide_num, {})
        title = info.get("title", f"Slide {slide_num}")
        timestamp = info.get("timestamp", "")
        points = info.get("points", [])
        
        points_html = ""
        if points:
            points_li = "".join([f"<li>{pt}</li>" for pt in points])
            points_html = f"<ul>{points_li}</ul>"
        else:
            points_html = "<div class='empty-notes'>[พื้นที่สำหรับจดโน้ตสรุปเพิ่มเติม / Additional Clinical Notes]</div>"
            
        badge_html = f"<div class='time-badge'>⏱️ {timestamp}</div>" if timestamp else ""
        
        page = f"""
        <div class="note-page">
            <div class="header-bar">
                <div class="title-group">
                    <span class="slide-num-pill">SLIDE {slide_num}</span>
                    <span class="slide-title">{title}</span>
                </div>
                {badge_html}
            </div>
            
            <div class="slide-frame">
                <img src="{data_uri}" alt="Slide {slide_num}" />
            </div>
            
            <div class="notes-card">
                <div class="notes-header">
                    <span class="card-icon">💡</span>
                    <span class="card-title">สรุปประเด็นสำคัญ & คำบรรยายอาจารย์ (Clinical Pearls)</span>
                </div>
                <div class="notes-body">
                    {points_html}
                </div>
            </div>
            
            <div class="footer-bar">
                <span>{lecture_title} • Clinical Lecture Notes</span>
                <span>Page {slide_num} of {len(slide_paths)}</span>
            </div>
        </div>
        """
        pages_html.append(page)
        
    full_html = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>{lecture_title} - Annotated Lecture Notes</title>
    <style>
        @page {{
            size: A4 portrait;
            margin: 0;
        }}
        * {{
            box-sizing: border-box;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
        body {{
            margin: 0;
            padding: 0;
            background-color: #FFFFFF;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Sarabun", Helvetica, Arial, sans-serif;
            color: #1e293b;
        }}
        .note-page {{
            width: 210mm;
            height: 297mm;
            page-break-after: always;
            box-sizing: border-box;
            padding: 14mm 16mm 12mm 16mm;
            display: flex;
            flex-direction: column;
            background: #FFFFFF;
            position: relative;
        }}
        .header-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 8px;
            margin-bottom: 12px;
        }}
        .title-group {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .slide-num-pill {{
            background: #0f766e;
            color: #ffffff;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }}
        .slide-title {{
            font-size: 15px;
            font-weight: 700;
            color: #0f172a;
        }}
        .time-badge {{
            background: #f1f5f9;
            color: #475569;
            font-size: 11px;
            font-weight: 600;
            padding: 3px 10px;
            border-radius: 12px;
            border: 1px solid #cbd5e1;
        }}
        .slide-frame {{
            width: 100%;
            height: 108mm;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            margin-bottom: 12px;
        }}
        .slide-frame img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
        }}
        .notes-card {{
            flex: 1;
            background: #ffffff;
            border: 1.5px solid #cbd5e1;
            border-left: 5px solid #0f766e;
            border-radius: 8px;
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
            box-shadow: 0 1px 3px rgba(0,0,0,0.03);
            margin-bottom: 8px;
        }}
        .notes-header {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 13px;
            font-weight: 700;
            color: #0f766e;
            margin-bottom: 8px;
            border-bottom: 1px dashed #e2e8f0;
            padding-bottom: 6px;
        }}
        .card-icon {{
            font-size: 14px;
        }}
        .notes-body {{
            font-size: 13px;
            line-height: 1.55;
            color: #334155;
            flex: 1;
        }}
        .notes-body ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .notes-body li {{
            margin-bottom: 6px;
        }}
        .notes-body strong {{
            color: #0f172a;
            font-weight: 600;
        }}
        .empty-notes {{
            color: #94a3b8;
            font-style: italic;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .footer-bar {{
            display: flex;
            justify-content: space-between;
            font-size: 10px;
            color: #94a3b8;
            border-top: 1px solid #f1f5f9;
            padding-top: 6px;
        }}
    </style>
</head>
<body>
    {''.join(pages_html)}
</body>
</html>
"""
    return full_html

def compile_html_to_pdf(html_content, output_pdf):
    """Renders HTML directly into a perfect vector/print PDF using Chrome headless."""
    temp_html = Path(output_pdf).parent / "temp_render.html"
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={output_pdf}",
        str(temp_html)
    ]
    subprocess.run(cmd, check=True)
    if temp_html.exists():
        temp_html.unlink()
    print(f"[✓] Created PDF: {output_pdf}")

def main():
    parser = argparse.ArgumentParser(description="Compile Medical Lecture Slides into iPad Study Notes")
    parser.add_argument("--pdf", required=True, help="Path to input presentation PDF")
    parser.add_argument("--notes-json", help="Path to JSON file with slide annotations and timestamps")
    parser.add_argument("--output-dir", help="Directory where final PDFs will be saved")
    parser.add_argument("--title", default="Lecture Notes", help="Title of the lecture")
    parser.add_argument("--mode", choices=["auto", "digital", "photo"], default="auto", help="Slide processing mode")
    
    args = parser.parse_args()
    
    pdf_path = Path(args.pdf).resolve()
    if not pdf_path.exists():
        print(f"Error: PDF not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)
        
    out_dir = Path(args.output_dir).resolve() if args.output_dir else pdf_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    
    temp_dir = out_dir / "_temp_lecture_slides"
    temp_dir.mkdir(exist_ok=True)
    
    slide_paths = render_slide_images(pdf_path, temp_dir, mode=args.mode)
    
    slides_data = {}
    if args.notes_json and Path(args.notes_json).exists():
        with open(args.notes_json, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            # Accept list of dicts or dict mapping str(slide) -> dict
            if isinstance(raw_data, list):
                for item in raw_data:
                    slides_data[int(item.get("slide", 0))] = item
            elif isinstance(raw_data, dict):
                for k, v in raw_data.items():
                    slides_data[int(k)] = v
                    
    annotated_html = generate_annotated_html(slide_paths, slides_data, lecture_title=args.title)
    output_annotated_pdf = out_dir / f"{pdf_path.stem}_Annotated_Lecture_Notes_White_iPad.pdf"
    compile_html_to_pdf(annotated_html, output_annotated_pdf)
    
    # Cleanup temp slides
    for p in temp_dir.glob("*.jpg"):
        p.unlink()
    temp_dir.rmdir()
    
    print("\n[Done] All deliverables successfully compiled!")

if __name__ == "__main__":
    main()
