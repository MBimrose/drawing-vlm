// Two slides in the Figures 1-2 style (numbered stage boxes, tinted icon cards, thick arrows, bordered stat boxes):
//   Figure 3: Fine Tuning (technical) - SFT -> GRPO (+2 self-improvement rounds) -> Repairer, with data, objective and
//             hyper-parameters on each card; IoU = medoid vote on held-out bench B (280 real parts).
//   Figure 4: Repair Loop - candidate -> repair -> score -> accept, loop-back arrow, handwheel example strip.
// Sources: PAPER_STATUS.md (SFT recipe), GRPO_HANDOFF.md (GRPO recipe, bench B), train_v14/configs/rp3-delta-e55.yaml,
// results/figures/results_deck/repair_ex (example renders).
//   NODE_PATH=<pptxgenjs, react, react-dom, react-icons, sharp> PPTX_SKILL=<pptx skill dir> node build_fig3tech_fig4.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const lu = require("react-icons/lu");
const sharp = require("sharp");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const HERE = __dirname;
const EX = path.join(HERE, "..", "results_deck", "repair_ex");
const NAVY = "13294B";
const THEME = {
  name: "Drawing to CAD", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: NAVY, lt2: "EEF2F8", accent1: "2F6FD6", accent2: "8A8F99",
            accent3: "5A5F69", accent4: "D3DEE0", accent5: "EEF4F0", accent6: "D6DEEA", hlink: "2F6FD6", folHlink: "5A5F69" },
};
const BLUE = { tint: "background2", border: "accent6" }, GREEN = { tint: "accent5", border: "accent4" };

const iconCache = {};
async function icon(name) {
  if (!iconCache[name]) {
    const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(lu[name], { size: 256, color: "#" + NAVY }));
    iconCache[name] = "image/png;base64," + (await sharp(Buffer.from(svg)).png().toBuffer()).toString("base64");
  }
  return iconCache[name];
}

