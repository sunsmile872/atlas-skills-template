#!/usr/bin/env node
/**
 * Full 17-Slide Visual-Learner SOTA Deck Builder v2.6 (PptxGenJS 4.x)
 * Reads ONLY locked evidence_bundle_17_v2_6.json + extracted_assets/*.png + icons/*.png.
 * v2.6 Upgrades:
 *   1. Dynamic 4-card Slide 11 + 14.0 pt body / 15.5-16.0 pt heading standard on spacious/primary slides
 *      (Slides 02, 03, 04, 05, 08, 09, 10, 11, 12, 16)
 *   2. Balanced 13.0-13.5 pt body on multi-column/matrix slides (Slides 06, 07, 13, 14, 15)
 *   3. Slide 12: 8-bar horizontal chart (single-line Y-axis labels) + 3 generously padded 14.0 pt cards
 *   4. Slide 06 preserves table_41_1_v2_5.png; Slides 04 & 10 keep top_figure_plus_strip
 *   5. Slide 17 preserves covers [1]-[3], muted book_open_slate.png placeholder [4], and 2-line [2] TOC (12.0 pt)
 *   6. 100% verbatim text, native superscript helper (`[[1]]`, `[[2,3]]`), bottom-right `01 / 17`..`17 / 17`
 */

const fs = require("fs");
const path = require("path");

function loadPptxGenJS() {
  const candidates = [
    path.join(__dirname, "node_modules", "pptxgenjs"),
    path.join(__dirname, "..", "node_modules", "pptxgenjs"),
    "~/.gemini/config/skills/pmr-slide-creator/templates/bento_engine/node_modules/pptxgenjs",
    "pptxgenjs",
  ];
  for (const modPath of candidates) {
    try {
      return require(modPath);
    } catch (_) {
      // try next candidate
    }
  }
  throw new Error("Unable to locate 'pptxgenjs'. Run 'npm install' in the project directory.");
}

const PptxGenJS = loadPptxGenJS();

const THEME_OVERRIDES = {
  navy_teal: { navyDark: "0F172A", navyMid: "1E293B", teal: "0D9488", tealBright: "14B8A6", tealDark: "0F766E", mintBg: "CCFBF1", mintSoft: "F0FDFA", bgLight: "F8FAFC" },
  academic_brick: { navyDark: "1E293B", navyMid: "334155", teal: "A73B24", tealBright: "C2410C", tealDark: "8A2C18", mintBg: "FEEBE4", mintSoft: "FFF7F5", bgLight: "FAF8F6" },
  emerald_charcoal: { navyDark: "064E3B", navyMid: "115E59", teal: "D97706", tealBright: "F59E0B", tealDark: "B45309", mintBg: "FEF3C7", mintSoft: "FFFBEB", bgLight: "F3F8F6" },
};

const PALETTE = {
  navyDark: "0F172A",
  navyMid: "1E293B",
  slate700: "334155",
  slate500: "64748B",
  slate300: "CBD5E1",
  slate200: "E2E8F0",
  slate100: "F1F5F9",
  bgLight: "F8FAFC",
  white: "FFFFFF",
  teal: "0D9488",
  tealBright: "14B8A6",
  tealDark: "0F766E",
  mintBg: "CCFBF1",
  mintSoft: "F0FDFA",
  amber: "D97706",
  amberBg: "FEF3C7",
  amberDark: "B45309",
  amberSoft: "FFFBEB",
  coral: "DC2626",
  coralBg: "FEF2F2",
  blueSoft: "EFF6FF",
  blueAccent: "2563EB",
};

const BUNDLED_ICONS_DIR = "~/.gemini/config/skills/pmr-slide-creator/templates/bento_engine/icons";
const FONT_HEAD = "Arial";
const FONT_BODY = "Arial";

function iconPath(name) {
  const localP = path.join(__dirname, "icons", name);
  if (fs.existsSync(localP)) return localP;
  const bundledP = path.join(BUNDLED_ICONS_DIR, name);
  return fs.existsSync(bundledP) ? bundledP : null;
}

function expandSupString(str, baseOpts, supColor) {
  const parts = String(str).split(/(\[\[[0-9,]+\]\])/g);
  const runs = [];
  for (const part of parts) {
    if (!part) continue;
    const m = part.match(/^\[\[([0-9,]+)\]\]$/);
    if (m) {
      runs.push({
        text: m[1],
        options: {
          fontFace: baseOpts.fontFace || FONT_BODY,
          fontSize: baseOpts.fontSize || 14,
          bold: true,
          color: supColor,
          superscript: true,
        },
      });
    } else {
      runs.push({
        text: part,
        options: {
          fontFace: baseOpts.fontFace || FONT_BODY,
          fontSize: baseOpts.fontSize || 14,
          bold: !!baseOpts.bold,
          italic: !!baseOpts.italic,
          color: baseOpts.color || PALETTE.slate700,
        },
      });
    }
  }
  return runs;
}

function createSlideWithSup(pres, dark = false) {
  const slide = pres.addSlide();
  const supColor = dark ? PALETTE.tealBright : PALETTE.tealDark;
  const origAddText = slide.addText.bind(slide);
  slide.addText = (content, opts = {}) => {
    if (typeof content === "string" && /\[\[[0-9,]+\]\]/.test(content)) {
      const runs = expandSupString(content, opts, supColor);
      return origAddText(runs, opts);
    }
    if (Array.isArray(content)) {
      const outRuns = [];
      for (const item of content) {
        if (item && typeof item.text === "string" && /\[\[[0-9,]+\]\]/.test(item.text)) {
          const itemOpts = item.options || {};
          const sub = expandSupString(item.text, itemOpts, supColor);
          sub.forEach((sr, idx) => {
            const merged = { ...sr.options };
            if (idx === 0 && itemOpts.bullet) merged.bullet = itemOpts.bullet;
            if (idx === 0 && itemOpts.paraSpaceAfter !== undefined) merged.paraSpaceAfter = itemOpts.paraSpaceAfter;
            if (idx === 0 && itemOpts.paraSpaceBefore !== undefined) merged.paraSpaceBefore = itemOpts.paraSpaceBefore;
            if (idx === sub.length - 1 && itemOpts.breakLine) merged.breakLine = true;
            outRuns.push({ text: sr.text, options: merged });
          });
        } else {
          outRuns.push(item);
        }
      }
      return origAddText(outRuns, opts);
    }
    return origAddText(content, opts);
  };
  return slide;
}

function getPngDimensions(filePath) {
  const buf = fs.readFileSync(filePath);
  if (buf.length < 24 || buf.toString("ascii", 1, 4) !== "PNG") {
    return { width: 1000, height: 800 };
  }
  return {
    width: buf.readUInt32BE(16),
    height: buf.readUInt32BE(20),
  };
}

function addEditorialHeader(slide, data, dark = false) {
  const headline = data.title || data.assertion_headline || "";

  slide.addText(data.eyebrow || "", {
    x: 0.65,
    y: 0.30,
    w: 12.0,
    h: 0.24,
    fontFace: FONT_HEAD,
    fontSize: 10,
    bold: true,
    charSpacing: 1.4,
    color: dark ? PALETTE.tealBright : PALETTE.teal,
    margin: 0,
  });

  const headLen = headline.length;
  const headSize = headLen > 80 ? 18.5 : headLen > 70 ? 20 : 21.5;

  slide.addText(headline, {
    x: 0.65,
    y: 0.54,
    w: 12.03,
    h: 0.50,
    fontFace: FONT_HEAD,
    fontSize: headSize,
    bold: true,
    color: dark ? PALETTE.white : PALETTE.navyDark,
    margin: 0,
    valign: "middle",
  });

  if (data.subtitle) {
    slide.addText(data.subtitle, {
      x: 0.65,
      y: 1.07,
      w: 12.03,
      h: 0.28,
      fontFace: FONT_BODY,
      fontSize: 12.5,
      color: dark ? "94A3B8" : PALETTE.slate500,
      margin: 0,
    });
  }

  slide.addShape("rect", {
    x: 0.65,
    y: 1.42,
    w: 12.03,
    h: 0.015,
    fill: { color: dark ? "1E293B" : PALETTE.slate200 },
    line: { type: "none" },
  });
}

