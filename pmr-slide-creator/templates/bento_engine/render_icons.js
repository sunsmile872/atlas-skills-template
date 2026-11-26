#!/usr/bin/env node
/**
 * Render crisp Lucide SVG icons to transparent 128x128 PNGs in exact palette colors.
 */
const fs = require("fs");
const path = require("path");
const { Resvg } = require("../node_modules/@resvg/resvg-js");
const lucide = require("../node_modules/lucide-static");

const OUT_DIR = path.join(__dirname, "icons");

const ICON_SPECS = [
  // Slide 2 KPIs & Associations
  { icon: "Users", color: "#0D9488", name: "users_teal.png" },
  { icon: "TrendingUp", color: "#0F172A", name: "trend_navy.png" },
  { icon: "Activity", color: "#D97706", name: "activity_amber.png" },
  { icon: "HeartPulse", color: "#0F766E", name: "heart_teal_dark.png" },
  // Slide 7 Differential Dx
  { icon: "Hand", color: "#0F172A", name: "hand_navy.png" },
  { icon: "CircleDot", color: "#0D9488", name: "dot_teal.png" },
  { icon: "Bone", color: "#2563EB", name: "bone_blue.png" },
  { icon: "Baby", color: "#D97706", name: "baby_amber.png" },
  // Slide 8 Care & Red Flags
  { icon: "Pill", color: "#0F766E", name: "pill_teal.png" },
  { icon: "Waves", color: "#0D9488", name: "waves_teal.png" },
  { icon: "Clock", color: "#D97706", name: "clock_amber.png" },
  { icon: "Layers", color: "#B45309", name: "layers_amber.png" },
  // Slide 12 CSI Outcomes
  { icon: "CheckCircle2", color: "#0F766E", name: "check_teal.png" },
  { icon: "AlertTriangle", color: "#DC2626", name: "alert_coral.png" },
  // Slide 13 Complications
  { icon: "ShieldAlert", color: "#0F172A", name: "shield_navy.png" },
  { icon: "AlertCircle", color: "#D97706", name: "warn_amber.png" },
  { icon: "Syringe", color: "#DC2626", name: "syringe_coral.png" },
  { icon: "Scissors", color: "#2563EB", name: "scissors_blue.png" },
  // Slide 14 Surgical Comparison
  { icon: "Scissors", color: "#FFFFFF", name: "scissors_white.png" },
  { icon: "Syringe", color: "#FFFFFF", name: "syringe_white.png" },
  // Slide 15 Continuum Steps
  { icon: "Hand", color: "#FFFFFF", name: "hand_white.png" },
  { icon: "Activity", color: "#FFFFFF", name: "activity_white.png" },
  // Slide 16 Dark Bento
  { icon: "Microscope", color: "#FFFFFF", name: "microscope_white.png" },
  { icon: "ShieldCheck", color: "#FFFFFF", name: "shieldcheck_white.png" },
  { icon: "HeartPulse", color: "#FFFFFF", name: "heart_white.png" },
];

function main() {
  fs.mkdirSync(OUT_DIR, { recursive: true });
  for (const spec of ICON_SPECS) {
    const rawSvg = lucide[spec.icon];
    if (!rawSvg) throw new Error(`Unknown Lucide icon: ${spec.icon}`);
    const coloredSvg = rawSvg
      .replace(/stroke="currentColor"/g, `stroke="${spec.color}"`)
      .replace(/stroke-width="2"/g, 'stroke-width="2.2"');
    const resvg = new Resvg(coloredSvg, {
      fitTo: { mode: "width", value: 128 },
      background: "rgba(0,0,0,0)",
    });
    const pngData = resvg.render().asPng();
    fs.writeFileSync(path.join(OUT_DIR, spec.name), pngData);
  }
  console.log(`SUCCESS: Rendered ${ICON_SPECS.length} crisp Lucide PNG icons -> ${OUT_DIR}`);
}

main();
