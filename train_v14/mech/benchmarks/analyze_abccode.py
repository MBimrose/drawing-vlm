#!/usr/bin/env python
"""Side-by-side best-of-8 summary of one model on the ABC ground-truth-code corpus rendered by both
renderers (draftwright 0.4.0+patch "dw400" = corpora 1-3 / training sheets, 0.4.23+patch "dw423"),
from the consistency_rerank outputs, sliced by determinacy (each rendering's own sidecar), by source
version group and by whether the GT program was polyline-cleaned.

  python analyze_abccode.py --dw400 <..._dw400_consistency.json> --dw423 <..._consistency.json> \
      --corpus data/rft_corpus_abccode --side-dw400 <dw400 renderers.json> --side-dw423 <dw423 renderers.json>
"""
import argparse, json, os, statistics as st

POL = ["first_exec", "consistency", "oracle"]
ap = argparse.ArgumentParser()
ap.add_argument("--dw400", required=True); ap.add_argument("--dw423", required=True); ap.add_argument("--corpus", required=True)
ap.add_argument("--side-dw400", required=True); ap.add_argument("--side-dw423", required=True)
ap.add_argument("--threshold", type=float, default=0.8)
a = ap.parse_args()
gt = {json.loads(l)["key"]: json.loads(l) for l in open(os.path.join(a.corpus, "gt_code.jsonl"))}
runs = {n: json.load(open(p))["per_part"] for n, p in (("dw400", a.dw400), ("dw423", a.dw423))}
under = {}
for n, p in (("dw400", a.side_dw400), ("dw423", a.side_dw423)):
    s = json.load(open(p)); under[n] = {k.rsplit("_v", 1)[0]: bool(v.get("dims_unplaced")) for k, v in s.items()}
keys = sorted(set(runs["dw400"]) & set(runs["dw423"]) & set(gt))


def line(name, ks):
    if not ks:
        return
    cells = []
    for n in ("dw400", "dw423"):
        r = runs[n]
        cells.append(" | ".join(f"{st.mean(r[k][p] for k in ks):.3f} / {sum(r[k][p] >= 0.85 for k in ks) / len(ks) * 100:3.0f}%" for p in POL))
    print(f"{name:26s} {len(ks):4d} | {cells[0]} || {cells[1]}")


print(f"e51 best-of-8 on rft_corpus_abccode ({len(keys)} parts scored under both renderings); columns first-exec | vote | oracle, mean / >=0.85")
print(f"{'slice':26s} {'n':>4s} | {'dw400 (0.4.0+patch)':^50s} || {'dw423 (0.4.23+patch)':^50s}")
line("ALL", keys)
for n in ("dw400", "dw423"):
    line(f"  determinate ({n} sidecar)", [k for k in keys if under[n].get(k) is False])
    line(f"  underdet.   ({n} sidecar)", [k for k in keys if under[n].get(k) is True])
line("  ds0b (first harvest)", [k for k in keys if gt[k]["source_version"] == "ds0b"])
line("  v5-v17 (re-exec gated)", [k for k in keys if gt[k]["source_version"].startswith("v") and gt[k]["source_version"] not in ("v1", "v2")])
line("  GT polyline-cleaned", [k for k in keys if gt[k].get("cleaned")])
line("  GT not cleaned", [k for k in keys if not gt[k].get("cleaned")])
t = a.threshold
u4 = {k for k in keys if runs["dw400"][k]["oracle"] < t}; u3 = {k for k in keys if runs["dw423"][k]["oracle"] < t}
print(f"\nunsolved (best-of-8 < {t}): dw400 {len(u4)} ({len(u4)/len(keys)*100:.0f}%), dw423 {len(u3)} ({len(u3)/len(keys)*100:.0f}%), "
      f"both {len(u4 & u3)}, only dw400 {len(u4 - u3)}, only dw423 {len(u3 - u4)}, solved under both {len(keys) - len(u4 | u3)}")
d = [runs["dw423"][k]["oracle"] - runs["dw400"][k]["oracle"] for k in keys]
print(f"per-part oracle delta dw423-dw400: mean {st.mean(d):+.3f} median {st.median(d):+.3f}, better>0.05 {sum(x > 0.05 for x in d)}, worse<-0.05 {sum(x < -0.05 for x in d)}")
print(f"underdetermined sheets: dw400 {sum(1 for k in keys if under['dw400'].get(k))}, dw423 {sum(1 for k in keys if under['dw423'].get(k))}")
print(f"exec>=1 of 8: dw400 {sum(1 for k in keys if runs['dw400'][k]['oracle'] > 0)/len(keys)*100:.0f}%, dw423 {sum(1 for k in keys if runs['dw423'][k]['oracle'] > 0)/len(keys)*100:.0f}%")
