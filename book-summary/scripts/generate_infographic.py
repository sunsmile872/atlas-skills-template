#!/usr/bin/env python3
"""
Infographic Generator for book-summary skill.
Generates a standalone, beautiful, vertical A4-styled Executive Infographic Poster (HTML & PDF)
following the Dark Navy Blue / Teal Green / Mint palette.
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} - Executive Book Infographic</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Sarabun:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
  :root {{
    --bg-main: #07101e;
    --bg-card: rgba(13, 27, 46, 0.85);
    --bg-card-inner: #09172a;
    --teal: #00b4d8;
    --teal-glow: rgba(0, 180, 216, 0.25);
    --mint: #64ffda;
    --mint-glow: rgba(100, 255, 218, 0.2);
    --navy-border: rgba(100, 255, 218, 0.18);
    --text-white: #f8fafc;
    --text-muted: #94a3b8;
    --text-accent: #38bdf8;
    --accent-gold: #fbbf24;
  }}

  * {{
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }}

  body {{
    background: var(--bg-main);
    color: var(--text-white);
    font-family: 'Sarabun', 'Plus Jakarta Sans', -apple-system, sans-serif;
    line-height: 1.6;
    padding: 40px 20px;
    display: flex;
    justify-content: center;
    background-image: radial-gradient(circle at 15% 15%, rgba(0, 180, 216, 0.08) 0%, transparent 40%),
                      radial-gradient(circle at 85% 85%, rgba(100, 255, 218, 0.06) 0%, transparent 40%);
  }}

  .poster-container {{
    width: 100%;
    max-width: 900px;
    background: var(--bg-main);
    border: 1px solid var(--navy-border);
    border-radius: 20px;
    padding: 48px 40px;
    box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 40px rgba(0, 180, 216, 0.1);
    position: relative;
    overflow: hidden;
  }}

  .poster-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: linear-gradient(90deg, var(--teal), var(--mint));
  }}

  .header {{
    text-align: center;
    margin-bottom: 36px;
    border-bottom: 1px solid rgba(100, 255, 218, 0.15);
    padding-bottom: 24px;
  }}

  .badge {{
    display: inline-block;
    padding: 6px 16px;
    background: rgba(0, 180, 216, 0.15);
    border: 1px solid var(--teal);
    color: var(--mint);
    font-size: 0.8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    border-radius: 9999px;
    margin-bottom: 12px;
  }}

  .title {{
    font-family: 'Plus Jakarta Sans', 'Sarabun', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.25;
    background: linear-gradient(135deg, #ffffff 40%, var(--text-accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }}

  .subtitle {{
    font-size: 1.05rem;
    color: var(--text-muted);
    font-weight: 400;
  }}

  .meta-bar {{
    display: flex;
    justify-content: center;
    gap: 24px;
    margin-top: 14px;
    font-size: 0.85rem;
    color: var(--mint);
  }}

  .grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    margin-bottom: 24px;
  }}

  .full-width {{
    grid-column: 1 / -1;
  }}

  .card {{
    background: var(--bg-card);
    border: 1px solid var(--navy-border);
    border-radius: 14px;
    padding: 24px;
    backdrop-filter: blur(12px);
    transition: transform 0.2s ease, border-color 0.2s ease;
  }}

  .card:hover {{
    border-color: rgba(100, 255, 218, 0.4);
    transform: translateY(-2px);
  }}

  .card-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 16px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.1);
    padding-bottom: 10px;
  }}

  .card-icon {{
    width: 28px;
    height: 28px;
    border-radius: 8px;
    background: var(--teal-glow);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--mint);
    font-weight: bold;
    font-size: 0.9rem;
  }}

  .card-title {{
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--text-white);
    letter-spacing: -0.2px;
  }}

  .core-thesis {{
    background: linear-gradient(135deg, rgba(0, 180, 216, 0.12), rgba(100, 255, 218, 0.05));
    border-left: 4px solid var(--mint);
    padding: 16px 20px;
    border-radius: 0 12px 12px 0;
    font-size: 1.05rem;
    color: #e2e8f0;
    margin-bottom: 16px;
  }}

  .pill-list {{
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }}

  .pill-item {{
    background: var(--bg-card-inner);
    border: 1px solid rgba(100, 255, 218, 0.1);
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }}

  .pill-num {{
    background: var(--teal);
    color: var(--bg-main);
    font-weight: 800;
    font-size: 0.75rem;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
  }}

  .pill-content strong {{
    color: var(--mint);
    display: block;
    margin-bottom: 2px;
  }}

  .pill-content {{
    font-size: 0.95rem;
    color: var(--text-muted);
  }}

  .rule-box {{
    background: var(--bg-card-inner);
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 10px;
    border-left: 3px solid var(--teal);
    font-size: 0.9rem;
  }}

  .rule-label {{
    color: var(--teal);
    font-weight: 700;
    font-size: 0.75rem;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}

  .comp-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.88rem;
    margin-top: 10px;
  }}

  .comp-table th {{
    background: rgba(0, 180, 216, 0.15);
    color: var(--mint);
    padding: 10px 12px;
    text-align: left;
    font-weight: 600;
    border-bottom: 1px solid var(--navy-border);
  }}

  .comp-table td {{
    padding: 10px 12px;
    border-bottom: 1px solid rgba(148, 163, 184, 0.08);
    color: var(--text-muted);
  }}

  .comp-table tr:hover td {{
    background: rgba(255, 255, 255, 0.02);
    color: var(--text-white);
  }}

  .question-item {{
    background: rgba(251, 191, 36, 0.05);
    border: 1px solid rgba(251, 191, 36, 0.2);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 10px;
    font-size: 0.92rem;
    color: #fef08a;
  }}

  .question-item strong {{
    color: var(--accent-gold);
    display: block;
    margin-bottom: 3px;
  }}

  .footer {{
    margin-top: 36px;
    padding-top: 20px;
    border-top: 1px solid rgba(100, 255, 218, 0.15);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.8rem;
    color: var(--text-muted);
  }}

  .footer-brand {{
    color: var(--mint);
    font-weight: 700;
  }}

  /* Print Styles for Perfect Vertical A4 PDF Export */
  @page {{
    size: A4;
    margin: 8mm;
  }}

  @media print {{
    body {{
      background: var(--bg-main) !important;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
      padding: 0 !important;
    }}

    .poster-container {{
      max-width: 100% !important;
      box-shadow: none !important;
      border: 1px solid rgba(100, 255, 218, 0.3) !important;
      padding: 24px !important;
    }}

    .card {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}

    .pill-item, .rule-box, .question-item, tr {{
      break-inside: avoid;
      page-break-inside: avoid;
    }}
  }}

  @media (max-width: 768px) {{
    .grid {{
      grid-template-columns: 1fr;
    }}
    .poster-container {{
      padding: 24px 18px;
    }}
    .title {{
      font-size: 1.6rem;
    }}
  }}
</style>
</head>
<body>

<div class="poster-container">
  <!-- Header -->
  <div class="header">
    <span class="badge">Executive Book Synthesizer</span>
    <h1 class="title">{title}</h1>
    <div class="subtitle">{author}</div>
    <div class="meta-bar">
      <span>📖 {category}</span>
      <span>⏱️ Quick Deep Dive</span>
      <span>⚡ 3-Tier Action Playbook</span>
    </div>
  </div>

  <!-- Executive Core Thesis -->
  <div class="core-thesis">
    <strong>💡 Core Thesis (แก่นความคิดรวบยอด):</strong><br>
    {core_thesis}
  </div>

  <div class="grid">
    <!-- Pillar 1: Key Mental Models & Principles -->
    <div class="card full-width">
      <div class="card-header">
        <div class="card-icon">01</div>
        <div class="card-title">Key Frameworks & Mental Models (กรอบแนวคิดหลัก)</div>
      </div>
      <div class="pill-list">
        {frameworks_html}
      </div>
    </div>

    <!-- Pillar 2: Action Playbook (If-Then Heuristics) -->
    <div class="card">
      <div class="card-header">
        <div class="card-icon">02</div>
        <div class="card-title">Action Playbook (แนวทางปฏิบัติจริง)</div>
      </div>
      {playbook_html}
    </div>

    <!-- Pillar 3: Critical Inquiry & Reflection -->
    <div class="card">
      <div class="card-header">
        <div class="card-icon">03</div>
        <div class="card-title">Critical Inquiry (คำถามและข้อฉุกคิด)</div>
      </div>
      {questions_html}
    </div>

    <!-- Pillar 4: Comparison Matrix / Mindset Shift -->
    <div class="card full-width">
      <div class="card-header">
        <div class="card-icon">04</div>
        <div class="card-title">Mindset Shift & Paradigm Contrast (การปรับกระบวนทัศน์)</div>
      </div>
      <table class="comp-table">
        <thead>
          <tr>
            <th>มิติการพิจารณา (Dimension)</th>
            <th>กระบวนทัศน์เดิม (Conventional Approach)</th>
            <th>แนวทางจากหนังสือ (The Book's Breakthrough)</th>
          </tr>
        </thead>
        <tbody>
          {table_rows_html}
        </tbody>
      </table>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <div>Generated by <span class="footer-brand">Book-Summary Skill</span></div>
    <div>Professional Clinical & Executive Knowledge Synthesis</div>
  </div>
</div>

</body>
</html>
"""

