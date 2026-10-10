"""Per-part served output of the deployed real-bench system (e55 vote pick -> rp3 repair chains ->
multi-start v3 pick, 0.695 on the 143-part permissive bench), plus the e55 best-of-8 vote stage.
Same selection rule as multistart_combine.py.

    python train_v14/geom/real_parts_served.py   -> results/figures/real_parts/served.json
"""
import json

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
CHAINS = [f"{DV}/results/repair/{c}.jsonl" for c in ("sys_pooled_rp3_rep_r32_r6", "sys_rp3_rank2_r6", "sys_rp3_rank3_r6")]
BO8 = f"{DV}/results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423.json"
CONS = f"{DV}/results/ext/bo8_ext_dw423p_e55-rft-real-u5-gt-dw423_consistency.json"


def final(r):
    h = r["hist"]; x = h[0]
    for y in h[1:]:
        if y.get("adopted"):
            x = y
    return x


chains = [{json.loads(l)["key"]: json.loads(l) for l in open(f)} for f in CHAINS]
cons = json.load(open(CONS)); cparts = {p["key"]: p for p in cons["parts"]}
rows = []
for k in sorted(chains[0]):
    fs = [(ci, final(c[k])) for ci, c in enumerate(chains) if k in c]
    ci, best = max(fs, key=lambda t: t[1].get("v3", 0))
    pp = cons["per_part"].get(k, {})
    rows.append({"key": k, "family": k[0], "served_iou": best["iou"], "served_code": best["code"], "served_chain": ci,
                 "served_round": best["round"], "vote_iou": pp.get("consistency"), "first_iou": pp.get("first_exec"),
                 "oracle8": pp.get("oracle"), "n_exec8": sum(cparts[k]["exec"]) if k in cparts else None})
json.dump(rows, open(f"{DV}/results/figures/real_parts/served.json", "w"), indent=1)
s = [r["served_iou"] for r in rows]
print(f"n={len(rows)} served mean {sum(s)/len(s):.3f}; >=0.85: {sum(x >= 0.85 for x in s)}; >=0.9: {sum(x >= 0.9 for x in s)}; "
      f"vote>=0.85: {sum((r['vote_iou'] or 0) >= 0.85 for r in rows)}")
