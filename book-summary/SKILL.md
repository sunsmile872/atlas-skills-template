---
name: book-summary
description: >-
  Comprehensive deep-reading and knowledge synthesis skill for full books (PDF, EPUB, AZW3/MOBI) across Non-Fiction, Business, Productivity, Psychology, Philosophy, and Medical/Scientific textbooks. Produces 3-Tier Detailed Summaries (Executive Core Thesis -> Chapter-by-Chapter Deep Dive -> Master Synthesis), generates Double-Loop Action Playbooks (Quick Wins, Systemic Integrations, If-Then Heuristics), formulates Socratic Critical Inquiries, and produces vertical A4-styled Executive Poster Infographics in Dark Navy Blue / Teal Green / Mint palette.
---

# Book Summary & Synthesizer (ระบบสรุปและสังเคราะห์หนังสือฉบับเจาะลึก)

## Overview
Skill นี้ใช้สำหรับอ่าน วิเคราะห์ กลั่นกรอง และสังเคราะห์หนังสือทั้งเล่มอย่างละเอียด รองรับทั้ง **Non-Fiction ทั่วไป (ธุรกิจ, การบริหาร, การพัฒนาตนเอง, จิตวิทยา, ปรัชญา)** และ **ตำราวิชาการ/การแพทย์ (Medical & Scientific Textbooks)** โดยเปลี่ยนเนื้อหาจากหนังสือเล่มหนา (300–800+ หน้า) ให้กลายเป็น:
1. **Master Markdown Report**: สรุปเจาะลึกครบถ้วนระดับ 3-Tier พร้อมเคส ตัวอย่าง และกลไก
2. **Double-Loop Action Playbook**: แนวทางนำไปปรับใช้จริง (Quick Wins + Systems + If-Then Decision Rules)
3. **Critical Inquiry**: คำถามขบคิดต่อยอด จุดบอดของหนังสือ และมุมมองแย้งทางวิชาการ
4. **Executive Poster Infographic**: สรุปภาพรวมแบบ Visual Poster ในธีม Dark Navy Blue, Teal Green, Mint และ White ตามมาตรฐานพรีเมียม

---

## Supported File Formats & Tools
รองรับไฟล์ต้นฉบับได้โดยตรง:
- **PDF**: ประมวลผลผ่าน `scripts/book_extractor.py` (ใช้ PyMuPDF/fitz ดึงสารบัญ หน้า และเนื้อหา)
- **EPUB**: แตกโครงสร้างและดึงรายบทผ่าน `scripts/book_extractor.py` (ใช้ built-in zipfile และ XML parser)
- **AZW3 / MOBI (Kindle KF8)**: แตกไฟล์ผ่านโมดูลของ `novel-translator-th`

---

## Ingestion & Extraction Workflow

เมื่อผู้ใช้ส่งไฟล์หนังสือเข้ามาในแชท หรือระบุพาธของไฟล์:

### ขั้นตอนที่ 1: ตรวจสอบข้อมูลหนังสือและสารบัญ (Inspect Metadata & TOC)
รันสคริปต์เพื่อดูโครงสร้าง สารบัญ และประเมินความยาว:
```bash
python3 ~/.gemini/config/skills/book-summary/scripts/book_extractor.py info "<path_to_book>"
```
- ตรวจสอบชื่อเรื่อง (Title), ผู้แต่ง (Author), จำนวนหน้า/บท, และสารบัญ (TOC)
- หากหนังสือมีความยาวมาก (> 200 หน้า) ให้ใช้ระบบประมวลผลแบบรายบท (Chapter-by-Chapter Chunking) เพื่อป้องกันไม่ให้ข้อมูลสำคัญสูญหายหรือตกหล่น

### ขั้นตอนที่ 2: สกัดเนื้อหารายบท (Extract Chapter Content)
สามารถดึงข้อความของบทที่ต้องการมาอ่านได้ทันที:
```bash
python3 ~/.gemini/config/skills/book-summary/scripts/book_extractor.py chapter "<path_to_book>" <chapter_index>
```
หรือดึงทุกบทออกมาเก็บในโฟลเดอร์ทำงานชั่วคราว:
```bash
python3 ~/.gemini/config/skills/book-summary/scripts/book_extractor.py dump "<path_to_book>" -o "<workspace_dir>/unpacked_book"
```

