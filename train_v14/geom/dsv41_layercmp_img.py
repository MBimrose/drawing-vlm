"""Per-layer HF vs vLLM on an image prompt, split by image-token vs text positions (2026-10-07)."""
import sys, torch
d = torch.load(sys.argv[1]); hf = d["layers"]; ids = d["ids"][0]
v = torch.load(sys.argv[2] + ".rank0.pt")
img = ids == 129264
def rel(a, b):
    return float((a - b).norm() / (b.norm() + 1e-30))
for i in list(range(0, 6)) + list(range(6, 40, 3)):
    row = []
    for k in ("attn_in", "attn_out", "ffn_in", "ffn_out"):
        a, b = hf.get(f"{k}.{i}"), v.get(f"{k}.{i}")
        if a is None or b is None or a.shape != b.shape: row.append(f"{k} -"); continue
        row.append(f"{k} img {rel(a[img], b[img]):.3f} txt {rel(a[~img], b[~img]):.3f}")
    print(f"L{i:02d} " + " | ".join(row))
