"""View-aware render-and-compare metric, computed offline from saved candidate sheets.

draftwright draws part geometry in black and every annotation (dimensions, leaders, labels,
title block) in blue, and it re-places views and dimensions whenever a candidate's proportions
move, so a whole-sheet ink F1 punishes near-correct candidates for annotation drift. This
metric keeps only the black geometry, splits it into views (connected components of the dilated
linework), matches views between the input and the candidate sheet (Hungarian assignment on
centre-aligned silhouette IoU) and scores

    sil   area-weighted silhouette IoU of matched views / max(total area)   (outer shape, size)
    edge  tolerance F1 of the linework inside matched, centre-aligned views  (holes, pockets, steps)
    v2    0.5 * sil + 0.5 * edge

Same sheet scale is implied: a candidate of the wrong size gets a different scale or a
different silhouette area and loses on `sil`.

    python rc_metric2.py --rc results/ext/rc_X_png.json --png-dir results/ext/rc_png_X \
        --bench <bench dir> --out results/ext/rc_X_v2.json [--workers 16]
"""
from __future__ import annotations

import argparse
import io
import json
import os
import pickle
from concurrent.futures import ProcessPoolExecutor

import numpy as np


def geometry_mask(png_bytes: bytes) -> np.ndarray:
    """Black linework only: dark pixels that are not blue-dominant (annotations are blue)."""
    from PIL import Image
    rgb = np.asarray(Image.open(io.BytesIO(png_bytes)).convert("RGB")).astype(np.int16)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    dark = (r + g + b) < 330
    blue = (b - np.maximum(r, g)) > 40
    return dark & ~blue


def views(mask: np.ndarray, min_extent: int = 24, join: int = 9):
    """Split the geometry mask into views: components of the dilated mask -> (bbox, linework crop, silhouette crop)."""
    from scipy import ndimage as ndi
    lab, n = ndi.label(ndi.binary_dilation(mask, iterations=join))
    out = []
    for sl in ndi.find_objects(lab):
        if sl is None:
            continue
        h, w = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        if max(h, w) < min_extent:
            continue
        crop = mask[sl]
        sil = ndi.binary_fill_holes(ndi.binary_closing(crop, iterations=2))
        out.append({"bbox": (sl[0].start, sl[1].start, h, w), "line": crop, "sil": sil, "area": int(sil.sum())})
    return out


def _centered(a: np.ndarray, H: int, W: int) -> np.ndarray:
    c = np.zeros((H, W), bool); h, w = a.shape
    y0, x0 = (H - h) // 2, (W - w) // 2
    c[y0:y0 + h, x0:x0 + w] = a
    return c


def _pair(va, vb, tol: float):
    from scipy.ndimage import distance_transform_edt
    H = max(va["line"].shape[0], vb["line"].shape[0]) + 8; W = max(va["line"].shape[1], vb["line"].shape[1]) + 8
    sa, sb = _centered(va["sil"], H, W), _centered(vb["sil"], H, W)
    inter = (sa & sb).sum(); union = (sa | sb).sum()
    sil = inter / union if union else 0.0
    la, lb = _centered(va["line"], H, W), _centered(vb["line"], H, W)
    if la.any() and lb.any():
        da, db = distance_transform_edt(~la), distance_transform_edt(~lb)
        rec, pre = float((db[la] <= tol).mean()), float((da[lb] <= tol).mean())
        edge = 0.0 if pre + rec == 0 else 2 * pre * rec / (pre + rec)
    else:
        edge = 0.0
    return sil, edge


def _norm(a: np.ndarray, size: int = 96) -> np.ndarray:
    """Aspect-preserving resize of a boolean crop so its longer side is `size` (nearest neighbour)."""
    from scipy.ndimage import zoom
    h, w = a.shape; f = size / max(h, w)
    return zoom(a.astype(np.uint8), (f, f), order=0).astype(bool) if min(h, w) * f >= 1 else np.zeros((1, 1), bool)


def _rescale(v: dict, f: float) -> dict:
    from scipy.ndimage import zoom
    if abs(f - 1.0) < 0.02:
        return v
    line = zoom(v["line"].astype(np.uint8), (f, f), order=0).astype(bool)
    sil = zoom(v["sil"].astype(np.uint8), (f, f), order=0).astype(bool)
    return {"bbox": v["bbox"], "line": line, "sil": sil, "area": int(sil.sum())}


def sheet_score_v3(png_in: bytes, png_cand: bytes, tol: float = 2.0) -> dict:
    """Scale-normalised variant: the renderer zooms the page by content, so two sheets of the same
    part can differ in px/mm. Match views by shape at a normalised size, estimate ONE global scale
    (median sqrt silhouette-area ratio over the matched views), rescale the candidate's views by it
    and then compare as in v2 -- a single scale keeps cross-view proportions honest."""
    from scipy.optimize import linear_sum_assignment
    A, B = views(geometry_mask(png_in)), views(geometry_mask(png_cand))
    if not A or not B:
        return {"sil3": 0.0, "edge3": 0.0, "v3": 0.0, "scale": 1.0}
    S0 = np.zeros((len(A), len(B)))
    for i, va in enumerate(A):
        na = _norm(va["sil"])
        for j, vb in enumerate(B):
            nb = _norm(vb["sil"]); H = max(na.shape[0], nb.shape[0]); W = max(na.shape[1], nb.shape[1])
            ca, cb = _centered(na, H, W), _centered(nb, H, W); u = (ca | cb).sum()
            S0[i, j] = (ca & cb).sum() / u if u else 0.0
    ri, cj = linear_sum_assignment(-S0)
    ratios = [np.sqrt(A[i]["area"] / max(1, B[j]["area"])) for i, j in zip(ri, cj) if S0[i, j] > 0.5]
    f = float(np.clip(np.median(ratios), 0.4, 2.5)) if ratios else 1.0
    B2 = [_rescale(v, f) for v in B]
    S = np.zeros((len(A), len(B2))); E = np.zeros_like(S)
    for i, va in enumerate(A):
        for j, vb in enumerate(B2):
            S[i, j], E[i, j] = _pair(va, vb, tol)
    ri, cj = linear_sum_assignment(-(S + E))
    wa = np.array([v["area"] for v in A], float); wb = np.array([v["area"] for v in B2], float)
    denom = max(wa.sum(), wb.sum(), 1.0)
    sil = float(sum(min(wa[i], wb[j]) * S[i, j] for i, j in zip(ri, cj)) / denom)
    edge = float(sum(min(wa[i], wb[j]) * E[i, j] for i, j in zip(ri, cj)) / denom)
    return {"sil3": sil, "edge3": edge, "v3": 0.5 * sil + 0.5 * edge, "scale": f}


