# Output Templates & PDPA Modes (`medical-record-summarizer`)

## PDPA Modes

- **Full Chart Mode *(default for private clinical handover/review)*:** Keep HN, AN, dates, treating team, and exact clinical identifiers.
- **De-identified Mode *(for teaching, case conference, or sharing)*:** Omit full name, national ID (CID), phone numbers, street address, and exact DOB (keep age/sex only).

---

## Mode 1: Clinical Summary & Chart Audit *(Default)*

Use when given an OPD/IPD folder or `.HEIC` photo set without a narrower request.

```markdown
# รายงานสรุปเวชระเบียนผู้ป่วย (Medical Record Summary & Chart Audit)

**สถานพยาบาล:** [Hospital / Unit]
**แหล่งข้อมูล:** [Folder name, file count & range]
**หมายเหตุ:** รายงานตามข้อเท็จจริงที่ปรากฏในเอกสารเท่านั้น (`Fact-First, Zero Extrapolation`)

## 1. ข้อมูลผู้ป่วยและพื้นฐานเดิม (Patient Profile & Baseline)
## 2. สรุปภาพรวมทางคลินิก (One-Liner)
## 3. รายการปัญหาทางคลินิกเรียงตามลำดับเวลา (Problem List by Onset)
| # | ปัญหา / การวินิจฉัย | Onset / Timeline | สถานะและข้อมูลสำคัญจากเวชระเบียน | แหล่งอ้างอิง |
## 4. ไทม์ไลน์เหตุการณ์สำคัญ (Chronological Timeline)
## 5. วิวัฒนาการทางคลินิกสำคัญ (Domain Trajectory — e.g. Neuro/Motor/Rehab or Weight/Lab)
## 6. สรุปผลการตรวจทางห้องปฏิบัติการและภาพถ่าย (Investigations)
## 7. สรุปยาและการเปลี่ยนแปลงสำคัญ (Medication Trajectory)
## 8. ผลการตรวจสอบความสอดคล้องของ Chart (Chart Audit & Gaps)
- ความคลาดเคลื่อน / ข้อมูลขัดแย้งระหว่างเอกสาร
- เอกสารที่ถูกอ้างถึงแต่ยังไม่พบในโฟลเดอร์
```

---

## Mode 2: IPD Discharge Summary & Problem Grouping

Use when summarizing a multi-day inpatient stay (`Admit` → `Discharge`).

- Header block: Hospital, Ward, HN/AN, Admit/Discharge dates & LOS, Discharge status, Primary attending team.
- **1. Admission Baseline & Workup** (CC, PE/Neuro baseline, initial labs/imaging).
- **2. Clinical Problem Grouping & Management** (group each major problem with pathophysiology, course, culture/imaging, and **Antibiotic/Medication Trajectory**).
- **3. Chronological In-Hospital Timeline** (Mermaid `timeline` or dated phase bullets).
- **4. Discharge Status, Home Medications & Follow-up Plan** (strictly as documented).

---

## Mode 3: In-Depth Chart Review

Use when reviewing long multi-visit OPD + IPD histories requiring full diagnostic logs.

- Full Demographics & Anthropometric/Weight Trend table.
- Problem List table with ICD-10 (if documented), Onset, Clinical Status & Findings.
- Verbatim key Pathology, Imaging (MRI/CT/Echo/Mammogram), and Operative sections with exact dates and specimen/accession numbers.
- Chronological Visit Log + Appointment schedule.

---

## Mode 4: Interactive Chart Q&A

Use when the user asks a targeted factual question against a summarized or raw chart (e.g., *"ใครสั่ง Aspirin?"*, *"เริ่มตรวจพบ Motor Grade 4 วันไหน?"*, *"CT เขียนว่าอะไรกันแน่?"*).

- Answer **directly** in 1–3 crisp bullets.
- Quote the exact documented text/value and cite `[File/Page | Date | Time | Author]`.
- Flag if other notes in the chart conflict or omit the item.
