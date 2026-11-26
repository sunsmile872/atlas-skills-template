---
name: academic-humanizer
version: 0.3.3
description: |
  Improve the clarity and voice of AI-assisted academic writing (papers, theses, rebuttals) and
  funding proposals (NSF Project Summary/Description, NIH Specific Aims): preserve scholarly
  conventions, match claims to evidence (and, for proposals, claims to feasibility), and match the
  author's own voice. It never changes a number, result, or citation, and it is not for evading
  AI-use disclosure. Use when editing AI-assisted academic prose or grant proposals.
license: MIT
compatibility: claude-code codex morphmind opencode
allowed-tools: [Read, Write, Edit, Grep, Glob, AskUserQuestion]
---

# Academic Humanizer

Improve the clarity and voice of AI-assisted *academic* writing while keeping the precise,
evidence-bound voice that scholarship requires and matching the author's own style. It preserves every
number, result, and citation, and it is not a tool for evading AI-use disclosure.

## When to use
Editing or reviewing academic prose: paper sections, abstracts, rebuttals, related work, and **funding
proposals** (NSF Project Summary/Description, NIH Specific Aims, fellowship and foundation proposals;
see Layer 6). **Not** for blogs, marketing, or personal essays, and **never** inject opinion, humor, or
first-person "personality" into a manuscript. For technical writing, neutral and precise *is* the human
voice. One caveat for proposals: their register is different from a paper's, since they are sold on
vision and feasibility, so the ambition language a paper would trim is appropriate there; apply Layer 6,
not the paper layers' stricter trimming, to vision statements.

## Core principle
Academic writing already has a correct human voice: neutral, precise, third-person plural ("we"), every
claim tied to its evidence. The job is to (1) strip the AI *tells* without casualizing, and (2) enforce
the discipline a general humanizer misses: **every claim earns its number, figure, or citation, and no
verb is stronger than its evidence.**

## Process
1. **Read** the manuscript and any author writing sample; note the document type (paper vs. funding
   proposal) and the target venue or funding agency. For proposals, also apply Layer 6 and preserve
   appropriate vision.
2. **Audit** (do not edit yet): list each detected pattern with its location and proposed fix, and each
   empirical claim's evidence status.
3. **Rewrite**: same structure and content, all claims and citations preserved, tells removed, over-claims
   matched to evidence, legitimate hedging kept.
4. **Report**: cleaned text plus a short change log (patterns removed, claims softened or given evidence
   pointers, voice notes). Cover everything the original covered: if it had five paragraphs, so does the
   rewrite.

---

## Layer 1: General AI-tell catalog
Scan for and fix the general patterns, subject to the academic exceptions in Layer 3:
inflated significance ("marking a pivotal moment"); superficial "-ing" tails that fake depth
("..., highlighting..."); promotional/figurative language ("rich", "vibrant", "groundbreaking");
vague attributions ("experts argue" with no cite); AI vocabulary (*delve, underscore, intricate,
tapestry, testament, landscape (abstract), pivotal, showcase, foster, leverage (filler), realm,
seamless*); copula avoidance ("serves as" -> "is"); negative parallelisms ("not just X, but Y");
rule-of-three padding; elegant variation (cycling synonyms for one referent); filler
("it is worth noting that", "in order to"); **overlong, clause-stacked sentences (split them; see 2.11)**;
and **em-dashes (remove entirely; recast with commas, colons, parentheses, or separate sentences)**.

**Before:** *Additionally, an enduring testament to the method's value is its ability to delve into
intricate dependencies, showcasing a seamless integration that underscores its pivotal role.*
**After:** *The method also captures higher-order dependencies, which the baselines miss (Table 2).*

---

## Layer 2: Academic AI tells (remove or fix)

### 2.1 Over-claiming verbs
Empirical work *shows* and *provides evidence*; it does not *prove* or *demonstrate* universal truths.
**Watch:** demonstrate, prove, establish, confirm, guarantee; "significantly" with no test/number.
**Before:** *We prove that our method significantly outperforms all prior approaches.*
**After:** *Our method improves held-out accuracy by 4--7 points over the strongest prior approach
(Table 3); the gain is significant at p < 0.01 by a paired test.*

