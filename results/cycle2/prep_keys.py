"""Cycle-2 (expert iteration round 2, 2026-10-09) search key lists. TRAINING parts only.
A = CADBench hard parts (corpora 4/2/1) with NO >=0.75 program in the round-1 tier (results/guide/rft1/tier)
C = CADBench hard parts whose round-1 tier program is < 0.9 (room to improve)
B = realpool2_hard_4500 (DeepCAD hard subset; never in any tier)
Hard universe: c4 = real4_hard_keys U bankv2_c4 U e55-bo8 max<=0.1; c2 = c2_hard_keys U bankv2_c2 U unsolved_rft_corpus2_dw423;
c1 = keys_c1 U unsolved_rft_corpus_dw423. Hard error on any held-out file_id (build_rft1_tier.py rule)."""
import json, os, sys
DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"; B = f"{DV}/train_v14/mech/benchmarks/data"; O = f"{DV}/results/cycle2/keys"
def kl(p): return [l.strip() for l in open(p) if l.strip()]
def file_id(k): return k.split("_", 1)[1].rsplit("_", 1)[0]
held = set(kl(f"{B}/heldout_file_ids.txt"))
for hb in ("ext_bench_dw423_perm", "ext_bench_dw423", "ext_bench"):
    p = f"{B}/{hb}/manifest.json"
    if os.path.exists(p): held |= {file_id(k) for k in json.load(open(p))["parts"]}
tier = {}
for l in open(f"{DV}/results/guide/rft1/tier/accepted-000.jsonl"):
    r = json.loads(l); tier[r["key"]] = r["iou"]
e4 = {p["key"]: max(float(c.get("iou") or 0) for c in p["cands"]) for p in json.load(open(f"{DV}/results/h6c/bo8_real4_e55.json"))["candidates"]}
U = {"c4": set(kl(f"{DV}/results/h6c/real4_hard_keys.txt")) | set(json.load(open(f"{DV}/results/guide/bankv2_c4.json"))) | {k for k, v in e4.items() if v <= 0.1},
     "c2": set(kl(f"{DV}/results/h6c/c2_hard_keys.txt")) | set(json.load(open(f"{DV}/results/guide/bankv2_c2.json"))) | set(kl(f"{B}/unsolved_rft_corpus2_dw423.txt")),
     "c1": set(kl(f"{DV}/results/guide/keys_c1.txt")) | set(kl(f"{B}/unsolved_rft_corpus_dw423.txt"))}
bench = {"c4": "rft_corpus4", "c2": "rft_corpus2_dw423", "c1": "rft_corpus_dw423"}
st = {}
allk = []
for c, s in U.items():
    gt = {x[:-4] for x in os.listdir(f"{B}/{bench[c]}/gt_meshes_v15")}
    s = sorted(k for k in s if k in gt)
    A = [k for k in s if k not in tier]; C = [k for k in s if k in tier and tier[k] < 0.9]
    open(f"{O}/A_{c}.txt", "w").write("\n".join(A) + "\n"); open(f"{O}/C_{c}.txt", "w").write("\n".join(C) + "\n")
    st[c] = {"universe": len(s), "A_noTier": len(A), "C_tierLt0.9": len(C), "tier_ge0.9": len(s) - len(A) - len(C)}
    allk += A + C
rp = kl(f"{DV}/results/h6c/realpool2_hard_4500.txt"); open(f"{O}/B_rp2.txt", "w").write("\n".join(rp) + "\n")
st["rp2"] = {"B": len(rp)}; allk += rp
bad = [k for k in allk if file_id(k) in held]
if bad: sys.exit(f"FATAL held-out overlap: {bad[:5]} ({len(bad)})")
assert len(set(allk)) == len(allk), "key collision"
st["heldout_file_ids_checked"] = len(held); st["total_parts"] = len(allk)
json.dump(st, open(f"{O}/keys_stats.json", "w"), indent=1); print(json.dumps(st))
