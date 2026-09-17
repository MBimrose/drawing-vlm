"""Overlay a candidate's drawing on the input drawing, view by view (the repair-turn image).

The input sheet is kept as is (black geometry, blue annotations); each candidate view, matched to
its input view and brought to the input's scale exactly as rc_metric2.sheet_score_v3 does, is
painted RED at the input view's position. Ink that is only red = geometry the candidate has and
the drawing does not; black with no red on it = geometry the candidate is missing.
    python rc_overlay.py --input in.png --cand cand.png --out overlay.png
"""
from __future__ import annotations
import argparse, io
import numpy as np
from rc_metric2 import geometry_mask, views, _rescale, match_views


def overlay(png_in: bytes, png_cand: bytes) -> bytes:
    from PIL import Image
    from scipy.optimize import linear_sum_assignment
    from scipy.ndimage import binary_dilation
    base = np.asarray(Image.open(io.BytesIO(png_in)).convert("RGB")).copy()
    A, B = views(geometry_mask(png_in)), views(geometry_mask(png_cand))
    if A and B:
        ma, mb = geometry_mask(png_in), geometry_mask(png_cand)
        pairs, S0 = match_views(A, B, ma.shape, mb.shape)
        ratios = [np.sqrt(A[i]["area"] / max(1, B[j]["area"])) for i, j in pairs if S0[i, j] > 0.5]
        f = float(np.clip(np.median(ratios), 0.4, 2.5)) if ratios else 1.0
        red = np.zeros(base.shape[:2], bool)
        for i, j in pairs:
            vb = _rescale(B[j], f); y, x, h, w = A[i]["bbox"]; hb, wb = vb["line"].shape
            y0, x0 = y + (h - hb) // 2, x + (w - wb) // 2          # centre the candidate view on the input view
            ys, xs = max(0, y0), max(0, x0); ye, xe = min(red.shape[0], y0 + hb), min(red.shape[1], x0 + wb)
            if ye > ys and xe > xs:
                red[ys:ye, xs:xe] |= vb["line"][ys - y0:ye - y0, xs - x0:xe - x0]
        red = binary_dilation(red, iterations=1)
        black = geometry_mask(png_in)
        only_red = red & ~binary_dilation(black, iterations=2)
        base[only_red] = (220, 30, 30)                              # candidate-only ink: solid red
        both = red & ~only_red
        base[both] = (base[both] * 0.6 + np.array([120, 0, 0]) * 0.4).astype(np.uint8)   # agreement: dark red tint
    out = io.BytesIO(); Image.fromarray(base).save(out, format="PNG"); return out.getvalue()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--input", required=True); ap.add_argument("--cand", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args(); open(a.out, "wb").write(overlay(open(a.input, "rb").read(), open(a.cand, "rb").read()))
