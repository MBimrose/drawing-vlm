# Flash-Next 180B full pipeline on serv-19 (started 2026-10-18)

User goal: "grind server 19 with the Flash-Next, run the entire training pipeline through, I want to see if we can make
it ever stronger than 27B."

Every stage is judged by a paired comparison against the 27B checkpoint at the same stage, on the main-table protocol:
K=8 (draw 0 greedy + 7 at T 0.7, think, 2400 tok), consistency vote, three benches, paired 2,000-sample bootstrap. The
test-time stage uses the S1 protocol.

| Stage | Flash-Next run | 27B reference | 27B vote: synthetic / real-144 / held-out |
|---|---|---|---|
| 1. SFT, e55 recipe | e59 (training, serv-19 x8) | e55 | 0.917 / 0.516 / 0.509 |
| 2. GRPO (ent_t10 recipe) | fn_grpo | ent_t10_s120 | 0.922 / 0.639 / 0.640 |
| 3. EI: cycle-2 tier SFT + short GRPO | fn_rft2, fn_rft2_rl | rft2_rl_s60 | 0.932 / 0.673 / 0.665 |
| 4. Test time: K=16 -> verifier -> 3 rp3 chains | fn S1 | EI + repair (S1) | 0.961 / 0.714* / 0.721 |

\* 143-part permissive bench.

## Stage details

1. **e59.** `configs/e59-flashnext-e55recipe.yaml`, launched by `fn55/train_e59.sh`. Afterwards abl_lane evaluates
   `final` and `best_model`, and ccc0442 scoring jobs 11648025/6 start 2026-10-20 22:00.
2. **GRPO.** The 27B recipe (cycle2/after_sft.sh, ent_t10):
   - Pool: real4 + c2 + fam hard keys.
   - lr 2e-5 from SFT (1e-5 for a mature adapter); T 1.0 with scaled logits, top_p 1; batch-std advantage.
   - 4 minibatches; KL 0; guard 0.6; entropy floor coef 0.1 (target auto or pinned), ceiling 0.35.
   - 16 parts x G 8, LoRA r64, about 120 steps (the 27B peaked at s120).

   Flash-Next port of `geom/grpo_round.py` (2026-10-19, defaults unchanged for the 27B):
   - The model spans the trainer GPUs through load_model's balanced device map, with the n-gram table on CPU.
   - The loss follows the logits' device.
   - `--lora-targets` takes e26's regex: attention, linear attention and shared expert (router and routed experts frozen).

   Layout: rollouts on vLLM TP4 with `--enable-lora` (Qwen4Exp declares SupportsLoRA in the image) on GPUs 0-3; the HF
   trainer on GPUs 4-7.

   Gates before the real run:
   - (a) vLLM hot-loads a Flash-Next adapter (test: e26fl).
   - (b) HF-vs-vLLM per-token logprob parity on sampled completions (the sampler mismatch was a real bug in both earlier ports).
   - (c) step time.
3. **EI.** The cycle-2 tier (5,502 search-verified programs >= 0.75 on 8,121 hard training parts; cycle2/ copied from
   serv-20) feeds a LoRA SFT initialised from the GRPO adapter (lora_init_adapter), then about 60 GRPO steps at lr 1e-5.
4. **Test time.** Flash-Next generates K=16; the 27B verifier and rp3 repairer run unchanged on its candidates.

## Levers beyond the 27B recipe (if a stage only ties)

- Re-mine the hard-key pools on Flash-Next's own rollouts (the current lists are e55-relative).
- Run an on-policy RFT round on Flash-Next's own samples.
- Train longer GRPO; the larger model may peak later than s120.

## Log
- 2026-10-18 21:44: e59 relaunched at ~46 s/step. The host is slow for environmental reasons: Aug/Sep runs did 19 s/step,
  and the Aug code is also 46 s/step now. ETA ~Oct 21 00:00.
