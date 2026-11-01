// Paper timing table as an editable PPTX table, in the style of the main results table: bold first column, bold header,
// navy rule under the header, thin grey rules between rows, no vertical lines, numbers centred.
// Numbers: paper_timing_table.md (bf16, render-compare pick, one copy per H200, 8 drawings in flight, 21 Oct 2026).
//   NODE_PATH=<pptxgenjs> node build_timing_table.js   -> timing_table.pptx
const path = require("path");
const pptxgen = require("pptxgenjs");

const NAVY = "13294B", GREY = "D3D6DB";
const rows = [
  ["Generate", "8 candidates (1 greedy + 7 sampled)", "10.7 ± 2.3", "9.9 ± 2.9"],
  ["Execute", "Run each program (build123d)", "3.2 ± 0.8", "3.2 ± 0.5"],
  ["Select", "Render each candidate, pick best render-compare", "11.9 ± 21.4", "8.9 ± 4.8"],
  ["Total", "Drawing to part", "25.9 ± 22.0", "22.0 ± 6.4", true],
  ["Visual Repair", "Optional: 3 chains × 6 rounds", "", "+267.9 ± 142.9"],
  ["Total with Visual Repair", "Drawing to repaired part", "", "294.3 ± 145.2"],
];
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE"; pres.title = "Pipeline timing";
const s = pres.addSlide(); s.background = { color: "FFFFFF" };
const base = { fontFace: "Arial", fontSize: 14, color: "000000", valign: "middle", margin: [0, 6, 0, 6] };
const rule = { type: "solid", pt: 0.75, color: GREY }, none = { type: "none" };
const hdr = (t, align) => ({ text: t, options: { ...base, bold: true, align, border: [none, none, { type: "solid", pt: 2, color: NAVY }, none] } });
const table = [[hdr("Stage", "left"), hdr("Description", "left"), hdr("Synthetic Test\nTime (s)", "center"), hdr("Real Test\nTime (s)", "center")]];
rows.forEach(([a, b, c, d, bold]) => {
  const o = { ...base, border: [none, none, rule, none] };
  table.push([{ text: a, options: { ...o, bold: true } }, { text: b, options: o },
              { text: c, options: { ...o, align: "center", bold: !!bold } }, { text: d, options: { ...o, align: "center", bold: !!bold } }]);
});
s.addTable(table, { x: 0.4, y: 0.6, w: 12.5, colW: [3.0, 5.3, 2.1, 2.1], rowH: [0.6, ...rows.map(() => 0.5)], objectName: "timing table" });
s.addNotes("SFT + GRPO (Qwen3.8-27B), bf16, one model copy per H200 on one 8xH200 node, 8 drawings in flight; mean ± std per drawing. " +
  "Synthetic n = 1,027 (std inflated by 7 render-compare timeouts; without them total 24.2 ± 7.3 s); real = bench B, n = 280. " +
  "Visual Repair rows: separate run with repair (20 Oct; verifier + render-compare starts, generator on 2 GPUs, repairer on 6), IoU 0.680 -> 0.706.");
pres.writeFile({ fileName: path.join(__dirname, "timing_table.pptx") }).then(f => console.log("wrote", f));
