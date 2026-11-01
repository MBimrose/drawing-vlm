"""American-VLM visual-repair summary (2026-10-28; flashnext/pipeline/summary_fn.py rules): chain final = last adopted
program; multi-start = per part the chain final with the highest v3 (label-free); IoU vs GT for reporting only; paired
3,000-sample bootstrap, rng 0; +/- = |d| > 0.05. Next to the 27B's S2 (e55 vote starts, rp3) and Flash-Next's (fnS2).
  glS2 = Glimmer glftpf K=8 vote -> top-3 distinct vote candidates -> 3 Glimmer-repairer chains 16x6 (margin 0.1) -> max-v3
Chains run in 24-key blocks on several hosts (am_runner.sh): out/ (ccc0442), out_s19/ (rsynced from serv-19 glpipe/out) and
h*/out/ (am_rp_cluster.sbatch on an H200 node; it resumed the serv-19 / ccc0442 partial blocks when serv-05 was freed).
    python summary_am.py [--name glS2] [--partial]   (--partial: only parts finished in every chain; no files written)"""
import argparse, glob, json, os
import numpy as np
P = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(os.path.dirname(P))
ap = argparse.ArgumentParser(); ap.add_argument("--name", default="glS2"); ap.add_argument("--partial", action="store_true")
ap.add_argument("--dir", default=None, help="pipeline dir of the chains (default: this dir; ../pipeline_gemma for gmS2)")
a = ap.parse_args()
REF = {"benchb": f"{RES}/bench_b/pipeline", "full": f"{RES}/indist_pipeline"}


def final(r):
    x = r["hist"][0]
    for y in r["hist"][1:]:
        if y.get("adopted"): x = y
    return x


def chains(d, name):
    out = []
    for c in (1, 2, 3):
        m = {}
        for f in sorted(glob.glob(f"{d}/out/{name}_c{c}.*jsonl") + glob.glob(f"{d}/out_s19/{name}_c{c}.*jsonl")
                        + glob.glob(f"{d}/h*/out/{name}_c{c}.*jsonl") + glob.glob(f"{d}/r*/out/{name}_c{c}.*jsonl")):
            if f.endswith(".dropped.jsonl"): continue
            for l in open(f):
                r = json.loads(l); m.setdefault(r["key"], r)
        out.append(m)
    return out


def ref_chains(bench):
    return [{json.loads(l)["key"]: json.loads(l) for l in open(f"{REF[bench]}/chain_e55_rp3_c{c}.jsonl")} for c in (1, 2, 3)]


def ms(ch, keys): return {k: max((final(c[k]) for c in ch), key=lambda x: x.get("v3", 0))["iou"] for k in keys}
def orc(ch, keys): return {k: max(final(c[k])["iou"] for c in ch) for k in keys}


rng = np.random.default_rng(0)
def ci(x):
    bs = [rng.choice(x, len(x)).mean() for _ in range(3000)]; return np.percentile(bs, 2.5), np.percentile(bs, 97.5)


lines = []
for bench, title in (("benchb", "Bench B (held-out 280)"), ("full", "Synthetic (1,027)")):
    G, R2 = chains(a.dir or P, f"{a.name}_{bench}"), ref_chains(bench)
    F = chains(f"{RES}/flashnext/pipeline", f"fnS2_{bench}")
    have = set.intersection(*[set(c) for c in G]); ref_keys = set(R2[0])
    keys = sorted(have) if a.partial else sorted(ref_keys)
    if not keys or not set(keys) <= have:
        lines.append(f"[{title}] {a.name}: {len(have)}/{len(ref_keys)} parts finished in every chain"); continue
    R = {f"{a.name} chain-1 start (vote)": {k: G[0][k]["hist"][0]["iou"] for k in keys},
         f"{a.name} single chain (c1)": {k: final(G[0][k])["iou"] for k in keys},
         f"{a.name} MULTI-START (3 chains, v3 pick)": ms(G, keys),
         f"{a.name} oracle over chain finals": orc(G, keys),
         "27B S2 MULTI-START": ms(R2, keys), "27B S2 chain-1 start": {k: R2[0][k]["hist"][0]["iou"] for k in keys}}
    if all(set(keys) <= set(c) for c in F): R["FN S2 MULTI-START"] = ms(F, keys)
    lines += ["", f"## {title}", "", "| stage | n | mean | ≥0.85 |", "|---|---|---|---|"]
    for n, d in R.items():
        x = np.array(list(d.values())); lines.append(f"| {n} | {len(x)} | {x.mean():.3f} | {np.mean(x >= 0.85):.0%} |")
    lines += ["", "| paired Δ | n | Δ [95% CI] | +/− |", "|---|---|---|---|"]
    M = f"{a.name} MULTI-START (3 chains, v3 pick)"
    for x_, y_ in ((M, "27B S2 MULTI-START"), (M, f"{a.name} chain-1 start (vote)"), (M, "FN S2 MULTI-START"),
                   (f"{a.name} chain-1 start (vote)", "27B S2 chain-1 start")):
        if x_ in R and y_ in R:
            ks = sorted(set(R[x_]) & set(R[y_])); d = np.array([R[x_][k] - R[y_][k] for k in ks]); lo, hi = ci(d)
            lines.append(f"| {x_} − {y_} | {len(ks)} | {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}] | +{(d > 0.05).sum()}/−{(d < -0.05).sum()} |")
txt = "\n".join(lines).strip(); print(txt)
if not a.partial: open(f"{P}/summary_{a.name}.txt", "w").write(txt + "\n")
