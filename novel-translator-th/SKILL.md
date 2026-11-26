---
name: novel-translator-th
description: >-
  Translates English fiction, light novels, and literary books (EPUB, AZW3/MOBI, or PDF) into professional, high-literary-quality Thai using a 3-Stage Multi-Agent Pipeline (Initial Translation -> Literary Polish -> Consistency QA). Automatically extracts and maintains Character & Tone Bibles, unpacks AZW3/MOBI/EPUB files natively, compiles clean Master Markdown and standard Thai EPUBs with strict XML compliance, preserving original color inserts and layout.
---

# Novel Translator TH (ระบบแปลนิยายและวรรณกรรมภาษาไทยเกรดพรีเมียม)

## Overview
Skill นี้ใช้สำหรับแปลหนังสือนิยาย วรรณกรรม และไลท์โนเวลภาษาอังกฤษ รองรับไฟล์ต้นฉบับทั้ง **EPUB, AZW3 (Kindle KF8), MOBI หรือ PDF** ให้เป็นภาษาไทยที่มีสำนวนวรรณกรรมสละสลวย เป็นธรรมชาติ กำจัดกลิ่นอายภาษาอังกฤษ (Anti-Translatorese) โดยจำลองกระบวนการทำงานของสำนักพิมพ์ชั้นนำด้วย **3-Stage Multi-Agent Architecture**

---

## Dependencies
- Python 3.9+ (มีติดตั้งมากับ macOS)
- โมดูลแตกไฟล์ Kindle KF8/AZW3 ในตัว (`scripts/kindleunpack/`)
- คำสั่ง `zip` ในระบบ (สำหรับแพ็กไฟล์ EPUB)
- `references/literary_style_guide.md`: คู่มือขัดเกลาสำนวนวรรณกรรมไทย
- `references/prompt_templates.md`: Prompts สำหรับแต่ละขั้นตอนของ Agent
- `scripts/translator.py`: เครื่องมือ CLI สำหรับแตกไฟล์ AZW3/MOBI/EPUB, สแกนตัวละคร, รวมเล่มเป็นไฟล์เดียว (`.md`) และประกอบเล่ม EPUB มาตรฐาน (`.epub`)

---

## Quick Start
เมื่อผู้ใช้แจ้งชื่อไฟล์ EPUB, AZW3, หรือ PDF ในห้องแชท หรือวางไฟล์ในโฟลเดอร์:

1. **แตกไฟล์และสแกนสารบบตัวละครทั้งเล่ม (Unpack & Full-Book Character Bible)**:
   - กรณีเป็นไฟล์ `.azw3` หรือ `.epub`: แตกโครงสร้างและตรวจสอบสารบัญ:
     ```bash
     python3 ~/.gemini/config/skills/novel-translator-th/scripts/translator.py unpack "<path-to-book.azw3>" -o "<workspace_dir>"
     ```
   - สแกนตัวละครและมุมมองการเล่า (POVs) จากเนื้อหาทุกบททั่วทั้งเล่ม:
     ```bash
     python3 ~/.gemini/config/skills/novel-translator-th/scripts/translator.py scan-characters "<workspace_dir/mobi8>"
     ```
   - รวบรวมตัวละครครบทุกตัว (ตัวละครหลัก, ตัวละครรอง, คนไข้/พยาน/เหยื่อ, คู่สนทนา) และสร้าง `Character_Bible_VolXX.md` นำเสนอให้ผู้ใช้ตรวจทานและอนุมัติก่อนเริ่มแปล

