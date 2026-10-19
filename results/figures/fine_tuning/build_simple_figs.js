// Simplified Figure 3 (Fine Tuning) and Figure 4 (Repair Loop) in the exact pattern of Figure 2: numbered stage box,
// one tinted card (bold title + two short lines), one visual, one big bordered number; thick arrows between boxes.
// Assets: prep_simple_assets.py. Numbers: bench B (results/bench_b/tables.md) and the 143-part repair run (PAPER_STATUS.md).
//   NODE_PATH=<pptxgenjs> PPTX_SKILL=<pptx skill dir> node build_simple_figs.js
const path = require("path");
const fs = require("fs");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const HERE = __dirname, A = path.join(HERE, "simple_assets");
const THEME = {
  name: "Drawing to CAD", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: "13294B", lt2: "EEF2F8", accent1: "E84A27", accent2: "8A8F99",
            accent3: "5A5F69", accent4: "D3DEE0", accent5: "EEF4F0", accent6: "D6DEEA", hlink: "2F6FD6", folHlink: "5A5F69" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Fine tuning and repair loop";
const C = pres.SchemeColor;
pres.defineSlideMaster({
  title: "TITLE_ONLY", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.52, y: 0.28, w: 12.3, h: 0.75, fontSize: 36,
                                         bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } }],
});

const Y = 1.26, H = 3.51;                    // Figure 2's box band
const txt = (s, t, o) => s.addText(t, { margin: 0, isTextBox: true, color: C.text1, valign: "middle", ...o });
const pxSize = f => { const b = fs.readFileSync(f); return [b.readUInt32BE(16), b.readUInt32BE(20)]; };   // PNG IHDR
const img = (s, file, box, name) => {
  const [pw, ph] = pxSize(path.join(A, file)), k = Math.min(box.w / pw, box.h / ph);
  s.addImage({ path: path.join(A, file), x: box.x + (box.w - pw * k) / 2, y: box.y + (box.h - ph * k) / 2, w: pw * k, h: ph * k, objectName: name });
};
const arrow = (s, x1, x2, y, name) => s.addShape(pres.shapes.LINE, { x: x1, y, w: x2 - x1, h: 0,
  line: { color: C.text1, width: 3, endArrowType: "triangle" }, objectName: name });

// one Figure-2-style stage; returns the visual area for the caller to fill
function stage(s, x, w, n, title, card, stat, green) {
  s.addShape(pres.shapes.RECTANGLE, { x, y: Y, w, h: H, fill: { color: C.background1 }, line: { color: C.text1, width: 1.75 }, objectName: `${n} frame` });
  txt(s, `${n}. ${title}`, { x, y: Y + 0.1, w, h: 0.42, fontSize: 20, bold: true, color: C.text2, align: "center", objectName: `${n} title` });
  s.addShape(pres.shapes.RECTANGLE, { x: x + 0.15, y: Y + 0.48, w: w - 0.3, h: 0.74, fill: { color: green ? C.accent5 : C.background2 },
                                      line: { color: green ? C.accent4 : C.accent6, width: 0.75 }, objectName: `${n} card` });
  txt(s, [{ text: card[0], options: { bold: true, fontSize: 14, color: C.text2, breakLine: true } },
          { text: card[1], options: { fontSize: 13, color: C.accent3, breakLine: true } },
          { text: card[2], options: { fontSize: 13, color: C.accent3 } }],
      { x: x + 0.15, y: Y + 0.48, w: w - 0.3, h: 0.74, align: "center", objectName: `${n} card text` });
  s.addShape(pres.shapes.RECTANGLE, { x: x + 0.15, y: Y + H - 0.56, w: w - 0.3, h: 0.44, fill: { color: C.background1 },
                                      line: { color: C.text2, width: 1.75 }, objectName: `${n} stat frame` });
  txt(s, stat, { x: x + 0.15, y: Y + H - 0.56, w: w - 0.3, h: 0.44, fontSize: 20, bold: true, color: C.text2, align: "center", objectName: `${n} stat` });
  return { x: x + 0.15, y: Y + 1.32, w: w - 0.3, h: H - 1.32 - 0.66 };
}

