"""Small follow-ups on out/brep_parts.csv + out/static_pred_*.jsonl (seconds; login-safe):
per-part mean face-type shares, family splits of the real benches, paired pred-vs-GT shape
descriptors on bench B / synthetic pool, IoU vs fill. -> out/extra.json, out/extra.md"""
import csv
import json
import os
import statistics as st

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "out")
rows = list(csv.DictReader(open(f"{OUT}/brep_parts.csv")))
for r in rows:
    for k, v in list(r.items()):
        if k not in ("ds", "id"):
            try:
                r[k] = float(v)
            except (TypeError, ValueError):
                r[k] = None if v in ("", None) else (v == "True")
by = {}
for r in rows:
    by.setdefault(r["ds"], {})[r["id"]] = r


def med(xs):
    xs = [x for x in xs if x is not None]
    return st.median(xs) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.fmean(xs) if xs else None


out, md = {}, []
md.append("## Per-part mean face-type shares (each part weighted equally)\n")
md.append("| set | n | plane | cylinder | cone | torus | sphere | bspline | parts with a hole-like concave cylinder | median fill | median aspect | median thin (min/max dim) |")
md.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
sets = [("plain", None), ("eval_synth_step", None), ("real144", None), ("real144", "F"), ("real144", "A"),
        ("bench_b", None), ("bench_b", "F"), ("bench_b", "A"), ("pred_e55_benchb_vote", None), ("pred_e55_full_vote", None)]
for ds, fam in sets:
    rs = [r for k, r in by.get(ds, {}).items() if fam is None or k.startswith(fam + "_")]
    if not rs:
        continue
    sh = lambda t: mean([r[f"ft_{t}"] / r["faces"] for r in rs if r["faces"]])
    s = {t: sh(t) for t in ("plane", "cylinder", "cone", "torus", "sphere", "bspline")}
    s.update({"n": len(rs), "has_concave_cyl": mean([1.0 if r["concave_cyl_faces"] > 0 else 0.0 for r in rs]),
              "fill_med": med([r["fill"] for r in rs]), "aspect_med": med([r["aspect"] for r in rs]),
              "thin_med": med([r["thin"] for r in rs]), "faces_med": med([r["faces"] for r in rs]),
              "genus_mean": mean([r["genus"] for r in rs])})
    name = ds + (f" [{fam}]" if fam else "")
    out[name] = s
    md.append(f"| {name} | {len(rs)} | " + " | ".join(f"{100 * s[t]:.1f}%" for t in ("plane", "cylinder", "cone", "torus", "sphere", "bspline"))
              + f" | {100 * s['has_concave_cyl']:.0f}% | {s['fill_med']:.2f} | {s['aspect_med']:.1f} | {s['thin_med']:.2f} |")

# paired pred vs GT
md.append("\n## Paired vote pick vs GT (same part)\n")
md.append("| model / bench | pairs | median fill pred / GT | pred fuller than GT | median faces pred / GT | pred fewer faces | genus exact | pred multi-solid | mean vote IoU |")
md.append("|---|---|---|---|---|---|---|---|---|")
pairs_out = {}
for model in ("e55", "glimmer"):
    for bench, g in (("benchb", "bench_b"), ("full", "eval_synth_step")):
        ds = f"pred_{model}_{bench}_vote"
        st_rows = {json.loads(l)["id"]: json.loads(l) for l in open(f"{OUT}/static_{ds}.jsonl")}
        P = [(by[ds][k], by[g][k], st_rows.get(k, {}).get("iou")) for k in by.get(ds, {}) if k in by.get(g, {})]
        if not P:
            continue
        s = {"pairs": len(P), "fill_pred_med": med([p["fill"] for p, _, _ in P]), "fill_gt_med": med([q["fill"] for _, q, _ in P]),
             "pred_fuller": mean([1.0 if p["fill"] > q["fill"] + 0.02 else 0.0 for p, q, _ in P]),
             "faces_pred_med": med([p["faces"] for p, _, _ in P]), "faces_gt_med": med([q["faces"] for _, q, _ in P]),
             "pred_fewer_faces": mean([1.0 if p["faces"] < q["faces"] else 0.0 for p, q, _ in P]),
             "genus_exact": mean([1.0 if p["genus"] == q["genus"] else 0.0 for p, q, _ in P]),
             "pred_multi_solid": mean([1.0 if p["solids"] > 1 else 0.0 for p, _, _ in P]),
             "iou_mean": mean([i for _, _, i in P])}
        # IoU by GT fill tercile
        fills = sorted(q["fill"] for _, q, _ in P)
        t1, t2 = fills[len(fills) // 3], fills[2 * len(fills) // 3]
        s["iou_by_gt_fill_tercile"] = {
            f"<= {t1:.2f}": mean([i for _, q, i in P if q["fill"] <= t1]),
            f"{t1:.2f}-{t2:.2f}": mean([i for _, q, i in P if t1 < q["fill"] <= t2]),
            f"> {t2:.2f}": mean([i for _, q, i in P if q["fill"] > t2])}
        pairs_out[f"{model}_{bench}"] = s
        md.append(f"| {model} {bench} | {len(P)} | {s['fill_pred_med']:.2f} / {s['fill_gt_med']:.2f} | {100 * s['pred_fuller']:.0f}% | "
                  f"{s['faces_pred_med']:.0f} / {s['faces_gt_med']:.0f} | {100 * s['pred_fewer_faces']:.0f}% | {100 * s['genus_exact']:.0f}% | "
                  f"{100 * s['pred_multi_solid']:.1f}% | {s['iou_mean']:.3f} |")
md.append("\n### Vote IoU by GT fill tercile\n")
for k, s in pairs_out.items():
    md.append(f"- {k}: " + ", ".join(f"fill {b}: {v:.3f}" for b, v in s["iou_by_gt_fill_tercile"].items()))
out["pairs"] = pairs_out
json.dump(out, open(f"{OUT}/extra.json", "w"), indent=1)
open(f"{OUT}/extra.md", "w").write("\n".join(md) + "\n")
print("\n".join(md))
