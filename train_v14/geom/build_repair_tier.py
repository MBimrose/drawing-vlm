"""Build a REPAIR tier: (drawing with a failed attempt overlaid in red, that attempt's code)
-> the corrected code.

Motivation (RECIPE 2026-09-18): e56/e57/e58 showed that distilling parts the model already solves
adds nothing, whatever the source or the volume. A repair turn is different in kind — at test time
the model is handed information it did not have on the first pass: a picture of how its own answer
differs from the drawing. This builds the supervision for that skill from passes already scored.

Per part, pair every failed candidate (executed, IoU < --bad-max) with the part's best certified
candidate (IoU >= --good-min). The failed candidate is executed to STEP, drawn by the sheet
renderer under the part key (same layout as the input drawing), and painted over the input sheet
in red by rc_overlay. Member layout, ready for pack-free tar shards:

    <key>__r<n>.png        the overlay image (input drawing + failed attempt in red)
    <key>__r<n>.user.txt   the repair prompt, carrying the failed code
    <key>__r<n>.code.py    the corrected (certified) code    <- the training target
    <key>__r<n>.think.txt  empty (repair reasoning is not supervised here)
    <key>__r<n>.meta.json  {src_key, bad_iou, good_iou, draw}

    python build_repair_tier.py --bo <scored bo json> --bench <corpus dir> --out rft_repair_x \
        --rpy dw_venv/bin/python --script-dir mech_step_to_drw [--workers 90] [--max-per-part 2]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import pickle
import sys
import tarfile
import time
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from render_compare import render_candidate            # noqa: E402
from rc_overlay import overlay                          # noqa: E402

REPAIR_PROMPT = (
    "Your previous attempt at this drawing is overlaid on it in RED; the drawing's own linework is "
    "black and its annotations are blue. Wherever red and black disagree, your attempt is wrong: red "
    "without black underneath is geometry you added that the drawing does not show, and black with no "
    "red on it is geometry you failed to model.\n\n"
    "This is the code that produced the red attempt:\n\n```python\n{code}\n```\n\n"
    "Study the disagreements, then write the corrected build123d script for the part the drawing "
    "actually specifies. Output the complete script, not a patch."
)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo", required=True, help="scored best-of-N json (candidates with code/exec/iou)")
    ap.add_argument("--bench", required=True, help="corpus dir with eval_cache_v15.pkl (the input sheets)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--py", default=sys.executable)
    ap.add_argument("--rpy", required=True)
    ap.add_argument("--script-dir", required=True)
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--good-min", type=float, default=0.8)
    ap.add_argument("--bad-max", type=float, default=0.5)
    ap.add_argument("--max-per-part", type=int, default=2)
    ap.add_argument("--shard-size", type=int, default=2000)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--exec-timeout", type=int, default=90)
    ap.add_argument("--render-timeout", type=int, default=420)
    a = ap.parse_args()

    cache = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]
    parts = json.load(open(a.bo))["candidates"]
    jobs = []
    for p in parts:
        key = p["key"]
        if key not in cache:
            continue
        good = max(p["cands"], key=lambda c: c.get("iou", 0.0))
        if good.get("iou", 0.0) < a.good_min or not (good.get("code") or "").strip():
            continue
        bad = [c for c in p["cands"]
               if c.get("exec") and c.get("iou", 0.0) < a.bad_max and (c.get("code") or "").strip()]
        seen = set(); uniq = []
        for c in sorted(bad, key=lambda c: -c.get("iou", 0.0)):   # near-misses first: the instructive ones
            code = c["code"].strip()
            if code in seen or code == good["code"].strip():
                continue
            seen.add(code); uniq.append(c)
        for n, c in enumerate(uniq[: a.max_per_part]):
            jobs.append((key, n, c, good))
        if a.limit and len({j[0] for j in jobs}) >= a.limit:
            break
    print(f"[repair] {len({j[0] for j in jobs})} parts, {len(jobs)} repair pairs to render", flush=True)
    os.makedirs(a.out, exist_ok=True)
    os.makedirs(os.path.join(a.out, "shards"), exist_ok=True)

    t0 = time.time(); written = [0]; failed = [0]
    shard = {"i": 0, "n": 0, "tf": None}

    def open_shard():
        shard["tf"] = tarfile.open(os.path.join(a.out, "shards", f"rft-{shard['i']:05d}.tar"), "w")

    def add(name: str, data: bytes):
        ti = tarfile.TarInfo(name); ti.size = len(data)
        shard["tf"].addfile(ti, io.BytesIO(data))

    def work(job):
        key, n, bad, good = job
        png, info = render_candidate(bad["code"], key, a.py, a.rpy, a.script_dir, a.exec_timeout, a.render_timeout)
        if png is None:
            return None
        try:
            ov = overlay(cache[key]["png"], png)
        except Exception as e:
            print(f"[repair] overlay failed {key}: {type(e).__name__}", flush=True)
            return None
        return key, n, bad, good, ov

    open_shard()
    with ThreadPoolExecutor(a.workers) as ex:
        for m, r in enumerate(ex.map(work, jobs), 1):
            if r is None:
                failed[0] += 1
            else:
                key, n, bad, good, ov = r
                base = f"{key}__r{n}"
                add(base + ".png", ov)
                add(base + ".user.txt", REPAIR_PROMPT.format(code=bad["code"].strip()).encode())
                add(base + ".code.py", good["code"].strip().encode())
                add(base + ".think.txt", b"")
                add(base + ".meta.json", json.dumps({"src_key": key, "bad_iou": bad.get("iou", 0.0),
                                                     "good_iou": good.get("iou", 0.0), "draw": bad.get("draw")}).encode())
                written[0] += 1; shard["n"] += 1
                if shard["n"] >= a.shard_size:
                    shard["tf"].close(); shard["i"] += 1; shard["n"] = 0; open_shard()
            if m % 200 == 0:
                print(f"[repair] {m}/{len(jobs)} written={written[0]} failed={failed[0]} "
                      f"{(time.time()-t0)/m:.1f} s/pair", flush=True)
    shard["tf"].close()
    stats = {"pairs_written": written[0], "render_failed": failed[0], "parts": len({j[0] for j in jobs}),
             "shards": shard["i"] + 1, "good_min": a.good_min, "bad_max": a.bad_max,
             "max_per_part": a.max_per_part, "bo": a.bo, "bench": a.bench}
    json.dump(stats, open(os.path.join(a.out, "stats.json"), "w"), indent=1)
    print("[repair] " + json.dumps(stats), flush=True)


if __name__ == "__main__":
    main()
