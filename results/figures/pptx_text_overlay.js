// Place a matplotlib chart in a PPTX with its text as native Arial text boxes: <base>_notext.svg is the chart with every
// label removed, <base>_text.json (plot_pipeline_timing.save_text_overlay) the labels with their boxes in inches. The
// SVG's own font never matters, so the chart reads as Arial in any viewer, and every label is editable.
//   const { addChart } = require("../pptx_text_overlay");  addChart(slide, "/path/repair_sft_vs_grpo", { x, y, w, h }, "repair curve");
const fs = require("fs");

function addChart(s, base, box, name) {
  const T = JSON.parse(fs.readFileSync(`${base}_text.json`, "utf8")), [sw, sh] = T.size;
  const k = Math.min(box.w / sw, box.h / sh), x0 = box.x + (box.w - sw * k) / 2, y0 = box.y + (box.h - sh * k) / 2;
  s.addImage({ path: `${base}_notext.svg`, x: x0, y: y0, w: sw * k, h: sh * k, objectName: `${name} chart` });
  T.texts.forEach((t, i) => {
    const vert = Math.abs(t.rot % 180) > 45, pad = 0.15;   // slack so a slightly wider Arial run never wraps
    const cx = x0 + (t.x + t.w / 2) * k, cy = y0 + (t.y + t.h / 2) * k;
    let w = (vert ? t.h : t.w) * k + 2 * pad, h = (vert ? t.w : t.h) * k + 0.04, x = cx - w / 2;
    if (!vert && t.ha === "left") x = x0 + t.x * k;              // keep the anchored edge where matplotlib put it
    if (!vert && t.ha === "right") x = x0 + (t.x + t.w) * k - w;
    s.addText(t.text, { x, y: cy - h / 2, w, h, margin: 0, fontFace: "Arial", fontSize: t.size * k, bold: t.bold, color: t.color,
                        align: vert ? "center" : t.ha, valign: "middle", rotate: vert ? 270 : 0, wrap: false,
                        objectName: `${name} text ${i + 1}: ${t.text}` });
  });
}
module.exports = { addChart };
