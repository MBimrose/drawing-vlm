"""Selection study on RL-generator candidates (2026-10-07, GRPO_HANDOFF "Selection on RL candidates").

Label-free selectors over the stored K-draw candidates of one or more models on the same bench, paired against
the consistency vote of the same model and against a control model's vote, with 2,000-sample bootstrap 95% CIs
(geom/grpo_eval_summary.py style). Inputs per model (name=...):
  cands      merged candidates JSON (exec / iou per draw; read exec+iou from HERE, never from the consistency file)
  cons       consistency_rerank output (parts[].pair_iou indexed by candidate position)
  vpreds     sel_vscore.py / verifier_select_offline preds ({key: [[pred,...]|null per draw]})   [optional]
  rc         rc_metric2 output (on a sel_concat.py file: rc_offset = first candidate index of this model)  [optional]

    python sel_study.py --spec specs.json --control e55ctl --k 8 [--k 16 32] --out results/selection/sel_k8.json

specs.json: {"<name>": {"cands": ..., "cons": ..., "vpreds": ..., "rc": ..., "rc_offset": 8}}
"""
from __future__ import annotations

import argparse
import json

import numpy as np

GATES = (0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95)
TOPK = (2, 3, 4)


def load_model(spec, rc_cache):
    parts = {}
    for p in json.load(open(spec["cands"]))["candidates"]:
        cs = sorted(p["cands"], key=lambda c: int(c.get("draw", 0)))
        parts[p["key"]] = {"exec": [bool(c.get("exec")) and bool((c.get("code") or "").strip()) for c in cs],
                           "iou": [float(c.get("iou") or 0.0) for c in cs]}
    mats = {cp["key"]: cp["pair_iou"] for cp in json.load(open(spec["cons"]))["parts"]}
    for k, p in parts.items():
        n = len(p["iou"])
        p["mat"] = mats.get(k) or [[None] * n for _ in range(n)]
        assert len(p["mat"]) == n, (k, len(p["mat"]), n)
    if spec.get("vpreds"):
        pr = json.load(open(spec["vpreds"]))
        for k, p in parts.items():
            v = pr.get(k) or [None] * len(p["iou"])
            assert len(v) == len(p["iou"])
            p["ver"] = [None if x is None else float(x[0]) for x in v]
    if spec.get("rc"):
        if spec["rc"] not in rc_cache:
            rc_cache[spec["rc"]] = json.load(open(spec["rc"]))
        d = rc_cache[spec["rc"]]
        for rp in d["parts"]:
            if rp["key"] not in parts:
                continue
            p = parts[rp["key"]]
            off = int(spec.get("rc_offset", 0))
            rows = rp["cands"][off:off + len(p["iou"])]
            assert len(rows) == len(p["iou"]), (rp["key"], len(rows), len(p["iou"]))
            if spec.get("rc_check", True):   # rc run on scored candidates: rows must line up with the cands file
                for c, t in zip(rows, p["iou"]):
                    assert abs(float(c["iou"]) - t) < 1e-6, (rp["key"], c["iou"], t)
            p["v3"] = [float(c.get("v3", 0.0)) for c in rows]
    return parts


def argmax(idx, f):
    best, bv = None, None
    for j in idx:
        v = f(j)
        if bv is None or v > bv:
            best, bv = j, v
    return best


def ranks(idx, f):
    from scipy.stats import rankdata
    r = rankdata([f(j) for j in idx])
    return {j: float(x) for j, x in zip(idx, r)}


def select(p, K):
    ex = [j for j in range(min(K, len(p["iou"]))) if p["exec"][j]]
    iou = p["iou"]
    has_v, has_r = "ver" in p, "v3" in p
    out = {}
    if not ex:
        return None
    m = p["mat"]
    agree = {j: (float(np.mean([(m[j][i] or 0.0) for i in ex if i != j])) if len(ex) > 1 else 0.0) for j in ex}
    jm = argmax(ex, lambda j: agree[j]); amax = agree[jm]
    out["first_exec"] = iou[ex[0]]
    out["vote"] = iou[jm]
    out["oracle"] = max(iou[j] for j in ex)
    topa = sorted(ex, key=lambda j: (-agree[j], j))
    if has_v:
        ver = {j: (p["ver"][j] if p["ver"][j] is not None else -1.0) for j in ex}
        jv = argmax(ex, lambda j: ver[j])
        out["verifier"] = iou[jv]
        for t in GATES:
            out[f"gate{t}"] = iou[jm] if amax >= t else iou[jv]
        for k in TOPK:
            out[f"ver|top{k}agree"] = iou[argmax(topa[:k], lambda j: ver[j])]
        topv = sorted(ex, key=lambda j: (-ver[j], j))[:4]
        out["vote|top4ver"] = iou[argmax(topv, lambda j: float(np.mean([(m[j][i] or 0.0) for i in topv if i != j])) if len(topv) > 1 else 0)]
        out["agree+ver"] = iou[argmax(ex, lambda j: agree[j] + ver[j])]
        ra, rv = ranks(ex, lambda j: agree[j]), ranks(ex, lambda j: ver[j])
        out["rank(agree,ver)"] = iou[argmax(ex, lambda j: ra[j] + rv[j])]
    if has_r:
        v3 = {j: p["v3"][j] for j in ex}
        j3 = argmax(ex, lambda j: v3[j])
        out["rc_v3"] = iou[j3]
        for k in TOPK:
            out[f"v3|top{k}agree"] = iou[argmax(topa[:k], lambda j: v3[j])]
        for t in (0.7, 0.85):
            out[f"gate{t}->v3"] = iou[jm] if amax >= t else iou[j3]
        out["agree+v3"] = iou[argmax(ex, lambda j: agree[j] + v3[j])]
        ra, r3 = ranks(ex, lambda j: agree[j]), ranks(ex, lambda j: v3[j])
        out["rank(agree,v3)"] = iou[argmax(ex, lambda j: ra[j] + r3[j])]
        if has_v:
            out["ver+v3"] = iou[argmax(ex, lambda j: ver[j] + v3[j])]
            out["agree+ver+v3"] = iou[argmax(ex, lambda j: agree[j] + ver[j] + v3[j])]
            rv = ranks(ex, lambda j: ver[j])
            out["rank(agree,ver,v3)"] = iou[argmax(ex, lambda j: ra[j] + rv[j] + r3[j])]
            for k in TOPK:
                out[f"(ver+v3)|top{k}agree"] = iou[argmax(topa[:k], lambda j: ver[j] + v3[j])]
            for t in (0.7, 0.85):
                out[f"gate{t}->ver+v3"] = iou[jm] if amax >= t else iou[argmax(ex, lambda j: ver[j] + v3[j])]
    return out


