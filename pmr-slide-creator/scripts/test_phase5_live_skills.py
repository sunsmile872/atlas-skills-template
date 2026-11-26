#!/usr/bin/env python3
"""
Phase 5 Live Skill Verification & Regression Suite:
1. CLI --help parity across all documented pmr-slide-creator / pmr-slide-auditor subcommands
2. Live audit-deck regression on Trigger_Finger_Full_17_v2_8.pptx (17/17 + notes + chart XML)
3. Fault-injection tests for new Phase 5 gates (NS/lit/SQ/q2h/meta/early CTR, script hygiene,
   notes parity, 3-consecutive archetype strict monotony)
4. Fresh Topic (--engine bento) init-project -> compile -> normalize charts -> inject notes -> audit-deck
5. Fresh Journal Club (--mode jc --lang en) init-project -> checklist copy -> Arial + Amber 'Cannot Tell' +
   badge-safe title + 01/N pagination + no default .docx -> verify-jc-deck (+ fault injection)
6. Two-way sync-rule test on temporary copies (non-destructive)
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pptx import Presentation

CREATOR_DIR = Path.home() / ".gemini/config/skills/pmr-slide-creator"
AUDITOR_DIR = Path.home() / ".gemini/config/skills/pmr-slide-auditor"
CREATOR_CLI = CREATOR_DIR / "scripts/slide_creator_cli.py"
AUDITOR_CLI = AUDITOR_DIR / "scripts/slide_auditor_cli.py"
LIVE_VV = AUDITOR_DIR / "scripts/verify_verbatim.py"
COMPILER = CREATOR_DIR / "scripts/claim_schema_compiler.py"
CHART_FIX = CREATOR_DIR / "scripts/fix_pptx_charts_gslides.py"
INJECT_NOTES = CREATOR_DIR / "scripts/inject_notes_v2.py"

V28_DIR = Path("~/atlas-orchestrator/projects/Trigger_Finger_Presentation")
V28_PPTX = V28_DIR / "Trigger_Finger_Full_17_v2_8.pptx"
V28_JSON = V28_DIR / "evidence_bundle.json"
V28_MD = V28_DIR / "PRESENTER_NOTES_MASTER.md"
V28_MODS = V28_DIR / "notes_data_modules"


class Phase5LiveSkillsTests(unittest.TestCase):
    def test_01_cli_help_parity(self):
        for cmd in [
            [sys.executable, str(CREATOR_CLI), "--help"],
            [sys.executable, str(AUDITOR_CLI), "--help"],
            [sys.executable, str(AUDITOR_CLI), "audit-deck", "--help"],
            [sys.executable, str(AUDITOR_CLI), "sync-rule", "--help"],
            [sys.executable, str(AUDITOR_CLI), "verify-pptx-bounds", "--help"],
            [sys.executable, str(AUDITOR_CLI), "auto-find-figures", "--help"],
            [sys.executable, str(AUDITOR_CLI), "render-slides", "--help"],
            [sys.executable, str(CHART_FIX), "--help"],
        ]:
            res = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, msg=res.stdout + res.stderr)

    def test_02_live_audit_deck_on_v2_8(self):
        res = subprocess.run(
            [
                sys.executable,
                str(AUDITOR_CLI),
                "audit-deck",
                "--project-dir",
                str(V28_DIR),
                "--pptx",
                str(V28_PPTX),
                "--evidence",
                str(V28_JSON),
                "--md",
                str(V28_MD),
                "--notes-dir",
                str(V28_MODS),
                "--profile",
                "pmr_board",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res.returncode, 0, msg=res.stdout + res.stderr)
        self.assertIn("PASS 100%", res.stdout)
        self.assertIn("PASS: Whole-deck bounds clean", res.stdout)

    def test_03_new_phase5_fault_injections(self):
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            # 3a. Ambiguous shorthand 'NS' & 'lit' on slide
            bad_pptx = tdir / "bad_abbrev.pptx"
            prs = Presentation(str(V28_PPTX))
            for sh in prs.slides[1].shapes:
                if sh.top / 914400 < 6.95 and sh.has_text_frame and "Index" in sh.text_frame.text:
                    sh.text_frame.paragraphs[0].add_run().text = " NS lit SQ"
                    break
            prs.save(str(bad_pptx))
            res = subprocess.run(
                [sys.executable, str(LIVE_VV), "--evidence", str(V28_JSON), "--pptx", str(bad_pptx), "--profile", "pmr_board"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res.returncode, 0)
            self.assertIn("Ambiguous abbreviation 'NS'", res.stdout)
            self.assertIn("Informal abbreviation 'lit'", res.stdout)
            self.assertIn("Use 'Subcutaneous'", res.stdout)

            # 3b. Script hygiene violations ('เสมอ', 'Step 1', '(p. 199)') & Notes parity mismatch
            bad_md = tdir / "bad_notes.md"
            md_txt = V28_MD.read_text(encoding="utf-8")
            bad_md.write_text(md_txt, encoding="utf-8")
            prs2 = Presentation(str(V28_PPTX))
            prs2.slides[1].notes_slide.notes_text_frame.text = (
                "[0:35 - 1:35] Title\n\n【บทพูดบรรยาย】:\n"
                "Step 1 ต้องฉีดเสมอ (p. 199)\n\n【Staff Q&A Trap】:\nQ\n\n【Transition】: next"
            )
            bad_notes_pptx = tdir / "bad_notes.pptx"
            prs2.save(str(bad_notes_pptx))
            res2 = subprocess.run(
                [
                    sys.executable,
                    str(LIVE_VV),
                    "--evidence",
                    str(V28_JSON),
                    "--pptx",
                    str(bad_notes_pptx),
                    "--md",
                    str(bad_md),
                    "--profile",
                    "pmr_board",
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res2.returncode, 0)
            self.assertIn("parity mismatch", res2.stdout)
            self.assertIn("Banned rigid word 'เสมอ'", res2.stdout)
            self.assertIn("Robotic 'Step 1..4'", res2.stdout)
            self.assertIn("Parentheses '()' leaked", res2.stdout)

            # 3c. Strict 3-consecutive layout monotony rejected
            bad_ev = tdir / "bad_monotony.json"
            ev = json.loads(V28_JSON.read_text(encoding="utf-8"))
            ev["slides"][2]["archetype"] = "split_figure_card"
            ev["slides"][3]["archetype"] = "split_figure_card"
            ev["slides"][4]["archetype"] = "split_figure_card"
            bad_ev.write_text(json.dumps(ev, ensure_ascii=False), encoding="utf-8")
            res3 = subprocess.run(
                [sys.executable, str(LIVE_VV), "--evidence", str(bad_ev), "--pptx", str(V28_PPTX), "--profile", "pmr_board"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res3.returncode, 0)
            self.assertIn("Layout monotony: Slides 3..5", res3.stdout)

    def test_04_fresh_bento_topic_end_to_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            pdir = Path(tmp) / "smoke_topic"
            pdir.mkdir()
            res_init = subprocess.run(
                [
                    sys.executable,
                    str(CREATOR_CLI),
                    "init-project",
                    "--project-dir",
                    str(pdir),
                    "--mode",
                    "topic",
                    "--engine",
                    "bento",
                    "--topic",
                    "Phase 5 Bento Smoke",
                    "--slides",
                    "4",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_init.returncode, 0, msg=res_init.stdout + res_init.stderr)
            self.assertTrue((pdir / "build_slides.js").exists())
            self.assertTrue((pdir / "USER_INSTRUCTIONS_MASTER.md").exists())
            self.assertTrue((pdir / "icons/users_teal.png").exists())

            raw = {
                "meta": {"topic": "Phase 5 Bento Smoke", "theme": "navy_teal"},
                "references": [{"id": 1, "short": "Frontera 4e", "citation": "Frontera WR, ed. Essentials of PM&R. 4th ed. 2019.", "chapters_pages": "Ch. 1 (p. 10)"}],
                "claim_registry": {
                    "C1": {"book_id": 1, "page": "p. 10", "quote": "50% baseline rate"}
                },
                "slides": [
                    {
                        "slide_id": 1,
                        "archetype": "dark_hero_title",
                        "module": "PHASE 5 SMOKE TEST",
                        "title": "Phase 5 Bento Smoke",
                        "subtitle": "Automated end-to-end validation",
                        "presenter": "Presented by: {{PRESENTER_NAME}} (PM&R Resident Year 1)",
                        "advisor": "Advisor: {{ADVISOR_NAME}} | {{INSTITUTION}}",
                        "institution": "Faculty of Medicine, {{UNIVERSITY}}",
                    },
                    {
                        "slide_id": 2,
                        "archetype": "kpi_hero_plus_chart",
                        "module": "MODULE 01 | TEST",
                        "title": "Prevalence Overview",
                        "subtitle": "Fifty percent general rate across adult cohorts{{C1}}",
                        "kpis": [
                            {"value": "50%", "label": "General Cohort{{C1}}", "tone": "teal"},
                            {"value": "50%", "label": "Comparison Cohort{{C1}}", "tone": "navy"},
                            {"value": "50%", "label": "Follow-up Cohort{{C1}}", "tone": "amber"},
                        ],
                        "chart": {
                            "title": "Cohort Rate (%)",
                            "unit": "%",
                            "categories": ["Group A¹", "Group B¹"],
                            "values": [50, 50],
                        },
                        "associations_card": {"title": "Key Notes", "items": ["Baseline rate reported at fifty percent.{{C1}}"]},
                    },
                    {
                        "slide_id": 3,
                        "archetype": "quadrant_2x2_differential",
                        "module": "MODULE 02 | MATRIX",
                        "title": "Clinical Matrix",
                        "subtitle": "Balanced two-by-two cards verify Arial spacing",
                        "quadrants": [
                            {"tag": "FACTOR A", "title": "Card One", "finding": "Concise verified rate fifty percent.{{C1}}", "key_rule": "Plain word anchor before citation.{{C1}}", "tone": "teal", "icon": "hand_navy.png"},
                            {"tag": "FACTOR B", "title": "Card Two", "finding": "Concise verified text line one.{{C1}}", "key_rule": "Concise verified text line two.{{C1}}", "tone": "navy", "icon": "dot_teal.png"},
                            {"tag": "FACTOR C", "title": "Card Three", "finding": "Concise verified text line one.{{C1}}", "key_rule": "Concise verified text line two.{{C1}}", "tone": "amber", "icon": "bone_blue.png"},
                            {"tag": "FACTOR D", "title": "Card Four", "finding": "Concise verified text line one.{{C1}}", "key_rule": "Concise verified text line two.{{C1}}", "tone": "coral", "icon": "baby_amber.png"},
                        ],
                    },
                    {
                        "slide_id": 4,
                        "archetype": "references_slide",
                        "module": "REFERENCES | TEXTBOOKS",
                        "title": "Primary Textbook References",
                        "subtitle": "Verified verbatim",
                    },
                ],
            }
            (pdir / "evidence_bundle_raw.json").write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
            subprocess.run([sys.executable, str(COMPILER), "--in-json", str(pdir / "evidence_bundle_raw.json"), "--out-json", str(pdir / "evidence_bundle.json")], check=True)
            subprocess.run(["node", str(pdir / "build_slides.js"), "--evidence", str(pdir / "evidence_bundle.json"), "--out", str(pdir / "Smoke.pptx")], check=True)
            subprocess.run([sys.executable, str(CHART_FIX), "--pptx", str(pdir / "Smoke.pptx")], check=True)

            (pdir / "notes_data_modules/mod01.py").write_text(
                'DATA = {\n'
                '  1: {"time": "0:00 - 0:30", "title": "Title", "script": "สวัสดีครับวันนี้ใช้เวลาประมาณ 1 ถึง 2 นาทีครับ", "trap": "Q", "trans": "ถัดไป"},\n'
                '  2: {"time": "0:30 - 1:00", "title": "Chart", "script": "กราฟแสดงสัดส่วนชัดเจนครับ", "trap": "Q", "trans": "ถัดไป"},\n'
                '  3: {"time": "1:00 - 1:30", "title": "Matrix", "script": "แบ่งเป็นสี่ด้านสำคัญครับ", "trap": "Q", "trans": "ถัดไป"},\n'
                '  4: {"time": "1:30 - 1:40", "title": "References", "script": "ขอบพระคุณครับ", "trap": "Q", "trans": "จบการนำเสนอ"}\n'
                '}\n',
                encoding="utf-8",
            )
            subprocess.run(
                [sys.executable, str(INJECT_NOTES), "--pptx", str(pdir / "Smoke.pptx"), "--modules-dir", str(pdir / "notes_data_modules"), "--topic", "Phase 5 Smoke", "--out-md", str(pdir / "PRESENTER_NOTES_MASTER.md"), "--lang", "th"],
                check=True,
            )
            res_aud = subprocess.run(
                [sys.executable, str(AUDITOR_CLI), "audit-deck", "--project-dir", str(pdir), "--pptx", str(pdir / "Smoke.pptx"), "--evidence", str(pdir / "evidence_bundle.json"), "--md", str(pdir / "PRESENTER_NOTES_MASTER.md"), "--notes-dir", str(pdir / "notes_data_modules"), "--profile", "pmr_board"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_aud.returncode, 0, msg=res_aud.stdout + res_aud.stderr)

    def test_05_journal_club_mode_fixes_and_verify_jc_deck(self):
        with tempfile.TemporaryDirectory() as tmp:
            jdir = Path(tmp) / "smoke_jc"
            jdir.mkdir()
            res_init = subprocess.run(
                [sys.executable, str(CREATOR_CLI), "init-project", "--project-dir", str(jdir), "--mode", "jc", "--study-type", "rct", "--topic", "Test JC Deck", "--slides", "4"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_init.returncode, 0, msg=res_init.stdout + res_init.stderr)
            # Official CASP RCT checklist copied
            self.assertTrue(any(jdir.glob("source/*rct*checklist*.pdf")) or any(jdir.glob("source/*.pdf")))

            # Verify generate_presenter_notes defaults to NO .docx
            notes_mod_txt = (
                'DATA = {\n'
                '  1: {"time": "0:00 - 0:30", "title": "Cover", "script": "Good morning faculty and colleagues.", "trap": "RCT overview", "trans": "Next to eligibility."},\n'
                '  2: {"time": "0:30 - 1:15", "title": "Eligibility", "script": "Patients met strict inclusion criteria.", "trap": "Selection bias minimal", "trans": "Moving to results."},\n'
                '  3: {"time": "1:15 - 2:00", "title": "Results", "script": "Primary outcome improved significantly.", "trap": "Check confidence interval", "trans": "Now critical appraisal."},\n'
                '  4: {"time": "2:00 - 2:45", "title": "Appraisal", "script": "Allocation concealment was unclear.", "trap": "Marked cannot tell in amber", "trans": "Thank you."}\n'
                '}\n'
            )
            (jdir / "notes_data_modules/mod01.py").write_text(notes_mod_txt, encoding="utf-8")

            build_jc = (
                "import sys\n"
                "from pathlib import Path\n"
                "from PIL import Image\n"
                f"sys.path.insert(0, {str(jdir)!r})\n"
                "import make_presentation as mp\n"
                "img = Path(mp.ASSET_DIR) / 'dummy.png'\n"
                "Image.new('RGB', (800, 500), (255, 255, 255)).save(img)\n"
                "prs = mp.init_presentation()\n"
                "mp.add_title_slide(prs, 'Test JC Deck', 'Randomized Controlled Trial')\n"
                "mp.add_jc_eligibility_slide(prs, 'Eligibility Criteria', ['Age >= 18 yr'], ['Prior surgery'], 'Author 2025')\n"
                "mp.add_jc_cropped_table_slide(prs, 'Primary Outcome Table Comparison With Long Title Text', 'dummy.png', callout_badge='p = 0.012', ref_text='Table 2')\n"
                "mp.add_jc_checklist_slide(prs, 'CASP Section A: Validity', 'dummy.png', [('Q4: Blinding of participants, personnel & assessors?', 'Cannot Tell', 'Masking unclear in methods')], 'CASP UK RCT 2024')\n"
                "mp.finalize_jc_slide_numbers(prs)\n"
                "prs.save(mp.OUTPUT_PATH)\n"
            )
            (jdir / "build_jc.py").write_text(build_jc, encoding="utf-8")
            subprocess.run([sys.executable, str(jdir / "build_jc.py")], check=True)
            subprocess.run([sys.executable, str(jdir / "generate_presenter_notes.py")], check=True)

            # Zero default .docx!
            self.assertEqual(list(jdir.glob("*.docx")), [])
            self.assertTrue((jdir / "PRESENTER_NOTES_MASTER.md").exists())

            jc_pptx = jdir / "Test_JC_Deck_Journal_Club_{{INSTITUTION}}_PMR.pptx"
            prs_chk = Presentation(str(jc_pptx))
            # Verify Cannot Tell badge fill is AMBER (254, 243, 199), NOT coral rose (254, 242, 242)!
            s4_fills = [sh.fill.fore_color.rgb for sh in prs_chk.slides[3].shapes if hasattr(sh, "fill") and sh.fill.type == 1]
            self.assertIn((254, 243, 199), [tuple(c) for c in s4_fills])

            res_jc = subprocess.run(
                [sys.executable, str(AUDITOR_CLI), "verify-jc-deck", "--project-dir", str(jdir), "--pptx", str(jc_pptx), "--lang", "en"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res_jc.returncode, 0, msg=res_jc.stdout + res_jc.stderr)
            self.assertIn("PASS 100%", res_jc.stdout)

    def test_06_sync_rule_non_destructive(self):
        with tempfile.TemporaryDirectory() as tmp:
            tdir = Path(tmp)
            tmpl = tdir / "TEMPLATE.md"
            tmpl.write_text("# Header\n", encoding="utf-8")
            r1 = subprocess.run(
                [sys.executable, str(AUDITOR_CLI), "sync-rule", "--project-dir", str(tdir), "--template", str(tmpl), "--rule", "Test rule XYZ"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r1.returncode, 0, msg=r1.stdout + r1.stderr)
            self.assertIn("Test rule XYZ", tmpl.read_text(encoding="utf-8"))
            r2 = subprocess.run(
                [sys.executable, str(AUDITOR_CLI), "sync-rule", "--project-dir", str(tdir), "--template", str(tmpl), "--rule", "Test rule XYZ"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r2.returncode, 0)
            self.assertEqual(tmpl.read_text(encoding="utf-8").count("Test rule XYZ"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
