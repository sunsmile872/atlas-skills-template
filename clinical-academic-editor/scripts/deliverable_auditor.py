#!/usr/bin/env python3
"""
deliverable_auditor.py
Read-only 4-Pillar Deliverable Auditor for clinical/PM&R Markdown drafts:
  Pillar 1: Citation forward/reverse integrity (+ optional live API pass)
  Pillar 2: Statistical & SOT triangulation (p-value bounds, subgroup arithmetic, percentage check, EPV >= 10)
  Pillar 3: LaTeX math delimiter balance & SI unit spacing
  Pillar 4: Anti-Slop lexicon & long sentence check
Emits deliverable_audit_report.md with SHA-256 invariance proof.
"""

import argparse
import hashlib
import os
import re
import subprocess
import sys
from typing import List, Tuple

BANNED_WORDS = [
    "crucial", "paramount", "testament", "game-changer", "revolutionary",
    "landscape", "beacon", "delve", "cutting-edge", "furthermore",
    "paves the way", "sheds light on", "it is important to note",
    "several studies have shown", "fundamentally", "at its core",
]

# Literal AI-translated Thai medical/research calques that Thai doctors never write
BANNED_THAI_CALQUES = {
    "ธรณีความเจ็บปวด": "ใช้ 'ระดับความไวต่อแรงกดเจ็บ (pressure pain threshold: PPT)' หรือ 'ค่า PPT'",
    "ปกปิดสองทาง": "ในชื่อเรื่องใช้ 'แบบปกปิดทั้งสองฝ่าย (Double-Blind)' ในเนื้อหาใช้ทับศัพท์ 'double-blind'",
    "สุ่มขนาน": "ใช้ 'แบบสุ่มเปรียบเทียบสองกลุ่มคู่ขนาน (parallel-group randomized)' หรือ 'parallel-group RCT'",
    "ผู้ประเมินปกปิด": "ใช้ 'ผู้ประเมินผลที่ไม่ทราบกลุ่มการรักษา (blinded assessor)' หรือ 'ผู้ประเมินผล (blinded assessor)'",
    "ผู้ประเมินที่ถูกปกปิด": "ใช้ 'ผู้ประเมินผลที่ไม่ทราบกลุ่มการรักษา (blinded assessor)' หรือ 'ผู้ประเมินผล (blinded assessor)'",
    "ดัชนีการปกปิด": "ใช้ทับศัพท์ 'ค่า Bang\\'s blinding index'",
    "ผลค้างข้ามรอบ": "ใช้ 'ผลตกค้างจากการรักษารอบก่อน (carryover effect)' หรือทับศัพท์ 'carryover effect'",
    "จุดกดเจ็บที่ทำงานอยู่": "ใช้ 'จุดกดเจ็บชนิดแสดงอาการ (active MTrP)' หรือ 'จุดกดเจ็บ active MTrP'",
    "ความบกพร่องของคอ": "ใช้ 'คะแนนความสามารถในการใช้งานคอ (Neck Disability Index: NDI)' หรือ 'คะแนน NDI'",
    "ท่ายืดเกร็ง": "ใช้ 'ท่ายืดกล้ามเนื้อบ่าเบาๆ (gentle stretch)'",
    "เชิงอัตวิสัย": "ใช้ 'ค่าที่ขึ้นกับการรับรู้ความรู้สึกของผู้ป่วย (subjective outcome)'",
    "พุทธิปัญญา": "ใช้ 'ภาวะสับสน ความจำเสื่อม หรือบกพร่องทางการรับรู้และการสื่อสาร'",
    "ความคงทนของผลลัพธ์": "ใช้ 'ความสอดคล้องของผลลัพธ์ (sensitivity analysis)'",
    "ได้พิสูจน์แล้วว่า": "กริยา Over-claim: ใช้ 'รายงานว่า', 'พบว่า', หรือ 'แสดงให้เห็นว่า'",
    "พิสูจน์แล้วว่า": "กริยา Over-claim: ใช้ 'รายงานว่า', 'พบว่า', หรือ 'แสดงให้เห็นว่า'",
    "พิสูจน์ซ้ำ": "กริยา Over-claim: ใช้ 'รายงานผลสอดคล้องกันว่า' หรือ 'ยืนยันตรงกันว่า'",
    "ปริศนาจากงาน": "สำนวน AI hype: ใช้ 'ประเด็นที่ยังไม่มีข้อสรุปชัดเจนจากการศึกษาของ...'",
    "ตอบคำถามที่ค้างคา": "สำนวน AI hype: ใช้ 'เพื่ออธิบายกลไกที่ยังไม่มีข้อสรุปชัดเจน...'",
    "อนุรักษนิยม": "คำแปลผิดบริบทจาก conservative estimate (การเมือง): ใช้ 'แบบรัดกุม (conservative)' หรือทับศัพท์ 'conservative'",
    "ระยะซักล้าง": "คำแปลตรงตัวจาก washout period: ใช้ 'ระยะพักล้างฤทธิ์ (washout period)' หรือทับศัพท์ 'washout period'",
    "ระยะชะล้าง": "คำแปลตรงตัวจาก washout period: ใช้ 'ระยะพักล้างฤทธิ์ (washout period)' หรือทับศัพท์ 'washout period'",
    "ผลกระทบเพดาน": "คำแปลตรงตัวจาก ceiling effect: ใช้ทับศัพท์ 'ceiling effect'",
    "ผลกระทบพื้น": "คำแปลตรงตัวจาก floor effect: ใช้ทับศัพท์ 'floor effect'",
    "ตัวแปรสับสน": "คำแปลตรงตัวจาก confounding variable: ใช้ 'ตัวแปรกวน (confounder)'",
    "ไร้เดียงสา": "คำแปลผิดบริบทจาก treatment-naive: ใช้ 'ผู้ป่วยที่ยังไม่เคยได้รับการรักษามาก่อน (treatment-naive)'",
    "ความตั้งใจที่จะรักษา": "คำแปลตรงตัวจาก intention-to-treat: ใช้ทับศัพท์ 'การวิเคราะห์แบบ intention-to-treat (ITT)'",
    "การกระตุ้นจอมปลอม": "คำแปลตรงตัวจาก sham stimulation: ใช้ 'การกระตุ้นหลอก (sham stimulation)' หรือ 'กลุ่ม sham'",
    "เปรียบเทียบ 2 แขน": "คำแปลตรงตัวจาก 2-arm comparison: ใช้ 'เปรียบเทียบ 2 กลุ่มการรักษา (2-arm)'",
    "2 แขนคู่ขนาน": "คำแปลตรงตัวจาก 2 parallel arms: ใช้ '2 กลุ่มคู่ขนาน (2-arm parallel)'",
    "แขน Sham": "คำแปลตรงตัวจาก Sham arm: ใช้ 'กลุ่มควบคุมหลอก (Sham)' หรือ 'กลุ่ม Sham'",
    "แขนทดลอง": "คำแปลตรงตัวจาก intervention/experimental arm: ใช้ 'กลุ่มทดลอง' หรือ 'กลุ่มแทรกแซง'",
}

