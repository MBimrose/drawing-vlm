#!/usr/bin/env python
"""Turn the merged best-of-8 on the real-geometry corpus into rft_v1-format files:
  <out>/accepted-000.jsonl : every candidate with exec and iou >= 0.8 (several per key allowed)
                             {key, iou, ok, think, code, sample}
  <out>/scored-000.jsonl   : every candidate that has code {key, iou, ok, exec, think, code, sample}
  <out>/png/<key>.png      : the sheet of every ACCEPTED key
  <out>/stats.json         : per-family parts / exec rate / yield@0.8 / @0.9 / oracle@8
  python write_rft_real.py --bo8 <merged.json> --png-dir <render/png> --manifest <manifest.json> --out <dir>
"""
import argparse, json, glob, os, shutil, collections, statistics as st
ap = argparse.ArgumentParser(); ap.add_argument("--bo8", required=True); ap.add_argument("--png-dir", required=True)
ap.add_argument("--manifest", required=True); ap.add_argument("--out", required=True); ap.add_argument("--sidecar", default="")
a = ap.parse_args()
d = json.load(open(a.bo8)); man = json.load(open(a.manifest))["parts"]
side = json.load(open(a.sidecar)) if a.sidecar else {}
unpl = {k.rsplit("_v", 1)[0]: bool(v.get("dims_unplaced")) for k, v in side.items()}
os.makedirs(os.path.join(a.out, "png"), exist_ok=True)
acc = open(os.path.join(a.out, "accepted-000.jsonl"), "w"); sc = open(os.path.join(a.out, "scored-000.jsonl"), "w")
per = collections.defaultdict(lambda: collections.Counter()); orc = collections.defaultdict(list); acc_keys = set(); n_acc = n_sc = 0
for p in d["candidates"]:
    key = p["key"]; fam = man.get(key, {}).get("family", key.split("_", 1)[0]); per[fam]["parts"] += 1
    best = 0.0; any8 = any9 = False
    for c in sorted(p["cands"], key=lambda c: c["draw"]):
        if not c.get("code"): continue
        per[fam]["cands"] += 1; ex = bool(c.get("exec")); iou = float(c.get("iou") or 0.0)
        per[fam]["exec"] += ex
        rec = {"key": key, "iou": iou, "ok": bool(ex and iou >= 0.8), "exec": ex, "think": c.get("think", ""), "code": c["code"], "sample": c["draw"]}
        sc.write(json.dumps(rec) + "\n"); n_sc += 1
        if ex:
            best = max(best, iou)
            if iou >= 0.8:
                acc.write(json.dumps({k: rec[k] for k in ("key", "iou", "ok", "think", "code", "sample")}) + "\n"); n_acc += 1; any8 = True; acc_keys.add(key)
            if iou >= 0.9: any9 = True
    orc[fam].append(best); per[fam]["keys_ge80"] += any8; per[fam]["keys_ge90"] += any9
acc.close(); sc.close()
for key in sorted(acc_keys):
    pngs = sorted(glob.glob(os.path.join(a.png_dir, f"{key}_v*.png")))
    if pngs: shutil.copy(pngs[0], os.path.join(a.out, "png", f"{key}.png"))
stats = {}
for fam in sorted(per):
    c = per[fam]; o = orc[fam]
    stats[fam] = dict(parts=c["parts"], cands=c["cands"], exec_rate=round(c["exec"] / max(c["cands"], 1), 3),
                      keys_ge80=c["keys_ge80"], yield80=round(c["keys_ge80"] / c["parts"], 3), keys_ge90=c["keys_ge90"], yield90=round(c["keys_ge90"] / c["parts"], 3),
                      oracle8_mean=round(st.mean(o), 3), oracle8_ge85=round(sum(x >= 0.85 for x in o) / len(o), 3),
                      underdetermined=sum(1 for p in d["candidates"] if man.get(p["key"], {}).get("family") == fam and unpl.get(p["key"])))
stats["accepted_records"] = n_acc; stats["scored_records"] = n_sc; stats["accepted_keys"] = len(acc_keys)
json.dump(stats, open(os.path.join(a.out, "stats.json"), "w"), indent=1); print(json.dumps(stats, indent=1))