def ci(d, rng, n=2000):
    bs = rng.choice(d, (n, len(d))).mean(1)
    return float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--control", default="e55ctl")
    ap.add_argument("--k", type=int, nargs="+", default=[8])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    specs = json.load(open(a.spec))
    rc_cache = {}
    models = {n: load_model(s, rc_cache) for n, s in specs.items()}
    res = {"spec": specs, "by_k": {}}
    lines = []
    for K in a.k:
        per = {}
        for n, parts in models.items():
            if K > min(len(p["iou"]) for p in parts.values()):
                continue
            rows = {}
            for key, p in parts.items():
                s = select(p, K)
                rows[key] = s
            names = next(r for r in rows.values() if r is not None).keys()
            per[n] = {key: (r if r is not None else {nm: 0.0 for nm in names}) for key, r in rows.items()}
        ctl = per.get(a.control)
        if ctl is None and a.control in models:   # control has fewer draws (e.g. K=8 e55ctl vs K=32): its own full-K vote
            cm = models[a.control]; kc = min(len(p["iou"]) for p in cm.values())
            ctl = {key: (select(p, kc) or {"vote": 0.0}) for key, p in cm.items()}
        res["by_k"][str(K)] = {"per_part": per, "summary": {}}
        for n, rows in per.items():
            rng = np.random.default_rng(0)
            keys = sorted(rows)
            names = list(next(iter(rows.values())).keys())
            vote = np.array([rows[k]["vote"] for k in keys]); orc = np.array([rows[k]["oracle"] for k in keys])
            gap = orc.mean() - vote.mean()
            lines.append(f"\n== {n}  K={K}  n={len(keys)}  vote {vote.mean():.3f}  oracle {orc.mean():.3f}  "
                         f"(vote->oracle gap {gap:.3f})")
            lines.append(f"  {'selector':22s} {'mean':>6s} {'>=.85':>6s}  {'d vs vote [95% CI]':>26s}  {'gap closed':>10s}"
                         + (f"  {'d vs ' + a.control + ' vote [95% CI]':>30s}" if ctl is not None and n != a.control else ""))
            summ = {}
            for nm in names:
                v = np.array([rows[k][nm] for k in keys])
                d = v - vote; lo, hi = ci(d, rng)
                row = {"mean": float(v.mean()), "ge85": float((v >= 0.85).mean()), "d_vote": float(d.mean()),
                       "d_vote_ci": [lo, hi], "gap_closed": float(d.mean() / gap) if gap > 0 else float("nan")}
                txt = (f"  {nm:22s} {v.mean():6.3f} {100*(v >= 0.85).mean():5.0f}%  {d.mean():+.3f} [{lo:+.3f},{hi:+.3f}]"
                       f"          {row['gap_closed']*100:6.0f}%")
                if ctl is not None and n != a.control:
                    kc = [k for k in keys if k in ctl]
                    dc = np.array([rows[k][nm] - ctl[k]["vote"] for k in kc]); lo2, hi2 = ci(dc, rng)
                    row.update({"d_ctlvote": float(dc.mean()), "d_ctlvote_ci": [lo2, hi2]})
                    txt += f"  {dc.mean():+.3f} [{lo2:+.3f},{hi2:+.3f}]"
                summ[nm] = row
                lines.append(txt)
            res["by_k"][str(K)]["summary"][n] = summ
    txt = "\n".join(lines)
    print(txt)
    res["table"] = txt
    json.dump(res, open(a.out, "w"), indent=1)
    open(a.out.rsplit(".json", 1)[0] + "_table.txt", "w").write(txt + "\n")


if __name__ == "__main__":
    main()
