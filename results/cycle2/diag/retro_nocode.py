"""Retro check (2026-10-09): did earlier collapsed GRPO runs fail through no-code completions (the format blind spot)?
Per run: steps aligned from round_log.jsonl ('parts' rollout lines per step); per 10-step bin on-policy exec rate,
no-code share (code_chars == 0), share of failures that are no-code. Guide (injected) rows excluded.
    python retro_nocode.py <runs dir> <arm> [<arm> ...]"""
import json, os, sys
root = sys.argv[1]
for arm in sys.argv[2:]:
    d = os.path.join(root, f"grpo_v_{arm}")
    if not os.path.exists(os.path.join(d, "rollouts.jsonl")): print(f"{arm}: no rollouts"); continue
    R = [json.loads(l) for l in open(os.path.join(d, "rollouts.jsonl"))]
    L = [json.loads(l) for l in open(os.path.join(d, "round_log.jsonl"))]
    i, bins = 0, {}
    for r in L:
        for x in R[i:i + r["parts"]]:
            b = bins.setdefault(r["step"] // 10 * 10, [0, 0, 0])
            for c in x["cands"]:
                if c.get("guide"): continue
                b[0] += 1; b[1] += c["exec"]; b[2] += c["code_chars"] == 0
        i += r["parts"]
    print(f"== {arm} ({len(L)} steps; aligned {i}/{len(R)} rollout lines)")
    for s in sorted(bins):
        n, e, nc = bins[s]
        print(f"  s{s:3d}-{s+9:3d} n={n:5d} exec={e/n:.3f} nocode={nc/n:.3f} nocode/fail={nc/max(1,n-e):.2f}")
