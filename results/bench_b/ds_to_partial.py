"""DeepSeek T0-regime episodes (dsv41_t0_rollout.py jsonl) -> gen_openai_bo.py .partial.json, so the vanilla-DeepSeek
baseline is scored by exactly the same scorer/settings as every e55/GRPO eval (score_partials.py: exec 60 s, IoU 90 s,
default --accept 0.8) and voted by consistency_rerank.py.
  --mode final : the episode's final program (<= 3 calls: answer-now / exec-fix) -- the T0 regime as defined
  --mode first : the first call's program only (single call per draw, like the e55 protocol); None if it had no code
Draw index = episode draw (all draws sampled at the hub default T 1.0; there is no greedy draw 0 for DeepSeek).
    python ds_to_partial.py <episodes.jsonl> <out stem> --mode final --k 8"""
import argparse, json
ap = argparse.ArgumentParser(); ap.add_argument("jsonl"); ap.add_argument("out"); ap.add_argument("--mode", default="final")
ap.add_argument("--k", type=int, default=8)
a = ap.parse_args()
eps = {}
for l in open(a.jsonl):
    r = json.loads(l); eps[(r["key"], r["draw"])] = r
keys = sorted({k for k, _ in eps})
cands, miss = [], 0
for k in keys:
    cs = []
    for d in range(a.k):
        r = eps.get((k, d))
        if r is None: miss += 1; code = None
        elif a.mode == "final": code = r["code"] or None
        else: code = (r["turns"][0].get("code") or None) if r["turns"] else None
        think = "" if r is None or not r["turns"] else (r["turns"][0].get("think") or "")[:2000]
        cs.append({"draw": d, "code": code, "think": think, "exec": False, "iou": 0.0})
    cands.append(cs)
json.dump({"keys": keys, "k": a.k, "cands": cands}, open(f"{a.out}.shard0.json.partial.json", "w"))
print(f"{len(keys)} parts, {sum(c['code'] is not None for cs in cands for c in cs)} candidates with code, {miss} missing episodes")