2. **แปลด้วย Fused Direct-Literary Pipeline (High-Efficiency Mode)**:
   - ผสานกฎการแปลวรรณกรรม, บุคลิกตัวละคร, และข้อห้าม Anti-Translatorese เข้าด้วยกันใน Prompt เดียว (Single-Pass Fused Prompt) เพื่อสร้างสำนวนวรรณกรรมเกรด A จบในรอบเดียว (ประหยัด Token 65-70%)
   - **Dynamic Bible Subsetting**: ใช้สคริปต์สกัดเฉพาะตัวละครที่ปรากฏในบทนั้น เพื่อประหยัด Input Tokens:
     ```bash
     python3 ~/.gemini/config/skills/novel-translator-th/scripts/translator.py filter-bible "Character_Bible.md" "chapter_text.txt" -o "compact_bible.md"
     ```
   - **Rolling Micro-Anchor**: แนบสรุปสถานการณ์และอารมณ์ค้าง 3 บรรทัดของบทก่อนหน้า เพื่อรักษาความต่อเนื่องของน้ำเสียง (Anti-Tone Drift) ตลอดทั้งเล่ม
   - **Zero-Token Local Linter**: ตรวจสอบคุณภาพภาษาไทยและคำต้องห้ามในเครื่องคอมพิวเตอร์ฟรี (Token = 0):
     ```bash
     python3 ~/.gemini/config/skills/novel-translator-th/scripts/translator.py lint Chapter_XX.md -b "Character_Bible.md"
     ```

3. **บันทึกไฟล์ประจำบท**:
   - บันทึกไฟล์ Markdown: `Chapter_XX.md`
   - อัปเดตไฟล์โครงสร้างของ EPUB: `unpacked/.../partXXXX.xhtml` (กำหนด `lang="th"` และ sanitize XML entities)
   - *(หมายเหตุ: **ไม่ต้องสร้างไฟล์ HTML Reader** เช่น `อ่านออนไลน์_บทที่XX.html` หรือ `อ่านออนไลน์_รวมเล่ม.html` เว้นแต่ผู้ใช้จะสั่งเจาะจง)*

4. **รวมเล่มเป็นไฟล์เดียวอัตโนมัติ (Unified Compilation) และล้างไฟล์ย่อย (Single Master Markdown Rule)**:
   - ผนวกรวมบทแปลทั้งหมดเป็น Master Markdown เล่มเดียว และรีคอมไพล์ EPUB ทันที:
     ```bash
     python3 ~/.gemini/config/skills/novel-translator-th/scripts/translator.py combine . -o "Title_Full_Thai.md" --epub "<epub_build_dir>" --epub-out "Title - Author[แปลไทย].epub" --title "Title - Author[แปลไทย]" --clean
     ```
   - **กฎเหล็กไฟล์ Master Markdown เดียว (Single Unified Markdown File)**:
     - เมื่อแปลจบทั้งเล่มและรันคำสั่ง `combine` เรียบร้อยแล้ว **ต้องรวมไฟล์ Markdown ทั้งหมดให้เหลือเพียงไฟล์เดียว (`Title_Full_Thai.md`) เสมอ**
     - **ต้องลบไฟล์ประจำบทย่อย (`Chapter_*.md`) ทั้งหมดทิ้ง** (สามารถใช้แฟล็ก `--clean` ในคำสั่ง `combine` หรือสั่งลบไฟล์) เพื่อไม่ให้มีไฟล์บทย่อยคั่งค้างในไดเรกทอรี
   - **กฎเหล็กการตั้งชื่อไฟล์ EPUB**: วงเล็บ `[แปลไทย]` **ต้องอยู่ด้านหลังสุดเสมอ** เช่น `Never Lie - Freida McFadden[แปลไทย].epub` (ห้ามขึ้นต้นด้วย `[แปลไทย]`)

---

## Utility Scripts

สคริปต์ `scripts/translator.py` มีคำสั่งย่อยดังนี้:

