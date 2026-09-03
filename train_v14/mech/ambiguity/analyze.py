"""Offline characterization of the stored e24 best-of-8 candidates on the
underdetermined eval sheets: HOW do candidates disagree (is it the unplaced
extent?), does the model pick a consistent default, is the vote choosing that
default, is the default right vs GT, and how much of the oracle-vote gap is
one-extent disagreement.

    python analyze.py --geom out/cand_geom_e24.jsonl --cons results/bo8_full_e24_consistency_v2.json
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict

import numpy as np

DV = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm"
HERE = os.path.dirname(os.path.abspath(__file__))
AXIS = {"m_env_width": 0, "m_env_depth": 1, "dim_height": 2}
TOL = 0.03   # relative extent tolerance for "same extent"


def medoid_idx(mat, execs):
    """Deployed selector: executing candidate with the highest mean pairwise IoU."""
    idx = [j for j, e in enumerate(execs) if e]
    if not idx:
        return None
    if len(idx) == 1:
        return idx[0]
    best, bs = None, -1
    for j in idx:
        s = np.mean([mat[j][i] for i in idx if i != j and mat[j][i] is not None])
        if s > bs:
            best, bs = j, s
    return best


def rel_err(a, b):
    return abs(a - b) / max(b, 1e-6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--geom", default=os.path.join(HERE, "out/cand_geom_e24.jsonl"))
    ap.add_argument("--cons", default=os.path.join(DV, "results/bo8_full_e24_consistency_v2.json"))
    ap.add_argument("--sidecar", default=os.path.join(HERE, "pool_sidecar.json"))
    ap.add_argument("--underdet", default=os.path.join(HERE, "keys_underdet.txt"))
    ap.add_argument("--out", default=os.path.join(HERE, "out/analysis_e24.json"))
    args = ap.parse_args()

    geom = {}
    for line in open(args.geom):
        r = json.loads(line); geom[r["key"]] = r
    cons = json.load(open(args.cons))
    cparts = {p["key"]: p for p in cons["parts"]}
    sidecar = json.load(open(args.sidecar))
    underdet = set(l.strip() for l in open(args.underdet) if l.strip())

    per_part = []
    for key, g in geom.items():
        if not g["gt"]:
            continue
        cp = cparts[key]
        sc = list(sidecar[key].values())[0]
        unplaced = sc["dims_unplaced"]
        env_axes = sorted({AXIS[d] for d in unplaced if d in AXIS})
        gt_ext = np.array(g["gt"]["ext"])
        cands = g["cands"]
        execs = [bool(c["exec"]) for c in cands]
        # sanity: stored exec flags vs re-execution
        vote = medoid_idx(cp["pair_iou"], [a and b for a, b in zip(cp["exec"], execs)])
        ious = [c["iou"] for c in cands]
        ex_idx = [j for j in range(len(cands)) if execs[j]]
        oracle = max(ex_idx, key=lambda j: ious[j]) if ex_idx else None
        rec = {"key": key, "underdet": key in underdet, "unplaced": unplaced, "env_axes": env_axes,
               "n_exec": len(ex_idx), "vote": vote, "oracle": oracle,
               "vote_iou": ious[vote] if vote is not None else 0.0,
               "oracle_iou": ious[oracle] if oracle is not None else 0.0,
               "first_iou": ious[ex_idx[0]] if ex_idx else 0.0,
               "cons_vote_iou": cons["per_part"][key]["consistency"]}
        # per-candidate extent errors on every axis
        errs = {}
        for j in ex_idx:
            errs[j] = [rel_err(cands[j]["ext"][a], gt_ext[a]) for a in range(3)]
        rec["ext_err"] = errs
        rec["gt_ext"] = gt_ext.tolist()
        rec["cand_ext"] = {j: cands[j]["ext"] for j in ex_idx}
        per_part.append(rec)

    def summarize(rows, label):
        out = {"label": label, "n": len(rows)}
        if not rows:
            return out
        out["vote_mean"] = float(np.mean([r["vote_iou"] for r in rows]))
        out["vote_iou85"] = float(np.mean([r["vote_iou"] >= 0.85 for r in rows]))
        out["oracle_mean"] = float(np.mean([r["oracle_iou"] for r in rows]))
        out["oracle_iou85"] = float(np.mean([r["oracle_iou"] >= 0.85 for r in rows]))
        out["first_mean"] = float(np.mean([r["first_iou"] for r in rows]))
        out["gap"] = out["oracle_mean"] - out["vote_mean"]
        # candidate-level extent correctness
        tot = wrong_any = 0
        wrong_axis = Counter()
        for r in rows:
            for j, e in r["ext_err"].items():
                tot += 1
                if max(e) > TOL:
                    wrong_any += 1
                for a in range(3):
                    if e[a] > TOL:
                        wrong_axis[a] += 1
        out["cand_envelope_wrong_frac"] = wrong_any / max(1, tot)
        out["cand_axis_wrong_frac"] = {"xyz"[a]: wrong_axis[a] / max(1, tot) for a in range(3)}
        # vote / oracle envelope correctness
        v_wrong = o_wrong = 0
        for r in rows:
            if r["vote"] is not None and max(r["ext_err"][r["vote"]]) > TOL:
                v_wrong += 1
            if r["oracle"] is not None and max(r["ext_err"][r["oracle"]]) > TOL:
                o_wrong += 1
        out["vote_envelope_wrong_frac"] = v_wrong / len(rows)
        out["oracle_envelope_wrong_frac"] = o_wrong / len(rows)
        return out

    U = [r for r in per_part if r["underdet"]]
    D = [r for r in per_part if not r["underdet"]]
    summ = {"underdetermined": summarize(U, "underdetermined (242)"),
            "determinate_control": summarize(D, "determinate control (120)")}
    cat = defaultdict(list)
    for r in U:
        kinds = {d.rstrip("0123456789") for d in r["unplaced"]}
        if kinds == {"m_env_width"}:
            k = "env_width_only"
        elif "m_env_width" in kinds:
            k = "env_width+other"
        elif kinds <= {"dim_loc_side_z", "dim_loc_front_z"}:
            k = "loc_z_only"
        else:
            k = "feature_dims_only"
        cat[k].append(r)
    summ["by_kind"] = {k: summarize(v, k) for k, v in cat.items()}

    # ---- the unplaced-extent question, on parts whose unplaced dim IS an envelope axis
    E = [r for r in U if r["env_axes"]]
    q = {"n_parts_with_unplaced_envelope_axis": len(E)}
    unpl_wrong = placed_wrong = n_unpl = n_placed = 0
    modal_right = modal_wrong = 0
    modal_share = []
    n_distinct = []
    vote_is_modal = 0
    vote_unpl_wrong = oracle_unpl_wrong = 0
    vote_unpl_wrong_oracle_right = 0
    gap_rows = 0; gap_extent_only = 0; gap_same_extent = 0
    gap_iou_extent = 0.0; gap_iou_total = 0.0
    modal_vs_gt = []
    for r in E:
        a = r["env_axes"][0]
        gt = r["gt_ext"][a]
        vals = []
        for j, e in r["ext_err"].items():
            n_unpl += 1
            if e[a] > TOL:
                unpl_wrong += 1
            for b in range(3):
                if b not in r["env_axes"]:
                    n_placed += 1
                    if e[b] > TOL:
                        placed_wrong += 1
            vals.append(r["cand_ext"][j][a])
        if not vals:
            continue
        # cluster candidate extents at 3% relative tolerance
        vs = sorted(vals); clusters = [[vs[0]]]
        for v in vs[1:]:
            if rel_err(v, clusters[-1][0]) <= TOL:
                clusters[-1].append(v)
            else:
                clusters.append([v])
        clusters.sort(key=len, reverse=True)
        modal = float(np.median(clusters[0]))
        n_distinct.append(len(clusters)); modal_share.append(len(clusters[0]) / len(vals))
        modal_vs_gt.append(modal / gt)
        if rel_err(modal, gt) <= TOL:
            modal_right += 1
        else:
            modal_wrong += 1
        v, o = r["vote"], r["oracle"]
        if v is not None and rel_err(r["cand_ext"][v][a], modal) <= TOL:
            vote_is_modal += 1
        vw = v is not None and r["ext_err"][v][a] > TOL
        ow = o is not None and r["ext_err"][o][a] > TOL
        vote_unpl_wrong += vw; oracle_unpl_wrong += ow
        if vw and not ow:
            vote_unpl_wrong_oracle_right += 1
        if v is not None and o is not None and r["oracle_iou"] - r["vote_iou"] > 0.02:
            gap_rows += 1
            gap_iou_total += r["oracle_iou"] - r["vote_iou"]
            ev, eo = r["ext_err"][v], r["ext_err"][o]
            same_placed = all(rel_err(r["cand_ext"][v][b], r["cand_ext"][o][b]) <= TOL
                              for b in range(3) if b != a)
            diff_unpl = rel_err(r["cand_ext"][v][a], r["cand_ext"][o][a]) > TOL
            if diff_unpl and same_placed:
                gap_extent_only += 1; gap_iou_extent += r["oracle_iou"] - r["vote_iou"]
            elif not diff_unpl:
                gap_same_extent += 1
        r["modal_ext"] = modal; r["modal_share"] = modal_share[-1]; r["n_clusters"] = len(clusters)
    q.update({
        "cand_unplaced_axis_wrong_frac": unpl_wrong / max(1, n_unpl),
        "cand_placed_axes_wrong_frac": placed_wrong / max(1, n_placed),
        "modal_default_right": modal_right, "modal_default_wrong": modal_wrong,
        "mean_modal_share": float(np.mean(modal_share)), "mean_n_clusters": float(np.mean(n_distinct)),
        "frac_single_cluster": float(np.mean([c == 1 for c in n_distinct])),
        "vote_picks_modal_frac": vote_is_modal / len(E),
        "vote_unplaced_wrong": vote_unpl_wrong, "oracle_unplaced_wrong": oracle_unpl_wrong,
        "vote_wrong_oracle_right": vote_unpl_wrong_oracle_right,
        "gap_parts(>0.02)": gap_rows, "gap_parts_extent_only": gap_extent_only,
        "gap_parts_same_unplaced_extent": gap_same_extent,
        "gap_iou_total_sum": gap_iou_total, "gap_iou_extent_only_sum": gap_iou_extent,
        "modal_over_gt_hist": dict(Counter(f"{round(x, 1):.1f}" for x in modal_vs_gt).most_common(12)),
    })
    summ["unplaced_envelope_axis"] = q

    print(json.dumps(summ, indent=1, default=float))
    json.dump({"summary": summ, "per_part": per_part}, open(args.out, "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