### 2.2 Significance hype
**Watch:** paves the way for, a crucial/pivotal step toward, has the potential to revolutionize, opens
new avenues, sheds light on, of paramount importance, bridges the gap.
**Before:** *This work paves the way for a new paradigm and sheds light on a problem of paramount
importance.*
**After:** *This work addresses one failure mode of prior methods: error accumulation under long-horizon
rollout (Section 4).*

### 2.3 Empty intensifiers
**Watch:** extensive/comprehensive/thorough experiments, a wide range of, numerous, various.
**Before:** *We conduct extensive experiments on a wide range of datasets.*
**After:** *We evaluate on three datasets (ImageNet, CIFAR-100, and iNaturalist).*

### 2.4 Novelty padding
**Watch:** "novel" used more than once per section; "to the best of our knowledge"; "for the first time".
**Before:** *We propose a novel framework and, to the best of our knowledge, are the first to study this.*
**After:** *We study online calibration under delayed labels, which prior calibration work (offline) does
not address.*

### 2.5 Formulaic openers
**Watch:** "In recent years, X has attracted increasing attention"; "With the rapid development of...";
"Despite recent advances,...".
**Before:** *In recent years, tabular deep learning has attracted increasing attention.*
**After:** *Tabular deep learning has a structural limitation: most models discard feature-type metadata
and must relearn it from data.*

### 2.6 Connective overuse
Do not start consecutive sentences with Moreover/Furthermore/Additionally/In particular; let logic carry.
**Before:** *Moreover, the method is fast. Furthermore, it is simple. Additionally, it scales.*
**After:** *The method is fast and simple, and it scales to one million rows (Section 5).*

### 2.7 Contribution-list cliches
Each contribution names a *specific* result, not a restatement of the abstract.
**Before:** *Our contributions are: (1) a novel method; (2) extensive experiments; (3) strong results.*
**After:** *We (1) introduce a metadata-aware encoder that reaches 0.91 AUROC vs 0.86 for the strongest
baseline; (2) show it stays within 2 points under 20% label noise where the baseline drops 9; (3) release
the benchmark.*

### 2.8 Citation dumping
Cite the one or two works that matter and say why, not a bracketed list.
**Before:** *Many methods exist [3, 7, 9, 12, 15].*
**After:** *The closest prior method is TabNet [7], which encodes all features jointly; we instead
condition on feature-type metadata.*

### 2.9 Hedging-by-vagueness
**Watch:** somewhat, relatively, fairly, to some extent, quite. Quantify or cut.
**Before:** *Performance is somewhat better and relatively robust.*
**After:** *Accuracy is 3 points higher and varies by less than 1 point across five seeds.*

### 2.10 Boilerplate emphasis
**Watch:** "It is worth noting that", "It should be emphasized that", "Notably,", "Importantly,".
If it matters, the sentence shows it.
**Before:** *It is worth noting that, importantly, the gain holds across scenarios.*
**After:** *The gain holds across all three scenarios (Table 4).*

### 2.11 Overlong, clause-stacked sentences
AI favors long sentences that chain three or four clauses with commas and "which", "that", "while", "with".
Split them: one idea per sentence, and cut subordinate clauses that carry no weight. **Watch:** sentences
past ~30 words, or with 3+ subordinate clauses.
**Before:** *Existing methods, though promising, are largely empirical, with unclear principles
underpinning their behavior, which limits their reliability and further progress.*
**After:** *Existing methods stay empirical. Their principles are unclear, which limits reliability and
progress.*

---

## Layer 3: Preserve these (do NOT over-correct)
A general humanizer flattens legitimate scholarly constructs. Keep them.

- **Evidence-tied hedging is correct and required.** Keep "suggests", "is consistent with", "we
  hypothesize that", "may indicate", "appears to" when the claim is genuinely uncertain.
  *Wrong fix:* turning *"the results suggest X"* into *"the results prove X"*: this manufactures
  over-claiming. Keep the calibrated verb.
- **Passive voice** is fine when the actor is irrelevant: *"Samples were normalized to total protein."*
- **First-person plural "we"** is standard; do not rewrite to avoid it.
- **Semicolons and an occasional triple** are fine in moderation. Em-dashes are the exception: remove
  them entirely (Layer 1), recasting with commas, colons, parentheses, or separate sentences.
