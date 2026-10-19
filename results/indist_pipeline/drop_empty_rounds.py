"""Remove records with an empty repair round (vr_serve writes one when the endpoint failed) from a block output so that
vr_serve redoes them on resume. Keeps a copy of removed records in <file>.dropped.jsonl.  python drop_empty_rounds.py out/X.jsonl"""
import json, os, sys
f = sys.argv[1]; keep, drop = [], []
for l in open(f):
    r = json.loads(l)
    (drop if any(len(x) == 0 for x in r.get("rounds", [])) else keep).append(l)
if drop:
    with open(f + ".dropped.jsonl", "a") as fo: fo.writelines(drop)
    tmp = f + ".tmp"; open(tmp, "w").writelines(keep); os.replace(tmp, f)
print(f"dropped {len(drop)} records with an empty round, kept {len(keep)}")