---

## โครงสร้างผลลัพธ์มาตรฐาน 3 ระดับ (3-Tier Output Architecture)

ไฟล์สรุปหลัก (`<Title>_Comprehensive_Summary.md`) จะต้องประกอบด้วย 3 ส่วนสำคัญอย่างเคร่งครัด:

### Tier 1: ภาพรวมสังเคราะห์ระดับผู้บริหาร (Executive Core Synthesis)
1. **Core Thesis (แก่นคิดรวบยอด 1 ประโยค)**: หนังสือเล่มนี้พยายามแก้ปัญหาอะไร และข้อเสนอหลักที่ปฏิวัติวงการคืออะไร
2. **Key Mental Models & Frameworks**: โมเดลทางความคิดหรือทฤษฎีหลัก 3–5 ตัว พร้อมนิยามและกลไกการทำงาน
3. **Paradigm Shift Matrix (ตารางเปรียบเทียบกระบวนทัศน์)**:
   | มิติการพิจารณา (Dimension) | ความเชื่อเดิม (Conventional Wisdom) | สิ่งที่หนังสือค้นพบ/เสนอ (Breakthrough Insight) |
   | :--- | :--- | :--- |
   | ... | ... | ... |

### Tier 2: สรุปเจาะลึกแบบรายบท (Chapter-by-Chapter Deep Dive)
สำหรับแต่ละบท (หรือกลุ่มบทสำคัญ) ให้สรุปโดยมีองค์ประกอบครบ:
* **ข้อโต้แย้งหลัก (Central Argument)**: บทนี้ต้องการพิสูจน์อะไร
* **หลักฐานเชิงประจักษ์ & กรณีศึกษา (Evidence & Case Studies)**: ยกตัวอย่างการทดลอง, เรื่องราวในประวัติศาสตร์, หรือ Clinical Cases ที่หนังสืออ้างอิง
* **กลไกและรายละเอียดเชิงลึก (Nuances & Mechanisms)**: เจาะลึกกระบวนการทำงาน ขั้นตอน หรือคำอธิบายทางสรีรวิทยา/จิตวิทยา/เศรษฐศาสตร์
* **คำศัพท์และนิยามสำคัญ (Key Terms)**: ใช้ภาษาไทยเชิงวิชาการ พร้อมกำกับคำศัพท์ภาษาอังกฤษในวงเล็บเสมอ (Bilingual Technical Terms)

### Tier 3: บูรณาการการนำไปใช้และข้อฉุกคิด (Double-Loop Application & Inquiry)

#### ส่วนที่ 1: Double-Loop Action Playbook (คู่มือการนำไปปรับใช้จริง)
1. ⚡ **Immediate Quick Wins (ทำได้ทันทีใน 24–48 ชม.)**:
   - พฤติกรรมหรือการทดลองขนาดเล็กที่เริ่มทำได้เลยโดยไม่ต้องรอเปลี่ยนระบบใหญ่
2. 🏗️ **Systemic & Habit Integration (การวางระบบและกระบวนการระยะยาว)**:
   - การออกแบบสภาพแวดล้อม, ขั้นตอนการทำงาน (SOP), หรือพิธีกรรมประจำวัน/สัปดาห์
3. 🧭 **If-Then Decision Heuristics (เกณฑ์ตัดสินใจเมื่อเผชิญสถานการณ์)**:
   - แปลงคำสอนในหนังสือให้อยู่ในรูปสูตรตัดสินใจ เช่น:
     - *IF (เมื่อพบสัญญาณ X)* → *THEN (ให้เลือกแนวทางปฏิบัติ Y ทันทีเพื่อป้องกัน Z)*

#### ส่วนที่ 2: Critical Inquiry & Reflection (คำถามและข้อฉุกคิดต่อยอด)
1. ❓ **Socratic Self-Reflection Questions**:
   - คำถามสำหรับย้อนถามตัวเอง ทีมงาน หรือองค์กร เพื่อประเมินความสอดคล้องกับแนวคิดในหนังสือ
2. 🛡️ **Steel-manning & Blind Spots (จุดบอดและข้อจำกัดของหนังสือ)**:
   - มุมมองแย้งทางวิชาการ (Counter-arguments)
   - กรณีที่ทฤษฎีในหนังสือใช้ไม่ได้ผล (Boundary Conditions & Edge Cases)