SI_UNSPACED_RE = re.compile(r"\b(\d+(?:\.\d+)?)(mmHg|mg|mcg|mL|cm|mm|kg|ms|Hz)\b")
P_VAL_RE = re.compile(r"\bp\s*([=<>≤≥])\s*(0?\.\d+|1\.0+)\b", re.I)
SUBGROUP_SUM_RE = re.compile(
    r"\bN\s*=\s*(\d+)\s*\([^)]*?=\s*(\d+)\s*,\s*[^)]*?=\s*(\d+)\)", re.I
)
PCT_CHECK_RE = re.compile(r"\b(\d+)\s*/\s*(\d+)\s*\(\s*(\d+(?:\.\d+)?)\s*%\s*\)")
EPV_RE = re.compile(r"\bEPV\s*[=:<≤≥]\s*(\d+(?:\.\d+)?)\b", re.I)
REF_HEADER_RE = re.compile(r"^#{1,3}\s+(?:References|Bibliography|เอกสารอ้างอิง)\b", re.I | re.M)
REF_LINE_RE = re.compile(r"^\s*(?:\[(\d+)\]|(\d+)\.)\s+")
INLINE_BRACKET_RE = re.compile(r"\[(\d+(?:\s*[-,]\s*\d+)*)\]")


def sha256_file(path: str) -> str:
    """Return hex SHA-256 digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_code_blocks(text: str) -> str:
    """Remove fenced code blocks and inline code spans before prose/math checks."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    return re.sub(r"`[^`\n]+`", "", text)


def check_pillar1_citations(text: str, doc_path: str, run_live: bool, library: str = None) -> Tuple[List[str], int]:
    """Check forward/reverse inline-to-bibliography alignment."""
    findings: List[str] = []
    m = REF_HEADER_RE.search(text)
    body = text[: m.start()] if m else text
    ref_block = text[m.start() :] if m else ""
    bib_nums = set()
    for line in ref_block.splitlines():
        rm = REF_LINE_RE.match(line)
        if rm:
            bib_nums.add(int(rm.group(1) or rm.group(2)))

    cited_nums = set()
    for bm in INLINE_BRACKET_RE.finditer(body):
        for part in bm.group(1).split(","):
            part = part.strip()
            if "-" in part:
                a, b = part.split("-", 1)
                if a.strip().isdigit() and b.strip().isdigit():
                    cited_nums.update(range(int(a.strip()), int(b.strip()) + 1))
            elif part.isdigit():
                cited_nums.add(int(part))

    missing = sorted(cited_nums - bib_nums)
    unused = sorted(bib_nums - cited_nums)
    if missing:
        findings.append(f"Orphan in-text citations missing from References: `{missing}`")
    if unused:
        findings.append(f"Uncited entries in References: `{unused}`")

    if run_live and bib_nums:
        engine = os.path.join(os.path.dirname(__file__), "citation_engine.py")
        cmd = [sys.executable, engine, "audit-2pass", doc_path]
        if library:
            cmd.extend(["--library", library])
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode != 0:
            findings.append(f"citation_engine.py exited with error: {res.stderr.strip()}")
        else:
            findings.append(f"Live 2-pass citation audit ran: `{res.stdout.strip()}`")

    deduction = 10 * len(missing) + 5 * len(unused)
    return findings, deduction


def check_pillar2_stats(text: str, sot_path: str = None) -> Tuple[List[str], int]:
    """Validate p-values, subgroup sums, percentage arithmetic, and EPV >= 10."""
    findings: List[str] = []
    deduction = 0

    for pm in P_VAL_RE.finditer(text):
        op, raw = pm.group(1), pm.group(2)
        val = float(raw)
        if op == "=" and val == 0.0:
            findings.append(f"Invalid exact zero p-value `{pm.group(0)}` -> use `p < 0.001`.")
            deduction += 8
        elif val > 1.0 or val < 0.0:
            findings.append(f"Out-of-bounds p-value `{pm.group(0)}`.")
            deduction += 10

    for sm in SUBGROUP_SUM_RE.finditer(text):
        total, a, b = int(sm.group(1)), int(sm.group(2)), int(sm.group(3))
        if a + b != total:
            findings.append(f"Subgroup arithmetic mismatch: `{sm.group(0)}` ({a} + {b} != {total}).")
            deduction += 10

    for pcm in PCT_CHECK_RE.finditer(text):
        k, n, pct = int(pcm.group(1)), int(pcm.group(2)), float(pcm.group(3))
        if n > 0:
            expected = (k / n) * 100.0
            if abs(expected - pct) > 0.6:
                findings.append(
                    f"Percentage mismatch `{pcm.group(0)}` (expected ~{expected:.1f}%)."
                )
                deduction += 5

    for em in EPV_RE.finditer(text):
        epv = float(em.group(1))
        if epv < 10.0:
            findings.append(f"Peduzzi EPV warning: `{em.group(0)}` (< 10 events per variable).")
            deduction += 8

    if sot_path and os.path.exists(sot_path):
        with open(sot_path, "r", encoding="utf-8") as sf:
            sot_txt = sf.read()
        sot_n = re.findall(r"\bN\s*=\s*(\d+)\b", sot_txt)
        doc_n = re.findall(r"\bN\s*=\s*(\d+)\b", text)
        if sot_n and doc_n and sot_n[0] not in doc_n:
            findings.append(
                f"SOT sample size `N = {sot_n[0]}` not matched in draft (`{doc_n[:3]}`)."
            )
            deduction += 10

    return findings, deduction


def check_pillar3_latex_si(prose: str) -> Tuple[List[str], int]:
    """Check balanced LaTeX delimiters and spaced SI units."""
    findings: List[str] = []
    deduction = 0

    cleaned = prose.replace(r"\$", "")
    display_count = len(re.findall(r"\$\$", cleaned))
    if display_count % 2 != 0:
        findings.append(f"Unbalanced display math `$$` delimiters (count = {display_count}).")
        deduction += 10

    no_display = re.sub(r"\$\$.*?\$\$", "", cleaned, flags=re.S)
    inline_count = len(re.findall(r"\$", no_display))
    if inline_count % 2 != 0:
        findings.append(f"Unbalanced inline math `$` delimiters (count = {inline_count}).")
        deduction += 10

    si_hits = [m.group(0) for m in SI_UNSPACED_RE.finditer(prose)]
    if si_hits:
        findings.append(f"Unspaced SI units found (add space): `{sorted(set(si_hits))}`")
        deduction += min(15, 3 * len(set(si_hits)))

    return findings, deduction


def check_pillar4_antislop(prose: str) -> Tuple[List[str], int]:
    """Flag banned AI lexicon and overly long (>45 word) sentences."""
    findings: List[str] = []
    deduction = 0
    lower = prose.lower()

    hits = [w for w in BANNED_WORDS if re.search(r"\b" + re.escape(w) + r"\b", lower)]
    if hits:
        findings.append(f"Banned AI lexicon detected: `{hits}`")
        deduction += min(20, 4 * len(hits))

    thai_calque_hits = [
        f"{term} ({hint})" for term, hint in BANNED_THAI_CALQUES.items() if term in prose
    ]
    if thai_calque_hits:
        findings.append(f"Banned AI-translated Thai medical calques detected: `{thai_calque_hits}`")
        deduction += min(25, 5 * len(thai_calque_hits))

    sentences = re.split(r"(?<=[.!?])\s+", prose)
    long_sents = [s for s in sentences if len(s.split()) > 45 and not s.lstrip().startswith("|")]
    if long_sents:
        findings.append(f"Clause-stacked sentences (>45 words): {len(long_sents)} found")
        deduction += min(10, 2 * len(long_sents))

    return findings, deduction


def grade_from_score(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    return "F"


def main() -> int:
    parser = argparse.ArgumentParser(description="4-Pillar Deliverable Auditor")
    parser.add_argument("doc", help="Markdown draft path")
    parser.add_argument("--sot", help="Optional SOT.md path for cohort triangulation")
    parser.add_argument("--library", help="Optional Literature_Library PDF directory")
    parser.add_argument("--skip-net", action="store_true", help="Skip live PubMed/CrossRef API calls")
    parser.add_argument("--out", help="Output report path")
    args = parser.parse_args()

    doc_path = os.path.abspath(args.doc)
    before_hash = sha256_file(doc_path)
    with open(doc_path, "r", encoding="utf-8") as f:
        text = f.read()

    prose = strip_code_blocks(text)
    p1, d1 = check_pillar1_citations(text, doc_path, not args.skip_net, args.library)
    p2, d2 = check_pillar2_stats(prose, args.sot)
    p3, d3 = check_pillar3_latex_si(prose)
    p4, d4 = check_pillar4_antislop(prose)

    score = max(0, 100 - (d1 + d2 + d3 + d4))
    grade = grade_from_score(score)

    lines = [
        "# 4-Pillar Deliverable Audit Report",
        "",
        f"- **Target**: `{doc_path}`",
        f"- **SHA-256 (Invariance Proof)**: `{before_hash}`",
        f"- **Composite Score**: **{score}/100 (Grade {grade})**",
        "",
        "## Pillar 1: Citation & Claim Grounding",
        *(f"- {x}" for x in (p1 or ["PASS — Zero orphan/uncited references."])),
        "",
        "## Pillar 2: Statistical & SOT Triangulation",
        *(f"- {x}" for x in (p2 or ["PASS — No p-value, subgroup arithmetic, percentage, or EPV issues."])),
        "",
        "## Pillar 3: LaTeX & SI Unit Invariance",
        *(f"- {x}" for x in (p3 or ["PASS — Balanced math delimiters and spaced SI units."])),
        "",
        "## Pillar 4: Anti-Slop & Epistemic Rigor",
        *(f"- {x}" for x in (p4 or ["PASS — Zero banned AI lexicon or clause-stacked (>45 word) sentences."])),
    ]

    out_path = args.out or os.path.join(os.path.dirname(doc_path), "deliverable_audit_report.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    after_hash = sha256_file(doc_path)
    assert before_hash == after_hash, "Source file hash changed during read-only audit!"
    print(f"Audit complete: {score}/100 (Grade {grade}) -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
