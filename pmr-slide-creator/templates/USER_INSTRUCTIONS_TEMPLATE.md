# USER_INSTRUCTIONS_MASTER.md
**Project**: {{TOPIC_TITLE}} ({{SLIDE_COUNT}} Slides)  
**Presenter**: {{PRESENTER_NAME}} (Resident Year 1, Physical Medicine and Rehabilitation, {{INSTITUTION}})  
**Advisor**: {{ADVISOR_NAME}}  
**Status**: STANDALONE PERSISTENT MASTER MEMORY (MANDATORY PRE-FLIGHT AUDIT BEFORE EVERY SLIDE)

> [!IMPORTANT]
> **MANDATORY INSTRUCTION FOR AGENTS & SUBAGENTS**:
> ก่อนเริ่มร่าง นำเสนอ หรือตรวจสอบ (Audit) สไลด์ใดๆ ในโปรเจกต์นี้ ตัวแทน AI (Agent/Subagent) **จะต้องใช้คำสั่ง `read_file` เพื่ออ่านและตรวจสอบกฎในเอกสาร `USER_INSTRUCTIONS_MASTER.md` นี้ให้ครบถ้วนทุกครั้งเสมอ** ห้ามข้ามขั้นตอนเด็ดขาด หากพบว่าละเมิดกฎแม้แต่ข้อเดียว จะถือเป็นข้อผิดพลาดร้ายแรงและไม่ผ่านการตรวจสอบ (Audit Failure).

---

## หมวดที่ 1: ข้อมูลบริบทแพทย์ประจำบ้าน (Resident & Academic Context)

1. **อัตลักษณ์ของผู้บรรยาย (Speaker Identity)**:
   - บรรยายในฐานะ **แพทย์ประจำบ้านเวชศาสตร์ฟื้นฟู ชั้นปีที่ 1 (PM&R Resident Year 1)** {{INSTITUTION}} คณะแพทยศาสตร์ {{UNIVERSITY}}
   - นำเสนอต่อหน้าอาจารย์ที่ปรึกษา (**{{ADVISOR_NAME}}**) คณาจารย์ และแพทย์เฉพาะทางเวชศาสตร์ฟื้นฟูและสหสาขาวิชาชีพ
2. **ระดับความน่าเชื่อถือทางวิชาการ (Academic Credibility)**:
   - มาตรฐานการนำเสนอเทียบเท่าการสอบบอร์ดเวชศาสตร์ฟื้นฟู (PM&R Board-Level Precision)
   - น้ำเสียงต้องสะท้อนความเป็นแพทย์ผู้เชี่ยวชาญ (Physician-to-Physician Tone) เป็นกลางทางวิชาการ ยึดหลักฐานเชิงประจักษ์ (Evidence-Based) ปราศจากการพูดจาโอ้อวดหรือภาษาการตลาด
3. **ขอบเขตวิชาชีพเวชศาสตร์ฟื้นฟู (Physiatric Scope of Practice - Standard 18)**:
   - **ห้ามเคลมว่า PM&R ทำหน้าที่ผ่าตัดหรือเซ็นประเมินความเสี่ยงผ่าตัด (Pre-Op Surgical/Medical Clearance)**: การประเมินความพร้อมทางการแพทย์และหัวใจก่อนดมยาเป็นหน้าที่ของศัลยแพทย์ วิสัญญีแพทย์ และอายุรแพทย์
   - บทบาทของ Physiatrist คือ **"Pre-Operative Readiness & Functional Optimization"** การวางแผนฟื้นฟู การป้องกันภาวะแทรกซ้อน และการสั่งการรักษาทางเวชศาสตร์ฟื้นฟู

---

## หมวดที่ 2: สถาปัตยกรรมสไลด์ เลย์เอาต์ และมาตรฐาน Selective Ultra-Lean (Slide Architecture, Layout & Density)

1. **สถาปนา Selective Ultra-Lean เป็นมาตรฐานเลย์เอาต์หลักระดับบอร์ด (Selective Ultra-Lean Layout Standard)**:
   - **สไลด์ทั่วไป (Tier 1 & Tier 2: ~90–93% ของเด็ค)**: กำหนดให้ใช้ **Option B (Ultra-Lean: 6–10 คำต่อ Bullet, รวม 35–45 คำต่อหน้า)** เป็น Default Choice เพื่อสร้างสไลด์ที่โปร่งตา สะอาด สบายตา ทรงพลัง และมี White Card Headroom ด้านล่างการ์ดอย่างน้อย $+1.75"$ ถึง $+3.00"$ เหนือขอบล่าง (Zero-Overflow Guard 100%) โดยคงขนาดฟอนต์ Auditorium Pro (Level 3 Baseline: Heading 16.0 pt Bold, Body 14.0 pt Regular) ไว้อย่างคมชัด
   - **สไลด์ลึกพิเศษ (Tier 3: ~7–10% ของเด็ค)**: สงวนไว้เฉพาะสไลด์สูตรคำนวณชีวกลศาสตร์ละเอียด, ตารางขนาดยา Titration หรือพยาธิสภาพที่เป็นข้อสอบบอร์ด ให้คงเนื้อหา Balanced Precision (12–16 คำ) ไว้ครบ 100% เพื่อไม่ให้ตัวเลขโดสยาและสูตรวิชาการตกหล่น
2. **สเกลตัวอักษรมาตรฐานสากล (Auditorium Pro Typography Standard - Level 3 Baseline)**:
   - ใช้ฟอนต์ **`Arial`** สม่ำเสมอทั้งหัวข้อและเนื้อหา (ป้องกัน Serif fallback และสัญลักษณ์ `>` เพี้ยนใน LibreOffice / Google Slides):
     - **Bento Engine Default (`--mode topic`)**: Heading `15.5–16.0 pt` Bold, Body `14.0 pt` Regular (`13.0–13.5 pt` เฉพาะตาราง/Matrix แน่น), Slide Title `21.5–24.0 pt` Bold, Subtitle `13.5 pt` Muted, Footer/Ref `9.0–9.5 pt` + เลขหน้ามุมขวาล่าง `01 / N` บนทุกหน้า
     - **Python Legacy / JC Fallback**: Slide Title `22.0–24.0 pt`, Bullet Heading `16.0–18.0 pt`, Body `14.0–16.5 pt`
7. **กฎ Visual-First & ห้าม Layout ซ้ำ (Anti-Monotony Rule)**:
   - ห้ามสร้างสไลด์เป็นกำแพงตัวหนังสือล้วนติดๆ กัน เลือก Archetype ให้ตรงข้อมูล (ตัวเลขเปรียบเทียบ = KPI Hero + Chart, หมวดหมู่ 4 ด้าน = 2×2 / Bento Grid, ลำดับขั้น = 4-Step Process Continuum, ภาพ/ตารางตำรา = Split Figure ซ้าย/ขวา หรือ Top Figure + Strip) และให้มีสไลด์เชิงภาพ/กราฟ/ผังอย่างน้อย `>= 50%` ของเด็ค
   - **ห้ามใช้ทรงสไลด์ (`archetype`) ซ้ำกัน 3 หน้าติด** และถ้าวาง `split_figure_card` ใกล้กันให้สลับฝั่งรูปซ้าย–ขวา (`figure_side`) หรือสลับเป็นรูปแนวนอนด้านบน (`top_figure_plus_strip`) เพื่อจังหวะสายตาที่เป็นธรรมชาติ