def sheet_score(png_in: bytes, png_cand: bytes, tol: float = 2.0) -> dict:
    from scipy.optimize import linear_sum_assignment
    A, B = views(geometry_mask(png_in)), views(geometry_mask(png_cand))
    if not A or not B:
        return {"sil": 0.0, "edge": 0.0, "v2": 0.0, "views_in": len(A), "views_cand": len(B)}
    S = np.zeros((len(A), len(B))); E = np.zeros_like(S)
    for i, va in enumerate(A):
        for j, vb in enumerate(B):
            # views sit in the same sheet region when the layout is stable: discourage far-apart matches
            S[i, j], E[i, j] = _pair(va, vb, tol)
    ri, cj = linear_sum_assignment(-(S + E))
    wa = np.array([v["area"] for v in A], float); wb = np.array([v["area"] for v in B], float)
    denom = max(wa.sum(), wb.sum(), 1.0)
    sil = float(sum(min(wa[i], wb[j]) * S[i, j] for i, j in zip(ri, cj)) / denom)
    edge = float(sum(min(wa[i], wb[j]) * E[i, j] for i, j in zip(ri, cj)) / denom)
    return {"sil": sil, "edge": edge, "v2": 0.5 * sil + 0.5 * edge, "views_in": len(A), "views_cand": len(B)}


_CACHE = {}


def _work(job):
    bench, key, idx, path, tol = job
    if bench not in _CACHE:
        _CACHE[bench] = pickle.load(open(os.path.join(bench, "eval_cache_v15.pkl"), "rb"))["samples"]
    try:
        cand = open(path, "rb").read()
        return key, idx, {**sheet_score(_CACHE[bench][key]["png"], cand, tol), **sheet_score_v3(_CACHE[bench][key]["png"], cand, tol)}
    except Exception as e:   # a malformed sheet must not kill the run
        return key, idx, {"sil": 0.0, "edge": 0.0, "v2": 0.0, "sil3": 0.0, "edge3": 0.0, "v3": 0.0, "error": f"{type(e).__name__}: {e}"[:120]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rc", required=True); ap.add_argument("--png-dir", required=True)
    ap.add_argument("--bench", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=16); ap.add_argument("--tol", type=float, default=2.0)
    a = ap.parse_args()
    d = json.load(open(a.rc)); jobs = []
    for p in d["parts"]:
        for i, c in enumerate(p["cands"]):
            f = os.path.join(a.png_dir, f"{p['key']}__{i}.png")
            if os.path.exists(f):
                jobs.append((a.bench, p["key"], i, f, a.tol))
    print(f"[rc2] {len(jobs)} candidate sheets", flush=True)
    res = {}
    with ProcessPoolExecutor(a.workers) as ex:
        for n, (key, i, r) in enumerate(ex.map(_work, jobs, chunksize=4), 1):
            res[(key, i)] = r
            if n % 100 == 0:
                print(f"[rc2] {n}/{len(jobs)}", flush=True)
    # identical code shares a sheet: copy scores to duplicates (render_compare rendered one of them)
    for p in d["parts"]:
        best_by_score = {}
        for i, c in enumerate(p["cands"]):
            r = res.get((p["key"], i))
            if r is not None:
                best_by_score[round(c.get("score", -1), 9)] = r
        for i, c in enumerate(p["cands"]):
            r = res.get((p["key"], i)) or (best_by_score.get(round(c.get("score", -1), 9)) if c.get("variant") else None) or {"sil": 0.0, "edge": 0.0, "v2": 0.0}
            c.update({k: r.get(k, 0.0) for k in ("sil", "edge", "v2", "sil3", "edge3", "v3", "scale")})
    n = max(1, len(d["parts"]))
    summ = {"n_parts": len(d["parts"])}
    for f in ("score", "sil", "edge", "v2", "sil3", "edge3", "v3"):
        summ[f"select_{f}"] = sum(max(p["cands"], key=lambda x: x.get(f, 0.0))["iou"] for p in d["parts"]) / n
        xs = np.array([(c.get(f, 0.0), c["iou"]) for p in d["parts"] for c in p["cands"] if c.get("variant")])
        summ[f"pearson_{f}"] = float(np.corrcoef(xs[:, 0], xs[:, 1])[0, 1]) if len(xs) > 2 else 0.0
    summ["ceiling"] = sum(max(c["iou"] for c in p["cands"]) for p in d["parts"]) / n
    d["summary_v2"] = summ
    json.dump(d, open(a.out, "w"))
    print("[rc2] " + json.dumps(summ), flush=True)


if __name__ == "__main__":
    main()
