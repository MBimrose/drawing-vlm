# GRPO Campaign Handoff (2026-10-06)

## 0. UPDATE 2026-10-06 midday — read this first (supersedes §1–§2 numbers)

**Corrections to the morning state.** The raw `mean_reward` curves in §2 were part-sampling
noise. Joined against e55's own best-of-8 on the SAME parts (per-step paired delta), the 1e-5
slow arms were ~flat: c2 +0.000, real4 +0.015 *constant from step 0* (= HF-vs-vLLM offset, not
learning), family arms +0.00–0.02, execp/t09/g16t09 negative. Only **lr2e5** (+0.03 → +0.06 by
steps 20–23, exec 0.73 → 0.82) and **indist** (+0.03–0.04 late) moved. Also: the `indist` arm
trains on `fullpool_dw423`, which IS the in-distribution eval pool — held-out subset =
`results/h6c/indist_held_keys_s48.txt` (259 parts never sampled through step 48).

**Held-out evals** (vLLM think-mode K=8, paired vs a same-path e55 control, bootstrap 95% CI;
`results/grpo_eval/`, `geom/grpo_eval_summary.py`). Run-to-run e55 noise: ±0.014 mean-cand.

| model | real 144 mean-cand | real draw-0 | famheld 200 mean | famheld draw-0 | indh 259 mean |
|---|---|---|---|---|---|
| e55 control | 0.396 | 0.390 | 0.251 | 0.240 | 0.780 |
| indist step 24 | +0.003 [-0.013,+0.019] | 0.390 | +0.020 [+0.007,+0.035] | 0.277 | +0.026 [+0.011,+0.042] |
| **lr2e5 step 24** | **+0.023 [+0.007,+0.041]** | 0.409 | **+0.051 [+0.039,+0.065]** | 0.325 | +0.035 [+0.018,+0.053] |

First held-out RL win: 24 slow steps at lr 2e-5 on family parts lift held-out real-part quality
(exec 0.788 → 0.814); best-of-8 unchanged (sharpening, as expected — PKPO arm targets it).
c2s24 / real4s20 / kl002s20 evals are scoring.

**Trainer fixes/features (all flags; defaults reproduce the old behaviour):**
- `--rollout-url` — vLLM rollouts with per-step LoRA hot-load (`load_lora_adapter`); launcher
  `serv19/grpo_vllm_arm.sh` co-locates vLLM (GMU 0.33) + trainer on one B300; cluster version
  `sbatch/grpo_fast_cluster.sbatch` (vLLM GPU + trainer GPU per arm, 4 arms/node).
  Step ≈ 4–6 min (gen 40–60 s) vs ~19 min. vLLM supports LoRA on all Qwen3.5 GDN modules.
- `--scale-logits` + `--top-p 1.0` — fixes an off-policy bias: rollouts were sampled at
  T=0.7/top_p 0.95 but logprobs came from untempered logits.
- `--minibatches 4` (PPO clip-higher 0.2/0.28, old logps from a no-grad pass), `--adv batchstd`,
  `--pkpo-k/--pkpo-anneal` (max@k reward transform, verified vs brute force),
  `--score-timeouts` (exec 60 s / IoU 90 s subprocesses = eval rule; in-thread IoU fallback
  took up to 486 s), multi-bench `--bench a,b --keys ka,kb`.
- `--repair-inputs/--repair-png-dirs` — **repairer RL**: prompt = [target sheet, start sheet] +
  REPAIR_PROMPT(code), no-think, reward = IoU of the repair (start IoU cancels in the group
  baseline); 2,792 real start programs (corpora 4/2/1).
- Trap fixed: HF gradient checkpointing is a no-op in eval mode; the vLLM path never called
  `model.train()` → 2× activation memory / OOM. `completion_logps` now calls `model.train()`.
- Hard-mined key lists (e55 mean < 0.75, best > 0.1, var > 0): `results/h6c/{real4,c2,fam}_hard_keys.txt`.

**Running (fast path, 300 steps, KL 0, batch-std adv, 4 minibatches, T 0.8 scaled, top_p 1):**

| arm | where | pool | variant |
|---|---|---|---|
| mix_lr2e5 | serv-20 GPU 0 | real4+c2+family hard | lr 2e-5 |
| mix_lr4e5 | serv-20 GPU 6 | same | lr 4e-5 |
| mix_pkpo | serv-20 GPU 7 | same | lr 2e-5, PKPO k=4 → 1 over 200 steps |
| real_lr2e5 | serv-20 GPU 5 | real4+c2 hard | lr 2e-5 |
| rep_rp3 | serv-20 GPU 1 | repairer (rp3 + LoRA) | lr 2e-5 (step ≈ 11 min) |
| rep_lr4e5 | serv-20 GPU 2 | repairer | lr 4e-5 |
| mix_t10 / mix_b32 / real_pkpo / mix_mb8 | cluster ccc0451 (job grpo-fast) | | T=1.0 / 32 parts lr 3e-5 / real+PKPO / 8 minibatches |

serv-20 GPU 3 = eval server (`serv19/grpo_eval.sh` → `serv19/grpo_eval_score.sh` →
`geom/grpo_eval_summary.py`). Slow cluster jobs grpo-r1d/e still run (lr2e5 → step 60).
Stopped (user-approved): serv-20 kl0/tok/frontier/frontkl0, cluster grpo-r1c.

**Next:** eval fast-arm adapters at step 20/40/... on the held-out benches; repairer adapters
through the in-house loop protocol (`serv19/rp1_loop.sh` with R=<merged>, vs rp3 K=8x3 0.631);
then the full system (generator + repairer multi-start) vs 0.695.

**Fast-path step-20 held-out (2026-10-06 15:00)** — real bench 144 (mean-cand Δ vs e55ctl, draw-0, exec):

| arm @ step 20 | real Δmean | real draw-0 | real exec | famheld Δmean |
|---|---|---|---|---|
| **mix_lr4e5** | **+0.045 [+0.022,+0.069]** | **0.467** (e55 0.390) | 0.868 (0.788) | +0.085 |
| mix_lr2e5 | +0.023 [+0.008,+0.040] | 0.426 | 0.825 | +0.055 |
| real_lr2e5 | +0.017 [-0.002,+0.034] | 0.388 | 0.833 | +0.046 |
| mix_pkpo | +0.005 (n.s.) | 0.383 | 0.804 | +0.038 |

Higher LR wins at this budget; family parts in the pool help real-part transfer; best-of-8 still ~flat.
Queued (afterany on grpo-r1d/e, ~17:40): ccc0474 = lr 6e-5 / 8e-5 / family-only 4e-5 / 4e-5+PKPO;
ccc0475 = 4e-5 with T 1.0 / G16x8 parts / 8 minibatches / 32 parts (`sbatch/arms/fast_ccc047{4,5}.txt`).
Auto-eval covers all fast arms at steps 20/60/120/200/300 (real + famheld; scoring async).
serv-20 load incident: unthreaded-capped scoring subprocesses + 24-worker repair eval -> load ~900;
fixed by `taskset` 32-core slices per trainer, `_ENV1` single-thread env in score_partials, OMP caps
in launchers, repair eval at 8 workers with absolute renderer paths.


**System-level check (2026-10-06 16:00) — RL internalizes the vote, does not (yet) raise it.** Real bench,
same vLLM path, paired, consistency_rerank on the K=8 draws (`results/grpo_eval/real_*_consistency.json`):
first-exec e55 0.466 → mix_lr4e5_s20 0.499 (+0.033 [+0.006,+0.062]); **vote 0.516 → 0.527 (+0.010
[-0.015,+0.038], n.s.)**; oracle 0.593 → 0.597 (n.s.). Single draws approach the vote, the vote/ceiling do not
move at step 20 → the deployed system (vote → repair) gains little from this generator yet. Levers that can
move the ceiling: max@k objectives (PKPO k=8 arm `mix_lr4e5_pk8` queued), exploration (T=1.0 arms), and
the repairer RL. Re-check vote at step 60+ (consistency jobs need --mem 300G on ccc0442).