def generate_poster(json_data: dict, output_path: str, export_pdf: bool = True):
    title = json_data.get("title", "Untitled Book")
    author = json_data.get("author", "Unknown Author")
    category = json_data.get("category", "Non-Fiction / Professional")
    core_thesis = json_data.get("core_thesis", "N/A")

    # Frameworks
    fw_items = []
    for idx, fw in enumerate(json_data.get("frameworks", []), 1):
        name = fw.get("name", f"Framework {idx}")
        desc = fw.get("desc", "")
        fw_items.append(f"""
        <li class="pill-item">
          <div class="pill-num">{idx}</div>
          <div class="pill-content">
            <strong>{name}</strong>
            {desc}
          </div>
        </li>
        """)
    frameworks_html = "\n".join(fw_items)

    # Playbook
    pb_items = []
    for pb in json_data.get("playbook", []):
        situation = pb.get("if", "")
        action = pb.get("then", "")
        pb_items.append(f"""
        <div class="rule-box">
          <div class="rule-label">IF (เมื่อเผชิญสถานการณ์):</div>
          <div>{situation}</div>
          <div class="rule-label" style="color: var(--mint); margin-top: 6px;">THEN (กลยุทธ์ปฏิบัติ):</div>
          <div style="color: var(--text-white);">{action}</div>
        </div>
        """)
    playbook_html = "\n".join(pb_items)

    # Questions
    q_items = []
    for idx, q in enumerate(json_data.get("critical_questions", []), 1):
        question = q.get("question", "")
        purpose = q.get("purpose", "")
        q_items.append(f"""
        <div class="question-item">
          <strong>❓ ข้อฉุกคิดที่ {idx}:</strong>
          {question}
          <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 4px;">🎯 <em>เป้าหมาย: {purpose}</em></div>
        </div>
        """)
    questions_html = "\n".join(q_items)

    # Comparison Table
    tr_items = []
    for row in json_data.get("comparison_table", []):
        dim = row.get("dimension", "")
        old = row.get("conventional", "")
        new = row.get("breakthrough", "")
        tr_items.append(f"""
        <tr>
          <td><strong>{dim}</strong></td>
          <td>{old}</td>
          <td style="color: var(--mint);">{new}</td>
        </tr>
        """)
    table_rows_html = "\n".join(tr_items)

    html = HTML_TEMPLATE.format(
        title=title,
        author=author,
        category=category,
        core_thesis=core_thesis,
        frameworks_html=frameworks_html,
        playbook_html=playbook_html,
        questions_html=questions_html,
        table_rows_html=table_rows_html
    )

    out = Path(output_path)
    if out.suffix.lower() == ".pdf":
        html_path = out.with_suffix(".html")
        pdf_path = out
    else:
        html_path = out
        pdf_path = out.with_suffix(".pdf")

    html_path.parent.mkdir(parents=True, exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] HTML Infographic saved: {html_path.resolve()}")

    if export_pdf:
        if os.path.exists(CHROME_PATH):
            cmd = [
                CHROME_PATH,
                "--headless",
                "--disable-gpu",
                "--no-pdf-header-footer",
                f"--print-to-pdf={pdf_path}",
                str(html_path.resolve())
            ]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if pdf_path.exists():
                    print(f"[OK] PDF Infographic generated: {pdf_path.resolve()}")
                else:
                    print(f"[Warning] PDF generation returned, but file missing: {res.stderr}")
            except Exception as e:
                print(f"[Error] Failed to invoke Chrome headless: {e}")
        else:
            print(f"[Notice] Chrome not found at {CHROME_PATH}, skipping PDF auto-render.")

def main():
    parser = argparse.ArgumentParser(description="Generate Executive Poster Infographic HTML & PDF")
    parser.add_argument("json_file", help="Path to book summary JSON data")
    parser.add_argument("-o", "--output", default="book_infographic.pdf", help="Output file path (.pdf or .html)")
    parser.add_argument("--no-pdf", action="store_true", help="Disable automatic PDF export")
    args = parser.parse_args()

    with open(args.json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    generate_poster(data, args.output, export_pdf=not args.no_pdf)

if __name__ == "__main__":
    main()
