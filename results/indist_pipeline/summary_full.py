"""In-distribution full-pipeline summary (2026-10-14): results/bench_b/pipeline/summary_b.py on mech_benchmarks/fullpool_dw423
(1,027 synthetic parts with GT = the keys of results/grpo_eval/full_e55ctl.json). Same systems, same rules (chain final = last
adopted program; multi-start = per part the chain final with the highest v3; IoU vs GT for reporting only; paired 3,000-sample
bootstrap, rng 0; helped/hurt = |d| > 0.05). The synthetic pool has no ABC/Fusion families, so those columns are dropped.
  S1 = rft2_rl_s60 K=16 -> v3b-EV + v3 ranking -> top-3 distinct -> 3 rp3 chains 16x6 (margin 0.1) -> max-v3 pick
  S2 = e55 K=8 vote -> top-3 distinct vote candidates -> 3 rp3 chains 16x6 -> max-v3 pick
Chains were run in 24-key blocks on two hosts (runner.sh); this script first merges out/ (ccc0442) and out_s20/ (rsynced from
serv-20) into chain_<sys>_rp3_c{1,2,3}.jsonl.
    python summary_full.py [--partial]   (--partial: only parts finished in every chain; no files written)"""
import argparse, glob, json, os
import numpy as np
P = os.path.dirname(os.path.abspath(__file__)); G = os.path.join(os.path.dirname(P), "grpo_eval")
ap = argparse.ArgumentParser(); ap.add_argument("--partial", action="store_true"); a = ap.parse_args()
POOL = sorted(p["key"] for p in json.load(open(f"{G}/full_e55ctl.json"))["candidates"])


def final(r):
    x = r["hist"][0]
    for y in r["hist"][1:]:
        if y.get("adopted"): x = y
    return x


def chains(sysname):
    out = []
    for c in (1, 2, 3):
        d = {}
        for f in sorted(f for f in glob.glob(f"{P}/out/{sysname}_c{c}.*jsonl") + glob.glob(f"{P}/out_s20/{sysname}_c{c}.*jsonl") if not f.endswith(".dropped.jsonl")):
            for l in open(f):
                r = json.loads(l)
                assert r["key"] not in d or json.dumps(d[r["key"]]["hist"]) == json.dumps(r["hist"]) or a.partial, (f, r["key"])
                d.setdefault(r["key"], r)
        if not a.partial:
            assert sorted(d) == POOL, (sysname, c, len(d), len(POOL))
            with open(f"{P}/chain_{sysname}_rp3_c{c}.jsonl", "w") as fo:
                for k in POOL: fo.write(json.dumps(d[k]) + "\n")
        out.append(d)
    return out


def bo(path, k=None):
    out = {}
    for p in json.load(open(path))["candidates"]:
        c = sorted(p["cands"], key=lambda c: c.get("draw", 0))[: k or None]
        out[p["key"]] = max(float(x.get("iou") or 0) for x in c)
    return out


def votes(path):
    return {k: float(v["consistency"]) for k, v in json.load(open(path))["per_part"].items()}


S1, S2 = chains("rl2s60"), chains("e55")
keys = sorted(set.intersection(*[set(c) for c in S1 + S2])) if a.partial else POOL
R = {}
def ms(ch): return {k: max((final(c[k]) for c in ch), key=lambda x: x.get("v3", 0))["iou"] for k in keys}
def orc(ch): return {k: max(final(c[k])["iou"] for c in ch) for k in keys}
R["S1 K=16 vote"] = votes(f"{P}/full_k16_rl2s60_consistency.json")
R["S1 K=16 selected pick (chain-1 start)"] = {k: S1[0][k]["hist"][0]["iou"] for k in keys}
R["S1 K=16 oracle"] = bo(f"{P}/full_k16_rl2s60.json")
R["S1 single chain (c1)"] = {k: final(S1[0][k])["iou"] for k in keys}
R["S1 MULTI-START (3 chains, v3 pick)"] = ms(S1)
R["S1 oracle over chain finals"] = orc(S1)
R["S2 e55 K=8 vote pick (chain-1 start)"] = {k: S2[0][k]["hist"][0]["iou"] for k in keys}
R["S2 e55 K=8 oracle"] = bo(f"{G}/full_e55ctl.json")
R["S2 single chain (c1)"] = {k: final(S2[0][k])["iou"] for k in keys}
R["S2 MULTI-START (3 chains, v3 pick)"] = ms(S2)
R["S2 oracle over chain finals"] = orc(S2)
R = {n: {k: d[k] for k in keys} for n, d in R.items()}


def row(n, d):
    v = np.array([d[k] for k in keys])
    return f"| {n} | {len(v)} | {v.mean():.3f} | {np.median(v):.3f} | {np.mean(v >= 0.85):.0%} |"


rng = np.random.default_rng(0)
def ci(x):
    bs = [rng.choice(x, len(x)).mean() for _ in range(3000)]; return np.percentile(bs, 2.5), np.percentile(bs, 97.5)
def pair(a_, b_):
    d = np.array([R[a_][k] - R[b_][k] for k in keys]); lo, hi = ci(d)
    return f"| {a_} − {b_} | {len(keys)} | {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}] | +{(d > 0.05).sum()}/−{(d < -0.05).sum()} |"


lines = ["| stage | n | mean | median | ≥0.85 |", "|---|---|---|---|---|"] + [row(n, d) for n, d in R.items()]
lines += ["", "| paired Δ | n | all | +/− |", "|---|---|---|---|"]
for x, y in (("S1 MULTI-START (3 chains, v3 pick)", "S2 MULTI-START (3 chains, v3 pick)"),
             ("S1 MULTI-START (3 chains, v3 pick)", "S1 K=16 selected pick (chain-1 start)"),
             ("S1 MULTI-START (3 chains, v3 pick)", "S1 single chain (c1)"),
             ("S1 single chain (c1)", "S1 K=16 selected pick (chain-1 start)"),
             ("S1 K=16 selected pick (chain-1 start)", "S1 K=16 vote"),
             ("S2 MULTI-START (3 chains, v3 pick)", "S2 e55 K=8 vote pick (chain-1 start)"),
             ("S2 MULTI-START (3 chains, v3 pick)", "S2 single chain (c1)"),
             ("S2 single chain (c1)", "S2 e55 K=8 vote pick (chain-1 start)"),
             ("S1 single chain (c1)", "S2 single chain (c1)"),
             ("S1 K=16 selected pick (chain-1 start)", "S2 MULTI-START (3 chains, v3 pick)"),
             ("S1 oracle over chain finals", "S2 oracle over chain finals")):
    lines.append(pair(x, y))
txt = "\n".join(lines); print(txt)
if not a.partial: open(f"{P}/summary_full.txt", "w").write(txt + "\n")
