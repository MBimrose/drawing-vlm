"""Flash-Next full-pipeline summary (2026-10-22): the bench-B / in-dist S1 and S2 systems rebuilt on Flash-Next, next to the 27B's,
with results/bench_b/pipeline/summary_b.py's rules (chain final = last adopted program; multi-start = per part the chain final
with the highest v3; IoU vs GT for reporting only; paired 3,000-sample bootstrap, rng 0; helped/hurt = |d| > 0.05).
  FN S2 = e59 K=8 vote -> top-3 distinct vote candidates -> 3 FNRP chains 16x6 (margin 0.1) -> max-v3 pick
  FN S1 = fnei K=16 -> v3b-EV + v3 ranking -> top-3 distinct -> 3 FNRP chains 16x6 -> max-v3 pick
  27B S2 / S1 = the same with e55 / rft2_rl_s60 and rp3 (bench B: results/bench_b/pipeline, synthetic: results/indist_pipeline)
FN chains ran in 24-key blocks on two hosts (fn_runner.sh): out/ (ccc0442) and out_s19/ (rsynced from serv-19 fnpipe/out).
    python summary_fn.py [--partial]   (--partial: only parts finished in every chain; no files written)"""
import argparse, glob, json, os
import numpy as np
P = os.path.dirname(os.path.abspath(__file__)); RES = os.path.dirname(os.path.dirname(P))
ap = argparse.ArgumentParser(); ap.add_argument("--partial", action="store_true"); a = ap.parse_args()
REF = {"benchb": f"{RES}/bench_b/pipeline", "full": f"{RES}/indist_pipeline"}


def final(r):
    x = r["hist"][0]
    for y in r["hist"][1:]:
        if y.get("adopted"): x = y
    return x


def fn_chains(name):
    out = []
    for c in (1, 2, 3):
        d = {}
        for f in sorted(glob.glob(f"{P}/out/{name}_c{c}.*jsonl") + glob.glob(f"{P}/out_s19/{name}_c{c}.*jsonl")):
            if f.endswith(".dropped.jsonl"): continue
            for l in open(f):
                r = json.loads(l); d.setdefault(r["key"], r)
        out.append(d)
    return out


def ref_chains(bench, sysname):
    return [{json.loads(l)["key"]: json.loads(l) for l in open(f"{REF[bench]}/chain_{sysname}_rp3_c{c}.jsonl")} for c in (1, 2, 3)]


def ms(ch, keys): return {k: max((final(c[k]) for c in ch), key=lambda x: x.get("v3", 0))["iou"] for k in keys}
def orc(ch, keys): return {k: max(final(c[k])["iou"] for c in ch) for k in keys}
def votes(path): return {k: float(v["consistency"]) for k, v in json.load(open(path))["per_part"].items()} if os.path.exists(path) else {}


rng = np.random.default_rng(0)
def ci(x):
    bs = [rng.choice(x, len(x)).mean() for _ in range(3000)]; return np.percentile(bs, 2.5), np.percentile(bs, 97.5)


lines = []
for bench, title in (("benchb", "Bench B (held-out 280)"), ("full", "Synthetic (1,027)")):
    S2, S1 = fn_chains(f"fnS2_{bench}"), fn_chains(f"fnS1_{bench}")
    R2, R1 = ref_chains(bench, "e55"), ref_chains(bench, "rl2s60")
    have2 = set.intersection(*[set(c) for c in S2]); have1 = set.intersection(*[set(c) for c in S1]) if all(S1) else set()
    ref_keys = set(R2[0])
    R = {}
    for tag, ch, have in (("S2", S2, have2), ("S1", S1, have1)):
        keys = sorted(have) if a.partial else sorted(ref_keys)
        if not keys or not set(keys) <= have:
            lines.append(f"[{title}] FN {tag}: {len(have)}/{len(ref_keys)} parts finished in every chain"); continue
        R[f"FN {tag} chain-1 start"] = {k: ch[0][k]["hist"][0]["iou"] for k in keys}
        R[f"FN {tag} single chain (c1)"] = {k: final(ch[0][k])["iou"] for k in keys}
        R[f"FN {tag} MULTI-START (3 chains, v3 pick)"] = ms(ch, keys)
        R[f"FN {tag} oracle over chain finals"] = orc(ch, keys)
        R[f"27B {tag} MULTI-START (3 chains, v3 pick)"] = ms(R2 if tag == "S2" else R1, keys)
        R[f"27B {tag} chain-1 start"] = {k: (R2 if tag == "S2" else R1)[0][k]["hist"][0]["iou"] for k in keys}
    v = votes(f"{P}/s1/{bench}_k16_fnei_consistency.json")
    if "FN S1 chain-1 start" in R and v:
        R["FN S1 K=16 vote"] = {k: v[k] for k in R["FN S1 chain-1 start"]}
    if not R:
        continue
    lines += ["", f"## {title}", "", "| stage | n | mean | ≥0.85 |", "|---|---|---|---|"]
    for n, d in R.items():
        x = np.array(list(d.values())); lines.append(f"| {n} | {len(x)} | {x.mean():.3f} | {np.mean(x >= 0.85):.0%} |")
    lines += ["", "| paired Δ | n | Δ [95% CI] | +/− |", "|---|---|---|---|"]
    for x_, y_ in (("FN S2 MULTI-START (3 chains, v3 pick)", "27B S2 MULTI-START (3 chains, v3 pick)"),
                   ("FN S1 MULTI-START (3 chains, v3 pick)", "27B S1 MULTI-START (3 chains, v3 pick)"),
                   ("FN S2 MULTI-START (3 chains, v3 pick)", "FN S2 chain-1 start"),
                   ("FN S1 MULTI-START (3 chains, v3 pick)", "FN S1 chain-1 start"),
                   ("FN S2 chain-1 start", "27B S2 chain-1 start"),
                   ("FN S1 chain-1 start", "27B S1 chain-1 start"),
                   ("FN S1 MULTI-START (3 chains, v3 pick)", "FN S2 MULTI-START (3 chains, v3 pick)")):
        if x_ in R and y_ in R:
            ks = sorted(set(R[x_]) & set(R[y_])); d = np.array([R[x_][k] - R[y_][k] for k in ks]); lo, hi = ci(d)
            lines.append(f"| {x_} − {y_} | {len(ks)} | {d.mean():+.3f} [{lo:+.3f}, {hi:+.3f}] | +{(d > 0.05).sum()}/−{(d < -0.05).sum()} |")
txt = "\n".join(lines).strip(); print(txt)
if not a.partial: open(f"{P}/summary_fn.txt", "w").write(txt + "\n")