| คำสั่ง | การใช้งาน | คำอธิบาย |
| :--- | :--- | :--- |
| `unpack <file>` | `python3 scripts/translator.py unpack <book.azw3/epub> [-o <out_dir>]` | แตกไฟล์ `.azw3`, `.mobi` หรือ `.epub` เป็นโฟลเดอร์โครงสร้างที่พร้อมแก้ไข |
| `inspect <path>` | `python3 scripts/translator.py inspect <path>` | ตรวจสอบโครงสร้างบท สารบัญ และรายชื่อไฟล์ (รองรับทั้งโฟลเดอร์ และไฟล์ `.azw3`/`.epub`) |
| `scan-characters <path>` | `python3 scripts/translator.py scan-characters <path>` | สแกนหาชื่อตัวละคร, บุคคลที่ถูกอ้างถึง, และ POVs ทั้งหมดทั่วทั้งเล่ม |
| `filter-bible <bible> <txt>` | `python3 scripts/translator.py filter-bible <bible.md> <ch.txt> [-o <out.md>]` | คัดกรอง Character Bible ให้เหลือเฉพาะตัวละครที่ปรากฏในบทนั้น (ลด Token ได้ 80%) |
| `lint <target>` | `python3 scripts/translator.py lint <Chapter_XX.md/dir> [-b <bible.md>]` | **Zero-Token Local Linter**: ตรวจจับคำต้องห้าม, Passive voice ผิดธรรมชาติ, คำอังกฤษตกค้าง และความสอดคล้องของชื่อตัวละคร |
| `audit <epub_dir>` | `python3 scripts/translator.py audit <workspace/OEBPS/Text>` | **Zero-Token Full Book Content Audit**: สแกนไฟล์ XHTML ทั้งหมดในเล่มเพื่อตรวจจับประโยคภาษาอังกฤษตกค้าง และตรวจสอบความถูกต้องของไวยากรณ์ XML 100% |
| `verify-completeness <orig> <trans>` | `python3 scripts/translator.py verify-completeness <orig.epub> <trans.epub>` | **Zero-Token Completeness Audit**: เปรียบเทียบจำนวนย่อหน้าและสัดส่วนเนื้อหากับเล่มต้นฉบับ ป้องกันปัญหาตัดทอน (Truncation) 100% |
| `split-chunks <file>` | `python3 scripts/translator.py split-chunks <chapter.txt/xhtml> [--max-paras 40]` | สกัดแบ่งบทที่ยาวเกิน 50-60 ย่อหน้าออกเป็น Chunks ย่อยละ 35-40 ย่อหน้าเพื่อป้องกัน Token truncation |
| `combine <dir>` | `python3 scripts/translator.py combine <dir> -o <master.md> [--epub <dir> --epub-out <out.epub>] [--clean]` | รวมทุกบท `Chapter_*.md` เข้าเป็นไฟล์รวมเล่มเดียว (`.md`), ลบไฟล์บทย่อยทิ้งเมื่อเสร็จ (`--clean`), และอัปเดต `.epub` อัตโนมัติ |
| `compile-epub <dir>` | `python3 scripts/translator.py compile-epub <source_dir> -o <out.epub>` | รวมโครงสร้างโฟลเดอร์ EPUB เป็นไฟล์ `.epub` มาตรฐาน พร้อม sanitize XML entities และฉีด CSS Reset Hyperlink สีน้ำเงินอัตโนมัติ |
| `build-reader <md>` | `python3 scripts/translator.py build-reader <ch.md> -o <out.html>` | *(ตัวเลือกเสริม)* สร้างไฟล์ HTML Reader เฉพาะเมื่อผู้ใช้ร้องขอ |

---

## Whole-Book Batch Execution & Token Management (ยุทธศาสตร์การแปลทั้งเล่มต่อเนื่อง)

เนื่องจากนิยายเต็มเล่มมีความยาวมากกว่า 60,000–100,000 คำ ซึ่งเกินขีดจำกัดขนาดของข้อความต่อหนึ่งรอบ (Single-Turn Token Limit ~8k tokens) ของโมเดลภาษา จึงต้องใช้ยุทธศาสตร์ดังนี้:

1. **การแบ่งรอบการแปลเป็นชุด (Batch Translation Loop)**:
   - แปลเนื้อหาต่อเนื่องทีละชุดละ **4–6 บท** ในแต่ละรอบ เพื่อให้โมเดลสามารถทุ่มเท Tokens ในการขัดเกลาสำนวนวรรณกรรม (3-Stage Polish) ได้อย่างลึกซึ้งโดยไม่ถูกบีบให้ย่อความ
   - ในแต่ละชุด ให้บันทึกไฟล์ประจำบท (`Chapter_XX.md` และ `unpacked/.../partXXXX.xhtml`) ทันที
