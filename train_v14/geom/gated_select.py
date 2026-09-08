"""Agreement-gated selection on stored best-of-N candidates (CPU, no model).

Inputs: a merged candidates JSON (bestofn_verifier_eval.py / merge_bo_shards.py),
its <name>_consistency.json (consistency_rerank.py: parts[].pair_iou, the
pairwise centered-IoU matrix indexed by candidate position) and a verifier
preds JSON (verifier_select_offline.py's <out>.preds.json:
{key: [[pred, pred_maxvar, p_yes] | null per candidate in draw order]}).

Policies, on the executing candidates of the first K draws (K = --k, default
all draws stored):
  first_exec  first executing candidate (draw order)
  vote        consistency medoid (highest mean pairwise IoU; ties by draw order)
  verifier    argmax verifier prediction
  gate<t>     the vote if the medoid's mean agreement >= t, else the verifier
              argmax  (t = --gates, default 0.85 and 0.7; 0.85 is the served policy)
  oracle      argmax true IoU (ceiling)
The selection arithmetic is identical to verifier_select_offline.select(), so
this reproduces its tables from the cached preds (vote / verifier / agree_gate).

Writes <out> (per-part picks + metrics per slice) and <out minus .json>_summary.txt
in the consistency_rerank style (mean, median, frac >= 0.85, frac >= 0.5), with
determinate / underdetermined / family slices when --split is given.

    python gated_select.py --cands results/ext/bo8_ext_<run>.json \
        --consistency results/ext/bo8_ext_<run>_consistency.json \
        --preds results/ext/vsel_bo8_ext_<run>.json.preds.json \
        --split train_v14/mech/benchmarks/data/ext_bench/split.json \
        --out results/ext/bo8_ext_<run>_gated.json
"""
from __future__ import annotations

import argparse
import json
import os

import numpy as np

DEFAULT_GATES = (0.85, 0.7)


def medoid(idx, mat):
    """Position with the highest mean pairwise IoU to the others (first on ties)."""
    if len(idx) == 1:
        return idx[0], 0.0
    best, best_agree = None, None
    for j in idx:
        agree = float(np.mean([(mat[j][i] or 0.0) for i in idx if i != j]))
        if best_agree is None or agree > best_agree:
            best, best_agree = j, agree
    return best, best_agree


def select_part(cands, mat, K, gates):
    """cands: list in draw order with exec / iou / pred (None if unscored)."""
    cs = cands[:K]
    ex = [j for j, c in enumerate(cs) if c.get("exec") and c.get("pred") is not None]
    names = ["first_exec", "vote", "verifier"] + [f"gate{t}" for t in gates] + ["oracle"]
    if not ex:
        return {"iou": {n: 0.0 for n in names}, "pick": {n: None for n in names},
                "agree": 0.0, "n_exec": 0, "branch": {f"gate{t}": "none" for t in gates}}
    jm, agree = medoid(ex, mat)
    jv = max(ex, key=lambda j: cs[j]["pred"])
    jo = max(ex, key=lambda j: cs[j]["iou"])
    pick = {"first_exec": ex[0], "vote": jm, "verifier": jv, "oracle": jo}
    branch = {}
    for t in gates:
        use_vote = agree >= t
        pick[f"gate{t}"] = jm if use_vote else jv
        branch[f"gate{t}"] = "vote" if use_vote else "verifier"
    return {"iou": {n: cs[pick[n]]["iou"] for n in names}, "pick": pick,
            "agree": agree, "n_exec": len(ex), "branch": branch}


