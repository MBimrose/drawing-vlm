#!/usr/bin/env python
"""Ground-truth-code tiers from the ABC corpus (rft_corpus_abccode, built by convert_cadfit_program.py),
rendered twice: draftwright 0.4.0+patch ("dw400", the renderer of corpora 1-3 and of every training
sheet so far) and 0.4.23+patch ("dw423"). The renderer alone moves e51 by ~0.07 on the held-out bench,
so "cannot write" is judged on the OLD renderer's sheets only.

Rows use the verified converted program as the supervision target (no model sample), in the
rft_v1 accepted-*.jsonl format pack_rft_shards_dir.py consumes:
  {key, iou (= verified iou_vs_step of the program vs the scaled banked STEP), ok: true, think: "",
   code, sample: 0, src: "gt", part_id, source_version, bo_best_dw400, bo_best_dw423}
Tiers written (each with png/<key>.png, keys.txt, stats.json):
  <out>            : unsolved parts (best-of-K of <run> on the dw400 sheet < --unsolved-below), dw400 PNGs
  <out>_dw423      : the same parts, keys suffixed "_dw423", dw423 PNGs (train on either or both)
  <out>_all        : every part rendered by both renderers, dw400 PNGs
  <out>_all_dw423  : same, dw423 PNGs, "_dw423" keys
plus <deltas>: per-part best-of-K IoU under both renderers and the agreement census.

  python write_rft_abccode.py --corpus <rft_corpus_abccode> --bo-dw400 <merged bo json, dw400 sheets> \
      --bo-dw423 <merged bo json, dw423 sheets> --png-dw400 <corpus_dw400/render/png> --png-dw423 <corpus/render/png> \
      --out rft_real_abccode --deltas results/abccode_render_deltas.json [--unsolved-below 0.8]
"""
import argparse, collections, glob, json, os, shutil, statistics as st

ap = argparse.ArgumentParser()
ap.add_argument("--corpus", required=True); ap.add_argument("--bo-dw400", required=True); ap.add_argument("--bo-dw423", required=True)
ap.add_argument("--png-dw400", required=True); ap.add_argument("--png-dw423", required=True)
ap.add_argument("--out", required=True); ap.add_argument("--deltas", required=True)
ap.add_argument("--unsolved-below", type=float, default=0.8)
a = ap.parse_args()

gt = {}
for line in open(os.path.join(a.corpus, "gt_code.jsonl")):
    r = json.loads(line); gt[r["key"]] = r
man = json.load(open(os.path.join(a.corpus, "manifest.json")))["parts"]


def cadbench_ok(k):
    """The CADBench prep filter of corpora 1-3 (prep_external_parts.py): aspect <= 15, fill >= 0.05, <= 120 faces."""
    p = man.get(k, {}); bb = sorted(p.get("bbox_mm") or [1, 1, 1])
    return bool(p) and bb[2] / max(bb[0], 1e-9) <= 15 and p.get("fill", 1.0) >= 0.05 and p.get("faces", 0) <= 120 and p.get("solids", 1) == 1


def best_of(path):
    d = json.load(open(path)); out = {}
    for p in d["candidates"]:
        ex = [float(c.get("iou") or 0.0) for c in p["cands"] if c.get("exec")]
        out[p["key"]] = {"best": max(ex) if ex else 0.0, "first_exec": ex[0] if ex else 0.0, "n_exec": len(ex)}
    return out


b400, b423 = best_of(a.bo_dw400), best_of(a.bo_dw423)
png400 = {k for k in gt if glob.glob(os.path.join(a.png_dw400, f"{k}_v*.png"))}
png423 = {k for k in gt if glob.glob(os.path.join(a.png_dw423, f"{k}_v*.png"))}
both = png400 & png423 & set(b400) & set(b423)
thr = a.unsolved_below
unsolved = {k for k in both if b400[k]["best"] < thr}
uns423 = {k for k in both if b423[k]["best"] < thr}
agree = {"n_scored_both": len(both), "unsolved_dw400": len(unsolved), "unsolved_dw423": len(uns423),
         "unsolved_both": len(unsolved & uns423), "unsolved_only_dw400": len(unsolved - uns423), "unsolved_only_dw423": len(uns423 - unsolved),
         "solved_both": len(both - unsolved - uns423),
         "mean_best_dw400": st.mean(b400[k]["best"] for k in both) if both else None, "mean_best_dw423": st.mean(b423[k]["best"] for k in both) if both else None,
         "mean_first_exec_dw400": st.mean(b400[k]["first_exec"] for k in both) if both else None, "mean_first_exec_dw423": st.mean(b423[k]["first_exec"] for k in both) if both else None,
         "mean_delta_best_dw423_minus_dw400": st.mean(b423[k]["best"] - b400[k]["best"] for k in both) if both else None,
         "parts_better_dw423_by_0.05": sum(1 for k in both if b423[k]["best"] - b400[k]["best"] > 0.05),
         "parts_worse_dw423_by_0.05": sum(1 for k in both if b423[k]["best"] - b400[k]["best"] < -0.05),
         "cadbench_filter_pass": sum(cadbench_ok(k) for k in both), "unsolved_dw400_cadbench_pass": sum(cadbench_ok(k) for k in unsolved)}
