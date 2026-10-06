# GRPO Campaign Handoff (2026-10-06)

Status of the reinforcement-learning campaign on drawing→build123d. Read this
first if you are picking up the RL work. Companion: `PAPER_STATUS.md` (project
status), `train_v14/RECIPE.md` (lab notebook through 2026-10-01).

## 1. What is running right now

17 GRPO arms training from e55 (`e55-rft-real-u5-gt-dw423`), all with the
validated trainer `train_v14/geom/grpo_round.py` (commit `66bb56d`):

**serv-20** (via `train_v14/serv19/grpo_r1_launch.sh`, nohup'd, logs in
`/srv/scratch/bimrose2/logs/`, outputs in `/srv/scratch/bimrose2/runs/`):

| arm | GPU | config | status @ 08:00 |
|---|---|---|---|
| `kl002` | 4 | Dr.GRPO loss, mean-adv, KL 0.02 | step 24/60 |
| `kl0` | 5 | same, KL off | step 24/60 |
| `tok` | 6 | token-level (DAPO) loss, KL 0.02 | step 23/60 |
| `frontier` | 7 | kl002 config, 1,492 frontier keys only | step 24/72 |
| `frontkl0` | 0 | **DEAD — relaunch failed (shell quoting: `\$COMMON` did not expand; argparse error). Relaunch command below.** | — |

**Cluster** (sbatch, 12 arms; logs in `/projects/.../logs/grpo_r1{c,d,e}_*.log`,
outputs in `/projects/.../runs/grpo_{c,d,e}_*/`):

| job | node | arms |
|---|---|---|
| 11175306 `grpo-r1c` | ccc0451 | `std` (std-adv), `g16` (G=16), `lr5e6`, `real4` (real corpus 4, 3,007 parts) |
| 11175307 `grpo-r1d` | ccc0474 | `c1` (real corpus 1), `indist` (in-dist pool 1,067), `execp` (exec penalty 0.1), `t09` (T=0.9) |
| 11175308 `grpo-r1e` | ccc0475 | `c2` (real corpus 2), `std0` (std+noKL), `lr2e5`, `g16t09` |

Common: LoRA r64 α128 on all LM linears (auto-targets, vision tower excluded),
G=8 @ T=0.7 (except g16/g16t09), n-parts 16/step, lr 1e-5 (except lr arms),
save-every 10 (serv-20) / 24 (cluster). Arms finish in ~19h (60 steps) /
~13h (72 steps) from their ~01:40 relaunch. Adapter checkpoints:
`runs/<arm>/adapter_step*/` — mergeable with
`train_v14/geom/merge_grpo_lora.py` for vLLM eval.

Cluster scoring jobs: `score-real4` (round-0 on real corpus 4) running;
`score-famheld` (e55 think-mode baseline on the 200-part family held bench)
done — outputs `results/h6b/bo8_famheld_e55think.json`.

## 2. Early curves (steps 0–24, honest post-fix numbers)

Baseline (e55 mean candidate reward, round-0 vLLM diagnostic): family 0.274,
in-dist ~0.65, corpus1 ~0.43, corpus2 ~0.44, corpus4 ~0.42.

- **`indist` (in-distribution): 0.645 → 0.80–0.88 — clear +0.15–0.2 rise.** The
  strongest arm. If it holds held-out, this is the "internalize the vote"
  effect (single-shot 0.79 → served 0.91 was the target).
- **`c2` (real corpus 2): 0.438 → 0.63 peak, ~0.50 at 27 — +0.06–0.19 rise.**
- **`real4`: 0.42 → 0.58 peak, ~0.47 — rising.**
- `c1`, `std`, `std0`, `lr2e5`, `execp`, `t09`, `g16*`, `kl002/kl0/tok`
  (family bench): flat-to-slightly-up at baseline, within part-sampling noise
  so far. Family bench is the hardest place to move (frontier is real but
  dense near-misses are rarer).
- Completion lengths stable everywhere (±10%) — **no length-bias collapse**.
- KL in anchored arms ~1e-4 — tiny, the anchor is not binding.

## 3. Bugs found and fixed this session (do not reintroduce)

1. **Rollout-to-part indexing (the big one)**: generations are draw-major
   (`outs[g * n_parts + pi]`), collection was part-major (`outs[pi * G + g]`)
   — every group mixed completions from G different parts scored against the
   wrong GT. Symptom: rewards ~0.2× baseline with normal exec rates. Fixed in
   `66bb56d`; validated by 1-step debug run (0.330 vs 0.063). All arms were
   restarted from e55 after the fix; any adapter from before 01:40 Oct 6 is
   invalid and was deleted.
2. Left padding breaks `VLMCollator`'s prompt-prefix masking (common prefix
   0 → prompt supervised). Fixed: `completion_logps` sets
   `processor.tokenizer.padding_side = "right"` for the collate; generation
   sets it back to `"left"`.
