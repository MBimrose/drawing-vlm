// Repair-step options for the "SFT + GRPO Replaces Repair Compute" slide: bench-B parts whose served repair chain
// adopted >= 2 repairs, both models, sorted by IoU gain. Every image, arrow and label is its own object so rows can
// be copied onto the slide. Inputs: prep_options.py -> deck/manifest.json.
//   NODE_PATH=<pptxgenjs> PPTX_SKILL=<pptx skill dir> node build_options.js
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
pres.title = "Repair step options";
const C = pres.SchemeColor;
pres.defineSlideMaster({
  title: "TITLE_ONLY", background: { color: "FFFFFF" },
  objects: [{ placeholder: { options: { name: "title", type: "title", x: 0.55, y: 0.3, w: 12.2, h: 0.75, fontSize: 32,
                                         bold: true, color: C.text2, align: "left", valign: "middle", margin: 0 }, text: "" } }],
});
const txt = (s, t, o) => s.addText(t, { margin: 0, isTextBox: true, color: C.text1, valign: "middle", ...o });
const fit = (px, b) => { const k = Math.min(b.w / px[0], b.h / px[1]); return { x: b.x + (b.w - px[0] * k) / 2, y: b.y + (b.h - px[1] * k) / 2, w: px[0] * k, h: px[1] * k }; };
const img = (s, file, px, b, name) => s.addImage({ path: path.join(A, file), ...fit(px, b), objectName: name });
const arrow = (s, x1, y, x2, name) => s.addShape(pres.shapes.LINE, { x: x1, y, w: x2 - x1, h: 0, line: { color: C.text1, width: 2, endArrowType: "triangle" }, objectName: name });

const NAME = { sft: "SFT + repair", grpo: "SFT + GRPO + repair" };
const PER = 3, RH = 1.95, CW = 1.75;
for (const model of ["grpo", "sft"]) {
  const parts = M[model];
  for (let p0 = 0; p0 < parts.length; p0 += PER) {
    const s = pres.addSlide({ masterName: "TITLE_ONLY" });
    s.addText(`${NAME[model]}: options ${p0 + 1}–${Math.min(p0 + PER, parts.length)}`, { placeholder: "title" });
    parts.slice(p0, p0 + PER).forEach((p, r) => {
      const y0 = 1.25 + r * RH, tag = `${model} ${p0 + r + 1}`;
      txt(s, `${p0 + r + 1}. ${p.key.slice(0, 22)}   gain ${p.gain >= 0 ? "+" : "−"}${Math.abs(p.gain).toFixed(3)}`,
          { x: 0.55, y: y0, w: 8, h: 0.25, fontSize: 12, bold: true, color: C.accent3, objectName: `${tag} title` });
      const cells = [{ file: `${p.id}_drawing.png`, size: p.drawing, label: "Drawing" }]
        .concat(p.steps.map((st, i) => ({ file: st.file, size: st.size, label: `${i ? `Round ${st.round}` : "Start"}\nIoU ${st.iou.toFixed(2)}`,
                                          bold: i === p.steps.length - 1, step: true })))
        .concat([{ file: `${p.id}_gt.png`, size: p.gt, label: "Ground truth" }]);
      cells.forEach((c, i) => {
        const x = 0.55 + i * (CW + 0.25);
        img(s, c.file, c.size, { x, y: y0 + 0.3, w: CW, h: 1.15 }, `${tag} ${c.label.split("\n")[0]}`);
        txt(s, c.label, { x: x - 0.1, y: y0 + 1.47, w: CW + 0.2, h: 0.42, fontSize: 11, bold: !!c.bold, align: "center",
                          color: C.text2, objectName: `${tag} label ${i + 1}` });
        if (c.step && cells[i + 1] && cells[i + 1].step) arrow(s, x + CW + 0.02, y0 + 0.88, x + CW + 0.23, `${tag} arrow ${i}`);
      });
    });
  }
}
(async () => {
  const out = path.join(H, "repair_options.pptx");
  await pres.writeFile({ fileName: out }); await applyTheme(out, THEME); console.log("wrote", out);
})();
