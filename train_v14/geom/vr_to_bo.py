"""vis_repair jsonl -> candidates file ({candidates:[{key,cands:[{draw=round,code,iou,exec}]}]}) for render_compare / rc_metric2."""
import json, sys
out = {"candidates": []}
for l in open(sys.argv[1]):
    r = json.loads(l)
    cs = [{"draw": h["round"], "code": h["code"], "iou": h["iou"], "exec": h.get("exec", True)} for h in r["hist"] if "code" in h]
    out["candidates"].append({"key": r["key"], "cands": cs})
json.dump(out, open(sys.argv[2], "w")); print(len(out["candidates"]), "parts")
