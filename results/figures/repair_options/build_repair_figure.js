// Repair figure (no title, figure-style slide): repair-curve chart on the left, chosen repair trajectories on the right,
// one row per part: drawing | Start -> Round a -> ... -> final (bold). Every image, arrow and label is an editable object.
// Inputs: prep_options.py -> deck/manifest.json; ../pipeline_timing/repair_sft_vs_grpo_{notext.svg,text.json}.
//   NODE_PATH=<pptxgenjs> node build_repair_figure.js <model: grpo|sft> <option numbers...>
//   e.g. node build_repair_figure.js grpo 3 8 12   -> repair_figure_grpo_3_8_12.pptx
//   NAMES=Coupling,Bushing,Shelf OUT=name.pptx: optional target labels and output file name
//   <model>_iso (renders at the drawing's isometric camera): the drawing column shows only the sheet's ISO view
const path = require("path");
const pptxgen = require("pptxgenjs");
const { addChart } = require("../pptx_text_overlay");

const H = __dirname, A = path.join(H, "deck"), PT = path.join(H, "..", "pipeline_timing");
const M = require(path.join(A, "manifest.json"));
const model = process.argv[2], picks = process.argv.slice(3).map(Number);
const NAMES = (process.env.NAMES || "").split(",").filter(Boolean);   // one-word part names under the drawings, e.g. NAMES=Coupling,Bushing,Shelf
const parts = picks.map(n => M[model][n - 1]);
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE"; pres.title = "Repair loop";
const s = pres.addSlide(); s.background = { color: "FFFFFF" };
const fit = (px, b) => { const k = Math.min(b.w / px[0], b.h / px[1]); return { x: b.x + (b.w - px[0] * k) / 2, y: b.y + (b.h - px[1] * k) / 2, w: px[0] * k, h: px[1] * k }; };
const img = (file, px, b, name) => s.addImage({ path: path.join(A, file), ...fit(px, b), objectName: name });

// chart: square house-style SVG, left half
const CH = 6.6;
addChart(s, path.join(PT, "repair_sft_vs_grpo"), { x: 0.3, y: (7.5 - CH) / 2, w: CH, h: CH }, "repair curve");   // labels as native Arial text

// rows on the right
const X0 = 7.15, XR = 13.15, ncell = Math.max(...parts.map(p => p.steps.length)), DW = 1.45, AW = 0.32;
const cw = (XR - X0 - DW - 0.1 - (ncell - 1) * AW) / ncell, RH = 6.6 / parts.length, Y0 = (7.5 - 6.6) / 2;
parts.forEach((p, r) => {
  const y = Y0 + r * RH, ih = RH - 0.75, tag = `row ${r + 1}`;
  if (model.endsWith("_iso")) img(`${p.id}_iso.png`, p.iso, { x: X0, y: y + 0.1, w: DW, h: ih }, `${tag} drawing ISO view`);
  else img(`${p.id}_drawing.png`, p.drawing, { x: X0, y: y + 0.1, w: DW, h: ih }, `${tag} drawing`);
  if (NAMES[r]) s.addText([{ text: "Target", options: { breakLine: true } }, { text: NAMES[r] }],
                          { x: X0 - 0.15, y: y + ih + 0.08, w: DW + 0.3, h: 0.55, margin: 0, fontFace: "Arial", fontSize: 14, color: "000000",
                            align: "center", valign: "top", objectName: `${tag} target label` });
  p.steps.forEach((st, i) => {
    const x = X0 + DW + 0.1 + i * (cw + AW), last = i === p.steps.length - 1;
    img(st.file, st.size, { x, y: y + 0.05, w: cw, h: ih }, `${tag} ${i ? "round " + st.round : "start"}`);
    s.addText([{ text: i ? `Round ${st.round}` : "Start", options: { breakLine: true } }, { text: `IoU ${st.iou.toFixed(2)}` }],
              { x: x - 0.15, y: y + ih + 0.08, w: cw + 0.3, h: 0.55, margin: 0, fontFace: "Arial", fontSize: 14, bold: last,
                color: "000000", align: "center", valign: "top", objectName: `${tag} label ${i + 1}` });
    if (!last) s.addShape(pres.shapes.LINE, { x: x + cw + 0.04, y: y + 0.05 + ih / 2, w: AW - 0.08, h: 0,
                                             line: { color: "000000", width: 2.5, endArrowType: "triangle" }, objectName: `${tag} arrow ${i + 1}` });
  });
});
s.addNotes(parts.map((p, r) => `Row ${r + 1}: ${model} option ${picks[r]}, ${p.key}, served repair chain (best render-compare of 3), ` +
  p.steps.map(st => `r${st.round} ${st.iou.toFixed(3)}`).join(" -> ")).join("\n") +
  "\nBench B (held-out real). Renders: every adopted program on one camera with the ground truth (same scale).");
const out = path.join(H, process.env.OUT || `repair_figure_${model}_${picks.join("_")}.pptx`);
pres.writeFile({ fileName: out }).then(f => console.log("wrote", f));