- **Formal definitions, named methods/metrics, technical terms, equations, and symbols** stay verbatim.
- **Never invent, drop, or alter a number, equation, or citation.** Same content; preserve every cite key.

---

## Layer 4: Claim-evidence discipline
For every empirical claim, check (a) is it backed by a number, figure, table, or citation in the text,
and (b) does the verb match the strength of that evidence?

- **Unbacked claim -> add the evidence pointer or soften.**
  *Before:* *Our method is more robust.*  *After:* *Our method's accuracy drops by 2 points under
  distribution shift, versus 11 points for the baseline (Figure 3).*
- **Verb stronger than evidence -> downgrade.**
  *Before:* *This demonstrates that our method is universally superior.*
  *After:* *On these three datasets, our method matches or exceeds the strongest baseline (Table 2).*
- **Vague magnitude -> a number or RANGE, attributed.**
  *Before:* *a large improvement.*  *After:* *a 2--6% improvement in balanced accuracy over the strongest
  baseline.*
  Prefer ranges (e.g., "2--6%") over single averaged values unless the averaging method is stated, and
  attribute each number to its method, metric, and baseline. When comparing, lead with the comparison
  against the strongest competitor, not the trivial baseline.

---

## Layer 5: Voice and venue matching
If the author supplies prior papers, read a sample first and note sentence rhythm, connective habits,
level and placement of hedging, how they open sections, notation, and recurring phrasings, then match
them. Match the venue's register too (e.g., ICLR/NeurIPS: terse, direct, results-forward; Nature/PNAS:
more expository). Absent a sample, default to clean, precise, venue-appropriate prose, not the casual,
opinionated voice of a general-purpose humanizer.

## Layer 6: Funding-proposal mode (NSF, NIH)
A proposal is not a paper. It is sold on **vision plus feasibility**, not on finished results, and
reviewers score it. The register shift matters: ambition language that the paper layers would trim
("long-term goal", "pioneer", "transformative", "establish a foundation") is *appropriate and expected*
here, provided a credible plan and evidence back it. So in proposal mode, **do not flatten the vision**;
enforce a different discipline instead: **claim <-> feasibility**.

### 6.1 Know the structure; the score lives in the first pages
Reviewers form a score from the opening, then skim the rest to confirm it. Put most editing effort there.
- **NSF.** A one-page **Project Summary** with the three review-criteria heads spelled out:
  **Overview**, **Intellectual Merit**, **Broader Impacts**, each self-contained. The Project
  Description then opens with **long-term vision -> this proposal's goal -> the gap -> the specific
  thrusts/aims -> the payoff**, ideally within the first 1--2 pages, with one overview figure. Broader
  Impacts must be substantive and integrated, never an afterthought.
- **NIH (R01).** The **Specific Aims page is the whole proposal in one page**, and is the most-read,
  most-decisive page. Standard arc: (1) opening: the problem, what is known, the **gap / critical need**;
  (2) the **long-term goal** and the **central hypothesis** with its rationale; (3) "**The objective of
  this application is...**" plus how the hypothesis was formed; (4) **2--3 Aims**, each a one-line goal +
  a phrase on approach + the expected outcome; (5) a **payoff** paragraph: what changes if it succeeds.
  Then **Significance, Innovation, Approach** as separately scored sections.

### 6.2 First-3-pages primacy (edit these hardest)
By the end of page 1 (NIH Aims) or pages ~2--3 (NSF), the reader must already hold: the **hook** (why it
matters, concretely), the **gap** (what is missing and the cost of the gap), the **central idea** (your
approach in one sentence), the **aims/thrusts** (crisp and parallel), and the **payoff**. If any is
missing or buried, fix that before touching later sections. A reviewer unconvinced by page 3 does not
recover on page 10.

### 6.3 Proposal-specific weak moves to fix
- **Vague importance.** *Watch:* "this is an important/timely problem", "X has many applications".
  **Before:** *Understanding this problem is critically important.*
  **After:** *Without bounds on how measurement noise propagates to diagnosis, clinical models are tuned by
  trial and error, the inefficiency this proposal removes.*