2. **การรวมเล่มอัตโนมัติทุกจบรอบ (Incremental Compilation) และการคลีนไฟล์ขยะทั้งหมดเมื่อแปลจบ (Zero-Clutter Rule)**:
   - ในระหว่างแปลแต่ละชุด ให้รันคำสั่ง `combine` เพื่อรวมไฟล์เข้าสู่ `Title_Full_Thai.md` และรีแพ็ก `Title - Author[แปลไทย].epub` โดยอัตโนมัติ
   - **เมื่อแปลจบครบทุกบท 100%**: ต้องรัน `combine ... --clean` เพื่อรวมไฟล์และลบไฟล์ `Chapter_*.md` ย่อยทั้งหมดทิ้ง
   - **ต้องเคลียร์ไฟล์ขยะทุกครั้ง (Strict Post-Translation Cleanup)**: เมื่อสร้างไฟล์ `.epub` และ Master `.md` เสร็จสมบูรณ์แล้ว **ต้องลบโฟลเดอร์แตกไฟล์ชั่วคราว (`*_unpacked/`), สคริปต์เฉพาะกิจ (เช่น `compile_*.py`), แผนงานชั่วคราว (`TRANSLATION_PLAN.md`), และไฟล์เศษย่อยทั้งหมดออกจาก Workspace ทันที** ให้หลงเหลืออยู่ในโฟลเดอร์เฉพาะผลงานส่งมอบจริงเท่านั้น ได้แก่:
     1. `Title - Author[แปลไทย].epub`
     2. `Title - Author[แปลไทย].md` (Master Markdown รวมเล่มฉบับสมบูรณ์ไฟล์เดียว)
     3. `Character_Bible_Title.md` (สารบบตัวละครและคำศัพท์)
     4. ไฟล์ต้นฉบับเดิมของผู้ใช้
   - **ไม่ต้อง**สร้างไฟล์ `อ่านออนไลน์_รวมเล่ม.html` หรือ HTML reader ย่อย ส่งมอบเฉพาะ `.epub` และ `.md` รวมเล่มเดียว
3. **การทำงานอัตโนมัติแบบไร้รอยต่อด้วย `/goal`**:
   - แนะนำผู้ใช้ให้สั่งงานผ่านคำสั่ง **`/goal`** เช่น `/goal แปลต่อจนจบทั้งเล่ม รวมไฟล์ทั้งหมด และเคลียร์ไฟล์ขยะ` เพื่อให้ระบบวนลูปแปลทีละชุดในเบื้องหลังจนครบ 100% และคลีน workspace สะอาดเกลี้ยงโดยอัตโนมัติ

---

## Workflow แบบละเอียด

### 1. Pre-flight Profiling (สร้าง Full Master Character & Tone Bible)
วิเคราะห์ตัวละครและระดับภาษาของเรื่องก่อนเริ่มแปล โดยต้องสแกนครอบคลุม**ทั้งเล่ม** (ไม่ใช่เพียงบทแรก):
- **สารบบตัวละครครบถ้วน (Full Character Roster)**: สแกนหาชื่อตัวละครทั้งหมด ทั้งตัวละครดำเนินเรื่อง (POV Leads), ตัวละครรอง, ตัวประกอบ, และบุคคลในบทสนทนา
- **ตารางคู่สนทนาและสรรพนาม (Pronoun Matrix)**: กำหนดสรรพนามที่ตัวละครใช้เรียกตัวเองและเรียกผู้อื่นในทุกความสัมพันธ์ (เช่น สามี-ภรรยา, คนรัก, หมอ-คนไข้, เพื่อนร่วมงาน)
- **คำลงท้ายหรือเอกลักษณ์ภาษา (Verbal Tics)**: เช่น คำอุทานติดปาก, สำนวนเฉพาะบุคคล
- **โทนเสียงการบรรยาย (Atmosphere & Voice)**: เช่น สืบสวนระทึกขวัญ = กระชับ บีบคั้น เยือกเย็น; แฟนตาซี = โวหารพรรณนา สละสลวย

