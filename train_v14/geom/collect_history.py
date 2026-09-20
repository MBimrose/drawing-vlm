"""Collect every experiment's evaluation numbers into one table for the progress figures.

Three sources, each a different bench, never mixed in a single series:

  real     `results/ext/bo8_ext_<run>_summary.txt` — 146 held-out REAL drawings (Fusion 360 and
           ABC parts). analyze_ext columns: first_exec, consistency (agreement vote), gated
           (served policy), oracle.
  synth96  `runs/<run>/geom_eval/final.json` — the in-training geometry eval on 96 held-out
           synthetic parts (Zero-To-CAD-1m derived), protocol v2 for every run: iou_mean is the
           greedy single shot, final_iou_mean is after the execution-repair loop. This reaches
           back to e1, before best-of-N sampling or the agreement vote existed.
  synthfull `results/bo8_full_<run>_consistency.json` — best-of-8 over the full 1,030-part
           certified pool: first_exec, consistency, oracle.

Renderer break: e55, e57, e58 and e59 were trained and scored on draftwright 0.4.23 sheets
("dw423"); every earlier run used the retired 0.4.0 sheets. Same parts, redrawn — so the two
eras are marked and must not be read as one continuous curve.

    python collect_history.py --out results/figures/history.json
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re

DW423 = {"e55", "e57", "e58", "e59"}          # runs trained/scored on the 0.4.23 sheets
VARIANTS = {"e55v4", "e55vb55", "e55vb55p"}   # verifier re-scores of an existing checkpoint


def enum(run: str) -> int | None:
    m = re.match(r"e(\d+)", run)
    return int(m.group(1)) if m else None


def collect(root: str) -> dict:
    out: dict[str, dict] = {}

    def row(run: str) -> dict:
        e = enum(run)
        return out.setdefault(run, {"run": run, "e": e, "dw423": f"e{e}" in DW423})

    for f in sorted(glob.glob(os.path.join(root, "results/ext/bo8_ext_e*_summary.txt"))):
        run = re.match(r"bo8_ext_(e[\w.-]+)_summary\.txt", os.path.basename(f)).group(1)
        if run in VARIANTS:
            continue
        txt = open(f).read()
        hdr, ext = re.search(r"^slice.*$", txt, re.M), re.search(r"^ALL external\s+(\d+) \|(.*)$", txt, re.M)
        if not hdr or not ext:
            continue
        cols = [c.strip() for c in hdr.group(0).split("|")[1:] if c.strip()]
        vals = re.findall(r"([\d.]+) /\s*(\d+)%", ext.group(2))
        r = row(run); r["real_n"] = int(ext.group(1))
        for c, (mean, pct) in zip(cols, vals):
            r[f"real_{c}"] = float(mean); r[f"real_{c}_85"] = int(pct) / 100

    for f in sorted(glob.glob(os.path.join(root, "runs/e*/geom_eval/final.json"))):
        run = f.split(os.sep)[-3]
        if enum(run) is None or run in VARIANTS:
            continue
        try:
            m = json.load(open(f))["metrics"]
        except Exception:
            continue
        if m.get("v") != 2 or m.get("n") != 96:      # only the stable protocol
            continue
        r = row(run)
        r.update({"synth96_greedy": m.get("iou_mean"), "synth96_repaired": m.get("final_iou_mean"),
                  "synth96_greedy_85": m.get("frac_iou85"), "synth96_repaired_85": m.get("final_frac_iou85"),
                  "synth96_exec": m.get("final_exec_ok_frac", m.get("exec_ok_frac")), "synth96_n": m.get("n")})

    for f in sorted(glob.glob(os.path.join(root, "results/bo8_full_e*_consistency.json"))):
        run = re.match(r"bo8_full_(e[\w.-]+)_consistency\.json", os.path.basename(f)).group(1)
        if enum(run) is None or run in VARIANTS:
            continue
        try:
            d = json.load(open(f))
        except Exception:
            continue
        r = row(run)
        for src, dst in (("first_exec", "full_first"), ("consistency", "full_vote"), ("oracle", "full_oracle")):
            if isinstance(d.get(src), dict):
                r[f"{dst}"] = d[src].get("iou_mean"); r[f"{dst}_85"] = d[src].get("frac_iou85")
        r["full_n"] = len(d.get("per_part", {})) or None
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm")
    ap.add_argument("--out", default="results/figures/history.json")
    a = ap.parse_args()
    rows = sorted(collect(a.root).values(), key=lambda r: (r["e"], r["run"]))
    out = a.out if os.path.isabs(a.out) else os.path.join(a.root, a.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(rows, open(out, "w"), indent=1)
    has = lambda k: sum(1 for r in rows if r.get(k) is not None)
    print(f"[history] {len(rows)} runs e{rows[0]['e']}..e{rows[-1]['e']} -> {out}")
    print(f"  real bench (146):      {has('real_first_exec')} runs with a first-draw number, "
          f"{has('real_gated')} with the served policy")
    print(f"  synthetic 96 (v2):     {has('synth96_greedy')} runs, reaching back to e{min(r['e'] for r in rows if r.get('synth96_greedy'))}")
    print(f"  synthetic full pool:   {has('full_first')} runs")
    print(f"  drawn on 0.4.23 sheets:{[r['run'] for r in rows if r['dw423']]}")


if __name__ == "__main__":
    main()
