// "Table 2: Results" slide for the three American open-weight VLMs (2026-10-31), in the layout of the user's slide 6:
// a native PowerPoint table, synthetic mean IoU over real (held-out bench B, 280 parts) mean IoU in each cell, the best
// American model per row and bench in bold. Blank = not run yet (Nemotron GRPO running). Numbers: results/american_vlm/README.md.
//   NODE_PATH=<dir with pptxgenjs> node build_slide.js
const pptxgen = require("pptxgenjs");

const NAVY = "13294B", RULE = "D9D9D9", TEXT = "222222";
const MODELS = ["Muse-Glimmer-30B", "Gemma-4-31B", "Nemotron-3.5-Super-VL\n(120B-A12B)"];
// [synthetic, real] per model; null = not run
const ROWS = [
  ["Off-the-shelf", [[0.007, 0.001], [0.000, 0.000], [0.032, 0.002]]],
  ["LoRA", [[0.778, 0.364], [0.727, 0.360], [0.645, 0.284]]],
  ["Full Fine-Tune (FFT)", [[0.808, 0.403], [0.760, 0.392], [0.790, 0.364]]],
  ["FFT + 8 Candidate Vote", [[0.919, 0.522], [0.888, 0.497], [0.897, 0.497]]],
  ["FFT + 8 Candidate Vote +\nGRPO", [[0.900, 0.621], [0.897, 0.565], null]],
  ["FFT + 8 Candidate Vote +\nVisual Repair", [[0.951, 0.633], [0.925, 0.617], [0.937, 0.613]]],
  ["FFT + 8 Candidate Vote +\nGRPO + Visual Repair", [[0.953, 0.665], [0.932, 0.630], null]],
];

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9";
pres.title = "Table 2: Results (American VLMs)";
const s = pres.addSlide();
s.background = { color: "FFFFFF" };
s.addText("Table 2: Results", { x: 0.35, y: 0.18, w: 6, h: 0.5, fontFace: "Arial", fontSize: 26, bold: true,
  color: NAVY, margin: 0, isTextBox: true });

const hdrBorder = [{ type: "none" }, { type: "none" }, { pt: 2, color: NAVY }, { type: "none" }];
const head = [{ text: "Synthetic Mean IoU\nReal Mean IoU", options: { bold: true, align: "center", border: hdrBorder } }]
  .concat(MODELS.map(m => ({ text: m, options: { bold: true, align: "center", border: hdrBorder } })));

const rows = [head];
ROWS.forEach(([label, cells]) => {
  const best = [0, 1].map(i => Math.max(...cells.filter(Boolean).map(c => c[i])));
  const lab = { text: label, options: { bold: true, align: "left",
    border: [{ type: "none" }, { pt: 1.25, color: TEXT }, { pt: 0.75, color: RULE }, { type: "none" }] } };
  const vals = cells.map(c => ({
    text: c === null ? [{ text: "" }] : [0, 1].map(i => ({ text: c[i].toFixed(3),
      options: { bold: c[i] === best[i] && best[i] > 0.01, breakLine: i === 0 } })),
    options: { align: "center", border: [{ type: "none" }, { type: "none" }, { pt: 0.75, color: RULE }, { type: "none" }] },
  }));
  rows.push([lab].concat(vals));
});

s.addTable(rows, {
  x: 0.98, y: 1.0, w: 7.8, colW: [2.31, 1.83, 1.83, 1.83],
  rowH: [0.42].concat(ROWS.map(() => 0.425)),
  fontFace: "Arial", fontSize: 12, color: TEXT, valign: "middle", margin: [0.02, 0.06, 0.02, 0.06],
});

s.addText("Synthetic: 1,027 parts. Real: held-out set, 280 parts. Bold: best of the three models.", {
  x: 0.98, y: 4.8, w: 7.8, h: 0.25, fontFace: "Arial", fontSize: 9, color: "666666", margin: 0, isTextBox: true });

// footer as on the user's template slide
s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 5.39, w: 10, h: 0.235, fill: { color: NAVY }, line: { type: "none" } });
s.addText("I", { x: 0.02, y: 5.39, w: 0.18, h: 0.235, fontFace: "Arial Black", fontSize: 13, bold: true, color: "FF5F05",
  align: "center", valign: "middle", margin: 0, isTextBox: true });
s.addText("Mechanical Science and Engineering", { x: 0.34, y: 5.39, w: 4, h: 0.235, fontFace: "Arial", fontSize: 8,
  charSpacing: 2, color: "FFFFFF", valign: "middle", margin: 0, isTextBox: true });
s.addText("6", { x: 9.5, y: 5.39, w: 0.3, h: 0.235, fontFace: "Arial", fontSize: 8, color: "FFFFFF", align: "right",
  valign: "middle", margin: 0, isTextBox: true });

pres.writeFile({ fileName: __dirname + "/table2_american_results.pptx" }).then(f => console.log("wrote", f));
