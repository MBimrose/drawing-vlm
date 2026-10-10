"""Selection study (2026-10-07): score several stored candidate files with a regression verifier (reg_ev) in ONE
model load. Writes <outdir>/vpreds_<name>.json in verifier_select_offline's preds format
({key: [[pred, pred_maxvar, p_yes] | null per candidate in draw order]}).

    python sel_vscore.py --cache <bench>/eval_cache_v15.pkl --outdir results/selection \
        [--verifier runs/v3b-verifier-real-reg/final --verifier-run v3b-verifier-real-reg --base <dir>] name=cands.json ...
"""
import argparse, json, os, pickle, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
from verifier_select_offline import score_all  # noqa: E402
from data_v14 import _decode_png  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--cache", required=True)
ap.add_argument("--outdir", required=True)
ap.add_argument("--verifier", default="runs/v3b-verifier-real-reg/final")
ap.add_argument("--verifier-run", default="v3b-verifier-real-reg")
ap.add_argument("--base", default="")
ap.add_argument("--batch", type=int, default=8)
ap.add_argument("--prefix", default="vpreds_")
ap.add_argument("specs", nargs="+")
a = ap.parse_args()
a.prompt_mode = "reg_ev"
samples = pickle.load(open(a.cache, "rb"))["samples"]
parts, images, todo = [], {}, []
for s in a.specs:
    n, f = s.split("=", 1)
    outp = os.path.join(a.outdir, f"{a.prefix}{n}.json")
    if os.path.exists(outp):
        print(f"[sel_v] skip {n} (exists)", flush=True); continue
    ps = json.load(open(f))["candidates"]
    for p in ps:
        p["cands"].sort(key=lambda c: int(c.get("draw", 0)))
        for c in p["cands"]:
            c.pop("pred", None)
        mk = f"{n}|{p['key']}"
        if mk not in images:
            images[mk] = _decode_png(samples[p["key"]]["png"])
        parts.append({"key": mk, "cands": p["cands"]})
    todo.append((n, outp))
print(f"[sel_v] {len(todo)} files, {len(parts)} parts, "
      f"{sum(1 for p in parts for c in p['cands'] if c.get('exec') and c.get('code'))} executing candidates", flush=True)
if todo:
    t0 = time.time(); score_all(a, parts, images); print(f"[sel_v] scored in {time.time()-t0:.0f} s", flush=True)
    for n, outp in todo:
        pr = {p["key"].split("|", 1)[1]: [([c["pred"], c["pred_maxvar"], c["p_yes"]] if "pred" in c else None)
                                         for c in p["cands"]] for p in parts if p["key"].startswith(n + "|")}
        json.dump(pr, open(outp, "w")); print(f"[sel_v] wrote {outp} ({len(pr)} parts)", flush=True)
