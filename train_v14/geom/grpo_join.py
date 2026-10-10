"""Paired training-curve check for a GRPO arm: join its rollouts against e55's own best-of-K on the
SAME parts, per block of steps. Raw `mean_reward` curves are dominated by which parts a step drew
(2026-10-06: the "indist 0.645 -> 0.85" rise was mostly part sampling); the per-part delta is not.

    python grpo_join.py <arm>/rollouts.jsonl <baseline.json>[,<baseline2.json>,...] [--parts-per-step 16] [--block 4]

Mixed pools (`--bench a,b,c`) log parts as "<bench index>:<key>"; give one baseline per bench, in
--bench order. Repair prompts ("<part>#<cand>") join on their part. Baselines are score_partials /
bestofn json ({"candidates": [{"key", "cands": [{iou, exec, draw}]}]}); only the first K=8 draws count.
"""
import argparse
import json

import numpy as np


def load_base(f, k=8):
    out = {}
    for p in json.load(open(f))["candidates"]:
        c = sorted(p["cands"], key=lambda c: c.get("draw", 0))[:k]
        out[p.get("key") or p.get("part")] = (np.mean([float(x.get("iou") or 0) for x in c]),
                                              np.mean([bool(x.get("exec")) for x in c]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rollouts")
    ap.add_argument("baselines", help="comma list, one per --bench entry")
    ap.add_argument("--parts-per-step", type=int, default=16)
    ap.add_argument("--block", type=int, default=4, help="steps per printed row")
    a = ap.parse_args()
    bases = [load_base(f) for f in a.baselines.split(",")]
    rows = []
    for i, line in enumerate(open(a.rollouts)):
        r = json.loads(line)
        part = r["part"].split("#", 1)[0]
        bi, key = (int(part.split(":", 1)[0]), part.split(":", 1)[1]) if ":" in part else (0, part)
        b = bases[bi].get(key) if bi < len(bases) else None
        if b is None:
            continue
        ex = np.mean([c["exec"] for c in r["cands"]])
        rows.append((i // a.parts_per_step, np.mean(r["rewards"]), b[0], ex, b[1]))
    if not rows:
        print("no joined rows")
        return
    x = np.array(rows)
    print(f"{a.rollouts}: joined {len(x)} part-groups")
    for lo in range(0, int(x[:, 0].max()) + 1, a.block):
        m = (x[:, 0] >= lo) & (x[:, 0] < lo + a.block)
        if m.any():
            y = x[m]; d = y[:, 1] - y[:, 2]
            print(f"  steps {lo:3d}-{lo + a.block - 1:3d} n={m.sum():3d} arm {y[:, 1].mean():.3f} e55 {y[:, 2].mean():.3f} "
                  f"d {d.mean():+.3f} (se {d.std() / np.sqrt(len(d)):.3f}) | exec arm {y[:, 3].mean():.2f} e55 {y[:, 4].mean():.2f}")
    d = x[:, 1] - x[:, 2]
    print(f"  ALL d {d.mean():+.3f} (se {d.std() / np.sqrt(len(d)):.3f})")


if __name__ == "__main__":
    main()
