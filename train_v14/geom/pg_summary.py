"""Full pipeline on the GRPO generator (2026-10-08): stage table + paired bootstrap CIs.

Stages per real-bench part (IoU vs GT, evaluation only; every selection is label-free):
  K=8 vote (grpo_eval file and first 8 of the K=16 file), K=16 vote, K=16 selected pick (v3b-EV + v3),
  K=16 oracle, chain 1 final (repair from the top-1 start), multi-start = v3-max over the chain finals
  (multistart_combine.py rule), oracle over chain finals.
References: the 0.695 system (multistart over the three Sep-30 chains, same rule) and its start = e55 vote pick.
Chain final = last adopted program (hist), as multistart_combine.py. A part missing from a chain file (vr_serve error,
e.g. no executing start) keeps its start program. Paired deltas on the keys common to both arms; 3,000-sample
bootstrap, rng 0. helped/hurt = |delta| > 0.05 (v3adopt_summary.py convention).

    python pg_summary.py --sel results/pipeline_grpo/sel_k16.json --starts results/pipeline_grpo/starts_sel_r1.json \
        --chains c1.jsonl c2.jsonl c3.jsonl --ref-chains r1.jsonl r2.jsonl r3.jsonl --out results/pipeline_grpo/summary
"""
import argparse
import json

import numpy as np


def final(r):
    h = r["hist"]; x = h[0]
    for y in h[1:]:
        if y.get("adopted"):
            x = y
    return x


def load_chain(f):
    return {json.loads(l)["key"]: json.loads(l) for l in open(f)}


def chain_arrays(files, starts, keys):
    """per key: chain-1 start, chain-1 final, multistart v3 pick, oracle over finals, #adoptions chain 1"""
    ch = [load_chain(f) for f in files]
    out = {}
    for k in keys:
        fs = []
        for ci, c in enumerate(ch):
            if k in c:
                fs.append(final(c[k]))
            elif starts and ci < len(starts) and k in starts[ci]:
                fs.append({"iou": starts[ci][k]["iou"], "v3": -1.0, "_missing": True})
        if not fs:
            continue
        st = ch[0][k]["hist"][0]["iou"] if k in ch[0] else (starts[0][k]["iou"] if starts else 0.0)
        out[k] = {"start": st, "c1": fs[0]["iou"], "ms": max(fs, key=lambda x: x.get("v3", 0))["iou"],
                  "orc": max(x["iou"] for x in fs), "missing": sum(1 for x in fs if x.get("_missing"))}
    return out