3. **มาตรฐานการจัดวางกรอบการ์ดคู่ (Balanced Dual White Card Framing & Zero-Overflow Guard)**:
   - **ขนาดเริ่มต้นมาตรฐานสากล**: การ์ดเนื้อหาซ้ายเริ่มต้นที่ `left_width = Inches(6.00)` (กล่องข้อความกว้าง $5.65"$, จุได้ ~64 ตัวอักษร/บรรทัด) และการ์ดรูปภาพขวาเริ่มต้นที่ `right_left = Inches(7.033)`, `right_width = Inches(5.50)`
   - **ระยะ Headroom ด้านล่างการ์ดปลอดภัย**: ขอบล่างของกล่องข้อความต้องไม่เกิน $Y \le 6.85"$ เหนือขอบล่างสไลด์ $7.50"$ เสมอ (มีระยะ Headroom ปลอดภัยอย่างน้อย $\ge 0.65"$ ถึง $+3.00"$)
4. **กฎความสะอาดไร้กรอบซ้อน (Zero Artificial Card-Inside-Card Framing & Clean Borderless Standard)**:
   - **ห้ามสร้างกล่องการ์ดสีเข้มครอบรูปเด็ดขาด**: ในฟังก์ชัน `add_split_content_slide()` ได้วาดกล่องการ์ดสีขาวขอบมน (`img_card`) ไว้อยู่แล้ว ห้ามสร้างรูปภาพที่มีพื้นหลังกล่องสี่เหลี่ยมสี Dark Navy หรือตีกรอบเส้นสีน้ำเงิน/ฟ้าล้อมรอบรูปอีกชั้นหนึ่งเด็ดขาด เพื่อป้องกันปัญหากรอบซ้อนหลายชั้น (Double/Triple Border Phenomenon)
   - **มาตรฐาน Clean Borderless บนพื้นขาวบริสุทธิ์**: หากทำภาพ Composite รวมหลายรูป ต้องใช้ Canvas พื้นหลังสีขาวบริสุทธิ์ (`RGB(255, 255, 255)`) โดยจัดวางข้อความกำกับเหนือหรือใต้รูปโดยตรง และ **ห้ามตีกรอบเส้น (No Outline/Borders) รอบกล่องย่อยเด็ดขาด**
   - **การสกัดแบบชิดขอบภาพจริง (Tight Bounding-Box Cropping)**: เมื่อสกัดภาพจากตำรา PDF ต้อง Crop ชิดขอบภาพจริงเสมอ ตัดขอบขาวหรือขอบดำส่วนเกินของหน้ากระดาษออกทั้งหมด
5. **กฎการใช้หัวข้อย่อยแบ่งกลุ่มแบบมีเงื่อนไข (Conditional Section Subheading Standard — `■  Subheading`)**:
   - **เมื่อใดที่ต้องใช้**: เมื่อสไลด์ `add_split_content_slide` หนึ่งหน้าต้องนำเสนอเนื้อหาที่แบ่งเป็น **2 หมวด/ทิศทาง/ระยะที่คู่ขนานกันชัดเจน** (เช่น *Ascent vs. Descent*, *Acute vs. Chronic*, *Indications vs. Contraindications*) ให้แทรกหัวข้อย่อยแบ่งกลุ่มด้วย tuple ที่มีคำอธิบายว่างเปล่า `("<Subheading>", "")` เพื่อให้ `make_presentation.py` เรนเดอร์เป็นหัวข้อสี Teal ตัวหนา (`■  <Subheading>`, 16.5 pt)
   - **โควต้าความโปร่ง (Ultra-Lean Guard)**: จำกัดไม่เกิน **2 Subheadings × 2 Bullets ต่อหมวด (รวม 4 body bullets)** และคงความยาว 6–10 คำต่อ bullet เพื่อรักษา White Card Headroom ($\ge +1.50"$) และ Zero-Overflow
   - **ห้ามอ่านหัวข้อซ้ำในบทพูด**: ในบทพูด 1:1 ให้เชื่อมโยงเข้าสู่แต่ละหมวดอย่างเป็นธรรมชาติ ห้ามอ่านชื่อ `■  Subheading` แบบทวนหัวข้อ
6. **กฎความชัดแจ้งของกลไกใน Bullet และบทพูด (Self-Explanatory Mechanism Rule)**:
   - **โครงสร้าง `Action/Deficit → Mechanism → Consequence`**: แม้จะใช้ Option B (กระชับ ~8–12 คำ) ห้ามย่อจนเหลือคำศัพท์ลอยๆ ต้องระบุให้ชัดว่า *ทำอะไร/ขาดอะไร → เกิดกลไกทางกายภาพอย่างไร → ส่งผลหรือต้องแก้อย่างไร*
   - **ใช้ภาษาที่เห็นภาพการเคลื่อนไหวจริง (Concrete Physical Action)**: เลี่ยงศัพท์นามธรรมหรือคำย่อที่กำกวมเมื่ออยู่เดี่ยวๆ (เช่น *jackknifing*, *blocks tibial advance*, *grading*) ให้เขียนบรรยายการเคลื่อนไหวจริงแทน (เช่น *sudden knee buckling*, *body weight stays behind foot*, *push posterior socket to lower slowly*)
   - **ปูพื้นกลไกปกติก่อนอธิบายข้อจำกัด (Normal-Baseline-First in Script)**: ในบทพูด 1:1 เมื่ออธิบายความผิดปกติหรือเทคนิคชดเชย ให้เกริ่นกลไกปกติของร่างกายสั้นๆ 1 ประโยคก่อนเสมอ แล้วค่อยเชื่อมเข้าสู่ข้อจำกัดและวิธีแก้เพื่อให้ผู้ฟังเห็นภาพเหตุ-ผลต่อเนื่องทันที

---

## หมวดที่ 3: สไตล์การ Audit 8 องค์ประกอบมาตรฐาน (Standard 16 Compliant)

ทุกสไลด์ที่จะนำเสนอต่อผู้ใช้ **จะต้องแสดง Audit Dossier ครบทั้ง 8 องค์ประกอบในหน้าแชตโดยตรงเสมอ (Inline Full 8-Element Presentation)** ห้ามย่อเป็นบทสรุปสั้นแล้วชี้ลิงก์ไปที่ไฟล์ `audit_buffer/` เด็ดขาด โดยประกอบด้วย 8 องค์ประกอบตามลำดับดังนี้:

1. **Header & Metadata**: Slide Number, Category, Slide Type (`add_split_content_slide` หรือ `add_table_slide`), และสถานะการ Audit
2. **ASCII Wireframe Layout Box**: กล่องแสดงผังตำแหน่งการ์ด 16:9 (`┌───────────────────────────┐`) ความละเอียดชัดเจน
3. **Bullets on Slide (`build_slides.py`) — Dual-Density Choices (Option A vs Option B)**: แสดงข้อความ Bullet บนสไลด์โดยนำเสนอ 2 ทางเลือกคู่กันเสมอใน Element 3: **Option A (Balanced Standard: 12–16 คำ/ข้อ)** เน้นความสมบูรณ์ของพยาธิสรีรวิทยา และ **Option B (Ultra-Lean Telegraphic: 6–10 คำ/ข้อ)** เน้นความสั้นกระชับ ตัดคำเชื่อม ตัวเลขโดดเด่น เปิด White Space โปร่งสบายตา พร้อมระบุ **Agent Recommendation** สั้นๆ 1 บรรทัด และหยุดรอให้อาจารย์เลือกตามกฎ Human Choice Gate
4. **Visual Asset & Textbook Provenance**: ระบุชื่อไฟล์รูปภาพ, ความละเอียดต้นฉบับจริง (Native pixels & scale factor), ขนาดพิกเซล, Chapter, Figure Number, เลขหน้า Book Page จากตำราจริง และตารางเปรียบเทียบรูปที่พิจารณาจากตำราหลัก (Best-Figure Selection Gate)
5. **1:1 Spoken Script (บทพูดภาษาไทยธรรมชาติ)**: บทพูดความยาวตามโมเดล 4-Tier Dynamic Pacing ที่สอดคล้อง 1:1 กับ Bullet ทุกข้อ โดยไม่มีการอ่านหัวข้อนำหน้า (Standard 21)
6. **Clinical Transition Hook**: ประโยคเชื่อมโยงทางคลินิกไปยังสไลด์ถัดไป (`*Transition*: ...`) ห้ามตกหล่นเด็ดขาด
7. **Staff Defense Trap (Spotlight Examination Trap)**: ข้อสอบถาม-ตอบเจาะลึกสไตล์อาจารย์ที่ปรึกษา (Staff Q&A) ครอบคลุมกลไกชีวกลศาสตร์ พยาธิสภาพ และคำตอบมาตรฐานแพทย์ประจำบ้าน
8. **Line-by-Line Textbook Citation Verification Table**: ตารางตรวจสอบความถูกต้องแบบบรรทัดต่อบรรทัด ระบุชื่อตำรา, เลขหน้าเล่มจริง (Book Page), เลขหน้า PDF, ข้อความจริงภาษาอังกฤษ (Verbatim quote), และผลการตรวจสอบ (PASS 100%)

> [!NOTE]
> **กฎการเรียนรู้สองทาง (Two-Way Continuous Learning Protocol)**:
> เมื่อผู้ใช้ให้คำแนะนำ ติชม หรือสั่งปรับแก้ข้อความในสไลด์ใดๆ ตัวแทน AI จะต้องอัปเดตข้อกำหนดนั้นลงใน `USER_INSTRUCTIONS_MASTER.md` และซิงก์กลับไปยังแม่แบบส่วนกลางและหน่วยความจำระบบทันที
>
> **กฎห้ามย้อนกลับไปใช้สำนวนยาว (No Regressive Lengthening Rule)**:
> ในการรัน Audit สไลด์ที่ได้รับการขัดเกลาเป็น Option B (Ultra-Lean) แล้ว ตัวแทน AI จะต้องทำหน้าที่เป็น Quality Guard ตรวจสอบความถูกต้องโดย **ห้ามเขียนย้อนกลับไปเป็นประโยคยาวเทอะทะเด็ดขาด** ให้คงความสั้นกระชับ คมชัด และตัวเลขสถิติที่แม่นยำไว้เสมอ

---

## หมวดที่ 4: ทะเบียนคำศัพท์ทางการแพทย์และสำนวนต้องห้าม (Clinical Terminology & Banned Registry)

เพื่อรักษาความเป็นธรรมชาติของภาษาพูดแพทย์ ให้ใช้ศัพท์เทคนิคภาษาอังกฤษล้วน โดยห้ามใช้คำแปลไทยที่แข็งทื่อ คำไทยโบราณ หรือคำคุณศัพท์เกินจริง:

### 1. คำศัพท์การบริบาลและผู้ป่วย (Clinical & Patient Care)
1. **Amputation / Limb Loss**: ห้ามใช้คำว่า *"สูญเสียรยางค์"* หรือ *"การตัดรยางค์"*
2. **Amputee / Patient**: ห้ามใช้คำว่า *"ผู้พิการแขนขาขาด"* หรือ *"คนไข้ตัดขา"*
3. **Residual limb**: ห้ามใช้คำว่า *"ตอขา"* หรือ *"stump"* ในบทพูดและการบรรยายเด็ดขาด ให้ใช้คำว่า **"residual limb"** หรือ **"ปลาย residual limb"** เสมอ เพื่อความเป็นมืออาชีพและเคารพศักดิ์ศรีผู้ป่วย
4. **Epidemiology**: ห้ามใช้คำว่า *"ระบาดวิทยา"* หรือ *"แบบแผนทางระบาดวิทยา"*
5. **Etiology**: ห้ามใช้คำว่า *"สาเหตุการเกิดโรค"*
6. **Global Demographics**: ตัดคำว่า *"Regional"* ออก เว้นแต่จะระบุเปรียบเทียบข้อมูลระดับภูมิภาคชัดเจน
7. **Deformity**: ห้ามใช้คำว่า *"ความพิการ"* หรือ *"เกิดความพิการสูงสุด"* ให้ใช้คำว่า **"Deformity"** หรือ *"ข้อผิดรูป"*

### 2. คำศัพท์กายวิภาคและชีวกลศาสตร์ (Anatomy & Biomechanics)
8. **Patella**: ห้ามใช้คำว่า *"ลูกสะบ้า"* หรือ *"กระดูกสะบ้า"* ให้ใช้คำว่า **"Patella"** ทับศัพท์ภาษาอังกฤษโดยตรง
9. **Tibia**: ห้ามใช้คำว่า *"กระดูกหน้าแข้ง"* ให้ใช้คำว่า **"Tibia"** หรือ **"กระดูก Tibia"**
10. **Fibula & Fibular head**: ให้ใช้คำว่า **"Fibula"** และ **"Fibular head"** แทนคำว่า *"กระดูกน่อง"* หรือ *"หัวกระดูก Fibula"*
11. **Scapula**: ห้ามใช้คำว่า *"กระดูกสะบัก"* ให้ใช้คำว่า **"Scapula"**
12. **Pelvic stability**: ห้ามใช้คำแปลไทยที่ฟังแล้วแปลกหรือประดิษฐ์อย่าง *"เพื่อรักษาแนวเชิงกราน"* ให้ใช้คำว่า **"Pelvic stability"**
13. **Pelvic movement**: ห้ามแปลว่า *"การเคลื่อนไหวเชิงกราน"* ให้ใช้คำว่า **"Pelvic movement"** ทับศัพท์ตรงๆ
14. **Circumduction**: ห้ามใช้คำว่า *"เหวี่ยงขาอ้อมข้าง"* ให้ใช้ **"Circumduction"** ทับศัพท์ตรงๆ
15. **Prosthetic / Affected side**: เมื่อพูดถึงตำแหน่งเชิงกรานหรือข้างที่ทำหัตถการ ให้ใช้ **"ฝั่ง Prosthetic side"** หรือ **"Affected side"** แทนการพูดว่า *"ข้างที่ตัด"*
16. **แนว AP และ แนว ML**: เมื่อพูดถึงมิติหรือระนาบของเบ้าหรืออุปกรณ์ ให้ใช้ **"แนว AP"** (Antero-Posterior) และ **"แนว ML"** (Medio-Lateral) แทนการพูดว่า *"แคบหน้าหลังแต่กว้างซ้ายขวา"*
17. **Biomechanics**: ในบทพูดบรรยาย ให้ใช้ทับศัพท์ว่า **"ในแง่ Biomechanics"** หรือ **"ด้าน Biomechanics"** แทนคำว่า *"ในแง่ชีวกลศาสตร์"* หรือ *"ทางชีวกลศาสตร์"*
18. **Lever Arm**: คำว่า Lever arm / Moment arm ให้ใช้ทับศัพท์ตรงๆ ว่า **"Lever arm"** ห้ามแปลแยกคำเป็นคำประหลาดอย่าง *"แขนงคาน"*, *"คานงัด"*, หรือ *"ก้านคาน"* เด็ดขาด
19. **Pronation / Supination & Rotation**: เมื่อกล่าวถึงการเคลื่อนไหวของปลายแขนหรือข้อต่อ ให้ใช้ศัพท์เทคนิคภาษาอังกฤษโดยตรงว่า **"Pronation/Supination"**, **"Pronation และ Supination"**, หรือ **"Pronation/Supination torque"** ห้ามแปลว่า *"การคว่ำหงายมือ"*, *"คว่ำ-หงาย"*, หรือ *"แรงหมุนคว่ำหงายมือ"* เด็ดขาด
20. **ห้ามใช้คำว่า "ชีวภาพ" พ่วงท้ายข้อต่อเด็ดขาด (No "ชีวภาพ / biological" for natural joints)**: ห้ามแปล biological knee / biological joint / biological elbow ว่า "ข้อเข่าชีวภาพ", "ข้อต่อชีวภาพ", หรือ "ข้อศอกชีวภาพ" เด็ดขาด ให้ใช้คำว่า **"ข้อเข่า"** (หรือ *"knee"*), **"ข้อศอก"** (หรือ *"elbow"*), และ **"ข้อต่อ"** ตามภาษาพูดแพทย์ที่เป็นธรรมชาติ
21. **Prosthetic socket**: ห้ามใช้คำว่า *"เบ้าเทียม"* ให้ใช้คำว่า **"เบ้าขาเทียม"** หรือ **"Prosthetic socket"**

### 3. คำศัพท์การบริบาล ฟื้นฟู และอุปกรณ์ (Clinical Management & Setup)
17. **figure of eight**: ห้ามแปลว่า *"ทแยงไขว้เป็นรูปเลขแปด"* ให้ใช้คำว่า **"figure of eight"** ทับศัพท์โดยตรง
18. **การลดบวมอย่าง aggressive**: ห้ามใช้คำว่า *"การลดบวมเชิงรุก"* ให้ใช้ภาษาพูดแพทย์ที่เป็นธรรมชาติว่า **"การลดบวมอย่าง aggressive"**
19. **Around the clock**: ให้ใช้คำว่า **"around the clock"** แทนคำว่า *"Scheduled"* เมื่อพูดถึงการให้ยาแบบต่อเนื่องสม่ำเสมอ
20. **Contraindication**: ให้ใช้คำว่า **"contraindication"** แทนคำว่า *"ข้อห้าม"* เพื่อความเป็นธรรมชาติของภาษาแพทย์
21. **ตัดคำว่า "ส่วนปลาย"**: เมื่อพูดถึงการคุมการอักเสบของแผลผ่าตัด ไม่ต้องใส่คำว่า *"ส่วนปลาย"* ให้ใช้ *"เพื่อคุมการอักเสบ"*
22. **Wheelchair & Mobility Setup**: ห้ามใช้ศัพท์เบิกประกันสหรัฐฯ อย่าง *"Durable Medical Equipment (DME)"*
23. **Rehabilitation Roadmap & Realistic Goals**: ห้ามใช้ศัพท์กฎหมายที่ผิดบริบทอย่าง *"Rehabilitation Continuum Consent"*
24. **ห้ามพิมพ์ไทยซ้ำซ้อนหลังภาษาอังกฤษ (No Redundant Thai Duplication)**: ห้ามใส่คำแปลไทยซ้ำหลังคำศัพท์อังกฤษ เช่น ตัด `Anatomical Self-Suspension (แขวนยึดตัวเองตามกายวิภาค)` ให้ใช้ภาษาอังกฤษอย่างเดียว

### 4. กฎเหล็กการสะกดตัวเต็มห้ามใช้ตัวย่อกำกวม (Strict Full-Term & Anti-Ambiguity Rule)
25. **ห้ามใช้ตัวย่อ PLP และ RLP เด็ดขาด ให้ใช้คำเต็ม Phantom Limb Pain และ Residual Limb Pain เสมอ** (ในกรณีที่มีเนื้อหาเกี่ยวกับอาการปวดตอขาหรืออาการปวดรยางค์ลวง):
   - ทั้งใน Slide Title, Bullets, Presenter Notes, Script, และ Trap Q&A ต้องเขียนสะกดเต็มคำว่า **"Phantom Limb Pain"** และ **"Residual Limb Pain"** ทุกจุด ห้ามใช้ตัวย่อภาษาอังกฤษ `PLP` หรือ `RLP` เด็ดขาด
26. **ห้ามใช้คำย่อกำกวม/ไม่มาตรฐานบนสไลด์และโน้ต (Ambiguous Shorthand Ban)**:
   - **ห้ามใช้เด็ดขาด:** `NS` (*not significant* — เพราะชนกับ *Normal Saline* ให้เขียน `not significant` หรือ `(not sig.)`), `lit` (ใช้ `range` / `published cohorts`), `SQ` (ใช้ `Subcutaneous` / `Subcut.`), `meta` เดี่ยวๆ (ใช้ `meta-analysis`), `q2h` (ใช้ `every 2 h` / `every 2 hours`), และ `CTR` ก่อนนิยามคำเต็ม `carpal tunnel release` ในสไลด์ก่อนหน้า
   - **เลี่ยงเมื่อมีพื้นที่:** `US` → `Ultrasound`, `27-ga, 5/8-in` → `27-gauge, 5/8-inch`, `avg`/`wks` → `average`/`weeks`, `1st-AM` → `first-morning`

### 5. ทะเบียนสำนวนและคำคุณศัพท์เกินจริงต้องห้าม (Master Banned Terms Registry - Zero Hype)
ห้ามปรากฏคำศัพท์ สำนวน หรือคำคุณศัพท์เกินจริงเหล่านี้ทั้งบนสไลด์ ในบทพูด หรือในเอกสารประกอบโดยเด็ดขาด:

| คำศัพท์ / สำนวนต้องห้าม | บริบทที่ถูกสั่งห้าม | คำหรือวิธีแก้ที่ต้องใช้แทน |
| :--- | :--- | :--- |
| **"Landmark" / "ระดับ Landmark" / "Landmark RCT"** | ผู้ใช้ย้ำชัดเจนว่าไม่ชอบคำนี้ | **ห้ามใช้คำว่า Landmark เด็ดขาด.** ให้ระบุชื่องานวิจัยเป็นกลางทางวิชาการ เช่น *"งานวิจัย RCT โดย [ผู้วิจัย] และคณะ"* |
| **"Workhorse level"** | สแลงอเมริกันที่ไม่เป็นมืออาชีพ | อธิบายทางคลินิกตรงๆ เช่น *"ระดับการรักษาที่พบบ่อยและได้ผลดี"* |
| **"Axiom"** | ศัพท์ปรัชญาที่ดูประดิษฐ์ | ใช้ *"หลักการทางคลินิก"* หรือ *"Core principle"* |
| **"กฎเหล็กทางศัลยกรรม" / "กฎเหล็กทางคลินิก"** | สำนวนเว่อร์และดราม่าเกินจริง | ใช้ *"หลักการสำคัญคือ"*, *"มาตรฐานทางคลินิกคือ"*, หรือ *"ข้อควรระวังสำคัญคือ"* |
| **"ท่องให้ขึ้นใจเลยนะครับ"** | น้ำเสียงเหมือนครูสั่งนักเรียน ดูถูกผู้ฟัง | ตัดออก บรรยายด้วยน้ำเสียงวิชาการระดับเพื่อนร่วมวิชาชีพแพทย์ |
| **"แพทย์ PM&R จะสั่งจ่าย... เสมอ"** | คำพูดเผด็จการ บังคับ rigid เกินจริง | ใช้น้ำเสียงยืดหยุ่นทางคลินิก เช่น *"ในทางเวชศาสตร์ฟื้นฟู จึงมักพิจารณา..."* หรือ *"การฟื้นฟูจึงมักพิจารณาออกแบบเป็น..."* |
| **"หลักการชีวกลศาสตร์พื้นฐาน" / "ชีวกลศาสตร์พื้นฐาน"** | ผู้ใช้ไม่ชอบคำนี้ ดูประดิษฐ์และซ้ำซาก | ใช้ *"ข้อปฏิบัติและข้อห้ามของการ..."*, *"หัวใจสำคัญของการ..."*, หรือ *"แนวทางการ..."* |
| **"บนเสื่อกายภาพ"** | สำนวนแปลกและแข็งทื่อในภาษาพูดแพทย์ | ตัดคำว่า "บนเสื่อกายภาพ" ออก โดยระบุชื่อท่าออกกำลังกายตรงๆ |
| **"เพื่อรักษาแนวเชิงกราน"** | สำนวนประดิษฐ์และฟังดูขัดหูในบริบทชีวกลศาสตร์ | ใช้ศัพท์การแพทย์ที่เป็นมาตรฐานว่า *"เพื่อเพิ่ม Pelvic stability และป้องกันไม่ให้เดินหลังแอ่นชดเชย"* |
| **"แนวทแยงหลัก" / "แนวทแยง"** | ศัพท์เรขาคณิตทฤษฎีที่คนฟังแล้วงง ไม่สื่อถึงการเคลื่อนไหว | แปลงเป็นหน้าที่ทางคลินิกตรงๆ เช่น *"เน้นการเคลื่อนไหวไปข้างหน้า (Forward progression) ควบคู่กับ Pelvic movement ที่สมมาตร"* |

---

## หมวดที่ 5: กฎบทพูดและการเล่าเรื่อง (Spoken Script & Rich Clinical Storytelling)

1. **สถาปนาปรัชญา "Lean Slide, Rich Script" (Auditorium Pro Ideal)**:
   - **บนจอฉาย (PowerPoint)**: ใช้สไลด์แบบ **Option B (Selective Ultra-Lean: 6–12 คำต่อการ์ด)** เพื่อให้ตัวหนังสือใหญ่ `14.0 pt` อ่านง่าย โปร่งสบายตา และมีระยะปลอดภัยชัดเจน
   - **ใน Speaker Notes (`.pptx` + `PRESENTER_NOTES_MASTER.md` เท่านั้น — งดสร้าง `.docx` อัตโนมัติ เว้นแต่ผู้ใช้สั่ง `--docx`)**: บรรจุ **บทพูดละเอียดเชิงลึก (กลไกพยาธิสภาพ, เหตุผลทางคลินิก, และข้อควรระวัง)** โดยให้เวลาที่ระบุบน Slide 01 ตรงกับผลรวม Timestamp (`[MM:SS - MM:SS]`) ของทั้งเด็ค (เช่น `18–20 นาที` สำหรับ 17 สไลด์ หรือ `72–75 นาที` สำหรับ 88 สไลด์ Grand Rounds) และคง 1:1 Character Parity ระหว่าง `.pptx Notes` กับ `PRESENTER_NOTES_MASTER.md`
2. **การเล่าเรื่องตามภาพ สี และข้อมูลจริง (Figure & Color-Synced Narrative)**:
   - สำหรับสไลด์ที่มีภาพแผนภาพคู่หรือภาพเปรียบเทียบ: ให้เดินเรื่องเชื่อมโยงตามภาพและสีจริงบนสไลด์โดยตรงอย่างเป็นธรรมชาติ (เช่น *"ภาพด้านบน...", "แถบสีเขียวอมฟ้าด้านบน..."*) **ห้ามพูดชื่อสีหรือตัวเลขที่ไม่ตรงกับสไลด์จริง** (เช่น ห้ามพูด `"100%"` ถ้าตำราไม่ได้ระบุค่านี้ หรือห้ามพูด `"สีน้ำเงิน"` ถ้ากราฟจริงใช้สีเขียวอมฟ้า)
3. **ห้ามอ่านหัวข้อ, ห้ามใส่เลขข้อ, ห้ามวงเล็บ/เลขหน้า, และห้าม `"เสมอ"` (Standard 21 & Script Cleanliness)**:
   - บทพูดต้อง NEVER เริ่มต้นประโยคด้วยการอ่านชื่อหัวข้อตัวหนาภาษาอังกฤษ
   - **ห้ามใส่เลขข้อ `1., 2., 3., 4., 5.` คั่นแต่ละประโยคในบทพูดเด็ดขาด**: ร้อยเรียงเป็น **Flowing Clinical Paragraphs**
   - **ห้ามใส่วงเล็บ `(...)`, เลขหน้า `(p. X)` / `pp.`, หรือคำฟันธง `"เสมอ"` ลงใน `script`** (เก็บเลขหน้าไว้เฉพาะใน `Ref:` ใต้สไลด์และ `trap` สำหรับอ้างอิงตอบอาจารย์)
4. **กฎการเชื่อมโยงพยาธิสภาพสู่การปฏิบัติการทางคลินิก (Standard 20 - Mechanism-to-Action Script Coherence)**:
   - เมื่อพูดถึงภาวะอันตรายหรือพยาธิสภาพ ห้ามพูดพยาธิสภาพมาลอยๆ แล้วจบประโยค
   - ต้องเชื่อมโยง 3 ขั้นตอนเสมอ: **เกิดอะไรขึ้นทางพยาธิสภาพ $\rightarrow$ ส่งผลร้ายอย่างไร $\rightarrow$ การปฏิบัติการทางคลินิกของแพทย์คืออะไร**
5. **บังคับใส่ประโยคเชื่อมโยงทางคลินิก (Clinical Transition Hook)**:
   - ทุกสไลด์ต้องมีประโยคเชื่อมโยง (`*Transition*: ...`) ไปยังสไลด์ถัดไปเสมอ ห้ามตัดทิ้งเด็ดขาด
6. **มาตรฐานบทพูดสไลด์ท้ายเรื่อง & ห้ามขอบคุณซ้ำ (Closing Academic Defense & No Double Thank-You)**:
   - แยกหน้าที่ให้ชัดระหว่าง **สไลด์รองสุดท้าย (`Take-Home Clinical Pearls`)** (สรุปแก่นทางคลินิก + ชวนถาม Q&A) กับ **สไลด์สุดท้าย (`Primary Textbook References`)** (เชื่อมเข้าสู่แหล่งอ้างอิงแล้วกล่าวปิดขอบคุณอาจารย์ที่ปรึกษาและคณาจารย์เพียงครั้งเดียว + เปิดฟลอร์ Q&A — **ห้ามกล่าว `"ขอบพระคุณ... ครับ"` ซ้ำติดกัน 2 หน้า**)

---

## หมวดที่ 6: มาตรฐานตำราและ Reference (Primary Textbook & Citation Standards)

1. **ยึดถือเฉพาะตำราหลักที่ได้รับการอนุมัติในโฟลเดอร์ `./textbook reference/` ของโปรเจกต์นั้นๆ เสมอ (Project-Specific Primary Textbooks)**:
   - **กลไกการสลับโปรเจกต์ (Dynamic Multi-Project Architecture)**: เมื่อสลับไปทำโปรเจกต์ใหม่ AI จะอ่านเฉพาะตำรา PDF ที่วางอยู่ใน `./textbook reference/` ของโปรเจกต์ใหม่นั้นเท่านั้น
{{TEXTBOOK_LIST}}
2. **ห้ามนำข้อมูลนอกเหนือจากใน `./textbook reference/` มาใช้เด็ดขาด (Strict Zero External Information & Zero Hallucination Rule)**:
   - **ห้ามใช้ข้อมูลจากแหล่งภายนอกหรือความรู้ทั่วไปของ AI (Internal Weights)**: ทุกข้อเท็จจริงทางการแพทย์ ตัวเลขสถิติ เปอร์เซ็นต์ เกณฑ์การวินิจฉัย ขนาดยา ชีวกลศาสตร์ และคำแนะนำในการรักษา (ทั้งบน Slide Bullets, ตาราง, บทพูด 1:1 Spoken Script, และ Staff Q&A Defense Trap) **จะต้องมีที่มาจากไฟล์ตำราในโฟลเดอร์ `./textbook reference/` ของโปรเจกต์นั้นๆ เท่านั้น**
   - ห้ามดึงข้อมูลจากอินเทอร์เน็ต งานวิจัยภายนอก ตำราเล่มอื่นที่ไม่ได้อยู่ในโฟลเดอร์ หรือคิดค้น/อนุมานตัวเลขและเกณฑ์ทางคลินิกขึ้นมาเองโดยเด็ดขาด หากข้อมูลใดไม่มีระบุใน `./textbook reference/` ห้ามนำมาใส่ในสไลด์หรือบทพูด และให้แจ้งผู้ใช้อย่างโปร่งใส
3. **แบนสไลด์และเอกสารรุ่นพี่เด็ดขาดในทุกโปรเจกต์ (Universal STRICT BAN on Copying Senior Slides)**:
   - ห้ามคัดลอก ดึงข้อความ ดึงรูปภาพ หรืออ้างอิง Reference จากสไลด์รุ่นพี่เด็ดขาด ให้ค้นหาจากตำราหลักใน `./textbook reference/` เท่านั้น
4. **มาตรฐานอ้างอิงแบบ Claim-ID & Native Superscripts (`¹ ² ³ ⁴`) + References Slide**:
   - **บนเนื้อหาสไลด์:** เลิกพิมพ์ชื่อตำรายาวๆ แทรกในการ์ด ใช้ Native Superscript (`[[1]]` → `¹`) แปะไว้ที่ **ท้ายคำ** เท่านั้น (**ห้ามแปะชิดตัวเลข** เช่น `A1²` ต้องเขียน `A1 pulley²`) และใช้ Unicode superscript (`²`, `³`) ในแกนกราฟเมื่ออ้างอิงรายชุดข้อมูล
   - **Footer ทุกหน้า:** ซ้ายล่างแสดงเฉพาะเลขหน้าพิมพ์จริง (`Ref: [1] p. 197 | [2] pp. 575–576` — Book Page Only, ห้ามใส่ PDF Page) และขวาล่างแสดงเลขหน้า `01 / N` ทุกหน้า
   - **สไลด์สุดท้าย (`Primary Textbook References`):** แสดงรายชื่อตำราฉบับเต็ม, บท/ช่วงหน้าจริงที่ใช้ทั้งเด็ค, และภาพปกตำราที่สกัดอัตโนมัติ (หรือไอคอนหนังสือมาตรฐานถ้า PDF ไม่มีปก) โดยทุก ID บนสไลด์, `Ref:` Footer, และ References Slide ต้องตรงกัน **1:1 (0 Phantom / 0 Orphan)**
   - เลขหน้าไฟล์ PDF ใช้ตรวจสอบเฉพาะภายใน Audit Dossier และ `claim_registry` เท่านั้น
6. **มาตรฐานกราฟบน Google Slides & PowerPoint (`fix_pptx_charts_gslides.py`)**:
   - กราฟ Native ทุกชุดต้องแปลง `<c:multiLvlStrRef>` → `<c:strRef>` (`<c:noMultiLvlLbl val="0"/>`) และแปลงค่าเปอร์เซ็นต์เป็นทศนิยม `0%` ทั้ง XML + embedded `.xlsx` เพื่อป้องกัน Google Slides แสดงแกน Y เป็น `1..8` และตัดเครื่องหมาย `%`
7. **ตัวเลขสถิติและค่าทางคลินิกจากตำราต้องยกมาแบบเป๊ะ 100% ห้ามดัดแปลงเด็ดขาด**:
   - เมื่อดึงตัวเลขใดๆ จากตำราใน `./textbook reference/` (เช่น เปอร์เซ็นต์ %, ช่วงตัวเลข range, จุดทศนิยม, ขนาดยา, องศามุมข้อต่อ, ระยะเวลาฟื้นตัว, หรือค่าสถิติ) **ต้องยกตัวเลขตามที่เขียนในตำรามาแบบเป๊ะๆ 100% คำต่อคำ**
   - **ห้ามปัดเศษ (No Rounding)**, **ห้ามแปลงเป็นค่าประมาณคร่าวๆ**, **ห้ามยุบรวมหรือเปลี่ยนขอบเขตช่วงตัวเลข (Range)**, และ **ห้ามแปลงหน่วยหรือคำนวณตัวเลขใหม่เอง** เด็ดขาด (ทั้งบนหน้าสไลด์, ในตาราง, ในบทพูด 1:1 Spoken Script, และใน Staff Q&A Defense Trap)

---

## หมวดที่ 7: มาตรฐานรูปภาพ ตาราง และกฎ Smart Visual Decision Rule (Visual Asset & Smart Layout Standards)

1. **กฎ Smart Visual Decision Rule & การเสนอ 3 ตัวเลือกเมื่อไม่มีรูปในตำรา (Smart 3-Way Comparison)**:
   - **กรณีที่ 1 (สังเคราะห์ข้ามหลายเล่ม หรือเปรียบเทียบหลายวิธี)** $\rightarrow$ สร้างตารางเปรียบเทียบ Native บน PowerPoint (`add_table_slide`) เพื่อให้ตัวอักษรใหญ่ คมชัด และรวมข้อมูลข้ามเล่มได้ครบ
   - **กรณีที่ 2 (มีรูปภาพคลินิก/ไดอะแกรม หรือมีตารางมาตรฐาน/กล่องข้อความสำคัญในตำรา)** $\rightarrow$ สกัดรูปหรือ Crop ตาราง/กล่องข้อความต้นฉบับจากตำราความละเอียดสูง (4x Zoom, ~300 DPI) มาใส่ในการ์ดขาวฝั่งขวา (`add_split_content_slide` พร้อมขยายกรอบขาว `right_width = 5.50"–6.50"`) คู่กับ Bullet ฝั่งซ้าย
   - **กรณีที่ 3 (ไม่มีรูปภาพ ไดอะแกรม หรือตารางที่ตรงประเด็นในตำราหลัก)** $\rightarrow$ **บังคับเรนเดอร์ภาพจริงเปรียบเทียบทั้ง 3 Options ให้ผู้ใช้เคาะเลือกเสมอ**:
     - **Option 1: AI-Generated Clean 2D Medical Vector Infographic** (`add_split_content_slide` พร้อมภาพเวกเตอร์ทางการแพทย์ที่การ์ดขวา)
     - **Option 2: Native Comparison Table** (`add_table_slide` สรุปตารางเปรียบเทียบมิติคลินิก)
     - **Option 3: Full-Width Content Card** (`add_split_content_slide(..., image_file=None)` การ์ดเนื้อหาเต็มหน้า)
   - **กรณีที่ 4: Clinical Algorithms, Pathways & Progressive Continuum (3–5 สเตจ)** $\rightarrow$ สร้าง Flowchart / Continuum ทางคลินิกแบบ Native บน PowerPoint (`add_algorithm_slide`)
2. **รูปภาพต้องตรงกับเนื้อหาจริงครบทุกประเด็น 100% (Visual Parity & Multi-Panel Matching)**:
   - รูปภาพฝั่งขวาต้องสะท้อนหัตถการ พยาธิสภาพ หรืออุปกรณ์ที่กำลังพูดถึงในสไลด์นั้นอย่างแม่นยำ
   - หากสไลด์เปรียบเทียบ 2 ภาวะหรือ 2 วิธีการรักษา ต้องสร้างภาพประกอบแบบ Dual-Panel Composite (Panel A / Panel B) ให้เห็นครบทั้งสองอย่างตั้งแต่แรกเสมอ
3. **รูปภาพต้องช่วยอธิบายประเด็นทางคลินิก (Explanatory Clinical Power)**:
   - รูปภาพที่ดีต้องเสริมความเข้าใจชีวกลศาสตร์ การกระจายแรง หรือพยาธิสรีรวิทยา ไม่ใช่แค่ภาพประดับตกแต่ง
4. **มาตรฐานและข้อกำหนดสำหรับภาพ AI Medical Vector Infographic (Aesthetic, Zero-Header & Canvas Guardrails - Option 1)**:
   - **Standard 25 (Zero Embedded Header Rule - ห้ามใส่หัวข้อเรื่องบนผืนผ้าใบภาพ)**:
     - ห้ามมี Title Banner, Embedded Header หรือข้อความพาดหัวเรื่องขนาดใหญ่แปะอยู่บนสุดของผืนผ้าใบภาพโดยเด็ดขาด
     - บนหน้าสไลด์ PowerPoint มี Native Category Tracker, Native Slide Title และ Figure Title ประจำการ์ดอยู่แล้ว การใส่หัวข้อเรื่องซ้ำบนตัวภาพทำให้สูญเสียพื้นที่แสดงเนื้อหาทางการแพทย์ไป 20–30% และทำให้ดีไซน์ดูรก ซ้ำซ้อน
     - ภาพเวกเตอร์ต้องเริ่มต้นด้วยเนื้อหาทางการแพทย์ทันที (เช่น ไดอะแกรม, คอลัมน์เปรียบเทียบ 3 panels, หรือภาพกายวิภาค) ให้ดูคลีน มินิมอล และไร้รอยต่อ
   - **กฎผืนผ้าใบสีขาวบริสุทธิ์ (Pure White Canvas Verification Gate & Style Bleed Prevention)**:
     - ห้ามใช้พื้นหลังสีเข้ม (Dark Navy Blue) หรือสีอื่น (ส้ม, เขียวมิ้นต์, เทาหม่น) เป็นผืนผ้าใบหลักของภาพเวกเตอร์ที่วางบนการ์ดขาวฝั่งขวาเด็ดขาด
     - ภาพเวกเตอร์ทุกภาพต้องอยู่บนผืนผ้าใบสีขาวบริสุทธิ์ (`#FFFFFF`) หรือโปร่งใส โดยมุมภาพทั้ง 4 ด้าน (Corner pixels) ต้องมีค่าสีเฉลี่ย `RGB >= 220` (ทดสอบผ่าน `slide_auditor_cli.py check-visual-compliance`) เพื่อให้ขอบภาพกลืนเป็นเนื้อเดียวกับการ์ดสีขาวของการนำเสนออย่างไร้รอยต่อ (Seamless Card Integration)
     - **ป้องกันภาวะ Style Bleed**: แยกแยะอย่างเด็ดขาดระหว่าง "โปสเตอร์อินโฟกราฟิกทางการแพทย์ขนาด A4" (ซึ่งอนุญาตให้ใช้ธีม Dark Navy/Teal/Mint ตาม User Global Rules ได้) กับ "ภาพประกอบบนสไลด์นำเสนอ PowerPoint" (ซึ่งวางอยู่บน White Container Card จึงต้องเป็น Pure White `#FFFFFF` 100% เสมอ)
   - **สไตล์ภาพ (Visual Style)**: Minimalist flat 2D medical vector infographic บนพื้นหลังสีขาวบริสุทธิ์ (`#FFFFFF`)
   - **ชุดสี (Color Palette)**: ใช้ชุดสีทางการแพทย์ระดับพรีเมียม สอดคล้องกับธีมงานนำเสนอ: Deep Navy Blue (`#0F172A`, `#1E293B`), Teal/Mint (`#0D9488`, `#14B8A6`, `#2DD4BF`), Slate Gray (`#64748B`, `#94A3B8`)
   - **กฎความสะอาดของภาพ (Visual Cleanliness)**:
     - ใน Prompt หลังบ้าน ต้องระบุคีย์เวิร์ดมุมและท่าทางให้เจาะจงระดับองศา แต่บนตัวภาพต้องสะอาด ไม่วาดตัวเลขหรือเส้นประคำนวณลอยบนตัวคน ให้ท่าทางที่ถูกต้องทำหน้าที่สื่อสารด้วยตัวเอง (Anatomy speaks for itself)
     - ภาพการยืดเหยียดและออกกำลังกาย: ยึดหลัก Balanced Minimalist ห้ามใส่เส้นโค้งวัดมุม (Angle arc) หรือตัวเลของศาลอยบนภาพ ให้ระบุตัวเลของศาและเวลาไว้ที่ Subtitle ใต้การ์ดหรือ Bullet ข้อความบนสไลด์เท่านั้น
     - **ข้อยกเว้น**: อนุญาตให้มีเส้นโค้งวัดมุม (Angle arc) ได้เฉพาะสไลด์ที่มีหัวข้อเรื่องการตรวจประเมินมุมทางคลินิกโดยตรง (Clinical / Goniometric Assessment) เท่านั้น
   - **ข้อห้ามเด็ดขาด (STRICT PROHIBITIONS)**:
     - ห้ามภาพคน AI เสมือนจริง (Photorealistic humans/faces) เด็ดขาด
     - ห้ามภาพ 3D สไตล์พลาสติกมันวาว (Glossy/Plastic sheen), ภาพการ์ตูนเด็กเล่น หรือ Corporate clipart เด็ดขาด
     - ห้ามภาพที่มีความสยดสยอง (Gore) หรืออวัยวะบิดเบี้ยวผิดรูป
   - **การระบุที่มาใต้ภาพอย่างโปร่งใส (Mandatory Academic Transparency Attribution)**:
     - บรรทัด `Source:` ใต้รูปบนหน้าสไลด์ ต้องระบุคำว่า AI ชัดเจน เช่น `figure_source="AI-Generated Clinical Infographic | Based on <Textbook Reference>"` เสมอ ห้ามอ้างอิงเฉพาะชื่อตำราลอยๆ โดยไม่มีคำว่า AI-Generated
     - แถบ Footnote ด้านล่างสุดของสไลด์ยังคงอ้างอิงเฉพาะเลขหน้าจริงของตำราหลัก (Book Page) เท่านั้น
5. **ขั้นตอนบังคับ: คัดเลือกรูปที่เหมาะที่สุดจากตำราหลัก (Best-Figure Selection Gate)**:
   - ก่อนจะพิจารณาใช้ภาพ AI หรือตาราง ตัวแทน AI ต้องเปิดค้นหาภาพจากตำราหลักก่อนเสมอ และต้องระบุเลขหน้าพร้อมขนาดพิกเซลจริงใน Element 4 ของ Audit Dossier
6. **การผสานบทพูดกับรูปภาพ**:
   - เมื่อรูปภาพแสดงกลไกหรือพยาธิสภาพใด บทพูดต้องร้อยเรียงอธิบายกลไกนั้นให้สอดคล้องกันอย่างแนบเนียน
7. **โปรโตคอลเมื่อโควตา AI Gen ภาพหมด (AI Image Generation Quota Fallback Protocol)**:
   - หากโควตา API ภาพหมด ให้สลับไปใช้ **Option 2: Native Comparison Table (`add_table_slide`)** หรือ Crop ตาราง/แผนภาพที่มีอยู่ในตำรามาใส่แทนทันที โดยแจ้งผู้ใช้อย่างโปร่งใส
8. **กฎการตัดสินใจแบบมีส่วนร่วม (Human Choice Gate & Proactive Recommendation)**:
   - **ห้ามตัดสินใจเปลี่ยนประเภทสไลด์หรือเลือกรูปภาพฝ่ายเดียว (No Unilateral Decision)**
   - สกัดตัวเลือกจริงมาทำตารางเปรียบเทียบใน Element 4 (Candidate A1/A2 จากตำรา, Option B ภาพเวกเตอร์ 2D, Option C ตาราง Native Table, Option D การ์ดข้อความล้วน)
   - ระบุ *"ข้อเสนอแนะประกอบการตัดสินใจ (Agent Recommendation)"* ใต้ตารางเสมอ พร้อมอธิบายเหตุผลทางคลินิกอย่างสุภาพ
   - **บังคับหยุดรอคำสั่ง (Hard Stop Protocol)**: หลังจากแสดงตาราง Element 4 AI **ต้องหยุดพิมพ์ทันที** เพื่อรอให้อาจารย์เป็นผู้ตัดสินใจเคาะเลือกตัวเลือก ห้ามแอบแก้โค้ดหรือคอมไพล์เด็กล่วงหน้าก่อนได้รับคำสั่งเด็ดขาด

---
## หมวดที่ 8: มาตรฐาน Journal Club Mode (`--mode jc` — Senior Glanceability & Official Checklists)

ใช้เมื่อสร้างสไลด์นำเสนอเปเปอร์ Journal Club (แยกจากสไลด์ติวสอบบอร์ดที่ใช้ `./textbook reference/`):
1. **100% Authentic Paper Figures & Tables (`4x` Zoom) + Direct Highlight Boxes**:
   - ใช้ภาพ Crop ตาราง/Flowchart/Forest plot จาก PDF งานวิจัย (`4x`) เป็นหลักแบบเต็มความสูง (`h ~ 6.08"`) พร้อมตีกรอบ Coral Red (`#DC2626`) / Teal (`#0D9488`) ครอบเซลล์หรือ `p`-value สำคัญโดยตรง (ตรวจพิกัดจากภาพ preview ทุกหน้าก่อนส่ง)
   - ใช้ Native Table เฉพาะตารางสังเคราะห์ที่ไม่มีในเปเปอร์ (เช่น Baseline Audit, Limitations, {{INSTITUTION}} Clinical Bridge)
2. **Official Checklists Only (`1 Section per Slide`, Never Self-Generated)**:
   - ใช้ PDF แบบฟอร์มจริงจาก `~/.gemini/config/skills/karpathy-paper-lab/assets/checklists/` (**CASP UK 11 แบบฟอร์ม** หรือ **NIH NHLBI Before-After / Case Series** สำหรับ Pre-Post ไม่มี Control) แยก **1 Section ต่อ 1 สไลด์** (ซ้ายแบบฟอร์มพร้อม `✓` `h ~ 6.10"`, ขวาการ์ดสรุป Verdict + เหตุผลสั้น 1 บรรทัด)
3. **Senior Glanceability (`4-6 sec scan`), `01 / N` Pagination & English Speaker Notes Default**:
   - ถอด Category Pill, Subtitle ซ้อน, กรอบการ์ดดำรอบรูป, และแถบ Text Takeaway ยาวๆ บนหน้าตารางออก; ใช้ Left-Accent-Bar Borderless Cards, Hero KPI Cards (`114`, `54.4%`, `4.46x`), Outcome Scale Primer Card, Study Strengths Grid, และ Conditional `Safety & Dropout Analysis` (เมื่อมี AE หรือ Attrition > 5-10% / ต่างกันระหว่างกลุ่ม); ย่อ `Ref:` ซ้ายล่างและแสดง `01 / N` มุมขวาล่างทุกหน้า + ใช้ฟอนต์ `Arial` และเช็กสี Badge `"Cannot Tell"`/`"Not Reported"` ให้เป็นสีเหลือง (`AMBER`) เสมอ
   - สำหรับ `--lang en` (Default ของ JC): เขียน Spoken Script, Staff Q&A Defense, และ Transition เป็นภาษาอังกฤษธรรมชาติ 100% ลงใน `.pptx Speaker Notes` + `PRESENTER_NOTES_MASTER.md` (งดสร้าง `.docx` อัตโนมัติ; ส่ง `--docx` เฉพาะเมื่อต้องการพิมพ์แจก; ไม่มีไทยปน, ไม่มีคำ AI Slop หรือ em-dash `—`) พร้อมเก็บรายละเอียดรหัส/ตัวเลขปลีกย่อยไว้ใน Notes ให้ครบถ้วน

---
*แม่แบบต้นฉบับปรับปรุงล่าสุด: 2026-11-25 (สถาปัตยกรรมเอกสาร 8 หมวดหมู่หลัก v2 — ครอบคลุม 5-Layer Claim-ID, Bento Visual-First, Anti-Monotony, Ambiguous Abbreviation Ban, Lean Slide/Rich Script, และ Journal Club fixes)*

---

## หมวดที่ 9: กฎเพิ่มเติมล่าสุด (Two-Way Synced Rules)
- PM&R Slide Hard Dispatch Lock (Zero Coordinator Bypass): แม้เป็นการแก้ไขหรือ Audit เฉพาะ 1-2 สไลด์ (Mode 2) ห้าม Coordinator อ่าน PDF ตำราหรือเสนอปรับสไลด์แบบ Inline เด็ดขาด ต้องส่ง Agent 02 [Sub·Pro] อ่าน ./textbook reference/ + evidence_bundle_raw.json + notes_data_modules/ เพื่อเสนอตัวเลือกก่อน Human Choice Gate และทุกการแก้ไขต้องวิ่งครบสาย Agent 02 [Sub·Pro] -> Agent 03 [Sub·Inherit, PDF-Firewalled] -> audit-deck -> Agent 11 [Sub·Pro] + Agent 12 [Sub·Inherit]
- Chart Data Hygiene & Micro-UX: 1 กราฟ = 1 ตัวหารและ 1 Study Design เท่านั้น; ห้ามผสมสัดส่วนนิ้วกับความชุกโรคร่วมหรือหลายโปรโตคอลบนแกนเดียว; ชื่อแกนต้องไม่กำกวม (เช่น "Trigger Finger in DM" แทน "Diabetes Prevalence"); กราฟแท่งแนวนอนเปรียบเทียบ (1st vs 2nd) ต้องเรียง 1st อยู่เหนือ 2nd ตรงตาม legend ซ้าย->ขวา และล็อก plotArea ให้แกน Y กราฟซ้อนบน-ล่างตรงแนวกัน
- Verbatim claim_registry & Subtitle Superscript Lock: ฟิลด์ quote ใน claim_registry ต้องยกข้อความจริงจากตำราแบบ verbatim (ห้ามสรุปความ/paraphrase) พร้อมระบุช่วงหน้าจริง (เช่น pp. 586-587); ตัวเลขเชิงสถิติใน Subtitle สไลด์ต้องติด superscript อ้างอิงให้ตรงกับเนื้อหา และบทพูดต้องระบุชนิดการ์ดสีให้ตรงความจริง ("การ์ดแถบสี..." สำหรับพื้นขาวขอบแถบ vs "การ์ดสี..." สำหรับพื้นเต็มสี)
- Large-PDF Guardrail & Isolated Preview Sandbox: ห้าม Agent 02 หรือ Agent 11 ใช้ read_file เปิดไฟล์ PDF ตำราขนาดใหญ่ตรงๆ (กัน >1M tokens crash) ให้สกัดเฉพาะหน้าเป้าหมายผ่าน PyMuPDF (fitz) หรือ search-textbooks; งานปรับโครงสร้าง/กราฟในเด็คที่ส่งงานแล้ว (Mode 2) ให้สร้างพรีวิวแยกใน audit_buffer/preview_<tag>/ พร้อมภาพเทียบ Before/After ให้ผู้ใช้ยืนยันก่อนแก้ไฟล์จริง
