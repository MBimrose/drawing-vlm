"""In-dist pipeline (2026-10-14): integrity check of the block outputs (out/ = ccc0442, out_s20/ = rsynced from serv-20).
Per chain: parts present / missing vs the pool, duplicates across hosts, records with an empty repair round (endpoint failure:
must be redone), records without repair rounds (start did not execute/render: legitimate, the chain final = start), rounds < 6.
    python validate.py"""
import glob, json, os
from collections import Counter
P = os.path.dirname(os.path.abspath(__file__))
POOL = {p["key"] for p in json.load(open(os.path.join(os.path.dirname(P), "grpo_eval", "full_e55ctl.json")))["candidates"]}
for sysname in ("e55", "rl2s60"):
    for c in (1, 2, 3):
        seen, dup, empty, norounds, short = {}, [], [], 0, 0
        for f in sorted(f for f in glob.glob(f"{P}/out/{sysname}_c{c}.*jsonl") + glob.glob(f"{P}/out_s20/{sysname}_c{c}.*jsonl") if not f.endswith(".dropped.jsonl")):
            for l in open(f):
                r = json.loads(l); k = r["key"]
                if k in seen: dup.append(k)
                seen[k] = f
                if any(len(x) == 0 for x in r["rounds"]): empty.append((k, f))
                if not r["rounds"]: norounds += 1
                elif len(r["rounds"]) < 6: short += 1
        miss = POOL - set(seen)
        print(f"{sysname}_c{c}: {len(seen)}/{len(POOL)} parts, missing {len(miss)}, dup {len(dup)}, empty-round {len(empty)}, "
              f"no-rounds (start not rendered) {norounds}, <6 rounds {short}")
        for k, f in empty[:5]: print("   empty round:", k, os.path.relpath(f, P))
