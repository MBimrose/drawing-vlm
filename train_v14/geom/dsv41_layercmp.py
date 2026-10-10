"""Compare HF (dsv41_unitcheck.py --dump) vs vLLM (dsv41_vllm_layerdump.py) sublayer tensors layer by layer.
    python dsv41_layercmp.py <hf.pt> <vllm prefix>"""
import sys, glob, torch
hf = torch.load(sys.argv[1])["layers"]
vs = [torch.load(f) for f in sorted(glob.glob(sys.argv[2] + ".rank*.pt"))]
v = vs[0]
def rel(a, b):
    a, b = a.flatten().float(), b.flatten().float(); return float((a - b).norm() / (b.norm() + 1e-30)), float(torch.nn.functional.cosine_similarity(a, b, dim=0))
for i in range(40):
    row = []
    for k in ("attn_in", "attn_out", "ffn_in", "ffn_out"):
        a, b = hf.get(f"{k}.{i}"), v.get(f"{k}.{i}")
        if a is None or b is None: row.append(f"{k} -"); continue
        if a.shape != b.shape:
            if k.endswith("out") and len(vs) > 1 and b.shape == a.shape:
                pass
            row.append(f"{k} shape hf{tuple(a.shape)} v{tuple(b.shape)}"); continue
        r, c = rel(a, b)
        # sum over ranks too (in case vLLM keeps partial sums)
        if k.endswith("out") and len(vs) > 1:
            bs = sum(x[f"{k}.{i}"] for x in vs); r2, _ = rel(a, bs); row.append(f"{k} {r:.3f}/sum{r2:.3f}")
        else:
            row.append(f"{k} {r:.3f} cos {c:.4f}")
    print(f"L{i:02d} " + " | ".join(row))
