"""Cycle 2 teacher: DeepSeek vis-repair picks = training parts whose best known program (search/starts_<c>.json) is < 0.3
(the lowest rp3 priority bands). Writes teacher/picks_<c>.json {key: {code, iou}}."""
import json, os
C = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/cycle2"; os.makedirs(f"{C}/teacher", exist_ok=True)
for c in ("c4", "c2", "c1", "rp2"):
    f = f"{C}/search/starts_{c}.json"
    if not os.path.exists(f): continue
    P = {p["key"]: {"code": p["cands"][0]["code"], "iou": p["cands"][0]["iou"]} for p in json.load(open(f))["candidates"]
         if float(p["cands"][0]["iou"]) < 0.3}
    json.dump(P, open(f"{C}/teacher/picks_{c}.json", "w")); print(c, len(P))
