"""Adaptive draw budget: spend the extra draws only where the vote is unsure.

The served policy (gated_select.py) draws a fixed K, takes the consistency
medoid when its mean agreement >= gate and the verifier's expected-IoU argmax
otherwise. K=32 beats K=8 (real bench 0.571 vs 0.554 for e55) but costs four
times the generation for every part -- while the gate already tells us, at
K=k0, which parts are the unsure ones.

Adaptive policy, per part:
  1. draw k0 candidates, execute, medoid agreement over the executing ones;
  2. agreement >= gate            -> serve that medoid            (cost k0)
     otherwise                    -> draw up to k1 and re-select  (cost k1)
     The escalated pick is the verifier argmax over all k1 draws
     (--escalate verifier, the default) or the k1 gate again
     (--escalate gate: medoid if the k1 agreement clears the gate).

Everything is replayed offline from a stored best-of-k1 run: the first k0
candidates in draw order ARE the k0-draw run (draw 0 greedy, the rest sampled),
so no generation is needed to measure this.

    python adaptive_k.py --cands results/ext/bo32_ext_<run>.json \
        --consistency results/ext/bo32_ext_<run>_consistency.json \
        --preds results/ext/bo32_ext_<run>_vsel.json.preds.json \
        --split .../ext_bench/split.json --k0 8 --k1 16 32 \
        --out results/ext/bo32_ext_<run>_adaptive.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from gated_select import medoid, metrics, slice_rows  # noqa: E402


def executing(cands, K):
    """Positions of the first K draws that executed and carry a verifier score."""
    return [j for j, c in enumerate(cands[:K]) if c.get("exec") and c.get("pred") is not None]


def fixed(cands, mat, K, gate):
    """The deployed fixed-budget policies at K (vote / verifier / gate / oracle)."""
    ex = executing(cands, K)
    if not ex:
        return {"vote": 0.0, "verifier": 0.0, "gate": 0.0, "oracle": 0.0, "agree": 0.0, "n_exec": 0}
    jm, agree = medoid(ex, mat)
    jv = max(ex, key=lambda j: cands[j]["pred"])
    jo = max(ex, key=lambda j: cands[j]["iou"])
    use_vote = len(ex) > 1 and agree >= gate
    return {"vote": cands[jm]["iou"], "verifier": cands[jv]["iou"],
            "gate": cands[jm if use_vote else jv]["iou"], "oracle": cands[jo]["iou"],
            "agree": agree, "n_exec": len(ex)}


def adaptive(cands, mat, k0, k1, gate, escalate):
    """Draw k0; escalate to k1 only when the k0 medoid's agreement misses the gate."""
    ex0 = executing(cands, k0)
    if len(ex0) > 1:
        jm0, agree0 = medoid(ex0, mat)
        if agree0 >= gate:
            return {"iou": cands[jm0]["iou"], "draws": k0, "branch": "vote", "agree": agree0}
    else:
        agree0 = 0.0
    ex1 = executing(cands, k1)
    if not ex1:
        return {"iou": 0.0, "draws": k1, "branch": "none", "agree": agree0}
    jv = max(ex1, key=lambda j: cands[j]["pred"])
    if escalate == "gate":
        jm1, agree1 = medoid(ex1, mat)
        if len(ex1) > 1 and agree1 >= gate:
            return {"iou": cands[jm1]["iou"], "draws": k1, "branch": "vote@k1", "agree": agree0}
    return {"iou": cands[jv]["iou"], "draws": k1, "branch": "verifier@k1", "agree": agree0}


