#!/usr/bin/env python
"""Pack rendered external-part sheets into an eval cache the existing eval
scripts accept unchanged (bestofn_verifier_eval.py / consistency_rerank.py /
geom_eval_worker.py read `cache["samples"][key]["png"]` and
`cache["pools"]["certified"]`; GT is `<bench>/gt_meshes_v15/<key>.stl`).

  .venv/bin/python train_v14/mech/benchmarks/build_ext_eval_cache.py \
      --bench <bench dir from prep_external_parts.py> --png-dir <dir of <key>*.png> \
      [--sidecar <renderers.json from the renderer>]   # drops dims_unplaced != [] sheets

Then point the eval scripts at it with env only (no code edits):
  export DRAWING_VLM_TRACES_JSON=<bench>/traces_v14.json      # written here, "{}"
  export DRAWING_VLM_EVAL_CACHE=<bench>/eval_cache_v14.pkl    # written here (= same cache)
  # e24 has data_version 2 -> scripts use <bench>/eval_cache_v15.pkl + <bench>/gt_meshes_v15/
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import pickle


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bench", required=True)
    ap.add_argument("--png-dir", required=True)
    ap.add_argument("--sidecar", default="")
    args = ap.parse_args()

    manifest = json.load(open(os.path.join(args.bench, "manifest.json")))["parts"]
    gt_dir = os.path.join(args.bench, "gt_meshes_v15")
    unplaced = set()
    if args.sidecar:
        side = json.load(open(args.sidecar))
        unplaced = {k.split("_v")[0] for k, v in side.items() if v.get("dims_unplaced")}
    samples, keys, missing = {}, [], []
    for key in manifest:
        pngs = sorted(glob.glob(os.path.join(args.png_dir, f"{key}*.png")))
        if not pngs or not os.path.exists(os.path.join(gt_dir, f"{key}.stl")):
            missing.append(key)
            continue
        if key in unplaced:
            continue
        with open(pngs[0], "rb") as f:
            samples[key] = {"png": f.read(), "code": "", "trace": "", "src": manifest[key]["src"]}
        keys.append(key)
    cache = {"samples": samples, "pools": {"certified": keys, "all": keys}}
    for name in ("eval_cache_v15.pkl", "eval_cache_v14.pkl"):
        with open(os.path.join(args.bench, name), "wb") as f:
            pickle.dump(cache, f)
    with open(os.path.join(args.bench, "traces_v14.json"), "w") as f:
        f.write("{}")
    open(os.path.join(args.bench, "legacy_keys_v14.txt"), "a").close()
    print(f"[cache] {len(keys)} sheets packed, {len(missing)} missing png/stl, "
          f"{len(unplaced & set(manifest))} underdetermined dropped -> {args.bench}")


if __name__ == "__main__":
    main()
