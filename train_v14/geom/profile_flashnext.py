"""Profile one training step of Qwen3.8-Flash-Next on a single node (no FSDP,
device_map=balanced over 8 GPUs) to find which op dominates. Text-only 4096
tokens, forward + backward, torch.profiler key_averages by CUDA time."""
import os, sys, time
import torch
sys.path.insert(0, "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/train_v14")
M = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/models/Qwen3.8-Flash-Next"
from transformers import AutoConfig, AutoModelForMultimodalLM
from flashnext_ple import replace_ngram_embedding

SEQ = int(os.environ.get("PROF_SEQ", 4096))
cfg = AutoConfig.from_pretrained(M)
cfg.use_cache = False
if hasattr(cfg, "text_config"):
    cfg.text_config.use_cache = False
t0 = time.time()
model = AutoModelForMultimodalLM.from_pretrained(M, config=cfg, dtype=torch.bfloat16,
                                                 device_map="balanced", low_cpu_mem_usage=True)
print(f"loaded in {time.time()-t0:.0f}s", flush=True)
replace_ngram_embedding(model, M)
model.train()
for n, p in model.named_parameters():
    p.requires_grad_(n.endswith("q_proj.weight") or n.endswith("in_proj_qkv.weight"))
dev0 = next(model.parameters()).device
ids = torch.randint(1000, 200000, (1, SEQ), device=dev0)
labels = ids.clone()

def step(tag):
    torch.cuda.synchronize()
    t = time.time()
    out = model(input_ids=ids, labels=labels, use_cache=False)
    torch.cuda.synchronize(); tf = time.time() - t
    out.loss.backward()
    torch.cuda.synchronize(); tb = time.time() - t - tf
    print(f"[{tag}] seq={SEQ} fwd={tf:.1f}s bwd={tb:.1f}s loss={out.loss.item():.3f}", flush=True)
    model.zero_grad(set_to_none=True)

step("warmup-ref")
step("reference-indexer")
from flashnext_qsa import patch_qsa_indexer
patch_qsa_indexer()
step("warmup-fast")
step("fast-indexer")
from torch.profiler import profile, ProfilerActivity
with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA]) as prof:
    step("profiled")
print(prof.key_averages().table(sort_by="cuda_time_total", row_limit=30, max_name_column_width=70))
print(prof.key_averages().table(sort_by="cpu_time_total", row_limit=15, max_name_column_width=70))
