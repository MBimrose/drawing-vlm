// Editable contact-sheet deck: per part a large input drawing with small GT (grey) and generation (blue) renders.
// Every image and label is its own object so the slides can be rearranged in PowerPoint.
//   node build_deck.js   (run from this directory; NODE_PATH must reach pptxgenjs)
const path = require("path");
const pptxgen = require("pptxgenjs");
const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");

const HERE = __dirname;
const parts = require(path.join(HERE, "manifest.json"));
const THEME = {
  name: "Drawing to CAD", headFontFace: "Arial", bodyFontFace: "Arial",
  colors: { dk1: "000000", lt1: "FFFFFF", dk2: "13294B", lt2: "F2F2F2", accent1: "2F6FD6", accent2: "8A8F99",
            accent3: "5A5F69", accent4: "E84A27", accent5: "9FB3D6", accent6: "4D4D4D", hlink: "2F6FD6", folHlink: "5A5F69" },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";           // 13.333 x 7.5 in
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.title = "Complex test parts: drawing to generation";
const C = pres.SchemeColor;

pres.defineSlideMaster({
  title: "TITLE_ONLY",
  background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.3, w: 8.6, h: 0.75, fontSize: 32,
                                         bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 },
                             text: "" } }],
});

// fit an image of (pw, ph) pixels inside a box, centred
function contain(px, box) {
  const [pw, ph] = px, s = Math.min(box.w / pw, box.h / ph);
  const w = pw * s, h = ph * s;
  return { x: box.x + (box.w - w) / 2, y: box.y + (box.h - h) / 2, w, h };
}

function legend(slide) {
  const items = [["Ground truth", C.accent2], ["Generation", C.accent1]];
  let x = 9.55;
  for (const [label, color] of items) {
    slide.addShape(pres.shapes.RECTANGLE, { x, y: 0.56, w: 0.22, h: 0.22, fill: { color }, line: { color, width: 0 },
                                             objectName: `legend ${label}` });
    slide.addText(label, { x: x + 0.3, y: 0.47, w: 1.45, h: 0.4, fontSize: 14, color: C.text1, margin: 0,
                           valign: "middle", isTextBox: true, objectName: `legend ${label} text` });
    x += 1.85;
  }
}

function tile(slide, p, x0, y0) {
  slide.addText(p.name, { x: x0, y: y0, w: 4.0, h: 0.34, fontSize: 15, bold: true, color: C.text2, margin: 0,
                          valign: "middle", isTextBox: true, objectName: `${p.id} name` });
  const D = path.join(HERE, "assets");
  slide.addImage({ path: path.join(D, `${p.id}_drawing.png`), ...contain(p.sizes.drawing, { x: x0, y: y0 + 0.4, w: 2.95, h: 2.0 }),
                   objectName: `${p.id} drawing`, altText: `Input drawing, ${p.name}` });
  slide.addImage({ path: path.join(D, `${p.id}_gt.png`), ...contain(p.sizes.gt, { x: x0 + 3.05, y: y0 + 0.4, w: 0.95, h: 0.95 }),
                   objectName: `${p.id} ground truth`, altText: `Ground-truth solid, ${p.name}` });
  slide.addImage({ path: path.join(D, `${p.id}_gen.png`), ...contain(p.sizes.gen, { x: x0 + 3.05, y: y0 + 1.45, w: 0.95, h: 0.95 }),
                   objectName: `${p.id} generation`, altText: `Generated solid, ${p.name}` });
  slide.addText([
    { text: `IoU ${p.iou.toFixed(3)}`, options: { bold: true, color: C.text2 } },
    { text: `   agreement ${p.agree.toFixed(2)}  ·  ${p.n_exec}/8 executed`, options: { color: C.accent3 } },
  ], { x: x0, y: y0 + 2.46, w: 4.0, h: 0.3, fontSize: 12, margin: 0, valign: "middle", isTextBox: true,
       objectName: `${p.id} metrics` });
}

const COLS = [0.5, 4.665, 8.83], ROWS = [1.3, 4.25];
const titles = ["Complex Test Parts", "Complex Test Parts (continued)"];
for (let s = 0; s < 2; s++) {
  const slide = pres.addSlide({ masterName: "TITLE_ONLY" });
  slide.addText(titles[s], { placeholder: "title" });
  legend(slide);
  parts.slice(6 * s, 6 * s + 6).forEach((p, i) => tile(slide, p, COLS[i % 3], ROWS[Math.floor(i / 3)]));
  slide.addNotes("Best-of-8 e55 generations on the synthetic test pool; the generation shown is the medoid (consistency vote). " +
                 "IoU = exact volumetric IoU vs ground truth; agreement = medoid's mean pairwise IoU with the other executing candidates.");
}

(async () => {
  const out = path.join(HERE, "complex_parts_contact_sheet.pptx");
  await pres.writeFile({ fileName: out });
  await applyTheme(out, THEME);
  console.log("wrote", out);
})();