**18:30 update.** Step-20 real-bench mean-cand Δ: mix_mb8 +0.055, mix_lr4e5 +0.045, mix_t10 +0.034,
real_pkpo +0.026 (best oracle 0.616), mix_lr2e5 +0.023, real_lr2e5 +0.017, mix_pkpo +0.005.
mix_lr4e5 step 60 famheld **+0.156** (exec 0.976). Completion length is shrinking in some arms
(real_lr2e5 ~1.85k → 1.3k chars) — watch for length collapse.
**Repairer RL** rep_rp3 step 20 through the rp3 loop protocol: r3 0.641 vs rp3 0.631, paired
+0.010 [-0.013,+0.034] (n.s.), fewer parts hurt (8 vs 11). Step-60 loop eval queued.
serv-20 GPU 5: real_lr2e5 (weakest) stopped at step 80 → `mix_pk8_t10` (max@8 PKPO + T 1.0, lr 4e-5) via
`serv19/grpo_trainer_on.sh` (trainer only, reuses the GPU's vLLM). Cluster ccc0474/0475 waves started 17:35.
Vote automation: `sbatch/grpo_cons_loop.sbatch` (ccc0442) computes consistency for every real eval;
`geom/grpo_eval_summary.py` prints vote + paired vote/oracle Δ. DeepSeek GRPO (low-resource,
serv-19 GPUs 4-7, user-approved) being built by a background agent — see its section when added.





**01:20 Oct 7 — vote moves, guided raises the ceiling.** Real bench paired vs e55: mix_lr4e5_s60 **vote 0.570
(+0.053 [+0.026,+0.081])**, oracle 0.635; mix_lr2e5_s60 vote +0.043; **guide_lr4e5_s60 best-of-8 0.681** (e55
0.593; unguided same step 0.635), mean +0.137; mix_lr4e5_s120 draw-0 0.582, mean +0.169, oracle 0.662,
exec 0.972. → Doubling down on guided GRPO: **bank v2 via GT-selected repair search** (`geom/gt_search.py`:
start = best GT-scored e55 draw, rp3 K=8 repairs/round, adopt by true IoU, render only the adopted program,
≤ 4 rounds) over the 1,945 hard real parts without a bank entry (`results/h6c/gts_keys_c{4,2}.txt`), rp3 on
serv-20 GPU 0 :8302 (driver `serv-20:tmp/gts_driver.sh`, log `logs/gts_driver.log`) → emit targets →
rationalize → `fp/guide/bank2_c{2,4}.json`. Eval daemons: GPU 3 only now (REP_ARMS = rep_rp3).










**04:50 Oct 10 — Bench B + baselines** (section "Bench B + baselines (Oct 10)"): new frozen 280-part held-out real bench (Fusion 360 Gallery + ABC, leak check clean); **rft2_rl_s60 replicates as best** (vote 0.665, best-of-8 0.732; vs rft1_rl2_s120 +0.014 [+0.003,+0.025] vote / +0.023 best-of-8); vanilla DeepSeek T0 vote 0.375 (144) / 0.393 (B), base Qwen3.8-27B 0.064 / 0.082 (exec 5%: no RL-from-scratch signal).

**12:10 Oct 9 — Expert-iteration round 2: search + tier + SFT done, RL running** (full section at the end, "Expert-iteration
round 2 (Oct 9)"). K=16 of rft1_rl2 s120 on 8,121 training parts + GT-selected rp3 search (3,648 parts) + DeepSeek teacher
(498) → tier 2 = 5,502 rows. 3,643 parts gained a ≥0.75 program with none in the round-1 tier (1,792 vs every earlier
sample; CADBench 617 / 388). SFT `rft2`: real best-of-8 0.724 (campaign high; +0.025 vs rft1, +0.010 n.s. vs the
search policy), vote 0.649 (n.s. vs 0.655), mean-cand −0.032. RL `rft2_rl` (serv-20 GPU 2) evaluated automatically.

**00:45 Oct 9 — serv-20 only from here (user: "keep running on 20").** ccc0474/0475 already free; ccc0451 leaves at 05:30
(migrate job 11217878 now targets serv-20 GPU 2 :8432 gfrom_cap and GPU 1 :8431 ent_mb8, stop arm "-"). Stale vLLM
servers of finished ent_t10/ent_s1 (resumed arms: grpo_resume.sh SIGKILLs the launcher, so nobody kills their vLLM
at the end) stopped → GPUs 5/6 free. Vote loop job had TIMEOUT 18:16 Oct 8 → resubmitted 11236971. s200 evals:
ent_pool2 mean-cand 0.612 / d0 0.611, ent_dense 0.604 / d0 0.618 (both still rising past s120, unlike ent_t10);
rft1_rl2 s60 oracle 0.708. New serv-20 arms (all pool2 = old pool + realpool2_hard_4500, floor 0.1): **ent_pd** (GPU 0,
+ dense 0.3), **ent_p2lr3** (GPU 5, lr 3e-5), **ent_pdcap** (GPU 6, + dense 0.3 + ceiling 0.35).

**14:30 Oct 8 — H200 nodes handed back (user: free ccc0451/0474/0475 from the morning of Oct 9).** Plan in place:
ccc0475 job 11182777 ends 17:35 today → migrate job 11217877 (afterany) pushes rft1_rl2's adapters to serv-20 and resumes
it there on GPU 7 :8433, stopping ent_hi (entropy 0.9 at s41, weak s20). rft1-resub 11215764 cancelled. ccc0451 job
11213000 / ccc0474 job 11205009 time limits cut to end 05:59 Oct 9; migrate job 11217878 (`--begin 05:30 Oct 9`) cancels
them (+ overlap jobs 11217696/11212829/11212830), final-rsyncs gfrom_cap + ent_mb8, cancels their sync jobs, resumes
gfrom_cap on serv-20 GPU 5 :8413 (stops ent_t10, s238, past its s120 peak) and ent_mb8 on GPU 6 :8411 (stops ent_s1).
Not migrated (past peak / weak): pkpo4_t10, mix_t10_g16, mix_t10_s1, pool2_mix, pool2_all. Scripts:
`serv19/grpo_migrate.sh`, `sbatch/grpo_migrate.sbatch`, `sbatch/arms/migr_*.txt`. serv-20's grpo_round.py updated to the
cluster copy (adds --ent-max; backup `.bak_1008`). Full pipeline repair runs on ccc0442 L40S (unaffected).
Also: gfrom_t10 collapsed at s211 (entropy explosion from s184) and gt10_np32 at s107; gfrom_cap = gfrom_t10 resumed
from s180 with an entropy ceiling 0.3 (ccc0451 GPU 3). ent_t10 s200 declined vs s120 (mean-cand 0.588 vs 0.600, oracle
0.677 vs 0.699) → the floor softens but does not stop the late decline.

**10:15 Oct 8 — ent_t10 s120 is the new best checkpoint; guided and dense-only collapse.** Real bench (144):
**ent_t10_s120 vote 0.639 / d0 0.615 / mean-cand 0.600 / oracle 0.699 / exec 0.984** (Δmean +0.205 [+0.173,+0.234] vs
e55ctl; mix_t10_s120 was 0.629 / 0.576 / 0.583 / 0.688). gfrom_t10_s200 oracle 0.705 / d0 0.604 (vote pending).
rft1 (SFT consolidation) s20: vote 0.624 / oracle 0.699; rft1_rl relaunched at lr 1e-5 (lr 2e-5 collapsed in 12 steps).
s60 Δmean: ent_c03 +0.153, ent_pool2 +0.152, ent_dense +0.147, ent_s1 +0.131 (seed replicate; ent_t10 was +0.141).
mix_t10_s1 s120 (seed replicate of mix_t10) vote 0.584 / oracle 0.665 → part of mix_t10's s120 edge is seed luck.
**Collapsed (guard: 3 rollbacks used → stop):** ent_guide s42 (guided + entropy floor: exec 0.37), dense_t10 s118
(dense reward without the floor: exec 0.41). ent_dense (dense + floor) is healthy at s80.
Note: ent_t10's entropy target auto-set to 0.13 but entropy sits ~0.25 from s20 on → the floor rarely binds. New serv-20
arms: **ent_hi** (GPU 7, target 0.3 so it binds) and **ent_lr3e5** (GPU 4, floor + lr 3e-5). v5 verifier eval failed
(started 26 s after its host job, venv still copying: libtiff ImportError) → resubmitted job 11214957. ent_mb8
adapters now mirrored (sync job 11214964).

**04:10 Oct 8 — selection closes ~40% of the vote→oracle gap.** Selection agent: argmax(v3b-EV verifier + render-compare
v3) beats the vote by +0.026..+0.031 on three generators (CIs > 0); the agreement gate now HURTS (RL candidates agree
more but agreement ≠ correct). Test-time scaling for mix_t10 s120: K=16 verifier+v3 **0.672** (vote 0.629, oracle
0.711), K=32 0.677 → **deployable label-free number without repair: 0.672 vs e55 vote 0.516**. v5 verifier retrain
trained (val loss flat); eval queued on ccc0451 GPU 7 (`results/selection/vscore_v5.sh`, job dependency).
ccc0451 job 11181389 ENDED 03:33 (last original arm finished) → pkpo4_t10 / gfrom_t10 overlap arms died →
fresh job 11213000: pkpo4_t10 (resumed s80), gfrom_t10 (resumed s170), ent_mb8 (new). Bank-v3 candidates scored
(`results/guide/v3/bo16_c{2,4}_t10.json`). RFT consolidation cycle (#4) handed to an agent (ccc0475 free pair).

**03:50 Oct 8 — entropy floor leads; DeepSeek wound down; pool v2.** Step-60 real mean-cand Δ: **ent_t10 +0.141**
(oracle 0.665) > dense_t10 +0.106, mix_t10_g16 +0.105 (vote 0.570), mix_t10_s1 +0.104 (vote 0.572), pkpo4_t10 +0.066.
DeepSeek: dsgrpo2 u12 +0.024 / u14 +0.004 (flat); guided dsgrpo3 degenerated (u8 −0.073, exec 106/144) and
self-stopped → DeepSeek wound down (dsgrpo2 finishes on serv-19; self-train rerun follows there). gt10 also ended
by its guard. Real-part pool v2: 12,969 hard DeepCAD parts (`rft_realpool_v2`; CADBench has no unused parts left).
New arms: serv-20 `ent_dense` (GPU 0), `ent_c03` (1), `ent_pool2` (2), `ent_s1` (6, seed replicate),
`ent_guide` (7, guided + entropy floor: tests whether guided collapse is entropy collapse); ccc0474 `pool2_mix`
(4,500-part subset) and `pool2_all` (all 12,969). Bank-v3 candidates scoring (v3score-c2/c4) for the RFT cycle.

**23:40 Oct 7 — guided GRPO collapses in every long run.** guide_mb8b (exec 0.01, guard exhausted), gt10_kl0 (0.18),
gt10_mb8 (0.16) stopped by the guard; gt10 and gt10_np32 rolled back. Unguided mix_b32 (lr 3e-5, 32 parts) also
collapsing at step ~240 (exec 0.37). Stable: unguided lr 2e-5 arms (mix_t10_g16, mix_t10_s1, gfrom_t10, ent_t10,
dense_t10, pkpo4_t10). Conclusion: guided checkpoints are only usable early (s20-s60: vote 0.589-0.628, best
oracle 0.698); the off-policy bank injection destabilizes training over time → move the bank's value into the
supervised side instead (RFT cycle on bank + RL best-of-16, #4), then unguided RL. Bank-v3 sampling finished
(c4 33,590 + c2 14,526 candidates with code, `results/guide/v3/bo16_c{2,4}_t10`), scoring jobs queued.

**15:00 Oct 7 — top tier converging; soup queued.** guide_mb8b s60 (guided, 8 minibatches): **vote 0.628 (+0.111),
best-of-8 0.698 (best ceiling yet)**, draw-0 0.561; mix_t10 s120 vote 0.629 / s200 0.618 (vote plateau, draw-0
0.598); mix_b32 s120 vote 0.615 / draw-0 0.590; gt10_mb8 s20 mean +0.102 (best step-20). The ccc0474 job ended
at 14:07 when its last ORIGINAL trainer was killed (EXIT trap took the vLLM servers and the overlap arms with it);
resubmitted as job 11205009 with guide_mb8b (resumed s60), gt10_kl0 (resumed s20), mix_t10_g16 (G16×8, lr 2e-5,
T 1.0), mix_t10_s1 (seed replicate of the best recipe). **Model soup** `geom/lora_soup.py`: exact weight-space
average of LoRAs by rank concatenation (rank 192; verified ΔW rel. err 2.6e-7): soup1 = mix_t10 s120 +
guide_mb8b s60 + mix_b32 s120 at `serv-20:runs/grpo_v_soup1/adapter_step20`, first in the eval queue.

**13:20 Oct 7 — DeepSeek all-in triggered; repairer RL closed.** dsgrpo2 **u6 0.327 vs u0 0.291 (+0.037
[+0.002,+0.072])** clears the user's bar → agent extending dsgrpo2 to 16 rounds (serv-19 4-7), building guided
DeepSeek GRPO `dsgrpo3` on serv-20 GPUs 0,1,2,7 (bank v2 rationalized in DeepSeek's voice, from dsgrpo2's best
adapter), and re-running the indexer-bug-invalidated self-train SFT. Repairer RL through the rp3 loop protocol:
s20 +0.010, s60 +0.013 (n.s.), s120 −0.002 / **−0.033 (rep_lr4e5, significant)** → stopped both rep arms (keep
s60 adapters); mix_vote stopped (vote 0.583 at s120, superseded). Qwen lr-2e-5 arms still improving: mix_t10
s200 draw-0 0.598 / mean +0.202; mix_cont s200 vote 0.616; real_pkpo s200 vote 0.606; guide2b s60 vote 0.590.

**11:00 Oct 7 — new best: T=1.0 at lr 2e-5.** `mix_t10` s120 (cluster wave 1: lr 2e-5, T 1.0, KL 0): real **vote
0.629 (+0.113 [+0.080,+0.148]), oracle 0.688, draw-0 0.576**, mean +0.187 — best on every metric. Next:
mix_mb8 s120 vote 0.600, mix_b32 s60 0.593, guide_mb8b s20 0.589 (guided, stabilized), mix_vote s120 0.583,
real_pkpo s120 0.583 (s200 oracle 0.675). Instability is LR-driven: lr ≥ 4e-5 eventually decays or collapses
(mix_lr4e5_g16 → exec 0 / 3.7k-char degenerate outputs; mix_lr4e5_mb8 exec 0.61; mix_lr8e5 back to e55 vote;
guide_cont KL blew up to 2.6e6 after 2 guard rollbacks). Guard works (guide2b rolled back once, recovered).
Bank v2 done: GT search improved c4 602 + c2 276 parts → banks c4 1,415 / c2 670 / c1 297 = **2,382 parts**
(`fp/guide/bankv2_c{4,2}.json`, cluster `results/guide/`). New arms = everything that works combined
(guided bank v2 + T 1.0 + lr 2e-5 + guard 0.6): `gt10` (serv-20 GPU 6, KL 0.01), `gt10_mb8` / `gt10_np32`
(ccc0475 GPUs 3 / 5), `gt10_kl0` (ccc0474 GPU 3). Stopped: guide_cont, mix_lr4e5_g16, mix_lr4e5_mb8, mix_lr8e5.
DeepSeek u4 0.301 (+0.011, n.s.; fell from u2) → not all-in; finishes 8 rounds on serv-19 4-7.

**05:40 Oct 7 — COLLAPSE + stabilized relaunch.** guide_lr4e5 collapsed to no-code at step ~85-90 (rollout exec
→ 0.0, ~700 chars; s120 eval all zeros). mix_lr4e5 over-optimized after ~160 (s200: vote 0.517 = e55, oracle
0.590, exec 0.976). lr 4e-5 / KL 0 is too hot for long runs; guidance accelerates it. Best checkpoints so far:
**guide_lr4e5/adapter_step60 (vote 0.608, oracle 0.681)** and **mix_lr4e5/adapter_step120 (vote 0.606, draw-0
0.582)**. Trainer: `--guard 0.6` (rolling-exec collapse → reload last healthy checkpoint, reset Adam, halve lr,
≤ 3 rollbacks), `--guide-adv-scale`. Stopped: guide_lr4e5, mix_lr4e5, guide2, guide_mb8. Relaunched (KL 0.01,
guard 0.6): `guide2b` (GPU 5, e55, bank v1+v2c2, lr 2e-5), `guide_cont` (GPU 6, from guide s60, lr 1e-5),
`mix_cont` (GPU 4, from mix s120, lr 1e-5), `guide_mb8b` (ccc0474 GPU 7, 8 minibatches, lr 2e-5).
DeepSeek dsgrpo2 u2: 0.316 vs u0 0.291 (+0.026 [-0.010,+0.059]) — below the all-in bar; u4 ~09:30 decides.

**03:40 Oct 7 — guided wins the vote; max@8 arms were degenerate.** guide_lr4e5_s60 **vote 0.608 (+0.091
[+0.061,+0.124])**, oracle 0.681 (+0.088); mix_lr4e5_s120 vote 0.606 (+0.090), draw-0 0.582. PKPO k=8 at G=8 is
a no-op (every draw's weight = group max → zero advantage); mix_lr4e5_pk8 / mix_pk8_t10 stayed at e55 → stopped;
trainer now asserts k < G. GT-search c2: 542 parts, 330 improved ≥ 0.03, mean 0.546 → 0.658; c4 (1,403) running.
New guided arms: `guide2` (serv-20 GPU 5, bank v1 + v2-c2, lr 4e-5; `tmp/launch_guide2.sh`) and `guide_mb8`
(ccc0474 GPU 7 inside job 11182776 via `sbatch/grpo_overlap_arm.sbatch` — an overlapping srun step kept alive by
a 1-CPU job on ccc0442; bank v1, 8 minibatches). Eval priority: guided arms first.

**DeepSeek decision rule (user, 2026-10-07: "if promising, go all in on finetuning deepseek").** dsgrpo2
evals at u2 (~06:00) / u4 (~10:00), paired vs u0 = 0.291 on the 144-part real bench. Promising = Δ ≥ +0.03 with
CI lower bound > 0, or a rising positive trend u2 → u4. All-in plan: scale GRPO loops (serv-20 / cluster nodes
from the weakest Qwen arms), guided DeepSeek GRPO with the GT bank, and re-run the indexer-bug-invalidated
fine-tunes (self-train tier, repairer LoRA) on the fixed trainer.

**End-of-campaign checks (user, 2026-10-07: "run the checks at the end"):** (1) vanilla DeepSeek-V4.1-Flash
best-of-8 on the real bench in the fixed short-reasoning regime (after the HF/vLLM mismatch fix) — the RL-zero
ceiling estimate; (2) off-the-shelf Qwen3.8-27B (no SFT) best-of-8 on the real bench — does an un-fine-tuned
model earn enough reward for RL-from-scratch? Then the full pipeline (generator → vote → repair → v3) vs 0.695
with the best RL generator + repairer, when the user asks for it.

**Step-60 real bench (2026-10-06 21:30) — the ceiling starts moving.** mix_lr4e5_s60: draw-0 0.517 (e55 0.390),
mean-cand +0.118 [+0.094,+0.142], first-exec 0.535 (+0.068), **best-of-8 0.635 (e55 0.593)**, exec 0.960.
mix_lr2e5_s60 +0.098 (oracle 0.631); real_lr2e5_s60 +0.087 (0.622); mix_pkpo_s60 +0.045. Vote at step 20:
mix_mb8 **+0.027 [+0.002,+0.055]** (first significant vote gain), mix_pkpo +0.022, others +0.01. Step-60 votes
pending (grpo_cons_loop). Repairer RL step 20 through the loop: rep_rp3 +0.010, rep_lr4e5 +0.003 (both n.s.).
DeepSeek: loop dsgrpo1 stopped (HF-vs-vLLM logprob mismatch: HF NLL 2.1 vs vLLM 0.3-0.55, top-1 agreement
~50%) — agent diagnosing/fixing the forward, then restarting as dsgrpo2 in the hub effort-low regime.

**Teaching the BEST answer, not the majority (2026-10-06 evening).** Three objective-level arms:
- `mix_vote` (serv-20 GPU 7): `--vote-bonus 1.0` — reward += max(0, IoU − IoU of the group's own vote pick
  (medoid by pairwise IoU)); explicitly rewards beating the consensus.
- PKPO max@8: `mix_lr4e5_pk8` (ccc0474), `mix_pk8_t10` (serv-20 GPU 5, + T 1.0).
- **Guided GRPO** `guide_lr4e5` (serv-20 GPU 4, replaces the obsolete slow kl002 arm): `--guide-bank` —
  a bank of GT-verified best-known programs (the DeepSeek repair-search targets: c4 813 parts 0.810 vs
  e55 best-of-8 0.718; c2 394 parts 0.789 vs 0.651; c1 297) with STaR-style rationalized plans in e55's own
  voice (`geom/build_guide_bank.py`, banks `serv-20:fp/guide/bank_c{4,2,1}.json`, 1,504/1,504 kept). When a
  part's bank program beats every sampled draw by 0.05 it joins the group as an off-policy member with its
  true IoU (LUFFY-style), inside the same PPO clip. Pool = bank parts + family hard. Step 0: 3/16 groups guided.
  Next if it works: grow the bank with GT-selected repair search over all ~4k hard parts (expert iteration).

**Tools added 15:00–15:40:** `serv19/grpo_resume.sh <arm> <N>` (fresh trainer from adapter_stepN with
`--start-step N`, reuses the arm's vLLM server; used to move all serv-20 fast arms onto the
thread-capped code — train phase back from ~400 s to ~215 s/step); `geom/make_vote_picks.py`
(scored bo-K + consistency → vote-pick / top-3-distinct start files for vr_serve; reproduces
e55_vote_picks.json exactly); `geom/grpo_join.py` (paired per-step curve vs e55 on the same parts).
Eval-path traps: a killed eval vLLM can keep serving on :8300 (health check then hits the OLD
model) → `port_free` in grpo_autoeval.sh kills by port; vr_serve needs absolute `--rpy/--script-dir`.

---


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

---

## DeepSeek GRPO (low-resource, serv-19 GPUs 4-7)

Started 2026-10-06 evening (user-approved: DeepSeek serving AND LoRA training on serv-19 GPUs 4-7 only; GPUs 0-3 /
port 8000 = hub replica, never touched; serv-19 CPUs stay light; scoring on serv-20 CPUs, 16 single-thread workers;
no serv-20 GPUs).

**Loop** (one round = serve -> sample -> score -> update -> merge, all automatic):
1. serve policy u_r on serv-19 GPUs 4-7 (vLLM TP4+EP, :8200, served name `pol`, ~11-14 min startup);
2. G=4 samples x P=48 hard real training parts (`results/h6c/real4_hard_keys.txt` + `c2_hard_keys.txt`, 3,009 parts,
   one Random(0) order, round r takes rows [48r, 48r+48)), thinking mode, prompt = `vis_repair.py` SYS + SCRATCH
   ("Do not deliberate at length", = hub T0 regime), `Reasoning Effort: 50` (= hub "low"), T=0.8, top_p 1;
   every 2 rounds also 1 draw x the 144-part held-out real bench (`ext_bench_dw423_perm`, never trained on);
3. stop server; score on serv-20 (`score_partials.py --accept 0`, exec 60 s / IoU 90 s);
4. reward = centred IoU if executed else 0; A = (r - group mean) / batch std (Dr.GRPO centring, batch-std scale);
   zero-variance groups skipped; rows = draws with code (incl. reward-0 exec failures); truncated/no-code draws are not
   trained but count in the group mean (=> length pressure);
5. one advantage-weighted pass on serv-19 GPUs 4-7: loss_row = A * mean token NLL(reasoning + reply) on logits/0.8,
   16 rows per AdamW step, lr 2e-5 constant, clip 1.0, LoRA r32 on attention q_a/q_b/kv/o_b of layers >= 24, adapter
   + AdamW state continued across rounds;
6. merge adapter -> BF16 attention tensors (see below) -> next round.

**Decisions / findings while building (all measured):**
- **8k budget infeasible**: vanilla at effort 50 truncates 20/24 samples at 8,192 tokens (effort 20: 19/24); at 16,384:
  14/24. Loop uses max_tokens 16,384 (trainer max-len 18,000). Eval uses the same budget, so the held-out number is
  "within 16k tokens" and partly rewards finishing (not comparable to the uncapped 0.299 or the hub 0.308 with fix turns).
- **FP8 merge eats RL updates**: `geom/dsv41_merge_diag.py` -- a 2-step RL adapter (|d|/|W| 2.7e-4) keeps only 1.1% of
  its delta after FP8 E4M3 requantisation (SFT adapter selftrain_r32, |d|/|W| 1.3e-2: 53%). Fix: `merge_dsv41_lora.py
  --bf16` writes adapted tensors as BF16 W+d (exact) and lists them in `quantization_config.ignored_layers` (checkpoint
  names, `language_model.model.` names AND the fused `fused_wqa_wkv` name -- the VL wrapper has no class-level
  packed_modules_mapping; without the fused name vLLM loads BF16 into MXFP8 params and emits hex garbage). Shared experts
  dropped from the LoRA (vLLM fuses them into MegaMoE; FP8 only). Round 0 serves the base in the SAME layout
  (`--delta-scale 0`, template `grpo_ds/zero_template`) so every eval delta is like-for-like.
- **4-GPU training memory**: a 9k-token row OOMed the last GPU in forward (16 trainable layers keep MoE activations).
  `dsv41_lora_train.py --grad-ckpt` = non-reentrant checkpointing of decoder layers >= min-layer through the layers'
  own GradientCheckpointingLayer hook, with a per-layer snapshot of the shared CSA2 `shared` dict (a recompute would
  otherwise read the last writer's state). `--ckpt-check`: LoRA grads with vs without checkpointing bit-identical
  (rel err 0, 12k tokens, layers >= 36). Peak at 15k tokens: 0/102/84/153 GiB (device_map leaves GPU 4 empty -- the
  planner books the CPU-resident engram tables there). Row cost ~10-15 s at 10-15k tokens; process start ~4 min +
  ~90 s Triton autotune on the first row.
- On-policy check: trainer token counts equal vLLM prompt+completion tokens exactly (1111 + n) for every row.
- **MAJOR RISK -- the HF trainer is not the served policy.** Same tokens (3 vLLM samples, 4,000 tokens each,
  `geom/dsv41_grpo_lpdiag.py` -> `dsv41_lora_train.py --adv-weighted --score-only`): vLLM raw mean NLL 0.51 / 0.29 /
  0.55 vs HF draft (PR #48768) 2.06 / 2.30 / 2.25, HF top-1 agreement with the sampled token only 47-54%, label
  alignment verified (offset 1 best). Invariant to: bf16 autocast on/off, chunked vs eager attention, use_cache
  True/False, train vs eval mode, and the upstream `malaiwah:deepseek-v41-review-fixes` UE8M0 tensor-route fp8 fix
  (tried on serv-19's `.venv_dsv41`, no change, reverted; original kept as `finegrained_fp8.py.orig_a290b39`). Worst
  tokens are long-range ones (identifiers defined earlier in the program: 15-20 nats; image-grounded words/numbers) ->
  suspect the draft's compressed/sparse (CSA/indexer) attention or the vision path. So the policy gradient is taken
  through a degraded copy of the policy (the same weights, LoRA in the same places). This likely also explains why
  every earlier DeepSeek LoRA (SFT think-LoRA -0.091, self-train +0.002) failed to help. The loop was launched anyway
  (cheap, user asked for it); its held-out eval decides whether updates through this forward transfer. Fixing the HF
  forward (or a trainer that matches vLLM) is the real next step if the curve is flat.

**Scripts** (all new, under `train_v14/`):
`serv19/dsv41_grpo_loop.sh` (driver, runs on serv-20), `serv19/dsv41_grpo_s19.sh` (serv-19 side: serve/up/stop/train/
merge), `serv19/dsv41_grpo_train_serv19.sh` (update), `geom/dsv41_grpo_rollout.py`, `geom/dsv41_grpo_rows.py`,
`geom/dsv41_grpo_parts.py`, `geom/dsv41_grpo_eval_summary.py`, `geom/dsv41_grpo_prompts.json`,
`geom/dsv41_grpo_zero_template.py`, `geom/dsv41_merge_diag.py`, `geom/dsv41_grpo_lpdiag.py`, `geom/dsv41_grpo_fake_tier.py`;
modified `geom/dsv41_lora_train.py` (`--adv-weighted --score-only --grad-ckpt --ckpt-check --logit-temp --opt-state
--const-lr --reasoning-effort`, reply.txt/adv.txt rows) and `geom/merge_dsv41_lora.py` (`--bf16 --delta-scale`).

**Monitor** (serv-20): `/srv/scratch/bimrose2/grpo_ds/<NAME>/loop.log`, `progress.tsv` (per round: mean reward, best-of-4,
first draw, exec, trunc, median tokens, frontier, rows, minutes), `r<NN>/stats.json`, `eval_summary.txt` (held-out,
paired vs u0 with bootstrap CI). serv-19: `/srv/scratch/bimrose2/grpo_ds/<NAME>/{serve_u*,train_u*,merge_u*}.log`.
**Stop**: `ssh wpk-serv-20 touch /srv/scratch/bimrose2/grpo_ds/<NAME>/STOP` (exits at the next stage boundary and
stops the server). Hard stop: `kill $(cat .../<NAME>/driver.pid)` on serv-20, then on serv-19
`bash /srv/scratch/bimrose2/train_v14/serv19/dsv41_grpo_s19.sh stop` (kills only the pgid in grpo_ds/serve.pgid). A running
update is `dsv41_lora_train.py` on GPUs 4-7 (kill its pid explicitly). Resume: `START=<r> NAME=<NAME> setsid nohup bash
train_v14/serv19/dsv41_grpo_loop.sh &` (needs `dsv41_ft/<NAME>_u<r>` merged and `grpo_ds/<NAME>/adapter_u<r>` on serv-19).

**Smoke test (2026-10-06 19:02-19:46, NAME=dssmoke, P=8, 8 eval parts):** every stage ran unattended -- zero-delta
BF16 merge -> serve (11 min) -> 32 rollouts (2.7 min) -> score -> 14 rows -> update (8 min incl. load; 64 LoRA targets,
30.4M params) -> BF16 merge (1.5 min) -> serve u1 (11 min) -> eval -> summary. Earlier the first BF16 merge without the
fused name served hex garbage (caught, fixed). 30 min/round at P=8.

**Status (launched 2026-10-06 20:10, NAME=dsgrpo1, ROUNDS=8, P=48, G=4, T=0.8, 16k tokens, lr 2e-5):** driver pid
538380 on serv-20 (`/srv/scratch/bimrose2/grpo_ds/dsgrpo1/driver.pid`). Round 0: 53 min (serve 12, rollouts + eval
16, score 1, update 22 incl. ~4 min load + 93 s first-row autotune, 87 rows / 6 AdamW steps, grad-norm 0.03-0.06,
peak 141 GiB on GPU 7; merge 1.5). Round-0 training stats: mean reward 0.153, best-of-4 0.305, exec 0.41, truncated
0.55, frontier 0.75. **Held-out u0 (vanilla, same layout, 16k budget, 1 draw, T 0.8): 0.105 over 144 parts** (37
executed, 9 >= 0.8; 102/144 truncated at 16k) -- the baseline every later eval (u2/u4/u6/u8) is paired against.
Not comparable to e55 first draw 0.390 / RL'd Qwen 0.467 (those finish; DeepSeek mostly does not within 16k).
u1 served and produced sane samples at 21:16. Expected finish ~05:00 2026-10-07 (9 policies, ~55 min/round).


### 2026-10-07 — trainer/sampler mismatch: ROOT CAUSE FOUND AND FIXED

`dsgrpo1` stopped cleanly (STOP file) after round 2 (u3 merged; u2 held-out 0.116 vs u0 0.105, +0.012 [-0.025,+0.051]).
Its updates went through the broken forward -> reference only, not resumed.

**Bisection** (harness: `geom/dsv41_parity.py` collect/score -- vLLM prompt_logprobs / sampled-token logprobs of the
SAME token ids are the reference; prompt ids verified identical, 1111/1111, for image prompts):
- (a) text-only, no image: gap present (HF 2.40 vs vLLM 2.00 in the first 128 tokens) -> not the vision path.
- (b) gap vs context: vLLM NLL falls with context (2.00 -> 0.88 -> 0.87 -> 0.59 at 0-128/128-512/512-2k/2k-8k), HF
  stays flat ~2.3 -> HF cannot use long-range context.
- (c)/(d) module unit checks vs a plain-PyTorch dequantized reference (`geom/dsv41_unitcheck.py`, reference
  inference/convert.py dequant: FP8 E4M3 x UE8M0 32x32; FP4 e2m1 low-nibble-first x UE8M0/32): every FP8 linear,
  the grouped o_a, shared expert, sqrt-softplus router and the FP4 routed experts match within activation-quant noise
  (rel 1-4%, cos >= 0.9997) at layers 0/2/21/30. Not weights/dequant/MoE.
- (e) per-layer vs vLLM (`serv19/dsv41_vllm_layerdump.sh` = offline vLLM TP4+EP eager with hooks on every layer's
  attention/FFN; `geom/dsv41_layercmp.py`): layers 0-1 (pure sliding window) match (rel 0.04-0.06); **layer 2 =
  the first compressed-attention layer: attention output rel 0.997**. A plain-PyTorch port of the reference attention
  (`geom/dsv41_attn_ref.py`) on HF's own layer-2 input matches vLLM (rel 0.10) but not HF (0.99); HF equals the
  "window-only" variant. The CSA2 `shared` dict after layer 2 holds compress_kv/compress_lens but NO `topk_idx` /
  `index_k` (`geom/dsv41_shared_dbg.py`).
- **Root cause:** the attention calls `self.indexer(..., cache_layer, shared)` with `shared` POSITIONALLY; under
  device_map, accelerate's AlignDevicesHook on the indexer `send_to_device(args)` rebuilds the dict, so the indexer's
  writes (`topk_idx`, `index_k`, `candidates`) land in a throw-away copy. `_skip_keys_device_placement=["shared"]`
  only covers keyword args. Every layer 2-39 silently ran sliding-window-only (128 tokens). (This also invalidates
  every earlier HF-path DeepSeek result: SFT think-LoRA, self-train, HF generate evals.)
- **Fix:** `geom/dsv41_hf_fixes.py::fix_shared_dict_hooks(model)` removes accelerate hooks from the 8 indexer modules
  (their inputs are already on the layer's device). Parity after the fix, 8,192-token text: HF 0.878/0.870/0.587 vs
  vLLM 0.878/0.866/0.586 (128-512/512-2k/2k-8k), top-1 agreement 0.92-0.97; image prompts (3 x 3,000 sampled tokens):
  HF NLL 0.824/0.839/0.825 vs vLLM 0.808/0.827/0.812 (within 2%), top-1 agreement 0.72 (being chased: image path).
- **Image path (second, smaller discrepancy):** the trainer used the torchvision image processor; vLLM and the
  reference use PIL (`ImageOps.pad`, PIL bicubic) -> ViT features at image positions differed ~4% at layer 0
  (text positions 0.3%). Trainer and harness now use `DeepseekV41ImageProcessorPil` (`--fast-image` restores the old
  one). The earlier "image top-1 0.72" was a measurement bug: vLLM lists the SAMPLED token first in `top_logprobs`, so
  it measured HF-argmax == sampled-token; the harness now takes the max-logprob entry of top_logprobs=5.

**Rollout regime (T0) reverse-engineered** (`geom/dsv41_t0_rollout.py`): the 0.308 run (vis_repair.py --arm scratch,
round 0) went through the hub's Anthropic /v1/messages: system = vis_repair.SYS, user = [sheet, SCRATCH], max_tokens
30000, `output_config.effort="low"`, no temperature (server default 1.0), and up to 3 calls (code-less reply -> "Answer
now ..."; exec failure -> fix turn with the last 15 traceback lines). Hub usage log for that window: 203 first/second-turn
DeepSeek calls, median 16.9k output tokens, ~25% at the 28.5k cap. vLLM renders effort "low" as **"Reasoning Effort:
25"** (encoding.py's own mapping says low = 50 -- the 16k-budget loop used 50). The client replays this exact request
against OUR server (/v1/messages on serv-19 :8200), scores like vis_repair (exec 120 s, IoU 300 s), saves every call's
context so the trainer rebuilds the final call's conversation (`ctx.json` rows; `dsv41_lora_train.py` multi-turn
`context`; EFFORT=25, LOGIT_TEMP=1.0 via `grpo_ds/<run>/train.env`).

**Parity after both fixes** (fixed indexer hooks + PIL images; `grpo_ds/logs/parity3.log`, `parity2.log` on serv-19):

| sequence | HF NLL | vLLM NLL | top-1 agreement (HF argmax vs vLLM argmax) |
|---|---|---|---|
| text 8,192 tok #1 (pos 512-2k / 2k-8k) | 0.870 / 0.587 | 0.866 / 0.586 | 0.945 / 0.956 |
| text 8,192 tok #2 (pos 512-2k / 2k-8k) | 0.673 / 0.478 | 0.672 / 0.480 | 0.957 / 0.965 |
| image prompt + 6,000 sampled tok #1 | 0.764 | 0.755 | 0.948 |
| image prompt + 6,000 sampled tok #2 | 0.744 | 0.732 | 0.951 |
| image prompt + 1,521 sampled tok #3 | 0.634 | 0.623 | 0.961 |
| (before the fix, same image prompts, 3,000 tok) | 2.47-2.55 | 0.81-0.83 | (n/a) |

Prompt token ids identical (1111/1111). T0 rows: trainer prompt/full lengths equal the server's input/input+output token
counts for 17/17 rows incl. 2-3-call contexts (`geom/dsv41_t0_tokcheck.py`).

**T0 regime reproduced:** vanilla FP8 base on our server, 144 held-out parts, 1 episode each: **0.318** (133 executed,
1.42 calls/episode, 22 min) vs the hub's 0.308 (132/143) (`serv-20 grpo_ds/t0check/base_fp8.jsonl`).

**Trainer checks on real T0 rows** (`grpo_ds/logs/t0_ckcheck.log`, `t0_smoke_train.log`): activation checkpointing with
the indexer now live (layers >= 36 incl. index source 36): LoRA grads with vs without checkpointing bit-identical (rel
err 0, 16.9k tokens). Full config (layers >= 24, 64 attention LoRA targets): rows up to 30.9k tokens fit, peak
0/107/105/205 GiB (GPUs 4-7), 31k-token row 19 s fwd + 19 s bwd, ~26 s/row average, per-row CE 0.48-0.62 (= vLLM's
~0.6 NLL on its own samples; the broken forward gave 2.2-2.4), grad norms non-zero.

**Run `dsgrpo2` (launched 2026-10-07 01:03, serv-20 driver pid 1635369):** `serv19/dsv41_grpo_loop2.sh`, NAME=dsgrpo2,
8 rounds, P=48 hard real parts x G=4 T0 episodes (inline exec/IoU scoring, 2 x 8 workers), held-out 144-part T0 eval at
u0/u2/u4/u6/u8 (paired vs u0, `eval_summary.txt`), lr 2e-5 const, AdamW continued, batch-std advantages, rows = final
call of each episode (<= 34k tokens), EFFORT=25 / LOGIT_TEMP=1.0, BF16-attention merges, gate: stops after round 0 if
u0 < 0.22. Monitor: serv-20 `/srv/scratch/bimrose2/grpo_ds/dsgrpo2/{loop.log,progress.tsv,eval_summary.txt}`, serv-19
`/srv/scratch/bimrose2/grpo_ds/dsgrpo2/{serve_u*,train_u*,merge_u*}.log`. Stop: `touch .../dsgrpo2/STOP` (serv-20).
`dsgrpo1` (broken forward, 16k/effort-50 regime) kept for reference only: serv-20 `grpo_ds/dsgrpo1/`, serv-19 adapters
`grpo_ds/dsgrpo1/adapter_u{1,2,3}`, merged `dsv41_ft/dsgrpo1_u3`.
- dsgrpo2 round 0 (2026-10-07 01:03-): merge 1.5 min, serve 11 min, 192 training episodes + 144 eval episodes
  concurrently 26 min, rows: 187 (92 pos / 95 neg), frontier 0.98, train mean reward 0.384, best-of-4 0.542, exec 0.99,
  1.16 calls/episode. **Held-out u0 (round-0 baseline, same BF16 layout as every later policy): 0.291** (132/144
  executed, 15 >= 0.8; first call only 0.248) -- gate passed (FP8 base on the same server: 0.318; single-draw noise
  about +-0.03). Update: 12 AdamW steps x 16 rows, ~330 s/step (~70 min incl. load), peak 203 GiB on GPU 7,
  grad-norm 0.003-0.004. Expected ~1 h 50 min per round, u8 eval around 2026-10-07 18:00-19:00.

### 2026-10-07 13:00 — DeepSeek all-in (coordinator GO: dsgrpo2 u6 = 0.327 vs u0 0.291, +0.037 [+0.002,+0.072])

dsgrpo2 held-out so far: u2 +0.026 [-0.010,+0.059], u4 +0.011 [-0.025,+0.043], u6 +0.037 [+0.002,+0.072] (0.327,
138 exec, 22 >= 0.8).

1. **dsgrpo2 extended to 16 rounds** without restart: `serv19/dsv41_grpo2_extend.sh` (serv-20 pid 2231529) waits for
   the running driver to finish round 8, then resumes `dsv41_grpo_loop2.sh` with START=8 ROUNDS=16 (u8 eval is reused
   by the resumable client; u8's merge is kept by the driver). Evals stay every 2 rounds. Follow-up when it ends:
   the self-train rerun (3).
2. **dsgrpo3 = guided GRPO on serv-20 GPUs 0,1,2,7** (`serv19/dsv41_grpo_loop3.sh`, driver pid 2974732; GPU side
   `serv19/dsv41_grpo_host.sh` + `serv19/hcfg_serv20.sh`, port 8500, image copied from serv-19
   (`containers/dsv41-flash-v0909.sif`; serv-20's `vllm-dsv41.sif` is a different build). GPUs 0-1 also hold ~18 GB
   of afm8's processes (left alone; BUSY_MIB=30000). Starts from dsgrpo2 adapter u6 (+ its AdamW state), lr 1.5e-5,
   same fixed trainer / T0 regime; held-out evals every 2 rounds paired vs dsgrpo2's vanilla u0. Guard: exec or code
   rate < 0.85 -> stop (previous adapter kept = rollback point).
   - Guidance: 1,000 of the 2,382 bank programs (bankv2_c4 1,415 / bankv2_c2 670 / bank_c1 297, all usable) are
     rationalized once with the round-0 server (`geom/dsv41_t0_rationalize.py`). The plain STaR hint FAILED in the T0
     regime: 87/100 traces were "the user provided a verified program, just output it" (and the first LEAK regex missed
     "verified correct program"). `--mode write` instead asks DeepSeek to WRITE the first-person solving notes for the
     drawing that lead to the program, never mentioning it (24/24 clean in a test, ~2k tokens, real read-the-views
     reasoning); the trained reply = the bank program. Training parts = rationalized bank parts only. Rows:
     `dsv41_t0_rows.py --bank` adds the bank program as an extra group member (true IoU) when it beats all G draws by
     >= 0.05. No KL anchor (the trainer has none; guard + conservative lr instead).
3. **Self-train rerun** queued on serv-19 after dsgrpo2 (`serv19/dsv41_selftrain_rerun.sh`, launched by the extend
   watcher): same 492-row tier, fixed trainer, T0 prompt + Reasoning Effort 25, attention-only LoRA r32 layers >= 24,
   lr 1e-4, 125 x 8, then BF16 merge + T0 eval vs dsgrpo2 u0. (Fixed: the SFT path ignored `--reasoning-effort`.)
- 2026-10-07 15:00 status. dsgrpo2: u8 = 0.305, +0.014 [-0.023,+0.050] (131 exec, 19 >= 0.8) -> paired deltas u2/u4/u6/u8 =
  +0.026/+0.011/+0.037/+0.014 (all positive, individually mostly n.s.). Original driver exited cleanly 14:56; the
  extension resumed at 14:58 (START=8 -> 16, same log). dsgrpo3: rationalization 998/1000 kept (write mode, 35 min,
  1 leak, 1 error); round 0 = 48 bank parts x 4: train mean reward 0.442, best-of-4 0.588, exec 0.95, 28/48 groups got
  the bank program as a guided member (215 rows, 28 guided); **first held-out eval u0 (= dsgrpo2 u6 weights, a second
  independent draw): 0.319, +0.028 [-0.010,+0.068] vs vanilla u0** (134 exec, 21 >= 0.8; dsgrpo2's own u6 draw: 0.327).
  First update crashed once (`dsv41_hf_fixes.py` not yet on serv-20) -> shipped, loop3 resumed with a no-server
  shortcut for already-complete episodes; update 1 running (14 steps x 16 rows, ~450 s/step, peak 202 GiB).

## Real-part pool v2 (2026-10-08 03:30) — 12,969 hard-mined real parts (DeepCAD/Onshape), ~3x the old pool

**CADBench is exhausted; the pool comes from DeepCAD instead.** CADBench = 18,000 rows, but MCB + Objaverse (6,000) carry
no STEP. Of the 12,000 STEP parts, corpora 1-3/abccode/benches used 4,860 file_ids and `build_corpus4.py` downloaded the
remaining 7,148 (`rft_corpus4/download_stats.json`); prep kept 3,203 (rejected aspect 1,149 / faces > 400 1,443 / freeform
1,179 / fill 140 / multi-body 9 / timeout 24) and 3,007 rendered. **Zero new CADBench parts pass corpus 4's filters.** The
other real source already rendered in the identical sheet format is the DeepCAD full split (`deepcad/corpus_full`, Onshape
user parts, CADBench's own "B" family is DeepCAD): draftwright 0.4.23 + font patch 5.25, `render_ext.py/worker_v11
VLM_MODE=1 via render_isolated.sh`, eval_cache_v15 + gt_meshes_v15, all sheets `renderer: draftwright` (no legacy), plus
e55 K=8 scores for 86,904 parts. No rendering was needed.

**Selection** (`train_v14/mech/benchmarks/build_realpool_v2.py select`): corpus-4 prep filters re-applied (min faces 6,
max aspect 15, max faces 400 — DeepCAD prep had run at 3 / 40), corpus-4 exclusion rule (every file_id in any
`data/*/manifest.json`: 71 dropped) + the DeepCAD gate bench (601), certified sheet + GT mesh required → **51,363 parts**.
Held-out benches (real 144 = F/A families, famheld, indh) cannot overlap. These parts were in e58's SFT tier only (not
in e55 / the GRPO lineage).

**Mining:** candidates = e55-hard by the same rule on e55's K=8 (24,657, shuffled seed 0, packed to
`rft_realpool_v2/mine/`). RL generator mix_t10 s120 (LoRA `t10s120` on e55) K=4 (draw 0 greedy + 3 at T 0.7 / top_p 0.95,
`gen_openai_bo.py`), served by job 11205009's idle vLLMs :8500/:8501 (ccc0474 GPUs 0/2, whose trainers had finished; adapter
unloaded afterwards) — 98,622 candidates in 3.0 h (~125 parts/min). Scored with `score_partials.py` (exec 60 s / IoU 90 s)
in overlap steps on the idle CPUs of grpo-fast jobs (ccc0474/0475/0451) + 24 CPUs on ccc0442 (ccc0442 had ~5 free CPUs at
the start) — 4.4 h. Rule = real4_hard_keys rule on the RL draws: 0.1 < max, mean < 0.75, var > 0 → **12,969 hard**
(`build_realpool_v2.py mine`; stats `realpool2_hard_keys_stats.json`). RL rejects: mean >= 0.75 11,083, max <= 0.1 146,
zero variance 1,757.

| on the 24,657 mined parts | first | mean | best | best >= 0.8 |
|---|---|---|---|---|
| e55 K=8 (DeepCAD full pass) | 0.465 | 0.454 | 0.689 | 38% |
| t10s120 K=4 | 0.674 | 0.670 | 0.755 | 53% |
| on the 12,969 hard: e55 / RL | 0.363 / 0.508 | 0.356 / 0.505 | 0.574 / 0.630 | 14% / 20% |

Paired RL − e55: mean +0.216, first +0.208. Caveat: candidates were picked by e55's own draws, so part of that gap is
regression to the mean; the 26,706 e55-easy parts (e55 mean >= 0.75) were not mined (a few may be RL-hard).

**Files.** Bench (GRPO `--bench`): cluster `train_v14/mech/benchmarks/data/rft_realpool_v2/` (eval_cache_v15.pkl 1.37 GB,
12,969 parts, pools certified = hard keys; gt_meshes_v15; manifest; `realpool2_hard_keys.txt`; `select_e55.json`;
`mine/` = the 24,657-part mining bench for re-thresholding) and serv-20 `/srv/scratch/bimrose2/mech_benchmarks/rft_realpool_v2/`
(same minus `mine/`, plus `bo8_realpool2_e55.json`). Keys: `results/h6c/realpool2_hard_keys.txt` (also serv-20
`fp/h6/`). Paired-join baseline (e55 K=8 on the hard parts): `results/h6c/bo8_realpool2_e55.json`. RL draws + scores:
`results/realpool_v2/bo4_t10s120.shard*.json.partial.json` + `*.scored.jsonl`; drivers `gen_rl.sh`, `score_loop.sh`,
`finalize.sh` there. Sheets with >= 1 unplaced dimension: 34% (corpus-4 hard: 43%; neither cache drops them).
**Use:** add as a 4th bench, e.g. `--bench ...,train_v14/mech/benchmarks/data/rft_realpool_v2 --keys ...,` (empty = whole
pool) — it is 3x the old 4,451-part pool by itself; consider weighting/sampling so CADBench F/A/E idiom is not swamped by
DeepCAD's sketch+extrude idiom (DeepCAD-as-SFT was inert on real benches, e58; as RL prompts it is untested).

## Selection on RL candidates (2026-10-08, selection agent)

**Question:** GRPO lifted the real-bench vote (0.516 → ~0.63) and oracle (0.593 → ~0.70); ~0.06–0.07 is lost in selection.
Do label-free selectors tuned on e55 recover it? All numbers: 144-part `ext_bench_dw423_perm`, paired bootstrap 95% CI
(2,000 resamples, `geom/grpo_eval_summary.py` style), exec/iou read from the candidates file (consistency files clean:
re-executed == n_exec for all). Tool: `geom/sel_study.py` (specs `results/selection/spec_*.json`, tables `sel_*_table.txt`).

**K=8 stored candidates** (Δ vs the same model's vote; "gap" = share of vote→oracle closed; last col Δ vs e55ctl vote):

| selector | e55ctl (0.516 / 0.593) | mix_t10_s120 (0.629 / 0.688) | guide_mb8b_s60 (0.628 / 0.698) | mix_t10 vs e55ctl vote |
|---|---|---|---|---|
| v3b-EV verifier argmax | +0.020 [-0.001,+0.042] 26% | +0.015 [-0.003,+0.033] 25% | +0.019 [+0.004,+0.036] 27% | +0.127 [+0.095,+0.161] |
| gate 0.85 (served) | +0.019 [-0.002,+0.041] | +0.015 [-0.002,+0.034] | +0.018 [+0.003,+0.035] | +0.128 |
| gate 0.7 | +0.015 | +0.008 [-0.006,+0.024] | +0.010 | +0.121 |
| render-compare v3 argmax | +0.021 [-0.001,+0.045] 27% | +0.014 [-0.002,+0.032] 24% | +0.017 [-0.001,+0.037] 24% | +0.127 |
| v3 among top-3 by agreement | +0.013 | −0.002 | +0.003 | +0.110 |
| **verifier EV + v3 (raw sum)** | **+0.031 [+0.010,+0.054] 40%** | **+0.026 [+0.010,+0.043] 43%** | **+0.030 [+0.013,+0.047] 42%** | **+0.138 [+0.107,+0.170]** |
| agreement + verifier + v3 | +0.029 | +0.015 | +0.021 | +0.128 |

Verifier over 9 RL checkpoints (mix_t10 s120/s200, guide_mb8b s60, soup1 s20, mix_b32 s120/s200, gt10_mb8 s60, mix_cont
s200, guide2b s120): mean Δ vs vote **+0.020 [+0.012,+0.029] (30% of the gap)**; gates sweep 0.5–0.95 (post-hoc) is
monotone: 0.5 +0.004, 0.7 +0.010, 0.85 +0.017, 0.95 +0.020 — **more vote = worse**. Why: RL makes candidates agree
(medoid agreement ≥ 0.85 on 40% of parts vs 19% for e55; median 0.82 vs 0.64) but agreement stops meaning correctness —
in the 0.7–0.85 band the mix_t10 vote is 0.505 (e55 0.646 in the same band); verifier beats vote in every band below 0.85.
Top-k-by-agreement restrictions (v3 or verifier among top 2–4) are all ≈ vote: the medoid's cluster dominates the top-k.
Verifier quality on RL candidates: AUROC ≥0.8 0.92–0.97 (e55 0.935) but per-part Spearman 0.26–0.47 (e55 0.47) —
within-part ranking of near-correct candidates is the weak spot. v4 (e55-base verifier) on the same files: e55ctl
+0.040 [+0.021,+0.061] (it was trained on e55 candidates) but RL +0.013 / +0.018 — same as v3b.
Per family (mix_t10 s120): F vote 0.683 → ver+v3 0.710; A 0.544 → 0.567. Post-hoc caveat: ~30 selectors were looked
at; ver+v3 is the one natural a-priori combo and replicates on 3 generators and on an independent K=8 draw (below).

**Test-time scaling** — mix_t10 s120 as LoRA `t10s120` on vLLM (ccc0451 :8503), K=32 (draw 0 greedy, T 0.7, the eval
recipe); K=8/16 = first draws of the same file (`results/selection/real_k32_t10s120*.json`):

| K | vote | verifier | gate0.85 | v3 | **ver+v3** | oracle | ver+v3 vs e55ctl vote |
|---|---|---|---|---|---|---|---|
| 8 | 0.622 | 0.644 | 0.642 | 0.638 | **0.651** (+0.029 [+0.014,+0.046]) | 0.682 | +0.135 |
| 16 | 0.629 | 0.660 | 0.658 | 0.665 | **0.672** (+0.043 [+0.027,+0.063]) | 0.711 | +0.156 [+0.123,+0.188] |
| 32 | 0.635 | 0.663 | 0.660 | 0.666 | **0.677** (+0.042 [+0.025,+0.060]) | 0.720 | +0.160 [+0.128,+0.193] |

Paired vs K=8: vote +0.007 (K16, n.s.) / +0.013 [+0.002,+0.025] (K32); verifier +0.016 / +0.019; oracle +0.029 / +0.038.
The vote barely scales; learned/visual selection does, and most of it arrives by K=16 (16→32 adds +0.005 for 2x draws).

**Verifier retrain (v5) — trained, NOT evaluated.** `runs/v5-verifier-rl-warm/final` = v3b warm start
(`lora_init_adapter`, new flag in `train_sft_v14.py`), 600 steps × 16 on one H200 (ccc0451 GPU 7, `configs/accelerate_1gpu.yaml`)
over 13.9k mix_t10 s120 K=16 T=1.0 candidates on the 908 corpus-2 hard TRAINING parts (`results/selection/bo16_c2_t10.json`,
scored here; held-out file_ids excluded and verified: 0 bench keys) + 2 v3b shards; val loss flat 0.383–0.386. Its bench
scoring (`results/selection/vscore_v5.sh`) died at 10.6k/15k candidates when host job 11181389 ended at 03:33 (preds are
written only at the end). Re-run that script on any free GPU (~75 min; `--prefix v5preds_`), then `sel_study.py` with
`vpreds` → `v5preds_*`. corpus-4 (2,101 parts) was not used.

**Recommended serving selector:** drop the agreement gate for RL generators; pick argmax(v3b-EV + render-compare v3) over
the executing draws, at K=16 (0.672 vs vote 0.629 at K=16, vs the e55 system's vote 0.516: +0.156). Cost: one verifier
forward pass + one draftwright render per candidate (~0.6 s/candidate on 16 serv-20 cores). Interaction with the rp3
repair loop untested — the repair start should be this pick, not the vote.

Files: `geom/sel_concat.py`, `sel_vscore.py` (one model load for many candidate files), `sel_study.py`, `sel_vquality.py`.
Trap: a NEW top-level dir created on ccc0442 (`rft_scored_rl_v5/`) stayed invisible on ccc0451 for 30+ min (stale Lustre
dentry; a polling `ls` probably cached the negative lookup) — keep cross-node job inputs under dirs that already exist.

## RFT consolidation cycle (2026-10-08, RL → RFT → RL)

**Hypothesis.** Every RL recipe peaks ~step 120 and loses diversity; guided GRPO (bank programs injected off-policy) lifts
best-of-8 to 0.698 but collapses in long runs. Put the good programs into SUPERVISED training (stable), then run plain RL
again from the consolidated adapter.

**Tier** (`geom/build_rft1_tier.py` → `results/guide/rft1/tier/`, stats `tier_stats.json`): per hard real training part, the
single best GT-scored program among {mix_t10 s120 K=16 T=1.0 samples (`results/guide/v3/bo16_c{2,4}_t10.json`; executing,
with think), bank entry (`bankv2_c4`, `bankv2_c2`, `bank_c1`; rationalized e55-voice plan)}, kept if IoU ≥ 0.75; ties keep
the RL sample; sheet PNG = the bench's `eval_cache_v15` sheet (the exact prompt image of RL/eval). Held-out guard: hard
error if any file_id is on `heldout_file_ids.txt` / `ext_bench_dw423_perm` (0 hits). **1,859 rows, mean IoU 0.891, 877 ≥ 0.9;
977 from RL samples, 882 from the bank.** corpus 4: 1,194 of 2,216 parts (0.900; 715 RL / 479 bank); corpus 2: 541 of 936
(0.878; 262 / 279); corpus 1: 124 of 297 bank-only parts (0.860). Packed with `pack_rft_shards_dir.py` (new `--per-shard`,
4 equal shards of 465; also fixed: a `--repeat N` value used to be parsed as the PNG dir).
**Mix** (`results/guide/rft1/build_mix.sh` → `results/guide/rft1/mix/`, 101 shard links): 4 tier shards × 22 + 13 shards of
the d0 e55 mix (10 dw423b base + 3 union5, ~26k rows); config `rft_frac 0.8 / reasoning 0.1 / plain 0.1` → tier ≈ 49% of
draws, e55 SFT/RFT/reasoning/plain rows ≈ 51% (anti-forgetting).

**SFT** `configs/rft1-from-t10.yaml`: `lora_init_adapter` = `runs/grpo_v_mix_t10/adapter_step120` on e55 final (r64, all 12
LM linear types, 467M trainable), lr 2e-5 cosine → 2e-6, warmup 3%, batch 2 × accum 8 = 16, 450 steps = 7,200 samples
(≈ 1.9 tier epochs), max_seq 5120, grad ckpt, no val. One H200: ccc0475 GPU 3 inside grpo-fast job 11182777
(`sbatch/grpo_overlap_cmd.sbatch`, `results/guide/rft1/train_rft1.sh`), 16.8 s/step, 2 h 06 min. Token loss 0.246 → ~0.18-0.19.
Output `runs/rft1_from_t10/final` (+ checkpoint-150/300/450); serv-20 copy `runs/grpo_v_rft1/adapter_step20`.

**Real bench** (144 parts, K=8, draw 0 greedy + T 0.7, serv-20 eval daemon, `grpo_cons_loop` vote: clean, 1,063/1,063
re-executed; `results/grpo_eval/real_rft1_s20{,_consistency}.json`):

| model | vote | draw-0 | first-exec | mean-cand | best-of-8 | exec |
|---|---|---|---|---|---|---|
| e55ctl | 0.516 | 0.390 | 0.466 | 0.396 | 0.593 | 0.788 |
| mix_t10_s120 | 0.629 | 0.576 | 0.586 | 0.583 | 0.688 | 0.966 |
| **rft1 (consolidated)** | **0.624** | 0.560 | 0.588 | 0.545 | **0.699** | 0.923 |
| rft1 − mix_t10_s120 | −0.005 [−0.028,+0.018] | −0.016 [−0.056,+0.022] | +0.002 [−0.028,+0.032] | **−0.038 [−0.056,−0.020]** | +0.011 [−0.004,+0.025] (cons-file oracle) | −0.043 |
| rft1 − e55ctl | +0.107 [+0.074,+0.142] | +0.171 | +0.122 | +0.149 | +0.106 [+0.082,+0.132] | +0.135 |

Reading: consolidation **keeps the vote** (n.s. vs the best RL checkpoint) and **re-opens diversity** — mean candidate and
exec drop (the ~51% e55 rows pull it partly back toward e55: T=1.0 rollout exec 0.84 vs ~0.98 for mix_t10 at s120,
completions 2.1k vs 1.7k chars), best-of-8 0.699 ≈ the best guided ceiling (0.698) without guided training's collapse.
That is the intended starting point for RL round 2. (A first vote computed inside the ccc0475 overlap step lost 24/1,063
candidates to re-execution timeouts → 0.611; discarded, kept as `results/guide/rft1/*_ccc0475_degraded.json`.)

**RL round 2 `rft1_rl`** (`sbatch/arms/ovl_rft1_rl.txt`; ccc0475 trainer GPU 3 + vLLM :8501 of job 11182777 via
`grpo_overlap_arm.sbatch`): best recipe (scaled logits, batch-std adv, top_p 1, 4 minibatches, T 1.0, KL 0, guard 0.6,
entropy floor 0.1) on the mixed hard pool (real4 + c2 + family hard), `--adapter runs/rft1_from_t10/final --start-step 0`.
- **lr 2e-5 collapsed in 12 steps** (`runs/grpo_v_rft1_rl_lr2e5`, log `logs/grpo_v_rft1_rl_lr2e5.log`): entropy 0.22 → 0.53 → 0.88
  → 1.31, rollout exec 0.83 → 0.38, completions 2.1k → 3.4k chars; clipfrac 0.002 → 0.03. Cause: a mature LoRA moves
  further per Adam step — clipfrac at step 0 was already 0.002-0.003 (mix_t10 from a fresh LoRA: 0.0006 at step 0, 0.002 at
  s110; mix_cont from s120 at lr 1e-5: 0.002-0.005, stable). Stopped by hand before the guard fired (its rollback target,
  step 10, was already drifting). **Rule: RL from a trained adapter uses lr 1e-5.**
- **Relaunched at lr 1e-5** (same name `rft1_rl`, ~6.5 min/step): steps 0-12 exec 0.78-0.89, entropy 0.16-0.37 (ent_t10 from
  e55 showed the same rise to ~0.3 by step 15), clipfrac 0.0004-0.003. Adapters every 10 steps, mirrored to serv-20 by
  grpo-sync job 11213835; serv-20 `results/grpo_eval/ARMS` starts `rft1 rft1_rl ...` (backup `ARMS.bak_rft1`), so step
  20/40/60/... evals and votes are automatic.
- **Host-job end:** 11182777 hits its 48 h wall ~17:35 Oct 8 (its last original arm, mix_lr4e5_b32, cannot finish first).
  `results/guide/rft1/resubmit_rl.sbatch` (`afterany:11182777`) then resumes the arm from its newest adapter in
  a fresh **2-GPU** `grpo_fast_cluster.sbatch` job (`--gres=gpu:H200:2`, excludes ccc0451/0474 because that script's EXIT
  trap pkills every `vllm serve` of the user on the node), entropy target pinned to the original first-5-step mean,
  arms file `sbatch/arms/fast_rft1_rl_resume.txt`.

**rft1_rl step 20 (lr 1e-5), real bench:** draw-0 **0.607**, first-exec 0.610, mean 0.581, **best-of-8 0.707** (highest of
the campaign; guided best 0.698), exec 0.970. Paired vs mix_t10_s120: best-of-8 **+0.018 [+0.006,+0.030]**, draw-0 +0.030
[+0.001,+0.057], first-exec +0.023 [+0.001,+0.047], mean −0.001 (n.s.); vs rft1 (its start): draw-0 +0.046, mean +0.036,
best-of-8 +0.007 (n.s.). 20 RL steps re-sharpened the consolidated policy to mix_t10's mean quality while keeping the
higher ceiling. **Vote 0.638** (+0.009 [−0.008,+0.026] vs mix_t10_s120; +0.121 [+0.090,+0.155] vs e55ctl), cons-file
oracle +0.018 [+0.006,+0.030]; clean (1,117/1,117 re-executed). Context at 12:45: best votes so far gfrom_t10_s200 0.650,
ent_t10_s120 0.639, rft1_rl_s20 0.638 — rft1_rl_s20 has the highest best-of-8 (0.707) of any checkpoint.

**rft1_rl at lr 1e-5 ALSO diverged, at step ~27:** entropy rose monotonically from step 8 (0.17 → 0.30 → 0.5 by step 25) and
then exploded (0.88 → 1.39 → 2.74 → 4.16 at steps 28-31; exec 0.68 → 0.12, completions 6.4k chars, clipfrac 0.2). Stable
arms (ent_t10, ent_s1 from e55) hold entropy at 0.2-0.3 for 200 steps while exec rises to ~1.0; the consolidated adapter
instead drifts to higher entropy under on-policy RL (more failing T=1.0 samples → negative advantages flatten the
distribution) and the entropy floor (one-sided, target 0.18) cannot stop it. The guard fired at step 31 but reloaded
adapter_step30 — saved after step 29 (exec 0.49, entropy 1.39) and marked healthy because only the 5-step rolling exec was
checked. Stopped by hand (`runs/grpo_v_rft1_rl` steps 20-33 = this segment; adapter_step20 is the measured good point).
**Trainer changes (`geom/grpo_round.py`, both opt-in/conservative):** `--ent-max` / `--ent-max-coef` (default 0.5) = entropy
CEILING, loss += coef × relu(H − ent_max); guard marks a checkpoint healthy only if the rolling AND the latest step's exec
clear the threshold (and, with --ent-max, H < 2 × ent_max). Resume trap: with `--ent-coef` and no `--ent-target`, a resumed
run re-measures the floor target from its own first 5 steps — pin `--ent-target` on every resume.

**rft1_rl2** (`sbatch/arms/ovl_rft1_rl2.txt`, same GPU/port): resume from `runs/grpo_v_rft1_rl/adapter_step20` (start-step 20),
lr 1e-5, entropy floor pinned 0.1829 + **ceiling 0.35**, guard 0.6. Step 20 (fresh Adam): entropy 0.43, clipfrac 0.015 →
step 21 entropy 0.24, exec 0.89. Adapters synced by grpo-sync job 11215762; serv-20 ARMS = `rft1 rft1_rl rft1_rl2 ...`
(evals at 40/60/...). Auto-continuation after host job 11182777 ends: `results/guide/rft1/resubmit_rl.sbatch`
(job 11215764, afterany:11182777; NAME=rft1_rl2, keeps the pinned entropy target). The lr-2e-5 auto-resubmit (11213925) and
rft1_rl sync (11213835) were cancelled.

**Decision rule:** rft1_rl beats the plateau if its s60-s120 vote/oracle exceed mix_t10's s120 (0.629 / 0.688) and the
curve keeps rising past step 120 where every earlier recipe peaked. If it does, iterate (RL K=16 resample of the new
policy → tier 2 → SFT → RL).

## Full pipeline on GRPO generator (Oct 8)

**Question.** Does the best label-free end-to-end system built on the new GRPO generator beat the current best system
(0.695 real bench = e55 vote top-3 distinct starts → rp3 16 × 6 per chain, v3-gated, final pick by v3 across chains)?
**Primary system, declared before any result:** ent_t10 step 120 (LoRA on e55) K=16 → rank the executing draws by
v3b-EV verifier + render-compare v3 (sel_study "ver+v3") → top-3 DISTINCT by that ranking (make_vote_picks rule:
pairwise IoU < 0.95 vs every earlier pick) → rp3 repair, K=16 × 6 rounds per chain, margin 0.1, max 6000 tokens,
T 0.7 (vr_serve.py unchanged since the 0.695 run, commit b4a4589) → final pick = max v3 over the 3 chain finals
(multistart_combine.py rule). IoU vs GT only for reporting.

**Result (real bench `ext_bench_dw423_perm`, 144 parts; paired CIs = 3,000-sample bootstrap, rng 0; helped/hurt = |Δ| > 0.05):**

| stage | mean | ABC | Fusion | ≥0.85 |
|---|---|---|---|---|
| K=8 vote (grpo_eval K=8 file) | 0.642 | 0.560 | 0.694 | 32% |
| K=8 vote (first 8 of the new K=16 draws) | 0.627 | 0.553 | 0.674 | 31% |
| K=16 vote | 0.632 | 0.554 | 0.682 | 33% |
| **K=16 selected pick (v3b-EV + v3)** = chain-1 start | **0.666** | 0.587 | 0.717 | 35% |
| K=16 oracle | 0.709 | 0.634 | 0.756 | 40% |
| single chain (rp3 16 × 6 from top-1) | 0.689 | 0.593 | 0.750 | 42% |
| **MULTI-START, 3 chains, v3 pick (PRIMARY)** | **0.716** | **0.632** | **0.770** | 44% |
| oracle over the 3 chain finals | 0.740 | 0.657 | 0.794 | 48% |
| ref: e55 vote pick (start of the 0.695 run, n=143) | 0.537 | 0.487 | 0.567 | 19% |
| ref: 0.695 system single chain (n=143) | 0.667 | 0.584 | 0.719 | 40% |
| ref: 0.695 system (n=143) | 0.695 | 0.598 | 0.757 | 45% |
| ref: 0.695 oracle over chain finals (n=143) | 0.721 | 0.634 | 0.775 | 47% |

| paired Δ | all | ABC | Fusion | +/− |
|---|---|---|---|---|
| **primary − 0.695 system** (143 common parts) | **+0.020 [−0.004, +0.044]** | +0.030 [−0.004, +0.065] | +0.014 [−0.021, +0.045] | +33/−27 |
| primary − e55 vote pick (143) | +0.179 [+0.143, +0.214] | +0.140 | +0.203 | +97/−11 |
| primary − GRPO K=16 selected pick (repair's contribution, 144) | +0.050 [+0.030, +0.074] | +0.045 [+0.007, +0.087] | +0.054 [+0.030, +0.080] | +45/−17 |
| primary − single chain (multi-start's contribution) | +0.028 [+0.012, +0.044] | +0.039 | +0.020 | +29/−12 |
| single chain − K=16 selected pick | +0.023 [+0.006, +0.042] | +0.006 [−0.025, +0.041] | +0.033 [+0.014, +0.054] | +23/−11 |
| single chain − 0.695's single chain (143) | +0.020 [−0.006, +0.048] | +0.004 | +0.030 | +40/−30 |
| K=16 selected pick − K=16 vote | +0.034 [+0.013, +0.056] | +0.033 | +0.035 | +32/−17 |
| K=16 selected pick − 0.695 system (143) | −0.028 [−0.054, −0.003] | −0.008 | −0.040 | +28/−45 |
| chain oracle − 0.695 chain oracle (143) | +0.018 [−0.002, +0.040] | +0.017 | +0.019 | +33/−21 |

Per-chain trajectories (v3adopt_summary): chain 1 (start 0.668) r1 0.684 → r6 0.689 (+0.021, +22/−11); chain 2 (0.631)
→ 0.677 (+0.046); chain 3 (0.596) → 0.694 (+0.098, +58/−6). With a near-correct start, repair adds little per
chain (the 0.695 run's chain 1 gained +0.131 from 0.537); the value now comes from the 2nd/3rd starts plus the v3 pick.

**Reading.** The new system scores **0.716 (ABC 0.632, Fusion 0.770), the highest real-bench number so far**, but
against the 0.695 system it is **+0.020 with a CI that includes 0** (paired, 143 parts): it does **not significantly beat
0.695**. Most of the RL gain over e55 (+0.13 at the selection stage) is absorbed because repair from a strong
start adds less: +0.050 here vs +0.159 for e55. The two systems end close together. ABC gets the larger (still n.s.) gain, +0.030. The
label-free K=16 pick without repair (0.666) is significantly **below** 0.695 (−0.028), so repair still matters. The
ceiling rose: chain-final oracle 0.740 vs 0.721, and the v3 pick still leaves 0.024 on the table (0.716 vs 0.740).

**Protocol and deviations from the 0.695 run.**
- Part count: 144 here vs 143 there. The 0.695 run lacks `A_00989278_…_step_000_medium` (no e55 start); all paired Δ vs
  0.695 / e55 use the 143 common parts. On that part the primary scores 0.899. Counted as 0 for 0.695, the 144-part
  comparison would be 0.716 vs 0.690.
- Hardware: rp3 served by vLLM on 8 × L40S (ccc0442, TP 2 × DP 4, bf16), not serv-20 B300 DP8. Same weights
  (`runs/rp3-delta-e55/final`), same vr_serve args, 24 workers per chain. The generator ran as an e55 + LoRA
  (`--lora-modules`) on one H200 (ccc0451 GPU 6, inside 11213000), as in the selection study, not as a merged model
  (the grpo_eval K=8 file came from the merged path; its K=8 vote is 0.642 vs 0.627 for the first 8 of the new draws, within sampling noise).
- Chain-1 start IoU is 0.666 in the scored candidates file and 0.668 in vr_serve's re-score. score_partials uses a
  90 s IoU timeout (17 of 2,304 candidates timed out → 0) and vr_serve uses 300 s. All selection-stage numbers use
  the scored file; chain numbers use vr_serve's.
- Verifier = v3b (`runs/v3b-verifier-real-reg/final`), not v5. Distinctness uses the same 0.95 pairwise-IoU rule as
  make_vote_picks.py. All 3 primary chains have 144/144 parts (no vr_serve errors).

**Commands / files** (all under `results/pipeline_grpo/` unless noted):
1. `gen_k16.sh` (overlap step, `sbatch --export=ALL,HOSTJOB=11213000,CMD_FILE=… train_v14/sbatch/grpo_overlap_cmd.sbatch`):
   `gen_openai_bo.py --k 16 --temperature 0.7` (draw 0 greedy, top_p 0.95, 2400 tokens) → `real_k16_ent_t10s120.shard0.json.partial.json`.
   Adapter copied from serv-20 to `runs/grpo_v_ent_t10/adapter_step120`.
2. `sbatch --export=ALL,STEM=results/pipeline_grpo/real_k16_ent_t10s120 train_v14/sbatch/pg_score_rc.sbatch` (ccc0442 CPU):
   score_partials → `real_k16_ent_t10s120.json`; consistency_rerank → `_consistency.json`; render_compare (GT re-render
   F1 0.998) + rc_metric2 → `_rc_v3.json` (sheets in `_rcpng/`).
3. `vscore_k16.sh` (overlap step, ccc0451 GPU 6): sel_vscore.py (v3b) → `vpreds_k16_ent_t10s120.json`.
4. `sel_study.py --spec spec_k16.json --k 8 16` → `sel_k16.json` / `sel_k16_table.txt` (all selectors, incl. e55ctl control).
5. `train_v14/geom/pg_make_starts.py` (new) → `starts_sel_r{1,2,3}.json` (0.666 / 0.630 / 0.594; r2/r3 differ from r1 on 135 parts).
6. `sbatch --gres=gpu:L40S:8 --cpus-per-task=74 --mem=300G --export=ALL,CHAINS_FILE=…/chains_primary.txt,WORKERS=24 train_v14/sbatch/pg_repair_l40s.sbatch`
   (new; no pkill trap, the server is killed by its own process-group id) → `chain_sel_c{1,2,3}.jsonl`.
7. `train_v14/geom/pg_summary.py` (new) → `summary_primary_table.txt`, `summary_primary_per_part.jsonl`;
   cross-check `multistart_combine.py chain_sel_c{1,2,3}.jsonl` → 0.716 / oracle 0.740.
Wall time: generation 16 min (10 min sampling) · scoring + vote + render 40 min · verifier 12 min (in parallel) · repair
job 5 h 05 min (33 min staging venvs/image + loading rp3 from Lustre, 4 h 32 min chains). About 6 h end to end, CPU-bound
in the repair stage (each draw is executed, IoU-scored and rendered).

**SECONDARY, exploratory (run after the primary finished): starts = top-3 distinct by K=16 VOTE** (exact 0.695 start
rule, `make_vote_picks.py` on the same K=16 draws → `starts_vote_r{1,2,3}.json`: 0.632 / 0.611 / 0.603; chains
`chain_vote_c{1,2,3}.jsonl`, `chains_secondary.txt`, job 11216484, 4 h 55 min; table `summary_secondary_table.txt`):
single chain 0.685, **multi-start 0.700 (ABC 0.577, Fusion 0.778)**, chain oracle 0.735. vs 0.695: +0.007 [−0.016, +0.031].
**Primary − secondary (paired, 144): multi-start +0.017 [−0.009, +0.041]** (+32/−24). Single chain +0.004, chain oracle +0.006.
So the selection step gives a small edge that is not significant. Its effect is mostly on ABC (primary 0.632 vs 0.577), where vote starts
lose after repair (secondary ABC −0.010 vs the K=16 selected pick). Vote r1 and the selected r1 are the same draw on only 7/144 parts.
POST-HOC, not pre-declared, 2× repair compute: v3 pick over all 6 chain finals = 0.729 (oracle 0.762), vs 0.695
+0.037 [+0.015, +0.060]. This hints that more diverse starts (6 chains) help, but it was chosen after seeing the data. It needs a
fresh-draw replication before anyone claims it. All result files: `results/pipeline_grpo/summary_table.txt` (both tables).

**Bottom line.** The GRPO generator + selection + rp3 multi-start pipeline reaches **0.716** (best measured,
label-free, pre-declared), **+0.020 [−0.004, +0.044] vs the 0.695 system: a tie within noise, not a significant win.**
RL's large gain at the generation/selection stage (+0.13 over e55) mostly does not carry through repair. Repair
adds +0.050 on top of the RL pick, vs +0.159 on top of e55's.

## Expert-iteration round 2 (Oct 9) — search on training parts → SFT → RL

**Why.** 84% of the best system's remaining real-bench error (0.716) is on parts where no candidate or repair chain gets
close; RL with an IoU reward only re-weights what the policy already samples. So the ceiling has to be raised with NEW
correct programs: search on TRAINING parts selected by ground truth, then SFT (stable; round 1 `rft1`), then short RL.
Everything under `results/cycle2/` (cluster) and `serv-20:/srv/scratch/bimrose2/cycle2/`.

**Search policy = rft1_rl2 step 120** (RL after round-1 SFT). Chosen on the real bench (model selection, not the final
test): s120 mean-cand 0.621 / oracle 0.714 / vote 0.655; s200 0.625 / 0.711 / 0.654 (paired s200−s120: mean +0.003
[−0.006,+0.013], oracle −0.003 [−0.015,+0.009]) → tie; s120 kept for the higher oracle (diversity matters for search).
Merged into e55 → `serv-20:runs/merged_cyc2_c2pol` (served as `c2pol`).

**Search set (training parts only; hard error on any held-out file_id, 146 checked, 0 hits; `results/cycle2/prep_keys.py`).**
CADBench hard universe = c4 (real4_hard ∪ bankv2_c4 ∪ e55-bo8 max ≤ 0.1, 2,310) + c2 (c2_hard ∪ bankv2_c2 ∪
unsolved_rft_corpus2_dw423, 1,071) + c1 (keys_c1 ∪ unsolved_rft_corpus_dw423, 1,117):
- A = no ≥0.75 program in the round-1 tier: c4 1,116, c2 530, c1 993 (2,639);
- C = round-1 tier program < 0.9: c4 568, c2 330, c1 84 (982);
- B = realpool2_hard_4500 (DeepCAD; never in a tier).
Total 8,121 parts.

**Stage 1: K=16 policy samples** (draw 0 greedy + 15 at T 1.0 / top_p 0.95, 2400 tokens = round 1; vLLM DP3 on serv-20
GPUs 1,2,5, 1 h 35 min for 129,920 candidates; `gen_driver.sh`). Scored vs GT on ccc0442 (venv in /dev/shm; Lustre
imports made it I/O-bound at 2 cands/s) + serv-20 (realpool2), exec 60 s / IoU 90 s, `--accept 0` (exact IoU, no
volume-bound shortcut) — ~5 h, the binding cost of the whole search (`score_loop.sbatch`, `score_s20.sh`).

| set | parts | exec | draw-0 | mean | best-of-16 | ≥0.75 | NEW ≥0.75 vs round-1 tier | NEW vs all earlier samples* |
|---|---|---|---|---|---|---|---|---|
| A_c4 | 1,116 | 0.990 | 0.395 | 0.390 | 0.498 | 81 | 81 | 72 |
| A_c2 | 530 | 0.994 | 0.488 | 0.477 | 0.608 | 149 | 149 | 54 |
| A_c1 | 993 | 0.989 | 0.468 | 0.460 | 0.584 | 253 | 253 | 142 |
| B_rp2 | 4,500 | 0.987 | 0.590 | 0.579 | 0.747 | 2,557 | 2,557 | 1,021 |
| C (c4/c2/c1) | 982 | 0.99 | 0.69 | 0.67 | 0.80 | 776 | – | – |
\* e55 best-of-32 (c1, c2) / best-of-8 (c4, realpool2), round-1 RL K=16 (c2, c4), realpool2 RL K=4 mining draws.

**Stage 2: GT-selected rp3 repair search** (`geom/gt_search2.py` = gt_search.py with several benches in one worker pool
and a global priority queue; rp3 K=8 repairs/round, ≤ 4 rounds, patience 2, adopt by true IoU — round-1 bank-v2
settings). Starts = best known program (K=16 / round-1 tier / bank). Priority: no-tier parts first, start band
[0.5,0.75) → [0.3,0.5) → … The CADBench pool ran on ccc0442 (rp3 TP2×DP4 on 8 L40S, 68 workers; GPU-bound),
realpool2 on serv-20 (rp3 on GPUs 2,5 + 4, 36 workers). **Stopped after the [0.3,0.5) band** (deviation, for time: the
0.75–0.9 band only polishes parts that already have a program, and rp3 yields ~0 below 0.3).
DeepSeek-V4.1-Flash teacher (lab hub, x-hub-user bimrose2, ≤ 32 in flight; `geom/vis_repair_gt.py --arm vis --adopt gt`,
3 rounds) on the parts whose best start was < 0.3.

| search | parts | improved (>+0.01) | crossed 0.75 | mean gain |
|---|---|---|---|---|
| rp3, CADBench, start 0.5–0.75 | 1,192 | 343 | 124 (10%) | +0.023 |
| rp3, CADBench, start 0.3–0.5 | 610 | 228 | 8 (1.3%) | +0.037 |
| rp3, realpool2, start 0.5–0.75 | 1,396 | 731 | 406 (29%) | +0.068 |
| rp3, realpool2, start 0.3–0.5 | 398 | 237 | 47 (12%) | +0.111 |
| DeepSeek, CADBench, start < 0.3 | 353 | 117 | 2 | +0.04 |
| DeepSeek, realpool2, start < 0.3 | 145 | 64 | 16 | +0.145 |
617 programs beat their start and reached ≥ 0.75 (rp3 599, DeepSeek 18) → rationalized by the policy itself
(`build_guide_bank.py` with c2pol; 617/617 kept, 0 leaks).

**Tier 2** (`geom/build_rft2_tier.py` → `results/cycle2/tier2/`): per part the best of {K=16 sample (own think), search /
teacher program (rationalized), round-1 tier row}, IoU ≥ 0.75, ties → own sample; round-1 rows of parts not resampled
(tier ≥ 0.9) carried over. **5,502 rows, mean IoU 0.884, 2,455 ≥ 0.9** (round 1: 1,859 / 0.891 / 877). Sources: own
samples 3,516, round-1 rows 1,369 (877 carried + 492 kept), search/teacher 617. Round-1 rows improved by round 2: 462.
**Capability expansion — parts that now have a ≥0.75 program and had none in the round-1 tier: 3,643** (CADBench 617,
realpool2 3,026); **vs every earlier sample of every model: 1,792** (CADBench 388, realpool2 1,404). By family
(new vs tier1 / vs all): ABC (A) 160 / 115, Fusion (F) 192 / 121, CADBench-DeepCAD (B) 202 / 108, E 63 / 44,
realpool2 DeepCAD (D) 3,026 / 1,404. Of the 617 CADBench new parts, 148 came from search (rp3/DeepSeek), 469 from K=16.

**SFT `rft2`** (`results/cycle2/c2-rft2.yaml`; round-1 recipe): LoRA warm start from rft1_rl2 adapter_step120 on e55,
lr 2e-5 cosine → 2e-6, warmup 3%, global batch 16 (serv-20 4×B300 DDP: 2 × 2 accum × 4), max_seq 5120. Mix
(`build_mix2.sh`, `assemble_mix2.sh`): tier ≈ 50% of draws as in round 1, but split CADBench 2/3 (2,476 rows × 11) :
realpool2 1/3 (3,026 rows × 5) so the DeepCAD idiom does not swamp CADBench (declared before training); same 13 e55
replay shards (24,887 rows). 955 steps = 2 epochs over the CADBench rows (~1 over realpool2), 3.3 s/step, 55 min.
Token loss 0.23 → ~0.19.

**SFT real bench** (144 parts, K=8 serv-20 daemon; vote clean, 1,094/1,094 re-executed; `results/cycle2/eval_table.py`):

| model | vote | draw-0 | first-exec | mean-cand | best-of-8 | exec |
|---|---|---|---|---|---|---|
| e55ctl | 0.516 | 0.390 | 0.466 | 0.396 | 0.593 | 0.788 |
| rft1 (round-1 SFT) s20 | 0.624 | 0.560 | 0.588 | 0.545 | 0.699 | 0.923 |
| ent_t10_s120 | 0.639 | 0.615 | 0.619 | 0.600 | 0.699 | 0.984 |
| rft1_rl2_s120 (search policy) | 0.655 | 0.618 | 0.627 | 0.621 | 0.714 | 0.988 |
| **rft2 (round-2 SFT)** | 0.649 | 0.612 | **0.636** | 0.589 | **0.724** | 0.950 |
| rft2 − e55ctl | +0.133 [+0.099,+0.170] | +0.222 | +0.169 | +0.194 | +0.131 [+0.103,+0.161] | +0.161 |
| rft2 − rft1 | +0.026 [−0.000,+0.054] | +0.051 [+0.008,+0.093] | +0.048 [+0.015,+0.080] | +0.044 [+0.026,+0.064] | **+0.025 [+0.012,+0.040]** | +0.027 |
| rft2 − rft1_rl2_s120 | −0.005 [−0.027,+0.015] | −0.007 [−0.043,+0.030] | +0.008 [−0.018,+0.035] | **−0.032 [−0.049,−0.017]** | +0.010 [−0.002,+0.023] | −0.038 |
| rft2 − ent_t10_s120 | +0.010 [−0.017,+0.036] | −0.003 | +0.017 | −0.011 | **+0.025 [+0.007,+0.044]** | −0.034 |

Reading: the same consolidation pattern as round 1. The round-2 SFT keeps the vote of the policy it started from
(n.s.) and reaches the **highest best-of-8 of the campaign (0.724)**. Paired vs the search policy that gain is
+0.010 and not significant; vs rft1 and ent_t10 it is +0.025 and significant. Mean candidate and exec drop (−0.032 /
−0.038), as in round 1 (the 50% e55 replay pulls toward e55). The round-1 cycle needed the following RL to turn the
re-opened diversity into mean/vote gains, so the verdict on round 2 waits for `rft2_rl`.

**RL round 2 `rft2_rl`** (serv-20 GPU 2, vLLM :8440, `cycle2/after_sft.sh`): `--adapter runs/rft2_from_rl2/final
--start-step 0`, lr 1e-5 (mature-adapter rule), T 1.0 scaled logits, top_p 1, batch-std adv, 4 minibatches, KL 0,
guard 0.6, `--ent-coef 0.1 --ent-target 0.1829` (pinned = rft1_rl2) `--ent-max 0.35`, pool2 (real4 + c2 + family hard +
realpool2_hard_4500), 300 steps, adapters every 10. ~4.8 min/step. Steps 0–6: exec 0.89–0.93, entropy 0.20–0.26,
clipfrac ≤ 0.004 (no drift). serv-20 `results/grpo_eval/ARMS` now starts `rft2 rft2_rl ...` (backup `ARMS.bak_c2`), so
s20/s60/s120/s200 are evaluated automatically and the cluster vote loop (job 11236971, ends Oct 10 ~23:00) adds votes.

**Deviations / notes.**
- Search stopped after the [0.3,0.5) start band on both pools (see above). The cluster pool's phase-1 stream
  (A_c4, 13 workers, 198 parts) was merged into phase 2. Duplicates between the two serv-20 realpool2 instances: none
  (disjoint bands, instance 1 stopped at the band edge). In-flight parts lost at the stops (~70 + ~20) were not retried.
- Rationalization used the search policy (c2pol), not e55 base as in round 1 (STaR with the current model; its plans
  have the same length/format as the K=16 own traces: median 620 vs 635 chars).
- Tier-2 SFT mix weights realpool2 at 1/3 of the tier draws (declared before training, see the mix).
- Round-1 C parts (tier program < 0.9) were resampled at K=16 but not searched. The round-1 bank entries that beat the
  K=16 draws served as search starts (src bank1, 306 parts).
- `score_partials.py --accept 0` for every stage-1 score (exact IoU; the default 0.8 volume bound would record an upper
  bound for sub-0.8 candidates).
- serv-20 load average reached 150–220 at times during the search, while `top` showed the CPUs 85–96% idle (short-lived
  scoring subprocesses). After 07:10 the search ran at ≤ 36 workers there.

**Files / commands** (cluster `results/cycle2/`, serv-20 `cycle2/`): `prep_keys.py` → `keys/` · `gen_driver.sh
runs/grpo_v_rft1_rl2/adapter_step120 c2pol` (serv-20) · `score_loop.sbatch` (TAG=c2pol, SETS=CADBench) + `score_s20.sh
B_rp2` → `gen/<set>_c2pol.json` · `k16_stats.py` → `k16_stats.json` · `build_starts.py`, `make_keys_all.py` →
`search/starts_*.json`, `keys_all.txt` · `gts_l40s.sbatch` (rp3 server, job 11237896) + `gts_phase2.sbatch` (job 11238260,
`geom/gt_search2.py`) → `search/gts_c4_p1.jsonl`, `gts_all.jsonl` · serv-20 `rp2_search.sh`, `rp2_search_b.sh` →
`search/gts_rp2{,b}.jsonl` · `ds_teacher.sh` (`geom/vis_repair_gt.py`) → `teacher/ds_*.jsonl` · `collect_search.py` →
`search/targets_*.json`, `search_stats.json` · serv-20 `rationalize.sh` → `search/bank_*.json` · `build_tier2.sh`
(`geom/build_rft2_tier.py`) → `tier2/` (`tier_stats.json`, `new_keys.json`) · `build_mix2.sh` → `tier2_{cad,rp2}/shards`,
`MIX_INFO` · serv-20 `assemble_mix2.sh` → `cycle2/mix` · `train_sft_s20.sh c2-rft2.yaml` (4 GPUs, `configs/accelerate_ddp_2gpu.yaml`
also added) → `serv-20:runs/rft2_from_rl2/final` (+ copy `runs/grpo_v_rft2/adapter_step20`) · `after_sft.sh` (ARMS +
rft2_rl launch). Wall clock: search 01:43–10:21 (stage 1 01:54–07:17, stage 2 04:31–10:21), tier/rationalize 10:21–10:30,
SFT 10:31–11:26, eval 11:32–12:05.

**Next (step 6, not started): retrain the repairer on the new generator's failures.** The data exists: 1,734
GT-improved repairs from this search (rp3 1,553 + DeepSeek 181; start = a policy program, target = the adopted program,
true IoU gain). Plan for `rp4`: rp3 warm start. Rows = (a) those pairs (target sheet + start-program sheet + start
code → adopted code), re-rendering each start program (~1.7k draftwright renders); (b) within-part self-repair pairs
from the K=16 draws, e.g. an executing draw at IoU 0.3–0.7 → the part's best draw (≥ 0.75, gain ≥ 0.15), one per part,
CADBench first (~1–2k); (c) ~50% replay of rp3's rows. Eval = the in-house loop protocol (vr_serve, v3-gated, margin
0.1) on the real bench, starting from the new generator's label-free K=16 picks, rp4 vs rp3 on the same starts. Run the
full end-to-end pipeline only after the user agrees.

### Round 2, continued (Oct 9 evening): RL s20/s60, repairer rp4c2, seed replicate, end-to-end run

**RL `rft2_rl` real bench** (votes clean: s20 1,127/1,127, s60 1,128/1,128):

| model | vote | draw-0 | first-exec | mean-cand | best-of-8 | exec |
|---|---|---|---|---|---|---|
| rft1_rl2_s120 (search policy) | 0.655 | 0.618 | 0.627 | 0.621 | 0.714 | 0.988 |
| rft2 (SFT) | 0.649 | 0.612 | 0.636 | 0.589 | 0.724 | 0.950 |
| **rft2_rl s20** | 0.664 | **0.638** | **0.648** | 0.622 | **0.740** | 0.978 |
| **rft2_rl s60** | **0.673** | 0.631 | 0.645 | **0.626** | 0.732 | 0.979 |
| s60 − rft1_rl2_s120 | **+0.019 [+0.001,+0.038]** | +0.013 | +0.018 | +0.005 | **+0.018 [+0.004,+0.034]** | −0.009 |
| s60 − ent_t10_s120 | **+0.034 [+0.013,+0.056]** | +0.017 | +0.026 | +0.026 | +0.033 | −0.004 |
| s20 − rft1_rl2_s120 | +0.009 [−0.008,+0.027] | +0.019 | +0.021 | +0.000 | **+0.026 [+0.012,+0.040]** | −0.010 |

Round 2 pays off after the short RL: vote 0.673 and best-of-8 0.740 are campaign highs, and the vote gain over the round-1
policy is significant (borderline). RL steps 0–110: entropy 0.20–0.26, no drift. s120 / s200 evaluate automatically.

**Repairer `rp4c2` (step 6).** Data (`results/cycle2/rp4/make_rp4_pairs.py`): target = best known program per training
part (tier-2 row, else a search/teacher best ≥ 0.6); inputs ≤ 2 executing programs ≥ 0.1 below it: the GT-search start
and the highest-IoU K=16 near miss of the new policy. CADBench 2,137 pairs, realpool2 capped at 2,140 →
4,277 rows (`pack_repair_shards.py`, renders on ccc0442). Only 141 CADBench pairs came from search starts: most search gains are < 0.1.
Training: a full fine-tune of rp3 on 2 B300 (FSDP2 2 ranks) ran at 150 s/step (memory thrash) and was stopped. Used instead:
LoRA r64 on rp3's weights, lr 2e-5, 200 steps × 64 (2-GPU DDP), rp3's mix + the new tier at ½ of RFT draws (×60),
2 h 09 min (`results/cycle2/rp4/rp4c2-lora-rp3.yaml`), merged → `runs/rp4c2-merged` (cluster + serv-20).
Eval = one repair chain, the 0.716 protocol (vr_serve, K=16 × 6 rounds, v3 gate margin 0.1, max 6000 tokens), from the
label-free top-1 start (v3b-EV + v3 over K=16 draws of rft2_rl s20), 4 L40S per repairer:

| chain 1 from rft2_rl s20 pick | mean | ABC | Fusion | ≥0.85 |
|---|---|---|---|---|
| start (selected pick) | 0.697 | 0.607 | 0.754 | 40% |
| rp3 | **0.721** | 0.631 | 0.779 | 45% |
| rp4c2 | 0.715 | 0.626 | 0.772 | 45% |
| ref: 0.716 system's chain 1 (ent_t10 s120 start 0.668) | 0.689 | 0.593 | 0.750 | 42% |

rp4c2 − rp3: **−0.006 [−0.019, +0.006]** (+10/−13) → **rp4c2 does not help**; repair on top of the stronger starts adds
+0.019 (rp4c2) / +0.025 [+0.010,+0.041] (rp3). rp3 single chain − 0.716's chain 1: +0.032 [+0.011, +0.054] (better
generator start: +0.029). The single rp3 chain on the round-2 generator (0.721) already matches the 0.716 three-chain system.

**Seed replicate `ent_s2`** (ent_t10 args, `--seed 2`, serv-20 GPU 7; GPU 3 stays the eval daemon). This is the third seed;
`ent_s1` (seed 1, Oct 8) already exists. Real bench, s60: draw-0 ent_t10 0.538 / ent_s1 0.525 / ent_s2 0.533; mean-cand 0.537 /
0.526 / 0.534; best-of-8 0.665 / 0.638 / 0.662; vote ent_t10 0.589 / ent_s1 0.571. s120: ent_t10 d0 0.615 / vote 0.639;
ent_s1 d0 0.582 / vote 0.610. ent_s2 s120 is pending; the run stops at step 130.

**End-to-end pipeline (user-approved), driver `results/cycle2/pipeline/e2e_driver.sbatch` (job 11255570).** Rules fixed
before their inputs existed:
- repairer = rp4c2 only if it beat rp3 on chain 1 → **rp3**;
- generator = rft2_rl s60 vs s120 by higher vote, |Δ| < 0.005 → by best-of-8;
- then K=16 → scoring/vote/render-compare → v3b-EV verifier → top-3 distinct starts → 3 rp3 chains on 8 L40S → multi-start
  v3 pick, paired vs the 0.716 and 0.695 systems (`summary_e2e_<gen>.txt`).

Notes:
- The verifier for s60/s120 runs on serv-20 GPU 4 (e51 base copied there). Its preds correlate 0.9999 with the cluster run
  (mean |Δ| 0.003); top-1 picks agree on 132/144 parts (near-ties), start mean 0.690 vs 0.691.
- ccc0442 jobs now link a persistent RAM-staged venv (`/dev/shm/bimrose2/c2stage`, `pipeline/stage_shm.sh`); staging from
  Lustre took 20–40 min per job.

### rft2_rl collapse: diagnosis and follow-up arms (Oct 9, 23:40)

**What happened.** rft2_rl exec 0.98 → 0.78 (s80) → ~0.6 (s110+). Entropy stayed flat at 0.22–0.25, so this was not
an entropy collapse. The guard rolled back to an already-degraded s110 and the coordinator stopped the run at 22:35.
s120 real bench: exec 0.679, d0 0.433. **s60 stays the pick**; the e2e driver uses it (vote s60 0.673 vs s120 0.665).

**Diagnosis** (`results/cycle2/diag/`). `diag_rl.py`: 120 training-pool parts (30 per bench) × 4 completions per
checkpoint at the rollout setting (T 1.0, top_p 1.0, 2400 tokens), raw text kept, each program executed.

| ckpt | exec | no extractable code (stop) | no code (length) | real exec errors | finish = length |
|---|---|---|---|---|---|
| s60 | 0.975 | 0.6% | 0 | ~2% | 0% |
| s80 | 0.573 | 40% | 0 | ~2% | 0.4% |
| s100 | 0.710 | 24% | 2% | ~2% | 4% |
| s120 | 0.660 | 27% | 4% | ~2% | 36% |

- **Not realpool2:** at s80 exec by pool is family 0.41, c2 0.58, c4 0.62, realpool2 0.69.
- **The failure is formatting, not CAD:** the program is written, then extra fences follow (a second, often empty
  ```python block, or a repeated closing fence). Later checkpoints run on to the token limit.
- **Why RL cannot correct it:** `grpo_round.py` parses each vLLM rollout to (think, code) (text after the last
  "```python") and rebuilds the training sequence in the canonical one-block form (`collate_v14.wrap_python`). Completions
  without parsable code are skipped ("nothing to reinforce"). So the sampled fence tokens are never in the loss and their
  reward 0 never gives a gradient. When stray fences end up inside the parsed code, the trainer penalizes a *cleaned* copy
  of the code instead.
- **This is a training/sampling mismatch at the format level.** It drifts at any lr.

**Retro check of earlier collapses** (`diag/retro_nocode.py`, `diag/retro_nocode.txt`; the parser's no-code share is a
lower bound on fence failures):
- mix_b32: s130–199 no-code 37 → 98% of all samples.
- gt10 / gt10_np32 / gt10_mb8: onsets at s20–50 with no-code 16–39%, 53–73% of failures.
- guide_mb8b: s70 33%. guide_lr4e5: 19–23% at s80–129.
- rft2_rl s70–89: 61–77% of failures.
- ent_hi, dense_t10, gfrom_t10: 5–12%, weaker.
- **The format blind spot is a plausible common cause of the campaign's late collapses, including the guided ones.** The
  "found answers belong in SFT, not RL" claim is confounded until g2_guided vs g2_guided_raw is in.

**Trainer changes** (opt-in; defaults reproduce old behaviour; serv-20 backups `grpo_round.py.bak_1009c2{,b}`,
`collate_v14.py.bak_1009c2`):
- `--train-raw`: train on the exact sampled answer text (`collate_v14` `content_raw`), including no-code completions.
- `--guard-abs X`: a rollback target needs rolling and latest exec ≥ X.
- `--kl-ref-adapter DIR`: KL to a frozen adapter, e.g. the SFT start, instead of e55.

**Follow-up arms** (serv-20; all in `results/grpo_eval/ARMS`; daemon STEPS include 20/60/120). Shared:
`--minibatches 4 --scale-logits --adv batchstd --temperature 1.0 --top-p 1.0 --ent-coef 0.1 --ent-target 0.1829 --ent-max 0.35
--lr 1e-5 --guard 0.85 --guard-abs 0.9 --save-every 10`, seed 0.

| arm | GPU | start | pool | difference |
|---|---|---|---|---|
| rft2_kl | 4 | rft2 | pool2 | KL 0.02 to the frozen rft2 adapter (step-0 KL 0.0004) |
| rft2_raw | 5 | rft2 | pool2 | `--train-raw` (the diagnosed fix), KL 0 |
| g2_guided | 6 | rft1_rl2 s120 | pool2 + 498 bank parts | guided: 4,133 round-2 tier rows (own K=16 bests + 617 search/teacher) as injected completions, 130 steps ≈ rft2 SFT + RL-to-s60 GPU-hours |
| g2_guided_raw | 0 (after e55_t2's SFT) | rft1_rl2 s120 | same | g2_guided + `--train-raw` |
| e55_t2 → e55_t2_rl | 2+0 SFT, then 2 | e55, fresh LoRA | rft2's mix | data-vs-compounding: SFT on the same tier-2 mix (955 steps, lr 2e-5), then the rft2_raw RL recipe to s130 |

Launchers: `cycle2/after_e55t2.sh`, `cycle2/after_e55t2_b.sh` (serv-20). Banks: `results/cycle2/guided/`
(`guided_stats.json`).

### Follow-up results (Oct 10, 04:10): end-to-end, seeds, first s60s

**End-to-end (pre-declared driver, job 11255570).** Repairer rp3 (rp4c2 lost on chain 1). Generator rft2_rl s60 (vote 0.673 vs
s120 0.665). K=16 → v3b-EV + v3 top-3 distinct starts → 3 rp3 chains (16 × 6, margin 0.1) → multi-start v3 pick.
`results/cycle2/pipeline/summary_e2e_rl2s60.txt`:

| | mean | ABC | Fusion | ≥0.85 |
|---|---|---|---|---|
| start (selected pick) | 0.696 | 0.612 | 0.750 | 41% |
| chain 1 | 0.706 | 0.629 | 0.754 | 44% |
| **multi-start (round-2 system)** | **0.714** | 0.635 | 0.764 | 45% |
| 0.716 system (Oct 8) | 0.716 | 0.632 | 0.770 | 44% |

- e2e − 0.716: **−0.003 [−0.025, +0.021]** (+27/−29) → a tie.
- e2e − 0.695: +0.017 [−0.006, +0.039] (n.s.).
- e2e − its start: +0.018 [−0.001, +0.036].
- **Reading:** the stronger generator raises the selected start by +0.028 over the 0.716 run's start, but the repair stage then
  adds less. The system number does not move (~0.71–0.72 plateau). Chain-1 run-to-run noise is about ±0.015: rp3 chain 1
  on rft2_rl s20 picks with a start of the same quality gave 0.721.

**Seed replicates of ent_t10 (e55 → GRPO, identical args).** Real bench at s120, seeds 0 / 1 / 2:
- draw-0 0.615 / 0.582 / 0.562 (mean 0.586, SD 0.027);
- mean-cand 0.600 / 0.584 / 0.567;
- vote 0.639 / 0.610 / 0.594 (mean 0.614, SD 0.023);
- best-of-8 0.699 / 0.687 / 0.651.

**The paper's headline ent_t10 is the best of 3 seeds. Report the seed mean (d0 0.586, vote 0.614) or all three.**

**Follow-up arms, first evals** (real bench 144; votes clean):

| arm | ckpt | vote | d0 | mean | best-of-8 | exec |
|---|---|---|---|---|---|---|
| rft2 (SFT) | — | 0.649 | 0.612 | 0.589 | 0.724 | 0.950 |
| rft2_rl (collapsed later) | s60 | 0.673 | 0.631 | 0.626 | 0.732 | 0.979 |
| rft2_kl (KL to rft2, k3 clamp 20) | s20 | 0.646 | 0.622 | 0.611 | 0.723 | 0.975 |
| rft2_raw (`--train-raw`) | s20 | 0.644 | 0.624 | 0.610 | 0.707 | 0.984 |
| rft2_raw | s60 | pending | 0.626 | 0.629 | 0.725 | **0.995** |
| g2_guided (guided GRPO from rft1_rl2 s120) | s20 | 0.654 | 0.613 | 0.619 | 0.718 | 0.984 |
| g2_guided | s60 | pending | 0.639 | 0.632 | 0.721 | 0.988 |
| g2_guided_raw | s20 | 0.647 | 0.622 | 0.622 | 0.710 | 0.988 |
| e55_t2 (fresh LoRA on the tier-2 mix) | SFT | 0.660 | 0.602 | 0.597 | 0.724 | 0.957 |
| e55_t2_rl (`--train-raw`) | s20 | 0.668 | 0.637 | 0.615 | 0.725 | 0.977 |

Paired at s60, all n.s.:
- g2_guided − rft2_rl s60: d0 +0.008, mean +0.005, best-of-8 −0.012 [−0.028, +0.003].
- rft2_raw − rft2_rl s60: mean +0.003, best-of-8 −0.007, exec +0.016 [+0.006, +0.026].
- e55_t2 − rft2 (SFT stage): vote +0.011, d0 −0.009, mean +0.008, best-of-8 −0.001.

Reading so far:
1. **Data vs compounding:** at the SFT stage, training e55 directly on the final dataset matches the round-structured rft2.
2. **SFT vs guided RL:** at matched compute, guided GRPO (s60, no collapse with the new guard) matches the SFT→RL path. There is no
   evidence yet that the found answers need SFT.
3. **Stability:** `--train-raw` gives the highest exec. Whether it prevents the collapse is the s120 question.

rft2_kl's k3 KL estimator (clamp 20) produced per-step spikes from step 34 (368 → 11,727 → 455,340) that dominated the loss,
and exec slipped to 0.94. The arm was stopped at s46. It was replaced by **rft2_kl2** (`--kl-clamp 5`, new opt-in flag,
serv-20 GPU 0, launched 03:00). A seed replicate of the fix, **rft2_raw_s1** (`--seed 1`, GPU 4), was added.
CPU pinning: arms moved off the cores of the separate CADFit run (120–159, 200–231).

## Bench B + baselines (Oct 10)

**Purpose.** Confirm the final generator picks on a real-part bench that no checkpoint was ever selected on. Also run the
two end-of-campaign baselines the user asked for on 2026-10-07: vanilla DeepSeek-V4.1-Flash best-of-8 in the T0
short-reasoning regime, and off-the-shelf Qwen3.8-27B with no fine-tune. Everything is under `results/bench_b/`
(README.md = construction + exclusion evidence; tables.md = every table with CIs; `summarize.py` regenerates it).

**Bench B (frozen 2026-10-09 23:52, before any model saw it).**
- 280 parts: **171 Fusion 360 + 109 ABC**, the 144 bench's 61/39 mix.
- Path: `results/bench_b/bench`, symlinked as `train_v14/mech/benchmarks/data/bench_b`; serv-20 copy `mech_benchmarks/bench_b`.
- Read-only. `FROZEN` holds the sha256 of the keys (`a32a8c6a…`), the eval cache (`9266e280…`) and the manifest.
- The 280 file_ids were appended to `data/heldout_file_ids.txt` (146 → 426 lines), so `build_rft{1,2}_tier.py`,
  `prep_keys.py`, `pack_scored_real.py` and `build_corpus.py` now reject them.
- Source: CADBench is exhausted, so bench B comes from the datasets CADBench sampled from. Fusion 360 Gallery
  segmentation s2.0.1 extended STEP: CADBench benchF ids are exactly its `<project>_<hash>_<n>` names. ABC STEP chunks
  0042/0043.
- Construction is the 144 bench's: `prep_external_parts.py --max-faces 80` (1 solid, analytic only, 6–80 faces,
  aspect ≤ 15, fill ≥ 0.05, 80 mm), then draftwright 0.4.23 + font patch via `render_isolated.sh` (permissive, **no
  fallback**: 377/383 rendered, 0 legacy; the 6 failures are logged verbatim in `render_failures.json`), then
  `build_ext_eval_cache.py`. Underdetermined sheets are kept.
- Selection rule:
  - one body per Fusion design; one part per ABC model id and per Onshape hash;
  - signature near-duplicate check (same face count + surface-type census, sorted bbox ratios and fill within 0.01) vs
    114,072 used parts, and within bench B: 47 + 62 dropped;
  - 4 face-count strata per family at the 144 bench's quartiles, quotas proportional to its counts
    (F 52/39/41/39, A 29/26/29/25), seeded rank inside each stratum.
- Result vs the 144 bench:

  | | faces p10/50/90 | fill p50 | underdetermined |
  |---|---|---|---|
  | F, 144 bench | 8/14/33 | 0.39 | 31% |
  | F, bench B | 9/14/33 | 0.46 | 32% |
  | A, 144 bench | 38/48/62 | 0.32 | 46% |
  | A, bench B | 38/48/67 | 0.31 | 50% |

  e55ctl scores the same on both benches (mean-cand 0.385 vs 0.396, vote 0.509 vs 0.516), so the difficulty matches.
- Exclusions, reusing the round-2 146-id leak check widened to every id source:
  - all 28 `data/*/manifest.json`, which cover CADBench corpora 1–4, the abccode corpora, `rft_realpool_v2` (realpool2 /
    realpool2_hard_4500), the DeepCAD gate, the 144 bench and its variants, and repair_bench_e55;
  - `deepcad/corpus_full`;
  - all 18,000 CADBench inventory rows;
  - the full 215,094-id DeepCAD list (DeepCAD ids are ABC ids);
  - a token scan of 3,443 key/tier/bank/pool files: `results/` (cycle2 keys/tier2/rp4/search/teacher, guide banks,
    h6c hard keys, grpo_eval), serv-20 `fp/` + `cycle2/` (RL arm key lists, guided banks), every repo-root `rft_*` tier
    including the repairer tiers `rft_repair_c1–c4/deepcad`, and the dsv41 tiers.
  - Totals: 2,225 Fusion designs, excluded at design level (19,984 bodies removed); 221,564 ABC/DeepCAD ids;
    5,379 Onshape hashes.
  - Post-freeze `leakcheck` result: **0 overlaps, 0 near-duplicates, no repeated design → CLEAN** (`leakcheck.json`).

**Protocol** (= results/grpo_eval). K=8: draw 0 greedy + 7 at T 0.7 / top_p 0.95, think, 2,400 tokens, `gen_openai_bo.py`,
vLLM DP=1 on **serv-20 GPU 7** (after ent_s2's trainer exited at 23:42). Adapters were merged into e55 exactly as in
`grpo_eval.sh` (`runs/merged_bb_*`). Scoring: `score_partials.py` with 16 workers, exec 60 s, IoU 90 s, default
`--accept 0.8`, then `consistency_rerank.py`. Every vote is clean (re-executed = executed for all 10 new files). Tables come
from `eval_table.py` (new `--prefix/--dir` flags) with the 2,000-sample paired bootstrap.
- Deviation 1: the bench-B jobs ran vLLM with `--enforce-eager`. At load ~340, CUDA-graph capture took > 30 min and the
  first e55ctl server never came up. Weights and sampling are unchanged, and all four bench-B generators share this path.
- Deviation 2: rft2_rl_s60 and ent_t10_s120 were scored on ccc0442 (`sbatch/bench_b_score.sbatch`, same settings), the
  rest on serv-20.

**Bench B, the four generators (n=280; Δ vs e55ctl):**

| model | vote | draw-0 | first-exec | mean-cand | best-of-8 | exec |
|---|---|---|---|---|---|---|
| e55ctl | 0.509 | 0.402 | 0.461 | 0.385 | 0.595 | 0.799 |
| ent_t10_s120 | 0.640 | 0.625 | 0.629 | 0.611 | 0.696 | 0.986 |
| rft1_rl2_s120 | 0.651 | 0.628 | 0.632 | 0.624 | 0.708 | 0.990 |
| **rft2_rl_s60** | **0.665** | 0.625 | **0.641** | 0.624 | **0.732** | 0.980 |
| rft2_rl_s60 − e55ctl | +0.155 [+0.134,+0.178] | +0.223 [+0.192,+0.254] | +0.180 [+0.156,+0.204] | +0.238 [+0.218,+0.258] | +0.136 [+0.119,+0.155] | +0.182 |
| rft1_rl2_s120 − e55ctl | +0.141 [+0.121,+0.162] | +0.226 | +0.171 | +0.239 | +0.113 [+0.097,+0.131] | +0.191 |
| ent_t10_s120 − e55ctl | +0.131 [+0.110,+0.153] | +0.223 | +0.168 | +0.225 | +0.101 [+0.083,+0.120] | +0.188 |
| **rft2_rl_s60 − rft1_rl2_s120** | **+0.014 [+0.003,+0.025]** | −0.003 [−0.022,+0.017] | +0.009 [−0.008,+0.025] | −0.000 [−0.010,+0.009] | **+0.023 [+0.014,+0.032]** | −0.009 [−0.018,−0.001] |
| **rft2_rl_s60 − ent_t10_s120** | **+0.024 [+0.008,+0.041]** | +0.000 [−0.023,+0.023] | +0.012 [−0.006,+0.031] | +0.013 [−0.001,+0.027] | **+0.035 [+0.023,+0.049]** | −0.006 [−0.016,+0.005] |

The same contrasts on the 144 bench, unchanged:

| contrast (144 bench) | vote | best-of-8 |
|---|---|---|
| rft2_rl_s60 − rft1_rl2_s120 | +0.019 [+0.001,+0.036] | +0.018 [+0.003,+0.034] |
| rft2_rl_s60 − ent_t10_s120 | +0.034 [+0.013,+0.055] | +0.033 [+0.015,+0.054] |

**Reading: rft2_rl_s60's advantage replicates on bench B.**
- It is again the best model on vote (0.665) and best-of-8 (0.732, identical to the 144 bench).
- The ranking is unchanged: rft2_rl_s60 > rft1_rl2_s120 > ent_t10_s120 > e55.
- Its edge over the round-1 search policy is significant on both benches and of similar size: vote +0.014 vs +0.019,
  best-of-8 +0.023 vs +0.018. Bench B's CIs are about half as wide.
- Mean-cand and draw-0 tie the round-1 policy on both benches. So the round-2 gain is in the candidate *set* (ceiling
  and vote), not in single draws, which matches the round-2 SFT reading.
- Every model's gain over e55 on bench B is within 0.01–0.02 of its 144-bench value. Selection on the 144 bench did
  not overfit.
- Per family (bench B), rft2_rl_s60 vs e55ctl, vote: Fusion 0.726 vs 0.570, ABC 0.569 vs 0.414. ABC remains the gap.

**Baselines** (Δ vs e55ctl; all CIs exclude 0):

| model | bench | vote | draw-0 | first-exec | mean-cand | best-of-8 | exec | Δvote vs e55ctl | Δvote vs rft2_rl_s60 |
|---|---|---|---|---|---|---|---|---|---|
| vanilla DeepSeek-V4.1 T0 (≤ 3 calls) | 144 | 0.375 | 0.311 | 0.338 | 0.315 | 0.470 | 0.928 | −0.141 [−0.198,−0.083] | −0.298 [−0.349,−0.245] |
| vanilla DeepSeek-V4.1 T0 (≤ 3 calls) | B | 0.393 | 0.315 | 0.336 | 0.328 | 0.513 | 0.941 | −0.116 [−0.153,−0.078] | −0.271 [−0.307,−0.235] |
| DeepSeek, first call only | 144 | 0.342 | 0.255 | 0.319 | 0.250 | 0.438 | 0.722 | −0.175 | −0.332 |
| DeepSeek, first call only | B | 0.378 | 0.255 | 0.331 | 0.263 | 0.484 | 0.738 | −0.132 | −0.287 |
| Qwen3.8-27B, no fine-tune | 144 | 0.064 | 0.016 | 0.057 | 0.013 | 0.071 | 0.045 | −0.452 [−0.504,−0.400] | −0.609 |
| Qwen3.8-27B, no fine-tune | B | 0.082 | 0.017 | 0.082 | 0.018 | 0.092 | 0.061 | −0.427 [−0.462,−0.391] | −0.582 |

- **DeepSeek setup.** `geom/dsv41_t0_rollout.py`, the exact T0 re-implementation, gained a `--hub-user` flag. Calls go
  to the lab hub (`wpk-serv-07:3456/v1/messages`, model `claude-deepseek-ai/DeepSeek-V4.1-Flash[1m]`, `x-hub-user:
  bimrose2`, 32 in flight, one process at a time), with effort low (= Reasoning Effort 25), 30k tokens and the default T
  1.0. Each draw gets ≤ 3 calls: answer-now if no code, exec-fix with the traceback if the code fails (label-free; e55
  gets no retries). "First call only" scores each draw's first reply alone.
- **DeepSeek results.** Per-draw mean 0.315 reproduces the T0 0.308/0.318. DeepSeek is far below e55 on every metric
  except exec, where the exec-fix calls lift it. Its gap to e55 is smallest on ABC (144-bench vote 0.385 vs 0.450).
  Median 15.7k output tokens; 21% of calls hit the 30k cap.
- **DeepSeek hub errors.** On the 144 run, 49/1,152 episodes died on hub connection errors (RemoteDisconnected /
  connection refused). They were re-run and re-scored; the old file is kept as `ds/real144_dsv41_t0.jsonl.with_hub_errors`.
  The numbers above are the repaired ones. Bench B had 0 errors.
- **Qwen3.8-27B (base) setup.** e55's exact prompt (SYSTEM_PROMPTS["detailed"] + USER_PROMPT, think on, K=8, same
  sampling). The one change: 16,000 max tokens / model-len 24,576 instead of 2,400, because the base model thinks for
  a median ~28k characters.
- **Qwen3.8-27B (base) results.** 96% of draws contain a ```python block, but only 4.5% / 6.1% execute. The failures
  are hallucinated build123d API: `Cylinder(pos=…)`, `Box(centered=…)`, lowercase `box`/`cylinder`,
  `ShapeList.filter_by_axis`, `extrude()` without a direction, and so on. **Answer to "RL from scratch?": no.** 114/144
  and 205/280 parts earn reward 0 on all 8 draws, i.e. degenerate GRPO groups with no gradient. Only 18/144 and 51/280
  parts reach IoU > 0.1. The SFT stack (API, dialect, drawing reading) is what makes RL possible here.

**Files.**
- `results/bench_b/`: README.md, tables.md, summarize.py, keys.txt, selection.json, leakcheck.json, exclusion/,
  render_failures.json, bench/, and eval/:
  - `benchb_*` and `real_{dsv41,dsv41_1call,qwenbase}` = scored + `_consistency`;
  - `real_{e55ctl,…}` = symlinks to results/grpo_eval;
  - `ds/` = raw DeepSeek episodes.
- Drivers: `eval_gpu7.sh`, `gpu7_resume*.sh`, `premerge.sh`, `ds_run.sh`, `ds_to_partial.py`, `score_vote_s20.sh`,
  `score_loop_b*.sh`, logs_s20/.
- Code: `train_v14/mech/benchmarks/build_bench_b.py`, `train_v14/sbatch/bench_b_build.sbatch`,
  `train_v14/sbatch/bench_b_score.sbatch`.
- Raw sources: `data_ext/bench_b_work/` (Fusion zip contents, ABC chunks, prep of 1,703 candidates, render set; can be
  deleted, everything needed is in `results/bench_b/bench`).
- serv-20: `/srv/scratch/bimrose2/bench_b/`; merged models `runs/merged_bb_{rft2_rl_s60,rft1_rl2_s120,ent_t10_s120}`
  (51 GB each, can be removed).
- GPU 7 is free again since 03:47. No commits made.

### Follow-up results (Oct 10, 08:15): s60 / s120

All votes clean (re-executed = n_exec). Real bench 144.

| arm | ckpt | vote | d0 | first-exec | mean | best-of-8 | exec |
|---|---|---|---|---|---|---|---|
| rft2_rl (no fix; collapsed) | s60 | 0.673 | 0.631 | 0.645 | 0.626 | 0.732 | 0.979 |
| rft2_rl | s120 | 0.665 | 0.433 | 0.661* | 0.433 | 0.719 | 0.679 |
| **rft2_raw** (`--train-raw`) | s60 | 0.653 | 0.626 | 0.632 | 0.629 | 0.725 | **0.995** |
| rft2_raw | s120 | pending | 0.617 | 0.630 | 0.627 | 0.722 | 0.985 |
| rft2_raw_s1 (seed 1) | s60 | pending | 0.656 | 0.665 | 0.630 | 0.735 | 0.988 |
| **g2_guided** (guided GRPO, round-2 banks, no fix) | s60 | 0.666 | 0.639 | 0.648 | 0.632 | 0.721 | 0.988 |
| **g2_guided** | s120 | **0.673** | **0.648** | **0.656** | 0.636 | 0.728 | 0.985 |
| g2_guided_raw | s60 | **0.673** | 0.632 | 0.641 | **0.637** | 0.728 | 0.983 |
| e55_t2_rl (fresh-LoRA SFT on tier 2 → RL, fix) | s60 | 0.661 | 0.607 | 0.622 | 0.625 | 0.726 | 0.978 |

\* first-exec and vote skip non-executing draws, so they stay high while d0/mean (failures count 0) collapse.

Key paired comparisons:
- rft2_raw s120 − rft2_rl s120: mean **+0.194 [+0.164, +0.226]**, exec +0.306. **`--train-raw` removes the collapse:** exec stays
  0.97–0.99 through s126, while rft2_rl was at 0.6. It does not keep improving after s60 (s120 − s60: mean −0.002).
- g2_guided s120 − rft2_rl s60 (best of the SFT→RL path): vote −0.000 [−0.016, +0.016], d0 +0.017, mean +0.010,
  best-of-8 −0.004 (all n.s.).
- g2_guided s120 − its start rft1_rl2 s120: d0 +0.030 [+0.006, +0.054], mean +0.015, best-of-8 +0.014 (significant).
- g2_guided_raw s60 − rft2_raw s60: vote +0.020 [+0.001, +0.040].
- e55_t2_rl s60 − rft2_rl s60: vote −0.012, d0 −0.024, mean −0.001 (n.s.).

**Reading.**
1. **Matched "SFT vs guided RL" for the found answers:** guided GRPO, from the same start at ~matched GPU-hours, ends
   **level with** the SFT→RL path. Its d0 is nominally higher, and neither guided arm collapsed under the new guard. The paper's
   "found answers belong in SFT, not RL" is **not supported by this matched test**. The earlier guided collapses coincide with
   the format blind spot (retro check), and g2_guided without `--train-raw` stayed healthy to s130 here. A seed replicate,
   g2_guided_s1, is running on GPU 6.
2. **Data vs compounding:** e55 + fresh LoRA trained on the final tier-2 dataset matches the round-structured path at SFT
   (vote +0.011) and after RL (n.s.).
3. **Plateau:** every route ends at vote 0.65–0.67, mean 0.625–0.637, best-of-8 0.72–0.735, and seed noise is ~±0.03 on d0.
   Round 2's measurable gain over the round-1 policy is small: vote +0.019 at best, significant only for rft2_rl s60.

Still running:
- rft2_raw → s200;
- g2_guided_raw → s130;
- e55_t2_rl → s130;
- rft2_kl2 (KL clamp 5) → s200;
- rft2_raw_s1 → s130;
- g2_guided_s1 → s130.

### Final results (Oct 12): bench-B system, late steps, extensions

Both helper agents stopped on Oct 10 (usage limit). All arms had already finished (s130/s200); the eval daemon (serv-20 GPU 3)
scored every checkpoint. serv-20 was idle Oct 10 20:00 – Oct 12 14:00.

**Bench B full pipeline (280 parts, pre-declared; `results/bench_b/pipeline/summary_b.py` → `summary_b.txt`).**

| system | mean | ABC | Fusion | ≥0.85 |
|---|---|---|---|---|
| S2 = e55 K=8 vote start | 0.514 | 0.414 | 0.578 | 15% |
| S2 = e55 + 3 rp3 chains, multi-start (0.695 recipe) | 0.664 | 0.542 | 0.742 | 37% |
| S1 = rft2_rl s60 K=16 selected start (no repair) | 0.691 | 0.585 | 0.758 | 38% |
| **S1 = rft2_rl s60 + 3 rp3 chains, multi-start** | **0.721** | 0.599 | 0.799 | 45% |

- S1 − S2: **+0.057 [+0.036, +0.078]** (+95/−32), the same on ABC and Fusion. On the 144 bench the systems were n.s. (+0.017),
  so on the bigger held-out bench the RL generator's gain **survives repair**.
- S1 start (no repair) − S2 full system: +0.026 [+0.004, +0.048], so the RL model alone beats e55 with repair.
- Repair: +0.150 on e55, +0.030 on the RL model (S1 multi-start − start). RL absorbs most of what repair used to add.

**Late-step 144-bench evals (Δ vs rft2_rl s60).**

| arm | step | vote | d0 | mean | bo8 | exec |
|---|---|---|---|---|---|---|
| rft2_raw | s200 | 0.667 | 0.651 | 0.646 | 0.732 | 0.984 |
| rft2_raw_s1 | s120 | 0.669 | **0.664** | 0.646 | 0.732 | 0.989 |
| rft2_kl2 (KL to rft2, clamp 5) | s200 | **0.678** | 0.646 | 0.641 | 0.733 | 0.989 |
| g2_guided_s1 | s120 | 0.664 | 0.642 | 0.631 | 0.722 | 0.984 |
| e55_t2_rl | s120 | 0.650 | 0.620 | 0.612 | 0.719 | 0.967 |

- `--train-raw` arms keep improving per-sample quality with no collapse: rft2_raw s200 mean +0.020 [+0.008, +0.034];
  rft2_raw_s1 s120 d0 +0.033 [+0.006, +0.059], mean +0.020 [+0.006, +0.034]. Vote and best-of-8 stay flat (plateau).
- rft2_kl2 s200 vote +0.004 (n.s.); KL anchoring is neutral.
- g2_guided_s1 replicates g2_guided (tie with SFT→RL).
- e55_t2_rl had a transient exec dip at s122–126 (0.78–0.84 per step) despite `--train-raw`; it recovered by s128.

**Extensions launched Oct 12 14:05 (serv-20; the rft2_raw recipe; daemon STEPS 20/60/120/200/300; ARMS has rft2_raw_s2 first):**
- rft2_raw: s200 → s300 (GPU 5, :8443, cores 24–47).
- rft2_raw_s1: s130 → s300 (GPU 4, :8447, cores 48–71).
- rft2_raw_s2: new seed 2 from runs/rft2_from_rl2/final → s200 (GPU 6, :8448, cores 72–95).

**Oct 12 22:45 update.** rft2_raw s300: vote 0.665, d0 0.654, mean 0.643, bo8 0.723, exec 0.993 (≈ s200; plateau). rft2_raw_s2
(seed 2): s60 vote 0.661 / d0 0.619; s120 vote 0.670 / d0 0.654 / mean 0.638 / exec 0.995. Three `--train-raw` seeds at s120:
d0 0.617 / 0.664 / 0.654, vote 0.659 / 0.669 / 0.670; minimum per-step exec over all steps 0.93. Votes for these were computed
on serv-20 (consistency_rerank.py) and copied to results/grpo_eval/. Running: rft2_raw_s1 → s300 (step 262), rft2_raw_s2 → s200 (step 132).

**Oct 13 final.** All arms done; serv-20 idle. rft2_raw_s1 s200 / s300: vote 0.663 / 0.662, d0 0.634 / 0.633, bo8 0.726 / 0.721.
rft2_raw_s2 s200: vote 0.680, d0 0.635, mean 0.642, bo8 0.729 (min per-step exec 0.86, recovered). Three-seed `--train-raw`
means: s120 vote 0.666 / d0 0.645; s200 vote 0.670 / d0 0.640. d0 peaks around s120 and does not keep rising (seed 0 holds 0.65 to
s300; seeds 1 and 2 fall back to ~0.635). No seed collapsed in 200–300 steps. Every comparison with rft2_rl s60 is n.s. on vote and bo8.

### In-distribution eval of the RL generators (Oct 13; for the paper's main table)

`mech_benchmarks/fullpool_dw423` (1,027 parts with GT), grpo_eval protocol (K=8, draw 0 greedy + T 0.7), serv-20 GPUs 4-6,
scored on serv-20 (`score_partials.py` + `consistency_rerank.py`); files `results/grpo_eval/full_*`; script
`/srv/scratch/bimrose2/tmp/indist_full.sh`. Table: `eval_table.py --prefix full --refs e55ctl ent_t10_s120 rft2_rl_s60`.

| model | vote | d0 | first-exec | mean | bo8 | exec |
|---|---|---|---|---|---|---|
| e55ctl | 0.917 (83% ≥0.85) | 0.804 | 0.899 | 0.788 | 0.943 | 0.876 |
| ent_t10_s120 (GRPO) | 0.922 (84%) | 0.910 | 0.912 | 0.909 | 0.948 | 0.996 |
| rft2_rl_s60 (expert iteration) | **0.932** (86%) | 0.877 | 0.915 | 0.878 | **0.958** | 0.959 |

- No in-distribution regression from RL. Single draw: +0.105 [+0.086, +0.124] (GRPO), +0.073 [+0.054, +0.092] (EI).
- Vote: GRPO +0.005 (n.s.); EI +0.015 [+0.009, +0.022].
- e55ctl reproduces the old 0.4.23-cache numbers: first-exec 0.886, vote 0.909, oracle 0.935.