### 2. กระบวนการแปลแบบ Fused Direct-Literary Pass (Single-Pass High-Efficiency)
- **Fused System Prompt**: ผสานบทบาทนักแปลวรรณกรรมเอก (Literary Author Persona), กฎ Anti-Translatorese, และตารางสรรพนามเฉพาะบท เข้าด้วยกันตั้งแต่รอบแรก
- **Dynamic Context Injection**: สกัดเฉพาะตัวละครที่มีบทบาทในบทนั้นด้วย `filter-bible` และแนบ **Rolling Micro-Anchor (3 บรรทัด)** เพื่อส่งต่ออารมณ์และสถานการณ์จากบทก่อนหน้า
- **Zero-Token Local Linting**: ตรวจสอบไฟล์ Markdown ที่แปลเสร็จด้วย `translator.py lint` ในเครื่องคอมพิวเตอร์ (ไม่เสีย Token) หากพบจุดบกพร่อง จึงส่งเฉพาะย่อหน้านั้นให้ AI ทำการแก้ไขแบบเจาะจง (Surgical Patch)

### 3. Checkpoint & Resume
- บันทึกงานแปลทุกช่วง (Section) หรือทุกบทเป็นไฟล์ Markdown อิสระ
- เมื่อเกิดเหตุขัดข้องหรือหลุดจากการเชื่อมต่อ สามารถโหลดไฟล์บทล่าสุดแล้วทำงานต่อได้ทันทีโดยไม่ต้องเริ่มใหม่

---

## กฎเหล็กวรรณกรรมไทย (Anti-Translatorese Rules)
1. **ห้ามใช้ "ถูก..." กับกริยาทั่วไป**: ภาษาอังกฤษมักใช้ `was grabbed`, `was embraced` ให้แปลว่า `ถูกจับคว้า`, `โอบกอดกลืนกิน` ไม่ใช้ `ถูกกอดโดย...`
2. **ห้ามแปลประธานซ้ำซากทุกบรรทัด**: ในภาษาไทย เมื่อทราบแล้วว่าหมายถึงใคร ให้ละประธานได้เพื่อความลื่นไหล
3. **รักษาคำเรียกเฉพาะ**: ยึดตามคำแปลยอดนิยมหรือตามที่ผู้ใช้เคาะอนุมัติ (เช่น แรมเรียกสุบารุว่า "บารุสุ")

---

