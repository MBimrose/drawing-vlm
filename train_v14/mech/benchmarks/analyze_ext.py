#!/usr/bin/env python
"""Summarise the external-parts best-of-8 result (consistency_rerank output)
split by family (F = Fusion 360 Gallery, A = ABC) and by determinacy
(sidecar dims_unplaced empty or not), next to the in-distribution champion
numbers from results/bo8_full_e24_consistency_v2.json.

  python analyze_ext.py results/bo8_ext_e24_consistency.json [--split data/ext_bench/split.json]
"""
import argparse
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
IN_DIST = {"first_exec": (0.878, 0.728), "consistency": (0.912, 0.814), "oracle": (0.942, 0.890)}
POLICIES = ["first_exec", "consistency", "oracle"]


def summarise(rows):
    out = {}
    for p in POLICIES:
        v = [r[p] for r in rows]
        out[p] = (st.mean(v) if v else float("nan"), sum(x >= 0.85 for x in v) / len(v) if v else float("nan"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--split", default=os.path.join(HERE, "data", "ext_bench", "split.json"))
    a = ap.parse_args()
    d = json.load(open(a.src))
    split = json.load(open(a.split))
    per = d["per_part"]
    parts = {p["key"]: p for p in d["parts"]}
    rows = []
    for k, m in per.items():
        s = split.get(k, {})
        ex = parts.get(k, {}).get("exec") or []
        rows.append(dict(key=k, family=s.get("family", "?"), under=s.get("underdetermined"),
                         faces=s.get("faces"), n_exec=sum(1 for e in ex if e), **{p: m[p] for p in POLICIES}))
    groups = [("ALL external", rows),
              ("  determinate", [r for r in rows if r["under"] is False]),
              ("  underdetermined", [r for r in rows if r["under"] is True]),
              ("Fusion360 (F)", [r for r in rows if r["family"] == "F"]),
              ("  F determinate", [r for r in rows if r["family"] == "F" and r["under"] is False]),
              ("ABC (A)", [r for r in rows if r["family"] == "A"]),
              ("  A determinate", [r for r in rows if r["family"] == "A" and r["under"] is False])]
    print(f"{'slice':22s} {'n':>4s} | " + " | ".join(f"{p:>18s}" for p in POLICIES) + " | exec>=1")
    print(f"{'':22s} {'':>4s} | " + " | ".join(f"{'mean / >=0.85':>18s}" for _ in POLICIES))
    print(f"{'in-dist 1030 pool':22s} {1030:4d} | " + " | ".join(f"{IN_DIST[p][0]:.3f} / {IN_DIST[p][1]*100:4.0f}%" for p in POLICIES) + " |")
    for name, g in groups:
        if not g:
            continue
        s = summarise(g)
        ex = sum(1 for r in g if r["n_exec"] > 0) / len(g)
        print(f"{name:22s} {len(g):4d} | " + " | ".join(f"{s[p][0]:.3f} / {s[p][1]*100:4.0f}%" for p in POLICIES) + f" | {ex*100:4.0f}%")
    print()
    print("worst 10 (consistency):")
    for r in sorted(rows, key=lambda r: r["consistency"])[:10]:
        print(f"  {r['key']:34s} fam={r['family']} under={r['under']} faces={r['faces']} exec={r['n_exec']}/8 "
              f"first={r['first_exec']:.3f} cons={r['consistency']:.3f} oracle={r['oracle']:.3f}")
    print("\nn parts with no candidate >= 0.85:", sum(1 for r in rows if r["oracle"] < 0.85),
          " of which underdetermined:", sum(1 for r in rows if r["oracle"] < 0.85 and r["under"]))
    json.dump(rows, open(os.path.splitext(a.src)[0] + "_rows.json", "w"), indent=1)


if __name__ == "__main__":
    main()
