"""H2: does the model read the sheet's dimensions? Dimension recall = share of distinct printed values that
appear in the candidate program as a literal (value, value/2 or 2x value, within 1% or 0.05 mm), real vs synthetic.
    python fp_h2_dimrecall.py <bo json> <renderers.json> <label>"""
import json, re, sys, numpy as np
NUM = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)")
def sheet_vals(ann):
    vals = set()
    for a in ann.values():
        lab = str(a.get("label", ""))
        lab = re.sub(r"^\s*\d+\s*[x×]\s*", "", lab)          # drop "4× " multiplicity
        lab = re.sub(r"\(\d+\s*[x×]\s*\d+\)", "", lab)       # drop "(4x5)" pattern counts
        for x in NUM.findall(lab):
            v = float(x)
            if v > 0: vals.add(round(v, 3))
    return vals
def code_vals(code):
    vs = set()
    for x in NUM.findall(code or ""):
        try: vs.add(float(x))
        except ValueError: pass
    return vs
def hit(v, cv):
    for t in (v, v / 2, v * 2):
        if any(abs(c - t) <= max(0.05, 0.01 * t) for c in cv): return True
    return False
if __name__ == "__main__":
    bo = json.load(open(sys.argv[1]))["candidates"]; rend = json.load(open(sys.argv[2]))
    side = {k.rsplit("_v", 1)[0]: v for k, v in rend.items() if v}
    rows = []
    for p in bo:
        s = side.get(p["key"]) or side.get(p["key"].rsplit("_v", 1)[0])
        if not s: continue
        sv = sheet_vals(s.get("annotations") or {})
        if not sv: continue
        for c in p["cands"]:
            if not c.get("code"): continue
            cv = code_vals(c["code"])
            rows.append((p["key"][0], len(sv), np.mean([hit(v, cv) for v in sv]), float(c.get("iou") or 0)))
    R = np.array([(r[1], r[2], r[3]) for r in rows]); fam = np.array([r[0] for r in rows])
    print(f"[{sys.argv[3]}] cands {len(R)} parts {len(set(p['key'] for p in bo))}: dims on sheet median {np.median(R[:,0]):.0f}, "
          f"dimension recall mean {R[:,1].mean():.3f}")
    for lo, hi in ((0, .5), (.5, .85), (.85, 1.01)):
        m = (R[:, 2] >= lo) & (R[:, 2] < hi)
        if m.any(): print(f"   IoU [{lo},{hi}) n={m.sum():5d} recall {R[m,1].mean():.3f}")
    for lo, hi in ((0, 6), (6, 12), (12, 99)):
        m = (R[:, 0] >= lo) & (R[:, 0] < hi)
        if m.any(): print(f"   sheet dims [{lo},{hi}) n={m.sum():5d} recall {R[m,1].mean():.3f}  IoU {R[m,2].mean():.3f}")
    for F in sorted(set(fam)):
        m = fam == F
        if F in "AF": print(f"   family {F}: recall {R[m,1].mean():.3f}  IoU {R[m,2].mean():.3f}")