(async () => {
  const pres = new pptxgen();
  pres.layout = "LAYOUT_WIDE";
  pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
  pres.title = "Fine tuning and repair loop";
  const C = pres.SchemeColor;
  pres.defineSlideMaster({
    title: "TITLE_ONLY", background: { color: "FFFFFF" },
    objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.6, y: 0.3, w: 12.1, h: 0.75, fontSize: 36,
                                           bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } }],
  });

  // ---- shared drawing helpers -------------------------------------------------------------------------------------
  const arrowLine = (s, x1, y1, x2, y2, width, name, head = true) => s.addShape(pres.shapes.LINE, {
    x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1), flipH: x2 < x1, flipV: y2 < y1,
    line: { color: C.text1, width, ...(head ? { endArrowType: "triangle" } : {}) }, objectName: name });
  const txt = (s, t, o) => s.addText(t, { margin: 0, isTextBox: true, color: C.text1, valign: "middle", ...o });

  async function stage(s, x, y, w, h, title, cards, opt) {
    const { cardH, cardY0, cardStep, align = "center", headSize = 12.5, subSize = 11, stat } = opt;
    s.addShape(pres.shapes.RECTANGLE, { x, y, w, h, fill: { color: C.background1 }, line: { color: C.text1, width: 1.75 },
                                        objectName: `${title} frame` });
    txt(s, title, { x, y: y + 0.1, w, h: 0.45, fontSize: 20, bold: true, color: C.text2, align: "center", objectName: `${title} title` });
    for (let j = 0; j < cards.length; j++) {
      const [ic, head, sub, col] = cards[j], cy = y + cardY0 + j * cardStep, cx = x + 0.15, cw = w - 0.3;
      s.addShape(pres.shapes.RECTANGLE, { x: cx, y: cy, w: cw, h: cardH, fill: { color: C[col.tint] },
                                          line: { color: C[col.border], width: 0.75 }, objectName: `${title} card ${j + 1}` });
      s.addImage({ data: await icon(ic), x: cx + 0.11, y: cy + (cardH - 0.3) / 2, w: 0.3, h: 0.3, objectName: `${title} icon ${j + 1}` });
      txt(s, [{ text: head, options: { bold: true, fontSize: headSize, color: C.text2, breakLine: true } },
              { text: sub, options: { fontSize: subSize, color: C.accent3 } }],
          { x: cx + 0.52, y: cy, w: cw - 0.62, h: cardH, align, objectName: `${title} card ${j + 1} text` });
      if (j < cards.length - 1) arrowLine(s, x + w / 2, cy + cardH, x + w / 2, cy + cardStep, 1.25, `${title} arrow ${j + 1}`);
    }
    if (stat) {
      const sy = y + cardY0 + (cards.length - 1) * cardStep + cardH + 0.13;
      s.addShape(pres.shapes.RECTANGLE, { x: x + 0.15, y: sy, w: w - 0.3, h: 0.44, fill: { color: C.background1 },
                                          line: { color: C.text2, width: 1.75 }, objectName: `${title} stat frame` });
      txt(s, stat, { x: x + 0.15, y: sy, w: w - 0.3, h: 0.44, fontSize: 20, bold: true, color: C.text2, align: "center",
                     objectName: `${title} stat` });
    }
  }

  // ================================ Figure 3: Fine Tuning (technical) ================================================
  {
    const s = pres.addSlide({ masterName: "TITLE_ONLY" });
    s.addText("Figure 3: Fine Tuning", { placeholder: "title" });
    const W = 3.75, GAP = 0.45, X0 = (13.333 - 3 * W - 2 * GAP) / 2, Y = 1.25;
    const opt = { cardH: 0.82, cardY0: 0.62, cardStep: 0.97, align: "left", headSize: 12, subSize: 10.5 };
    const H = opt.cardY0 + 3 * opt.cardStep + opt.cardH + 0.13 + 0.44 + 0.15;
    const ST = [
      ["1. Supervised FT", "IoU 0.509", [
        ["LuDatabase", "Data", "~500k drawing → build123d pairs (Zero-to-CAD), each program executed and IoU-checked", BLUE],
        ["LuLayers", "Mix", "60% own programs with IoU ≥ 0.8 · 20% Kimi-K3 reasoning traces (53k) · 20% ground-truth code", BLUE],
        ["LuRefreshCw", "Self-Training (RFT)", "each new model regenerates the 60% tier from its own correct samples", BLUE],
        ["LuBrainCircuit", "Qwen3.8-27B, Full FT", "FSDP2 bf16, vision tower frozen · lr 6e-6, batch 64, seq 5,120, 4k steps", BLUE]]],
      ["2. GRPO", "IoU 0.665", [
        ["LuShuffle", "Rollouts", "G = 8 programs per drawing, T = 1.0 (vLLM) · LoRA r = 64 on all linear layers", BLUE],
        ["LuTarget", "Reward", "r = IoU(exec(code), ground truth); r = 0 if the program fails", BLUE],
        ["LuSigma", "Objective", "A = r − group mean, batch-std scaled · token-level PPO clip 0.2/0.28 · KL 0 · lr 1–2e-5", BLUE],
        ["LuRepeat", "Self-Improvement ×2", "16 samples + guided repair on 8,121 hard parts → 5,502 programs (IoU ≥ 0.75) → LoRA SFT → 60 GRPO steps", BLUE]]],
      ["3. Repairer", "IoU 0.721", [
        ["LuImages", "Input", "target drawing + candidate's rendered drawing + candidate code", GREEN],
        ["LuWrench", "Output", "corrected build123d program", GREEN],
        ["LuGitCompareArrows", "Data", "repair pairs (worse → better program), incl. real-part repairs distilled from a DeepSeek-V4.1 search", GREEN],
        ["LuCpu", "Full FT from SFT Model", "300 steps · lr 2e-6, batch 64, seq 7,168", GREEN]]],
    ];
    for (let i = 0; i < ST.length; i++) {
      const x = X0 + i * (W + GAP);
      await stage(s, x, Y, W, H, ST[i][0], ST[i][2], { ...opt, stat: ST[i][1] });
      if (i < ST.length - 1) arrowLine(s, x + W, Y + H / 2, x + W + GAP, Y + H / 2, 3, `stage arrow ${i + 1}`);
    }
    txt(s, "IoU: mean volumetric IoU of the selected candidate (medoid of 8) on 280 held-out real parts; stage 3 = stage-2 " +
           "generator + three repair chains. Self-improvement: guided repair = rp3 and DeepSeek-V4.1 search scored against " +
           "ground truth on training parts only.",
        { x: X0, y: Y + H + 0.12, w: 3 * W + 2 * GAP, h: 0.5, fontSize: 11, color: C.accent3, valign: "top", objectName: "footnote" });
    s.addNotes(
      "SFT (e55): Qwen3.8-27B full fine-tune, FSDP2 FULL_SHARD, bf16 compute + fp32 master, vision tower frozen, seq 5,120, " +
      "effective batch 64, lr 6e-6, 4k steps. Mix 60/20/20: RFT rows (own generations kept at exact IoU >= 0.8 with think traces, " +
      "STaR rounds), certified Kimi-K3 reasoning traces (53k, +-5% reverse-reconstruction gate), plain filtered GT. Base model " +
      "without fine-tuning: 6% of programs run, IoU 0.082 on bench B.\n" +
      "GRPO: LoRA r64 on e55, G = 8 rollouts via vLLM, T = 1.0 with scaled logits, top_p 1, reward = exact IoU (0 on failure), " +
      "batch-std advantages, 4 minibatches with PPO clip-higher 0.2/0.28, KL 0, entropy floor, rollback guard; lr 2e-5 from e55, " +
      "1e-5 from trained adapters. Plain GRPO (ent_t10 s120, best of 3 seeds): 0.640. Self-improvement (expert iteration) x2 -> " +
      "rft2_rl s60: 0.665, +0.024 [+0.008, +0.041]; best of 8 0.732.\n" +
      "Repairer rp3: full fine-tune continued from e55 (300 steps, lr 2e-6, batch 64 = 4 ranks x accum 16, seq 7,168), rp2 repair " +
      "tiers + real repair rows from CADBench corpora (DeepSeek search). Stage 3 = rft2_rl s60 K=16 -> verifier + render-compare " +
      "pick -> 3 rp3 chains (16 x 6, gate margin 0.1) -> 0.721; same repair on e55: 0.664.");
  }

  // ================================ Figure 4: Repair Loop ============================================================
  {
    const s = pres.addSlide({ masterName: "TITLE_ONLY" });
    s.addText("Figure 4: Repair Loop", { placeholder: "title" });
    const W = 2.8, GAP = 0.42, X0 = (13.333 - 4 * W - 3 * GAP) / 2, Y = 1.2;
    const opt = { cardH: 0.6, cardY0: 0.6, cardStep: 0.76 };
    const H = opt.cardY0 + 2 * opt.cardStep + opt.cardH + 0.15;
    const ST = [
      ["1. Candidate", [["LuFileCode", "Start Program", "generator's selected pick", BLUE],
                        ["LuPlay", "Execute", "build123d → solid", BLUE],
                        ["LuPenTool", "Draw It", "same compiler as the input", BLUE]]],
      ["2. Repair", [["LuImages", "Repairer Input", "both drawings + code", GREEN],
                     ["LuCpu", "Repairer (rp3)", "fine-tuned Qwen3.8-27B", GREEN],
                     ["LuCopy", "16 Repairs", "sampled at T = 0.7", GREEN]]],
      ["3. Score", [["LuPlay", "Execute + Draw", "every repair", GREEN],
                    ["LuScanEye", "Render-Compare", "vs target, view by view", GREEN],
                    ["LuEyeOff", "No Ground Truth", "label-free; r = 0.67 with IoU", GREEN]]],
      ["4. Accept", [["LuShieldCheck", "Gate", "keep best only if score +0.1", GREEN],
                     ["LuRepeat", "Up to 6 Rounds", "restart from last accepted", GREEN],
                     ["LuGitBranch", "3 Chains", "top-3 starts, pick best score", GREEN]]],
    ];
    for (let i = 0; i < ST.length; i++) {
      const x = X0 + i * (W + GAP);
      await stage(s, x, Y, W, H, ST[i][0], ST[i][1], opt);
      if (i < ST.length - 1) arrowLine(s, x + W, Y + H / 2, x + W + GAP, Y + H / 2, 3, `stage arrow ${i + 1}`);
    }
    // loop back: from under "4. Accept" to under "1. Candidate"
    const LY = Y + H + 0.28, xa = X0 + 3 * (W + GAP) + W / 2, xb = X0 + W / 2;
    arrowLine(s, xa, Y + H, xa, LY, 2.25, "loop down", false);
    arrowLine(s, xa, LY, xb, LY, 2.25, "loop across", false);
    arrowLine(s, xb, LY, xb, Y + H, 2.25, "loop up");
    txt(s, "next round: accepted program becomes the new candidate", { x: xb + 0.3, y: LY + 0.04, w: 5.5, h: 0.25, fontSize: 11,
        color: C.accent3, objectName: "loop label" });

    // example strip: handwheel (real bench part F_73525), one repair chain
    const EY = LY + 0.4;
    txt(s, "Example: handwheel (real part)", { x: X0, y: EY, w: 4, h: 0.3, fontSize: 14, bold: true, color: C.text2, objectName: "example title" });
    const fit = (px, b) => { const k = Math.min(b.w / px[0], b.h / px[1]); return { x: b.x + (b.w - px[0] * k) / 2, y: b.y + (b.h - px[1] * k) / 2, w: px[0] * k, h: px[1] * k }; };
    const IY = EY + 0.36, IH = 1.45;
    s.addImage({ path: path.join(EX, "F_73525_drawing.png"), ...fit([1608, 1015], { x: X0, y: IY, w: 2.3, h: IH }), objectName: "example drawing" });
    txt(s, "Target drawing", { x: X0, y: IY + IH + 0.04, w: 2.3, h: 0.25, fontSize: 11, color: C.accent3, align: "center", objectName: "example drawing label" });
    const cells = [["F_73525_step0.png", [480, 634], "Start  IoU 0.52"], ["F_73525_step1.png", [482, 634], "Round 1  IoU 0.35"],
                   ["F_73525_step2.png", [482, 634], "Round 3  IoU 0.93"], ["F_73525_gt.png", [481, 634], "Ground truth"]];
    let cx = X0 + 2.55;
    cells.forEach(([f, sz, label], i) => {
      s.addImage({ path: path.join(EX, f), ...fit(sz, { x: cx, y: IY, w: 1.25, h: IH }), objectName: `example ${label}` });
      txt(s, label, { x: cx - 0.2, y: IY + IH + 0.04, w: 1.65, h: 0.25, fontSize: 11, bold: i === 2, color: i === 3 ? C.accent3 : C.text2,
                      align: "center", objectName: `example label ${i + 1}` });
      if (i < 2) arrowLine(s, cx + 1.3, IY + IH / 2, cx + 1.62, IY + IH / 2, 1.5, `example arrow ${i + 1}`);
      cx += i < 2 ? 1.67 : 1.85;
    });
    // headline numbers
    const SX = X0 + 4 * W + 3 * GAP - 2.55, stats = [["0.537 → 0.695", "real parts, e55 + repair"], ["0.925 → 0.929", "synthetic parts: safe"]];
    stats.forEach(([v, l], i) => {
      const sy = IY + i * 0.86;
      s.addShape(pres.shapes.RECTANGLE, { x: SX, y: sy, w: 2.55, h: 0.72, fill: { color: C.background1 }, line: { color: C.text2, width: 1.75 },
                                          objectName: `stat ${i + 1} frame` });
      txt(s, [{ text: v, options: { fontSize: 18, bold: true, color: C.text2, breakLine: true } }, { text: l, options: { fontSize: 11, color: C.accent3 } }],
          { x: SX, y: sy, w: 2.55, h: 0.72, align: "center", objectName: `stat ${i + 1}` });
    });
    s.addNotes(
      "One round: run the current program, draw it with the same drawing compiler (draftwright 0.4.23) that made the input sheets; " +
      "the repairer rp3 (full fine-tune of e55) sees the target drawing, the candidate's drawing and its code and samples 16 " +
      "corrected programs (T 0.7, <= 6,000 tokens). Each is executed and drawn; the render-compare score (v3: per-view comparison with " +
      "one scale per sheet pair, geometry separated from annotations by colour) measures the match to the target. Pearson r 0.67 with " +
      "true IoU on the real bench. The best repair is adopted only if its score beats the current program's by 0.1 (fixed a priori); " +
      "up to 6 rounds. Multi-start: 3 chains from the top-3 distinct starting candidates; final answer = highest render-compare score. " +
      "Ground truth is never used; the IoU values on the example are for illustration. Real bench (143 parts): e55 medoid pick 0.537 " +
      "-> one chain 0.667 -> 3 chains 0.695 (e55's own best of 8: 0.591). Synthetic pool: 0.925 -> 0.929. Handwheel = CADBench " +
      "Fusion 360 part F_73525; this chain started from the generator's third-ranked candidate. Limits: the colour-based score needs " +
      "draftwright-style sheets (all-black SolidWorks drawings score ~0), and on ABC parts the score tracks IoU less well (r 0.42 " +
      "vs 0.61 on Fusion 360).");
  }

  const out = path.join(HERE, "figures_3_4.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
