"""CPU check (2026-10-07): the trainer's rendering of T0 rows vs the server's token counts. For every row of a tier:
HF prompt tokens (labels == -100) vs the episode's final-call input_tokens, and prompt+answer vs input+output.
    python dsv41_t0_tokcheck.py <tier dir> <episodes.jsonl> [effort]"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
from dsv41_lora_train import load_tier, build_sample
from transformers import AutoTokenizer
from transformers.models.deepseek_v41.image_processing_pil_deepseek_v41 import DeepseekV41ImageProcessorPil
from transformers.models.deepseek_v41.processing_deepseek_v41 import DeepseekV41Processor
M = "/srv/scratch/bimrose2/models/DeepSeek-V4.1-Flash"; sys.path.insert(0, os.path.join(M, "encoding")); import encoding as dsenc
tok = AutoTokenizer.from_pretrained(M); proc = DeepseekV41Processor(image_processor=DeepseekV41ImageProcessorPil(), tokenizer=tok)
from dsv41_t0_rollout import SYS, SCRATCH
effort = int(sys.argv[3]) if len(sys.argv) > 3 else 25
eps = {}
for l in open(sys.argv[2]):
    r = json.loads(l); eps[f"{r['key']}__d{r['draw']}"] = r["turns"][-1]
ok = 0; rows = load_tier(sys.argv[1])
for row in rows:
    enc = build_sample(proc, dsenc, SYS, SCRATCH, row["png"], row["code"], proc.image_token, 10**9, None, row.get("think") or "",
                       row.get("reply"), effort, row.get("context"))
    n_pre = int((enc["labels"][0] == -100).sum()); n = enc["input_ids"].shape[-1]; t = eps[row["key"]]
    good = n_pre == t["input_tokens"]
    ok += good
    print(f"{row['key'][:34]:34s} ctx {len(row.get('context') or [])} prompt hf {n_pre} srv {t['input_tokens']} | full hf {n} srv {t['input_tokens'] + t['output_tokens']} {'OK' if good else 'MISMATCH'}")
print(f"{ok}/{len(rows)} prompts identical in length")
