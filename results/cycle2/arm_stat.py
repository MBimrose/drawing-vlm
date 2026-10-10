import json, sys, os
for a in sys.argv[1:]:
    f = f"runs/grpo_v_{a}/round_log.jsonl"
    if not os.path.exists(f): continue
    L = [json.loads(l) for l in open(f)][-5:]
    if not L: continue
    ex = sum(r["mean_exec"] for r in L) / len(L); h = sum(r.get("mean_entropy", 0) for r in L) / len(L)
    print(f"{a:14s} step {L[-1]['step']:3d} exec5 {ex:.3f} H5 {h:.3f} kl {L[-1]['kl']} guided {L[-1]['guided']} chars {L[-1]['mean_completion_chars']}")
