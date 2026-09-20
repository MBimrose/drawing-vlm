"""Turn a scored best-of-N run into a REPAIR bench: for each part, the candidate the serving
policy actually picked is overlaid on the drawing, and that overlay becomes the part's input
image with a repair prompt carrying the picked candidate's code.

Feeding this bench to gen_openai_bo (with --user-prompts) asks the model to fix its own answer
given a picture of what it got wrong — the test-time information a selector can never add. The
ground-truth meshes are symlinked from the source bench, so scoring and every downstream summary
work unchanged and the repaired IoU is directly comparable with the original pick.

    python make_repair_bench.py --bo results/ext/bo8_ext_dw423p_<run>.json \
        --gated results/ext/bo8_ext_dw423p_<run>_gated.json --bench <src bench> \
        --png-dir results/ext/rc_png_bo8_dw423p_e55 --out <repair bench dir>
"""
from __future__ import annotations

import argparse
import json
import os
import pickle
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from build_repair_tier import REPAIR_PROMPT     # noqa: E402
from rc_overlay import overlay                   # noqa: E402


def picked_index(part, gated, key):
    """Index of the candidate the policy served: the gated selection when available, else the
    medoid by candidate agreement, else the first executed draw."""
    g = (gated or {}).get(key)
    if isinstance(g, dict):
        pick = g.get("pick")                    # gated_select.py: {"pick": {policy: index}}
        if isinstance(pick, dict):
            for pol in ("gate0.85", "verifier", "vote", "first_exec"):
                if isinstance(pick.get(pol), int):
                    return pick[pol]
        for f in ("idx", "index", "choice"):
            if isinstance(g.get(f), int):
                return g[f]
    ex = [i for i, c in enumerate(part["cands"]) if c.get("exec")]
    return ex[0] if ex else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo", required=True)
    ap.add_argument("--bench", required=True)
    ap.add_argument("--png-dir", required=True, help="candidate sheets from render_compare --save-png-dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--gated", default="")
    ap.add_argument("--rc", default="", help="rc json: use the best render-score candidate as the pick")
    ap.add_argument("--max-iou", type=float, default=1.01, help="only build parts whose pick scores below this")
    a = ap.parse_args()

    src_cache = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))
    parts = {p["key"]: p for p in json.load(open(a.bo))["candidates"]}
    gated = {}
    if a.gated and os.path.exists(a.gated):
        g = json.load(open(a.gated))
        gated = g.get("picks") or {}
    rc = {}
    if a.rc and os.path.exists(a.rc):
        rc = {p["key"]: p["cands"] for p in json.load(open(a.rc))["parts"]}

    os.makedirs(a.out, exist_ok=True)
    gt_src = os.path.abspath(os.path.join(a.bench, "gt_meshes_v15"))
    gt_dst = os.path.join(a.out, "gt_meshes_v15")
    if not os.path.lexists(gt_dst):
        os.symlink(gt_src, gt_dst)
    for extra in ("split.json", "eval_cache_v14.pkl", "manifest.json"):
        s, d = os.path.abspath(os.path.join(a.bench, extra)), os.path.join(a.out, extra)
        if os.path.exists(s) and not os.path.lexists(d):
            os.symlink(s, d)

    samples = {}; prompts = {}; rows = []; skipped = 0
    for key, p in parts.items():
        if key not in src_cache["samples"]:
            continue
        i = (max(range(len(rc[key])), key=lambda j: rc[key][j].get("v3", rc[key][j].get("score", 0.0)))
             if rc.get(key) else picked_index(p, gated, key))
        i = min(i, len(p["cands"]) - 1)
        cand = p["cands"][i]
        if not (cand.get("code") or "").strip() or cand.get("iou", 0.0) > a.max_iou:
            skipped += 1; continue
        png = os.path.join(a.png_dir, f"{key}__{i}.png")
        if not os.path.exists(png):      # identical code shares one rendered sheet
            alt = [j for j, c in enumerate(p["cands"])
                   if (c.get("code") or "").strip() == cand["code"].strip() and os.path.exists(os.path.join(a.png_dir, f"{key}__{j}.png"))]
            if not alt:
                skipped += 1; continue
            png = os.path.join(a.png_dir, f"{key}__{alt[0]}.png")
        try:
            ov = overlay(src_cache["samples"][key]["png"], open(png, "rb").read())
        except Exception as e:
            print(f"[repair-bench] overlay failed {key}: {type(e).__name__}", flush=True); skipped += 1; continue
        samples[key] = {"png": ov, "code": "", "trace": "", "src": key}
        prompts[key] = REPAIR_PROMPT.format(code=cand["code"].strip())
        rows.append({"key": key, "pick_index": i, "pick_iou": cand.get("iou", 0.0),
                     "best_iou": max(c.get("iou", 0.0) for c in p["cands"])})

    keys = sorted(samples)
    pickle.dump({"samples": samples, "pools": {"certified": keys, "all": keys}},
                open(os.path.join(a.out, "eval_cache_v15.pkl"), "wb"))
    json.dump(prompts, open(os.path.join(a.out, "user_prompts.json"), "w"))
    json.dump(rows, open(os.path.join(a.out, "picks.json"), "w"), indent=1)
    n = max(1, len(rows))
    print(f"[repair-bench] {len(rows)} parts ({skipped} skipped) -> {a.out}\n"
          f"  picked-candidate IoU mean {sum(r['pick_iou'] for r in rows)/n:.3f}, "
          f"{sum(r['pick_iou'] >= 0.85 for r in rows)/n:.1%} >= 0.85 | "
          f"their best-of-N {sum(r['best_iou'] for r in rows)/n:.3f}", flush=True)


if __name__ == "__main__":
    main()
