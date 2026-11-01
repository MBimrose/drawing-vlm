"""Collator check for a new VLM (2026-10-26, American-VLM screen): run VLMCollator on N rows of the e55 v2 mix and
report token lengths, label-mask boundaries and the batch keys. CPU only.
    python geom/collate_check.py <model_dir> [N] [processor_kwargs_json]"""
import json, sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transformers import AutoProcessor
from data_v14 import build_mixed_v2
from collate_v14 import VLMCollator

mid, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 40
pk = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
proc = AutoProcessor.from_pretrained(mid, **pk)
print("processor", type(proc).__name__, "padding_side", proc.tokenizer.padding_side, pk)
col = VLMCollator(proc, max_seq_len=100000, system_prompt="detailed", reasoning_effort="medium", trace_style="think")
ds = build_mixed_v2(reasoning_frac=0.2, image_aug=True, exec_filter=True, rft_frac=0.6, seed=43)
lens, plens, traced = [], [], 0
for i, row in enumerate(ds):
    if i >= n:
        break
    b = col([row])
    ids, lab = b["input_ids"][0], b["labels"][0]
    k = int((lab == -100).sum())
    lens.append(len(ids)); plens.append(k); traced += bool((row.get("reasoning_content") or row.get("trace") or "").strip())
    if i < 2:
        print("keys", {kk: tuple(v.shape) for kk, v in b.items() if hasattr(v, "shape")})
        print("TARGET START:", repr(proc.tokenizer.decode(ids[k:k + 25])))
        print("TARGET END:", repr(proc.tokenizer.decode(ids[-12:])))
lens, plens = np.array(lens), np.array(plens)
print(f"rows {len(lens)} traced~{traced} | total tokens p50 {np.median(lens):.0f} p90 {np.percentile(lens, 90):.0f} max {lens.max()} "
      f"| prompt p50 {np.median(plens):.0f} | answer p50 {np.median(lens - plens):.0f} max {(lens - plens).max()}")