## ข้อผิดพลาดที่พบบ่อย (Common Mistakes to Avoid)
- **Apple Books แคชเล่มเดิม**: หากส่งออก EPUB โดยใช้ Book ID (`<dc:identifier>`) เดิมตรงกับเล่มภาษาอังกฤษ Apple Books จะเปิดหน้าแคชเดิมเสมอ **ต้องเปลี่ยนรหัสหนังสือและชื่อเรื่องให้ชัดเจน** เช่น `never-lie-th-v1`
- **ไม่ระบุภาษาไทย**: ต้องใส่ `lang="th"` ในแท็ก `<html>` ของทุกไฟล์ เพื่อให้ E-reader แสดงสระและวรรณยุกต์ไทยได้อย่างถูกต้อง ไม่ลอย
- **Apple Books XML Entity Crash (`Entity 'nbsp' not defined`)**: Apple Books ใช้ WebKit XML parser ที่เคร่งครัดมาก ห้ามมี Named Entities ของ HTML เช่น `&nbsp;`, `&eacute;`, `&copy;` ในไฟล์ `.xhtml` เด็ดขาด เพราะจะทำให้ผู้อ่านติดหน้าแดง Error **ต้องแปลงเป็น Numeric Entities เสมอ** เช่น `&nbsp;` ➔ `&#160;`, `&eacute;` ➔ `&#233;`
- **Apple Books Raw XML Tree Bug (`This XML file does not appear to have any style information...`)**: หากแท็ก `<html>` ในไฟล์ `.xhtml` ขาดการประกาศ Namespace `xmlns="http://www.w3.org/1999/xhtml"` หรือขาด `<?xml version="1.0" encoding="utf-8"?>` WebKit จะมองว่าเป็นไฟล์ XML ทั่วไปและแสดงผลเป็นหน้าต่างโค้ด XML ดิบแทนหน้าหนังสือ **ต้องมี `xmlns="http://www.w3.org/1999/xhtml"` ในทุกไฟล์เสมอ**
- **E-Reader Default Blue Hyperlinks**: แอปอ่านอย่าง Apple Books/Kindle จะเรนเดอร์แท็ก `<a>` (เช่น เลขหน้า, ดัชนี, เชิงอรรถ) เป็นสีน้ำเงินหากไม่มีสไตล์บังคับ **ต้องฉีด CSS `a, a:link, a:visited { color: inherit !important; text-decoration: none !important; }` ในไฟล์สไตล์ชีตเสมอ**
- **ปัญหาตัวอักษรเล็กใหญ่ไม่เท่ากัน (Small Caps Typography Bug)**: ในหนังสือภาษาอังกฤษ มักใช้ `<span class="small_caps">` ที่คำขึ้นต้นบท โดย CSS ต้นทางมักตั้งค่า `font-size: 0.75em` หรือ `0.8em` เพื่อจำลอง Small Capitals ของภาษาอังกฤษ แต่เมื่อแปลเป็นภาษาไทยซึ่งไม่มีตัวพิมพ์ใหญ่-เล็ก สไตล์นี้จะทำให้คำไทย 2-3 คำแรกกลายเป็นตัวอักษรขนาดแคระแกร็นดูขัดตา **ต้องรีเซ็ตหรือโอเวอร์ไรด์ CSS เสมอ** เป็น `.small_caps, [class*="small_caps"], [class*="smallcaps"] { font-size: 1em !important; font-variant: normal !important; }` เพื่อให้ขนาดตัวอักษรกลมกลืนเท่ากันทั้งย่อหน้า
- **ประโยคหรือบทแปลตกค้าง (Untranslated Leakage)**: ก่อนส่งมอบงานหรือรันคำสั่งแพ็กเกจเสร็จสิ้น **ต้องรัน `audit` เสมอ** เพื่อตรวจจับข้อความภาษาอังกฤษที่อาจหลุดจากการแปลในไฟล์ XHTML ทุกไฟล์ทั่วทั้งเล่ม
- **ปัญหาเนื้อหาถูกตัดทอนจากการจำกัด Token (Hallucinatory Truncation Bug)**: หากบทใดมีความยาวเกิน 50-60 ย่อหน้า หรือเกิน 3,000 คำ โมเดลมักจะแอบสรุปย่อความเพื่อหนี Output Token Limit ทำให้เนื้อหาหายไป 40-80% **กฎเหล็กเพื่อป้องกัน**:
  1. **Enforced Chunking**: ต้องใช้คำสั่ง `translator.py split-chunks` แบ่งบทออกเป็น Chunks ละไม่เกิน 35-40 ย่อหน้า โดยมีแท็ก `--- PARA X ---` กำกับเสมอ
  2. **Zero-Token Completeness Audit**: ก่อนรวมเล่มและส่งมอบงาน **ต้องรัน `python3 scripts/translator.py verify-completeness <orig.epub> <trans.epub>` เสมอ** หาก Paragraph Ratio ต่ำกว่า 70% ระบบจะไม่อนุญาตให้ปิด Goal หรือส่งมอบงานเด็ดขาด (ทำงานในเครื่อง 0 Token)
