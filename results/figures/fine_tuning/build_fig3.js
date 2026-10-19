// Figure 3 (Fine Tuning), editable: the user's two-box layout (1. Supervised FT -> 2. GRPO RL) filled with the
// training recipe, the GRPO loop + expert iteration as shapes, key numbers as text, and the house-style progression
// chart (finetune_progress.svg from train_v14/geom/plot_finetune_fig.py). Numbers: GRPO_HANDOFF.md / results/bench_b.
//   NODE_PATH=<dir with pptxgenjs> PPTX_SKILL=<pptx skill dir> node build_fig3.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const HERE = __dirname;
const THEME = {
  name: "Drawing to CAD", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: "13294B", lt2: "F2F2F2", accent1: "2F6FD6", accent2: "8A8F99",
            accent3: "5A5F69", accent4: "E84A27", accent5: "E8EDF5", accent6: "4D4D4D", hlink: "2F6FD6", folHlink: "5A5F69" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Figure 3: Fine Tuning";
const C = pres.SchemeColor;
pres.defineSlideMaster({
  title: "TITLE_ONLY", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.52, y: 0.3, w: 12.3, h: 0.7, fontSize: 32,
                                         bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } }],
});
const s = pres.addSlide({ masterName: "TITLE_ONLY" });
s.addText("Figure 3: Fine Tuning", { placeholder: "title" });

const txt = (t, o) => s.addText(t, { margin: 0, isTextBox: true, color: C.text1, fontSize: 12, valign: "top", ...o });
const frame = (x, y, w, h, name) => s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: C.background1 },
                                                                        line: { color: C.text1, width: 1.5 }, objectName: name });
const arrow = (x1, y1, x2, y2, name) => s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2),
  w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1,
  line: { color: C.text1, width: 2, endArrowType: "triangle" }, objectName: name });

// frames and connector, as in the template
const Y = 1.58, H = 4.33, B1 = { x: 1.83, w: 2.64 }, B2 = { x: 5.0, w: 6.72 };
frame(B1.x, Y, B1.w, H, "box 1 frame"); frame(B2.x, Y, B2.w, H, "box 2 frame");
arrow(B1.x + B1.w, Y + H / 2, B2.x, Y + H / 2, "stage arrow");
txt("1. Supervised FT", { x: B1.x, y: Y + 0.14, w: B1.w, h: 0.35, fontSize: 16, bold: true, color: C.text2, align: "center", objectName: "box 1 header" });
txt("2. GRPO Reinforcement Learning", { x: B2.x, y: Y + 0.14, w: B2.w, h: 0.35, fontSize: 16, bold: true, color: C.text2, align: "center", objectName: "box 2 header" });

// ---- box 1: supervised fine-tuning
const b1 = [
  "Qwen3.8-27B vision-language model, full fine-tune",
  "Drawing sheet → build123d program pairs (Zero-to-CAD-derived corpus)",
  "Mix: own correct programs (IoU\u00a0≥\u00a00.8) 60%, reasoning traces 20%, ground truth 20%",
];
txt(b1.map((t, i) => ({ text: t, options: { bullet: { indent: 12 }, breakLine: i < b1.length - 1 } })),
    { x: B1.x + 0.14, y: Y + 0.62, w: B1.w - 0.28, h: 2.0, fontSize: 12, paraSpaceAfter: 6, objectName: "box 1 recipe" });
const stat = (x, y, w, big, small, name) => {
  txt(big, { x, y, w, h: 0.42, fontSize: 22, bold: true, color: C.text2, align: "center", objectName: `${name} value` });
  txt(small, { x, y: y + 0.42, w, h: 0.3, fontSize: 11, color: C.accent3, align: "center", objectName: `${name} label` });
};
stat(B1.x + 0.1, Y + 2.72, B1.w - 0.2, "6% → 80%", "programs that run", "sft exec");
stat(B1.x + 0.1, Y + 3.5, B1.w - 0.2, "0.08 → 0.51", "real-part IoU (vote), base → SFT", "sft iou");

// ---- box 2, left: GRPO loop (2 x 2 cycle) + expert iteration
const LX = B2.x + 0.18, LW = 1.3, LH = 0.66, GX = 0.26, GY = 0.28, LY = Y + 0.62;
const cells = [["Sample 8 programs per drawing", LX, LY], ["Run each; reward = IoU vs ground truth", LX + LW + GX, LY],
               ["Compare to the group average", LX + LW + GX, LY + LH + GY], ["Update LoRA weights", LX, LY + LH + GY]];
