"""Kimi-trace A/B (2026-10-29): paired comparison of the round-1 arms against each other and the e55-recipe Glimmer.

  A  = aba1    own samples + 20% Kimi K3 reasoning tier (no Qwen data)
  B  = abb1    own samples, plain (no reasoning, no Qwen data)
  e55 = glftpf the e55 mix (60% Qwen-27B RFT rows + 20% Kimi + 20% plain), the paper's Glimmer FFT row

Per bench: d0 (draw 0, 0 if it did not execute) and vote (consistency medoid) means, then paired bootstrap
deltas (10,000 resamples, 95% CI) on the parts both systems scored. Report bench B (held-out); real-144 is the dev set.
    python compare_ab.py            # writes compare_ab.md next to this file
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
SYS = {"A (own + Kimi)": f"{HERE}/{{b}}_aba1_consistency.json", "B (own, plain)": f"{HERE}/{{b}}_abb1_consistency.json",
       "e55 mix": f"{HERE}/../{{b}}_glftpf_consistency.json"}
BENCH = [("benchb", "Held-out (280)"), ("full", "Synthetic (1,027)"), ("real", "Real-144 (dev)")]
PAIRS = [("A (own + Kimi)", "B (own, plain)"), ("A (own + Kimi)", "e55 mix"), ("B (own, plain)", "e55 mix")]


def load(path):
    if not os.path.exists(path):
        return None
    d = json.load(open(path))
    d0 = {p["key"]: (p["iou"][0] if p["exec"][0] else 0.0) for p in d["parts"]}
    vote = {k: v["consistency"] for k, v in d["per_part"].items()}
    return {"d0": d0, "vote": vote}


def boot(a, b, n=10000, seed=0):
    keys = sorted(set(a) & set(b)); diffs = [a[k] - b[k] for k in keys]
    rng = random.Random(seed); m = len(diffs)
    means = sorted(sum(diffs[rng.randrange(m)] for _ in range(m)) / m for _ in range(n))
    return m, sum(diffs) / m, means[int(0.025 * n)], means[int(0.975 * n)], sum(x > 0 for x in diffs), sum(x < 0 for x in diffs)


def main():
    out = ["# Kimi-trace A/B: round-1 Glimmer arms vs the e55-recipe Glimmer", ""]
    for b, title in BENCH:
        res = {s: load(p.format(b=b)) for s, p in SYS.items()}
        out += [f"## {title}", "", "| system | n | d0 | vote |", "|---|---|---|---|"]
        for s, r in res.items():
            out.append(f"| {s} | " + ("— | — | — |" if r is None else
                       f"{len(r['vote'])} | {sum(r['d0'].values()) / len(r['d0']):.3f} | {sum(r['vote'].values()) / len(r['vote']):.3f} |"))
        out += ["", "| paired Δ | metric | n | Δ [95% CI] | +/− |", "|---|---|---|---|---|"]
        for x, y in PAIRS:
            if res[x] is None or res[y] is None:
                continue
            for m in ("d0", "vote"):
                n, d, lo, hi, p, q = boot(res[x][m], res[y][m])
                out.append(f"| {x} − {y} | {m} | {n} | {d:+.3f} [{lo:+.3f}, {hi:+.3f}] | +{p}/−{q} |")
        out.append("")
    open(f"{HERE}/compare_ab.md", "w").write("\n".join(out))
    print("\n".join(out))


if __name__ == "__main__":
    main()