def metrics(vals):
    n = len(vals)
    if n == 0:
        return {"n": 0, "iou_mean": float("nan"), "iou_median": float("nan"),
                "frac_iou85": float("nan"), "frac_iou50": float("nan")}
    s = sorted(vals)
    return {"n": n, "iou_mean": float(sum(vals) / n), "iou_median": float(s[n // 2]),
            "frac_iou85": float(sum(v >= 0.85 for v in vals) / n),
            "frac_iou50": float(sum(v >= 0.5 for v in vals) / n)}


def slice_rows(rows, split):
    slices = {"all": rows}
    if split:
        slices["determinate"] = [r for r in rows if split.get(r["key"], {}).get("underdetermined") is False]
        slices["underdetermined"] = [r for r in rows if split.get(r["key"], {}).get("underdetermined") is True]
        slices["F"] = [r for r in rows if split.get(r["key"], {}).get("family") == "F"]
        slices["A"] = [r for r in rows if split.get(r["key"], {}).get("family") == "A"]
    return {k: v for k, v in slices.items() if v}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cands", required=True)
    ap.add_argument("--consistency", required=True)
    ap.add_argument("--preds", required=True)
    ap.add_argument("--split", default="")
    ap.add_argument("--k", type=int, nargs="*", default=[], help="draw budgets (default: all stored draws)")
    ap.add_argument("--gates", type=float, nargs="+", default=list(DEFAULT_GATES))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.load(open(args.cands))
    parts = data["candidates"]
    for p in parts:
        p["cands"].sort(key=lambda c: c.get("draw", 0))
    cons = {cp["key"]: cp["pair_iou"] for cp in json.load(open(args.consistency))["parts"]}
    preds = json.load(open(args.preds))
    split = json.load(open(args.split)) if args.split else {}
    missing_pred = missing_mat = 0
    for p in parts:
        pr = preds.get(p["key"])
        if pr is None:
            missing_pred += 1
            pr = [None] * len(p["cands"])
        assert len(pr) == len(p["cands"]), f"{p['key']}: {len(pr)} preds vs {len(p['cands'])} candidates"
        for c, v in zip(p["cands"], pr):
            c["pred"] = None if v is None else float(v[0])
        if cons.get(p["key"]) is None:
            missing_mat += 1
            k = len(p["cands"])
            cons[p["key"]] = [[None] * k for _ in range(k)]
    if missing_pred or missing_mat:
        print(f"[gated] WARNING: {missing_pred} parts without preds, {missing_mat} without pair_iou "
              f"(scored as unverified / zero agreement)", flush=True)
    ks = args.k or [max(len(p["cands"]) for p in parts)]
    names = ["first_exec", "vote", "verifier"] + [f"gate{t}" for t in args.gates] + ["oracle"]

    result = {"cands": args.cands, "consistency": args.consistency, "preds": args.preds,
              "gates": args.gates, "n_parts": len(parts), "policies": names, "by_k": {}}
    lines = []
    for K in ks:
        sel = {p["key"]: select_part(p["cands"], cons[p["key"]], K, args.gates) for p in parts}
        rows = [dict(key=k, **s["iou"]) for k, s in sel.items()]
        slices = slice_rows(rows, split)
        m = {sn: {n: metrics([r[n] for r in rs]) for n in names} for sn, rs in slices.items()}
        branch = {f"gate{t}": {b: sum(s["branch"][f"gate{t}"] == b for s in sel.values()) / len(sel)
                               for b in ("vote", "verifier", "none")} for t in args.gates}
        result["by_k"][str(K)] = {
            "metrics": m["all"], "slices": m, "branch_frac": branch,
            "per_part": {k: s["iou"] for k, s in sel.items()},
            "picks": {k: {"pick": s["pick"], "agree": s["agree"], "n_exec": s["n_exec"],
                          "branch": s["branch"]} for k, s in sel.items()}}
        lines.append(f"\nK={K}  (n={len(parts)}; " + ", ".join(
            f"gate{t}: vote on {branch[f'gate{t}']['vote']*100:.0f}% of parts" for t in args.gates) + ")")
        lines.append(f"{'policy':12s} | " + " | ".join(f"{sn:>22s}" for sn in slices))
        lines.append(f"{'':12s} | " + " | ".join(f"{'mean / med / >=.85 / >=.5':>22s}" for _ in slices))
        for n in names:
            lines.append(f"{n:12s} | " + " | ".join(
                f"{m[sn][n]['iou_mean']:.3f} / {m[sn][n]['iou_median']:.3f} / {m[sn][n]['frac_iou85']*100:3.0f}% / "
                f"{m[sn][n]['frac_iou50']*100:3.0f}%" for sn in slices))
    # top level = first K (what analyze_ext.py reads)
    top = result["by_k"][str(ks[0])]
    result.update({"k": ks[0], "per_part": top["per_part"], "picks": top["picks"], "metrics": top["metrics"]})
    txt = "\n".join(lines)
    print(txt, flush=True)
    result["table"] = txt
    with open(args.out, "w") as f:
        json.dump(result, f, indent=1)
    with open(os.path.splitext(args.out)[0] + "_summary.txt", "w") as f:
        f.write(txt + "\n")


if __name__ == "__main__":
    main()
