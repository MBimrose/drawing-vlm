"""Expert-iteration round-2 tier (2026-10-09, GRPO_HANDOFF "Expert-iteration round 2"). Per TRAINING part, the single
best GT-verified program among
  rl    round-2 policy K=16 samples (own think + code, executing),           --part ...:<k16 json[,json]>:...
  gts   GT-selected rp3 repair-search result, with a STaR-rationalized think  --part ...:...:<rationalized bank json[,json]>
        in the policy's voice (geom/build_guide_bank.py output {key: {code, iou, think}}; also teacher programs),
  tier1 the round-1 tier row (results/guide/rft1/tier/accepted-000.jsonl; union: kept where round 2 does not improve),
kept if IoU >= --min-iou. Ties prefer rl > tier1 > gts (the model's own voice first). Sheet PNG = the bench's
eval_cache_v15 sheet (exact RL/eval prompt image). Hard error on any held-out file_id (build_rft1_tier.py rule).
Also reports capability expansion: parts kept now that had NO >= min-iou program in round 1 (and none among the
--prior scored files, e.g. e55 best-of-32 / best-of-8 and the realpool2 RL K=4 mining draws).
    python build_rft2_tier.py --out <dir> --tier1 <accepted-000.jsonl> \
      --part <bench_dir>:<k16 json,...>:<bank json,...> [--part ...] [--prior <scored json> ...] [--min-iou 0.75]
Writes <out>/accepted-000.jsonl ({key, iou, think, code, src, bench}), <out>/png/<key>.png, <out>/tier_stats.json,
<out>/new_keys.json."""
import argparse, json, os, pickle, sys
from collections import Counter

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
BD = f"{DV}/train_v14/mech/benchmarks/data"


def file_id(key):
    return key.split("_", 1)[1].rsplit("_", 1)[0]


