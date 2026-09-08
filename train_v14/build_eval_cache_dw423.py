"""Certified eval cache on re-rendered sheets.

eval_cache_v15.pkl holds the frozen manifest's 1,072 certified eval samples
(png + code + trace, keyed by uuid; the png is the tars_v14 member named by the
manifest's tar_key). This swaps every png for the same part's sheet rendered by
another draftwright build (rerender_tars.py dir mode with --variants over
gt_meshes_v15/<uuid>.step, i.e. the bundle's generated.step, same variant index),
keeps code / trace / GT meshes unchanged, and drops parts without a new sheet.

    python build_eval_cache_dw423.py --png-dir <render/png> [--src eval_cache_v15.pkl]
        [--out eval_cache_v15_dw423.pkl] [--sidecar <render/renderers.json>]

Legacy-fallback sheets are already excluded by the renderer driver; the sidecar
(if given) is stored under cache["render_meta"] for per-part slicing.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import pickle

WDS = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--png-dir", required=True)
    ap.add_argument("--src", default=os.path.join(WDS, "eval_cache_v15.pkl"))
    ap.add_argument("--out", default=os.path.join(WDS, "eval_cache_v15_dw423.pkl"))
    ap.add_argument("--sidecar", default="")
    a = ap.parse_args()
    with open(a.src, "rb") as f:
        cache = pickle.load(f)
    pngs = {}
    for p in glob.glob(os.path.join(a.png_dir, "*_v*.png")):
        pngs[os.path.basename(p).rsplit("_v", 1)[0]] = p
    samples, missing = {}, []
    for uuid, s in cache["samples"].items():
        if uuid not in pngs:
            missing.append(uuid)
            continue
        with open(pngs[uuid], "rb") as f:
            samples[uuid] = dict(s, png=f.read())
    pools = {name: [k for k in keys if k in samples] for name, keys in cache["pools"].items()}
    out = {"samples": samples, "pools": pools,
           "source": {"src": a.src, "png_dir": a.png_dir, "missing": missing}}
    if a.sidecar:
        side = json.load(open(a.sidecar))
        out["render_meta"] = {k.rsplit("_v", 1)[0]: v for k, v in side.items()}
    with open(a.out + ".tmp", "wb") as f:
        pickle.dump(out, f)
    os.replace(a.out + ".tmp", a.out)
    print(f"[eval-cache-dw423] {len(samples)} samples, pools "
          + "  ".join(f"{k}={len(v)}" for k, v in pools.items())
          + f", {len(missing)} without a new sheet -> {a.out} ({os.path.getsize(a.out) / 1e6:.0f} MB)")
    if missing:
        with open(a.out + ".missing.txt", "w") as f:
            f.write("\n".join(missing) + "\n")


if __name__ == "__main__":
    main()
