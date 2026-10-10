"""Part lists for the DeepSeek GRPO loop (2026-10-06).
train: hard real training parts (e55 mean < 0.75, best > 0.1, var > 0; corpus 4 + corpus 2), GT mesh present, one
       deterministic Random(0) order over the union -> round r takes rows [r*P, (r+1)*P) (no repeats until exhausted).
eval:  the held-out real bench (certified keys with GT, = probe_openai_vlm's list). NEVER in the training pool.
    python dsv41_grpo_parts.py train <out.tsv> <bench>:<keys.txt> [<bench>:<keys.txt> ...]
    python dsv41_grpo_parts.py eval <out.tsv> <bench>
    python dsv41_grpo_parts.py slice <all.tsv> <round> <P> <out.tsv>
"""
import os, pickle, random, sys

mode = sys.argv[1]
if mode == "train":
    rows = []
    for spec in sys.argv[3:]:
        b, kf = spec.split(":")
        rows += [(b, k.strip()) for k in open(kf) if k.strip() and os.path.exists(os.path.join(b, "gt_meshes_v15", k.strip() + ".stl"))]
    random.Random(0).shuffle(rows)
    open(sys.argv[2], "w").write("".join(f"{b}\t{k}\n" for b, k in rows)); print(len(rows), "training parts")
elif mode == "eval":
    b = sys.argv[3]; c = pickle.load(open(os.path.join(b, "eval_cache_v15.pkl"), "rb"))
    keys = [k for k in c["pools"]["certified"] if os.path.exists(os.path.join(b, "gt_meshes_v15", k + ".stl"))]
    open(sys.argv[2], "w").write("".join(f"{b}\t{k}\n" for k in keys)); print(len(keys), "eval parts")
elif mode == "slice":
    rows = [l for l in open(sys.argv[2]) if l.strip()]; r, p = int(sys.argv[3]), int(sys.argv[4])
    sel = [rows[(r * p + i) % len(rows)] for i in range(p)]
    open(sys.argv[5], "w").write("".join(sel)); print(len(sel), "parts for round", r)
