"""Debug: what the CSA2 `shared` dict holds after each compressed layer's attention in the HF draft (2026-10-07)."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import argparse, torch
ap = argparse.ArgumentParser(); ap.add_argument("--ref"); ap.add_argument("--n", type=int, default=128)
ap.add_argument("--model", default="models/DeepSeek-V4.1-Flash"); ap.add_argument("--chunked-attn", type=int, default=0); ap.add_argument("--patch", default="")
a = ap.parse_args()
from dsv41_parity import load_model
model, proc, tok = load_model(a)
ids = torch.tensor([json.load(open(a.ref))["text"][0]["ids"][: a.n]], device=model.device)
layers = [m for m in model.modules() if type(m).__name__ == "DeepseekV41DecoderLayer"]
def desc(v):
    if torch.is_tensor(v): return f"T{tuple(v.shape)}{str(v.dtype)[6:]}" + (f" min{int(v.min())} max{int(v.max())}" if v.dtype in (torch.long, torch.int32, torch.int64) and v.numel() else "")
    return repr(v)[:40]
for L in (2, 3, 8, 20, 21, 24):
    att = layers[L].self_attn
    def pre(m, args, kw, L=L):
        print(f"[dbg] L{L} pre kwargs: {sorted(kw.keys())} past={type(kw.get('past_key_values')).__name__}", flush=True)
    def post(m, args, kw, out, L=L):
        sh = kw.get("shared")
        print(f"[dbg] L{L} shared after: " + ", ".join(f"{k}={desc(v)}" for k, v in (sh or {}).items()), flush=True)
    att.register_forward_pre_hook(pre, with_kwargs=True); att.register_forward_hook(post, with_kwargs=True)
for uc in (False, True):
    print(f"[dbg] ===== use_cache={uc}", flush=True)
    with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16):
        model(input_ids=ids, attention_mask=torch.ones_like(ids), use_cache=uc)