- **Method-as-aim** (an aim naming a technique instead of a question or outcome).
  **Before:** *Aim 2: Apply transfer learning to the dataset.*
  **After:** *Aim 2: Determine whether fusing wearable and lab signals improves early detection, and for
  which patient subgroups it helps or hurts.*
- **Dominoed aims** (Aim 2/3 collapse if Aim 1 fails; reviewers flag this as fragile). *Fix:* phrase
  aims as **parallel and independently valuable**; where one depends on another, state the fallback.
- **Ambition without feasibility.** Every bold claim needs a footing: preliminary data, a prior
  result/publication, a classical theorem you build on, or a collaborator/letter. *Fix:* attach the
  evidence beside the claim ("our preliminary result in Fig. X shows...", "building on a classical minimax
  lower bound...").
- **Boilerplate Broader Impacts / training plan.** *Watch:* "we will mentor students and disseminate via
  talks and papers." *Fix:* make it concrete, enumerated, and tied to the research: specific programs,
  named courses or tools, measurable outreach.
- **Hedged central hypothesis.** The Aims-page hypothesis is a falsifiable commitment, not "we will
  explore whether possibly...". Calibrated hedging belongs in the Approach's interpretation, not the
  central claim.

### 6.4 Preserve and deploy (funded-proposal craft)
These read as strength; keep or add them rather than editing them out.
- **Vision/ambition framing**: a bold long-term goal up front, with this proposal as one principled step
  toward it.
- **Run-in lead-ins for scannability**: bold/italic **Goal:**, **Motivation:**, **Innovation:**,
  *Thrust/Aim N (one-line mission):*. Reviewers skim; visible structure earns time.
- **A concrete running example or protagonist** to make an abstract method vivid and consistent across aims.
- **Sharp challenge/aim statements posed as questions**: a crisp open question reads as a well-posed
  problem (a boxed or set-off question per aim works well).
- **Anchoring novel work in deep, named classical results** to signal rigor and lineage: a known
  inequality, capacity notion, or test that the new method generalizes.
- **Foreground the team's standing as feasibility evidence**: prior funded work, preliminary results,
  publications, collaborators, and demonstration partners belong *early*, as proof the plan is executable.
  A real track record is evidence, not boasting; place it where it de-risks the aims. *(Use only the PI's
  own real, supplied record; never invent funding, results, partners, or letters.)*

### 6.5 Claim <-> feasibility (the proposal analog of Layer 4)
For every aim and promised outcome, check: is the ambition matched by a credible means, such as
preliminary data, a prior method, a classical foundation, a collaborator, or staged de-risking? If yes,
keep the ambitious verb. If no, attach the missing evidence or scale the claim to what the plan supports.
Never invent preliminary results, prior funding, partners, or letters; if the support does not exist, flag
the gap for the author rather than papering over it.

---

## Layer 7: Thai Medical & Clinical Academic Register (Anti-Calque & Natural Code-Switching)
When writing or editing Thai medical manuscripts, residency theses, IRB protocols (`Med{{INSTITUTION}} / EC{{INSTITUTION}}`), or advisor pitch notes, never use awkward literal dictionary translations (AI calques) that Thai clinicians do not say in real academic or hospital practice.

### 7.1 Two-Register Audience Split
- **Physician / Advisor / Ethics Committee Register (`Pitch Note`, `16-Section Protocol`, `SUB-01/02/10`, `CRF`, `SOT`):**
  Define the standard Thai clinical term alongside its English term/acronym on first mention (or in the formal Thai title), then **use natural English medical loanwords or acronyms (`double-blind`, `blinded assessor`, `carryover effect`, `ค่า PPT`, `ค่า SWV`, `จุดกดเจ็บ active MTrP`, `ค่า Bang's blinding index`, `คะแนน NDI`)** in running prose.
- **Patient Consent Register (`PIS / ICF`):**
  Use everyday Prathom-6 Thai explanations (*"ระดับแรงกดที่เริ่มรู้สึกเจ็บ"*, *"การสุ่มโดยที่ทั้งผู้ป่วยและผู้ประเมินไม่ทราบกลุ่ม"*), never stiff AI calques.

### 7.2 Banned Thai AI Calques -> Natural Thai Medical Replacements
- **`ธรณีความเจ็บปวดจากการกด` / `ธรณีความเจ็บปวด`** (*threshold = ธรณีประตู* calque) -> **`ระดับความไวต่อแรงกดเจ็บ (pressure pain threshold: PPT)`** on first mention / title, then **`ค่า PPT`**, **`ค่า local PPT`**, **`ค่า remote PPT`**
- **`ปกปิดสองทาง` / `การทดลองแบบสุ่มขนาน`** -> In formal title: **`การศึกษาทดลองแบบสุ่มและมีกลุ่มควบคุมหลอกแบบปกปิดทั้งสองฝ่าย (Double-Blind)`**; in body prose: **`การวิจัยแบบ double-blind randomized sham-controlled trial`** (or **`การวิจัยแบบ double-blind`**)
- **`ผู้ประเมินปกปิด` / `ผู้ประเมินที่ถูกปกปิด`** -> **`ผู้ประเมินผลที่ไม่ทราบกลุ่มการรักษา (blinded assessor)`** on first mention, then **`ผู้ประเมินผล (blinded assessor)`**
- **`ดัชนีการปกปิด`** -> **`ค่า Bang's blinding index`**
- **`ผลค้างข้ามรอบ`** -> **`ผลตกค้างจากการรักษารอบก่อน (carryover effect)`** on first mention, then **`carryover effect`**
- **`จุดกดเจ็บที่ทำงานอยู่`** -> **`จุดกดเจ็บชนิดแสดงอาการ (active myofascial trigger point: active MTrP)`** on first mention, then **`จุดกดเจ็บ active MTrP`**
- **`ความเร็วคลื่นเฉือน` (repeated in every clause)** -> Define once as **`ค่าความเร็วคลื่นเฉือน (shear wave velocity: SWV)`**, then use **`ค่า SWV (m/s)`** or **`ค่าความตึงตัวของกล้ามเนื้อจาก 2D-SWE (ค่า SWV)`**
- **`ความบกพร่องของคอ (NDI)`** -> **`คะแนนความสามารถในการใช้งานคอ (Neck Disability Index: NDI)`** or **`คะแนน NDI`**
- **`ท่ายืดเกร็งเล็กน้อย`** (contradictory *stretch + contract*) -> **`ท่ายืดกล้ามเนื้อบ่าเบาๆ (เอียงศีรษะไปด้านตรงข้าม 15 องศา; gentle stretch 15°)`**
- **`ภาวะบกพร่องทางพุทธิปัญญารุนแรง`** -> **`มีภาวะสับสน ความจำเสื่อม หรือบกพร่องทางการรับรู้และการสื่อสารจนไม่สามารถให้ข้อมูลและประเมินความปวดได้`**
- **`เชิงอัตวิสัยของผู้ป่วย` vs. `ผลลัพธ์เชิงประจักษ์ทางกายภาพโดยตรง`** -> **`ค่าที่ขึ้นกับการรับรู้ความรู้สึกของผู้ป่วย (subjective outcome)`** vs. **`การวัดคุณสมบัติทางกายภาพของเนื้อเยื่อโดยตรง (objective outcome)`**
- **`ตรวจสอบความคงทนของผลลัพธ์`** (*robustness* calque) -> **`ตรวจสอบความสอดคล้องของผลลัพธ์ (sensitivity analysis)`**
- **`ได้พิสูจน์แล้วว่า...` / `พิสูจน์ไว้แล้ว` / `พิสูจน์ซ้ำตรงกันแล้วว่า...`** (Layer 2.1 over-claiming verb) -> **`รายงานว่า...`**, **`รายงานไว้แล้ว`**, **`พบว่า...`**, or **`แสดงให้เห็นว่า...`**
- **`ปริศนาจากงานของ...` / `ตอบคำถามที่ค้างคา` / `สร้างหลักฐาน...เป็นครั้งแรก`** (Layer 2.2/2.4 hype) -> **`ประเด็นที่ยังไม่มีข้อสรุปชัดเจนจากการศึกษาของ...`** and **`เพื่ออธิบายกลไกการออกฤทธิ์ฉับพลันของ rPMS...`**
- **`แบบอนุรักษนิยม`** (political calque for *conservative estimate*) -> **`การประเมินค่าแบบรัดกุม (conservative estimate)`** or **`แบบ conservative`**
- **`เปรียบเทียบ 2 แขน` / `แขน Sham` / `แขนทดลอง` / `ระยะซักล้าง` / `ตัวแปรสับสน` / `ผลกระทบเพดาน`** -> **`เปรียบเทียบ 2 กลุ่ม (2-arm)`**, **`กลุ่มควบคุมหลอก (Sham)` / `กลุ่ม Sham`**, **`กลุ่มทดลอง` / `กลุ่มแทรกแซง`**, **`ระยะพัก (washout period)`**, **`ตัวแปรกวน (confounder)`**, **`ceiling/floor effect`** *(synced with `deliverable_auditor.py` `BANNED_THAI_CALQUES`)*

### 7.3 Open-Ended Generative Detection Protocol (For Unseen Future Terms Across Any Specialty)
Because static word lists cannot anticipate every new literal translation an LLM might invent in future topics (e.g., *EMG/NCS, Spasticity, Dysphagia, Gait/Biomechanics, SCI, WBV, Cardiopulmonary Rehab*), both the Author Agent (`03`/`05`) and the Independent Reviewer (`Gate 12`) MUST perform an **Open-Ended Semantic Thai Clinical Ear Scan** on every paragraph using **3 Generative Rules**:

1. **Rule 1 — The "{{INSTITUTION}} Morning Conference / Ward Round" Ear Test:**
   For every Thai technical noun phrase in the draft, ask: *"เวลาแพทย์ประจำบ้านและอาจารย์เวชศาสตร์ฟื้นฟู {{INSTITUTION}} พูดใน Morning Conference หรือเขียนวิทยานิพนธ์ เขาพูดคำไทยคำนี้จริงๆ หรือพูดทับศัพท์ภาษาอังกฤษ?"*
   - If Thai clinicians normally speak the term in English (`double-blind`, `crossover`, `washout period`, `carryover effect`, `ceiling/floor effect`, `baseline`, `follow-up`, `cut-off`, `confounder`, `covariate`, `effect size`, `power`, `conservative`, `sensitivity analysis`, `intention-to-treat`, `per-protocol`, `sham`, `active MTrP`, `taut band`, `local twitch response`, `PPT`, `SWV`, `ROI`, `probe`, `standoff pad`, `coil`, `pulse train`, `sub-threshold`, `suprathreshold`, `spasticity`, `onset latency`, `amplitude`, `CMAP`, `SNAP`, `MUAP`, `recruitment`), **never leave an invented Thai dictionary translation standing alone**. Write `[คำไทยสั้นๆ ที่เข้าใจธรรมชาติ] ([English term])` on first mention, and use the **English loanword/acronym (`ทับศัพท์`)** from the 2nd mention onward.
2. **Rule 2 — Polysemous English Root Calque Detector:**
   Automatically flag any Thai phrase where an English technical word with multiple meanings (*conservative, threshold, arm, blind, washout, ceiling, floor, naive, train, robust, power, active, burden, landscape*) was translated using its non-medical everyday/political/physical dictionary meaning (`อนุรักษนิยม`, `ธรณี`, `แขน`, `ตาบอด/ปกปิดสองทาง`, `ซักล้าง`, `เพดาน`, `ไร้เดียงสา`, `ขบวน`, `ความคงทน`).
3. **Rule 3 — Two-Way Continuous Learning Loop (`Auto-Grow Dictionary`):**
   Whenever `Gate 12` or the user spots a *new* unnatural Thai calque in any future session, `Gate 12` must immediately append that term to `BANNED_THAI_CALQUES` in `~/.gemini/config/skills/clinical-academic-editor/scripts/deliverable_auditor.py` and Section `7.2` of this skill so the deterministic check permanently blocks it in all future projects.

---

## Output
Return the cleaned text plus a short change report: patterns removed (by type), claims softened or given
evidence pointers, and any voice/venue notes. Confirm that no number, equation, or citation was altered.
