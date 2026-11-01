// Pipeline-timing + bench-B repair slides (serv-05 lean 8x H200 run). Charts are house-style SVGs (Convert to Shape
// to edit); everything else is native, editable text/shapes/images. Inputs: prep_deck.py -> deck/manifest.json.
//   NODE_PATH=<pptxgenjs> PPTX_SKILL=<pptx skill dir> node build_deck.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const H = __dirname, A = path.join(H, "deck");
const M = require(path.join(A, "manifest.json"));
const THEME = {
  name: "Drawing to CAD", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: "13294B", lt2: "EEF2F8", accent1: "2F6FD6", accent2: "8A8F99",
            accent3: "5A5F69", accent4: "D3DEE0", accent5: "EEF4F0", accent6: "D6DEEA", hlink: "2F6FD6", folHlink: "5A5F69" },
};
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Drawing to part: timing and repair";
const C = pres.SchemeColor;
pres.defineSlideMaster({
  title: "TITLE_ONLY", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.55, y: 0.3, w: 12.2, h: 0.75, fontSize: 36,
                                         bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } }],
});
const txt = (s, t, o) => s.addText(t, { margin: 0, isTextBox: true, color: C.text1, valign: "middle", ...o });
const fit = (px, b) => { const k = Math.min(b.w / px[0], b.h / px[1]); return { x: b.x + (b.w - px[0] * k) / 2, y: b.y + (b.h - px[1] * k) / 2, w: px[0] * k, h: px[1] * k }; };
const img = (s, file, px, b, name) => s.addImage({ path: path.join(A, file), ...fit(px, b), objectName: name });
const chart = (s, name, x, y, w) => s.addImage({ path: path.join(H, `${name}.svg`), x, y, w, h: w * M.aspect[name], objectName: `${name} chart` });
const arrow = (s, x1, y, x2, name) => s.addShape(pres.shapes.LINE, { x: x1, y, w: x2 - x1, h: 0, line: { color: C.text1, width: 2, endArrowType: "triangle" }, objectName: name });
const f2 = v => v.toFixed(2), f3 = v => v.toFixed(3);
const B = M.table.bench_b, S = M.table.fullpool_dw423;

// 1. GRPO replaces repair compute: SFT + repair vs GRPO + repair (bench B) ------------------------------------------
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" }); s.addText("SFT + GRPO Replaces Repair Compute", { placeholder: "title" });
  chart(s, "repair_sft_vs_grpo", 0.55, 1.25, 5.3);
  // representative examples: one part at the 75th percentile, median and 10th percentile of the per-part repair gain
  const hx = [6.15, 7.75, 9.55, 11.35], hw = 1.45;
  ["Drawing", "SFT + GRPO", "After repair", "Ground truth"].forEach((h, i) =>
    txt(s, h, { x: hx[i] - 0.1, y: 1.2, w: hw + 0.2, h: 0.3, fontSize: 13, bold: true, align: "center", color: C.text2, objectName: `column ${i + 1}` }));
  M.repair_rep.forEach((e, r) => {
    const y0 = 1.6 + r * 1.75, g = e.gain;
    txt(s, `${e.pct}: ${g >= 0 ? "+" : "\u2212"}${Math.abs(g).toFixed(3)}`, { x: 6.15, y: y0, w: 6.7, h: 0.25, fontSize: 12, bold: true,
        color: C.accent3, objectName: `example ${r + 1} title` });
    img(s, `${e.id}_drawing.png`, e.drawing, { x: hx[0], y: y0 + 0.28, w: hw, h: 1.15 }, `example ${r + 1} drawing`);
    const cells = [[e.pick, e.pick_size, e.iou_start], [`${e.id}_final.png`, e.final, e.iou_final], [`${e.id}_gt.png`, e.gt, null]];
    cells.forEach(([f, sz, v], i) => {
      const x = hx[i + 1];
      img(s, f, sz, { x, y: y0 + 0.28, w: hw, h: 1.05 }, `example ${r + 1} ${["pick", "repaired", "ground truth"][i]}`);
      if (v !== null) txt(s, `IoU ${f2(v)}`, { x, y: y0 + 1.33, w: hw, h: 0.22, fontSize: 12, bold: i === 1, align: "center",
                                               color: C.text2, objectName: `example ${r + 1} IoU ${i + 1}` });
    });
    arrow(s, hx[1] + hw + 0.05, y0 + 0.8, hx[2] - 0.05, `example ${r + 1} arrow`);
  });
  const a = M.curve_sft, g = M.curve;
  txt(s, `280 held-out real parts. SFT + GRPO with no repair (${f3(g.multistart_mean[0])}) matches SFT alone after 6 repair rounds ` +
         `(${f3(a.multistart_mean[6])}); repair on SFT + GRPO adds +0.025 on average. Examples: representative parts by per-part repair gain.`,
      { x: 0.55, y: 6.75, w: 12.2, h: 0.4, fontSize: 12, color: C.accent3, objectName: "footnote" });
  s.addNotes("Both curves: 3 rp3 repair chains x 6 rounds x 16 repairs, render-compare gate (margin 0.1), served pick = chain with the best " +
    "render-compare score; mean IoU vs ground truth of the served program after each round, SEM whiskers. SFT = e55, K=8, starts = top-3 " +
    "distinct by consistency vote (12 Oct run). GRPO = rft2_rl_s60, K=8, starts = top-3 distinct by verifier + render-compare (20 Oct serv-05 run). " +
    "Paired, 280 parts: GRPO round 0 - SFT round 6 = +0.017 [-0.004, +0.039] (tie); GRPO round 6 - SFT round 6 = +0.042 [+0.020, +0.064]; " +
    "SFT gains +0.138 from repair, GRPO +0.025 [+0.008, +0.041]. GRPO no repair ~26 s per drawing vs ~294 s with repair.");
}

