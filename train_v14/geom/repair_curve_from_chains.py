"""Repair-loop curve (mean IoU after each round) from S2 chain records (results/american_vlm/pipeline*: 3 chains per part,
each record's hist = round-0 start + every adopted repair with its stored IoU and v3 score). No execution needed.
Per round r, a chain's current program = its last hist entry with round <= r;
  single chain = chain 1 (top vote start), multi-start = per part the chain with the highest v3 (the served pick).
Round 6 reproduces summary_am.py's chain-1 / multi-start cells. Output in the format plot_pipeline_timing.repair_compare reads.

    python3 train_v14/geom/repair_curve_from_chains.py --dir results/american_vlm/pipeline --name glS2_benchb \
        --out results/figures/pipeline_timing/repair_curve_bench_b_glS2.json
"""
import argparse
import glob
import json

import numpy as np


def chains(d, name):
    """Same file set and first-record-wins rule as pipeline/summary_am.py."""
    out = []
    for c in (1, 2, 3):
        m = {}
        for f in sorted(glob.glob(f"{d}/out/{name}_c{c}.*jsonl") + glob.glob(f"{d}/out_s19/{name}_c{c}.*jsonl")
                        + glob.glob(f"{d}/h*/out/{name}_c{c}.*jsonl") + glob.glob(f"{d}/r*/out/{name}_c{c}.*jsonl")):
            if f.endswith(".dropped.jsonl"):
                continue
            for l in open(f):
                r = json.loads(l); m.setdefault(r["key"], r)
        out.append(m)
    return out


def at(r, rnd):
    x = r["hist"][0]
    for y in r["hist"][1:]:
        if y["round"] <= rnd and y.get("adopted"):
            x = y
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True); ap.add_argument("--name", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--rounds", type=int, default=6)
    a = ap.parse_args()
    G = chains(a.dir, a.name); keys = sorted(set.intersection(*[set(c) for c in G]))
    o = {"n": len(keys), "rounds": list(range(a.rounds + 1)), "source": f"{a.dir} {a.name}"}
    for tag, pick in (("chain1", lambda k, r: at(G[0][k], r)["iou"]),
                      ("multistart", lambda k, r: max((at(c[k], r) for c in G), key=lambda x: x.get("v3", 0))["iou"])):
        M = np.array([[pick(k, r) for k in keys] for r in o["rounds"]])
        o[f"{tag}_mean"] = M.mean(1).tolist(); o[f"{tag}_sem"] = (M.std(1, ddof=1) / np.sqrt(len(keys))).tolist()
        o[f"{tag}_frac85"] = (M >= 0.85).mean(1).tolist()
    json.dump(o, open(a.out, "w"), indent=1)
    print(a.name, "n", len(keys), "chain1", np.round(o["chain1_mean"], 3), "multistart", np.round(o["multistart_mean"], 3))


if __name__ == "__main__":
    main()
