"""Visual-repair tier (2026-09-29): one row per wrong candidate that rendered.
    image = the part's target sheet, cand.png = the candidate's own sheet (render_compare --save-png-dir,
    <key>__<cand index>.png), user.txt = collate_v14.REPAIR_PROMPT with the candidate code, code.py = the part's
    ground-truth program, think.txt empty (repair turns are served in no-think format).
    python pack_repair_shards.py --bo <candidates json> --png-dir <rc png dir> --bench <bench with eval_cache_v15.pkl> --out <tier dir>"""
import argparse, io, json, os, pickle, sys, tarfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collate_v14 import REPAIR_PROMPT
ap = argparse.ArgumentParser(); ap.add_argument("--bo"); ap.add_argument("--png-dir"); ap.add_argument("--bench"); ap.add_argument("--out")
ap.add_argument("--per-shard", type=int, default=2000); ap.add_argument("--max-code", type=int, default=6000)
a = ap.parse_args()
S = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]
os.makedirs(os.path.join(a.out, "shards"), exist_ok=True)
def add(tf, name, data):
    ti = tarfile.TarInfo(name); ti.size = len(data); tf.addfile(ti, io.BytesIO(data))
n = shard = 0; tf = None; miss = 0; long_ = 0
for p in json.load(open(a.bo))["candidates"]:
    gt = S[p["key"]]["code"]
    if not gt or len(gt) > a.max_code: long_ += 1; continue
    for i, c in enumerate(p["cands"]):
        f = os.path.join(a.png_dir, f"{p['key']}__{i}.png")
        if not os.path.exists(f): miss += 1; continue
        if len(c["code"]) > a.max_code: long_ += 1; continue
        if tf is None or n % a.per_shard == 0:
            if tf: tf.close()
            tf = tarfile.open(os.path.join(a.out, "shards", f"rft-{shard:05d}.tar"), "w"); shard += 1
        k = f"{p['key']}__r{i}"
        add(tf, k + ".png", S[p["key"]]["png"]); add(tf, k + ".cand.png", open(f, "rb").read())
        add(tf, k + ".user.txt", REPAIR_PROMPT.format(code=c["code"]).encode()); add(tf, k + ".code.py", gt.encode())
        add(tf, k + ".think.txt", b""); add(tf, k + ".meta.json", json.dumps({"iou": 1.0, "cand_iou": c["iou"], "src_key": p["key"]}).encode())
        n += 1
if tf: tf.close()
print(f"repair tier: {n} rows in {shard} shards ({miss} unrendered, {long_} too long) -> {a.out}")