// 2. GRPO pipeline time (no repair) + table with optional repair -------------------------------------------------
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" }); s.addText("SFT + GRPO Pipeline: Time per Drawing", { placeholder: "title" });
  chart(s, "grpo_stage_times", 0.55, 1.25, 5.6);
  const T = M.grpo_times, ms = d => `${d.mean.toFixed(1)} ± ${d.std.toFixed(1)}`;
  const hdr = { bold: true, color: C.background1, fill: { color: C.text2 }, fontSize: 14, valign: "middle" };
  const cell = (t, o = {}) => ({ text: t, options: { fontSize: 14, color: C.text1, valign: "middle", ...o } });
  const opt = { color: C.accent3, italic: true };
  const rows = [[{ text: "Stage", options: hdr }, { text: "Time (s), mean ± std", options: { ...hdr, align: "center" } }],
    [cell("Generate 8 candidates"), cell(ms(T.generate), { align: "center" })],
    [cell("Execute candidates"), cell(ms(T.execute), { align: "center" })],
    [cell("Select best candidate (render-compare)"), cell(ms(T.select), { align: "center" })],
    [cell("Pipeline total (no repair)", { bold: true }), cell(ms(T.total), { align: "center", bold: true })],
    [cell(`Mean IoU`, { bold: true }), cell(f3(T.iou), { align: "center", bold: true })],
    [cell("Optional: repair (3 chains × 6 rounds)", opt), cell(ms(T.repair), { align: "center", ...opt })],
    [cell("Total with repair", opt), cell(ms(T.total_repair), { align: "center", ...opt })],
    [cell("Mean IoU, before → after repair", opt), cell(`${f3(T.iou_repair_start)} → ${f3(T.iou_repair)}`, { align: "center", ...opt })]];
  s.addTable(rows, { x: 6.55, y: 1.45, w: 6.2, colW: [3.9, 2.3], rowH: 0.48, border: { type: "solid", pt: 0.75, color: "8A8F99" },
                     objectName: "time table" });
  txt(s, T.paper_config
      ? `${T.n} held-out real parts (bench B); one model in bf16, a copy on each of 8 H200s, 8 drawings in flight. ` +
        `Repair rows (grey): separate run with repair; it adds ~+0.025 IoU for ~10× the time.`
      : `${T.n} held-out real parts (bench B), 8× H200 serving 6 drawings at once; repair adds +0.026 IoU for ~10× the time.`,
      { x: 6.55, y: 6.0, w: 6.2, h: 0.6, fontSize: 12, color: C.accent3, valign: "top", objectName: "footnote" });
  s.addNotes("Generate = 1 greedy + 7 sampled candidates (T 0.7, thinking, 2,400 tokens) from the SFT + GRPO model, bf16, one copy per H200 " +
    "(vLLM data parallel 8, 21 Oct, wpk-serv-05); execute = build123d -> STEP + STL; select = render each executing candidate as a drawing " +
    "and pick the best render-compare match (no verifier: offline it ties verifier + render-compare, +0.002 on bench B and synthetic). " +
    "Chart = median with interquartile whiskers. Repair rows come from the 20 Oct run with repair (3 rp3 chains x 6 rounds, verifier + " +
    "render-compare starts, 6 drawings in flight): total with repair " + ms(T.total_repair) + " s, IoU " + f3(T.iou_repair_start) + " -> " +
    f3(T.iou_repair) + ".");
}

