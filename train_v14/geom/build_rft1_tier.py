"""RFT consolidation tier (2026-10-08, GRPO_HANDOFF "RFT consolidation cycle"): per hard real training part, the single
best GT-verified program among {RL K=16 samples (mix_t10 s120, T=1.0; own think + code), bank entry (GT-search program
with its rationalized e55-voice plan)}, kept if IoU >= --min-iou. Writes <out>/accepted-000.jsonl ({key, iou, think,
code, src}) + <out>/png/<key>.png from the bench's eval_cache_v15 (the exact sheet the RL/eval prompts use), ready for
pack_rft_shards_dir.py. Parts whose file_id is on a held-out real bench are refused (hard error).
    python build_rft1_tier.py --out <tier dir> \
      --part <bench_dir>:<rl_bo_json or ''>:<bank_json or ''> [--part ...] [--min-iou 0.75]"""
import argparse, json, os, pickle, sys

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
BD = f"{DV}/train_v14/mech/benchmarks/data"


def file_id(key):  # = pack_scored_real.file_id
    return key.split("_", 1)[1].rsplit("_", 1)[0]


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True)
ap.add_argument("--part", action="append", required=True)
ap.add_argument("--min-iou", type=float, default=0.75)
a = ap.parse_args()

held = set(l.strip() for l in open(f"{BD}/heldout_file_ids.txt") if l.strip())
for hb in ("ext_bench_dw423_perm", "ext_bench_dw423", "ext_bench"):
    p = f"{BD}/{hb}/manifest.json"
    if os.path.exists(p):
        held |= {file_id(k) for k in json.load(open(p))["parts"]}
print(f"[tier] {len(held)} held-out file_ids", flush=True)

os.makedirs(f"{a.out}/png", exist_ok=True)
rows, stats = [], {}
for spec in a.part:
    bench, rl, bank = spec.split(":")
    tag = os.path.basename(bench)
    cache = pickle.load(open(f"{bench}/eval_cache_v15.pkl", "rb"))["samples"]
    best = {}  # key -> (iou, src, think, code)
    n_rl = n_bank = 0
    if rl:
        for p in json.load(open(rl))["candidates"]:
            for c in p["cands"]:
                i = fnum(c.get("iou"))
                if i is None or not c.get("code") or not (c.get("think") or "").strip():
                    continue
                if str(c.get("exec")).lower() not in ("true", "1"):
                    continue
                n_rl += 1
                if p["key"] not in best or i > best[p["key"]][0]:
                    best[p["key"]] = (i, "rl", c["think"].strip(), c["code"])
    if bank:
        for k, v in json.load(open(bank)).items():
            i = fnum(v.get("iou"))
            if i is None or not v.get("code") or not (v.get("think") or "").strip():
                continue
            n_bank += 1
            if k not in best or i > best[k][0]:   # ties keep the RL sample (the model's own voice)
                best[k] = (i, "bank", v["think"].strip(), v["code"])
    st = {"parts": len(best), "rl_cands": n_rl, "bank_entries": n_bank, "kept": 0, "kept_rl": 0, "kept_bank": 0,
          "below": 0, "no_png": 0}
    for k, (i, src, think, code) in sorted(best.items()):
        if file_id(k) in held:
            sys.exit(f"[tier] FATAL: {k} ({tag}) is a held-out bench part")
        if i < a.min_iou:
            st["below"] += 1; continue
        s = cache.get(k)
        if not s or not s.get("png"):
            st["no_png"] += 1; continue
        with open(f"{a.out}/png/{k}.png", "wb") as f:
            f.write(s["png"])
        rows.append({"key": k, "iou": i, "think": think, "code": code, "src": src, "bench": tag})
        st["kept"] += 1; st[f"kept_{src}"] += 1
    st["mean_iou_kept"] = round(sum(r["iou"] for r in rows if r["bench"] == tag) / max(1, st["kept"]), 4)
    stats[tag] = st
    print(f"[tier] {tag}: {st}", flush=True)
    del cache

assert len({r["key"] for r in rows}) == len(rows), "key collision across benches"
with open(f"{a.out}/accepted-000.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
tot = {"rows": len(rows), "mean_iou": round(sum(r["iou"] for r in rows) / max(1, len(rows)), 4),
       "from_rl": sum(r["src"] == "rl" for r in rows), "from_bank": sum(r["src"] == "bank" for r in rows),
       "iou_ge_0.9": sum(r["iou"] >= 0.9 for r in rows), "per_bench": stats, "min_iou": a.min_iou}
json.dump(tot, open(f"{a.out}/tier_stats.json", "w"), indent=1)
print(f"[tier] TOTAL {json.dumps({k: v for k, v in tot.items() if k != 'per_bench'})}", flush=True)
