"""Per-layer ground truth from vLLM (2026-10-07): offline LLM (TP4+EP, eager) with forward pre-hooks on every decoder
layer's attention and FFN modules; dumps the normalized sublayer INPUTS for the first N tokens of a parity text
sequence (rank-local tensors, one file per rank). Compare with dsv41_unitcheck.py --dump-sub (HF) to find the first
module where the two implementations diverge. Runs inside the vLLM image (dsv41_vllm_layerdump.sh)."""
import json, os, sys
os.environ.setdefault("VLLM_ALLOW_INSECURE_SERIALIZATION", "1")
from dsv41_vllm_hooks import reg, dump  # noqa: E402


if __name__ == "__main__":
    from vllm import LLM, SamplingParams
    ref, n, out, base = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
    os.environ["VDUMP_OUT"] = out
    ids = json.load(open(ref))["text"][0]["ids"][:n]
    llm = LLM(model=base, tokenizer_mode="deepseek_v41", tensor_parallel_size=4, enable_expert_parallel=True, enforce_eager=True,
              max_model_len=8192, gpu_memory_utilization=0.80, load_format="safetensors", limit_mm_per_prompt={"image": 1 if os.environ.get("VDUMP_IMAGE") else 0},
              max_num_seqs=4, max_num_batched_tokens=8192, enable_prefix_caching=False)

    print("[vdump] hooks:", llm.apply_model(reg), flush=True)
    if os.environ.get("VDUMP_IMAGE"):   # image prompt: the first image record of ref.json, same chat messages as the rollouts
        import base64, pickle
        r = json.load(open(ref))["image"][0]
        pj = json.load(open("/scratch/bimrose2/train_v14/geom/dsv41_grpo_prompts.json"))
        png = pickle.load(open(os.path.join(r["bench"], "eval_cache_v15.pkl"), "rb"))["samples"][r["key"]]["png"]
        msgs = [{"role": "system", "content": pj["system"]}, {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + base64.b64encode(png).decode()}},
            {"type": "text", "text": pj["user"]}]}]
        o = llm.chat(msgs, SamplingParams(max_tokens=1, temperature=0.0),
                     chat_template_kwargs={"thinking": True, "enable_thinking": True, "reasoning_effort": 50})
        print(f"[vdump] image prompt {len(o[0].prompt_token_ids)} tokens, identical to ref: {list(o[0].prompt_token_ids) == r['prompt_ids']}", flush=True)
    else:
        o = llm.generate([{"prompt_token_ids": ids}], SamplingParams(max_tokens=1, temperature=0.0, prompt_logprobs=0))
        lp = o[0].prompt_logprobs
        nll = [-d[ids[i]].logprob for i, d in enumerate(lp) if d is not None]
        print(f"[vdump] {len(ids)} tokens, offline vLLM NLL {sum(nll)/len(nll):.4f}", flush=True)


    print("[vdump] saved:", llm.apply_model(dump), flush=True)