def fnum(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


ap = argparse.ArgumentParser()
ap.add_argument("--out", required=True); ap.add_argument("--tier1", required=True)
ap.add_argument("--part", action="append", required=True); ap.add_argument("--prior", action="append", default=[])
ap.add_argument("--min-iou", type=float, default=0.75)
a = ap.parse_args()

held = set(l.strip() for l in open(f"{BD}/heldout_file_ids.txt") if l.strip())
for hb in ("ext_bench_dw423_perm", "ext_bench_dw423", "ext_bench"):
    p = f"{BD}/{hb}/manifest.json"
    if os.path.exists(p):
        held |= {file_id(k) for k in json.load(open(p))["parts"]}
print(f"[tier2] {len(held)} held-out file_ids", flush=True)

t1 = {}
for l in open(a.tier1):
    r = json.loads(l); t1[r["key"]] = r
prior = {}  # best IoU any earlier model reached (for the 'new vs everything' count)
for f in a.prior:
    for p in json.load(open(f))["candidates"]:
        b = max((fnum(c.get("iou")) or 0 for c in p["cands"] if c.get("exec")), default=0.0)
        prior[p["key"]] = max(prior.get(p["key"], 0.0), b)
RANK = {"rl": 0, "tier1": 1, "gts": 2}
os.makedirs(f"{a.out}/png", exist_ok=True)
rows, stats, new = [], {}, {}
for spec in a.part:
    bench, k16s, banks = spec.split(":")
    tag = os.path.basename(bench)
    best, keys = {}, set()

    def offer(k, i, src, think, code):
        cur = best.get(k)
        if cur is None or i > cur[0] or (i == cur[0] and RANK[src] < RANK[cur[1]]):
            best[k] = (i, src, think, code)
    n_rl = n_bank = 0
    for f in filter(None, k16s.split(",")):
        for p in json.load(open(f))["candidates"]:
            keys.add(p["key"])
            for c in p["cands"]:
                i = fnum(c.get("iou"))
                if i is None or not c.get("code") or not (c.get("think") or "").strip() or not c.get("exec"):
                    continue
                n_rl += 1; offer(p["key"], i, "rl", c["think"].strip(), c["code"])
    for f in filter(None, banks.split(",")):
        for k, v in json.load(open(f)).items():
            i = fnum(v.get("iou"))
            if k not in keys or i is None or not v.get("code") or not (v.get("think") or "").strip():
                continue
            n_bank += 1; offer(k, i, "gts", v["think"].strip(), v["code"])
    for k in keys:
        if k in t1:
            r = t1[k]; offer(k, float(r["iou"]), "tier1", r["think"].strip(), r["code"])
    cache = pickle.load(open(f"{bench}/eval_cache_v15.pkl", "rb"))["samples"]
    st = Counter(parts=len(keys), rl_cands=n_rl, bank_entries=n_bank)
    for k, (i, src, think, code) in sorted(best.items()):
        if file_id(k) in held:
            sys.exit(f"[tier2] FATAL: {k} ({tag}) is a held-out bench part")
        if i < a.min_iou:
            st["below"] += 1; continue
        s = cache.get(k)
        if not s or not s.get("png"):
            st["no_png"] += 1; continue
        with open(f"{a.out}/png/{k}.png", "wb") as fh:
            fh.write(s["png"])
        is_new = k not in t1
        rows.append({"key": k, "iou": i, "think": think, "code": code, "src": src, "bench": tag, "new_vs_tier1": is_new,
                     "new_vs_all": is_new and prior.get(k, 0.0) < a.min_iou})
        st["kept"] += 1; st[f"kept_{src}"] += 1; st[f"fam_{k[0]}"] += 1
        if is_new:
            st["new_vs_tier1"] += 1; st[f"new_fam_{k[0]}"] += 1; st[f"new_src_{src}"] += 1
            st["new_vs_all"] += rows[-1]["new_vs_all"]
            new[k] = {"iou": i, "src": src, "prior_best": prior.get(k), "bench": tag}
        elif i > float(t1[k]["iou"]) + 1e-9:
            st["improved_tier1"] += 1
    kept = [r["iou"] for r in rows if r["bench"] == tag]
    st = dict(st); st["mean_iou_kept"] = round(sum(kept) / max(1, len(kept)), 4)
    st["ge_0.9"] = sum(x >= 0.9 for x in kept)
    stats[tag] = st
    print(f"[tier2] {tag}: {st}", flush=True)
    del cache

# union: round-1 tier rows of parts that no round-2 spec covered are carried over unchanged
covered = {r["key"] for r in rows}
seen_keys = set()
for spec in a.part:
    for f in filter(None, spec.split(":")[1].split(",")):
        seen_keys |= {p["key"] for p in json.load(open(f))["candidates"]}
carried = 0
for k, r in t1.items():
    if k in seen_keys or k in covered:
        continue
    src_png = os.path.join(os.path.dirname(a.tier1), "png", f"{k}.png")
    if not os.path.exists(src_png):
        sys.exit(f"[tier2] FATAL: no round-1 png for {k}")
    if file_id(k) in held:
        sys.exit(f"[tier2] FATAL: {k} is a held-out bench part")
    with open(src_png, "rb") as fi, open(f"{a.out}/png/{k}.png", "wb") as fo:
        fo.write(fi.read())
    rows.append({"key": k, "iou": float(r["iou"]), "think": r["think"], "code": r["code"], "src": "tier1",
                 "bench": r["bench"], "new_vs_tier1": False, "new_vs_all": False})
    carried += 1

assert len({r["key"] for r in rows}) == len(rows), "key collision across benches"
with open(f"{a.out}/accepted-000.jsonl", "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
json.dump(new, open(f"{a.out}/new_keys.json", "w"), indent=0)
tot = {"rows": len(rows), "mean_iou": round(sum(r["iou"] for r in rows) / max(1, len(rows)), 4),
       "by_src": dict(Counter(r["src"] for r in rows)), "iou_ge_0.9": sum(r["iou"] >= 0.9 for r in rows),
       "new_vs_tier1": sum(r["new_vs_tier1"] for r in rows), "new_vs_all": sum(r["new_vs_all"] for r in rows),
       "new_by_family": dict(Counter(r["key"][0] for r in rows if r["new_vs_tier1"])),
       "carried_tier1_unsampled": carried, "tier1_rows": len(t1), "per_bench": stats, "min_iou": a.min_iou}
json.dump(tot, open(f"{a.out}/tier_stats.json", "w"), indent=1)
print(f"[tier2] TOTAL {json.dumps({k: v for k, v in tot.items() if k != 'per_bench'})}", flush=True)