os.makedirs(os.path.dirname(os.path.abspath(a.deltas)), exist_ok=True)
json.dump({"threshold": thr, "agreement": agree,
           "parts": {k: {"best_dw400": b400[k]["best"], "best_dw423": b423[k]["best"], "first_exec_dw400": b400[k]["first_exec"],
                         "first_exec_dw423": b423[k]["first_exec"], "delta_best": b423[k]["best"] - b400[k]["best"],
                         "unsolved_dw400": k in unsolved, "unsolved_dw423": k in uns423, "iou_vs_step": gt[k]["iou_vs_step"],
                         "cadbench_filter_pass": cadbench_ok(k), "faces": man.get(k, {}).get("faces"), "bbox_mm": man.get(k, {}).get("bbox_mm"),
                         "source_version": gt[k]["source_version"]} for k in sorted(both)}},
          open(a.deltas, "w"), indent=1)
print(json.dumps(agree, indent=1))


def write(out, keys, label, png_dir, suffix):
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(os.path.join(out, "png"))
    with open(os.path.join(out, "accepted-000.jsonl"), "w") as f, open(os.path.join(out, "keys.txt"), "w") as kf:
        for k in sorted(keys):
            r = gt[k]; kk = k + suffix
            f.write(json.dumps({"key": kk, "iou": r["iou_vs_step"], "ok": True, "think": "", "code": r["code"], "sample": 0, "src": "gt",
                                "part_id": r["part_id"], "source_version": r["source_version"], "corpus_key": k,
                                "bo_best_dw400": b400[k]["best"], "bo_best_dw423": b423[k]["best"], "cadbench_filter_pass": cadbench_ok(k)}) + "\n")
            kf.write(kk + "\n")
            shutil.copy(sorted(glob.glob(os.path.join(png_dir, f"{k}_v*.png")))[0], os.path.join(out, "png", f"{kk}.png"))
    s = {"tier": label, "renderer": "draftwright 0.4.23+patch" if suffix else "draftwright 0.4.0+patch", "rows": len(keys), "keys": len(keys),
         "corpus_parts": len(gt), "rendered_dw400": len(png400), "rendered_dw423": len(png423), "scored_both": len(both),
         "unsolved_threshold": thr, "unsolved_judged_on": "dw400", "per_version": dict(collections.Counter(gt[k]["source_version"] for k in keys)),
         "cleaned_rows": sum(1 for k in keys if gt[k].get("cleaned")), "cadbench_filter_pass": sum(cadbench_ok(k) for k in keys),
         "mean_bo_best_dw400": st.mean(b400[k]["best"] for k in keys) if keys else None,
         "mean_bo_best_dw423": st.mean(b423[k]["best"] for k in keys) if keys else None}
    json.dump(s, open(os.path.join(out, "stats.json"), "w"), indent=1)
    print(label, "->", out, json.dumps({k: s[k] for k in ("rows", "renderer", "mean_bo_best_dw400", "mean_bo_best_dw423")}))


print(f"corpus {len(gt)} parts, rendered dw400 {len(png400)} / dw423 {len(png423)}, scored by both runs {len(both)}, "
      f"unsolved on dw400 (<{thr}) {len(unsolved)}, on dw423 {len(uns423)}, both {len(unsolved & uns423)}")
write(a.out, unsolved, "unsolved (dw400 sheets)", a.png_dw400, "")
write(a.out + "_dw423", unsolved, "unsolved (dw423 sheets)", a.png_dw423, "_dw423")
write(a.out + "_all", both, "all (dw400 sheets)", a.png_dw400, "")
write(a.out + "_all_dw423", both, "all (dw423 sheets)", a.png_dw423, "_dw423")
