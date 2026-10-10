"""Held-out summary for the T0-regime DeepSeek GRPO loop (2026-10-07): one episode per part (<= 3 calls), final
program's centred IoU (exec failures = 0), paired vs the u0 eval with a 2,000-sample bootstrap CI.
    python dsv41_t0_eval_summary.py --evals 'grpo_ds/<run>/eval_u*/ep.jsonl' --base grpo_ds/<run>/eval_u00/ep.jsonl"""
import argparse, glob, json, random, re


def load(f):
    out, ex, first = {}, 0, {}
    for l in open(f):
        r = json.loads(l)
        out[r["key"]] = r["iou"] if r.get("exec") else 0.0; ex += bool(r.get("exec"))
        t = r["turns"][0] if r["turns"] else {}
        first[r["key"]] = t.get("iou", 0.0) if t.get("exec") else 0.0
    return out, ex, first


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--evals", required=True); ap.add_argument("--base", required=True); ap.add_argument("--out", default="")
    a = ap.parse_args(); base, _, _ = load(a.base); rows = []
    for f in sorted(glob.glob(a.evals)):
        s, ex, first = load(f); keys = sorted(set(s) & set(base)); n = len(keys)
        if not n: continue
        d = [s[k] - base[k] for k in keys]; rng = random.Random(0)
        bs = sorted(sum(d[rng.randrange(n)] for _ in range(n)) / n for _ in range(2000))
        m = re.search(r"eval_u(\d+)", f)
        rows.append({"policy": int(m.group(1)) if m else -1, "n": n, "mean": sum(s[k] for k in keys) / n, "delta": sum(d) / n,
                     "ci": [bs[50], bs[1949]], "exec": ex, "ge80": sum(s[k] >= 0.8 for k in keys),
                     "first_call_mean": sum(first.get(k, 0.0) for k in keys) / n})
    for r in rows:
        print(f"u{r['policy']:02d}  n {r['n']}  mean {r['mean']:.3f}  vs u0 {r['delta']:+.3f} [{r['ci'][0]:+.3f},{r['ci'][1]:+.3f}]  "
              f"exec {r['exec']}  >=0.8 {r['ge80']}  first-call-only {r['first_call_mean']:.3f}")
    if a.out:
        json.dump(rows, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
