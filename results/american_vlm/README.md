# American open-weight VLM screen (started 2026-10-26)

User (2026-10-26): "I need to do a pivot to open weight american VLMs, can you please do a search of recent releases and
find the best candidates to run experiments with. I need to replace qwen 3.8, it is ok if it heavier like Nemotron 3.5
Super / Super VL. Can you do some initial experiments on server 19 and 5 please".

## Candidates (checked on Hugging Face 2026-10-26)

What matters for this task: a drawing is 1920 x 1280 with small dimension text. The question is whether the model sees the
sheet at native resolution. The 27B e55 recipe downscales to 1.18 MP (max_pixels 1179648).

| Model | Org, date | Size | Image budget | License | Status |
|---|---|---|---|---|---|
| **Muse-Glimmer-30B** (`meta-models/Muse-Glimmer-30B`) | Meta, 2026-08-09 | dense 29.8B (1.85B perception encoder) | 4,096 tokens of 28 px = 3.2 MP; a sheet is ~3.1k tokens | Apache 2.0, not gated | top pick: closest drop-in for Qwen3.8-27B |
| **Gemma 4 31B-it** (`google/gemma-4-31B-it`) | Google, 2026-03-11 | dense 31.3B (0.57B vision) | `max_soft_tokens` 70-1120; 1120 = 2.6 MP, a sheet ~1.07k tokens (default 280 would blur the text) | Apache 2.0 | top pick |
| **Nemotron 3.5 Super VL 120B-A12B** | NVIDIA, 2026-10-12 | MoE 121B / 12B active | 13k patches | OpenMDW | already fine-tuned on e55 (`nemoft_pf`): synthetic 0.897 / held-out 0.497 vs 27B 0.917 / 0.509 (−0.012 [−0.032, +0.006]) |
| Nemotron 3.5 Bolt 74B-A9B (`...-Bolt-74B-A9B-BF16`) | NVIDIA, 2026-10-09 | MoE 74B / 9B active (Super VL compressed) | 13,312 patches = 3.4 MP | NVIDIA | zero-shot gate; reuses the Nemotron port |
| Gemma 4 26B-A4B-it | Google | MoE 26B / 4B active | as Gemma 4 | Apache 2.0 | downloaded on serv-05, not run |
| Inkling-Small / Inkling (`thinkingmachines/`) | Thinking Machines, 2026-07 | MoE, 532 GB / 1.9 TB | — | Apache 2.0 | too big for full FT on one box (LoRA only) |
| Phi-4-reasoning-vision-15B | Microsoft, 2026-03 | 15B | 3,600 patches = 0.9 MP | MIT | downloaded; its template replaces our system prompt; small |
| Molmo2-O-7B / Granite Vision 4.1 4B | Ai2 / IBM | 7B / 4B | — | Apache 2.0 | too small to replace the 27B |
| Llama 4 Scout / Maverick | Meta, 2025-04 | MoE 109B / 400B | — | gated | our HF token gets 403 (access not granted); older than Glimmer |

Not American, or no image input: Mistral Large 4 (France); Molmo2-4B/8B (Qwen3 backbone); Reflection Beam, gpt-oss and
poolside Laguna (text only).

## Experiments

1. **Zero-shot gates** (serv-19, `train_v14/serv19/zs_american_gates.sh`). Main protocol: K=8 (draw 0 greedy + 7 at T 0.7 /
   top_p 0.95), think, 2400 tokens, the e55 prompt, on real-144 / synthetic 1,027 / bench B. Servers:
   - Glimmer: TP2 :8901 (`muse_glimmer` parser).
   - Gemma 4 31B: TP2 :8902 (`gemma4` parser, `max_soft_tokens` 1120).
   - Bolt: TP2 :8903 (`nemotron_v3` parser).

   Scored on ccc0442 (`nemo_score.sbatch` → this folder). These give each model's "Off-the-shelf" row; the 27B's was 0.041 / 0.017.
