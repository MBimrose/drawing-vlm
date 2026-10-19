// Figure 3 (Fine Tuning), simplified three-stage version (expert iteration folded into GRPO), in the style of
// Figures 1-2: three numbered stage boxes joined by thick arrows, tinted cards
// with line icons and small down-arrows, and a bordered stat box per stage. Every element is a native, editable object.
// Stage IoU = medoid vote on held-out bench B (280 real parts); stage 2 = GRPO incl. 2 self-improvement (expert
// iteration) rounds = rft2_rl s60; stage 3 = that generator + 3 rp3 repair chains.
// Numbers: results/bench_b/tables.md and GRPO_HANDOFF.md "Final results (Oct 12)".
//   NODE_PATH=<dir with pptxgenjs, react, react-dom, react-icons, sharp> PPTX_SKILL=<pptx skill dir> node build_fig3_pipeline.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const lu = require("react-icons/lu");
const sharp = require("sharp");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const HERE = __dirname;
const NAVY = "13294B";
const THEME = {
  name: "Drawing to CAD", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: NAVY, lt2: "EEF2F8", accent1: "2F6FD6", accent2: "8A8F99",
            accent3: "5A5F69", accent4: "D3DEE0", accent5: "EEF4F0", accent6: "D6DEEA", hlink: "2F6FD6", folHlink: "5A5F69" },
};

async function icon(name) {
  const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(lu[name], { size: 256, color: "#" + NAVY }));
  return "image/png;base64," + (await sharp(Buffer.from(svg)).png().toBuffer()).toString("base64");
}

