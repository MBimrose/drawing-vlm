"""Flash-Next GPU smoke on H200: load, inspect classes, one generation."""
import io, sys, tarfile
import torch
from PIL import Image

M = "/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/models/Qwen3.8-Flash-Next"
from transformers import AutoConfig, AutoProcessor
cfg = AutoConfig.from_pretrained(M)
print("arch:", cfg.architectures, flush=True)
try:
    from transformers import AutoModelForMultimodalLM as AM
except ImportError:
    from transformers import AutoModelForImageTextToText as AM
processor = AutoProcessor.from_pretrained(M)
model = AM.from_pretrained(M, dtype=torch.bfloat16, device_map="balanced",
                           low_cpu_mem_usage=True)
model.eval()
print("loaded:", type(model).__name__, "| cuda:", torch.cuda.is_available(), flush=True)
# layer classes for the FSDP wrap policy
names = sorted({type(m2).__name__ for m2 in model.modules()
                if "DecoderLayer" in type(m2).__name__
                or "Block" in type(m2).__name__})
print("wrap candidates:", names, flush=True)

tf = tarfile.open("/projects/illinois/eng/ece/wpk/bimrose2/drawing_vlm/v14_bundle/shards/eval-000000.tar")
m = next(x for x in tf.getmembers() if x.name.endswith(".png"))
img = Image.open(io.BytesIO(tf.extractfile(m).read())).convert("RGB")
msgs = [{"role": "user", "content": [
    {"type": "image", "image": img},
    {"type": "text", "text": "Write a complete build123d Python script reconstructing the part in this engineering drawing. Export with export_step(part, \"output.step\")."}]}]
text = processor.apply_chat_template(msgs, add_generation_prompt=True, tokenize=False)
enc = processor(text=[text], images=[img], return_tensors="pt").to(model.device)
with torch.no_grad():
    out = model.generate(**enc, max_new_tokens=700, do_sample=False)
resp = processor.tokenizer.decode(out[0, enc["input_ids"].shape[1]:],
                                  skip_special_tokens=True)
print("=== GENERATION head:", flush=True)
print(resp[:900])
print("SMOKE-PASS" if "import" in resp else "SMOKE-WEAK")
