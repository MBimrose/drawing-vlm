"""Self-distilled think tier (H6c): h6b-n1655 generated in THINK mode on its own family training parts; keep up to
--per-part draws with IoU >= --min-iou (its own think + its own code), PNG from the tier dir.
    python build_self_tier.py --bo <scored trainT json> --png-dir <tier>/png --out <tier dir>"""
import argparse, json, os, shutil
ap = argparse.ArgumentParser(); ap.add_argument("--bo"); ap.add_argument("--png-dir"); ap.add_argument("--out")
ap.add_argument("--min-iou", type=float, default=0.8); ap.add_argument("--per-part", type=int, default=2)
a = ap.parse_args(); os.makedirs(os.path.join(a.out, "png"), exist_ok=True); n = parts = 0
with open(os.path.join(a.out, "accepted-000.jsonl"), "w") as f:
    for p in json.load(open(a.bo))["candidates"]:
        cs = sorted([c for c in p["cands"] if c.get("exec") and float(c.get("iou") or 0) >= a.min_iou and (c.get("think") or "").strip()],
                    key=lambda c: -float(c["iou"]))[: a.per_part]
        if not cs: continue
        parts += 1; shutil.copy(os.path.join(a.png_dir, p["key"] + ".png"), os.path.join(a.out, "png", p["key"] + ".png"))
        for c in cs: f.write(json.dumps({"key": p["key"], "iou": float(c["iou"]), "think": c["think"], "code": c["code"]}) + "\n"); n += 1
print(f"self tier: {n} rows / {parts} parts -> {a.out}")