- 2026-10-19 00:00: GRPO/EI inputs staged serv-20 -> serv-19 (job 11656452); grpo_round.py multi-device port compiled.
- 2026-10-19 10:35: the user restricted the campaign to serv-19 only (no H200s).
  - e59 is at step 1012, val 0.507 (s250) / 0.484 / 0.476 / 0.479 (s1000).
  - Host load fell to ~18 and steps run 31 s and falling, consistent with the CADFit-load hypothesis. ETA ~Oct 20 morning.
  - Armed `train_v14/serv19/fn_after_e59.sh` (log fn55/logs/after_e59.log). After e59's eval lanes it runs gate A
    (vLLM LoRA hot-load of e26fl on e59/final) and gate B (fn_parity.py base + LoRA; tolerance mean_abs < 0.06,
    |mean_diff| < 0.02, id_match > 0.95), then launches GRPO fn1 (fn_grpo_arm.sh). On failure it writes fn55/GATE_FAILED.
  - Scoring jobs 11648025/6 moved to begin Oct 20 12:00.
- 2026-10-21 02:13: e59 TRAIN DONE rc=0 (4,000 steps; val 0.4552 best @3250, 0.4555 final).
  - The first eval lanes died: vLLM custom all-reduce failed during CUDA-graph capture (`custom_all_reduce.cuh:164 invalid argument`), and train_e59.sh still printed "E59 EVAL LANES DONE".
  - Relaunched with `VLLM_EXTRA=--disable-custom-all-reduce`; generation finished 04:17 / 04:29. Scoring jobs 11648025/6 started 04:36.
  - fn_after_e59.sh now waits on the LANE_DONE markers, and the gate and GRPO servers carry the same flag.
- 2026-10-21 04:51: gates passed.
  - A: e26fl hot-load OK.
  - B: parity base mean_abs 0.028 / bias +0.0015 / id_match 1.0; LoRA 0.023 / +0.0022 / 1.0.
- 2026-10-21 04:52: GRPO fn1 launched from e59/final.
  - Step time ~6 min: gen 70-140 s, score 40-80 s, train ~160 s. 200 steps take ~20 h; s120 lands ~Oct 21 17:00.
  - The trainer's device map uses 2 of the 4 trainer GPUs (peak 217 GB).
  - Steps 0-2: reward 0.21 / 0.33 / 0.24, exec 0.70-0.77, entropy 0.13-0.16.
- 2026-10-21 07:49: **Stage 1 verdict: e59 TIES e55.** Main protocol (K=8 vote), synthetic / real-144 / held-out 280:
  - e59 final: 0.911 / 0.523 / 0.525.
  - e59 best_model: 0.909 / 0.518 / 0.527.
  - e55: 0.917 / 0.516 / 0.509.
  - Paired deltas, e59 − e55: synthetic −0.006 [−0.013, +0.000]; real-144 +0.006 [−0.020, +0.033]; held-out +0.015 [−0.005, +0.034].
  - Checkpoint chosen on dev benches only: final beats best_model on both synthetic and real-144, so final is the stage-1 model (already the GRPO fn1 start).
- 2026-10-21 23:20: GRPO fn1 at step 194/200. Training reward rose 0.30 -> 0.52 by s80, then stayed flat (s184-193: 0.519); exec 0.99; entropy 0.22-0.23; no guard trips. Evals for s40/80/120/160 are generated, and s200 is in progress.
  - The first scoring jobs (11716893/4, 11717774) died in 15 s: a ccc0442 reboot wiped /dev/shm, c2stage included.
  - nemo_score.sbatch now re-stages the venvs under flock. Re-submitted s40-s160 (11720331-5); s200 is queued behind GEN_DONE.
- 2026-10-21 23:53: fn1 finished all 200 steps. Real-144 (dev) vote, scored so far:

  | Step | Vote | vs e59 | vs 27B ent_t10 |
  |---|---|---|---|
  | s40 | 0.576 | | |
  | s80 | 0.598 | | s60 +0.008 [−0.016, +0.031] |
  | s120 | 0.619 | +0.096 [+0.065, +0.132] | s120 −0.020 [−0.045, +0.006] |
  | s160 | 0.609 | | s120 −0.031 [−0.054, −0.006] |

  - fn1 peaks at s120, like the 27B. Synthetic / held-out are scoring; the s200 eval is running.
  - From 01:30, serv-19 goes to the queued DeepSeek e55-recipe run (results/dsv41_e55/README.md, user request).