cells.forEach(([t, x, y], i) => s.addText(t, { x, y, w: LW, h: LH, shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.08,
  fill: { color: C.accent5 }, line: { color: C.text2, width: 1 }, fontSize: 11, color: C.text2, bold: true, align: "center",
  valign: "middle", margin: 3, objectName: `loop step ${i + 1}` }));
arrow(LX + LW, LY + LH / 2, LX + LW + GX, LY + LH / 2, "loop arrow 1");
arrow(LX + LW + GX + LW / 2, LY + LH, LX + LW + GX + LW / 2, LY + LH + GY, "loop arrow 2");
arrow(LX + LW + GX, LY + LH + GY + LH / 2, LX + LW, LY + LH + GY + LH / 2, "loop arrow 3");
arrow(LX + LW / 2, LY + LH + GY, LX + LW / 2, LY + LH, "loop arrow 4");
txt("Hard real training parts (CADBench, DeepCAD); LoRA on the SFT model",
    { x: LX, y: LY + 2 * LH + GY + 0.08, w: 2 * LW + GX, h: 0.42, fontSize: 10, color: C.accent3, align: "center", objectName: "loop caption" });
const EY = LY + 2 * LH + GY + 0.62;
txt("Expert iteration, 2 rounds", { x: LX, y: EY, w: 2 * LW + GX, h: 0.28, fontSize: 12, bold: true, color: C.text2, objectName: "expert iteration header" });
const ei = [
  "Search 8,121 hard training parts: 16 samples + ground-truth-guided repair",
  "Keep the best programs: 5,502 at IoU\u00a0≥\u00a00.75",
  "SFT on them, then short GRPO",
];
txt(ei.map((t, i) => ({ text: t, options: { bullet: { type: "number" }, breakLine: i < ei.length - 1 } })),
    { x: LX, y: EY + 0.32, w: 2 * LW + GX, h: 1.0, fontSize: 11, paraSpaceAfter: 3, objectName: "expert iteration steps" });

// ---- box 2, right: progression chart + key numbers
const CW = 3.3, CX = B2.x + B2.w - CW - 0.15, CY = Y + 0.55;
s.addImage({ path: path.join(HERE, "finetune_progress.svg"), x: CX, y: CY, w: CW, h: CW * 1388 / 1395, objectName: "progress chart",
             altText: "Mean IoU on 280 held-out real parts after each training stage" });
txt([{ text: "Held-out bench B, 280 real parts", options: { breakLine: true } },
     { text: "Full system with repair: 0.66\u00a0→\u00a00.72", options: { bold: true, color: C.text2 } }],
    { x: CX - 0.05, y: CY + CW * 1388 / 1395 + 0.02, w: CW + 0.1, h: 0.4, fontSize: 10, color: C.accent3, align: "center", objectName: "chart caption" });

s.addNotes(
  "Box 1: e55 = Qwen3.8-27B full fine-tune (FSDP2, lr 6e-6, seq 5120, batch 64), vision tower frozen; STaR/RFT rounds keep own " +
  "generations at IoU >= 0.8. Base Qwen3.8-27B with no fine-tune: 6.1% of programs execute, vote 0.082 on bench B (hallucinated " +
  "build123d API); e55: 79.9% execute, vote 0.509.\n" +
  "Box 2: GRPO on e55 + LoRA r64, G = 8 rollouts per part (vLLM), reward = exact IoU vs ground truth (0 if the program fails), " +
  "group-normalised advantages, lr 1e-5 to 2e-5, T 1.0, trained on the raw sampled text (fixes a format blind spot behind the late " +
  "collapses). Expert iteration: RL policy samples 16 programs on 8,121 hard training parts + ground-truth-selected rp3 / DeepSeek " +
  "repair search -> tier of 5,502 programs >= 0.75 IoU -> LoRA SFT -> short GRPO (rft2_rl step 60).\n" +
  "Chart, bench B (280 parts, frozen before any model saw it, never used to pick checkpoints): SFT e55 / GRPO ent_t10 s120 / round 1 " +
  "rft1_rl2 s120 / round 2 rft2_rl s60. Vote 0.509 / 0.640 / 0.651 / 0.665; best of 8 0.595 / 0.696 / 0.708 / 0.732; single draw " +
  "0.402 / 0.625 / 0.628 / 0.625. Round 2 vs round 1: vote +0.014 [+0.003, +0.025], best of 8 +0.023 [+0.014, +0.032]. " +
  "The GRPO point is the best of 3 seeds (seed mean on the 144 bench: vote 0.614 vs 0.639). Full system with rp3 multi-start repair: " +
  "e55 0.664 -> round 2 0.721, +0.057 [+0.036, +0.078]. Gains plateau around vote 0.65-0.68 across all recipes.");

(async () => {
  const out = path.join(HERE, "figure3_fine_tuning.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