// 2b. best SFT + GRPO reconstructions (no repair), contact-sheet style ---------------------------------------------
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" }); s.addText("SFT + GRPO Reconstructions", { placeholder: "title" });
  const legend = [["Ground truth", "8A8F99"], ["SFT + GRPO", "2F6FD6"]]; let lx = 9.55;
  for (const [label, color] of legend) {
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 0.56, w: 0.22, h: 0.22, fill: { color }, line: { color, width: 0 }, objectName: `legend ${label}` });
    txt(s, label, { x: lx + 0.3, y: 0.47, w: 1.5, h: 0.4, fontSize: 14, objectName: `legend ${label} text` }); lx += 1.85;
  }
  M.best.forEach((p, i) => {
    const x0 = 0.45 + (i % 4) * 3.15, y0 = 1.25 + Math.floor(i / 4) * 2.85;
    txt(s, p.name, { x: x0, y: y0, w: 3.0, h: 0.32, fontSize: 14, bold: true, color: C.text2, objectName: `${p.id} name` });
    img(s, `best_${p.id}_drawing.png`, p.drawing, { x: x0, y: y0 + 0.38, w: 2.05, h: 1.95 }, `${p.id} drawing`);
    img(s, `best_${p.id}_gt.png`, p.gt, { x: x0 + 2.15, y: y0 + 0.38, w: 0.85, h: 0.92 }, `${p.id} ground truth`);
    img(s, `best_${p.id}_pick.png`, p.pick, { x: x0 + 2.15, y: y0 + 1.4, w: 0.85, h: 0.92 }, `${p.id} reconstruction`);
    txt(s, `IoU ${p.iou.toFixed(3)}`, { x: x0, y: y0 + 2.36, w: 3.0, h: 0.3, fontSize: 12, bold: true, color: C.text2, objectName: `${p.id} iou` });
  });
  txt(s, "Held-out real parts (bench B). SFT + GRPO, 8 candidates, best one picked without labels; no repair (~26 s per drawing).",
      { x: 0.45, y: 6.95, w: 12.4, h: 0.35, fontSize: 12, color: C.accent3, objectName: "footnote" });
}

