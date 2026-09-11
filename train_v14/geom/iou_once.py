"""One centered volumetric IoU, as a subprocess so the caller can bound its cost.

`iou_pair` can take minutes on real-part geometry: when both boolean engines fail it
falls back to ray-parity Monte Carlo, whose cost is driven by mesh face count (observed
143 s and 251 s for 20k-face pairs, and the module's own note records 56 min for a
1.13M-face candidate). Python threads cannot be interrupted, so bulk scoring runs this
in a subprocess and kills it on timeout.

    python iou_once.py <pred.stl> <gt.stl>     ->  {"iou_centered": 0.873} on stdout
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from iou import iou_pair  # noqa: E402

if __name__ == "__main__":
    try:
        r = iou_pair(sys.argv[1], sys.argv[2])
        print(json.dumps({"iou_centered": float(r["iou_centered"])}))
    except Exception as e:
        print(json.dumps({"iou_centered": 0.0, "error": f"{type(e).__name__}: {e}"}))