function addFooter(slide, footnote, slideNum, totalSlides, dark = false) {
  if (footnote) {
    slide.addText(`Ref: ${footnote}`, {
      x: 0.65,
      y: 7.10,
      w: 10.6,
      h: 0.26,
      fontFace: FONT_BODY,
      fontSize: 9.5,
      italic: true,
      color: dark ? "94A3B8" : PALETTE.slate500,
      margin: 0,
    });
  }

  const label = `${String(slideNum).padStart(2, "0")} / ${String(totalSlides).padStart(2, "0")}`;
  slide.addText(label, {
    x: 11.45,
    y: 7.10,
    w: 1.23,
    h: 0.26,
    fontFace: FONT_HEAD,
    fontSize: 10,
    bold: true,
    align: "right",
    color: dark ? "94A3B8" : PALETTE.slate500,
    margin: 0,
  });
}

function drawFigureCard(slide, figure, x, y, w, h) {
  slide.addShape("roundRect", {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: PALETTE.white },
    line: { color: PALETTE.slate200, width: 1 },
  });

  const imgPath = path.join(__dirname, "extracted_assets", figure.image_file);
  if (!fs.existsSync(imgPath)) {
    throw new Error(`Missing extracted asset: ${imgPath}`);
  }
  const dims = getPngDimensions(imgPath);
  const maxW = w - 0.36;
  const maxH = h - 1.02;
  const scale = Math.min(maxW / dims.width, maxH / dims.height);
  const picW = dims.width * scale;
  const picH = dims.height * scale;
  const picX = x + (w - picW) / 2;
  const picY = y + 0.16 + (maxH - picH) / 2;

  slide.addImage({
    path: imgPath,
    x: picX,
    y: picY,
    w: picW,
    h: picH,
  });

  slide.addText(figure.title, {
    x: x + 0.18,
    y: y + h - 0.78,
    w: w - 0.36,
    h: 0.42,
    fontFace: FONT_HEAD,
    fontSize: 10.5,
    bold: true,
    color: PALETTE.navyMid,
    align: "center",
    valign: "middle",
    margin: 0,
  });

  slide.addText(`Source: ${figure.source}`, {
    x: x + 0.18,
    y: y + h - 0.36,
    w: w - 0.36,
    h: 0.24,
    fontFace: FONT_BODY,
    fontSize: 9.5,
    italic: true,
    color: PALETTE.slate500,
    align: "center",
    margin: 0,
  });
}

function buildDarkHeroTitle(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, true);
  slide.background = { color: PALETTE.navyDark };

  slide.addShape("rect", {
    x: 0,
    y: 0,
    w: 0.22,
    h: 7.5,
    fill: { color: PALETTE.teal },
    line: { type: "none" },
  });

  slide.addShape("rect", {
    x: 1.1,
    y: 1.15,
    w: 10.2,
    h: 0.38,
    fill: { color: "134E4A" },
    line: { color: PALETTE.teal, width: 1 },
  });
  slide.addText(data.eyebrow, {
    x: 1.1,
    y: 1.15,
    w: 10.2,
    h: 0.38,
    fontFace: FONT_HEAD,
    fontSize: 10.5,
    bold: true,
    charSpacing: 1.1,
    color: PALETTE.mintBg,
    align: "center",
    valign: "middle",
    margin: 0,
  });

  const mainTitle = data.title || data.assertion_headline || "";
  slide.addText(mainTitle, {
    x: 1.1,
    y: 2.02,
    w: 11.1,
    h: 1.65,
    fontFace: FONT_HEAD,
    fontSize: 38,
    bold: true,
    color: PALETTE.white,
    margin: 0,
  });

  slide.addText(data.subtitle, {
    x: 1.1,
    y: 3.78,
    w: 10.8,
    h: 0.65,
    fontFace: FONT_BODY,
    fontSize: 16,
    color: "CBD5E1",
    margin: 0,
  });

  slide.addShape("rect", {
    x: 1.1,
    y: 4.72,
    w: 3.2,
    h: 0.03,
    fill: { color: PALETTE.tealBright },
    line: { type: "none" },
  });

  const meta = data.meta || data;
  slide.addText(meta.presenter || "", {
    x: 1.1,
    y: 5.02,
    w: 10.8,
    h: 0.36,
    fontFace: FONT_HEAD,
    fontSize: 16,
    bold: true,
    color: PALETTE.white,
    margin: 0,
  });

  slide.addText(meta.advisor || "", {
    x: 1.1,
    y: 5.42,
    w: 10.8,
    h: 0.34,
    fontFace: FONT_BODY,
    fontSize: 14.5,
    bold: true,
    color: PALETTE.tealBright,
    margin: 0,
  });

  slide.addText(meta.institution || "", {
    x: 1.1,
    y: 5.80,
    w: 10.8,
    h: 0.32,
    fontFace: FONT_BODY,
    fontSize: 13,
    color: "94A3B8",
    margin: 0,
  });

  addFooter(slide, data.footnote || "", slideNum, totalSlides, true);
}

