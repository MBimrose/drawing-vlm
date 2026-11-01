// Failure-case figure (2 x 2), layout of the earlier failure slide: per panel a title, the drawing sheet, IoU, and on the
// right the ground truth (grey) over the SFT + GRPO generation (blue), both rendered at the drawing's isometric angle.
// Every image and label is an editable object. Inputs: options.json + renders/<key>/{drawing,gt,pick}.png
// (render_callouts.py --iso, bf16 run).
//   NODE_PATH=<pptxgenjs> node build_failure_figure.js OUT.pptx "Title|n" "Title|n" "Title|n" "Title|n"
const path = require("path"), fs = require("fs");
const pptxgen = require("pptxgenjs");

const H = __dirname, A = path.join(H, "fig_assets"); fs.mkdirSync(A, { recursive: true });
const O = Object.fromEntries(require(path.join(H, "options.json")).map(o => [o.n, o]));
const M = require(path.join(A, "manifest.json"));   // written by prep_failure_figure.py: crop sizes per option
const [out, ...panels] = process.argv.slice(2);
const pres = new pptxgen(); pres.layout = "LAYOUT_WIDE"; pres.title = "Failure cases";
const s = pres.addSlide(); s.background = { color: "FFFFFF" };
const fit = (px, b) => { const k = Math.min(b.w / px[0], b.h / px[1]); return { x: b.x + (b.w - px[0] * k) / 2, y: b.y + (b.h - px[1] * k) / 2, w: px[0] * k, h: px[1] * k }; };
const T = (t, o) => s.addText(t, { margin: 0, fontFace: "Arial", color: "000000", valign: "middle", ...o });
panels.forEach((p, i) => {
  const [title, n] = p.split("|"), o = O[+n], m = M[n], x0 = 0.35 + (i % 2) * 6.45, y0 = 0.2 + Math.floor(i / 2) * 3.55;
  T(title, { x: x0, y: y0, w: 6.2, h: 0.5, fontSize: 24, bold: true, color: "13294B", align: "center", objectName: `${title} title` });
  s.addImage({ path: path.join(A, `${n}_drawing.png`), ...fit(m.drawing, { x: x0, y: y0 + 0.6, w: 3.9, h: 2.1 }), objectName: `${n} drawing` });
  T(`IoU ${o.iou.toFixed(2)}`, { x: x0 + 0.3, y: y0 + 2.8, w: 2.4, h: 0.4, fontSize: 18, bold: true, color: "13294B", objectName: `${n} IoU` });
  s.addImage({ path: path.join(A, `${n}_gt.png`), ...fit(m.gt, { x: x0 + 4.05, y: y0 + 0.6, w: 2.1, h: 1.25 }), objectName: `${n} ground truth` });
  s.addImage({ path: path.join(A, `${n}_pick.png`), ...fit(m.pick, { x: x0 + 4.05, y: y0 + 1.9, w: 2.1, h: 1.25 }), objectName: `${n} generation` });
});
// legend, bottom right
[["8A8F99", "Ground truth", 9.0], ["2F6FD6", "Generation", 11.2]].forEach(([c, t, x]) => {
  s.addShape(pres.shapes.RECTANGLE, { x, y: 7.17, w: 0.22, h: 0.22, fill: { color: c }, line: { type: "none" }, objectName: `${t} swatch` });
  T(t, { x: x + 0.3, y: 7.1, w: 1.8, h: 0.36, fontSize: 18, bold: true, objectName: `${t} legend` });
});
s.addNotes(panels.map(p => { const [t, n] = p.split("|"), o = O[+n]; return `${t}: option ${n}, ${o.key}, ${o.set}, ${o.faces} faces, IoU ${o.iou.toFixed(3)}`; }).join("\n") +
  "\nSFT + GRPO without repair, bf16 run (21 Oct). Renders at the drawing's isometric camera; ground truth and generation share one scale.");
pres.writeFile({ fileName: path.join(H, out) }).then(f => console.log("wrote", f));
