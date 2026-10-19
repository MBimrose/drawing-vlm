"""In-dist pipeline (2026-10-14): S1 starts for the parts whose consistency shards are finished, so S1 chains can start
before the slowest shards (pathological Monte-Carlo IoU pairs) end. pg_make_starts.py ranks each part from its own data
only, so a part's starts are identical whether computed on a subset or on the full pool.
    python s1_partial.py <tag> <shard ids...>   -> part_<tag>_cands.json, part_<tag>_consistency.json"""
import json, sys
tag, ids = sys.argv[1], [int(x) for x in sys.argv[2:]]
cands = json.load(open("full_k16_rl2s60.json"))
parts = {}
for i in ids:
    for p in json.load(open(f"cons_shards/shard_{i}_consistency.json"))["parts"]: parts[p["key"]] = p
sub = dict(cands, candidates=[p for p in cands["candidates"] if p["key"] in parts])
json.dump(sub, open(f"part_{tag}_cands.json", "w"))
json.dump({"parts": [parts[p["key"]] for p in sub["candidates"]]}, open(f"part_{tag}_consistency.json", "w"))
print(tag, len(sub["candidates"]), "parts")
