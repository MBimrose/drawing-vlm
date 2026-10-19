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
