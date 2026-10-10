"""Bench B full-pipeline summary (2026-10-10): start -> repair -> multi-start decomposition for the two pre-declared systems,
in the format of results/pipeline_grpo/summary_table.txt / cycle2 summary_e2e (chain_compare.py rules: chain final = last
adopted program; multi-start = per part the chain final with the highest v3; IoU vs GT for reporting only; paired 3,000-sample
bootstrap, rng 0; helped/hurt = |d| > 0.05).
  S1 = rft2_rl_s60 K=16 -> v3b-EV + v3 ranking -> top-3 distinct -> 3 rp3 chains 16x6 (margin 0.1) -> max-v3 pick (e2e / 0.714 protocol)
  S2 = e55 K=8 vote -> top-3 distinct vote candidates -> 3 rp3 chains 16x6 -> max-v3 pick (the 0.695 system's recipe)
    python summary_b.py [--partial]   (--partial: only parts finished in every chain)"""
import argparse, json, os
import numpy as np
P = os.path.dirname(os.path.abspath(__file__)); E = os.path.join(os.path.dirname(P), "eval")
ap = argparse.ArgumentParser(); ap.add_argument("--partial", action="store_true"); a = ap.parse_args()


def final(r):
    x = r["hist"][0]
    for y in r["hist"][1:]:
        if y.get("adopted"): x = y
    return x


def chains(stem):
    return [{json.loads(l)["key"]: json.loads(l) for l in open(f"{P}/{stem}_c{c}.jsonl")} for c in (1, 2, 3)]


def bo(path, k=None, vote=None):
    out = {}
    for p in json.load(open(path))["candidates"]:
        c = sorted(p["cands"], key=lambda c: c.get("draw", 0))[: k or None]
        out[p["key"]] = max(float(x.get("iou") or 0) for x in c)
    return out


def votes(path):
    return {k: float(v["consistency"]) for k, v in json.load(open(path))["per_part"].items()}


S1, S2 = chains("chain_rl2s60_rp3"), chains("chain_e55_rp3")
keys = sorted(set.intersection(*[set(c) for c in S1 + S2])) if a.partial else sorted(S1[0])
R = {}
def ms(ch): return {k: max((final(c[k]) for c in ch), key=lambda x: x.get("v3", 0))["iou"] for k in keys}
def orc(ch): return {k: max(final(c[k])["iou"] for c in ch) for k in keys}
R["S1 K=16 vote"] = votes(f"{P}/benchb_k16_rl2s60_consistency.json")
R["S1 K=16 selected pick (chain-1 start)"] = {k: S1[0][k]["hist"][0]["iou"] for k in keys}
R["S1 K=16 oracle"] = bo(f"{P}/benchb_k16_rl2s60.json")
R["S1 single chain (c1)"] = {k: final(S1[0][k])["iou"] for k in keys}
R["S1 MULTI-START (3 chains, v3 pick)"] = ms(S1)
R["S1 oracle over chain finals"] = orc(S1)
R["S2 e55 K=8 vote pick (chain-1 start)"] = {k: S2[0][k]["hist"][0]["iou"] for k in keys}
R["S2 e55 K=8 oracle"] = bo(f"{E}/benchb_e55ctl.json")
R["S2 single chain (c1)"] = {k: final(S2[0][k])["iou"] for k in keys}
R["S2 MULTI-START (3 chains, v3 pick)"] = ms(S2)
R["S2 oracle over chain finals"] = orc(S2)
R = {n: {k: d[k] for k in keys} for n, d in R.items()}


def row(n, d):
    v = np.array([d[k] for k in keys]); ab = [d[k] for k in keys if k.startswith("A_")]; fu = [d[k] for k in keys if k.startswith("F_")]
    return f"| {n} | {len(v)} | {v.mean():.3f} | {np.mean(ab):.3f} | {np.mean(fu):.3f} | {np.mean(v >= 0.85):.0%} |"


rng = np.random.default_rng(0)
def ci(x):
    bs = [rng.choice(x, len(x)).mean() for _ in range(3000)]; return np.percentile(bs, 2.5), np.percentile(bs, 97.5)
def pair(a_, b_):
    out = []
    for sub in ("all", "A_", "F_"):
        ks = [k for k in keys if sub == "all" or k.startswith(sub)]
        d = np.array([R[a_][k] - R[b_][k] for k in ks]); lo, hi = ci(d); out.append(f"{d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}]")
    d = np.array([R[a_][k] - R[b_][k] for k in keys])
    return f"| {a_} − {b_} | {len(keys)} | " + " | ".join(out) + f" | +{(d > 0.05).sum()}/−{(d < -0.05).sum()} |"


lines = ["| stage | n | mean | ABC | Fusion | ≥0.85 |", "|---|---|---|---|---|---|"] + [row(n, d) for n, d in R.items()]
lines += ["", "| paired Δ | n | all | ABC | Fusion | +/− |", "|---|---|---|---|---|---|"]
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
if not a.partial: open(f"{P}/summary_b.txt", "w").write(txt + "\n")