const STAGES = [
  { title: "1. Supervised FT", tint: "background2", border: "accent6", stat: "IoU 0.509", cards: [
    ["LuDatabase", "Drawing → Code", "~500k training pairs"],
    ["LuBrainCircuit", "Qwen 3.8-27B", "full fine-tune"],
    ["LuRefreshCw", "Self-Training", "keep own IoU ≥\u00a00.8"]] },
  { title: "2. GRPO", tint: "background2", border: "accent6", stat: "IoU 0.665", cards: [
    ["LuLayers", "Sample 8 Programs", "per drawing"],
    ["LuTarget", "Reward", "IoU vs ground truth"],
    ["LuSlidersHorizontal", "Update LoRA", "+ 2 self-improvement rounds"]] },
  { title: "3. Repairer", tint: "accent5", border: "accent4", stat: "IoU 0.721", cards: [
    ["LuImages", "Two Drawings In", "target + candidate render"],
    ["LuWrench", "Corrected Program", "real-part repair pairs"],
    ["LuCpu", "Full Fine-Tune", "from the SFT model"]] },
];

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "Figure 3: Fine Tuning";
  const C = pres.SchemeColor;
  pres.defineSlideMaster({
    title: "TITLE_ONLY", background: { color: "FFFFFF" },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.3, w: 12.1, h: 0.75, fontSize: 36,
                                           bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } }],
  });
  const s = pres.addSlide({ masterName: "TITLE_ONLY" });
  s.addText("Figure 3: Fine Tuning", { placeholder: "title" });

  const W = 3.3, GAP = 0.7, X0 = (13.333 - 3 * 3.3 - 2 * 0.7) / 2, Y = 1.35, H = 3.75;
  const CARD_H = 0.66, CARD_Y0 = 0.65, CARD_STEP = 0.86, STAT_Y = 3.17, STAT_H = 0.44;
  const line = (x1, y1, x2, y2, width, name) => s.addShape(pres.shapes.LINE, { x: x1, y: y1, w: x2 - x1, h: y2 - y1,
    line: { color: C.text1, width, endArrowType: "triangle" }, objectName: name });

  for (let i = 0; i < STAGES.length; i++) {
    const st = STAGES[i], x = X0 + i * (W + GAP);
    s.addShape(pres.shapes.RECTANGLE, { x, y: Y, w: W, h: H, fill: { color: C.background1 }, line: { color: C.text1, width: 1.75 },
                                        objectName: `stage ${i + 1} frame` });
    s.addText(st.title, { x, y: Y + 0.12, w: W, h: 0.45, fontSize: 20, bold: true, color: C.text2, align: "center", valign: "middle",
                          margin: 0, isTextBox: true, objectName: `stage ${i + 1} title` });
    for (let j = 0; j < st.cards.length; j++) {
      const [ic, head, sub] = st.cards[j], cy = Y + CARD_Y0 + j * CARD_STEP, cx = x + 0.15, cw = W - 0.3;
      s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w: cw, h: CARD_H, fill: { color: C[st.tint] },
                                          line: { color: C[st.border], width: 0.75 }, objectName: `stage ${i + 1} card ${j + 1}` });
      s.addImage({ data: await icon(ic), x: cx + 0.12, y: cy + (CARD_H - 0.3) / 2, w: 0.3, h: 0.3, objectName: `stage ${i + 1} icon ${j + 1}` });
      s.addText([{ text: head, options: { bold: true, fontSize: 12.5, color: C.text2, breakLine: true } },
                 { text: sub, options: { fontSize: 11, color: C.accent3 } }],
                { x: cx + 0.52, y: cy, w: cw - 0.6, h: CARD_H, align: "center", valign: "middle", margin: 0, isTextBox: true,
                  objectName: `stage ${i + 1} card ${j + 1} text` });
      if (j < st.cards.length - 1)
        line(x + W / 2, cy + CARD_H, x + W / 2, cy + CARD_STEP, 1.25, `stage ${i + 1} arrow ${j + 1}`);
    }
    s.addShape(pres.shapes.RECTANGLE, { x: x + 0.15, y: Y + STAT_Y, w: W - 0.3, h: STAT_H, fill: { color: C.background1 },
                                        line: { color: C.text2, width: 1.75 }, objectName: `stage ${i + 1} stat frame` });
    s.addText(st.stat, { x: x + 0.15, y: Y + STAT_Y, w: W - 0.3, h: STAT_H, fontSize: 20, bold: true, color: C.text2, align: "center",
                         valign: "middle", margin: 0, isTextBox: true, objectName: `stage ${i + 1} stat` });
    if (i < STAGES.length - 1) line(x + W, Y + H / 2, x + W + GAP, Y + H / 2, 3, `stage arrow ${i + 1}`);
  }
  s.addText("IoU: mean volumetric IoU of the selected candidate (medoid of 8) on 280 held-out real parts. Self-improvement: " +
            "search hard training parts, fine-tune on the best programs found, short GRPO. Stage 3: full system, the " +
            "stage-2 generator plus three repair chains.",
            { x: X0, y: Y + H + 0.18, w: 3 * W + 2 * GAP, h: 0.7, fontSize: 12, color: C.accent3, margin: 0, isTextBox: true,
              objectName: "footnote" });
  s.addNotes(
    "Bench B: 280 real parts (171 Fusion 360 + 109 ABC), frozen before any model saw it, never used to pick checkpoints. " +
    "Vote (medoid of 8): base Qwen3.8-27B 0.082 (6% of programs run), SFT e55 0.509, GRPO with 2 self-improvement rounds " +
    "(rft2_rl s60) 0.665 (best of 8: 0.595 -> 0.732). Plain GRPO without them (ent_t10 s120, best of 3 seeds) 0.640; the " +
    "self-improvement rounds add +0.024 [+0.008, +0.041]. Each round: the current policy samples 16 programs on hard " +
    "training parts, rp3 repair search + DeepSeek-V4.1-Flash teacher improve them using ground truth, the best (IoU >= 0.75) " +
    "are fine-tuned into the LoRA, then short GRPO; round 2 kept 5,502 programs on 8,121 parts. " +
    "Stage 4: rft2_rl s60, K=16, verifier + render-compare selection, 3 rp3 repair chains (16 repairs x 6 rounds, render-compare " +
    "gate, margin 0.1), multi-start pick = 0.721; the same repair on e55 gives 0.664 (+0.057 [+0.036, +0.078]). " +
    "rp3 = full fine-tune continued from e55 (300 steps, lr 2e-6) on repair pairs (target drawing + candidate's rendered drawing " +
    "+ code -> better program), incl. real-part repairs from a DeepSeek search.");

  const out = path.join(HERE, "figure3_fine_tuning_3stage.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
