"""Selection study (2026-10-07): concatenate several models' stored K-draw candidate files on the SAME bench into
one candidates file (per part: model 0's draws, then model 1's, ...), so render_compare / verifier scoring run once.
Part keys stay unchanged (render_ext seeds the sheet layout from the key). Split back with sel_study.py.

    python sel_concat.py --out results/selection/rc_in.json name=path.json [name=path.json ...]
"""
import argparse, json

ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("specs", nargs="+")
a = ap.parse_args()
names, per = [], []
for s in a.specs:
    n, f = s.split("=", 1)
    d = {p["key"]: sorted(p["cands"], key=lambda c: int(c.get("draw", 0))) for p in json.load(open(f))["candidates"]}
    names.append(n); per.append(d)
keys = sorted(set.intersection(*[set(d) for d in per]))
ks = [len(next(iter(d.values()))) for d in per]
out = {"models": names, "k": ks, "candidates": []}
for k in keys:
    cs = []
    for mi, d in enumerate(per):
        assert len(d[k]) == ks[mi], (names[mi], k, len(d[k]))
        for j, c in enumerate(d[k]):
            cs.append({"draw": len(cs), "model": names[mi], "mdraw": j, "code": c.get("code") or "",
                       "exec": bool(c.get("exec")), "iou": float(c.get("iou") or 0.0)})
    out["candidates"].append({"key": k, "cands": cs})
out["metrics"] = {"k": sum(ks)}
json.dump(out, open(a.out, "w"))
print(f"{len(keys)} parts x {sum(ks)} candidates ({dict(zip(names, ks))}) -> {a.out}")