// 3. A: pipeline filmstrip ------------------------------------------------------------------------------------------
{
  const F = M.filmstrip, T = F.times;
  const s = pres.addSlide({ masterName: "TITLE_ONLY" }); s.addText("One Drawing Through the Pipeline", { placeholder: "title" });
  // stage time strip, to scale
  const segs = [["Generate", T.generate], ["Execute", T.execute], ["Select", T.select], ["Repair", T.repair]];
  const cols = ["13294B", "7E1E9C", "CF4C77", "F89540"], X0 = 0.6, WW = 12.1, tot = segs.reduce((a, b) => a + b[1], 0);
  let x = X0;
  segs.forEach(([lab, t], i) => {
    const w = Math.max(0.03, WW * t / tot);
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.2, w, h: 0.32, fill: { color: cols[i] }, line: { color: "FFFFFF", width: 0.75 }, objectName: `time ${lab}` });
    x += w;
  });
  txt(s, segs.map(([l, t]) => `${l} ${t.toFixed(0)} s`).join("   ·   ") + `   ·   total ${T.total.toFixed(0)} s`,
      { x: X0, y: 1.55, w: WW, h: 0.3, fontSize: 12, color: C.accent3, objectName: "time labels" });
  // drawing
  img(s, `${F.id}_drawing.png`, F.drawing, { x: 0.55, y: 2.05, w: 2.4, h: 2.0 }, "drawing");
  txt(s, "Input drawing", { x: 0.55, y: 4.1, w: 2.4, h: 0.3, fontSize: 12, bold: true, color: C.text2, align: "center", objectName: "drawing label" });
  // 8 candidates (2 x 4)
  txt(s, "1. Eight candidates", { x: 3.2, y: 1.95, w: 4.5, h: 0.3, fontSize: 14, bold: true, color: C.text2, objectName: "cand header" });
  F.cands.forEach((c, j) => {
    const cx = 3.2 + (j % 4) * 1.18, cy = 2.3 + Math.floor(j / 4) * 1.55;
    if (c.chosen !== null) s.addShape(pres.shapes.RECTANGLE, { x: cx - 0.04, y: cy - 0.04, w: 1.1, h: 1.43, fill: { color: C.background2 },
                                                              line: { color: C.text2, width: 1.5 }, objectName: `cand ${j} start box` });
    if (c.img) img(s, `${F.id}_cand${j}.png`, c.img, { x: cx, y: cy, w: 1.02, h: 1.0 }, `cand ${j}`);
    else txt(s, "failed", { x: cx, y: cy, w: 1.02, h: 1.0, fontSize: 11, color: C.accent2, align: "center", objectName: `cand ${j}` });
    txt(s, c.img ? `IoU ${f2(c.iou)}` : "no solid", { x: cx, y: cy + 1.03, w: 1.02, h: 0.3, fontSize: 11, align: "center",
        bold: c.chosen !== null, color: C.text2, objectName: `cand ${j} label` });
  });
  txt(s, "outlined = 3 repair starts", { x: 3.2, y: 5.4, w: 4.6, h: 0.3, fontSize: 11, color: C.accent3, objectName: "start note" });
  // repair chain -> final -> GT
  txt(s, "2. Repair (served chain)", { x: 8.15, y: 1.95, w: 4.6, h: 0.3, fontSize: 14, bold: true, color: C.text2, objectName: "repair header" });
  const cells = F.steps.map(st => ({ file: st.file, size: st.size, label: `${st.label}\nIoU ${f2(st.iou)}` }));
  cells.push({ file: `${F.id}_gt.png`, size: F.gt, label: "Ground truth", gt: true });
  const cw = 1.35;
  cells.forEach((c, i) => {
    const cx = 8.15 + i * (cw + 0.28);
    img(s, c.file, c.size, { x: cx, y: 2.4, w: cw, h: 1.5 }, `chain ${i + 1}`);
    txt(s, c.label, { x: cx - 0.1, y: 3.95, w: cw + 0.2, h: 0.5, fontSize: 12, align: "center", bold: i === cells.length - 2,
                      color: c.gt ? C.accent3 : C.text2, objectName: `chain label ${i + 1}` });
    if (i < cells.length - 2) arrow(s, cx + cw + 0.03, 3.15, cx + cw + 0.25, `chain arrow ${i + 1}`);
  });
  txt(s, "Bench-B part. Candidates are ranked by the verifier + render-compare score (no ground truth); IoU shown for reference.",
      { x: 0.55, y: 6.75, w: 12.2, h: 0.4, fontSize: 12, color: C.accent3, objectName: "footnote" });
}

// 4. C: time to scale for three parts ----------------------------------------------------------------------------
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" }); s.addText("Where the Time Goes", { placeholder: "title" });
  chart(s, "stage_bars", 0.55, 1.25, 6.0);
  M.abc.forEach((p, i) => {
    const y = 1.45 + i * 1.75;
    txt(s, String.fromCharCode(65 + i), { x: 7.0, y, w: 0.4, h: 1.4, fontSize: 24, bold: true, color: C.text2, objectName: `part ${i} letter` });
    img(s, `${p.id}_drawing.png`, p.drawing, { x: 7.45, y, w: 2.0, h: 1.4 }, `part ${i} drawing`);
    img(s, `${p.id}_final.png`, p.final, { x: 9.65, y, w: 1.4, h: 1.4 }, `part ${i} result`);
    txt(s, [{ text: `${p.times.total.toFixed(0)} s`, options: { bold: true, fontSize: 16, color: C.text2, breakLine: true } },
            { text: `repair ${(100 * p.times.repair / p.times.total).toFixed(0)}% of time`, options: { fontSize: 12, color: C.accent3, breakLine: true } },
            { text: `IoU ${f2(p.iou_start)} → ${f2(p.iou_final)}`, options: { fontSize: 12, color: C.accent3 } }],
        { x: 11.2, y, w: 1.9, h: 1.4, objectName: `part ${i} stats` });
  });
}