2. **Full fine-tune on the exact e55 recipe** (60/20/20 RFT / reasoning / plain, exec filter, image aug, lr 6e-6 cosine →
   10%, 4,000 × 64 rows, vision frozen). Only the model, its FSDP layer classes and its image budget change.
   - Gemma 4 31B → serv-05 (8x H200, the 27B e55 run's own hardware). `configs/am-gemma4-31b-e55recipe.yaml`, seq 5120.
   - Muse-Glimmer-30B → serv-19 (8x B300) after the gates. `configs/am-glimmer-30b-e55recipe.yaml`, seq 6144.
   - Port: `collate_v14.py` native-image path (raw sheet to the model's own processor); `train_sft_v14.py` processor
     branch (`processor_kwargs`); `geom/collate_check.py` checks masking and lengths.
3. Then the 27B's pipeline on the winner: vote → GRPO → EI → visual repair.

Known risk, from the Nemotron port: in both new templates an untraced row ("plain" tier, 20%) trains the model to answer
without thinking:
- Gemma 4: no `<|channel>thought` block.
- Glimmer: straight to `assistant to=user`.

Nemotron learned to skip thinking on 22% of draws and lost 0.04 until evaluated with a thought prefill. Evaluate the
fine-tunes with and without a prefill (Gemma `<|channel>thought\n1.`, Glimmer ` to=self<|message|>1.`).

## Log
- 2026-10-26 14:00: candidates downloaded: Gemma 4 31B / 26B-A4B on serv-05; Glimmer, Gemma 4 31B, Bolt, Phi-4-rv on serv-19.
  - e55 data copied to serv-05.
  - serv-05 venv `.venv_g4` = a copy of serv-19's `.venv` (torch 2.13, transformers 5.16.1).
- 14:04: zero-shot gates started. Glimmer and Gemma serve fine, and both write valid build123d for a text prompt. Bolt was relaunched 14:08 (missing serve script).
- 14:14: Gemma 4 smoke 1 failed in accelerate's rank-0 loading on Gemma 4's 62 checkpoint-valued persistent buffers.
  Fix: `demote_persistent_buffers` + `broadcast_buffers`. Smoke 2 started 14:17.
- 14:19: Gemma 4 smoke 2 failed at FSDP lazy init: the tied `lm_head` shares `embed_tokens.weight`, and accelerate's FSDP2
  tied-weight path groups the embedding with the final norm while the head falls to the root group.
  - Fix: one-line patch in serv-05 `.venv_g4/.../accelerate/utils/fsdp_utils.py` (original kept as `.orig`) so the head joins the embedding's group. The 27B's head is not tied, which is why this never came up.
- 14:30: **Gemma 4 31B smoke passed**: 24.4 s/step on 8x H200, loss 56 → 32 in 20 steps (summed scale), all 8 ranks' buffer checksums identical. The full 4,000-step run started 14:30, ETA ~Oct 27 18:00.
- 14:30: zero-shot real-144 done. Under the main protocol's 2,400-token cap the base models are still thinking when cut off:
  - empty answer: Glimmer 100%, Gemma 94%, Bolt 94% (Bolt writes its code inside the reasoning block).
  - median reasoning: ~9.5k characters for Glimmer, ~7.5k for Gemma.
  - So the off-the-shelf rows will be near zero, like the 27B's 0.041 / 0.017. That says nothing about how well they read drawings. A long-budget zero-shot run (16k tokens) was skipped to free serv-19 for the Glimmer fine-tune.
- Glimmer fine-tune queued on serv-19 (`am_glimmer_after_gates.sh`); it starts when the gates finish and the GPUs are free.
- 16:11: zero-shot gates done. Off-the-shelf rows (K=8 vote, mean IoU; real-144 / synthetic / held-out):
  Glimmer 0.000 / 0.024 / 0.006; Gemma 4 31B 0.005 / 0.003 / 0.000; Bolt 0.002 / 0.001 / 0.000 (27B: 0.041 / 0.017).
- 16:29: **Glimmer smoke passed** on serv-19 (loss 39 → 28 in 20 steps, 37.6 s/step incl. warm-up). Full run started 16:29.
- 16:15: **Gemma 4 run died at step 250** (val/loss 0.494, new best) while saving the optimizer: the H200s sit at the
  150 GB limit all run (the allocator survives by freeing its cache), but the DCP save's NCCL gather allocates outside
  the cache and got nothing. Fix: `torch.cuda.empty_cache()` after each eval and before the final save
  (`train_sft_v14.py`). The partial run is in serv-05 `amvlm/runs/_trash/am-gemma4-31b-e55recipe.oom250`. A 10-step
  save test (eval + save at step 5) runs before the 4,000-step restart.
- 16:40: save test passed (10 steps, saves at steps 5 and 10 complete with optimizer state, ~350 GB each).
  **Gemma 4 full run restarted 16:41** from step 0, ETA ~Oct 27 20:00.
- Glimmer: ~29 s/step after warm-up → 4,000 steps ≈ 32 h, ETA ~Oct 28 01:00.
- 22:50: both runs healthy; every save since the fix completed.
  - Gemma 4: step 918, 22.7 s/step, val/loss 0.509 / 0.497 / 0.473 at 250 / 500 / 750. ETA ~Oct 27 18:00.
  - Glimmer: step 1,203, now 14.7 s/step (down from ~25), val/loss 0.570 / 0.528 / 0.528 / 0.514 at 250-1000. ETA ~Oct 27 10:00.
  - Val losses are not comparable across models (different tokenizers and templates); the main-protocol eval decides.
- 10-27 01:00: **Gemma 4 OOM at step ~1,248** (backward, 2.5 GiB request with 129.7 GB allocated by PyTorch), so not
  fragmentation. Rank 0 drew a ~2.5k-token row, and the full-length 262k-vocab softcapped logits are the peak. GPUs idle
  01:00-03:10 (no crash watcher on that run, now added for both).
  - Fix: `answer_logits_only` (collate_v14 `answer_positions` → `logits_to_keep`): lm_head only at positions followed by
    a supervised label (~1/3 of a row), loss unchanged. `geom/answer_logits_check.py` on 6 rows: max |ΔCE| 2.4e-7,
    logits 3.4x smaller.
  - Resumed from checkpoint-1000 (val/loss 0.462) at ~03:10; steps 1,010-1,020 loss 0.23-0.26 (continuous), 18.9 s/step
    (was 22.7 before the fix), ETA ~Oct 27 19:00.
- Glimmer s/step by 100-step window: 24-25 (steps 0-300), 15-18 (300-1,200, ~18:00-23:30), 25 again from 1,300. No
  throttling, clocks at max, power 525-815 W of 1,100 W, CPU idle (load 17 of 344), the render server on GPU 0 idle.
  Same unexplained serv-19 pattern as Flash-Next in October (19 → 46 s/step).
- 10-27 15:46: Glimmer step 3,786 (val/loss best 0.4923 at 3,500), ~17:15 finish. Gemma step 2,902 (best 0.4277 at
  2,500), back to ~24 s/step, ~23:00 finish.
- FT eval runner `train_v14/serv19/am_eval_ft.sh` (serv-19, 4 TP2 servers): plain and thought-prefilled on real-144 /
  synthetic / bench B.
  - The prefill is a served chat template whose generation prompt ends `<|start|>assistant to=self<|message|>1.`
    (Glimmer) or `<|turn>model\n<|channel>thought\n1.` (Gemma). An assistant-message prefill renders into Glimmer's
    answer channel, so it can't be used. Both template rewrites change only the generation-prompt line (checked).
  - Each prefill server is probed once to log how the reply splits into reasoning and code.
  - Glimmer chain armed (tags `glft` / `glftpf`); scoring jobs 11867846 / 11867847 on ccc0442 begin 18:00.
- Gemma chain armed on serv-05 (`am_gemma_after_train.sh`: copy final/ to serv-19, then am_eval_ft tags `gmft` / `gmftpf` once serv-19 is free); scoring jobs queued to begin Oct 28 00:30.

**2026-10-27 17:05** Glimmer FT finished (exit 0): val/loss 0.4924 @3,250, **0.4923 @3,500 (best)**, 0.4954 @3,750, 0.4929 @4,000.
Eval chain started 17:06; probes OK (plain: 528-char numbered plan in reasoning + code in content; prefill: code in
content, reasoning None as expected since the `to=self` opener is in the prompt). **Bug fixed 17:15:** am_eval_ft.sh's
own `TAG=glft` leaked into eval_nemo.sh (`${TAG:-$NAME}`), so the prefill servers wrote into the plain stems; killed the
generators (servers kept), collided partials moved to american_vlm/results/_trash_collide on serv-19, script now passes
`TAG=$1` and reuses healthy servers; generation restarted 17:15 into real/benchb/full_glft and _glftpf.
Gemma at step 3,115 (val/loss 0.4245 @3,000, new best), ~22.9 s/step, finish ~23:00.

**17:40** Glimmer FT generation complete (6 stems). real_glftpf lost 1 part to a vLLM HTTP 500 ("multi-modal cache drift",
retryable, not retried by gen_openai_bo; likely from the requests aborted at 17:15) -> redrawn alone, now 144/144.
Plain glft: thinking on 84% / 77% / 75% of draws (real / bench B / synthetic); **empty code on 7% / 11% / 0.0%**.
Raw replay of 5 real-144 greedy empties (no reasoning parser, special tokens kept): 4 = thinking skipped -> straight to
`to=user` with long converter-style polyline code -> hit 2,400 tokens (a real failure at the shared budget); 1 = complete
code (finish=stop) that the muse_glimmer parser dropped when the reply opens directly in `to=user`. Prefill glftpf: ~0
empties. glftpf is the comparable config (as nemoft_pf); plain loses ~1/5 of its empties to the parser.
run_vllm_any_serv19.sh: `RPARSER=` (set, empty) now serves with no reasoning parser.

**20:30 Glimmer FT scored** (vote mean IoU / greedy draw 0; paired 2,000-sample bootstrap vs e55ctl, logs/tmp/paired_am.py):

| | Synthetic (1,027) | Real-144 (dev) | Held-out bench B (280) |
|---|---|---|---|
| 27B e55ctl | 0.917 / 0.804 | 0.516 / 0.390 | 0.509 / 0.402 |
| Nemotron nemoft_pf | 0.897 / 0.790 | 0.489 / 0.384 | 0.497 / 0.364 |
| Glimmer glft (plain) | 0.912 / 0.809 | 0.487 / 0.363 | 0.505 / 0.369 |
| **Glimmer glftpf (prefill)** | 0.919 / 0.808 | 0.507 / 0.366 | **0.522 / 0.403** |

glftpf − e55ctl: real-144 vote −0.009 [−0.046,+0.026]; bench B vote **+0.013 [−0.006,+0.031]**, d0 +0.000 [−0.032,+0.032].
glftpf − nemoft_pf: bench B vote +0.025 [+0.007,+0.044]. => Glimmer FT + prefill ties the 27B and beats Nemotron.
full_glftpf: score_partials done (7,346/8,216 exec); consistency_rerank OOM-killed at the 220 GB cgroup (job 11867847)
-> vote alone re-run as job 11876605 (450 GB). Gemma scoring jobs 11867877/78 raised to 300 GB.
full_glftpf vote (job 11876605): 0.919 (oracle 0.949); − e55ctl vote +0.002 [−0.005,+0.009], d0 +0.004 [−0.019,+0.026];
− nemoft_pf vote +0.022 [+0.014,+0.030]. Glimmer paper cells so far: off-the-shelf 0.007 / 0.001, FFT 0.808 / 0.403,
FFT + vote 0.919 / 0.522.

**21:0x** User cancelled the Flash-Next S1/finish and DeepSeek dse55 waiters on serv-19 (stopped). Data provenance note: the e55 mix the Glimmer/Gemma runs use is 20% certified Kimi K3 traces (traces_v14) + 60% RFT rows = the Qwen 27B's own verified samples incl. its thinking + 20% plain converter code.

## 2026-10-27 21:xx — user: fill the paper table (Off-the-shelf / LoRA / FFT / +vote / +GRPO / +repair / +GRPO+repair)
for the best American model ASAP, then two others. Columns: Glimmer 30B (best so far), Gemma 4 31B, Nemotron 3.5 Super VL.
Cells = synthetic / held-out bench B; off-the-shelf + FFT rows = greedy draw 0, vote rows = K=8 consistency vote.
Plan for Glimmer (each stage mirrors the Flash-Next pipeline, results/flashnext/PLAN.md):
- **GRPO** (serv-19 GPUs 0-3; `serv19/am_grpo_arm.sh`): ent_t10 recipe, LoRA r64 on LM attention + MLP, 200 steps, rollouts
  vLLM TP2 with the thought-prefilled template and NO reasoning parser; `grpo_round.py --raw-channels glimmer
  --think-prefill "1." --chat-template glftpf.jinja --max-seq-len 8704 --train-raw` (new: the parser drops the prefilled
  thought, so raw replies are split in the trainer and its processor renders the same template). Gate B = fn_parity.py
  raw-channel mode (vLLM sampled-token logprobs vs HF on the same tokens). Pick rule as fn1 (real-144 + synthetic only).
  Then one EI round (cycle-2 tier SFT from the GRPO adapter + ~60 GRPO steps), as Flash-Next.
- **Visual repairer** (serv-05 after Gemma; `configs/am-glimmer-rp3recipe.yaml`, `amvlm/glrp_serv05.sh`): rp3 recipe =
  continued FFT from Glimmer final, 300 steps lr 2e-6, rft_mix_rp3 (resolved copy), seq 10240, answer-only logits.
  Then the S2 chains (vote top-3 starts -> 3 repair chains, K=16 x 6 rounds) on bench B + synthetic.
- **GRPO + repair**: S1 from the EI policy. The 27B's v3b-EV verifier is a Qwen model -> for the American column use
  vote-ranked starts (S2-style) instead of the verifier pick (to state in the footnote).
- **LoRA**: r64 on the e55 recipe (serv-05 after the repairer); the 27B row used e1 data (footnote).
- Gemma 4 eval moved to serv-19 GPUs 4-7 (two servers, `PAIRS='4,5 6,7'`), chain relaunched on serv-05.

**21:06** Gate B (base, raw-channel parity, 6 parts / 4,073 tokens): mean_abs 0.0104, bias −0.0009, id_match 1.0 -> pass.
**21:44 GRPO gl1 running** (serv-19 GPUs 0-1 rollouts, 2-3 trainer). Steps 0-1: reward 0.19 / 0.32, exec 0.70 / 0.73,
entropy 0.19 / 0.16 (Flash-Next fn1: 0.21 / 0.33). ~8 min/step (train ~410 s): the balanced device map runs GPUs 2/3
as a pipeline (sampled: both busy in 2 of 77 busy samples), and TB 16 vs 4 changed nothing (first attempt kept as
runs/gl1.tb4). 200 steps ~27 h -> s120 ~Oct 28 13:00, s200 ~Oct 29 00:30. Data-parallel trainer = the speedup if needed.
Checkpoint evals armed (eval_gl1_a/b, GPUs 4-7 after the Gemma FT eval).
User 2026-10-27: no verifier anywhere (repair starts = 8-candidate vote); LoRA on e55 data OK; third column = Nemotron Super VL.
**23:3x** Gemma FT save fixed (fix_gemma4_final.py -> final_vllm: 62 non-persistent buffers + base config.json);
probes gmft / gmftpf return a numbered plan in reasoning and code in content. Eval relaunched on serv-19 GPUs 4-7.

## 2026-10-28 ~01:00 — Glimmer repair (no verifier) and LoRA armed
- Repairer `am-glimmer-rp3recipe` (serv-05, all 8 H200): smoke OK 23:37 (37 s/it), full 300 steps started 23:37, ~40 s/step
  -> done ~02:20.
- **Repair serving** (`serv19/am_rp_serve05.sh`, serv-05 GPUs 0-3, :8851/:8852 TP2, `NIMG=2`): base Glimmer chat template
  (generation prompt `<|start|>assistant`; the collator rendered the untraced repair rows as ` to=user<|message|>code`),
  NO reasoning parser (muse_glimmer drops replies opening in to=user); vr_serve takes the last fenced python block.
  vllm-nemotron-3f1bcfd8.sif copied to serv-05. `run_vllm_any_serv19.sh` gained `NIMG` (images per prompt, default 1).
- **S2 chains** (`pipeline/`): starts = glftpf K=8 vote -> top-3 distinct (`make_vote_picks.py`; r1 = the vote:
  bench B 0.522, synthetic 0.919; r2 0.510 / 0.886; r3 0.482 / 0.864) -> 3 chains, K=16 x 6 rounds, margin 0.1,
  6000 tok, T 0.7 (the 27B / Flash-Next S2 protocol). 165 blocks of 24 keys, bench B (36) first.
  Runners: serv-19 (`glpipe/am_s2_launch.sh`, 10 x 12 workers, cores 96-343, ssh tunnels to serv-05, 2-part probe first)
  + ccc0442 job 11879301 (`am_chains_c442.sbatch`, 5 x 12). Claims on serv-19 `glpipe/claims`. Summary: `pipeline/summary_am.py`.
- **LoRA row** (`configs/am-glimmer-lora-e55recipe.yaml`, `serv19/am_lora_serv05.sh`): r64 / alpha 128 on LM attention +
  MLP (the GRPO targets), e55 data, lr 1e-4, 4 GPUs x GA 8, 2,500 steps (the 27B e3 schedule), serv-05 GPUs 4-7 after
  the repairer servers are up.
- **EI round armed** (`serv19/am_ei.sh`, pid 151058 on serv-19; waits for `amvlm/grpo/GL1_BEST`, which I write after the
  gl1 step pick): SFT `configs/am-glimmer-rft2.yaml` (gl1 adapter warm start, cycle-2 mix, 955 x 16, lr 2e-5, FSDP2 x4 on
  GPUs 0-3) -> RL glei 60 steps (lr 1e-5, entropy floor 0.1694 = gl1's auto target, pool2) -> evals s20/s40/s60.
  GRPO + repair row = S2-style chains from glei's K=8 vote (no verifier).
**01:23 repairer OOM on serv-05**: rank 4 died at step ~155/300 (133.7 GB allocated on a 150 GB H200; the rp3 rows carry
two sheets at seq 10240); no checkpoint (save_strategy no). Moved to serv-19 GPUs 4-7 (4 B300, 288 GB):
`configs/am-glimmer-rp3recipe-s19.yaml` (4 ranks x 16 accum = the same batch 64), `serv19/am_rp_s19.sh` (smoke -> 300
steps -> copy the final to serv-05, where `am_rp_serve05.sh` still waits -> restart the gl1 eval lanes). The idle gl1 eval
lanes (waiting for adapter_step40) and their servers were stopped for it; s40 eval ~1.5 h late. Glimmer LoRA started now
on serv-05 GPUs 4-7 (no longer waits for the repairer servers).
**01:50** Smokes passed. Repairer (serv-19 GPUs 4-7) 58 s/it -> 300 steps done ~06:45. Glimmer LoRA (serv-05 GPUs 4-7):
PEFT 383.4M trainable (1.27%; the "[model] trainable 27.9B" line prints before the wrap), 20.6 s/it -> 2,500 steps ~16:30.

**03:xx Gemma 4 31B FT scored** (final_vllm; vote / d0):

| | Synthetic (1,027) | Real-144 (dev) | Held-out bench B (280) |
|---|---|---|---|
| Gemma gmft (plain) | 0.882 / 0.757 | 0.478 / 0.441* | 0.463 / 0.353 |
| **Gemma gmftpf (prefill)** | 0.888 / 0.760 | 0.502 / 0.463* | 0.497 / 0.392 |

(*real-144 column = first-exec, not d0.) gmftpf − e55ctl: bench B vote −0.013 [−0.032,+0.006], synthetic vote −0.029
[−0.037,−0.021]; − nemoft_pf: bench B vote −0.000 [−0.022,+0.021], synthetic −0.009 [−0.017,−0.001]. => Gemma ties
Nemotron on held-out, trails on synthetic, and is below Glimmer (0.919 / 0.522). Glimmer stays the "best model" column.
Gemma paper cells: off-the-shelf 0.000 / 0.000, FFT 0.760 / 0.392, FFT + vote 0.888 / 0.497.

**10-28 10:40 Scale-up: the 3 H200 nodes + campus cluster are free again (user).** The serv-05 / serv-19 stacks run on
the cluster unchanged: `train_v14/sbatch/mirror_srv.sbatch` copies venvs (.venv_g4, .venv_nemo + the uv Python), data,
models, finals, the vLLM image and CUDA 13 into `/projects/illinois/eng/ece/wpk/bimrose2/srvmirror`, and
`train_v14/sbatch/srv_exec.sh` runs commands in apptainer with that mirror bound to /srv/scratch/bimrose2.
- ccc0474 `pipeline/am_rp_cluster.sbatch` (job 11884124): 8 more Glimmer repairer servers (TP1) + 8 chain runners
  (ROOT `pipeline/h474`, same serv-19 claims) -> S2 chains ~5x the serv-05 serving capacity.
- ccc0451 `am_train_cluster.sbatch` CFG=am-gemma4-lora-e55recipe (job 11884129): Gemma LoRA row (Glimmer LoRA recipe,
  8 x GA 4 = batch 32).
- ccc0475 same with CFG=am-nemo-lora-e55recipe (job 11884130, .venv_nemo): Nemotron LoRA row, r64 on every dense LLM
  projection (attention q/k/v/o, Mamba in/out, shared experts, latent projections); routed experts frozen.
- ccc0441 (L40S) `am_eval_cluster.sbatch` (job 11884261): the gl1 s120/s160/s200 evals moved off serv-19 (adapters pulled
  when written; scoring job 11884268 local; s40/s80 scoring job 11884267 from serv-19).
- serv-19 GPUs 4-7: **Gemma GRPO gm1** (`serv19/am_grpo_gemma.sh`, gl1's recipe on the gmft LoRA; `grpo_round.py` /
  `fn_parity.py` gained `--raw-channels gemma`: thought closed by `<channel|>`, answer to `<turn|>`; parity gate first).
- Prepared: `configs/am-gemma4-rp3recipe.yaml` (Gemma repairer, rp3 recipe from final_vllm, seq 7168),
  `train_v14/sbatch/am_grpo_cluster.sbatch` (GRPO on an H200 node).
**11:45 status.**
- Gemma GRPO gm1 running (serv-19 GPUs 4-7): parity mean |dlogp| 0.027 (id match 1.0); first try died at the first update
  (Gemma 4 processor reads a flat image list as one sample -> `collate_v14._collate_native` now nests images per row for
  Gemma 4; the batch-1 SFT path is unchanged). Step 0 reward 0.18 / exec 0.71 (gl1 step 0: 0.19 / 0.70); 7.5 min/step ->
  s200 ~Oct 29 12:00.
- Gemma LoRA (ccc0451): smoke 14.8 s/it -> 2,500 steps ~21:15. Then the Gemma repairer (`am-gemma4-rp3recipe`, job
  11885463, afterany) on the same node; serving template `american_vlm/templates/gmrp.jinja` (enable_thinking pinned on:
  the repair rows were rendered '<|turn>model\n' + code). Gemma S2 starts/blocks ready in `pipeline_gemma/` (vote r1
  0.497 / 0.888 = the vote cells).
- Nemotron LoRA: 8 ranks cannot load on an H200 node (each rank materialises ~the model while the per-expert checkpoint
  is grouped: rank 1 had 29 GB anonymous at 8% of tensors; 8 copies > 1.5 TB) -> 4 ranks x GA 8 (same batch 32), weights
  staged on node-local disk (job 11885349).
- ccc0474 repair servers 8/8 healthy at 11:26, 8 runners claiming full-pool blocks. The node is CPU-bound (load ~146 on 128
  cores: rendering + scoring), not GPU-bound.
- Nemotron prepared: `templates/nemopf.jinja` (prefill "<think>\n1."), `--raw-channels nemotron`, the nemotron case in
  `am_grpo_cluster.sbatch`, `configs/am-nemo-rp3recipe.yaml` (repairer; routed experts frozen to fit one H200 node -> footnote).
**12:11 Nemotron LoRA running** (ccc0475, 4 ranks, job 11885694): two fixes on the way. (1) PEFT targets: runtime names are
`language_model.model.layers.N.mixer.*` (checkpoint keys say `backbone`); regex fixed in the config and in
`am_grpo_cluster.sbatch` -> 177.0M trainable (0.15%). (2) serv-19's .venv_nemo kernels (causal_conv1d, selective_scan)
were built for sm_100/103 only ("no kernel image" on H200): rebuilt in the MIRROR venv with sm_90 added
(`train_v14/sbatch/nemo_kernels_sm90.sbatch`, sources `srvmirror/nemo_build`, setup.py + compute_90). Smoke 27.2 s/it
-> 2,500 steps ~Oct 29 07:15.

## 10-28 15:50 status
- gl1 eval job 11884261 (ccc0441): 3 of 4 TP2 vLLM servers deadlocked in gloo init ("Timed out waiting 1800000ms") when
  started together; am_eval_cluster.sbatch now starts servers one at a time with distinct VLLM_PORT. Resubmitted as
  11889077 with gl1 s120/s140/s160/s180/s200; scoring 11884268 (s120/160/200) + 11889079 (s140/180).
- Gemma gm1 GRPO step evals s40/s80/s120/s160: job 11889086 on the 4 free H200s of ccc0475 (NSRV 2 x TP2, 100G);
  scoring 11889087.
- gl1 step 147 (reward 0.41, exec 0.99); gm1 step 40 (reward 0.39, exec 0.91).
- Gemma LoRA 1690/2500 (ETA ~17:50, then the Gemma repairer 11885463); Nemotron LoRA 630/2500 at ~19.6 s/it (ETA ~01:40).
- Glimmer S2 repair chains: 143/165 blocks claimed, 38 marked done on the cluster side + serv-19's out.

## 10-28 16:30 queue for the remaining cells
- `pipeline/am_rp_cluster.sbatch` gained `MODEL=gemma` (blocks `pipeline_gemma/`, claims serv-19 `gmpipe/claims`, Gemma
  repairer final -> fix_gemma4_final.py -> final_vllm served as gmrp with gmrp.jinja + max_soft_tokens 1120): job 11889176
  on ccc0451, afterok the Gemma repairer 11885463.
- Nemotron repairer `am-nemo-rp3recipe`: 4 ranks x 16 accum (batch 64 as the rp3 recipe; new
  `accelerate_fsdp2_4gpu_nemotron_purebf16.yaml`), STAGE=1: job 11889186 on ccc0474 afterany the Glimmer repair job.
- Nemotron S2 inputs: `pipeline_nemo/` starts from nemoft_pf K=8 vote (`make_vote_picks.py`): r1 0.497 / 0.897 (= the vote
  cells), r2 0.484 / 0.856, r3 0.431 / 0.830; 165 blocks `nmS2_*`, bench B first.
- vLLM image supports LoRA on Nemotron-H VL (SupportsLoRA; Mamba in_proj via MergedColumnParallelLinearVariableSliceWithLoRA,
  latent projections ReplicatedLinear). `am_eval_cluster.sbatch` gained `MODEL=nemotron` (nemotron_v3 parser + PREFILL
  "<think>\n1.", as nemoft_pf) and waits for cluster-trained adapters.
- LoRA-row evals: Gemma `gmlora` job 11889282 (ccc0442, 4 L40S, base Gemma 4 31B); Nemotron `nmlora` job 11889284
  (ccc0475, 4 H200, afterany the Nemotron LoRA). Scoring 11889517 (gl1 s140/s180), 11889518 (gm1 s40-s160),
  11889519 (gmlora, nmlora) on ccc0441; RHOST=local needs RDIR=<mirror>/american_vlm/results.

## 10-28 16:50 serv-05 released (user: needed for someone else)
- Stopped the two Glimmer repairer servers on serv-05 (GPUs 0-3); serv-05 GPUs now empty (the Glimmer LoRA there had
  finished; its final was already pulled into the mirror for eval 11884458). serv-05 is off-limits from now.
- The serv-19 runners (10, via ssh tunnels to serv-05) and the ccc0442 runners (job 11879301) were stopped (STOP_s19 /
  STOP_c442, runners killed; serv-19 launcher am_s2_launch.sh stopped, tunnels closed; ccc0442 `ports.txt` emptied so its
  job loop opens no tunnel). Cluster compute nodes refuse ssh forwarding, so they cannot reach the ccc0474 servers.
- 15 unfinished blocks (10 s19, 5 c442) released from serv-19 `glpipe/claims`; their partial outputs (records with an empty
  round dropped) copied to `pipeline/h474/out/` (vr_serve resumes by key; originals in `out_moved_to_h474/` on both
  sides). The 8 ccc0474 runners finish the remaining ~40 blocks alone (~75 min per block per runner -> ~23:00-24:00).
- `summary_am.py` now also reads `h*/out/`.

## 10-28 20:05 Glimmer visual-repair row DONE (glS2, vote starts, no verifier)
All 165 blocks finished on ccc0474 at 19:46 (`pipeline/summary_am.py --name glS2`, out/ + out_s19/ + h474/out/):
| | Bench B (280) | Synthetic (1,027) |
|---|---|---|
| chain-1 start = K=8 vote | 0.522 | 0.919 |
| single chain (c1) | 0.603 | 0.939 |
| **multi-start (3 chains, v3 pick)** = paper cell | **0.633** | **0.951** |
| oracle over chain finals | 0.676 | 0.960 |
| 27B S2 multi-start (verifier-era starts) | 0.664 | 0.949 |
glS2 − 27B S2: bench B −0.032 [−0.052, −0.011]; synthetic +0.002 [−0.004, +0.009]. Repair gain over the vote:
bench B +0.110 [+0.089, +0.133], synthetic +0.032 [+0.026, +0.039].
- ccc0441 eval servers: only the TP2 pair on GPUs 4,5 ever initialises (others die in the gloo barrier of
  in_the_same_node_as, twice, also with staggered start + distinct VLLM_PORT) -> node issue; the remaining gl1 evals
  (s120/s140/s180/s200) moved to ccc0474's 4 free H200s (TP1 x 4, job 11897066). `am_eval_cluster.sbatch` bug fixed:
  the final bare `wait` also waited on the servers, so finished eval jobs held their GPUs (11884458, 11889077 cancelled;
  11889282 / 11889086 are cancelled by a watcher when their last eval is done).

## 10-28 20:20 relay approved by the user -> used for the Gemma repair chains
The Glimmer chains had already finished on ccc0474 alone, so the relay goes to the Gemma S2 chains (job 11889176 on
ccc0451, starts ~22:15 after the Gemma repairer). RUNNING since 20:35 (user added the permission rule; first attempt was denied by the classifier
at 20:20): `pipeline/am_relay_launch.sh 11889176 ccc0451 gemma gmpipe` waits for the 8 servers, then starts on ccc0451 `tcp_relay.py` (cluster-internal address,
:38851-38858 -> the servers; exits with the job) and `rtunnel_keep.sh` (reverse ssh forward serv-19:18851-18858 -> ccc0451),
submits `pipeline/am_chains_relay.sbatch` on ccc0442 (5 runners x 12, ROOT `pipeline_gemma/r442`) and starts 8 runners on
serv-19 (`gmpipe/`, only if its load is < 150). All share serv-19 `gmpipe/claims`; `summary_am.py --name gmS2 --dir
../pipeline_gemma` reads out/, out_s19/ (rsync serv-19 gmpipe/out), h*/out and r*/out.
- **20:34 Nemotron repairer running** (job 11897195, ccc0474 GPUs 0-3): the first try (11889186) died in its smoke at
  processor load (`no attribute NemotronH_Omni_Reasoning_V3Processor`): 4 ranks wrote the HF dynamic-module cache for
  `best_model` at once and two imported a half-written file; the cache is complete now. Retry smoke exit 0 (loss 18.65 ->
  18.08), 55.8 s/it -> 300 steps ~01:20, then nemotron_finalize_ckpt.py before serving.

## 10-28 21:50
- **gl1 GRPO done** (200 steps, trainer exit 0, 21:42; last step reward 0.566 / best-of-8 0.685 / exec 0.98; step 0 was
  0.19). Adapters every 10 steps on serv-19. Step pick waits for the s120-s200 evals (real-144 + synthetic only), then
  GL1_BEST -> am_ei.sh (serv-19 GPUs 0-3, idle until then).
- ccc0474 eval job 11897066: weights load ~30-35 min per server from Lustre (100G cgroup, page cache thrash) and the
  staggered start serialises them -> lanes start ~22:10. Next time: stage the model to node-local /tmp, stagger only where needed.
- Gemma repairer 300/300 done (2h42m), saving; then job 11889176 (Gemma chains) + the relay launcher.
- Dataset statistics: `results/dataset_stats/README.md` (subagent, 2026-10-28).

## 2026-10-28 23:15 status
- **Glimmer LoRA row DONE** (r64, e55-recipe data, main-protocol vote): synthetic 0.880 / held-out 0.507 (real-144 0.509).
- gl1 GRPO step evals s120/s140/s180/s200 generated (ccc0474, 22:46); scoring on ccc0441 (s40 0.918/0.583, s80 0.909/0.606
  shown for reference only; the step is picked on real-144 + synthetic).
- Gemma LoRA row (gmlora) scored ~0.01: every candidate came back with empty code and empty reasoning, though training is
  healthy (val loss 0.445, token acc 0.92). Probe 11901962 (probe/probe_gmlora.sbatch, ccc0474 1 GPU) prints raw replies.
- Gemma S2 chains: ccc0451 (job 11889176) + relay runners on ccc0442 (11901939, via tcp_relay on ccc0451) + 4 serv-19 runners
  (reverse tunnel). serv-19 load ~200/344 cores (mostly another session's CADFit scan_cad).

## 2026-10-29 00:55: Gemma LoRA row was a port collision, rerunning
- Probe 11901962 (base gemma-4-31B-it + gmlora, 1 H200): proper numbered plan + build123d code. The adapter is fine.
- Cause: eval job 11889282 and 11884458 (Glimmer LoRA) both ran on ccc0442 on port 8970. 11889282's server died "Address
  already in use", and its lane loaded gmlora into 11884458's Glimmer server and generated there (empty code). gllora is
  clean: it finished at 17:29, before gmlora was loaded at 17:49. No other eval jobs overlapped on a node.
- Fixed am_eval_cluster.sbatch (per-job ports PB / DP, lane checks its own server pid). Old gmlora outputs ->
  _trash/gmlora_portclash (repo + mirror). Rerun: eval 11903468 (ccc0474, 4 GPU TP4), scoring 11903469 (ccc0442).
  nmlora eval resubmitted with the fixed script as 11903467 (after LoRA 11885694, ccc0475).

## 2026-10-29 01:20: correction, Glimmer LoRA cell
The LoRA row is a single greedy draw, like the FFT row: **0.778 / 0.364** (synthetic / held-out). The 0.880 / 0.507 noted
at 23:15 is LoRA + 8-candidate vote. Cells via scratch cells.py (d0 = draw-0 IoU, failures = 0; vote = consistency line).

## 10-29 04:50 status
- **Kimi-trace A/B re-laid out.** Arm A round 0 (11903924, ccc0474) OOMed in its smoke: Glimmer full FT at seq 6144 takes
  ~145 GB/GPU on serv-19's B300s, and an H200 has 140. Its chain then sampled nothing. Now all four training rounds run
  serially on serv-19 (`train_v14/serv19/ab_serial_s19.sh`, log `amvlm/ab/logs/serial.log`: B0 [running, 453/1500 at
  04:35, 25.6 s/it] -> A0 -> B1 -> A1). Both arms train on the same hardware. ccc0474 handles sampling, scoring and evals
  (`sbatch/ab_pull.sh` copies each final to the mirror; `ab_score.sbatch PUSH=1`; `am_eval_cluster MODEL=glimmer_plain`
  for arm B). Jobs: 11904882-11904889. ETA: B ~Oct 30 evening, A ~Oct 31 midday.
- **Glimmer GRPO step pick = s180** (on real-144 + synthetic only):

  | step | real-144 vote | synthetic vote |
  |---|---|---|
  | 40 | 0.582 | 0.918 |
  | 80 | 0.602 | 0.909 |
  | 120 | 0.605 | 0.893 |
  | 140 | 0.577 | 0.884 |
  | 160 | 0.601 | 0.892 |
  | 180 | **0.618** | 0.900 |
  | 200 | 0.613 | 0.901 |

  Its GRPO + repair chains (`pipeline_glgrpo/`, glgS2, same repairer, vote starts) go on ccc0474 until 10:45, bench B first.
- LoRA cells (single draw, synthetic / bench B): Gemma 0.727 / 0.360 (port-clash rerun); Nemotron synthetic 0.645,
  bench B scoring. Gemma GRPO (s40) vote 0.897 / 0.565.
- EI is stopped: its SFT mix was Qwen-derived.
- 05:15: **Glimmer FFT + vote + GRPO cell = 0.900 / 0.621** (gl1 s180 K=8 vote, synthetic / bench B; bench B looked at
  only after the pick). Repair job 11905140 on ccc0474 (165 glgS2 blocks; STOP_h474 at 10:45 from setup_glgrpo.sh).
  Nemotron repair 11903953: servers up 04:50 (the old 60-min health wait nearly expired), runners claiming nmS2 blocks;
  first records accept repairs.
- 16:30: **Glimmer FFT + vote + GRPO + repair, bench B = 0.665** (glgS2 multi-start, 36/36 bench-B blocks; vote start
  0.622; +0.042 [+0.022, +0.064] over its start; vs 27B S2 +0.001 [−0.020, +0.023]; vs glS2 0.633). Synthetic: 4/129
  blocks (one runner's synthetic block took 5.8 h); STOP_h474 at 10:49 freed ccc0474 at 16:28 for ab-sample-b.
  Resume the synthetic blocks on the next free H200 (`sbatch --nodelist=<node> --export=ALL,MODEL=glgrpo,NR=8,W=12
  pipeline/am_rp_cluster.sbatch`; rm the h<node>/STOP file first if reusing ccc0474).
- Alignment column: `train_v14/geom/align_cells.py` (+ `align_once.py`, `sbatch/align_cells.sbatch`), job 11909351 on
  ccc0441 (staging venv_meshalign to /dev/shm took 5 h on slow Lustre) -> `results/alignment/aligned_cells.md`.
- 17:05: **Gemma FFT + vote + repair = 0.925 / 0.617** (gmS2 multi-start; 165/165 blocks finished 11:12, serv-19 outputs
  rsynced to pipeline_gemma/out_s19; +0.037 / +0.120 over the vote start; vs 27B S2 −0.024 / −0.048).
  ccc0474: 11905140 cancelled at 16:55 (its last runner had started a retry of glgS2_full_c1.b04; claim released) ->
  ab-sample-b running. Glimmer GRPO+repair synthetic blocks moved to ccc0451 (11913421). Gemma GRPO + repair queued
  after it (pipeline_gmgrpo/, gm1 s40 vote starts 0.565 / 0.897, claims serv-19 gmgpipe; job 11913444).
  Nemotron repair (ccc0475): 37/165 blocks after 12 h (2 TP4 servers) -> ~40 h more.

## 10-29 19:00 status
- Alignment column done for every cell (results/alignment/aligned_cells.md, job 11909351, 50,667 programs, 0 errors). Aligned = max(centred, meshalign rigid ICP IoU); selection unchanged. Held-out gains: +0.045 to +0.060 on FFT/vote rows, +0.02 to +0.04 after GRPO/repair; the ranking of models is unchanged. Rerun 11914437 adds the Gemma repair outputs from serv-19 (out_s19) and the newly finished Nemotron cells.
- Nemotron LoRA held-out scored: 0.284 (synthetic 0.645).
- Nemotron repair held-out 279/280 parts: 0.614 (synthetic chains ~51/165 blocks, ~7 min/block -> ~13 h).
- Glimmer GRPO+repair synthetic on ccc0451: 12/129 synthetic blocks, ~4 blocks/h -> ~29 h.
- A/B: A0 at 1042/1500 on serv-19 (~22:15). Arm B: syn lanes sampled, scoring on ccc0442 (c2 executed 9,926/13,200).
- 19:05 alignment rerun 11914437 done: Gemma repair 0.925->0.937 / 0.617->0.649 (full n); Nemotron repair held-out complete (280): 0.613->0.647.

## 10-30 11:30 status
- **Glimmer FFT + vote + GRPO + repair complete: 0.953 synthetic / 0.665 held-out** (glgS2, 129/129 synthetic blocks).
  Synthetic: +0.052 [+0.045, +0.060] over its vote start 0.901; vs 27B S2 (no GRPO) +0.004 [−0.001, +0.010].
  27B GRPO + repair (verifier starts) is 0.961 / 0.721. Alignment for this cell: align_cells ONLY=... rerun.
- Arm A sampling 11904884 produced nothing: 8 vLLM servers each reading the 108 GB A0 final from Lustre were still
  loading weights at 00:43 when the 60-min health wait expired (arm B loaded in 15 min at 17:08). ab_sample.sh now copies
  the final to node-local /tmp (or /dev/shm) once on HOST=cc and waits up to 2 h (HW=480). Resubmitted 11927152 on ccc0474
  (score-a 11904885 on ccc0442 was waiting on GEN_DONE and picks it up). Arm A now ~4 h later than planned.
- B1 on serv-19 1719/2500 at 11:12 (23 s/it, done ~16:15). Gemma GRPO + repair 11913444 started on ccc0451 at 11:00.
  Nemotron repair synthetic 115/129.
- 16:45: **Nemotron FFT + vote + repair complete: 0.937 / 0.613** (nmS2, job 11903953 ended 13:52). vs its vote start
  +0.039 / +0.116; vs 27B S2 −0.012 [−0.019, −0.005] / −0.051 [−0.073, −0.030]. B1 done on serv-19 at 16:14; A1 waits
  for tier_a (score-a on ccc0442, ~17:15). Arm A sampling finished 13:23 (11/11, think kept on every candidate);
  eval-b 11904886 released at 16:43 on ccc0474 (was held to 17:00). ccc0475 free.
- 17:10: Gemma GRPO + repair held-out complete (36/36): **0.630** (+0.065 [+0.044, +0.086] over vote start 0.565; vs 27B S2 −0.034). Synthetic 13/129; added ccc0475 (11936396, MODEL=gmgrpo) to the shared claims. Nemotron repair aligned 0.947 / 0.647.
- 21:00: **A/B arm B (own samples, plain, no Qwen/Kimi) scored**: held-out d0 0.278 / vote 0.385 vs e55-mix Glimmer 0.403 / 0.522 (vote Δ −0.138 [−0.164, −0.112]); synthetic 0.789 / 0.891 vs 0.808 / 0.919 (vote −0.028); real-144 vote 0.398 vs 0.507. ab/compare_ab.py -> ab/compare_ab.md. Arm A: A1 training on serv-19 since 17:10 (~09:00 Oct 31), then eval-a 11904888 -> nscore 11904889.

## 10-31 13:45 Kimi-trace A/B result (ab/compare_ab.md)
Held-out vote: A (own + Kimi) 0.444, B (own, plain) 0.385, e55 mix 0.522. A − B +0.059 [+0.031, +0.086];
A − e55 −0.079 [−0.100, −0.058]. Synthetic vote: A 0.891 = B 0.891 < e55 0.919. Real-144 vote A − B +0.038 [+0.003, +0.075].
Exec rate held-out: A 0.695, B 0.599, e55 0.811. Kimi recovers ~43% of the own-data gap on real parts; the rest is
confounded with volume/rounds: own tiers are one round, ~36-39k synthetic rows over ~21-23k parts + ~2.6k real rows,
vs the e55 RFT tier's 155,655 rows over 84,513 parts from several Qwen rounds (rft_v1-v3).

## 10-31 15:00 user: "do 1 then 2" (A/B round 2 for arm A, then Nemotron GRPO). User will not include Qwen data in the paper.
- Round 2 for arm A: A1 samples 84k synthetic parts (round 1's 42k syn_s0..7 again + 42k new disjoint syn2_s0..7,
  `ab_build_benches.py --seed 31 --exclude`, srun 11947979 on ccc0442) + the real corpora (jobs_r2.txt, 19 jobs).
  Sampling 11948125/6/7 on ccc0474/0475/0451 (ab_sample.sh RND=1 TAG=a2). Scoring: claim-based ab_score.sbatch TAG=a2,
  packer 11948128 (ccc0442, PREV=scored_a: pools both rounds per part before the cap) + helpers 11948131 (ccc0475) /
  11948132 (ccc0474) after sampling. tier_a2 -> serv-19 `ab_r2_s19.sh` (pid 1501407) trains am-glimmer-ab-a2 (A1 final,
  2,500 steps, seed 44) -> eval (to submit after TRAIN_DONE) -> compare_ab.py.
- Nemotron GRPO nm1: am_grpo_cluster.sbatch MODEL=nemotron on ccc0451 (11948134, afterany its sampling job).
