"""Answer-only logits check (2026-10-27): on N rows of the e55 mix, the cross-entropy from logits_to_keep logits must
equal the full-logits one, and the logits tensor shrinks. Loads the model on one GPU.
    python geom/answer_logits_check.py <model_dir> [N] [processor_kwargs_json]"""
import json, sys, os
import torch
import torch.nn.functional as F
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from transformers import AutoProcessor, AutoModelForMultimodalLM
from data_v14 import build_mixed_v2
from collate_v14 import VLMCollator, answer_targets

mid, n = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 6
pk = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
proc = AutoProcessor.from_pretrained(mid, **pk)
kw = dict(max_seq_len=5120, system_prompt="detailed", reasoning_effort="medium", trace_style="think")
full, ans = VLMCollator(proc, **kw), VLMCollator(proc, answer_logits_only=True, **kw)
model = AutoModelForMultimodalLM.from_pretrained(mid, dtype=torch.bfloat16, device_map={"": 0}, attn_implementation="sdpa")  # one GPU, as in training (62 GB)
model.eval()
dev = next(model.parameters()).device
ds = build_mixed_v2(reasoning_frac=0.2, image_aug=False, exec_filter=True, rft_frac=0.6, seed=43)
worst = 0.0
for i, row in enumerate(ds):
    if i >= n:
        break
    res = []
    for col in (full, ans):
        b = {k: (v.to(dev) if torch.is_tensor(v) else v) for k, v in col([row]).items()}
        labels = b.pop("labels")
        with torch.no_grad():
            lg = model(**b).logits
            l2, t2 = answer_targets(lg, labels)
            ce = F.cross_entropy(l2.reshape(-1, l2.size(-1)).float(), t2.reshape(-1).to(l2.device), ignore_index=-100)
        res.append((float(ce), tuple(lg.shape)))
    worst = max(worst, abs(res[0][0] - res[1][0]))
    print(f"row {i}: full CE {res[0][0]:.5f} logits {res[0][1]} | answer-only CE {res[1][0]:.5f} logits {res[1][1]}", flush=True)
print(f"max |diff| {worst:.2e}")