- **กฎเหล็กการตั้งชื่อไฟล์ EPUB**: ให้นำวงเล็บ `[แปลไทย]` ไว้**ท้ายชื่อไฟล์เสมอ** เช่น `Never Lie - Freida McFadden[แปลไทย].epub` (ห้ามขึ้นต้นด้วย `[แปลไทย]`)
- **ไม่ต้องสร้างไฟล์ HTML Reader**: ส่งมอบเฉพาะไฟล์ `.epub` และ `.md` รวมเล่มเท่านั้น ไม่ต้องสร้างไฟล์ `อ่านออนไลน์_*.html` มาให้รกพื้นที่
- **มาตรฐานความถูกต้องของโครงสร้าง EPUB และการป้องกันไฟล์เปิดไม่ได้ (EPUB Strict Validity & Health Gate)**:
  1. **Strict 20-byte Mimetype Rule**: ไฟล์ `mimetype` ต้องมีขนาด 20 ไบต์ถ้วน (`application/epub+zip`) ห้ามมี `\r\n` หรือช่องว่างต่อท้ายเด็ดขาด เพราะ Apple Books และ e-Reader มาตรฐานจะปฏิเสธการเปิดไฟล์ทันที
  2. **Zero UTF-8 BOM Rule**: ห้ามมี Byte Order Mark (`\xef\xbb\xbf` หรือ `\ufeff`) ในไฟล์โครงสร้างใดๆ (`container.xml`, `content.opf`, `*.xhtml`, `*.css`) เพราะจะทำให้ XML Parser มองว่าเอกสารไม่สมบูรณ์
  3. **Duplicate XML Declaration Guard**: ตรวจสอบว่าไม่มีการประกาศ `<?xml version="1.0" ... ?>` ซ้ำซ้อนเกินกว่า 1 ครั้งในไฟล์ `.xhtml` เดียวกัน (โดยเฉพาะหน้าแรก `title.xhtml`)
  4. **Thai Typography Font Fallback**: หากไฟล์ต้นฉบับฝังฟอนต์เฉพาะ (เช่น ฟอนต์ภาษาละตินล้วน) CSS ต้องระบุ Fallback สำหรับฟอนต์ระบบภาษาไทยเสมอ (`-apple-system, BlinkMacSystemFont, "Sarabun", "Thonburi", "Noto Sans Thai", sans-serif`) ป้องกันตัวหนังสือไทยแสดงเป็นกล่องสี่เหลี่ยมหรือหายไป
  5. **Automated Health Gate Validation**: ทุกครั้งที่รันคำสั่ง `compile-epub` หรือ `verify-completeness` ระบบจะทดสอบเปิด ZIP และ Validate ไวยากรณ์ XML ของทุกไฟล์ในเล่ม 100% อัตโนมัติ หากพบไฟล์ชำรุดแม้แต่ไฟล์เดียว ระบบจะสั่งระงับการส่งมอบทันที
- **ลืมเคลียร์ไฟล์ขยะทุกครั้ง (Zero-Clutter Workspace Hygiene Rule)**: เมื่อแปลจบครบทั้งเล่มและคอมไพล์ EPUB/Markdown สมบูรณ์แล้ว **ต้องเคลียร์ไฟล์และโฟลเดอร์ขยะทั้งหมดออกจาก Workspace ทันที**:
  - ลบไฟล์ `Chapter_*.md` ย่อยทั้งหมดทิ้ง (ให้เหลือเพียงไฟล์รวมเล่ม `*_Thai.md` / `[แปลไทย].md` เพียงไฟล์เดียว)
  - ลบโฟลเดอร์แตกไฟล์ชั่วคราว (`*_unpacked/`) ทิ้งทันทีเมื่อรวมเล่ม EPUB สำเร็จ
  - ลบสคริปต์เฉพาะกิจชั่วคราว เช่น `compile_*.py`, `patch_*.py`
  - ลบแผนงานชั่วคราว เช่น `TRANSLATION_PLAN.md`
  - Workspace ต้องคงเหลือเฉพาะ: **ไฟล์ส่งมอบจริง (`.epub`, `.md` รวมเล่มเดียว, `Character_Bible_*.md`)** และไฟล์ต้นฉบับเดิมเท่านั้น ห้ามทิ้งไฟล์ชั่วคราวไว้กระจัดกระจายเด็ดขาด