- 2026-10-22 00:30: user asked for the Flash-Next visual-repair and GRPO rows to complete the comparison to the 27B, then DeepSeek. In answer to a question, they chose a Flash-Next repairer (not reusing rp3) and an EI round that matches the 27B. The DeepSeek chain (dse55) is paused; its 256k-row tier keeps building. Queued on serv-19:

  1. **FNRP**, the rp3 recipe on e59/final (`configs/fnrp-flashnext-rp3recipe.yaml`, `fn55/fn_train_rp.sh`).
     - 300 steps at lr 2e-6, batch 64, seq 7168, all 8 GPUs; starts after the fn1 s200 eval.
     - Data: `rft_mix_rp3`, rebuilt on serv-19 from the cluster's symlink map. The 4 repair tiers were copied and md5-checked.
  2. **S2-FN chains** (`fnpipe/fn_s2_launch.sh`, `fn_runner.sh`).
     - Starts: e59's main-protocol K=8 vote → top-3 distinct (`make_vote_picks.py`; it reproduces the 27B's bench-B S2 starts 280/280) → 3 chains.
     - Repair loop: K=16 × 6 rounds, margin 0.1.
     - Repairer: FNRP on 2 TP2 servers (GPUs 4-7). Runners: 10 × 12 on serv-19 (cores 96-343) and 8 × 12 on ccc0442 through ssh tunnels (job 11721409, begins 06:30).
     - Bench B blocks run first, then synthetic. Real-144 is skipped (dev only).
     - Checks: serv-19's bench copies, renderer (draftwright 0.4.23 + font 5.25) and render scripts match the cluster's.
     - A dry run reproduced the start IoUs. Cost: exec 3.4 s + IoU 3.4 s + render 12 s per candidate.
  3. **EI** (`fn55/fn_ei.sh`, GPUs 0-3).
     - SFT `fn_rft2` (`configs/fn-rft2.yaml`): fn1's dev-picked adapter (`fn55/FN1_BEST`) warm-started, cycle-2 mix, 955 × 16, FSDP2 ×4.
     - RL `fnei`: the rft2_rl recipe, 60 steps, entropy target pinned to fn1's 0.1536. Rollouts TP2 on GPUs 0-1, trainer on GPUs 2-3.
     - Then main-protocol evals of s20/s40/s60.
  4. **S1-FN**, to prepare: fnei's dev-picked step K=16 → stage 2 (score, vote, render + v3, the 27B v3b-EV verifier) → `pg_make_starts` → 3 FNRP chains.
  5. Then the DeepSeek chain (`results/dsv41_e55/README.md`).
- 2026-10-22 01:10: fn1 s120 / s160 scored on all benches.

  | Step | Synthetic | Real-144 | Held-out | − e59 held-out | − 27B ent_t10_s120 (synthetic / real-144 / held-out) |
  |---|---|---|---|---|---|
  | s120 | 0.896 | 0.619 | 0.603 | +0.079 [+0.057, +0.101] | −0.025 [−0.033, −0.018] / −0.020 [−0.046, +0.006] / −0.037 [−0.056, −0.019] |
  | s160 | 0.901 | 0.609 | 0.615 | +0.090 | −0.021 / −0.031 / −0.026 |

  - **Stage 2: Flash-Next GRPO trails the 27B's GRPO.**
  - GRPO costs Flash-Next ~0.01 on synthetic (the 27B gained +0.005).
  - s40/s80/s200 synthetic still scoring; the pick (real-144 + synthetic) goes into `fn55/FN1_BEST`.
  - FNRP training started 00:58. The S2 launcher, EI round, S1 stage and wrap-up are armed; the DeepSeek chain waits on FN_DONE.
- 2026-10-22 02:44: all fn1 steps scored. Pick = **s200** (written to `fn55/FN1_BEST`).
  - Rule, fixed before s200's synthetic score landed: highest real-144 vote among the steps whose synthetic vote stays within 0.02 of e59's (≥ 0.891). Bench B was not used.

  | Step | Synthetic | Real-144 | Held-out |
  |---|---|---|---|
  | e59 | 0.911 | 0.523 | 0.525 |
  | s40 | 0.914 | 0.576 | 0.588 |
  | s80 | 0.914 | 0.598 | 0.612 |
  | s120 | 0.896 | 0.619 | 0.603 |
  | s160 | 0.901 | 0.609 | 0.615 |
  | **s200** | 0.898 | **0.633** | 0.612 |
  | 27B ent_t10_s120 | 0.922 | 0.639 | 0.640 |

  - s200 − e59: −0.013 [−0.021, −0.005] / +0.110 [+0.076, +0.147] / +0.087 [+0.064, +0.109] (synthetic / real-144 / held-out).
  - s200 − 27B ent_t10_s120: −0.024 [−0.032, −0.017] / −0.007 [−0.033, +0.021] / −0.028 [−0.048, −0.009].
  - **Flash-Next GRPO ties the 27B's GRPO on dev and trails it on held-out by 0.028.** It was still rising at s200, but the next stage is the EI round, so it does not run more steps (the 27B used 120).
  - FNRP training at step 118/300 (46 s/step), done ~05:05. EI (GPUs 0-3) and the S2 chains (GPUs 4-7) then start on their own.
