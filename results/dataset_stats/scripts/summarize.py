"""Aggregate out/static_*.jsonl + out/exec_results.jsonl into out/tables.md, out/summary.json and
out/brep_parts.csv. Light CPU (a minute over ~700k rows) but run it via the sbatch / cpu_run anyway.
"""
from __future__ import annotations

import csv
import glob
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from code_ast import CAT, FEATURE_CATS  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "out")


def q(xs, p):
    xs = sorted(xs)
    if not xs:
        return float("nan")
    k = (len(xs) - 1) * p
    f, c = math.floor(k), math.ceil(k)
    return xs[f] if f == c else xs[f] + (xs[c] - xs[f]) * (k - f)


def desc(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    if not xs:
        return {"n": 0}
    return {"n": len(xs), "mean": statistics.fmean(xs), "median": q(xs, 0.5), "p10": q(xs, 0.1),
            "p90": q(xs, 0.9), "max": max(xs), "min": min(xs)}


def fmt(d, nd=1):
    if not d or d.get("n", 0) == 0:
        return "—"
    f = lambda v: f"{v:.{nd}f}" if isinstance(v, float) and abs(v) < 1e5 else f"{v:,.0f}" if isinstance(v, (int, float)) else str(v)
    return f"{f(d['mean'])} / {f(d['median'])} / {f(d['p10'])}–{f(d['p90'])} / {f(d['max'])}"


def load(ds):
    p = f"{OUT}/static_{ds}.jsonl"
    if not os.path.exists(p):
        return []
    return [json.loads(l) for l in open(p)]


DYN_FEATURE_KEYS = {
    "bool_add": ["bool3d_add", "builder_add"], "bool_subtract": ["bool3d_subtract", "builder_subtract"],
    "bool_intersect": ["bool3d_intersect", "builder_intersect"],
}
MODIFIERS = CAT["fillet"] + CAT["chamfer"] + CAT["shell_offset"] + CAT["mirror"] + CAT["split_section"]


def dyn_summary(dyn):
    g = lambda ks: sum(dyn.get(k, 0) for k in ks)
    booleans = g(sum(DYN_FEATURE_KEYS.values(), []))
    out = {
        "exec_ops": sum(v for k, v in dyn.items() if not k.startswith("inst_")),
        "solid_features": 1 + booleans + g(MODIFIERS),
        "booleans3d": booleans,
        "bool_add": g(DYN_FEATURE_KEYS["bool_add"]), "bool_subtract": g(DYN_FEATURE_KEYS["bool_subtract"]),
        "bool_intersect": g(DYN_FEATURE_KEYS["bool_intersect"]),
        "bool2d": g(["bool2d_add", "bool2d_subtract", "bool2d_intersect"]),
        "solid_prim_inst": g(["inst_" + n for n in CAT["solid_prim"]]),
        "hole_inst": g(["inst_" + n for n in CAT["hole"]]),
        "sketch_prim_inst": g(["inst_" + n for n in CAT["sketch_prim"]]),
        "curve_prim": g(CAT["curve_prim"]),
        "extrude": g(CAT["extrude"]), "revolve": g(CAT["revolve"]), "loft": g(CAT["loft"]),
        "sweep": g(CAT["sweep"]), "fillet": g(CAT["fillet"]), "chamfer": g(CAT["chamfer"]),
        "shell_offset": g(CAT["shell_offset"]), "mirror": g(CAT["mirror"]),
        "split_section": g(CAT["split_section"]), "pattern": g(CAT["pattern"]),
    }
    return out


FTYPES = ["plane", "cylinder", "cone", "torus", "sphere", "bspline", "revolution", "extrusion", "offset", "bezier", "other"]


def brep_row(b):
    ft = b.get("face_types", {})
    F = max(1, b["faces"])
    r = {k: b.get(k) for k in ("solids", "shells", "faces", "edges", "vertices", "genus", "inner_loops",
                               "concave_cyl_faces", "volume", "area", "fill", "aspect", "max_dim")}
    r["bbox_min"], r["bbox_mid"], r["bbox_max"] = b["bbox"]
    for t in FTYPES:
        r[f"ft_{t}"] = ft.get(t, 0)
    r["analytic_only"] = all(k in ("plane", "cylinder", "cone", "torus", "sphere") for k in ft)
    r["non_planar_frac"] = 1 - ft.get("plane", 0) / F
    r["edge_bspline"] = b.get("edge_types", {}).get("bspline", 0)
    r["thin"] = (b["bbox"][0] / b["bbox"][2]) if b["bbox"][2] > 0 else None
    return r


def main():
    lines = []
    P = lines.append
    summary = {}
    meta = json.load(open(f"{OUT}/collect_meta.json")) if os.path.exists(f"{OUT}/collect_meta.json") else {}

    # ------------------------------------------------------------------ static code tables
    code_sets = [("plain", "Plain GT tier (tars_v14_dw423, e55 filter)", lambda r: r.get("in_tier")),
                 ("plain", "Plain GT, all rows (incl. exec-bad / eval / holdout)", None),
                 ("reasoning", "Reasoning tier (certified Kimi-K3 traces + GT code)", None),
                 ("rft_synth", "RFT tier, synthetic (own accepted programs)", None),
                 ("rft_real", "RFT tier, real CADBench parts (own accepted programs)", None),
                 ("abc_gt", "ABC GT-code tier", None),
                 ("eval_synth", "Synthetic eval pool (1,027) GT code", None),
                 ("repair_fam", "Repair tier, synthetic families (target program)", None),
                 ("repair_real", "Repair tier, real parts (target program)", None)]
    preds = sorted({os.path.basename(p)[7:-6] for p in glob.glob(f"{OUT}/static_pred_*.jsonl")})
    code_sets += [(p, f"Prediction {p[5:]}", None) for p in preds]
    cache = {}
    P("## Code statistics (static, AST)\n")
    P("Cells: mean / median / p10–p90 / max. Tokens = Qwen3.8-27B tokenizer. SLOC = non-blank, non-comment lines.\n")
    P("| set | n | tokens | SLOC | build123d calls | feature ops (static) | numeric params | for-loops | think tokens |")
    P("|---|---|---|---|---|---|---|---|---|")
    opshare_rows = []
    for ds, label, filt in code_sets:
        if ds not in cache:
            cache[ds] = load(ds)
        rows = [r for r in cache[ds] if r.get("parse_ok") is not None and (filt is None or filt(r))]
        if not rows:
            continue
        rows_ok = [r for r in rows if r.get("parse_ok")]
        th = [r["think"]["tokens"] for r in rows if r.get("think") and r["think"]["tokens"]]
        s = {"n": len(rows), "parse_fail": len(rows) - len(rows_ok),
             "tokens": desc([r["tokens"] for r in rows]), "sloc": desc([r["sloc"] for r in rows]),
             "b3d_calls": desc([r["b3d_calls"] for r in rows_ok]),
             "feature_ops_static": desc([r["feature_ops_static"] for r in rows_ok]),
             "num_params": desc([r["num_params"] for r in rows_ok]),
             "n_for": desc([r["n_for"] for r in rows_ok]),
             "think_tokens": desc(th), "think_steps": desc([r["think"]["steps"] for r in rows if r.get("think") and r["think"]["tokens"]]),
             "style": {k: sum(r["style"] == k for r in rows_ok) / max(1, len(rows_ok)) for k in ("builder", "hybrid", "algebra")},
             "uses_cat": {c: sum(1 for r in rows_ok if r["cats"].get(c, 0) > 0) / max(1, len(rows_ok)) for c in CAT},
             "mean_cat": {c: statistics.fmean(r["cats"].get(c, 0) for r in rows_ok) for c in CAT},
             "uses_bool": sum(1 for r in rows_ok if sum(r["bool_static"].values()) + r["cats"]["bool_method"] > 0) / max(1, len(rows_ok)),
             "n_op_types": desc([len(r["op_types_static"]) for r in rows_ok]),
             "uses_loop_or_comp": sum(1 for r in rows_ok if r["n_for"] + r["n_comp"] + r["n_while"] > 0) / max(1, len(rows_ok)),
             "uses_def": sum(1 for r in rows_ok if r["n_def"] > 0) / max(1, len(rows_ok)),
             }
        calls = {}
        for r in rows_ok:
            for k, v in r.get("calls", {}).items():
                calls[k] = calls.get(k, 0) + 1
        s["top_calls_doc_share"] = sorted(((k, v / len(rows_ok)) for k, v in calls.items()), key=lambda x: -x[1])[:25]
        if ds.startswith("repair"):
            s["start_tokens"] = desc([r.get("start_tokens") for r in rows])
            s["diff_ratio"] = desc([r.get("diff_ratio") for r in rows])
            s["diff_lines_changed"] = desc([(r.get("diff_added") or 0) + (r.get("diff_removed") or 0) for r in rows])
            s["cand_iou"] = desc([r.get("cand_iou") for r in rows])
            s["target_iou"] = desc([r.get("iou") for r in rows])
            s["parts"] = len({r.get("src_key") or r["id"].split("__r")[0] for r in rows})
        if ds in ("rft_synth", "rft_real"):
            s["parts"] = len({r["id"].split("-s")[0].rsplit("_v", 1)[0] for r in rows})
            s["accept_iou"] = desc([r.get("iou") for r in rows])
        key = ds + ("" if filt is None else "_tier")
        summary.setdefault("code", {})[key] = s
        P(f"| {label} | {len(rows):,} | {fmt(s['tokens'], 0)} | {fmt(s['sloc'], 0)} | {fmt(s['b3d_calls'])} | "
          f"{fmt(s['feature_ops_static'])} | {fmt(s['num_params'])} | {fmt(s['n_for'])} | {fmt(s['think_tokens'], 0)} |")
        opshare_rows.append((label, s))
    P("\n### Share of programs using each operation category (static)\n")
    cats = ["solid_prim", "extrude", "revolve", "loft", "sweep", "hole", "fillet", "chamfer", "shell_offset",
            "mirror", "split_section", "sketch_prim", "curve_prim", "pattern", "transform"]
    P("| set | " + " | ".join(cats) + " | boolean | loop/comp | API style builder/hybrid/algebra |")
    P("|---|" + "---|" * (len(cats) + 3))
    for label, s in opshare_rows:
        P(f"| {label} | " + " | ".join(f"{100 * s['uses_cat'][c]:.0f}%" for c in cats)
          + f" | {100 * s['uses_bool']:.0f}% | {100 * s['uses_loop_or_comp']:.0f}% | "
          + "/".join(f"{100 * s['style'][k]:.0f}" for k in ("builder", "hybrid", "algebra")) + " |")

    # ------------------------------------------------------------------ exec / brep
    res = {}
    if os.path.exists(f"{OUT}/exec_results.jsonl"):
        for l in open(f"{OUT}/exec_results.jsonl"):
            r = json.loads(l)
            res[r["id"]] = r
    by = {}
    for rid, r in res.items():
        by.setdefault(r.get("ds", rid.split("/")[0]), []).append(r)
    P("\n## Execution + B-rep (sampled / full sets)\n")
    P("Cells: mean / median / p10–p90 / max over parts that executed (code) or loaded (STEP).\n")
    P("| set | tasks | ok | faces | edges | genus | concave cyl. faces | max dim mm | fill | aspect |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    order = ["plain", "reasoning", "rft_synth", "rft_real", "abc_gt", "eval_synth", "eval_synth_step",
             "real144", "bench_b"] + sorted(k for k in by if k.startswith("pred_"))
    csv_rows = []
    brep_sum = {}
    for ds in order:
        rs = by.get(ds, [])
        if not rs:
            continue
        ok = [r for r in rs if r.get("ok")]
        br = [brep_row(r["brep"]) for r in ok]
        for r, b in zip(ok, br):
            csv_rows.append({"ds": ds, "id": r["id"].split("/", 1)[1], **b,
                             **({f"dyn_{k}": v for k, v in dyn_summary(r["dyn"]).items()} if "dyn" in r else {})})
        s = {"tasks": len(rs), "ok": len(ok),
             "fail_stages": {st: sum(1 for r in rs if not r.get("ok") and r.get("stage") == st) for st in ("exec", "nostep", "brep", "timeout", "crash", "worker")}}
        for k in ("faces", "edges", "vertices", "genus", "inner_loops", "concave_cyl_faces", "max_dim", "fill", "aspect", "volume", "thin", "solids"):
            s[k] = desc([b[k] for b in br])
        F = sum(b["faces"] for b in br) or 1
        s["face_type_share"] = {t: sum(b[f"ft_{t}"] for b in br) / F for t in FTYPES}
        s["has_face_type"] = {t: sum(1 for b in br if b[f"ft_{t}"] > 0) / max(1, len(br)) for t in FTYPES}
        s["analytic_only"] = sum(b["analytic_only"] for b in br) / max(1, len(br))
        s["multi_solid"] = sum(1 for b in br if (b["solids"] or 0) > 1) / max(1, len(br))
        s["faces_le80"] = sum(1 for b in br if b["faces"] <= 80) / max(1, len(br))
        s["genus0"] = sum(1 for b in br if b["genus"] == 0) / max(1, len(br))
        dy = [dyn_summary(r["dyn"]) for r in ok if "dyn" in r]
        if dy:
            s["dyn"] = {k: desc([d[k] for d in dy]) for k in dy[0]}
            s["dyn_uses"] = {k: sum(1 for d in dy if d[k] > 0) / len(dy) for k in dy[0]}
        if ds in ("bench_b", "real144"):
            for fam in ("F", "A"):
                fb = [b for r, b in zip(ok, br) if r["id"].split("/", 1)[1].startswith(fam + "_")]
                s[f"faces_{fam}"] = desc([b["faces"] for b in fb])
                s[f"genus_{fam}"] = desc([b["genus"] for b in fb])
        brep_sum[ds] = s
        P(f"| {ds} | {len(rs):,} | {len(ok):,} | {fmt(s['faces'])} | {fmt(s['edges'])} | {fmt(s['genus'])} | "
          f"{fmt(s['concave_cyl_faces'])} | {fmt(s['max_dim'])} | {fmt(s['fill'], 2)} | {fmt(s['aspect'], 1)} |")
    summary["brep"] = brep_sum
    P("\n### Face-type mix (share of all faces; in parentheses: share of parts with ≥1 such face)\n")
    shown = ["plane", "cylinder", "cone", "torus", "sphere", "bspline", "revolution", "extrusion"]
    P("| set | " + " | ".join(shown) + " | analytic-only parts | genus 0 parts | multi-solid |")
    P("|---|" + "---|" * (len(shown) + 3))
    for ds, s in brep_sum.items():
        P(f"| {ds} | " + " | ".join(f"{100 * s['face_type_share'][t]:.1f}% ({100 * s['has_face_type'][t]:.0f}%)" for t in shown)
          + f" | {100 * s['analytic_only']:.0f}% | {100 * s['genus0']:.0f}% | {100 * s['multi_solid']:.1f}% |")
    P("\n### Executed operations (dynamic counts; code sets only)\n")
    dk = ["exec_ops", "solid_features", "booleans3d", "bool_subtract", "bool_add", "solid_prim_inst", "hole_inst",
          "extrude", "fillet", "chamfer"]
    P("| set | " + " | ".join(dk) + " |")
    P("|---|" + "---|" * len(dk))
    for ds, s in brep_sum.items():
        if "dyn" in s:
            P(f"| {ds} | " + " | ".join(f"{s['dyn'][k]['mean']:.1f} / {s['dyn'][k]['median']:.0f} / {s['dyn'][k]['p90']:.0f}" for k in dk) + " |")
    P("\nCells: mean / median / p90.\n")
    P("| set (share of programs executing ≥1) | " + " | ".join(["revolve", "loft", "sweep", "hole_inst", "fillet", "chamfer", "shell_offset", "mirror", "pattern", "bool_intersect", "bool2d"]) + " |")
    P("|---|" + "---|" * 11)
    for ds, s in brep_sum.items():
        if "dyn_uses" in s:
            P(f"| {ds} | " + " | ".join(f"{100 * s['dyn_uses'][k]:.1f}%" for k in ["revolve", "loft", "sweep", "hole_inst", "fillet", "chamfer", "shell_offset", "mirror", "pattern", "bool_intersect", "bool2d"]) + " |")

    # ------------------------------------------------------------------ drawings
    P("\n## Drawing annotations (draftwright sidecars)\n")
    P("| set | sheets | annotations | dimensions | leaders | hole callouts | underdetermined sheets | first-angle |")
    P("|---|---|---|---|---|---|---|---|")
    dsum = {}
    for ds, label, filt in [("plain", "plain tier", lambda r: r.get("in_tier")), ("eval_synth", "eval_synth", None),
                            ("real144", "real144", None), ("bench_b", "bench_b", None)]:
        rows = [r for r in (cache.get(ds) or load(ds)) if (filt is None or filt(r)) and r.get("drawing")]
        if not rows:
            continue
        d = [r["drawing"] for r in rows]
        s = {"n": len(d), "n_ann": desc([x["n_ann"] for x in d]), "n_dim": desc([x["n_dim"] for x in d]),
             "n_leader": desc([x["n_leader"] for x in d]), "n_hole_callout": desc([x["n_hole_callout"] for x in d]),
             "underdetermined": sum(1 for x in d if x["n_unplaced"] > 0) / len(d),
             "first_angle": sum(1 for x in d if x["projection"] == "first") / len(d)}
        dsum[ds] = s
        P(f"| {label} | {len(d):,} | {fmt(s['n_ann'])} | {fmt(s['n_dim'])} | {fmt(s['n_leader'])} | {fmt(s['n_hole_callout'])} | "
          f"{100 * s['underdetermined']:.0f}% | {100 * s['first_angle']:.0f}% |")
    summary["drawing"] = dsum

    # ------------------------------------------------------------------ prediction vs GT, IoU vs complexity
    P("\n## Generated vs ground truth (paired by part)\n")
    pv = {}
    gt_faces = {}
    for ds in ("eval_synth_step", "bench_b", "real144"):
        for r in by.get(ds, []):
            if r.get("ok"):
                gt_faces[(ds, r["id"].split("/", 1)[1])] = r["brep"]
    bench_gt = {"full": "eval_synth_step", "benchb": "bench_b"}
    gt_code = {r["id"]: r for r in cache.get("eval_synth") or load("eval_synth")}
    P("| model / bench | pairs | pred faces | GT faces | pred/GT faces (median ratio) | pred tokens | GT tokens | pred genus | GT genus |")
    P("|---|---|---|---|---|---|---|---|---|")
    for ds in sorted(k for k in by if k.startswith("pred_") and k.endswith("_vote")):
        model, bench = ds.split("_")[1], ds.split("_")[2]
        g = bench_gt.get(bench)
        if not g:
            continue
        pairs = []
        stat_rows = {r["id"]: r for r in (cache.get(ds) or load(ds))}
        for r in by[ds]:
            k = r["id"].split("/", 1)[1]
            if r.get("ok") and (g, k) in gt_faces:
                pairs.append((r["brep"], gt_faces[(g, k)], stat_rows.get(k), gt_code.get(k)))
        if not pairs:
            continue
        ratio = [p["faces"] / max(1, gg["faces"]) for p, gg, _, _ in pairs]
        s = {"pairs": len(pairs), "pred_faces": desc([p["faces"] for p, _, _, _ in pairs]),
             "gt_faces": desc([gg["faces"] for _, gg, _, _ in pairs]), "face_ratio": desc(ratio),
             "pred_tokens": desc([sr["tokens"] for _, _, sr, _ in pairs if sr]),
             "gt_tokens": desc([gc["tokens"] for _, _, _, gc in pairs if gc]),
             "pred_genus": desc([p["genus"] for p, _, _, _ in pairs]), "gt_genus": desc([gg["genus"] for _, gg, _, _ in pairs]),
             "frac_fewer_faces": sum(1 for x in ratio if x < 1) / len(ratio),
             "frac_exact_faces": sum(1 for p, gg, _, _ in pairs if p["faces"] == gg["faces"]) / len(pairs),
             "frac_genus_match": sum(1 for p, gg, _, _ in pairs if p["genus"] == gg["genus"]) / len(pairs)}
        pv[ds] = s
        P(f"| {model} {bench} | {len(pairs)} | {fmt(s['pred_faces'])} | {fmt(s['gt_faces'])} | {s['face_ratio']['median']:.2f} | "
          f"{fmt(s['pred_tokens'], 0)} | {fmt(s['gt_tokens'], 0)} | {fmt(s['pred_genus'])} | {fmt(s['gt_genus'])} |")
    summary["pred_vs_gt"] = pv

    # IoU by GT face-count quartile (vote pick IoU, e55 and glimmer)
    P("\n### Vote-pick IoU by GT face-count bin\n")
    P("| model / bench | " + " | ".join(["faces ≤10", "11–20", "21–40", "41–80", ">80"]) + " |")
    P("|---|---|---|---|---|---|")
    bins = [(0, 10), (11, 20), (21, 40), (41, 80), (81, 10 ** 9)]
    iou_bins = {}
    for model in ("e55", "glimmer"):
        for bench, g in (("full", "eval_synth_step"), ("benchb", "bench_b"), ("real", "real144")):
            # vote IoU per part = consistency pick IoU (from the pred static rows; non-matched parts -> 0)
            rows0 = cache.get(f"pred_{model}_{bench}_d0") or load(f"pred_{model}_{bench}_d0")
            vote = {r["id"]: r.get("iou") or 0.0 for r in (cache.get(f"pred_{model}_{bench}_vote") or load(f"pred_{model}_{bench}_vote"))}
            cells = []
            row = {}
            for lo, hi in bins:
                xs = [vote.get(r["id"], 0.0) for r in rows0 if (g, r["id"]) in gt_faces and lo <= gt_faces[(g, r["id"])]["faces"] <= hi]
                row[f"{lo}-{hi}"] = {"n": len(xs), "mean_iou": statistics.fmean(xs) if xs else None}
                cells.append(f"{statistics.fmean(xs):.3f} (n={len(xs)})" if xs else "—")
            iou_bins[f"{model}_{bench}"] = row
            P(f"| {model} {bench} | " + " | ".join(cells) + " |")
    summary["iou_by_faces"] = iou_bins

    with open(f"{OUT}/tables.md", "w") as f:
        f.write("\n".join(lines) + "\n")
    json.dump({"collect_meta": meta, **summary}, open(f"{OUT}/summary.json", "w"), indent=1, default=str)
    if csv_rows:
        keys = sorted({k for r in csv_rows for k in r}, key=lambda k: (k not in ("ds", "id"), k))
        with open(f"{OUT}/brep_parts.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys)
            w.writeheader()
            w.writerows(csv_rows)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
