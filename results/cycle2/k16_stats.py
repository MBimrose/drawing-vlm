"""Cycle 2: stats of the round-2 K=16 search samples per set, + how many parts gain a NEW >= 0.75 program
(vs the round-1 tier, and vs every earlier scored sample: e55 bo32/bo8, round-1 RL K=16, realpool2 RL K=4 mining).
    python k16_stats.py --tag c2pol [--sets A_c4,...]  -> results/cycle2/k16_stats.json"""
import argparse, json, os
import numpy as np
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"; C = f"{DV}/results/cycle2"; BD = f"{DV}/train_v14/mech/benchmarks/data"
PRIOR = {"c1": [f"{BD}/rft_corpus_dw423/results/bo32_rft_corpus_dw423_e55-rft-real-u5-gt-dw423.json"],
         "c2": [f"{BD}/rft_corpus2_dw423/results/bo32_rft_corpus2_dw423_e55-rft-real-u5-gt-dw423.json", f"{DV}/results/guide/v3/bo16_c2_t10.json"],
         "c4": [f"{DV}/results/h6c/bo8_real4_e55.json", f"{DV}/results/guide/v3/bo16_c4_t10.json"],
         "rp2": [f"{DV}/results/h6c/bo8_realpool2_e55.json", f"{DV}/results/realpool_v2/bo4_t10s120_a.json", f"{DV}/results/realpool_v2/bo4_t10s120_b.json"]}
ap = argparse.ArgumentParser(); ap.add_argument("--tag", default="c2pol"); ap.add_argument("--sets", default="A_c4,A_c2,A_c1,B_rp2,C_c4,C_c2,C_c1")
a = ap.parse_args()
tier = {json.loads(l)["key"]: json.loads(l)["iou"] for l in open(f"{DV}/results/guide/rft1/tier/accepted-000.jsonl")}
for b in ("bankv2_c4", "bankv2_c2", "bank_c1"):
    for k, v in json.load(open(f"{DV}/results/guide/{b}.json")).items():
        tier.setdefault(f"bank:{k}", v["iou"])
prior_cache = {}
def prior(c):
    if c not in prior_cache:
        d = {}
        for f in PRIOR[c]:
            if not os.path.exists(f): print("missing prior", f); continue
            for p in json.load(open(f))["candidates"]:
                b = max((float(x.get("iou") or 0) for x in p["cands"] if x.get("exec")), default=0.0)
                d[p["key"]] = max(d.get(p["key"], 0.0), b)
        prior_cache[c] = d
    return prior_cache[c]
out = {}
for s in a.sets.split(","):
    f = f"{C}/gen/{s}_{a.tag}.json"
    if not os.path.exists(f): continue
    c = s.split("_")[1]; P = prior(c)
    rows = []
    for p in json.load(open(f))["candidates"]:
        iou = [float(x.get("iou") or 0) for x in p["cands"]]; ex = [bool(x.get("exec")) for x in p["cands"]]
        rows.append((p["key"], iou, ex))
    best = np.array([max(i) for _, i, _ in rows]); k = [r[0] for r in rows]
    t1 = np.array([tier.get(x, 0.0) for x in k]); pr = np.array([P.get(x, 0.0) for x in k])
    new_t1 = (best >= 0.75) & (t1 < 0.75); new_all = new_t1 & (pr < 0.75)
    fam = {}
    for x, n1, na in zip(k, new_t1, new_all):
        d = fam.setdefault(x[0], [0, 0, 0]); d[0] += 1; d[1] += int(n1); d[2] += int(na)
    out[s] = {"parts": len(rows), "cands": int(sum(len(i) for _, i, _ in rows)),
              "exec": round(float(np.mean([e for _, _, ex in rows for e in ex])), 3),
              "draw0": round(float(np.mean([i[0] for _, i, _ in rows])), 3),
              "mean_cand": round(float(np.mean([np.mean(i) for _, i, _ in rows])), 3),
              "best16": round(float(best.mean()), 3), "best16_ge0.75": int((best >= 0.75).sum()), "best16_ge0.9": int((best >= 0.9).sum()),
              "best16_lt0.5": int((best < 0.5).sum()), "prior_best_mean": round(float(pr.mean()), 3),
              "beats_prior_by_0.03": int((best > pr + 0.03).sum()),
              "NEW_ge0.75_vs_tier1": int(new_t1.sum()), "NEW_ge0.75_vs_all_prior": int(new_all.sum()),
              "by_family[parts,new_t1,new_all]": fam}
    print(s, json.dumps(out[s]), flush=True)
json.dump(out, open(f"{C}/k16_stats.json", "w"), indent=1)