- 2026-10-22 14:51: FNRP finished 05:18. S2 chains launched 05:46 (serv-19 + ccc0442 job 11721794); by 14:50, 38 of 165 blocks were done (bench B 33 / 36).
  - **The EI SFT crashed at 05:21 on start-up**: `save_only_model: true` is rejected with FSDP `SHARDED_STATE_DICT`. My config error; e26 used false.
  - GPUs 0-3 sat idle 05:21-14:51. Fixed `configs/fn-rft2.yaml`, and `fn_ei.sh` relaunched 14:51 (failed log kept as `train_fn_rft2.fail1.log`).
- 2026-10-22 15:10: EI SFT running at 6.7 s/step (loss 5.9 → 4.7 by step 30), so it ends ~17:00; the RL and evals follow on their own.
  - Bench-B S2 partial (276 / 280 parts finished in all 3 chains, `summary_fn.py --partial`):

    | | FN S2 | 27B S2 |
    |---|---|---|
    | chain-1 start (vote) | 0.525 | 0.512 |
    | multi-start | **0.681** | 0.663 |

    - FN multi-start − 27B multi-start: +0.018 [−0.004, +0.040] (+82 / −60 parts).
    - FN repair lift: +0.155 [+0.130, +0.180]. FN oracle over the chain finals: 0.716.
    - **On held-out, Flash-Next's S2 ties the 27B's (+0.018, CI includes 0). It is the first stage where Flash-Next does not trail.** Synthetic S2 still to run.
- 2026-10-22 17:10: EI SFT done 16:46 (955 steps, 6.7 s/step). RL `fnei` running.
  - First three steps: reward 0.41 / 0.53 / 0.57, exec 0.91-0.96, entropy 0.22-0.28; 3-5 min/step, so it ends ~21:00.
  - Evals of s20 / s40 / s60 follow automatically. Each is scored on ccc0442 as soon as its 3 benches are generated.
  - **fnei pick rule, fixed before any score**: the same rule as for fn1. Take the highest real-144 vote among s20 / s40 / s60 whose synthetic vote is ≥ 0.891 (e59 − 0.02); bench B is not used. Fall back to fn1 s200 if none qualifies. The pick goes into `fn55/FNEI_BEST` (it starts S1) and `results/flashnext/grpo/FNEI_BEST` (the paper table).
  - Target: the 27B's rft2_rl_s60, 0.932 / 0.673 / 0.665. fn1 s200 trails it by −0.034 / −0.040 / −0.053.
- 2026-10-26: **S2 done (all 165 blocks); EI scored; pipeline paused for the user's pivot to American open-weight VLMs.**
  - S2 multi-start, FN vs 27B: held-out 0.682 vs 0.664, +0.018 [−0.003, +0.039]; synthetic 0.952 vs 0.949, +0.003 [−0.003, +0.009]. A tie on both.
  - EI (fnei) vote, synthetic / real-144 / held-out: s20 0.926 / 0.659 / 0.657; s40 0.929 / 0.661 / 0.655; s60 0.927 / 0.659 / 0.663.
  - Pick by the pre-registered rule = **s40** (written to `results/flashnext/grpo/FNEI_BEST` only).
  - s40 − 27B rft2_rl_s60: −0.003 [−0.010, +0.003] / −0.012 [−0.035, +0.010] / −0.010 [−0.027, +0.008]. **Tie with one EI round vs the 27B's two.**
  - serv-19: STOP_s19 set and FNRP servers stopped (GPUs free). The S1 stage was NOT started: `fn55/FNEI_BEST` was not written, so `fn_s1.sh`, `fn_finish.sh` and the DeepSeek chain stay idle, waiting.

**2026-10-27 21:0x** Cancelled by the user (American-VLM pivot): fn_s1.sh / fn_finish.sh waiters stopped on serv-19; the Flash-Next GRPO + repair row stays unfilled.
