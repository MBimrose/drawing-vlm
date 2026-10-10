"""Held-out real-bench summary for the DeepSeek GRPO loop (2026-10-06): one sampled draw per part per eval,
mean centred IoU (exec failures = 0), paired difference vs the round-0 (vanilla) eval with a 2,000-sample bootstrap CI.
    python dsv41_grpo_eval_summary.py --evals 'grpo_ds/run/eval_u*/scored_ext_bench_dw423_perm.json' --base <round-0 file>
"""
import argparse, glob, json, os, random, re


def load(f):
    d = json.load(open(f)); out = {}
    for p in d["candidates"]:
        c = sorted(p["cands"], key=lambda c: c.get("draw", 0))[0]
        out[p["key"]] = float(c.get("iou", 0.0)) if c.get("exec") else 0.0
    ex = sum(1 for p in d["candidates"] if sorted(p["cands"], key=lambda c: c.get("draw", 0))[0].get("exec"))
    return out, ex


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--evals", required=True); ap.add_argument("--base", required=True)
    ap.add_argument("--out", default=""); a = ap.parse_args()
    base, _ = load(a.base); rows = []
    for f in sorted(glob.glob(a.evals)):
        s, ex = load(f); keys = sorted(set(s) & set(base)); n = len(keys)
        d = [s[k] - base[k] for k in keys]; rng = random.Random(0); bs = []
        for _ in range(2000):
            smp = [d[rng.randrange(n)] for _ in range(n)]; bs.append(sum(smp) / n)
        bs.sort()
        m = re.search(r"eval_u(\d+)", f)
        rows.append({"round": int(m.group(1)) if m else -1, "file": f, "n": n, "mean": sum(s[k] for k in keys) / n,
                     "base_mean": sum(base[k] for k in keys) / n, "delta": sum(d) / n, "ci": [bs[50], bs[1949]],
                     "exec": ex, "ge80": sum(s[k] >= 0.8 for k in keys)})
    for r in rows:
        print(f"round {r['round']:2d}  n {r['n']}  mean {r['mean']:.3f}  vs r0 {r['delta']:+.3f} [{r['ci'][0]:+.3f},{r['ci'][1]:+.3f}]"
              f"  exec {r['exec']}  >=0.8 {r['ge80']}")
    if a.out:
        json.dump(rows, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
