"""Offline analysis for mechanism 2 on the stored champion candidates.

Questions (no GPU):
  1. How much of the failure mass is envelope-level (built bbox != GT bbox)
     or hole-count-level (mesh genus != GT genus)?  [uses GT: diagnosis only]
  2. Does envelope agreement across the 8 candidates predict a wrong candidate,
     and does gating the consistency medoid on the majority envelope / genus
     change the served number?  [no GT in selection]
  3. On RFT-scored candidates that carry a <think> plan: does the envelope the
     model STATES in its plan match what it BUILT, and is the stated envelope
     right more often than the built one (= what a verify/repair loop could
     recover)?

    python analyze_envelope.py --bo8 out/env_bo8_full_e24.jsonl \
        --cons results/bo8_full_e24_consistency_v2.json --scored out/env_scored_v1.jsonl
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict

import numpy as np


def load_jsonl(p):
    with open(p) as f:
        return [json.loads(l) for l in f if l.strip()]


def env_key(ext, q=0.5):
    return tuple(sorted(round(round(e / q) * q, 3) for e in ext))


def env_match(a, b, rel=0.02, absol=0.5):
    a, b = sorted(a), sorted(b)
    return all(abs(x - y) <= max(absol, rel * max(x, y)) for x, y in zip(a, b))


def auroc(scores, labels):
    """AUROC of score for label==1 (rank-based)."""
    s = np.asarray(scores, float); y = np.asarray(labels, bool)
    if y.all() or (~y).all():
        return float("nan")
    order = s.argsort(); ranks = np.empty(len(s)); ranks[order] = np.arange(1, len(s) + 1)
    # average ranks for ties
    for v in np.unique(s):
        m = s == v
        if m.sum() > 1:
            ranks[m] = ranks[m].mean()
    n1 = y.sum(); n0 = len(y) - n1
    return float((ranks[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))


def summarize(ious):
    ious = list(ious); n = len(ious)
    return {"mean": round(sum(ious) / n, 4), "iou85": round(sum(i >= 0.85 for i in ious) / n, 4),
            "median": round(sorted(ious)[n // 2], 4)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bo8", required=True)
    ap.add_argument("--cons", default="/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/results/bo8_full_e24_consistency_v2.json")
    ap.add_argument("--scored", default="")
    ap.add_argument("--out", default="")
    args = ap.parse_args()
    report = {}

    recs = load_jsonl(args.bo8)
    by_part = defaultdict(dict)
    for r in recs:
        by_part[r["key"]][r["draw"]] = r
    print(f"[bo8] {len(recs)} candidates, {len(by_part)} parts")

    # ---------------- 1. candidate-level diagnosis (uses GT) ----------------
    ex = [r for r in recs if r["built"] and r["gt"]]
    env_ok = np.array([env_match(r["built"]["ext"], r["gt"]["ext"]) for r in ex])
    gen_ok = np.array([(r["built"].get("genus") is not None and r["gt"].get("genus") is not None
                        and r["built"]["genus"] == r["gt"]["genus"]) for r in ex])
    gen_known = np.array([(r["built"].get("genus") is not None and r["gt"].get("genus") is not None) for r in ex])
    iou = np.array([r["iou"] for r in ex])
    bad = iou < 0.85
    d = {
        "n_exec": len(ex),
        "env_correct_frac": float(env_ok.mean()),
        "iou_given_env_ok": summarize(iou[env_ok]), "iou_given_env_bad": summarize(iou[~env_ok]),
        "failures(iou<0.85)": int(bad.sum()),
        "failures_with_env_wrong_frac": float((~env_ok[bad]).mean()),
        "successes_with_env_wrong_frac": float((~env_ok[~bad]).mean()),
        "genus_known_frac": float(gen_known.mean()),
        "failures_env_ok_genus_wrong_frac": float((env_ok[bad] & gen_known[bad] & ~gen_ok[bad]).mean()),
        "failures_env_ok_genus_ok_frac": float((env_ok[bad] & gen_ok[bad]).mean()),
        "auroc_envwrong_for_failure": auroc((~env_ok).astype(float), bad),
    }
    report["candidate_diagnosis"] = d
    print(json.dumps(d, indent=1))

    # ---------------- 2. selection on stored agreement matrices ----------------
    cons = json.load(open(args.cons))
    cparts = {p["key"]: p for p in cons["parts"]}

    def medoid(p, allowed):
        """index of the max-mean-agreement candidate among `allowed` (agreement
        computed against ALL executing candidates, as deployed)."""
        best, bscore = None, -1
        for j in allowed:
            row = [v for v in p["pair_iou"][j] if v is not None]
            s = sum(row) / len(row) if row else 0.0
            if s > bscore:
                best, bscore = j, s
        return best, bscore

    sel = defaultdict(list)
    stats = Counter()
    per_part_rows = []
    for key, p in cparts.items():
        feats = by_part.get(key, {})
        execj = [j for j in range(len(p["exec"])) if p["exec"][j] and feats.get(j, {}).get("built")]
        if not execj:
            for k in ("medoid", "env_gate", "env_genus_gate", "first_exec", "oracle"):
                sel[k].append(0.0)
            continue
        first = [j for j in range(len(p["exec"])) if p["exec"][j]]
        sel["first_exec"].append(p["iou"][first[0]] if first else 0.0)
        m, magree = medoid(p, execj)
        sel["medoid"].append(p["iou"][m])
        sel["oracle"].append(max(p["iou"][j] for j in execj))
        # majority envelope
        keys = Counter(env_key(feats[j]["built"]["ext"]) for j in execj)
        maj, nmaj = keys.most_common(1)[0]
        in_maj = [j for j in execj if env_key(feats[j]["built"]["ext"]) == maj]
        g, _ = medoid(p, in_maj)
        sel["env_gate"].append(p["iou"][g])
        # majority genus among majority-envelope candidates
        gens = Counter(feats[j]["built"].get("genus") for j in in_maj)
        gmaj = gens.most_common(1)[0][0]
        in_g = [j for j in in_maj if feats[j]["built"].get("genus") == gmaj] or in_maj
        gg, _ = medoid(p, in_g)
        sel["env_genus_gate"].append(p["iou"][gg])
        gt = feats[execj[0]]["gt"]
        maj_right = env_match(list(maj), gt["ext"]) if gt else None
        med_env_right = env_match(feats[m]["built"]["ext"], gt["ext"]) if gt else None
        any_right = any(env_match(feats[j]["built"]["ext"], gt["ext"]) for j in execj) if gt else None
        stats["parts"] += 1
        stats["maj_env_right"] += bool(maj_right)
        stats["medoid_env_right"] += bool(med_env_right)
        stats["any_env_right"] += bool(any_right)
        stats["unanimous_env"] += (nmaj == len(execj))
        stats["medoid_in_majority"] += (m in in_maj)
        med_bad = p["iou"][m] < 0.85
        stats["medoid_bad"] += med_bad
        if med_bad:
            stats["medoid_bad&env_wrong"] += (not med_env_right)
            stats["medoid_bad&maj_env_right"] += bool(maj_right)
            stats["medoid_bad&any_env_right"] += bool(any_right)
            stats["medoid_bad&not_unanimous"] += (nmaj < len(execj))
        unsolved = max(p["iou"][j] for j in execj) < 0.85
        stats["unsolved"] += unsolved
        if unsolved:
            stats["unsolved&any_env_right"] += bool(any_right)
            stats["unsolved&maj_env_right"] += bool(maj_right)
            gt_g = gt.get("genus") if gt else None
            stats["unsolved&any_genus_right"] += any(feats[j]["built"].get("genus") == gt_g for j in execj) if gt_g is not None else 0
        per_part_rows.append({"key": key, "n_exec": len(execj), "maj_frac": nmaj / len(execj),
                              "unanimous": nmaj == len(execj), "medoid_iou": p["iou"][m],
                              "medoid_agree": magree, "medoid_in_maj": m in in_maj,
                              "maj_env_right": maj_right, "medoid_env_right": med_env_right})
    sel_summary = {k: summarize(v) for k, v in sel.items()}
    report["selection"] = sel_summary
    report["part_stats"] = dict(stats)
    print(json.dumps(sel_summary, indent=1)); print(json.dumps(dict(stats), indent=1))
    # does envelope disagreement across candidates predict the served part is wrong?
    rows = per_part_rows
    report["part_predictors"] = {
        "auroc_nonunanimous_for_medoid_bad": auroc([1 - r["maj_frac"] for r in rows], [r["medoid_iou"] < 0.85 for r in rows]),
        "auroc_medoid_agree_for_medoid_bad": auroc([-r["medoid_agree"] for r in rows], [r["medoid_iou"] < 0.85 for r in rows]),
        "auroc_medoid_not_in_maj_for_medoid_bad": auroc([0.0 if r["medoid_in_maj"] else 1.0 for r in rows], [r["medoid_iou"] < 0.85 for r in rows]),
        "frac_unanimous": float(np.mean([r["unanimous"] for r in rows])),
        "medoid_bad_given_unanimous": float(np.mean([r["medoid_iou"] < 0.85 for r in rows if r["unanimous"]])),
        "medoid_bad_given_nonunanimous": float(np.mean([r["medoid_iou"] < 0.85 for r in rows if not r["unanimous"]])),
    }
    print(json.dumps(report["part_predictors"], indent=1))

    # ---------------- 3. stated vs built envelope (RFT candidates with think) ----------------
    if args.scored:
        sc = [r for r in load_jsonl(args.scored) if r["built"] and r["gt"] and len(r["stated"]) >= 2]
        def stated_covers(stated, ext):
            return all(any(abs(e - s) <= max(0.5, 0.02 * e) for s in stated) for e in ext)
        st_ok = np.array([stated_covers(r["stated"], r["gt"]["ext"]) for r in sc])
        bu_ok = np.array([env_match(r["built"]["ext"], r["gt"]["ext"]) for r in sc])
        consistent = np.array([stated_covers(r["stated"], r["built"]["ext"]) for r in sc])
        iou = np.array([r["iou"] for r in sc]); bad = iou < 0.85
        s3 = {
            "n": len(sc),
            "stated_env_right": float(st_ok.mean()), "built_env_right": float(bu_ok.mean()),
            "stated_right&built_wrong (recoverable by verify/repair)": float((st_ok & ~bu_ok).mean()),
            "stated_wrong&built_right": float((~st_ok & bu_ok).mean()),
            "both_wrong": float((~st_ok & ~bu_ok).mean()),
            "stated_built_consistent_frac": float(consistent.mean()),
            "iou_given_consistent": summarize(iou[consistent]), "iou_given_inconsistent": summarize(iou[~consistent]),
            "auroc_inconsistent_for_failure": auroc((~consistent).astype(float), bad),
            "failures_with_inconsistent_frac": float((~consistent[bad]).mean()),
            "failures_with_built_env_wrong_frac": float((~bu_ok[bad]).mean()),
        }
        report["stated_vs_built"] = s3
        print(json.dumps(s3, indent=1))

    if args.out:
        with open(args.out, "w") as f:
            json.dump({"report": report, "per_part": per_part_rows}, f, indent=1)


if __name__ == "__main__":
    main()
