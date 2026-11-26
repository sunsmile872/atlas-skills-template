#!/usr/bin/env python3
"""
Automated Verbatim, Citation Parity & Hygiene Verifier (Phase 3/4 Prototype)
Checks compiled .pptx slides (text frames, tables, and charts) against Stage 1 evidence_bundle.json:
  1. Verbatim numeric fidelity (no unverified/fabricated numbers)
  2. Superscript <-> Ref: Footer set equality (zero phantom [k] or orphan superscripts)
  3. Deck <-> References slide parity (all cited books listed, zero unused books)
  4. Anti-digit-adjacency (\d\.? before superscript) & unexpanded [[k]] token guard
  5. Profile-scoped banned terms & Claim-ID registry validation (when present)
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import re
import sys
from pptx import Presentation
from pptx.oxml.ns import qn

UNIVERSAL_BANNED = [
    (r"\blandmark\b", "Banned word 'Landmark'"),
    (r"\bworkhorse\b", "Banned slang 'Workhorse'"),
    (r"\baxiom\b", "Banned word 'Axiom'"),
    (r"\bcrucial\b|\bparamount\b|\bdelve\b|\btestament\b|\bgame[- ]changer\b", "Banned AI hype lexicon"),
    (r"\blandscape\b|\bnotably\b", "Banned AI boilerplate"),
    (r"—", "Banned em-dash '—' (use colon, comma, parentheses, or hyphen)"),
    (r"ทั้ง\s*\d+\s*แขน|แขน\s*Sham|แขนทดลอง", "Banned Thai AI calque 'แขน' (use 'กลุ่ม')"),
    (r"เชิงวัตถุวิสัย|เชิงอัตวิสัย", "Banned Thai AI calque"),
    (r"ผู้ประเมินปกปิด|ปกปิดสองทาง|ธรณีความเจ็บปวด", "Banned Thai AI calque"),
    (r"อนุรักษนิยม", "Banned Thai AI calque 'อนุรักษนิยม'"),
]

PMR_BANNED = [
    (r"กฎเหล็ก|ท่องให้ขึ้นใจ", "Banned dramatic/condescending Thai phrase"),
    (r"ลูกสะบ้า|กระดูกหน้าแข้ง|กระดูกสะบัก|ชีวกลศาสตร์|ระบาดวิทยา|สาเหตุการเกิดโรค", "Use English technical term instead of awkward Thai translation"),
    (r"ข้อห้าม(?!\s*ของ)", "Use 'contraindication' in natural medical speech"),
]

AMPUTATION_BANNED = [
    (r"สูญเสียรยางค์|การตัดรยางค์|ผู้พิการแขนขาขาด|คนไข้ตัดขา", "Use 'Amputation' / 'Amputee'"),
    (r"ตอขา|\bstumps?\b|เบ้าเทียม|ข้างที่ตัด", "Use 'residual limb' / 'Prosthetic socket' / 'Prosthetic side'"),
    (r"\bPLP\b|\bRLP\b", "Spell out Phantom Limb Pain / Residual Limb Pain"),
]

ABBREV_ERRORS = [
    (r"\bNS\b", "Ambiguous abbreviation 'NS' (clashes with Normal Saline; use 'not significant' or '(not sig.)')"),
    (r"\blit\b", "Informal abbreviation 'lit' (use 'range' or 'published cohorts')"),
    (r"\bSQ\b", "Use 'Subcutaneous' / 'Subcut.' instead of 'SQ'"),
    (r"\bmeta\b(?!-analys|-analytic)", "Standalone 'meta' (use 'meta-analysis')"),
    (r"\bq\d+h\b", "Use 'every N h' / 'every N hours' instead of prescription shorthand 'q2h'"),
]

ABBREV_WARNINGS = [
    (r"\bUS\b", "Consider spelling out 'Ultrasound' instead of 'US'"),
    (r"\b\d+-ga\b|\b\d+/\d+-in\b", "Consider spelling out '-gauge' / '-inch'"),
    (r"\bavg\b|\bwks\b|\b1st[- ]AM\b", "Consider expanding compact shorthand ('average', 'weeks', 'first-morning')"),
]

VISUAL_ARCHETYPES = {
    "kpi_hero_plus_chart",
    "kpi_hero_plus_dual_charts",
    "bento_epidemiology_2col",
    "top_figure_plus_strip",
    "split_grading_table_card",
    "split_figure_card",
    "quadrant_2x2_differential",
    "quadrant_2x2_complications",
    "bento_2col_care",
    "chart_plus_comparison_cards",
    "dual_chart_plus_comparison_cards",
    "comparison_2col_plus_stats",
    "process_continuum_4step",
    "dark_bento_takehome",
}

NUM_RE = re.compile(r"\d+(?:\.\d+)?%?")
RAW_TOKEN_RE = re.compile(r"\[\[\d+(?:,\s*\d+)*\]\]")
UNICODE_SUP = {
    "\u00b9": 1,
    "\u00b2": 2,
    "\u00b3": 3,
    "\u2074": 4,
    "\u2075": 5,
    "\u2076": 6,
    "\u2077": 7,
    "\u2078": 8,
    "\u2079": 9,
}
UNICODE_SUP_CHARS = "".join(UNICODE_SUP.keys())


def _is_xml_superscript(run) -> bool:
    rPr = run._r.find(qn("a:rPr"))
    if rPr is None:
        return False
    baseline = rPr.get("baseline")
    if baseline is None:
        return False
    try:
        return int(baseline) > 0
    except ValueError:
        return False


def _scan_text_runs(paragraphs, s_num: int, is_body: bool) -> tuple[set[int], list[str], list[str]]:
    """Extracts superscript IDs, digit-adjacency errors, and raw token leaks from paragraphs."""
    refs: set[int] = set()
    adj_errors: list[str] = []
    token_errors: list[str] = []

    for p in paragraphs:
        p_text = p.text or ""
        if RAW_TOKEN_RE.search(p_text):
            token_errors.append(f"Slide {s_num:02d}: Unexpanded superscript token in '{p_text.strip()}'")

        if not is_body:
            continue

        stripped = p_text.strip()
        if stripped.startswith("Source:"):
            for m in re.findall(r"\[(\d+)\]", stripped):
                refs.add(int(m))

        prev_text = ""
        for run in p.runs:
            r_txt = run.text or ""
            if not r_txt:
                continue
            if _is_xml_superscript(run):
                if re.search(r"\d\.?$", prev_text):
                    adj_errors.append(
                        f"Slide {s_num:02d}: Digit-adjacent superscript '{prev_text[-12:]}{r_txt}' (anchor on a word instead)"
                    )
                for d in re.findall(r"\d+", r_txt):
                    refs.add(int(d))
            else:
                for idx_c, ch in enumerate(r_txt):
                    if ch in UNICODE_SUP:
                        before = prev_text + r_txt[:idx_c]
                        if re.search(r"\d\.?$", before):
                            adj_errors.append(
                                f"Slide {s_num:02d}: Digit-adjacent Unicode superscript '{before[-12:]}{ch}'"
                            )
                        refs.add(UNICODE_SUP[ch])
            prev_text += r_txt

    return refs, adj_errors, token_errors


def inspect_slide(slide, s_num: int) -> dict:
    """Extracts content/footer text, citation superscripts, figure sources, and hygiene faults."""
    content: list[str] = []
    footer: list[str] = []
    body_refs: set[int] = set()
    adj_errors: list[str] = []
    token_errors: list[str] = []

    for sh in slide.shapes:
        top_in = sh.top / 914400
        if sh.has_text_frame:
            txt = sh.text_frame.text.strip()
            is_footer = top_in >= 6.95
            if txt:
                (footer if is_footer else content).append(txt)
            r_ids, r_adj, r_tok = _scan_text_runs(sh.text_frame.paragraphs, s_num, is_body=not is_footer)
            body_refs.update(r_ids)
            adj_errors.extend(r_adj)
            token_errors.extend(r_tok)

        if sh.has_table:
            for row in sh.table.rows:
                for cell in row.cells:
                    t = cell.text.strip()
                    if t:
                        content.append(t)
                    r_ids, r_adj, r_tok = _scan_text_runs(cell.text_frame.paragraphs, s_num, is_body=True)
                    body_refs.update(r_ids)
                    adj_errors.extend(r_adj)
                    token_errors.extend(r_tok)

        if sh.has_chart:
            chart = sh.chart
            if chart.has_title and chart.chart_title.has_text_frame:
                ct_txt = chart.chart_title.text_frame.text.strip()
                content.append(ct_txt)
                r_ids, r_adj, r_tok = _scan_text_runs(
                    chart.chart_title.text_frame.paragraphs, s_num, is_body=True
                )
                body_refs.update(r_ids)
                adj_errors.extend(r_adj)
                token_errors.extend(r_tok)
            for plot in chart.plots:
                for cat in plot.categories:
                    cat_s = str(cat)
                    content.append(cat_s)
                    for idx_c, ch in enumerate(cat_s):
                        if ch in UNICODE_SUP:
                            before = cat_s[:idx_c]
                            if re.search(r"\d\.?$", before):
                                adj_errors.append(
                                    f"Slide {s_num:02d}: Digit-adjacent chart label superscript '{before[-12:]}{ch}'"
                                )
                            body_refs.add(UNICODE_SUP[ch])
                for ser in plot.series:
                    content.append(str(ser.name))
                    is_pct = False
                    try:
                        dlbls = ser._element.find(qn("c:dLbls"))
                        if dlbls is None:
                            dlbls = plot._element.find(qn("c:dLbls"))
                        if dlbls is not None:
                            nf = dlbls.find(qn("c:numFmt"))
                            if nf is not None and "%" in (nf.get("formatCode") or ""):
                                is_pct = True
                    except Exception:
                        pass
                    for v in ser.values:
                        if v is not None:
                            fv = float(v)
                            if is_pct and 0.0 <= fv <= 1.0:
                                pct = round(fv * 100, 1)
                                content.append(f"{int(pct)}%" if pct.is_integer() else f"{pct}%")
                            else:
                                content.append(str(int(fv)) if fv.is_integer() else str(v))

    return {
        "content": content,
        "footer": footer,
        "body_refs": body_refs,
        "adj_errors": adj_errors,
        "token_errors": token_errors,
    }


def allowed_numbers_from_slide_spec(spec_slide: dict) -> set[str]:
    """Collects all numbers explicitly present in the locked Stage 1 slide spec."""
    blob = json.dumps(spec_slide, ensure_ascii=False)
    nums: set[str] = set()
    for m in NUM_RE.findall(blob):
        nums.add(m)
        nums.add(m.rstrip("%"))
    for n in spec_slide.get("allowed_label_numbers", []):
        nums.add(str(n))
        nums.add(str(n).rstrip("%"))
    return nums


def validate_claim_registry(evidence: dict) -> list[str]:
    """Validates atomic Claim-ID registry & slide bindings when schema v3_claim_id is used."""
    issues: list[str] = []
    registry = evidence.get("claim_registry")
    if not registry:
        return issues

    if not isinstance(registry, dict):
        return ["Schema error: 'claim_registry' must be a dict mapping claim_id -> claim object"]

    for cid, cobj in registry.items():
        for req_key in ("book_id", "page", "quote"):
            if not cobj.get(req_key):
                issues.append(f"Claim '{cid}': Missing required field '{req_key}' in claim_registry")

    for s_spec in evidence.get("slides", []):
        sid = s_spec.get("slide_id", "?")
        for used_cid in s_spec.get("claim_ids", []):
            if used_cid not in registry:
                issues.append(f"Slide {sid}: References unknown claim_id '{used_cid}'")
    return issues


def _parse_pptx_note(raw: str) -> dict:
    raw = (raw or "").strip()
    m_hdr = re.match(r"^\[([^\]]+)\]\s*(.+?)\n\n(.*)$", raw, re.DOTALL)
    if not m_hdr:
        return {"time": "", "title": "", "script": raw, "trap": "", "trans": ""}
    t_str, title, body = m_hdr.group(1).strip(), m_hdr.group(2).strip(), m_hdr.group(3)
    if "【บทพูดบรรยาย】:" in body:
        parts = body.split("【บทพูดบรรยาย】:", 1)[1]
        scr, rest = parts.split("【Staff Q&A Trap】:", 1) if "【Staff Q&A Trap】:" in parts else (parts, "")
        trp, trn = rest.split("【Transition】:", 1) if "【Transition】:" in rest else (rest, "")
        return {"time": t_str, "title": title, "script": scr.strip(), "trap": trp.strip(), "trans": trn.strip()}
    if "[Spoken Script]:" in body:
        parts = body.split("[Spoken Script]:", 1)[1]
        scr, rest = parts.split("[Staff Q&A Defense]:", 1) if "[Staff Q&A Defense]:" in parts else (parts, "")
        trp, trn = rest.split("[Transition]:", 1) if "[Transition]:" in rest else (rest, "")
        return {"time": t_str, "title": title, "script": scr.strip(), "trap": trp.strip(), "trans": trn.strip()}
    return {"time": t_str, "title": title, "script": body.strip(), "trap": "", "trans": ""}


def _parse_md_notes(md_path: str) -> dict[int, dict]:
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()
    blocks = re.split(r"^###\s+Slide\s+(\d+)\s*[:|]\s*", text, flags=re.MULTILINE)
    out: dict[int, dict] = {}
    for i in range(1, len(blocks), 2):
        s_num = int(blocks[i])
        blk = blocks[i + 1]
        lines = blk.splitlines()
        hdr_line = lines[0].strip() if lines else ""
        m_t = re.match(r"^(.+?)\s*\(([^)]+)\)\s*$", hdr_line)
        title = m_t.group(1).strip() if m_t else hdr_line
        t_str = m_t.group(2).strip() if m_t else ""
        rest = "\n".join(lines[1:])

        m_scr = re.search(r"\*\*(?:บทพูดบรรยาย|Spoken Script|บทพูดปิดท้าย|Spoken Guidepost)\*\*:\s*\n((?:>.*\n?)+)", rest)
        script = ""
        if m_scr:
            script = "\n".join(re.sub(r"^>\s?", "", ln) for ln in m_scr.group(1).splitlines()).strip()

        m_trp = re.search(r"\*\*(?:Staff Q&A Defense Trap|Staff Q&A Defense)\*\*:\s*\n```[^\n]*\n(.*?)\n```", rest, re.DOTALL)
        trap = m_trp.group(1).strip() if m_trp else ""

        m_trn = re.search(r"\*Transition\*:\s*`([^`]*)`", rest)
        trans = m_trn.group(1).strip() if m_trn else ""

        out[s_num] = {"time": t_str, "title": title, "script": script, "trap": trap, "trans": trans}
    return out


def _load_notes_modules_dict(modules_dir: str) -> dict[int, dict]:
    notes_data: dict[int, dict] = {}
    for py_file in sorted(glob.glob(f"{modules_dir.rstrip('/')}/mod*.py")):
        spec = importlib.util.spec_from_file_location(py_file, py_file)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "DATA"):
                notes_data.update(mod.DATA)
    return notes_data


def _parse_end_minutes(time_str: str) -> float | None:
    m = re.search(r"(\d+):(\d{2})\s*-\s*(\d+):(\d{2})", time_str or "")
    if not m:
        return None
    return int(m.group(3)) + int(m.group(4)) / 60.0


def main():
    parser = argparse.ArgumentParser(description="Verify PPTX verbatim fidelity, citation parity, notes & clarity hygiene")
    parser.add_argument("--evidence", required=True, help="Path to evidence_bundle.json")
    parser.add_argument("--pptx", required=True, help="Path to compiled .pptx")
    parser.add_argument("--md", default="", help="Optional PRESENTER_NOTES_MASTER.md for 1:1 notes & script hygiene checks")
    parser.add_argument("--notes-dir", default="", help="Optional notes_data_modules/ dir for mod*.py parity check")
    parser.add_argument(
        "--profile",
        default="pmr_board",
        choices=["universal", "pmr_board", "journal_club", "amputation"],
    )
    parser.add_argument(
        "--skip-parity",
        action="store_true",
        help="Skip superscript <-> Ref footer parity checks (for legacy v1 decks without superscripts)",
    )
    parser.add_argument(
        "--allow-legacy-shorthand",
        action="store_true",
        help="Downgrade ambiguous shorthand & monotony strict errors to warnings for legacy snapshots",
    )
    parser.add_argument(
        "--strict-warnings",
        action="store_true",
        help="Treat hygiene warnings (e.g. Double thank-you, timing mismatch) as release-blocking errors",
    )
    args = parser.parse_args()

    with open(args.evidence, "r", encoding="utf-8") as f:
        evidence = json.load(f)

    prs = Presentation(args.pptx)
    spec_slides = evidence.get("slides", [])
    issues: list[str] = []
    warnings: list[str] = []

    issues.extend(validate_claim_registry(evidence))

    if len(prs.slides) != len(spec_slides):
        issues.append(f"Slide count mismatch: PPTX has {len(prs.slides)} vs evidence_bundle {len(spec_slides)}")

    patterns = list(UNIVERSAL_BANNED)
    if args.profile in ("pmr_board", "amputation"):
        patterns.extend(PMR_BANNED)
    if args.profile == "amputation":
        patterns.extend(AMPUTATION_BANNED)

    archetypes = [s.get("archetype", "unknown") for s in spec_slides]
    for i in range(2, len(archetypes)):
        if archetypes[i] == archetypes[i - 1] == archetypes[i - 2]:
            msg = f"Layout monotony: Slides {i-1}..{i+1} use '{archetypes[i]}' 3 times consecutively"
            (warnings if args.allow_legacy_shorthand else issues).append(msg)

    # Alternating figure_side check on adjacent split_figure_card slides
    for i in range(1, len(spec_slides)):
        prev_s, cur_s = spec_slides[i - 1], spec_slides[i]
        if prev_s.get("archetype") == "split_figure_card" and cur_s.get("archetype") == "split_figure_card":
            ps, cs = prev_s.get("figure_side"), cur_s.get("figure_side")
            if ps and cs and ps == cs:
                warnings.append(f"Layout symmetry: Slides {i} and {i+1} repeat split_figure_card figure_side='{cs}'")

    # Visual Diversity check (>= 50% body slides use visual/structured archetypes)
    body_specs = [s for s in spec_slides if s.get("archetype") not in ("dark_hero_title", "references_slide")]
    if len(body_specs) >= 6:
        vis_count = sum(1 for s in body_specs if s.get("archetype") in VISUAL_ARCHETYPES)
        ratio = vis_count / len(body_specs)
        if ratio < 0.50:
            warnings.append(f"Visual-First ratio low: {vis_count}/{len(body_specs)} ({ratio:.0%}) < 50% visual/structured archetypes")

    inspected = [inspect_slide(slide, idx + 1) for idx, slide in enumerate(prs.slides)]
    has_deck_superscripts = any(bool(item["body_refs"]) for item in inspected)

    all_deck_refs: set[int] = set()
    ref_slide_ids: set[int] | None = None
    ctr_expanded_yet = False

    for idx, item in enumerate(inspected):
        s_num = idx + 1
        s_spec = spec_slides[idx] if idx < len(spec_slides) else {}
        arch = s_spec.get("archetype", "")
        full_content = "\n".join(item["content"])
        full_footer = "\n".join(item["footer"])
        combined_text = full_content + "\n" + full_footer

        if re.search(r"carpal tunnel release", full_content, flags=re.IGNORECASE):
            ctr_expanded_yet = True

        # 1. Bottom-right slide number
        expected_num = f"{s_num:02d} / {len(prs.slides):02d}"
        if expected_num not in full_footer and f"{s_num}/{len(prs.slides)}" not in full_footer.replace(" ", ""):
            issues.append(f"Slide {s_num:02d}: Missing bottom-right slide number '{expected_num}' in footer")

        # 2. Ref: footnote check
        if s_num > 1 and s_spec.get("footnote") and "Ref:" not in full_footer:
            issues.append(f"Slide {s_num:02d}: Missing 'Ref:' footnote in footer")

        # 3. Banned patterns
        for pat, msg in patterns:
            if re.search(pat, combined_text, flags=re.IGNORECASE):
                issues.append(f"Slide {s_num:02d}: Banned pattern [{msg}]")

        # 3b. Ambiguous Abbreviation Linter (v2.8 clarity standard)
        for pat, msg in ABBREV_ERRORS:
            if re.search(pat, full_content):
                target_list = warnings if args.allow_legacy_shorthand else issues
                target_list.append(f"Slide {s_num:02d}: {msg}")
        if re.search(r"\bCTR\b", full_content) and not ctr_expanded_yet:
            target_list = warnings if args.allow_legacy_shorthand else issues
            target_list.append(f"Slide {s_num:02d}: Unexpanded 'CTR' before 'carpal tunnel release' is defined")
        for pat, msg in ABBREV_WARNINGS:
            if re.search(pat, full_content):
                warnings.append(f"Slide {s_num:02d}: {msg}")

        # 4. Unexpanded tokens & digit-adjacent superscripts
        issues.extend(item["token_errors"])
        issues.extend(item["adj_errors"])

        # 5. Numeric verbatim fidelity against Stage 1 spec
        if s_spec:
            allowed = allowed_numbers_from_slide_spec(s_spec)
            for fn in NUM_RE.findall(full_content):
                base = fn.rstrip("%")
                if fn not in allowed and base not in allowed:
                    issues.append(f"Slide {s_num:02d}: Unverified number '{fn}' not found in Stage 1 evidence spec")

        # 6. Superscript <-> Ref: footer parity (content slides)
        footer_refs = {int(m) for m in re.findall(r"\[(\d+)\]", full_footer)}
        if arch == "references_slide":
            ref_slide_ids = set()
            for line in item["content"]:
                for m in re.findall(r"^\[(\d+)\]$", line.strip()):
                    ref_slide_ids.add(int(m))
        elif not args.skip_parity and s_num > 1 and (item["body_refs"] or (has_deck_superscripts and footer_refs)):
            phantom = sorted(footer_refs - item["body_refs"])
            orphan = sorted(item["body_refs"] - footer_refs)
            if phantom:
                issues.append(
                    f"Slide {s_num:02d}: Phantom Ref footer citation(s) {phantom} not used by any superscript/source on slide"
                )
            if orphan:
                issues.append(
                    f"Slide {s_num:02d}: Orphaned superscript/source {orphan} missing from Ref: footer"
                )
            all_deck_refs.update(item["body_refs"])
            all_deck_refs.update(footer_refs)

    # 7. Deck <-> References Slide parity
    if not args.skip_parity and ref_slide_ids is not None and has_deck_superscripts:
        unused_cards = sorted(ref_slide_ids - all_deck_refs)
        missing_cards = sorted(all_deck_refs - ref_slide_ids)
        if unused_cards:
            issues.append(f"References slide lists unused textbook ID(s): {unused_cards}")
        if missing_cards:
            issues.append(f"References slide is missing textbook ID(s) cited in deck: {missing_cards}")

    # 8. Speaker Notes 1:1 Parity, Script Hygiene & Timing Sync (when --md or --notes-dir supplied)
    if args.md or args.notes_dir:
        md_map = _parse_md_notes(args.md) if args.md else {}
        mod_map = _load_notes_modules_dict(args.notes_dir) if args.notes_dir else {}
        pptx_notes = {
            idx + 1: _parse_pptx_note(s.notes_slide.notes_text_frame.text if s.has_notes_slide else "")
            for idx, s in enumerate(prs.slides)
        }
        scripts_by_slide: dict[int, str] = {}
        last_end_min: float | None = None

        for s_num in range(1, len(prs.slides) + 1):
            pn = pptx_notes[s_num]
            if not pn["script"]:
                issues.append(f"Notes Slide {s_num:02d}: Missing PPTX Speaker Notes")
                continue
            scripts_by_slide[s_num] = pn["script"]
            end_m = _parse_end_minutes(pn["time"])
            if end_m is not None:
                last_end_min = end_m

            if md_map and s_num in md_map:
                mn = md_map[s_num]
                for fld in ("script", "trap", "trans"):
                    if mn[fld] and pn[fld] != mn[fld]:
                        issues.append(f"Notes Slide {s_num:02d}: PPTX vs Markdown '{fld}' parity mismatch")
            if mod_map and s_num in mod_map:
                dn = mod_map[s_num]
                for fld in ("script", "trap", "trans"):
                    if pn[fld] != str(dn.get(fld, "")).strip():
                        issues.append(f"Notes Slide {s_num:02d}: PPTX vs notes_data_modules '{fld}' parity mismatch")

            scr = pn["script"]
            for pat, msg in patterns:
                if re.search(pat, scr + "\n" + pn["trap"], flags=re.IGNORECASE):
                    issues.append(f"Notes Slide {s_num:02d}: Banned pattern [{msg}]")
            for pat, msg in ABBREV_ERRORS:
                if re.search(pat, scr + "\n" + pn["trap"]):
                    target_list = warnings if args.allow_legacy_shorthand else issues
                    target_list.append(f"Notes Slide {s_num:02d}: {msg}")

            # Script-only hygiene checks (Thai/EN clinical natural speech)
            if "เสมอ" in scr:
                issues.append(f"Notes Slide {s_num:02d}: Banned rigid word 'เสมอ' inside spoken script")
            if re.search(r"\bStep\s*[1-4]\b", scr, flags=re.IGNORECASE):
                issues.append(f"Notes Slide {s_num:02d}: Robotic 'Step 1..4' recital in spoken script")
            if re.search(r"[()]", scr):
                issues.append(f"Notes Slide {s_num:02d}: Parentheses '()' leaked into spoken script")
            if re.search(r"\bpp?\.\s*\d+", scr):
                issues.append(f"Notes Slide {s_num:02d}: Page reference '(p./pp. N)' leaked into spoken script")
            if re.search(r"(?:^|\n)\s*\d+[\.)]\s+", scr):
                issues.append(f"Notes Slide {s_num:02d}: Numbered list bullet in spoken script (must flow naturally)")

        # Cumulative timestamp vs Slide 1 stated duration sanity check
        s1_scr = scripts_by_slide.get(1, "")
        m_dur = re.search(r"(\d+)\s*(?:ถึง|-)\s*(\d+)\s*นาที", s1_scr)
        if m_dur and last_end_min is not None:
            lo, hi = float(m_dur.group(1)), float(m_dur.group(2))
            if last_end_min < lo - 2.0 or last_end_min > hi + 2.0:
                warnings.append(
                    f"Notes Timing: Cumulative timestamps end at {last_end_min:.1f} min vs Slide 01 intro '{lo:.0f}-{hi:.0f} นาที'"
                )

        # No Double Thank-You across final two slides
        n_tot = len(prs.slides)
        if n_tot >= 2:
            ty_re = re.compile(r"ขอบพระคุณ|ขอบคุณ|thank\s+you", flags=re.IGNORECASE)
            if ty_re.search(scripts_by_slide.get(n_tot - 1, "")) and ty_re.search(scripts_by_slide.get(n_tot, "")):
                warnings.append(
                    f"Notes Closing: Double thank-you detected across Slides {n_tot-1:02d} and {n_tot:02d} (close only once on final slide)"
                )

    print(f"=== Verbatim, Parity & Hygiene Verification ({len(prs.slides)} slides, profile={args.profile}) ===")
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  ! {w}")
        if getattr(args, "strict_warnings", False):
            issues.extend([f"[strict-warning] {w}" for w in warnings])
    if not issues:
        print(f"PASS 100%: All {len(prs.slides)} slides verified (verbatim numbers + superscript/Ref parity + zero leaks)!")
    else:
        print(f"FAILED ({len(issues)} issue(s)):")
        for iss in issues:
            print(f"  - {iss}")
        sys.exit(1)


if __name__ == "__main__":
    main()
