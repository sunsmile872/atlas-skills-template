---
name: travel-guide-pdf
description: Builds comprehensive, print-ready A4 PDF travel guides (PDF-only, no HTML output) with Navy/Teal/Mint styling, real Esri World_Imagery satellite route maps, SVG venue diagrams, meal-by-meal local-language food guides, time-ordered pre-trip checklists, and visual render QA. Use when planning a trip, organizing flight/hotel/ticket bookings, or generating a complete travel playbook PDF.
---

# Travel Guide PDF (`travel-guide-pdf`)

Generates a polished, print-ready **A4 PDF travel guide** (`.pdf` + companion `.md` source in `projects/<Trip_Name>/`) without creating standalone HTML web guides.

> **Storage Rule:** Save outputs inside `projects/<Trip_Name>/` by default. **Do NOT** auto-sync to iCloud Drive unless the user explicitly asks.

---

## Step 1: Intake & Clarification

Accept **either** or **both** input modes:
1. **Booking Files & Folders:** Read flight tickets, hotel confirmations, theme park/attraction vouchers, or Gmail booking emails (`composio-email` / `gmail`). Extract exact flight numbers, terminal/baggage rules, booking refs, hotel addresses (including local script), check-in/out dates, and ticket purchase windows.
2. **Short Prompt:** If the user provides only a destination/duration (e.g., `"วางแผนเที่ยวฟุกุโอกะ 4 วัน"`), ask **1–2 concise multiple-choice questions** (travel dates/season, pace/style, hotel area or must-visit spots) before drafting.

---

## Step 2: Live Destination Verification

Always search the web (`search_web`) to verify current rules and logistics before finalizing the guide:
- **Entry & Customs:** Online arrival card / visa rules, prohibited items (e.g., fresh fruit/meat, power bank `Wh` / `mAh` cabin rules), liquid limits.
- **Payments & Connectivity:** Cashless apps (e.g., Alipay/WeChat Pay fee thresholds, IC cards), eSIM/roaming OTP tips, recommended offline apps (maps, transit, translation).
- **Venues & Transit:** Current opening hours, closed days, ticket release windows (e.g., 30 days ahead), and airport/shuttle transit options.

---

## Step 3: Satellite Maps & Venue Diagrams

1. **Real Satellite Maps (`Esri World_Imagery`):**
   - Use `scripts/generate_satellite_map.py` (bundled in this skill) to render high-resolution satellite PNGs for:
     - **Map 1 (Overview):** Airport ↔ City Center ↔ Hotel ↔ Key Hubs.
     - **Map 2+ (Day Zooms):** Walking/metro routes per day with numbered pins and route lines.
   - Visually inspect each generated map PNG (`read_file`) to confirm labels do not overlap and all pins fall inside the frame.
2. **SVG Venue Diagrams (When Applicable):**
   - For complex multi-zone venues (e.g., Disneyland, Universal Studios, large temple/palace complexes), embed a clean inline **SVG zone diagram** showing entrances, key zones, and recommended loop order.

---

## Step 4: Standard 10-Section Content Architecture

Include all relevant sections with full practical detail:
1. **Trip Snapshot & Bookings:** Flights (times, terminals, baggage `kg`), Hotel (English + local script name, shuttle/transit), Ticket status & booking-window alerts, Key shopping/landmarks.
2. **Satellite Route Maps:** Overview + per-day zoom maps.
3. **Venue Zone Diagram (if applicable):** Inline SVG overview of complex parks/sites.
4. **Day-by-Day Deep Dive:** Time blocks, transit badges (Metro line/exit, Express train, Taxi/Didi), opening hours, entry fees, **couple photo spots**, and backup transit options.
5. **Highlight / Theme Park Strategy (if applicable):** Early Entry / FastPass / Premier double-ride tactics, ride table with **thrill rating (⭐)** and **minimum height (`cm+`)**, non-pass hidden gems, and indoor shows.
6. **Meal-by-Meal Food & Drink Guide:** **2–3 options per meal**, signature dishes in **Thai + local script** (e.g., 汉字 / 日本語 / 한국어), est. price/person, queue/ordering tips, plus must-try drinks/snacks/souvenirs.
7. **Ready-to-Send Email Templates:** Hotel shuttle reservation, early check-in, or special requests.
8. **Time-Ordered Pre-Trip Checklist:** Grouped strictly by deadline:
   - `30+ days / Booking Window`
   - `1 week before` (apps, cards, offline packs, packing, cash reserve)
   - `1–2 days before` (shuttle/concierge email, online arrival card, 24h web check-in)
   - `Departure day` (passport, boarding pass, cabin items, SIM/SMS OTP)
9. **Country-Specific Survival Tips:** Weather gear, payment tricks, offline apps, power bank / liquid / customs rules.

---

## Step 5: A4 PDF Build & Mandatory Visual QA

1. **Theme & Typography:**
   - Navy (`#0B172A`), Teal (`#0F766E` / `#2DD4BF`), Mint (`#F0FDFA`), White (`#FFFFFF`), Slate (`#334155`).
   - Clean Thai + English + CJK font stack (`"Sarabun", "Noto Sans Thai", "PingFang SC", "Hiragino Sans", sans-serif`).
2. **Preventing Awkward Page Breaks (Critical):**
   - **Never** wrap multi-row tables in `break-inside: avoid;` — this causes huge blank gaps when a table overflows onto the next page.
   - Instead, use `.card-flow` (no `break-inside: avoid`), `thead { display: table-header-group; }`, and `tr { break-inside: avoid; }`.
   - Keep `.callout` and small `.card` blocks with `break-inside: avoid;`.
3. **Compile via Chrome Headless:**
   ```bash
   "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
     --headless --disable-gpu --no-pdf-header-footer \
     --print-to-pdf="<OUTPUT_PDF_PATH>" "file://<SOURCE_HTML_PATH>"
   ```
   *(Remove temporary scratch HTML/PNGs or keep them in the conversation scratch directory — do not leave unwanted HTML deliverables in the user's final folder.)*
4. **Mandatory Visual Render Verification:**
   - Render **every page** of the compiled PDF to PNG via PyMuPDF (`fitz`) at 150 DPI and inspect them with `read_file`.
   - Check specifically for:
     - Half-empty pages caused by `break-inside: avoid`
     - 1-row orphan spillovers onto a new mostly-blank page (tighten `td` / `.card-flow` padding slightly so it fits cleanly on the prior page)
     - Clipped text, overlapping badges, or unreadable map labels
   - Only deliver the PDF after visual inspection passes on all pages.