3. 🌐 **Cross-Domain Transfer Questions**:
   - คำถามเพื่อกระตุ้นให้ผู้อ่านคิดนำแนวคิดนี้ไปประยุกต์ข้ามสายงาน (เช่น นำปรัชญา Stoic ไปใช้ในการบริหาร หรือนำแนวคิด Systems Thinking ไปใช้ในการรักษาคนไข้)

---

### Tier 4: การประยุกต์ใช้เฉพาะบุคคลตามบริบทชีวิตจริง (Personalized Life & Career Translation)
*อ้างอิงข้อมูลจากแฟ้มบริบทชีวิต: `references/user_life_context.md` เสมอ เพื่อแปลผลแบบตัดสูทเฉพาะบุคคล (Tailored Advisory)*:

1. 🏥 **มิติเวชศาสตร์ฟื้นฟู & คลินิกความงาม (Clinical & Medical Practice)**:
   - ทฤษฎี/บทเรียนนี้ นำมาปรับใช้กับการประเมินคนไข้ (EMG/NCS, Biomechanics, Facial Mapping), การตัดสินใจภายใต้ความไม่แน่นอน, หรือการสื่อสารและสร้างความสัมพันธ์กับคนไข้ได้อย่างไร
2. 💻 **มิตินักพัฒนาระบบ & AI Workflow (Developer & Systems Thinking)**:
   - แปลงหลักการในหนังสือให้เป็น "Algorithm / Architecture / Automation Workflow" ในชีวิตจริง (เช่น เชื่อมโยงกับ React, Web apps, Apple Shortcuts หรือ AI Agents)
3. ⚡ **มิติการบริหารพลังงานและตารางชีวิตแพทย์ประจำบ้าน (Resident Time & Energy Leverage)**:
   - ข้อเสนอที่ High-Leverage ทำน้อยแต่ได้ผลมาก (เหมาะกับตารางเวรที่แน่น) โดยไม่ทำให้เกิดภาวะหมดไฟ (Burnout)
4. 🍷 **มิติสมดุลชีวิต สุนทรียภาพ และความสัมพันธ์ (Life Mastery & Relationships)**:
   - การประยุกต์ใช้เพื่อรักษาความสัมพันธ์กับคนรักและครอบครัว, วินัยในการออกกำลังกาย (Strength Training), และการรักษาสุนทรียภาพในชีวิตประจำวัน
5. 💰 **มิติสถาปัตยกรรมการเงิน ความมั่งคั่ง และกระแสเงินสด (Wealth, Financial Architecture & Cash Flow)**:
   - แปลงหลักการของหนังสือสู่ระบบกระแสเงินสดและการลงทุนส่วนบุคคล: การจัดการรายรับ, การตัดออม/ค่าใช้จ่ายคงที่, การบริหารกองทุนสำรอง (Sinking Funds: ประกัน/ภาษี), การสร้างผลตอบแทนทบต้นแบบอัตโนมัติ (Auto-DCA) และกฎ Surplus Capital Sweep กวาดเงินคงเหลือเข้าบัญชีลงทุนอย่างมีวินัย
6. 🎯 **สูตรการตัดสินใจเฉพาะบุคคล (Custom Personal If-Then Rules)**:
   - ตัวอย่างสถานการณ์จริงที่คุณมักเผชิญในแต่ละวัน พร้อม Action ที่ควรทำทันที

---

## การสร้าง Executive Poster Infographic (Visual Deliverable)

เมื่อสรุปเนื้อหาเสร็จเรียบร้อย ให้สร้างไฟล์ข้อมูลสรุป JSON และรันสคริปต์เพื่อผลิตโปสเตอร์อินโฟกราฟิกความละเอียดสูง:

> [!IMPORTANT]
> **ข้อกำหนดการส่งมอบงาน (Output Constraints & Format)**:
> 1. **รูปแบบไฟล์ Infographic**: ต้องส่งมอบเป็นไฟล์ **PDF เสมอ** (สคริปต์ `generate_infographic.py` จะคอมไพล์ HTML เป็น A4 PDF ผ่าน headless Chrome ให้โดยอัตโนมัติ)
> 2. **ปลายทางการบันทึกไฟล์**: ต้องบันทึกไฟล์สรุป (`.md`) และอินโฟกราฟิก (`.pdf`) ไว้ในโฟลเดอร์ **`~/Gemini Antigravity/Playground`** (หรือ Active Workspace) เท่านั้น **ห้ามบันทึกไฟล์ผลลัพธ์กลับไปยังไดรฟ์ต้นฉบับ เช่น `<EXTERNAL_SSD>` เป็นอันขาด** ให้คงไดรฟ์ภายนอกไว้สำหรับเก็บ source e-books เดิมเท่านั้น

