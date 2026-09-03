"""Before/after table for the visual self-check on the same 96 parts.

Policies (all offline on selfcheck_96.json):
  served          : consistency medoid (baseline, what is deployed)
  rev_if_exec     : revision whenever it executes (else served)
  rev_if_agree    : revision if it executes AND its mean agreement with the
                    other stored candidates >= served agreement - MARGIN
  rev_if_changed  : rev_if_exec but only when the model actually changed code
  gated<τ         : rev_if_agree applied only to low-agreement parts (served agreement < τ)
  oracle2         : max(served, revision)  (upper bound of a 2-way choice)

    python analyze.py --out out/selfcheck_96.json
"""
from __future__ import annotations

import argparse
import json
import os
import statistics as st


def summarize(ious):
    n = len(ious)
    return {"mean": sum(ious) / n, "median": st.median(ious),
            "iou85": sum(i >= 0.85 for i in ious) / n, "iou50": sum(i >= 0.5 for i in ious) / n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--margin", type=float, default=0.05)
    ap.add_argument("--md", default="")
    a = ap.parse_args()
    recs = json.load(open(a.out))["records"]
    n = len(recs)
    served = [r["served_iou"] for r in recs]

    def choose(r, mode, tau=None):
        ok = r["rev_exec"] and r["rev_code"]
        if tau is not None and r["served_agree"] >= tau:
            return r["served_iou"]
        if mode == "rev_if_exec":
            return r["rev_iou"] if ok else r["served_iou"]
        if mode == "rev_if_changed":
            return r["rev_iou"] if ok and r["changed"] else r["served_iou"]
        if mode == "rev_if_agree":
            if ok and r["rev_agree"] is not None and r["rev_agree"] >= r["served_agree"] - a.margin:
                return r["rev_iou"]
            return r["served_iou"]
        if mode == "rev_if_agree_up":
            if ok and r["rev_agree"] is not None and r["rev_agree"] > r["served_agree"]:
                return r["rev_iou"]
            return r["served_iou"]
        if mode == "oracle2":
            return max(r["served_iou"], r["rev_iou"] if ok else 0.0)
        raise ValueError(mode)

    rows = [("served (consistency medoid)", served)]
    for mode in ["rev_if_exec", "rev_if_changed", "rev_if_agree", "rev_if_agree_up", "oracle2"]:
        rows.append((mode, [choose(r, mode) for r in recs]))
    for tau in (0.8, 0.9):
        rows.append((f"rev_if_agree, gated served_agree<{tau}", [choose(r, "rev_if_agree", tau) for r in recs]))

    lines = []
    lines.append(f"n = {n} parts; revisions: executed {sum(r['rev_exec'] for r in recs)}, "
                 f"code changed {sum(bool(r['changed']) for r in recs)}, "
                 f"no code {sum(r['rev_code'] is None for r in recs)}, "
                 f"render failed {sum(not r['render_ok'] for r in recs)}")
    lines.append("")
    lines.append("| policy | mean IoU | median | ≥0.85 | ≥0.5 | Δmean vs served |")
    lines.append("|---|---|---|---|---|---|")
    base = summarize(served)["mean"]
    for name, ious in rows:
        s = summarize(ious)
        lines.append(f"| {name} | {s['mean']:.4f} | {s['median']:.4f} | {100*s['iou85']:.1f}% | "
                     f"{100*s['iou50']:.1f}% | {s['mean']-base:+.4f} |")

    # per-part deltas for rev_if_exec
    d = [(r["rev_iou"] - r["served_iou"]) if r["rev_exec"] else 0.0 for r in recs]
    lines.append("")
    lines.append(f"Per-part deltas (rev_if_exec): improved >0.05: {sum(x > 0.05 for x in d)}, "
                 f"worsened >0.05: {sum(x < -0.05 for x in d)}, |Δ|≤0.05: {sum(abs(x) <= 0.05 for x in d)}; "
                 f"mean Δ on changed+exec parts: "
                 f"{(sum(x for x, r in zip(d, recs) if r['changed'] and r['rev_exec']) / max(1, sum(r['changed'] and r['rev_exec'] for r in recs))):+.4f}")
    # low-agreement / failing slices
    for name, sel in [("served_agree < 0.8", lambda r: r["served_agree"] < 0.8),
                      ("served_agree < 0.9", lambda r: r["served_agree"] < 0.9),
                      ("served IoU < 0.85", lambda r: r["served_iou"] < 0.85)]:
        sub = [r for r in recs if sel(r)]
        if not sub:
            continue
        sv = [r["served_iou"] for r in sub]
        rv = [choose(r, "rev_if_exec") for r in sub]
        ra = [choose(r, "rev_if_agree") for r in sub]
        o2 = [choose(r, "oracle2") for r in sub]
        lines.append(f"Slice {name} (n={len(sub)}): served {sum(sv)/len(sv):.3f} -> rev_if_exec "
                     f"{sum(rv)/len(rv):.3f}, rev_if_agree {sum(ra)/len(ra):.3f}, oracle2 {sum(o2)/len(o2):.3f}; "
                     f"improved>0.05: {sum(r['rev_exec'] and r['rev_iou']-r['served_iou']>0.05 for r in sub)}, "
                     f"worsened>0.05: {sum(r['rev_exec'] and r['rev_iou']-r['served_iou']<-0.05 for r in sub)}")
    # largest movers
    mv = sorted(((r["rev_iou"] - r["served_iou"], r) for r in recs if r["rev_exec"]), key=lambda t: t[0])
    lines.append("")
    lines.append("Largest movers (Δ, key, served→rev, agree served→rev):")
    for x, r in mv[:5] + mv[-5:]:
        lines.append(f"  {x:+.3f} {r['key'][:8]} {r['served_iou']:.3f}->{r['rev_iou']:.3f} "
                     f"agree {r['served_agree']:.3f}->{(r['rev_agree'] or 0):.3f} changed={r['changed']}")
    gs = [r["gen_s"] for r in recs if r["gen_s"]]
    if gs:
        lines.append(f"Generation time: mean {sum(gs)/len(gs):.1f} s/part (batched)")
    txt = "\n".join(lines)
    print(txt)
    if a.md:
        with open(a.md, "w") as f:
            f.write(txt + "\n")


if __name__ == "__main__":
    main()