function buildKpiHeroPlusChart(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  const accentMap = {
    teal: { color: PALETTE.teal, bg: PALETTE.mintSoft, icon: "users_teal.png" },
    navy: { color: PALETTE.navyDark, bg: "E2E8F0", icon: "trend_navy.png" },
    amber: { color: PALETTE.amber, bg: PALETTE.amberBg, icon: "activity_amber.png" },
  };

  const kpiW = 3.81;
  const gap = 0.30;
  data.kpis.forEach((kpi, idx) => {
    const x = 0.65 + idx * (kpiW + gap);
    const y = 1.62;
    const st = accentMap[kpi.accent] || accentMap.teal;

    slide.addShape("roundRect", {
      x,
      y,
      w: kpiW,
      h: 1.55,
      rectRadius: 0.08,
      fill: { color: PALETTE.white },
      line: { type: "none" },
    });
    slide.addShape("rect", {
      x: x + 0.02,
      y,
      w: kpiW - 0.04,
      h: 0.07,
      fill: { color: st.color },
      line: { type: "none" },
    });

    const ic = iconPath(st.icon);
    if (ic) {
      slide.addShape("ellipse", {
        x: x + kpiW - 0.68,
        y: y + 0.18,
        w: 0.46,
        h: 0.46,
        fill: { color: st.bg },
        line: { type: "none" },
      });
      slide.addImage({
        path: ic,
        x: x + kpiW - 0.58,
        y: y + 0.28,
        w: 0.26,
        h: 0.26,
      });
    }

    slide.addText(kpi.value, {
      x: x + 0.22,
      y: y + 0.14,
      w: kpiW - 1.0,
      h: 0.60,
      fontFace: FONT_HEAD,
      fontSize: 34,
      bold: true,
      color: st.color,
      margin: 0,
    });
    slide.addText(kpi.label, {
      x: x + 0.22,
      y: y + 0.80,
      w: kpiW - 0.44,
      h: kpi.source ? 0.38 : 0.62,
      fontFace: FONT_HEAD,
      fontSize: 14,
      bold: true,
      color: PALETTE.navyMid,
      valign: "top",
      margin: 0,
    });
    if (kpi.source) {
      slide.addText(kpi.source, {
        x: x + 0.22,
        y: y + 1.22,
        w: kpiW - 0.44,
        h: 0.24,
        fontFace: FONT_BODY,
        fontSize: 9.5,
        italic: true,
        color: PALETTE.slate500,
        margin: 0,
      });
    }
  });

  // Bottom-left Chart Panel
  slide.addShape("roundRect", {
    x: 0.65,
    y: 3.38,
    w: 7.35,
    h: 3.54,
    rectRadius: 0.08,
    fill: { color: PALETTE.white },
    line: { type: "none" },
  });
  slide.addText(data.chart.title, {
    x: 0.90,
    y: 3.52,
    w: 6.90,
    h: 0.36,
    fontFace: FONT_HEAD,
    fontSize: 15,
    bold: true,
    color: PALETTE.navyDark,
    margin: 0,
  });

  slide.addChart(
    pres.ChartType.bar,
    [
      {
        name: data.chart.unit || "%",
        labels: data.chart.categories,
        values: data.chart.values,
      },
    ],
    {
      x: 0.85,
      y: 3.90,
      w: 6.95,
      h: 2.90,
      barDir: "bar",
      barGrouping: "clustered",
      chartColors: [PALETTE.teal],
      showLegend: false,
      showTitle: false,
      showValue: true,
      dataLabelPosition: "outEnd",
      dataLabelColor: PALETTE.navyDark,
      dataLabelFontFace: FONT_HEAD,
      dataLabelFontSize: 11,
      dataLabelFormatCode: '0"%"',
      catAxisLabelColor: PALETTE.slate700,
      catAxisLabelFontFace: FONT_BODY,
      catAxisLabelFontSize: 11,
      valAxisMinVal: 0,
      valAxisMaxVal: 72,
      valAxisHidden: true,
      valGridLine: { style: "none" },
      catGridLine: { style: "none" },
    }
  );

  // Bottom-right Mint Soft Associations Panel (15.5 pt heading + 14.0 pt body)
  slide.addShape("roundRect", {
    x: 8.25,
    y: 3.38,
    w: 4.43,
    h: 3.54,
    rectRadius: 0.08,
    fill: { color: PALETTE.mintSoft },
    line: { type: "none" },
  });
  slide.addShape("rect", {
    x: 8.25,
    y: 3.54,
    w: 0.08,
    h: 3.22,
    fill: { color: PALETTE.teal },
    line: { type: "none" },
  });
  const icHeart = iconPath("heart_teal_dark.png");
  if (icHeart) {
    slide.addImage({ path: icHeart, x: 8.50, y: 3.56, w: 0.28, h: 0.28 });
  }
  slide.addText(data.associations_card.title, {
    x: 8.86,
    y: 3.48,
    w: 3.68,
    h: 0.50,
    fontFace: FONT_HEAD,
    fontSize: 15.5,
    bold: true,
    color: PALETTE.tealDark,
    valign: "middle",
    margin: 0,
  });

  const assocRuns = data.associations_card.items.map((item) => ({
    text: item,
    options: {
      bullet: { code: "25AA", color: PALETTE.teal },
      fontFace: FONT_BODY,
      fontSize: 14,
      color: PALETTE.navyMid,
      paraSpaceAfter: 12,
      breakLine: true,
    },
  }));
  slide.addText(assocRuns, {
    x: 8.52,
    y: 4.10,
    w: 3.98,
    h: 2.66,
    valign: "top",
    margin: 0,
  });

  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function buildTopFigurePlusStrip(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  // Top White Figure Card (x: 0.60", y: 1.48", w: 12.13", h: 2.94")
  const topX = 0.60;
  const topY = 1.48;
  const topW = 12.13;
  const topH = 2.94;

  slide.addShape("roundRect", {
    x: topX,
    y: topY,
    w: topW,
    h: topH,
    rectRadius: 0.08,
    fill: { color: PALETTE.white },
    line: { color: PALETTE.slate200, width: 1 },
  });

  const imgPath = path.join(__dirname, "extracted_assets", data.figure.image_file);
  if (!fs.existsSync(imgPath)) {
    throw new Error(`Missing extracted asset: ${imgPath}`);
  }
  const dims = getPngDimensions(imgPath);
  const padTop = 0.12;
  const captionZoneH = 0.56;
  const maxW = topW - 0.48;
  const maxH = topH - padTop - captionZoneH; // 2.26"
  const scale = Math.min(maxW / dims.width, maxH / dims.height);
  const picW = dims.width * scale;
  const picH = dims.height * scale;
  const picX = topX + (topW - picW) / 2;
  const picY = topY + padTop + (maxH - picH) / 2;

  slide.addImage({
    path: imgPath,
    x: picX,
    y: picY,
    w: picW,
    h: picH,
    sizing: { type: "contain", w: picW, h: picH },
  });

  slide.addText(data.figure.title, {
    x: topX + 0.24,
    y: topY + topH - 0.55,
    w: topW - 0.48,
    h: 0.26,
    fontFace: FONT_HEAD,
    fontSize: 10.5,
    bold: true,
    color: PALETTE.navyMid,
    align: "center",
    valign: "middle",
    margin: 0,
  });

  slide.addText(`Source: ${data.figure.source}`, {
    x: topX + 0.24,
    y: topY + topH - 0.28,
    w: topW - 0.48,
    h: 0.22,
    fontFace: FONT_BODY,
    fontSize: 9.5,
    italic: true,
    color: PALETTE.slate500,
    align: "center",
    valign: "middle",
    margin: 0,
  });

  // Bottom 4-column card strip (y: 4.58", h: 2.24") — 15.5 pt head + 14.0 pt body
  const stripY = 4.58;
  const stripH = 2.24;
  const n = data.bullets.length;
  const gap = 0.20;
  const cardW = (topW - gap * (n - 1)) / n; // 2.8825"
  const tones = ["teal", "navy", "teal", "amber"];

  data.bullets.forEach((b, idx) => {
    const cx = topX + idx * (cardW + gap);
    const tone = tones[idx % tones.length];
    const isWarn = tone === "amber";
    const barCol =
      tone === "amber" ? PALETTE.amber : tone === "navy" ? PALETTE.navyDark : PALETTE.teal;
    const bgCol = isWarn ? PALETTE.amberSoft : PALETTE.white;
    const headCol = isWarn ? PALETTE.amberDark : PALETTE.navyDark;

    slide.addShape("roundRect", {
      x: cx,
      y: stripY,
      w: cardW,
      h: stripH,
      rectRadius: 0.08,
      fill: { color: bgCol },
      line: { color: isWarn ? "FDE68A" : PALETTE.slate200, width: 1 },
    });

    slide.addShape("rect", {
      x: cx,
      y: stripY + 0.14,
      w: 0.08,
      h: stripH - 0.28,
      fill: { color: barCol },
      line: { type: "none" },
    });

    slide.addText(b.head, {
      x: cx + 0.18,
      y: stripY + 0.14,
      w: cardW - 0.28,
      h: 0.36,
      fontFace: FONT_HEAD,
      fontSize: 15,
      bold: true,
      color: headCol,
      valign: "middle",
      margin: 0,
    });

    slide.addShape("rect", {
      x: cx + 0.18,
      y: stripY + 0.54,
      w: cardW - 0.30,
      h: 0.015,
      fill: { color: isWarn ? "FDE68A" : PALETTE.slate200 },
      line: { type: "none" },
    });

    slide.addText(b.desc, {
      x: cx + 0.18,
      y: stripY + 0.62,
      w: cardW - 0.28,
      h: stripH - 0.72,
      fontFace: FONT_BODY,
      fontSize: 14,
      color: PALETTE.slate700,
      lineSpacingMultiple: 1.16,
      valign: "top",
      margin: 0,
    });
  });

  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function buildSplitGradingTableCard(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  const cardY = 1.56;
  const cardH = 5.36; // bottom = 6.92"
  const leftW = 5.15;
  const rightX = 0.65 + leftW + 0.25;
  const rightW = 12.68 - rightX; // 6.63"

  const gradeStyles = [
    { badge: "GRADE I", color: PALETTE.teal, bg: PALETTE.mintBg, txt: PALETTE.tealDark },
    { badge: "GRADE II", color: PALETTE.blueAccent, bg: PALETTE.blueSoft, txt: PALETTE.blueAccent },
    { badge: "GRADE III", color: PALETTE.amber, bg: PALETTE.amberBg, txt: PALETTE.amberDark },
    { badge: "GRADE IV", color: PALETTE.coral, bg: "FEE2E2", txt: PALETTE.coral },
  ];

  const nRows = 4;
  const rowH = 0.99;
  const rowGap = 0.13;
  data.bullets.slice(0, nRows).forEach((b, idx) => {
    const ry = cardY + idx * (rowH + rowGap);
    const gs = gradeStyles[idx];

    slide.addShape("roundRect", {
      x: 0.65,
      y: ry,
      w: leftW,
      h: rowH,
      rectRadius: 0.06,
      fill: { color: PALETTE.white },
      line: { type: "none" },
    });
    slide.addShape("rect", {
      x: 0.65,
      y: ry + 0.10,
      w: 0.07,
      h: rowH - 0.20,
      fill: { color: gs.color },
      line: { type: "none" },
    });
    slide.addShape("roundRect", {
      x: 0.84,
      y: ry + 0.12,
      w: 1.18,
      h: 0.26,
      rectRadius: 0.05,
      fill: { color: gs.bg },
      line: { type: "none" },
    });
    slide.addText(gs.badge, {
      x: 0.84,
      y: ry + 0.12,
      w: 1.18,
      h: 0.26,
      fontFace: FONT_HEAD,
      fontSize: 9.5,
      bold: true,
      color: gs.txt,
      align: "center",
      valign: "middle",
      margin: 0,
    });
    slide.addText(b.head.replace(/^Grade\s+[IVX]+\s*/, ""), {
      x: 2.12,
      y: ry + 0.11,
      w: leftW - 1.62,
      h: 0.28,
      fontFace: FONT_HEAD,
      fontSize: 13.5,
      bold: true,
      color: PALETTE.navyDark,
      valign: "middle",
      margin: 0,
    });
    slide.addText(b.desc, {
      x: 0.84,
      y: ry + 0.43,
      w: leftW - 0.34,
      h: 0.50,
      fontFace: FONT_BODY,
      fontSize: 13,
      color: PALETTE.slate700,
      lineSpacingMultiple: 1.15,
      valign: "top",
      margin: 0,
    });
  });

  if (data.bullets[4]) {
    const ny = cardY + 4 * rowH + 3 * rowGap + 0.14;
    const nh = cardY + cardH - ny;
    slide.addShape("roundRect", {
      x: 0.65,
      y: ny,
      w: leftW,
      h: nh,
      rectRadius: 0.06,
      fill: { color: PALETTE.mintSoft },
      line: { type: "none" },
    });
    slide.addShape("rect", {
      x: 0.65,
      y: ny + 0.10,
      w: 0.07,
      h: nh - 0.20,
      fill: { color: PALETTE.teal },
      line: { type: "none" },
    });
    slide.addText(`${data.bullets[4].head}: ${data.bullets[4].desc}`, {
      x: 0.84,
      y: ny + 0.08,
      w: leftW - 0.34,
      h: nh - 0.16,
      fontFace: FONT_BODY,
      fontSize: 12.5,
      bold: true,
      color: PALETTE.tealDark,
      valign: "middle",
      margin: 0,
    });
  }

  drawFigureCard(slide, data.figure, rightX, cardY, rightW, cardH);
  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function buildSplitFigureSmart(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  const sid = data.slide_id;
  const n = data.bullets.length;

  // Variant C (Slides 5 & 11): De-Boxed Stacked Callout Strips ON LEFT + Figure ON RIGHT
  // Dynamically sizes 4-card (15.5 pt head / 14.0 pt body) vs >=5-card layouts
  if (sid === 5 || sid === 11) {
    const cardY = 1.56;
    const cardH = 5.36; // bottom = 6.92"
    const leftW = sid === 11 ? 6.08 : 5.95;
    const rightX = 0.65 + leftW + 0.25;
    const rightW = 12.68 - rightX;

    const gap = n >= 5 ? 0.14 : 0.16;
    const itemH = (cardH - gap * (n - 1)) / n; // n=4 -> 1.22" per card!

    data.bullets.forEach((b, idx) => {
      const iy = cardY + idx * (itemH + gap);
      const barCol = idx % 2 === 0 ? PALETTE.teal : PALETTE.navyDark;
      slide.addShape("roundRect", {
        x: 0.65,
        y: iy,
        w: leftW,
        h: itemH,
        rectRadius: 0.06,
        fill: { color: PALETTE.white },
        line: { type: "none" },
      });
      slide.addShape("rect", {
        x: 0.65,
        y: iy + 0.12,
        w: 0.07,
        h: itemH - 0.24,
        fill: { color: barCol },
        line: { type: "none" },
      });
      slide.addText(b.head, {
        x: 0.86,
        y: iy + (n >= 5 ? 0.08 : 0.10),
        w: leftW - 0.34,
        h: 0.28,
        fontFace: FONT_HEAD,
        fontSize: n >= 5 ? 13 : 15.5,
        bold: true,
        color: PALETTE.navyDark,
        valign: "middle",
        margin: 0,
      });
      slide.addText(b.desc, {
        x: 0.86,
        y: iy + (n >= 5 ? 0.36 : 0.42),
        w: leftW - 0.34,
        h: itemH - (n >= 5 ? 0.42 : 0.48),
        fontFace: FONT_BODY,
        fontSize: n >= 5 ? 12 : 14,
        color: PALETTE.slate700,
        lineSpacingMultiple: n >= 5 ? 1.15 : 1.14,
        valign: "top",
        margin: 0,
      });
    });

    drawFigureCard(slide, data.figure, rightX, cardY, rightW, cardH);
    addFooter(slide, data.footnote, slideNum, totalSlides, false);
    return;
  }

  // Variant D (Slides 3 & 9): Clean Left/Right White Cards (15.5 pt head / 14.0 pt body)
  const cardY = 1.56;
  const cardH = 5.36; // bottom = 6.92"
  const leftW = 6.02;
  const rightX = 0.65 + leftW + 0.25;
  const rightW = 12.68 - rightX;

  slide.addShape("roundRect", {
    x: 0.65,
    y: cardY,
    w: leftW,
    h: cardH,
    rectRadius: 0.08,
    fill: { color: PALETTE.white },
    line: { color: PALETTE.slate200, width: 1 },
  });

  const itemH = (cardH - 0.38) / n; // 1.245" per item for n=4
  data.bullets.forEach((b, idx) => {
    const iy = cardY + 0.20 + idx * itemH;
    if (idx > 0) {
      slide.addShape("rect", {
        x: 0.90,
        y: iy - 0.06,
        w: leftW - 0.50,
        h: 0.012,
        fill: { color: PALETTE.slate200 },
        line: { type: "none" },
      });
    }
    slide.addShape("ellipse", {
      x: 0.92,
      y: iy + 0.13,
      w: 0.16,
      h: 0.16,
      fill: { color: PALETTE.teal },
      line: { type: "none" },
    });
    slide.addText(b.head, {
      x: 1.22,
      y: iy + 0.04,
      w: leftW - 0.78,
      h: 0.32,
      fontFace: FONT_HEAD,
      fontSize: 15.5,
      bold: true,
      color: PALETTE.navyDark,
      margin: 0,
    });
    slide.addText(b.desc, {
      x: 1.22,
      y: iy + 0.38,
      w: leftW - 0.78,
      h: itemH - 0.44,
      fontFace: FONT_BODY,
      fontSize: 14,
      color: PALETTE.slate700,
      lineSpacingMultiple: 1.14,
      valign: "top",
      margin: 0,
    });
  });

  drawFigureCard(slide, data.figure, rightX, cardY, rightW, cardH);
  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function buildQuadrant2x2(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  const toneMap = {
    navy: { bar: PALETTE.navyDark, bg: PALETTE.white, badgeBg: "E2E8F0", badgeText: PALETTE.navyDark },
    teal: { bar: PALETTE.teal, bg: PALETTE.white, badgeBg: PALETTE.mintBg, badgeText: PALETTE.tealDark },
    slate: { bar: PALETTE.blueAccent, bg: PALETTE.white, badgeBg: PALETTE.blueSoft, badgeText: PALETTE.blueAccent },
    amber: { bar: PALETTE.amber, bg: PALETTE.amberSoft, badgeBg: PALETTE.amberBg, badgeText: PALETTE.amberDark },
    coral: { bar: PALETTE.coral, bg: PALETTE.coralBg, badgeBg: "FEE2E2", badgeText: PALETTE.coral },
  };

  const iconSets = {
    7: ["hand_navy.png", "dot_teal.png", "bone_blue.png", "baby_amber.png"],
    13: ["shield_navy.png", "warn_amber.png", "syringe_coral.png", "scissors_blue.png"],
  };
  const slideIcons = iconSets[data.slide_id] || [];

  const cardW = 5.86;
  const cardH = 2.50;
  const gapX = 0.31;
  const gapY = 0.28;

  data.quadrants.forEach((q, idx) => {
    const col = idx % 2;
    const row = Math.floor(idx / 2);
    const x = 0.65 + col * (cardW + gapX);
    const y = 1.62 + row * (cardH + gapY);
    const st = toneMap[q.tone] || toneMap.navy;

    slide.addShape("roundRect", {
      x,
      y,
      w: cardW,
      h: cardH,
      rectRadius: 0.08,
      fill: { color: st.bg },
      line: { type: "none" },
    });

    slide.addShape("rect", {
      x,
      y: y + 0.14,
      w: 0.09,
      h: cardH - 0.28,
      fill: { color: st.bar },
      line: { type: "none" },
    });

    const badgeW = Math.min(cardW - 1.15, Math.max(2.10, q.tag.length * 0.11 + 0.45));
    slide.addShape("roundRect", {
      x: x + 0.28,
      y: y + 0.18,
      w: badgeW,
      h: 0.28,
      rectRadius: 0.06,
      fill: { color: st.badgeBg },
      line: { type: "none" },
    });
    slide.addText(q.tag, {
      x: x + 0.28,
      y: y + 0.18,
      w: badgeW,
      h: 0.28,
      fontFace: FONT_HEAD,
      fontSize: 9.5,
      bold: true,
      color: st.badgeText,
      align: "center",
      valign: "middle",
      margin: 0,
    });

    const icName = q.icon || slideIcons[idx];
    const ic = icName ? iconPath(icName) : null;
    if (ic) {
      slide.addShape("ellipse", {
        x: x + cardW - 0.66,
        y: y + 0.16,
        w: 0.44,
        h: 0.44,
        fill: { color: st.badgeBg },
        line: { type: "none" },
      });
      slide.addImage({
        path: ic,
        x: x + cardW - 0.56,
        y: y + 0.26,
        w: 0.24,
        h: 0.24,
      });
    }

    slide.addText(q.title, {
      x: x + 0.28,
      y: y + 0.52,
      w: cardW - 1.05,
      h: 0.36,
      fontFace: FONT_HEAD,
      fontSize: 16.5,
      bold: true,
      color: PALETTE.navyDark,
      margin: 0,
    });

    slide.addText(q.finding, {
      x: x + 0.28,
      y: y + 0.94,
      w: cardW - 0.48,
      h: 0.72,
      fontFace: FONT_BODY,
      fontSize: 13.5,
      color: PALETTE.slate700,
      lineSpacingMultiple: 1.14,
      margin: 0,
    });

    slide.addShape("rect", {
      x: x + 0.28,
      y: y + 1.74,
      w: cardW - 0.48,
      h: 0.015,
      fill: { color: PALETTE.slate200 },
      line: { type: "none" },
    });
    slide.addText(q.key_rule, {
      x: x + 0.28,
      y: y + 1.82,
      w: cardW - 0.48,
      h: 0.58,
      fontFace: FONT_BODY,
      fontSize: 13,
      bold: true,
      color: st.bar,
      lineSpacingMultiple: 1.14,
      margin: 0,
    });
  });

  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function buildBento2ColCare(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  const colToneMap = {
    teal: {
      headerBg: PALETTE.tealDark,
      bar: PALETTE.teal,
      cardBg: PALETTE.white,
      badgeBg: PALETTE.mintBg,
      badgeTxt: PALETTE.tealDark,
      icons: ["pill_teal.png", "waves_teal.png"],
    },
    amber: {
      headerBg: PALETTE.amber,
      bar: PALETTE.amber,
      cardBg: PALETTE.amberSoft,
      badgeBg: PALETTE.amberBg,
      badgeTxt: PALETTE.amberDark,
      icons: ["clock_amber.png", "layers_amber.png"],
    },
  };

  const colW = 5.86;
  const gapX = 0.31;

  data.columns.forEach((col, colIdx) => {
    const x = 0.65 + colIdx * (colW + gapX);
    const st = colToneMap[col.tone] || colToneMap.teal;

    slide.addShape("roundRect", {
      x,
      y: 1.62,
      w: colW,
      h: 0.44,
      rectRadius: 0.06,
      fill: { color: st.headerBg },
      line: { type: "none" },
    });
    slide.addText(col.header, {
      x: x + 0.20,
      y: 1.62,
      w: colW - 0.40,
      h: 0.44,
      fontFace: FONT_HEAD,
      fontSize: 12,
      bold: true,
      charSpacing: 1.0,
      color: PALETTE.white,
      valign: "middle",
      margin: 0,
    });

    const cardH = 2.24;
    const cardGap = 0.26;
    col.cards.forEach((c, cardIdx) => {
      const y = 2.18 + cardIdx * (cardH + cardGap);

      slide.addShape("roundRect", {
        x,
        y,
        w: colW,
        h: cardH,
        rectRadius: 0.08,
        fill: { color: st.cardBg },
        line: { type: "none" },
      });

      slide.addShape("rect", {
        x,
        y: y + 0.16,
        w: 0.09,
        h: cardH - 0.32,
        fill: { color: st.bar },
        line: { type: "none" },
      });

      const badgeW = Math.min(colW - 1.15, Math.max(2.15, c.tag.length * 0.11 + 0.45));
      slide.addShape("roundRect", {
        x: x + 0.28,
        y: y + 0.20,
        w: badgeW,
        h: 0.28,
        rectRadius: 0.05,
        fill: { color: st.badgeBg },
        line: { type: "none" },
      });
      slide.addText(c.tag, {
        x: x + 0.28,
        y: y + 0.20,
        w: badgeW,
        h: 0.28,
        fontFace: FONT_HEAD,
        fontSize: 9.5,
        bold: true,
        color: st.badgeTxt,
        align: "center",
        valign: "middle",
        margin: 0,
      });

      const ic = st.icons[cardIdx] ? iconPath(st.icons[cardIdx]) : null;
      if (ic) {
        slide.addShape("ellipse", {
          x: x + colW - 0.70,
          y: y + 0.20,
          w: 0.48,
          h: 0.48,
          fill: { color: st.badgeBg },
          line: { type: "none" },
        });
        slide.addImage({
          path: ic,
          x: x + colW - 0.59,
          y: y + 0.31,
          w: 0.26,
          h: 0.26,
        });
      }

      slide.addText(c.title, {
        x: x + 0.28,
        y: y + 0.58,
        w: colW - 1.05,
        h: 0.40,
        fontFace: FONT_HEAD,
        fontSize: 17,
        bold: true,
        color: PALETTE.navyDark,
        margin: 0,
      });

      slide.addShape("rect", {
        x: x + 0.28,
        y: y + 1.06,
        w: colW - 0.50,
        h: 0.015,
        fill: { color: PALETTE.slate200 },
        line: { type: "none" },
      });

      slide.addText(c.body, {
        x: x + 0.28,
        y: y + 1.18,
        w: colW - 0.50,
        h: 0.92,
        fontFace: FONT_BODY,
        fontSize: 14,
        color: PALETTE.slate700,
        lineSpacingMultiple: 1.24,
        margin: 0,
      });
    });
  });

  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function buildChartPlusComparisonCards(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  // Left Chart Card
  const chartCardW = 6.45;
  slide.addShape("roundRect", {
    x: 0.65,
    y: 1.62,
    w: chartCardW,
    h: 5.30,
    rectRadius: 0.08,
    fill: { color: PALETTE.white },
    line: { type: "none" },
  });
  slide.addText(data.chart.title, {
    x: 0.88,
    y: 1.78,
    w: chartCardW - 0.46,
    h: 0.36,
    fontFace: FONT_HEAD,
    fontSize: 14.5,
    bold: true,
    color: PALETTE.navyDark,
    margin: 0,
  });

  const s = data.chart.series[0];
  slide.addChart(
    pres.ChartType.bar,
    [
      {
        name: s.name,
        labels: s.categories,
        values: s.values,
      },
    ],
    {
      x: 0.80,
      y: 2.16,
      w: chartCardW - 0.30,
      h: 4.62,
      barDir: "bar",
      barGrouping: "clustered",
      chartColors: [PALETTE.teal],
      showLegend: false,
      showTitle: false,
      showValue: true,
      dataLabelPosition: "outEnd",
      dataLabelColor: PALETTE.navyDark,
      dataLabelFontFace: FONT_HEAD,
      dataLabelFontSize: 11,
      dataLabelFormatCode: '0"%"',
      catAxisLabelColor: PALETTE.slate700,
      catAxisLabelFontFace: FONT_BODY,
      catAxisLabelFontSize: 10.5,
      valAxisMinVal: 0,
      valAxisMaxVal: 112,
      valAxisHidden: true,
      valGridLine: { style: "none" },
      catGridLine: { style: "none" },
    }
  );

  // Right 3 Comparison Cards (15.5 pt heading + 14.0 pt body)
  const toneStyles = {
    teal: { accent: PALETTE.teal, bg: PALETTE.white, badgeBg: PALETTE.mintBg, badgeTxt: PALETTE.tealDark, icon: "check_teal.png" },
    coral: { accent: PALETTE.coral, bg: PALETTE.coralBg, badgeBg: "FEE2E2", badgeTxt: PALETTE.coral, icon: "alert_coral.png" },
    amber: { accent: PALETTE.amber, bg: PALETTE.amberSoft, badgeBg: PALETTE.amberBg, badgeTxt: PALETTE.amberDark, icon: "clock_amber.png" },
  };

  const cardX = 7.34;
  const cardW = 5.34; // 7.34 + 5.34 = 12.68"
  const cardH = 1.64;
  const gap = 0.19; // 1.62 + 3*1.64 + 2*0.19 = 6.92"

  data.comparison_cards.forEach((c, idx) => {
    const y = 1.62 + idx * (cardH + gap);
    const st = toneStyles[c.tone] || toneStyles.teal;

    slide.addShape("roundRect", {
      x: cardX,
      y,
      w: cardW,
      h: cardH,
      rectRadius: 0.08,
      fill: { color: st.bg },
      line: { type: "none" },
    });
    slide.addShape("rect", {
      x: cardX,
      y: y + 0.14,
      w: 0.08,
      h: cardH - 0.28,
      fill: { color: st.accent },
      line: { type: "none" },
    });

    const badgeW = Math.min(cardW - 1.05, Math.max(2.15, c.badge.length * 0.11 + 0.40));
    slide.addShape("roundRect", {
      x: cardX + 0.24,
      y: y + 0.12,
      w: badgeW,
      h: 0.25,
      rectRadius: 0.05,
      fill: { color: st.badgeBg },
      line: { type: "none" },
    });
    slide.addText(c.badge, {
      x: cardX + 0.24,
      y: y + 0.12,
      w: badgeW,
      h: 0.25,
      fontFace: FONT_HEAD,
      fontSize: 9,
      bold: true,
      color: st.badgeTxt,
      align: "center",
      valign: "middle",
      margin: 0,
    });

    const ic = iconPath(st.icon);
    if (ic) {
      slide.addImage({
        path: ic,
        x: cardX + cardW - 0.48,
        y: y + 0.12,
        w: 0.28,
        h: 0.28,
      });
    }

    slide.addText(c.title, {
      x: cardX + 0.24,
      y: y + 0.41,
      w: cardW - 0.46,
      h: 0.34,
      fontFace: FONT_HEAD,
      fontSize: 15.5,
      bold: true,
      color: PALETTE.navyDark,
      valign: "middle",
      margin: 0,
    });

    slide.addText(c.body, {
      x: cardX + 0.24,
      y: y + 0.78,
      w: cardW - 0.46,
      h: 0.78,
      fontFace: FONT_BODY,
      fontSize: 14,
      color: PALETTE.slate700,
      lineSpacingMultiple: 1.14,
      valign: "top",
      margin: 0,
    });
  });

  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function buildComparison2ColPlusStats(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  const toneMap = {
    navy: {
      headerBg: PALETTE.navyDark,
      accent: PALETTE.navyDark,
      kpiBg: PALETTE.slate100,
      pillBg: "E2E8F0",
      pillTxt: PALETTE.navyDark,
      icon: "scissors_white.png",
    },
    teal: {
      headerBg: PALETTE.tealDark,
      accent: PALETTE.teal,
      kpiBg: PALETTE.mintSoft,
      pillBg: PALETTE.mintBg,
      pillTxt: PALETTE.tealDark,
      icon: "syringe_white.png",
    },
  };

  const colW = 5.86;
  const colH = 5.30;
  const gapX = 0.31;

  data.columns.forEach((col, colIdx) => {
    const x = 0.65 + colIdx * (colW + gapX);
    const y = 1.62;
    const st = toneMap[col.tone] || toneMap.navy;

    slide.addShape("roundRect", {
      x,
      y,
      w: colW,
      h: colH,
      rectRadius: 0.08,
      fill: { color: PALETTE.white },
      line: { type: "none" },
    });

    slide.addShape("roundRect", {
      x,
      y,
      w: colW,
      h: 0.46,
      rectRadius: 0.06,
      fill: { color: st.headerBg },
      line: { type: "none" },
    });
    const ic = iconPath(st.icon);
    if (ic) {
      slide.addImage({ path: ic, x: x + 0.18, y: y + 0.10, w: 0.26, h: 0.26 });
    }
    slide.addText(col.header, {
      x: x + 0.54,
      y,
      w: colW - 0.74,
      h: 0.46,
      fontFace: FONT_HEAD,
      fontSize: 13,
      bold: true,
      charSpacing: 1.0,
      color: PALETTE.white,
      valign: "middle",
      margin: 0,
    });

    const kpiX = x + 0.22;
    const kpiY = y + 0.58;
    const kpiW = colW - 0.44;
    const kpiH = 1.28;

    slide.addShape("roundRect", {
      x: kpiX,
      y: kpiY,
      w: kpiW,
      h: kpiH,
      rectRadius: 0.06,
      fill: { color: st.kpiBg },
      line: { type: "none" },
    });
    slide.addShape("rect", {
      x: kpiX,
      y: kpiY + 0.10,
      w: 0.08,
      h: kpiH - 0.20,
      fill: { color: st.accent },
      line: { type: "none" },
    });

    slide.addText(col.stat_value, {
      x: kpiX + 0.20,
      y: kpiY + 0.08,
      w: kpiW - 0.36,
      h: 0.50,
      fontFace: FONT_HEAD,
      fontSize: 30,
      bold: true,
      color: st.accent,
      margin: 0,
    });
    slide.addText(col.stat_label, {
      x: kpiX + 0.20,
      y: kpiY + 0.62,
      w: kpiW - 0.36,
      h: col.source ? 0.38 : 0.54,
      fontFace: FONT_HEAD,
      fontSize: 12.5,
      bold: true,
      color: PALETTE.navyMid,
      valign: "top",
      margin: 0,
    });
    if (col.source) {
      slide.addText(col.source, {
        x: kpiX + 0.20,
        y: kpiY + 1.00,
        w: kpiW - 0.36,
        h: 0.22,
        fontFace: FONT_BODY,
        fontSize: 9.5,
        italic: true,
        color: PALETTE.slate500,
        margin: 0,
      });
    }

    const rowsTop = kpiY + kpiH + 0.18;
    const rowH = 1.04;
    col.rows.forEach((r, rowIdx) => {
      const ry = rowsTop + rowIdx * rowH;
      if (rowIdx > 0) {
        slide.addShape("rect", {
          x: x + 0.22,
          y: ry - 0.07,
          w: colW - 0.44,
          h: 0.015,
          fill: { color: PALETTE.slate200 },
          line: { type: "none" },
        });
      }

      slide.addShape("roundRect", {
        x: x + 0.22,
        y: ry + 0.06,
        w: 1.50,
        h: 0.34,
        rectRadius: 0.05,
        fill: { color: st.pillBg },
        line: { type: "none" },
      });
      slide.addText(r.attr, {
        x: x + 0.22,
        y: ry + 0.06,
        w: 1.50,
        h: 0.34,
        fontFace: FONT_HEAD,
        fontSize: 11,
        bold: true,
        color: st.pillTxt,
        align: "center",
        valign: "middle",
        margin: 0,
      });

      slide.addText(r.text, {
        x: x + 1.86,
        y: ry + 0.04,
        w: colW - 2.08,
        h: 0.92,
        fontFace: FONT_BODY,
        fontSize: 13.5,
        color: PALETTE.slate700,
        lineSpacingMultiple: 1.16,
        valign: "top",
        margin: 0,
      });
    });
  });

  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function buildProcessContinuum4Step(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  const toneMap = {
    navy: { header: PALETTE.navyDark, accent: PALETTE.navyDark, icon: "hand_white.png" },
    teal: { header: PALETTE.teal, accent: PALETTE.tealDark, icon: "syringe_white.png" },
    navy_mid: { header: PALETTE.navyMid, accent: PALETTE.blueAccent, icon: "scissors_white.png" },
    teal_bright: { header: PALETTE.tealDark, accent: PALETTE.teal, icon: "activity_white.png" },
  };

  const cardW = 2.80;
  const gap = 0.277;
  const cardY = 1.56;
  const cardH = 5.36; // bottom = 6.92"

  data.steps.forEach((step, idx) => {
    const x = 0.65 + idx * (cardW + gap);
    const st = toneMap[step.tone] || toneMap.navy;

    slide.addShape("roundRect", {
      x,
      y: cardY,
      w: cardW,
      h: cardH,
      rectRadius: 0.08,
      fill: { color: PALETTE.white },
      line: { type: "none" },
    });

    slide.addShape("roundRect", {
      x,
      y: cardY,
      w: cardW,
      h: 0.84,
      rectRadius: 0.06,
      fill: { color: st.header },
      line: { type: "none" },
    });

    const ic = iconPath(st.icon);
    if (ic) {
      slide.addImage({
        path: ic,
        x: x + cardW - 0.46,
        y: cardY + 0.12,
        w: 0.28,
        h: 0.28,
      });
    }

    slide.addText(step.step_label, {
      x: x + 0.16,
      y: cardY + 0.10,
      w: cardW - 0.68,
      h: 0.22,
      fontFace: FONT_HEAD,
      fontSize: 10,
      bold: true,
      charSpacing: 1.2,
      color: PALETTE.mintBg,
      margin: 0,
    });
    slide.addText(step.title, {
      x: x + 0.16,
      y: cardY + 0.34,
      w: cardW - 0.32,
      h: 0.42,
      fontFace: FONT_HEAD,
      fontSize: 15.5,
      bold: true,
      color: PALETTE.white,
      valign: "middle",
      margin: 0,
    });

    if (idx < data.steps.length - 1) {
      slide.addShape("chevron", {
        x: x + cardW + 0.035,
        y: cardY + 0.27,
        w: 0.205,
        h: 0.30,
        fill: { color: PALETTE.teal },
        line: { type: "none" },
      });
    }

    // 4x3 Grid Boxes — balanced 13.0 pt body with clean divider clearance
    const itemsTop = cardY + 0.96; // y = 2.52"
    const itemPitch = 1.44; // 3 * 1.44 = 4.32" -> ends at 6.84"
    step.items.forEach((item, itemIdx) => {
      const iy = itemsTop + itemIdx * itemPitch;
      if (itemIdx > 0) {
        slide.addShape("rect", {
          x: x + 0.16,
          y: iy - 0.09,
          w: cardW - 0.32,
          h: 0.015,
          fill: { color: PALETTE.slate200 },
          line: { type: "none" },
        });
      }

      slide.addText(item.label.toUpperCase(), {
        x: x + 0.16,
        y: iy,
        w: cardW - 0.32,
        h: 0.24,
        fontFace: FONT_HEAD,
        fontSize: 10.5,
        bold: true,
        charSpacing: 0.8,
        color: st.accent,
        margin: 0,
      });

      slide.addText(item.text, {
        x: x + 0.16,
        y: iy + 0.26,
        w: cardW - 0.32,
        h: itemPitch - 0.40, // 1.04"
        fontFace: FONT_BODY,
        fontSize: 13,
        color: PALETTE.slate700,
        lineSpacingMultiple: 1.12,
        valign: "top",
        margin: 0,
      });
    });
  });

  addFooter(slide, data.footnote, slideNum, totalSlides, false);
}

function renderDarkCard(slide, c, x, y, w, h, iconName) {
  slide.addShape("roundRect", {
    x,
    y,
    w,
    h,
    rectRadius: 0.08,
    fill: { color: PALETTE.navyMid },
    line: { color: "334155", width: 1 },
  });

  slide.addShape("ellipse", {
    x: x + 0.24,
    y: y + 0.22,
    w: 0.44,
    h: 0.44,
    fill: { color: PALETTE.teal },
    line: { type: "none" },
  });
  slide.addText(c.num, {
    x: x + 0.24,
    y: y + 0.22,
    w: 0.44,
    h: 0.44,
    fontFace: FONT_HEAD,
    fontSize: 13,
    bold: true,
    color: PALETTE.white,
    align: "center",
    valign: "middle",
    margin: 0,
  });

  const ic = iconName ? iconPath(iconName) : null;
  if (ic) {
    slide.addImage({
      path: ic,
      x: x + w - 0.50,
      y: y + 0.27,
      w: 0.28,
      h: 0.28,
    });
  }

  slide.addText(c.title, {
    x: x + 0.76,
    y: y + 0.23,
    w: w - 1.34,
    h: 0.42,
    fontFace: FONT_HEAD,
    fontSize: w < 4.5 ? 14.5 : 16,
    bold: true,
    color: PALETTE.tealBright,
    valign: "middle",
    margin: 0,
  });

  slide.addText(c.body, {
    x: x + 0.24,
    y: y + 0.80,
    w: w - 0.48,
    h: h - 0.96,
    fontFace: FONT_BODY,
    fontSize: 14.5,
    color: "E2E8F0",
    lineSpacingMultiple: 1.18,
    margin: 0,
  });
}

function buildDarkBentoTakehome(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, true);
  slide.background = { color: PALETTE.navyDark };
  addEditorialHeader(slide, data, true);

  const cardIcons = [
    "microscope_white.png",
    "shieldcheck_white.png",
    "syringe_white.png",
    "heart_white.png",
    "activity_white.png",
  ];

  const topW = 3.81;
  const topH = 2.45;
  const gap = 0.30;

  data.cards.slice(0, 3).forEach((c, idx) => {
    const x = 0.65 + idx * (topW + gap);
    const y = 1.66;
    renderDarkCard(slide, c, x, y, topW, topH, cardIcons[idx]);
  });

  const botW = 5.86;
  const botH = 2.45;
  data.cards.slice(3, 5).forEach((c, idx) => {
    const x = 0.65 + idx * (botW + 0.31);
    const y = 4.35;
    renderDarkCard(slide, c, x, y, botW, botH, cardIcons[3 + idx]);
  });

  addFooter(slide, data.footnote, slideNum, totalSlides, true);
}

function buildReferencesSlide(pres, data, slideNum, totalSlides) {
  const slide = createSlideWithSup(pres, false);
  slide.background = { color: PALETTE.bgLight };
  addEditorialHeader(slide, data, false);

  const refs = data.references || [];
  const startY = 1.56;
  const rowH = 1.24;
  const gap = 0.14;

  refs.forEach((r, idx) => {
    const y = startY + idx * (rowH + gap);
    const isEven = idx % 2 === 0;
    const accent = isEven ? PALETTE.teal : PALETTE.navyDark;
    const badgeBg = isEven ? PALETTE.mintBg : "E2E8F0";
    const badgeTxt = isEven ? PALETTE.tealDark : PALETTE.navyDark;

    slide.addShape("roundRect", {
      x: 0.65,
      y,
      w: 12.03,
      h: rowH,
      rectRadius: 0.08,
      fill: { color: PALETTE.white },
      line: { type: "none" },
    });
    slide.addShape("rect", {
      x: 0.65,
      y: y + 0.12,
      w: 0.08,
      h: rowH - 0.24,
      fill: { color: accent },
      line: { type: "none" },
    });

    slide.addShape("roundRect", {
      x: 0.88,
      y: y + 0.37,
      w: 0.54,
      h: 0.50,
      rectRadius: 0.08,
      fill: { color: badgeBg },
      line: { type: "none" },
    });
    slide.addText(`[${r.id}]`, {
      x: 0.88,
      y: y + 0.37,
      w: 0.54,
      h: 0.50,
      fontFace: FONT_HEAD,
      fontSize: 16,
      bold: true,
      color: badgeTxt,
      align: "center",
      valign: "middle",
      margin: 0,
    });

    const slotX = 1.56;
    const maxW = 0.84;
    const maxH = 1.04;
    if (r.cover_image) {
      const covPath = path.join(__dirname, "extracted_assets", r.cover_image);
      if (fs.existsSync(covPath)) {
        const dims = getPngDimensions(covPath);
        const sc = Math.min(maxW / dims.width, maxH / dims.height);
        const cw = dims.width * sc;
        const ch = dims.height * sc;
        const cx = slotX + (maxW - cw) / 2;
        const cy = y + (rowH - ch) / 2;
        slide.addImage({ path: covPath, x: cx, y: cy, w: cw, h: ch });
        slide.addShape("rect", {
          x: cx,
          y: cy,
          w: cw,
          h: ch,
          fill: { type: "none" },
          line: { color: PALETTE.slate200, width: 0.75 },
        });
      }
    } else {
      const phW = 0.78;
      const phH = 1.02;
      const cx = slotX + (maxW - phW) / 2;
      const cy = y + (rowH - phH) / 2;
      slide.addShape("roundRect", {
        x: cx,
        y: cy,
        w: phW,
        h: phH,
        rectRadius: 0.06,
        fill: { color: PALETTE.slate100 },
        line: { color: PALETTE.slate300, width: 1 },
      });
      const icBook = iconPath("book_open_slate.png");
      if (icBook) {
        const icSz = 0.34;
        slide.addImage({
          path: icBook,
          x: cx + (phW - icSz) / 2,
          y: cy + (phH - icSz) / 2,
          w: icSz,
          h: icSz,
        });
      }
    }

    slide.addText(r.citation, {
      x: 2.58,
      y: y + 0.12,
      w: 9.86,
      h: 0.56,
      fontFace: FONT_BODY,
      fontSize: 13.5,
      bold: true,
      color: PALETTE.navyDark,
      valign: "top",
      margin: 0,
    });

    slide.addText(r.chapters_pages, {
      x: 2.58,
      y: y + 0.70,
      w: 9.86,
      h: 0.46,
      fontFace: FONT_BODY,
      fontSize: 12,
      color: PALETTE.tealDark,
      bold: true,
      lineSpacingMultiple: 1.12,
      valign: "top",
      margin: 0,
    });
  });

  addFooter(slide, "", slideNum, totalSlides, false);
}

function parseCliArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--evidence" && argv[i + 1]) out.evidence = argv[++i];
    else if (argv[i] === "--out" && argv[i + 1]) out.out = argv[++i];
    else if (argv[i] === "--theme" && argv[i + 1]) out.theme = argv[++i];
  }
  return out;
}

async function main() {
  const cli = parseCliArgs(process.argv.slice(2));
  const baseDir = __dirname;
  const themeName = cli.theme || "{{THEME_NAME}}";
  if (THEME_OVERRIDES[themeName]) {
    Object.assign(PALETTE, THEME_OVERRIDES[themeName]);
  }
  const specPath = path.resolve(baseDir, cli.evidence || "evidence_bundle.json");
  const outPptx = path.resolve(baseDir, cli.out || "{{PPTX_FILENAME}}");
  const spec = JSON.parse(fs.readFileSync(specPath, "utf-8"));

  const pres = new PptxGenJS();
  pres.layout = "LAYOUT_WIDE";
  pres.author = "{{PRESENTER_NAME}} (PM&R Resident Year 1, {{INSTITUTION}})";
  pres.title = spec.meta?.title || spec.slides?.[0]?.title || "{{TOPIC_TITLE}}";

  const totalSlides = spec.slides.length;
  spec.slides.forEach((slideData, idx) => {
    const slideNum = idx + 1;
    switch (slideData.archetype) {
      case "dark_hero_title":
        buildDarkHeroTitle(pres, slideData, slideNum, totalSlides);
        break;
      case "kpi_hero_plus_chart":
        buildKpiHeroPlusChart(pres, slideData, slideNum, totalSlides);
        break;
      case "top_figure_plus_strip":
        buildTopFigurePlusStrip(pres, slideData, slideNum, totalSlides);
        break;
      case "split_grading_table_card":
        buildSplitGradingTableCard(pres, slideData, slideNum, totalSlides);
        break;
      case "split_figure_card":
        buildSplitFigureSmart(pres, slideData, slideNum, totalSlides);
        break;
      case "quadrant_2x2_differential":
      case "quadrant_2x2_complications":
        buildQuadrant2x2(pres, slideData, slideNum, totalSlides);
        break;
      case "bento_2col_care":
        buildBento2ColCare(pres, slideData, slideNum, totalSlides);
        break;
      case "chart_plus_comparison_cards":
        buildChartPlusComparisonCards(pres, slideData, slideNum, totalSlides);
        break;
      case "comparison_2col_plus_stats":
        buildComparison2ColPlusStats(pres, slideData, slideNum, totalSlides);
        break;
      case "process_continuum_4step":
        buildProcessContinuum4Step(pres, slideData, slideNum, totalSlides);
        break;
      case "dark_bento_takehome":
        buildDarkBentoTakehome(pres, slideData, slideNum, totalSlides);
        break;
      case "references_slide":
        buildReferencesSlide(pres, { ...slideData, references: slideData.references || spec.references }, slideNum, totalSlides);
        break;
      default:
        throw new Error(`Unknown archetype: ${slideData.archetype}`);
    }
  });

  await pres.writeFile({ fileName: outPptx });
  console.log(`SUCCESS: Generated ${totalSlides} v2.8 slides -> ${outPptx}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