1. บันทึกข้อมูลภาพรวมลงไฟล์ `summary_data.json`
2. รันสคริปต์แปลงเป็นโปสเตอร์ HTML และ PDF อัตโนมัติ:
   ```bash
   python3 ~/.gemini/config/skills/book-summary/scripts/generate_infographic.py summary_data.json -o "~/Gemini Antigravity/Playground/<Title>_Infographic.html"
   # สคริปต์จะสร้างทั้ง .html และ .pdf ในชื่อเดียวกันโดยอัตโนมัติ
   ```

3. **ธีมโปสเตอร์**: ออกแบบตามแนวคิด Dark Navy Blue (`#07101e`), Teal Green (`#00b4d8`), Mint (`#64ffda`), และ White Text พร้อมกล่องข้อมูลที่คมชัด จัดวางสวยงามระดับพรีเมียม สเกล A4 พร้อมใช้งานทางการแพทย์และการบริหารทันที

---

## การแปลงเอกสารสำหรับ Google Docs และซิงก์ Google Drive (iPad & Cloud Reading)

เพื่อความสะดวกในการเปิดอ่านและจดโน้ตต่อยอดบน iPad Pro ผ่าน Google Docs:
1. แปลงไฟล์ Markdown เป็น `.docx` พร้อมเรนเดอร์แผนภาพ Mermaid เป็นรูปภาพความละเอียดสูงฝังในตัว:
   ```bash
   ~/.local/bin/uv run --with markdown --with python-docx --with htmldocx python3 \
     ~/.gemini/config/skills/book-summary/scripts/md_to_docx.py "<workspace_dir>/<Title>_Comprehensive_Summary.md"
   ```
2. สคริปต์จะสร้างไฟล์ `.docx` ใน Workspace และทำการซิงก์ไปยังโฟลเดอร์ Google Drive บนเครื่องอัตโนมัติ:
   - ปลายทาง Google Drive: `~/Library/CloudStorage/GoogleDrive-{{USER_EMAIL}}/My Drive/Gemini/Book summary/<ชื่อหนังสือ>/`
   - **กฎเหล็กการส่งมอบขึ้น Cloud (Strict Deliverables Rule)**:
     - ให้นำส่งเฉพาะ **2 ไฟล์นี้เท่านั้น**:
       1. เอกสารสรุปเนื้อหา `.docx` (เปิดเป็น Google Docs ได้ทันที)
       2. โปสเตอร์อินโฟกราฟิก `.pdf` (สำหรับเปิดดูบน iPad หรือสั่งปรินต์)
     - ❌ **ห้ามอัปโหลดหรือคัดลอกไฟล์ `.md` และ `.html` เข้าไปยัง Google Drive เด็ดขาด** (ไฟล์ `.md` และ `.html` ให้คงไว้เฉพาะใน Local Workspace สำหรับการประมวลผลภายในเท่านั้น)

---

## มาตรฐานภาษาและการนำเสนอ (Tone & Style Guide)
- **ภาษา**: ใช้ภาษาไทยเชิงวิชาการระดับพรีเมียม (Professional & Analytical Thai) กระชับ ตรงประเด็น ปราศจากน้ำเสียงเวิ่นเว้อ
- **คำศัพท์**: คงคำศัพท์เฉพาะทาง, ศัพท์แพทย์, ชื่อทฤษฎี และโมเดลภาษาอังกฤษไว้ในวงเล็บเสมอ (เช่น *อคติจากการยึดติด (Anchoring Bias)*, *กระบวนการควบคุมภาวะธำรงดุล (Homeostatic Regulation)*)
- **แผนภาพ**: แทรกแผนผัง Mermaid ในเอกสาร Markdown เพื่อให้เห็นความเชื่อมโยงเชิงระบบ (System Diagrams / Mindmaps / Decision Trees)
