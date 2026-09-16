"""Merge score_partials outputs from shard slices into one bestofn json (candidates concatenated,
metrics recomputed over the union) so write_rft_real / bestofn_verifier_eval see a single run.

    python merge_scored.py --out <merged.json> <slice1.json> <slice2.json> ...
"""
import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("slices", nargs="+")
    a = ap.parse_args()
    parts, seen = [], set()
    for s in a.slices:
        d = json.load(open(s))
        for p in d["candidates"]:
            if p["key"] in seen:
                continue
            seen.add(p["key"]); parts.append(p)
    n_c = sum(len(p["cands"]) for p in parts)
    n_ex = sum(1 for p in parts for c in p["cands"] if c.get("exec"))
    best = [max((c.get("iou", 0.0) for c in p["cands"]), default=0.0) for p in parts]
    first = [next((c.get("iou", 0.0) for c in p["cands"] if c.get("draw", 0) == 0), 0.0) for p in parts]
    metrics = {"n_parts": len(parts), "n_candidates": n_c, "executed": n_ex,
               "first_draw_mean": sum(first) / max(1, len(first)), "first_draw_ge85": sum(x >= 0.85 for x in first) / max(1, len(first)),
               "best_mean": sum(best) / max(1, len(best)), "best_ge85": sum(x >= 0.85 for x in best) / max(1, len(best)),
               "best_ge80": sum(x >= 0.80 for x in best) / max(1, len(best)), "slices": a.slices}
    json.dump({"metrics": metrics, "candidates": parts}, open(a.out, "w"))
    print(json.dumps(metrics, indent=1))


if __name__ == "__main__":
    main()