3. `skip_special_tokens=True` strips think markers — split think/code on the
   LAST ```python fence instead (`rfind`).
4. LoRA target regex didn't match the hybrid stack — use the auto-target
   leaf-name collector (includes Gated-DeltaNet `in_proj_*`/`out_proj`).
5. OOM in training forward — gradient checkpointing (disabled during
   generation) + per-row logprob gather over completion tokens only.
6. `pkill` over ssh self-kills if the pattern matches the launching shell
   command line — use `[e]`-style patterns and separate ssh calls.

Debug methodology that caught #1 (keep using it): join every arm's rollout
rewards against the e55 baseline **on the same parts**
(`results/h6c/bo8_famtrain_e55.json` + arm `rollouts.jsonl`), then controlled
ablation (raw vs peft, greedy vs sampled) with text dumps
(`--dump-texts`).

## 4. Round-0 diagnostic (valid, vLLM path)

e55 G=8 on all 1,655 family-train parts (`results/h6c/bo8_famtrain_e55.json`):
best-of-8 0.482, first-exec 0.368, **90% frontier fraction** (1,492 parts with
gradient signal; 518 in the 0.5–0.8 near-miss band; only 19 zero-signal).
Frontier keys: `results/h6c/famtrain_frontier_keys.txt` (shipped to serv-20 at
`fp/h6/famtrain_frontier_keys.txt`). Analysis tool: `train_v14/geom/grpo_frontier.py`.

## 5. What to do next

1. **Relaunch `frontkl0`** (GPU 0, serv-20) — the quoting bug killed it:
   ```
   ssh wpk-serv-20.mechse.illinois.edu
   cd /srv/scratch/bimrose2 && CUDA_VISIBLE_DEVICES=0 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
     setsid nohup .venv/bin/python train_v14/geom/grpo_round.py \
     --run e55-rft-real-u5-gt-dw423 --model-base /srv/scratch/bimrose2/models/Qwen3.8-27B \
     --ckpt /srv/scratch/bimrose2/runs/e55-rft-real-u5-gt-dw423/final \
     --bench fp/h6/train_bench --keys fp/h6/famtrain_frontier_keys.txt \
     --steps 72 --lr 1e-5 --gen-batch 16 --train-batch 4 --score-workers 20 \
     --save-every 24 --n-parts 16 --g 8 --kl-beta 0 --out runs/grpo_f_frontkl0 \
     > logs/grpo_f_frontkl0.log 2>&1 < /dev/null &
   ```
2. **Eval the `indist`, `c2`, `real4` arms as soon as they finish** (or use
   `adapter_step20+`): merge with `merge_grpo_lora.py` (serv-20 GPU 2/3 free),
   restart the vLLM server (`train_v14/serv19/run_vllm_e55_serv20.sh`) pointing
   at the merged dir, generate with `gen_openai_bo.py` on the held-out benches,
   score via `sbatch/score_generic.sbatch`. Compare against:
   - family held bench 200: e55 think baseline `results/h6b/bo8_famheld_e55think.json`
   - real bench 143: existing famNT/real baselines in `results/h6b/`, `results/repair/`
   - in-dist pool: `bo8_full_e55*` results
   The win condition is a held-out first-exec/vote gain, not training reward.
3. **Round 2**: continue from the best arm's adapter (`--adapter` flag resumes),
   prefer frontier keys + the benches that moved (c2/real4/indist); consider
   G=16 there. If family arms stay flat through step 60, the read is that the
   family frontier needs the repairer-distillation route instead.
4. **The next big lever if generator RL works**: GRPO on the repairer (rp3) —
   reward = IoU on real corpora with GT; distills the +0.16 search-loop gain
   into the policy. Infrastructure (reward server, benches) is identical.
5. DeepSeek RL: assessed as poor first target (50× compute per group, merge-
   restart friction); revisit only after Qwen results (RECIPE has the numbers).

## 6. Monitoring (this session's pattern)

- serv-20 arms: `ssh wpk-serv-20 "tail /srv/scratch/bimrose2/logs/grpo_*.log"`
  (step lines are JSON; watch `mean_reward` vs the baselines in §2, and
  `mean_completion_chars` for length collapse)
- cluster arms: `logs/grpo_r1{c,d,e}_*.log` on /projects
- scoring: `squeue -u bimrose2`
- a step is ~19 min (gen dominates; think-mode 2400-token budget)

## 7. Map of new files (all committed)

- `train_v14/geom/grpo_round.py` — the trainer (validated; see §3 for the traps)
- `train_v14/geom/grpo_frontier.py` — round-0 → frontier keys/stats
- `train_v14/geom/merge_grpo_lora.py` — adapter → servable HF dir
- `train_v14/serv19/grpo_r1_launch.sh` — serv-20 3-arm launcher
- `train_v14/sbatch/grpo_r1_cluster.sbatch`, `grpo_r1d.sbatch`, `grpo_r1e.sbatch`
- `results/h6c/bo8_famtrain_e55.json` + `famtrain_frontier_*` — round-0 artifacts

## 8. Honest assessment

The campaign has: working on-policy GRPO at 17-arm scale, a validated reward
path (after two hard bugs), a rich frontier, and the first genuine positive
signals — in-distribution +0.15–0.2 training-reward rise and real-corpus rises
(c2, real4) — with no length collapse. Nothing is claimed until held-out
evals confirm (§5.2). Family-bench arms are flat so far, consistent with the
shape-vocabulary wall: RL internalizes what the policy can already almost do;
it does not create new capability. The paper-relevant outcomes either way:
(a) generator RL lifts real-bench first-draw toward the vote/oracle ceiling, or
(b) it does not, and the repairer-distillation (§5.4) is the remaining RL play.
