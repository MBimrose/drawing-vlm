"""Split a vr_serve --picks start file into fixed blocks of B sorted keys (2026-10-14, in-dist pipeline).
The chain for <name> is the union of its blocks' outputs (out/<name>.bNN.jsonl); blocks are claimed by runners on
either host (runner.sh). vr_serve processes each key independently, so splitting does not change the protocol.
    python make_blocks.py <starts.json> <name> [--b 24]   -> blocks/<name>.bNN.json"""
import argparse, json, os
ap = argparse.ArgumentParser(); ap.add_argument("starts"); ap.add_argument("name"); ap.add_argument("--b", type=int, default=24)
a = ap.parse_args()
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blocks"); os.makedirs(D, exist_ok=True)
S = json.load(open(a.starts)); keys = sorted(S)
for i in range(0, len(keys), a.b):
    f = os.path.join(D, f"{a.name}.b{i // a.b:02d}.json")
    tmp = f + ".tmp"; json.dump({k: S[k] for k in keys[i:i + a.b]}, open(tmp, "w")); os.replace(tmp, f)
print(a.name, len(keys), "keys ->", (len(keys) + a.b - 1) // a.b, "blocks")