def ci(a, b, rng):
    d = np.asarray(a) - np.asarray(b)
    bs = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(3000)]
    return d.mean(), np.percentile(bs, 2.5), np.percentile(bs, 97.5), int((d > 0.05).sum()), int((d < -0.05).sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sel", required=True, help="sel_study.py output with k16 + k8eval specs at K=8 and K=16")
    ap.add_argument("--gen", default="k16_ent_t10s120"); ap.add_argument("--k8eval", default="k8eval_ent_t10s120")
    ap.add_argument("--starts", nargs="+", required=True, help="start files of the chains (same order as --chains)")
    ap.add_argument("--chains", nargs="+", required=True)
    ap.add_argument("--ref-chains", nargs="+", required=True)
    ap.add_argument("--label", default="primary (starts = top-3 distinct by v3b-EV + v3)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    S = json.load(open(a.sel))["by_k"]
    pp16 = S["16"]["per_part"][a.gen]; pp8 = S["8"]["per_part"][a.gen]
    pp8e = S["8"]["per_part"].get(a.k8eval, {})
    starts = [json.load(open(f)) for f in a.starts]
    keys = sorted(pp16)
    mine = chain_arrays(a.chains, starts, keys)
    ref = chain_arrays(a.ref_chains, None, sorted(load_chain(a.ref_chains[0])))
    rows = {}
    for k in keys:
        r = {"k8_vote_eval": pp8e.get(k, {}).get("vote"), "k8_vote": pp8[k]["vote"], "k16_vote": pp16[k]["vote"],
             "k16_sel": pp16[k]["ver+v3"], "k16_oracle": pp16[k]["oracle"], "start_r1": starts[0][k]["iou"]}
        if k in mine:
            r.update({"chain1": mine[k]["c1"], "multistart": mine[k]["ms"], "chain_oracle": mine[k]["orc"],
                      "missing_chains": mine[k]["missing"]})
        if k in ref:
            r.update({"ref_e55_vote": ref[k]["start"], "ref_chain1": ref[k]["c1"], "ref_695": ref[k]["ms"],
                      "ref_chain_oracle": ref[k]["orc"]})
        rows[k] = r
    L = []
    def stat(name, col, ks=None):
        ks = [k for k in (ks or keys) if rows[k].get(col) is not None]
        v = np.array([rows[k][col] for k in ks]); A = [k for k in ks if k[0] == "A"]; F = [k for k in ks if k[0] == "F"]
        L.append(f"  {name:44s} {v.mean():.3f}  ABC {np.mean([rows[k][col] for k in A]):.3f}  Fusion "
                 f"{np.mean([rows[k][col] for k in F]):.3f}  >=0.85 {100*(v >= 0.85).mean():3.0f}%  n={len(ks)}")
    L.append(f"== Full pipeline on GRPO generator ent_t10 s120 — {a.label}")
    L.append(f"  chain files: {' '.join(a.chains)}")
    L.append("  stage                                        mean")
    stat("K=8 vote (grpo_eval K=8 file)", "k8_vote_eval")
    stat("K=8 vote (first 8 of the K=16 draws)", "k8_vote")
    stat("K=16 vote", "k16_vote")
    stat("K=16 selected pick (v3b-EV + v3) = chain-1 start", "k16_sel")
    stat("K=16 oracle (best-of-16, GT)", "k16_oracle")
    stat("single chain (rp3 16x6 from top-1)", "chain1")
    stat("MULTI-START 3 chains, v3 pick (label-free)", "multistart")
    stat("oracle over the 3 chain finals (GT)", "chain_oracle")
    stat("ref: e55 vote pick (0.695 run start)", "ref_e55_vote")
    stat("ref: 0.695 system single chain", "ref_chain1")
    stat("ref: 0.695 system (multi-start)", "ref_695")
    stat("ref: 0.695 oracle over chain finals", "ref_chain_oracle")
    nmiss = sum(r.get("missing_chains", 0) for r in rows.values())
    L.append(f"  (chain entries missing -> start kept: {nmiss})")
    L.append("\n  paired deltas [95% bootstrap CI]  (+helped / -hurt at |d| > 0.05)")
    def pair(name, ca, cb):
        rng = np.random.default_rng(0)
        ks = [k for k in keys if rows[k].get(ca) is not None and rows[k].get(cb) is not None]
        m, lo, hi, up, dn = ci([rows[k][ca] for k in ks], [rows[k][cb] for k in ks], rng)
        L.append(f"  {name:52s} {m:+.3f} [{lo:+.3f},{hi:+.3f}]  +{up}/-{dn}  n={len(ks)}")
        for fam in ("A", "F"):
            kf = [k for k in ks if k[0] == fam]
            m, lo, hi, up, dn = ci([rows[k][ca] for k in kf], [rows[k][cb] for k in kf], np.random.default_rng(0))
            L.append(f"      {('ABC' if fam == 'A' else 'Fusion'):48s} {m:+.3f} [{lo:+.3f},{hi:+.3f}]  +{up}/-{dn}  n={len(kf)}")
    pair("multi-start  vs  0.695 system (per part)", "multistart", "ref_695")
    pair("multi-start  vs  e55 vote pick", "multistart", "ref_e55_vote")
    pair("multi-start  vs  GRPO K=16 selected pick (repair adds)", "multistart", "k16_sel")
    pair("multi-start  vs  single chain", "multistart", "chain1")
    pair("single chain vs  K=16 selected pick", "chain1", "k16_sel")
    pair("single chain vs  0.695 system's single chain", "chain1", "ref_chain1")
    pair("K=16 selected pick vs K=16 vote", "k16_sel", "k16_vote")
    pair("K=16 selected pick vs e55 vote pick", "k16_sel", "ref_e55_vote")
    pair("K=16 selected pick vs 0.695 system", "k16_sel", "ref_695")
    pair("chain oracle vs 0.695 chain oracle", "chain_oracle", "ref_chain_oracle")
    txt = "\n".join(L)
    print(txt)
    open(a.out + "_table.txt", "w").write(txt + "\n")
    with open(a.out + "_per_part.jsonl", "w") as f:
        for k in keys:
            f.write(json.dumps({"key": k, **rows[k]}) + "\n")


if __name__ == "__main__":
    main()
