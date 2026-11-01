"""Renderer statistics for the paper: render time, failure rate and drawing completeness.

Reads the per-sheet sidecars (`<shard>.renderers.json`) of the original training tars
(draftwright 0.4.0 with the legacy fallback) and of the 0.4.23 re-render (no fallback), plus
the 0.4.23 per-key failure logs (`tars_v14_dw423_failures/<shard>.json`).

    python results/dataset_stats/scripts/render_stats.py [--workers N] [--out results/dataset_stats/out/render_stats.json]
"""
import argparse
import collections
import glob
import json
import os
import re
from multiprocessing import Pool

import numpy as np

W = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/step_to_drw/wds_dataset"
SETS = {"v14_dw400": f"{W}/tars_v14", "v14_dw423": f"{W}/tars_v14_dw423"}
FAIL_DIR = f"{W}/tars_v14_dw423_failures"


def _sheet_rows(path):
    rows = []
    for key, m in json.load(open(path)).items():
        ann = m.get("annotations") or {}
        rows.append((
            key,
            m.get("renderer"),
            m.get("render_s"),
            m.get("wall_s"),
            len(m.get("dims_placed") or []),
            len(m.get("dims_unplaced") or []),
            len(ann),
            sum(1 for a in ann.values() if a.get("kind") == "Leader"),
            m.get("lint_errors"),
            m.get("lint_warnings"),
        ))
    return rows


def _pct(a, qs=(10, 50, 90, 99)):
    a = np.asarray([x for x in a if x is not None], float)
    if not len(a):
        return {}
    out = {"n": int(len(a)), "mean": float(a.mean())}
    out.update({f"p{q}": float(np.percentile(a, q)) for q in qs})
    return out


def sheet_stats(rows):
    by_r = collections.defaultdict(list)
    for r in rows:
        by_r[r[1]].append(r)
    out = {"n_sheets": len(rows), "by_renderer": {}}
    for ren, rs in by_r.items():
        placed = np.array([r[4] for r in rs], float)
        unplaced = np.array([r[5] for r in rs], float)
        out["by_renderer"][ren] = {
            "n": len(rs),
            "render_s": _pct([r[2] for r in rs]),
            "wall_s": _pct([r[3] for r in rs]),
            "dims_placed_per_sheet": float(placed.mean()),
            "dims_unplaced_per_sheet": float(unplaced.mean()),
            "share_dims_placed": float(placed.sum() / max(1.0, placed.sum() + unplaced.sum())),
            "share_sheets_all_dims_placed": float((unplaced == 0).mean()),
            "annotations_per_sheet": float(np.mean([r[6] for r in rs])),
            "leaders_per_sheet": float(np.mean([r[7] for r in rs])),
            "lint_errors_per_sheet": _pct([r[8] for r in rs], qs=(50,)).get("mean"),
            "lint_warnings_per_sheet": _pct([r[9] for r in rs], qs=(50,)).get("mean"),
        }
    return out


_EXC = re.compile(r"([A-Za-z_][A-Za-z0-9_.]*(?:Error|Exception|Timeout|Iteration|Mismatch|NullObject|Value))")


def _fail_class(reason, msg):
    if reason in ("exec_error", "exec_timeout", "skipped_known_bad", "render_timeout"):
        return reason
    m = msg or ""
    if any(s in m for s in ("valid solid", "valid closed solid", "Attribution", "AmbiguousTurnedOwnership",
                            "recess pattern members", "slot drafting", "canonical quarter arc",
                            "wall role has ambiguous")):
        return "render_fail:feature_recognition"
    if "_DrawingTimeout" in m:
        return "render_fail:drawing_timeout"
    if "Standard_" in m or "OCP" in m or "Geom_" in m:
        return "render_fail:occt"
    if "StopIteration" in m:
        return "render_fail:StopIteration"
    if reason == "render_legacy":
        return "render_legacy"
    exc = _EXC.findall(m)
    return f"{reason}:{exc[-1] if exc else 'other'}"


def _fail_rows(path):
    d = json.load(open(path))
    recovered = set(d.get("recovered") or [])
    out = []
    for key, v in d.items():
        if key == "recovered":
            continue
        reason, msg = (v + ["", ""])[:2]
        out.append((key, reason, msg, key in recovered))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--out", default="results/dataset_stats/out/render_stats.json")
    args = ap.parse_args()
    res = {}
    with Pool(args.workers) as pool:
        sheets = {}
        for name, d in SETS.items():
            files = sorted(glob.glob(f"{d}/*.renderers.json"))
            rows = [r for rs in pool.imap_unordered(_sheet_rows, files, chunksize=8) for r in rs]
            sheets[name] = {r[0] for r in rows}
            res[name] = sheet_stats(rows)
            res[name]["n_shards"] = len(files)
            print(name, json.dumps(res[name], indent=1), flush=True)
        files = sorted(glob.glob(f"{FAIL_DIR}/shard_*.json"))
        frows = [r for rs in pool.imap_unordered(_fail_rows, files, chunksize=8) for r in rs]

    ok423 = sheets["v14_dw423"]
    skipped = sum(1 for r in frows if r[1] == "skipped_known_bad")
    # final failures = logged, not skipped, and without a sheet in the packed tars
    final = [r for r in frows if r[1] != "skipped_known_bad" and r[0] not in ok423]
    cls = collections.Counter(_fail_class(r[1], r[2]) for r in final)
    attempted = len(ok423) + len(final)
    exec_fail = sum(n for c, n in cls.items() if c.startswith("exec"))
    render_fail = len(final) - exec_fail
    res["dw423_failures"] = {
        "skipped_exec_bad_blocklist": skipped,
        "attempted": attempted,
        "ok_sheets": len(ok423),
        "failed": len(final),
        "fail_rate_attempted": len(final) / attempted,
        "exec_failed": exec_fail,
        "render_failed": render_fail,
        "render_fail_rate_of_executed": render_fail / (attempted - exec_fail),
        "logged_recovered_by_retry": sum(1 for r in frows if r[3]),
        "logged_but_has_sheet": sum(1 for r in frows if r[1] != "skipped_known_bad" and r[0] in ok423),
        "classes": dict(cls.most_common()),
    }
    print(json.dumps(res["dw423_failures"], indent=1))
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    json.dump(res, open(args.out, "w"), indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