// 5. E: face count vs pipeline time, called-out parts as separate images ------------------------------------------
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" }); s.addText("Part Complexity vs Pipeline Time", { placeholder: "title" });
  chart(s, "faces_vs_pipeline_time", 0.55, 1.25, 5.9);
  M.abc.forEach((p, i) => {
    const x = 7.0 + i * 2.05;
    txt(s, String.fromCharCode(65 + i), { x, y: 1.6, w: 1.85, h: 0.4, fontSize: 20, bold: true, color: C.text2, align: "center", objectName: `callout ${i} letter` });
    img(s, `${p.id}_final.png`, p.final, { x, y: 2.05, w: 1.85, h: 1.85 }, `callout ${i} render`);
    txt(s, `${p.times.total.toFixed(0)} s`, { x, y: 3.95, w: 1.85, h: 0.3, fontSize: 13, bold: true, color: C.text2, align: "center", objectName: `callout ${i} time` });
  });
  txt(s, "Called-out parts are separate images: move, resize or delete them as needed.",
      { x: 7.0, y: 4.5, w: 6.0, h: 0.4, fontSize: 12, color: C.accent3, objectName: "note" });
}

// 7. Face count vs time, coloured by IoU, with called-out parts ----------------------------------------------------
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" }); s.addText("Part Complexity, Time and Accuracy", { placeholder: "title" });
  s.addImage({ path: path.join(H, "iou_time_faces", "v3_faces_time_by_iou_callouts.svg"), x: 0.55, y: 1.2, w: 5.9, h: 5.9 * M.aspect.v3,
               objectName: "v3 chart" });
  const hx = [7.35, 9.25, 11.15], hw = 1.65;
  ["Drawing", "SFT + GRPO", "Ground truth"].forEach((h, i) =>
    txt(s, h, { x: hx[i] - 0.1, y: 1.2, w: hw + 0.2, h: 0.3, fontSize: 13, bold: true, align: "center", color: C.text2, objectName: `column ${i + 1}` }));
  const rh = Math.min(1.75, 5.6 / M.v3.length);
  M.v3.forEach((c, r) => {
    const y0 = 1.6 + r * rh;
    txt(s, c.letter, { x: 6.75, y: y0 + 0.45, w: 0.45, h: 0.5, fontSize: 24, bold: true, color: C.text2, objectName: `callout ${c.letter}` });
    img(s, `v3_${c.letter}_drawing.png`, c.drawing, { x: hx[0], y: y0 + 0.05, w: hw, h: rh - 0.45 }, `${c.letter} drawing`);
    img(s, `v3_${c.letter}_pick.png`, c.pick, { x: hx[1], y: y0 + 0.05, w: hw, h: rh - 0.45 }, `${c.letter} pick`);
    img(s, `v3_${c.letter}_gt.png`, c.gt, { x: hx[2], y: y0 + 0.05, w: hw, h: rh - 0.45 }, `${c.letter} ground truth`);
    txt(s, `${c.faces} faces  ·  ${c.time.toFixed(0)} s  ·  IoU ${f2(c.iou)}`, { x: hx[0], y: y0 + rh - 0.37, w: hx[2] + hw - hx[0], h: 0.25,
        fontSize: 12, align: "center", color: C.accent3, objectName: `${c.letter} stats` });
  });
  s.addNotes("SFT + GRPO without repair: 8 candidates -> execute -> render-compare pick (no verifier: offline it ties verifier + " +
    "render-compare, +0.002 on bench B and synthetic). bf16, one copy per H200 (vLLM data parallel 8, wpk-serv-05, 21 Oct), 8 drawings in " +
    "flight. Time = generate + execute + select per drawing; IoU = ground truth vs the served pick. Squares = bench B (280 real), circles " +
    "= synthetic pool (1,027). Left out: 7 synthetic parts above 150 s (193-315 s), render-compare timeouts (300 s cap on one candidate's " +
    "drawing render). Renders at the drawing's isometric camera. " + M.v3.map(c => `${c.letter}: ${c.key}`).join("; "));
}

(async () => {
  const out = path.join(H, "pipeline_timing.pptx");
  await pres.writeFile({ fileName: out }); await applyTheme(out, THEME); console.log("wrote", out);
})();
