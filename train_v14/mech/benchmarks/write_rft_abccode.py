#!/usr/bin/env python
"""Ground-truth-code tier from the ABC corpus (rft_corpus_abccode, built by convert_cadfit_program.py).

Rows use the verified converted program as the supervision target (no model sample), in the
rft_v1 accepted-*.jsonl format pack_rft_shards_dir.py consumes:
  {key, iou (= verified iou_vs_step of the program against the scaled banked STEP), ok: true,
   think: "", code, sample: 0, src: "gt"}
Two tiers are written:
  <out>        : parts the generator could NOT write — best-of-K IoU of <run> on the corpus sheet
                 below --unsolved-below (default 0.8), from the merged best-of-K json
  <out>_all    : every rendered corpus part
plus png/<key>.png (the corpus sheet), keys.txt and stats.json in each.

  python write_rft_abccode.py --corpus <rft_corpus_abccode> --bo <results/bo8_rft_corpus_abccode_<run>.json> \
      --out rft_real_abccode [--unsolved-below 0.8]
"""
import argparse, collections, glob, json, os, shutil

ap = argparse.ArgumentParser()
ap.add_argument("--corpus", required=True); ap.add_argument("--bo", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--unsolved-below", type=float, default=0.8)
a = ap.parse_args()

gt = {}
for line in open(os.path.join(a.corpus, "gt_code.jsonl")):
    r = json.loads(line); gt[r["key"]] = r
bo = json.load(open(a.bo))
best = {}
for p in bo["candidates"]:
    best[p["key"]] = max([float(c.get("iou") or 0.0) for c in p["cands"] if c.get("exec")] or [0.0])
png_dir = os.path.join(a.corpus, "render", "png")
rendered = {k for k in gt if glob.glob(os.path.join(png_dir, f"{k}_v*.png"))}


def write(out, keys, label):
    os.makedirs(os.path.join(out, "png"), exist_ok=True)
    with open(os.path.join(out, "accepted-000.jsonl"), "w") as f, open(os.path.join(out, "keys.txt"), "w") as kf:
        for k in sorted(keys):
            r = gt[k]
            f.write(json.dumps({"key": k, "iou": r["iou_vs_step"], "ok": True, "think": "", "code": r["code"], "sample": 0, "src": "gt",
                                "part_id": r["part_id"], "source_version": r["source_version"], "bo_best": best.get(k)}) + "\n")
            kf.write(k + "\n")
            shutil.copy(sorted(glob.glob(os.path.join(png_dir, f"{k}_v*.png")))[0], os.path.join(out, "png", f"{k}.png"))
    st = {"tier": label, "rows": len(keys), "keys": len(keys), "corpus_parts": len(gt), "rendered": len(rendered),
          "unsolved_threshold": a.unsolved_below, "bo_file": os.path.basename(a.bo), "bo_keys": len(best),
          "per_version": dict(collections.Counter(gt[k]["source_version"] for k in keys)),
          "cleaned_rows": sum(1 for k in keys if gt[k].get("cleaned")),
          "mean_bo_best": (sum(best.get(k, 0.0) for k in keys) / len(keys)) if keys else None}
    json.dump(st, open(os.path.join(out, "stats.json"), "w"), indent=1)
    print(label, json.dumps(st))


scored = {k for k in rendered if k in best}
unsolved = {k for k in scored if best[k] < a.unsolved_below}
print(f"corpus {len(gt)} parts, rendered {len(rendered)}, scored by best-of-K {len(scored)}, "
      f"unsolved (<{a.unsolved_below}) {len(unsolved)}, solved {len(scored) - len(unsolved)}")
write(a.out, unsolved, "unsolved")
write(a.out + "_all", rendered, "all")
