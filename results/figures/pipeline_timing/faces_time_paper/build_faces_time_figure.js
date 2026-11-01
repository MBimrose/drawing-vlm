// 1-column figure as an editable one-slide PPTX: the chart (figure/chart.svg, fixed layout) fills the slide, and every
// overlay is its own object: a circle + letter on each called-out point, and in the empty top band a panel per
// callout (letter, drawing ISO view, SFT + GRPO pick). Inputs: faces_time_figure.py -> figure/manifest.json.
//   NODE_PATH=<pptxgenjs> [ABOVE=D] [NORING=D] node build_faces_time_figure.js
const path = require("path");
const pptxgen = require("pptxgenjs");

const H = path.join(__dirname, "figure");
const M = require(path.join(H, "manifest.json"));
const [W, HT] = M.fig_in;
const pres = new pptxgen(); pres.defineLayout({ name: "FIG", width: W, height: HT }); pres.layout = "FIG";
pres.title = "Face count vs drawing-to-part time";
const s = pres.addSlide(); s.background = { color: "FFFFFF" };
s.addImage({ path: path.join(H, "chart.svg"), x: 0, y: 0, w: W, h: HT, objectName: "chart" });

const fit = (px, b) => { const k = Math.min(b.w / px[0], b.h / px[1]); return { x: b.x + (b.w - px[0] * k) / 2, y: b.y + (b.h - px[1] * k) / 2, w: px[0] * k, h: px[1] * k }; };
const letter = (t, x, y, name, halo) => s.addText(t, { x, y, w: 0.3, h: 0.25, margin: 0, fontFace: "Arial", fontSize: 13, bold: true,
                                                   color: "000000", valign: "middle", objectName: name,
                                                   ...(halo ? { glow: { size: 4, opacity: 1, color: "FFFFFF" } } : {}) });
const ABOVE = (process.env.ABOVE || "").split(",");    // letters placed above their ring
const NORING = (process.env.NORING || "").split(",");  // letters with no ring: a leader line from the label to the point itself
const [ax, ay, aw] = M.axes, n = M.callouts.length;
const bandTop = M.band[0] * HT, bandH = (M.band[1] - M.band[0]) * HT, pw = aw * W / n;
M.callouts.forEach((c, i) => {
  // marker on the data point
  const px = c.pt[0] * W, py = c.pt[1] * HT, ring = !NORING.includes(c.letter), d = ring ? 0.2 : 0.04;   // no ring: leader runs to the point
  if (ring) s.addShape(pres.shapes.OVAL, { x: px - d / 2, y: py - d / 2, w: d, h: d, line: { color: "000000", width: 1.75 }, fill: { type: "none" },
                                 objectName: `${c.letter} marker` });
  if (c.label_pt) {   // label off the point in the emptiest nearby spot, thin leader line from the ring edge to the letter
    const lx = c.label_pt[0] * W, ly = c.label_pt[1] * HT, dx = lx - px, dy = ly - py, L = Math.hypot(dx, dy);
    const ux = dx / L, uy = dy / L, x1 = px + ux * (d / 2 + 0.02), y1 = py + uy * (d / 2 + 0.02), x2 = lx - ux * 0.12, y2 = ly - uy * 0.12;
    s.addShape(pres.shapes.LINE, { x: Math.min(x1, x2), y: Math.min(y1, y2), w: Math.abs(x2 - x1), h: Math.abs(y2 - y1),
                                   flipH: (x2 < x1) !== (y2 < y1), line: { color: "000000", width: 1 }, objectName: `${c.letter} leader line` });
    s.addText(c.letter, { x: lx - 0.15, y: ly - 0.125, w: 0.3, h: 0.25, margin: 0, fontFace: "Arial", fontSize: 13, bold: true, color: "000000",
                          align: "center", valign: "middle", objectName: `${c.letter} point letter` });
  } else {            // letter centred directly under the ring (above it for letters in ABOVE, e.g. when a mean marker sits below)
    const up = ABOVE.includes(c.letter);
    s.addText(c.letter, { x: px - 0.15, y: up ? py - d / 2 - 0.23 : py + d / 2 + 0.01, w: 0.3, h: 0.22, margin: 0, fontFace: "Arial", fontSize: 13,
                          bold: true, color: "000000", align: "center", valign: up ? "bottom" : "top",
                          objectName: `${c.letter} point letter` });
  }
  // panel in the top band: letter, ISO view of the drawing, generated part
  const x0 = ax * W + i * pw + 0.04;
  letter(c.letter, x0, bandTop + 0.04, `${c.letter} panel letter`);
  s.addImage({ path: path.join(H, `iso_${c.letter}.png`), ...fit(c.iso, { x: x0 + 0.06, y: bandTop + 0.08, w: pw - 0.16, h: bandH * 0.42 }),
               objectName: `${c.letter} drawing ISO view` });
  s.addImage({ path: path.join(H, `pick_${c.letter}.png`), ...fit(c.pick, { x: x0 + 0.06, y: bandTop + 0.1 + bandH * 0.44, w: pw - 0.16, h: bandH * 0.5 }),
               objectName: `${c.letter} SFT + GRPO part` });
});
s.addNotes(M.callouts.map(c => `${c.letter}: ${c.key} — ${c.faces} faces, ${c.time.toFixed(0)} s, IoU ${c.iou.toFixed(2)}`).join("\n"));
pres.writeFile({ fileName: path.join(__dirname, "faces_time_figure.pptx") }).then(f => console.log("wrote", f));
