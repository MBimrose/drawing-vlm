"""Pack DeepSeek's own successful samples (IoU >= 0.8) into RFT shards for dsv41_lora_train.py --think:
<key>.png (input sheet), <key>.think.txt (its own reasoning), <key>.code.py (its own code). Up to --per-part samples per
part, shortest completion first, at most --max-tok completion tokens. (2026-10-01)"""
import argparse, collections, io, json, os, pickle, tarfile
ap = argparse.ArgumentParser(); ap.add_argument("--ok", nargs="+"); ap.add_argument("--bench"); ap.add_argument("--out")
ap.add_argument("--per-part", type=int, default=2); ap.add_argument("--max-tok", type=int, default=32000); a = ap.parse_args()
S = pickle.load(open(os.path.join(a.bench, "eval_cache_v15.pkl"), "rb"))["samples"]
by = collections.defaultdict(list)
for f in a.ok:
    for l in open(f):
        r = json.loads(l); t = (r.get("usage") or {}).get("completion_tokens", 0) or 0
        if t <= a.max_tok: by[r["key"]].append((t, r))
os.makedirs(os.path.join(a.out, "shards"), exist_ok=True); tf = tarfile.open(os.path.join(a.out, "shards", "rft-00000.tar"), "w"); n = 0
def add(name, data):
    ti = tarfile.TarInfo(name); ti.size = len(data); tf.addfile(ti, io.BytesIO(data))
for k, rows in by.items():
    for i, (t, r) in enumerate(sorted(rows, key=lambda x: x[0])[: a.per_part]):
        kk = f"{k}__d{r['draw']}"; add(kk + ".png", S[k]["png"]); add(kk + ".think.txt", r["reasoning"].encode()); add(kk + ".code.py", r["code"].encode())
        add(kk + ".meta.json", json.dumps({"iou": r["iou"], "tokens": t, "src_key": k}).encode()); n += 1
tf.close(); print(f"self-training tier: {n} rows over {len(by)} parts (<= {a.max_tok} tokens) -> {a.out}")
