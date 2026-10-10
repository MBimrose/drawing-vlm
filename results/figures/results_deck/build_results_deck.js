// Editable results-section slides. Charts are the house-style SVGs from plot_results_deck.py (PowerPoint:
// right-click > Convert to Shape makes every line and label editable); titles, takeaways and gallery labels are
// native text boxes; gallery images are separate objects. Numbers come from data/summary.json.
//   NODE_PATH=<dir with pptxgenjs> PPTX_SKILL=<pptx skill dir> node build_results_deck.js
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const HERE = __dirname;
const S = require(path.join(HERE, "data", "summary.json"));
const THEME = {
  name: "Drawing to CAD", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: "13294B", lt2: "F2F2F2", accent1: "2F6FD6", accent2: "8A8F99",
            accent3: "5A5F69", accent4: "E84A27", accent5: "9FB3D6", accent6: "4D4D4D", hlink: "2F6FD6", folHlink: "5A5F69" },
};
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Results figures";
const C = pres.SchemeColor;
pres.defineSlideMaster({
  title: "TITLE_ONLY", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 12.3, h: 0.75, fontSize: 32,
                                         bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } }],
});

function chart(slide, name, x, y, size) {
  slide.addImage({ path: path.join(HERE, `${name}.svg`), x, y, w: size, h: size * S.aspect[name], objectName: `${name} chart`,
                   altText: name.replace(/_/g, " ") });
}

function bullets(slide, items, x, y, w, h) {
  slide.addText(items.map((t, i) => ({ text: t, options: { bullet: true, breakLine: i < items.length - 1 } })),
                { x, y, w, h, fontSize: 16, color: C.text1, valign: "top", paraSpaceAfter: 10, margin: 0, isTextBox: true,
                  objectName: "takeaways" });
}

function chartSlide(title, name, items, note) {
  const s = pres.addSlide({ masterName: "TITLE_ONLY" });
  s.addText(title, { placeholder: "title" });
  chart(s, name, 0.6, 1.25, 5.75);
  bullets(s, items, 7.0, 1.6, 5.8, 4.6);
  if (note) s.addNotes(note);
  return s;
}

// 1. repair loop (real bench)
const R = S.repair;
chartSlide("Repair Loop on Real Parts", "repair_loop", [
  `${R.n} held-out real parts (CADBench Fusion 360 + ABC), starting from the e55 medoid pick: mean IoU ${R.start.toFixed(3)}`,
  `One repair round: ${R.chain1_r1.toFixed(3)}, already above the generator's own best of 8 (${R.oracle8.toFixed(3)})`,
  `After 6 rounds: ${R.chain1_final.toFixed(3)} with one chain, ${R.ms_final.toFixed(3)} with 3 chains (multi-start)`,
  `Parts at IoU ≥ 0.85: ${(100 * R.frac85_start).toFixed(0)}% → ${(100 * R.frac85_final).toFixed(0)}%`,
  `Multi-start final by source: Fusion 360 ${R.fusion.toFixed(3)}, ABC ${R.abc.toFixed(3)}`,
], "Repair: rp3 LoRA, K=16 draws per round, adopt only when the label-free render-compare score improves by 0.1. " +
   "Multi-start: 3 chains from the top-3 distinct e55 candidates, final pick by render-compare score. Error bars: SEM over parts.");

// 1b. repair-loop example: drawing, every adopted program, ground truth
if (S.repair_ex && S.repair_ex.length) {
  const s = pres.addSlide({ masterName: "TITLE_ONLY" });
  s.addText("Repair Loop Example", { placeholder: "title" });
  const fit = (px, b) => { const k = Math.min(b.w / px[0], b.h / px[1]); return { x: b.x + (b.w - px[0] * k) / 2, y: b.y + (b.h - px[1] * k) / 2, w: px[0] * k, h: px[1] * k }; };
  const A = path.join(HERE, "repair_ex"), CELL = 2.05, GAP = 0.45, X0 = 3.55;
  S.repair_ex.forEach((r, ri) => {
    const y0 = 1.3 + ri * 2.95;
    s.addText(r.name, { x: 0.5, y: y0, w: 2.8, h: 0.34, fontSize: 15, bold: true, color: C.text2, margin: 0, isTextBox: true, objectName: `${r.id} name` });
    s.addImage({ path: path.join(A, `${r.id}_drawing.png`), ...fit(r.drawing, { x: 0.5, y: y0 + 0.4, w: 2.8, h: 2.1 }), objectName: `${r.id} drawing` });
    const cells = r.steps.map(st => ({ img: `${r.id}_step${st.step}.png`, size: st.size,
      label: st.round === 0 ? `Start  IoU ${st.iou.toFixed(2)}` : `Round ${st.round}  IoU ${st.iou.toFixed(2)}`, color: C.text2 }));
    cells.push({ img: `${r.id}_gt.png`, size: r.gt, label: "Ground truth", color: C.accent3 });
    cells.forEach((c, i) => {
      const x = X0 + i * (CELL + GAP);
      s.addImage({ path: path.join(A, c.img), ...fit(c.size, { x, y: y0 + 0.4, w: CELL, h: 1.75 }), objectName: `${r.id} ${c.label}` });
      s.addText(c.label, { x, y: y0 + 2.2, w: CELL, h: 0.3, fontSize: 12, bold: i === cells.length - 2, color: c.color, align: "center",
                           margin: 0, isTextBox: true, objectName: `${r.id} label ${i}` });
      if (i < cells.length - 1) s.addShape(pres.shapes.RIGHT_ARROW, { x: x + CELL + 0.08, y: y0 + 1.15, w: GAP - 0.16, h: 0.26,
        fill: { color: i === cells.length - 2 ? C.background1 : C.accent2 }, line: { color: C.background1, width: 0 }, objectName: `${r.id} arrow ${i}` });
    });
  });
  s.addNotes("Real-bench parts. Each image is a program the repair chain adopted (only adopted when the label-free render-compare score " +
             "improved by 0.1; IoU is computed afterwards against ground truth). Handwheel: chain started from the third-ranked e55 candidate; " +
             "hex nut: chain started from the e55 medoid pick.");
}