// ===================================== Figure 3: Fine Tuning =======================================================
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" });
  s.addText("Figure 3: Fine Tuning", { placeholder: "title" });
  const W = 3.3, GAP = 0.62, X0 = (13.333 - 3 * W - 2 * GAP) / 2, xs = [0, 1, 2].map(i => X0 + i * (W + GAP));

  // 1. base model: hallucinated API
  let v = stage(s, xs[0], W, 1, "Base Model", ["Qwen3.8-27B", "no fine-tuning", "invents CAD API calls"], "IoU 0.08");
  s.addShape(pres.shapes.RECTANGLE, { ...v, fill: { color: C.background1 }, line: { color: C.accent6, width: 0.75 }, objectName: "1 code frame" });
  txt(s, [{ text: "part = Box(80, 50, 10,", options: { breakLine: true } },
          { text: "          centered=True)", options: { breakLine: true } },
          { text: "part -= Cylinder(pos=(0, 0, 5),", options: { breakLine: true } },
          { text: "                 r=10)", options: { breakLine: true } },
          { text: "TypeError: unexpected", options: { bold: true, color: C.accent1, breakLine: true } },
          { text: "keyword 'centered'", options: { bold: true, color: C.accent1, breakLine: true } },
          { text: "only 6% of programs run", options: { fontFace: "Arial", italic: true, color: C.accent3 } }],
      { x: v.x + 0.12, y: v.y, w: v.w - 0.2, h: v.h, fontSize: 11, fontFace: "Courier New", color: C.text2, objectName: "1 code" });

  // 2. supervised fine-tuning: data mix
  v = stage(s, xs[1], W, 2, "Supervised FT", ["Full Fine-Tune", "~500k drawing → code pairs", "+ self-training rounds"], "IoU 0.51");
  const mix = [["Own correct programs", 0.6, C.text2], ["Reasoning traces", 0.2, C.accent2], ["Ground-truth code", 0.2, C.accent2]];
  mix.forEach(([label, f, col], i) => {
    const ry = v.y + 0.05 + i * 0.52;
    txt(s, [{ text: label, options: {} }, { text: `  ${Math.round(f * 100)}%`, options: { bold: true, color: C.text2 } }],
        { x: v.x, y: ry, w: v.w, h: 0.26, fontSize: 12, color: C.accent3, align: "left", objectName: `2 mix label ${i + 1}` });
    s.addShape(pres.shapes.RECTANGLE, { x: v.x, y: ry + 0.28, w: v.w * f, h: 0.16, fill: { color: col }, line: { color: col, width: 0 },
                                        objectName: `2 mix bar ${i + 1}` });
  });

  // 3. GRPO: 8 candidates with their rewards
  v = stage(s, xs[2], W, 3, "GRPO", ["Reinforcement Learning", "8 programs per drawing", "reward = IoU vs ground truth"], "IoU 0.67");
  const G = JSON.parse(fs.readFileSync(path.join(A, "grpo_cands.json"))), cw = v.w / 4;
  G.cands.forEach((c, i) => {
    const cx = v.x + (i % 4) * cw, cy = v.y + Math.floor(i / 4) * 0.8, good = c.ok && c.iou >= G.mean;
    if (c.ok) img(s, `grpo_c${c.j}.png`, { x: cx + 0.06, y: cy, w: cw - 0.12, h: 0.52 }, `3 candidate ${i + 1}`);
    else txt(s, "no solid", { x: cx, y: cy, w: cw, h: 0.52, fontSize: 10, color: C.accent2, align: "center", objectName: `3 candidate ${i + 1}` });
    txt(s, c.ok ? c.iou.toFixed(2) : "0", { x: cx, y: cy + 0.53, w: cw, h: 0.22, fontSize: 12, bold: good, align: "center",
                                            color: good ? C.text2 : C.accent2, objectName: `3 reward ${i + 1}` });
  });

  txt(s, "IoU: mean volumetric IoU of the selected program on 280 held-out real parts. GRPO includes two self-improvement " +
         "rounds on hard training parts. Rewards shown for one synthetic part; bold = above the group average, which gets reinforced.",
      { x: xs[0], y: Y + H + 0.15, w: 3 * W + 2 * GAP, h: 0.5, fontSize: 12, color: C.accent3, valign: "top", objectName: "footnote" });
  for (let i = 0; i < 2; i++) arrow(s, xs[i] + W, xs[i + 1], Y + 2.15, `stage arrow ${i + 1}`);
  s.addNotes("Bench B (280 real parts, never used for selection), medoid of 8. Base Qwen3.8-27B: vote 0.082, 6.1% of programs " +
    "execute (hallucinated build123d API, e.g. Box(centered=...), Cylinder(pos=...)). SFT e55: full fine-tune on ~500k drawing-code " +
    "pairs, mix 60% own correct programs (IoU >= 0.8) / 20% Kimi-K3 reasoning traces / 20% ground truth; vote 0.509. GRPO: LoRA on " +
    "e55, 8 rollouts per drawing, reward = IoU (0 if the program fails), advantage = reward - group mean; plus two self-improvement " +
    "rounds (search hard training parts, fine-tune on the best programs, short GRPO): rft2_rl s60, vote 0.665. Example rewards: " +
    "synthetic part 1fbfa3c8, e55 candidates (group mean 0.81).");
}

