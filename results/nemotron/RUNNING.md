# Nemotron-3.5-Super-VL-120B-A12B port — running log

Task: port the best pipeline (e55 SFT -> GRPO --train-raw -> EI rft2 -> rp3) to
nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16 (HF sha fc067b34), same eval protocol.
Host: wpk-serv-20, GPUs 4-7 ONLY (afm8 on 0-3). Everything under /srv/scratch/bimrose2.

## 2026-10-15

- 10:44 serv-20 state: GPUs 0-3 hold ~28-30 GB each (others' processes), GPUs 4-7 empty, load 0.4.
- 10:45 weights: `hf download nvidia/NVIDIA-Nemotron-3.5-Super-VL-120B-A12B-BF16 --local-dir
  /srv/scratch/bimrose2/models/Nemotron-3.5-Super-VL-120B-A12B-BF16` (pid 2936284) -> done 10:47, 232 GiB, 64 shards.
- 10:48 container: `apptainer pull /srv/scratch/bimrose2/containers/vllm-v0.32.0.sif docker://vllm/vllm-openai:v0.32.0`
  (pid 2942923, cache/tmp under containers/), log logs/nemotron/pull_vllm.log.
- 10:55 data: e55 trained on `rft_strict90_all_dw423` (cluster; serv-20 only had the later `b` repack) ->
  rsync cluster `rft_strict90_all_dw423/shards` + `rft_real_abccode_train/shards` to serv-20 (same paths).
  tars_v14_dw423 (5000 shards), v14_bundle (data/v14_bundle), eval_cache_v15_dw423.pkl (md5 c32ad190... = cluster) already on serv-20.
- 10:51 `vllm/vllm-openai:v0.32.0` is NOT on Docker Hub (manifest unknown). Pulled the card's pinned build instead:
  `docker://vllm/vllm-openai:nightly-3f1bcfd82bb2e93fcd364fc7a5491718453a77e2` -> `containers/vllm-nemotron-3f1bcfd8.sif`
  (vLLM 0.32.0rc1.dev190+g3f1bcfd82, torch 2.14+cu130; has `nemotron_v3` reasoning parser, nemotron_h / nano_nemotron_vl).
- 10:52 training venv `/srv/scratch/bimrose2/.venv_nemo` (separate from .venv: installing causal_conv1d there would switch
  Qwen3.5's GDN conv path in the other pipelines): torch 2.13.0+cu130 / Triton 3.7.1 / torchvision 0.28 (cu130 index),
  transformers 5.16.1, accelerate 1.14.0, peft 0.20.0 (= .venv pins). `tmp/nemo_venv.sh`.
- 10:57-11:03 kernels from source: causal_conv1d 1.7.0 + mamba_ssm 2.3.2.post1 (CUDA ext), gencode trimmed to sm_100/sm_103,
  CUDA 13.0 (`tmp/nemo_kernels.sh`, `tmp/nemo_mamba.sh`, build dir `nemo_build/`). Import check OK (causal_conv1d_cuda,
  selective_scan_cuda, Triton ssd_combined / selective_state_update). transformers' NemotronHMamba2Mixer picks these
  up as the "original package" fallback (no hub kernels).
- 11:00 code snapshot for this campaign: serv-20 `/srv/scratch/bimrose2/nemotron/train_v14` (rsync of cluster train_v14
  *.py/*.sh/*.yaml/*.sbatch). Changes (cluster repo, all opt-in; Qwen paths unchanged):
  `train_sft_v14.py` (trust_remote_code, Nemotron arch dispatch + processor, `experts_implementation`, `freeze_routed_experts`,
  trainable-param print, `best_save_mode: trainable` = gather only trained params), `collate_v14.py` (Nemotron branch:
  raw PIL images to the processor; untraced rows rendered "<think>\n</think>code" so the no-think target follows the
  think-mode prompt as in Qwen), `env.sh` (preset DRAWING_VLM_TRACES_JSON wins), `serv19/run_vllm_nemotron_serv20.sh`,
  `geom/nemotron_collate_check.py`. Data env: serv-20 `nemotron/env_nemo.sh`.
- data-path trap found: `env.sh` reset DRAWING_VLM_TRACES_JSON to a serv-20 dir without legacy_keys_v14.txt ->
  "WARN legacy_keys_v14.txt missing — no renderer filter" (plain tier would include legacy-renderer sheets). Fixed for
  this campaign by pointing at `cycle2/wds/` (legacy keys md5 2148660a = cluster).
- 11:02 zero-shot server: `NAME=nemobase PORT=8600 MLEN=24576 run_vllm_nemotron_serv20.sh` (TP4, GPUs 4-7, MTP 3,
  GMU 0.85, 64 seqs), pid 2999954, log nemotron/logs/vllm-nemobase.log.
- 11:05 collator check (`geom/nemotron_collate_check.py`, 150 rows/tier, CPU): Nemotron rows p50 3.0-3.2k / max 3.9k tokens
  (image 2,400 tokens = native 1920x1280 at 32 px/token; Qwen e55 recipe: 1,107 tokens at max_pixels 1179648, i.e.
  Nemotron reads the sheets at 1.45x the linear resolution). Supervised tokens Nemotron/Qwen median 0.99-1.00.
  0% truncated at 5120 -> keep max_seq_len 5120. No mask-prefix warnings. Truncation honoured; legacy filter active (2,479 keys).
- 11:12 probe: prompt 2,546 tokens; zero-shot greedy draw thinks the full 16,000 tokens (55k chars) without answering;
  ~530 tok/s single stream (MTP 3).
- 11:20 server relaunched TP2 on GPUs 4,5 (`GPUS=4,5 TP=2 GMU=0.88 SEQS=256`), pid 3045653 — frees GPUs 6,7 for a
  2-rank plumbing debug of the training path in parallel with the zero-shot eval.
- 11:21 debug SFT `GPUS=6,7 nemotron/train_nemo.sh configs/nemo-debug.yaml` (2 ranks, accum 2, 6 steps), pid 3050282,
  log nemotron/logs/nemo-debug.log.
- 11:18-11:22 debug SFT ran (2 ranks GPUs 6-7, after fixing attn_implementation: the remote top-level class has no SDPA
  flag -> `{"": eager, llm_config: sdpa, vision_config: sdpa}`, experts `{llm_config: grouped_mm}`): loaded fine,
  trainable 8.115B / 121.51B, step 1 loss 0.799 tok_acc 0.797, step 2 loss 0.699 tok_acc 0.817 (2 ranks x accum 2 = 4 seqs/step;
  step 1 216 s incl. Triton JIT, step 2 ~9 s), GPU mem ~200 GB/rank at 2-way sharding.
- 11:22 STOPPED on coordinator instruction ("clear off server 20"): killed pgid 3045653 (vLLM nemobase TP2, GPUs 4-5,
  was still loading) and pgid 3055577 (debug SFT, GPUs 6-7). GPUs 4-7 at 0 MiB. No zero-shot numbers yet (eval never started).
  Work moves to serv-19 (all 8 GPUs, full FT) when main gives the go-ahead.

## 2026-10-15 (afternoon) — moved to serv-19, FULL fine-tune (main's go-ahead 12:46)

serv-19 = all 8 B300s ours (GPU 0 shares a 2.5 GB render_server.py of the user, pid 3640292: leave >= 5 GB free).
Not ours, never touch: CADFit edit_critic runner.py, Claude remote-session processes. serv-20 = other agent (no compute).
- 12:48 pull from serv-20 (rsync --bwlimit 400 MB/s, `tmp/pull_nemo.sh`, pid 3320786, log logs/nemotron/pull_from_s20.log):
  weights, vllm-nemotron-3f1bcfd8.sif, .venv_nemo (python home = shared NFS uv python, exists on serv-19), nemotron/ code, nemo_build/.
- data on serv-19, md5-checked against the cluster: tars_v14_dw423 (name+size listing of all 5,000 tars identical, shard_000000
  md5 equal), rft_strict90_all_dw423 shards 0/76, rft_real_union5_dw423 shard 3, data/eval_cache_v15_dw423.pkl, data/v14_bundle
  manifest, data/legacy_keys_v14.txt, data/exec_bad_keys_v14.txt. Pulled: rft_real_abccode_train (md5 =), data/traces_v14.json,
  mech_benchmarks/{bench_b,fullpool_dw423} (eval caches md5 =). Rebuilt rft_mix_u6_gt_dw423 (110 links). Env: nemotron/env_nemo19.sh.
- Design (main): FULL FT of all LLM params incl. routed experts, vision frozen, pure-bf16 FSDP2 + bf16_sr_adamw (bf16 weights with
  stochastic-rounded updates, bf16 grads, fp32 moments: 12 B/param ~ 182 GB/GPU), validated first vs fp32 AdamW on the
  frozen-expert config (nemo-optA = fp32 AdamW mixed-bf16, nemo-optB = bf16_sr pure bf16; 2 ranks each, same seed/data, batch 64
  = 1 x 32 accum x 2, constant LR 5e-6 after 10 warmup steps, 100 steps, val loss at 50/100).
- Code added: train_sft_v14.py `RouterLoadMonitor` (per-layer expert-load max/mean, CV, dead share; stop on collapse),
  `BroadcastBuffers` (cpu_ram_efficient_loading: 8 x 243 GB host copies > 1.84 TB, so rank 0 loads; buffers are demoted
  and would keep placeholder values on ranks 1-7 -> router e_score_correction_bias garbage; broadcast from rank 0 at train begin).
  HF NemotronH has no router aux loss and never updates e_score_correction_bias -> kept as HF defines (fixed).
  Configs: nemo-optA/B.yaml, nemo-fullft(.yaml|-smoke.yaml), accelerate_fsdp2_{2gpu_nemotron_purebf16,8gpu_nemotron_purebf16}.yaml.
  Scoring on ccc0442: train_v14/sbatch/nemo_score.sbatch (/dev/shm python). vLLM: serv19/run_vllm_nemotron_serv19.sh.
- 13:00 pull done; weights listing md5 = serv-20 (676e3e87). Code synced (cluster train_v14 -> serv-19 nemotron/train_v14).
  Kernel check on serv-19 B300: fused mamba_split_conv1d_scan_combined fwd/bwd OK with the copied .venv_nemo.
- 13:01 launches (serv-19):
  - zero-shot server `NAME=nemobase PORT=8600 MLEN=24576 SEQS=256 GPUS=4,5,6,7 run_vllm_nemotron_serv19.sh` (TP4, MTP 3), pgid 3359840,
    log nemotron/logs/vllm-nemobase.log
  - optimizer check A `GPUS=0,1 CORES=0-47 train_nemo.sh configs/nemo-optA.yaml` pgid 3360059, log nemotron/logs/nemo-optA.log
  - optimizer check B `GPUS=2,3 CORES=48-95 train_nemo.sh configs/nemo-optB.yaml` pgid 3360060, log nemotron/logs/nemo-optB.log
- 13:05 zero-shot generation `NAME=nemobase MTOK=16000 BENCHES="real benchb" nemotron/eval_nemo.sh` (4 client shards x 12
  workers; prompt md5 = cluster), pid 3391698, log nemotron/logs/eval_nemobase.log. Scoring: ccc0442 job 11471834
  (`sbatch --export=NAMES="real_nemobase benchb_nemobase" nemo_score.sbatch`), outputs results/nemotron/.
- 13:10 optimizer arms at ~74 s/step (2 ranks, batch 64), BUT data order differed between arms (step-2 loss A 0.812 vs B 0.844
  with LR 0 at step 1): webdataset seeds the shard resampler, the shard shuffle (WDS_SEED or unseeded random.randint) and
  the sample shuffle from pid/time. Added opt-in `DRAWING_VLM_DATA_SEED` to data_v14.py (deterministic resampler per
  rank/worker, WDS_SEED, seeded shuffle buffer; unset = old behaviour). Verified: two processes -> identical first 8 rows.
- 13:25 killed arms (pgids 3360059/3360060; logs kept as nemo-opt{A,B}.unseeded.log) and relaunched with DRAWING_VLM_DATA_SEED=43:
  A pgid 3405072 (GPUs 0,1), B pgid 3405073 (GPUs 2,3).
- 13:27 zero-shot real-144 generation done (19 min; only 150/1,152 draws contain code — most hit the 16k cap mid-think);
  bench B generating. ccc0442 job 11471834 scoring real_nemobase.
- 13:30 seeded arms paired at steps 1-2 (0.7789/0.7795, 0.8430/0.8431) then B fell fast (0.63 by step 7, 0.45-0.50 by 14)
  while A stayed ~0.78-0.85. Probe runs (accum 2, lr 5e-6 from step 1, 4 steps; `param_probe` callback, configs
  nemo-probe{A,B}.yaml, logs nemotron/logs/nemo-probe{A,B}.log): A's optimizer holds all 648 live FSDP2 params (fp32) and they
  move; after ONE update, loss A 0.592 vs B 0.504 on the same batch. Mechanism: in A the bf16 compute copy is
  round-to-nearest of the fp32 master, and a 5e-6 Adam step (~2.5e-4 relative) is far below half a bf16 ulp (~2e-3 relative),
  so A's forward model does not change for ~8 full-LR steps (longer in warmup); B's stochastic rounding applies the expected
  update every step. A is not broken, it lags. Killed run-2 A (pgid 3405072, log nemo-optA.run2.log) for the probes;
  13:40 relaunched seeded A for the full 100 steps (B keeps running).
- 13:45 chained the synthetic-pool zero-shot (`BENCHES=full`, after bench B; pid 3467497, log nemotron/logs/eval_nemobase_full.log)
  + ccc0442 scoring job 11472523 (NAMES=full_nemobase). Reference files symlinked into results/nemotron (real/benchb/full x
  qwenbase/e55ctl/ent_t10_s120/rft2_rl_s60) so `eval_table.py --dir results/nemotron` works.
- RESULT zero-shot real-144 (K=8, think, 16k tokens; ccc0442 score+vote): nemobase vote 0.041 / d0 0.005 / first-exec 0.036 /
  mean 0.011 / best-of-8 0.042 / exec 0.027 (150/1,152 draws have code, 31 execute). vs Qwen3.8-27B base (0.064):
  vote -0.023 [-0.056,+0.010] (n.s.).
- geom/nemotron_finalize_ckpt.py: makes a fine-tune servable (adds base mtp.* head + demoted buffers, rewrites index, base
  config/code/tokenizer files; fails on any unexpected key).
- 14:02 zero-shot bench B generation done; full-pool zero-shot generation started (GPUs 4-7).
- 14:41 arm B (bf16_sr) done: val/loss step 50 0.5813, step 100 0.5516. Arm A at step 50: val 0.5895.
- 14:42 save test `nemo-savetest.yaml` (frozen-expert pure-bf16, 1 step, full gather-save via save_full_model, demoted buffers)
  on GPUs 2,3, pgid 3674110 -> runs/nemo-savetest/best_model, then nemotron_finalize_ckpt.py.
- RESULT zero-shot bench B (280): nemobase vote 0.044 / d0 0.002 / first-exec 0.041 / mean 0.009 / best-of-8 0.046 / exec 0.029
  (64/2,240 execute). vs Qwen3.8-27B base 0.082: vote -0.039 [-0.066,-0.011]. Failure mode = runaway thinking: median think
  54k chars (real-144) = the 16k-token cap; 13% of draws reach an answer.
- 14:50 save test: full gather-save 227 GB (~4 min at 2 ranks). nemotron_finalize_ckpt.py: trained key set = base minus
  1,040 mtp + 43 buffers, plus 64 HF-only RADIO layer_scale*.lambda1 (all exactly 1.0 = identity; dropped). After finalize: 43,079
  keys = base. Also removes torch _fsdp_*.py that save_pretrained copies as "custom code". vLLM TP2 loads it (GPUs 2,3, test
  server pgid 3701337, stopped): coherent think trace, MTP mean acceptance length 3.23 (74%).
- 15:02 RESULT optimizer check (frozen-expert config, 2 ranks each, batch 64, constant LR 5e-6 after 10 warmup steps, 100 steps,
  DRAWING_VLM_DATA_SEED=43 -> identical batches; step-1/2 losses equal to 4 decimals):
  | steps | A fp32 AdamW | B bf16_sr | B-A |
  | 3-10 | 0.7530 | 0.6477 | -0.105 |   | 11-20 | 0.5389 | 0.4806 | -0.058 |   | 21-30 | 0.4520 | 0.4292 | -0.023 |
  | 41-50 | 0.3954 | 0.3881 | -0.007 |  | 71-80 | 0.3683 | 0.3655 | -0.003 |  | 91-100 | 0.3350 | 0.3332 | -0.002 |
  steps 51-100 paired B-A -0.0035 [-0.0041,-0.0030]; val loss (16 fixed rows) step 50 A 0.5895 / B 0.5813, step 100 A 0.5511 /
  B 0.5516. Grad norm last 10 steps 52.7 / 52.2. Router (frozen experts, router trained): max/mean load median 8.8 (step 10)
  -> 10.9 / 10.7 (step 100), no dead experts, both arms alike. Verdict: bf16_sr tracks fp32 AdamW (early lead = A's bf16
  compute copy lagging the fp32 master; converged by step ~100) -> full FT with bf16_sr_adamw.
- 15:03 paused full-pool zero-shot (killed pgids 3467497 eval chain + gen clients, 3359840 vLLM; resumable from partials,
  ~100/256 parts per shard done) to free all 8 GPUs; full-FT smoke `nemo-fullft-smoke.yaml` GPUS=0-7 CORES=0-191, pgid 3746862,
  log nemotron/logs/nemo-fullft-smoke.log.
- 15:22 RESULT full-FT smoke (8 ranks, pure bf16 + bf16_sr_adamw, 20 steps, cosine over 20, lr 5e-6, batch 64 = 1 x 8 accum x 8):
  trainable 120.857B of 121.51B (vision 0.654B frozen). Load: rank 0 only (cpu_ram_efficient_loading), 41 buffers broadcast,
  identical |sum| 5.086309e+05 on all 8 ranks. Steady 18-19 s/step (steps 5-9, 11-19; step 1 124 s incl. JIT). Step-10 eval
  (16 rows) + full gather-save 227 GB: ~160 s. GPU memory 210-216 GB per GPU (GPU 0 ~215 GB incl. the user's 2.5 GB) ->
  ~60 GB headroom; host RAM peak ~260 GB. Train loss 0.684 (step 1) -> 0.33 (steps 19-20); val 0.6411 (s10) -> 0.6187 (s20).
  Router: max/mean load median 8.80 (s5) -> 10.02 (s20), max 18.8 -> 19.6 (L36), dead-expert share mean 0.000 / max 0.002.
  Smoke checkpoint finalizer dry-run: key set = base. Projected full run: 4,000 x 18.5 s = 20.6 h + <= 16 eval/save x 2.7 min
  ~ 21-22 h.
- 15:25 resumed full-pool zero-shot: vLLM DP2 x TP4 on GPUs 0-7 (pgid 3808106, log vllm-nemobase-dp2.log) + eval chain
  `BENCHES=full WORKERS=24` (pgid 3808107, log eval_nemobase_full2.log); preemptible (resumable) when the full SFT is approved.
- 15:26 GATE A report sent to main; WAITING for go-ahead before the full SFT (configs/nemo-fullft.yaml).

## 2026-10-15 15:35 — FULL SFT (main's GO)
- Stopped the resumed zero-shot synthetic run (pgids 3808107 eval chain, 3808106 vLLM DP2xTP4); partials kept:
  nemotron/results/full_nemobase.shard{0-3}.json.partial.json = 100 parts each (400 / 1,027). Cancelled ccc0442 job 11472523
  (resubmit `NAMES=full_nemobase nemo_score.sbatch` once generation is finished).
- 15:36 launch `DRAWING_VLM_DATA_SEED=43 GPUS=0-7 CORES=0-191 nemotron/train_nemo.sh configs/nemo-fullft.yaml`, pgid 3828982,
  log nemotron/logs/nemo-fullft.log, output nemotron/runs/nemo-fullft/{best_model,final}. Recipe: e55 (60/20/20 exact shards,
  exec filter, detailed prompt, seq 5120, batch 64 = 1 x 8 accum x 8, 4,000 steps, cosine -> 10%, warmup 3% = 120 steps,
  lr 5e-6), all LLM params incl. routed experts (120.857B trainable), vision frozen, projector trainable, native-res images,
  pure-bf16 FSDP2 + bf16_sr_adamw, val (16 rows) every 250 -> best_model (full gather) + final, router monitor every 10 with
  auto-stop (max/mean > max(3x baseline, 20) or dead share +0.25). Disk policy (main): keep /srv/scratch < 50% (now 19%);
  runs/nemo-savetest and runs/nemo-fullft-smoke kept (deletions wait for the user).
- 15:55 full SFT healthy: step 49/4000, 17.7 s/step (ETA ~19.5 h -> ~11:30 Oct 16 incl. evals), loss (rank 0, 10-step means)
  0.740 (s10) -> 0.601 -> 0.521 -> 0.424 (s40); router max/mean median 8.7 -> 9.5, max 18.8-19.2 (L36), dead 0.000.
  Watchdog (cluster, scratchpad watch_ft.sh): exits on done / crash / collapse / nan / mean loss > 0.9 / 40-min stall.
- 15:58 post-training driver `nemotron/post_sft.sh` staged on serv-19 (waits for TRAIN DONE): finalize best_model + final ->
  serve FT TP4 GPUs 0-3 :8601 (standard eval: K=8, think, 2,400 tokens; real-144, bench B, synthetic pool; TAG nemoft) and base
  TP4 GPUs 4-7 :8600 (resume zero-shot synthetic, 16k). Scoring on ccc0442 submitted from the cluster when generation nears done.

## 2026-10-16 — slowdown diagnosis + warm restart (user: "3 with one as a fallback", then "Restart is ok")
- Step time 18 s (steps 50-150) -> 26-39 s (150-1000) -> 40-55 s (1000-1300) -> ~34 s (1300-1960). Val (16 rows) improved at
  every eval: 0.5128 (250) 0.4945 (500) 0.4841 (750) 0.4787 (1000) 0.4784 (1250) 0.4758 (1500) 0.4711 (1750).
- No outside cause: only our 8 ranks on the GPUs, clocks 2032 MHz, no throttle reasons / ECC errors, data local and prefetched
  (workers ~3% CPU), disk 19%. GPUs show 100% util at 15-20% memory bandwidth with one rank at a time dropping idle -> ranks
  stall on host-side work and the others wait in collectives. py-spy (rank 0 main thread): ~50% autograd backward, ~30% the
  RouterLoadMonitor hook (torch.bincount on CUDA = host sync per router per forward), plus per-micro-batch .item() syncs in
  vlm_loss and HF's isnan nan-filter. These syncs were present in the 18 s/step phase too, so they are not proven to be the cause.
- Restart build (train_sft_v14.py, opt-in): router counts via index_add_ (no sync); lean_sync (loss/acc kept on device, no nan
  filter); StepTimer (step_timing_every: per-rank GPU drain time, wait at a tiny all_reduce [straggler waits least], tokens,
  allocator retries / device alloc+free deltas, reserved GB); Trainer.lr_resume (continue cosine_with_min_lr over 4000 from
  global step S with a 50-step linear re-warm for the fresh Adam moments; formula checked against the logged lr at steps
  200-1000 to 4 digits). Config configs/nemo-fullft-r2.yaml (seed 44, DRAWING_VLM_DATA_SEED=44, max_steps 4000-S).
- 10:25 serv-19 nemotron/restart_r2.sh armed (log nemotron/logs/restart_r2.log): on the first new-best eval after step 1750
  (expected step 2000) it stops post_sft.sh + the training pgid, finalizes best_model, installs the staged code
  (nemotron/train_v14_r2_stage), launches r2 (log nemotron/logs/nemo-fullft-r2.log, runs/nemo-fullft-r2) and
  post_sft_r2.sh. Caveat for the write-up: optimizer state is reset once at step S.
- 10:54 restart fired at the step-2000 new best (val 0.4703); 10:57 r2 launched from global 2000 (max_steps 2000), post_sft_r2.sh
  armed. Buffers |sum| 5.086309e+05 (= base), first lr 5.719e-08 (= 2.859e-06 / 50, correct).
- RESULT: r2 is ~36 s/step from its first steps (step 20 window 36.4 s/step) -> the slowdown is NOT process state (fresh
  process, clean allocator: 0 retries, no device alloc/free churn) and NOT the bincount/.item() syncs (removed in r2). It
  follows the WEIGHTS: base weights 18 s/step (smoke + steps 1-150), trained weights ~35 s. Leading hypothesis: MoE routing
  skew from the trained router (grouped_mm wgrad tiles scale with the busiest expert per micro-batch), unverified.
  StepTimer end-of-step waits are ~0.1 s on all ranks (no persistent straggler); tokens/rank/step 25-27k.
- r2 logging bug: lean_sync stores loss.detach(), which HF's in-place `loss *= num_processes` then scales -> logged train
  loss is 8x (step 10: 1.6431 = 8 x 0.2054). Training is unaffected; divide logged r2 train loss by 8. Fix (clone) on next edit.
- ETA r2: 2000 x ~36 s ~ 20 h -> ~07:00 Oct 17, then post_sft_r2.sh (finalize, eval). Optimizer reset once at global 2000.

## 2026-10-17 training done + Gate B eval
- r2 val (global = 2000 + r2 step): 0.4664 (2250) 0.4672 0.4608 (2750) 0.4606 (3000) 0.4624 0.4601 (3500, best) 0.4622
  0.4604 (4000, final). TRAIN DONE 06:31; best_model (3500) + final finalized (key sets = base).
- Eval (K=8, draw 0 greedy + 7 at T 0.7, 2400 tok; ccc0442 score + vote; paired vs results/nemotron refs):
  real-144 nemoft vote 0.450 (e55ctl 0.516; -0.066 [-0.103,-0.031]), exec 0.636 (e55 0.788).
  bench B nemoft 0.464 (e55ctl 0.509; -0.046 [-0.070,-0.020]), exec 0.663. Zero-shot nemobase 0.041 / 0.044.
- Diagnosis: nemoft SKIPS THINKING on 22% of draws (252/1152 real; e55 0/1152): it closes the forced "<think>\n" at once
  and writes code (32 of them in the auto-converted `_plane_1`/Polyline-dump style, 139 run into repetition loops to the cap
  -> empty code). Those draws: exec 0.29, mean IoU 0.083; the thinking draws: exec 0.73, mean IoU 0.379 (e55 0.396).
  Source: the untraced "<think>\n</think>code" rows in the e55 mix (collate_v14 _nemotron_msgs); Qwen learned to always
  think, Nemotron did not. Greedy 8k-token probe (probe_real_nemoft_greedy8k.json on serv-19): 18/144 hit 8000 (loops),
  only 3 finish in 2400-4000 -> a longer budget recovers ~2%; not run.
- Fix (inference): gen_openai_bo.py --prefill / eval_nemo.sh PREFILL="<think>\n1." (assistant prefill via
  continue_final_message; all 900 traces start "1."). real-144 nemoft_pf: no-think 0, empty 1/1152, exec 0.769, vote 0.489
  (+0.039 [+0.014,+0.068] vs nemoft; vs e55ctl -0.028 [-0.062,+0.006] = tied). bench B / synthetic _pf scoring.
- Final (vote): real 0.489 / bench B 0.497 / synthetic 0.897 (prefill; -0.019 [-0.027,-0.012]) vs e55 0.516 / 0.509 / 0.917; with the prefill
  Nemotron ties e55 at best (bench B -0.012 [-0.031,+0.006]) and is 0.15-0.18 below GRPO/EI on the real benches.
- 2026-10-17 user: "Ok so this is a dead end." Port closed; RL not run. vLLM servers stopped, serv-19 GPUs freed.
  Checkpoints kept (runs/nemo-savetest, nemo-fullft-smoke, nemo-fullft, nemo-fullft-r2) pending the user's call.