// 2. complexity vs IoU
const F = S.faces;
chartSlide("Part Complexity vs Accuracy", "faces_vs_iou", [
  `${F.n} synthetic test parts; complexity = face count of the ground-truth B-rep`,
  `Spearman ρ = ${F.rho.toFixed(2)} between face count and IoU`,
  ...F.bins.map(b => `${b.label} faces (n=${b.n}): mean IoU ${b.mean.toFixed(3)}, ${(100 * b.frac85).toFixed(0)}% at IoU ≥ 0.85`),
], "IoU of the served medoid (best of 8, consistency vote). Face count from the ground-truth STEP.");

// 3. execution time vs IoU
const T = S.exec;
if (T) chartSlide("Program Execution Time", "exectime_vs_iou", [
  `Time to execute the served build123d program into a solid (import excluded, STEP export included)`,
  `Median ${T.median.toFixed(2)} s, 95th percentile ${T.p95.toFixed(2)} s, max ${T.max.toFixed(1)} s (n=${T.n})`,
  `Spearman ρ = ${T.rho.toFixed(2)} with IoU`,
  `Parts at IoU ≥ 0.85 median ${T.median_ok.toFixed(2)} s vs ${T.median_bad.toFixed(2)} s below`,
], "Measured on the cluster CPU node (ccc0442), 12 programs in parallel, one subprocess per program.");

// 4. IoU distribution
{
  const s = pres.addSlide({ masterName: "TITLE_ONLY" });
  s.addText("Distribution of IoU", { placeholder: "title" });
  chart(s, "iou_hist", 0.6, 1.3, 5.6);
  chart(s, "iou_survival", 6.9, 1.3, 5.6);
  const D = S.dist;
  s.addText(`${D.n} synthetic test parts, e55 best of 8. Medoid: mean ${D.mean.toFixed(3)}, median ${D.median.toFixed(3)}, ` +
            `${(100 * D.frac85).toFixed(0)}% at IoU ≥ 0.85 (first executing draw ${(100 * D.first85).toFixed(0)}%, oracle ${(100 * D.oracle85).toFixed(0)}%)`,
            { x: 0.6, y: 6.85, w: 12.1, h: 0.4, fontSize: 14, color: C.accent3, margin: 0, isTextBox: true, objectName: "caption" });
}

// 5. failure gallery
if (S.gallery.length) {
  const s = pres.addSlide({ masterName: "TITLE_ONLY" });
  s.addText("Failure Cases", { placeholder: "title" });
  const items = [["Ground truth", C.accent2], ["Generation", C.accent1]]; let lx = 9.55;
  for (const [label, color] of items) {
    s.addShape(pres.shapes.RECTANGLE, { x: lx, y: 0.56, w: 0.22, h: 0.22, fill: { color }, line: { color, width: 0 }, objectName: `legend ${label}` });
    s.addText(label, { x: lx + 0.3, y: 0.47, w: 1.45, h: 0.4, fontSize: 14, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
    lx += 1.85;
  }
  const COLS = [0.5, 4.665, 8.83], ROWS = [1.3, 4.25], A = path.join(HERE, "gallery");
  const contain = (px, b) => { const k = Math.min(b.w / px[0], b.h / px[1]); return { x: b.x + (b.w - px[0] * k) / 2, y: b.y + (b.h - px[1] * k) / 2, w: px[0] * k, h: px[1] * k }; };
  S.gallery.forEach((p, i) => {
    const x0 = COLS[i % 3], y0 = ROWS[Math.floor(i / 3)];
    s.addText(p.mode, { x: x0, y: y0, w: 4.0, h: 0.34, fontSize: 15, bold: true, color: C.text2, margin: 0, valign: "middle", isTextBox: true, objectName: `${p.id} failure mode` });
    s.addImage({ path: path.join(A, `${p.id}_drawing.png`), ...contain(p.sizes.drawing, { x: x0, y: y0 + 0.4, w: 2.95, h: 2.0 }), objectName: `${p.id} drawing` });
    s.addImage({ path: path.join(A, `${p.id}_gt.png`), ...contain(p.sizes.gt, { x: x0 + 3.05, y: y0 + 0.4, w: 0.95, h: 0.95 }), objectName: `${p.id} ground truth` });
    s.addImage({ path: path.join(A, `${p.id}_gen.png`), ...contain(p.sizes.gen, { x: x0 + 3.05, y: y0 + 1.45, w: 0.95, h: 0.95 }), objectName: `${p.id} generation` });
    s.addText([{ text: `IoU ${p.iou.toFixed(2)}`, options: { bold: true, color: C.text2 } },
               { text: `   best of 8 ${p.oracle.toFixed(2)}  ·  ${p.n_exec}/8 executed`, options: { color: C.accent3 } }],
              { x: x0, y: y0 + 2.46, w: 4.0, h: 0.3, fontSize: 12, margin: 0, valign: "middle", isTextBox: true, objectName: `${p.id} metrics` });
  });
  s.addNotes("Lowest-IoU served parts on the synthetic test pool (e55 best of 8, medoid shown). Failure-mode labels are by inspection.");
}

(async () => {
  const out = path.join(HERE, "results_figures.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
