// GRPO illustration slide: three groups of 8 sampled programs (e55 = the starting policy, K=8 at T=0.7) for three
// drawings, each candidate shown as its 3D render with reward r = IoU vs ground truth (0 if the program fails) and
// advantage A = r - group mean as a navy (reinforced) / orange (discouraged) bar. Every element is editable.
// Renders: complex_parts_render.py (--agree) -> parts/<key>/c{j}.png; rewards: parts/<key>/data.json.
//   NODE_PATH=<pptxgenjs> PPTX_SKILL=<pptx skill dir> node build_grpo_fig.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const FIG = path.join(__dirname, "..");
const GROUPS = [
  ["complex_parts/parts", "40a1be28", "Flared pedestal mount"],
  ["complex_parts/parts", "27b61d00", "Slotted cage sleeve"],
  ["real_parts/parts", "F_73525", "Handwheel (real part)"],
];
const THEME = {
  name: "Drawing to CAD", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: "13294B", lt2: "EEF2F8", accent1: "E84A27", accent2: "8A8F99",
            accent3: "5A5F69", accent4: "D3DEE0", accent5: "EEF4F0", accent6: "D6DEEA", hlink: "2F6FD6", folHlink: "5A5F69" },
};
const pxSize = f => { const b = fs.readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "GRPO group rewards";
const C = pres.SchemeColor;
pres.defineSlideMaster({
  title: "TITLE_ONLY", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.52, y: 0.28, w: 12.3, h: 0.75, fontSize: 36,
                                         bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } }],
});
const s = pres.addSlide({ masterName: "TITLE_ONLY" });
s.addText("GRPO: Learning From Groups of Samples", { placeholder: "title" });
const txt = (t, o) => s.addText(t, { margin: 0, isTextBox: true, color: C.text1, valign: "middle", ...o });
const img = (file, box, name) => {
  const [pw, ph] = pxSize(file), k = Math.min(box.w / pw, box.h / ph);
  s.addImage({ path: file, x: box.x + (box.w - pw * k) / 2, y: box.y + (box.h - ph * k) / 2, w: pw * k, h: ph * k, objectName: name });
};

// legend line under the title
txt([{ text: "8 programs sampled per drawing · reward ", options: { color: C.accent3 } },
     { text: "r = IoU vs ground truth", options: { bold: true, color: C.text2 } },
     { text: " (0 if it fails) · advantage ", options: { color: C.accent3 } },
     { text: "A = r − group mean", options: { bold: true, color: C.text2 } },
     { text: ":  ", options: { color: C.accent3 } },
     { text: "reinforced", options: { bold: true, color: C.text2 } }, { text: "  /  ", options: { color: C.accent3 } },
     { text: "discouraged", options: { bold: true, color: C.accent1 } }],
    { x: 0.52, y: 1.02, w: 12.3, h: 0.3, fontSize: 14, objectName: "legend" });

const X0 = 0.45, DW = 1.6, CX0 = X0 + DW + 0.2, CW = (13.333 - CX0 - 0.35) / 8, Y0 = 1.45, RH = 1.72;
GROUPS.forEach(([dir, pre, name], r) => {
  const base = path.join(FIG, dir), key = fs.readdirSync(base).find(k => k.startsWith(pre));
  const d = JSON.parse(fs.readFileSync(path.join(base, key, "data.json")));
  const rew = d.iou.map((v, j) => (d.exec[j] ? v : 0)), mean = rew.reduce((a, b) => a + b, 0) / rew.length;
  const y = Y0 + r * RH;
  if (r > 0) s.addShape(pres.shapes.LINE, { x: X0, y: y - 0.08, w: 13.333 - X0 - 0.35, h: 0, line: { color: C.accent6, width: 1 }, objectName: `row ${r + 1} divider` });
  // drawing + group mean
  s.addShape(pres.shapes.RECTANGLE, { x: X0, y: y + 0.02, w: DW, h: 1.12, fill: { color: C.background1 }, line: { color: C.accent6, width: 0.75 }, objectName: `row ${r + 1} drawing frame` });
  img(path.join(base, key, "drawing.png"), { x: X0 + 0.04, y: y + 0.05, w: DW - 0.08, h: 1.06 }, `row ${r + 1} drawing`);
  txt(name, { x: X0, y: y + 1.17, w: DW, h: 0.22, fontSize: 11, bold: true, color: C.text2, align: "center", objectName: `row ${r + 1} name` });
  txt(`group mean ${mean.toFixed(2)}`, { x: X0, y: y + 1.38, w: DW, h: 0.22, fontSize: 11, color: C.accent3, align: "center", objectName: `row ${r + 1} mean` });
  for (let j = 0; j < 8; j++) {
    const cx = CX0 + j * CW, A = rew[j] - mean, file = path.join(base, key, `c${j}.png`), ok = d.exec[j] && fs.existsSync(file);
    if (ok) img(file, { x: cx + 0.06, y: y, w: CW - 0.12, h: 1.05 }, `row ${r + 1} sample ${j + 1}`);
    else txt("no solid", { x: cx, y, w: CW, h: 1.05, fontSize: 11, color: C.accent2, align: "center", objectName: `row ${r + 1} sample ${j + 1}` });
    txt(`r ${rew[j].toFixed(2)}`, { x: cx, y: y + 1.08, w: CW, h: 0.22, fontSize: 12, bold: true, color: C.text2, align: "center", objectName: `row ${r + 1} reward ${j + 1}` });
    // advantage bar about a centre tick: half the cell width = |A| of 0.5
    const mid = cx + CW / 2, half = (CW - 0.2) / 2, bw = Math.max(0.02, Math.min(1, Math.abs(A) / 0.5) * half), col = A >= 0 ? C.text2 : C.accent1;
    s.addShape(pres.shapes.RECTANGLE, { x: A >= 0 ? mid : mid - bw, y: y + 1.34, w: bw, h: 0.11, fill: { color: col }, line: { color: col, width: 0 }, objectName: `row ${r + 1} advantage bar ${j + 1}` });
    s.addShape(pres.shapes.LINE, { x: mid, y: y + 1.31, w: 0, h: 0.17, line: { color: C.accent2, width: 0.75 }, objectName: `row ${r + 1} advantage axis ${j + 1}` });
    txt(`A ${A >= 0 ? "+" : "−"}${Math.abs(A).toFixed(2)}`, { x: cx, y: y + 1.47, w: CW, h: 0.2, fontSize: 10.5, color: col, align: "center", objectName: `row ${r + 1} advantage ${j + 1}` });
  }
});
txt("Samples from the fine-tuned starting model (before GRPO). Each update raises the probability of programs with A > 0 and " +
    "lowers it for A < 0, so the model learns from relative quality even when no sample is exactly right (handwheel).",
    { x: X0, y: Y0 + 3 * RH - 0.02, w: 13.333 - X0 - 0.35, h: 0.45, fontSize: 12, color: C.accent3, valign: "top", objectName: "footnote" });
s.addNotes("Groups = e55's 8 samples (draw 0 greedy + 7 at T 0.7) for synthetic parts 40a1be28 and 27b61d00 and real bench part " +
  "F_73525 (CADBench Fusion 360). GRPO training itself samples at T 1.0 from the current policy; these rows illustrate the reward " +
  "and advantage computation at step 0. Advantage here is r minus the group mean; the training recipe additionally divides by the " +
  "batch standard deviation (batch-std advantages) and applies token-level PPO clipping (0.2/0.28), no KL term.");

(async () => {
  const out = path.join(__dirname, "grpo_groups.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