def ladder(cands, mat, stages, gate, escalate):
    """Multi-stage version: stop at the first stage whose medoid clears the gate."""
    for K in stages[:-1]:
        ex = executing(cands, K)
        if len(ex) > 1:
            jm, agree = medoid(ex, mat)
            if agree >= gate:
                return {"iou": cands[jm]["iou"], "draws": K, "branch": f"vote@{K}", "agree": agree}
    # last stage: the gate has failed at every earlier budget, so select without it
    K = stages[-1]
    ex = executing(cands, K)
    if not ex:
        return {"iou": 0.0, "draws": K, "branch": "none", "agree": 0.0}
    jv = max(ex, key=lambda j: cands[j]["pred"])
    if escalate == "gate":
        jm, agree = medoid(ex, mat)
        if len(ex) > 1 and agree >= gate:
            return {"iou": cands[jm]["iou"], "draws": K, "branch": f"vote@{K}", "agree": agree}
    return {"iou": cands[jv]["iou"], "draws": K, "branch": f"final@{K}", "agree": 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cands", required=True)
    ap.add_argument("--consistency", required=True)
    ap.add_argument("--preds", required=True)
    ap.add_argument("--split", default="")
    ap.add_argument("--k0", type=int, default=8)
    ap.add_argument("--k1", type=int, nargs="+", default=[16, 32])
    ap.add_argument("--gates", type=float, nargs="+", default=[0.85])
    ap.add_argument("--escalate", nargs="+", default=["verifier", "gate"],
                    choices=["verifier", "gate"])
    ap.add_argument("--ladder", type=int, nargs="+", default=[],
                    help="multi-stage budgets, e.g. --ladder 8 16 32")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    data = json.load(open(args.cands))
    parts = data["candidates"]
    for p in parts:
        p["cands"].sort(key=lambda c: c.get("draw", 0))
    cons = {cp["key"]: cp["pair_iou"] for cp in json.load(open(args.consistency))["parts"]}
    preds = json.load(open(args.preds))
    split = json.load(open(args.split)) if args.split else {}
    for p in parts:
        pr = preds.get(p["key"]) or [None] * len(p["cands"])
        for c, v in zip(p["cands"], pr):
            c["pred"] = None if v is None else float(v[0])
        cons.setdefault(p["key"], [[None] * len(p["cands"])] * len(p["cands"]))

    kmax = max(len(p["cands"]) for p in parts)
    result = {"cands": args.cands, "k0": args.k0, "kmax": kmax, "n_parts": len(parts), "rows": {}}
    lines = [f"adaptive draw budget (k0={args.k0}, escalate when the k0 medoid misses the gate)",
             f"cands {os.path.basename(args.cands)}  n={len(parts)}", ""]
    hdr = f"{'policy':34s} | {'mean':>6s} {'med':>6s} {'>=.85':>6s} {'>=.5':>6s} | {'draws/part':>10s} {'escalated':>9s}"
    lines += [hdr, "-" * len(hdr)]

    def row(name, vals, draws, esc):
        m = metrics(vals)
        result["rows"][name] = dict(m, draws_per_part=draws, escalated=esc)
        lines.append(f"{name:34s} | {m['iou_mean']:6.3f} {m['iou_median']:6.3f} "
                     f"{m['frac_iou85']:6.1%} {m['frac_iou50']:6.1%} | {draws:10.1f} "
                     + (f"{esc:8.1%}" if esc is not None else "        -"))

    for gate in args.gates:
        # fixed budgets, for reference
        for K in sorted({args.k0, *args.k1, kmax}):
            f = [fixed(p["cands"], cons[p["key"]], K, gate) for p in parts]
            for pol in ("vote", "verifier", "gate", "oracle"):
                row(f"K={K:<3d} {pol}" + (f" (gate {gate})" if pol == "gate" else ""),
                    [x[pol] for x in f], float(K), None)
            lines.append("")
        # adaptive
        for esc in args.escalate:
            for k1 in args.k1:
                a = [adaptive(p["cands"], cons[p["key"]], args.k0, k1, gate, esc) for p in parts]
                n_esc = sum(x["branch"] != "vote" for x in a)
                row(f"adaptive {args.k0}->{k1} {esc} (gate {gate})", [x["iou"] for x in a],
                    sum(x["draws"] for x in a) / len(a), n_esc / len(a))
                key = f"adaptive_{args.k0}_{k1}_{esc}_gate{gate}"
                result[key] = {p["key"]: x for p, x in zip(parts, a)}
                if split:
                    rows = [dict(key=p["key"], iou=x["iou"]) for p, x in zip(parts, a)]
                    for sn, rs in slice_rows(rows, split).items():
                        if sn != "all":
                            m = metrics([r["iou"] for r in rs])
                            lines.append(f"{'  ' + sn:34s} | {m['iou_mean']:6.3f} {m['iou_median']:6.3f} "
                                         f"{m['frac_iou85']:6.1%} {m['frac_iou50']:6.1%} |")
            lines.append("")
        if args.ladder:
            for esc in args.escalate:
                a = [ladder(p["cands"], cons[p["key"]], args.ladder, gate, esc) for p in parts]
                stops = {}
                for x in a:
                    stops[x["branch"]] = stops.get(x["branch"], 0) + 1
                row(f"ladder {'-'.join(map(str, args.ladder))} {esc} (gate {gate})",
                    [x["iou"] for x in a], sum(x["draws"] for x in a) / len(a),
                    sum(x["draws"] > args.ladder[0] for x in a) / len(a))
                lines.append("    stops: " + ", ".join(f"{k} {v}" for k, v in sorted(stops.items())))
                result[f"ladder_{'_'.join(map(str, args.ladder))}_{esc}_gate{gate}"] = \
                    {p["key"]: x for p, x in zip(parts, a)}
            lines.append("")

    txt = "\n".join(lines)
    print(txt)
    json.dump(result, open(args.out, "w"), indent=1)
    with open(os.path.splitext(args.out)[0] + "_summary.txt", "w") as f:
        f.write(txt + "\n")
    print(f"[adaptive] -> {args.out}")


if __name__ == "__main__":
    main()