// ===================================== Figure 4: Repair Loop =======================================================
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" });
  s.addText("Figure 4: Repair Loop", { placeholder: "title" });
  const W = 2.65, xs = [0.56, 3.72, 6.89, 10.06];

  let v = stage(s, xs[0], W, 1, "Candidate", ["Generator Pick", "best of 8 candidates", "run to a 3D solid"], "IoU 0.52");
  img(s, "hw_start.png", v, "1 start render");

  v = stage(s, xs[1], W, 2, "Repair", ["Repairer Model", "sees target + its drawing", "writes 16 fixes"], "16 Repairs", true);
  const hw = (v.w - 0.1) / 2;   // iso views of the two drawings, side by side
  img(s, "hw_target_drawing.png", { x: v.x, y: v.y, w: hw, h: v.h - 0.26 }, "2 target drawing");
  img(s, "hw_candidate_drawing.png", { x: v.x + hw + 0.1, y: v.y, w: hw, h: v.h - 0.26 }, "2 candidate drawing");
  txt(s, "target", { x: v.x, y: v.y + v.h - 0.24, w: hw, h: 0.22, fontSize: 11, bold: true, color: C.text2, align: "center", objectName: "2 target label" });
  txt(s, "candidate", { x: v.x + hw + 0.1, y: v.y + v.h - 0.24, w: hw, h: 0.22, fontSize: 11, bold: true, color: C.accent1, align: "center", objectName: "2 candidate label" });

  v = stage(s, xs[2], W, 3, "Score", ["Render-Compare", "redraw every fix", "match the input drawing"], "No Labels", true);
  img(s, "hw_overlay.png", { x: v.x, y: v.y, w: v.w, h: v.h - 0.24 }, "3 overlay");
  txt(s, [{ text: "target", options: { bold: true, color: C.text2 } }, { text: "  vs  ", options: { color: C.accent3 } },
          { text: "candidate", options: { bold: true, color: C.accent1 } }],
      { x: v.x, y: v.y + v.h - 0.22, w: v.w, h: 0.22, fontSize: 11, align: "center", objectName: "3 overlay legend" });

  v = stage(s, xs[3], W, 4, "Accept", ["Keep If Better", "repeat up to 6 rounds", "best of 3 chains"], "IoU 0.93", true);
  img(s, "hw_final.png", v, "4 final render");

  for (let i = 0; i < 3; i++) arrow(s, xs[i] + W, xs[i + 1], Y + 2.15, `stage arrow ${i + 1}`);
  txt(s, "Example: handwheel (real part). Over 143 real parts, the loop raises mean IoU from 0.537 to 0.695. " +
         "Ground truth is never used; IoU is shown for illustration.",
      { x: xs[0], y: Y + H + 0.15, w: xs[3] + W - xs[0], h: 0.5, fontSize: 12, color: C.accent3, valign: "top", objectName: "footnote" });
  s.addNotes("Handwheel = CADBench Fusion 360 part F_73525. Start = e55 candidate 7 (third distinct start of the served chain), IoU 0.52. " +
    "Repairer rp3 (full fine-tune of e55) sees the target drawing, the candidate's drawing (same draftwright compiler) and the code, " +
    "samples 16 repairs per round (T 0.7). Each repair is executed, redrawn and scored by render-compare (v3, per-view match, " +
    "geometry separated from blue annotations; r = 0.67 with true IoU). The best is accepted only if the score improves by 0.1; up to " +
    "6 rounds; 3 chains from the top-3 starts, final = best score. This chain: 0.52 -> 0.35 (round 1) -> 0.93 (round 3). " +
    "Real bench: e55 medoid 0.537 -> one chain 0.667 -> 3 chains 0.695 (e55 best of 8: 0.591). Overlay: front views of the " +
    "target (navy) and of the start candidate's drawing (orange where it differs).");
}

(async () => {
  const out = path.join(HERE, "figures_3_4_simple.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
